"""Lacunas do corpus: perguntas em que o RAG se absteve viram consultas para achar fontes novas.

O registro é desligado por padrão (liga com PANDORA_REGISTRAR_LACUNAS=1) e guarda só a pergunta
mascarada: CPF, CNPJ, valores, números longos, e-mails, telefones, datas e nomes próprios saem antes
de qualquer coisa ir para o disco (LGPD). Nunca grava o contexto da conversa nem a resposta.
"""
from __future__ import annotations

import json
import re
import threading
import unicodedata
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from pandora_rag.config import LACUNAS_PATH

MASCARAS = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[email]"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[cpf]"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "[cnpj]"),
    (re.compile(r"R\$\s*[\d.,]+(?:\s*(?:mil|milh[õo]es|reais))?", re.IGNORECASE), "[valor]"),
    (re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b"), "[telefone]"),
    (re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"), "[data]"),
    (re.compile(r"\b\d[\d.,]{3,}\b"), "[numero]"),
]
# palavras com maiúscula que não são nome de pessoa e podem ficar na pergunta
TERMOS_LIVRES = {
    "pix", "cet", "cdc", "stf", "stj", "cnj", "cmn", "bcb", "cvm", "procon", "senacon", "serasa", "spc", "inss",
    "fgts", "iof", "lei", "decreto", "resolução", "resolucao", "súmula", "sumula", "banco", "central", "caixa",
    "nubank", "itaú", "itau", "bradesco", "santander", "med", "detran", "aneel", "selic", "ipca", "tr", "o", "a",
    "os", "as", "um", "uma", "eu", "meu", "minha", "posso", "como", "qual", "quais", "quando", "onde", "por",
    "que", "se", "é", "tenho", "fiz", "estou", "devo", "pode", "o que", "existe", "há", "sou", "recebi",
}
PALAVRA_MAIUSCULA = re.compile(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\b")
VAZIAS = {
    "a", "o", "e", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "um", "uma", "para", "por", "com",
    "que", "se", "eu", "meu", "minha", "me", "é", "ou", "ao", "à", "como", "qual", "quais", "quando", "posso", "pode",
    "tenho", "sou", "estou", "isso", "esse", "essa", "mais", "muito", "não", "nao", "sim", "já", "ja", "ter", "foi",
    "ser", "está", "esta", "quanto", "onde", "porque", "sobre", "valor", "numero", "data", "telefone", "email", "cpf",
}


def mascarar(pergunta: str) -> str:
    texto = unicodedata.normalize("NFC", pergunta)
    for padrao, troca in MASCARAS:
        texto = padrao.sub(troca, texto)

    def nome(m: re.Match) -> str:
        palavra = m.group(0)
        antes = texto[: m.start()].rstrip()
        inicio_de_frase = not antes or antes[-1] in ".?!:"
        if palavra.lower() in TERMOS_LIVRES:
            return palavra
        # no começo da frase a maiúscula é gramatical, a não ser que venha outro nome em seguida ("Maria Souza")
        seguinte = PALAVRA_MAIUSCULA.match(texto, m.end() + 1)
        if inicio_de_frase and not (seguinte and texto[m.end() : m.end() + 1] == " "):
            return palavra
        return "[nome]"

    return PALAVRA_MAIUSCULA.sub(nome, texto)[:500]


class Registrador:
    def __init__(self, caminho: Path = LACUNAS_PATH):
        self.caminho = caminho
        self._trava = threading.Lock()

    def __call__(self, pergunta: str, motivo: str, melhor_nota: float | None) -> None:
        linha = {
            "em": datetime.now(UTC).strftime("%Y-%m-%d"),  # só o dia: sem horário que identifique a sessão
            "motivo": motivo,
            "melhor_nota": None if melhor_nota is None else round(melhor_nota, 4),
            "pergunta": mascarar(pergunta),
        }
        with self._trava:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with self.caminho.open("a", encoding="utf-8") as f:
                f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def ler_lacunas(caminho: Path = LACUNAS_PATH) -> list[dict]:
    if not caminho.exists():
        return []
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def termos(pergunta: str) -> list[str]:
    palavras = re.findall(r"[a-záéíóúâêôãõç0-9-]{3,}", pergunta.lower())
    return [p for p in palavras if p not in VAZIAS and not p.startswith("[")]


def agrupar(lacunas: list[dict], minimo: int = 2, maximo: int = 15) -> list[tuple[str, int]]:
    """Pares de termos que mais se repetem nas perguntas sem resposta, como consultas de busca."""
    contagem: Counter[str] = Counter()
    for l in lacunas:
        t = sorted(set(termos(l["pergunta"])))
        contagem.update(t)
        contagem.update(f"{a} {b}" for i, a in enumerate(t) for b in t[i + 1 :])
    pares = [(c, n) for c, n in contagem.most_common() if " " in c and n >= minimo]
    soltos = [(c, n) for c, n in contagem.most_common() if " " not in c and n >= minimo]
    return (pares + soltos)[:maximo]
