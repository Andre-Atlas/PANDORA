"""Métricas de recuperação com relevância definida pelo texto do trecho-ouro.

Um chunk é relevante para um trecho-ouro quando é da mesma fonte e contém pelo menos
`LIMIAR` dos trigramas de palavras do trecho. Como o critério é textual, trocar a
estratégia de chunking não invalida o gabarito, e um artigo dividido em duas partes
ainda marca as duas como relevantes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from evals.metrics.textos import palavras

LIMIAR = 0.4


@dataclass(frozen=True)
class Ouro:
    fonte_id: str
    trecho: str
    artigo: str | None = None


def trigramas(texto: str) -> set[tuple[str, ...]]:
    p = palavras(texto)
    if len(p) < 3:
        return {tuple(p)} if p else set()
    return {tuple(p[i : i + 3]) for i in range(len(p) - 2)}


def cobertura(trecho_ouro: str, chunk: str) -> float:
    alvo = trigramas(trecho_ouro)
    return len(alvo & trigramas(chunk)) / len(alvo) if alvo else 0.0


def cobre(chunk_fonte: str, chunk_texto: str, ouro: Ouro, limiar: float = LIMIAR) -> bool:
    return chunk_fonte == ouro.fonte_id and cobertura(ouro.trecho, chunk_texto) >= limiar


def _primeiros_acertos(recuperados: list[tuple[str, str]], ouros: list[Ouro], limiar: float) -> list[int | None]:
    """Para cada posição, o índice do ouro que ela cobre pela primeira vez (ou None)."""
    cobertos: set[int] = set()
    saida: list[int | None] = []
    for fonte, texto in recuperados:
        novo = None
        for j, o in enumerate(ouros):
            if j not in cobertos and cobre(fonte, texto, o, limiar):
                novo = j
                cobertos.add(j)
                break
        saida.append(novo)
    return saida


def avaliar(recuperados: list[tuple[str, str]], ouros: list[Ouro], ks=(1, 3, 5, 10), limiar: float = LIMIAR) -> dict[str, float]:
    """`recuperados`: lista ordenada de (fonte_id, texto). Devolve recall/precision/hit@k, MRR e nDCG@10."""
    if not ouros:
        raise ValueError("pergunta sem trecho-ouro: use as métricas de abstenção")
    novos = _primeiros_acertos(recuperados, ouros, limiar)
    relevante = [any(cobre(f, t, o, limiar) for o in ouros) for f, t in recuperados]
    saida: dict[str, float] = {}
    for k in ks:
        saida[f"recall@{k}"] = len({j for j in novos[:k] if j is not None}) / len(ouros)
        topo = relevante[:k]
        saida[f"precision@{k}"] = sum(topo) / k
        saida[f"hit@{k}"] = float(any(topo))
    saida["mrr"] = next((1 / (i + 1) for i, r in enumerate(relevante) if r), 0.0)
    dcg = sum(1 / math.log2(i + 2) for i, j in enumerate(novos[:10]) if j is not None)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(10, len(ouros))))
    saida["ndcg@10"] = dcg / ideal
    return saida


def acerto_artigo(recuperados: list[tuple[str, str | None]], ouros: list[Ouro], k: int = 3) -> float:
    """1 se o artigo-ouro (fonte + rótulo) aparece nos k primeiros, ignorando partes de artigo longo."""
    alvo = {(o.fonte_id, o.artigo) for o in ouros if o.artigo}
    if not alvo:
        return float("nan")
    return float(any((f, a) in alvo for f, a in recuperados[:k]))


def media(linhas: list[dict[str, float]]) -> dict[str, float]:
    chaves = linhas[0].keys()
    return {c: sum(l[c] for l in linhas) / len(linhas) for c in chaves}
