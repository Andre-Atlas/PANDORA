from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from pandora_api.portas.repositorios import ApagaDadosDoUsuario


class Privacidade:
    """Exclusão total dos dados da pessoa (RNF01, LGPD art. 18, VI)."""

    def __init__(self, repositorios: Sequence[ApagaDadosDoUsuario]) -> None:
        self._repositorios = repositorios

    def apagar_tudo(self, usuario_id: UUID) -> None:
        # O usuário vai por último: se algo falhar no meio, a conta continua
        # existindo e a pessoa pode pedir de novo.
        for repo in self._repositorios:
            repo.apagar_do_usuario(usuario_id)
