"""Geração fundamentada: prompt com fontes numeradas, citação obrigatória e abstenção."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from pandora_rag.generate.gateway import Gateway
from pandora_rag.retrieve.hybrid import Hit

SEM_RESPOSTA = "NAO_SUSTENTADO"
MENSAGEM_ABSTENCAO = (
    "Não encontrei isso nas fontes oficiais que tenho, então não vou arriscar uma resposta. "
    "Para esse caso, procure o Procon, a Defensoria Pública ou o canal de atendimento do Banco Central."
)

SISTEMA = f"""Você é o PANDORA, assistente de educação financeira para pessoas endividadas no Brasil.
Responda somente com base nas FONTES numeradas fornecidas. Regras:
1. Cada afirmação sobre lei, prazo, valor, percentual ou direito termina com a citação da fonte, no formato [1] ou [2][3].
2. Não use conhecimento externo e não invente artigo, prazo ou número. Se as fontes não sustentam a resposta, responda apenas: {SEM_RESPOSTA}
3. Se uma fonte traz AVISO DE VIGÊNCIA, repita o aviso na resposta.
4. Não recomende compra ou venda de ativos específicos nem preveja retorno.
5. Seja claro e direto, em português, sem jargão desnecessário, em até 180 palavras."""

RE_CITACAO = re.compile(r"\[(\d+)\]")


@dataclass
class Citacao:
    n: int
    norma: str
    artigo: str | None
    link: str
    trecho: str
    pagina: int | None = None
    ressalva: str | None = None


@dataclass
class Resposta:
    texto: str
    abstencao: bool
    citacoes: list[Citacao] = field(default_factory=list)
    hits: list[Hit] = field(default_factory=list)
    modelo: str = ""
    custo_usd: float = 0.0
    latencia_s: float = 0.0
    citacao_valida: bool = False


def montar_prompt(pergunta: str, hits: list[Hit]) -> str:
    blocos = []
    for n, h in enumerate(hits, start=1):
        r = h.registro
        cab = f"[{n}] {r.norma}" + (f", {r.artigo}" if r.artigo else "") + (f" (p. {r.pagina})" if r.pagina else "")
        aviso = f"\nAVISO DE VIGÊNCIA: {r.ressalva}" if r.ressalva else ""
        blocos.append(f"{cab}{aviso}\n{r.texto}")
    return "FONTES:\n\n" + "\n\n".join(blocos) + f"\n\nPERGUNTA: {pergunta}"


def citacoes_validas(texto: str, n_fontes: int) -> list[int]:
    """Números citados que existem nas fontes fornecidas, sem repetir."""
    vistos: list[int] = []
    for m in RE_CITACAO.finditer(texto):
        n = int(m.group(1))
        if 1 <= n <= n_fontes and n not in vistos:
            vistos.append(n)
    return vistos


def montar_citacoes(hits: list[Hit], numeros: list[int]) -> list[Citacao]:
    saida = []
    for n in numeros:
        r = hits[n - 1].registro
        saida.append(Citacao(n, r.norma, r.artigo, r.link, r.texto[:400], r.pagina, r.ressalva))
    return saida


def responder(gateway: Gateway, modelo: str, pergunta: str, hits: list[Hit], max_tokens: int = 700,
              limiar_abstencao: float | None = None) -> Resposta:
    if not hits:
        return Resposta(MENSAGEM_ABSTENCAO, True)
    if limiar_abstencao is not None and hits[0].score_rerank is not None and hits[0].score_rerank < limiar_abstencao:
        return Resposta(MENSAGEM_ABSTENCAO, True, [], hits, "portao", 0.0, 0.0)  # recuperação fraca: o LLM nem é chamado
    c = gateway.gerar(modelo, SISTEMA, montar_prompt(pergunta, hits), max_tokens=max_tokens)
    texto = c.texto.strip()
    numeros = citacoes_validas(texto, len(hits))
    abst = SEM_RESPOSTA in texto
    if abst:
        return Resposta(MENSAGEM_ABSTENCAO, True, [], hits, c.modelo, c.custo_usd, c.latencia_s)
    return Resposta(
        texto, False, montar_citacoes(hits, numeros), hits, c.modelo, c.custo_usd, c.latencia_s, citacao_valida=bool(numeros)
    )
