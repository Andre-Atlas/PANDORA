import json
from pathlib import Path

import pytest

from pandora_api.exportar_openapi import DESTINO, gerar

ROTAS_DO_CONTRATO = {
    ("post", "/extratos"),
    ("get", "/extratos/{extrato_id}"),
    ("get", "/transacoes"),
    ("patch", "/transacoes/{transacao_id}/categoria"),
    ("get", "/raio-x"),
    ("get", "/dividas"),
    ("get", "/score"),
    ("post", "/plano"),
    ("get", "/previsao"),
    ("post", "/chat"),
    ("get", "/trilha"),
    ("get", "/trilha/licoes/{licao_id}"),
    ("post", "/trilha/licoes/{licao_id}/porque"),
    ("post", "/consentimentos"),
    ("delete", "/eu/dados"),
}


def test_openapi_json_esta_atualizado():
    assert Path(DESTINO).exists(), "Rode: uv run python -m pandora_api.exportar_openapi"
    assert Path(DESTINO).read_text(encoding="utf-8") == gerar(), (
        "openapi.json desatualizado. Rode: uv run python -m pandora_api.exportar_openapi "
        "e, no front, npm run api:tipos -w @pandora/web"
    )


def test_contrato_cobre_todas_as_areas_da_issue():
    caminhos = json.loads(gerar())["paths"]
    presentes = {(metodo, caminho) for caminho, ops in caminhos.items() for metodo in ops}
    assert ROTAS_DO_CONTRATO <= presentes, ROTAS_DO_CONTRATO - presentes


def test_operation_ids_unicos_e_legiveis():
    doc = json.loads(gerar())
    ids = [op["operationId"] for ops in doc["paths"].values() for op in ops.values()]
    assert len(ids) == len(set(ids)), ids
    assert "cadastrar" in ids and "perguntar" in ids


def test_rotas_protegidas_pedem_bearer():
    doc = json.loads(gerar())
    publicas = {
        ("get", "/saude"),
        ("post", "/auth/cadastro"),
        ("post", "/auth/sessoes"),
        # Elpis e trilha: sem login por enquanto, nenhum dado pessoal é guardado.
        ("post", "/chat"),
        ("get", "/trilha"),
        ("get", "/trilha/licoes/{licao_id}"),
        ("post", "/trilha/licoes/{licao_id}/porque"),
    }
    for caminho, ops in doc["paths"].items():
        for metodo, op in ops.items():
            if (metodo, caminho) not in publicas:
                assert op.get("security"), f"{metodo.upper()} {caminho} sem segurança"


@pytest.mark.parametrize(
    ("metodo", "caminho", "corpo", "issue"),
    [
        ("get", "/dividas", None, 72),
        ("get", "/score", None, 72),
        ("post", "/plano", {"metodo": "avalanche"}, 71),
        ("get", "/previsao?horizonte=60", None, 84),
    ],
)
def test_rotas_futuras_respondem_501_com_a_issue(autenticado, metodo, caminho, corpo, issue):
    r = autenticado.request(metodo.upper(), caminho, json=corpo)
    assert r.status_code == 501
    assert r.headers["content-type"] == "application/problem+json"
    assert r.json()["issue"] == issue


def test_rotas_futuras_ainda_validam_entrada_e_sessao(cliente, autenticado):
    assert cliente.get("/transacoes", headers={"Authorization": "Bearer x"}).status_code == 401
    assert autenticado.get("/raio-x?mes=outubro").status_code == 422
    assert autenticado.get("/previsao?horizonte=45").status_code == 422
