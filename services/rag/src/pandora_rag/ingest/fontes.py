"""Leitura e validação do manifesto de fontes."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from pandora_rag.config import FONTES_PATH

CamadaDominio = Literal[
    "educacao_orcamento",
    "comportamental_vieses",
    "juridico_superendividamento",
    "regulatorio_bancario",
    "defesa_bens_servicos",
]


class Fonte(BaseModel):
    id: str
    titulo: str
    orgao: str
    tipo: Literal["lei", "decreto", "resolucao", "sumula", "jurisprudencia", "cartilha", "estudo"]
    formato: Literal["html", "pdf", "bcb_api"]
    url: str
    url_citacao: str | None = None
    camada_dominio: CamadaDominio
    modalidade_divida: str = "geral"
    elegivel_lei_14181: bool | None = None
    nivel_urgencia: str = "moderado_reorganizacao"
    data_referencia_normativa: str
    itens: list[str] | None = None  # restringe a ingestão a estes artigos (ou súmulas)
    norma_alvo: str | None = None  # norma alterada, para artigos entre aspas em leis alteradoras
    ressalva: str | None = None  # nota de vigência exibida junto do trecho
    recorte_inicio: str | None = None  # páginas de notícia: começa no bloco com este texto
    recorte_fim: str | None = None  # e termina antes do bloco com este texto

    @property
    def link(self) -> str:
        return self.url_citacao or self.url


def carregar_fontes(caminho: Path = FONTES_PATH) -> list[Fonte]:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    fontes = [Fonte(**item) for item in dados["fontes"]]
    ids = [f.id for f in fontes]
    if len(ids) != len(set(ids)):
        raise ValueError("fontes.yaml tem ids repetidos")
    return fontes
