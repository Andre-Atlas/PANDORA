"""Testes da Tarefa 2: ArtifactStore (EXIF/TTL), codecs ITF-25/BRCode e ingestão em 2 estágios."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from reportlab.graphics.barcode.common import I2of5
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from pandora_rag.agents.artifact_store import ArtifactStore
from pandora_rag.agents.codecs_financeiros import (
    barras_44_para_linha_digitavel_47,
    calcular_crc16_ccitt_false,
    decodificar_pix_brcode,
    ler_codigos_imagem_ou_pdf,
    linha_digitavel_47_para_barras_44,
    modulo_11_febraban,
    validar_barras_44,
)
from pandora_rag.agents.ingestao_adapter import ingerir_extrato_adaptado
from pandora_rag.agents.models import ExtratoDocumentalVLM, LancamentoExtratoVLM


def _barras_44_valida(banco: str = "001", valor_centavos: int = 119800) -> str:
    campo_livre = "1234567890123456789012345"
    sem_dv = f"{banco}9" + f"9999{valor_centavos:010d}" + campo_livre
    assert len(sem_dv) == 43
    dv = modulo_11_febraban(sem_dv)
    return f"{sem_dv[:4]}{dv}{sem_dv[4:]}"


def _montar_pix_brcode_valido(chave: str = "12345678900", nome: str = "FULANO DE TAL", valor: str = "1800.00") -> str:
    gui = "0014br.gov.bcb.pix"
    c_chave = f"01{len(chave):02d}{chave}"
    tag26_val = gui + c_chave
    partes = [
        "000201",
        f"26{len(tag26_val):02d}{tag26_val}",
        "52040000",
        "5303986",
        f"54{len(valor):02d}{valor}",
        "5802BR",
        f"59{len(nome):02d}{nome}",
        "6008BRASILIA",
        "6304",
    ]
    corpo = "".join(partes)
    crc = calcular_crc16_ccitt_false(corpo.encode("utf-8"))
    return corpo + crc


def test_artifact_store_remove_exif_e_expurga():
    store = ArtifactStore()
    img = Image.new("RGB", (2400, 1200), color="white")
    exif = Image.Exif()
    exif[271] = "CameraTesteGPS"
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)

    ref = store.registrar_bytes(
        buf.getvalue(),
        tipo="imagem_documento",
        nome_original="../boleto suspeito.jpg",
        mime_type="image/jpeg",
    )
    assert len(ref.artefato_id) == 32
    assert ".." not in ref.nome_original_sanitizado

    salva = Image.open(io.BytesIO(store.obter_bytes(ref.artefato_id)))
    assert salva.size == (2400, 1200)
    assert len(salva.getexif()) == 0

    vlm_img = Image.open(io.BytesIO(store.obter_imagem_vlm_bytes(ref.artefato_id, max_lado=960)))
    assert max(vlm_img.size) == 960

    assert store.expurgar_tudo() == 1
    assert not store.diretorio.exists()


def test_codecs_itf25_44_47_e_brcode_pix_crc16():
    barras = _barras_44_valida("001", 119800)
    dv_ok, valor = validar_barras_44(barras)
    assert dv_ok is True
    assert valor == 119800

    linha47 = barras_44_para_linha_digitavel_47(barras)
    assert len(linha47) == 47
    assert linha_digitavel_47_para_barras_44(linha47) == barras

    brcode = _montar_pix_brcode_valido()
    dados_ok = decodificar_pix_brcode(brcode)
    assert dados_ok.crc16_valido is True
    assert dados_ok.valor_centavos == 180000
    assert dados_ok.suspeito is False

    brcode_adulterado = brcode[:-4] + "0000"
    dados_ruim = decodificar_pix_brcode(brcode_adulterado)
    assert dados_ruim.crc16_valido is False
    assert dados_ruim.suspeito is True


def test_zxingcpp_le_itf25_e_qrcode_de_pdf(tmp_path: Path):
    barras = _barras_44_valida("341", 25000)
    brcode = _montar_pix_brcode_valido(valor="250.00")

    pdf_path = tmp_path / "boleto_qr.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    c.drawString(50, 780, "BANCO ITAU S.A. - R$ 250,00")
    I2of5(barras, checksum=0, bearers=0, barWidth=1.1, barHeight=45).drawOn(c, 50, 680)
    qr = QrCodeWidget(brcode, barWidth=140, barHeight=140)
    d = Drawing(140, 140)
    d.add(qr)
    d.drawOn(c, 50, 480)
    c.save()

    achados = ler_codigos_imagem_ou_pdf(pdf_path.read_bytes(), "application/pdf")
    assert achados["barras_44"] == barras
    assert achados["qr_pix_bruto"] == brcode


def test_ingestao_adapter_descarta_pdf_incompleto_e_usa_estagio_2_vlm(tmp_path: Path):
    pdf_path = tmp_path / "quebrado.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(40, 800, "Periodo: 01/10/2026 a 31/10/2026")
    c.drawString(40, 780, "Data Descricao Valor")
    c.drawString(40, 760, "SALDO ANTERIOR 1.000,00")
    c.drawString(40, 740, "05/10/2026 ALUGUEL APARTAMENTO -500,00")
    c.drawString(40, 720, "SALDO FINAL 300,00")  # falta -200,00 -> Estágio 1 fica divergente (-20000)
    c.save()

    def vlm_mock(_bytes: bytes) -> ExtratoDocumentalVLM:
        return ExtratoDocumentalVLM(
            eh_fatura_cartao=False,
            saldo_inicial_brl="1.000,00",
            saldo_final_ou_total_brl="300,00",
            lancamentos=[
                LancamentoExtratoVLM(data="05/10/2026", descricao="ALUGUEL APARTAMENTO", valor_brl="500,00", natureza="D"),
                LancamentoExtratoVLM(data="06/10/2026", descricao="PIX ENVIADO BETANO BET", valor_brl="200,00", natureza="D"),
            ],
        )

    res = ingerir_extrato_adaptado(
        "quebrado.pdf",
        pdf_path.read_bytes(),
        persona_id="diego_24",
        extrator_vlm_fn=vlm_mock,
    )
    assert res.estagio_usado == "estagio_2_vlm"
    assert res.reconciliado is True
    assert res.divergencia_centavos == 0
    assert len(res.transacoes) == 2
    assert any(t.is_bet for t in res.transacoes)
