"""Normalização e métricas de sobreposição de texto (BLEU, ROUGE) para português.

O tokenizador padrão do `rouge-score` descarta letras acentuadas; aqui o texto é
tokenizado por palavras Unicode, em minúsculas e sem pontuação.
"""
from __future__ import annotations

import re
import unicodedata

RE_PALAVRA = re.compile(r"\w+(?:[.,]\d+)*", re.U)
RE_NUMERO = re.compile(r"\d+(?:[.,]\d+)*")


def normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texto).casefold()).strip()


def palavras(texto: str) -> list[str]:
    return [p.strip(".,") for p in RE_PALAVRA.findall(normalizar(texto)) if p.strip(".,")]


class TokenizadorPT:
    """Interface esperada pelo `rouge-score`."""

    def tokenize(self, texto: str) -> list[str]:
        return palavras(texto)


def bleu(hipoteses: list[str], referencias: list[str]) -> float:
    """BLEU de corpus (0 a 100), com tokenização internacional do sacrebleu."""
    import sacrebleu

    return float(sacrebleu.corpus_bleu(hipoteses, [referencias], tokenize="intl").score)


def bleu_sentenca(hipotese: str, referencia: str) -> float:
    import sacrebleu

    return float(sacrebleu.sentence_bleu(hipotese, [referencia], tokenize="intl").score)


def rouge(hipotese: str, referencia: str) -> dict[str, float]:
    """F1 de ROUGE-1, ROUGE-2 e ROUGE-L (0 a 1)."""
    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False, tokenizer=TokenizadorPT())
    s = scorer.score(referencia, hipotese)
    return {k: float(v.fmeasure) for k, v in s.items()}


def numeros(texto: str) -> set[str]:
    """Números do texto, sem separador de milhar ('1.000' e '1000' contam como iguais)."""
    saida = set()
    for n in RE_NUMERO.findall(texto):
        if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", n):  # '50.000' e '50.000,00': ponto de milhar, vírgula decimal
            v = n.replace(".", "").replace(",", ".")
        else:
            v = n.replace(",", ".")
        if re.fullmatch(r"\d+\.0+", v):  # '600,00' e '600' são o mesmo valor
            v = v.split(".")[0]
        saida.add(v)
    return saida


def acerto_numerico(resposta: str, referencia: str) -> float | None:
    """Fração dos números da referência que aparecem na resposta; None se a referência não tem números."""
    alvo = numeros(referencia)
    if not alvo:
        return None
    return len(alvo & numeros(resposta)) / len(alvo)
