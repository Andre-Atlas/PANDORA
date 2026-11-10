from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Finalidade(StrEnum):
    """Para que a pessoa autoriza o uso dos dados (LGPD, art. 7º, I)."""

    DIAGNOSTICO_FINANCEIRO = "diagnostico_financeiro"
    """Ler extratos e faturas para montar o Raio-X. Exigido antes de qualquer upload."""


@dataclass(frozen=True)
class Consentimento:
    id: UUID
    usuario_id: UUID
    finalidade: Finalidade
    versao_termo: str
    aceito_em: datetime
    revogado_em: datetime | None = None

    @property
    def ativo(self) -> bool:
        return self.revogado_em is None

    def revogar(self, quando: datetime) -> Consentimento:
        return self if not self.ativo else replace(self, revogado_em=quando)
