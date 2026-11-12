"""Esquemas do contrato. Valores em centavos inteiros; taxas em decimal (string no JSON)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import IntEnum, StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from pandora_api.dominio.consentimento import Finalidade
from pandora_api.dominio.extrato import StatusExtrato
from pandora_api.dominio.transacao import Categoria, FormaPagamento, OrigemCategoria
from pandora_api.dominio.usuario import TAMANHO_MINIMO_SENHA


class Esquema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Sistema ---------------------------------------------------------------


class Saude(Esquema):
    status: Literal["ok"] = "ok"
    versao: str


# --- Conta e sessão --------------------------------------------------------


class Cadastro(Esquema):
    email: EmailStr
    senha: str = Field(min_length=TAMANHO_MINIMO_SENHA, max_length=128)


class Credenciais(Esquema):
    email: EmailStr
    senha: str = Field(max_length=128)


class UsuarioSaida(Esquema):
    id: UUID
    email: EmailStr
    criado_em: datetime


class SessaoSaida(Esquema):
    token: str = Field(description="Envie em `Authorization: Bearer <token>`. Só é mostrado agora.")
    tipo: Literal["Bearer"] = "Bearer"
    expira_em: datetime


# --- Consentimento (LGPD) --------------------------------------------------


class ConsentimentoEntrada(Esquema):
    finalidade: Finalidade
    versao_termo: str = Field(min_length=1, max_length=40, examples=["2026-11"], description="Versão do termo aceito.")


class ConsentimentoSaida(Esquema):
    id: UUID
    finalidade: Finalidade
    versao_termo: str
    aceito_em: datetime
    revogado_em: datetime | None
    ativo: bool


# --- Cálculo determinístico ------------------------------------------------


class EntradaCalculo(Esquema):
    nome: str = Field(examples=["Renda do mês"])
    valor: str = Field(examples=["R$ 2.850,00"])


class Calculo(Esquema):
    """Presente em todo valor que vem do motor determinístico (RNF03).

    O front mostra o selo "Calculado" só quando este bloco existe.
    """

    fonte: Literal["motor_deterministico"] = "motor_deterministico"
    entradas: list[EntradaCalculo] = Field(description="Valores usados no cálculo (#65).")


# --- Transações (rascunho do esquema único) --------------------------------


class ParcelaSaida(Esquema):
    numero: int = Field(ge=1)
    total: int = Field(ge=1)


class TransacaoSaida(Esquema):
    """RASCUNHO: segue o dataset sintético da #51; falta fechar com a ingestão (#57).

    Enquanto o classificador da #68 não é servido, `versao_modelo` começa com `provisorio-`.
    """

    id: UUID
    conta_id: str
    data_hora: datetime
    valor_centavos: int = Field(description="Negativo para saída, positivo para entrada.")
    forma_pagamento: FormaPagamento
    descricao_mascarada: str = Field(description="Sem nome, CPF ou conta (RNF01).")
    mcc: str | None = Field(None, pattern=r"^\d{4}$")
    categoria: Categoria
    origem_categoria: OrigemCategoria
    confianca_categoria: float | None = Field(None, ge=0, le=1)
    versao_modelo: str | None = None
    essencial: bool = Field(description="Faz parte do Mínimo Existencial (Lei 14.181/2021).")
    parcela: ParcelaSaida | None = None


class PaginaTransacoes(Esquema):
    itens: list[TransacaoSaida]
    total: int
    pagina: int
    por_pagina: int


class CorrecaoCategoria(Esquema):
    categoria: Categoria


# --- Raio-X ----------------------------------------------------------------


class GastoPorCategoria(Esquema):
    categoria: Categoria
    total_centavos: int = Field(description="Saídas do mês nesta categoria, em valor positivo.")
    essencial_centavos: int = Field(description="Parte do total que é Mínimo Existencial.")


class RaioX(Esquema):
    mes: str = Field(pattern=r"^\d{4}-\d{2}$", examples=["2026-10"])
    renda_centavos: int
    minimo_existencial_centavos: int = Field(
        description="Soma dos gastos essenciais do mês. Protegido: nenhum plano mexe nesse valor."
    )
    folga_centavos: int = Field(description="Renda menos Mínimo Existencial. Negativa quando o essencial não cabe.")
    gastos: list[GastoPorCategoria] = Field(
        description="Da maior para a menor. Sem RENDA, TRANSFERENCIA (inclui pagar a fatura inteira) e INVESTIMENTO."
    )
    calculo: Calculo


# --- Upload de extrato -----------------------------------------------------


class ExtratoSaida(Esquema):
    id: UUID
    nome_arquivo: str
    status: StatusExtrato
    transacoes_importadas: int | None = None
    avisos: list[str] = Field(default_factory=list, description="Ex.: linhas que não deu para ler. Nada é inventado.")
    recebido_em: datetime


# --- Dívidas, score e plano ------------------------------------------------


class AlertaDivida(Esquema):
    tipo: Literal["risco_corte", "teto_rotativo", "acima_media_bcb"]
    mensagem: str


class DividaSaida(Esquema):
    id: UUID
    credor: str
    saldo_centavos: int
    parcela_mensal_centavos: int | None
    cet_anual: Decimal = Field(description="Custo efetivo total ao ano, em %.")
    media_bcb_cet_anual: Decimal | None = Field(None, description="Média do BCB para a modalidade, em % ao ano.")
    serie_sgs: str | None = Field(None, examples=["22022"])
    dias_atraso: int = Field(ge=0)
    servico_essencial: bool = Field(description="Ex.: luz e água, com risco de corte.")
    alertas: list[AlertaDivida]
    calculo: Calculo


class ComponenteScore(Esquema):
    nome: Literal["comprometimento_renda", "custo_medio_divida", "reserva", "dias_sem_apostas"]
    valor: int = Field(ge=0, le=100)
    peso: Decimal


class Score(Esquema):
    valor: int = Field(ge=0, le=100)
    componentes: list[ComponenteScore]
    calculo: Calculo


class MetodoPlano(StrEnum):
    AVALANCHE = "avalanche"
    BOLA_DE_NEVE = "bola_de_neve"


class PlanoEntrada(Esquema):
    metodo: MetodoPlano


class ItemPlano(Esquema):
    posicao: int = Field(ge=1)
    divida_id: UUID
    motivo: str = Field(examples=["Maior custo total (CET)"])


class Plano(Esquema):
    metodo: MetodoPlano
    minimo_existencial_centavos: int
    folga_mensal_centavos: int
    ordem: list[ItemPlano]
    calculo: Calculo


# --- Previsão de caixa -----------------------------------------------------


class Horizonte(IntEnum):
    DIAS_30 = 30
    DIAS_60 = 60
    DIAS_90 = 90


class PontoPrevisao(Esquema):
    data: date
    saldo_previsto_centavos: int
    faixa_inferior_centavos: int
    faixa_superior_centavos: int


class Previsao(Esquema):
    horizonte_dias: Horizonte
    pontos: list[PontoPrevisao]
    probabilidade_furo: float = Field(ge=0, le=1)
    alerta_furo: str | None = Field(None, description="Texto sem culpar a pessoa.")


# --- Chat com a Elpis ------------------------------------------------------


class PerguntaChat(Esquema):
    pergunta: str = Field(min_length=1, max_length=2000)
    conversa_id: UUID | None = None


class CitacaoSaida(Esquema):
    """Mesmo formato da `Citacao` do RAG (services/rag, generate/answer.py)."""

    n: int
    norma: str
    artigo: str | None
    link: str
    trecho: str
    pagina: int | None = None
    ressalva: str | None = Field(None, description="Aviso de vigência da norma, quando houver.")


class RespostaChat(Esquema):
    texto: str
    abstencao: bool = Field(description="True quando não há fonte suficiente: o front mostra 'Sem fonte suficiente'.")
    citacoes: list[CitacaoSaida]
    crise: bool = Field(False, description="O classificador de crise (#64) disparou: o front abre o fluxo de crise.")
    modelo: str


# --- Trilha ----------------------------------------------------------------


class EtapaTrilha(Esquema):
    """Um degrau do `TrilhaCaminho`. O estado (feito, atual, próximo) é do navegador de quem usa."""

    n: int
    t: str = Field(description="Título da etapa.")
    x: int = Field(description="Posição horizontal no desenho do caminho.")
    lado: Literal["d", "e"]
    marco: str | None
    emblema: str
    licao_id: str


class PerguntaTrilha(Esquema):
    enunciado: str
    opcoes: list[str]
    certa: int = Field(description="Índice da opção correta em `opcoes`.")
    feedback: str = Field(description="Explicação com citação `[n]`, que aponta para `fontes` da lição.")
    citacoes: list[int]


class LicaoSaida(Esquema):
    id: str
    titulo: str
    explicacao: str
    citacoes_explicacao: list[int]
    fontes: list[CitacaoSaida]
    perguntas: list[PerguntaTrilha]


class PorqueEntrada(Esquema):
    pergunta_idx: int = Field(ge=0, description="Posição da pergunta em `perguntas` da lição.")
    opcao: int = Field(ge=0, description="Índice da opção que a pessoa escolheu.")
