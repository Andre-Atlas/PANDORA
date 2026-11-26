"""Trilha de educação financeira: etapas, lições com fontes e o "por quê?" respondido pela Elpis.

Rotas públicas, como o chat: o conteúdo é o mesmo para todos e o progresso fica no navegador.
"""

from fastapi import APIRouter

from pandora_api.adaptadores.http.dependencias import ConteinerDep
from pandora_api.adaptadores.http.esquemas import EtapaTrilha, LicaoSaida, PorqueEntrada, RespostaChat
from pandora_api.adaptadores.http.problemas import respostas
from pandora_api.adaptadores.http.rotas.chat import saida_do_chat

router = APIRouter(tags=["trilha"], responses=respostas(404))


@router.get("/trilha", summary="Etapas da trilha")
def listar_etapas(c: ConteinerDep) -> list[EtapaTrilha]:
    return [
        EtapaTrilha(n=e.n, t=e.t, x=e.x, lado=e.lado, marco=e.marco, emblema=e.emblema, licao_id=e.licao.id)
        for e in c.trilha.etapas()
    ]


@router.get("/trilha/licoes/{licao_id}", summary="Lição com explicação, fontes e perguntas")
def obter_licao(licao_id: str, c: ConteinerDep) -> LicaoSaida:
    return LicaoSaida.model_validate(c.trilha.licao(licao_id), from_attributes=True)


@router.post(
    "/trilha/licoes/{licao_id}/porque",
    summary="Por quê? A Elpis explica a resposta de uma questão, com fontes",
    description="Leva de 8 a 15 s, como o chat.",
    responses=respostas(422, 503),
)
def explicar_resposta(licao_id: str, dados: PorqueEntrada, c: ConteinerDep) -> RespostaChat:
    return saida_do_chat(c.trilha.porque(licao_id, dados.pergunta_idx, dados.opcao))
