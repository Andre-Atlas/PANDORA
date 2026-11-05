"""Embeddings locais com sentence-transformers.

A família E5 exige os prefixos `query: ` e `passage: `. Os vetores saem normalizados, então
o produto escalar é o cosseno.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence

import numpy as np

logger = logging.getLogger("pandora.embedder")


def prefixos(modelo: str) -> tuple[str, str]:
    return ("query: ", "passage: ") if "e5" in modelo.lower() else ("", "")


class Embedder:
    def __init__(self, modelo: str, max_seq_length: int = 512, batch_size: int = 16, caminho: str | None = None):
        from sentence_transformers import SentenceTransformer

        self.modelo = modelo
        self.batch_size = batch_size
        self._modelo = SentenceTransformer(caminho or modelo)
        if str(getattr(self._modelo, "device", "")).startswith("mps"):
            try:
                self._modelo.encode(["teste"], show_progress_bar=False)
            except Exception:  # noqa: BLE001 - MPS indisponível em alguns ambientes
                logger.info("MPS indisponível; usando CPU")
                self._modelo = self._modelo.to("cpu")
        maximo = self._modelo[0].auto_model.config.max_position_embeddings
        self._modelo.max_seq_length = min(max_seq_length, maximo)
        self._q, self._p = prefixos(modelo)
        self.dim = int(self._modelo.get_sentence_embedding_dimension())

    def _codificar(self, textos: Sequence[str], prefixo: str) -> np.ndarray:
        vetores = self._modelo.encode(
            [prefixo + t for t in textos],
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(textos) > 64,
            convert_to_numpy=True,
        )
        return np.asarray(vetores, dtype=np.float32)

    def passagens(self, textos: Sequence[str]) -> np.ndarray:
        return self._codificar(textos, self._p)

    def consultas(self, textos: Sequence[str]) -> np.ndarray:
        return self._codificar(textos, self._q)
