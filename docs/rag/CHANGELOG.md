# Changelog do RAG

Formato: versão, data, o que mudou. Versões do corpus, do golden e dos modelos ficam nos respectivos `*.lock` e `config.json` das execuções.

## Não lançado

- Serviço HTTP (`pandora-rag servir`, porta 8010): `GET /saude` e `POST /responder`, com `contexto` opcional que orienta o LLM e nunca vira fonte.
- Variável do banco do RAG passa a ser `PANDORA_RAG_DB_URL`; `PANDORA_DB_URL` ainda vale, com aviso.
- `pandora-rag gerar-trilha`: gera as 6 lições com explicação citada e perguntas de múltipla escolha. Valida citações, números (no enunciado, na opção certa e no retorno) e fontes com aviso de vigência. A triagem manual (`scripts/triagem_trilha.py`) removeu 4 perguntas e editou 1, cada uma com motivo; conteúdo atual: validação `automatica+triagem`, 7 perguntas.
- API: `/chat` e `/trilha*` públicas, com detector de crise por expressões (paliativo até a #64).

## rag-v0.1.0 (2026-11-09)

- Corpus: 33 fontes oficiais, 1.183 chunks, versão `515669eb8f54`.
- Chunking estrutural com cabeçalho, bge-m3, pgvector HNSW, BM25 próprio, RRF e reranker bge-reranker-v2-m3.
- Portão de abstenção com limiar 0,02 (nota do reranker).
- LLM provisório: qwen2.5:14b, top-3.
- Golden set 169 + dev 51 gerados e validados automaticamente; revisão humana pendente.
- Ajuste fino do bge-m3 testado e não adotado.
- Qwen3-Embedding-4B e Qwen3-Reranker-4B testados e não adotados.
- Métricas de teste: citação 96%, abstenção 70%, p95 14,4 s (todas abaixo da meta). Ver [07](07-metricas-e-resultados.md).
