"""Decodificadores determinísticos FEBRABAN (ITF-25 44<->47), EMV BRCode Pix (CRC-16) e leitor óptico zxing-cpp."""
from __future__ import annotations

import io
import itertools
import re
from decimal import Decimal, InvalidOperation
from typing import Any

import pymupdf
import zxingcpp
from PIL import Image

from pandora_rag.agents.models import DadosPixBRCode
from pandora_rag.generate.pii import mascarar

_DOMINIOS_SUSPEITOS = (".xyz", ".top", ".click", ".tk", "bit.ly", "tinyurl")


def modulo_10(bloco: str) -> int:
    """Dígito verificador FEBRABAN pelo algoritmo Módulo 10."""
    soma = 0
    peso = 2
    for ch in reversed(bloco):
        prod = int(ch) * peso
        soma += prod // 10 + prod % 10
        peso = 1 if peso == 2 else 2
    return (10 - (soma % 10)) % 10


def modulo_11_febraban(bloco_43: str) -> int:
    """Calcula DV geral FEBRABAN (posição 4 do código de barras de 44 dígitos) via Módulo 11."""
    soma = 0
    peso = 2
    for ch in reversed(bloco_43):
        soma += int(ch) * peso
        peso = 2 if peso == 9 else peso + 1
    resto = soma % 11
    dv = 11 - resto
    if dv in (0, 10, 11):
        return 1
    return dv


def barras_44_para_linha_digitavel_47(barras_44: str) -> str:
    """Converte código de barras ITF-25 bancário (44 dígitos) na linha digitável (47 dígitos)."""
    limpo = re.sub(r"\D", "", barras_44)
    if len(limpo) != 44:
        raise ValueError(f"Código de barras bancário exige 44 dígitos (recebido: {len(limpo)}).")
    c1 = limpo[0:4] + limpo[19:24]
    dv1 = modulo_10(c1)
    c2 = limpo[24:34]
    dv2 = modulo_10(c2)
    c3 = limpo[34:44]
    dv3 = modulo_10(c3)
    dv_geral = limpo[4]
    fator_valor = limpo[5:19]
    return f"{c1}{dv1}{c2}{dv2}{c3}{dv3}{dv_geral}{fator_valor}"


def linha_digitavel_47_para_barras_44(linha_47: str) -> str:
    """Reconstrói os 44 dígitos do código de barras a partir da linha digitável (47 dígitos)."""
    d = re.sub(r"\D", "", linha_47)
    if len(d) != 47:
        raise ValueError(f"Linha digitável bancária exige 47 dígitos (recebido: {len(d)}).")
    return d[0:4] + d[32] + d[33:47] + d[4:9] + d[10:20] + d[21:31]


def validar_barras_44(barras_44: str) -> tuple[bool, int | None]:
    """Valida o DV geral Módulo 11 e extrai o valor em centavos do código de barras (44 dígitos)."""
    limpo = re.sub(r"\D", "", barras_44)
    if len(limpo) != 44:
        return False, None
    bloco_43 = limpo[:4] + limpo[5:]
    dv_ok = modulo_11_febraban(bloco_43) == int(limpo[4])
    valor_centavos = int(limpo[9:19])
    return dv_ok, valor_centavos


def calcular_crc16_ccitt_false(dados: bytes) -> str:
    """Calcula CRC-16/CCITT-FALSE (polinômio 0x1021, inicial 0xFFFF) do padrão EMV Pix."""
    crc = 0xFFFF
    for byte in dados:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def _ler_tlv(texto: str) -> dict[str, str]:
    campos: dict[str, str] = {}
    pos = 0
    while pos + 4 <= len(texto):
        tag = texto[pos : pos + 2]
        tam_str = texto[pos + 2 : pos + 4]
        if not tam_str.isdigit():
            break
        tam = int(tam_str)
        ini = pos + 4
        fim = ini + tam
        if fim > len(texto):
            break
        campos[tag] = texto[ini:fim]
        pos = fim
    return campos


def _classificar_chave_pix(chave: str | None) -> str | None:
    if not chave:
        return None
    if "@" in chave:
        return "email"
    dig = re.sub(r"\D", "", chave)
    if len(dig) == 11 and chave.strip().isdigit():
        return "cpf"
    if len(dig) == 14 and chave.strip().isdigit():
        return "cnpj"
    if chave.startswith("+"):
        return "telefone"
    if re.fullmatch(r"[0-9a-fA-F-]{32,36}", chave.strip()):
        return "evp_aleatoria"
    return "outro"


def decodificar_pix_brcode(payload: str) -> DadosPixBRCode:
    """Decodifica e valida criptograficamente (CRC-16) um payload Pix EMV BRCode."""
    limpo = payload.strip()
    motivos: list[str] = []

    idx_crc = limpo.rfind("6304")
    if idx_crc == -1 or len(limpo) < idx_crc + 8:
        payload_masc, _ = mascarar(limpo)
        return DadosPixBRCode(
            payload_mascarado=payload_masc,
            crc16_valido=False,
            suspeito=True,
            motivos=["QR Code Pix inválido: tag CRC-16 (6304) ausente ou truncada."],
        )

    corpo_sem_crc = limpo[: idx_crc + 4]
    crc_informado = limpo[idx_crc + 4 : idx_crc + 8].upper()
    crc_calculado = calcular_crc16_ccitt_false(corpo_sem_crc.encode("utf-8"))
    crc_ok = crc_informado == crc_calculado
    if not crc_ok:
        motivos.append(
            f"Checksum CRC-16 inválido no QR Code Pix (informado={crc_informado}, esperado={crc_calculado})."
        )

    tlv = _ler_tlv(limpo)
    tag26 = _ler_tlv(tlv.get("26", ""))
    chave = tag26.get("01")
    url_dinamica = tag26.get("25")
    tipo_chave = _classificar_chave_pix(chave)
    mcc = tlv.get("52")
    nome_recebedor = tlv.get("59")
    cidade = tlv.get("60")

    valor_centavos: int | None = None
    if tlv.get("54"):
        try:
            dec = Decimal(tlv["54"].replace(",", "."))
            if not dec.is_finite() or dec < 0:
                motivos.append("Valor negativo ou inválido na tag 54 do QR Code Pix.")
            else:
                valor_centavos = int((dec * 100).to_integral_value())
        except (InvalidOperation, ValueError, OverflowError):
            motivos.append("Valor inválido na tag 54 do QR Code Pix.")

    if mcc == "7995":
        motivos.append("QR Code Pix identificado com MCC 7995 (apostas online / bets).")
    if url_dinamica and any(dom in url_dinamica.lower() for dom in _DOMINIOS_SUSPEITOS):
        motivos.append("URL dinâmica do Pix aponta para domínio suspeito/encurtador.")

    payload_redigido = limpo
    if chave:
        payload_redigido = payload_redigido.replace(chave, "[CHAVE_PIX]")
    if nome_recebedor and tipo_chave == "cpf":
        payload_redigido = payload_redigido.replace(nome_recebedor, "***")
    payload_masc, _ = mascarar(payload_redigido)
    chave_masc = "[CPF]" if tipo_chave == "cpf" else (mascarar(chave)[0] if chave else None)
    nome_masc = "***" if (nome_recebedor and tipo_chave == "cpf") else (mascarar(nome_recebedor)[0] if nome_recebedor else None)
    url_masc = mascarar(url_dinamica)[0] if url_dinamica else None

    return DadosPixBRCode(
        payload_mascarado=payload_masc,
        crc16_valido=crc_ok,
        chave_pix_mascarada=chave_masc,
        tipo_chave=tipo_chave,
        nome_recebedor_mascarado=nome_masc,
        cidade=cidade,
        valor_centavos=valor_centavos,
        mcc=mcc,
        url_dinamica=url_masc,
        suspeito=bool(motivos),
        motivos=motivos,
    )


def _ler_codigos_na_imagem(img: Image.Image) -> tuple[str | None, str | None, str | None]:
    barras_44: str | None = None
    linha_47: str | None = None
    qr_pix_bruto: str | None = None
    leituras = list(zxingcpp.read_barcodes(img))
    if not any(c.format == zxingcpp.BarcodeFormat.QRCode for c in leituras):
        leituras.extend(zxingcpp.read_barcodes(img, formats=zxingcpp.BarcodeFormat.QRCode))
    if not any(c.format == zxingcpp.BarcodeFormat.ITF for c in leituras):
        leituras.extend(zxingcpp.read_barcodes(img, formats=zxingcpp.BarcodeFormat.ITF))
    for codigo in leituras:
        texto = (codigo.text or "").strip()
        if codigo.format == zxingcpp.BarcodeFormat.QRCode and (
            "BR.GOV.BCB.PIX" in texto.upper() or texto.startswith("000201")
        ):
            qr_pix_bruto = texto
        elif codigo.format == zxingcpp.BarcodeFormat.ITF:
            dig = re.sub(r"\D", "", texto)
            if len(dig) == 44:
                barras_44 = dig
                linha_47 = barras_44_para_linha_digitavel_47(dig)
            elif len(dig) == 45 and validar_barras_44(dig[:44])[0]:
                barras_44 = dig[:44]
                linha_47 = barras_44_para_linha_digitavel_47(dig[:44])
            elif len(dig) == 47:
                linha_47 = dig
                barras_44 = linha_digitavel_47_para_barras_44(dig)
    return barras_44, linha_47, qr_pix_bruto


def ler_codigos_imagem_ou_pdf(dados: bytes, mime_type: str) -> dict[str, Any]:
    """Extrai códigos ITF-25 (boletos) e QR Codes Pix BRCode em resolução cheia com zxing-cpp."""
    barras_44: str | None = None
    linha_47: str | None = None
    qr_pix_bruto: str | None = None

    if mime_type == "application/pdf":
        with pymupdf.open(stream=dados, filetype="pdf") as doc:
            for pag in itertools.islice(doc, 3):
                pix = pag.get_pixmap(dpi=200)
                with Image.open(io.BytesIO(pix.tobytes("png"))) as img:
                    b44, l47, qr = _ler_codigos_na_imagem(img)
                    barras_44 = barras_44 or b44
                    linha_47 = linha_47 or l47
                    qr_pix_bruto = qr_pix_bruto or qr
    else:
        with Image.open(io.BytesIO(dados)) as img:
            barras_44, linha_47, qr_pix_bruto = _ler_codigos_na_imagem(img)

    return {
        "barras_44": barras_44,
        "linha_47": linha_47,
        "qr_pix_bruto": qr_pix_bruto,
    }
