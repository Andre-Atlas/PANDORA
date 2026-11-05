"""Armazenamento vetorial: em memória (experimentos) e pgvector (índice real).

Os dois expõem `buscar_vetor`, que devolve (posição, cosseno) ordenados, e aceitam o mesmo
filtro por metadado: `{campo: valor | [valores]}`.
"""
from __future__ import annotations

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

        assert tabela.replace("_", "").isalnum(), "nome de tabela inválido"
        self.tabela, self.dim = tabela, dim
        self.conn = psycopg.connect(url, autocommit=True)
        self.conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(self.conn)
        self.registros: list[Registro] = []

    def criar_esquema(self, recriar: bool = False) -> None:
        if recriar:
            self.conn.execute(f"DROP TABLE IF EXISTS {self.tabela}")
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS {self.tabela} ({SQL_COLUNAS}, embedding vector({self.dim}))")
        self.conn.execute(
            f"CREATE INDEX IF NOT EXISTS {self.tabela}_hnsw ON {self.tabela} "
            "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
        )
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS {self.tabela}_fonte ON {self.tabela} (fonte_id)")

    def inserir(self, registros: list[Registro], vetores: np.ndarray) -> None:
        marcadores = ", ".join(["%s"] * (len(COLUNAS) + 1))
        sql = f"INSERT INTO {self.tabela} ({', '.join(COLUNAS)}, embedding) VALUES ({marcadores}) ON CONFLICT (id) DO UPDATE SET " + ", ".join(
            f"{c} = EXCLUDED.{c}" for c in COLUNAS[1:] + ["embedding"]
        )
        with self.conn.cursor() as cur:
            cur.executemany(sql, [[getattr(r, c) for c in COLUNAS] + [v] for r, v in zip(registros, vetores)])

    def carregar_registros(self) -> list[Registro]:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(COLUNAS)} FROM {self.tabela} ORDER BY fonte_id, ordem")
            linhas = cur.fetchall()
        self.registros = [Registro(**{c: (str(v) if c == "data_referencia_normativa" else v) for c, v in zip(COLUNAS, l)}) for l in linhas]
        return self.registros

    def contar(self) -> int:
        return self.conn.execute(f"SELECT count(*) FROM {self.tabela}").fetchone()[0]

    def buscar_vetor(self, consulta: np.ndarray, k: int, filtro: dict[str, Any] | None = None) -> list[tuple[int, float]]:
        if not self.registros:
            self.carregar_registros()
        posicao = {r.id: i for i, r in enumerate(self.registros)}
        onde, params = [], []
        for campo, valor in (filtro or {}).items():
            assert campo in CAMPOS_FILTRO, f"campo de filtro inválido: {campo}"
            valores = list(valor) if isinstance(valor, (list, tuple, set)) else [valor]
            onde.append(f"{campo} = ANY(%s)")
            params.append(valores)
        clausula = f"WHERE {' AND '.join(onde)}" if onde else ""
        self.conn.execute("SET LOCAL hnsw.ef_search = 100") if False else None
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT id, 1 - (embedding <=> %s) FROM {self.tabela} {clausula} ORDER BY embedding <=> %s LIMIT %s",
                [consulta, *params, consulta, k],
            )
            return [(posicao[i], float(s)) for i, s in cur.fetchall()]
