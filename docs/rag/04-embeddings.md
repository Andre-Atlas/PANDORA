# Embeddings

Dev, estrutural, híbrido, sem reranker (46 perguntas, nDCG@10):

| Modelo | Hit@5 | nDCG@10 |
|---|---|---|
| MiniLM multilíngue (baseline do estágio 0) | 0,15 (só vetor) | 0,09 |
| **BAAI/bge-m3** | **0,80** | **0,69** |
| intfloat/multilingual-e5-large | 0,76 | 0,66 |
| Legal-BERTimbau | 0,59 | 0,49 |
| Qwen3-Embedding-4B (corte para 1024) | 0,74 | 0,67 |
| bge-m3 ajustado com negativos difíceis | 0,76 | 0,71 |

Escolha: **bge-m3**, o melhor com Hit@5. O ajuste fino melhora nDCG e MRR em frações, mas perde em Hit@5 e no artigo do top-3; a diferença fica dentro do ruído (1 pergunta vale ~2 p.p.), então o modelo base foi mantido. Detalhes em [08](08-treinamento.md).
