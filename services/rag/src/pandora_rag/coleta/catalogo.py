"""Modelo e leitura do inventário das 31 fontes do catálogo (seção `catalogo` de fontes.yaml)."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, model_validator

from pandora_rag.config import FONTES_PATH

Formato = Literal["html", "pdf", "api"]
Frequencia = Literal["diaria", "mensal", "trimestral", "semestral", "anual", "eventual", "estatica"]
TOTAL_ITENS = 31


class Alvo(BaseModel):
    """Um arquivo ou endpoint concreto dentro de um item do catálogo."""

    id: str
    url: str | None = None
    formato: Formato | None = None
    ext: str | None = None  # força a extensão do bruto (csv, zip); padrão por formato
    fonte_id: str | None = None  # id em `fontes` quando o alvo também alimenta o corpus do RAG
    manual: str | None = None  # motivo do tratamento manual; sem isso o alvo é automático
    obs: str | None = None

    @model_validator(mode="after")
    def _coerente(self) -> "Alvo":
        if not self.manual and not (self.url and self.formato):
            raise ValueError(f"alvo {self.id}: automático exige url e formato")
        return self


class ItemCatalogo(BaseModel):
    numero: int
    nome: str
    grupo: int
    orgao: str
    frequencia: Frequencia
    alvos: list[Alvo]

    @property
    def formatos(self) -> list[str]:
        return sorted({a.formato for a in self.alvos if a.formato} or {"manual"})


def carregar_catalogo(caminho: Path = FONTES_PATH) -> list[ItemCatalogo]:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    itens = [ItemCatalogo(**i) for i in dados["catalogo"]]
    numeros = [i.numero for i in itens]
    if sorted(numeros) != list(range(1, TOTAL_ITENS + 1)):
        raise ValueError(f"o catálogo deve ter os itens 1 a {TOTAL_ITENS}, sem repetição")
    ids = [a.id for i in itens for a in i.alvos]
    if len(ids) != len(set(ids)):
        raise ValueError("catálogo com ids de alvo repetidos")
    return sorted(itens, key=lambda i: i.numero)
