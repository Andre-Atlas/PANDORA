"""Implementação dos 7 agentes especializados colaborativos do PANDORA."""
from __future__ import annotations

import logging
import re
import unicodedata

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
    analisar_compulsao_bets,
    calcular_raio_x,
    carregar_transacoes_persona,
    detectar_inducao_cvm,
    detectar_sinais_crise,
    inspecionar_fraudes,
    perfil_persona,
    simular_estrategias_divida,
)
from pandora_rag.generate.answer import MENSAGEM_ABSTENCAO, citacoes_validas
from pandora_rag.generate.gateway import Gateway, OrcamentoExcedido
from pandora_rag.generate.pii import mascarar
from pandora_rag.retrieve.hybrid import Hit, Retriever

logger = logging.getLogger(__name__)

_RE_RECOMENDACAO_DIRETA_CVM = re.compile(
    r"\b(?:compre|invista|aplique|escolha)\s+(?:o\s+|a\s+|no\s+|na\s+)?(?:cdb|acao|acoes|fundo|cripto|petr4|banco\s+\w+)\b"
)


def _norm(texto: str) -> str:
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", sem_acentos.lower()).strip()


def _formatar_brl(valor: float) -> str:
    inteiro, dec = f"{valor:,.2f}".split(".")
    return f"R$ {inteiro.replace(',', '.')},{dec}"


def _proximo_destino_analista(estado: EstadoMultiagente) -> AgentRole:
    for papel in estado.agentes_planejados:
        if papel in {"estrategista", "coach", "guardiao", "educador", "compliance"}:
            return papel
    return "educador"


def _classificar_intencoes(estado: EstadoMultiagente, texto_limpo: str) -> list[str]:
    norm = _norm(texto_limpo)
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
        crise_ativa = detectar_sinais_crise(estado.consulta_usuario) or (
            estado.veredito is not None and estado.veredito.crise_acionada
        )
        cvm_ativo = detectar_inducao_cvm(estado.consulta_usuario) or (
            estado.veredito is not None and estado.veredito.bloqueio_cvm_acionado
        )

        blocos: list[str] = []

        if tom == "acessivel_idoso":
            blocos.append(
                f"Olá, {nome}. Analisei com calma e cuidado o que você enviou para proteger seu dinheiro:"
            )
        elif tom == "parceiro_sem_julgamento":
            blocos.append(
                f"{nome}, aqui não há julgamento — vamos olhar juntos os números reais e proteger seu trabalho:"
            )
        else:
            blocos.append(
                f"Olá, {nome}. Organizei sua situação passo a passo com base nos seus dados e nas normas oficiais:"
            )

        if crise_ativa:
            blocos.append(
                "APOIO IMEDIATO E CONFIDENCIAL (PROTOCOLO DE CRISE):\n"
                "- Você não precisa enfrentar isso sozinho(a). Pause agora as decisões financeiras e fale com apoio especializado gratuito:\n"
                "- CVV (Centro de Valorização da Vida): ligue 188 (24h, gratuito e sigiloso) ou acesse cvv.org.br.\n"
                "- CAPS AD (SUS): atendimento presencial gratuito para compulsão e saúde mental.\n"
                "- Jogadores Anônimos (JA): grupos de apoio mútuo em jogadoresanonimos.com.br."
            )

        if estado.diagnostico is not None:
            d = estado.diagnostico
            linhas_diag = [
                "1. RAIO-X DO ORÇAMENTO:",
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
            blocos.append("\n".join(linhas_diag))

        if estado.plano_dividas is not None:
            p = estado.plano_dividas
            linhas_plano = [
                "2. PRIORIDADE DE PAGAMENTOS (MÍNIMO EXISTENCIAL BLINDADO):",
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
            blocos.append("\n".join(linhas_plano))

        if estado.analise_compulsao is not None:
            c = estado.analise_compulsao
            linhas_bets = [
                "2. RETRATO OBJETIVO DAS APOSTAS (SEM JULGAMENTO):",
                f"- Total enviado para apostas no recorte: {_formatar_brl(c.total_apostado)} (prêmios recebidos: {_formatar_brl(c.premios_recebidos)})",
                f"- Perda líquida real: {_formatar_brl(c.perda_liquida)} ({c.pct_renda_comprometida:.1f}% do repasse/renda analisada)",
                f"- Concentração de risco: {c.aposta_madrugada_qtd} aposta(s) de madrugada (23h–06h); pós-repasse: {'sim' if c.aposta_pos_salario else 'não'}",
                f"- Impacto real no seu trabalho: {c.custo_oportunidade}",
                f"- Sugestão prática: ativar Pausa Noturna (22h–07h) e janela de resfriamento (cooling-off) de {c.sugestao_cooling_off_horas}h + autoexclusão nas plataformas .bet.br.",
            ]
            blocos.append("\n".join(linhas_bets))

        if estado.inspecao_fraude is not None:
            f = estado.inspecao_fraude
            num_bloco = "3" if estado.plano_dividas is not None else "2"
            linhas_fraude = [f"{num_bloco}. ALERTA DE SEGURANÇA E GOLPE (GUARDIÃO):"]
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
                    linhas_fraude.append("- Linha digitável estruturalmente válida; ainda assim confirme o CNPJ recebedor no app do banco.")
            if f.roteiro_med_pix:
                linhas_fraude.append(
                    "- Como tentar recuperar o Pix já enviado (MED — prazo legal de até 80 dias):"
                )
                linhas_fraude.extend(f"  {passo}" for passo in f.roteiro_med_pix)
            blocos.append("\n".join(linhas_fraude))

        if cvm_ativo:
            selic = SERIES_SGS_BCB["432"]["valor_referencia"]
            cdi = SERIES_SGS_BCB["12"]["valor_referencia"]
            ipca = SERIES_SGS_BCB["433"]["valor_referencia"]
            meta_6m = perfil.get("meta_reserva_6_meses", 0.0)
            poupanca = perfil.get("capacidade_poupanca", 0.0)
            linhas_cvm = [
                "2. EDUCAÇÃO FINANCEIRA SOB CONFORMIDADE CVM (RECUSA EDUCATIVA):",
                "- Pelas regras da CVM (Resoluções CVM 19 e 20/2021), eu sou um copiloto educacional e não faço recomendação específica de ação, fundo ou CDB de um banco determinado.",
                "- Em vez de indicar um produto único, use estes 3 critérios objetivos para avaliar qualquer opção de Reserva de Emergência com segurança:",
                "  1. Liquidez Diária (D+0): poder resgatar no mesmo dia se surgir um imprevisto.",
                "  2. Baixo Risco de Crédito: títulos públicos federais (Tesouro Nacional) ou instituições cobertas pelo FGC (até R$ 250 mil por CPF/instituição).",
                f"  3. Rendimento Pós-Fixado: acompanhar 100% da Selic ({selic:.2f}% a.a.) ou do CDI ({cdi:.2f}% a.a.) para superar a inflação (IPCA {ipca:.2f}% a.m.) sem risco de marcação a mercado.",
            ]
            if meta_6m > 0 and poupanca > 0:
                linhas_cvm.append(
                    f"- Sua escada da reserva: poupando {_formatar_brl(poupanca)}/mês, sua meta de 6 meses de tranquilidade é {_formatar_brl(meta_6m)}."
                )
            blocos.append("\n".join(linhas_cvm))

        if estado.evidencias is not None:
            ev = estado.evidencias
            num_ev = "4" if (estado.plano_dividas is not None and estado.inspecao_fraude is not None) else "3"
            if ev.abstencao and not (cvm_ativo or estado.plano_dividas or estado.analise_compulsao or estado.inspecao_fraude):
                blocos.append(MENSAGEM_ABSTENCAO)
            elif ev.citacoes:
                linhas_ev = [f"{num_ev}. BASE LEGAL E FONTES OFICIAIS CITADAS:"]
                for c in ev.citacoes:
                    art = f", {c.artigo}" if c.artigo else ""
                    resumo_trecho = c.trecho.strip().replace("\n", " ")[:180]
                    linhas_ev.append(
                        f"- [{c.n}] {c.norma}{art}: {resumo_trecho}... (Fonte: {c.link})"
                    )
                blocos.append("\n".join(linhas_ev))

        rascunho = "\n\n".join(blocos)

        if gateway is not None and modelo and not modo_revisao:
            prompt_usuario = (
                "Reescreva de forma clara, acolhedora e concisa (até 220 palavras) mantendo TODOS os números em reais, "
                "percentuais, prazos, blocos de alerta (CVV 188 / CVM / PARE NÃO PAGUE) e marcadores de citação [1], [2] exatamente como estão:\n\n"
                + rascunho
            )
            try:
                comp = gateway.gerar(
                    modelo,
                    "Você é o Orquestrador/Elpis do PANDORA. Nunca invente números, não recomende ativos específicos e preserve todas as citações [n].",
                    prompt_usuario,
                    max_tokens=700,
                )
                if comp.texto.strip():
                    rascunho = comp.texto.strip()
            except (httpx.HTTPError, OrcamentoExcedido, KeyError, RuntimeError, ValueError) as exc:
                logger.warning("Fallback determinístico na síntese do Orquestrador: %s", exc)

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

        destino = _proximo_destino_analista(estado)
        estado.registrar_mensagem(
            origem="analista",
            destino=destino,
            tipo="analise",
            resumo=(
                f"Raio-X calculado para {pid}: renda={_formatar_brl(diag.renda_mensal)}, "
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

        estado.registrar_mensagem(
            origem="estrategista",
            destino="educador",
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

        estado.registrar_mensagem(
            origem="coach",
            destino="educador",
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

        estado.registrar_mensagem(
            origem="guardiao",
            destino="educador",
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

    def executar(
        self,
        estado: EstadoMultiagente,
        retriever: Retriever,
        k: int = 3,
        limiar_abstencao: float = 0.02,
    ) -> EstadoMultiagente:
        queries = list(estado.queries_normativas)
        if not queries:
            if detectar_inducao_cvm(estado.consulta_usuario) or "cvm" in estado.intencoes_detectadas:
                queries.append("Resolucao CVM 19 20 consultoria valores mobiliarios suitability 30")
            else:
                queries.append(estado.consulta_mascarada or estado.consulta_usuario)

        hits_por_id: dict[str, Hit] = {}
        hits_por_query: list[Hit] = []
        for q in queries:
            resultados_q = [
                h
                for h in retriever.buscar(q, k=k)
                if h.score_rerank is None or h.score_rerank >= limiar_abstencao
            ]
            for h in resultados_q[:1]:
                if h.registro.id not in hits_por_id:
                    hits_por_id[h.registro.id] = h
                    hits_por_query.append(h)
            for h in resultados_q[1:]:
                atual = hits_por_id.get(h.registro.id)
                if atual is None:
                    hits_por_id[h.registro.id] = h

        if len(hits_por_query) >= max(k, len(queries)):
            hits_ordenados = hits_por_query[: max(k, len(queries))]
        else:
            faltam = max(k, len(queries)) - len(hits_por_query)
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
                trecho=h.registro.texto[:400],
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

    def validar(self, estado: EstadoMultiagente) -> EstadoMultiagente:
        consulta = estado.consulta_mascarada or estado.consulta_usuario
        rascunho = estado.rascunho_resposta
        norm_rascunho = _norm(rascunho)

        crise_necessaria = detectar_sinais_crise(consulta) or (
            estado.analise_compulsao is not None
            and estado.analise_compulsao.risco_compulsao == "critico"
            and "nao consigo" in _norm(consulta)
        )
        cvm_necessario = detectar_inducao_cvm(consulta) or bool(
            _RE_RECOMENDACAO_DIRETA_CVM.search(norm_rascunho)
        )
        _, pii_achada = mascarar(rascunho)
        pii_detectada = bool(pii_achada)

        tem_hits = estado.evidencias is not None and estado.evidencias.hits_aprovados > 0
        n_fontes = estado.evidencias.hits_aprovados if estado.evidencias else 0
        cit_ok = (not tem_hits) or bool(citacoes_validas(rascunho, n_fontes))

        motivos_reprovacao: list[str] = []
        alertas: list[str] = []

        if crise_necessaria:
            alertas.append("Protocolo de Crise acionado: CVV 188, CAPS AD e Jogadores Anônimos.")
            if "188" not in rascunho and "cvv" not in norm_rascunho:
                motivos_reprovacao.append(
                    "Rascunho omitiu o acolhimento obrigatório do Protocolo de Crise (CVV 188)."
                )

        if cvm_necessario:
            alertas.append("Trava CVM (Res. 19/20) acionada: vedada recomendação específica de ativos.")
            tem_recusa_educativa = (
                "cvm" in norm_rascunho
                and "liquidez" in norm_rascunho
                and ("fgc" in norm_rascunho or "tesouro" in norm_rascunho)
            )
            violou_recomendacao = bool(_RE_RECOMENDACAO_DIRETA_CVM.search(norm_rascunho))
            if violou_recomendacao or not tem_recusa_educativa:
                motivos_reprovacao.append(
                    "Rascunho contém recomendação vedada ou omitiu a Recusa Educativa CVM com os 3 critérios objetivos."
                )

        if pii_detectada:
            alertas.append(f"PII detectada na resposta gerada: {pii_achada}.")
            motivos_reprovacao.append("Resposta contém dado pessoal (PII) não mascarado.")

        if not cit_ok:
            motivos_reprovacao.append(
                "Há evidências oficiais recuperadas pelo EducadorAgent, mas faltam citações [n] na síntese."
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
