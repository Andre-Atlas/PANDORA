"""Repositórios em Postgres (psycopg 3). O mesmo banco pgvector do RAG."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from pandora_api.dominio.consentimento import Consentimento, Finalidade
from pandora_api.dominio.usuario import Sessao, Usuario

MIGRACOES = [
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id UUID PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        senha_hash TEXT NOT NULL,
        criado_em TIMESTAMPTZ NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sessoes (
        token_hash TEXT PRIMARY KEY,
        usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        criada_em TIMESTAMPTZ NOT NULL,
        expira_em TIMESTAMPTZ NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS consentimentos (
        id UUID PRIMARY KEY,
        usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        finalidade TEXT NOT NULL,
        versao_termo TEXT NOT NULL,
        aceito_em TIMESTAMPTZ NOT NULL,
        revogado_em TIMESTAMPTZ
    )
    """,
    "CREATE INDEX IF NOT EXISTS consentimentos_usuario ON consentimentos (usuario_id)",
]


class BancoPostgres:
    def __init__(self, url: str) -> None:
        # Sessão sempre em UTC: datas saem do banco no mesmo fuso em que entram.
        self.pool = ConnectionPool(url, kwargs={"row_factory": dict_row, "options": "-c TimeZone=UTC"}, open=True)

    def migrar(self) -> None:
        with self.conexao() as con:
            for sql in MIGRACOES:
                con.execute(sql)

    @contextmanager
    def conexao(self) -> Iterator[psycopg.Connection]:
        with self.pool.connection() as con:
            yield con

    def fechar(self) -> None:
        self.pool.close()


class UsuariosPostgres:
    def __init__(self, banco: BancoPostgres) -> None:
        self._banco = banco

    def adicionar(self, u: Usuario) -> None:
        with self._banco.conexao() as con:
            con.execute(
                "INSERT INTO usuarios (id, email, senha_hash, criado_em) VALUES (%s, %s, %s, %s)",
                (u.id, u.email, u.senha_hash, u.criado_em),
            )

    def _um(self, sql: str, parametro: object) -> Usuario | None:
        with self._banco.conexao() as con:
            linha = con.execute(sql, (parametro,)).fetchone()
        return Usuario(**linha) if linha else None

    def por_email(self, email: str) -> Usuario | None:
        return self._um("SELECT id, email, senha_hash, criado_em FROM usuarios WHERE email = %s", email)

    def por_id(self, usuario_id: UUID) -> Usuario | None:
        return self._um("SELECT id, email, senha_hash, criado_em FROM usuarios WHERE id = %s", usuario_id)

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        with self._banco.conexao() as con:
            con.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))


class SessoesPostgres:
    def __init__(self, banco: BancoPostgres) -> None:
        self._banco = banco

    def adicionar(self, s: Sessao) -> None:
        with self._banco.conexao() as con:
            con.execute(
                "INSERT INTO sessoes (token_hash, usuario_id, criada_em, expira_em) VALUES (%s, %s, %s, %s)",
                (s.token_hash, s.usuario_id, s.criada_em, s.expira_em),
            )

    def por_token_hash(self, token_hash: str) -> Sessao | None:
        with self._banco.conexao() as con:
            linha = con.execute(
                "SELECT token_hash, usuario_id, criada_em, expira_em FROM sessoes WHERE token_hash = %s",
                (token_hash,),
            ).fetchone()
        return Sessao(**linha) if linha else None

    def remover(self, token_hash: str) -> None:
        with self._banco.conexao() as con:
            con.execute("DELETE FROM sessoes WHERE token_hash = %s", (token_hash,))

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        with self._banco.conexao() as con:
            con.execute("DELETE FROM sessoes WHERE usuario_id = %s", (usuario_id,))


class ConsentimentosPostgres:
    _COLUNAS = "id, usuario_id, finalidade, versao_termo, aceito_em, revogado_em"

    def __init__(self, banco: BancoPostgres) -> None:
        self._banco = banco

    @staticmethod
    def _de_linha(linha: dict) -> Consentimento:
        return Consentimento(**{**linha, "finalidade": Finalidade(linha["finalidade"])})

    def adicionar(self, c: Consentimento) -> None:
        with self._banco.conexao() as con:
            con.execute(
                f"INSERT INTO consentimentos ({self._COLUNAS}) VALUES (%s, %s, %s, %s, %s, %s)",
                (c.id, c.usuario_id, c.finalidade.value, c.versao_termo, c.aceito_em, c.revogado_em),
            )

    def atualizar(self, c: Consentimento) -> None:
        with self._banco.conexao() as con:
            con.execute("UPDATE consentimentos SET revogado_em = %s WHERE id = %s", (c.revogado_em, c.id))

    def por_id(self, consentimento_id: UUID) -> Consentimento | None:
        with self._banco.conexao() as con:
            linha = con.execute(
                f"SELECT {self._COLUNAS} FROM consentimentos WHERE id = %s", (consentimento_id,)
            ).fetchone()
        return self._de_linha(linha) if linha else None

    def do_usuario(self, usuario_id: UUID) -> list[Consentimento]:
        with self._banco.conexao() as con:
            linhas = con.execute(
                f"SELECT {self._COLUNAS} FROM consentimentos WHERE usuario_id = %s", (usuario_id,)
            ).fetchall()
        return [self._de_linha(linha) for linha in linhas]

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        with self._banco.conexao() as con:
            con.execute("DELETE FROM consentimentos WHERE usuario_id = %s", (usuario_id,))
