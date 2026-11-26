"""Linha de comando: coletar, extrair, indexar, buscar e perguntar."""
from __future__ import annotations

import json
import logging
from typing import Optional

import typer

from pandora_rag.montagem import LLM_PADRAO, MODELO_EMBEDDING, montar_retriever

app = typer.Typer(help="RAG híbrido do PANDORA", no_args_is_help=True)


def _fontes_escolhidas(ids: list[str] | None):
    from pandora_rag.ingest.fontes import carregar_fontes

    fontes = carregar_fontes()
    if not ids:
        return fontes
    desconhecidas = sorted(set(ids) - {f.id for f in fontes})
    if desconhecidas:
        raise typer.BadParameter(f"fontes que não estão em fontes.yaml: {desconhecidas}")
    return [f for f in fontes if f.id in set(ids)]


@app.command()
def coletar(fonte: Optional[list[str]] = typer.Option(None, "--fonte", "-f", help="id da fonte (repetível); sem ele, todas")) -> None:
    """Baixa as fontes de fontes.yaml (condicional, com robots.txt e ritmo por domínio) e atualiza corpus.lock."""
    from pandora_rag.ingest.collect import coletar as _coletar, mudaram

    logging.basicConfig(level=logging.WARNING)
    situacao = _coletar(_fontes_escolhidas(fonte))
    for f, s in situacao.items():
        typer.echo(f"{f:22} {s}")
    typer.echo(f"\n{len(mudaram(situacao))} fonte(s) com texto novo ou alterado")


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
def indexar(modelo: str = MODELO_EMBEDDING, estrategia: str = "estrutural", tabela: str = "chunks", recriar: bool = True,
            incremental: bool = typer.Option(False, help="re-embeda só as fontes que mudaram, sem apagar a tabela")) -> None:
    """Gera embeddings e grava os chunks no pgvector.

    Sem --incremental, apaga e recria a tabela: com o serviço no ar, prefira `reindexar`."""
    from pandora_rag.config import DB_URL
    from pandora_rag.index.build import embeddings
    from pandora_rag.index.embedder import Embedder
    from pandora_rag.index.registro import montar_registros
    from pandora_rag.index.store import PgVectorStore

    registros = montar_registros(estrategia)
    emb = Embedder(modelo)
    if incremental:
        from pandora_rag.index.incremental import atualizar

        pg = PgVectorStore(DB_URL, tabela, emb.dim)
        pg.criar_esquema(recriar=False)
        rel = atualizar(pg, registros, lambda regs: emb.passagens([r.texto_indexado(True) for r in regs]))
        typer.echo(f"'{tabela}': {rel.resumo()}")
        return
    vetores = embeddings(registros, emb)
    pg = PgVectorStore(DB_URL, tabela, emb.dim)
    pg.criar_esquema(recriar=recriar)
    pg.inserir(registros, vetores)
    typer.echo(f"{pg.contar()} chunks em '{tabela}' (corpus {registros[0].versao_corpus}, modelo {modelo})")


def _retriever(modelo: str, tabela: str, rerank: bool):
    return montar_retriever(modelo, tabela, rerank)


@app.command()
def buscar(pergunta: str, k: int = 5, tabela: str = "chunks", rerank: bool = False, modelo: str = MODELO_EMBEDDING) -> None:
    """Mostra os chunks recuperados, sem gerar resposta."""
    for n, h in enumerate(_retriever(modelo, tabela, rerank).buscar(pergunta, k), start=1):
        r = h.registro
        typer.echo(f"[{n}] {r.norma} {r.artigo or ''}  score={h.score:.4f} vet={h.score_vetor} bm25={h.score_bm25}\n    {r.link}\n    {r.texto[:200]!r}")


@app.command()
def ask(pergunta: str, llm: str = LLM_PADRAO, k: int = 5, tabela: str = "chunks", rerank: bool = True,
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


@app.command("gerar-trilha")
def gerar_trilha(saida: str = "", llm: str = LLM_PADRAO, k: int = 4, tentativas: int = 3, etapa: Optional[str] = None) -> None:
    """Gera e valida o conteúdo da trilha (explicação e perguntas com fontes) e salva em JSON."""
    from pathlib import Path

    from pandora_rag.config import LIMIAR_ABSTENCAO, REPO_ROOT
    from pandora_rag.montagem import montar_gateway
    from pandora_rag.trilha import ROTEIRO, montar_documento

    destino = Path(saida) if saida else REPO_ROOT / "apps" / "api" / "src" / "pandora_api" / "dados" / "trilha.v1.json"
    retr, gw = montar_retriever(), montar_gateway()
    from pandora_rag.trilha import gerar_etapa

    etapas, falhas = [], 0
    for e in ROTEIRO:
        if etapa and e["id"] != etapa:
            continue
        r = gerar_etapa(retr, gw, llm, e, LIMIAR_ABSTENCAO, k, tentativas)
        etapas.append(r)
        ctl = r["_controle"]
        typer.echo(f"{e['n']}. {e['t']:24} perguntas={len(r['licao']['perguntas'])} descartadas={len(ctl['perguntas_descartadas'])} "
                   f"problemas={ctl['problemas'] or '-'}")
        for d in ctl["perguntas_descartadas"]:
            typer.echo(f"     descartada: {' | '.join(d['erros'])}  ({(d['pergunta'] or '')[:70]})")
        falhas += bool(ctl["problemas"])
    versao = retr.registros[0].versao_corpus if retr.registros else "?"
    doc = montar_documento(etapas, versao, gw.config["modelos"][llm]["id"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"salvo em {destino} (corpus {versao}, hash {doc['hash'][:12]})")
    if falhas:
        raise typer.Exit(1)


@app.command()
def descobrir(
    max_paginas: int = typer.Option(150, help="limite de páginas visitadas pelo crawler"),
    crawler: bool = typer.Option(True, help="rastreia as sementes de sementes.yaml"),
    bcb: bool = typer.Option(True, help="busca normativos novos na API do BCB"),
    classificar: bool = typer.Option(True, help="sugere camada, modalidade e urgência com o LLM local"),
    llm: str = LLM_PADRAO,
) -> None:
    """Acha fontes oficiais novas e grava em fontes.candidatas.yaml. Nada entra no índice aqui."""
    from pandora_rag.ingest import descobrir as d
    from pandora_rag.ingest.collect import ler_lock
    from pandora_rag.ingest.fontes import carregar_candidatas, carregar_fontes, salvar_candidatas
    from pandora_rag.ingest.web import ClienteEducado

    logging.basicConfig(level=logging.WARNING)
    fontes, cands = carregar_fontes(), carregar_candidatas()
    urls, hashes, ids = d.conhecidos(fontes, cands, ler_lock())
    config = d.carregar_sementes()
    classificador = None
    if classificar:
        from pandora_rag.montagem import montar_gateway

        gw = montar_gateway()
        classificador = lambda titulo, blocos: d.classificar_com_llm(gw, llm, titulo, blocos)  # noqa: E731
    novas, pulos = [], {}
    with ClienteEducado() as cli:
        if crawler:
            r = d.rastrear(config, cli, urls, hashes, ids, classificador, max_paginas)
            novas += r.candidatas
            pulos.update(r.pulos)
            typer.echo(f"crawler: {r.visitadas} páginas, {len(r.candidatas)} candidatas, {r.repetidas} já conhecidas")
        if bcb and config.bcb:
            r = d.buscar_normativos_bcb(cli, config.bcb, ids, urls | {c.url for c in novas})
            novas += r.candidatas
            pulos.update(r.pulos)
            typer.echo(f"API do BCB: {r.visitadas} consultas, {len(r.candidatas)} candidatas, {r.repetidas} já conhecidas")
    salvar_candidatas(cands + novas)
    for c in novas:
        typer.echo(f"  + {c.id:40} {c.confianca:5} {c.tipo:10} {c.camada_dominio}  {c.url}")
    for url, motivo in list(pulos.items())[:25]:
        typer.echo(f"  - pulada: {motivo[:90]}  {url}")
    typer.echo(f"\n{len(novas)} candidata(s) nova(s); {len(cands) + len(novas)} em fontes.candidatas.yaml")


@app.command()
def lacunas(buscar: bool = typer.Option(False, help="procura normativos no BCB com os termos das lacunas"),
            minimo: int = 2) -> None:
    """Agrupa as perguntas sem resposta (data/lacunas.jsonl) em consultas para achar fontes."""
    from pandora_rag.ingest.lacunas import agrupar, ler_lacunas

    registros = ler_lacunas()
    grupos = agrupar(registros, minimo)
    typer.echo(f"{len(registros)} pergunta(s) sem resposta registradas")
    for consulta, n in grupos:
        typer.echo(f"  {n:3}x  {consulta}")
    if not buscar or not grupos:
        return
    from pandora_rag.ingest import descobrir as d
    from pandora_rag.ingest.collect import ler_lock
    from pandora_rag.ingest.fontes import carregar_candidatas, carregar_fontes, salvar_candidatas
    from pandora_rag.ingest.web import ClienteEducado

    fontes, cands = carregar_fontes(), carregar_candidatas()
    urls, _, ids = d.conhecidos(fontes, cands, ler_lock())
    config = d.carregar_sementes().bcb
    novas = []
    with ClienteEducado() as cli:
        for consulta, _ in grupos[:5]:
            cfg = {**config, "texto_livre": consulta, "dias": 3650}
            r = d.buscar_normativos_bcb(cli, cfg, ids, urls | {c.url for c in novas})
            for c in r.candidatas:
                c.origem = "lacuna"
                c.motivos.append(f"achada pela lacuna: {consulta}")
            novas += r.candidatas
    salvar_candidatas(cands + novas)
    typer.echo(f"{len(novas)} candidata(s) nova(s) a partir das lacunas")


@app.command()
def reindexar(
    modelo: str = MODELO_EMBEDDING,
    promover: bool = typer.Option(True, help="testa e promove as candidatas de confiança alta"),
    rerank: bool = typer.Option(False, help="avalia com reranker (mais lento, mais fiel ao serviço)"),
    tolerancia: float = typer.Option(0.01, help="queda máxima aceita em cada métrica"),
    recarregar: bool = typer.Option(True, help="pede ao serviço no ar para recarregar o índice"),
    retestar: bool = typer.Option(False, help="testa de novo candidatas recusadas pela trava há menos de 30 dias"),
) -> None:
    """Indexa o que mudou numa tabela sombra, passa pela trava do golden e só então troca o índice."""
    import os

    from pandora_rag.ingest.pipeline import reindexar as _reindexar

    logging.basicConfig(level=logging.WARNING)
    r = _reindexar(modelo, promover=promover, rerank=rerank, tolerancia=tolerancia, recarregar_servico=recarregar,
                   token=os.environ.get("PANDORA_RAG_TOKEN_ADMIN"), eco=typer.echo, retestar=retestar)
    typer.echo(f"\n{r.motivo}")
    if r.promovidas:
        typer.echo(f"promovidas: {', '.join(r.promovidas)}")
    for cid, motivo in r.barradas.items():
        typer.echo(f"  ficou como candidata: {cid} ({motivo[:100]})")
    if r.relatorio:
        typer.echo(f"relatório: {r.relatorio}")
    if r.veredito and not r.veredito.passou:
        raise typer.Exit(1)


@app.command()
def monitorar(
    modelo: str = MODELO_EMBEDDING,
    bcb: bool = typer.Option(True, help="também procura normativos novos no BCB"),
    recarregar: bool = typer.Option(True, help="pede ao serviço no ar para recarregar o índice"),
) -> None:
    """Rotina semanal: recoleta as fontes, busca normativos novos e reindexa só se algo mudou."""
    import os

    from pandora_rag.ingest import descobrir as d
    from pandora_rag.ingest.collect import coletar as _coletar, ler_lock, mudaram
    from pandora_rag.ingest.fontes import carregar_candidatas, carregar_fontes, salvar_candidatas
    from pandora_rag.ingest.pipeline import reindexar as _reindexar
    from pandora_rag.ingest.web import ClienteEducado

    logging.basicConfig(level=logging.WARNING)
    situacao = _coletar()
    falhas = {f: s for f, s in situacao.items() if s.startswith("falha")}
    alteradas = mudaram(situacao)
    typer.echo(f"coleta: {len(situacao)} fontes, {len(alteradas)} com texto novo/alterado, {len(falhas)} falha(s)")
    for f, s in falhas.items():
        typer.echo(f"  falha {f}: {s[:120]}")
    novas = []
    if bcb:
        fontes, cands = carregar_fontes(), carregar_candidatas()
        urls, _, ids = d.conhecidos(fontes, cands, ler_lock())
        cfg = d.carregar_sementes().bcb
        if cfg:
            with ClienteEducado() as cli:
                novas = d.buscar_normativos_bcb(cli, {**cfg, "dias": 60}, ids, urls).candidatas
            salvar_candidatas(cands + novas)
            typer.echo(f"normativos novos no BCB: {len(novas)}")
    from datetime import date

    pendentes = [c for c in carregar_candidatas() if c.testavel(date.today().isoformat())]
    if not alteradas and not pendentes:
        typer.echo("nada mudou: índice mantido")
        return
    r = _reindexar(modelo, recarregar_servico=recarregar, token=os.environ.get("PANDORA_RAG_TOKEN_ADMIN"), eco=typer.echo)
    typer.echo(f"\n{r.motivo}" + (f"\nrelatório: {r.relatorio}" if r.relatorio else ""))
    if r.veredito and not r.veredito.passou:
        raise typer.Exit(1)


@app.command()
def servir(porta: int = 8010, host: str = "127.0.0.1") -> None:
    """Sobe o serviço HTTP (POST /responder), carregando os modelos uma vez."""
    import uvicorn

    uvicorn.run("pandora_rag.servico.app:app_padrao", factory=True, host=host, port=porta)


if __name__ == "__main__":
    app()
