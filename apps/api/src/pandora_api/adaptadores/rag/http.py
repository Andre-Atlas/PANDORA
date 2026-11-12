"""Fala com o serviço do RAG (services/rag, `pandora-rag servir`) por HTTP."""

from __future__ import annotations

import httpx

from pandora_api.dominio.citacao import Citacao
from pandora_api.dominio.erros import AssistenteIndisponivel
from pandora_api.portas.assistente import RespostaElpis

# O modelo local leva de 8 a 15 s; o teto cobre uma pergunta lenta sem deixar o front pendurado.
TEMPO_MAXIMO = httpx.Timeout(60.0, connect=3.0)


class AssistenteHttp:
    def __init__(self, url: str, cliente: httpx.Client | None = None, k: int = 3) -> None:
        self._cliente = cliente or httpx.Client(base_url=url, timeout=TEMPO_MAXIMO)
        self._k = k

    def responder(self, pergunta: str, contexto: str | None = None) -> RespostaElpis:
        corpo: dict = {"pergunta": pergunta, "k": self._k}
        if contexto:
            corpo["contexto"] = contexto
        try:
            r = self._cliente.post("/responder", json=corpo)
        except httpx.HTTPError as exc:
            raise AssistenteIndisponivel(f"sem resposta do RAG ({type(exc).__name__})") from exc
        if r.status_code != 200:
            raise AssistenteIndisponivel(f"o RAG respondeu {r.status_code}")
        try:
            d = r.json()
            citacoes = tuple(
                Citacao(c["n"], c["norma"], c.get("artigo"), c["link"], c["trecho"], c.get("pagina"), c.get("ressalva"))
                for c in d["citacoes"]
            )
            return RespostaElpis(d["texto"], bool(d["abstencao"]), d["modelo"], citacoes)
        except (ValueError, KeyError, TypeError) as exc:
            raise AssistenteIndisponivel("resposta inesperada do RAG") from exc
