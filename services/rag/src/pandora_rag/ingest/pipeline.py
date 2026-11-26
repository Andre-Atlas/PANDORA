"""Orquestração do povoamento: reindexar com trava, monitorar fontes e promover candidatas.

A reindexação testa em lotes, sempre contra o índice atual:
1. só as mudanças das fontes que já estão no manifesto;
2. cada grupo de candidatas (por origem), por cima do que já passou. Um grupo que falha é dividido
   ao meio até isolar a candidata que piora a busca.
Como toda comparação é com o índice atual, a soma das quedas nunca passa da tolerância.
"""
from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

import httpx

from pandora_rag.config import CANDIDATAS_PATH, DB_URL, FONTES_PATH, LOCK_PATH
from pandora_rag.ingest import trava
from pandora_rag.ingest.collect import agora, ler_lock, salvar_lock
from pandora_rag.ingest.fontes import (
    acrescentar_fontes,
    carregar_candidatas,
    carregar_fontes,
    salvar_candidatas,
)

logger = logging.getLogger("pandora.pipeline")
TABELA, CANDIDATA, ANTERIOR = "chunks", "chunks_candidato", "chunks_anterior"
URL_RAG = "http://127.0.0.1:8010"


@dataclass
class Teste:
    passou: bool
    mudou: bool
    veredito: trava.Veredito | None = None
    resumo: str = ""


@dataclass
class ResultadoReindexacao:
    trocou: bool = False
    motivo: str = ""
    promovidas: list[str] = field(default_factory=list)
    barradas: dict[str, str] = field(default_factory=dict)
    incremental: str = ""
    veredito: trava.Veredito | None = None
    lotes: list[dict] = field(default_factory=list)
    retidas: str = ""  # mudanças das fontes atuais que não passaram e ficaram fora
    recarga: str = ""
    relatorio: str = ""


def selecionar(testar: Callable[[list], Teste], grupos: list[list], eco=print) -> tuple[Teste, list, dict[str, str], list[dict]]:
    """Escolhe as candidatas que entram. `testar(candidatas)` monta e avalia fontes atuais + candidatas.

    Devolve o teste das fontes atuais sozinhas, as aceitas, as barradas (id -> motivo) e o histórico.
    """
    historico: list[dict] = []
    base = testar([])
    historico.append({"lote": "fontes atuais", "passou": base.passou, "mudou": base.mudou, "resumo": base.resumo})
    if not base.passou:
        motivo = "; ".join(base.veredito.motivos) if base.veredito else base.resumo
        return base, [], {c.id: f"não testada: as fontes atuais já falharam ({motivo})" for g in grupos for c in g}, historico
    aceitas: list = []
    barradas: dict[str, str] = {}
    fila = [g for g in grupos if g]
    while fila:
        lote = fila.pop(0)
        t = testar(aceitas + lote)
        ids = [c.id for c in lote]
        historico.append({"lote": ids, "passou": t.passou, "resumo": t.resumo})
        eco(f"  lote de {len(lote)}: {'passou' if t.passou else 'barrado'} ({t.resumo})")
        if t.passou:
            aceitas += lote
        elif len(lote) > 1:
            meio = len(lote) // 2
            fila[:0] = [lote[:meio], lote[meio:]]  # divide ao meio para achar a culpada
        else:
            motivo = "; ".join(t.veredito.motivos) if t.veredito else t.resumo
            barradas[lote[0].id] = f"piora a busca: {motivo}"
    return base, aceitas, barradas, historico


def pedir_recarga(url: str = URL_RAG, token: str | None = None) -> str:
    cab = {"x-pandora-admin": token} if token else {}
    try:
        r = httpx.post(f"{url}/recarregar", headers=cab, timeout=600)
        return f"{r.status_code} {r.text[:200]}"
    except httpx.HTTPError as erro:
        return f"serviço não recarregado ({type(erro).__name__}); reinicie o `servir` ou chame POST /recarregar"


def reindexar(
    modelo: str,
    estrategia: str = "estrutural",
    promover: bool = True,
    rerank: bool = False,
    tolerancia: float = trava.TOLERANCIA,
    recarregar_servico: bool = True,
    token: str | None = None,
    eco=print,
    retestar: bool = False,
) -> ResultadoReindexacao:
    import numpy as np

    from pandora_rag.index.embedder import Embedder
    from pandora_rag.index.incremental import atualizar
    from pandora_rag.index.registro import montar_registros
    from pandora_rag.index.store import PgVectorStore
    from pandora_rag.retrieve.hybrid import IndiceBM25, Reranker, Retriever

    res = ResultadoReindexacao()
    fontes = carregar_fontes()
    candidatas = carregar_candidatas() if promover else []
    hoje = date.today().isoformat()
    promoviveis = [c for c in candidatas if c.testavel(hoje, 0 if retestar else 30)]
    for c in candidatas:
        if c.confianca != "alta":
            res.barradas[c.id] = f"confiança {c.confianca}: {'; '.join(c.motivos[-2:])}"
        elif c not in promoviveis:
            res.barradas[c.id] = f"recusada pela trava em {c.barrada_em}; volta a ser testada em 30 dias (ou com --retestar)"
    prontas = trava.preparar_candidatas(promoviveis)
    for c in promoviveis:
        if c not in prontas:
            res.barradas[c.id] = "bruto ou texto da candidata não encontrado em data/crawl"
    if prontas:
        # a entrada no lock já agora, para a data de coleta do teste ser a mesma da fonte promovida
        lock, momento = ler_lock(LOCK_PATH), agora()
        for c in prontas:
            lock["fontes"][c.id] = trava.entrada_lock(c, momento)
        salvar_lock(lock, LOCK_PATH)
    eco(f"fontes: {len(fontes)} no manifesto + {len(prontas)} candidatas em teste")

    aceitas: list = []
    try:
        emb = Embedder(modelo)
        rr = Reranker() if rerank else None
        cache: dict[str, np.ndarray] = {}

        def embedar(regs):
            textos = [r.texto_indexado(True) for r in regs]
            chaves = [hashlib.sha256(t.encode()).hexdigest() for t in textos]
            faltam = [i for i, k in enumerate(chaves) if k not in cache]
            if faltam:
                for i, v in zip(faltam, emb.passagens([textos[i] for i in faltam])):
                    cache[chaves[i]] = v
            return np.stack([cache[k] for k in chaves])

        cand = PgVectorStore(DB_URL, CANDIDATA, emb.dim)
        tem_atual = cand.conn.execute("SELECT to_regclass(%s) IS NOT NULL", [TABELA]).fetchone()[0]
        itens = trava.carregar_golden()
        atual_m = atual_pp = None
        if tem_atual:
            eco(f"avaliando o índice atual com {len(itens)} perguntas do golden…")
            pg_atual = PgVectorStore(DB_URL, TABELA, emb.dim)
            regs_atual = pg_atual.carregar_registros()
            atual_m, atual_pp = trava.avaliar_retriever(Retriever(pg_atual, IndiceBM25(regs_atual), emb, rr), itens)
            pg_atual.conn.close()

        congelar = {"ativo": False}  # modo de reserva: fontes atuais ficam como estão no índice

        def registros_de(lote: list):
            novos = montar_registros(estrategia, [c.como_fonte() for c in lote]) if lote else []
            if congelar["ativo"]:
                return [r.model_copy() for r in regs_atual] + novos
            return montar_registros(estrategia, fontes) + novos

        def testar(lote: list) -> Teste:
            registros = registros_de(lote)
            problemas = trava.checar_corpus(registros)
            if problemas:
                return Teste(False, True, None, "conferência do corpus: " + " | ".join(problemas))
            cand.copiar_de(TABELA)
            rel = atualizar(cand, registros, embedar)
            if not rel.mudou:
                return Teste(True, False, None, rel.resumo())
            regs_cand = cand.carregar_registros()
            cand_m, cand_pp = trava.avaliar_retriever(Retriever(cand, IndiceBM25(regs_cand), emb, rr), itens)
            v = trava.julgar(atual_m, cand_m, tolerancia, atual_pp, cand_pp)
            return Teste(v.passou, True, v, rel.resumo() + " | " + "; ".join(v.motivos))

        grupos: dict[str, list] = {}
        for c in prontas:
            grupos.setdefault(c.origem or "crawler", []).append(c)
        eco("testando em lotes (fontes atuais primeiro, depois cada grupo de candidatas)…")
        base, aceitas, barradas, res.lotes = selecionar(testar, list(grupos.values()), eco)
        eco(f"  fontes atuais: {'passou' if base.passou else 'barrado'} ({base.resumo})")
        if not base.passou:
            res.retidas = base.resumo
            if not prontas or not tem_atual:
                res.barradas.update(barradas)
                res.veredito = base.veredito
                res.motivo = "as mudanças das fontes atuais pioram a busca: nada foi trocado"
                return _fim(res, prontas)
            eco("  as mudanças das fontes atuais ficam retidas; testando as candidatas sobre o índice atual…")
            congelar["ativo"] = True
            base, aceitas, barradas, lotes = selecionar(testar, list(grupos.values()), eco)
            res.lotes += lotes
        res.barradas.update(barradas)
        recusadas = [c for c in prontas if c.id in barradas and barradas[c.id].startswith("piora a busca")]
        for c in recusadas:
            c.barrada_em = hoje
            c.motivos = [m for m in c.motivos if not m.startswith("trava:")] + [f"trava: {barradas[c.id][:160]}"]
        if recusadas:
            salvar_candidatas(candidatas, CANDIDATAS_PATH)
        if not base.mudou and not aceitas:
            cand.conn.execute(f"DROP TABLE IF EXISTS {CANDIDATA}")
            res.motivo = "nada mudou ou nenhuma candidata passou: o índice atual continua valendo"
            return _fim(res, prontas, salvar=bool(prontas))

        # remonta o estado final aceito (o último lote testado pode ter sido barrado)
        final = testar(aceitas)
        res.veredito, res.incremental = final.veredito, final.resumo
        if not final.passou:  # não deveria acontecer: cada lote aceito já passou contra o atual
            res.motivo = "o conjunto final não passou na trava: nada foi trocado"
            return _fim(res, prontas)
        rejeitadas = [c for c in prontas if c not in aceitas]
        if aceitas:
            _promover(aceitas, candidatas)
            res.promovidas = [c.id for c in aceitas]
        _desfazer(rejeitadas)
        cand.trocar_com(TABELA, ANTERIOR)
        cand.conn.close()
        res.trocou = True
        res.motivo = f"índice trocado ({len(aceitas)} candidata(s) promovida(s))"
        if res.retidas:
            res.motivo += "; as mudanças das fontes atuais foram retidas porque pioram a busca"
        if recarregar_servico:
            res.recarga = pedir_recarga(token=token)
            eco(f"recarga do serviço: {res.recarga}")
        return _fim(res, [])
    except Exception:
        if not res.trocou:
            _desfazer(prontas)
        raise


def _promover(prontas, todas) -> None:
    acrescentar_fontes([c.como_fonte() for c in prontas], FONTES_PATH)
    ids = {c.id for c in prontas}
    salvar_candidatas([c for c in todas if c.id not in ids], CANDIDATAS_PATH)


def _desfazer(prontas) -> None:
    if not prontas:
        return
    trava.desfazer_candidatas(prontas)
    lock = ler_lock(LOCK_PATH)
    for c in prontas:
        lock["fontes"].pop(c.id, None)
    salvar_lock(lock, LOCK_PATH)


def _fim(res: ResultadoReindexacao, desfazer, salvar: bool = True) -> ResultadoReindexacao:
    if desfazer and not res.trocou:
        _desfazer(desfazer)
    if not salvar:
        return res
    pasta = trava.salvar_relatorio({
        "data": date.today().isoformat(), "trocou": res.trocou, "motivo": res.motivo, "incremental": res.incremental,
        "promovidas": res.promovidas, "barradas": res.barradas, "retidas": res.retidas, "lotes": res.lotes,
        "veredito": res.veredito,
        "recarga": res.recarga,
    })
    res.relatorio = str(pasta)
    return res
