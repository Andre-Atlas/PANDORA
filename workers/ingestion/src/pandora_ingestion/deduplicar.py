"""Chave estável por transação, para importar o mesmo extrato duas vezes sem duplicar.

Com FITID (OFX) a chave é conta + FITID. Sem ele, é conta + data/hora + valor + descrição, mais a ordem
de ocorrência dentro do arquivo: dois cafés iguais no mesmo minuto são duas transações, e reimportar o
mesmo arquivo gera as mesmas chaves. Limite conhecido: extratos que se sobrepõem, mas cortam um mesmo
dia em pontos diferentes, podem contar ocorrências diferentes.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Iterable
from dataclasses import replace

from pandora_ingestion.esquema import Transacao


def _base(t: Transacao) -> str:
    if t.id_externo:
        return f"{t.conta_id}|id|{t.id_externo}"
    return f"{t.conta_id}|{t.data_hora.isoformat()}|{t.valor_centavos}|{t.descricao_mascarada}"


def atribuir_chaves(transacoes: Iterable[Transacao]) -> list[Transacao]:
    vistas: Counter[str] = Counter()
    com_chave = []
    for t in transacoes:
        base = _base(t)
        vistas[base] += 1
        chave = hashlib.sha256(f"{base}#{vistas[base]}".encode()).hexdigest()[:24]
        com_chave.append(replace(t, chave=chave))
    return com_chave


def separar_novas(transacoes: Iterable[Transacao], ja_importadas: set[str]) -> tuple[list[Transacao], int]:
    """Devolve as transações novas e quantas já existiam."""
    novas, repetidas = [], 0
    for t in transacoes:
        if t.chave in ja_importadas:
            repetidas += 1
        else:
            novas.append(t)
    return novas, repetidas
