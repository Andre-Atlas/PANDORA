"""Ferramentas determinísticas de finanças, bets, antifraude e guardrails (RNF01–RNF05)."""
from __future__ import annotations

import csv
import re
import unicodedata
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from pandora_rag.agents.models import (
    AnaliseCompulsao,
    DiagnosticoFinanceiro,
    DividaItem,
    EstrategiaDivida,
    InspecaoFraude,
    PlanoReestruturacao,
    TransacaoPersona,
    ValidacaoBoleto,
)
from pandora_rag.agents.personas_data import (
    BANCOS_POR_NOME,
    PERFIL_PADRAO,
    PERFIS_PERSONAS,
    ROTEIRO_MED_PIX,
    SERIES_SGS_BCB,
)
from pandora_rag.config import REPO_ROOT
from pandora_rag.generate.pii import mascarar

CSV_PERSONAS_PADRAO = (
    REPO_ROOT / "docs" / "evidencias" / "datasets" / "amostra_transacoes_sinteticas_personas.csv"
)

_CATEGORIAS_ESSENCIAIS = {"MORADIA", "ALIMENTACAO", "SAUDE", "TRANSPORTE"}
_RE_PERSONA_ID_SEGURA = re.compile(r"[a-z0-9_]{1,40}")
_RE_TAG_DOC = re.compile(r"</?documento_externo_nao_confiavel\b[^>]*>", re.IGNORECASE)

_PADROES_INJECTION: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(?:as\s+|todas\s+as\s+)?instruc"),
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions"),
    re.compile(r"desconsidere\s+(?:as\s+)?regras"),
    re.compile(r"esqueca\s+(?:as\s+)?instruc"),
    re.compile(r"aprove\s+(?:o\s+pagamento\s+)?imediatamente"),
    re.compile(
        r"(?:aprove|confirme|diga)\s+(?:o\s+pagamento|que\s+o\s+boleto\s+e\s+(?:seguro|legitimo|valido|confiavel))"
    ),
    re.compile(r"(?:^|\s)(?:system|human|assistant)\s*:"),
    re.compile(r"<\|im_(?:start|end)\|>"),
    re.compile(r"</?system>"),
    re.compile(r"\[/?inst\]"),
    re.compile(r"override\s+(?:safety|rules|system)"),
]

_PADROES_CRISE: list[re.Pattern[str]] = [
    re.compile(r"\b(?:nao|n)\s+consigo\s+(?:mais\s+)?(?:me\s+)?(?:parar|controlar|sair)\b"),
    re.compile(r"\bnao\s+consigo\s+sair\s+disso\b"),
    re.compile(r"\bperdi\s+tudo\b"),
    re.compile(
        r"\b(?:me\s+mat(?:ar|o)|suicid\w*|quero\s+morrer|vontade\s+de\s+morrer|"
        r"tirar\s+(?:a\s+)?minha\s+vida|acabar\s+com\s+(?:tudo|a\s+minha\s+vida)|"
        r"nao\s+quero\s+(?:mais\s+)?viver|desistir\s+da\s+vida)\b"
    ),
    re.compile(r"\b(?:sem\s+saida|nao\s+aguento\s+mais|desespero\s+total)\b"),
]

_ATIVOS_REGULADOS = (
    r"(?:acao|acoes|cdb|lci|lca|fundo|fiis?|etf|bdr|coe|cri|cra|debenture|"
    r"cripto\w*|bitcoin|ativo|papel|titulo|carteira|tesouro)"
)
_VERBOS_CVM = (
    r"(?:comprar|vender|investir|aplicar|escolher|manter|colocar|"
    r"compro|invisto|aplico|coloco|recomenda\w*|recomende|indica\w*|indique|suger\w*|sugira|vale\s+a\s+pena)"
)

_PADROES_CVM: list[re.Pattern[str]] = [
    re.compile(rf"\b(?:qual|quais)\b.{{0,120}}\b(?:{_ATIVOS_REGULADOS}|banco)\b.{{0,120}}\b{_VERBOS_CVM}\b"),
    re.compile(rf"\b(?:qual|quais)\b.{{0,120}}\b{_VERBOS_CVM}\b.{{0,120}}\b(?:{_ATIVOS_REGULADOS}|banco)\b"),
    re.compile(rf"\b(?:qual|quais)\s+(?:o\s+|a\s+)?melhor\b.{{0,120}}\b(?:{_ATIVOS_REGULADOS}|banco|investimento)\b"),
    re.compile(
        rf"\b(?:devo|posso|vale\s+a\s+pena|onde|em\s+qual(?:\s+banco)?)\s+{_VERBOS_CVM}\b"
        rf".{{0,120}}\b(?:{_ATIVOS_REGULADOS}|banco|corretora|dinheiro|reserva)\b"
    ),
    re.compile(
        rf"\b(?:recomenda\w*|recomende|indica\w*|indique|suger\w*|sugira|me\s+diz\s+qual|diga\s+qual)\b"
        rf".{{0,120}}\b(?:{_ATIVOS_REGULADOS}|banco)\b"
    ),
    re.compile(
        rf"\b(?:[a-z]{{4}}(?:3|4|5|6|11|34|35|39)\b.{{0,120}}\b{_VERBOS_CVM}|{_VERBOS_CVM}\b.{{0,120}}\b[a-z]{{4}}(?:3|4|5|6|11|34|35|39))\b"
    ),
]


def _normalizar_texto(texto: str) -> str:
    """Remove acentos, caracteres invisíveis (Cf) e normaliza espaços."""
    sem_invisiveis = "".join(c for c in texto if unicodedata.category(c) != "Cf")
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", sem_invisiveis) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", sem_acentos.lower()).strip()


def _parse_iso(timestamp: str) -> datetime | None:
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        return None


def _eh_aposta(tx: TransacaoPersona) -> bool:
    return tx.is_bet or tx.mcc == "7995" or tx.category == "APOSTAS_BETS"


def _simular_amortizacao_12m(dividas: list[DividaItem], orcamento_mensal: float) -> float:
    """Calcula juros acumulados em 12 meses aplicando o orçamento na ordem das dívidas."""
    saldos = [d.saldo for d in dividas]
    taxas_mensais = [(1.0 + d.cet_anual_pct / 100.0) ** (1.0 / 12.0) - 1.0 for d in dividas]
    juros_totais = 0.0
    for _ in range(12):
        for i in range(len(saldos)):
            if saldos[i] > 0:
                juro_mes = saldos[i] * taxas_mensais[i]
                saldos[i] += juro_mes
                juros_totais += juro_mes
        restante = orcamento_mensal
        for i in range(len(saldos)):
            if saldos[i] <= 0 or restante <= 0:
                continue
            pagamento = min(saldos[i], restante)
            saldos[i] -= pagamento
            restante -= pagamento
    return round(juros_totais, 2)


def _alocar_folga_mensal(dividas: list[DividaItem], folga: float) -> dict[str, float]:
    """Distribui a folga mensal disponível seguindo exatamente a ordem de prioridade."""
    alocacao: dict[str, float] = {}
    restante = round(max(0.0, folga), 2)
    for d in dividas:
        pago = round(min(restante, d.saldo), 2) if restante > 0 else 0.0
        alocacao[d.credor] = pago
        restante = round(restante - pago, 2)
    return alocacao


def _modulo_10(bloco: str) -> int:
    """Calcula dígito verificador FEBRABAN pelo algoritmo de módulo 10."""
    soma = 0
    peso = 2
    for ch in reversed(bloco):
        prod = int(ch) * peso
        soma += prod // 10 + prod % 10
        peso = 1 if peso == 2 else 2
    return (10 - (soma % 10)) % 10


def _normalizar_codigo_banco(banco: str | None) -> str | None:
    if not banco:
        return None
    limpo = banco.strip()
    if limpo.isdigit():
        return limpo.zfill(3)[:3]
    norm = _normalizar_texto(limpo)
    for nome, codigo in BANCOS_POR_NOME.items():
        if re.search(rf"\b{re.escape(nome)}\b", norm):
            return codigo
    return None


def _inferir_banco_em_texto(texto: str) -> str | None:
    norm = _normalizar_texto(texto)
    for nome, codigo in BANCOS_POR_NOME.items():
        if re.search(rf"\b{re.escape(nome)}\b", norm):
            return codigo
    return None


def carregar_transacoes_persona(
    persona_id: str,
    csv_path: Path | None = None,
) -> list[TransacaoPersona]:
    """Lê as transações sintéticas de uma persona no CSV oficial do repositório."""
    caminho = csv_path or CSV_PERSONAS_PADRAO
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de transações não encontrado: {caminho}")
    transacoes: list[TransacaoPersona] = []
    with caminho.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["persona_id"] != persona_id:
                continue
            transacoes.append(
                TransacaoPersona(
                    transaction_id=row["transaction_id"],
                    persona_id=row["persona_id"],
                    posted_at=row["posted_at"],
                    amount=float(row["amount"]),
                    payment_method=row["payment_method"],
                    description_masked=row["description_masked"],
                    mcc=row["mcc"],
                    category=row["category"],
                    is_bet=row["is_bet"].strip().lower() == "true",
                    anomaly_score=float(row["anomaly_score"]),
                    ground_truth_note=row.get("ground_truth_note", ""),
                )
            )
    return transacoes


def perfil_persona(persona_id: str) -> dict[str, Any]:
    """Retorna metadados financeiros e de tom da persona, com fallback neutro seguro."""
    dados = PERFIS_PERSONAS.get(persona_id)
    if dados is None:
        copia = deepcopy(PERFIL_PADRAO)
        copia["persona_id"] = persona_id if _RE_PERSONA_ID_SEGURA.fullmatch(persona_id) else "visitante"
        return copia
    return deepcopy(dados)


def calcular_raio_x(
    persona_id: str,
    transacoes: list[TransacaoPersona],
) -> DiagnosticoFinanceiro:
    """Calcula renda, mínimo existencial, folga líquida e comparativos SGS determinísticos."""
    perfil = perfil_persona(persona_id)
    renda_txs = round(
        sum(tx.amount for tx in transacoes if tx.category == "RENDA" or (tx.amount > 0 and not _eh_aposta(tx))),
        2,
    )
    renda_mensal = renda_txs if renda_txs > 0 else float(perfil.get("renda_mensal", 0.0))

    essenciais_txs = round(
        sum(abs(tx.amount) for tx in transacoes if tx.amount < 0 and tx.category in _CATEGORIAS_ESSENCIAIS),
        2,
    )
    minimo_perfil = float(perfil.get("minimo_existencial", 0.0))
    minimo_existencial = round(max(minimo_perfil, essenciais_txs), 2)
    folga_disponivel = round(max(0.0, renda_mensal - minimo_existencial), 2)

    gasto_dividas_mensal = round(
        sum(abs(tx.amount) for tx in transacoes if tx.amount < 0 and tx.category == "DIVIDA_JUROS"),
        2,
    )
    dividas_identificadas = [DividaItem(**d) for d in perfil.get("dividas", [])]
    saldo_dividas = round(sum(d.saldo for d in dividas_identificadas), 2)
    total_dividas = saldo_dividas if saldo_dividas > 0 else gasto_dividas_mensal
    comprometimento_pct = round(
        (gasto_dividas_mensal / renda_mensal * 100.0) if renda_mensal > 0 else 0.0,
        2,
    )

    comparativos_sgs: dict[str, Any] = {}
    alertas: list[str] = []

    for d in dividas_identificadas:
        if "rotativo" in d.modalidade:
            ref = SERIES_SGS_BCB["22022"]["valor_referencia"]
            comparativos_sgs["22022"] = {
                "serie": SERIES_SGS_BCB["22022"]["nome"],
                "cet_usuario_pct_aa": d.cet_anual_pct,
                "media_bcb_pct_aa": ref,
                "diferenca_pp": round(d.cet_anual_pct - ref, 2),
            }
            if d.cet_anual_pct > ref:
                alertas.append(
                    f"CET do rotativo ({d.cet_anual_pct:.1f}% a.a.) supera a média oficial BCB SGS 22022 ({ref:.1f}% a.a.)."
                )
        elif "consignado" in d.modalidade:
            ref = SERIES_SGS_BCB["25467"]["valor_referencia"]
            comparativos_sgs["25467"] = {
                "serie": SERIES_SGS_BCB["25467"]["nome"],
                "cet_usuario_pct_aa": d.cet_anual_pct,
                "media_bcb_pct_aa": ref,
                "diferenca_pp": round(d.cet_anual_pct - ref, 2),
            }

    if not comparativos_sgs:
        comparativos_sgs["432"] = SERIES_SGS_BCB["432"]
        comparativos_sgs["12"] = SERIES_SGS_BCB["12"]
        comparativos_sgs["433"] = SERIES_SGS_BCB["433"]

    if comprometimento_pct > 50.0:
        alertas.append(
            f"Comprometimento mensal com dívidas ({comprometimento_pct:.1f}% da renda) ameaça o Mínimo Existencial."
        )
    if minimo_existencial >= renda_mensal > 0:
        alertas.append(
            "Despesas vitais igualam ou superam a renda mensal; folga para dívidas é R$ 0,00."
        )

    return DiagnosticoFinanceiro(
        persona_id=perfil["persona_id"],
        renda_mensal=renda_mensal,
        minimo_existencial=minimo_existencial,
        folga_disponivel=folga_disponivel,
        gasto_dividas_mensal=gasto_dividas_mensal,
        total_dividas=total_dividas,
        comprometimento_dividas_pct=comprometimento_pct,
        dividas_identificadas=dividas_identificadas,
        comparativos_sgs=comparativos_sgs,
        alertas=alertas,
    )


def simular_estrategias_divida(
    diagnostico: DiagnosticoFinanceiro,
    dividas: list[DividaItem],
) -> PlanoReestruturacao:
    """Blinda o mínimo existencial e compara Avalanche vs. Bola de Neve com teto da Lei 14.690."""
    minimo_blindado = round(diagnostico.minimo_existencial, 2)
    diferenca = round(diagnostico.renda_mensal - minimo_blindado, 2)
    if diferenca < 0:
        folga_acordos = 0.0
        deficit_vital = round(abs(diferenca), 2)
    else:
        folga_acordos = diferenca
        deficit_vital = 0.0

    ordenadas_avalanche = sorted(
        dividas,
        key=lambda d: (not d.essencial, -d.dias_atraso, -d.cet_anual_pct, d.saldo),
    )
    ordenadas_bola = sorted(
        dividas,
        key=lambda d: (not d.essencial, -d.dias_atraso, d.saldo, -d.cet_anual_pct),
    )

    juros_avalanche = _simular_amortizacao_12m(ordenadas_avalanche, folga_acordos)
    juros_bola = _simular_amortizacao_12m(ordenadas_bola, folga_acordos)
    economia_juros = round(max(0.0, juros_bola - juros_avalanche), 2)

    avalanche = EstrategiaDivida(
        nome="avalanche",
        ordem_credores=[d.credor for d in ordenadas_avalanche],
        alocacao_mensal=_alocar_folga_mensal(ordenadas_avalanche, folga_acordos),
        juros_12m_estimado=juros_avalanche,
        justificativa="Prioriza serviços essenciais em atraso e depois o maior CET anual para reduzir juros compostos.",
    )
    bola_de_neve = EstrategiaDivida(
        nome="bola_de_neve",
        ordem_credores=[d.credor for d in ordenadas_bola],
        alocacao_mensal=_alocar_folga_mensal(ordenadas_bola, folga_acordos),
        juros_12m_estimado=juros_bola,
        justificativa="Prioriza serviços essenciais e depois o menor saldo devedor para ganhar fôlego rápido.",
    )

    alerta_rotativo = any(
        "rotativo" in d.modalidade.lower()
        and (d.cet_anual_pct > 100.0 or (d.saldo_original is not None and d.saldo >= d.saldo_original * 2.0))
        for d in dividas
    )
    soma_parcelas = round(sum(d.parcela_mensal for d in dividas), 2)
    requer_repactuacao = deficit_vital > 0 or soma_parcelas > folga_acordos

    alertas: list[str] = []
    if deficit_vital > 0:
        alertas.append(
            f"Déficit vital de R$ {deficit_vital:.2f}: preservar 100% do Mínimo Existencial e buscar repactuação global (Lei 14.181/2021)."
        )
    elif requer_repactuacao:
        alertas.append(
            f"Parcelas atuais (R$ {soma_parcelas:.2f}) excedem a folga real (R$ {folga_acordos:.2f}); elegível à conciliação da Lei 14.181/2021."
        )
    if alerta_rotativo:
        alertas.append(
            "Alerta Lei 14.690/2023: juros e encargos do rotativo não podem ultrapassar 100% do valor original da dívida."
        )

    return PlanoReestruturacao(
        minimo_existencial_blindado=minimo_blindado,
        folga_para_acordos=folga_acordos,
        deficit_vital=deficit_vital,
        avalanche=avalanche,
        bola_de_neve=bola_de_neve,
        estrategia_recomendada="avalanche",
        economia_estimada_juros=economia_juros,
        alerta_teto_rotativo_lei_14690=alerta_rotativo,
        requer_repactuacao_lei_14181=requer_repactuacao,
        alertas=alertas,
    )


def analisar_compulsao_bets(
    transacoes: list[TransacaoPersona],
    renda_mensal: float,
) -> AnaliseCompulsao:
    """Apura perda líquida real em apostas, madrugada (23h–06h) e gatilho pós-salário."""
    apostas = [tx for tx in transacoes if _eh_aposta(tx)]
    saidas = [tx for tx in apostas if tx.amount < 0]
    entradas_premio = [tx for tx in apostas if tx.amount > 0]

    total_apostado = round(sum(abs(tx.amount) for tx in saidas), 2)
    premios_recebidos = round(sum(tx.amount for tx in entradas_premio), 2)
    perda_liquida = round(max(0.0, total_apostado - premios_recebidos), 2)
    pct_renda = round((perda_liquida / renda_mensal * 100.0) if renda_mensal > 0 else 0.0, 2)

    horarios_renda = [
        dt
        for tx in transacoes
        if (tx.category == "RENDA" or (tx.amount > 0 and not _eh_aposta(tx)))
        and (dt := _parse_iso(tx.posted_at)) is not None
    ]

    madrugada_qtd = 0
    valor_risco = 0.0
    pos_salario = False
    for tx in saidas:
        dt = _parse_iso(tx.posted_at)
        eh_madrugada = dt is not None and (dt.hour >= 23 or dt.hour < 6)
        eh_pos_salario = dt is not None and any(
            0.0 <= (dt - dt_renda).total_seconds() <= 86400.0 for dt_renda in horarios_renda
        )
        if eh_madrugada:
            madrugada_qtd += 1
        if eh_pos_salario:
            pos_salario = True
        if eh_madrugada or eh_pos_salario:
            valor_risco += abs(tx.amount)

    concentracao_risco_pct = round(
        (valor_risco / total_apostado * 100.0) if total_apostado > 0 else 0.0,
        2,
    )

    tanques_combustivel = int(perda_liquida // 65.0)
    custo_oportunidade = (
        f"R$ {perda_liquida:.2f} equivale a cerca de {tanques_combustivel} tanques de gasolina (R$ 65/tanque) "
        f"ou {perda_liquida / 450.0:.1f}x uma parcela mensal de R$ 450,00."
        if perda_liquida > 0
        else "Nenhuma perda líquida em apostas detectada no recorte."
    )

    if pct_renda >= 30.0 or (madrugada_qtd >= 2 and pos_salario):
        risco = "critico"
    elif total_apostado > 0 and (madrugada_qtd >= 1 or pos_salario):
        risco = "alto"
    elif total_apostado > 0:
        risco = "moderado"
    else:
        risco = "baixo"

    alertas: list[str] = []
    if madrugada_qtd > 0:
        alertas.append(f"Identificadas {madrugada_qtd} apostas em horário noturno/madrugada (23h–06h).")
    if pos_salario:
        alertas.append("Aposta realizada nas primeiras 24h após recebimento de renda/repasse.")
    if perda_liquida > 0:
        alertas.append(f"Perda líquida real de R$ {perda_liquida:.2f} ({pct_renda:.1f}% da renda analisada).")

    return AnaliseCompulsao(
        total_apostado=total_apostado,
        premios_recebidos=premios_recebidos,
        perda_liquida=perda_liquida,
        pct_renda_comprometida=pct_renda,
        aposta_madrugada_qtd=madrugada_qtd,
        aposta_pos_salario=pos_salario,
        concentracao_risco_pct=concentracao_risco_pct,
        custo_oportunidade=custo_oportunidade,
        sugestao_cooling_off_horas=48 if risco in {"alto", "critico"} else 24,
        risco_compulsao=risco,
        alertas=alertas,
    )


def sanitizar_documento_nao_confiavel(texto: str) -> tuple[str, bool]:
    """Neutraliza prompt injection (linha e multi-linha) em OCR e encapsula com delimitadores."""
    injection_linha = False
    linhas_limpas: list[str] = []
    for linha in texto.splitlines():
        norm = _normalizar_texto(linha)
        if any(p.search(norm) for p in _PADROES_INJECTION):
            injection_linha = True
            linhas_limpas.append("[CONTEUDO_BLOQUEADO_INJECTION]")
        else:
            linha_segura = _RE_TAG_DOC.sub("", linha)
            linha_mascarada, _ = mascarar(linha_segura)
            linhas_limpas.append(linha_mascarada)

    corpo_linhas = "\n".join(linhas_limpas).strip()
    norm_global = _normalizar_texto(_RE_TAG_DOC.sub("", texto))
    injection_global = any(p.search(norm_global) for p in _PADROES_INJECTION)

    if injection_global and not injection_linha:
        # Injeção dividida entre múltiplas linhas: substitui o bloco textual suspeito por marcador único.
        corpo = "[CONTEUDO_BLOQUEADO_INJECTION]"
    else:
        corpo = corpo_linhas

    encapsulado = f"<documento_externo_nao_confiavel>\n{corpo}\n</documento_externo_nao_confiavel>"
    return encapsulado, (injection_linha or injection_global)


def validar_boleto_febraban(
    linha_digitavel: str,
    banco_alegado: str | None = None,
    beneficiario_pf: bool = False,
) -> ValidacaoBoleto:
    """Valida comprimento (47 dígitos), DVs módulo 10 (campos 1–3), banco e beneficiário."""
    digitos = re.sub(r"\D", "", linha_digitavel)
    tamanho_valido = len(digitos) == 47
    codigo_banco = digitos[:3] if len(digitos) >= 3 else None
    motivos: list[str] = []

    if not tamanho_valido:
        motivos.append(
            f"Linha digitável possui {len(digitos)} dígitos; padrão FEBRABAN bancário exige 47."
        )

    dv_valido = False
    if tamanho_valido:
        dv1 = _modulo_10(digitos[0:9]) == int(digitos[9])
        dv2 = _modulo_10(digitos[10:20]) == int(digitos[20])
        dv3 = _modulo_10(digitos[21:31]) == int(digitos[31])
        dv_valido = dv1 and dv2 and dv3
        if not dv_valido:
            motivos.append("Dígito verificador (módulo 10) inválido na linha digitável.")

    banco_esperado = _normalizar_codigo_banco(banco_alegado)
    if banco_esperado and codigo_banco and banco_esperado != codigo_banco:
        motivos.append(
            f"Código do banco extraído ({codigo_banco}) diverge do banco alegado ({banco_esperado})."
        )

    if beneficiario_pf:
        motivos.append("Beneficiário pessoa física (PF) suspeito para boleto de instituição/INSS.")

    suspeito = (not tamanho_valido) or (not dv_valido) or bool(motivos)
    return ValidacaoBoleto(
        linha_digitavel_limpa=digitos,
        tamanho_valido=tamanho_valido,
        digito_verificador_valido=dv_valido,
        codigo_banco_extraido=codigo_banco,
        banco_alegado=banco_esperado or banco_alegado,
        beneficiario_pf=beneficiario_pf,
        suspeito=suspeito,
        motivos=motivos,
    )


def inspecionar_fraudes(
    transacoes: list[TransacaoPersona],
    documento_ocr: str | None = None,
    linha_digitavel: str | None = None,
    banco_alegado: str | None = None,
    beneficiario_pf: bool = False,
) -> InspecaoFraude:
    """Executa isolamento anti-injection, auditoria FEBRABAN e roteiro do MED do Pix."""
    texto_sanitizado = ""
    injection_detectada = False
    banco_inferido = banco_alegado
    pf_inferido = beneficiario_pf

    if documento_ocr:
        texto_sanitizado, injection_detectada = sanitizar_documento_nao_confiavel(documento_ocr)
        if not banco_inferido:
            banco_inferido = _inferir_banco_em_texto(texto_sanitizado)
        norm_ocr = _normalizar_texto(texto_sanitizado)
        if not pf_inferido and any(
            termo in norm_ocr for termo in ("beneficiario pf", "pessoa fisica", "terceirospf", "[cpf]")
        ):
            pf_inferido = True

    boleto = (
        validar_boleto_febraban(
            linha_digitavel,
            banco_alegado=banco_inferido,
            beneficiario_pf=pf_inferido,
        )
        if linha_digitavel
        else None
    )

    suspeitas = [
        tx
        for tx in transacoes
        if tx.category == "FRAUDE_SUSPEITA"
        or "golpe" in tx.ground_truth_note.lower()
        or "fraude" in tx.ground_truth_note.lower()
    ]

    fraude_detectada = (
        injection_detectada
        or (boleto is not None and boleto.suspeito)
        or bool(suspeitas)
    )

    alertas: list[str] = []
    if injection_detectada:
        alertas.append("Tentativa de prompt injection oculta no documento foi neutralizada.")
    if boleto is not None and boleto.suspeito:
        alertas.extend(boleto.motivos)
    if suspeitas:
        alertas.append(f"{len(suspeitas)} transação(ões) marcada(s) com indício de fraude no histórico.")

    roteiro_med = list(ROTEIRO_MED_PIX) if fraude_detectada else []

    return InspecaoFraude(
        texto_sanitizado=texto_sanitizado,
        injection_detectada=injection_detectada,
        boleto=boleto,
        transacoes_suspeitas=suspeitas,
        fraude_detectada=fraude_detectada,
        roteiro_med_pix=roteiro_med,
        prazo_med_dias=80,
        alertas=alertas,
    )


def detectar_sinais_crise(texto: str) -> bool:
    """Detecta sinais de sofrimento psíquico agudo para acionar CVV 188, CAPS AD e JA."""
    norm = _normalizar_texto(texto)
    return any(p.search(norm) for p in _PADROES_CRISE)


def detectar_inducao_cvm(texto: str) -> bool:
    """Detecta pedido de recomendação específica de ativo, ação ou CDB (Res. CVM 19/20)."""
    norm = _normalizar_texto(texto)
    return any(p.search(norm) for p in _PADROES_CVM)
