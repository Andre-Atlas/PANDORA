"""Tokenizador do BM25: preserva números de norma e usa o stemmer RSLP para português.

`14.181/2021` vira `14181` e `2021`; `54-A` vira `54-a`. Os tokens de número não passam por
stemmer nem por lista de stopwords.
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

STOPWORDS = frozenset(
    """a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre entre ate ao aos
    e ou mas que se como quando onde qual quais quem cujo cuja ser sao era foi sera tem ter tinha ha houve
    esta estao estar este esse essa isso isto aquele aquela eu me meu minha seu sua nos nosso voce voces ele
    ela eles elas lhe lhes mais menos muito muita ja nao sim so tambem pelo pela pelos pelas num numa
    deste desta nesse nessa disto nisso art artigo paragrafo inciso""".split()
)
RE_TOKEN = re.compile(r"\d+(?:[./]\d+)*(?:-[a-z])?|[a-zà-ÿ]+", re.I)


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


@lru_cache(maxsize=1)
def _stemmer():
    import nltk
    from nltk.stem import RSLPStemmer

    try:
        return RSLPStemmer()
    except LookupError:
        nltk.download("rslp", quiet=True)
        return RSLPStemmer()


@lru_cache(maxsize=100_000)
def _raiz(palavra: str) -> str:
    return sem_acento(_stemmer().stem(palavra))


def tokenizar(texto: str) -> list[str]:
    texto = unicodedata.normalize("NFC", texto).lower()
    saida: list[str] = []
    for m in RE_TOKEN.finditer(texto):
        tok = m.group()
        if tok[0].isdigit():
            for parte in tok.split("/"):
                saida.append(parte.replace(".", ""))
        elif sem_acento(tok) not in STOPWORDS and len(tok) > 1:
            saida.append(_raiz(tok))
    return saida
