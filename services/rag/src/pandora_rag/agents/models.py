"""Contratos Pydantic tipados compartilhados entre os 7 agentes do PANDORA."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TipoMidia = Literal[
    "imagem_documento",
    "pdf_documento",
    "extrato_arquivo",
    "audio_voz",
    "audio_tts_saida",
]

AgentRole = Literal[
    "perceiver",
    "orquestrador",
    "analista",
    "estrategista",
    "coach",
    "guardiao",
    "educador",
    "compliance",
]

TipoMensagem = Literal[
    "percepcao",
    "roteamento",
    "analise",
    "solicitacao_pesquisa",
    "evidencia",
    "sintese",
    "validacao",
    "revisao",
    "entrega",
]


class MensagemAgente(BaseModel):
    """Registro tipado de cada colaboração ou handoff no trace do grafo."""

    ordem: int = Field(ge=1)
    origem: AgentRole
    destino: AgentRole
    tipo: TipoMensagem
    resumo: str
    dados_chave: dict[str, Any] = Field(default_factory=dict)


class TransacaoPersona(BaseModel):
    """Representação tipada de uma linha do dataset sintético de transações."""

    transaction_id: str
    persona_id: str
    posted_at: str
    amount: float
    payment_method: str
    description_masked: str
    mcc: str
    category: str
    is_bet: bool = False
    anomaly_score: float = 0.0
    ground_truth_note: str = ""


class DividaItem(BaseModel):
    """Contrato de uma obrigação financeira considerada na reestruturação."""

    credor: str
    modalidade: str
    saldo: float = Field(ge=0.0)
    cet_anual_pct: float = Field(ge=0.0)
    parcela_mensal: float = Field(default=0.0, ge=0.0)
    dias_atraso: int = Field(default=0, ge=0)
    essencial: bool = False
    saldo_original: float | None = Field(default=None, ge=0.0)


class DiagnosticoFinanceiro(BaseModel):
    """Saída determinística do AnalistaAgent com renda, mínimo existencial e comparativos SGS."""

    persona_id: str
    renda_mensal: float = Field(ge=0.0)
    minimo_existencial: float = Field(ge=0.0)
    folga_disponivel: float = Field(ge=0.0)
    gasto_dividas_mensal: float = Field(default=0.0, ge=0.0)
    total_dividas: float = Field(default=0.0, ge=0.0)
    comprometimento_dividas_pct: float = Field(default=0.0, ge=0.0)
    dividas_identificadas: list[DividaItem] = Field(default_factory=list)
    comparativos_sgs: dict[str, Any] = Field(default_factory=dict)
    alertas: list[str] = Field(default_factory=list)


class EstrategiaDivida(BaseModel):
    """Ordem de quitação e alocação mensal calculada para uma estratégia."""

    nome: Literal["avalanche", "bola_de_neve"]
    ordem_credores: list[str] = Field(default_factory=list)
    alocacao_mensal: dict[str, float] = Field(default_factory=dict)
    juros_12m_estimado: float = Field(default=0.0, ge=0.0)
    justificativa: str = ""


class PlanoReestruturacao(BaseModel):
    """Plano de reestruturação com blindagem do mínimo existencial e teto da Lei 14.690."""

    minimo_existencial_blindado: float = Field(ge=0.0)
    folga_para_acordos: float = Field(ge=0.0)
    deficit_vital: float = Field(default=0.0, ge=0.0)
    avalanche: EstrategiaDivida
    bola_de_neve: EstrategiaDivida
    estrategia_recomendada: Literal["avalanche", "bola_de_neve"] = "avalanche"
    economia_estimada_juros: float = Field(default=0.0, ge=0.0)
    alerta_teto_rotativo_lei_14690: bool = False
    requer_repactuacao_lei_14181: bool = False
    alertas: list[str] = Field(default_factory=list)


class AnaliseCompulsao(BaseModel):
    """Diagnóstico determinístico de apostas (bets), perda líquida e concentração temporal."""

    total_apostado: float = Field(default=0.0, ge=0.0)
    premios_recebidos: float = Field(default=0.0, ge=0.0)
    perda_liquida: float = Field(default=0.0, ge=0.0)
    pct_renda_comprometida: float = Field(default=0.0, ge=0.0)
    aposta_madrugada_qtd: int = Field(default=0, ge=0)
    aposta_pos_salario: bool = False
    concentracao_risco_pct: float = Field(default=0.0, ge=0.0)
    custo_oportunidade: str = ""
    sugestao_cooling_off_horas: int = Field(default=48, ge=0)
    risco_compulsao: Literal["baixo", "moderado", "alto", "critico"] = "baixo"
    alertas: list[str] = Field(default_factory=list)


class ReferenciaMidia(BaseModel):
    """Ponteiro leve para artefato no ArtifactStore efêmero (zero bytes/base64 no estado)."""

    artefato_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    tipo: TipoMidia
    nome_original_sanitizado: str = Field(max_length=128)
    mime_type: str = Field(max_length=64)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    tamanho_bytes: int = Field(ge=0)


class DadosPixBRCode(BaseModel):
    """Payload EMV BRCode Pix decodificado e validado via CRC-16/CCITT-FALSE."""

    payload_mascarado: str = ""
    crc16_valido: bool = False
    chave_pix_mascarada: str | None = None
    tipo_chave: str | None = None
    nome_recebedor_mascarado: str | None = None
    cidade: str | None = None
    valor_centavos: int | None = Field(default=None, ge=0)
    mcc: str | None = None
    url_dinamica: str | None = None
    suspeito: bool = False
    motivos: list[str] = Field(default_factory=list)


class ExtracaoVisualQuarantinada(BaseModel):
    """Schema fechado emitido pelo VLM Perceiver em quarentena (zero @tools)."""

    tipo_visual: Literal[
        "boleto",
        "print_whatsapp",
        "comprovante_pix",
        "extrato_ou_fatura",
        "outro",
    ] = "outro"
    banco_impresso_no_layout: str | None = None
    beneficiario_impresso: str | None = None
    beneficiario_parece_pf: bool = False
    valor_impresso_centavos: int | None = Field(default=None, ge=0)
    linha_digitavel_visivel: str | None = None
    sinais_engenharia_social: list[str] = Field(default_factory=list)
    possui_instrucao_oculta_suspeita: bool = False


class LancamentoExtratoVLM(BaseModel):
    """Lançamento estruturado extraído pelo VLM no Estágio 2 de extratos PDF."""

    data: str
    descricao: str
    valor_brl: str
    natureza: Literal["D", "C"] = "D"


class ExtratoDocumentalVLM(BaseModel):
    """Estrutura fechada de extrato/fatura retornada pelo VLM em quarentena."""

    eh_fatura_cartao: bool = False
    saldo_inicial_brl: str | None = None
    saldo_final_ou_total_brl: str | None = None
    lancamentos: list[LancamentoExtratoVLM] = Field(default_factory=list)


class ResultadoPercepcaoMultimodal(BaseModel):
    """Consolidação sanitizada produzida pelo PerceiverNode para os 7 agentes."""

    transcricao_voz_mascarada: str | None = None
    codigo_barras_44d: str | None = None
    linha_digitavel_47d: str | None = None
    valor_barras_centavos: int | None = Field(default=None, ge=0)
    dv_geral_mod11_valido: bool | None = None
    pix_brcode: DadosPixBRCode | None = None
    visual: ExtracaoVisualQuarantinada | None = None
    extrato_lido_qtd: int = Field(default=0, ge=0)
    extrato_reconciliado: bool | None = None
    extrato_divergencia_centavos: int = 0
    extrato_estagio_usado: str | None = None
    latencia_percepcao_s: float = Field(default=0.0, ge=0.0)
    modelo_vlm: str | None = None


class ValidacaoBoleto(BaseModel):
    """Resultado da validação estrutural e de módulo 10/11 de linha digitável FEBRABAN."""

    linha_digitavel_limpa: str = ""
    tamanho_valido: bool = False
    digito_verificador_valido: bool = False
    dv_geral_mod11_valido: bool | None = None
    valor_boleto_centavos: int | None = Field(default=None, ge=0)
    divergencia_valor_impresso: bool = False
    codigo_banco_extraido: str | None = None
    banco_alegado: str | None = None
    beneficiario_pf: bool = False
    suspeito: bool = False
    motivos: list[str] = Field(default_factory=list)


class InspecaoFraude(BaseModel):
    """Saída do GuardiaoAgent com sanitização anti-injection, boleto, Pix QR e roteiro MED Pix."""

    texto_sanitizado: str = ""
    injection_detectada: bool = False
    boleto: ValidacaoBoleto | None = None
    pix_brcode: DadosPixBRCode | None = None
    sinais_engenharia_social: list[str] = Field(default_factory=list)
    transacoes_suspeitas: list[TransacaoPersona] = Field(default_factory=list)
    fraude_detectada: bool = False
    roteiro_med_pix: list[str] = Field(default_factory=list)
    prazo_med_dias: int = 80
    alertas: list[str] = Field(default_factory=list)


class CitacaoAgente(BaseModel):
    """Citação rastreável [n] vinculada a documento oficial recuperado pelo RAG."""

    n: int = Field(ge=1)
    norma: str
    artigo: str | None = None
    link: str
    trecho: str
    pagina: int | None = None
    ressalva: str | None = None
    score: float | None = None


class EvidenciaNormativa(BaseModel):
    """Evidências jurídicas/regulatórias consolidadas pelo EducadorAgent."""

    queries_executadas: list[str] = Field(default_factory=list)
    hits_aprovados: int = Field(default=0, ge=0)
    abstencao: bool = False
    citacoes: list[CitacaoAgente] = Field(default_factory=list)
    motivo_abstencao: str | None = None


class VereditoCompliance(BaseModel):
    """Veredito dos 4 invariantes ético-regulatórios avaliados pelo ComplianceAgent."""

    aprovado: bool
    crise_acionada: bool = False
    bloqueio_cvm_acionado: bool = False
    pii_detectada: bool = False
    citacoes_validas: bool = True
    precisou_revisao: bool = False
    motivo_revisao: str | None = None
    alertas: list[str] = Field(default_factory=list)


class EstadoMultiagente(BaseModel):
    """Estado tipado compartilhado ao longo de toda a execução do GrafoPandora."""

    persona_id: str | None = Field(default=None, max_length=64)
    consulta_usuario: str = Field(max_length=8000)
    documento_ocr: str | None = Field(default=None, max_length=20000)
    linha_digitavel: str | None = Field(default=None, max_length=256)
    banco_alegado: str | None = Field(default=None, max_length=256)
    beneficiario_pf: bool = False
    midias: list[ReferenciaMidia] = Field(default_factory=list)
    qrcode_pix_bruto: str | None = Field(default=None, max_length=4096)
    percepcao: ResultadoPercepcaoMultimodal | None = None
    gerar_audio_tts: bool = False
    resumo_falado_tts: str = ""
    audio_saida: ReferenciaMidia | None = None
    consulta_mascarada: str = ""
    pii_contagem: dict[str, int] = Field(default_factory=dict)
    intencoes_detectadas: list[str] = Field(default_factory=list)
    agentes_planejados: list[AgentRole] = Field(default_factory=list)
    transacoes: list[TransacaoPersona] = Field(default_factory=list)
    diagnostico: DiagnosticoFinanceiro | None = None
    plano_dividas: PlanoReestruturacao | None = None
    analise_compulsao: AnaliseCompulsao | None = None
    inspecao_fraude: InspecaoFraude | None = None
    queries_normativas: list[str] = Field(default_factory=list)
    evidencias: EvidenciaNormativa | None = None
    rascunho_resposta: str = ""
    veredito: VereditoCompliance | None = None
    resposta_final: str = ""
    revisoes_realizadas: int = Field(default=0, ge=0)
    trace: list[MensagemAgente] = Field(default_factory=list)
    modo: Literal["deterministico", "hibrido_llm", "langgraph_llm"] = "deterministico"
    modelo_llm: str | None = None
    pareceres_agentes: dict[str, str] = Field(default_factory=dict)
    total_tool_calls: int = Field(default=0, ge=0)

    def registrar_mensagem(
        self,
        origem: AgentRole,
        destino: AgentRole,
        tipo: TipoMensagem,
        resumo: str,
        dados_chave: dict[str, Any] | None = None,
    ) -> MensagemAgente:
        """Acrescenta uma mensagem sequencial numerada ao trace do grafo."""
        msg = MensagemAgente(
            ordem=len(self.trace) + 1,
            origem=origem,
            destino=destino,
            tipo=tipo,
            resumo=resumo,
            dados_chave=dados_chave or {},
        )
        self.trace.append(msg)
        return msg


class ResultadoMultiagente(BaseModel):
    """Resultado consolidado retornado pelo GrafoPandora e serializado pela CLI."""

    persona_id: str | None = None
    consulta_mascarada: str
    modo: Literal["deterministico", "hibrido_llm", "langgraph_llm"] = "deterministico"
    modelo_llm: str | None = None
    total_tool_calls: int = Field(default=0, ge=0)
    pareceres_agentes: dict[str, str] = Field(default_factory=dict)
    latencia_s: float = Field(default=0.0, ge=0.0)
    intencoes_detectadas: list[str] = Field(default_factory=list)
    agentes_acionados: list[AgentRole] = Field(default_factory=list)
    diagnostico: DiagnosticoFinanceiro | None = None
    plano_dividas: PlanoReestruturacao | None = None
    analise_compulsao: AnaliseCompulsao | None = None
    inspecao_fraude: InspecaoFraude | None = None
    evidencias: EvidenciaNormativa | None = None
    veredito: VereditoCompliance | None = None
    percepcao: ResultadoPercepcaoMultimodal | None = None
    resumo_falado_tts: str = ""
    audio_saida: ReferenciaMidia | None = None
    resposta_final: str = ""
    trace: list[MensagemAgente] = Field(default_factory=list)

    @classmethod
    def de_estado(
        cls,
        estado: EstadoMultiagente,
        latencia_s: float = 0.0,
    ) -> ResultadoMultiagente:
        """Constrói o resultado final a partir do estado concluído do grafo."""
        agentes: list[AgentRole] = []
        for msg in estado.trace:
            if msg.origem not in agentes:
                agentes.append(msg.origem)
            if msg.destino not in agentes:
                agentes.append(msg.destino)
        return cls(
            persona_id=estado.persona_id,
            consulta_mascarada=estado.consulta_mascarada,
            modo=estado.modo,
            modelo_llm=estado.modelo_llm,
            total_tool_calls=estado.total_tool_calls,
            pareceres_agentes=dict(estado.pareceres_agentes),
            latencia_s=round(latencia_s, 4),
            intencoes_detectadas=list(estado.intencoes_detectadas),
            agentes_acionados=agentes,
            diagnostico=estado.diagnostico,
            plano_dividas=estado.plano_dividas,
            analise_compulsao=estado.analise_compulsao,
            inspecao_fraude=estado.inspecao_fraude,
            evidencias=estado.evidencias,
            veredito=estado.veredito,
            percepcao=estado.percepcao,
            resumo_falado_tts=estado.resumo_falado_tts,
            audio_saida=estado.audio_saida,
            resposta_final=estado.resposta_final,
            trace=list(estado.trace),
        )
