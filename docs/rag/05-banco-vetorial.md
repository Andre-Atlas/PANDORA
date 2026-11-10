# Banco vetorial e BM25

- **pgvector 0.8.1** em `pgvector/pgvector:0.8.1-pg17`, porta 5433 (a 5432 já tem um Postgres local). Índice HNSW em `vector_cosine_ops`, `m=16`, `ef_construction=64`.
- **BM25** (`bm25s`) com tokenizador próprio: preserva `14.181` e `54-A`, usa stemmer RSLP (`index/tokenizer.py`). Não usa `ts_rank`, que não é BM25.
- **Fusão**: RRF ponderada, `k=60`. Parâmetros do dev: pesos vetor:BM25 de 2:1 foram os melhores (nDCG@10 0,71), mas a diferença para 1:1 (0,69) é de ruído.
- **Filtros**: metadados (fonte, camada de domínio, modalidade de dívida, elegibilidade à Lei 14.181).
- **Reranker**: bge-reranker-v2-m3 sobre os top-30. O Qwen3-Reranker-4B também foi testado: latência média de 33 s e p95 de 64 s, inviável; fora.

Tabelas e colunas: ver `services/rag/src/pandora_rag/index/store.py`.
