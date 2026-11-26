import pytest

from pandora_api.aplicacao.chat import MENSAGEM_CRISE
from pandora_api.dominio.crise import detecta_crise


def test_chat_responde_com_fontes_sem_pedir_login(cliente, assistente):
    r = cliente.post("/chat", json={"pergunta": "Qual o prazo do plano de pagamento?"})
    assert r.status_code == 200
    d = r.json()
    assert d["texto"].endswith("[1].") and d["abstencao"] is False and d["crise"] is False and d["modelo"] == "falso"
    assert d["citacoes"] == [
        {
            "n": 1,
            "norma": "Lei 14.181/2021",
            "artigo": "Art. 104-A",
            "link": "https://www.planalto.gov.br/x",
            "trecho": "O plano pode durar até cinco anos.",
            "pagina": None,
            "ressalva": None,
        }
    ]
    assert assistente.chamadas == [("Qual o prazo do plano de pagamento?", None)]


def test_chat_repassa_a_abstencao(cliente, assistente):
    from pandora_api.portas.assistente import RespostaElpis

    assistente.resposta = RespostaElpis("Não encontrei isso nas fontes oficiais.", True, "portao")
    d = cliente.post("/chat", json={"pergunta": "Devo comprar bitcoin?"}).json()
    assert d["abstencao"] is True and d["citacoes"] == [] and d["crise"] is False


def test_chat_em_crise_acolhe_sem_consultar_o_modelo(cliente, assistente):
    r = cliente.post("/chat", json={"pergunta": "não aguento mais essas dívidas, quero sumir"})
    d = r.json()
    assert r.status_code == 200 and d["crise"] is True and d["texto"] == MENSAGEM_CRISE and d["modelo"] == "regra-crise"
    assert "188" in d["texto"] and d["citacoes"] == [] and assistente.chamadas == []


def test_chat_com_assistente_fora_do_ar_devolve_503_problem_json(cliente, assistente):
    assistente.indisponivel = True
    r = cliente.post("/chat", json={"pergunta": "Oi?"})
    assert r.status_code == 503 and r.headers["content-type"] == "application/problem+json"
    assert r.json()["type"] == "urn:pandora:erro:elpis-indisponivel"


@pytest.mark.parametrize("corpo", [{}, {"pergunta": ""}, {"pergunta": "x" * 2001}])
def test_chat_valida_a_pergunta(cliente, corpo):
    assert cliente.post("/chat", json=corpo).status_code == 422


@pytest.mark.parametrize(
    "texto",
    [
        "quero morrer",
        "Vou me MATAR",
        "estou pensando em suicídio",
        "quero acabar com tudo",
        "NÃO AGUENTO MAIS VIVER",
        "penso em me machucar",
        "melhor sem mim",
        "quero sumir",
    ],
)
def test_detecta_sinais_de_crise(texto):
    assert detecta_crise(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "Posso ser executado e perder o salário?",
        "como sumir com os juros do cartão",
        "o banco quer me matar de juros? qual o limite",
        "qual o prazo para quitar a dívida",
        "acabar com a dívida do cartão",
        "Podem bloquear meu salário?",
    ],
)
def test_nao_dispara_crise_em_pergunta_financeira(texto):
    assert not detecta_crise(texto)
