"""Ponto de entrada: escolhe o parser pelo arquivo, normaliza, tira duplicatas e grava."""
from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import PurePath

from pandora_ingestion.armazem import Armazem
from pandora_ingestion.csv_ import ler_csv
from pandora_ingestion.deduplicar import atribuir_chaves, separar_novas
from pandora_ingestion.erros import FormatoNaoSuportado
from pandora_ingestion.esquema import Leitura
from pandora_ingestion.ofx import ler_ofx
from pandora_ingestion.pdf import ler_pdf

# Só contagens e extensão: nome de arquivo, descrição e valores podem identificar a pessoa.
logger = logging.getLogger("pandora.ingestao")


def ler(
    nome_arquivo: str,
    conteudo: bytes,
    nomes: tuple[str, ...] = (),
    extrator_ocr: Callable[[bytes], Sequence[str]] | None = None,
) -> Leitura:
    """Lê OFX, CSV ou PDF e devolve transações no esquema único, já com chave de deduplicação."""
    extensao = PurePath(nome_arquivo).suffix.lower()
    if extensao in (".ofx", ".qfx"):
        leitura = ler_ofx(conteudo, nomes)
    elif extensao in (".csv", ".txt"):
        leitura = ler_csv(conteudo, nomes)
    elif extensao == ".pdf":
        leitura = ler_pdf(conteudo, nomes, extrator_ocr=extrator_ocr)
    else:
        raise FormatoNaoSuportado("Envie o extrato em OFX, CSV ou PDF.")
    return Leitura(
        tuple(atribuir_chaves(leitura.transacoes)),
        leitura.avisos,
        reconciliado=leitura.reconciliado,
        divergencia_centavos=leitura.divergencia_centavos,
        usou_ocr=leitura.usou_ocr,
    )


@dataclass(frozen=True)
class Resultado:
    lidas: int
    novas: int
    repetidas: int
    avisos: tuple[str, ...]


def importar(nome_arquivo: str, conteudo: bytes, armazem: Armazem, nomes: tuple[str, ...] = ()) -> Resultado:
    leitura = ler(nome_arquivo, conteudo, nomes)
    novas, repetidas = separar_novas(leitura.transacoes, armazem.chaves())
    armazem.adicionar(novas)
    logger.info(
        "importação: formato=%s lidas=%d novas=%d repetidas=%d avisos=%d",
        PurePath(nome_arquivo).suffix.lower(), len(leitura.transacoes), len(novas), repetidas, len(leitura.avisos),
    )
    return Resultado(len(leitura.transacoes), len(novas), repetidas, leitura.avisos)
