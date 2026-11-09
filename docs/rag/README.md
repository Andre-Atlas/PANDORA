# RAG do PANDORA: documentação

Índice da documentação do RAG (issues #50, #52 e #53). Versão base: `rag-v0.1.0`.

> **Estado desta versão.** A recuperação está fechada no bge-m3 com chunking estrutural e bge-reranker-v2-m3. O LLM provisório é o qwen2.5:14b, com portão de abstenção. O golden set foi **validado automaticamente, mas ainda não foi revisado por humanos**; a revisão manual fica para o segundo refinamento. Algumas metas não foram atingidas (ver [09-decisao-llm](09-decisao-llm.md) e [07-metricas-e-resultados](07-metricas-e-resultados.md)).

| Documento | Conteúdo |
|---|---|
| [01-arquitetura](01-arquitetura.md) | Diagrama e componentes |
| [02-pipeline-ingestao](02-pipeline-ingestao.md) | Coleta, extração, chunking e indexação |
| [03-chunking](03-chunking.md) | Chunking estrutural × fixo |
| [04-embeddings](04-embeddings.md) | Modelos testados e escolha |
| [05-banco-vetorial](05-banco-vetorial.md) | pgvector, BM25 e fusão |
| [06-golden-set](06-golden-set.md) | Golden, dev e treino: como foram feitos e validados |
| [07-metricas-e-resultados](07-metricas-e-resultados.md) | Métricas e resultados |
| [08-treinamento](08-treinamento.md) | Ablação, ajuste fino e abstenção |
| [09-decisao-llm](09-decisao-llm.md) | Escolha do LLM (#53) |
| [CHANGELOG](CHANGELOG.md) | Versões do corpus, do golden e dos modelos |

Execuções reproduzíveis ficam em `evals/runs/`, e o histórico de rodadas do teste em `evals/test_log.md`.
