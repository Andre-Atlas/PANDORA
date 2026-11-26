"""Esquema único de transação: toda fonte (OFX, CSV, e depois PDF e Open Finance) chega aqui.

Os campos e os valores dos enums são os mesmos de `TransacaoLida` em `apps/api` (dominio/transacao.py),
combinados com o contrato da API (#62), para o adaptador da API ser só uma conversão campo a campo.
Valores sempre em centavos inteiros: negativo é saída, positivo é entrada.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from zoneinfo import ZoneInfo

FUSO_DA_PESSOA = ZoneInfo("America/Sao_Paulo")
"""Extrato sem fuso está no horário de Brasília."""


class FormaPagamento(StrEnum):
    PIX = "PIX"
    CARTAO_DEBITO = "DEBIT_CARD"
    CARTAO_CREDITO = "CREDIT_CARD"
    BOLETO = "BOLETO"
    DEBITO_AUTOMATICO = "DIRECT_DEBIT"
    OUTRA = "OTHER"


class Origem(StrEnum):
    OFX = "ofx"
    CSV = "csv"


@dataclass(frozen=True)
class Parcela:
    numero: int
    total: int


@dataclass(frozen=True)
class Transacao:
    conta_id: str
    data_hora: datetime
    valor_centavos: int
    forma_pagamento: FormaPagamento
    descricao_mascarada: str
    """Sem CPF, CNPJ, e-mail, telefone, números de conta nem nome de pessoa."""
    origem: Origem
    mcc: str | None = None
    parcela: Parcela | None = None
    categoria_no_arquivo: str | None = None
    """Só o dataset sintético (#51) traz rótulo; extrato de banco de verdade não."""
    essencial_no_arquivo: bool | None = None
    id_externo: str | None = None
    """FITID do OFX, quando existe. Entra na chave de deduplicação."""
    chave: str = field(default="", compare=False)
    """Identificador estável para não duplicar entre importações (ver `deduplicar.py`)."""

    def como_dict(self) -> dict:
        dados = asdict(self)
        dados["data_hora"] = self.data_hora.isoformat()
        dados["forma_pagamento"] = self.forma_pagamento.value
        dados["origem"] = self.origem.value
        return dados


@dataclass(frozen=True)
class Leitura:
    transacoes: tuple[Transacao, ...]
    avisos: tuple[str, ...] = ()
    """Linhas que não deu para ler e por quê. Sem repetir o conteúdo da linha, que pode ter PII."""


def hash_curto(texto: str, tamanho: int = 12) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:tamanho]
