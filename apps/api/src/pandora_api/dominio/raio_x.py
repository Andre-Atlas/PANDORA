"""Raio-X do mês (RF02): renda, Mínimo Existencial e folga, a partir das transações.

Conta pura, sem estimativa: só soma o que está nas transações do mês.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pandora_api.dominio.transacao import Categoria, Transacao

FORA_DOS_GASTOS = frozenset({Categoria.RENDA, Categoria.TRANSFERENCIA, Categoria.INVESTIMENTO})
"""Não são gasto: entrada, dinheiro que só muda de conta (inclui o pagamento integral da fatura) e aplicação."""


@dataclass(frozen=True)
class GastoCategoria:
    categoria: Categoria
    total_centavos: int
    essencial_centavos: int


@dataclass(frozen=True)
class RaioX:
    mes: str
    renda_centavos: int
    minimo_existencial_centavos: int
    """Soma dos gastos essenciais do mês. Nenhum plano mexe nesse valor (Lei 14.181/2021)."""
    folga_centavos: int
    """Renda menos o Mínimo Existencial. Pode ser negativa: aí o essencial já não cabe na renda."""
    gastos: tuple[GastoCategoria, ...]
    transacoes_consideradas: int


def montar_raio_x(mes: str, transacoes: Iterable[Transacao]) -> RaioX:
    do_mes = [t for t in transacoes if t.mes == mes]
    renda = sum(t.valor_centavos for t in do_mes if t.categoria == Categoria.RENDA and t.valor_centavos > 0)

    totais: dict[Categoria, list[int]] = {}
    for t in do_mes:
        if t.categoria in FORA_DOS_GASTOS or t.valor_centavos >= 0:
            continue
        total, essencial = totais.setdefault(t.categoria, [0, 0])
        valor = -t.valor_centavos
        totais[t.categoria] = [total + valor, essencial + (valor if t.essencial else 0)]

    gastos = tuple(
        sorted(
            (GastoCategoria(c, total, essencial) for c, (total, essencial) in totais.items()),
            key=lambda g: (-g.total_centavos, g.categoria.value),
        )
    )
    minimo = sum(g.essencial_centavos for g in gastos)
    return RaioX(mes, renda, minimo, renda - minimo, gastos, len(do_mes))
