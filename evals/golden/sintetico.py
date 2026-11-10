"""Perguntas sintéticas de treino: uma por chunk que não está no teste nem no dev.

Cada item é checado pelas mesmas regras do rascunho (trecho literal, número conferido).
Depois, perguntas com similaridade ≥ 0,85 a qualquer pergunta de teste são removidas, e
10% dos artigos são separados como hold-out (nunca entram no treino).
Não há revisão humana: estes dados são para ajuste, não para medir.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from evals.golden import rascunhar as R
from pandora_rag.generate.gateway import Gateway
from pandora_rag.index.registro import montar_registros

RAIZ = Path(__file__).resolve().parents[2]
GOLDEN = RAIZ / "evals" / "golden"
SAIDA = RAIZ / "training" / "dados"
SEMENTE = 20261108
MODELO = "qwen25-14b"
LIMIAR_SIMILAR = 0.85


def usados_no_teste() -> set[str]:
    ids = set()
    for n in ("golden.v1", "dev.v1"):
        for l in (GOLDEN / f"{n}.jsonl").read_text(encoding="utf-8").splitlines():
            ids |= {t["chunk_origem"] for t in json.loads(l)["trechos_ouro"]}
    return ids


def gerar() -> list[dict]:
    regs = montar_registros()
    versao = regs[0].versao_corpus
    teste = usados_no_teste()
    candidatos = [r for r in R.elegiveis(regs) if r.id not in teste]
    g, saida, falhas = Gateway(), [], {}
    for n, r in enumerate(candidatos, 1):
        item, motivo = None, []
        for _ in range(2):
            c = g.gerar(MODELO, R.SISTEMA_NORMATIVA, f"TRECHO ({r.norma}, {r.artigo}):\n{r.texto}", max_tokens=500, json_modo=True)
            it = R.extrair_json(c.texto) or {}
            motivo = R.verificar_item(it, r.texto) if it else ["json_invalido"]
            if not motivo:
                item = it
                break
        if item is None:
            for m in motivo:
                falhas[m] = falhas.get(m, 0) + 1
            continue
        saida.append({"id": f"t-{len(saida) + 1:04d}", "pergunta": item["pergunta"], "resposta": item["resposta"],
                      "trecho_ouro": item["trecho_ouro"], "chunk_origem": r.id, "fonte_id": r.fonte_id,
                      "artigo": r.artigo, "norma": r.norma, "versao_corpus": versao, "gerador": MODELO})
        if n % 50 == 0:
            print(f"{n}/{len(candidatos)} processados, {len(saida)} aprovados", flush=True)
    print("falhas", falhas, flush=True)
    return saida


def filtrar_similares(itens: list[dict]) -> tuple[list[dict], int]:
    """Remove perguntas de treino com cosseno ≥ 0,85 a qualquer pergunta de teste ou entre si."""
    from pandora_rag.index.embedder import Embedder
    import numpy as np

    teste = []
    for n in ("golden.v1", "dev.v1"):
        teste += [json.loads(l)["pergunta"] for l in (GOLDEN / f"{n}.jsonl").read_text(encoding="utf-8").splitlines()]
    emb = Embedder("BAAI/bge-m3")
    v_teste = emb.consultas(teste)
    v_treino = emb.consultas([x["pergunta"] for x in itens])
    manter, fora, vistos = [], 0, []
    for i, x in enumerate(itens):
        if (v_teste @ v_treino[i]).max() >= LIMIAR_SIMILAR:
            fora += 1
            continue
        if vistos and (np.stack(vistos) @ v_treino[i]).max() >= LIMIAR_SIMILAR:
            fora += 1
            continue
        vistos.append(v_treino[i])
        manter.append(x)
    return manter, fora


def separar_holdout(itens: list[dict]) -> list[dict]:
    artigos = sorted({(x["fonte_id"], x["artigo"]) for x in itens}, key=str)
    random.Random(SEMENTE).shuffle(artigos)
    reservados = set(artigos[: max(1, len(artigos) // 10)])
    for x in itens:
        x["particao"] = "holdout" if (x["fonte_id"], x["artigo"]) in reservados else "treino"
    return itens


if __name__ == "__main__":
    bruto = gerar()
    limpo, removidos = filtrar_similares(bruto)
    final = separar_holdout(limpo)
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "treino.v1.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in final), encoding="utf-8")
    from collections import Counter
    print("gerados", len(bruto), "removidos por similaridade", removidos, "final", len(final), Counter(x["particao"] for x in final))
