from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime

_N, _R, _P, _TAMANHO = 2**14, 8, 1, 32


def _b64(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).decode().rstrip("=")


def _de_b64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


class HasherScrypt:
    """scrypt da biblioteca padrão. Formato: scrypt$n$r$p$sal$hash."""

    def gerar(self, senha: str) -> str:
        sal = secrets.token_bytes(16)
        derivado = hashlib.scrypt(senha.encode(), salt=sal, n=_N, r=_R, p=_P, dklen=_TAMANHO)
        return f"scrypt${_N}${_R}${_P}${_b64(sal)}${_b64(derivado)}"

    def conferir(self, senha: str, senha_hash: str) -> bool:
        try:
            nome, n, r, p, sal, esperado = senha_hash.split("$")
            if nome != "scrypt":
                return False
            derivado = hashlib.scrypt(
                senha.encode(), salt=_de_b64(sal), n=int(n), r=int(r), p=int(p), dklen=len(_de_b64(esperado))
            )
        except ValueError:
            return False
        return hmac.compare_digest(derivado, _de_b64(esperado))


class RelogioDoSistema:
    def agora(self) -> datetime:
        return datetime.now(UTC)
