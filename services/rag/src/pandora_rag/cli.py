"""Linha de comando: coletar, extrair, indexar, buscar e perguntar."""
from __future__ import annotations

import json
import logging
from pathlib import Path
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
def ask(pergunta: str, llm: str = "haiku", k: int = 5, tabela: str = "chunks", rerank: bool = True,
        modelo: str = MODELO_EMBEDDING, saida_json: Optional[bool] = False) -> None:
    """Consulta completa: busca, resposta fundamentada e fontes."""
    from pandora_rag.generate.answer import responder
    from pandora_rag.generate.gateway import Gateway

    retr = _retriever(modelo, tabela, rerank)
    hits = retr.buscar(pergunta, k)
    resp = responder(Gateway(), llm, pergunta, hits)
    if saida_json:
        typer.echo(json.dumps({"pergunta": pergunta, "resposta": resp.texto, "abstencao": resp.abstencao,
                               "citacoes": [c.__dict__ for c in resp.citacoes]}, ensure_ascii=False, indent=2))
        return
    typer.echo(f"PERGUNTA: {pergunta}\n\nCHUNKS RECUPERADOS:")
    for n, h in enumerate(hits, start=1):
        typer.echo(f"  [{n}] {h.registro.norma} {h.registro.artigo or ''}  score={h.score:.3f}")
    typer.echo(f"\nRESPOSTA ({resp.modelo}, {resp.latencia_s:.1f}s, US$ {resp.custo_usd:.4f}):\n{resp.texto}\n\nFONTES:")
    for c in resp.citacoes:
        typer.echo(f"  [{c.n}] {c.norma} {c.artigo or ''}\n      {c.link}")
    if resp.abstencao:
        typer.echo("  (abstenção: sem trecho que sustente a resposta)")


@app.command()
def agent(
    pergunta: str,
    persona: str | None = None,
    llm: str | None = None,
    offline: bool = False,
    documento_ocr: str | None = None,
    linha_digitavel: str | None = None,
    saida_json: bool = False,
) -> None:
    """Executa uma consulta completa no grafo dos 7 agentes especializados."""
    from pandora_rag.agents.graph import GrafoPandora, construir_retriever_padrao
    from pandora_rag.generate.gateway import Gateway

    retr, origem = construir_retriever_padrao(usar_reranker=False, preferir_embutido=offline)
    gw = Gateway() if (llm and not offline) else None
    grafo = GrafoPandora(retriever=retr, gateway=gw, origem_retriever=origem)
    res = grafo.executar(
        consulta=pergunta,
        persona_id=persona,
        documento_ocr=documento_ocr,
        linha_digitavel=linha_digitavel,
        llm=None if offline else llm,
    )
    if saida_json:
        typer.echo(res.model_dump_json(indent=2))
        return
    typer.echo(f"ORIGEM RAG: {origem} | MODO: {res.modo} | AGENTES: {' -> '.join(res.agentes_acionados)}")
    typer.echo("\nTRACE DE COLABORAÇÃO:")
    for m in res.trace:
        typer.echo(f"  [{m.ordem}] {m.origem} -> {m.destino} ({m.tipo}): {m.resumo}")
    typer.echo(f"\nRESPOSTA FINAL:\n{res.resposta_final}")


@app.command()
def demo(
    llm: str | None = None,
    offline: bool = False,
    saida_dir: Path | None = None,
) -> None:
    """Executa as 4 jornadas demonstrativas das personas e exporta o trace completo."""
    from pandora_rag.agents.graph import GrafoPandora, construir_retriever_padrao
    from pandora_rag.agents.scenarios import CENARIOS_DEMO, executar_demonstracao
    from pandora_rag.generate.gateway import Gateway

    retr, origem = construir_retriever_padrao(usar_reranker=False, preferir_embutido=offline)
    gw = Gateway() if (llm and not offline) else None
    grafo = GrafoPandora(retriever=retr, gateway=gw, origem_retriever=origem)
    resultados = executar_demonstracao(grafo, llm=None if offline else llm, saida_dir=saida_dir)
    typer.echo(f"Demonstração concluída ({len(resultados)} jornadas, retriever={origem}):")
    for cen, res in zip(CENARIOS_DEMO, resultados, strict=True):
        typer.echo(f"\n=== {cen.titulo} ===")
        typer.echo(f"Agentes: {' -> '.join(res.agentes_acionados)} ({len(res.trace)} interações)")
        typer.echo(res.resposta_final)
    if saida_dir:
        typer.echo(f"\nArtefatos gravados em: {saida_dir}")


if __name__ == "__main__":
    app()
