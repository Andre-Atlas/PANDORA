"""Caminhos e configuração do serviço, sobrescrevíveis por variável de ambiente."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parents[1]
FONTES_PATH = ROOT / "fontes.yaml"
LOCK_PATH = ROOT / "corpus.lock"
CATALOGO_LOCK_PATH = ROOT / "catalogo.lock.json"
_RE_ENV_CHAVE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _resolver_data_dir() -> Path:
    """Resolve data/ localmente ou a partir do repositório principal em git worktrees."""
    if env := os.environ.get("PANDORA_DATA_DIR"):
        return Path(env)
    local = ROOT / "data"
    if (local / "text").exists():
        return local
    git_bin = shutil.which("git")
    if git_bin:
        try:
            comum = subprocess.run(
                [git_bin, "rev-parse", "--git-common-dir"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            ).stdout.strip()
            if comum:
                p = Path(comum)
                resolved = p.resolve() if p.is_absolute() else (REPO_ROOT / p).resolve()
                cand = resolved.parent / "services" / "rag" / "data"
                if (cand / "text").exists():
                    return cand
        except (OSError, subprocess.SubprocessError):
            pass
    return local


DATA_DIR = _resolver_data_dir()
RAW_DIR = DATA_DIR / "raw"
TEXT_DIR = DATA_DIR / "text"

LIMIAR_PATH = REPO_ROOT / "training" / "abstencao" / "limiar.json"
LIMIAR_ABSTENCAO = json.loads(LIMIAR_PATH.read_text(encoding="utf-8"))["limiar"] if LIMIAR_PATH.exists() else None

DB_URL_PADRAO = "postgresql://pandora:pandora_local@localhost:5433/pandora_rag"


def resolver_db_url(env: dict | None = None) -> str:
    """PANDORA_RAG_DB_URL é o nome atual; PANDORA_DB_URL (da API, porta 5434) só vale como alternativa antiga."""
    env = os.environ if env is None else env
    if env.get("PANDORA_RAG_DB_URL"):
        return env["PANDORA_RAG_DB_URL"]
    if env.get("PANDORA_DB_URL"):
        warnings.warn("PANDORA_DB_URL no RAG está obsoleta; use PANDORA_RAG_DB_URL", DeprecationWarning, stacklevel=2)
        return env["PANDORA_DB_URL"]
    return DB_URL_PADRAO


DB_URL = resolver_db_url()
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


def carregar_env(caminho: Path = ROOT / ".env") -> None:
    """Lê chaves de .env (fora do git) sem sobrescrever variáveis já definidas."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, _, valor = linha.partition("=")
            chave_limpa = chave.strip()
            if _RE_ENV_CHAVE.fullmatch(chave_limpa):
                os.environ.setdefault(chave_limpa, valor.strip().strip("\"'"))


carregar_env()
