"""Onde ficam as transações já importadas. A porta é pequena; o arquivo JSONL serve à CLI e aos testes."""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from pandora_ingestion.esquema import Transacao


class Armazem(Protocol):
    def chaves(self) -> set[str]: ...

    def adicionar(self, transacoes: Iterable[Transacao]) -> None: ...


class ArmazemJsonl:
    def __init__(self, caminho: Path) -> None:
        self.caminho = caminho

    def chaves(self) -> set[str]:
        if not self.caminho.exists():
            return set()
        with self.caminho.open(encoding="utf-8") as arquivo:
            return {json.loads(linha)["chave"] for linha in arquivo if linha.strip()}

    def adicionar(self, transacoes: Iterable[Transacao]) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.caminho.open("a", encoding="utf-8") as arquivo:
            for t in transacoes:
                arquivo.write(json.dumps(t.como_dict(), ensure_ascii=False) + "\n")
