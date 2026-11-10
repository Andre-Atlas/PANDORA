"""Repositórios em memória. Usados nos testes; não guardam nada entre execuções."""

from __future__ import annotations

from uuid import UUID

from pandora_api.dominio.consentimento import Consentimento
from pandora_api.dominio.usuario import Sessao, Usuario


class UsuariosEmMemoria:
    def __init__(self) -> None:
        self.dados: dict[UUID, Usuario] = {}

    def adicionar(self, usuario: Usuario) -> None:
        self.dados[usuario.id] = usuario

    def por_email(self, email: str) -> Usuario | None:
        return next((u for u in self.dados.values() if u.email == email), None)

    def por_id(self, usuario_id: UUID) -> Usuario | None:
        return self.dados.get(usuario_id)

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        self.dados.pop(usuario_id, None)


class SessoesEmMemoria:
    def __init__(self) -> None:
        self.dados: dict[str, Sessao] = {}

    def adicionar(self, sessao: Sessao) -> None:
        self.dados[sessao.token_hash] = sessao

    def por_token_hash(self, token_hash: str) -> Sessao | None:
        return self.dados.get(token_hash)

    def remover(self, token_hash: str) -> None:
        self.dados.pop(token_hash, None)

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        for chave in [k for k, s in self.dados.items() if s.usuario_id == usuario_id]:
            del self.dados[chave]


class ConsentimentosEmMemoria:
    def __init__(self) -> None:
        self.dados: dict[UUID, Consentimento] = {}

    def adicionar(self, consentimento: Consentimento) -> None:
        self.dados[consentimento.id] = consentimento

    def atualizar(self, consentimento: Consentimento) -> None:
        self.dados[consentimento.id] = consentimento

    def por_id(self, consentimento_id: UUID) -> Consentimento | None:
        return self.dados.get(consentimento_id)

    def do_usuario(self, usuario_id: UUID) -> list[Consentimento]:
        return [c for c in self.dados.values() if c.usuario_id == usuario_id]

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        for chave in [k for k, c in self.dados.items() if c.usuario_id == usuario_id]:
            del self.dados[chave]
