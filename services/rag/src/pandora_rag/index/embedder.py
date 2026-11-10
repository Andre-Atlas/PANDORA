"""Embeddings locais com sentence-transformers.

A família E5 exige os prefixos `query: ` e `passage: `. Os vetores saem normalizados, então
o produto escalar é o cosseno.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence

import numpy as np

logger = logging.getLogger("pandora.embedder")


INSTRUCAO_QWEN3 = "Dada uma pergunta de um consumidor sobre dívidas, crédito ou seus direitos, recupere o trecho de norma ou cartilha que a responde"


def prefixos(modelo: str) -> tuple[str, str]:
    m = modelo.lower()
    if "e5" in m:
        return "query: ", "passage: "
    if "qwen3-embedding" in m:
        return f"Instruct: {INSTRUCAO_QWEN3}\nQuery: ", ""
    return "", ""


class Embedder:
    def __init__(self, modelo: str, max_seq_length: int = 512, batch_size: int = 16, caminho: str | None = None,
                 dim: int | None = None):
        from sentence_transformers import SentenceTransformer

        self.modelo = modelo
        self.batch_size = batch_size
        qwen = "qwen3-embedding" in modelo.lower()
        if qwen:  # 4B em float16 (~8 GB), padding à esquerda como o modelo exige; vetor cortado por Matryoshka
            import torch

            self._modelo = SentenceTransformer(caminho or modelo, model_kwargs={"torch_dtype": torch.float16},
                                               tokenizer_kwargs={"padding_side": "left"})
            max_seq_length, self.batch_size, dim = max(max_seq_length, 768), 4, dim or 1024
        else:
            self._modelo = SentenceTransformer(caminho or modelo)
        self._dim_saida = dim
        if str(getattr(self._modelo, "device", "")).startswith("mps"):
            try:
                self._modelo.encode(["teste"], show_progress_bar=False)
            except Exception:  # noqa: BLE001 - MPS indisponível em alguns ambientes
                logger.info("MPS indisponível; usando CPU")
                self._modelo = self._modelo.to("cpu")
        maximo = self._modelo[0].auto_model.config.max_position_embeddings
        self._modelo.max_seq_length = min(max_seq_length, maximo)
        self._q, self._p = prefixos(modelo)
        self.dim = self._dim_saida or int(self._modelo.get_sentence_embedding_dimension())

    def _codificar(self, textos: Sequence[str], prefixo: str) -> np.ndarray:
        vetores = self._modelo.encode(
            [prefixo + t for t in textos],
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(textos) > 64,
            convert_to_numpy=True,
        )
        vetores = np.asarray(vetores, dtype=np.float32)
        if self._dim_saida and vetores.shape[1] > self._dim_saida:
            vetores = vetores[:, : self._dim_saida]
            vetores /= np.linalg.norm(vetores, axis=1, keepdims=True)
        return vetores

    def passagens(self, textos: Sequence[str]) -> np.ndarray:
        return self._codificar(textos, self._p)

    def consultas(self, textos: Sequence[str]) -> np.ndarray:
        return self._codificar(textos, self._q)
