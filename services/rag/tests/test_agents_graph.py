from typer.testing import CliRunner

from pandora_rag.agents.graph import GrafoPandora, construir_retriever_padrao
from pandora_rag.agents.scenarios import CENARIOS_DEMO, executar_demonstracao
from pandora_rag.cli import app
from pandora_rag.generate.gateway import Completude, Gateway


class GatewayVioladorCVM(Gateway):
    """Gateway simulado que tenta recomendar CDB específico no 1º turno para testar o loop de revisão."""

    def __init__(self):
        self.gasto = 0.0
        self.orcamento = 30.0
        self.log = None
        self.config = {}

    def gerar(self, chave, sistema, usuario, max_tokens=1024, json_modo=False):
        return Completude(
            texto="Compre o CDB do Banco X hoje mesmo para render mais.",
            modelo="simulado",
            tokens_in=10,
            tokens_out=10,
            custo_usd=0.0,
            latencia_s=0.01,
            pii_mascarada={},
        )


def test_quatro_jornadas_demo_exercitam_todos_os_7_agentes_e_cumprem_guardrails(tmp_path):
    retr, origem = construir_retriever_padrao(usar_reranker=False, preferir_embutido=True)
    assert origem == "corpus_embutido_oficial"
    assert len(CENARIOS_DEMO) == 4
    grafo = GrafoPandora(retriever=retr)
    resultados = executar_demonstracao(grafo, saida_dir=tmp_path)
    assert len(resultados) == 4
    agentes_ativos = {m.origem for r in resultados for m in r.trace} | {
        m.destino for r in resultados for m in r.trace
    }
    assert {
        "orquestrador",
        "analista",
        "estrategista",
        "coach",
        "guardiao",
        "educador",
        "compliance",
    }.issubset(agentes_ativos)

    carla, diego, julia, antonio = resultados
    assert "2.100" in carla.resposta_final or "2100" in carla.resposta_final
    assert carla.veredito is not None and carla.veredito.citacoes_validas is True
    assert diego.veredito is not None and diego.veredito.crise_acionada is True and "188" in diego.resposta_final
    assert (
        julia.veredito is not None
        and julia.veredito.bloqueio_cvm_acionado is True
        and "CVM" in julia.resposta_final
    )
    assert antonio.inspecao_fraude is not None and antonio.inspecao_fraude.injection_detectada is True
    assert antonio.inspecao_fraude.boleto is not None and antonio.inspecao_fraude.boleto.suspeito is True
    assert "MED" in antonio.resposta_final or "147" in antonio.resposta_final
    assert antonio.agentes_acionados == [
        "orquestrador",
        "analista",
        "estrategista",
        "guardiao",
        "educador",
        "compliance",
    ]
    assert (tmp_path / "demonstracao_multiagente.md").exists()
    assert (tmp_path / "demonstracao_multiagente.json").exists()


def test_consulta_fora_de_dominio_ativa_abstencao_segura():
    retr, _ = construir_retriever_padrao(usar_reranker=False, preferir_embutido=True)
    grafo = GrafoPandora(retriever=retr)
    res_off = grafo.executar("Qual a melhor receita de bolo de cenoura com cobertura de chocolate?")
    assert res_off.evidencias is not None and res_off.evidencias.abstencao is True
    assert res_off.veredito is not None and res_off.veredito.aprovado is True
    assert "Não encontrei isso nas fontes oficiais" in res_off.resposta_final

    res_ok = grafo.executar("Como funciona a Lei 14.181 do minimo existencial?")
    assert res_ok.evidencias is not None and res_ok.evidencias.abstencao is False
    assert res_ok.evidencias.hits_aprovados >= 1
    assert "[1]" in res_ok.resposta_final


def test_compliance_fail_closed_nao_expoe_rascunho_reprovado(monkeypatch):
    retr, _ = construir_retriever_padrao(usar_reranker=False, preferir_embutido=True)
    grafo = GrafoPandora(retriever=retr)

    def _rascunho_vazado(estado, *args, **kwargs):
        estado.rascunho_resposta = "Compre o CDB do Banco X com CPF 123.456.789-00."
        return estado

    monkeypatch.setattr(grafo.orquestrador, "sintetizar", _rascunho_vazado)
    res = grafo.executar("Qual CDB específico devo comprar hoje?", persona_id="julia_31")
    assert res.veredito is not None and res.veredito.aprovado is False
    assert "123.456.789-00" not in res.resposta_final
    assert "Compre o CDB do Banco X" not in res.resposta_final
    assert "Liquidez Diária" in res.resposta_final


def test_loop_de_revisao_compliance_corrige_rascunho_que_viola_cvm():
    retr, _ = construir_retriever_padrao(usar_reranker=False, preferir_embutido=True)
    grafo = GrafoPandora(retriever=retr, gateway=GatewayVioladorCVM())
    res = grafo.executar(
        consulta="Qual CDB específico de qual banco devo comprar hoje com R$ 1.500?",
        persona_id="julia_31",
        llm="simulado",
    )
    assert res.veredito is not None
    assert res.veredito.aprovado is True
    assert res.veredito.bloqueio_cvm_acionado is True
    assert res.veredito.precisou_revisao is True
    assert any(m.tipo == "validacao" and m.origem == "compliance" for m in res.trace)
    assert any(m.tipo == "revisao" and m.origem == "orquestrador" for m in res.trace)
    assert "Liquidez Diária" in res.resposta_final


def test_cli_agent_e_demo_executam_com_sucesso(tmp_path):
    runner = CliRunner()
    res_agent = runner.invoke(
        app,
        [
            "agent",
            "Meu CPF 123.456.789-00. Estou no rotativo do cartao e a luz atrasou.",
            "--persona",
            "carla_34",
            "--offline",
            "--saida-json",
        ],
    )
    assert res_agent.exit_code == 0, res_agent.output
    assert "[CPF]" in res_agent.output
    assert "123.456.789-00" not in res_agent.output

    res_demo = runner.invoke(app, ["demo", "--offline", "--saida-dir", str(tmp_path)])
    assert res_demo.exit_code == 0, res_demo.output
    assert (tmp_path / "demonstracao_multiagente.md").exists()
    assert (tmp_path / "demonstracao_multiagente.json").exists()
