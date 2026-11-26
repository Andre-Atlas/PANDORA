from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pandora_api.dominio.citacao import Citacao


@dataclass(frozen=True)
class RespostaElpis:
    texto: str
    abstencao: bool
    modelo: str
    citacoes: tuple[Citacao, ...] = field(default_factory=tuple)
    crise: bool = False


class AssistenteElpis(Protocol):
    """Quem responde com fontes. A implementação real chama o serviço do RAG."""

    def responder(self, pergunta: str, contexto: str | None = None) -> RespostaElpis: ...
