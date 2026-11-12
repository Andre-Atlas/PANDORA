from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Citacao:
    """Fonte oficial que sustenta uma afirmação. Mesmo formato da `Citacao` do RAG."""

    n: int
    norma: str
    artigo: str | None
    link: str
    trecho: str
    pagina: int | None = None
    ressalva: str | None = None
