"""Monta os casos de uso com os adaptadores escolhidos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from pandora_api.aplicacao.chat import Chat
from pandora_api.aplicacao.consentimentos import Consentimentos
from pandora_api.aplicacao.contas import Contas
from pandora_api.aplicacao.privacidade import Privacidade
from pandora_api.aplicacao.raio_x import Extratos, Transacoes
from pandora_api.aplicacao.trilha import Trilha
from pandora_api.portas.assistente import AssistenteElpis
from pandora_api.portas.ingestao import ClassificadorTransacoes, LeitorExtrato
from pandora_api.portas.repositorios import (
    RepositorioConsentimentos,
    RepositorioExtratos,
    RepositorioSessoes,
    RepositorioTransacoes,
    RepositorioUsuarios,
)
from pandora_api.portas.servicos import HasherSenha, Relogio
from pandora_api.portas.trilha import RepositorioTrilha


@dataclass(frozen=True)
class Conteiner:
    contas: Contas
    consentimentos: Consentimentos
    privacidade: Privacidade
    chat: Chat
    trilha: Trilha
    extratos: Extratos
    transacoes: Transacoes


@dataclass(frozen=True)
class Financeiro:
    """Repositórios e adaptadores do Raio-X (#72)."""

    extratos: RepositorioExtratos
    transacoes: RepositorioTransacoes
    leitor: LeitorExtrato
    classificador: ClassificadorTransacoes


def montar(
    usuarios: RepositorioUsuarios,
    sessoes: RepositorioSessoes,
    consentimentos: RepositorioConsentimentos,
    hasher: HasherSenha,
    relogio: Relogio,
    duracao_sessao: timedelta,
    assistente: AssistenteElpis,
    repositorio_trilha: RepositorioTrilha,
    financeiro: Financeiro,
) -> Conteiner:
    casos_consentimento = Consentimentos(consentimentos, relogio)
    return Conteiner(
        contas=Contas(usuarios, sessoes, hasher, relogio, duracao_sessao),
        consentimentos=casos_consentimento,
        # Todo repositório com dado pessoal entra aqui. O de usuários vai por último.
        privacidade=Privacidade([financeiro.transacoes, financeiro.extratos, sessoes, consentimentos, usuarios]),
        chat=Chat(assistente),
        trilha=Trilha(repositorio_trilha, assistente),
        extratos=Extratos(
            financeiro.extratos,
            financeiro.transacoes,
            financeiro.leitor,
            financeiro.classificador,
            casos_consentimento,
            relogio,
        ),
        transacoes=Transacoes(financeiro.transacoes, financeiro.classificador),
    )
