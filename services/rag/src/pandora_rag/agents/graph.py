"""Grafo de orquestração multiagente do PANDORA e construtor de retriever com fallback."""
from __future__ import annotations

import logging
import time
import zlib

import numpy as np

from pandora_rag.agents.models import EstadoMultiagente, ResultadoMultiagente
from pandora_rag.agents.specialists import (
    AnalistaAgent,
    CoachAgent,
    ComplianceAgent,
    EducadorAgent,
    EstrategistaAgent,
    GuardiaoAgent,
    OrquestradorAgent,
)
from pandora_rag.config import DB_URL, TEXT_DIR
from pandora_rag.generate.gateway import Gateway
from pandora_rag.index.registro import Registro, montar_registros
from pandora_rag.index.store import MemoryStore, PgVectorStore
from pandora_rag.index.tokenizer import tokenizar
from pandora_rag.retrieve.hybrid import IndiceBM25, Parametros, Reranker, Retriever

logger = logging.getLogger(__name__)


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
            from pandora_rag.index.embedder import Embedder

            emb = Embedder(modelo_embedding)
            pg = PgVectorStore(DB_URL, tabela, emb.dim)
            regs = pg.carregar_registros()
            if regs:
                rer = Reranker() if usar_reranker else None
                return Retriever(pg, IndiceBM25(regs), emb, rer), "pgvector"
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            logger.info("Postgres indisponível para agentes; tentando índice local em memória: %s", exc)

        if TEXT_DIR.exists() and any(TEXT_DIR.iterdir()):
            try:
                regs = montar_registros("estrutural", texto_dir=TEXT_DIR)
                if regs:
                    emb_hash = EmbedderHash()
                    store = MemoryStore(regs, emb_hash.passagens([r.texto_indexado() for r in regs]))
                    rer = Reranker() if usar_reranker else None
                    return Retriever(store, IndiceBM25(regs), emb_hash, rer), "corpus_local_bm25_hash"
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                logger.info("Falha ao carregar corpus local extraído; usando embutido: %s", exc)

    regs_emb = corpus_embutido_oficial()
    emb_hash = EmbedderHash()
    store_emb = MemoryStore(regs_emb, emb_hash.passagens([r.texto_indexado() for r in regs_emb]))
    return Retriever(store_emb, IndiceBM25(regs_emb), emb_hash, None, Parametros()), "corpus_embutido_oficial"


class GrafoPandora:
    """Máquina de estados que coordena os 7 agentes especializados do PANDORA."""

    def __init__(
        self,
        retriever: Retriever | None = None,
        gateway: Gateway | None = None,
        k_evidencias: int = 3,
        limiar_abstencao: float = 0.02,
    ):
        if retriever is None:
            retriever, origem = construir_retriever_padrao(usar_reranker=False, preferir_embutido=False)
            self.origem_retriever = origem
        else:
            self.origem_retriever = "retriever_injetado"
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

    def executar(
        self,
        consulta: str,
        persona_id: str | None = None,
        documento_ocr: str | None = None,
        linha_digitavel: str | None = None,
        banco_alegado: str | None = None,
        beneficiario_pf: bool = False,
        llm: str | None = None,
    ) -> ResultadoMultiagente:
        """Executa o fluxo completo multiagente e devolve ResultadoMultiagente auditável."""
        t0 = time.perf_counter()
        gw = self.gateway if llm else None
        modo = "hibrido_llm" if (gw is not None and llm) else "deterministico"

        estado = EstadoMultiagente(
            persona_id=persona_id,
            consulta_usuario=consulta,
            documento_ocr=documento_ocr,
            linha_digitavel=linha_digitavel,
            banco_alegado=banco_alegado,
            beneficiario_pf=beneficiario_pf,
            modo=modo,
        )

        estado = self.orquestrador.planejar(estado)

        if "analista" in estado.agentes_planejados:
            estado = self.analista.executar(estado)
        if "estrategista" in estado.agentes_planejados:
            estado = self.estrategista.executar(estado)
        if "coach" in estado.agentes_planejados:
            estado = self.coach.executar(estado)
        if "guardiao" in estado.agentes_planejados:
            estado = self.guardiao.executar(estado)

        estado = self.educador.executar(
            estado,
            self.retriever,
            k=self.k_evidencias,
            limiar_abstencao=self.limiar_abstencao,
        )
        estado = self.orquestrador.sintetizar(estado, gateway=gw, modelo=llm, modo_revisao=False)
        estado = self.compliance.validar(estado)

        if estado.veredito is not None and not estado.veredito.aprovado:
            estado.revisoes_realizadas += 1
            estado = self.orquestrador.sintetizar(estado, gateway=None, modelo=None, modo_revisao=True)
            estado = self.compliance.validar(estado)

        if not estado.resposta_final:
            estado.resposta_final = estado.rascunho_resposta

        return ResultadoMultiagente.de_estado(estado, latencia_s=time.perf_counter() - t0)
