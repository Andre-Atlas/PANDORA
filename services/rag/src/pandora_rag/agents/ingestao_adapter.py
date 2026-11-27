"""Adaptador de ingestão em 2 estágios (pandora_ingestion PR #116 -> Estágio 2 VLM) para o GrafoPandora."""
from __future__ import annotations

import base64
import io
import json
import logging
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

import httpx
import pymupdf
from pandora_ingestion.deduplicar import atribuir_chaves
from pandora_ingestion.erros import ArquivoIlegivel, ErroDeIngestao
from pandora_ingestion.esquema import (
    FUSO_DA_PESSOA,
    FormaPagamento,
    Leitura,
    Origem,
    Transacao,
)
from pandora_ingestion.importador import ler as ler_extrato_base
from pandora_ingestion.mascara import mascarar as mascarar_extrato
from pandora_ingestion.normalizar import (
    aplicar_natureza,
    centavos,
    data_do_texto,
    forma_de_pagamento,
    parcela_da_descricao,
)
from pandora_ingestion.pdf import PrecisaDeOcr
from PIL import Image

from pandora_rag.agents.models import ExtratoDocumentalVLM, TransacaoPersona
from pandora_rag.config import OLLAMA_URL

logger = logging.getLogger(__name__)

_RE_BET = re.compile(r"\b(?:bet|bets|aposta|apostas|tigrinho|fortune|cassino|blaze|betano|pixbet)\b", re.IGNORECASE)
_RE_RENDA = re.compile(r"\b(?:salario|provento|aposentadoria|pensao|repasse|rendimento)\b", re.IGNORECASE)
_RE_MORADIA = re.compile(r"\b(?:aluguel|condominio|energia|luz|agua|saneamento|sabesp|enel|gas|iptu)\b", re.IGNORECASE)
_RE_ALIMENTACAO = re.compile(r"\b(?:mercado|supermercado|atacadao|padaria|acougue|alimentacao|hortifruti)\b", re.IGNORECASE)
_RE_SAUDE = re.compile(r"\b(?:farmacia|drogaria|hospital|clinica|medico|consulta|plano de saude)\b", re.IGNORECASE)
_RE_TRANSPORTE = re.compile(r"\b(?:uber|99pop|onibus|metro|passagem|combustivel|posto|gasolina)\b", re.IGNORECASE)
_RE_DIVIDA = re.compile(r"\b(?:juros|rotativo|fatura|emprestimo|consignado|parcela|acordo|financiamento)\b", re.IGNORECASE)
_RE_FRAUDE = re.compile(r"\b(?:falsa central|golpe|fraude|suspeita)\b", re.IGNORECASE)

SYSTEM_EXTRATOR_EXTRATO_VLM = (
    "Você é um extrator documental financeiro em quarentena (sem ferramentas).\n"
    "Extraia APENAS os lançamentos visíveis na tabela deste extrato ou fatura bancária.\n"
    "NUNCA invente datas, valores ou descrições. Copie os números exatos em reais (ex: '1.250,00').\n"
    "Mapeie 'SALDO ANTERIOR' ou 'SALDO INICIAL' para `saldo_inicial_brl` e "
    "'SALDO FINAL', 'SALDO ATUAL' ou 'TOTAL DA FATURA' para `saldo_final_ou_total_brl` sempre que impressos (ex: '1.000,00', '300,00')."
)

_RE_SALDO_INICIAL_ANCORA = re.compile(
    r"SALDO\s+(?:ANTERIOR|INICIAL)\s*:?\s*(?:R\$\s*)?([+-]?\d[\d.]*,\d{2})",
    re.IGNORECASE,
)
_RE_SALDO_FINAL_ANCORA = re.compile(
    r"(?:SALDO\s+(?:FINAL|ATUAL)|TOTAL\s+DA\s+FATURA)\s*:?\s*(?:R\$\s*)?([+-]?\d[\d.]*,\d{2})",
    re.IGNORECASE,
)


@dataclass
class ResultadoIngestaoAdaptada:
    """Resultado consolidado da ingestão em 2 estágios já convertido para TransacaoPersona."""

    transacoes: list[TransacaoPersona]
    reconciliado: bool | None
    divergencia_centavos: int
    estagio_usado: str
    usou_ocr: bool
    avisos: list[str]


def _inferir_categoria(tx: Transacao) -> tuple[str, bool]:
    if tx.categoria_no_arquivo:
        eh_bet = tx.mcc == "7995" or tx.categoria_no_arquivo == "APOSTAS_BETS"
        return tx.categoria_no_arquivo, eh_bet
    desc = tx.descricao_mascarada
    if tx.mcc == "7995" or _RE_BET.search(desc):
        return "APOSTAS_BETS", True
    if _RE_FRAUDE.search(desc):
        return "FRAUDE_SUSPEITA", False
    if tx.valor_centavos > 0 and _RE_RENDA.search(desc):
        return "RENDA", False
    if tx.valor_centavos < 0:
        if _RE_MORADIA.search(desc):
            return "MORADIA", False
        if _RE_ALIMENTACAO.search(desc):
            return "ALIMENTACAO", False
        if _RE_SAUDE.search(desc):
            return "SAUDE", False
        if _RE_TRANSPORTE.search(desc):
            return "TRANSPORTE", False
        if _RE_DIVIDA.search(desc):
            return "DIVIDA_JUROS", False
        return "COMPRAS_IMPULSO", False
    return "RENDA", False


def converter_para_transacoes_persona(
    transacoes: Sequence[Transacao],
    persona_id: str | None = None,
) -> list[TransacaoPersona]:
    """Converte Transacao (pandora_ingestion) para TransacaoPersona usada pelos agentes."""
    convertidas: list[TransacaoPersona] = []
    for idx, tx in enumerate(transacoes, start=1):
        cat, eh_bet = _inferir_categoria(tx)
        convertidas.append(
            TransacaoPersona(
                transaction_id=tx.chave or tx.id_externo or f"ing_{idx:04d}",
                persona_id=persona_id or tx.conta_id or "visitante",
                posted_at=tx.data_hora.isoformat(),
                amount=round(tx.valor_centavos / 100.0, 2),
                payment_method=tx.forma_pagamento.value,
                description_masked=tx.descricao_mascarada,
                mcc=tx.mcc or ("7995" if eh_bet else "0000"),
                category=cat,
                is_bet=eh_bet,
                anomaly_score=0.0,
                ground_truth_note="",
            )
        )
    return convertidas


def extrair_extrato_vlm_ollama(
    pdf_bytes: bytes,
    modelo_vlm: str = "qwen2.5vl:7b",
    ollama_url: str = OLLAMA_URL,
) -> ExtratoDocumentalVLM:
    """Estágio 2: renderiza páginas do PDF via PyMuPDF e extrai tabela via VLM em quarentena."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    imagens_b64: list[str] = []
    try:
        for pag in list(doc)[:3]:
            pix = pag.get_pixmap(dpi=150)
            with Image.open(io.BytesIO(pix.tobytes("png"))) as im:
                im.thumbnail((768, 768), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                im.convert("RGB").save(buf, format="JPEG", quality=85)
                imagens_b64.append(base64.b64encode(buf.getvalue()).decode("ascii"))
    finally:
        doc.close()

    if not imagens_b64:
        return ExtratoDocumentalVLM()

    resp = httpx.post(
        f"{ollama_url}/api/chat",
        json={
            "model": modelo_vlm,
            "stream": False,
            "keep_alive": "30m",
            "format": ExtratoDocumentalVLM.model_json_schema(),
            "messages": [
                {"role": "system", "content": SYSTEM_EXTRATOR_EXTRATO_VLM},
                {
                    "role": "user",
                    "content": "Extraia os lançamentos, saldos e datas deste extrato/fatura em JSON.",
                    "images": imagens_b64,
                },
            ],
            "options": {"temperature": 0, "num_ctx": 2048, "num_predict": 512},
        },
        timeout=90.0,
    )
    resp.raise_for_status()
    conteudo = resp.json()["message"]["content"]
    return ExtratoDocumentalVLM.model_validate(json.loads(conteudo))


def _completar_saldos_ancora_pdf(conteudo: bytes, extrato: ExtratoDocumentalVLM) -> ExtratoDocumentalVLM:
    """Preenche saldos âncora ausentes a partir de texto nativo do PDF para prova matemática em centavos."""
    if extrato.saldo_inicial_brl is not None and extrato.saldo_final_ou_total_brl is not None:
        return extrato
    try:
        with pymupdf.open(stream=conteudo, filetype="pdf") as doc:
            texto = "\n".join(pag.get_text("text") for pag in list(doc)[:3])
    except (pymupdf.FileDataError, RuntimeError, ValueError, OSError) as exc:
        logger.debug("Não foi possível ler texto nativo do PDF para saldos-âncora: %s", exc)
        return extrato

    saldo_ini = extrato.saldo_inicial_brl
    if saldo_ini is None:
        m_ini = _RE_SALDO_INICIAL_ANCORA.search(texto)
        if m_ini:
            saldo_ini = m_ini.group(1)

    saldo_fim = extrato.saldo_final_ou_total_brl
    if saldo_fim is None:
        m_fim = _RE_SALDO_FINAL_ANCORA.search(texto)
        if m_fim:
            saldo_fim = m_fim.group(1)

    if saldo_ini == extrato.saldo_inicial_brl and saldo_fim == extrato.saldo_final_ou_total_brl:
        return extrato
    return extrato.model_copy(
        update={
            "saldo_inicial_brl": saldo_ini,
            "saldo_final_ou_total_brl": saldo_fim,
        }
    )


def _converter_extrato_vlm_para_leitura(
    extrato: ExtratoDocumentalVLM,
    nomes: tuple[str, ...] = (),
) -> Leitura:
    transacoes: list[Transacao] = []
    avisos: list[str] = []
    for idx, item in enumerate(extrato.lancamentos, start=1):
        try:
            dt = data_do_texto(item.data)
            val = centavos(item.valor_brl)
            if extrato.eh_fatura_cartao:
                val = abs(val) if item.natureza == "C" else -abs(val)
            elif val < 0:
                val = -abs(val)
            else:
                val = aplicar_natureza(val, item.natureza)
            desc = mascarar_extrato(item.descricao, nomes)
            if not desc:
                raise ValueError("descrição vazia.")
            forma = FormaPagamento.CARTAO_CREDITO if extrato.eh_fatura_cartao else forma_de_pagamento(desc)
            transacoes.append(
                Transacao(
                    conta_id="cartao" if extrato.eh_fatura_cartao else "principal",
                    data_hora=dt if dt.tzinfo else dt.replace(tzinfo=FUSO_DA_PESSOA),
                    valor_centavos=val,
                    forma_pagamento=forma,
                    descricao_mascarada=desc,
                    origem=Origem.PDF,
                    parcela=parcela_da_descricao(desc),
                )
            )
        except ValueError as err:
            avisos.append(f"Lançamento VLM {idx}: {err}")

    if not transacoes:
        raise ArquivoIlegivel("Estágio 2 VLM não encontrou lançamentos válidos no PDF.")

    reconciliado: bool | None = None
    divergencia = 0
    if extrato.saldo_inicial_brl and extrato.saldo_final_ou_total_brl:
        try:
            s_ini = centavos(extrato.saldo_inicial_brl)
            s_fim = centavos(extrato.saldo_final_ou_total_brl)
            esperado = s_ini + sum(t.valor_centavos for t in transacoes)
            divergencia = s_fim - esperado
            reconciliado = divergencia == 0
        except ValueError:
            reconciliado, divergencia = None, 0
    elif extrato.eh_fatura_cartao and extrato.saldo_final_ou_total_brl and not any(t.valor_centavos > 0 for t in transacoes):
        try:
            total_fat = abs(centavos(extrato.saldo_final_ou_total_brl))
            divergencia = total_fat - sum(abs(t.valor_centavos) for t in transacoes)
            reconciliado = divergencia == 0
        except ValueError:
            reconciliado, divergencia = None, 0

    return Leitura(
        tuple(atribuir_chaves(transacoes)),
        tuple(avisos),
        reconciliado=reconciliado,
        divergencia_centavos=divergencia,
        usou_ocr=True,
    )


def ingerir_extrato_adaptado(
    nome_arquivo: str,
    conteudo: bytes,
    *,
    persona_id: str | None = None,
    nomes_titular: tuple[str, ...] = (),
    extrator_ocr: Callable[[bytes], Sequence[str]] | None = None,
    extrator_vlm_fn: Callable[[bytes], ExtratoDocumentalVLM] | None = None,
    usar_vlm_fallback: bool = True,
) -> ResultadoIngestaoAdaptada:
    """Executa ingestão em 2 estágios: Estágio 1 (pandora_ingestion) e descarte/upgrade p/ VLM se necessário."""
    leitura_est1: Leitura | None = None
    erro_est1: Exception | None = None

    try:
        leitura_est1 = ler_extrato_base(
            nome_arquivo,
            conteudo,
            nomes=nomes_titular,
            extrator_ocr=extrator_ocr,
        )
    except (PrecisaDeOcr, ErroDeIngestao) as exc:
        erro_est1 = exc

    precisa_estagio_2 = (
        usar_vlm_fallback
        and nome_arquivo.lower().endswith(".pdf")
        and (
            leitura_est1 is None
            or leitura_est1.reconciliado is False
        )
    )

    if not precisa_estagio_2 and leitura_est1 is not None:
        return ResultadoIngestaoAdaptada(
            transacoes=converter_para_transacoes_persona(leitura_est1.transacoes, persona_id=persona_id),
            reconciliado=leitura_est1.reconciliado,
            divergencia_centavos=leitura_est1.divergencia_centavos,
            estagio_usado="estagio_1_ingestion",
            usou_ocr=leitura_est1.usou_ocr,
            avisos=list(leitura_est1.avisos),
        )

    leitura_est2: Leitura | None = None
    if precisa_estagio_2 and extrator_vlm_fn is not None:
        try:
            extrato_vlm = extrator_vlm_fn(conteudo)
            if extrato_vlm.lancamentos:
                extrato_vlm = _completar_saldos_ancora_pdf(conteudo, extrato_vlm)
                leitura_est2 = _converter_extrato_vlm_para_leitura(extrato_vlm, nomes=nomes_titular)
        except Exception as exc:  # noqa: BLE001
            logger.info("Estágio 2 VLM indisponível ou falhou: %s", exc)

    if leitura_est2 is not None and (
        leitura_est1 is None
        or leitura_est2.reconciliado is True
        or (
            leitura_est1.reconciliado is False
            and leitura_est2.reconciliado is False
            and abs(leitura_est2.divergencia_centavos) < abs(leitura_est1.divergencia_centavos)
        )
    ):
        return ResultadoIngestaoAdaptada(
            transacoes=converter_para_transacoes_persona(leitura_est2.transacoes, persona_id=persona_id),
            reconciliado=leitura_est2.reconciliado,
            divergencia_centavos=leitura_est2.divergencia_centavos,
            estagio_usado="estagio_2_vlm",
            usou_ocr=True,
            avisos=list(leitura_est2.avisos),
        )

    if leitura_est1 is not None:
        return ResultadoIngestaoAdaptada(
            transacoes=converter_para_transacoes_persona(leitura_est1.transacoes, persona_id=persona_id),
            reconciliado=leitura_est1.reconciliado,
            divergencia_centavos=leitura_est1.divergencia_centavos,
            estagio_usado="estagio_1_ingestion",
            usou_ocr=leitura_est1.usou_ocr,
            avisos=list(leitura_est1.avisos),
        )

    raise erro_est1 if erro_est1 is not None else ArquivoIlegivel("Não foi possível extrair transações do arquivo.")


def datetime_agora_brasilia() -> datetime:
    return datetime.now(tz=FUSO_DA_PESSOA)
