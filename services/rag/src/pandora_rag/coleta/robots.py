"""Consulta ao robots.txt, com cache por origem."""
from __future__ import annotations

from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx

AGENTE = "PANDORA-RAG"


class RobotsIndisponivel(Exception):
    """robots.txt com erro de servidor ou rede: por prudência, a coleta daquela origem não segue."""


class Robots:
    def __init__(self, cliente: httpx.Client, agente: str = AGENTE) -> None:
        self._cliente = cliente
        self._agente = agente
        self._cache: dict[str, RobotFileParser | None] = {}

    def permitido(self, url: str) -> bool:
        partes = urlsplit(url)
        origem = f"{partes.scheme}://{partes.netloc}"
        if origem not in self._cache:
            self._cache[origem] = self._carregar(origem)
        regras = self._cache[origem]
        return True if regras is None else regras.can_fetch(self._agente, url)

    def _carregar(self, origem: str) -> RobotFileParser | None:
        try:
            resposta = self._cliente.get(f"{origem}/robots.txt")
        except httpx.HTTPError as erro:
            raise RobotsIndisponivel(f"robots.txt de {origem}: {erro}") from erro
        if resposta.status_code >= 500:
            raise RobotsIndisponivel(f"robots.txt de {origem}: HTTP {resposta.status_code}")
        if resposta.status_code >= 400:  # sem robots.txt: tudo permitido (RFC 9309)
            return None
        regras = RobotFileParser()
        regras.parse(resposta.text.splitlines())
        return regras
