"""Um coletor por tipo de fonte: HTML, PDF e API. Cada um valida o que baixou."""
from __future__ import annotations

import json
import re
from typing import Protocol

from pandora_rag.coleta.catalogo import Formato


class ConteudoInvalido(Exception):
    """A resposta veio com 200, mas não é o tipo de arquivo esperado (ex.: página de erro)."""


class Coletor(Protocol):
    extensao: str

    def validar(self, conteudo: bytes) -> None: ...

    def impressao(self, conteudo: bytes) -> bytes | None:
        """O que realmente define o documento, ou None quando o arquivo inteiro é o documento.

        Páginas web trazem ruído que muda a cada requisição (tokens de WAF, estado do React, contadores de
        cache). Detectar mudança sobre o texto visível evita regravar o bruto sem que nada tenha mudado.
        """
        ...


_SEM_TEXTO = re.compile(rb"<(script|style|noscript)\b.*?</\1\s*>|<!--.*?-->", re.IGNORECASE | re.DOTALL)
_TAGS = re.compile(rb"<[^>]+>")


class ColetorHtml:
    extensao = "html"

    def impressao(self, conteudo: bytes) -> bytes | None:
        texto = _TAGS.sub(b" ", _SEM_TEXTO.sub(b" ", conteudo))
        return b" ".join(texto.split())

    def validar(self, conteudo: bytes) -> None:
        inicio = conteudo[:4096].lower()
        if not any(marca in inicio for marca in (b"<html", b"<!doctype html", b"<body", b"<head")):
            raise ConteudoInvalido("a resposta não parece HTML")


class _Bruto:
    def impressao(self, conteudo: bytes) -> bytes | None:
        return None


class ColetorPdf(_Bruto):
    extensao = "pdf"

    def validar(self, conteudo: bytes) -> None:
        if not conteudo.lstrip()[:5] == b"%PDF-":
            raise ConteudoInvalido("a resposta não é um PDF")


class ColetorApi(_Bruto):
    """APIs devolvem JSON, salvo quando o alvo declara outra extensão (csv, zip)."""

    extensao = "json"

    def validar(self, conteudo: bytes) -> None:
        try:
            json.loads(conteudo)
        except ValueError as erro:
            raise ConteudoInvalido("a resposta da API não é JSON válido") from erro


class ColetorArquivo(ColetorApi):
    """Alvo de API com extensão própria (csv, zip): só confere que não veio vazio."""

    def __init__(self, extensao: str) -> None:
        self.extensao = extensao

    def validar(self, conteudo: bytes) -> None:
        if not conteudo:
            raise ConteudoInvalido("arquivo vazio")


COLETORES: dict[Formato, Coletor] = {"html": ColetorHtml(), "pdf": ColetorPdf(), "api": ColetorApi()}


def coletor_para(formato: Formato, ext: str | None = None) -> Coletor:
    if formato == "api" and ext and ext != "json":
        return ColetorArquivo(ext)
    return COLETORES[formato]
