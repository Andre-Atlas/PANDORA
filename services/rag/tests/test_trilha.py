import json

import pytest

from pandora_rag.generate.gateway import Completude
from pandora_rag.index.registro import Registro
from pandora_rag.retrieve.hybrid import Hit
from pandora_rag.trilha import (
    N_OPCOES, ROTEIRO, embaralhar_opcoes, extrair_json, gerar_etapa, gerar_perguntas, limpar_marcadores, montar_documento,
    numeros_relevantes, validar_pergunta,
)


def hit(texto="O mínimo existencial é a renda de R$ 600,00 por mês e o prazo é de 60 meses.", score=0.9):
    r = Registro(id="x#1", fonte_id="x", titulo="T", orgao="O", tipo="lei", norma="Lei 14.181/2021", artigo="Art. 104-A", texto=texto,
                 hash="h", link="https://x", data_referencia_normativa="2021-07-01", camada_dominio="juridico_superendividamento",
                 ressalva=None, versao_corpus="c1")
    h = Hit(r, 1.0)
    h.score_rerank = score
    return h


def boa(**mudancas):
    p = {"enunciado": "Qual é o prazo máximo do plano de pagamento?", "opcoes": ["60 meses", "12 meses", "Sem prazo definido"],
         "certa": 0, "feedback": "O plano pode ter até 60 meses [1]."}
    p.update(mudancas)
    return p


def test_pergunta_valida_nao_tem_erros():
    assert validar_pergunta(boa(), [hit()]) == []


@pytest.mark.parametrize("mudanca,trecho", [
    ({"opcoes": ["a", "b"]}, "3 opções"),
    ({"opcoes": ["60 meses", "60 meses", "Outra"]}, "repetidas"),
    ({"certa": 3}, "inválido"),
    ({"certa": True}, "inválido"),
    ({"feedback": "O plano pode ter até 60 meses."}, "sem citação"),
    ({"feedback": "O plano pode ter até 60 meses [4]."}, "sem citação"),
    ({"enunciado": "Curto?"}, "enunciado"),
    ({"feedback": "O plano pode ter até 84 meses [1]."}, "84"),
])
def test_regras_de_validacao(mudanca, trecho):
    erros = validar_pergunta(boa(**mudanca), [hit()])
    assert any(trecho in e for e in erros), erros


def test_numero_so_conta_se_aparece_inteiro_na_fonte():
    # 700 não está na fonte; 60 não "contém" 600 nem o contrário
    assert validar_pergunta(boa(opcoes=["700 meses", "12 meses", "Sem prazo"]), [hit()])
    # opção errada pode ter número fora da fonte
    assert validar_pergunta(boa(opcoes=["60 meses", "999 meses", "Sem prazo"]), [hit()]) == []
    # R$ 600,00 na fonte equivale a 600 na pergunta
    assert validar_pergunta(boa(enunciado="A renda protegida é de R$ 600 por mês?", opcoes=["Sim", "Não", "Talvez"], feedback="É de R$ 600 [1]."), [hit()]) == []


def test_numero_da_norma_no_rotulo_da_fonte_conta_como_fonte():
    # "Lei 14.181/2021, Art. 104-A" está no rótulo da fonte, mesmo fora do corpo do texto
    p = boa(enunciado="O que diz o Art. 104-A da Lei 14.181/2021 sobre o plano?", feedback="Pelo Art. 104-A da Lei 14.181/2021 [1].")
    assert validar_pergunta(p, [hit()]) == []
    assert validar_pergunta(boa(feedback="Pela Lei 99.999/2021 [1]."), [hit()])


def test_marcador_de_citacao_nao_e_numero():
    assert numeros_relevantes("veja [12] e o art. 6") == []
    assert numeros_relevantes("prazo de 60 meses e 2,5%") == ["60", "25"]


def test_embaralhar_preserva_a_resposta_certa_e_e_deterministico():
    p = boa()
    q = embaralhar_opcoes(p, "semente")
    assert q["opcoes"][q["certa"]] == "60 meses" and sorted(q["opcoes"]) == sorted(p["opcoes"])
    assert embaralhar_opcoes(p, "semente") == q
    posicoes = {embaralhar_opcoes(p, f"s{i}")["certa"] for i in range(30)}
    assert posicoes == set(range(N_OPCOES))


def test_extrair_json_aceita_cerca_e_texto_em_volta():
    assert extrair_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extrair_json('Claro! {"a": 2} pronto') == {"a": 2}
    with pytest.raises(json.JSONDecodeError):
        extrair_json("sem json")


class GatewayRoteirizado:
    """Responde a explicação (texto) e depois cada rodada de perguntas (JSON), na ordem."""

    def __init__(self, *respostas):
        self.respostas, self.chamadas = list(respostas), []

    def gerar(self, chave, sistema, usuario, max_tokens=1024, json_modo=False):
        self.chamadas.append(json_modo)
        return Completude(self.respostas.pop(0), "falso", 1, 1, 0.0, 0.1, {})


class RetrieverFalso:
    def __init__(self, score=0.9):
        self.score, self.registros = score, [hit().registro]

    def buscar(self, pergunta, k):
        return [hit(score=self.score)]


def rodada(*perguntas):
    return json.dumps({"perguntas": list(perguntas)})


def test_gerar_perguntas_descarta_invalidas_e_tenta_de_novo():
    invalida = boa(enunciado="Outra pergunta sobre o plano de pagamento?", feedback="sem citação")
    gw = GatewayRoteirizado(rodada(boa(), invalida), rodada(boa(enunciado="Quantos meses dura o plano de pagamento?")))
    r = gerar_perguntas(gw, "x", [hit()], "etapa", tentativas=3)
    assert len(r.perguntas) == 2 and len(r.descartadas) == 1
    assert all(p["citacoes"] == [1] for p in r.perguntas)


def test_gerar_perguntas_para_ao_atingir_o_numero_e_tolera_lixo():
    gw = GatewayRoteirizado("isto não é json", rodada(boa(), boa(enunciado="Quantos meses dura o plano de pagamento?")))
    r = gerar_perguntas(gw, "x", [hit()], "etapa", tentativas=3)
    assert len(r.perguntas) == 2 and gw.respostas == [] and r.descartadas[0]["erros"] == ["resposta não é JSON"]


def test_gerar_etapa_completa():
    gw = GatewayRoteirizado("O plano pode durar até 60 meses [1].", rodada(boa(), boa(enunciado="Quantos meses dura o plano de pagamento?")))
    e = gerar_etapa(RetrieverFalso(), gw, "x", ROTEIRO[0], limiar=0.02)
    assert e["_controle"]["problemas"] == [] and e["licao"]["citacoes_explicacao"] == [1]
    assert e["licao"]["fontes"][0]["artigo"] == "Art. 104-A" and gw.chamadas == [False, True]
    assert e["licao"]["perguntas"][0]["citacoes"] == [1]


def test_gerar_etapa_registra_problemas_quando_o_rag_se_abstem():
    gw = GatewayRoteirizado()
    e = gerar_etapa(RetrieverFalso(score=0.001), gw, "x", ROTEIRO[0], limiar=0.02)
    assert "explicação: o RAG se absteve" in e["_controle"]["problemas"] and e["licao"]["perguntas"] == [] and gw.chamadas == []


def test_documento_nao_leva_o_controle_e_tem_hash_estavel():
    e = gerar_etapa(RetrieverFalso(), GatewayRoteirizado("Texto [1].", rodada(boa(), boa(enunciado="Quantos meses dura o plano de pagamento?"))), "x", ROTEIRO[1], limiar=0.02)
    d = montar_documento([e], "c1", "qwen2.5:14b")
    assert "_controle" not in d["etapas"][0] and d["validacao"] == "automatica" and d["corpus"] == "c1"
    assert d["hash"] == montar_documento([e], "c1", "qwen2.5:14b")["hash"]


def test_roteiro_segue_as_seis_etapas_do_design_system():
    assert [e["t"] for e in ROTEIRO] == ["Mínimo existencial", "Juros e CET", "Rotativo", "Repactuação", "Golpes e MED", "Reserva de emergência"]
    assert len({e["id"] for e in ROTEIRO}) == 6


def test_pergunta_nao_pode_citar_fonte_com_aviso_de_vigencia():
    com_aviso = hit()
    com_aviso.registro.ressalva = "Trecho superado pelo STF."
    assert validar_pergunta(boa(), [com_aviso]) == ["cita fonte com aviso de vigência"]


@pytest.mark.parametrize("texto,esperado", [
    ("O prazo é de 60 meses [1][8].", "O prazo é de 60 meses [1]."),
    ("Veja [9] e [2].", "Veja e [2]."),
    ("Sem marcador.", "Sem marcador."),
    ("Tudo certo [1][2].", "Tudo certo [1][2]."),
])
def test_limpar_marcadores_remove_so_os_que_nao_tem_fonte(texto, esperado):
    assert limpar_marcadores(texto, 4 if "[8]" in texto or "[9]" in texto else 2).replace("  ", " ") == esperado
