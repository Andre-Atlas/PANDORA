"""Decisão do LLM (#53): gera respostas com cada candidato local sobre o dev.v1, com a recuperação fixa
(bge-m3 estrutural + bge-reranker-v2-m3, top-5), e mede citação, abstenção, número, ROUGE/BLEU (diagnóstico)
e latência. Cada candidato vira uma execução em evals/runs.

Uso (de services/rag): PYTHONPATH=../.. uv run python -m evals.llm_run [modelo ...]
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from evals.metrics.respostas import CitacaoResposta, abstencao, citacao_valida, taxa
from evals.metrics.textos import acerto_numerico, bleu_sentenca, rouge
from evals.recuperacao_run import GOLDEN, RAIZ, carregar
from pandora_rag.generate.answer import MENSAGEM_ABSTENCAO, Resposta, responder
from pandora_rag.generate.gateway import Gateway
from pandora_rag.index.build import construir
from pandora_rag.retrieve.hybrid import Parametros, Reranker, Retriever

CANDIDATOS = ["qwen25-14b", "gemma3-12b", "llama31-8b"]
K = 5
CONJUNTO = ["dev.v1"]  # preenchido pelo __main__ antes de cada avaliação
LIMIAR_ABSTENCAO = json.loads((RAIZ / "training" / "abstencao" / "limiar.json").read_text(encoding="utf-8"))["limiar"]


def recuperar_tudo(k: int = K, conjunto: str = "dev.v1") -> list[tuple[dict, list]]:
    store, bm25, emb = construir("estrutural", "BAAI/bge-m3", True)
    retr = Retriever(store, bm25, emb, Reranker(), Parametros(), True)
    itens = [x for x in map(json.loads, (GOLDEN / f"{conjunto}.jsonl").read_text(encoding="utf-8").splitlines())]
    return [(x, retr.buscar(x["pergunta"], k)) for x in itens]


def avaliar_modelo(modelo: str, pares: list, g: Gateway, sufixo: str = "", k: int = K, max_tokens: int = 700) -> dict:
    linhas, detalhe, lat = [], [], []
    for x, hits in pares:
        if hits and hits[0].score_rerank is not None and hits[0].score_rerank < LIMIAR_ABSTENCAO:
            r = Resposta(MENSAGEM_ABSTENCAO, True, [], hits, "portao", 0.0, 0.0)  # portão: recuperação fraca, LLM nem chamado
        else:
            r = responder(g, modelo, x["pergunta"], hits[:k], max_tokens=max_tokens)
        lat.append(r.latencia_s)
        dev_abster = x["deve_abster"]
        cit = [CitacaoResposta(c.norma, c.link, c.artigo) for c in r.citacoes]
        linha = {"abstencao_pred": r.abstencao, "deve_abster": dev_abster}
        if not dev_abster:
            linha["citacao_valida"] = citacao_valida(r.texto, cit, exige_artigo=False) if not r.abstencao else False
            num = acerto_numerico(r.texto, x["resposta_referencia"] or "")
            if num is not None:
                linha["numero"] = num
            rg = rouge(r.texto, x["resposta_referencia"] or "")
            linha["rougeL"] = rg["rougeL"]
            linha["bleu"] = bleu_sentenca(r.texto, x["resposta_referencia"] or "")
        linhas.append(linha)
        detalhe.append({"id": x["id"], "tipo": x["tipo"], "tema": x["tema"], "pergunta": x["pergunta"],
                        "resposta": r.texto, "citacoes": [c.n for c in r.citacoes], "latencia_s": round(r.latencia_s, 2),
                        **{k: v for k, v in linha.items() if k != "deve_abster"}})
    norm = [l for l in linhas if not l["deve_abster"]]
    fora = [l for l in linhas if l["deve_abster"]]
    nums = [l["numero"] for l in norm if "numero" in l]
    res = {
        "citacao_valida": taxa([l["citacao_valida"] for l in norm]),
        "recusa_indevida": taxa([l["abstencao_pred"] for l in norm]),
        "abstencao_correta": taxa([l["abstencao_pred"] for l in fora]),
        "acerto_numerico": sum(nums) / len(nums) if nums else float("nan"),
        "rougeL": statistics.mean(l["rougeL"] for l in norm),
        "bleu": statistics.mean(l["bleu"] for l in norm),
        "latencia_media_s": statistics.mean(lat),
        "latencia_p95_s": sorted(lat)[int(0.95 * (len(lat) - 1))],
        "n": len(linhas),
    }
    pasta = RAIZ / "evals" / "runs" / f"{date.today():%Y-%m-%d}-llm-{modelo}{sufixo}"
    pasta.mkdir(parents=True, exist_ok=True)
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    (pasta / "config.json").write_text(json.dumps({"modelo": modelo, "recuperacao": "bge-m3 estrutural + bge-reranker-v2-m3",
                                                  "k": k, "max_tokens": max_tokens, "conjunto": CONJUNTO[0], "limiar_abstencao": LIMIAR_ABSTENCAO, "git": sha}, indent=1), encoding="utf-8")
    (pasta / "metrics.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (pasta / "por_pergunta.jsonl").write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in detalhe), encoding="utf-8")
    return res


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("modelos", nargs="*", default=CANDIDATOS)
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--max-tokens", type=int, default=700)
    ap.add_argument("--sufixo", default="")
    ap.add_argument("--conjunto", default="dev.v1")
    a = ap.parse_args()
    CONJUNTO[0] = a.conjunto
    t0 = time.time()
    pares = recuperar_tudo(max(a.k, K), a.conjunto)
    print("recuperação pronta em", round(time.time() - t0), "s", flush=True)
    g = Gateway()
    for m in a.modelos:
        r = avaliar_modelo(m, pares, g, a.sufixo, a.k, a.max_tokens)
        print(m, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
