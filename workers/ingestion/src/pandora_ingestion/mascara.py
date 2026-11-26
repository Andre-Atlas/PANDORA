"""Máscara de dados pessoais na descrição da transação (RNF01).

Cobre CPF, CNPJ, e-mail, telefone, agência/conta, sequências longas de dígitos e nomes de pessoas.
Nome é o caso difícil: sem lista de nomes, só dá para pegar o que vem depois de expressões típicas de
extrato ("PIX ENVIADO", "TED", "TRANSF") e o nome do titular, quando o chamador o informa.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_CNPJ = re.compile(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)")
_CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
_CPF_PARCIAL = re.compile(r"[*•x]{3}\.?\d{3}\.?\d{3}-?[*•x]{2}", re.IGNORECASE)
_TELEFONE = re.compile(r"(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}(?!\d)")
_AGENCIA_CONTA = re.compile(
    r"\b(?:AG(?:ENCIA|\.)?|C/?C|CONTA(?: CORRENTE| POUPANCA)?|CC|CP)\s*[:.]?\s*\d(?:[\d.\-/ ]*\d)?",
    re.IGNORECASE,
)
_DIGITOS_LONGOS = re.compile(r"\d[\d .-]{5,}\d")

# Depois destas expressões, o que sobra costuma ser o nome da outra parte.
_ANTES_DE_NOME = re.compile(
    r"\b(PIX(?:\s+(?:ENVIADO|RECEBIDO|ENV|REC|TRANSF(?:ERENCIA)?))?|TRANSF(?:ERENCIA)?(?:\s+(?:ENVIADA|RECEBIDA|PIX))?"
    r"|TED|DOC|PAGAMENTO\s+PARA|PAGTO\s+PARA|ENVIADO\s+PARA|RECEBIDO\s+DE)\b\s*[-:]?\s*",
    re.IGNORECASE,
)
_EMPRESA = re.compile(
    r"\b(LTDA|S/?A|ME|MEI|EIRELI|EPP|BANCO|BCO|CARTAO|FATURA|LOJA|MERCADO|SUPERMERCADO|FARMACIA|POSTO|PADARIA"
    r"|RESTAURANTE|PAGSEGURO|MERCADOPAGO|NUBANK|ITAU|BRADESCO|SANTANDER|CAIXA|INSS|IPTU|IPVA|DARF|GPS)\b",
    re.IGNORECASE,
)
_PALAVRA_DE_NOME = re.compile(r"^[A-Za-zÀ-ÿ'.]+$")
_ARTIGOS = {"DE", "DA", "DO", "DAS", "DOS", "E"}


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def _parece_nome_de_pessoa(trecho: str) -> bool:
    palavras = trecho.split()
    if len(palavras) < 2 or len(palavras) > 6 or _EMPRESA.search(_sem_acento(trecho)):
        return False
    return all(_PALAVRA_DE_NOME.match(p) or p.upper() in _ARTIGOS for p in palavras)


def _mascarar_nome_depois_de_expressao(texto: str) -> str:
    achada = _ANTES_DE_NOME.search(texto)
    if not achada:
        return texto
    resto = texto[achada.end():]
    # o nome vai até o primeiro marcador de fim (números já mascarados, hífen, barra) ou o fim do texto
    nome = re.split(r"\s+-\s+|\s*\*\*\*|\s*/", resto, maxsplit=1)[0].strip()
    if nome and _parece_nome_de_pessoa(nome):
        return texto[: achada.end()] + "***" + resto[len(nome):]
    return texto


def mascarar(texto: str, nomes: Iterable[str] = (), limite: int = 200) -> str:
    """Devolve a descrição sem PII. `nomes` são nomes conhecidos (do titular) a esconder em qualquer posição."""
    for padrao in (_EMAIL, _CNPJ, _CPF, _CPF_PARCIAL, _AGENCIA_CONTA, _TELEFONE, _DIGITOS_LONGOS):
        texto = padrao.sub("***", texto)
    for nome in nomes:
        if nome and len(nome.strip()) >= 3:
            texto = re.sub(re.escape(nome.strip()), "***", texto, flags=re.IGNORECASE)
    texto = _mascarar_nome_depois_de_expressao(texto)
    return " ".join(texto.split())[:limite]
