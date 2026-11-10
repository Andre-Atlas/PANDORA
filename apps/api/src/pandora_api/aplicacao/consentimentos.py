from __future__ import annotations

from uuid import UUID, uuid4

from pandora_api.dominio.consentimento import Consentimento, Finalidade
from pandora_api.dominio.erros import ConsentimentoNaoEncontrado, ConsentimentoNecessario
from pandora_api.portas.repositorios import RepositorioConsentimentos
from pandora_api.portas.servicos import Relogio


class Consentimentos:
    def __init__(self, repositorio: RepositorioConsentimentos, relogio: Relogio) -> None:
        self._repo = repositorio
        self._relogio = relogio

    def registrar(self, usuario_id: UUID, finalidade: Finalidade, versao_termo: str) -> Consentimento:
        consentimento = Consentimento(uuid4(), usuario_id, finalidade, versao_termo, self._relogio.agora())
        self._repo.adicionar(consentimento)
        return consentimento

    def listar(self, usuario_id: UUID) -> list[Consentimento]:
        return sorted(self._repo.do_usuario(usuario_id), key=lambda c: c.aceito_em, reverse=True)

    def revogar(self, usuario_id: UUID, consentimento_id: UUID) -> Consentimento:
        consentimento = self._repo.por_id(consentimento_id)
        if consentimento is None or consentimento.usuario_id != usuario_id:
            raise ConsentimentoNaoEncontrado()
        revogado = consentimento.revogar(self._relogio.agora())
        self._repo.atualizar(revogado)
        return revogado

    def exigir(self, usuario_id: UUID, finalidade: Finalidade) -> None:
        """Barra a operação se não houver consentimento ativo para a finalidade."""
        if not any(c.ativo and c.finalidade == finalidade for c in self._repo.do_usuario(usuario_id)):
            raise ConsentimentoNecessario(finalidade)
