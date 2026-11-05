"""Caminhos e configuração do serviço, sobrescrevíveis por variável de ambiente."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parents[1]
FONTES_PATH = ROOT / "fontes.yaml"
LOCK_PATH = ROOT / "corpus.lock"
DATA_DIR = Path(os.environ.get("PANDORA_DATA_DIR", ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
TEXT_DIR = DATA_DIR / "text"

DB_URL = os.environ.get(
    "PANDORA_DB_URL", "postgresql://pandora:pandora_local@localhost:5433/pandora_rag"
)
