from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class Config:
    url_banco: str
    duracao_sessao: timedelta
    origens_cors: tuple[str, ...]

    @classmethod
    def do_ambiente(cls) -> Config:
        url = os.environ.get("PANDORA_DB_URL")
        if not url:
            raise RuntimeError("Defina PANDORA_DB_URL (veja apps/api/.env.example).")
        horas = int(os.environ.get("PANDORA_SESSAO_HORAS", "168"))
        origens = os.environ.get("PANDORA_ORIGENS_CORS", "http://localhost:3000")
        return cls(url, timedelta(hours=horas), tuple(o.strip() for o in origens.split(",") if o.strip()))
