# 1. Base de conhecimento curada

**33 documentos-fonte oficiais e 1.183 chunks indexados** (meta do desafio: mínimo de 20 documentos). A lista completa, com órgão, data de referência, hash e link de cada fonte, está em [fontes.md](fontes.md). A definição machine-readable fica em `services/rag/fontes.yaml`, e os hashes em `services/rag/corpus.lock`.

## Critérios de curadoria

- **Só fonte oficial**: Planalto, BCB, CMN, CVM, CNJ, STF, STJ, Senacon, MPF, TJSP e Procon. Blogs de advocacia e coletâneas de terceiros ficaram de fora.
- **Aderência ao problema**: pessoas endividadas ou com comportamento financeiro compulsivo (dívida de cartão, superendividamento, apostas, golpes, renegociação, educação financeira).
- **Rastreabilidade**: cada fonte tem SHA-256 do arquivo bruto, tamanho e data da coleta em `corpus.lock`. Alterou a fonte, o hash muda e o corpus ganha nova versão.
- **Vigência**: texto riscado (revogado) é removido na extração. Quando uma decisão posterior afeta um trecho, ele recebe uma `ressalva`, que o prompt manda repetir na resposta. Exemplo: o Decreto 11.150/2022 (⚠ na tabela) teve um inciso declarado inconstitucional pelo STF em 23/04/2026 (ADPFs 1005, 1006 e 1097).

## Composição

| Grupo | Exemplos |
|---|---|
| Leis e decretos | CDC compilado, Lei 14.181/2021 (superendividamento), Lei 14.690/2023 (teto do rotativo), Lei 14.790/2023 (apostas), Lei 8.009/1990, CPC (art. 833), DL 911/1969, Lei 9.514/1997, Lei 14.015/2020, Decretos 11.150/2022 e 11.567/2023 |
| Normas do CMN, BCB e CVM | Resoluções CMN 4.558, 4.881, 4.882, 5.057 e 5.112; Resolução BCB 147; Resoluções CVM 19, 20 e 30 |
| Jurisprudência | Súmulas do STJ, decisão do STF nas ADPFs sobre o mínimo existencial |
| Educação e cartilhas | Caderno de Educação Financeira do BCB, Série Cidadania Financeira nº 8, Cartilha do CNJ, Manual do TJSP, cartilhas dos Procons (PAS e Juiz de Fora), Manual da Senacon, Série CVM Comportamental, Estudo Especial BCB 119/2024 |

## Esquema de metadados de cada chunk

`id`, `fonte_id`, `titulo`, `orgao`, `tipo`, `norma`, `artigo`, `secao`, `pagina`, `ordem`, `texto`, `hash`, `link`, `data_referencia_normativa`, `camada_dominio`, `ressalva`. O `link` aponta para a página oficial, e é ele que aparece na lista de fontes da resposta.

## Onde está o conteúdo

- `base_de_conhecimento/chunks.jsonl` (no zip): os 1.183 chunks com todos os metadados.
- `base_de_conhecimento/fontes.yaml` e `corpus.lock` (no zip): o catálogo e os hashes.
- O texto bruto baixado (HTML e PDF, 31 MB) não vai no repositório. Quem quiser refazer roda `pandora-rag coletar`, e o `corpus.lock` permite conferir se a fonte mudou.

Para regenerar a tabela e o `chunks.jsonl`: `uv run --project services/rag python docs/entregas/02-base-conhecimento-e-prototipo-rag/gerar_artefatos.py --chunks chunks.jsonl`.
