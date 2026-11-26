from __future__ import annotations

from typing import Protocol

from pandora_api.dominio.trilha import Etapa


class RepositorioTrilha(Protocol):
    def etapas(self) -> list[Etapa]: ...
