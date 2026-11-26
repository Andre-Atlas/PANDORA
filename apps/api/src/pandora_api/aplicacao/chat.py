from __future__ import annotations

from dataclasses import replace

from pandora_api.dominio.crise import detecta_crise
from pandora_api.portas.assistente import AssistenteElpis, RespostaElpis

MENSAGEM_CRISE = (
    "Sinto muito que esteja tão pesado. Você não precisa passar por isso sozinho. "
    "Se pensa em se machucar, ligue agora para o CVV no 188 (24 horas, gratuito) ou para o SAMU no 192. "
    "Deixei os contatos de apoio na tela. Quando quiser, a gente volta às dívidas, no seu ritmo."
)


class Chat:
    def __init__(self, assistente: AssistenteElpis) -> None:
        self._assistente = assistente

    def perguntar(self, pergunta: str, contexto: str | None = None) -> RespostaElpis:
        if detecta_crise(pergunta):
            # Em crise, a prioridade é o acolhimento e os contatos: nada de buscar fontes nem chamar o modelo.
            return RespostaElpis(MENSAGEM_CRISE, abstencao=True, modelo="regra-crise", crise=True)
        resposta = self._assistente.responder(pergunta, contexto)
        return replace(resposta, crise=False)
