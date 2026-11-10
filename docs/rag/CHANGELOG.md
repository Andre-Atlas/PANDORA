# Changelog do RAG

Formato: versão, data, o que mudou. Versões do corpus, do golden e dos modelos ficam nos respectivos `*.lock` e `config.json` das execuções.

## rag-v0.1.0 (2026-11-09)

- Corpus: 33 fontes oficiais, 1.183 chunks, versão `515669eb8f54`.
- Chunking estrutural com cabeçalho, bge-m3, pgvector HNSW, BM25 próprio, RRF e reranker bge-reranker-v2-m3.
- Portão de abstenção com limiar 0,02 (nota do reranker).
- LLM provisório: qwen2.5:14b, top-3.
- Golden set 169 + dev 51 gerados e validados automaticamente; revisão humana pendente.
- Ajuste fino do bge-m3 testado e não adotado.
- Qwen3-Embedding-4B e Qwen3-Reranker-4B testados e não adotados.
- Métricas de teste: citação 96%, abstenção 70%, p95 14,4 s (todas abaixo da meta). Ver [07](07-metricas-e-resultados.md).
