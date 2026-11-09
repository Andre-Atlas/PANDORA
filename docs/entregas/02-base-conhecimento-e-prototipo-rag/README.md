# Entregável: Base de Conhecimento + Protótipo de RAG

**Segundo Desafio · RES IA ELD UNB · Turma 2 · PANDORA**
Foco desta etapa: qualidade da recuperação, fundamentação das respostas e rastreabilidade das fontes. A interface não faz parte do escopo.

## Checklist do entregável

| Requisito | Onde está |
|---|---|
| Base de conhecimento curada | [01-base-de-conhecimento.md](01-base-de-conhecimento.md) e `base_de_conhecimento/chunks.jsonl` (zip) |
| Mínimo de 20 documentos-fonte | **33 fontes oficiais**, lista em [fontes.md](fontes.md) |
| Estratégia de chunking | [02-estrategia-de-chunking.md](02-estrategia-de-chunking.md) |
| Estratégia de embeddings | [03-estrategia-de-embeddings.md](03-estrategia-de-embeddings.md) |
| Banco vetorial implementado | [04-banco-vetorial.md](04-banco-vetorial.md): PostgreSQL + pgvector (HNSW), 1.183 chunks |
| Consulta, recuperação, resposta e fontes (demonstração) | [06-demonstracao.md](06-demonstracao.md) e [demo/](demo/) |
| Diagrama de arquitetura | [05-arquitetura-e-pipeline.md](05-arquitetura-e-pipeline.md), imagem em [diagramas/arquitetura.png](diagramas/arquitetura.png) |
| Pipeline de ingestão | [05-arquitetura-e-pipeline.md](05-arquitetura-e-pipeline.md), imagem em [diagramas/pipeline-ingestao.png](diagramas/pipeline-ingestao.png) |
| Qualidade e limitações (extra) | [07-qualidade-e-limitacoes.md](07-qualidade-e-limitacoes.md) |

## Em uma frase

Pergunta → busca híbrida (vetorial bge-m3 no pgvector + BM25) → fusão RRF → reranker → portão de abstenção → LLM local que só pode usar os trechos recuperados → resposta com `[n]` e lista de fontes com link oficial.

## Como reproduzir

Pré-requisitos: Docker, [uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.com) com `qwen2.5:14b`.

```bash
cd services/rag
docker compose up -d                      # PostgreSQL + pgvector na porta 5433
uv run pandora-rag coletar                # baixa as 33 fontes e grava os hashes
uv run pandora-rag extrair                # HTML/PDF para texto
uv run pandora-rag indexar                # chunking, embeddings e carga no banco
uv run pandora-rag ask "Existe limite de juros no rotativo do cartão?"
```

O comando `ask` usa por padrão o modelo local `qwen25-14b`, sem chave de API.

## Estado e limitações

A versão é a base do RAG. Citação (96%), abstenção (70%) e latência p95 (14,4 s) ainda ficam abaixo das metas do escopo, a revisão humana do golden set está pendente e Ragas não foi medido. Os detalhes e dois exemplos de falha estão em [07](07-qualidade-e-limitacoes.md) e [06](06-demonstracao.md).

## Mapa do repositório

| Pasta | Conteúdo |
|---|---|
| `services/rag/` | Código do RAG (`src/pandora_rag`), testes, `fontes.yaml`, `corpus.lock`, `docker-compose.yml` |
| `evals/` | Golden set, métricas e registro das rodadas |
| `training/` | Treino sintético, ajuste fino e limiar de abstenção |
| `docs/rag/` | Documentação técnica completa (arquitetura, métricas, decisão do LLM) |
