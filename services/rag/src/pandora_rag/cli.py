"""Linha de comando: coletar, extrair, indexar, buscar e perguntar."""
from __future__ import annotations

import json
import logging
from typing import Optional

import typer

app = typer.Typer(help="RAG híbrido do PANDORA", no_args_is_help=True)
MODELO_EMBEDDING = "BAAI/bge-m3"


@app.command()
def coletar() -> None:
    """Baixa as fontes de fontes.yaml e atualiza corpus.lock."""
    from pandora_rag.ingest.collect import coletar as _coletar

    logging.basicConfig(level=logging.WARNING)
    for fonte, situacao in _coletar().items():
        typer.echo(f"{fonte:18} {situacao}")


@app.command()
def extrair() -> None:
    """Extrai o texto limpo de data/raw para data/text."""
    from pandora_rag.ingest.extract import extrair as _extrair, salvar_texto
    from pandora_rag.ingest.fontes import carregar_fontes

    for f in carregar_fontes():
        blocos = _extrair(f)
        salvar_texto(f, blocos)
        typer.echo(f"{f.id:18} {len(blocos):5} blocos")


@app.command()
def indexar(modelo: str = MODELO_EMBEDDING, estrategia: str = "estrutural", tabela: str = "chunks", recriar: bool = True) -> None:
    """Gera embeddings e grava os chunks no pgvector."""
    from pandora_rag.config import DB_URL
    from pandora_rag.index.build import embeddings
    from pandora_rag.index.embedder import Embedder
    from pandora_rag.index.registro import montar_registros
    from pandora_rag.index.store import PgVectorStore

    registros = montar_registros(estrategia)
    emb = Embedder(modelo)
    vetores = embeddings(registros, emb)
    pg = PgVectorStore(DB_URL, tabela, emb.dim)
    pg.criar_esquema(recriar=recriar)
    pg.inserir(registros, vetores)
    typer.echo(f"{pg.contar()} chunks em '{tabela}' (corpus {registros[0].versao_corpus}, modelo {modelo})")


def _retriever(modelo: str, tabela: str, rerank: bool):
    from pandora_rag.config import DB_URL
    from pandora_rag.index.embedder import Embedder
    from pandora_rag.index.store import PgVectorStore
    from pandora_rag.retrieve.hybrid import IndiceBM25, Reranker, Retriever

    emb = Embedder(modelo)
    pg = PgVectorStore(DB_URL, tabela, emb.dim)
    regs = pg.carregar_registros()
    return Retriever(pg, IndiceBM25(regs), emb, Reranker() if rerank else None)


@app.command()
def buscar(pergunta: str, k: int = 5, tabela: str = "chunks", rerank: bool = False, modelo: str = MODELO_EMBEDDING) -> None:
    """Mostra os chunks recuperados, sem gerar resposta."""
    for n, h in enumerate(_retriever(modelo, tabela, rerank).buscar(pergunta, k), start=1):
        r = h.registro
        typer.echo(f"[{n}] {r.norma} {r.artigo or ''}  score={h.score:.4f} vet={h.score_vetor} bm25={h.score_bm25}\n    {r.link}\n    {r.texto[:200]!r}")


@app.command()
def ask(pergunta: str, llm: str = "qwen25-14b", k: int = 5, tabela: str = "chunks", rerank: bool = True,
        modelo: str = MODELO_EMBEDDING, saida_json: Optional[bool] = False) -> None:
    """Consulta completa: busca, resposta fundamentada e fontes."""
    from pandora_rag.config import LIMIAR_ABSTENCAO
    from pandora_rag.generate.answer import responder
    from pandora_rag.generate.gateway import Gateway

    retr = _retriever(modelo, tabela, rerank)
    hits = retr.buscar(pergunta, k)
    resp = responder(Gateway(), llm, pergunta, hits, limiar_abstencao=LIMIAR_ABSTENCAO if rerank else None)
    if saida_json:
        typer.echo(json.dumps({"pergunta": pergunta, "resposta": resp.texto, "abstencao": resp.abstencao,
                               "citacoes": [c.__dict__ for c in resp.citacoes]}, ensure_ascii=False, indent=2))
        return
    typer.echo(f"PERGUNTA: {pergunta}\n\nCHUNKS RECUPERADOS:")
    for n, h in enumerate(hits, start=1):
        typer.echo(f"  [{n}] {h.registro.norma} {h.registro.artigo or ''}  score={h.score:.3f}\n      \"{' '.join(h.registro.texto.split())[:220]}...\"")
    typer.echo(f"\nRESPOSTA ({resp.modelo}, {resp.latencia_s:.1f}s, US$ {resp.custo_usd:.4f}):\n{resp.texto}\n\nFONTES:")
    for c in resp.citacoes:
        typer.echo(f"  [{c.n}] {c.norma} {c.artigo or ''}\n      {c.link}\n      trecho: \"{' '.join(c.trecho.split())[:220]}...\"")
    if resp.abstencao:
        typer.echo("  (abstenção: sem trecho que sustente a resposta)")


if __name__ == "__main__":
    app()
