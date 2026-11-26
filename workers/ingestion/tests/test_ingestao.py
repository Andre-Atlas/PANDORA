"""Critérios da #57: OFX e CSV no mesmo esquema, importar duas vezes sem duplicar, nenhuma PII em logs."""
import logging
from pathlib import Path

import pytest

from pandora_ingestion.armazem import ArmazemJsonl
from pandora_ingestion.cli import main
from pandora_ingestion.erros import ArquivoIlegivel, FormatoNaoSuportado
from pandora_ingestion.esquema import FormaPagamento, Origem
from pandora_ingestion.importador import importar, ler
from pandora_ingestion.mascara import mascarar
from pandora_ingestion.normalizar import centavos, data_do_ofx, data_do_texto

FIXTURES = Path(__file__).parent / "fixtures"
ARQUIVOS = ["extrato_v1.ofx", "extrato_v2.ofx", "extrato_br.csv", "extrato_iso.csv"]
PII = ["123.456.789-09", "12345-6", "JOAO PEREIRA", "SANTOS"]


def conteudo(nome: str) -> bytes:
    return (FIXTURES / nome).read_bytes()


def essencia(leitura):
    """O que tem de ser igual, seja qual for o formato de origem."""
    return [(t.data_hora, t.valor_centavos, t.forma_pagamento, t.descricao_mascarada, t.parcela) for t in leitura.transacoes]


# --- mesmo esquema ---


@pytest.mark.parametrize("nome", ARQUIVOS)
def test_cada_formato_le_as_7_transacoes(nome):
    leitura = ler(nome, conteudo(nome))
    assert len(leitura.transacoes) == 7 and not leitura.avisos


def test_ofx_e_csv_chegam_ao_mesmo_esquema():
    referencia = essencia(ler("extrato_v1.ofx", conteudo("extrato_v1.ofx")))
    for nome in ARQUIVOS[1:]:
        assert essencia(ler(nome, conteudo(nome))) == referencia, nome


def test_valores_e_sinais_normalizados():
    t = ler("extrato_v1.ofx", conteudo("extrato_v1.ofx")).transacoes
    assert [x.valor_centavos for x in t] == [285000, -95000, -62050, -8990, -1200, -1200, -15000]


def test_csv_com_coluna_de_natureza_da_o_sinal():
    t = ler("extrato_iso.csv", conteudo("extrato_iso.csv")).transacoes
    assert t[0].valor_centavos == 285000 and t[1].valor_centavos == -95000


def test_datas_vao_para_o_fuso_de_brasilia():
    t = ler("extrato_v1.ofx", conteudo("extrato_v1.ofx")).transacoes[0]
    assert t.data_hora.isoformat() == "2026-10-05T12:00:00-03:00"
    assert data_do_ofx("20261005150000[0:GMT]").isoformat() == "2026-10-05T12:00:00-03:00"
    assert data_do_ofx("20261005").isoformat() == "2026-10-05T00:00:00-03:00"
    assert data_do_texto("05/10/2026").isoformat() == "2026-10-05T00:00:00-03:00"


def test_forma_de_pagamento_e_parcela():
    t = ler("extrato_v1.ofx", conteudo("extrato_v1.ofx")).transacoes
    assert [x.forma_pagamento for x in t] == [
        FormaPagamento.OUTRA, FormaPagamento.PIX, FormaPagamento.CARTAO_DEBITO, FormaPagamento.BOLETO,
        FormaPagamento.CARTAO_DEBITO, FormaPagamento.CARTAO_DEBITO, FormaPagamento.CARTAO_CREDITO,
    ]
    assert (t[6].parcela.numero, t[6].parcela.total) == (2, 5)
    assert {x.origem for x in t} == {Origem.OFX}


@pytest.mark.parametrize("texto,esperado", [
    ("1.234,56", 123456), ("1234.56", 123456), ("R$ -50,00", -5000), ("(50,00)", -5000), ("50,00-", -5000), ("0,05", 5),
])
def test_centavos(texto, esperado):
    assert centavos(texto) == esperado


@pytest.mark.parametrize("texto", ["abc", "10,555", "1.234"])
def test_centavos_invalido(texto):
    with pytest.raises(ValueError):
        centavos(texto)


def test_linha_ruim_vira_aviso_sem_ecoar_o_conteudo():
    csv = "data;descricao;valor\n05/10/2026;PIX ENVIADO - JOAO PEREIRA DOS SANTOS;abc\n06/10/2026;MERCADO;-10,00\n".encode()
    leitura = ler("x.csv", csv)
    assert len(leitura.transacoes) == 1 and len(leitura.avisos) == 1
    assert "JOAO" not in leitura.avisos[0] and "abc" not in leitura.avisos[0]


def test_arquivos_invalidos():
    with pytest.raises(ArquivoIlegivel):
        ler("x.csv", b"coluna;outra\n1;2\n")
    with pytest.raises(ArquivoIlegivel):
        ler("x.ofx", b"isto nao e um ofx")
    with pytest.raises(ArquivoIlegivel):
        ler("x.pdf", b"%PDF")  # PDF tem testes próprios em test_pdf.py
    with pytest.raises(FormatoNaoSuportado):
        ler("x.xlsx", b"")


# --- deduplicação ---


@pytest.mark.parametrize("nome", ARQUIVOS)
def test_importar_duas_vezes_nao_duplica(tmp_path, nome):
    armazem = ArmazemJsonl(tmp_path / "t.jsonl")
    primeira = importar(nome, conteudo(nome), armazem)
    segunda = importar(nome, conteudo(nome), armazem)
    assert (primeira.novas, primeira.repetidas) == (7, 0)
    assert (segunda.novas, segunda.repetidas) == (0, 7)
    assert len((tmp_path / "t.jsonl").read_text(encoding="utf-8").splitlines()) == 7


@pytest.mark.parametrize("nome", ARQUIVOS)
def test_duas_transacoes_iguais_no_mesmo_dia_continuam_duas(nome):
    chaves = [t.chave for t in ler(nome, conteudo(nome)).transacoes]
    assert len(set(chaves)) == 7


def test_extrato_com_sobreposicao_so_acrescenta_o_que_falta(tmp_path):
    armazem = ArmazemJsonl(tmp_path / "t.jsonl")
    linhas = conteudo("extrato_br.csv").decode().splitlines()
    importar("a.csv", "\n".join(linhas[:5]).encode(), armazem)  # cabeçalho + 4
    resultado = importar("b.csv", "\n".join([linhas[0], *linhas[3:]]).encode(), armazem)  # sobrepõe 2
    assert (resultado.novas, resultado.repetidas) == (3, 2)


# --- PII ---


@pytest.mark.parametrize("nome", ARQUIVOS)
def test_descricao_sem_pii(nome):
    for t in ler(nome, conteudo(nome)).transacoes:
        assert not any(p in t.descricao_mascarada for p in PII), t.descricao_mascarada
        assert not any(p in str(t.como_dict()) for p in PII)


def test_conta_do_ofx_vira_identificador_opaco():
    conta = ler("extrato_v1.ofx", conteudo("extrato_v1.ofx")).transacoes[0].conta_id
    assert conta.startswith("ofx-") and "12345" not in conta


@pytest.mark.parametrize("bruto,esperado", [
    ("PIX ENVIADO - JOAO PEREIRA DOS SANTOS", "PIX ENVIADO - ***"),
    ("TED MARIA APARECIDA DA SILVA", "TED ***"),
    ("PIX RECEBIDO CARLOS ALBERTO", "PIX RECEBIDO ***"),
    ("PIX ENVIADO MERCADO LIVRE LTDA", "PIX ENVIADO MERCADO LIVRE LTDA"),
    ("COMPRA DEBITO ATACADAO SUPERMERCADO", "COMPRA DEBITO ATACADAO SUPERMERCADO"),
    ("PAGAMENTO DE ALUGUEL RESIDENCIAL", "PAGAMENTO DE ALUGUEL RESIDENCIAL"),
    ("CONTATO fulano@exemplo.com 11 98765-4321", "CONTATO *** ***"),
    ("PAGTO CNPJ 12.345.678/0001-90 CPF 12345678909", "PAGTO CNPJ *** CPF ***"),
    ("TRANSF AG 1234 CONTA 98765-4", "TRANSF *** ***"),
])
def test_mascara(bruto, esperado):
    assert mascarar(bruto) == esperado


def test_nome_do_titular_some_em_qualquer_posicao():
    assert mascarar("COMPRA PADARIA MARIA DA SILVA 10/10", nomes=("maria da silva",)) == "COMPRA PADARIA *** 10/10"


def test_logs_e_saida_da_cli_sem_pii(tmp_path, caplog, capsys):
    caplog.set_level(logging.DEBUG)
    armazem = ArmazemJsonl(tmp_path / "t.jsonl")
    for nome in ARQUIVOS:
        importar(nome, conteudo(nome), armazem, nomes=("JOAO PEREIRA DOS SANTOS",))
    assert caplog.records
    texto = " ".join(r.getMessage() for r in caplog.records)
    assert not any(p in texto for p in PII) and "SALARIO" not in texto

    assert main([str(FIXTURES / "extrato_br.csv"), "--saida", str(tmp_path / "cli.jsonl")]) == 0
    saida = capsys.readouterr()
    assert "7 lidas, 7 novas, 0 já importadas" in saida.out
    assert not any(p in saida.out + saida.err for p in PII)


def test_cli_devolve_erro_sem_ecoar_conteudo(tmp_path, capsys):
    ruim = tmp_path / "ruim.csv"
    ruim.write_text("a;b\n123.456.789-09;x\n", encoding="utf-8")
    assert main([str(ruim), "--saida", str(tmp_path / "s.jsonl")]) == 1
    assert "123.456.789-09" not in capsys.readouterr().err
