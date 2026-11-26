"""Ponto de entrada: `uvicorn pandora_api.principal:app`."""

from __future__ import annotations

from contextlib import asynccontextmanager

from pandora_api.adaptadores.dados.trilha_json import CAMINHO_PADRAO, TrilhaEmArquivo
from pandora_api.adaptadores.http.app import criar_app
from pandora_api.adaptadores.http.conteiner import Financeiro, montar
from pandora_api.adaptadores.ingestao.classificador_provisorio import ClassificadorProvisorio
from pandora_api.adaptadores.ingestao.csv_provisorio import LeitorCsvProvisorio
from pandora_api.adaptadores.persistencia.postgres import (
    BancoPostgres,
    ConsentimentosPostgres,
    ExtratosPostgres,
    SessoesPostgres,
    TransacoesPostgres,
    UsuariosPostgres,
)
from pandora_api.adaptadores.rag.http import AssistenteHttp
from pandora_api.adaptadores.seguranca.scrypt import HasherScrypt, RelogioDoSistema
from pandora_api.config import Config


def criar_app_padrao():
    config = Config.do_ambiente()
    banco = BancoPostgres(config.url_banco)

    @asynccontextmanager
    async def ciclo(_app):
        banco.migrar()
        yield
        banco.fechar()

    conteiner = montar(
        UsuariosPostgres(banco),
        SessoesPostgres(banco),
        ConsentimentosPostgres(banco),
        HasherScrypt(),
        RelogioDoSistema(),
        config.duracao_sessao,
        AssistenteHttp(config.url_rag),
        TrilhaEmArquivo(config.caminho_trilha or CAMINHO_PADRAO),
        # Leitor e classificador provisórios: trocar pelos da #57 e da #68 quando chegarem.
        Financeiro(
            ExtratosPostgres(banco), TransacoesPostgres(banco), LeitorCsvProvisorio(), ClassificadorProvisorio()
        ),
    )
    return criar_app(conteiner, config.origens_cors, lifespan=ciclo)


app = criar_app_padrao()
