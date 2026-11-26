"""Critérios da #66: PDFs de exemplo geram as transações esperadas, falha não inventa dado, PDF é só dado."""
import logging
from pathlib import Path

import pytest

pytest.importorskip("pdfplumber")

from pandora_ingestion.armazem import ArmazemJsonl
from pandora_ingestion.erros import ArquivoIlegivel
from pandora_ingestion.esquema import FormaPagamento, Origem
from pandora_ingestion.importador import importar, ler
from pandora_ingestion.pdf import PrecisaDeOcr

FIXTURES = Path(__file__).parent / "fixtures"
EXTRATOS = ["layout_a_grade.pdf", "layout_b_debito_credito.pdf"]
PII = ["123.456.789-09", "12345-6", "JOAO PEREIRA", "MARIA APARECIDA", "1234"]


def pdf(nome: str):
    return ler(nome, (FIXTURES / nome).read_bytes())


def essencia(leitura):
    return [(t.data_hora.date().isoformat(), t.valor_centavos, t.forma_pagamento, t.descricao_mascarada)
            for t in leitura.transacoes]


ESPERADO_EXTRATO = [
    ("2026-10-05", 285000, FormaPagamento.OUTRA, "CREDITO SALARIO EMPRESA XYZ LTDA"),
    ("2026-10-06", -95000, FormaPagamento.PIX, "PIX ENVIADO - ***"),
    ("2026-10-07", -62050, FormaPagamento.CARTAO_DEBITO, "COMPRA DEBITO ATACADAO SUPERMERCADO"),
    ("2026-10-10", -8990, FormaPagamento.BOLETO, "PAGTO BOLETO CPF ***"),
    ("2026-10-12", -1200, FormaPagamento.CARTAO_DEBITO, "COMPRA DEBITO PADARIA CENTRAL"),
    ("2026-10-12", -1200, FormaPagamento.CARTAO_DEBITO, "COMPRA DEBITO PADARIA CENTRAL"),
    ("2026-10-15", -15000, FormaPagamento.CARTAO_CREDITO, "COMPRA CREDITO LOJA XPTO PARC 2/5"),
]


@pytest.mark.parametrize("nome", EXTRATOS)
def test_layouts_de_extrato_geram_as_transacoes_esperadas(nome):
    leitura = pdf(nome)
    assert essencia(leitura) == ESPERADO_EXTRATO and not leitura.avisos
    assert {t.origem for t in leitura.transacoes} == {Origem.PDF}
    assert (leitura.transacoes[6].parcela.numero, leitura.transacoes[6].parcela.total) == (2, 5)


def test_fatura_de_cartao_com_ano_vindo_do_vencimento():
    leitura = pdf("layout_c_fatura.pdf")
    assert [(t.data_hora.date().isoformat(), t.valor_centavos, t.descricao_mascarada) for t in leitura.transacoes] == [
        ("2026-12-03", -15000, "LOJA XPTO PARC 02/05"),  # compra: positiva na fatura, saída aqui
        ("2026-12-08", -32045, "MERCADO CENTRAL"),
        ("2026-12-15", 150000, "PAGAMENTO RECEBIDO"),  # "-" na fatura é crédito
        ("2026-12-28", -4590, "FARMACIA POPULAR"),  # dezembro de uma fatura que vence em janeiro: ano anterior
        ("2027-01-02", 3000, "ESTORNO COMPRA LOJA XPTO"),  # sufixo CR é crédito
    ]
    assert {t.forma_pagamento for t in leitura.transacoes} == {FormaPagamento.CARTAO_CREDITO}
    assert {t.conta_id for t in leitura.transacoes} == {"cartao"}


def test_3_layouts_diferentes_sao_reconhecidos():
    assert all(len(pdf(n).transacoes) >= 5 for n in [*EXTRATOS, "layout_c_fatura.pdf"])


# --- falha não inventa dado ---


def test_pdf_escaneado_pede_ocr_e_nao_devolve_nada():
    with pytest.raises(PrecisaDeOcr, match="OCR"):
        pdf("escaneado.pdf")
    assert issubclass(PrecisaDeOcr, ArquivoIlegivel)


def test_layout_desconhecido_nao_chuta():
    with pytest.raises(ArquivoIlegivel, match="layout"):
        pdf("sem_layout.pdf")  # tem uma data e um valor soltos num parágrafo: não podem virar transação


def test_pdf_corrompido_ou_nao_pdf():
    for lixo in (b"isto nao e um pdf", b"%PDF-1.4\n%%EOF", b""):
        with pytest.raises(ArquivoIlegivel):
            ler("x.pdf", lixo)


def test_linhas_ruins_viram_aviso_e_so_a_boa_vira_transacao():
    leitura = pdf("linhas_ruins.pdf")
    assert [t.descricao_mascarada for t in leitura.transacoes] == ["COMPRA BOA"]
    assert len(leitura.avisos) == 3
    assert any("valor" in a for a in leitura.avisos)
    assert any("data inválida" in a for a in leitura.avisos)
    assert any("fora do período" in a for a in leitura.avisos)
    assert not any("SEM VALOR" in a or "IMPOSSIVEL" in a for a in leitura.avisos)  # sem ecoar o conteúdo


def test_pdf_sem_ano_no_documento_nao_inventa_o_ano(tmp_path):
    from reportlab.pdfgen import canvas

    caminho = tmp_path / "sem_ano.pdf"
    c = canvas.Canvas(str(caminho))
    c.drawString(40, 800, "Cartao Ficticio - Fatura")
    c.drawString(40, 780, "05/10 COMPRA SEM ANO 10,00")
    c.save()
    with pytest.raises(ArquivoIlegivel, match="ano"):
        ler("x.pdf", caminho.read_bytes())


# --- conteúdo do PDF é dado ---


def test_texto_que_da_ordens_nao_vira_transacao_nem_efeito():
    leitura = pdf("injecao.pdf")
    # a linha de ordem sem data é ignorada; a que tem data e valor é uma compra de R$ 10,00 e só isso
    assert len(leitura.transacoes) == 1
    t = leitura.transacoes[0]
    assert t.valor_centavos == -1000 and t.data_hora.date().isoformat() == "2026-10-05"
    assert "999" not in str(leitura.transacoes) and "exemplo.invalido" not in str(leitura.transacoes)


def test_so_o_esquema_sai_do_pdf():
    """A saída tem só os campos do esquema, e a descrição fica limitada e sem caracteres de controle."""
    t = pdf("injecao.pdf").transacoes[0]
    assert set(t.como_dict()) == {"conta_id", "data_hora", "valor_centavos", "forma_pagamento", "descricao_mascarada",
                                  "origem", "mcc", "parcela", "categoria_no_arquivo", "essencial_no_arquivo",
                                  "id_externo", "chave"}
    assert len(t.descricao_mascarada) <= 200 and t.descricao_mascarada.isprintable()


# --- no fluxo de importação ---


@pytest.mark.parametrize("nome", [*EXTRATOS, "layout_c_fatura.pdf"])
def test_importar_pdf_duas_vezes_nao_duplica(tmp_path, nome):
    armazem = ArmazemJsonl(tmp_path / "t.jsonl")
    dados = (FIXTURES / nome).read_bytes()
    primeira, segunda = importar(nome, dados, armazem), importar(nome, dados, armazem)
    assert primeira.novas == primeira.lidas and segunda.novas == 0 and segunda.repetidas == primeira.lidas


def test_pdf_sem_pii_na_saida_nem_nos_logs(tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    armazem = ArmazemJsonl(tmp_path / "t.jsonl")
    for nome in [*EXTRATOS, "layout_c_fatura.pdf", "linhas_ruins.pdf"]:
        resultado = importar(nome, (FIXTURES / nome).read_bytes(), armazem)
        assert not any(p in " ".join(resultado.avisos) for p in PII)
    saida = (tmp_path / "t.jsonl").read_text(encoding="utf-8")
    assert not any(p in saida for p in PII)
    assert not any(p in " ".join(r.getMessage() for r in caplog.records) for p in PII)
