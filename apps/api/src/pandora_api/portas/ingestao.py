"""Portas para a ingestão (#57, #66) e o classificador (#68).

Enquanto essas issues não chegam, a API usa adaptadores provisórios
(`adaptadores/ingestao`). Quem entregar o adaptador de verdade só precisa
cumprir estes contratos e trocar a montagem em `principal.py`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from pandora_api.dominio.transacao import Categoria, Transacao, TransacaoLida


@dataclass(frozen=True)
class LeituraExtrato:
    transacoes: tuple[TransacaoLida, ...]
    avisos: tuple[str, ...] = field(default_factory=tuple)
    """Linhas que não deu para ler e por quê. Nada é inventado para tapar buraco."""


class LeitorExtrato(Protocol):
    def ler(self, nome_arquivo: str, conteudo: bytes) -> LeituraExtrato:
        """Lê o arquivo. Levanta `FormatoNaoSuportado` ou `ArquivoIlegivel`."""
        ...


@dataclass(frozen=True)
class Classificacao:
    categoria: Categoria
    confianca: float | None
    versao_modelo: str
    essencial: bool


class ClassificadorTransacoes(Protocol):
    def classificar(self, transacoes: Sequence[TransacaoLida]) -> list[Classificacao]:
        """Uma classificação por transação, na mesma ordem."""
        ...

    def essencial(self, transacao: Transacao, categoria: Categoria) -> bool:
        """Reavalia o Mínimo Existencial quando a pessoa corrige a categoria (RF10)."""
        ...
