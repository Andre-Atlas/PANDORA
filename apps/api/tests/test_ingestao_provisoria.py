"""Leitor de CSV e classificador provisórios, e as contas puras do Raio-X."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from pandora_api.adaptadores.ingestao.classificador_provisorio import (
    VERSAO_REGRAS,
    VERSAO_ROTULO,
    ClassificadorProvisorio,
)
from pandora_api.adaptadores.ingestao.csv_provisorio import LeitorCsvProvisorio
from pandora_api.dominio.raio_x import montar_raio_x
from pandora_api.dominio.transacao import (
    FUSO_DA_PESSOA,
    Categoria,
    FormaPagamento,
    OrigemCategoria,
    Transacao,
    mascarar_descricao,
)


def test_le_csv_brasileiro_com_ponto_e_virgula_e_latin1():
    csv = "Data;Histórico;Valor\n05/10/2026;SUPERMERCADO SÃO JOÃO;-1.234,56\n06/10/2026 14:30;PARC 03/10 LOJA;-99,90\n"
    leitura = LeitorCsvProvisorio().ler("extrato.CSV", csv.encode("latin-1"))
    primeira, segunda = leitura.transacoes
    assert primeira.valor_centavos == -123456
    assert primeira.descricao_mascarada == "SUPERMERCADO SÃO JOÃO"
    assert primeira.data_hora == datetime(2026, 10, 5, tzinfo=FUSO_DA_PESSOA)
    assert primeira.forma_pagamento == FormaPagamento.OUTRA and primeira.conta_id == "principal"
    assert segunda.parcela is not None and (segunda.parcela.numero, segunda.parcela.total) == (3, 10)


def test_le_o_formato_do_dataset_sintetico():
    csv = (
        b"transaction_id,posted_at,amount,payment_method,description_masked,mcc,category,is_essential\n"
        b"tx-1,2026-10-05T08:15:00,2850.00,PIX,CREDITO SALARIO,0000,RENDA,false\n"
    )
    (t,) = LeitorCsvProvisorio().ler("x.csv", csv).transacoes
    assert (t.valor_centavos, t.forma_pagamento, t.mcc) == (285000, FormaPagamento.PIX, None)
    assert t.categoria_no_arquivo == Categoria.RENDA and t.essencial_no_arquivo is False


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("PIX ENVIADO 123.456.789-09 MARIA", "PIX ENVIADO *** MARIA"),
        ("TED 12.345.678/0001-90 EMPRESA", "TED *** EMPRESA"),
        ("AG 1234 CC 98765-4 CARTAO 5502 0912 3456 7890", "AG 1234 CC *** CARTAO ***"),
        ("COBRANCA contato@exemplo.com", "COBRANCA ***"),
        ("PARC 03/10  LOJA   X", "PARC 03/10 LOJA X"),
    ],
)
def test_mascara_documentos_contas_e_emails(texto, esperado):
    assert mascarar_descricao(texto) == esperado


def _lida(valor: int, descricao: str = "LOJA", mcc: str | None = None, categoria=None, essencial=None):
    csv = f"data,valor,descricao,mcc,categoria,essencial\n2026-10-01,{valor / 100:.2f},{descricao},{mcc or ''},"
    csv += f"{categoria or ''},{'' if essencial is None else str(essencial).lower()}\n"
    return LeitorCsvProvisorio().ler("x.csv", csv.encode()).transacoes[0]


def test_classificador_usa_o_rotulo_do_arquivo_quando_existe():
    (c,) = ClassificadorProvisorio().classificar([_lida(-5000, mcc="5411", categoria="LAZER")])
    assert (c.categoria, c.versao_modelo, c.essencial, c.confianca) == (Categoria.LAZER, VERSAO_ROTULO, False, None)
    (c,) = ClassificadorProvisorio().classificar([_lida(-5000, categoria="LAZER", essencial=True)])
    assert c.essencial is True, "a regra de essencialidade do arquivo vence a aproximação por categoria"


def test_classificador_sem_rotulo_usa_mcc_e_nao_chuta():
    classificador = ClassificadorProvisorio()
    mercado, salario, desconhecida = classificador.classificar(
        [_lida(-5000, mcc="5411"), _lida(280000, "CREDITO SALARIO"), _lida(-5000, "PIX FULANO")]
    )
    assert (mercado.categoria, mercado.essencial, mercado.versao_modelo) == (Categoria.ALIMENTACAO, True, VERSAO_REGRAS)
    assert salario.categoria == Categoria.RENDA and salario.essencial is False
    assert desconhecida.categoria == Categoria.TRANSFERENCIA, "fora dos gastos: não infla nenhuma categoria"


def _transacao(valor: int, categoria: Categoria, essencial: bool, quando: datetime) -> Transacao:
    return Transacao(
        uuid4(),
        "c",
        quando,
        valor,
        FormaPagamento.PIX,
        "x",
        None,
        categoria,
        OrigemCategoria.MODELO,
        None,
        None,
        essencial,
    )


def test_raio_x_usa_o_mes_de_brasilia_e_ignora_transferencias():
    virada = datetime(2026, 11, 1, 2, 30, tzinfo=UTC)  # 31/10 às 23h30 em Brasília
    transacoes = [
        _transacao(300000, Categoria.RENDA, False, virada),
        _transacao(-100000, Categoria.MORADIA, True, virada),
        _transacao(-20000, Categoria.LAZER, False, virada),
        _transacao(-50000, Categoria.TRANSFERENCIA, False, virada),
        _transacao(-30000, Categoria.INVESTIMENTO, False, virada),
        _transacao(5000, Categoria.LAZER, False, virada),  # estorno: entrada não é gasto
        _transacao(-999, Categoria.LAZER, False, datetime(2026, 11, 1, 12, tzinfo=UTC)),
    ]
    r = montar_raio_x("2026-10", transacoes)
    assert (r.renda_centavos, r.minimo_existencial_centavos, r.folga_centavos) == (300000, 100000, 200000)
    assert [(g.categoria, g.total_centavos) for g in r.gastos] == [
        (Categoria.MORADIA, 100000),
        (Categoria.LAZER, 20000),
    ]
    assert r.transacoes_consideradas == 6


def test_folga_negativa_quando_o_essencial_nao_cabe_na_renda():
    quando = datetime(2026, 10, 10, tzinfo=FUSO_DA_PESSOA)
    r = montar_raio_x(
        "2026-10",
        [_transacao(100000, Categoria.RENDA, False, quando), _transacao(-150000, Categoria.MORADIA, True, quando)],
    )
    assert r.folga_centavos == -50000
