"""#72: do envio do extrato ao Raio-X, com dados fictícios, e testes de contrato."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pandora_api.adaptadores.http.esquemas import ExtratoSaida, PaginaTransacoes, RaioX, TransacaoSaida
from pandora_api.dominio.extrato import TAMANHO_MAXIMO_BYTES
from pandora_api.exportar_openapi import gerar

AMOSTRA = Path(__file__).resolve().parents[3] / "docs/evidencias/datasets/amostra_transacoes_sinteticas_personas.csv"


def _carla() -> bytes:
    """As 6 linhas da Carla na amostra sintética do repositório (outubro de 2026)."""
    linhas = AMOSTRA.read_text(encoding="utf-8").splitlines()
    return "\n".join([linhas[0], *[x for x in linhas[1:] if x.split(",")[1] == "carla_34"]]).encode()


@pytest.fixture
def com_consentimento(autenticado):
    autenticado.post("/consentimentos", json={"finalidade": "diagnostico_financeiro", "versao_termo": "2026-11"})
    return autenticado


def _enviar(cliente, conteudo: bytes, nome: str = "extrato.csv"):
    return cliente.post("/extratos", files={"arquivo": (nome, conteudo, "text/csv")})


def test_fluxo_do_upload_ao_raio_x(com_consentimento):
    r = _enviar(com_consentimento, _carla())
    assert r.status_code == 202
    extrato = ExtratoSaida.model_validate(r.json())
    assert extrato.status == "concluido" and extrato.transacoes_importadas == 6 and extrato.avisos == []

    situacao = com_consentimento.get(f"/extratos/{extrato.id}")
    assert situacao.status_code == 200 and situacao.json() == r.json()

    raio_x = RaioX.model_validate(com_consentimento.get("/raio-x?mes=2026-10").json())
    assert raio_x.renda_centavos == 285000
    assert raio_x.minimo_existencial_centavos == 95000 + 62050  # aluguel + mercado
    assert raio_x.folga_centavos == 285000 - 157050
    gastos = {g.categoria: (g.total_centavos, g.essencial_centavos) for g in raio_x.gastos}
    assert gastos == {
        "DIVIDA_JUROS": (89000 + 34218 + 48000, 0),
        "MORADIA": (95000, 95000),
        "ALIMENTACAO": (62050, 62050),
    }
    assert [g.categoria for g in raio_x.gastos][0] == "DIVIDA_JUROS", "da maior para a menor"
    assert raio_x.calculo.fonte == "motor_deterministico"
    assert {"Renda do mês": "R$ 2.850,00"}.items() <= {e.nome: e.valor for e in raio_x.calculo.entradas}.items()


def test_mesmo_extrato_duas_vezes_nao_duplica(com_consentimento):
    _enviar(com_consentimento, _carla())
    segundo = _enviar(com_consentimento, _carla()).json()
    assert segundo["transacoes_importadas"] == 0
    assert "6 transação(ões) já estavam importadas" in segundo["avisos"][0]
    assert com_consentimento.get("/transacoes").json()["total"] == 6


def test_linhas_iguais_no_mesmo_arquivo_sao_duas_transacoes(com_consentimento):
    csv = b"data;valor;descricao\n05/10/2026;-8,50;PADARIA\n05/10/2026;-8,50;PADARIA\n"
    assert _enviar(com_consentimento, csv).json()["transacoes_importadas"] == 2


def test_listar_filtra_pagina_e_ordena(com_consentimento):
    _enviar(com_consentimento, _carla())
    pagina = PaginaTransacoes.model_validate(com_consentimento.get("/transacoes?por_pagina=4&pagina=2").json())
    assert (pagina.total, pagina.pagina, pagina.por_pagina, len(pagina.itens)) == (6, 2, 4, 2)

    todas = com_consentimento.get("/transacoes").json()["itens"]
    datas = [t["data_hora"] for t in todas]
    assert datas == sorted(datas, reverse=True)
    assert todas[-1]["data_hora"] == "2026-10-05T08:15:00-03:00"

    dividas = com_consentimento.get("/transacoes?categoria=DIVIDA_JUROS").json()
    assert dividas["total"] == 3 and {t["categoria"] for t in dividas["itens"]} == {"DIVIDA_JUROS"}
    assert com_consentimento.get("/transacoes?mes=2026-09").json() == {
        "itens": [],
        "total": 0,
        "pagina": 1,
        "por_pagina": 50,
    }


def test_corrigir_categoria_com_um_toque(com_consentimento):
    _enviar(com_consentimento, _carla())
    mercado = com_consentimento.get("/transacoes?categoria=ALIMENTACAO").json()["itens"][0]
    assert mercado["origem_categoria"] == "modelo" and mercado["essencial"] is True

    r = com_consentimento.patch(f"/transacoes/{mercado['id']}/categoria", json={"categoria": "LAZER"})
    assert r.status_code == 200
    corrigida = TransacaoSaida.model_validate(r.json())
    assert corrigida.categoria == "LAZER" and corrigida.origem_categoria == "pessoa"
    assert corrigida.essencial is False and corrigida.confianca_categoria is None

    raio_x = com_consentimento.get("/raio-x?mes=2026-10").json()
    assert raio_x["minimo_existencial_centavos"] == 95000, "o mercado saiu do Mínimo Existencial"


def test_ninguem_ve_nem_corrige_o_dado_de_outra_pessoa(com_consentimento, cliente):
    extrato_id = _enviar(com_consentimento, _carla()).json()["id"]
    transacao_id = com_consentimento.get("/transacoes").json()["itens"][0]["id"]

    cliente.post("/auth/cadastro", json={"email": "diego@exemplo.com", "senha": "senha-forte-2"})
    token = cliente.post("/auth/sessoes", json={"email": "diego@exemplo.com", "senha": "senha-forte-2"}).json()["token"]
    diego = {"Authorization": f"Bearer {token}"}
    assert cliente.get(f"/extratos/{extrato_id}", headers=diego).status_code == 404
    r = cliente.patch(f"/transacoes/{transacao_id}/categoria", json={"categoria": "LAZER"}, headers=diego)
    assert r.status_code == 404 and r.json()["type"] == "urn:pandora:erro:transacao-nao-encontrada"
    assert cliente.get("/transacoes", headers=diego).json()["total"] == 0
    assert cliente.get("/raio-x?mes=2026-10", headers=diego).json()["renda_centavos"] == 0


def test_raio_x_sem_transacoes_vem_zerado(autenticado):
    raio_x = autenticado.get("/raio-x?mes=2026-10").json()
    assert (raio_x["renda_centavos"], raio_x["minimo_existencial_centavos"], raio_x["gastos"]) == (0, 0, [])


@pytest.mark.parametrize(
    ("nome", "conteudo", "trecho"),
    [
        ("extrato.ofx", b"OFXHEADER:100", "#57"),
        ("fatura.pdf", b"%PDF-1.7", "#66"),
        ("planilha.xlsx", b"PK", "CSV, OFX ou PDF"),
        ("extrato.csv", b"coluna_a,coluna_b\n1,2\n", "data, valor, descricao"),
        ("extrato.csv", b"data,valor,descricao\nontem,abc,LOJA\n", "Nenhuma transação"),
    ],
)
def test_arquivo_que_nao_da_para_ler_falha_com_o_motivo(com_consentimento, nome, conteudo, trecho):
    r = _enviar(com_consentimento, conteudo, nome)
    assert r.status_code == 202
    assert r.json()["status"] == "falhou" and r.json()["transacoes_importadas"] == 0
    assert trecho in r.json()["avisos"][0]
    assert com_consentimento.get(f"/extratos/{r.json()['id']}").json()["status"] == "falhou"


def test_linha_ruim_vira_aviso_e_as_outras_entram(com_consentimento):
    csv = b"data,valor,descricao\n2026-10-01,-10.00,LOJA\n2026-13-40,-5.00,LOJA\n2026-10-02,-1.234,LOJA\n"
    r = _enviar(com_consentimento, csv).json()
    assert r["status"] == "concluido" and r["transacoes_importadas"] == 1
    assert r["avisos"][0].startswith("Linha 3: data inválida") and r["avisos"][1].startswith("Linha 4: valor com")


def test_arquivo_grande_demais(com_consentimento):
    r = _enviar(com_consentimento, b"x" * (TAMANHO_MAXIMO_BYTES + 1))
    assert r.status_code == 413
    assert r.json()["type"] == "urn:pandora:erro:arquivo-grande-demais" and "5 MB" in r.json()["detail"]


def test_exclusao_total_apaga_extratos_e_transacoes(com_consentimento, repos):
    _enviar(com_consentimento, _carla())
    assert com_consentimento.delete("/eu/dados").status_code == 204
    for repo in repos:
        assert repo.dados == {}, type(repo).__name__


def test_rotas_validam_entrada_e_sessao(autenticado):
    invalido = {"Authorization": "Bearer inventado"}
    assert autenticado.get("/raio-x?mes=2026-10", headers=invalido).status_code == 401
    arquivo = {"arquivo": ("a.csv", b"", "text/csv")}
    assert autenticado.post("/extratos", files=arquivo, headers=invalido).status_code == 401
    assert autenticado.get("/raio-x?mes=2026-13").status_code == 422
    assert autenticado.get("/raio-x").status_code == 422
    assert autenticado.get("/transacoes?categoria=NADA").status_code == 422
    assert autenticado.get("/transacoes?por_pagina=201").status_code == 422
    r = autenticado.patch("/transacoes/00000000-0000-0000-0000-000000000001/categoria", json={"categoria": "LAZER"})
    assert r.status_code == 404


def test_contrato_documenta_os_erros_do_raio_x():
    caminhos = json.loads(gerar())["paths"]
    assert {"401", "403", "413"} <= set(caminhos["/extratos"]["post"]["responses"])
    assert "404" in caminhos["/extratos/{extrato_id}"]["get"]["responses"]
    assert "404" in caminhos["/transacoes/{transacao_id}/categoria"]["patch"]["responses"]
    assert "501" not in caminhos["/raio-x"]["get"]["responses"], "o Raio-X já está implementado"
