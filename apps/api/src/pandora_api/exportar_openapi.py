"""Gera apps/api/openapi.json sem precisar de banco: `uv run python -m pandora_api.exportar_openapi`."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from pandora_api.adaptadores.http.app import criar_app
from pandora_api.adaptadores.http.conteiner import montar
from pandora_api.adaptadores.persistencia.memoria import (
    ConsentimentosEmMemoria,
    SessoesEmMemoria,
    UsuariosEmMemoria,
)
from pandora_api.adaptadores.seguranca.scrypt import HasherScrypt, RelogioDoSistema
from pandora_api.portas.assistente import RespostaElpis

DESTINO = Path(__file__).resolve().parents[2] / "openapi.json"


class _SemAssistente:
    def responder(self, pergunta, contexto=None) -> RespostaElpis:
        raise NotImplementedError


class _SemTrilha:
    def etapas(self):
        return []


def gerar() -> str:
    conteiner = montar(
        UsuariosEmMemoria(),
        SessoesEmMemoria(),
        ConsentimentosEmMemoria(),
        HasherScrypt(),
        RelogioDoSistema(),
        timedelta(hours=1),
        _SemAssistente(),
        _SemTrilha(),
    )
    return json.dumps(criar_app(conteiner).openapi(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    DESTINO.write_text(gerar(), encoding="utf-8")
    print(f"OpenAPI escrito em {DESTINO}")
