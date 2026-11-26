"""Leitor PROVISÓRIO de CSV, até a ingestão da Luana (#57) chegar.

Lê o formato do dataset sintético (#51: `posted_at`, `amount`,
`description_masked`...) e CSVs simples com `data`, `valor` e `descricao`,
separados por vírgula ou ponto e vírgula. OFX e PDF ficam para #57 e #66.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import PurePath

from pandora_api.dominio.erros import ArquivoIlegivel, FormatoNaoSuportado
from pandora_api.dominio.transacao import (
    FUSO_DA_PESSOA,
    Categoria,
    FormaPagamento,
    Parcela,
    TransacaoLida,
    mascarar_descricao,
)
from pandora_api.portas.ingestao import LeituraExtrato

COLUNAS = {
    "data": ("posted_at", "data", "data_hora", "date"),
    "valor": ("amount", "valor"),
    "descricao": ("description_masked", "descricao", "descrição", "historico", "histórico", "description"),
    "forma": ("payment_method", "forma_pagamento"),
    "mcc": ("mcc",),
    "categoria": ("category", "categoria"),
    "essencial": ("is_essential", "essencial"),
    "conta": ("cartao_ou_conta_id", "conta_id", "conta"),
}
OBRIGATORIAS = ("data", "valor", "descricao")
MAXIMO_AVISOS = 20
_PARCELA = re.compile(r"PARC(?:ELA)?\s*(\d{1,2})\s*/\s*(\d{1,2})", re.IGNORECASE)


class LeitorCsvProvisorio:
    def ler(self, nome_arquivo: str, conteudo: bytes) -> LeituraExtrato:
        extensao = PurePath(nome_arquivo).suffix.lower()
        if extensao == ".ofx":
            raise FormatoNaoSuportado("Ainda não lemos OFX. Chega com a issue #57; por enquanto, envie em CSV.")
        if extensao == ".pdf":
            raise FormatoNaoSuportado("Ainda não lemos PDF. Chega com a issue #66; por enquanto, envie em CSV.")
        if extensao not in (".csv", ".txt"):
            raise FormatoNaoSuportado("Envie o extrato em CSV, OFX ou PDF.")

        linhas = csv.reader(io.StringIO(_decodificar(conteudo)), delimiter=_separador(conteudo))
        cabecalho = [c.strip().lower() for c in next(linhas, [])]
        indices = {campo: _indice(cabecalho, nomes) for campo, nomes in COLUNAS.items()}
        faltando = [c for c in OBRIGATORIAS if indices[c] is None]
        if faltando:
            raise ArquivoIlegivel(f"Não encontramos as colunas: {', '.join(faltando)}.")

        transacoes: list[TransacaoLida] = []
        avisos: list[str] = []
        problemas = 0
        for numero, linha in enumerate(linhas, start=2):
            if not any(c.strip() for c in linha):
                continue
            try:
                transacoes.append(_transacao(linha, indices))
            except ValueError as erro:
                problemas += 1
                if problemas <= MAXIMO_AVISOS:
                    avisos.append(f"Linha {numero}: {erro}")
        if problemas > MAXIMO_AVISOS:
            avisos.append(f"Mais {problemas - MAXIMO_AVISOS} linha(s) com problema não listadas.")
        if not transacoes:
            raise ArquivoIlegivel("Nenhuma transação pôde ser lida. " + " ".join(avisos[:3]))
        return LeituraExtrato(tuple(transacoes), tuple(avisos))


def _decodificar(conteudo: bytes) -> str:
    try:
        return conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        return conteudo.decode("latin-1")  # exportação comum de bancos brasileiros


def _separador(conteudo: bytes) -> str:
    primeira = conteudo.split(b"\n", 1)[0]
    return ";" if primeira.count(b";") > primeira.count(b",") else ","


def _indice(cabecalho: list[str], nomes: tuple[str, ...]) -> int | None:
    return next((cabecalho.index(n) for n in nomes if n in cabecalho), None)


def _celula(linha: list[str], indice: int | None) -> str:
    if indice is None or indice >= len(linha):
        return ""
    return linha[indice].strip()


def _transacao(linha: list[str], i: dict[str, int | None]) -> TransacaoLida:
    descricao = mascarar_descricao(_celula(linha, i["descricao"]))
    if not descricao:
        raise ValueError("descrição vazia.")
    mcc = _celula(linha, i["mcc"])
    achada = _PARCELA.search(descricao)
    parcela = Parcela(int(achada[1]), int(achada[2])) if achada and 0 < int(achada[1]) <= int(achada[2]) else None
    return TransacaoLida(
        conta_id=_celula(linha, i["conta"]) or "principal",
        data_hora=_data(_celula(linha, i["data"])),
        valor_centavos=_centavos(_celula(linha, i["valor"])),
        forma_pagamento=_forma(_celula(linha, i["forma"])),
        descricao_mascarada=descricao,
        mcc=mcc if re.fullmatch(r"\d{4}", mcc) and mcc != "0000" else None,
        parcela=parcela,
        categoria_no_arquivo=_categoria(_celula(linha, i["categoria"])),
        essencial_no_arquivo=_booleano(_celula(linha, i["essencial"])),
    )


def _data(texto: str) -> datetime:
    for formato in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            momento = datetime.strptime(texto, formato)
            break
        except ValueError:
            continue
    else:
        try:
            momento = datetime.fromisoformat(texto)
        except ValueError:
            raise ValueError(f"data inválida ({texto!r}).") from None
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=FUSO_DA_PESSOA)  # extrato sem fuso está no horário de Brasília
    return momento


def _centavos(texto: str) -> int:
    limpo = texto.replace("R$", "").replace(" ", "")
    if "," in limpo:  # formato brasileiro: 1.234,56
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        centavos = Decimal(limpo) * 100
    except InvalidOperation:
        raise ValueError(f"valor inválido ({texto!r}).") from None
    if centavos != centavos.to_integral_value():
        raise ValueError(f"valor com mais de 2 casas decimais ({texto!r}).")
    return int(centavos)


def _forma(texto: str) -> FormaPagamento:
    try:
        return FormaPagamento(texto.upper())
    except ValueError:
        return FormaPagamento.OUTRA


def _categoria(texto: str) -> Categoria | None:
    try:
        return Categoria(texto.upper()) if texto else None
    except ValueError:
        return None


def _booleano(texto: str) -> bool | None:
    return {"true": True, "1": True, "sim": True, "false": False, "0": False, "nao": False, "não": False}.get(
        texto.lower()
    )
