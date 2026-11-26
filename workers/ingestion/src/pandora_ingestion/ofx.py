"""Parser de OFX 1.x (SGML, sem tags de fechamento) e 2.x (XML).

Não usa biblioteca: lê só o que o esquema precisa (conta, data, valor, FITID, descrição) e é tolerante
com as variações dos bancos brasileiros (encoding 1252, vírgula decimal, tags sem fechamento).
"""
from __future__ import annotations

import re

from pandora_ingestion.erros import ArquivoIlegivel
from pandora_ingestion.esquema import FormaPagamento, Leitura, Origem, Transacao, hash_curto
from pandora_ingestion.mascara import mascarar
from pandora_ingestion.normalizar import centavos, data_do_ofx, forma_de_pagamento, parcela_da_descricao

_BLOCO = re.compile(r"<STMTTRN>(.*?)(?=</STMTTRN>|<STMTTRN>|</BANKTRANLIST>|</CCSTMTRS>|</STMTRS>|$)", re.DOTALL | re.IGNORECASE)
_CHARSET = re.compile(r"CHARSET:\s*(\w+)", re.IGNORECASE)
MAXIMO_AVISOS = 20


def _campo(trecho: str, tag: str) -> str | None:
    # OFX 1.x: <TAG>valor até o fim da linha ou da próxima tag; OFX 2.x: <TAG>valor</TAG>
    achada = re.search(rf"<{tag}>\s*([^<\r\n]*)", trecho, re.IGNORECASE)
    return achada.group(1).strip() if achada else None


def _decodificar(conteudo: bytes) -> str:
    cabecalho = conteudo[:400].decode("ascii", errors="ignore")
    achada = _CHARSET.search(cabecalho)
    if achada and achada.group(1) in ("1252", "WINDOWS-1252"):
        return conteudo.decode("cp1252", errors="replace")
    try:
        return conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        return conteudo.decode("cp1252", errors="replace")


def _conta(texto: str) -> str:
    """ACCTID é dado pessoal: o esquema guarda só um identificador opaco, derivado dele."""
    acct = _campo(texto, "ACCTID")
    return f"ofx-{hash_curto(acct)}" if acct else "principal"


def ler_ofx(conteudo: bytes, nomes: tuple[str, ...] = ()) -> Leitura:
    texto = _decodificar(conteudo)
    if "<OFX" not in texto.upper():
        raise ArquivoIlegivel("O arquivo não parece um OFX.")
    cartao = "<CCSTMTRS>" in texto.upper()
    conta = _conta(texto)
    transacoes: list[Transacao] = []
    avisos: list[str] = []
    problemas = 0
    for numero, bloco in enumerate(_BLOCO.finditer(texto), start=1):
        trecho = bloco.group(1)
        try:
            transacoes.append(_transacao(trecho, conta, cartao, nomes))
        except ValueError as erro:
            problemas += 1
            if problemas <= MAXIMO_AVISOS:
                avisos.append(f"Lançamento {numero}: {erro}")
    if problemas > MAXIMO_AVISOS:
        avisos.append(f"Mais {problemas - MAXIMO_AVISOS} lançamento(s) com problema não listados.")
    if not transacoes:
        raise ArquivoIlegivel("Nenhuma transação pôde ser lida. " + " ".join(avisos[:3]))
    return Leitura(tuple(transacoes), tuple(avisos))


def _transacao(trecho: str, conta: str, cartao: bool, nomes: tuple[str, ...]) -> Transacao:
    data, valor = _campo(trecho, "DTPOSTED"), _campo(trecho, "TRNAMT")
    if not data or not valor:
        raise ValueError("faltam data ou valor.")
    memo, nome, tipo = _campo(trecho, "MEMO") or "", _campo(trecho, "NAME") or "", _campo(trecho, "TRNTYPE") or ""
    bruta = memo or nome
    if not bruta:
        raise ValueError("descrição vazia.")
    descricao = mascarar(bruta, nomes)
    forma = forma_de_pagamento(tipo, memo, nome)
    if forma is FormaPagamento.OUTRA and cartao:
        forma = FormaPagamento.CARTAO_CREDITO  # extrato de cartão: o que não é outra coisa é compra no crédito
    return Transacao(
        conta_id=conta,
        data_hora=data_do_ofx(data),
        valor_centavos=centavos(valor),
        forma_pagamento=forma,
        descricao_mascarada=descricao,
        origem=Origem.OFX,
        parcela=parcela_da_descricao(descricao),
        id_externo=_campo(trecho, "FITID"),
    )
