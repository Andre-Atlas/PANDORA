"""Máscara de dados pessoais antes de qualquer chamada a modelo externo (RNF01)."""
from __future__ import annotations

import re

PADROES: list[tuple[str, re.Pattern]] = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("CNPJ", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("CPF", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("CARTAO", re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")),
    ("TELEFONE", re.compile(r"(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}(?!\d)")),
]


def mascarar(texto: str) -> tuple[str, dict[str, int]]:
    """Devolve o texto mascarado e a contagem por tipo."""
    contagem: dict[str, int] = {}
    for nome, padrao in PADROES:
        texto, n = padrao.subn(f"[{nome}]", texto)
        if n:
            contagem[nome] = n
    return texto, contagem
