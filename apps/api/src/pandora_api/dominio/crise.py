"""Detecção simples de sinais de crise, até o classificador da #64. Prefere errar para o lado da cautela."""

from __future__ import annotations

import re
import unicodedata

_PADROES = [
    r"\bquero morrer\b",
    r"\bvou me matar\b",
    r"\bme matar\b(?! de )",  # "me matar de juros" é figura de linguagem
    r"\bsuicid",
    r"\btirar (a )?minha vida\b",
    r"\bacabar com (a minha vida|tudo)\b",
    r"\bquero sumir\b",
    r"\bnao aguento mais viver\b",
    r"\bnao quero mais viver\b",
    r"\bdesistir de viver\b",
    r"\bmelhor (morto|morta|sem mim)\b",
    r"\bme machucar\b",
    r"\bautomutila",
    r"\bcortar (os )?pulsos\b",
]
_REGEX = re.compile("|".join(_PADROES))


def _normalizar(texto: str) -> str:
    sem_acento = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return " ".join(sem_acento.lower().split())


def detecta_crise(texto: str) -> bool:
    return bool(_REGEX.search(_normalizar(texto)))
