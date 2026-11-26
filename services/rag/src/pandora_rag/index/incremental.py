"""Reindexação incremental: só as fontes cujo conteúdo ou metadado mudou são re-embedadas.

A assinatura de uma fonte é o hash dos registros dela sem `versao_corpus`. Ela é calculada do mesmo
jeito para o que está no banco e para o que sai de `montar_registros`, então não depende de nenhum
arquivo de estado à parte: a própria tabela diz o que já está indexado.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from pandora_rag.index.registro import Registro, versao_do_corpus


class StoreIncremental(Protocol):
    def carregar_registros(self) -> list[Registro]: ...
    def apagar_fontes(self, fonte_ids: list[str]) -> int: ...
    def inserir(self, registros: list[Registro], vetores: np.ndarray) -> None: ...
    def definir_versao(self, versao: str) -> None: ...


@dataclass
class Relatorio:
    novas: list[str] = field(default_factory=list)
    alteradas: list[str] = field(default_factory=list)
    removidas: list[str] = field(default_factory=list)
    iguais: list[str] = field(default_factory=list)
    trechos_embedados: int = 0
    versao_antes: str | None = None
    versao_depois: str | None = None
    total: int = 0

    @property
    def mudou(self) -> bool:
        return bool(self.novas or self.alteradas or self.removidas)

    def resumo(self) -> str:
        return (f"novas={len(self.novas)} alteradas={len(self.alteradas)} removidas={len(self.removidas)} "
                f"iguais={len(self.iguais)} embedados={self.trechos_embedados} total={self.total} "
                f"corpus {self.versao_antes} -> {self.versao_depois}")


def assinatura(registros: list[Registro]) -> str:
    linhas = sorted(r.model_dump_json(exclude={"versao_corpus"}) for r in registros)
    return hashlib.sha256("\n".join(linhas).encode("utf-8")).hexdigest()


def _por_fonte(registros: list[Registro]) -> dict[str, list[Registro]]:
    grupos: dict[str, list[Registro]] = defaultdict(list)
    for r in registros:
        grupos[r.fonte_id].append(r)
    return grupos


def atualizar(store: StoreIncremental, novos: list[Registro], embedar, remover_ausentes: bool = True) -> Relatorio:
    """Leva `store` ao estado de `novos`. `embedar(registros) -> np.ndarray` só é chamado para fontes mudadas."""
    atuais = store.carregar_registros()
    rel = Relatorio(versao_antes=atuais[0].versao_corpus if atuais else None)
    antes, depois = _por_fonte(atuais), _por_fonte(novos)
    for fonte_id, regs in depois.items():
        if fonte_id not in antes:
            rel.novas.append(fonte_id)
        elif assinatura(antes[fonte_id]) != assinatura(regs):
            rel.alteradas.append(fonte_id)
        else:
            rel.iguais.append(fonte_id)
    if remover_ausentes:
        rel.removidas = sorted(set(antes) - set(depois))
    trocar = rel.novas + rel.alteradas
    store.apagar_fontes(rel.alteradas + rel.removidas)
    para_embedar = [r for f in trocar for r in depois[f]]
    if para_embedar:
        store.inserir(para_embedar, embedar(para_embedar))
    rel.trechos_embedados = len(para_embedar)
    finais = [r for f, regs in depois.items() for r in regs]
    if not remover_ausentes:
        finais += [r for f, regs in antes.items() if f not in depois for r in regs]
    rel.versao_depois = versao_do_corpus([r.hash for r in finais])
    rel.total = len(finais)
    if rel.mudou or rel.versao_antes != rel.versao_depois:
        store.definir_versao(rel.versao_depois)
    return rel


class MemoriaIncremental:
    """Store em memória com a mesma interface, para testes e ensaios sem Postgres."""

    def __init__(self, registros: list[Registro] | None = None, vetores: np.ndarray | None = None):
        self.linhas: dict[str, tuple[Registro, np.ndarray]] = {}
        if registros:
            vetores = vetores if vetores is not None else np.zeros((len(registros), 1), dtype=np.float32)
            for r, v in zip(registros, vetores):
                self.linhas[r.id] = (r, v)

    def carregar_registros(self) -> list[Registro]:
        return [r for r, _ in self.linhas.values()]

    def apagar_fontes(self, fonte_ids: list[str]) -> int:
        alvo = [k for k, (r, _) in self.linhas.items() if r.fonte_id in set(fonte_ids)]
        for k in alvo:
            del self.linhas[k]
        return len(alvo)

    def inserir(self, registros: list[Registro], vetores: np.ndarray) -> None:
        for r, v in zip(registros, vetores):
            self.linhas[r.id] = (r.model_copy(), v)

    def definir_versao(self, versao: str) -> None:
        for r, _ in self.linhas.values():
            r.versao_corpus = versao
