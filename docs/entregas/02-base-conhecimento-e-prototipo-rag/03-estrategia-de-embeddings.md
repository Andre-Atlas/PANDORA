# 3. Estratégia de embeddings

**Modelo escolhido: `BAAI/bge-m3`**, multilíngue, 1.024 dimensões, vetores normalizados (o produto escalar é o cosseno). Roda localmente, sem API. O texto embutido é o chunk com o cabeçalho da norma, e os vetores são guardados em cache por conteúdo (`index/build.py`).

**Busca híbrida.** Só embedding falha em número de artigo e termos exatos (`14.181`, `54-A`). Por isso a consulta combina duas buscas e funde os rankings:
1. busca vetorial (pgvector, top-50);
2. BM25 (`bm25s`, top-50) com tokenizador que preserva `14.181` e `54-A` e usa stemmer RSLP;
3. fusão por RRF (k = 60);
4. reranker `bge-reranker-v2-m3` sobre os 30 melhores.

**Comparação de modelos** (conjunto de desenvolvimento, chunking estrutural, híbrido, sem reranker):

| Modelo | Hit@5 | nDCG@10 |
|---|---|---|
| MiniLM multilíngue (baseline) | 0,15 (só vetor) | 0,09 |
| **bge-m3** | **0,80** | **0,69** |
| multilingual-e5-large | 0,76 | 0,66 |
| Legal-BERTimbau | 0,59 | 0,49 |
| Qwen3-Embedding-4B (corte para 1.024) | 0,74 | 0,67 |
| bge-m3 com ajuste fino (negativos difíceis) | 0,76 | 0,71 |

O ajuste fino melhorou nDCG e MRR em frações, mas piorou Hit@5; a diferença está dentro do ruído (uma pergunta vale cerca de 2 p.p.), então o modelo base foi mantido.

Mais detalhes: `docs/rag/04-embeddings.md` e `docs/rag/08-treinamento.md`.
