"""Busca híbrida: vetorial + BM25, fusão por RRF ponderado e reranking opcional."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import bm25s
import numpy as np

from pandora_rag.index.registro import Registro
from pandora_rag.index.store import Store, mascara
from pandora_rag.index.tokenizer import tokenizar


@dataclass
class Hit:
    registro: Registro
    score: float
    score_vetor: float | None = None
    score_bm25: float | None = None
    score_rerank: float | None = None
    rank_vetor: int | None = None
    rank_bm25: int | None = None
    sinais: dict = field(default_factory=dict)


@dataclass
class Parametros:
    k_vetor: int = 50
    k_bm25: int = 50
    rrf_k: int = 60
    peso_vetor: float = 1.0
    peso_bm25: float = 1.0
    k_rerank: int = 30
    usar_vetor: bool = True
    usar_bm25: bool = True


class IndiceBM25:
    def __init__(self, registros: list[Registro], k1: float = 1.5, b: float = 0.75, com_cabecalho: bool = True):
        self.k1, self.b = k1, b
        corpo = [tokenizar(r.texto_indexado(com_cabecalho)) for r in registros]
        self.bm25 = bm25s.BM25(k1=k1, b=b)
        self.bm25.index(corpo, show_progress=False)
        self.n = len(registros)

    def pontuar(self, pergunta: str) -> np.ndarray:
        tokens = [t for t in tokenizar(pergunta) if t in self.bm25.vocab_dict]
        if not tokens:
            return np.zeros(self.n, dtype=np.float32)
        return np.asarray(self.bm25.get_scores(tokens), dtype=np.float32)


def rrf(rankings: list[tuple[list[int], float]], k: int) -> dict[int, float]:
    fundido: dict[int, float] = {}
    for ordem, peso in rankings:
        for pos, idx in enumerate(ordem, start=1):
            fundido[idx] = fundido.get(idx, 0.0) + peso / (k + pos)
    return fundido


class Retriever:
    def __init__(self, store: Store, bm25: IndiceBM25, embedder, reranker=None, params: Parametros | None = None, com_cabecalho_rerank: bool = True):
        self.store, self.bm25, self.embedder, self.reranker = store, bm25, embedder, reranker
        self.params = params or Parametros()
        self.com_cabecalho_rerank = com_cabecalho_rerank

    @property
    def registros(self) -> list[Registro]:
        return self.store.registros

    def buscar(self, pergunta: str, k: int = 5, filtro: dict[str, Any] | None = None, params: Parametros | None = None) -> list[Hit]:
        p = params or self.params
        regs = self.registros
        rankings: list[tuple[list[int], float]] = []
        sv: dict[int, float] = {}
        sb: dict[int, float] = {}
        rv: dict[int, int] = {}
        rb: dict[int, int] = {}
        if p.usar_vetor:
            consulta = self.embedder.consultas([pergunta])[0]
            achados = self.store.buscar_vetor(consulta, p.k_vetor, filtro)
            sv = dict(achados)
            ordem = [i for i, _ in achados]
            rv = {i: n for n, i in enumerate(ordem, start=1)}
            rankings.append((ordem, p.peso_vetor))
        if p.usar_bm25:
            scores = self.bm25.pontuar(pergunta)
            scores = np.where(mascara(regs, filtro), scores, -np.inf)
            ordem = [int(i) for i in np.argsort(-scores)[: p.k_bm25] if scores[i] > 0]
            sb = {i: float(scores[i]) for i in ordem}
            rb = {i: n for n, i in enumerate(ordem, start=1)}
            rankings.append((ordem, p.peso_bm25))
        fundido = rrf(rankings, p.rrf_k)
        candidatos = sorted(fundido, key=fundido.get, reverse=True)
        topo = candidatos[: max(k, p.k_rerank) if self.reranker else k]
        hits = [
            Hit(regs[i], fundido[i], sv.get(i), sb.get(i), None, rv.get(i), rb.get(i))
            for i in topo
        ]
        if self.reranker and hits:
            notas = self.reranker.pontuar(pergunta, [h.registro.texto_indexado(self.com_cabecalho_rerank) for h in hits])
            for h, n in zip(hits, notas):
                h.score_rerank = float(n)
                h.score = float(n)
            hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]


class Reranker:
    def __init__(self, modelo: str = "BAAI/bge-reranker-v2-m3", max_length: int = 512, batch_size: int = 8):
        from sentence_transformers import CrossEncoder

        self.modelo, self.batch_size = modelo, batch_size
        self._ce = CrossEncoder(modelo, max_length=max_length)

    def pontuar(self, pergunta: str, textos: list[str]) -> list[float]:
        return [float(x) for x in self._ce.predict([(pergunta, t) for t in textos], batch_size=self.batch_size, show_progress_bar=False)]
