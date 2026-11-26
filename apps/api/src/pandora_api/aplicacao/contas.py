from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from pandora_api.dominio.erros import CredenciaisInvalidas, EmailJaCadastrado, SenhaFraca, SessaoInvalida
from pandora_api.dominio.usuario import TAMANHO_MINIMO_SENHA, Sessao, Usuario, normalizar_email
from pandora_api.portas.repositorios import RepositorioSessoes, RepositorioUsuarios
from pandora_api.portas.servicos import HasherSenha, Relogio


def hash_do_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass(frozen=True)
class SessaoAberta:
    token: str
    """Só é mostrado uma vez. O servidor guarda apenas o hash."""
    expira_em: datetime


class Contas:
    def __init__(
        self,
        usuarios: RepositorioUsuarios,
        sessoes: RepositorioSessoes,
        hasher: HasherSenha,
        relogio: Relogio,
        duracao_sessao: timedelta,
    ) -> None:
        self._usuarios = usuarios
        self._sessoes = sessoes
        self._hasher = hasher
        self._relogio = relogio
        self._duracao = duracao_sessao
        # Hash usado quando o e-mail não existe, para o tempo de resposta não
        # revelar quais e-mails têm conta.
        self._hash_falso = hasher.gerar(secrets.token_urlsafe(16))

    def cadastrar(self, email: str, senha: str) -> Usuario:
        if len(senha) < TAMANHO_MINIMO_SENHA:
            raise SenhaFraca(f"A senha precisa de pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
        email = normalizar_email(email)
        if self._usuarios.por_email(email) is not None:
            raise EmailJaCadastrado(email)
        usuario = Usuario(uuid4(), email, self._hasher.gerar(senha), self._relogio.agora())
        self._usuarios.adicionar(usuario)
        return usuario

    def entrar(self, email: str, senha: str) -> SessaoAberta:
        usuario = self._usuarios.por_email(normalizar_email(email))
        senha_hash = usuario.senha_hash if usuario else self._hash_falso
        if not self._hasher.conferir(senha, senha_hash) or usuario is None:
            raise CredenciaisInvalidas()
        token = secrets.token_urlsafe(32)
        agora = self._relogio.agora()
        expira = agora + self._duracao
        self._sessoes.adicionar(Sessao(hash_do_token(token), usuario.id, agora, expira))
        return SessaoAberta(token, expira)

    def usuario_da_sessao(self, token: str) -> Usuario:
        sessao = self._sessoes.por_token_hash(hash_do_token(token))
        if sessao is None or not sessao.valida_em(self._relogio.agora()):
            raise SessaoInvalida()
        usuario = self._usuarios.por_id(sessao.usuario_id)
        if usuario is None:
            raise SessaoInvalida()
        return usuario

    def sair(self, token: str) -> None:
        self._sessoes.remover(hash_do_token(token))
