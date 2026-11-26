"""Geração e validação do conteúdo da trilha: explicação com fontes e perguntas de múltipla escolha.

O conteúdo é gerado uma vez, validado por regras objetivas e salvo em JSON versionado. A API só lê o arquivo.
A revisão humana fica para o segundo refino; por isso o arquivo declara `validacao: automatica`.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from pandora_rag.generate.answer import RE_CITACAO, citacoes_validas, montar_prompt, responder
from pandora_rag.retrieve.hybrid import Hit

N_PERGUNTAS = 2
N_OPCOES = 3

# Geometria e emblemas vêm do TrilhaCaminho do design system; o estado (feito/atual/próximo) é do usuário.
ROTEIRO = [
    {"id": "minimo-existencial", "n": 1, "t": "Mínimo existencial", "x": 70, "lado": "d", "marco": None, "emblema": "templo",
     "busca": "mínimo existencial superendividamento Lei 14.181 renda preservada repactuação",
     "guia": "O que é o mínimo existencial e como ele protege quem está superendividado?"},
    {"id": "juros-e-cet", "n": 2, "t": "Juros e CET", "x": 200, "lado": "e", "marco": None, "emblema": "balanca",
     "busca": "custo efetivo total CET taxa de juros contrato de crédito informação ao consumidor",
     "guia": "O que é o Custo Efetivo Total (CET) e por que comparar o CET e não só a taxa de juros?"},
    {"id": "rotativo", "n": 3, "t": "Rotativo", "x": 288, "lado": "e", "marco": None, "emblema": "espiral",
     "busca": "juros do cartão de crédito rotativo limite dos juros e encargos Lei 14.690",
     "guia": "Como funcionam os juros do cartão de crédito rotativo e existe limite para eles?"},
    {"id": "repactuacao", "n": 4, "t": "Repactuação", "x": 200, "lado": "e", "marco": "Marco: conheço meus direitos", "emblema": "oliveira",
     "busca": "repactuação de dívidas conciliação audiência plano de pagamento prazo superendividamento",
     "guia": "Como funciona a repactuação de dívidas pela Lei do Superendividamento?"},
    {"id": "golpes-e-med", "n": 5, "t": "Golpes e MED", "x": 78, "lado": "d", "marco": "Marco: sei me proteger", "emblema": "elmo",
     "busca": "golpe Pix Mecanismo Especial de Devolução MED contestação fraude devolução",
     "guia": "O que é o MED do Pix e o que fazer ao cair em um golpe?"},
    {"id": "reserva-de-emergencia", "n": 6, "t": "Reserva de emergência", "x": 200, "lado": "e", "marco": "Marco: tenho um plano", "emblema": "anfora",
     "busca": "reserva de emergência planejamento financeiro orçamento educação financeira poupança",
     "guia": "O que é uma reserva de emergência e por onde começar a formá-la?"},
]

SISTEMA_QUESTOES = f"""Você cria perguntas de múltipla escolha para uma trilha de educação financeira, para pessoas endividadas no Brasil.
Use somente as FONTES numeradas. Regras:
1. Crie {N_PERGUNTAS} perguntas diferentes, cada uma com exatamente {N_OPCOES} opções curtas (até 18 palavras) e uma só correta.
2. As opções erradas devem ser plausíveis, mas claramente incompatíveis com as fontes.
3. O enunciado, a opção correta e o feedback só usam números, prazos e artigos que estão nas fontes. As opções erradas podem trazer outros valores plausíveis.
4. O campo "feedback" explica a resposta certa em até 55 palavras e termina com a citação da fonte, no formato [1] ou [2].
5. Não recomende compra ou venda de ativos nem preveja retorno.
Responda apenas com JSON neste formato:
{{"perguntas": [{{"enunciado": "...", "opcoes": ["...", "...", "..."], "certa": 0, "feedback": "... [1]"}}]}}
"certa" é o índice (0 a {N_OPCOES - 1}) da opção correta."""

RE_NUMERO = re.compile(r"\d+(?:[.,]\d+)*")


@dataclass
class ResultadoPerguntas:
    perguntas: list[dict] = field(default_factory=list)
    descartadas: list[dict] = field(default_factory=list)  # {"pergunta": ..., "erros": [...]}


def extrair_json(texto: str) -> dict:
    """Aceita JSON puro ou dentro de uma cerca ```json."""
    t = texto.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.IGNORECASE)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        ini, fim = t.find("{"), t.rfind("}")
        if ini >= 0 and fim > ini:
            return json.loads(t[ini : fim + 1])
        raise


def limpar_marcadores(texto: str, n_fontes: int) -> str:
    """Tira os `[n]` que não apontam para nenhuma fonte da lição (o modelo às vezes inventa `[8]`)."""
    sem = RE_CITACAO.sub(lambda m: m.group(0) if 1 <= int(m.group(1)) <= n_fontes else "", texto)
    return re.sub(r" +([.,;])", r"\1", re.sub(r"[ \t]{2,}", " ", sem)).strip()


def _normalizar_numero(s: str) -> str:
    """`1.000,00` e `1000` são o mesmo número; separadores de milhar e decimal zero saem."""
    return re.sub(r"[.,]", "", re.sub(r"[.,]0+$", "", s))


def numeros_relevantes(texto: str) -> list[str]:
    """Números que um leitor tomaria por fato: com 2 ou mais dígitos, ou com decimal."""
    saida = []
    for m in RE_NUMERO.finditer(RE_CITACAO.sub("", texto)):
        bruto = m.group(0)
        if len(_normalizar_numero(bruto)) >= 2 or "," in bruto or "." in bruto:
            saida.append(_normalizar_numero(bruto))
    return saida


def validar_pergunta(p: dict, hits: list[Hit]) -> list[str]:
    """Lista de erros; vazia quando a pergunta passa em todas as regras."""
    erros: list[str] = []
    enun, ops, certa, fb = p.get("enunciado"), p.get("opcoes"), p.get("certa"), p.get("feedback")
    if not isinstance(enun, str) or len(enun.strip()) < 15:
        erros.append("enunciado ausente ou curto")
    if not isinstance(ops, list) or len(ops) != N_OPCOES or not all(isinstance(o, str) and o.strip() for o in ops):
        erros.append(f"precisa de exatamente {N_OPCOES} opções de texto")
    elif len({o.strip().lower() for o in ops}) != N_OPCOES:
        erros.append("opções repetidas")
    if not isinstance(certa, int) or isinstance(certa, bool) or not (0 <= certa < N_OPCOES):
        erros.append("índice da opção certa inválido")
    if not isinstance(fb, str) or not fb.strip():
        erros.append("feedback ausente")
        return erros
    citados = citacoes_validas(fb, len(hits))
    if not citados:
        erros.append("feedback sem citação válida")
        return erros
    # o rótulo da fonte ("[1] Lei 14.690/2023, Art. 28") também é visto pelo modelo: vale como fonte do número
    visivel = " ".join(
        f"{r.norma} {r.artigo or ''} {r.texto}" for r in (hits[n - 1].registro for n in citados)
    )
    if any(hits[n - 1].registro.ressalva for n in citados):
        # norma com aviso de vigência (superada ou restrita) não serve de gabarito de prova
        erros.append("cita fonte com aviso de vigência")
        return erros
    base = {_normalizar_numero(m.group(0)) for m in RE_NUMERO.finditer(visivel)}
    certa_ok = isinstance(ops, list) and isinstance(certa, int) and not isinstance(certa, bool) and 0 <= certa < len(ops)
    # opções erradas podem trazer valores que não estão nas fontes: só enunciado, opção certa e feedback são conferidos
    partes = [enun if isinstance(enun, str) else "", ops[certa] if certa_ok and isinstance(ops[certa], str) else "", fb]
    for num in numeros_relevantes(" ".join(partes)):
        if num not in base:
            erros.append(f"número {num} não aparece nas fontes citadas")
    return erros


def embaralhar_opcoes(p: dict, semente: str) -> dict:
    """Modelos tendem a pôr a certa sempre na mesma posição; sorteia de forma determinística."""
    ordem = list(range(N_OPCOES))
    random.Random(hashlib.sha256(semente.encode()).hexdigest()).shuffle(ordem)
    return {**p, "opcoes": [p["opcoes"][i] for i in ordem], "certa": ordem.index(p["certa"])}


def _fontes(hits: list[Hit]) -> list[dict]:
    saida = []
    for n, h in enumerate(hits, start=1):
        r = h.registro
        saida.append({"n": n, "norma": r.norma, "artigo": r.artigo, "link": r.link, "trecho": " ".join(r.texto.split())[:400],
                      "pagina": r.pagina, "ressalva": r.ressalva})
    return saida


def gerar_perguntas(gateway, modelo: str, hits: list[Hit], etapa_id: str, tentativas: int = 3) -> ResultadoPerguntas:
    res = ResultadoPerguntas()
    pedido = montar_prompt(f"Crie {N_PERGUNTAS} perguntas de múltipla escolha sobre o tema, com base nas fontes.", hits)
    for tentativa in range(tentativas):
        if len(res.perguntas) >= N_PERGUNTAS:
            break
        c = gateway.gerar(modelo, SISTEMA_QUESTOES, pedido, max_tokens=900, json_modo=True)
        try:
            bruto = extrair_json(c.texto).get("perguntas", [])
        except (json.JSONDecodeError, AttributeError):
            res.descartadas.append({"pergunta": None, "erros": ["resposta não é JSON"]})
            continue
        for p in bruto if isinstance(bruto, list) else []:
            if not isinstance(p, dict) or len(res.perguntas) >= N_PERGUNTAS:
                continue
            if any(p.get("enunciado") == q["enunciado"] for q in res.perguntas):
                continue
            erros = validar_pergunta(p, hits)
            if erros:
                res.descartadas.append({"pergunta": p.get("enunciado"), "erros": erros})
                continue
            p = embaralhar_opcoes(p, f"{etapa_id}:{len(res.perguntas)}")
            p["citacoes"] = citacoes_validas(p["feedback"], len(hits))
            res.perguntas.append({k: p[k] for k in ("enunciado", "opcoes", "certa", "feedback", "citacoes")})
    return res


def gerar_etapa(retriever, gateway, modelo: str, etapa: dict, limiar: float | None, k: int = 4, tentativas: int = 3) -> dict:
    hits = retriever.buscar(etapa["busca"], k)
    resp = responder(gateway, modelo, etapa["guia"], hits, max_tokens=500, limiar_abstencao=limiar)
    perguntas = gerar_perguntas(gateway, modelo, hits, etapa["id"], tentativas) if not resp.abstencao else ResultadoPerguntas()
    problemas = []
    if resp.abstencao:
        problemas.append("explicação: o RAG se absteve")
    elif not resp.citacao_valida:
        problemas.append("explicação sem citação válida")
    if len(perguntas.perguntas) < 1:
        problemas.append("nenhuma pergunta válida")
    return {
        "id": etapa["id"], "n": etapa["n"], "t": etapa["t"], "x": etapa["x"], "lado": etapa["lado"],
        "marco": etapa["marco"], "emblema": etapa["emblema"],
        "licao": {
            "id": etapa["id"], "titulo": etapa["t"], "pergunta_guia": etapa["guia"],
            "explicacao": "" if resp.abstencao else limpar_marcadores(resp.texto, len(hits)),
            "fontes": _fontes(hits),
            "citacoes_explicacao": [c.n for c in resp.citacoes],
            "perguntas": perguntas.perguntas,
        },
        "_controle": {"problemas": problemas, "perguntas_descartadas": perguntas.descartadas},
    }


def montar_documento(etapas: list[dict], versao_corpus: str, modelo_llm: str) -> dict:
    corpo = [{k: v for k, v in e.items() if k != "_controle"} for e in etapas]
    hash_corpo = hashlib.sha256(json.dumps(corpo, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return {
        "versao": "1",
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "corpus": versao_corpus,
        "modelo": modelo_llm,
        "validacao": "automatica",
        "hash": hash_corpo,
        "etapas": corpo,
    }
