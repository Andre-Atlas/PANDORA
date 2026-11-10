"""Ajuste fino do bge-m3 com negativos difíceis, a partir das perguntas de treino (partição "treino").

Negativo difícil: um chunk que o próprio modelo base ranqueia entre os 2º e 30º para a pergunta,
que não é o chunk de origem e que não cobre o trecho-ouro (evita falso negativo).
Perda: MultipleNegativesRankingLoss (lotes em que os outros positivos também são negativos).
Os pesos vão para training/embeddings/saida/ (ignorado pelo git); a avaliação é feita pelo executor de recuperação.

Uso (de services/rag): PYTHONPATH=../.. uv run python ../../training/embeddings/treinar.py --epocas 1
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np

from evals.metrics.recuperacao import Ouro, cobertura
from pandora_rag.index.build import construir
from pandora_rag.index.registro import montar_registros

RAIZ = Path(__file__).resolve().parents[2]
TREINO = RAIZ / "training" / "dados" / "treino.v1.jsonl"
SAIDA = RAIZ / "training" / "embeddings" / "saida"
BASE = "BAAI/bge-m3"


def pares(modelo_base: str, semente: int) -> list[tuple[str, str, str]]:
    itens = [x for x in map(json.loads, TREINO.read_text(encoding="utf-8").splitlines()) if x["particao"] == "treino"]
    registros = montar_registros()
    por_id = {r.id: r for r in registros}
    store, _, emb = construir("estrutural", modelo_base, True)
    consultas = emb.consultas([x["pergunta"] for x in itens])
    rng = random.Random(semente)
    saida = []
    for x, q in zip(itens, consultas):
        pos = por_id[x["chunk_origem"]]
        ranking = [i for i, _ in store.buscar_vetor(q, 30)]
        candidatos = []
        for i in ranking[1:]:  # pula o 1º: costuma ser o próprio positivo ou um quase-duplicado
            r = store.registros[i]
            if r.id == pos.id or cobertura(x["trecho_ouro"], r.texto) >= 0.4:
                continue
            candidatos.append(r)
        if candidatos:
            neg = rng.choice(candidatos)
            saida.append((x["pergunta"], pos.texto_indexado(True), neg.texto_indexado(True)))
    return saida


def treinar(epocas: int, lote: int, lr: float, nome: str, semente: int = 7) -> Path:
    import torch
    from sentence_transformers import InputExample, SentenceTransformer, losses
    from torch.utils.data import DataLoader

    random.seed(semente)
    dados = [InputExample(texts=list(t)) for t in pares(BASE, semente)]
    print("pares de treino:", len(dados), flush=True)
    dispositivo = "mps" if torch.backends.mps.is_available() else "cpu"
    modelo = SentenceTransformer(BASE, device=dispositivo)
    modelo.max_seq_length = 384
    # A camada de embeddings (~250 mil tokens, quase metade dos parâmetros) fica congelada: cabe na memória do MPS
    for p in modelo[0].auto_model.embeddings.parameters():
        p.requires_grad = False
    carga = DataLoader(dados, shuffle=True, batch_size=lote)
    perda = losses.MultipleNegativesRankingLoss(modelo)
    destino = SAIDA / nome
    destino.mkdir(parents=True, exist_ok=True)
    modelo.fit(train_objectives=[(carga, perda)], epochs=epocas, warmup_steps=max(1, len(carga) // 10),
               optimizer_params={"lr": lr}, show_progress_bar=True)
    modelo.save(str(destino))
    (destino / "treino.json").write_text(json.dumps({"base": BASE, "epocas": epocas, "lote": lote, "lr": lr,
                                                    "pares": len(dados), "semente": semente}, indent=1), encoding="utf-8")
    print("salvo em", destino, flush=True)
    return destino


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--epocas", type=int, default=1)
    ap.add_argument("--lote", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--nome", default="bge-m3-ft-v1")
    a = ap.parse_args()
    treinar(a.epocas, a.lote, a.lr, a.nome)
