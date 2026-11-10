"""Caminhos e configuração do serviço, sobrescrevíveis por variável de ambiente."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parents[1]
FONTES_PATH = ROOT / "fontes.yaml"
LOCK_PATH = ROOT / "corpus.lock"
DATA_DIR = Path(os.environ.get("PANDORA_DATA_DIR", ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
TEXT_DIR = DATA_DIR / "text"

LIMIAR_PATH = REPO_ROOT / "training" / "abstencao" / "limiar.json"
LIMIAR_ABSTENCAO = json.loads(LIMIAR_PATH.read_text(encoding="utf-8"))["limiar"] if LIMIAR_PATH.exists() else None

DB_URL = os.environ.get(
    "PANDORA_DB_URL", "postgresql://pandora:pandora_local@localhost:5433/pandora_rag"
)


def carregar_env(caminho: Path = ROOT / ".env") -> None:
    """Lê chaves de .env (fora do git) sem sobrescrever variáveis já definidas."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, _, valor = linha.partition("=")
            os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))


carregar_env()
