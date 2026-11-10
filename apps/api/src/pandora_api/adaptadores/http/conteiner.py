"""Monta os casos de uso com os adaptadores escolhidos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from pandora_api.aplicacao.consentimentos import Consentimentos
from pandora_api.aplicacao.contas import Contas
from pandora_api.aplicacao.privacidade import Privacidade
from pandora_api.portas.repositorios import RepositorioConsentimentos, RepositorioSessoes, RepositorioUsuarios
from pandora_api.portas.servicos import HasherSenha, Relogio


@dataclass(frozen=True)
class Conteiner:
    contas: Contas
    consentimentos: Consentimentos
    privacidade: Privacidade


def montar(
    usuarios: RepositorioUsuarios,
    sessoes: RepositorioSessoes,
    consentimentos: RepositorioConsentimentos,
    hasher: HasherSenha,
    relogio: Relogio,
    duracao_sessao: timedelta,
) -> Conteiner:
    return Conteiner(
        contas=Contas(usuarios, sessoes, hasher, relogio, duracao_sessao),
        consentimentos=Consentimentos(consentimentos, relogio),
        # Todo repositório com dado pessoal entra aqui. O de usuários vai por último.
        privacidade=Privacidade([sessoes, consentimentos, usuarios]),
    )
