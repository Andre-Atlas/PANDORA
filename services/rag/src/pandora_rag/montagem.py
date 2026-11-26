"""Montagem dos componentes do RAG, compartilhada pela CLI e pelo serviço HTTP."""
from __future__ import annotations

MODELO_EMBEDDING = "BAAI/bge-m3"
LLM_PADRAO = "qwen25-14b"


def montar_retriever(modelo: str = MODELO_EMBEDDING, tabela: str = "chunks", rerank: bool = True, reaproveitar=None):
    """Carrega embedder, índice vetorial, BM25 e reranker. É a parte lenta: faça uma vez só.

    Com `reaproveitar` (um Retriever já montado), recarrega só o índice (registros, pgvector e BM25)
    e mantém os modelos na memória: é o que o /recarregar usa depois de uma reindexação.
    """
    from pandora_rag.config import DB_URL
    from pandora_rag.index.embedder import Embedder
    from pandora_rag.index.store import PgVectorStore
    from pandora_rag.retrieve.hybrid import IndiceBM25, Reranker, Retriever

    if reaproveitar is not None:
        emb, rr = reaproveitar.embedder, reaproveitar.reranker
    else:
        emb, rr = Embedder(modelo), (Reranker() if rerank else None)
    pg = PgVectorStore(DB_URL, tabela, emb.dim)
    regs = pg.carregar_registros()
    return Retriever(pg, IndiceBM25(regs), emb, rr)


def recarregar_retriever(antigo):
    """Monta um retriever novo sobre a tabela atual, reaproveitando os modelos do antigo."""
    novo = montar_retriever(tabela=getattr(antigo.store, "tabela", "chunks"), reaproveitar=antigo)
    conn = getattr(antigo.store, "conn", None)
    if conn is not None:
        conn.close()
    return novo


def montar_gateway():
    from pandora_rag.generate.gateway import Gateway

    return Gateway()
