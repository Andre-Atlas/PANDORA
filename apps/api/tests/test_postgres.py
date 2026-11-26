"""Integração com Postgres real. Roda quando PANDORA_TEST_DB_URL está definido:

docker compose up -d db
PANDORA_TEST_DB_URL=postgresql://pandora:pandora_local@localhost:5434/pandora uv run pytest tests/test_postgres.py
"""

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from pandora_api.adaptadores.http.conteiner import Financeiro, montar
from pandora_api.adaptadores.ingestao.classificador_provisorio import ClassificadorProvisorio
from pandora_api.adaptadores.ingestao.csv_provisorio import LeitorCsvProvisorio
from pandora_api.adaptadores.seguranca.scrypt import HasherScrypt, RelogioDoSistema
from pandora_api.aplicacao.contas import hash_do_token
from pandora_api.dominio.consentimento import Finalidade
from pandora_api.dominio.transacao import Categoria, OrigemCategoria

URL = os.environ.get("PANDORA_TEST_DB_URL")
pytestmark = pytest.mark.skipif(not URL, reason="PANDORA_TEST_DB_URL não definido")


class _SemTrilha:
    def etapas(self):
        return []


@pytest.fixture
def banco():
    from pandora_api.adaptadores.persistencia.postgres import BancoPostgres

    b = BancoPostgres(URL)
    b.migrar()
    b.migrar()  # idempotente
    yield b
    b.fechar()


def test_fluxo_completo_e_exclusao(banco):
    from pandora_api.adaptadores.persistencia.postgres import (
        ConsentimentosPostgres,
        ExtratosPostgres,
        SessoesPostgres,
        TransacoesPostgres,
        UsuariosPostgres,
    )

    usuarios, sessoes, consentimentos = UsuariosPostgres(banco), SessoesPostgres(banco), ConsentimentosPostgres(banco)
    extratos, transacoes = ExtratosPostgres(banco), TransacoesPostgres(banco)
    financeiro = Financeiro(extratos, transacoes, LeitorCsvProvisorio(), ClassificadorProvisorio())
    c = montar(
        usuarios,
        sessoes,
        consentimentos,
        HasherScrypt(),
        RelogioDoSistema(),
        timedelta(hours=1),
        None,
        _SemTrilha(),
        financeiro,
    )

    email = f"teste-{uuid4().hex[:8]}@exemplo.com"
    usuario = c.contas.cadastrar(email, "senha-forte-1")
    sessao = c.contas.entrar(email, "senha-forte-1")
    assert c.contas.usuario_da_sessao(sessao.token).id == usuario.id
    assert sessao.expira_em > datetime.now(UTC)

    lido = usuarios.por_id(usuario.id)
    assert lido.criado_em == usuario.criado_em
    assert lido.criado_em.utcoffset() == timedelta(0), "o banco deve devolver datas em UTC"

    consentimento = c.consentimentos.registrar(usuario.id, Finalidade.DIAGNOSTICO_FINANCEIRO, "2026-11")
    c.consentimentos.exigir(usuario.id, Finalidade.DIAGNOSTICO_FINANCEIRO)

    csv = (
        b"posted_at,amount,payment_method,description_masked,mcc,category\n"
        b"2026-10-05T08:15:00,2850.00,PIX,CREDITO SALARIO,0000,RENDA\n"
        b"2026-10-06T10:22:00,-950.00,PIX,ALUGUEL,6513,MORADIA\n"
        b"2026-10-31T23:30:00,-40.00,CREDIT_CARD,PIZZA PARC 01/02,5814,LAZER\n"
    )
    extrato = c.extratos.enviar(usuario.id, "out.csv", csv)
    assert extrato.transacoes_importadas == 3
    assert extratos.por_id(usuario.id, extrato.id).status == extrato.status
    assert c.extratos.enviar(usuario.id, "out.csv", csv).transacoes_importadas == 0, "não importa de novo"
    itens, total = c.transacoes.listar(usuario.id, "2026-10", None, 1, 2)
    assert total == 3 and len(itens) == 2
    assert itens[0].descricao_mascarada == "PIZZA PARC 01/02", "23h30 de Brasília ainda é outubro"
    assert itens[0].parcela is not None and itens[0].parcela.total == 2
    corrigida = c.transacoes.corrigir_categoria(usuario.id, itens[1].id, Categoria.UTILIDADES)
    assert transacoes.por_id(usuario.id, corrigida.id).origem_categoria == OrigemCategoria.PESSOA
    raio_x = c.transacoes.raio_x(usuario.id, "2026-10")
    assert (raio_x.renda_centavos, raio_x.minimo_existencial_centavos) == (285000, 95000)

    assert c.consentimentos.revogar(usuario.id, consentimento.id).ativo is False
    assert consentimentos.por_id(consentimento.id).revogado_em is not None

    c.privacidade.apagar_tudo(usuario.id)
    assert usuarios.por_id(usuario.id) is None
    assert sessoes.por_token_hash(hash_do_token(sessao.token)) is None
    assert consentimentos.do_usuario(usuario.id) == []
    with banco.conexao() as con:
        for tabela in ("usuarios", "sessoes", "consentimentos", "extratos", "transacoes"):
            coluna = "id" if tabela == "usuarios" else "usuario_id"
            restantes = con.execute(f"SELECT count(*) AS n FROM {tabela} WHERE {coluna} = %s", (usuario.id,)).fetchone()
            assert restantes["n"] == 0, tabela
