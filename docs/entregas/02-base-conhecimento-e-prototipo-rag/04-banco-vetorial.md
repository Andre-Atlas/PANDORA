# 4. Banco vetorial

- **PostgreSQL com pgvector 0.8.1**, imagem `pgvector/pgvector:0.8.1-pg17`, publicado na porta **5433** (a 5432 costuma estar ocupada por um Postgres local). Definido em `services/rag/docker-compose.yml`.
- **Tabela `chunks`**: texto, metadados do esquema da base (norma, artigo, link, vigência, hash) e a coluna `embedding vector(1024)`.
- **Índice HNSW** em `vector_cosine_ops`, com `m = 16` e `ef_construction = 64`.
- **BM25 fora do banco**: o `ts_rank` do Postgres não é BM25, então o índice lexical é construído em memória a partir dos registros do banco, a cada versão do corpus. O Postgres é a fonte da verdade.
- **Filtros por metadado**: fonte, camada de domínio, modalidade de dívida e elegibilidade à Lei 14.181.
- **Estado atual**: 1.183 chunks de 33 fontes (conferido com `select count(*), count(distinct fonte_id) from chunks`).

Código: `services/rag/src/pandora_rag/index/store.py`. Subir o banco e indexar:

```bash
cd services/rag
docker compose up -d
uv run pandora-rag coletar && uv run pandora-rag extrair && uv run pandora-rag indexar
```
