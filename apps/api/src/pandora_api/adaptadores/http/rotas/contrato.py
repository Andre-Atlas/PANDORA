"""Rotas que já estão no contrato, mas são implementadas por outras issues.

Respondem 501 com o número da issue. Nada de dados inventados.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from pandora_api.adaptadores.http.dependencias import UsuarioDep
from pandora_api.adaptadores.http.esquemas import (
    DividaSaida,
    Horizonte,
    Plano,
    PlanoEntrada,
    Previsao,
    Score,
)
from pandora_api.adaptadores.http.problemas import NaoImplementado, respostas

dividas = APIRouter(tags=["dividas"], responses=respostas(401, 501))
previsao = APIRouter(tags=["previsao"], responses=respostas(401, 501))


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
