"""Gera a tabela de fontes (markdown) e a exportação dos chunks (jsonl) da base de conhecimento.

Uso, a partir da raiz do repositório:
    uv run --project services/rag python docs/entregas/02-base-conhecimento-e-prototipo-rag/gerar_artefatos.py [--chunks SAIDA.jsonl]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[3]
RAG = RAIZ / "services" / "rag"
SAIDA_MD = Path(__file__).with_name("fontes.md")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks", type=Path, help="grava todos os chunks indexáveis em jsonl")
    args = ap.parse_args()

    from pandora_rag.index.registro import montar_registros

    fontes = yaml.safe_load((RAG / "fontes.yaml").read_text(encoding="utf-8"))["fontes"]
    lock = json.loads((RAG / "corpus.lock").read_text(encoding="utf-8"))["fontes"]
    regs = montar_registros("estrutural")
    por_fonte = Counter(r.fonte_id for r in regs)

    linhas = ["| # | Documento | Órgão | Tipo | Referência | Chunks | SHA-256 (início) | Link |", "|---|---|---|---|---|---|---|---|"]
    for n, f in enumerate(fontes, start=1):
        l = lock.get(f["id"], {})
        url = f.get("url_citacao") or f["url"]
        ressalva = " ⚠" if f.get("ressalva") else ""
        linhas.append(
            f"| {n} | {f['titulo']}{ressalva} | {f['orgao']} | {f['tipo']} | {f.get('data_referencia_normativa', '')} | "
            f"{por_fonte.get(f['id'], 0)} | `{l.get('sha256_bruto', '')[:12]}` | [fonte]({url}) |"
        )
    total = sum(por_fonte.values())
    SAIDA_MD.write_text("\n".join(linhas) + f"\n\n**{len(fontes)} documentos-fonte, {total} chunks indexáveis.**\n", encoding="utf-8")
    print(f"{SAIDA_MD.name}: {len(fontes)} fontes, {total} chunks")

    if args.chunks:
        with args.chunks.open("w", encoding="utf-8") as f:
            for r in regs:
                f.write(json.dumps(r.model_dump() if hasattr(r, 'model_dump') else vars(r), ensure_ascii=False, default=str) + "\n")
        print(f"{args.chunks}: {len(regs)} chunks")


if __name__ == "__main__":
    main()
