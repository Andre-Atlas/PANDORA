"""Grafo de orquestração multiagente do PANDORA com LangGraph (StateGraph) e Tool Calling."""
from __future__ import annotations

import logging
import time
import zlib
from typing import Any

import numpy as np
import psycopg
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from pandora_rag.agents.llm_provider import (
    MODELO_PADRAO_AGENTES,
    construir_chat_model,
    ollama_disponivel,
    resolver_config_modelo,
)
from pandora_rag.agents.models import EstadoMultiagente, ResultadoMultiagente
from pandora_rag.agents.specialists import (
    BLOCO_PROTOCOLO_CRISE,
    AnalistaAgent,
    CoachAgent,
    ComplianceAgent,
    EducadorAgent,
    EstrategistaAgent,
    GuardiaoAgent,
    OrquestradorAgent,
    bloco_recusa_educativa_cvm,
)
from pandora_rag.agents.tools import perfil_persona
from pandora_rag.config import DB_URL, TEXT_DIR
from pandora_rag.generate.answer import MENSAGEM_ABSTENCAO
from pandora_rag.generate.gateway import Gateway
from pandora_rag.generate.pii import mascarar
from pandora_rag.index.build import CACHE as EMBEDDINGS_CACHE
from pandora_rag.index.build import embeddings as carregar_ou_gerar_embeddings
from pandora_rag.index.registro import Registro, montar_registros
from pandora_rag.index.store import MemoryStore, PgVectorStore
from pandora_rag.index.tokenizer import tokenizar
from pandora_rag.retrieve.hybrid import IndiceBM25, Parametros, Reranker, Retriever

logger = logging.getLogger(__name__)

_ORDEM_ESPECIALISTAS_DOMINIO = ("analista", "estrategista", "coach", "guardiao")


def _cache_embeddings_dir_disponivel() -> bool:
    return EMBEDDINGS_CACHE.exists() and any(EMBEDDINGS_CACHE.glob("*.npy"))


class EmbedderHash:
    """Embedder vetorial determinístico sem rede/GPU para fallback e testes offline."""

    dim = 128

    def _vetor(self, texto: str) -> np.ndarray:
        v = np.zeros(self.dim, dtype=np.float32)
        for tok in tokenizar(texto):
            v[zlib.crc32(tok.encode("utf-8")) % self.dim] += 1.0
        norma = float(np.linalg.norm(v))
        return v / norma if norma > 0 else v

    def passagens(self, textos: list[str]) -> np.ndarray:
        return np.stack([self._vetor(t) for t in textos])

    consultas = passagens


def corpus_embutido_oficial() -> list[Registro]:
    """Subconjunto fiel de normas oficiais do corpus PANDORA para modo offline/CI."""
    return [
        Registro(
            id="lei14181#54-A",
            fonte_id="lei_14181",
            titulo="Lei nº 14.181/2021 (Lei do Superendividamento)",
            orgao="Presidência da República",
            tipo="lei",
            norma="Lei 14.181/2021",
            artigo="Art. 54-A do CDC",
            texto=(
                "Dispõe sobre a prevenção e o tratamento do superendividamento da pessoa natural, "
                "entendido como a impossibilidade manifesta de o consumidor pagar a totalidade de suas "
                "dívidas de consumo exigíveis e vincendas sem comprometer seu mínimo existencial."
            ),
            hash="embutido-14181-54a",
            link="https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm",
            data_referencia_normativa="2021-07-01",
            camada_dominio="juridico_superendividamento",
            elegivel_lei_14181=True,
        ),
        Registro(
            id="lei14181#104-A",
            fonte_id="lei_14181",
            titulo="Lei nº 14.181/2021 (Repactuação de Dívidas)",
            orgao="Presidência da República",
            tipo="lei",
            norma="Lei 14.181/2021",
            artigo="Art. 104-A do CDC",
            texto=(
                "A requerimento do consumidor superendividado pessoa natural, o juiz, o Procon ou a "
                "Defensoria Pública poderá instaurar processo de repactuação de dívidas visando à "
                "realização de audiência conciliatória com plano de pagamento de até 5 anos, preservado "
                "o mínimo existencial."
            ),
            hash="embutido-14181-104a",
            link="https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm",
            data_referencia_normativa="2021-07-01",
            camada_dominio="juridico_superendividamento",
            elegivel_lei_14181=True,
        ),
        Registro(
            id="lei14690#28",
            fonte_id="lei_14690",
            titulo="Lei nº 14.690/2023 (Teto do Rotativo do Cartão)",
            orgao="Presidência da República",
            tipo="lei",
            norma="Lei 14.690/2023",
            artigo="Art. 28",
            texto=(
                "O valor total cobrado a título de juros e encargos financeiros no crédito rotativo "
                "e no parcelamento de saldo devedor da fatura de cartão de crédito não pode exceder "
                "100% do valor original da dívida."
            ),
            hash="embutido-14690-28",
            link="https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm",
            data_referencia_normativa="2023-10-03",
            camada_dominio="regulatorio_bancario",
        ),
        Registro(
            id="cpc#833-IV",
            fonte_id="cpc_833",
            titulo="Código de Processo Civil (Impenhorabilidade Salarial)",
            orgao="Presidência da República",
            tipo="lei",
            norma="CPC (Lei 13.105/2015)",
            artigo="Art. 833, IV",
            texto=(
                "São absolutamente impenhoráveis os vencimentos, os subsídios, os soldos, os salários, "
                "as remunerações, os proventos de aposentadoria, as pensões e os ganhos de trabalhador "
                "autônomo destinados ao sustento da família."
            ),
            hash="embutido-cpc-833",
            link="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm",
            data_referencia_normativa="2015-03-16",
            camada_dominio="juridico_superendividamento",
        ),
        Registro(
            id="lei14790#jogo_responsavel",
            fonte_id="lei_14790",
            titulo="Lei nº 14.790/2023 (Marco das Apostas de Quota Fixa)",
            orgao="Presidência da República",
            tipo="lei",
            norma="Lei 14.790/2023",
            artigo="Arts. 24 e 25",
            texto=(
                "As operadoras de apostas de quota fixa autorizadas pela SPA/MF (.bet.br) devem "
                "assegurar mecanismos de jogo responsável, incluindo definição de limites de depósito, "
                "pausas temporárias e autoexclusão do apostador."
            ),
            hash="embutido-14790-24",
            link="https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm",
            data_referencia_normativa="2023-12-29",
            camada_dominio="regulatorio_bancario",
        ),
        Registro(
            id="bcb147#med",
            fonte_id="res_bcb_147",
            titulo="Resolução BCB nº 147/2021 (Mecanismo Especial de Devolução — MED do Pix)",
            orgao="Banco Central do Brasil",
            tipo="resolucao",
            norma="Resolução BCB 147/2021",
            artigo="Regulamento do Pix — MED",
            texto=(
                "Institui o Mecanismo Especial de Devolução (MED) no Pix para casos de fundada suspeita "
                "de fraude ou golpe, permitindo o bloqueio cautelar dos recursos na conta recebedora e a "
                "solicitação de devolução pelo usuário pagador em até 80 dias da transação."
            ),
            hash="embutido-bcb-147",
            link="https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=147",
            data_referencia_normativa="2021-09-28",
            camada_dominio="fraudes_pix_med",
        ),
        Registro(
            id="cvm19#consultoria",
            fonte_id="res_cvm_19",
            titulo="Resolução CVM nº 19/2021 (Consultoria de Valores Mobiliários)",
            orgao="Comissão de Valores Mobiliários",
            tipo="resolucao",
            norma="Resolução CVM 19/2021",
            artigo="Art. 2º",
            texto=(
                "A prestação de serviço de consultoria de valores mobiliários, incluindo recomendação "
                "específica de ativos, ações ou títulos, é atividade regulada que exige autorização "
                "prévia da CVM, sendo vedada a assistentes educacionais não registrados."
            ),
            hash="embutido-cvm-19",
            link="https://conteudo.cvm.gov.br/legislacao/resolucoes/resol019.html",
            data_referencia_normativa="2021-02-25",
            camada_dominio="regulatorio_bancario",
        ),
        Registro(
            id="cvm30#suitability",
            fonte_id="res_cvm_30",
            titulo="Resolução CVM nº 30/2021 (Dever de Verificação de Adequação — Suitability)",
            orgao="Comissão de Valores Mobiliários",
            tipo="resolucao",
            norma="Resolução CVM 30/2021",
            artigo="Arts. 2º e 3º",
            texto=(
                "A adequação de investimentos deve considerar objetivos financeiros, horizonte de "
                "liquidez e tolerância a risco do investidor, priorizando liquidez diária e baixo risco "
                "para reserva de emergência."
            ),
            hash="embutido-cvm-30",
            link="https://conteudo.cvm.gov.br/legislacao/resolucoes/resol030.html",
            data_referencia_normativa="2021-05-11",
            camada_dominio="educacao_orcamento",
        ),
    ]


def construir_retriever_padrao(
    usar_reranker: bool = False,
    preferir_embutido: bool = False,
    tabela: str = "chunks",
    modelo_embedding: str = "BAAI/bge-m3",
) -> tuple[Retriever, str]:
    """Constrói o Retriever priorizando Postgres, depois corpus local extraído, e por fim corpus embutido."""
    if not preferir_embutido:
        try:
            with psycopg.connect(DB_URL, connect_timeout=2) as _:
                pass
            from pandora_rag.index.embedder import Embedder

            emb = Embedder(modelo_embedding)
            pg = PgVectorStore(DB_URL, tabela, emb.dim)
            regs = pg.carregar_registros()
            if regs:
                rer = Reranker() if usar_reranker else None
                return Retriever(pg, IndiceBM25(regs), emb, rer), "pgvector"
        except (ImportError, OSError, RuntimeError, ValueError, psycopg.Error) as exc:
            logger.info("Postgres indisponível para agentes; tentando índice local em memória: %s", exc)

        if TEXT_DIR.exists() and any(TEXT_DIR.iterdir()):
            try:
                regs = montar_registros("estrutural", texto_dir=TEXT_DIR)
                if regs:
                    rer = Reranker() if usar_reranker else None
                    if _cache_embeddings_dir_disponivel():
                        from pandora_rag.index.embedder import Embedder

                        emb = Embedder(modelo_embedding)
                        vetores = carregar_ou_gerar_embeddings(regs, emb)
                        store = MemoryStore(regs, vetores)
                        return Retriever(store, IndiceBM25(regs), emb, rer), "corpus_local_bge_m3"
                    emb_hash = EmbedderHash()
                    store = MemoryStore(regs, emb_hash.passagens([r.texto_indexado() for r in regs]))
                    return Retriever(store, IndiceBM25(regs), emb_hash, rer), "corpus_local_bm25_hash"
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                logger.info("Falha ao carregar corpus local extraído; usando embutido: %s", exc)

    regs_emb = corpus_embutido_oficial()
    emb_hash = EmbedderHash()
    store_emb = MemoryStore(regs_emb, emb_hash.passagens([r.texto_indexado() for r in regs_emb]))
    rer_emb = Reranker() if usar_reranker else None
    return Retriever(store_emb, IndiceBM25(regs_emb), emb_hash, rer_emb, Parametros()), "corpus_embutido_oficial"


def _resposta_segura_fail_closed(estado: EstadoMultiagente) -> str:
    """Resposta fail-closed caso a validação final de compliance continue reprovada após revisão."""
    partes: list[str] = []
    if estado.veredito and estado.veredito.crise_acionada:
        partes.append(BLOCO_PROTOCOLO_CRISE)
    if estado.veredito and estado.veredito.bloqueio_cvm_acionado:
        perfil = perfil_persona(estado.persona_id) if estado.persona_id else None
        partes.append(bloco_recusa_educativa_cvm(perfil))
    if estado.inspecao_fraude is not None and estado.inspecao_fraude.fraude_detectada:
        partes.append(
            "ALERTA DE SEGURANÇA: Detectamos indícios de fraude no documento ou transação analisada. "
            "Não efetue pagamentos nem forneça dados bancários e acione o MED do Pix em até 80 dias."
        )
    if partes:
        partes.append(
            "Para os demais pontos, não consegui validar uma resposta segura; procure o Procon, "
            "a Defensoria Pública ou o canal de atendimento do Banco Central."
        )
    else:
        partes.append(MENSAGEM_ABSTENCAO)
    texto_seguro, _ = mascarar("\n\n".join(partes))
    return texto_seguro


class GrafoPandora:
    """Orquestrador multiagente compilado com LangGraph (StateGraph) e Tool Calling nativo."""

    def __init__(
        self,
        retriever: Retriever | None = None,
        gateway: Gateway | None = None,
        k_evidencias: int = 3,
        limiar_abstencao: float = 0.02,
        origem_retriever: str | None = None,
    ):
        if retriever is None:
            retriever, origem = construir_retriever_padrao(usar_reranker=False, preferir_embutido=False)
            self.origem_retriever = origem_retriever or origem
        else:
            self.origem_retriever = origem_retriever or "retriever_injetado"
        self.retriever = retriever
        self.gateway = gateway
        self.k_evidencias = k_evidencias
        self.limiar_abstencao = limiar_abstencao

        self.orquestrador = OrquestradorAgent()
        self.analista = AnalistaAgent()
        self.estrategista = EstrategistaAgent()
        self.coach = CoachAgent()
        self.guardiao = GuardiaoAgent()
        self.educador = EducadorAgent()
        self.compliance = ComplianceAgent()

        # Contexto da execução atual usado pelos nós do StateGraph
        self._chat_model_atual: BaseChatModel | None = None
        self._modelo_id_atual: str = "offline"
        self._gateway_atual: Gateway | None = None
        self._llm_chave_atual: str | None = None

        self.state_graph = self._construir_state_graph()
        self.compiled_graph = self.state_graph.compile()

    def _construir_state_graph(self) -> StateGraph:
        """Constrói o StateGraph declarativo do LangGraph com os 7 agentes e arestas condicionais."""
        workflow = StateGraph(EstadoMultiagente)

        def node_orquestrador_planejar(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.orquestrador.planejar(
                estado,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_analista(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.analista.executar(
                estado,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_estrategista(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.estrategista.executar(
                estado,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_coach(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.coach.executar(
                estado,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_guardiao(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.guardiao.executar(
                estado,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_educador(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.educador.executar(
                estado,
                self.retriever,
                k=self.k_evidencias,
                limiar_abstencao=self.limiar_abstencao,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_orquestrador_sintetizar(estado: EstadoMultiagente) -> EstadoMultiagente:
            modo_revisao = estado.revisoes_realizadas > 0
            return self.orquestrador.sintetizar(
                estado,
                gateway=None if modo_revisao else self._gateway_atual,
                modelo=None if modo_revisao else self._llm_chave_atual,
                modo_revisao=modo_revisao,
                chat_model=None if modo_revisao else self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_compliance(estado: EstadoMultiagente) -> EstadoMultiagente:
            return self.compliance.validar(
                estado,
                chat_model=self._chat_model_atual,
                modelo_id=self._modelo_id_atual,
            )

        def node_preparar_revisao(estado: EstadoMultiagente) -> EstadoMultiagente:
            estado.revisoes_realizadas += 1
            return estado

        def node_fail_closed(estado: EstadoMultiagente) -> EstadoMultiagente:
            estado.resposta_final = _resposta_segura_fail_closed(estado)
            return estado

        workflow.add_node("orquestrador_planejar", node_orquestrador_planejar)
        workflow.add_node("analista", node_analista)
        workflow.add_node("estrategista", node_estrategista)
        workflow.add_node("coach", node_coach)
        workflow.add_node("guardiao", node_guardiao)
        workflow.add_node("educador", node_educador)
        workflow.add_node("orquestrador_sintetizar", node_orquestrador_sintetizar)
        workflow.add_node("compliance", node_compliance)
        workflow.add_node("preparar_revisao", node_preparar_revisao)
        workflow.add_node("fail_closed", node_fail_closed)

        def rotear_apos_planejamento(estado: EstadoMultiagente) -> str:
            for cand in _ORDEM_ESPECIALISTAS_DOMINIO:
                if cand in estado.agentes_planejados:
                    return cand
            return "educador"

        def _criar_roteador_pos_especialista(atual: str):
            idx_atual = _ORDEM_ESPECIALISTAS_DOMINIO.index(atual)
            seguintes = _ORDEM_ESPECIALISTAS_DOMINIO[idx_atual + 1 :]

            def _rotear(estado: EstadoMultiagente) -> str:
                for cand in seguintes:
                    if cand in estado.agentes_planejados:
                        return cand
                return "educador"

            return _rotear

        def rotear_pos_compliance(estado: EstadoMultiagente) -> str:
            if estado.veredito is not None and estado.veredito.aprovado and estado.resposta_final:
                return END
            if estado.revisoes_realizadas < 1:
                return "preparar_revisao"
            return "fail_closed"

        mapa_destinos = {
            "analista": "analista",
            "estrategista": "estrategista",
            "coach": "coach",
            "guardiao": "guardiao",
            "educador": "educador",
        }

        workflow.add_edge(START, "orquestrador_planejar")
        workflow.add_conditional_edges("orquestrador_planejar", rotear_apos_planejamento, mapa_destinos)

        for esp in _ORDEM_ESPECIALISTAS_DOMINIO:
            workflow.add_conditional_edges(esp, _criar_roteador_pos_especialista(esp), mapa_destinos)

        workflow.add_edge("educador", "orquestrador_sintetizar")
        workflow.add_edge("orquestrador_sintetizar", "compliance")
        workflow.add_conditional_edges(
            "compliance",
            rotear_pos_compliance,
            {
                "preparar_revisao": "preparar_revisao",
                "fail_closed": "fail_closed",
                END: END,
            },
        )
        workflow.add_edge("preparar_revisao", "orquestrador_sintetizar")
        workflow.add_edge("fail_closed", END)

        return workflow

    def _preparar_llm_execucao(self, llm: str | None) -> tuple[BaseChatModel | None, str, str]:
        """Resolve ChatOllama / ChatAnthropic para a execução do grafo."""
        if not llm or llm.strip().lower() in {"offline", "deterministico", "none"}:
            return None, "offline", "deterministico"

        # Se um Gateway customizado/mock foi injetado explicitamente no construtor
        if self.gateway is not None and type(self.gateway) is not Gateway:
            return None, llm, "hibrido_llm"

        info = resolver_config_modelo(llm)
        if info is None:
            return None, "offline", "deterministico"

        if info.get("provedor") == "ollama" and not ollama_disponivel():
            logger.info("Daemon Ollama indisponível em localhost:11434; rodando nós em fallback determinístico.")
            return None, "offline", "deterministico"

        chat_model, modelo_id = construir_chat_model(llm)
        return chat_model, modelo_id, "langgraph_llm"

    def executar(
        self,
        consulta: str,
        persona_id: str | None = None,
        documento_ocr: str | None = None,
        linha_digitavel: str | None = None,
        banco_alegado: str | None = None,
        beneficiario_pf: bool = False,
        llm: str | None = None,
        chat_model: BaseChatModel | None = None,
    ) -> ResultadoMultiagente:
        """Executa o StateGraph compilado do LangGraph e devolve ResultadoMultiagente auditável."""
        t0 = time.perf_counter()

        if chat_model is not None:
            self._chat_model_atual = chat_model
            self._modelo_id_atual = llm or getattr(chat_model, "model", MODELO_PADRAO_AGENTES)
            modo: Any = "langgraph_llm"
        else:
            self._chat_model_atual, self._modelo_id_atual, modo = self._preparar_llm_execucao(llm)

        if self._modelo_id_atual == "offline":
            self._gateway_atual = None
            self._llm_chave_atual = None
        else:
            self._gateway_atual = self.gateway if llm else None
            self._llm_chave_atual = llm
            if self._gateway_atual is not None and llm and modo == "deterministico":
                modo = "hibrido_llm"

        estado_inicial = EstadoMultiagente(
            persona_id=persona_id,
            consulta_usuario=consulta,
            documento_ocr=documento_ocr,
            linha_digitavel=linha_digitavel,
            banco_alegado=banco_alegado,
            beneficiario_pf=beneficiario_pf,
            modo=modo,
            modelo_llm=self._modelo_id_atual,
        )

        resultado_raw = self.compiled_graph.invoke(estado_inicial)
        if isinstance(resultado_raw, EstadoMultiagente):
            estado_final = resultado_raw
        else:
            estado_final = EstadoMultiagente.model_validate(resultado_raw)

        if estado_final.veredito is None or not estado_final.veredito.aprovado or not estado_final.resposta_final:
            estado_final.resposta_final = _resposta_segura_fail_closed(estado_final)

        return ResultadoMultiagente.de_estado(estado_final, latencia_s=time.perf_counter() - t0)
