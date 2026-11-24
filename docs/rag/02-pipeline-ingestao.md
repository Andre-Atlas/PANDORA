# Pipeline de ingestão

`coletar → extrair → chunking → indexar`, na CLI `pandora-rag`. Para o corpus crescer sozinho, há mais quatro comandos: `descobrir`, `lacunas`, `reindexar` e `monitorar` (ver [Povoamento contínuo](#povoamento-contínuo)).

1. **Coleta** (`ingest/collect.py`, `ingest/web.py`): baixa as fontes de `fontes.yaml`, todas ou só as escolhidas com `--fonte ID`. Cada requisição passa pelo `ClienteEducado`:
   - só domínios de `dominios.yaml`, inclusive nos redirecionamentos;
   - respeita o robots.txt, com curingas `*` e `$`;
   - no máximo 1 requisição por segundo por domínio;
   - limite de 30 MB por arquivo e HTTP/1.1 (o Planalto recusa HTTP/2);
   - página de verificação anti-robô vira `AntiRobo` e a fonte é pulada. Nunca é contornada.

   A coleta é condicional (`ETag` e `If-Modified-Since`). O `corpus.lock` guarda dois hashes:
   - `sha256_bruto`, do arquivo baixado;
   - `sha256_texto`, do texto extraído. É este que decide se a fonte mudou.

   Cada fonte volta com uma situação: `nova`, `texto mudou`, `só layout` (o HTML mudou e o texto não) ou `sem mudança`.
2. **Extração** (`ingest/extract.py`): HTML por blocos de texto; PDF com pymupdf, filtrando cabeçalho e rodapé. Remove texto riscado (`<strike>`, `<s>`, `<del>`), que é revogado. Grava em `data/text/{id}.jsonl`, fora do git. A coleta já grava o texto das fontes que mudaram.
3. **Chunking** (`ingest/chunk.py`): ver [03](03-chunking.md). Ids `fonte#numero`; artigos citados ganham `#c{n}`; partes ganham `-pN`; colisões ganham `~n`.
4. **Indexação** (`pandora-rag indexar`): embedding com cache por conteúdo e carga no pgvector. Sem `--incremental`, recria a tabela. Com o serviço no ar, use `reindexar`.

Revogações e ressalvas: artigos vetados ou revogados ficam fora. Normas que alteram outra (ex.: trecho inserido na Lei 8.009) registram a norma alterada em `alvo`. A decisão do STF de 23/04/2026 (ADPFs 1005/1006/1097) fica como `ressalva` nos trechos afetados, e aparece na resposta.

Versão do corpus: hash do conjunto de SHA-256 dos trechos (`versao_do_corpus`).

O manifesto é validado com rigor: chave desconhecida dá erro, e `modalidade_divida`, `nivel_urgencia`, `camada_dominio` e `tipo` só aceitam os valores do catálogo. A data é `AAAA-MM-DD`.

## Povoamento contínuo

```bash
uv run pandora-rag descobrir     # crawler + API do BCB → fontes.candidatas.yaml
uv run pandora-rag reindexar     # testa candidatas e mudanças numa tabela sombra; troca só se a trava passar
uv run pandora-rag monitorar     # rotina semanal: recoleta, busca normativos novos e reindexa se algo mudou
uv run pandora-rag lacunas       # perguntas sem resposta viram consultas (--buscar procura no BCB)
```

### Descoberta (`ingest/descobrir.py`)

- **Crawler:**
  - busca em largura a partir de `sementes.yaml`, com profundidade máxima 2, só dentro de `dominios.yaml`;
  - segue um link só se o texto ou o endereço tiver um dos `termos_relevantes`;
  - deduplica pela URL canônica (sem fragmento, rastreio ou id de sessão) e pelo hash do texto contra o corpus e as outras candidatas;
  - descarta páginas de navegação (mais de 40% do texto em links) e textos com menos de 200 palavras.
- **API de normativos do BCB:**
  - lista as resoluções CMN, BCB e Conjuntas do período;
  - filtra pelo assunto, que precisa de um termo ligado ao consumidor pessoa física e de nenhum termo de exclusão (rural, contábil, liquidez…);
  - pula as revogadas e canceladas.
- **Metadados:**
  - a `dica` da semente vale primeiro;
  - `tipo` sai por regra de URL e título;
  - `camada_dominio`, `modalidade_divida` e `nivel_urgencia` são sugeridos pelo LLM local, que só pode responder valores da lista fechada. O texto raspado entra como dado, nunca como instrução;
  - a data vem do texto (por extenso ou dd/mm/aaaa), ou só do ano.
- **Confiança:**
  - `alta` exige camada, data explícita e pelo menos 200 palavras;
  - título de navegação ("Notícias", "Portal"…) nunca é alta;
  - só `alta` é testada pela reindexação. As outras ficam em `fontes.candidatas.yaml` com o motivo.

Limites conhecidos:
- As páginas índice do BCB (Biblioteca de Cidadania Financeira, Estudos Especiais) montam a lista de links por JavaScript, então o crawler não vê links nelas. Os PDFs entram como sementes diretas.
- PDF escaneado, sem camada de texto, fica de fora (não há OCR).
- O LexML exige verificação anti-robô, por isso não é usado.

### Reindexação com trava (`ingest/pipeline.py`, `ingest/trava.py`, `index/incremental.py`)

1. Junta o manifesto e as candidatas testáveis: confiança alta e nenhuma recusa da trava nos últimos 30 dias (`--retestar` ignora o prazo).
2. Avalia o índice atual com o golden (as 149 perguntas com trecho-ouro). Essa é a régua de todos os testes.
3. Testa em lotes. Cada teste:
   - confere o corpus (ids únicos, link https, data, artigos centrais, sem cabeçalho vazado);
   - copia `chunks` para `chunks_candidato` e atualiza só as fontes cuja assinatura mudou. A assinatura é o hash dos registros sem `versao_corpus`, então metadado novo, como uma ressalva, também conta;
   - passa se nenhuma métrica (recall@5, MRR, `artigo_top3`) cair mais de 1 ponto percentual em relação ao índice atual.
4. A ordem dos lotes:
   1. Só as mudanças das fontes atuais. Se pioram a busca, ficam retidas: os trechos delas continuam como estão no índice, e as candidatas são testadas por cima.
   2. Cada grupo de candidatas (por origem: `crawler`, `bcb_busca`, `lacuna`), por cima do que já passou. O grupo que falha é dividido ao meio até isolar a candidata culpada.

   Como a régua é sempre o índice atual, a soma das quedas nunca passa da tolerância. Os embeddings ficam em cache durante a execução, então um trecho é embedado uma vez só.
5. No fim:
   - as aceitas vão para o fim do `fontes.yaml`, sem mexer nas linhas curadas;
   - as recusadas ganham `barrada_em` e o motivo em `fontes.candidatas.yaml`;
   - as tabelas trocam numa transação (`chunks` vira `chunks_anterior`, para voltar atrás);
   - o serviço recebe `POST /recarregar`.

   Se nada passar, nada muda.
6. O relatório, com cada lote, vai para `evals/runs/AAAA-MM-DD-reindexacao/`.

**Limite da trava:** o golden só tem perguntas sobre o corpus antigo. Uma fonte nova não ganha ponto por responder perguntas novas, só perde se empurrar um trecho-ouro para fora do top-5. Por isso cartilhas longas e gerais (como os módulos do Caderno do BCB) tendem a ser barradas. Para elas entrarem, o golden precisa de perguntas que só elas respondem.

Na primeira execução real (2026-11-24):
- o crawler e a API do BCB acharam 20 candidatas, 16 delas de confiança alta;
- a trava aceitou 10, todas resoluções do BCB e do CMN, mais a Recomendação CNJ 125;
- o índice foi de 1.183 para 1.292 trechos;
- ficaram retidas as mudanças de 10 fontes atuais. O texto delas não mudou; o índice foi gerado antes de uma mudança no rótulo `norma` dos artigos citados, e reindexar com o código atual derruba o `artigo_top3` de 0,804 para 0,794.

O serviço recarrega sem reiniciar: `POST /recarregar` monta o índice novo com os modelos já carregados e troca sob a trava. Ele só aceita chamadas da própria máquina, ou com o cabeçalho `x-pandora-admin` igual a `PANDORA_RAG_TOKEN_ADMIN`. O `/saude` mostra a `versao_corpus`.

### Lacunas (`ingest/lacunas.py`)

Com `PANDORA_REGISTRAR_LACUNAS=1`, o serviço grava em `data/lacunas.jsonl` cada pergunta que terminou em abstenção. Cada linha tem só o dia, o motivo, a melhor nota e a pergunta mascarada. A máscara tira CPF, CNPJ, valores, números longos, e-mails, telefones, datas e nomes próprios. O contexto da conversa e a resposta nunca são gravados. `pandora-rag lacunas` agrupa os termos que se repetem, e `--buscar` usa esses termos na busca de texto do BCB.

### Agendamento

O corpus fica fora do git, então o monitoramento roda na máquina, não no CI. Exemplo de cron semanal (segunda, 6h):

```cron
0 6 * * 1 cd /caminho/PANDORA/services/rag && uv run pandora-rag monitorar >> data/monitorar.log 2>&1
```
