from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

TAMANHO_MINIMO_SENHA = 8


@dataclass(frozen=True)
class Usuario:
    id: UUID
    email: str
    senha_hash: str
    criado_em: datetime


@dataclass(frozen=True)
class Sessao:
    """Sessão por token opaco. Só o hash do token é guardado."""

    token_hash: str
    usuario_id: UUID
    criada_em: datetime
    expira_em: datetime

    def valida_em(self, agora: datetime) -> bool:
        return agora < self.expira_em


def normalizar_email(email: str) -> str:
    return email.strip().lower()
