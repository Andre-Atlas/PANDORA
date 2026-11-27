"""Parser de PDF de extrato e de fatura de cartão, com pdfplumber.

Lê as palavras com a posição na página e monta as linhas. Dois modos:

- **Com cabeçalho de colunas** (Data, Descrição, Valor, Débito, Crédito, Saldo): cada valor vai para a
  coluna de cabeçalho mais próxima. Funciona com ou sem grade desenhada.
- **Fatura de cartão** (sem cabeçalho de colunas): data no começo da linha, valor no fim; compra é saída,
  pagamento, estorno ou valor com "-" ou "CR" é entrada.

O conteúdo do PDF é sempre dado: nada é executado nem interpretado como instrução, só linhas que começam
com data e têm valor viram transação, e o que não deu para ler vira aviso (sem o conteúdo da linha), nunca
um valor inventado. PDF escaneado, sem texto, pede OCR (`PrecisaDeOcr`).
"""
from __future__ import annotations

import io
import logging
import re
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime

import pdfplumber

from pandora_ingestion.erros import ArquivoIlegivel
from pandora_ingestion.esquema import (
    FUSO_DA_PESSOA,
    FormaPagamento,
    Leitura,
    Origem,
    Transacao,
)
from pandora_ingestion.mascara import mascarar
from pandora_ingestion.normalizar import (
    centavos,
    forma_de_pagamento,
    parcela_da_descricao,
)

# O pdfminer registra em DEBUG cada operação de texto do PDF, ou seja, o conteúdo do extrato. Nunca em log.
for _nome in ("pdfminer", "pdfplumber"):
    logging.getLogger(_nome).setLevel(logging.ERROR)

MAXIMO_PAGINAS = 60
MAXIMO_AVISOS = 20
TOLERANCIA_LINHA = 3.0  # pontos de diferença vertical para duas palavras estarem na mesma linha

_DATA = re.compile(r"^(\d{2})/(\d{2})(?:/(\d{4}|\d{2}))?$")
_VALOR = re.compile(r"^\(?-?R?\$?\d{1,3}(?:\.\d{3})*,\d{2}\)?-?$|^-?R?\$?\d+,\d{2}-?$")
_PERIODO = re.compile(r"(\d{2}/\d{2}/\d{4})\s*(?:a|até|ate|-|–)\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
_VENCIMENTO = re.compile(r"vencimento\D{0,12}(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
_CONTROLE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_CABECALHO = {
    "data": "data",
    "descricao": "descricao", "historico": "descricao", "lancamento": "descricao", "lancamentos": "descricao",
    "discriminacao": "descricao",
    "valor": "valor", "debito": "debito", "credito": "credito", "saldo": "saldo",
}
_COLUNAS_DE_VALOR = ("valor", "debito", "credito", "saldo")
_ENTRADA_NA_FATURA = ("PAGAMENTO", "PGTO", "ESTORNO", "CREDITO", "DEVOLUCAO")


class PrecisaDeOcr(ArquivoIlegivel):
    """O PDF é imagem (escaneado ou foto): sem texto para ler. O OCR é do Agente Multimodal (#73)."""


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


@dataclass(frozen=True)
class _Palavra:
    texto: str
    x0: float
    x1: float

    @property
    def centro(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass(frozen=True)
class _Contexto:
    periodo: tuple[date, date] | None
    vencimento: date | None
    fatura: bool


def _linhas(pagina) -> list[list[_Palavra]]:
    palavras = pagina.extract_words(x_tolerance=1.5, y_tolerance=2)
    palavras.sort(key=lambda p: (round(p["top"]), p["x0"]))
    linhas: list[tuple[float, list[_Palavra]]] = []
    for p in palavras:
        palavra = _Palavra(_CONTROLE.sub("", p["text"]), p["x0"], p["x1"])
        if linhas and abs(linhas[-1][0] - p["top"]) <= TOLERANCIA_LINHA:
            linhas[-1][1].append(palavra)
        else:
            linhas.append((p["top"], [palavra]))
    return [sorted(l, key=lambda w: w.x0) for _, l in linhas]


def _data_br(texto: str) -> date:
    dia, mes, ano = texto.split("/")
    return date(int(ano), int(mes), int(dia))


def _contexto(texto: str) -> _Contexto:
    periodo = None
    achado = _PERIODO.search(texto)
    if achado:
        try:
            periodo = (_data_br(achado[1]), _data_br(achado[2]))
        except ValueError:
            periodo = None
    venc = _VENCIMENTO.search(texto)
    vencimento = None
    if venc:
        try:
            vencimento = _data_br(venc[1])
        except ValueError:
            vencimento = None
    return _Contexto(periodo, vencimento, "fatura" in _sem_acento(texto))


def _data_da_linha(token: str, contexto: _Contexto) -> datetime:
    achada = _DATA.match(token)
    if not achada:
        raise ValueError("data inválida.")
    dia, mes, ano = int(achada[1]), int(achada[2]), achada[3]
    try:
        if ano:
            com_ano = date(int(ano) + (2000 if len(ano) == 2 else 0), mes, dia)
            if contexto.periodo and not contexto.periodo[0] <= com_ano <= contexto.periodo[1]:
                raise ValueError("data fora do período do documento.")
            return _como_data_hora(com_ano)
        if contexto.periodo:
            inicio, fim = contexto.periodo
            for y in sorted({inicio.year, fim.year}):
                if inicio <= date(y, mes, dia) <= fim:
                    return _como_data_hora(date(y, mes, dia))
            raise ValueError("data fora do período do documento.")
        if contexto.vencimento:
            v = contexto.vencimento
            return _como_data_hora(date(v.year if mes <= v.month else v.year - 1, mes, dia))
    except ValueError as erro:
        if "fora do período" in str(erro):
            raise
        raise ValueError("data inválida.") from None
    raise ValueError("o documento não informa o ano (período ou vencimento).")


def _como_data_hora(dia: date) -> datetime:
    return datetime(dia.year, dia.month, dia.day, tzinfo=FUSO_DA_PESSOA)


def _cabecalho(linhas: list[list[_Palavra]]) -> tuple[int, dict[str, _Palavra]] | None:
    """Primeira linha com 'data' e pelo menos uma coluna de valor: devolve o índice e a âncora de cada coluna."""
    for indice, linha in enumerate(linhas):
        ancoras: dict[str, _Palavra] = {}
        for palavra in linha:
            campo = _CABECALHO.get(_sem_acento(palavra.texto).strip("():"))
            if campo and campo not in ancoras:
                ancoras[campo] = palavra
        if "data" in ancoras and any(c in ancoras for c in ("valor", "debito", "credito")):
            return indice, ancoras
    return None


def _coluna(palavra: _Palavra, ancoras: dict[str, _Palavra]) -> str:
    def distancia(campo: str) -> float:
        a = ancoras[campo]
        return min(abs(palavra.x1 - a.x1), abs(palavra.centro - a.centro))

    return min((c for c in _COLUNAS_DE_VALOR if c in ancoras), key=distancia)


def _transacao_com_colunas(linha: list[_Palavra], ancoras: dict[str, _Palavra], contexto: _Contexto, nomes) -> Transacao:
    data = _data_da_linha(linha[0].texto, contexto)
    valores: dict[str, str] = {}
    descricao: list[str] = []
    for palavra in linha[1:]:
        if palavra.texto.upper() == "R$":
            continue
        if _VALOR.match(palavra.texto):
            coluna = _coluna(palavra, ancoras)
            if coluna in valores:
                raise ValueError("mais de um valor na mesma coluna.")
            valores[coluna] = palavra.texto
        else:
            descricao.append(palavra.texto)
    com_valor = {c: v for c, v in valores.items() if c != "saldo"}
    if len(com_valor) != 1:
        raise ValueError("não foi possível identificar o valor da linha.")
    coluna, texto = next(iter(com_valor.items()))
    valor = centavos(texto)
    if coluna == "debito":
        valor = -abs(valor)
    elif coluna == "credito":
        valor = abs(valor)
    return _montar(data, valor, " ".join(descricao), nomes, cartao=False)


def _transacao_de_fatura(linha: list[_Palavra], contexto: _Contexto, nomes) -> Transacao:
    data = _data_da_linha(linha[0].texto, contexto)
    corpo = [p.texto for p in linha[1:] if p.texto.upper() != "R$"]
    credito_marcado = bool(corpo) and corpo[-1].upper() == "CR"
    if credito_marcado:
        corpo = corpo[:-1]
    if not corpo or not _VALOR.match(corpo[-1]):
        raise ValueError("não foi possível identificar o valor da linha.")
    texto_valor, descricao = corpo[-1], " ".join(corpo[:-1])
    valor = centavos(texto_valor)
    credito = credito_marcado or valor < 0 or _sem_acento(descricao).upper().startswith(_ENTRADA_NA_FATURA)
    valor = abs(valor) if credito else -abs(valor)  # na fatura, compra vem positiva e é saída
    return _montar(data, valor, descricao, nomes, cartao=True)


def _montar(data: datetime, valor: int, bruta: str, nomes, cartao: bool) -> Transacao:
    bruta = bruta.strip()
    if not bruta:
        raise ValueError("descrição vazia.")
    descricao = mascarar(bruta, nomes)
    forma = FormaPagamento.CARTAO_CREDITO if cartao else forma_de_pagamento(bruta)
    return Transacao(
        conta_id="cartao" if cartao else "principal",
        data_hora=data,
        valor_centavos=valor,
        forma_pagamento=forma,
        descricao_mascarada=descricao,
        origem=Origem.PDF,
        parcela=parcela_da_descricao(descricao),
    )


def _reconciliar_saldos(
    todas: list[list[_Palavra]],
    transacoes: list[Transacao],
    fatura: bool,
) -> tuple[bool | None, int]:
    """Confere em centavos inteiros se Saldo Anterior + lançamentos == Saldo Final."""
    saldo_inicial: int | None = None
    saldo_final: int | None = None
    total_fatura: int | None = None

    for linha in todas:
        texto_linha = _sem_acento(" ".join(p.texto for p in linha))
        valores = [p.texto for p in linha if _VALOR.match(p.texto)]
        if not valores:
            continue
        if ("saldo anterior" in texto_linha or "saldo inicial" in texto_linha) and saldo_inicial is None:
            try:
                saldo_inicial = centavos(valores[-1])
            except ValueError:
                pass
        elif ("saldo final" in texto_linha or "saldo atual" in texto_linha) and saldo_final is None:
            try:
                saldo_final = centavos(valores[-1])
            except ValueError:
                pass
        elif fatura and "total da fatura" in texto_linha and total_fatura is None:
            try:
                total_fatura = abs(centavos(valores[-1]))
            except ValueError:
                pass

    if saldo_inicial is not None and saldo_final is not None:
        esperado = saldo_inicial + sum(t.valor_centavos for t in transacoes)
        divergencia = saldo_final - esperado
        return divergencia == 0, divergencia

    if fatura and total_fatura is not None and not any(t.valor_centavos > 0 for t in transacoes):
        esperado_fatura = sum(abs(t.valor_centavos) for t in transacoes)
        divergencia = total_fatura - esperado_fatura
        return divergencia == 0, divergencia

    return None, 0


def _processar_linhas_pdf(
    todas: list[list[_Palavra]],
    nomes: tuple[str, ...] = (),
    usou_ocr: bool = False,
) -> Leitura:
    texto = "\n".join(" ".join(p.texto for p in linha) for linha in todas)
    contexto = _contexto(texto)

    cabecalho = _cabecalho(todas)
    if cabecalho is None and not contexto.fatura:
        raise ArquivoIlegivel("Não reconhecemos o layout do PDF: sem cabeçalho de colunas nem fatura de cartão.")

    transacoes: list[Transacao] = []
    avisos: list[str] = []
    problemas = 0
    for numero, linha in enumerate(todas, start=1):
        if not _DATA.match(linha[0].texto):
            continue  # cabeçalho, saldo, rodapé, qualquer texto livre: só linha com data vira transação
        if cabecalho and linha is todas[cabecalho[0]]:
            continue
        try:
            if cabecalho:
                transacoes.append(_transacao_com_colunas(linha, cabecalho[1], contexto, nomes))
            else:
                transacoes.append(_transacao_de_fatura(linha, contexto, nomes))
        except ValueError as erro:
            problemas += 1
            if problemas <= MAXIMO_AVISOS:
                avisos.append(f"Linha {numero} do PDF: {erro}")
    if problemas > MAXIMO_AVISOS:
        avisos.append(f"Mais {problemas - MAXIMO_AVISOS} linha(s) com problema não listadas.")
    if not transacoes:
        raise ArquivoIlegivel("Nenhuma transação pôde ser lida. " + " ".join(avisos[:3]))
    reconciliado, divergencia = _reconciliar_saldos(todas, transacoes, contexto.fatura)
    return Leitura(
        tuple(transacoes),
        tuple(avisos),
        reconciliado=reconciliado,
        divergencia_centavos=divergencia,
        usou_ocr=usou_ocr,
    )


def ler_linhas_ocr(linhas_texto: Sequence[str], nomes: tuple[str, ...] = ()) -> Leitura:
    """Reaproveita o parser determinístico de PDF sobre linhas de texto extraídas via OCR/VLM."""
    todas: list[list[_Palavra]] = []
    for bruta in linhas_texto:
        limpa = _CONTROLE.sub("", bruta).strip()
        if not limpa:
            continue
        palavras: list[_Palavra] = []
        cursor = 0.0
        for tok in limpa.split():
            largura = float(len(tok) * 6)
            palavras.append(_Palavra(tok, cursor, cursor + largura))
            cursor += largura + 6.0
        if palavras:
            todas.append(palavras)
    if not todas:
        raise ArquivoIlegivel("OCR não retornou linhas legíveis para o PDF.")
    return _processar_linhas_pdf(todas, nomes=nomes, usou_ocr=True)


def ler_pdf(
    conteudo: bytes,
    nomes: tuple[str, ...] = (),
    extrator_ocr: Callable[[bytes], Sequence[str]] | None = None,
) -> Leitura:
    try:
        pdf = pdfplumber.open(io.BytesIO(conteudo))
    except Exception:  # pdfminer levanta vários tipos; a mensagem para a pessoa é uma só
        raise ArquivoIlegivel("Não foi possível abrir o PDF. Ele pode estar corrompido ou protegido por senha.") from None
    with pdf:
        if len(pdf.pages) > MAXIMO_PAGINAS:
            raise ArquivoIlegivel(f"O PDF tem mais de {MAXIMO_PAGINAS} páginas.")
        try:
            paginas = [_linhas(p) for p in pdf.pages]
        except Exception:
            raise ArquivoIlegivel("Não foi possível ler o texto do PDF.") from None

    todas = [linha for pagina in paginas for linha in pagina]
    if not todas:
        if extrator_ocr is not None:
            return ler_linhas_ocr(extrator_ocr(conteudo), nomes=nomes)
        raise PrecisaDeOcr("O PDF não tem texto para ler (parece escaneado). É preciso passar por OCR.")
    return _processar_linhas_pdf(todas, nomes=nomes, usou_ocr=False)
