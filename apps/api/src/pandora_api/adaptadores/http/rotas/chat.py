"""Elpis: pergunta com resposta fundamentada em fontes oficiais.

Rota pública: o app ainda não tem login e nada aqui guarda dado pessoal.
"""

from fastapi import APIRouter

from pandora_api.adaptadores.http.dependencias import ConteinerDep
from pandora_api.adaptadores.http.esquemas import CitacaoSaida, PerguntaChat, RespostaChat
from pandora_api.adaptadores.http.problemas import respostas
from pandora_api.portas.assistente import RespostaElpis

router = APIRouter(tags=["chat"], responses=respostas(503))


def saida_do_chat(r: RespostaElpis) -> RespostaChat:
    return RespostaChat(
        texto=r.texto,
        abstencao=r.abstencao,
        citacoes=[CitacaoSaida.model_validate(c) for c in r.citacoes],
        crise=r.crise,
        modelo=r.modelo,
    )


@router.post(
    "/chat",
    summary="Perguntar à Elpis (RF09)",
    description=(
        "Responde só com base nas fontes oficiais, sempre com citação. Sem fonte suficiente, devolve `abstencao`. "
        "Sinais de crise devolvem `crise` e os contatos de apoio, sem consultar o modelo. "
        "Pública, sem token: o app ainda não tem login. Leva de 8 a 15 s."
    ),
)
def perguntar(dados: PerguntaChat, c: ConteinerDep) -> RespostaChat:
    return saida_do_chat(c.chat.perguntar(dados.pergunta))
