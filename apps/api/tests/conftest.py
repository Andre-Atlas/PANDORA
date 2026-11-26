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
from pandora_api.dominio.citacao import Citacao
from pandora_api.dominio.erros import AssistenteIndisponivel
from pandora_api.dominio.trilha import Etapa, Licao, Pergunta
from pandora_api.portas.assistente import RespostaElpis


class RelogioParado:
    def __init__(self) -> None:
        self.momento = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)

    def agora(self) -> datetime:
        return self.momento

    def avancar(self, **delta) -> None:
        self.momento += timedelta(**delta)


FONTE = Citacao(
    1, "Lei 14.181/2021", "Art. 104-A", "https://www.planalto.gov.br/x", "O plano pode durar até cinco anos."
)


class AssistenteFalso:
    """Registra as chamadas e devolve a resposta combinada, ou falha como o serviço fora do ar."""

    def __init__(self) -> None:
        self.chamadas: list[tuple[str, str | None]] = []
        self.resposta = RespostaElpis("O plano dura até cinco anos [1].", False, "falso", (FONTE,))
        self.indisponivel = False

    def responder(self, pergunta: str, contexto: str | None = None) -> RespostaElpis:
        self.chamadas.append((pergunta, contexto))
        if self.indisponivel:
            raise AssistenteIndisponivel("fora do ar")
        return self.resposta


class TrilhaFalsa:
    def etapas(self) -> list[Etapa]:
        perguntas = (
            Pergunta(
                "Qual o prazo máximo do plano de pagamento?",
                ("Cinco anos", "Um ano", "Sem prazo"),
                0,
                "Até cinco anos [1].",
                (1,),
            ),
        )
        licao = Licao("rotativo", "Rotativo", "Explicação do rotativo [1].", (1,), (FONTE,), perguntas)
        return [Etapa("rotativo", 3, "Rotativo", 288, "e", None, "espiral", licao)]


@pytest.fixture
def assistente() -> AssistenteFalso:
    return AssistenteFalso()


@pytest.fixture
def relogio() -> RelogioParado:
    return RelogioParado()


@pytest.fixture
def repos():
    return UsuariosEmMemoria(), SessoesEmMemoria(), ConsentimentosEmMemoria()


@pytest.fixture
def conteiner(repos, relogio, assistente) -> Conteiner:
    usuarios, sessoes, consentimentos = repos
    return montar(
        usuarios, sessoes, consentimentos, HasherScrypt(), relogio, timedelta(hours=24), assistente, TrilhaFalsa()
    )


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
