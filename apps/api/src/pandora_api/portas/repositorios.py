from __future__ import annotations

from typing import Protocol
from uuid import UUID

from pandora_api.dominio.consentimento import Consentimento
from pandora_api.dominio.extrato import Extrato
from pandora_api.dominio.transacao import Categoria, Transacao
from pandora_api.dominio.usuario import Sessao, Usuario


class ApagaDadosDoUsuario(Protocol):
    """Todo repositório com dado pessoal implementa isto (RNF01: exclusão total).

    A exclusão percorre todos os repositórios registrados, então um repositório
    novo não tem como ficar de fora sem quebrar o teste de exclusão.
    """

    def apagar_do_usuario(self, usuario_id: UUID) -> None: ...


class RepositorioUsuarios(ApagaDadosDoUsuario, Protocol):
    def adicionar(self, usuario: Usuario) -> None: ...
    def por_email(self, email: str) -> Usuario | None: ...
    def por_id(self, usuario_id: UUID) -> Usuario | None: ...


class RepositorioSessoes(ApagaDadosDoUsuario, Protocol):
    def adicionar(self, sessao: Sessao) -> None: ...
    def por_token_hash(self, token_hash: str) -> Sessao | None: ...
    def remover(self, token_hash: str) -> None: ...


class RepositorioConsentimentos(ApagaDadosDoUsuario, Protocol):
    def adicionar(self, consentimento: Consentimento) -> None: ...
    def atualizar(self, consentimento: Consentimento) -> None: ...
    def por_id(self, consentimento_id: UUID) -> Consentimento | None: ...
    def do_usuario(self, usuario_id: UUID) -> list[Consentimento]: ...


class RepositorioExtratos(ApagaDadosDoUsuario, Protocol):
    def salvar(self, extrato: Extrato) -> None:
        """Insere ou atualiza."""
        ...

    def por_id(self, usuario_id: UUID, extrato_id: UUID) -> Extrato | None: ...


class RepositorioTransacoes(ApagaDadosDoUsuario, Protocol):
    def adicionar(self, usuario_id: UUID, transacoes: list[Transacao]) -> None: ...
    def atualizar(self, usuario_id: UUID, transacao: Transacao) -> None: ...
    def por_id(self, usuario_id: UUID, transacao_id: UUID) -> Transacao | None: ...

    def listar(
        self, usuario_id: UUID, mes: str | None, categoria: Categoria | None, deslocamento: int, limite: int
    ) -> tuple[list[Transacao], int]:
        """Da mais nova para a mais antiga. Devolve a página e o total do filtro."""
        ...

    def do_mes(self, usuario_id: UUID, mes: str) -> list[Transacao]: ...
