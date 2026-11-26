from uuid import UUID

from fastapi import APIRouter, Response, status

from pandora_api.adaptadores.http.dependencias import ConteinerDep, UsuarioDep
from pandora_api.adaptadores.http.esquemas import ConsentimentoEntrada, ConsentimentoSaida
from pandora_api.adaptadores.http.problemas import respostas

router = APIRouter(tags=["privacidade"], responses=respostas(401))


def _saida(c) -> ConsentimentoSaida:
    return ConsentimentoSaida(
        id=c.id,
        finalidade=c.finalidade,
        versao_termo=c.versao_termo,
        aceito_em=c.aceito_em,
        revogado_em=c.revogado_em,
        ativo=c.ativo,
    )


@router.post("/consentimentos", status_code=status.HTTP_201_CREATED, summary="Registrar consentimento")
def registrar_consentimento(dados: ConsentimentoEntrada, usuario: UsuarioDep, c: ConteinerDep) -> ConsentimentoSaida:
    return _saida(c.consentimentos.registrar(usuario.id, dados.finalidade, dados.versao_termo))


@router.get("/consentimentos", summary="Listar consentimentos, do mais novo ao mais antigo")
def listar_consentimentos(usuario: UsuarioDep, c: ConteinerDep) -> list[ConsentimentoSaida]:
    return [_saida(x) for x in c.consentimentos.listar(usuario.id)]


@router.post("/consentimentos/{consentimento_id}/revogacao", summary="Revogar consentimento", responses=respostas(404))
def revogar_consentimento(consentimento_id: UUID, usuario: UsuarioDep, c: ConteinerDep) -> ConsentimentoSaida:
    return _saida(c.consentimentos.revogar(usuario.id, consentimento_id))


@router.delete(
    "/eu/dados",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Apagar todos os meus dados",
    description="Exclusão total e imediata: conta, sessões, consentimentos e tudo o que vier a ser guardado (RNF01).",
)
def apagar_tudo(usuario: UsuarioDep, c: ConteinerDep) -> Response:
    c.privacidade.apagar_tudo(usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
