"""Montagem dos componentes do RAG, compartilhada pela CLI e pelo serviço HTTP."""
from __future__ import annotations

MODELO_EMBEDDING = "BAAI/bge-m3"
LLM_PADRAO = "qwen25-14b"


def montar_retriever(modelo: str = MODELO_EMBEDDING, tabela: str = "chunks", rerank: bool = True):
    """Carrega embedder, índice vetorial, BM25 e reranker. É a parte lenta: faça uma vez só."""
    from pandora_rag.config import DB_URL
    from pandora_rag.index.embedder import Embedder
    from pandora_rag.index.store import PgVectorStore
    from pandora_rag.retrieve.hybrid import IndiceBM25, Reranker, Retriever

    emb = Embedder(modelo)
    pg = PgVectorStore(DB_URL, tabela, emb.dim)
    regs = pg.carregar_registros()
    return Retriever(pg, IndiceBM25(regs), emb, Reranker() if rerank else None)


def montar_gateway():
    from pandora_rag.generate.gateway import Gateway

    return Gateway()
