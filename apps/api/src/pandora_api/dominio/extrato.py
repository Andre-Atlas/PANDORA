"""Extrato ou fatura enviado pela pessoa (RF01)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID

TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024
"""5 MB: um extrato de um ano em CSV tem poucas centenas de KB."""


class StatusExtrato(StrEnum):
    RECEBIDO = "recebido"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    FALHOU = "falhou"


@dataclass(frozen=True)
class Extrato:
    id: UUID
    usuario_id: UUID
    nome_arquivo: str
    status: StatusExtrato
    recebido_em: datetime
    transacoes_importadas: int | None = None
    avisos: tuple[str, ...] = field(default_factory=tuple)

    def concluir(self, importadas: int, avisos: tuple[str, ...]) -> Extrato:
        return replace(self, status=StatusExtrato.CONCLUIDO, transacoes_importadas=importadas, avisos=avisos)

    def falhar(self, avisos: tuple[str, ...]) -> Extrato:
        return replace(self, status=StatusExtrato.FALHOU, transacoes_importadas=0, avisos=avisos)
