"""Ablação dos estágios 0 a 4 da recuperação, sempre no dev.v1. Cada linha vira uma execução em evals/runs.

Uso (de services/rag): PYTHONPATH=../.. uv run python -m evals.ablacao [estagio ...]
"""
from __future__ import annotations

import json
import sys

from evals.recuperacao_run import RAIZ, rodar
from pandora_rag.retrieve.hybrid import Parametros

MINILM = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BGE = "BAAI/bge-m3"
E5 = "intfloat/multilingual-e5-large"
LEGAL = "rufimelo/Legal-BERTimbau-sts-large-ma-v3"
HIB = Parametros()
VET = Parametros(usar_bm25=False)
BM = Parametros(usar_vetor=False)

# (estágio, nome, estratégia, modelo, parâmetros, cabeçalho, k1, b)
CONFIGS = [
    ("0", "0-baseline-fixo-minilm-vetor", "fixo", MINILM, VET, False, 1.5, 0.75),
    ("1", "1a-fixo-bge-hibrido", "fixo", BGE, HIB, False, 1.5, 0.75),
    ("1", "1b-estrutural-bge-hibrido-sem-cabecalho", "estrutural", BGE, HIB, False, 1.5, 0.75),
    ("1", "1c-estrutural-bge-hibrido", "estrutural", BGE, HIB, True, 1.5, 0.75),
    ("2", "2a-estrutural-minilm-hibrido", "estrutural", MINILM, HIB, True, 1.5, 0.75),
    ("2", "2b-estrutural-e5-hibrido", "estrutural", E5, HIB, True, 1.5, 0.75),
    ("2", "2c-estrutural-legalbertimbau-hibrido", "estrutural", LEGAL, HIB, True, 1.5, 0.75),
    ("2", "2d-estrutural-bge-vetor", "estrutural", BGE, VET, True, 1.5, 0.75),
    ("3", "3a-estrutural-bm25", "estrutural", BGE, BM, True, 1.5, 0.75),
    ("3", "3b-hibrido-pesos-1-2", "estrutural", BGE, Parametros(peso_vetor=1.0, peso_bm25=2.0), True, 1.5, 0.75),
    ("3", "3c-hibrido-pesos-2-1", "estrutural", BGE, Parametros(peso_vetor=2.0, peso_bm25=1.0), True, 1.5, 0.75),
    ("3", "3d-hibrido-k1-1.2-b-0.75", "estrutural", BGE, HIB, True, 1.2, 0.75),
    ("3", "3e-hibrido-k1-2.0-b-0.75", "estrutural", BGE, HIB, True, 2.0, 0.75),
    ("3", "3f-hibrido-k1-1.5-b-0.5", "estrutural", BGE, HIB, True, 1.5, 0.5),
    ("3", "3g-hibrido-rrf-k-30", "estrutural", BGE, Parametros(rrf_k=30), True, 1.5, 0.75),
    ("4", "4a-hibrido-rerank-bge", "estrutural", BGE, HIB, True, 1.5, 0.75),
]
COLS = ["hit@1", "hit@3", "hit@5", "hit@10", "mrr", "ndcg@10", "artigo_top3"]


def main(estagios: set[str]):
    linhas = []
    reranker = None
    for est, nome, estr, modelo, params, cab, k1, b in CONFIGS:
        if estagios and est not in estagios:
            continue
        rr = None
        if est == "4":
            from pandora_rag.retrieve.hybrid import Reranker
            reranker = reranker or Reranker()
            rr = reranker
        r = rodar(nome, estr, modelo, params, "dev.v1", cab, k1, b, rr)
        g = r["geral"]
        linhas.append((nome, g))
        print(nome, {c: round(g[c], 3) for c in COLS}, flush=True)
    tabela = "| Configuração | " + " | ".join(COLS) + " |\n|---|" + "---|" * len(COLS) + "\n"
    for nome, g in linhas:
        tabela += f"| {nome} | " + " | ".join(f"{g[c]:.3f}" for c in COLS) + " |\n"
    (RAIZ / "evals" / "runs" / f"tabela-estagios-{'-'.join(sorted(estagios)) or 'todos'}.md").write_text(tabela, encoding="utf-8")
    print(tabela)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
