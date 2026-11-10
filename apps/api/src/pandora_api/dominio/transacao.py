"""Transação: RASCUNHO do esquema único.

Os campos seguem o dataset sintético da #51 (`services/ml/sintetico`), que é o
que o classificador da Mariana consome. Falta fechar com a ingestão da Luana
(#57) — passo 3 da #62. Valores sempre em centavos inteiros (RNF03).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Categoria(StrEnum):
    # Consumo (alvo do F1 macro do classificador)
    MORADIA = "MORADIA"
    UTILIDADES = "UTILIDADES"
    ALIMENTACAO = "ALIMENTACAO"
    SAUDE = "SAUDE"
    TRANSPORTE = "TRANSPORTE"
    EDUCACAO = "EDUCACAO"
    LAZER = "LAZER"
    COMPRAS_IMPULSO = "COMPRAS_IMPULSO"
    INSUMO_MEI = "INSUMO_MEI"
    # Contexto
    RENDA = "RENDA"
    DIVIDA_JUROS = "DIVIDA_JUROS"
    INVESTIMENTO = "INVESTIMENTO"
    TRANSFERENCIA = "TRANSFERENCIA"
    APOSTAS_BETS = "APOSTAS_BETS"
    FRAUDE_SUSPEITA = "FRAUDE_SUSPEITA"


CATEGORIAS_CONSUMO = frozenset(
    {
        Categoria.MORADIA,
        Categoria.UTILIDADES,
        Categoria.ALIMENTACAO,
        Categoria.SAUDE,
        Categoria.TRANSPORTE,
        Categoria.EDUCACAO,
        Categoria.LAZER,
        Categoria.COMPRAS_IMPULSO,
        Categoria.INSUMO_MEI,
    }
)


class FormaPagamento(StrEnum):
    PIX = "PIX"
    CARTAO_DEBITO = "DEBIT_CARD"
    CARTAO_CREDITO = "CREDIT_CARD"
    BOLETO = "BOLETO"
    DEBITO_AUTOMATICO = "DIRECT_DEBIT"


class OrigemCategoria(StrEnum):
    MODELO = "modelo"
    PESSOA = "pessoa"
    """Corrigida pela pessoa com um toque (RF10). Vence a do modelo."""


@dataclass(frozen=True)
class Parcela:
    numero: int
    total: int


@dataclass(frozen=True)
class Transacao:
    id: UUID
    conta_id: str
    data_hora: datetime
    valor_centavos: int
    """Negativo para saída, positivo para entrada."""
    forma_pagamento: FormaPagamento
    descricao_mascarada: str
    """Sem PII: nome, CPF e conta já mascarados (RNF01)."""
    mcc: str | None
    categoria: Categoria
    origem_categoria: OrigemCategoria
    confianca_categoria: float | None
    versao_modelo: str | None
    essencial: bool
    """Faz parte do Mínimo Existencial (Lei 14.181/2021)."""
    parcela: Parcela | None = None
