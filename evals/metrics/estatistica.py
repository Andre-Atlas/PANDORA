"""Incerteza e comparação pareada: bootstrap percentil e McNemar exato."""
from __future__ import annotations

import numpy as np


def ic_bootstrap(valores, n: int = 2000, alfa: float = 0.05, semente: int = 7) -> tuple[float, float, float]:
    """Média e intervalo de confiança (percentil) por bootstrap."""
    v = np.asarray(valores, dtype=float)
    v = v[~np.isnan(v)]
    rng = np.random.default_rng(semente)
    medias = rng.choice(v, size=(n, len(v)), replace=True).mean(axis=1)
    return float(v.mean()), float(np.quantile(medias, alfa / 2)), float(np.quantile(medias, 1 - alfa / 2))


def ic_diferenca_pareada(a, b, n: int = 2000, alfa: float = 0.05, semente: int = 7) -> tuple[float, float, float]:
    """Diferença média (a - b) por pergunta, com IC bootstrap sobre os pares."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    return ic_bootstrap(d, n, alfa, semente)


def mcnemar_exato(a_acerta, b_acerta) -> float:
    """p-valor bicaudal do teste de McNemar exato para dois sistemas avaliados nas mesmas perguntas."""
    from scipy.stats import binomtest

    a, b = np.asarray(a_acerta, dtype=bool), np.asarray(b_acerta, dtype=bool)
    so_a, so_b = int((a & ~b).sum()), int((~a & b).sum())
    if so_a + so_b == 0:
        return 1.0
    return float(binomtest(so_a, so_a + so_b, 0.5).pvalue)
