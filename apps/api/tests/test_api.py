PROBLEMA = "application/problem+json"


def test_saude(cliente):
    r = cliente.get("/saude")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_cadastro_entrar_eu_sair(cliente):
    r = cliente.post("/auth/cadastro", json={"email": "Carla@Exemplo.com", "senha": "senha-forte-1"})
    assert r.status_code == 201
    assert r.json()["email"] == "carla@exemplo.com"
    assert "senha" not in r.text

    token = cliente.post("/auth/sessoes", json={"email": "carla@exemplo.com", "senha": "senha-forte-1"}).json()["token"]
    cabecalho = {"Authorization": f"Bearer {token}"}
    assert cliente.get("/eu", headers=cabecalho).json()["email"] == "carla@exemplo.com"

    assert cliente.delete("/auth/sessoes/atual", headers=cabecalho).status_code == 204
    assert cliente.get("/eu", headers=cabecalho).status_code == 401


def test_erros_em_problem_json(cliente):
    cliente.post("/auth/cadastro", json={"email": "carla@exemplo.com", "senha": "senha-forte-1"})
    repetido = cliente.post("/auth/cadastro", json={"email": "carla@exemplo.com", "senha": "senha-forte-1"})
    assert repetido.status_code == 409
    assert repetido.headers["content-type"] == PROBLEMA
    assert repetido.json()["type"] == "urn:pandora:erro:email-ja-cadastrado"

    errado = cliente.post("/auth/sessoes", json={"email": "carla@exemplo.com", "senha": "nao-e-essa"})
    assert errado.status_code == 401
    assert errado.headers["www-authenticate"] == "Bearer"


def test_sem_token_e_token_invalido(cliente):
    assert cliente.get("/eu").status_code == 401
    assert cliente.get("/eu", headers={"Authorization": "Bearer inventado"}).status_code == 401


def test_consentimento_registrar_listar_revogar(autenticado):
    r = autenticado.post("/consentimentos", json={"finalidade": "diagnostico_financeiro", "versao_termo": "2026-11"})
    assert r.status_code == 201 and r.json()["ativo"] is True
    cid = r.json()["id"]
    assert [c["id"] for c in autenticado.get("/consentimentos").json()] == [cid]

    revogado = autenticado.post(f"/consentimentos/{cid}/revogacao")
    assert revogado.status_code == 200
    assert revogado.json()["ativo"] is False and revogado.json()["revogado_em"]


def test_nao_revoga_consentimento_de_outra_pessoa(autenticado, cliente):
    cid = autenticado.post(
        "/consentimentos", json={"finalidade": "diagnostico_financeiro", "versao_termo": "2026-11"}
    ).json()["id"]
    cliente.post("/auth/cadastro", json={"email": "diego@exemplo.com", "senha": "senha-forte-2"})
    token = cliente.post("/auth/sessoes", json={"email": "diego@exemplo.com", "senha": "senha-forte-2"}).json()["token"]
    r = cliente.post(f"/consentimentos/{cid}/revogacao", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404


def test_upload_exige_consentimento_ativo(autenticado):
    arquivo = {"arquivo": ("extrato.csv", b"data,valor\n", "text/csv")}
    sem = autenticado.post("/extratos", files=arquivo)
    assert sem.status_code == 403
    assert sem.json()["type"] == "urn:pandora:erro:consentimento-necessario"

    cid = autenticado.post(
        "/consentimentos", json={"finalidade": "diagnostico_financeiro", "versao_termo": "2026-11"}
    ).json()["id"]
    com = autenticado.post("/extratos", files=arquivo)
    assert com.status_code == 202

    autenticado.post(f"/consentimentos/{cid}/revogacao")
    assert autenticado.post("/extratos", files=arquivo).status_code == 403


def test_apagar_tudo_remove_conta_sessoes_e_consentimentos(autenticado, repos):
    autenticado.post("/consentimentos", json={"finalidade": "diagnostico_financeiro", "versao_termo": "2026-11"})
    assert autenticado.delete("/eu/dados").status_code == 204
    for repo in repos:
        assert repo.dados == {}, type(repo).__name__
    assert autenticado.get("/eu").status_code == 401
