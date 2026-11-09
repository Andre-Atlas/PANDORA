"""Gera rascunhos de perguntas do golden set a partir dos chunks do corpus.

O modelo escreve pergunta, resposta de referência e o trecho-ouro; o script rejeita o que não
passa nas checagens automáticas. Nada vira referência sem a revisão humana (status_revisao).
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from evals.metrics.recuperacao import trigramas
from evals.metrics.textos import normalizar, numeros, palavras

PERSONAS = Path(__file__).resolve().parents[2] / "docs" / "personas"

SISTEMA_NORMATIVA = """Você ajuda a montar o conjunto de avaliação de um assistente de educação financeira.
Receba um TRECHO de norma, súmula ou cartilha e devolva um JSON com exatamente estas chaves:
"pergunta": uma pergunta natural em português, como uma pessoa comum faria, que o TRECHO responde por inteiro. Não cite número de artigo, não copie frases do trecho.
"resposta": resposta de referência com no máximo 60 palavras, usando só informação do TRECHO.
"trecho_ouro": cópia LITERAL de uma ou duas frases do TRECHO que sustentam a resposta, sem mudar nenhuma palavra.
Devolva só o JSON."""

SISTEMA_PERSONA = """Você ajuda a montar o conjunto de avaliação de um assistente de educação financeira.
Receba o PERFIL de uma pessoa e um TRECHO de norma ou cartilha. Escreva, em primeira pessoa e no tom dessa pessoa, uma dúvida que o TRECHO responde por inteiro. Devolva um JSON com exatamente estas chaves:
"pergunta": a dúvida em primeira pessoa, natural, sem citar número de artigo nem copiar frases do trecho.
"resposta": resposta de referência com no máximo 60 palavras, usando só informação do TRECHO.
"trecho_ouro": cópia LITERAL de uma ou duas frases do TRECHO que sustentam a resposta, sem mudar nenhuma palavra.
Devolva só o JSON."""


def perfil_persona(arquivo: Path) -> dict:
    t = arquivo.read_text(encoding="utf-8")
    titulo = re.search(r"^# Persona (\d+) · (.+?) \((\d+) anos\)", t, re.M)
    arq = re.search(r"\*\*Arquétipo:\*\* (.+)", t)
    frase = re.search(r'> \*"(.+?)"\*', t)
    return {
        "id": f"persona{int(titulo.group(1)):02d}", "nome": titulo.group(2), "idade": titulo.group(3),
        "arquetipo": arq.group(1).strip() if arq else "", "frase": frase.group(1) if frase else "",
    }


def carregar_personas() -> list[dict]:
    return [perfil_persona(p) for p in sorted(PERSONAS.glob("[0-9][0-9]-*.md"))]


def verificar_item(item: dict, chunk_texto: str) -> list[str]:
    """Falhas automáticas; lista vazia = passou."""
    falhas = []
    p, r, o = item.get("pergunta", ""), item.get("resposta", ""), item.get("trecho_ouro", "")
    if not (15 <= len(p) <= 320) or "?" not in p:
        falhas.append("pergunta_mal_formada")
    if not o or normalizar(o).strip(" .") not in normalizar(chunk_texto):
        falhas.append("trecho_nao_literal")
    if len(r.split()) > 90 or len(r.split()) < 4:
        falhas.append("resposta_tamanho")
    if numeros(r) - numeros(chunk_texto):
        falhas.append("numero_inventado")
    elif numeros(r) - numeros(o):
        falhas.append("numero_fora_do_trecho_ouro")
    if len(palavras(p)) < 7:
        falhas.append("pergunta_vaga")
    tp = trigramas(p)
    if tp and len(tp & trigramas(chunk_texto)) / len(tp) > 0.5:
        falhas.append("pergunta_copiada_do_trecho")
    return falhas


def extrair_json(texto: str) -> dict | None:
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def elegiveis(registros, minimo: int = 30, maximo: int = 260):
    return [
        r for r in registros
        if minimo <= len(r.texto.split()) <= maximo and "preambulo" not in r.id and "Rua Sete" not in r.texto
        and not r.id.endswith("-p2")
        and not re.search(r"entra(m)? em vigor|revoga[mdo]|vig[êe]ncia", r.texto[:260], re.I)
    ]


def amostrar(registros, cotas: dict[str, int], semente: int, excluir: set[str] = frozenset()):
    """cotas: {rótulo: n}; cada rótulo é resolvido por `filtros` abaixo. Sorteio reprodutível."""
    rng = random.Random(semente)
    escolhidos, usados = [], set(excluir)
    for rotulo, n in cotas.items():
        pool = [r for r in registros if FILTROS[rotulo](r) and r.id not in usados]
        rng.shuffle(pool)
        pegos = pool[:n]
        usados.update(r.id for r in pegos)
        escolhidos += [(rotulo, r) for r in pegos]
    return escolhidos


def _art_cdc(r) -> bool:
    """Artigos do CDC sobre crédito e superendividamento (54-A a 54-G e 104-A a 104-C)."""
    return bool(re.search(r"\b(54|104)-[A-G]\b", r.artigo or ""))


FILTROS = {
    "superendividamento": lambda r: r.fonte_id in ("lei-14181", "cdc", "decreto-11150", "decreto-11567", "mpf-adpf-1005", "stf-adpf-1005") and (r.fonte_id != "cdc" or _art_cdc(r)),
    "cartao_juros": lambda r: r.fonte_id in ("lei-14690", "cmn-5112", "cmn-4881", "cmn-4882", "cmn-4558", "cmn-5057"),
    "apostas": lambda r: r.fonte_id in ("lei-14790", "bcb-ee119"),
    "pix_med": lambda r: r.fonte_id == "bcb-147",
    "impenhorabilidade": lambda r: r.fonte_id in ("lei-8009", "cpc", "dl-911", "lei-9514", "lei-14015"),
    "cvm": lambda r: r.fonte_id in ("cvm-19", "cvm-20", "cvm-30"),
    "sumulas_cdc": lambda r: r.fonte_id == "stj-sumulas" or (r.fonte_id == "cdc" and not _art_cdc(r)),
    "cartilhas": lambda r: r.tipo in ("cartilha", "estudo"),
}

# Perguntas normativas (100 no golden, 40 no dev) e de personas (50 e 15), conforme escopo/06
COTAS_GOLDEN = {"superendividamento": 22, "cartao_juros": 14, "apostas": 8, "pix_med": 10, "impenhorabilidade": 12, "cvm": 12, "sumulas_cdc": 12, "cartilhas": 10}
COTAS_DEV = {"superendividamento": 9, "cartao_juros": 6, "apostas": 3, "pix_med": 4, "impenhorabilidade": 5, "cvm": 5, "sumulas_cdc": 5, "cartilhas": 3}
