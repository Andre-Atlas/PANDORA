# Chunking

**Escolhido: estrutural.** Um chunk por artigo (com caput, parágrafos e incisos), por súmula ou por seção de cartilha. Cada texto indexado começa com o cabeçalho da norma (`norma | seção | artigo`).

**Controle: fixo**, de 300 palavras com sobreposição de 40.

Limites: artigos acima de 320 palavras são divididos; alvo de 260 palavras por seção. Na base, a mediana é de 171 palavras, o p95 é de 289 e o máximo, ~374 (≈1,45 token por palavra em PT).

Resultado no dev (bge-m3, híbrido, sem reranker):

| Chunking | Hit@5 | nDCG@10 |
|---|---|---|
| Fixo, sem cabeçalho | 0,67 | 0,58 |
| Estrutural, sem cabeçalho | 0,76 | 0,62 |
| **Estrutural, com cabeçalho** | **0,80** | **0,69** |

O cabeçalho ajuda por si só: o artigo certo, que é o que a pessoa precisa para conferir a fonte, sobe para o topo.
