from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from pandora_api.adaptadores.http.conteiner import Conteiner
from pandora_api.dominio.erros import SessaoInvalida
from pandora_api.dominio.usuario import Usuario

_bearer = HTTPBearer(auto_error=False, description="Token de `POST /auth/sessoes`.")


def conteiner(request: Request) -> Conteiner:
    return request.app.state.conteiner


def token_atual(credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]) -> str:
    if credenciais is None:
        raise SessaoInvalida()
    return credenciais.credentials


def usuario_atual(token: Annotated[str, Depends(token_atual)], c: Annotated[Conteiner, Depends(conteiner)]) -> Usuario:
    return c.contas.usuario_da_sessao(token)


ConteinerDep = Annotated[Conteiner, Depends(conteiner)]
UsuarioDep = Annotated[Usuario, Depends(usuario_atual)]
TokenDep = Annotated[str, Depends(token_atual)]
