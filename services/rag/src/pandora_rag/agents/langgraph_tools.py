"""Ferramentas (@tool) nativas do LangChain/LangGraph para os 7 agentes do PANDORA."""
from __future__ import annotations

import re
from typing import Any

from langchain_core.tools import BaseTool, tool

from pandora_rag.agents.models import (
    AnaliseCompulsao,
    CitacaoAgente,
    DiagnosticoFinanceiro,
    DividaItem,
    EvidenciaNormativa,
    InspecaoFraude,
    PlanoReestruturacao,
    ResultadoPercepcaoMultimodal,
    TransacaoPersona,
)
from pandora_rag.agents.tools import (
    _normalizar_texto,
    analisar_compulsao_bets,
    calcular_raio_x,
    carregar_transacoes_persona,
    detectar_inducao_cvm,
    detectar_sinais_crise,
    inspecionar_fraudes,
    simular_estrategias_divida,
)
from pandora_rag.generate.pii import mascarar
from pandora_rag.index.tokenizer import tokenizar
from pandora_rag.retrieve.hybrid import Hit, Retriever

_MIN_SCORE_VETOR_DENSO = 0.50
_MIN_SCORE_VETOR_HASH = 0.25
_MIN_SCORE_BM25_HASH = 1.5
_DIM_EMBEDDER_DENSO = 512

# Vocabulário normativo/financeiro em português para bloquear falsos positivos fora de domínio
# no portão RNF04 sem reranker (ex.: stemmer RSLP casando 'acordar' com 'acordo' ou texto em inglês).
_TERMOS_DOMINIO_PANDORA = frozenset(
    {
        "divida",
        "dividas",
        "superendividamento",
        "superendividado",
        "minimo",
        "existencial",
        "rotativo",
        "cartao",
        "cartoes",
        "fatura",
        "credito",
        "juros",
        "cet",
        "parcelamento",
        "parcela",
        "consignado",
        "emprestimo",
        "financiamento",
        "banco",
        "bancos",
        "bacen",
        "bcb",
        "pix",
        "med",
        "devolucao",
        "fraude",
        "golpe",
        "boleto",
        "febraban",
        "aposta",
        "apostas",
        "bet",
        "bets",
        "cvm",
        "consultoria",
        "suitability",
        "reserva",
        "emergencia",
        "selic",
        "cdi",
        "ipca",
        "orcamento",
        "salario",
        "salarios",
        "impenhoravel",
        "impenhoraveis",
        "impenhorabilidade",
        "penhora",
        "procon",
        "defensoria",
        "cdc",
        "cpc",
        "consumidor",
        "repactuacao",
        "conciliacao",
        "desenrola",
        "inadimplencia",
        "inadimplente",
        "serasa",
        "spc",
        "fgc",
        "tesouro",
        "poupanca",
        "cdb",
        "lci",
        "lca",
        "corretora",
        "investimento",
        "investimentos",
        "tarifa",
        "tarifas",
        "alienacao",
        "fiduciaria",
        "inss",
        "aposentadoria",
        "lei",
        "resolucao",
        "decreto",
        "sumula",
        "14181",
        "14690",
        "14790",
        "147",
        "833",
        "8078",
        "8009",
        "14015",
        "9514",
        "911",
        "11150",
        "11567",
        "5112",
        "5057",
        "4881",
        "4882",
        "4558",
        "19",
        "20",
        "30",
    }
)

_RE_CLAUSULA_VAZIA = re.compile(
    r"^(?:art\.?\s*\d+[a-z\-]*\.?\s*)?(?:ficam\s+revogad[oa]s|revoga[m\-]se|esta\s+lei\s+entra\s+em\s+vigor)\b",
    re.IGNORECASE,
)


@tool
def tool_classificar_roteamento(
    intencoes: list[str],
    agentes_especialistas: list[str],
    sinal_crise: bool = False,
    inducao_cvm: bool = False,
    justificativa_roteamento: str = "",
) -> dict[str, Any]:
    """Classifica as intenções da consulta financeira e define quais agentes especialistas devem atuar.

    Args:
        intencoes: Lista de intenções detectadas entre ['dividas', 'bets', 'fraude', 'cvm', 'crise', 'educacao'].
        agentes_especialistas: Lista ordenada de especialistas a acionar entre ['analista', 'estrategista', 'coach', 'guardiao', 'educador', 'compliance'].
        sinal_crise: True se a mensagem contém sofrimento psíquico agudo ou desespero financeiro extremo.
        inducao_cvm: True se o usuário pede recomendação específica de ação, fundo, cripto ou CDB de banco.
        justificativa_roteamento: Breve explicação técnica do plano de roteamento escolhido.
    """
    intencoes_validas = {
        i.strip().lower()
        for i in intencoes
        if i.strip().lower() in {"dividas", "bets", "fraude", "cvm", "crise", "educacao"}
    }
    if sinal_crise:
        intencoes_validas.add("crise")
    if inducao_cvm:
        intencoes_validas.add("cvm")
    if not intencoes_validas:
        intencoes_validas.add("educacao")

    agentes_validos = [
        a.strip().lower()
        for a in agentes_especialistas
        if a.strip().lower() in {"analista", "estrategista", "coach", "guardiao", "educador", "compliance"}
    ]
    return {
        "intencoes": sorted(intencoes_validas),
        "agentes_especialistas": agentes_validos,
        "sinal_crise": bool(sinal_crise),
        "inducao_cvm": bool(inducao_cvm),
        "justificativa_roteamento": justificativa_roteamento.strip(),
    }


def criar_tool_analista(
    persona_id: str,
    transacoes: list[TransacaoPersona],
) -> BaseTool:
    """Cria a @tool vinculada ao contexto de transações da persona para o AnalistaAgent."""

    @tool
    def tool_calcular_raio_x_financeiro(
        foco_analise: str = "orcamento_e_minimo_existencial",
        query_normativa_sugerida: str = "",
    ) -> dict[str, Any]:
        """Calcula o Raio-X financeiro determinístico (renda mensal, mínimo existencial, folga real e comparativo SGS do Banco Central).

        Args:
            foco_analise: Foco principal identificado pelo Analista (ex.: 'superendividamento', 'reserva_emergencia', 'apostas', 'protecao_patrimonial').
            query_normativa_sugerida: Consulta jurídica ou regulatória sugerida pelo Analista para o Educador pesquisar no RAG.
        """
        txs = list(transacoes)
        if persona_id and persona_id != "visitante" and not txs:
            try:
                txs = carregar_transacoes_persona(persona_id)
            except FileNotFoundError:
                txs = []
        diag: DiagnosticoFinanceiro = calcular_raio_x(persona_id or "visitante", txs)
        return {
            "diagnostico": diag,
            "transacoes": txs,
            "foco_analise": foco_analise,
            "query_normativa_sugerida": query_normativa_sugerida.strip(),
        }

    return tool_calcular_raio_x_financeiro


def criar_tool_estrategista(
    diagnostico: DiagnosticoFinanceiro,
    dividas: list[DividaItem],
) -> BaseTool:
    """Cria a @tool vinculada ao diagnóstico financeiro para o EstrategistaAgent."""

    @tool
    def tool_simular_reestruturacao_dividas(
        queries_normativas: list[str],
        recomendacao_abertura: str = "",
    ) -> dict[str, Any]:
        """Simula a priorização de dívidas (Método Avalanche vs. Bola de Neve) blindando 100% do Mínimo Existencial e verificando o teto do rotativo (Lei 14.690/2023).

        Args:
            queries_normativas: Lista de queries jurídicas que o Estrategista solicita ao Educador (ex.: Lei 14.181/2021, Lei 14.690/2023, CPC art. 833).
            recomendacao_abertura: Parecer prático do Estrategista explicando por que priorizar serviços essenciais e qual método economiza mais juros.
        """
        plano: PlanoReestruturacao = simular_estrategias_divida(diagnostico, dividas)
        queries_limpas = [mascarar(q.strip())[0] for q in queries_normativas if q and q.strip()]
        return {
            "plano": plano,
            "queries_normativas": queries_limpas,
            "recomendacao_abertura": recomendacao_abertura.strip(),
        }

    return tool_simular_reestruturacao_dividas


def criar_tool_coach(
    transacoes: list[TransacaoPersona],
    renda_mensal: float,
    parcela_referencia: float | None = 450.0,
) -> BaseTool:
    """Cria a @tool vinculada às transações da persona para o CoachAgent."""

    @tool
    def tool_analisar_compulsao_apostas(
        queries_normativas: list[str],
        mensagem_acolhimento_sem_julgamento: str = "",
    ) -> dict[str, Any]:
        """Apura a perda líquida real em apostas (MCC 7995), apostas de madrugada (23h–06h), gatilho pós-salário e custo de oportunidade.

        Args:
            queries_normativas: Queries regulatórias sobre apostas de quota fixa, jogo responsável e bloqueios de proteção.
            mensagem_acolhimento_sem_julgamento: Orientação empática e sem julgamento moral propondo pausa noturna e pausa de 48h.
        """
        analise: AnaliseCompulsao = analisar_compulsao_bets(
            transacoes,
            renda_mensal=renda_mensal,
            parcela_referencia=parcela_referencia,
        )
        queries_limpas = [mascarar(q.strip())[0] for q in queries_normativas if q and q.strip()]
        return {
            "analise": analise,
            "queries_normativas": queries_limpas,
            "mensagem_acolhimento_sem_julgamento": mensagem_acolhimento_sem_julgamento.strip(),
        }

    return tool_analisar_compulsao_apostas


def criar_tool_guardiao(
    transacoes: list[TransacaoPersona],
    documento_ocr: str | None,
    linha_digitavel: str | None,
    banco_alegado: str | None,
    beneficiario_pf: bool,
    percepcao: ResultadoPercepcaoMultimodal | None = None,
) -> BaseTool:
    """Cria a @tool vinculada aos artefatos suspeitos e à percepção multimodal para o GuardiaoAgent."""

    @tool
    def tool_inspecionar_fraude_e_boleto(
        queries_normativas: list[str],
        orientacao_emergencial: str = "",
    ) -> dict[str, Any]:
        """Sanitiza documentos externos contra Prompt Injection, valida linha digitável FEBRABAN (Módulo 10/11) e QR Pix (CRC-16) e gera roteiro do MED Pix (Res. BCB 147/2021).

        Args:
            queries_normativas: Queries regulatórias sobre fraude bancária, MED do Pix (Resolução BCB 147/2021) e segurança.
            orientacao_emergencial: Alerta direto e acessível orientando a não pagar boleto fraudulento e como acionar o MED em até 80 dias.
        """
        inspecao: InspecaoFraude = inspecionar_fraudes(
            transacoes,
            documento_ocr=documento_ocr,
            linha_digitavel=linha_digitavel,
            banco_alegado=banco_alegado,
            beneficiario_pf=beneficiario_pf,
            percepcao=percepcao,
        )
        queries_limpas = [mascarar(q.strip())[0] for q in queries_normativas if q and q.strip()]
        return {
            "inspecao": inspecao,
            "queries_normativas": queries_limpas,
            "orientacao_emergencial": orientacao_emergencial.strip(),
        }

    return tool_inspecionar_fraude_e_boleto


def _query_no_dominio_pandora(query: str) -> bool:
    """Verifica se a consulta livre contém ao menos um termo real do domínio financeiro/jurídico em português."""
    palavras = set(re.findall(r"[a-z0-9]+", _normalizar_texto(query)))
    return bool(palavras & _TERMOS_DOMINIO_PANDORA)


def _eh_chunk_cabecalho_ou_revogacao(hit: Hit) -> bool:
    """Filtra preâmbulos, títulos sem conteúdo, promulgações de veto e cláusulas revogatórias."""
    rid = (hit.registro.id or "").lower()
    if "#preambulo" in rid:
        return True
    txt = (hit.registro.texto or "").strip()
    if len(txt) < 55:
        return True
    norm = _normalizar_texto(txt)
    if norm.endswith("passa a vigorar com as seguintes alteracoes:") and len(txt) < 180:
        return True
    if "faco saber que o congresso nacional decreta" in norm:
        return True
    if "clausula del credere" in norm:
        return True
    return bool(_RE_CLAUSULA_VAZIA.match(norm))


def _hit_relevante_rag(
    hit: Hit,
    limiar_abstencao: float,
    embedder_dim: int = 0,
    query: str | None = None,
) -> bool:
    if hit.score_rerank is not None:
        return hit.score_rerank >= limiar_abstencao
    if embedder_dim >= _DIM_EMBEDDER_DENSO:
        return hit.score_vetor is not None and hit.score_vetor >= _MIN_SCORE_VETOR_DENSO
    vetor_ok = hit.score_vetor is not None and hit.score_vetor >= _MIN_SCORE_VETOR_HASH
    bm25_ok = hit.score_bm25 is not None and hit.score_bm25 >= _MIN_SCORE_BM25_HASH
    if not (vetor_ok and bm25_ok):
        return False
    if query:
        toks_q = set(tokenizar(query))
        toks_doc = set(tokenizar(hit.registro.texto_indexado()))
        if not (toks_q & toks_doc):
            return False
    return True


def executar_busca_evidencias_rag(
    queries_brutas: list[str],
    retriever: Retriever,
    k: int = 3,
    limiar_abstencao: float = 0.02,
    consulta_livre: bool = False,
) -> EvidenciaNormativa:
    """Executa a busca híbrida (bge-m3 + BM25 + RRF) e aplica o portão de abstenção RNF04."""
    queries: list[str] = []
    for q in queries_brutas:
        q_limpa, _ = mascarar(q.strip())
        if q_limpa and q_limpa not in queries:
            queries.append(q_limpa)
    queries = queries[:6]

    if consulta_livre and not any(_query_no_dominio_pandora(q) for q in queries):
        return EvidenciaNormativa(
            queries_executadas=queries,
            hits_aprovados=0,
            abstencao=True,
            citacoes=[],
            motivo_abstencao="Consulta fora do domínio financeiro/normativo oficial do PANDORA.",
        )

    embedder_dim = int(getattr(retriever.embedder, "dim", 0) or 0)
    k_busca = max(k * 3, 10)
    hits_por_id: dict[str, Hit] = {}
    hits_por_query: list[Hit] = []
    for q in queries:
        candidatos_q = [
            h
            for h in retriever.buscar(q, k=k_busca)
            if _hit_relevante_rag(h, limiar_abstencao, embedder_dim, query=q)
        ]
        substantivos_q = [h for h in candidatos_q if not _eh_chunk_cabecalho_ou_revogacao(h)]
        resultados_q = substantivos_q if substantivos_q else candidatos_q
        for h in resultados_q[:1]:
            if h.registro.id not in hits_por_id:
                hits_por_id[h.registro.id] = h
                hits_por_query.append(h)
        for h in resultados_q[1:]:
            if h.registro.id not in hits_por_id:
                hits_por_id[h.registro.id] = h

    limite = min(max(k, 3), 4)
    if len(hits_por_query) >= limite:
        hits_ordenados = hits_por_query[:limite]
    else:
        faltam = limite - len(hits_por_query)
        restantes = sorted(
            (h for rid, h in hits_por_id.items() if all(x.registro.id != rid for x in hits_por_query)),
            key=lambda h: h.score,
            reverse=True,
        )
        hits_ordenados = hits_por_query + restantes[:faltam]

    citacoes = [
        CitacaoAgente(
            n=idx,
            norma=h.registro.norma,
            artigo=h.registro.artigo,
            link=h.registro.link,
            trecho=mascarar(h.registro.texto[:400])[0],
            pagina=h.registro.pagina,
            ressalva=h.registro.ressalva,
            score=round(h.score, 4),
        )
        for idx, h in enumerate(hits_ordenados, start=1)
    ]
    abstencao = len(citacoes) == 0
    return EvidenciaNormativa(
        queries_executadas=queries,
        hits_aprovados=len(citacoes),
        abstencao=abstencao,
        citacoes=citacoes,
        motivo_abstencao="Nenhum chunk atingiu o limiar mínimo de evidência." if abstencao else None,
    )


def criar_tool_educador(
    retriever: Retriever,
    queries_acumuladas: list[str],
    consulta_mascarada: str,
    intencoes: list[str],
    k: int = 3,
    limiar_abstencao: float = 0.02,
) -> BaseTool:
    """Cria a @tool de busca híbrida RAG para o EducadorAgent (Research Agent)."""

    @tool
    def tool_buscar_evidencias_rag(
        queries_pesquisa: list[str],
    ) -> dict[str, Any]:
        """Recupera artigos de leis, resoluções do Banco Central/CVM e cartilhas oficiais no índice RAG híbrido (bge-m3 + BM25 + RRF).

        Args:
            queries_pesquisa: Lista de consultas técnicas ou jurídicas formuladas para buscar no corpus oficial.
        """
        combinadas: list[str] = list(queries_acumuladas)
        # Se há queries vindas dos especialistas financeiros ou de CVM, adiciona as queries do LLM;
        # se é consulta avulsa sem especialistas, preserva a consulta original para não furar o portão RNF04 fora de domínio.
        tem_contexto_cvm = detectar_inducao_cvm(consulta_mascarada) or "cvm" in intencoes
        if tem_contexto_cvm:
            q_cvm = "Resolucao CVM 19 20 consultoria valores mobiliarios suitability 30"
            if q_cvm not in combinadas:
                combinadas.insert(0, q_cvm)

        tem_contexto_financeiro = bool(queries_acumuladas) or any(
            i in intencoes for i in ("dividas", "bets", "fraude", "cvm", "crise")
        )
        if tem_contexto_financeiro and "crise" not in intencoes:
            for q in queries_pesquisa:
                if q and q.strip() and q.strip() not in combinadas:
                    combinadas.append(q.strip())

        consulta_livre = not combinadas and not tem_contexto_cvm
        if not combinadas:
            combinadas.append(consulta_mascarada)

        ev = executar_busca_evidencias_rag(
            combinadas,
            retriever=retriever,
            k=k,
            limiar_abstencao=limiar_abstencao,
            consulta_livre=consulta_livre,
        )
        return {"evidencias": ev}

    return tool_buscar_evidencias_rag


@tool
def tool_auditar_invariantes_compliance(
    aprovado_semantico: bool,
    contem_recomendacao_implicita_cvm: bool = False,
    contem_julgamento_moral: bool = False,
    observacao_auditoria: str = "",
) -> dict[str, Any]:
    """Registra o veredito semântico do ComplianceAgent (LLM-as-a-Judge) em conjunto com os 4 invariantes regulatórios duros (RNF01–RNF05).

    Args:
        aprovado_semantico: True se o rascunho respeita as normas éticas, regulatórias e o tom acolhedor.
        contem_recomendacao_implicita_cvm: True se o texto sugere comprar um ativo, ação, cripto ou CDB específico.
        contem_julgamento_moral: True se o texto usa linguagem punitiva, culpabilizante ou estigmatizante.
        observacao_auditoria: Parecer técnico curto do auditor de compliance.
    """
    return {
        "aprovado_semantico": bool(aprovado_semantico),
        "contem_recomendacao_implicita_cvm": bool(contem_recomendacao_implicita_cvm),
        "contem_julgamento_moral": bool(contem_julgamento_moral),
        "observacao_auditoria": observacao_auditoria.strip(),
    }


__all__ = [
    "criar_tool_analista",
    "criar_tool_coach",
    "criar_tool_educador",
    "criar_tool_estrategista",
    "criar_tool_guardiao",
    "detectar_inducao_cvm",
    "detectar_sinais_crise",
    "executar_busca_evidencias_rag",
    "tool_auditar_invariantes_compliance",
    "tool_classificar_roteamento",
]
