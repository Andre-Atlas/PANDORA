"""Métricas de resposta: citação verificável e abstenção."""
from __future__ import annotations

import re
from dataclasses import dataclass

RE_CITACAO = re.compile(r"\[(\d+)\]")
RE_LINK = re.compile(r"^https?://\S+$")


@dataclass
class CitacaoResposta:
    norma: str
    link: str
    artigo: str | None = None


def citacao_valida(texto: str, citacoes: list[CitacaoResposta], exige_artigo: bool = True) -> bool:
    """Resposta normativa válida: marcador [n] no texto e, para cada fonte citada, norma e link válidos
    (e artigo, quando a fonte é uma norma com artigos)."""
    if not RE_CITACAO.search(texto) or not citacoes:
        return False
    for c in citacoes:
        if not c.norma or not RE_LINK.match(c.link):
            return False
        if exige_artigo and c.artigo is None:
            return False
    return True


def taxa(valores: list[bool]) -> float:
    return sum(valores) / len(valores) if valores else float("nan")


def abstencao(deve_abster: list[bool], abstevou: list[bool]) -> dict[str, float]:
    """Abstenção correta (recall sobre as que exigem abstenção), recusa indevida e precisão da abstenção."""
    assert len(deve_abster) == len(abstevou)
    fora = [a for d, a in zip(deve_abster, abstevou) if d]
    dentro = [a for d, a in zip(deve_abster, abstevou) if not d]
    abstidas = [d for d, a in zip(deve_abster, abstevou) if a]
    return {
        "abstencao_correta": taxa(fora),
        "recusa_indevida": taxa(dentro),
        "precisao_abstencao": taxa(abstidas),
    }
