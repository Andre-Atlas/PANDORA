"""Critério de aceite da #62: o domínio não importa FastAPI nem banco."""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "src" / "pandora_api"
CAMADAS_PURAS = ["dominio", "portas", "aplicacao"]
PROIBIDOS = (
    "fastapi",
    "starlette",
    "pydantic",
    "uvicorn",
    "psycopg",
    "psycopg_pool",
    "sqlalchemy",
    "pandora_api.adaptadores",
)


def _importacoes(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.Import):
            nomes.update(a.name for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


@pytest.mark.parametrize("camada", CAMADAS_PURAS)
def test_camadas_puras_nao_conhecem_framework_nem_banco(camada):
    arquivos = list((RAIZ / camada).rglob("*.py"))
    assert arquivos, camada
    for arquivo in arquivos:
        for nome in _importacoes(arquivo):
            assert not nome.startswith(PROIBIDOS), f"{arquivo.relative_to(RAIZ)} importa {nome}"


def test_dominio_nao_depende_das_outras_camadas():
    for arquivo in (RAIZ / "dominio").rglob("*.py"):
        for nome in _importacoes(arquivo):
            assert not nome.startswith(("pandora_api.portas", "pandora_api.aplicacao")), arquivo.name
