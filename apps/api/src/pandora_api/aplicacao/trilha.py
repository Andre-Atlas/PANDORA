from __future__ import annotations

from pandora_api.dominio.erros import LicaoNaoEncontrada, PerguntaInvalida
from pandora_api.dominio.trilha import Etapa, Licao
from pandora_api.portas.assistente import AssistenteElpis, RespostaElpis
from pandora_api.portas.trilha import RepositorioTrilha


class Trilha:
    def __init__(self, repositorio: RepositorioTrilha, assistente: AssistenteElpis) -> None:
        self._etapas = repositorio.etapas()
        self._assistente = assistente

    def etapas(self) -> list[Etapa]:
        return list(self._etapas)

    def licao(self, licao_id: str) -> Licao:
        for e in self._etapas:
            if e.licao.id == licao_id:
                return e.licao
        raise LicaoNaoEncontrada(licao_id)

    def porque(self, licao_id: str, pergunta_idx: int, opcao: int) -> RespostaElpis:
        """Explica a resposta de uma questão. A pergunta vai completa, para a busca achar as fontes certas."""
        licao = self.licao(licao_id)
        if not 0 <= pergunta_idx < len(licao.perguntas):
            raise PerguntaInvalida(f"pergunta {pergunta_idx}")
        p = licao.perguntas[pergunta_idx]
        if not 0 <= opcao < len(p.opcoes):
            raise PerguntaInvalida(f"opção {opcao}")
        certa, escolhida = p.opcoes[p.certa], p.opcoes[opcao]
        pergunta = f'{p.enunciado} Por que a resposta correta é "{certa}"?'
        if opcao != p.certa:
            pergunta += f' E por que não "{escolhida}"?'
        contexto = (
            f'Questão de múltipla escolha da lição "{licao.titulo}". '
            f"Resposta certa: {certa}. Resposta escolhida pela pessoa: {escolhida}."
        )
        return self._assistente.responder(pergunta, contexto)
