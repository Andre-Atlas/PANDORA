"""Transação: RASCUNHO do esquema único.

Os campos seguem o dataset sintético da #51 (`services/ml/sintetico`), que é o
que o classificador da Mariana consome. Falta fechar com a ingestão da Luana
(#57) — passo 3 da #62. Valores sempre em centavos inteiros (RNF03).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID
from zoneinfo import ZoneInfo

FUSO_DA_PESSOA = ZoneInfo("America/Sao_Paulo")
"""O mês do Raio-X é o mês do calendário da pessoa, não o de UTC."""


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
    OUTRA = "OTHER"
    """O extrato não diz a forma de pagamento. Melhor assumir que não sabe do que chutar."""


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

    @property
    def mes(self) -> str:
        return mes_local(self.data_hora)

    def corrigida_pela_pessoa(self, categoria: Categoria, essencial: bool) -> Transacao:
        """RF10: a correção da pessoa vence a do modelo e não tem confiança de modelo."""
        return replace(
            self,
            categoria=categoria,
            origem_categoria=OrigemCategoria.PESSOA,
            confianca_categoria=None,
            essencial=essencial,
        )


@dataclass(frozen=True)
class TransacaoLida:
    """Linha lida de um extrato, antes da classificação (saída da ingestão, #57)."""

    conta_id: str
    data_hora: datetime
    valor_centavos: int
    forma_pagamento: FormaPagamento
    descricao_mascarada: str
    mcc: str | None = None
    parcela: Parcela | None = None
    categoria_no_arquivo: Categoria | None = None
    """Só o dataset sintético (#51) traz rótulo. Extrato de banco de verdade não traz."""
    essencial_no_arquivo: bool | None = None


def mes_local(momento: datetime) -> str:
    return momento.astimezone(FUSO_DA_PESSOA).strftime("%Y-%m")


# CPF, CNPJ e qualquer sequência longa de dígitos (conta, cartão, telefone).
_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_DIGITOS_LONGOS = re.compile(r"\d[\d .-]{5,}\d")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def mascarar_descricao(texto: str) -> str:
    """RNF01: tira da descrição o que identifica alguém. Nomes de pessoas ainda passam (ver README)."""
    for padrao in (_EMAIL, _CNPJ, _CPF, _DIGITOS_LONGOS):
        texto = padrao.sub("***", texto)
    return " ".join(texto.split())[:200]
