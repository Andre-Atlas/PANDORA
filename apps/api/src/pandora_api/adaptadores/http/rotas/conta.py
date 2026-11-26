from fastapi import APIRouter, Response, status

from pandora_api.adaptadores.http.dependencias import ConteinerDep, TokenDep, UsuarioDep
from pandora_api.adaptadores.http.esquemas import Cadastro, Credenciais, SessaoSaida, UsuarioSaida
from pandora_api.adaptadores.http.problemas import respostas

router = APIRouter(tags=["conta"])


@router.post(
    "/auth/cadastro", status_code=status.HTTP_201_CREATED, summary="Criar conta", responses=respostas(409, 422)
)
def cadastrar(dados: Cadastro, c: ConteinerDep) -> UsuarioSaida:
    return UsuarioSaida.model_validate(c.contas.cadastrar(dados.email, dados.senha))


@router.post("/auth/sessoes", status_code=status.HTTP_201_CREATED, summary="Entrar", responses=respostas(401))
def entrar(dados: Credenciais, c: ConteinerDep) -> SessaoSaida:
    sessao = c.contas.entrar(dados.email, dados.senha)
    return SessaoSaida(token=sessao.token, expira_em=sessao.expira_em)


@router.delete("/auth/sessoes/atual", status_code=status.HTTP_204_NO_CONTENT, summary="Sair", responses=respostas(401))
def sair(token: TokenDep, c: ConteinerDep) -> Response:
    c.contas.usuario_da_sessao(token)
    c.contas.sair(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/eu", summary="Quem está conectado", responses=respostas(401))
def eu(usuario: UsuarioDep) -> UsuarioSaida:
    return UsuarioSaida.model_validate(usuario)
