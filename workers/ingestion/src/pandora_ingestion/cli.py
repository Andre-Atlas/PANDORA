"""Linha de comando: importa um extrato OFX ou CSV para um arquivo JSONL no esquema único."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from pandora_ingestion.armazem import ArmazemJsonl
from pandora_ingestion.erros import ErroDeIngestao
from pandora_ingestion.importador import importar


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pandora-ingestion", description=__doc__)
    parser.add_argument("arquivo", type=Path, help="extrato em OFX ou CSV")
    parser.add_argument("--saida", type=Path, default=Path("transacoes.jsonl"), help="arquivo JSONL de destino")
    parser.add_argument("--nome", action="append", default=[], help="nome do titular a mascarar (repita se preciso)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        resultado = importar(args.arquivo.name, args.arquivo.read_bytes(), ArmazemJsonl(args.saida), tuple(args.nome))
    except ErroDeIngestao as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1
    print(f"{resultado.lidas} lidas, {resultado.novas} novas, {resultado.repetidas} já importadas")
    for aviso in resultado.avisos:
        print(f"aviso: {aviso}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
