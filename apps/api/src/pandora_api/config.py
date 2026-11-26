from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path


@dataclass(frozen=True)
class Config:
    url_banco: str
    duracao_sessao: timedelta
    origens_cors: tuple[str, ...]
    url_rag: str
    caminho_trilha: Path | None

    @classmethod
    def do_ambiente(cls) -> Config:
        url = os.environ.get("PANDORA_DB_URL")
        if not url:
            raise RuntimeError("Defina PANDORA_DB_URL (veja apps/api/.env.example).")
        horas = int(os.environ.get("PANDORA_SESSAO_HORAS", "168"))
        origens = os.environ.get("PANDORA_ORIGENS_CORS", "http://localhost:3000")
        trilha = os.environ.get("PANDORA_TRILHA_JSON")
        return cls(
            url,
            timedelta(hours=horas),
            tuple(o.strip() for o in origens.split(",") if o.strip()),
            os.environ.get("PANDORA_RAG_URL", "http://localhost:8010"),
            Path(trilha) if trilha else None,
        )
