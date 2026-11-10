"""Roda uma configuração de recuperação contra o dev (ou o golden) e grava a execução em evals/runs.

Uso (de services/rag): PYTHONPATH=../.. uv run python -m evals.recuperacao_run --nome baseline \
    --estrategia fixo --modelo sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --so-vetor
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import asdict
from datetime import date
from pathlib import Path

from evals.metrics.recuperacao import Ouro, acerto_artigo, avaliar, media
from pandora_rag.index.build import construir
from pandora_rag.retrieve.hybrid import Parametros, Retriever

RAIZ = Path(__file__).resolve().parents[1]
GOLDEN = RAIZ / "evals" / "golden"


def carregar(conjunto: str) -> list[dict]:
    linhas = (GOLDEN / f"{conjunto}.jsonl").read_text(encoding="utf-8").splitlines()
    return [x for x in map(json.loads, linhas) if not x["deve_abster"]]


def git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()


def rodar(nome: str, estrategia: str, modelo: str, params: Parametros, conjunto: str = "dev.v1", cabecalho: bool = True,
          k1: float = 1.5, b: float = 0.75, reranker=None, k: int = 10) -> dict:
    store, bm25, emb = construir(estrategia, modelo, cabecalho, k1, b)
    retr = Retriever(store, bm25, emb, reranker, params, cabecalho)
    itens = carregar(conjunto)
    linhas, detalhe, t0 = [], [], time.time()
    for x in itens:
        hits = retr.buscar(x["pergunta"], k)
        rec = [(h.registro.fonte_id, h.registro.texto) for h in hits]
        ouros = [Ouro(t["fonte_id"], t["texto"], x["artigo"]) for t in x["trechos_ouro"]]
        m = avaliar(rec, ouros)
        m["artigo_top3"] = acerto_artigo([(h.registro.fonte_id, h.registro.artigo) for h in hits], ouros, 3)
        linhas.append(m)
        detalhe.append({"id": x["id"], "tipo": x["tipo"], "tema": x["tema"], **m, "top": [h.registro.id for h in hits[:5]]})
    resumo = media(linhas)
    resumo["n"] = len(itens)
    resumo["latencia_media_s"] = round((time.time() - t0) / max(len(itens), 1), 3)
    por_tipo = {t: media([l for l, d in zip(linhas, detalhe) if d["tipo"] == t]) for t in {d["tipo"] for d in detalhe}}
    pasta = RAIZ / "evals" / "runs" / f"{date.today():%Y-%m-%d}-{nome}"
    pasta.mkdir(parents=True, exist_ok=True)
    config = {"nome": nome, "estrategia": estrategia, "modelo": modelo, "parametros": asdict(params), "conjunto": conjunto,
              "cabecalho": cabecalho, "k1": k1, "b": b, "reranker": getattr(reranker, "modelo", None) and reranker.modelo,
              "git": git_sha(), "versao_corpus": store.registros[0].versao_corpus, "chunks": len(store.registros),
              "golden_lock": json.loads((GOLDEN / "golden.lock").read_text())}
    (pasta / "config.json").write_text(json.dumps(config, indent=1, ensure_ascii=False), encoding="utf-8")
    (pasta / "metrics.json").write_text(json.dumps({"geral": resumo, "por_tipo": por_tipo}, indent=1), encoding="utf-8")
    (pasta / "por_pergunta.jsonl").write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in detalhe), encoding="utf-8")
    return {"geral": resumo, "por_tipo": por_tipo, "pasta": str(pasta.relative_to(RAIZ))}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", required=True)
    ap.add_argument("--estrategia", default="estrutural")
    ap.add_argument("--modelo", default="BAAI/bge-m3")
    ap.add_argument("--conjunto", default="dev.v1")
    ap.add_argument("--so-vetor", action="store_true")
    ap.add_argument("--so-bm25", action="store_true")
    ap.add_argument("--sem-cabecalho", action="store_true")
    ap.add_argument("--rerank", action="store_true")
    a = ap.parse_args()
    p = Parametros(usar_bm25=not a.so_vetor, usar_vetor=not a.so_bm25)
    rr = None
    if a.rerank:
        from pandora_rag.retrieve.hybrid import Reranker
        rr = Reranker()
    r = rodar(a.nome, a.estrategia, a.modelo, p, a.conjunto, not a.sem_cabecalho, reranker=rr)
    print(json.dumps(r["geral"], indent=1)); print(r["pasta"])
