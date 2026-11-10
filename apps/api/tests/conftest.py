from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from pandora_api.adaptadores.http.app import criar_app
from pandora_api.adaptadores.http.conteiner import Conteiner, montar
from pandora_api.adaptadores.persistencia.memoria import (
    ConsentimentosEmMemoria,
    SessoesEmMemoria,
    UsuariosEmMemoria,
)
from pandora_api.adaptadores.seguranca.scrypt import HasherScrypt


class RelogioParado:
    def __init__(self) -> None:
        self.momento = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)

    def agora(self) -> datetime:
        return self.momento

    def avancar(self, **delta) -> None:
        self.momento += timedelta(**delta)


@pytest.fixture
def relogio() -> RelogioParado:
    return RelogioParado()


@pytest.fixture
def repos():
    return UsuariosEmMemoria(), SessoesEmMemoria(), ConsentimentosEmMemoria()


@pytest.fixture
def conteiner(repos, relogio) -> Conteiner:
    usuarios, sessoes, consentimentos = repos
    return montar(usuarios, sessoes, consentimentos, HasherScrypt(), relogio, timedelta(hours=24))


@pytest.fixture
def cliente(conteiner) -> TestClient:
    return TestClient(criar_app(conteiner))


@pytest.fixture
def autenticado(cliente) -> TestClient:
    """Cliente com conta criada e token no cabeçalho."""
    cliente.post("/auth/cadastro", json={"email": "carla@exemplo.com", "senha": "senha-forte-1"})
    token = cliente.post("/auth/sessoes", json={"email": "carla@exemplo.com", "senha": "senha-forte-1"}).json()["token"]
    cliente.headers["Authorization"] = f"Bearer {token}"
    return cliente
