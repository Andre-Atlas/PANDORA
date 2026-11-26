import time

import pytest
from fastapi.testclient import TestClient

from pandora_rag.config import resolver_db_url
from pandora_rag.generate.answer import SEM_RESPOSTA
from pandora_rag.generate.gateway import Completude
from pandora_rag.index.registro import Registro
from pandora_rag.retrieve.hybrid import Hit
from pandora_rag.servico.app import criar_app, pergunta_para_llm


def hit(score_rerank=0.9):
    r = Registro(id="x#1", fonte_id="x", titulo="T", orgao="O", tipo="lei", norma="Lei 14.181/2021", artigo="Art. 54-A",
                 texto="Texto do artigo sobre crédito responsável.", hash="h", link="https://planalto.gov.br/x",
                 data_referencia_normativa="2021-07-01", camada_dominio="juridico_superendividamento", ressalva=None)
    h = Hit(r, 1.0)
    h.score_rerank = score_rerank
    return h


class RetrieverFalso:
    def __init__(self, score_rerank=0.9):
        self.score_rerank, self.perguntas = score_rerank, []
        self.registros = [object()] * 3

    def buscar(self, pergunta, k):
        self.perguntas.append((pergunta, k))
        return [hit(self.score_rerank)]


class GatewayFalso:
    def __init__(self, texto="O prazo é de cinco anos [1]."):
        self.texto, self.usuarios = texto, []

    def gerar(self, chave, sistema, usuario, max_tokens=1024, json_modo=False):
        self.usuarios.append(usuario)
        return Completude(self.texto, "qwen-falso", 1, 1, 0.0, 0.1, {})


def cliente(retr=None, gw=None, limiar=0.02):
    retr, gw = retr or RetrieverFalso(), gw or GatewayFalso()
    app = criar_app(lambda: retr, lambda: gw, "qwen25-14b", limiar)
    return TestClient(app), retr, gw


def esperar_pronto(c):
    for _ in range(100):
        if c.get("/saude").json()["pronto"]:
            return
        time.sleep(0.02)
    raise AssertionError("serviço não ficou pronto")


def test_saude_informa_chunks_quando_pronto():
    with TestClient(criar_app(lambda: RetrieverFalso(), lambda: GatewayFalso(), "x", None)) as c:
        esperar_pronto(c)
        assert c.get("/saude").json() == {"estado": "pronto", "pronto": True, "chunks": 3}


def test_responde_com_citacoes_e_motivo_ok():
    c, retr, _ = cliente()
    with c:
        esperar_pronto(c)
        r = c.post("/responder", json={"pergunta": "Qual o prazo?"})
    assert r.status_code == 200
    d = r.json()
    assert d["abstencao"] is False and d["motivo"] == "ok" and d["modelo"] == "qwen-falso"
    assert d["citacoes"][0]["artigo"] == "Art. 54-A" and d["citacoes"][0]["link"].startswith("https://")
    assert retr.perguntas == [("Qual o prazo?", 3)]


def test_portao_abstem_sem_chamar_o_llm():
    gw = GatewayFalso()
    c, _, _ = cliente(RetrieverFalso(score_rerank=0.001), gw)
    with c:
        esperar_pronto(c)
        d = c.post("/responder", json={"pergunta": "Devo comprar bitcoin?"}).json()
    assert d["abstencao"] is True and d["motivo"] == "portao" and d["citacoes"] == [] and gw.usuarios == []


def test_llm_que_nao_sustenta_vira_abstencao_com_motivo_llm():
    c, _, _ = cliente(gw=GatewayFalso(SEM_RESPOSTA))
    with c:
        esperar_pronto(c)
        d = c.post("/responder", json={"pergunta": "algo"}).json()
    assert d["abstencao"] is True and d["motivo"] == "llm"


def test_contexto_vai_ao_llm_mas_nao_a_busca():
    c, retr, gw = cliente()
    with c:
        esperar_pronto(c)
        c.post("/responder", json={"pergunta": "Por que a b?", "contexto": "Questão: qual o prazo?"})
    assert retr.perguntas[0][0] == "Por que a b?"
    assert "Questão: qual o prazo?" in gw.usuarios[0] and "não é fonte" in gw.usuarios[0]


@pytest.mark.parametrize("corpo", [{"pergunta": ""}, {"pergunta": "x" * 2001}, {}, {"pergunta": "ok", "k": 0}])
def test_entrada_invalida_devolve_422(corpo):
    c, _, _ = cliente()
    with c:
        esperar_pronto(c)
        assert c.post("/responder", json=corpo).status_code == 422


def test_pergunta_so_com_espacos_devolve_422():
    c, _, _ = cliente()
    with c:
        esperar_pronto(c)
        assert c.post("/responder", json={"pergunta": "   "}).status_code == 422


def test_503_enquanto_carrega_e_quando_a_montagem_falha():
    def lento():
        time.sleep(0.3)
        return RetrieverFalso()

    with TestClient(criar_app(lento, lambda: GatewayFalso(), "x", None)) as c:
        assert c.get("/saude").json()["estado"] == "carregando"
        assert c.post("/responder", json={"pergunta": "oi"}).status_code == 503

    def quebra():
        raise ConnectionError("banco fora do ar")

    with TestClient(criar_app(quebra, lambda: GatewayFalso(), "x", None)) as c:
        for _ in range(100):
            if "ConnectionError" in c.get("/saude").json()["estado"]:
                break
            time.sleep(0.02)
        assert c.get("/saude").json()["pronto"] is False
        assert c.post("/responder", json={"pergunta": "oi"}).status_code == 503


def test_falha_do_llm_vira_502():
    class GatewayQuebrado:
        def gerar(self, *a, **k):
            raise RuntimeError("ollama fora")

    c, _, _ = cliente(gw=GatewayQuebrado())
    with c:
        esperar_pronto(c)
        assert c.post("/responder", json={"pergunta": "oi"}).status_code == 502


def test_pergunta_para_llm_sem_contexto_e_identica():
    assert pergunta_para_llm("q", None) == "q"


def test_db_url_prefere_a_variavel_do_rag_e_avisa_sobre_a_antiga():
    assert resolver_db_url({"PANDORA_RAG_DB_URL": "a", "PANDORA_DB_URL": "b"}) == "a"
    with pytest.warns(DeprecationWarning):
        assert resolver_db_url({"PANDORA_DB_URL": "b"}) == "b"
    assert resolver_db_url({}).endswith(":5433/pandora_rag")
