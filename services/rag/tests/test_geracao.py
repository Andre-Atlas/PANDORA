import pytest

from pandora_rag.generate.answer import SEM_RESPOSTA, citacoes_validas, montar_prompt, responder
from pandora_rag.generate.gateway import Completude, Gateway, OrcamentoExcedido
from pandora_rag.generate.pii import mascarar
from pandora_rag.index.registro import Registro
from pandora_rag.retrieve.hybrid import Hit


def hit(artigo="Art. 54-A", ressalva=None):
    r = Registro(id="x#1", fonte_id="x", titulo="T", orgao="O", tipo="lei", norma="Lei 14.181/2021", artigo=artigo, texto="Texto do artigo.",
                 hash="h", link="https://x", data_referencia_normativa="2021-07-01", camada_dominio="juridico_superendividamento", ressalva=ressalva)
    return Hit(r, 1.0)


def test_mascara_pii_ficticia():
    t, c = mascarar("CPF 123.456.789-09, cnpj 12.345.678/0001-95, tel (61) 99999-1234, mail ana@ex.com, cartão 4111 1111 1111 1111")
    assert "123.456" not in t and "12.345.678" not in t and "99999" not in t and "ana@" not in t and "4111" not in t
    assert c == {"CPF": 1, "CNPJ": 1, "TELEFONE": 1, "EMAIL": 1, "CARTAO": 1}


def test_mascara_nao_toca_numeros_de_norma():
    t, c = mascarar("A Lei 14.181/2021 e o art. 104-A, prazo de 60 meses, R$ 600")
    assert t == "A Lei 14.181/2021 e o art. 104-A, prazo de 60 meses, R$ 600" and c == {}


def test_citacoes_ignoram_numeros_inexistentes_e_repetidos():
    assert citacoes_validas("A [1] e a [2][1] mas não a [7].", 2) == [1, 2]


def test_prompt_traz_fontes_numeradas_e_aviso_de_vigencia():
    p = montar_prompt("Pergunta?", [hit(), hit("Art. 4", ressalva="Superado pelo STF.")])
    assert "[1] Lei 14.181/2021, Art. 54-A" in p and "AVISO DE VIGÊNCIA: Superado pelo STF." in p and p.endswith("PERGUNTA: Pergunta?")


class GatewayFalso(Gateway):
    def __init__(self, texto):
        self.texto, self.gasto, self.orcamento, self.log, self.config = texto, 0, 30, None, {}

    def gerar(self, chave, sistema, usuario, max_tokens=1024):
        return Completude(self.texto, "falso", 1, 1, 0.0, 0.1, {})


def test_resposta_com_citacao_valida():
    r = responder(GatewayFalso("O prazo é de cinco anos [1]."), "x", "q", [hit()])
    assert not r.abstencao and r.citacao_valida and r.citacoes[0].artigo == "Art. 54-A"


def test_resposta_sem_citacao_e_marcada_invalida():
    r = responder(GatewayFalso("O prazo é de cinco anos."), "x", "q", [hit()])
    assert not r.abstencao and not r.citacao_valida


def test_abstencao_quando_modelo_sinaliza_ou_nao_ha_trechos():
    assert responder(GatewayFalso(SEM_RESPOSTA), "x", "q", [hit()]).abstencao
    assert responder(GatewayFalso("qualquer"), "x", "q", []).abstencao


def test_orcamento_bloqueia_chamada_externa():
    g = Gateway(config={"modelos": {"m": {"provedor": "anthropic", "id": "x", "externo": True}}}, orcamento_usd=1.0)
    g.gasto = 1.0
    with pytest.raises(OrcamentoExcedido):
        g.gerar("m", "s", "u")


class GatewayProibido:
    def gerar(self, *a, **k):
        raise AssertionError("o portão deveria barrar antes de chamar o LLM")


def test_portao_barra_recuperacao_fraca_sem_chamar_llm():
    h = hit()
    h.score_rerank = 0.001
    r = responder(GatewayProibido(), "qwen25-14b", "pergunta fora do corpus", [h], limiar_abstencao=0.02)
    assert r.abstencao and r.modelo == "portao" and r.custo_usd == 0.0
