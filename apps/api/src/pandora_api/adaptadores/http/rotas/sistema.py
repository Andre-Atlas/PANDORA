from fastapi import APIRouter

from pandora_api import __version__
from pandora_api.adaptadores.http.esquemas import Saude

router = APIRouter(tags=["sistema"])


@router.get("/saude", summary="A API está no ar")
def saude() -> Saude:
    return Saude(versao=__version__)
