import json

import httpx
import pytest

from pandora_api.adaptadores.dados.trilha_json import TrilhaEmArquivo
from pandora_api.adaptadores.rag.http import AssistenteHttp
from pandora_api.dominio.erros import AssistenteIndisponivel


def test_lista_as_etapas_no_formato_do_caminho(cliente):
    r = cliente.get("/trilha")
    assert r.status_code == 200
    assert r.json() == [
        {"n": 3, "t": "Rotativo", "x": 288, "lado": "e", "marco": None, "emblema": "espiral", "licao_id": "rotativo"}
    ]


def test_licao_traz_explicacao_fontes_e_perguntas(cliente):
    d = cliente.get("/trilha/licoes/rotativo").json()
    assert d["titulo"] == "Rotativo" and d["citacoes_explicacao"] == [1] and d["fontes"][0]["artigo"] == "Art. 104-A"
    p = d["perguntas"][0]
    assert p["certa"] == 0 and p["opcoes"][p["certa"]] == "Cinco anos" and p["citacoes"] == [1]


def test_licao_inexistente_devolve_404(cliente):
    r = cliente.get("/trilha/licoes/nao-existe")
    assert r.status_code == 404 and r.json()["type"] == "urn:pandora:erro:licao-nao-encontrada"


def test_porque_monta_pergunta_completa_para_a_busca(cliente, assistente):
    r = cliente.post("/trilha/licoes/rotativo/porque", json={"pergunta_idx": 0, "opcao": 1})
    assert r.status_code == 200 and r.json()["citacoes"][0]["n"] == 1
    pergunta, contexto = assistente.chamadas[0]
    assert 'Qual o prazo máximo do plano de pagamento? Por que a resposta correta é "Cinco anos"?' in pergunta
    assert 'E por que não "Um ano"?' in pergunta
    assert "Resposta escolhida pela pessoa: Um ano" in contexto


def test_porque_de_quem_acertou_nao_pergunta_pela_errada(cliente, assistente):
    cliente.post("/trilha/licoes/rotativo/porque", json={"pergunta_idx": 0, "opcao": 0})
    assert "E por que não" not in assistente.chamadas[0][0]


@pytest.mark.parametrize("corpo", [{"pergunta_idx": 5, "opcao": 0}, {"pergunta_idx": 0, "opcao": 9}])
def test_porque_com_indice_fora_da_lição_devolve_422(cliente, assistente, corpo):
    r = cliente.post("/trilha/licoes/rotativo/porque", json=corpo)
    assert r.status_code == 422 and assistente.chamadas == []


def test_porque_valida_corpo_e_licao(cliente):
    assert cliente.post("/trilha/licoes/rotativo/porque", json={"pergunta_idx": -1, "opcao": 0}).status_code == 422
    assert cliente.post("/trilha/licoes/x/porque", json={"pergunta_idx": 0, "opcao": 0}).status_code == 404


def test_porque_com_assistente_fora_do_ar_devolve_503(cliente, assistente):
    assistente.indisponivel = True
    assert cliente.post("/trilha/licoes/rotativo/porque", json={"pergunta_idx": 0, "opcao": 0}).status_code == 503


# --- adaptador do RAG ------------------------------------------------------


def _cliente_http(manipulador):
    return httpx.Client(base_url="http://rag", transport=httpx.MockTransport(manipulador))


def test_adaptador_traduz_a_resposta_do_rag():
    def rag(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/responder" and json.loads(req.content) == {"pergunta": "q", "k": 3, "contexto": "ctx"}
        return httpx.Response(
            200,
            json={
                "texto": "ok [1]",
                "abstencao": False,
                "motivo": "ok",
                "modelo": "qwen",
                "latencia_s": 1.0,
                "citacoes": [{"n": 1, "norma": "N", "artigo": None, "link": "https://x", "trecho": "t"}],
            },
        )

    r = AssistenteHttp("http://rag", _cliente_http(rag)).responder("q", "ctx")
    assert r.texto == "ok [1]" and r.citacoes[0].norma == "N" and r.citacoes[0].artigo is None and not r.crise


@pytest.mark.parametrize(
    "resposta",
    [
        httpx.Response(503, json={"detail": "carregando"}),
        httpx.Response(502, text="x"),
        httpx.Response(200, text="não é json"),
        httpx.Response(200, json={"texto": "falta o resto"}),
    ],
)
def test_adaptador_converte_falhas_em_assistente_indisponivel(resposta):
    with pytest.raises(AssistenteIndisponivel):
        AssistenteHttp("http://rag", _cliente_http(lambda req: resposta)).responder("q")


def test_adaptador_converte_timeout_e_conexao_recusada():
    def cai(req):
        raise httpx.ConnectError("recusada")

    with pytest.raises(AssistenteIndisponivel):
        AssistenteHttp("http://rag", _cliente_http(cai)).responder("q")


# --- conteúdo gerado -------------------------------------------------------


def _doc(**mudancas):
    licao = {
        "id": "a",
        "titulo": "A",
        "explicacao": "Texto [1].",
        "citacoes_explicacao": [1],
        "fontes": [{"n": 1, "norma": "N", "artigo": "Art. 1", "link": "https://x", "trecho": "t"}],
        "perguntas": [
            {
                "enunciado": "Pergunta?",
                "opcoes": ["a", "b", "c"],
                "certa": 1,
                "feedback": "Porque sim [1].",
                "citacoes": [1],
            }
        ],
    }
    licao.update(mudancas)
    return {
        "versao": "1",
        "etapas": [
            {"id": "a", "n": 1, "t": "A", "x": 70, "lado": "d", "marco": None, "emblema": "templo", "licao": licao}
        ],
    }


def _arquivo(tmp_path, doc):
    p = tmp_path / "trilha.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_le_o_conteudo_gerado(tmp_path):
    e = TrilhaEmArquivo(_arquivo(tmp_path, _doc())).etapas()[0]
    assert e.licao.perguntas[0].opcoes == ("a", "b", "c") and e.licao.fontes[0].artigo == "Art. 1"


@pytest.mark.parametrize(
    "mudanca",
    [
        {"explicacao": ""},
        {"fontes": []},
        {"perguntas": []},
        {"citacoes_explicacao": [7]},
        {"perguntas": [{"enunciado": "P?", "opcoes": ["a", "b"], "certa": 5, "feedback": "f [1]", "citacoes": [1]}]},
        {"perguntas": [{"enunciado": "P?", "opcoes": ["a", "b"], "certa": 0, "feedback": "f [3]", "citacoes": [3]}]},
    ],
)
def test_rejeita_conteudo_inconsistente_na_inicializacao(tmp_path, mudanca):
    with pytest.raises(ValueError):
        TrilhaEmArquivo(_arquivo(tmp_path, _doc(**mudanca)))


def test_conteudo_real_da_trilha_carrega_e_segue_o_desenho_do_caminho():
    from pandora_api.adaptadores.dados.trilha_json import CAMINHO_PADRAO

    etapas = TrilhaEmArquivo(CAMINHO_PADRAO).etapas()
    assert [e.t for e in etapas] == [
        "Mínimo existencial",
        "Juros e CET",
        "Rotativo",
        "Repactuação",
        "Golpes e MED",
        "Reserva de emergência",
    ]
    assert [e.n for e in etapas] == [1, 2, 3, 4, 5, 6]
    for e in etapas:
        assert e.licao.perguntas and e.licao.explicacao and e.licao.fontes, e.id
        assert all(f.link.startswith("https://") for f in e.licao.fontes), e.id
