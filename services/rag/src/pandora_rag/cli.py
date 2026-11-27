"""Linha de comando: coletar, extrair, indexar, buscar, perguntar e orquestrar agentes."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated

import typer

from pandora_rag.montagem import LLM_PADRAO, MODELO_EMBEDDING, montar_retriever

app = typer.Typer(help="RAG híbrido do PANDORA", no_args_is_help=True)


@app.command()
def coletar() -> None:
    """Baixa as fontes de fontes.yaml e atualiza corpus.lock."""
    from pandora_rag.ingest.collect import coletar as _coletar

    logging.basicConfig(level=logging.WARNING)
    for fonte, situacao in _coletar().items():
        typer.echo(f"{fonte:18} {situacao}")


@app.command("coletar-catalogo")
def coletar_catalogo_cmd(
    alvo: Annotated[list[str] | None, typer.Option("--alvo", help="Coleta só estes ids de alvo")] = None,
) -> None:
    """Coleta os alvos dos 31 itens do catálogo (HTML, PDF, API) e atualiza catalogo.lock.json."""
    from pandora_rag.coleta.executor import coletar_catalogo

    logging.basicConfig(level=logging.WARNING)
    for id_alvo, situacao in coletar_catalogo(apenas=set(alvo) if alvo else None).items():
        typer.echo(f"{id_alvo:34} {situacao}")


@app.command()
def inventario(
    md: Annotated[str | None, typer.Option("--md", help="Grava a tabela em Markdown neste caminho")] = None,
) -> None:
    """Mostra os 31 itens com formato, frequência e situação (coletada, manual, mista, falha, pendente)."""
    from pandora_rag.coleta.catalogo import carregar_catalogo
    from pandora_rag.coleta.executor import ler_lock, situacao_do_item
    from pandora_rag.coleta.inventario import markdown, resumo

    itens, lock = carregar_catalogo(), ler_lock()
    if md:
        Path(md).write_text(markdown(itens, lock), encoding="utf-8")
        typer.echo(f"inventário gravado em {md}")
    for item in itens:
        typer.echo(
            f"{item.numero:2} {situacao_do_item(item, lock):9} {item.frequencia:10} "
            f"{','.join(item.formatos):12} {item.nome[:70]}"
        )
    typer.echo(f"\n{len(itens)} itens: {resumo(itens, lock)}")


@app.command()
def extrair() -> None:
    """Extrai o texto limpo de data/raw para data/text."""
    from pandora_rag.ingest.extract import extrair as _extrair
    from pandora_rag.ingest.extract import salvar_texto
    from pandora_rag.ingest.fontes import carregar_fontes

    for f in carregar_fontes():
        blocos = _extrair(f)
        salvar_texto(f, blocos)
        typer.echo(f"{f.id:18} {len(blocos):5} blocos")


@app.command()
def indexar(
    modelo: str = MODELO_EMBEDDING,
    estrategia: str = "estrutural",
    tabela: str = "chunks",
    recriar: bool = True,
) -> None:
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
    return montar_retriever(modelo, tabela, rerank)


@app.command()
def buscar(
    pergunta: str,
    k: int = 5,
    tabela: str = "chunks",
    rerank: bool = False,
    modelo: str = MODELO_EMBEDDING,
) -> None:
    """Mostra os chunks recuperados, sem gerar resposta."""
    for n, h in enumerate(_retriever(modelo, tabela, rerank).buscar(pergunta, k), start=1):
        r = h.registro
        typer.echo(
            f"[{n}] {r.norma} {r.artigo or ''}  score={h.score:.4f} vet={h.score_vetor} bm25={h.score_bm25}\n"
            f"    {r.link}\n    {r.texto[:200]!r}"
        )


@app.command()
def ask(
    pergunta: str,
    llm: str = LLM_PADRAO,
    k: int = 5,
    tabela: str = "chunks",
    rerank: bool = True,
    modelo: str = MODELO_EMBEDDING,
    saida_json: bool | None = False,
) -> None:
    """Consulta completa: busca, resposta fundamentada e fontes."""
    from pandora_rag.config import LIMIAR_ABSTENCAO
    from pandora_rag.generate.answer import responder
    from pandora_rag.generate.gateway import Gateway
    from pandora_rag.generate.pii import mascarar

    retr = _retriever(modelo, tabela, rerank)
    hits = retr.buscar(pergunta, k)
    resp = responder(Gateway(), llm, pergunta, hits, limiar_abstencao=LIMIAR_ABSTENCAO if rerank else None)
    if saida_json:
        pergunta_limpa, _ = mascarar(pergunta)
        typer.echo(
            json.dumps(
                {
                    "pergunta": pergunta_limpa,
                    "resposta": resp.texto,
                    "abstencao": resp.abstencao,
                    "citacoes": [c.__dict__ for c in resp.citacoes],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    typer.echo(f"PERGUNTA: {pergunta}\n\nCHUNKS RECUPERADOS:")
    for n, h in enumerate(hits, start=1):
        typer.echo(
            f"  [{n}] {h.registro.norma} {h.registro.artigo or ''}  score={h.score:.3f}\n"
            f"      \"{' '.join(h.registro.texto.split())[:220]}...\""
        )
    typer.echo(f"\nRESPOSTA ({resp.modelo}, {resp.latencia_s:.1f}s, US$ {resp.custo_usd:.4f}):\n{resp.texto}\n\nFONTES:")
    for c in resp.citacoes:
        typer.echo(
            f"  [{c.n}] {c.norma} {c.artigo or ''}\n      {c.link}\n"
            f"      trecho: \"{' '.join(c.trecho.split())[:220]}...\""
        )
    if resp.abstencao:
        typer.echo("  (abstenção: sem trecho que sustente a resposta)")


@app.command()
def agent(
    pergunta: str = typer.Argument("", help="Consulta ou pergunta financeira do usuário"),
    persona: str | None = None,
    llm: str = "qwen25-7b",
    offline: bool = False,
    documento_ocr: str | None = None,
    linha_digitavel: str | None = None,
    banco_alegado: str | None = None,
    beneficiario_pf: bool = False,
    imagem: Path | None = None,
    pdf: Path | None = None,
    extrato: Path | None = None,
    audio: Path | None = None,
    qrcode_pix: str | None = None,
    vlm: str = "qwen25-vl-7b",
    tts_saida: Annotated[
        Path | None,
        typer.Option("--tts-saida", "--saida-audio", help="Caminho WAV para gravar a resposta falada auditada"),
    ] = None,
    saida_json: bool = False,
) -> None:
    """Executa uma consulta completa no StateGraph (LangGraph) com suporte multimodal."""
    from pandora_rag.agents.artifact_store import ArtifactStore
    from pandora_rag.agents.graph import GrafoPandora, construir_retriever_padrao
    from pandora_rag.generate.gateway import Gateway

    retr, origem = construir_retriever_padrao(usar_reranker=False, preferir_embutido=offline)
    gw = Gateway() if (llm and not offline) else None
    grafo = GrafoPandora(retriever=retr, gateway=gw, origem_retriever=origem)
    store = ArtifactStore()
    try:
        res = grafo.executar(
            consulta=pergunta,
            persona_id=persona,
            documento_ocr=documento_ocr,
            linha_digitavel=linha_digitavel,
            banco_alegado=banco_alegado,
            beneficiario_pf=beneficiario_pf,
            llm=None if offline else llm,
            caminho_imagem=imagem,
            caminho_pdf=pdf,
            caminho_extrato=extrato,
            caminho_audio=audio,
            qrcode_pix=qrcode_pix,
            vlm=None if offline else vlm,
            gerar_audio_tts=tts_saida is not None,
            artifact_store=store,
        )
        if tts_saida is not None and res.audio_saida is not None:
            tts_saida.parent.mkdir(parents=True, exist_ok=True)
            tts_saida.write_bytes(store.obter_bytes(res.audio_saida.artefato_id))
    finally:
        store.expurgar_tudo()

    if saida_json:
        typer.echo(res.model_dump_json(indent=2))
        return
    typer.echo(
        f"ORIGEM RAG: {origem} | MODO: {res.modo} | LLM: {res.modelo_llm} | "
        f"TOOL CALLS: {res.total_tool_calls} | AGENTES: {' -> '.join(res.agentes_acionados)}"
    )
    typer.echo("\nTRACE DE COLABORAÇÃO:")
    for m in res.trace:
        typer.echo(f"  [{m.ordem}] {m.origem} -> {m.destino} ({m.tipo}): {m.resumo}")
    typer.echo(f"\nRESPOSTA FINAL:\n{res.resposta_final}")
    if tts_saida is not None:
        typer.echo(f"\nÁUDIO TTS GRAVADO EM: {tts_saida}")


@app.command()
def demo(
    llm: str = "qwen25-7b",
    offline: bool = False,
    saida_dir: Path | None = None,
) -> None:
    """Executa as 4 jornadas demonstrativas das personas no LangGraph e exporta o trace completo."""
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
        typer.echo(
            f"Agentes: {' -> '.join(res.agentes_acionados)} "
            f"({len(res.trace)} interações, LLM={res.modelo_llm}, tool_calls={res.total_tool_calls})"
        )
        typer.echo(res.resposta_final)
    if saida_dir:
        typer.echo(f"\nArtefatos gravados em: {saida_dir}")


@app.command("gerar-trilha")
def gerar_trilha(
    saida: str = "",
    llm: str = LLM_PADRAO,
    k: int = 4,
    tentativas: int = 3,
    etapa: str | None = None,
) -> None:
    """Gera e valida o conteúdo da trilha (explicação e perguntas com fontes) e salva em JSON."""
    from pandora_rag.config import LIMIAR_ABSTENCAO, REPO_ROOT
    from pandora_rag.montagem import montar_gateway
    from pandora_rag.trilha import ROTEIRO, gerar_etapa, montar_documento

    destino = Path(saida) if saida else REPO_ROOT / "apps" / "api" / "src" / "pandora_api" / "dados" / "trilha.v1.json"
    retr, gw = montar_retriever(), montar_gateway()

    etapas, falhas = [], 0
    for e in ROTEIRO:
        if etapa and e["id"] != etapa:
            continue
        r = gerar_etapa(retr, gw, llm, e, LIMIAR_ABSTENCAO, k, tentativas)
        etapas.append(r)
        ctl = r["_controle"]
        typer.echo(
            f"{e['n']}. {e['t']:24} perguntas={len(r['licao']['perguntas'])} "
            f"descartadas={len(ctl['perguntas_descartadas'])} problemas={ctl['problemas'] or '-'}"
        )
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
def servir(porta: int = 8010, host: str = "127.0.0.1") -> None:
    """Sobe o serviço HTTP (POST /responder), carregando os modelos uma vez."""
    import uvicorn

    uvicorn.run("pandora_rag.servico.app:app_padrao", factory=True, host=host, port=porta)


if __name__ == "__main__":
    app()
