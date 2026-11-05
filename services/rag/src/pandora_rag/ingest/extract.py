"""Extrai texto limpo das fontes brutas em blocos (parágrafos) com página quando houver.

Regras que afetam a recuperação:
- trechos riscados nas leis compiladas do Planalto (revogados) são descartados;
- cabeçalhos e rodapés repetidos de PDF são removidos;
- o texto é normalizado em NFC, sem espaços invisíveis.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from pandora_rag.config import RAW_DIR, TEXT_DIR
from pandora_rag.ingest.collect import caminho_bruto
from pandora_rag.ingest.fontes import Fonte

BLOCOS = ("p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "blockquote", "pre", "div")
INVISIVEIS = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)
RISCADO = re.compile(r"line-through", re.I)
PRESERVAR = re.compile(r"^(S[ÚU]MULA|Art\.|CAP[ÍI]TULO|SE[ÇC][ÃA]O)\b", re.I)  # marcadores estruturais nunca são cabeçalho
QUEBRA = "\u2028"  # <br> é quebra de bloco; quebra de linha do código-fonte HTML não é


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFC", texto).translate(INVISIVEIS)
    texto = texto.replace("\xa0", " ").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", texto).strip()


def decodificar(dados: bytes) -> str:
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return dados.decode("cp1252", errors="replace")


def _descartar_riscados(sopa: BeautifulSoup) -> None:
    for tag in sopa.find_all(["strike", "s", "del"]):
        tag.decompose()
    for tag in sopa.find_all(style=RISCADO):
        tag.decompose()


def blocos_html(html: str) -> list[str]:
    sopa = BeautifulSoup(html, "lxml")
    for tag in sopa(["script", "style", "noscript", "nav", "header", "footer", "form", "svg", "title"]):
        tag.decompose()
    _descartar_riscados(sopa)
    for br in sopa.find_all("br"):
        br.replace_with(QUEBRA)
    saida: list[str] = []
    for el in sopa.find_all(BLOCOS):
        if not isinstance(el, Tag) or el.find(BLOCOS):
            continue
        for linha in el.get_text(" ").split(QUEBRA):
            linha = normalizar(linha)
            if linha:
                saida.append(linha)
    return saida


def blocos_pdf(dados: bytes) -> list[tuple[int, str]]:
    import pymupdf

    doc = pymupdf.open(stream=dados, filetype="pdf")
    paginas: list[list[str]] = []
    for pagina in doc:
        blocos = [b for b in pagina.get_text("blocks", sort=True) if b[6] == 0]
        paginas.append([normalizar(b[4].replace("\n", " ")) for b in blocos])
    chave = lambda t: re.sub(r"\d+", "#", t)[:80]  # noqa: E731
    # cabeçalho e rodapé: só os 2 primeiros e os 2 últimos blocos de cada página
    freq = Counter(chave(t) for pag in paginas for t in set(pag[:2] + pag[-2:]) if t)
    limite = max(3, int(len(paginas) * 0.4))
    saida: list[tuple[int, str]] = []
    for n, pag in enumerate(paginas, start=1):
        for k, t in enumerate(pag):
            borda = k < 2 or k >= len(pag) - 2
            if not t or len(t) < 2 or (borda and len(paginas) > 4 and freq[chave(t)] >= limite and len(t) < 120 and not PRESERVAR.match(t)):
                continue
            saida.append((n, t))
    return saida


def blocos_bcb(dados: bytes) -> list[str]:
    conteudo = json.loads(dados)["conteudo"][0]
    return blocos_html(conteudo["Texto"] or "")


def recortar(blocos: list[str], inicio: str | None, fim: str | None) -> list[str]:
    """Mantém só o corpo de páginas de notícia entre dois marcadores."""
    if inicio:
        ix = next((i for i, b in enumerate(blocos) if inicio in b), None)
        if ix is not None:
            blocos = blocos[ix:]
    if fim:
        ix = next((i for i, b in enumerate(blocos) if fim in b), None)
        if ix is not None:
            blocos = blocos[:ix]
    return blocos


def extrair(fonte: Fonte, raiz_bruta: Path = RAW_DIR) -> list[dict]:
    dados = caminho_bruto(fonte, raiz_bruta).read_bytes()
    if fonte.formato == "pdf":
        return [{"p": p, "t": t} for p, t in blocos_pdf(dados)]
    if fonte.formato == "bcb_api":
        blocos = blocos_bcb(dados)
    else:
        blocos = blocos_html(decodificar(dados))
    blocos = recortar(blocos, fonte.recorte_inicio, fonte.recorte_fim)
    return [{"p": None, "t": t} for t in blocos]


def salvar_texto(fonte: Fonte, blocos: list[dict], raiz: Path = TEXT_DIR) -> Path:
    raiz.mkdir(parents=True, exist_ok=True)
    caminho = raiz / f"{fonte.id}.jsonl"
    caminho.write_text("\n".join(json.dumps(b, ensure_ascii=False) for b in blocos) + "\n", encoding="utf-8")
    return caminho


def carregar_texto(fonte_id: str, raiz: Path = TEXT_DIR) -> list[dict]:
    linhas = (raiz / f"{fonte_id}.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in linhas if x]
