"""Sinais de recuperação para abstenção: nota do reranker, nota vetorial e nota RRF do melhor chunk.

Gera um arquivo com os sinais de cada pergunta do dev.v1 (e do golden, só para registrar a distribuição;
o limiar não é escolhido nele). O limiar é escolhido no dev e depois congelado.
"""
from __future__ import annotations

import json

from evals.llm_run import K, recuperar_tudo
from evals.recuperacao_run import RAIZ

SAIDA = RAIZ / "training" / "abstencao" / "sinais_dev.jsonl"


def sinais(pares) -> list[dict]:
    out = []
    for x, hits in pares:
        top = hits[0]
        out.append({"id": x["id"], "tipo": x["tipo"], "deve_abster": x["deve_abster"],
                    "rerank": top.score_rerank, "vetor": top.score_vetor, "rrf": top.score,
                    "rerank_top2": hits[1].score_rerank if len(hits) > 1 else None})
    return out


if __name__ == "__main__":
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    dados = sinais(recuperar_tudo())
    SAIDA.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in dados), encoding="utf-8")
    fora = [d["rerank"] for d in dados if d["deve_abster"]]
    dentro = sorted(d["rerank"] for d in dados if not d["deve_abster"])
    print("fora de domínio rerank:", sorted(round(v, 2) for v in fora))
    print("dentro (min, p10, mediana):", round(dentro[0], 2), round(dentro[len(dentro)//10], 2), round(dentro[len(dentro)//2], 2))
