# Entregável: LLM × RAG

**Terceiro Desafio · RES IA ELD UNB · Turma 2 · PANDORA**
12 de novembro de 2026 · Víctor Moreira Almeida

Comparamos quatro formas de responder às mesmas 66 perguntas: LLM sozinho, RAG sozinho, RAG + qwen2.5:14b e RAG + qwen2.5:7b. **A escolhida para o PANDORA é RAG + qwen2.5:14b**, com nota 0,96 numa rubrica às cegas de 0 a 1, 100% de citação válida e nenhum número inventado. O LLM sozinho ficou em 0,11 e inventou norma ou número em 76% das respostas. O ganho do RAG foi de +85 p.p., contra a meta de +25 p.p. do escopo. O ponto pendente é a latência: nenhuma configuração com LLM cumpre o p95 de 8 s nesta máquina.

## O que é RAG

RAG (Retrieval-Augmented Generation, geração aumentada por recuperação) é buscar trechos relevantes numa base de documentos e entregá-los ao LLM junto com a pergunta, para que a resposta se apoie nesses trechos e não só no que o modelo memorizou no treino.

O pipeline tem duas metades:

1. **Indexação (offline):** coletar as fontes, extrair o texto, dividir em chunks, gerar um embedding de cada chunk e guardar tudo num índice (vetorial e, no nosso caso, também BM25).
2. **Consulta (online):** transformar a pergunta em embedding, buscar os chunks mais parecidos, reordenar com um reranker e montar o prompt com os melhores trechos numerados. O LLM escreve a resposta citando esses números.

O RAG resolve três limites do LLM sozinho: o conhecimento parado na data de corte, a falta de fonte verificável e a tendência de inventar prazo, artigo ou valor quando não sabe.

## Como o RAG está no PANDORA

O RAG da branch `develop` (versão `rag-v0.1.0`) responde dúvidas de pessoas endividadas com base em 33 fontes oficiais: leis, resoluções do CMN e da CVM, súmulas do STJ e cartilhas do BCB, CNJ e Procon. Ele alimenta a Elpis (chat) e a Trilha do app.

| Etapa | Escolha atual | De onde veio |
| --- | --- | --- |
| Chunking | Estrutural (por artigo/seção), com cabeçalho da norma | Ablação da semana 2 |
| Embedding | `BAAI/bge-m3` | Venceu MiniLM, e5, Legal-BERTimbau e Qwen3-Embedding |
| Busca | Híbrida: vetor + BM25, fusão RRF (k=60) | Venceu vetor puro e BM25 puro |
| Reranker | `bge-reranker-v2-m3` | Hit@1 subiu para 0,57 no dev |
| Portão de abstenção | Se a nota do melhor trecho for menor que 0,02, não chama o LLM | Limiar treinado no dev |
| Geração | `qwen2.5:14b` local (Ollama), top-3 trechos, citação [n] obrigatória | Escolha provisória da semana 2 |

Na semana 2, o LLM foi escolhido com a recuperação fixa, mas nunca se mediu o quanto o RAG muda a resposta em relação ao LLM sozinho. Essa comparação era uma meta do escopo (rubrica LLM × RAG, ganho ≥ 25 p.p.) e é o foco desta semana.

## LLM sozinho, RAG sozinho e RAG com LLM: o que muda

Cada modo erra de um jeito diferente. O LLM sozinho escreve bem, mas inventa a fonte. O RAG sozinho acha a fonte, mas não responde à pergunta. Juntos, um cobre o defeito do outro.

**Exemplo 1 (d-001):** *"Qual é o valor considerado como mínimo existencial para a renda mensal de um consumidor em casos de superendividamento?"* A resposta certa é R$ 600,00 (Decreto 11.150/2022, art. 3º, com redação do Decreto 11.567/2023).

| Modo | Resposta (resumida) | O que aconteceu |
| --- | --- | --- |
| LLM sozinho (T1) | "O mínimo existencial não está definido por um valor específico na legislação… De acordo com a Lei nº 10.522/2002 e o CDC…" | Errou o valor e citou uma lei sem relação. O modelo não conhece o decreto de 2023 e preenche a lacuna com algo plausível. |
| RAG sozinho (T2) | "Segundo Decreto 11.150/2022, Art. 3: 'Art. 3º No âmbito da prevenção… equivalente a R$ 600,00 (seiscentos reais). § 1º A apuração…'" | A fonte e o valor estão certos, mas a pessoa recebe 180 palavras de texto legal e precisa achar a resposta sozinha. |
| RAG + LLM (T3) | "O mínimo existencial é R$ 600,00 [1][3]. AVISO DE VIGÊNCIA: … o consignado entra na proteção do mínimo existencial (STF, ADPFs 1005, 1006 e 1097)." | Resposta direta, com as duas normas citadas e o aviso de que o STF mudou a regra do consignado. |

**Exemplo 2 (dx-001), uma pergunta com premissa falsa:** *"Qual artigo do CDC obriga o banco a aceitar qualquer proposta de pagamento que eu fizer?"* Nenhum artigo faz isso.

- **RAG sozinho:** devolveu o art. 35 do CDC (recusa de oferta pelo fornecedor) como se fosse a resposta. A busca sempre acha algo parecido e, sem um leitor, não percebe que o trecho não responde.
- **LLM sozinho:** disse que não existe tal artigo, mas acrescentou que "o art. 42 fala sobre a negociação de dívidas", o que é falso (o art. 42 trata de cobrança abusiva).
- **RAG + LLM:** recusou e indicou Procon, Defensoria e Banco Central.

**Por que muda.** O LLM sem fontes depende do que memorizou, e normas recentes (Desenrola, teto do rotativo, decisões do STF de 2026) estão fora ou mal representadas no treino. O RAG traz o texto oficial, mas só mede semelhança: não sabe se o trecho responde, não resume e não recusa premissa falsa. Com o LLM lendo apenas as fontes recuperadas, a resposta fica fundamentada e legível, e o LLM vira um segundo filtro de abstenção depois do portão.

## Metodologia

Os quatro testes respondem às mesmas 66 perguntas, com a mesma recuperação e no mesmo computador (Apple M4, 24 GB, modelos locais no Ollama, temperatura 0). Só muda a forma de responder.

**Perguntas.** O conjunto de desenvolvimento `dev.v1` (46 perguntas respondíveis: 31 normativas e 15 de persona, mais 5 fora de domínio) e 15 perguntas novas fora de domínio, escritas antes de qualquer rodada nas mesmas categorias do golden: premissa falsa, norma inexistente, assunto alheio, recomendação de ativo, informação fora do corpus e promessa de resultado. O conjunto de teste (golden, 169 perguntas) não foi usado: ele tem rodadas contadas e fica para a validação final.

**Recuperação comum.** bge-m3 + BM25 com fusão RRF, reranker bge-reranker-v2-m3, top-3 trechos e portão de abstenção 0,02, como na versão atual. Corpus `515669eb8f54` (1.183 chunks), o mesmo da semana 2.

**Métricas.** As da semana 2 foram mantidas e quatro foram acrescentadas ou corrigidas:

| Métrica | O que mede | Novidade |
| --- | --- | --- |
| Rubrica às cegas 0/1/2 | 2 = correta e completa; 1 = parcial, ou trecho bruto que contém a resposta; 0 = errada, inventada ou recusa indevida | Nova: meta do escopo que ainda não tinha sido medida |
| Citação válida | Resposta com marcador [n] ligado a norma e link reais | — |
| Abstenção correta / recusa indevida | Recusa o que deve recusar, responde o que deve responder | Agora com 20 perguntas fora de domínio, e não 5 |
| Acerto de número | Fração dos números da referência presentes na resposta | Normalizador corrigido ("50.000,00" = "50.000") |
| Números sem suporte | Respostas com número (2+ dígitos) que não está na pergunta, na referência, nos trechos de ouro nem nas fontes entregues | Nova: sinal de número inventado |
| Norma correta | A resposta ou a fonte citada traz o número da norma esperada (ex.: 14.181) | Nova: vale para o LLM sozinho também |
| ROUGE-L | Sobreposição de palavras com a referência | Só diagnóstico: as referências foram rascunhadas pelo qwen2.5:14b, o que favorece esse modelo |
| Latência média e p95 | Tempo por pergunta | Corrigida: agora de ponta a ponta (busca + geração); antes só contava o LLM |

Todo número sai com intervalo de confiança bootstrap de 95%. Cada teste vira uma execução reproduzível em `evals/runs/2026-11-12-s3-*`, com `config.json`, `metrics.json` e as respostas pergunta a pergunta.

## Os 4 testes e os resultados

O RAG com LLM vence em qualidade com folga: 0,96 na rubrica contra 0,11 do LLM sozinho. O RAG sozinho é fiel às fontes, mas responde mal. O modelo menor corta a latência quase pela metade e perde 10 p.p. de qualidade.

| Teste | Como responde |
| --- | --- |
| T1 · LLM sozinho | qwen2.5:14b sem fontes, só com o que memorizou; instruído a recusar se não tiver certeza |
| T2 · RAG sozinho | Busca + portão; devolve o melhor trecho (até 180 palavras) com a fonte, sem LLM |
| T3 · RAG + LLM 14B | Busca + portão + qwen2.5:14b lendo os 3 melhores trechos (configuração atual) |
| T4 · RAG + LLM 7B | Igual ao T3, com qwen2.5:7b no lugar do 14B |

**Resultados** (dev.v1 + 15 fora de domínio; 46 respondíveis e 20 que devem ser recusadas; IC 95% entre colchetes)

| Métrica | T1 LLM sozinho | T2 RAG sozinho | T3 RAG + 14B | T4 RAG + 7B |
| --- | --- | --- | --- | --- |
| Rubrica às cegas (0 a 1) | 0,11 [0,04–0,19] | 0,41 [0,36–0,47] | **0,96** [0,91–0,99] | 0,86 [0,77–0,94] |
| Respostas nota 2 / 1 / 0 | 2 / 6 / 38 | 0 / 38 / 8 | **42 / 4 / 0** | 36 / 7 / 3 |
| Citação válida | 0% | 100% | **100%** | 96% |
| Recusa indevida | 28% (13 de 46) | 0% | **0%** | 4% (2) |
| Abstenção correta (20) | 80% | 40% | **85%** | 80% |
| Norma correta | 23% | 81% | 94% | **97%** |
| Respostas com número sem suporte | 76% [61–88%] | 0% | **0%** | 5% [0–11%] |
| Acerto de número | 0,07 | 0,79 | **0,88** | 0,71 |
| ROUGE-L (diagnóstico) | 0,15 | 0,15 | 0,29 | 0,31 |
| Latência média / p95 | 13,1 s / 27,7 s | **3,4 s / 4,3 s** | 30,8 s / 56,2 s | 17,5 s / 25,1 s |

Como ler a tabela:

- **Ganho do RAG sobre o LLM sozinho:** +85 p.p. na rubrica para o T3 (IC 76 a 92 p.p.) e +75 p.p. para o T4. A meta do escopo era +25 p.p.
- **T3 × T4:** o 14B fica 10 p.p. acima na rubrica (IC 1 a 18 p.p.). Na contagem de notas máximas, a diferença não é significativa (McNemar p = 0,11). O 7B recusou 2 perguntas respondíveis e inventou uma data de vigência ("31 de dezembro de 2023").
- **Acerto de número** só vale para as 5 a 8 perguntas cuja referência tem número. Serve de indício, não de prova.
- **Latência** foi medida num Apple M4 base, em que o qwen2.5:14b gera 8,4 tokens/s. Na máquina da semana 2, o mesmo T3 levou 7 s em média só de geração. O que vale aqui é a comparação entre os testes. A busca custa 3,4 s por pergunta (bge-m3 + reranker), e a semana 2 não contava esse tempo.

## Escolha para o PANDORA

**Escolhido: T3, RAG + qwen2.5:14b, com o RAG sozinho (T2) como modo de contingência.** Num app que fala de lei, prazo e dívida com pessoas vulneráveis, uma resposta errada custa mais do que uma resposta lenta. O T3 foi o único sem nenhuma nota 0, sem número inventado e sem recusa indevida.

Por que não os outros:

- **T1, LLM sozinho:** inventou norma ou número em 76% das respostas e acertou a norma em 23%. Ainda recusou 28% das perguntas que tinham resposta. Sem fontes, não dá para verificar nada.
- **T2, RAG sozinho:** nunca inventa e é 9 vezes mais rápido, mas entrega texto legal bruto e não sabe recusar. No exemplo da premissa falsa, devolveu um artigo sem relação como se fosse a resposta, e só recusou 8 de 20 perguntas fora de domínio.
- **T4, RAG + 7B:** é a alternativa mais forte. Responde em pouco mais da metade do tempo e acerta a norma tanto quanto o 14B. Perde 10 p.p. na rubrica, tem 2 recusas indevidas e inventou uma data de vigência. Fica como plano B se a latência virar bloqueio.

**Uso do T2 no produto.** Quando o LLM falhar ou passar do tempo limite, a Elpis mostra os trechos recuperados com as fontes, no lugar de uma mensagem de erro. Isso mantém a regra de nunca responder sem fonte.

**O que ainda não fecha:**

- **Latência.** Nenhuma configuração com LLM cumpre o p95 ≤ 8 s nesta máquina. Próximos passos: streaming da resposta (o usuário começa a ler antes do fim), servir o modelo numa máquina com GPU e, no refinamento, testar o Claude Haiku 5.5 pelo gateway, que já está configurado.
- **Abstenção.** O portão recusa 8 das 20 perguntas fora de domínio, e o LLM recusa mais 9. Das 3 que o T3 respondeu, 2 eram promessas de resultado e a resposta negou a promessa corretamente ("não há garantia de que a dívida seja reduzida pela metade"). A métrica deveria aceitar essa negação como acerto. A terceira (telefone do Procon) é falha real.
- **Rubrica.** Foi aplicada por um avaliador automatizado (Claude), cego quanto ao rótulo. O estilo denuncia parte dos modos, e por isso a equipe deve revisar uma amostra antes da entrega final.
- **Confirmação no teste.** A escolha foi feita no dev. A rodada 2 do golden (169 perguntas) deve confirmar o T3 depois da revisão humana do golden.

## Links e reprodução

**Projeto**

- Repositório: [github.com/Andre-Atlas/PANDORA](https://github.com/Andre-Atlas/PANDORA)
- Código do RAG (branch develop): [services/rag](https://github.com/Andre-Atlas/PANDORA/tree/develop/services/rag)
- Documentação do RAG: [docs/rag](https://github.com/Andre-Atlas/PANDORA/tree/develop/docs/rag)
- Escolha do LLM da semana 2: [09-decisao-llm.md](https://github.com/Andre-Atlas/PANDORA/blob/develop/docs/rag/09-decisao-llm.md)
- Conjunto dev: [evals/golden/dev.v1.jsonl](https://github.com/Andre-Atlas/PANDORA/blob/develop/evals/golden/dev.v1.jsonl)

**Desta semana** (branch `entrega/llm-x-rag-terceiro-desafio`, a partir da develop)

| Arquivo | O que é |
| --- | --- |
| [`evals/llm_x_rag.py`](../../../evals/llm_x_rag.py) | Roda os 4 testes e calcula as métricas |
| [`evals/rubrica_cega.py`](../../../evals/rubrica_cega.py) | Gera a folha às cegas e pontua a rubrica |
| [`evals/golden/fora_de_dominio.py`](../../../evals/golden/fora_de_dominio.py) | 15 perguntas novas fora de domínio (`DEV_EXTRA`) |
| [`evals/metrics/textos.py`](../../../evals/metrics/textos.py) | Correção do normalizador de números, com teste |
| [`evals/runs/`](../../../evals/runs/) (`2026-11-12-s3-*`) | Configuração, métricas e respostas de cada teste, mais a rubrica |
| [`docs/rag/10-llm-x-rag.md`](../../rag/10-llm-x-rag.md) | Resumo técnico deste relatório |

**Para reproduzir** (de `services/rag`, com Ollama instalado; cerca de 2 h num M4 base):

```bash
uv sync --extra eval --extra dev
uv run pandora-rag coletar && uv run pandora-rag extrair
ollama pull qwen2.5:14b && ollama pull qwen2.5:7b
PYTHONPATH=../.. uv run python -m evals.llm_x_rag
PYTHONPATH=../.. uv run python -m evals.rubrica_cega exportar
PYTHONPATH=../.. uv run python -m evals.rubrica_cega pontuar
```
