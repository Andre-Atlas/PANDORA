"""Parser de CSV: extratos de banco (; e vírgula, valor brasileiro) e o dataset sintético das personas (#51)."""
from __future__ import annotations

import csv
import io
import re

from pandora_ingestion.erros import ArquivoIlegivel
from pandora_ingestion.esquema import Leitura, Origem, Transacao
from pandora_ingestion.mascara import mascarar
from pandora_ingestion.normalizar import (
    aplicar_natureza,
    centavos,
    data_do_texto,
    forma_de_pagamento,
    mcc_valido,
    parcela_da_descricao,
)

COLUNAS = {
    "data": ("posted_at", "data", "data_hora", "data lancamento", "data lançamento", "date"),
    "valor": ("amount", "valor", "value"),
    "descricao": ("description_masked", "descricao", "descrição", "historico", "histórico", "lancamento",
                  "lançamento", "description"),
    "natureza": ("tipo", "natureza", "dc", "d/c", "type"),
    "forma": ("payment_method", "forma_pagamento"),
    "mcc": ("mcc",),
    "categoria": ("category", "categoria"),
    "essencial": ("is_essential", "essencial"),
    "conta": ("cartao_ou_conta_id", "conta_id", "conta", "persona_id"),
    "id": ("transaction_id", "id", "fitid", "documento"),
}
OBRIGATORIAS = ("data", "valor", "descricao")
MAXIMO_AVISOS = 20


def ler_csv(conteudo: bytes, nomes: tuple[str, ...] = ()) -> Leitura:
    texto = _decodificar(conteudo)
    linhas = csv.reader(io.StringIO(texto), delimiter=_separador(texto))
    cabecalho = [c.strip().lower() for c in next(linhas, [])]
    indices = {campo: _indice(cabecalho, opcoes) for campo, opcoes in COLUNAS.items()}
    faltando = [c for c in OBRIGATORIAS if indices[c] is None]
    if faltando:
        raise ArquivoIlegivel(f"Não encontramos as colunas: {', '.join(faltando)}.")

    transacoes: list[Transacao] = []
    avisos: list[str] = []
    problemas = 0
    for numero, linha in enumerate(linhas, start=2):
        if not any(c.strip() for c in linha):
            continue
        try:
            transacoes.append(_transacao(linha, indices, nomes))
        except ValueError as erro:
            problemas += 1
            if problemas <= MAXIMO_AVISOS:
                avisos.append(f"Linha {numero}: {erro}")  # só o motivo: o conteúdo da linha pode ter PII
    if problemas > MAXIMO_AVISOS:
        avisos.append(f"Mais {problemas - MAXIMO_AVISOS} linha(s) com problema não listadas.")
    if not transacoes:
        raise ArquivoIlegivel("Nenhuma transação pôde ser lida. " + " ".join(avisos[:3]))
    return Leitura(tuple(transacoes), tuple(avisos))


def _decodificar(conteudo: bytes) -> str:
    try:
        return conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        return conteudo.decode("latin-1")  # exportação comum de bancos brasileiros


def _separador(texto: str) -> str:
    primeira = texto.split("\n", 1)[0]
    return ";" if primeira.count(";") > primeira.count(",") else ","


def _indice(cabecalho: list[str], opcoes: tuple[str, ...]) -> int | None:
    return next((cabecalho.index(o) for o in opcoes if o in cabecalho), None)


def _celula(linha: list[str], indice: int | None) -> str:
    return linha[indice].strip() if indice is not None and indice < len(linha) else ""


def _booleano(texto: str) -> bool | None:
    return {"true": True, "1": True, "sim": True, "false": False, "0": False, "nao": False, "não": False}.get(
        texto.lower()
    )


def _transacao(linha: list[str], i: dict[str, int | None], nomes: tuple[str, ...]) -> Transacao:
    bruta = _celula(linha, i["descricao"])
    if not bruta:
        raise ValueError("descrição vazia.")
    valor = centavos(_celula(linha, i["valor"]))
    if i["natureza"] is not None:
        valor = aplicar_natureza(valor, _celula(linha, i["natureza"]))
    descricao = mascarar(bruta, nomes)
    forma = forma_de_pagamento(_celula(linha, i["forma"]), bruta)
    categoria = _celula(linha, i["categoria"]).upper() or None
    return Transacao(
        conta_id=_celula(linha, i["conta"]) or "principal",
        data_hora=data_do_texto(_celula(linha, i["data"])),
        valor_centavos=valor,
        forma_pagamento=forma,
        descricao_mascarada=descricao,
        origem=Origem.CSV,
        mcc=mcc_valido(_celula(linha, i["mcc"])),
        parcela=parcela_da_descricao(descricao),
        categoria_no_arquivo=categoria if categoria and re.fullmatch(r"[A-Z_]+", categoria) else None,
        essencial_no_arquivo=_booleano(_celula(linha, i["essencial"])),
        id_externo=_celula(linha, i["id"]) or None,
    )
