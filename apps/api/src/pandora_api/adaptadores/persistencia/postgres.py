"""Repositórios em Postgres (psycopg 3). O mesmo banco pgvector do RAG."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from pandora_api.dominio.consentimento import Consentimento, Finalidade
from pandora_api.dominio.extrato import Extrato, StatusExtrato
from pandora_api.dominio.transacao import (
    FUSO_DA_PESSOA,
    Categoria,
    FormaPagamento,
    OrigemCategoria,
    Parcela,
    Transacao,
)
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
    """
    CREATE TABLE IF NOT EXISTS extratos (
        id UUID PRIMARY KEY,
        usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        nome_arquivo TEXT NOT NULL,
        status TEXT NOT NULL,
        recebido_em TIMESTAMPTZ NOT NULL,
        transacoes_importadas INTEGER,
        avisos TEXT[] NOT NULL DEFAULT '{}'
    )
    """,
    "CREATE INDEX IF NOT EXISTS extratos_usuario ON extratos (usuario_id)",
    """
    CREATE TABLE IF NOT EXISTS transacoes (
        id UUID PRIMARY KEY,
        usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        conta_id TEXT NOT NULL,
        data_hora TIMESTAMPTZ NOT NULL,
        mes CHAR(7) NOT NULL,
        valor_centavos BIGINT NOT NULL,
        forma_pagamento TEXT NOT NULL,
        descricao_mascarada TEXT NOT NULL,
        mcc CHAR(4),
        categoria TEXT NOT NULL,
        origem_categoria TEXT NOT NULL,
        confianca_categoria DOUBLE PRECISION,
        versao_modelo TEXT,
        essencial BOOLEAN NOT NULL,
        parcela_numero SMALLINT,
        parcela_total SMALLINT
    )
    """,
    "CREATE INDEX IF NOT EXISTS transacoes_usuario_mes ON transacoes (usuario_id, mes, data_hora DESC)",
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


class ExtratosPostgres:
    _COLUNAS = "id, usuario_id, nome_arquivo, status, recebido_em, transacoes_importadas, avisos"

    def __init__(self, banco: BancoPostgres) -> None:
        self._banco = banco

    def salvar(self, e: Extrato) -> None:
        with self._banco.conexao() as con:
            con.execute(
                f"""INSERT INTO extratos ({self._COLUNAS}) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status,
                    transacoes_importadas = EXCLUDED.transacoes_importadas, avisos = EXCLUDED.avisos""",
                (
                    e.id,
                    e.usuario_id,
                    e.nome_arquivo,
                    e.status.value,
                    e.recebido_em,
                    e.transacoes_importadas,
                    list(e.avisos),
                ),
            )

    def por_id(self, usuario_id: UUID, extrato_id: UUID) -> Extrato | None:
        with self._banco.conexao() as con:
            linha = con.execute(
                f"SELECT {self._COLUNAS} FROM extratos WHERE id = %s AND usuario_id = %s", (extrato_id, usuario_id)
            ).fetchone()
        if linha is None:
            return None
        return Extrato(**{**linha, "status": StatusExtrato(linha["status"]), "avisos": tuple(linha["avisos"])})

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        with self._banco.conexao() as con:
            con.execute("DELETE FROM extratos WHERE usuario_id = %s", (usuario_id,))


class TransacoesPostgres:
    _COLUNAS = (
        "id, conta_id, data_hora, valor_centavos, forma_pagamento, descricao_mascarada, mcc, categoria, "
        "origem_categoria, confianca_categoria, versao_modelo, essencial, parcela_numero, parcela_total"
    )

    def __init__(self, banco: BancoPostgres) -> None:
        self._banco = banco

    @staticmethod
    def _de_linha(linha: dict) -> Transacao:
        numero, total = linha.pop("parcela_numero"), linha.pop("parcela_total")
        return Transacao(
            **{
                **linha,
                "data_hora": linha["data_hora"].astimezone(FUSO_DA_PESSOA),
                "forma_pagamento": FormaPagamento(linha["forma_pagamento"]),
                "categoria": Categoria(linha["categoria"]),
                "origem_categoria": OrigemCategoria(linha["origem_categoria"]),
                "parcela": Parcela(numero, total) if numero else None,
            }
        )

    @staticmethod
    def _valores(usuario_id: UUID, t: Transacao) -> tuple:
        return (
            t.id,
            usuario_id,
            t.conta_id,
            t.data_hora,
            t.mes,
            t.valor_centavos,
            t.forma_pagamento.value,
            t.descricao_mascarada,
            t.mcc,
            t.categoria.value,
            t.origem_categoria.value,
            t.confianca_categoria,
            t.versao_modelo,
            t.essencial,
            t.parcela.numero if t.parcela else None,
            t.parcela.total if t.parcela else None,
        )

    def adicionar(self, usuario_id: UUID, transacoes: list[Transacao]) -> None:
        if not transacoes:
            return
        with self._banco.conexao() as con, con.cursor() as cur:
            cur.executemany(
                """INSERT INTO transacoes (id, usuario_id, conta_id, data_hora, mes, valor_centavos, forma_pagamento,
                    descricao_mascarada, mcc, categoria, origem_categoria, confianca_categoria, versao_modelo,
                    essencial, parcela_numero, parcela_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                [self._valores(usuario_id, t) for t in transacoes],
            )

    def atualizar(self, usuario_id: UUID, t: Transacao) -> None:
        with self._banco.conexao() as con:
            con.execute(
                """UPDATE transacoes SET categoria = %s, origem_categoria = %s, confianca_categoria = %s,
                    essencial = %s WHERE id = %s AND usuario_id = %s""",
                (t.categoria.value, t.origem_categoria.value, t.confianca_categoria, t.essencial, t.id, usuario_id),
            )

    def por_id(self, usuario_id: UUID, transacao_id: UUID) -> Transacao | None:
        with self._banco.conexao() as con:
            linha = con.execute(
                f"SELECT {self._COLUNAS} FROM transacoes WHERE id = %s AND usuario_id = %s", (transacao_id, usuario_id)
            ).fetchone()
        return self._de_linha(linha) if linha else None

    def listar(
        self, usuario_id: UUID, mes: str | None, categoria: Categoria | None, deslocamento: int, limite: int
    ) -> tuple[list[Transacao], int]:
        filtro = (
            "usuario_id = %(u)s AND (%(m)s::text IS NULL OR mes = %(m)s) AND (%(c)s::text IS NULL OR categoria = %(c)s)"
        )
        p = {"u": usuario_id, "m": mes, "c": categoria.value if categoria else None, "o": deslocamento, "l": limite}
        with self._banco.conexao() as con:
            total = con.execute(f"SELECT count(*) AS n FROM transacoes WHERE {filtro}", p).fetchone()["n"]
            linhas = con.execute(
                f"SELECT {self._COLUNAS} FROM transacoes WHERE {filtro} "
                "ORDER BY data_hora DESC, id DESC OFFSET %(o)s LIMIT %(l)s",
                p,
            ).fetchall()
        return [self._de_linha(linha) for linha in linhas], total

    def do_mes(self, usuario_id: UUID, mes: str) -> list[Transacao]:
        with self._banco.conexao() as con:
            linhas = con.execute(
                f"SELECT {self._COLUNAS} FROM transacoes WHERE usuario_id = %s AND mes = %s", (usuario_id, mes)
            ).fetchall()
        return [self._de_linha(linha) for linha in linhas]

    def apagar_do_usuario(self, usuario_id: UUID) -> None:
        with self._banco.conexao() as con:
            con.execute("DELETE FROM transacoes WHERE usuario_id = %s", (usuario_id,))
