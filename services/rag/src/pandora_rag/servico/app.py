"""Serviço HTTP do RAG: carrega os modelos uma vez e responde perguntas com fontes.

A API do PANDORA chama este serviço; o front nunca fala com ele direto.
"""
from __future__ import annotations

import threading
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from pandora_rag.generate.answer import Resposta, responder

MAX_PERGUNTA = 2000
MAX_CONTEXTO = 4000


class PerguntaEntrada(BaseModel):
    pergunta: str = Field(min_length=1, max_length=MAX_PERGUNTA)
    contexto: str | None = Field(default=None, max_length=MAX_CONTEXTO)
    k: int = Field(default=3, ge=1, le=10)


class CitacaoSaida(BaseModel):
    n: int
    norma: str
    artigo: str | None = None
    link: str
    trecho: str
    pagina: int | None = None
    ressalva: str | None = None


class RespostaSaida(BaseModel):
    texto: str
    abstencao: bool
    motivo: str
    citacoes: list[CitacaoSaida]
    modelo: str
    latencia_s: float


class Saude(BaseModel):
    estado: str
    pronto: bool
    chunks: int | None = None


def motivo_da(resp: Resposta) -> str:
    if not resp.abstencao:
        return "ok"
    return "portao" if resp.modelo == "portao" else "llm"


def pergunta_para_llm(pergunta: str, contexto: str | None) -> str:
    """O contexto (por exemplo, a questão de uma lição) orienta a resposta, mas nunca vira fonte."""
    if not contexto:
        return pergunta
    return f"CONTEXTO DA CONVERSA (não é fonte):\n{contexto.strip()}\n\n{pergunta}"


def criar_app(
    montar_retriever: Callable[[], object],
    montar_gateway: Callable[[], object],
    llm: str,
    limiar_abstencao: float | None,
) -> FastAPI:
    estado: dict = {"retriever": None, "gateway": None, "erro": None}
    trava = threading.Lock()  # a conexão com o pgvector é única

    def carregar() -> None:
        try:
            estado["retriever"] = montar_retriever()
            estado["gateway"] = montar_gateway()
        except Exception as exc:  # o serviço sobe e informa o erro em /saude
            estado["erro"] = f"{type(exc).__name__}: {exc}"

    @asynccontextmanager
    async def ciclo(_: FastAPI):
        # carrega em segundo plano para /saude responder já durante o aquecimento
        threading.Thread(target=carregar, daemon=True).start()
        yield

    app = FastAPI(title="PANDORA RAG", version="0.1.0", lifespan=ciclo)

    @app.get("/saude", response_model=Saude)
    def saude() -> Saude:
        if estado["erro"]:
            return Saude(estado=estado["erro"], pronto=False)
        pronto = estado["retriever"] is not None
        n = len(estado["retriever"].registros) if pronto else None
        return Saude(estado="pronto" if pronto else "carregando", pronto=pronto, chunks=n)

    def _responder(p: PerguntaEntrada) -> RespostaSaida:
        t0 = time.perf_counter()
        with trava:
            hits = estado["retriever"].buscar(p.pergunta, p.k)
            resp = responder(
                estado["gateway"], llm, pergunta_para_llm(p.pergunta, p.contexto), hits,
                limiar_abstencao=limiar_abstencao,
            )
        return RespostaSaida(
            texto=resp.texto,
            abstencao=resp.abstencao,
            motivo=motivo_da(resp),
            citacoes=[CitacaoSaida(**c.__dict__) for c in resp.citacoes],
            modelo=resp.modelo,
            latencia_s=round(time.perf_counter() - t0, 2),
        )

    @app.post("/responder", response_model=RespostaSaida)
    async def responder_pergunta(p: PerguntaEntrada) -> RespostaSaida:
        if estado["erro"]:
            raise HTTPException(503, f"RAG indisponível: {estado['erro']}")
        if estado["retriever"] is None:
            raise HTTPException(503, "RAG ainda carregando os modelos")
        if not p.pergunta.strip():
            raise HTTPException(422, "pergunta vazia")
        try:
            return await run_in_threadpool(_responder, p)
        except Exception as exc:
            raise HTTPException(502, f"falha ao gerar a resposta: {type(exc).__name__}") from exc

    return app


def app_padrao() -> FastAPI:
    """Fábrica para `uvicorn --factory`: monta o serviço com os componentes reais."""
    from pandora_rag.config import LIMIAR_ABSTENCAO
    from pandora_rag.montagem import LLM_PADRAO, montar_gateway, montar_retriever

    return criar_app(montar_retriever, montar_gateway, LLM_PADRAO, LIMIAR_ABSTENCAO)
