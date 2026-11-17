"""Implementação dos 7 agentes especializados colaborativos do PANDORA."""
from __future__ import annotations

import logging
import re

import anthropic
import httpx

from pandora_rag.agents.models import (
    AgentRole,
    CitacaoAgente,
    DividaItem,
    EstadoMultiagente,
    EvidenciaNormativa,
    VereditoCompliance,
)
from pandora_rag.agents.tools import (
    SERIES_SGS_BCB,
    _normalizar_texto,
    analisar_compulsao_bets,
    calcular_raio_x,
    carregar_transacoes_persona,
    detectar_inducao_cvm,
    detectar_sinais_crise,
    inspecionar_fraudes,
    perfil_persona,
    simular_estrategias_divida,
)
from pandora_rag.generate.answer import MENSAGEM_ABSTENCAO, RE_CITACAO
from pandora_rag.generate.gateway import Gateway, OrcamentoExcedido
from pandora_rag.generate.pii import mascarar
from pandora_rag.retrieve.hybrid import Hit, Retriever

logger = logging.getLogger(__name__)

_RE_RECOMENDACAO_DIRETA_CVM = re.compile(
    r"\b(?:compre|invista|aplique|escolha|recomendo|sugiro|indico|vale\s+a\s+pena\s+(?:comprar|aplicar|investir))"
    r"(?:\s+(?:em|um|uma|o|a|no|na|os|as)){0,3}\s+"
    r"(?:cdb|acao|acoes|fundo|fiis?|etf|bdr|cripto\w*|bitcoin|[a-z]{4}(?:3|4|5|6|11|34|35|39)|banco\s+\w+|itau|nubank|bradesco|santander)\b"
)

_MIN_SCORE_BM25_SEM_RERANK = 2.5
_MIN_SCORE_VETOR_SEM_RERANK = 0.45

BLOCO_PROTOCOLO_CRISE = (
    "APOIO IMEDIATO E CONFIDENCIAL (PROTOCOLO DE CRISE):\n"
    "- Você não precisa enfrentar isso sozinho(a). Pause agora as decisões financeiras e fale com apoio especializado gratuito:\n"
    "- CVV (Centro de Valorização da Vida): ligue 188 (24h, gratuito e sigiloso) ou acesse cvv.org.br.\n"
    "- CAPS AD (SUS): atendimento presencial gratuito para compulsão e saúde mental.\n"
    "- Jogadores Anônimos (JA): grupos de apoio mútuo em jogadoresanonimos.com.br."
)


def bloco_recusa_educativa_cvm(perfil: dict | None = None) -> str:
    """Bloco determinístico de Recusa Educativa conforme Resoluções CVM 19 e 20/2021."""
    selic = SERIES_SGS_BCB["432"]["valor_referencia"]
    cdi = SERIES_SGS_BCB["12"]["valor_referencia"]
    ipca = SERIES_SGS_BCB["433"]["valor_referencia"]
    linhas = [
        "EDUCAÇÃO FINANCEIRA SOB CONFORMIDADE CVM (RECUSA EDUCATIVA):",
        "- Pelas regras da CVM (Resoluções CVM 19 e 20/2021), eu sou um copiloto educacional e não faço recomendação específica de ação, fundo ou CDB de um banco determinado.",
        "- Em vez de indicar um produto único, use estes 3 critérios objetivos para avaliar qualquer opção de Reserva de Emergência com segurança:",
        "  1. Liquidez Diária (D+0): poder resgatar no mesmo dia se surgir um imprevisto.",
        "  2. Baixo Risco de Crédito: títulos públicos federais (Tesouro Nacional) ou instituições cobertas pelo FGC (até R$ 250 mil por CPF/instituição).",
        f"  3. Rendimento Pós-Fixado: acompanhar 100% da Selic ({selic:.2f}% a.a.) ou do CDI ({cdi:.2f}% a.a.) para superar a inflação (IPCA {ipca:.2f}% a.m.) sem risco de marcação a mercado.",
    ]
    if perfil:
        meta_6m = perfil.get("meta_reserva_6_meses", 0.0)
        poupanca = perfil.get("capacidade_poupanca", 0.0)
        if meta_6m > 0 and poupanca > 0:
            linhas.append(
                f"- Sua escada da reserva: poupando {_formatar_brl(poupanca)}/mês, sua meta de 6 meses de tranquilidade é {_formatar_brl(meta_6m)}."
            )
    return "\n".join(linhas)


def _formatar_brl(valor: float) -> str:
    inteiro, dec = f"{valor:,.2f}".split(".")
    return f"R$ {inteiro.replace(',', '.')},{dec}"


def _proximo_agente(estado: EstadoMultiagente, atual: AgentRole) -> AgentRole:
    """Resolve o próximo agente planejado em sequência após o nó atual."""
    if atual in estado.agentes_planejados:
        idx = estado.agentes_planejados.index(atual)
        if idx + 1 < len(estado.agentes_planejados):
            return estado.agentes_planejados[idx + 1]
    return "educador"


def _classificar_intencoes(estado: EstadoMultiagente, texto_limpo: str) -> list[str]:
    norm = _normalizar_texto(texto_limpo)
    intencoes: list[str] = []

    if any(
        kw in norm
        for kw in (
            "divida",
            "rotativo",
            "cartao",
            "fatura",
            "emprestimo",
            "consignado",
            "atrasad",
            "superendividamento",
            "priorizar",
            "pagar primeiro",
            "juros",
            "luz",
        )
    ):
        intencoes.append("dividas")

    if any(
        kw in norm
        for kw in ("aposta", "bet", "cassino", "jogo", "madrugada", "repasse")
    ):
        intencoes.append("bets")

    if (
        estado.documento_ocr
        or estado.linha_digitavel
        or any(
            kw in norm
            for kw in ("golpe", "fraude", "boleto", "falsa central", "med", "pix")
        )
    ):
        intencoes.append("fraude")

    if detectar_inducao_cvm(texto_limpo):
        intencoes.append("cvm")

    if detectar_sinais_crise(texto_limpo):
        intencoes.append("crise")

    if any(
        kw in norm
        for kw in (
            "lei",
            "direito",
            "reserva",
            "selic",
            "cdi",
            "ipca",
            "invest",
            "educa",
            "cvm",
            "tesouro",
            "cdb",
            "poupanca",
        )
    ) or not intencoes:
        intencoes.append("educacao")

    return intencoes


def _saudacao_por_tom(nome: str, tom: str) -> str:
    if tom == "acessivel_idoso":
        return f"Olá, {nome}. Analisei com calma e cuidado o que você enviou para proteger seu dinheiro:"
    if tom == "parceiro_sem_julgamento":
        return f"{nome}, aqui não há julgamento — vamos olhar juntos os números reais e proteger seu trabalho:"
    return f"Olá, {nome}. Organizei sua situação passo a passo com base nos seus dados e nas normas oficiais:"


def _montar_blocos_sintese(
    estado: EstadoMultiagente,
    perfil: dict,
    cvm_ativo: bool,
) -> list[str]:
    """Monta os blocos determinísticos com numeração sequencial consistente."""
    secoes: list[tuple[str, str]] = []

    if estado.diagnostico is not None:
        d = estado.diagnostico
        linhas_diag = [
            f"- Renda apurada no recorte: {_formatar_brl(d.renda_mensal)}",
            f"- Mínimo Existencial (moradia, alimentação e itens vitais): {_formatar_brl(d.minimo_existencial)}",
            f"- Folga real disponível após despesas vitais: {_formatar_brl(d.folga_disponivel)}",
        ]
        if "22022" in d.comparativos_sgs:
            comp = d.comparativos_sgs["22022"]
            linhas_diag.append(
                f"- Comparativo Banco Central (SGS 22022): seu rotativo está em {comp['cet_usuario_pct_aa']:.1f}% a.a. "
                f"contra a média oficial de {comp['media_bcb_pct_aa']:.1f}% a.a."
            )
        secoes.append(("RAIO-X DO ORÇAMENTO", "\n".join(linhas_diag)))

    if estado.plano_dividas is not None:
        p = estado.plano_dividas
        linhas_plano = [
            f"- Valor intocável para família/casa: {_formatar_brl(p.minimo_existencial_blindado)}",
            f"- Folga mensal segura para acordos: {_formatar_brl(p.folga_para_acordos)}",
            f"- Ordem recomendada (Método Avalanche — maior juro primeiro): {' -> '.join(p.avalanche.ordem_credores)}",
            f"- Alternativa Bola de Neve (menor saldo): {' -> '.join(p.bola_de_neve.ordem_credores)}",
        ]
        if p.economia_estimada_juros > 0:
            linhas_plano.append(
                f"- Economia estimada em juros em 12 meses no Avalanche: {_formatar_brl(p.economia_estimada_juros)}"
            )
        if p.alerta_teto_rotativo_lei_14690:
            linhas_plano.append(
                "- Proteção contra juros abusivos: verifique o teto legal de 100% sobre a dívida original do rotativo (Lei 14.690/2023)."
            )
        if p.requer_repactuacao_lei_14181:
            linhas_plano.append(
                "- Como as parcelas atuais ultrapassam sua folga, você tem direito à audiência de repactuação preservando o Mínimo Existencial (Lei 14.181/2021) via Procon ou Defensoria Pública."
            )
        secoes.append(("PRIORIDADE DE PAGAMENTOS (MÍNIMO EXISTENCIAL BLINDADO)", "\n".join(linhas_plano)))

    if estado.analise_compulsao is not None:
        c = estado.analise_compulsao
        linhas_bets = [
            f"- Total enviado para apostas no recorte: {_formatar_brl(c.total_apostado)} (prêmios recebidos: {_formatar_brl(c.premios_recebidos)})",
            f"- Perda líquida real: {_formatar_brl(c.perda_liquida)} ({c.pct_renda_comprometida:.1f}% do repasse/renda analisada)",
            f"- Concentração de risco: {c.aposta_madrugada_qtd} aposta(s) de madrugada (23h–06h); pós-repasse: {'sim' if c.aposta_pos_salario else 'não'}",
            f"- Impacto real no seu trabalho: {c.custo_oportunidade}",
            f"- Sugestão prática: ativar Pausa Noturna (22h–07h) e janela de resfriamento (cooling-off) de {c.sugestao_cooling_off_horas}h + autoexclusão nas plataformas .bet.br.",
        ]
        secoes.append(("RETRATO OBJETIVO DAS APOSTAS (SEM JULGAMENTO)", "\n".join(linhas_bets)))

    if estado.inspecao_fraude is not None:
        f = estado.inspecao_fraude
        linhas_fraude: list[str] = []
        if f.injection_detectada:
            linhas_fraude.append(
                "- Aviso técnico: o documento enviado continha texto oculto tentando manipular a análise, mas foi isolado e bloqueado com segurança."
            )
        if f.boleto is not None:
            if f.boleto.suspeito:
                linhas_fraude.append(
                    "- PARE! NÃO PAGUE ESTE BOLETO. Motivos detectados: "
                    + " | ".join(f.boleto.motivos)
                )
            else:
                linhas_fraude.append(
                    "- Linha digitável estruturalmente válida; ainda assim confirme o CNPJ recebedor no app do banco."
                )
        if f.roteiro_med_pix:
            linhas_fraude.append(
                "- Como tentar recuperar o Pix já enviado (MED — prazo legal de até 80 dias):"
            )
            linhas_fraude.extend(f"  {passo}" for passo in f.roteiro_med_pix)
        if linhas_fraude:
            secoes.append(("ALERTA DE SEGURANÇA E GOLPE (GUARDIÃO)", "\n".join(linhas_fraude)))

    if cvm_ativo:
        bloco_cvm = bloco_recusa_educativa_cvm(perfil)
        titulo_cvm, _, corpo_cvm = bloco_cvm.partition("\n")
        secoes.append((titulo_cvm.rstrip(":"), corpo_cvm))

    blocos_numerados = [f"{i}. {titulo}:\n{corpo}" for i, (titulo, corpo) in enumerate(secoes, start=1)]

    if estado.evidencias is not None:
        ev = estado.evidencias
        if ev.abstencao and not (cvm_ativo or estado.plano_dividas or estado.analise_compulsao or estado.inspecao_fraude):
            blocos_numerados.append(MENSAGEM_ABSTENCAO)
        elif ev.citacoes:
            linhas_ev: list[str] = []
            for c in ev.citacoes:
                art = f", {c.artigo}" if c.artigo else ""
                trecho_mascarado, _ = mascarar(c.trecho.strip().replace("\n", " ")[:180])
                linhas_ev.append(
                    f"- [{c.n}] {c.norma}{art}: {trecho_mascarado}... (Fonte: {c.link})"
                )
            blocos_numerados.append(
                f"{len(secoes) + 1}. BASE LEGAL E FONTES OFICIAIS CITADAS:\n" + "\n".join(linhas_ev)
            )

    return blocos_numerados


class OrquestradorAgent:
    """Agente 1: sanitiza PII, planeja o roteamento condicional e adapta a comunicação."""

    def planejar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        consulta_limpa, pii = mascarar(estado.consulta_usuario)
        estado.consulta_mascarada = consulta_limpa
        estado.pii_contagem = pii

        intencoes = _classificar_intencoes(estado, consulta_limpa)
        estado.intencoes_detectadas = intencoes

        planejados: list[AgentRole] = []
        if estado.persona_id:
            planejados.append("analista")
        if "dividas" in intencoes:
            planejados.append("estrategista")
        if "bets" in intencoes:
            planejados.append("coach")
        if "fraude" in intencoes:
            planejados.append("guardiao")
        planejados.extend(["educador", "compliance"])
        estado.agentes_planejados = planejados

        destino: AgentRole = planejados[0] if planejados else "educador"
        estado.registrar_mensagem(
            origem="orquestrador",
            destino=destino,
            tipo="roteamento",
            resumo=(
                f"Entrada sanitizada (PII mascarada: {sum(pii.values())}); "
                f"intenções={intencoes}; sequência={planejados}."
            ),
            dados_chave={
                "pii_contagem": pii,
                "intencoes": intencoes,
                "agentes_planejados": planejados,
            },
        )
        return estado

    def sintetizar(
        self,
        estado: EstadoMultiagente,
        gateway: Gateway | None = None,
        modelo: str | None = None,
        modo_revisao: bool = False,
    ) -> EstadoMultiagente:
        """Compila a resposta adaptada ao perfil com os dados determinísticos e citações."""
        perfil = perfil_persona(estado.persona_id) if estado.persona_id else perfil_persona("visitante")
        nome = perfil["nome"]
        tom = perfil["tom_comunicacao"]
        consulta_base = estado.consulta_mascarada or mascarar(estado.consulta_usuario)[0]

        crise_ativa = detectar_sinais_crise(consulta_base) or (
            estado.veredito is not None and estado.veredito.crise_acionada
        ) or (
            estado.analise_compulsao is not None
            and estado.analise_compulsao.risco_compulsao == "critico"
            and "crise" in estado.intencoes_detectadas
        )
        cvm_ativo = detectar_inducao_cvm(consulta_base) or (
            estado.veredito is not None and estado.veredito.bloqueio_cvm_acionado
        )

        secoes = _montar_blocos_sintese(estado, perfil, cvm_ativo=cvm_ativo)
        blocos: list[str] = [_saudacao_por_tom(nome, tom)]
        if crise_ativa:
            blocos.append(BLOCO_PROTOCOLO_CRISE)
        blocos.extend(secoes)
        rascunho = "\n\n".join(blocos)

        if gateway is not None and modelo and not modo_revisao and not crise_ativa:
            rascunho_externo = rascunho.replace(nome, "[USUARIO]")
            rascunho_externo, _ = mascarar(rascunho_externo)
            prompt_usuario = (
                "Reescreva de forma clara, acolhedora e concisa (até 220 palavras) mantendo TODOS os números em reais, "
                "percentuais, prazos, blocos de alerta (CVM / PARE NÃO PAGUE) e marcadores de citação [1], [2] exatamente como estão:\n\n"
                + rascunho_externo
            )
            try:
                comp = gateway.gerar(
                    modelo,
                    "Você é o Orquestrador/Elpis do PANDORA. Nunca invente números, não recomende ativos específicos e preserve todas as citações [n].",
                    prompt_usuario,
                    max_tokens=700,
                )
                if comp.texto.strip():
                    texto_llm = comp.texto.strip().replace("[USUARIO]", nome)
                    if cvm_ativo:
                        texto_llm = f"{texto_llm}\n\n{bloco_recusa_educativa_cvm(perfil)}"
                    rascunho = texto_llm
            except (httpx.HTTPError, anthropic.AnthropicError, OrcamentoExcedido, KeyError, RuntimeError, ValueError) as exc:
                logger.warning("Fallback determinístico na síntese do Orquestrador: %s", exc)

        rascunho, _ = mascarar(rascunho)
        estado.rascunho_resposta = rascunho
        estado.registrar_mensagem(
            origem="orquestrador",
            destino="compliance",
            tipo="revisao" if modo_revisao else "sintese",
            resumo=(
                "Revisão aplicada incorporando exigências do Compliance Guard."
                if modo_revisao
                else "Síntese adaptada ao perfil compilada para validação final."
            ),
            dados_chave={
                "tom_comunicacao": tom,
                "modo_revisao": modo_revisao,
                "tamanho_caracteres": len(rascunho),
            },
        )
        return estado


class AnalistaAgent:
    """Agente 2: extrai o Raio-X financeiro determinístico e compara taxas com o BCB SGS."""

    def executar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        if estado.persona_id and not estado.transacoes:
            try:
                estado.transacoes = carregar_transacoes_persona(estado.persona_id)
            except FileNotFoundError:
                estado.transacoes = []

        pid = estado.persona_id or "visitante"
        diag = calcular_raio_x(pid, estado.transacoes)
        estado.diagnostico = diag

        destino = _proximo_agente(estado, "analista")
        estado.registrar_mensagem(
            origem="analista",
            destino=destino,
            tipo="analise",
            resumo=(
                f"Raio-X calculado para {diag.persona_id}: renda={_formatar_brl(diag.renda_mensal)}, "
                f"mínimo existencial={_formatar_brl(diag.minimo_existencial)}, "
                f"folga={_formatar_brl(diag.folga_disponivel)}."
            ),
            dados_chave={
                "renda_mensal": diag.renda_mensal,
                "minimo_existencial": diag.minimo_existencial,
                "folga_disponivel": diag.folga_disponivel,
                "comprometimento_dividas_pct": diag.comprometimento_dividas_pct,
                "comparativos_sgs": list(diag.comparativos_sgs.keys()),
            },
        )
        return estado


class EstrategistaAgent:
    """Agente 3: blinda o Mínimo Existencial e simula Avalanche vs. Bola de Neve."""

    def executar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        if estado.diagnostico is None:
            estado = AnalistaAgent().executar(estado)
        diag = estado.diagnostico
        assert diag is not None

        dividas: list[DividaItem] = list(diag.dividas_identificadas)
        if not dividas and diag.gasto_dividas_mensal > 0:
            dividas = [
                DividaItem(
                    credor="Dívidas identificadas no extrato",
                    modalidade="rotativo_cartao",
                    saldo=diag.total_dividas,
                    cet_anual_pct=435.9,
                    parcela_mensal=diag.gasto_dividas_mensal,
                )
            ]

        plano = simular_estrategias_divida(diag, dividas)
        estado.plano_dividas = plano

        queries = [
            "Lei 14.181 minimo existencial repactuacao superendividamento",
            "Lei 14.690 teto juros rotativo cartao 100%",
            "CPC art 833 impenhorabilidade salario",
        ]
        for q in queries:
            if q not in estado.queries_normativas:
                estado.queries_normativas.append(q)

        destino = _proximo_agente(estado, "estrategista")
        estado.registrar_mensagem(
            origem="estrategista",
            destino=destino,
            tipo="solicitacao_pesquisa",
            resumo=(
                f"Plano Avalanche vs. Bola de Neve gerado blindando {_formatar_brl(plano.minimo_existencial_blindado)}; "
                f"solicitando fundamentação na Lei 14.181/2021, Lei 14.690/2023 e CPC art. 833."
            ),
            dados_chave={
                "ordem_avalanche": plano.avalanche.ordem_credores,
                "economia_juros": plano.economia_estimada_juros,
                "alerta_lei_14690": plano.alerta_teto_rotativo_lei_14690,
                "queries_solicitadas": queries,
            },
        )
        return estado


class CoachAgent:
    """Agente 4: detecta compulsão em bets, perda líquida real e propõe fricção positiva."""

    def executar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        if estado.diagnostico is None:
            estado = AnalistaAgent().executar(estado)
        renda = estado.diagnostico.renda_mensal if estado.diagnostico else 0.0

        analise = analisar_compulsao_bets(estado.transacoes, renda_mensal=renda)
        estado.analise_compulsao = analise

        query = "Lei 14.790 apostas quota fixa autoexclusao limites jogo responsavel"
        if query not in estado.queries_normativas:
            estado.queries_normativas.append(query)

        destino = _proximo_agente(estado, "coach")
        estado.registrar_mensagem(
            origem="coach",
            destino=destino,
            tipo="solicitacao_pesquisa",
            resumo=(
                f"Compulsão avaliada (risco={analise.risco_compulsao}, perda líquida={_formatar_brl(analise.perda_liquida)}, "
                f"madrugada={analise.aposta_madrugada_qtd}); solicitando base na Lei 14.790/2023."
            ),
            dados_chave={
                "perda_liquida": analise.perda_liquida,
                "aposta_madrugada_qtd": analise.aposta_madrugada_qtd,
                "aposta_pos_salario": analise.aposta_pos_salario,
                "risco_compulsao": analise.risco_compulsao,
                "queries_solicitadas": [query],
            },
        )
        return estado


class GuardiaoAgent:
    """Agente 5: isola prompt injection, audita boletos FEBRABAN e gera roteiro MED Pix."""

    def executar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        if estado.persona_id and not estado.transacoes:
            try:
                estado.transacoes = carregar_transacoes_persona(estado.persona_id)
            except FileNotFoundError:
                estado.transacoes = []

        inspecao = inspecionar_fraudes(
            estado.transacoes,
            documento_ocr=estado.documento_ocr,
            linha_digitavel=estado.linha_digitavel,
            banco_alegado=estado.banco_alegado,
            beneficiario_pf=estado.beneficiario_pf,
        )
        estado.inspecao_fraude = inspecao

        query = "Resolucao BCB 147 Mecanismo Especial de Devolucao MED Pix fraude 80 dias"
        if query not in estado.queries_normativas:
            estado.queries_normativas.append(query)

        destino = _proximo_agente(estado, "guardiao")
        estado.registrar_mensagem(
            origem="guardiao",
            destino=destino,
            tipo="solicitacao_pesquisa",
            resumo=(
                f"Inspeção antifraude concluída (fraude={inspecao.fraude_detectada}, "
                f"injection_neutralizada={inspecao.injection_detectada}); "
                f"solicitando Res. BCB 147/2021 (MED Pix)."
            ),
            dados_chave={
                "fraude_detectada": inspecao.fraude_detectada,
                "injection_detectada": inspecao.injection_detectada,
                "boleto_suspeito": inspecao.boleto.suspeito if inspecao.boleto else False,
                "queries_solicitadas": [query],
            },
        )
        return estado


class EducadorAgent:
    """Agente 6 (Research Agent): recupera trechos oficiais no RAG híbrido e aplica portão."""

    @staticmethod
    def _hit_relevante(hit: Hit, limiar_abstencao: float) -> bool:
        if hit.score_rerank is not None:
            return hit.score_rerank >= limiar_abstencao
        bm25_ok = hit.score_bm25 is not None and hit.score_bm25 >= _MIN_SCORE_BM25_SEM_RERANK
        vetor_ok = hit.score_vetor is not None and hit.score_vetor >= _MIN_SCORE_VETOR_SEM_RERANK
        return bm25_ok or vetor_ok

    def executar(
        self,
        estado: EstadoMultiagente,
        retriever: Retriever,
        k: int = 3,
        limiar_abstencao: float = 0.02,
    ) -> EstadoMultiagente:
        consulta_limpa, _ = mascarar(estado.consulta_mascarada or estado.consulta_usuario)
        queries_brutas = list(estado.queries_normativas)
        if not queries_brutas:
            if detectar_inducao_cvm(consulta_limpa) or "cvm" in estado.intencoes_detectadas:
                queries_brutas.append("Resolucao CVM 19 20 consultoria valores mobiliarios suitability 30")
            else:
                queries_brutas.append(consulta_limpa)
        queries = [mascarar(q)[0] for q in queries_brutas]

        hits_por_id: dict[str, Hit] = {}
        hits_por_query: list[Hit] = []
        for q in queries:
            resultados_q = [h for h in retriever.buscar(q, k=k) if self._hit_relevante(h, limiar_abstencao)]
            for h in resultados_q[:1]:
                if h.registro.id not in hits_por_id:
                    hits_por_id[h.registro.id] = h
                    hits_por_query.append(h)
            for h in resultados_q[1:]:
                if h.registro.id not in hits_por_id:
                    hits_por_id[h.registro.id] = h

        limite = max(k, len(queries))
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
        estado.evidencias = EvidenciaNormativa(
            queries_executadas=queries,
            hits_aprovados=len(citacoes),
            abstencao=abstencao,
            citacoes=citacoes,
            motivo_abstencao="Nenhum chunk atingiu o limiar mínimo de evidência." if abstencao else None,
        )

        estado.registrar_mensagem(
            origem="educador",
            destino="orquestrador",
            tipo="evidencia",
            resumo=(
                f"RAG retornou {len(citacoes)} citação(ões) oficial(is) para {len(queries)} query(s) "
                f"(abstenção={abstencao})."
            ),
            dados_chave={
                "queries": queries,
                "normas": [f"[{c.n}] {c.norma} {c.artigo or ''}".strip() for c in citacoes],
                "abstencao": abstencao,
            },
        )
        return estado


class ComplianceAgent:
    """Agente 7 (Validation Agent): aplica os 4 invariantes ético-regulatórios (RNF01–RNF05)."""

    def _citacoes_consistentes(self, rascunho: str, n_fontes: int) -> bool:
        encontrados = [int(m.group(1)) for m in RE_CITACAO.finditer(rascunho)]
        if n_fontes == 0:
            return len(encontrados) == 0
        if not encontrados:
            return False
        return all(1 <= n <= n_fontes for n in encontrados)

    def _numeros_deterministico_preservados(self, estado: EstadoMultiagente, rascunho: str) -> bool:
        if estado.modo != "hibrido_llm":
            return True
        if estado.diagnostico is not None:
            valores_obrigatorios = [
                _formatar_brl(estado.diagnostico.minimo_existencial),
                _formatar_brl(estado.diagnostico.renda_mensal),
            ]
            if any(v not in rascunho for v in valores_obrigatorios):
                return False
        return not (
            estado.analise_compulsao is not None
            and estado.analise_compulsao.perda_liquida > 0
            and _formatar_brl(estado.analise_compulsao.perda_liquida) not in rascunho
        )

    def validar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        consulta = estado.consulta_mascarada or mascarar(estado.consulta_usuario)[0]
        rascunho = estado.rascunho_resposta
        norm_rascunho = _normalizar_texto(rascunho)

        crise_necessaria = detectar_sinais_crise(consulta) or (
            estado.analise_compulsao is not None
            and estado.analise_compulsao.risco_compulsao == "critico"
            and ("crise" in estado.intencoes_detectadas or "nao consigo" in _normalizar_texto(consulta))
        )
        cvm_necessario = detectar_inducao_cvm(consulta) or bool(
            _RE_RECOMENDACAO_DIRETA_CVM.search(norm_rascunho)
        )
        _, pii_achada = mascarar(rascunho)
        pii_detectada = bool(pii_achada)

        n_fontes = estado.evidencias.hits_aprovados if estado.evidencias else 0
        cit_ok = self._citacoes_consistentes(rascunho, n_fontes)

        motivos_reprovacao: list[str] = []
        alertas: list[str] = []

        if crise_necessaria:
            alertas.append("Protocolo de Crise acionado: CVV 188, CAPS AD e Jogadores Anônimos.")
            tem_protocolo_crise = (
                bool(re.search(r"\bcvv\b", norm_rascunho))
                and bool(re.search(r"\b188\b", norm_rascunho))
                and "caps ad" in norm_rascunho
                and "jogadores anonimos" in norm_rascunho
            )
            if not tem_protocolo_crise:
                motivos_reprovacao.append(
                    "Rascunho omitiu o acolhimento obrigatório do Protocolo de Crise (CVV 188, CAPS AD e JA)."
                )

        if cvm_necessario:
            alertas.append("Trava CVM (Res. 19/20) acionada: vedada recomendação específica de ativos.")
            tem_recusa_educativa = (
                "cvm" in norm_rascunho
                and "liquidez" in norm_rascunho
                and ("fgc" in norm_rascunho or "tesouro" in norm_rascunho)
                and ("selic" in norm_rascunho or "cdi" in norm_rascunho)
            )
            violou_recomendacao = bool(_RE_RECOMENDACAO_DIRETA_CVM.search(norm_rascunho))
            if violou_recomendacao or not tem_recusa_educativa:
                motivos_reprovacao.append(
                    "Rascunho contém recomendação vedada ou omitiu a Recusa Educativa CVM com os 3 critérios objetivos."
                )

        if (
            estado.inspecao_fraude is not None
            and estado.inspecao_fraude.fraude_detectada
            and not any(termo in norm_rascunho for termo in ("pare", "nao pague", "med"))
        ):
            motivos_reprovacao.append(
                "Rascunho omitiu alerta antifraude obrigatório para golpe/boleto suspeito."
            )

        if pii_detectada:
            alertas.append(f"PII detectada na resposta gerada: {pii_achada}.")
            motivos_reprovacao.append("Resposta contém dado pessoal (PII) não mascarado.")

        if not cit_ok:
            motivos_reprovacao.append(
                "Citações [n] inconsistentes com as evidências recuperadas ou ausentes."
            )

        if not self._numeros_deterministico_preservados(estado, rascunho):
            motivos_reprovacao.append(
                "Síntese omitiu valores determinísticos obrigatórios calculados pelos especialistas."
            )

        aprovado = len(motivos_reprovacao) == 0
        veredito = VereditoCompliance(
            aprovado=aprovado,
            crise_acionada=crise_necessaria,
            bloqueio_cvm_acionado=cvm_necessario,
            pii_detectada=pii_detectada,
            citacoes_validas=cit_ok,
            precisou_revisao=(not aprovado) or (estado.revisoes_realizadas > 0),
            motivo_revisao="; ".join(motivos_reprovacao) if motivos_reprovacao else None,
            alertas=alertas,
        )
        estado.veredito = veredito

        if aprovado:
            estado.resposta_final = rascunho
            estado.registrar_mensagem(
                origem="compliance",
                destino="orquestrador",
                tipo="entrega",
                resumo="Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII).",
                dados_chave={
                    "aprovado": True,
                    "crise_acionada": crise_necessaria,
                    "bloqueio_cvm_acionado": cvm_necessario,
                    "citacoes_validas": cit_ok,
                    "precisou_revisao": veredito.precisou_revisao,
                },
            )
        else:
            estado.registrar_mensagem(
                origem="compliance",
                destino="orquestrador",
                tipo="validacao",
                resumo=f"Veredito REPROVADO — solicitando revisão: {veredito.motivo_revisao}",
                dados_chave={
                    "aprovado": False,
                    "motivo_revisao": veredito.motivo_revisao,
                    "crise_acionada": crise_necessaria,
                    "bloqueio_cvm_acionado": cvm_necessario,
                },
            )
        return estado
