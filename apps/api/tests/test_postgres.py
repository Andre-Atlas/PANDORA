"""Integração com Postgres real. Roda quando PANDORA_TEST_DB_URL está definido:

docker compose up -d db
PANDORA_TEST_DB_URL=postgresql://pandora:pandora_local@localhost:5434/pandora uv run pytest tests/test_postgres.py
"""

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from pandora_api.adaptadores.http.conteiner import montar
from pandora_api.adaptadores.seguranca.scrypt import HasherScrypt, RelogioDoSistema
from pandora_api.aplicacao.contas import hash_do_token
from pandora_api.dominio.consentimento import Finalidade

URL = os.environ.get("PANDORA_TEST_DB_URL")
pytestmark = pytest.mark.skipif(not URL, reason="PANDORA_TEST_DB_URL não definido")


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
        SessoesPostgres,
        UsuariosPostgres,
    )

    usuarios, sessoes, consentimentos = UsuariosPostgres(banco), SessoesPostgres(banco), ConsentimentosPostgres(banco)
    c = montar(usuarios, sessoes, consentimentos, HasherScrypt(), RelogioDoSistema(), timedelta(hours=1), None, None)

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
    assert c.consentimentos.revogar(usuario.id, consentimento.id).ativo is False
    assert consentimentos.por_id(consentimento.id).revogado_em is not None

    c.privacidade.apagar_tudo(usuario.id)
    assert usuarios.por_id(usuario.id) is None
    assert sessoes.por_token_hash(hash_do_token(sessao.token)) is None
    assert consentimentos.do_usuario(usuario.id) == []
    with banco.conexao() as con:
        for tabela in ("usuarios", "sessoes", "consentimentos"):
            coluna = "id" if tabela == "usuarios" else "usuario_id"
            restantes = con.execute(f"SELECT count(*) AS n FROM {tabela} WHERE {coluna} = %s", (usuario.id,)).fetchone()
            assert restantes["n"] == 0, tabela
