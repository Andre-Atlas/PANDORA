from __future__ import annotations

from datetime import datetime
from typing import Protocol


class HasherSenha(Protocol):
    def gerar(self, senha: str) -> str: ...
    def conferir(self, senha: str, senha_hash: str) -> bool: ...


class Relogio(Protocol):
    def agora(self) -> datetime: ...
