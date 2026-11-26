"""Raio-X (#72): envio de extrato, transações, correção de categoria e Raio-X do mês."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile, status

from pandora_api.adaptadores.http.dependencias import ConteinerDep, UsuarioDep
from pandora_api.adaptadores.http.esquemas import (
    Calculo,
    CorrecaoCategoria,
    EntradaCalculo,
    ExtratoSaida,
    GastoPorCategoria,
    PaginaTransacoes,
    ParcelaSaida,
    RaioX,
    TransacaoSaida,
)
from pandora_api.adaptadores.http.problemas import respostas
from pandora_api.dominio import raio_x as dominio
from pandora_api.dominio.extrato import TAMANHO_MAXIMO_BYTES, Extrato
from pandora_api.dominio.transacao import Categoria, Transacao

Mes = Annotated[str, Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", examples=["2026-10"])]

router = APIRouter(tags=["raio-x"], responses=respostas(401))


def _extrato(e: Extrato) -> ExtratoSaida:
    return ExtratoSaida(
        id=e.id,
        nome_arquivo=e.nome_arquivo,
        status=e.status,
        transacoes_importadas=e.transacoes_importadas,
        avisos=list(e.avisos),
        recebido_em=e.recebido_em,
    )


def _transacao(t: Transacao) -> TransacaoSaida:
    return TransacaoSaida(
        id=t.id,
        conta_id=t.conta_id,
        data_hora=t.data_hora,
        valor_centavos=t.valor_centavos,
        forma_pagamento=t.forma_pagamento,
        descricao_mascarada=t.descricao_mascarada,
        mcc=t.mcc,
        categoria=t.categoria,
        origem_categoria=t.origem_categoria,
        confianca_categoria=t.confianca_categoria,
        versao_modelo=t.versao_modelo,
        essencial=t.essencial,
        parcela=ParcelaSaida(numero=t.parcela.numero, total=t.parcela.total) if t.parcela else None,
    )


def _reais(centavos: int) -> str:
    sinal = "-" if centavos < 0 else ""
    inteiro, resto = divmod(abs(centavos), 100)
    return f"{sinal}R$ {inteiro:,}".replace(",", ".") + f",{resto:02d}"


def _raio_x(r: dominio.RaioX) -> RaioX:
    return RaioX(
        mes=r.mes,
        renda_centavos=r.renda_centavos,
        minimo_existencial_centavos=r.minimo_existencial_centavos,
        folga_centavos=r.folga_centavos,
        gastos=[
            GastoPorCategoria(
                categoria=g.categoria, total_centavos=g.total_centavos, essencial_centavos=g.essencial_centavos
            )
            for g in r.gastos
        ],
        calculo=Calculo(
            entradas=[
                EntradaCalculo(nome="Transações do mês", valor=str(r.transacoes_consideradas)),
                EntradaCalculo(nome="Renda do mês", valor=_reais(r.renda_centavos)),
                EntradaCalculo(
                    nome="Gastos essenciais (Mínimo Existencial)", valor=_reais(r.minimo_existencial_centavos)
                ),
                EntradaCalculo(nome="Folga = renda − Mínimo Existencial", valor=_reais(r.folga_centavos)),
            ]
        ),
    )


@router.post(
    "/extratos",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar extrato ou fatura (OFX, CSV ou PDF)",
    description=(
        "Exige consentimento ativo para `diagnostico_financeiro`. O conteúdo do arquivo é tratado só como dado. "
        f"Até {TAMANHO_MAXIMO_BYTES // (1024 * 1024)} MB. Hoje só CSV é lido: OFX (#57) e PDF (#66) voltam com "
        "`status = falhou` e o motivo em `avisos`. Linhas já importadas não entram de novo."
    ),
    responses=respostas(403, 413),
)
def enviar_extrato(arquivo: Annotated[UploadFile, File()], usuario: UsuarioDep, c: ConteinerDep) -> ExtratoSaida:
    # Rota síncrona: o FastAPI a roda numa thread, e o banco não trava o loop.
    # Lê um byte além do limite: basta para saber se passou, sem carregar um arquivo enorme na memória.
    conteudo = arquivo.file.read(TAMANHO_MAXIMO_BYTES + 1)
    return _extrato(c.extratos.enviar(usuario.id, arquivo.filename or "extrato", conteudo))


@router.get("/extratos/{extrato_id}", summary="Situação de um extrato enviado", responses=respostas(404))
def situacao_extrato(extrato_id: UUID, usuario: UsuarioDep, c: ConteinerDep) -> ExtratoSaida:
    return _extrato(c.extratos.situacao(usuario.id, extrato_id))


@router.get("/transacoes", summary="Listar transações, da mais nova para a mais antiga")
def listar_transacoes(
    usuario: UsuarioDep,
    c: ConteinerDep,
    mes: Mes | None = None,
    categoria: Categoria | None = None,
    pagina: Annotated[int, Query(ge=1)] = 1,
    por_pagina: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PaginaTransacoes:
    itens, total = c.transacoes.listar(usuario.id, mes, categoria, pagina, por_pagina)
    return PaginaTransacoes(itens=[_transacao(t) for t in itens], total=total, pagina=pagina, por_pagina=por_pagina)


@router.patch(
    "/transacoes/{transacao_id}/categoria",
    summary="Corrigir a categoria com um toque (RF10)",
    description="A correção da pessoa vence a do modelo (`origem_categoria = pessoa`) e recalcula se é essencial.",
    responses=respostas(404),
)
def corrigir_categoria(
    transacao_id: UUID, dados: CorrecaoCategoria, usuario: UsuarioDep, c: ConteinerDep
) -> TransacaoSaida:
    return _transacao(c.transacoes.corrigir_categoria(usuario.id, transacao_id, dados.categoria))


@router.get(
    "/raio-x",
    summary="Raio-X do mês",
    description="Mês no horário de Brasília. Sem transações no mês, tudo vem zerado e `gastos` vazio.",
)
def obter_raio_x(usuario: UsuarioDep, c: ConteinerDep, mes: Mes) -> RaioX:
    return _raio_x(c.transacoes.raio_x(usuario.id, mes))
