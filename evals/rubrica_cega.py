"""Rubrica 0/1/2 às cegas para o LLM × RAG (semana 3).

  exportar: monta evals/runs/<data>-s3-rubrica/folha.md com as respostas das 4 execuções em ordem aleatória
            (rótulos A-D por pergunta) e guarda a chave em chave.json. Quem avalia lê só a folha.
  pontuar:  lê notas.csv (id,rotulo,nota) e devolve a média por teste e a diferença pareada com IC.

Nota: 2 = correta e completa frente à referência e aos trechos de ouro; 1 = parcialmente correta ou incompleta,
sem erro grave, ou trecho bruto da fonte que contém a resposta mas não responde à pergunta; 0 = errada, com
afirmação inventada (norma, artigo ou número), trecho que não responde, ou recusa de pergunta respondível.
Avaliador desta rodada: Claude (Opus 5.5), às cegas quanto ao rótulo; o estilo denuncia parte dos modos
(o RAG sozinho começa com "Segundo …"), então a cegueira é parcial. Recomendada a revisão humana de uma amostra.

Uso (de services/rag): PYTHONPATH=../.. uv run python -m evals.rubrica_cega exportar|pontuar
"""
from __future__ import annotations

import csv
import json
import random
import sys

from evals.metrics.estatistica import ic_bootstrap, ic_diferenca_pareada
from evals.recuperacao_run import RAIZ

RUNS = RAIZ / "evals" / "runs"
TESTES = ["t1-llm-sozinho", "t2-rag-sozinho", "t3-rag-llm-14b", "t4-rag-llm-7b"]
PASTA = RUNS / "2026-11-12-s3-rubrica"


def carregar() -> dict[str, dict[str, dict]]:
    out = {}
    for t in TESTES:
        pasta = next(RUNS.glob(f"*-s3-{t}"))
        out[t] = {d["id"]: d for d in map(json.loads, (pasta / "por_pergunta.jsonl").read_text(encoding="utf-8").splitlines())}
    return out


def exportar() -> None:
    golden = {x["id"]: x for x in map(json.loads, (RAIZ / "evals/golden/dev.v1.jsonl").read_text(encoding="utf-8").splitlines())}
    res, rng = carregar(), random.Random(12)
    chave, linhas = {}, ["# Folha de avaliação às cegas\n"]
    for qid, x in golden.items():
        if x["deve_abster"]:
            continue
        ordem = TESTES[:]
        rng.shuffle(ordem)
        chave[qid] = dict(zip("ABCD", ordem))
        ouro = " | ".join(t["texto"] for t in x["trechos_ouro"])
        linhas.append(f"## {qid} ({x['tipo']})\n\n**Pergunta:** {x['pergunta']}\n\n**Referência:** {x['resposta_referencia']}\n\n"
                      f"**Trecho de ouro:** {ouro[:600]}\n")
        for rot, t in chave[qid].items():
            linhas.append(f"**{rot}:** {' '.join(res[t][qid]['resposta'].split())}\n")
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "folha.md").write_text("\n".join(linhas), encoding="utf-8")
    (PASTA / "chave.json").write_text(json.dumps(chave, indent=1), encoding="utf-8")
    print(len(chave), "perguntas exportadas para", PASTA / "folha.md")


def pontuar() -> None:
    chave = json.loads((PASTA / "chave.json").read_text(encoding="utf-8"))
    notas: dict[str, dict[str, int]] = {t: {} for t in TESTES}
    with (PASTA / "notas.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            notas[chave[r["id"]][r["rotulo"]]][r["id"]] = int(r["nota"])
    ids = sorted(chave)
    resumo = {}
    for t in TESTES:
        v = [notas[t][i] / 2 for i in ids]
        m, lo, hi = ic_bootstrap(v)
        resumo[t] = {"media_0a1": round(m, 3), "ic95": [round(lo, 3), round(hi, 3)],
                     "dist": {n: sum(notas[t][i] == n for i in ids) for n in (0, 1, 2)}}
    base = [notas["t1-llm-sozinho"][i] / 2 for i in ids]
    for t in TESTES[1:]:
        d, lo, hi = ic_diferenca_pareada([notas[t][i] / 2 for i in ids], base)
        resumo[t]["ganho_sobre_llm_pp"] = [round(100 * d, 1), round(100 * lo, 1), round(100 * hi, 1)]
    (PASTA / "resultado.json").write_text(json.dumps(resumo, indent=1), encoding="utf-8")
    print(json.dumps(resumo, indent=1))


if __name__ == "__main__":
    {"exportar": exportar, "pontuar": pontuar}[sys.argv[1]]()
