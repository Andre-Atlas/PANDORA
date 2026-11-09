"""Monta o índice: registros, embeddings (com cache por conteúdo) e BM25."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from pandora_rag.config import DATA_DIR
from pandora_rag.index.embedder import Embedder
from pandora_rag.index.registro import Registro, montar_registros
from pandora_rag.index.store import MemoryStore
from pandora_rag.retrieve.hybrid import IndiceBM25

CACHE = DATA_DIR / "embeddings"


def embeddings(registros: list[Registro], embedder: Embedder, com_cabecalho: bool = True) -> np.ndarray:
    textos = [r.texto_indexado(com_cabecalho) for r in registros]
    chave = hashlib.sha256((embedder.modelo + "|" + "\x00".join(textos)).encode()).hexdigest()[:20]
    arq = CACHE / f"{embedder.modelo.replace('/', '_')}-{chave}.npy"
    if arq.exists():
        return np.load(arq)
    vetores = embedder.passagens(textos)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(arq, vetores)
    return vetores


def construir(estrategia: str, modelo: str, com_cabecalho: bool = True, k1: float = 1.5, b: float = 0.75,
              registros: list[Registro] | None = None, embedder: Embedder | None = None):
    registros = registros if registros is not None else montar_registros(estrategia)
    embedder = embedder or Embedder(modelo)
    store = MemoryStore(registros, embeddings(registros, embedder, com_cabecalho))
    return store, IndiceBM25(registros, k1=k1, b=b, com_cabecalho=com_cabecalho), embedder
