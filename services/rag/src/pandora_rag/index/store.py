"""Armazenamento vetorial: em memória (experimentos) e pgvector (índice real).

Os dois expõem `buscar_vetor`, que devolve (posição, cosseno) ordenados, e aceitam o mesmo
filtro por metadado: `{campo: valor | [valores]}`.
"""
from __future__ import annotations

import re
from typing import Any, Protocol

import numpy as np

from pandora_rag.index.registro import Registro

CAMPOS_FILTRO = ("camada_dominio", "modalidade_divida", "elegivel_lei_14181", "nivel_urgencia", "fonte_id", "tipo")


def _aceita(reg: Registro, filtro: dict[str, Any] | None) -> bool:
    if not filtro:
        return True
    for campo, valor in filtro.items():
        atual = getattr(reg, campo)
        permitido = valor if isinstance(valor, (list, tuple, set)) else [valor]
        if atual not in permitido:
            return False
    return True


def mascara(registros: list[Registro], filtro: dict[str, Any] | None) -> np.ndarray:
    return np.array([_aceita(r, filtro) for r in registros], dtype=bool)


class Store(Protocol):
    registros: list[Registro]

    def buscar_vetor(self, consulta: np.ndarray, k: int, filtro: dict[str, Any] | None = None) -> list[tuple[int, float]]: ...


class MemoryStore:
    def __init__(self, registros: list[Registro], vetores: np.ndarray):
        assert len(registros) == len(vetores)
        self.registros = registros
        self.vetores = vetores.astype(np.float32)

    def buscar_vetor(self, consulta: np.ndarray, k: int, filtro: dict[str, Any] | None = None) -> list[tuple[int, float]]:
        scores = self.vetores @ consulta.astype(np.float32)
        scores = np.where(mascara(self.registros, filtro), scores, -np.inf)
        ordem = np.argsort(-scores)[:k]
        return [(int(i), float(scores[i])) for i in ordem if np.isfinite(scores[i])]


SQL_COLUNAS = """
    id TEXT PRIMARY KEY, fonte_id TEXT NOT NULL, titulo TEXT, orgao TEXT, tipo TEXT, norma TEXT,
    artigo TEXT, secao TEXT, pagina INT, ordem INT, texto TEXT NOT NULL, hash TEXT NOT NULL,
    citado BOOLEAN, estrategia TEXT, link TEXT, data_coleta TEXT, data_referencia_normativa DATE,
    camada_dominio TEXT, modalidade_divida TEXT, elegivel_lei_14181 BOOLEAN, nivel_urgencia TEXT,
    ressalva TEXT, versao_corpus TEXT, indexado_em TIMESTAMPTZ DEFAULT now()
"""
COLUNAS = [
    "id", "fonte_id", "titulo", "orgao", "tipo", "norma", "artigo", "secao", "pagina", "ordem", "texto", "hash",
    "citado", "estrategia", "link", "data_coleta", "data_referencia_normativa", "camada_dominio",
    "modalidade_divida", "elegivel_lei_14181", "nivel_urgencia", "ressalva", "versao_corpus",
]


class PgVectorStore:
    """Índice HNSW de cosseno no Postgres com pgvector. Uma tabela por coleção."""

    def __init__(self, url: str, tabela: str = "chunks", dim: int = 1024):
        import psycopg
        from pgvector.psycopg import register_vector
        from psycopg import sql

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", tabela):
            raise ValueError(f"nome de tabela inválido: {tabela!r}")
        self.tabela, self.dim = tabela, dim
        self._ident = sql.Identifier(tabela)
        self._idx_hnsw = sql.Identifier(f"{tabela}_hnsw")
        self._idx_fonte = sql.Identifier(f"{tabela}_fonte")
        self.conn = psycopg.connect(url, autocommit=True)
        self.conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(self.conn)
        self.registros: list[Registro] = []

    def criar_esquema(self, recriar: bool = False) -> None:
        from psycopg import sql

        if recriar:
            self.conn.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(self._ident))
        self.conn.execute(
            sql.SQL("CREATE TABLE IF NOT EXISTS {} ({}, embedding vector({}))").format(
                self._ident, sql.SQL(SQL_COLUNAS), sql.Literal(self.dim)
            )
        )
        self.conn.execute(
            sql.SQL(
                "CREATE INDEX IF NOT EXISTS {} ON {} "
                "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
            ).format(self._idx_hnsw, self._ident)
        )
        self.conn.execute(
            sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} (fonte_id)").format(
                self._idx_fonte, self._ident
            )
        )

    def inserir(self, registros: list[Registro], vetores: np.ndarray) -> None:
        from psycopg import sql

        marcadores = ", ".join(["%s"] * (len(COLUNAS) + 1))
        atualiza = ", ".join(f"{c} = EXCLUDED.{c}" for c in COLUNAS[1:] + ["embedding"])
        stmt = sql.SQL("INSERT INTO {} ({}, embedding) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}").format(
            self._ident,
            sql.SQL(", ".join(COLUNAS)),
            sql.SQL(marcadores),
            sql.SQL(atualiza),
        )
        with self.conn.cursor() as cur:
            cur.executemany(stmt, [[getattr(r, c) for c in COLUNAS] + [v] for r, v in zip(registros, vetores)])

    def carregar_registros(self) -> list[Registro]:
        from psycopg import sql

        stmt = sql.SQL("SELECT {} FROM {} ORDER BY fonte_id, ordem").format(
            sql.SQL(", ".join(COLUNAS)), self._ident
        )
        with self.conn.cursor() as cur:
            cur.execute(stmt)
            linhas = cur.fetchall()
        self.registros = [Registro(**{c: (str(v) if c == "data_referencia_normativa" else v) for c, v in zip(COLUNAS, l)}) for l in linhas]
        return self.registros

    def contar(self) -> int:
        from psycopg import sql

        return self.conn.execute(sql.SQL("SELECT count(*) FROM {}").format(self._ident)).fetchone()[0]

    def buscar_vetor(self, consulta: np.ndarray, k: int, filtro: dict[str, Any] | None = None) -> list[tuple[int, float]]:
        from psycopg import sql

        if not self.registros:
            self.carregar_registros()
        posicao = {r.id: i for i, r in enumerate(self.registros)}
        onde, params = [], []
        for campo, valor in (filtro or {}).items():
            if campo not in CAMPOS_FILTRO:
                raise ValueError(f"campo de filtro inválido: {campo}")
            valores = list(valor) if isinstance(valor, (list, tuple, set)) else [valor]
            onde.append(sql.SQL("{} = ANY(%s)").format(sql.Identifier(campo)))
            params.append(valores)
        clausula = sql.SQL("WHERE ") + sql.SQL(" AND ").join(onde) if onde else sql.SQL("")
        stmt = sql.SQL("SELECT id, 1 - (embedding <=> %s) FROM {} {} ORDER BY embedding <=> %s LIMIT %s").format(
            self._ident, clausula
        )
        with self.conn.cursor() as cur:
            cur.execute(stmt, [consulta, *params, consulta, k])
            return [(posicao[i], float(s)) for i, s in cur.fetchall()]
