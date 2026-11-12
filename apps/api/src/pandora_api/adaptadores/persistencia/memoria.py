"""Repositórios em memória. Usados nos testes; não guardam nada entre execuções."""

from __future__ import annotations

from uuid import UUID

from pandora_api.dominio.consentimento import Consentimento
from pandora_api.dominio.extrato import Extrato
from pandora_api.dominio.transacao import Categoria, Transacao
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


class ExtratosEmMemoria:
    def __init__(self) -> None:
        self.dados: dict[UUID, Extrato] = {}

    def salvar(self, extrato: Extrato) -> None:
        self.dados[extrato.id] = extrato

    def por_id(self, usuario_id: UUID, extrato_id: UUID) -> Extrato | None:
        extrato = self.dados.get(extrato_id)
        return extrato if extrato and extrato.usuario_id == usuario_id else None

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        for chave in [k for k, e in self.dados.items() if e.usuario_id == usuario_id]:
            del self.dados[chave]


class TransacoesEmMemoria:
    def __init__(self) -> None:
        self.dados: dict[UUID, tuple[UUID, Transacao]] = {}

    def adicionar(self, usuario_id: UUID, transacoes: list[Transacao]) -> None:
        for t in transacoes:
            self.dados[t.id] = (usuario_id, t)

    def atualizar(self, usuario_id: UUID, transacao: Transacao) -> None:
        self.dados[transacao.id] = (usuario_id, transacao)

    def por_id(self, usuario_id: UUID, transacao_id: UUID) -> Transacao | None:
        dono, t = self.dados.get(transacao_id, (None, None))
        return t if dono == usuario_id else None

    def _do_usuario(self, usuario_id: UUID) -> list[Transacao]:
        return [t for dono, t in self.dados.values() if dono == usuario_id]

    def listar(
        self, usuario_id: UUID, mes: str | None, categoria: Categoria | None, deslocamento: int, limite: int
    ) -> tuple[list[Transacao], int]:
        filtradas = [
            t
            for t in self._do_usuario(usuario_id)
            if (mes is None or t.mes == mes) and (categoria is None or t.categoria == categoria)
        ]
        filtradas.sort(key=lambda t: (t.data_hora, str(t.id)), reverse=True)
        return filtradas[deslocamento : deslocamento + limite], len(filtradas)

    def do_mes(self, usuario_id: UUID, mes: str) -> list[Transacao]:
        return [t for t in self._do_usuario(usuario_id) if t.mes == mes]

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        for chave in [k for k, (dono, _) in self.dados.items() if dono == usuario_id]:
            del self.dados[chave]
