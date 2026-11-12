from __future__ import annotations

from dataclasses import dataclass

from pandora_api.dominio.citacao import Citacao


@dataclass(frozen=True)
class Pergunta:
    enunciado: str
    opcoes: tuple[str, ...]
    certa: int
    feedback: str
    citacoes: tuple[int, ...]


@dataclass(frozen=True)
class Licao:
    id: str
    titulo: str
    explicacao: str
    citacoes_explicacao: tuple[int, ...]
    fontes: tuple[Citacao, ...]
    perguntas: tuple[Pergunta, ...]


@dataclass(frozen=True)
class Etapa:
    """Um degrau do caminho. A posição (x, lado) e o emblema vêm do desenho da trilha."""

    id: str
    n: int
    t: str
    x: int
    lado: str
    marco: str | None
    emblema: str
    licao: Licao
