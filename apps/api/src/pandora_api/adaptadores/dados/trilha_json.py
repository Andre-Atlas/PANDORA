"""Lê o conteúdo da trilha gerado pelo RAG (`pandora-rag gerar-trilha`) e o valida na inicialização."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pandora_api.dominio.citacao import Citacao
from pandora_api.dominio.trilha import Etapa, Licao, Pergunta

CAMINHO_PADRAO = Path(__file__).resolve().parents[2] / "dados" / "trilha.v1.json"


class _Estrito(BaseModel):
    model_config = ConfigDict(extra="ignore")


class _Fonte(_Estrito):
    n: int
    norma: str
    artigo: str | None = None
    link: str
    trecho: str
    pagina: int | None = None
    ressalva: str | None = None


class _Pergunta(_Estrito):
    enunciado: str = Field(min_length=1)
    opcoes: list[str] = Field(min_length=2)
    certa: int
    feedback: str = Field(min_length=1)
    citacoes: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _certa_existe(self) -> _Pergunta:
        if not 0 <= self.certa < len(self.opcoes):
            raise ValueError("a opção certa precisa existir")
        return self


class _Licao(_Estrito):
    id: str
    titulo: str
    explicacao: str = Field(min_length=1)
    citacoes_explicacao: list[int] = Field(min_length=1)
    fontes: list[_Fonte] = Field(min_length=1)
    perguntas: list[_Pergunta] = Field(min_length=1)

    @model_validator(mode="after")
    def _citacoes_existem(self) -> _Licao:
        validas = {f.n for f in self.fontes}
        citadas = set(self.citacoes_explicacao) | {n for p in self.perguntas for n in p.citacoes}
        if not citadas <= validas:
            raise ValueError(f"citação sem fonte na lição {self.id}: {sorted(citadas - validas)}")
        return self


class _Etapa(_Estrito):
    id: str
    n: int
    t: str
    x: int
    lado: str
    marco: str | None = None
    emblema: str
    licao: _Licao


class _Documento(_Estrito):
    versao: str
    etapas: list[_Etapa] = Field(min_length=1)


def _etapa(e: _Etapa) -> Etapa:
    lc = e.licao
    licao = Licao(
        lc.id,
        lc.titulo,
        lc.explicacao,
        tuple(lc.citacoes_explicacao),
        tuple(Citacao(**f.model_dump()) for f in lc.fontes),
        tuple(Pergunta(p.enunciado, tuple(p.opcoes), p.certa, p.feedback, tuple(p.citacoes)) for p in lc.perguntas),
    )
    return Etapa(e.id, e.n, e.t, e.x, e.lado, e.marco, e.emblema, licao)


class TrilhaEmArquivo:
    def __init__(self, caminho: Path = CAMINHO_PADRAO) -> None:
        self._etapas = [
            _etapa(e) for e in _Documento.model_validate(json.loads(caminho.read_text(encoding="utf-8"))).etapas
        ]
        ids = [e.licao.id for e in self._etapas]
        if len(ids) != len(set(ids)):
            raise ValueError("ids de lição repetidos")

    def etapas(self) -> list[Etapa]:
        return list(self._etapas)
