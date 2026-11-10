"""Rotas que já estão no contrato, mas são implementadas por outras issues.

Respondem 501 com o número da issue. Nada de dados inventados.
"""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile, status

from pandora_api.adaptadores.http.dependencias import ConteinerDep, UsuarioDep
from pandora_api.adaptadores.http.esquemas import (
    CorrecaoCategoria,
    DividaSaida,
    ExtratoSaida,
    Horizonte,
    PaginaTransacoes,
    PerguntaChat,
    Plano,
    PlanoEntrada,
    Previsao,
    RaioX,
    RespostaChat,
    Score,
    TransacaoSaida,
)
from pandora_api.adaptadores.http.problemas import NaoImplementado, respostas
from pandora_api.dominio.consentimento import Finalidade
from pandora_api.dominio.transacao import Categoria

Mes = Annotated[str, Query(pattern=r"^\d{4}-\d{2}$", examples=["2026-10"])]

raio_x = APIRouter(tags=["raio-x"], responses=respostas(401, 501))
dividas = APIRouter(tags=["dividas"], responses=respostas(401, 501))
previsao = APIRouter(tags=["previsao"], responses=respostas(401, 501))
chat = APIRouter(tags=["chat"], responses=respostas(401, 501))


@raio_x.post(
    "/extratos",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar extrato ou fatura (OFX, CSV ou PDF)",
    description=(
        "Exige consentimento ativo para `diagnostico_financeiro`. O conteúdo do arquivo é tratado só como dado."
    ),
    responses=respostas(403),
)
def enviar_extrato(arquivo: Annotated[UploadFile, File()], usuario: UsuarioDep, c: ConteinerDep) -> ExtratoSaida:
    c.consentimentos.exigir(usuario.id, Finalidade.DIAGNOSTICO_FINANCEIRO)
    raise NaoImplementado(72, "O envio de extratos")


@raio_x.get("/extratos/{extrato_id}", summary="Situação de um extrato enviado")
def situacao_extrato(extrato_id: UUID, usuario: UsuarioDep) -> ExtratoSaida:
    raise NaoImplementado(72, "A situação do extrato")


@raio_x.get("/transacoes", summary="Listar transações")
def listar_transacoes(
    usuario: UsuarioDep,
    mes: Mes | None = None,
    categoria: Categoria | None = None,
    pagina: Annotated[int, Query(ge=1)] = 1,
    por_pagina: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PaginaTransacoes:
    raise NaoImplementado(72, "A lista de transações")


@raio_x.patch("/transacoes/{transacao_id}/categoria", summary="Corrigir a categoria com um toque (RF10)")
def corrigir_categoria(transacao_id: UUID, dados: CorrecaoCategoria, usuario: UsuarioDep) -> TransacaoSaida:
    raise NaoImplementado(72, "A correção de categoria")


@raio_x.get("/raio-x", summary="Raio-X do mês")
def obter_raio_x(usuario: UsuarioDep, mes: Mes) -> RaioX:
    raise NaoImplementado(72, "O Raio-X")


@dividas.get("/dividas", summary="Mapa de dívidas, com CET comparado à média do BCB (RF03)")
def listar_dividas(usuario: UsuarioDep) -> list[DividaSaida]:
    raise NaoImplementado(72, "O mapa de dívidas")


@dividas.get("/score", summary="Score de saúde financeira explicável (RF10)")
def obter_score(usuario: UsuarioDep) -> Score:
    raise NaoImplementado(72, "O score")


@dividas.post("/plano", summary="Plano de pagamento: Avalanche ou Bola de Neve (RF06)")
def gerar_plano(dados: PlanoEntrada, usuario: UsuarioDep) -> Plano:
    raise NaoImplementado(71, "O plano de pagamento")


@previsao.get("/previsao", summary="Previsão de caixa para 30, 60 ou 90 dias (RF13)")
def obter_previsao(
    usuario: UsuarioDep,
    horizonte: Annotated[Horizonte, Query(description="Dias à frente: 30, 60 ou 90.")] = Horizonte.DIAS_30,
    a_partir_de: date | None = None,
) -> Previsao:
    raise NaoImplementado(84, "A previsão de caixa")


@chat.post("/chat", summary="Perguntar à Elpis (RF09)")
def perguntar(dados: PerguntaChat, usuario: UsuarioDep) -> RespostaChat:
    raise NaoImplementado(85, "O chat com a Elpis")
