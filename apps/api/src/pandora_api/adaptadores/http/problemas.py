"""Erros no formato application/problem+json (RFC 9457)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pandora_api.dominio import erros


class Problema(BaseModel):
    type: str = Field(examples=["urn:pandora:erro:nao-implementado"])
    title: str
    status: int
    detail: str | None = None
    issue: int | None = Field(None, description="Issue do GitHub que vai implementar o recurso (só em 501).")


class NaoImplementado(Exception):
    """Rota que já está no contrato, mas cuja implementação é de outra issue."""

    def __init__(self, issue: int, recurso: str) -> None:
        super().__init__(recurso)
        self.issue = issue
        self.recurso = recurso


def _resposta(status: int, codigo: str, titulo: str, detalhe: str | None = None, **extra) -> JSONResponse:
    corpo = Problema(type=f"urn:pandora:erro:{codigo}", title=titulo, status=status, detail=detalhe, **extra)
    return JSONResponse(
        corpo.model_dump(exclude_none=True),
        status_code=status,
        media_type="application/problem+json",
        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
    )


def registrar_tratadores(app: FastAPI) -> None:
    tabela: list[tuple[type[Exception], int, str, str]] = [
        (erros.EmailJaCadastrado, 409, "email-ja-cadastrado", "Este e-mail já tem conta."),
        (erros.SenhaFraca, 422, "senha-fraca", "A senha é curta demais."),
        (erros.CredenciaisInvalidas, 401, "credenciais-invalidas", "E-mail ou senha não conferem."),
        (erros.SessaoInvalida, 401, "sessao-invalida", "Entre de novo para continuar."),
        (erros.ConsentimentoNaoEncontrado, 404, "consentimento-nao-encontrado", "Consentimento não encontrado."),
        (erros.LicaoNaoEncontrada, 404, "licao-nao-encontrada", "Lição não encontrada."),
        (erros.PerguntaInvalida, 422, "pergunta-invalida", "A pergunta ou a opção não existe nesta lição."),
        (erros.AssistenteIndisponivel, 503, "elpis-indisponivel", "A Elpis não está disponível agora."),
    ]
    for classe, status, codigo, titulo in tabela:

        async def tratar(_: Request, exc: Exception, status=status, codigo=codigo, titulo=titulo) -> JSONResponse:
            detalhe = str(exc) if isinstance(exc, erros.SenhaFraca) else None
            return _resposta(status, codigo, titulo, detalhe)

        app.add_exception_handler(classe, tratar)

    async def consentimento(_: Request, exc: erros.ConsentimentoNecessario) -> JSONResponse:
        return _resposta(
            403,
            "consentimento-necessario",
            "Falta o seu consentimento.",
            f"Registre um consentimento para '{exc.finalidade}' em POST /consentimentos antes de continuar.",
        )

    async def nao_implementado(_: Request, exc: NaoImplementado) -> JSONResponse:
        return _resposta(
            501,
            "nao-implementado",
            "Ainda não implementado.",
            f"{exc.recurso} chega na issue #{exc.issue}.",
            issue=exc.issue,
        )

    app.add_exception_handler(erros.ConsentimentoNecessario, consentimento)
    app.add_exception_handler(NaoImplementado, nao_implementado)


def respostas(*status: int) -> dict[int | str, dict]:
    """Documenta respostas de erro no OpenAPI."""
    return {s: {"model": Problema, "content": {"application/problem+json": {}}} for s in status}
