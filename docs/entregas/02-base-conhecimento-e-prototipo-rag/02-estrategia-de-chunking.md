# 2. Estratégia de chunking

**Escolhida: divisão estrutural.** Um chunk por artigo de lei ou resolução (com caput, parágrafos e incisos juntos), um por verbete de súmula e um por pergunta-resposta ou seção de cartilha. Cada texto indexado começa com um cabeçalho `norma | seção | artigo`, para que o artigo certo suba no ranking e a fonte possa ser conferida.

**Controle:** divisão de tamanho fixo (300 palavras, sobreposição de 40), usada só para medir o ganho.

**Limites:** artigos acima de 320 palavras são divididos; o alvo por seção de cartilha é de 260 palavras. Na base, a mediana é de 171 palavras e o p95 é de 289. Artigos vetados ou revogados ficam fora. Normas que alteram outra (por exemplo, a Lei 14.181 inserida no CDC) guardam a norma alterada.

**Resultado no conjunto de desenvolvimento** (46 perguntas respondíveis, bge-m3, busca híbrida, sem reranker):

| Chunking | Hit@5 | nDCG@10 |
|---|---|---|
| Fixo, sem cabeçalho | 0,67 | 0,58 |
| Estrutural, sem cabeçalho | 0,76 | 0,62 |
| **Estrutural, com cabeçalho** | **0,80** | **0,69** |

Implementação: `services/rag/src/pandora_rag/ingest/chunk.py`, com testes em `services/rag/tests/test_chunk.py`.
