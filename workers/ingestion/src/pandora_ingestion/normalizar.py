"""Normalização de datas, valores, sinais e forma de pagamento, comum a todos os parsers."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from pandora_ingestion.esquema import FUSO_DA_PESSOA, FormaPagamento, Parcela

_PARCELA = re.compile(r"PARC(?:ELA)?\s*(\d{1,2})\s*/\s*(\d{1,2})", re.IGNORECASE)
_FORMATOS_DATA = ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def data_do_texto(texto: str) -> datetime:
    """Data de extrato brasileiro (dd/mm/aaaa) ou ISO. Sem fuso vale o horário de Brasília."""
    texto = texto.strip()
    for formato in _FORMATOS_DATA:
        try:
            momento = datetime.strptime(texto, formato)
            break
        except ValueError:
            continue
    else:
        try:
            momento = datetime.fromisoformat(texto)
        except ValueError:
            raise ValueError("data inválida.") from None
    return _com_fuso(momento)


def _com_fuso(momento: datetime) -> datetime:
    if momento.tzinfo is None:
        return momento.replace(tzinfo=FUSO_DA_PESSOA)
    return momento.astimezone(FUSO_DA_PESSOA)


_OFX_DATA = re.compile(r"^(\d{4})(\d{2})(\d{2})(?:(\d{2})(\d{2})(\d{2}))?(?:\.\d+)?(?:\[\s*([+-]?\d+(?:\.\d+)?)(?::\w+)?\s*\])?$")


def data_do_ofx(texto: str) -> datetime:
    """DTPOSTED: AAAAMMDD[HHMMSS[.mmm]][[fuso:NOME]]."""
    achada = _OFX_DATA.match(texto.strip())
    if not achada:
        raise ValueError("data inválida.")
    ano, mes, dia, hora, minuto, segundo, fuso = achada.groups()
    try:
        momento = datetime(int(ano), int(mes), int(dia), int(hora or 0), int(minuto or 0), int(segundo or 0))
    except ValueError:
        raise ValueError("data inválida.") from None
    if fuso is not None:
        return momento.replace(tzinfo=timezone(timedelta(hours=float(fuso)))).astimezone(FUSO_DA_PESSOA)
    return _com_fuso(momento)


def centavos(texto: str) -> int:
    """'1.234,56', '1234.56', 'R$ -50,00', '(50,00)' e '50,00-' viram centavos inteiros, com sinal."""
    limpo = texto.replace("R$", "").replace(" ", "").replace(" ", "")
    negativo = False
    if limpo.startswith("(") and limpo.endswith(")"):
        negativo, limpo = True, limpo[1:-1]
    if limpo.endswith("-"):
        negativo, limpo = True, limpo[:-1]
    if "," in limpo:  # formato brasileiro: ponto separa milhar, vírgula separa centavos
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(limpo) * 100
    except InvalidOperation:
        raise ValueError("valor inválido.") from None
    if valor != valor.to_integral_value():
        raise ValueError("valor com mais de 2 casas decimais.")
    return -abs(int(valor)) if negativo else int(valor)


_SAIDA = {"d", "debito", "débito", "saida", "saída", "s", "debit"}
_ENTRADA = {"c", "credito", "crédito", "entrada", "e", "credit"}


def aplicar_natureza(valor_centavos: int, natureza: str) -> int:
    """Colunas D/C ou débito/crédito: o valor vem positivo e a natureza dá o sinal."""
    natureza = natureza.strip().lower()
    if natureza in _SAIDA:
        return -abs(valor_centavos)
    if natureza in _ENTRADA:
        return abs(valor_centavos)
    return valor_centavos


def forma_de_pagamento(*pistas: str) -> FormaPagamento:
    texto = " ".join(pistas).upper()
    if "PIX" in texto:
        return FormaPagamento.PIX
    if "BOLETO" in texto or "TITULO" in texto or "TÍTULO" in texto:
        return FormaPagamento.BOLETO
    if "DEB AUT" in texto or "DEBITO AUTOMATICO" in texto or "DÉBITO AUTOMÁTICO" in texto or "DIRECTDEBIT" in texto:
        return FormaPagamento.DEBITO_AUTOMATICO
    if "CREDITO" in texto and "COMPRA" in texto or "CREDIT_CARD" in texto or "CARTAO DE CREDITO" in texto:
        return FormaPagamento.CARTAO_CREDITO
    if "DEBITO" in texto and "COMPRA" in texto or "DEBIT_CARD" in texto or "CARTAO DE DEBITO" in texto:
        return FormaPagamento.CARTAO_DEBITO
    return FormaPagamento.OUTRA


def parcela_da_descricao(descricao: str) -> Parcela | None:
    achada = _PARCELA.search(descricao)
    if achada and 0 < int(achada[1]) <= int(achada[2]):
        return Parcela(int(achada[1]), int(achada[2]))
    return None


def mcc_valido(texto: str) -> str | None:
    texto = texto.strip()
    return texto if re.fullmatch(r"\d{4}", texto) and texto != "0000" else None
