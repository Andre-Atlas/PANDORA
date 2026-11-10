"""Coleta as fontes para data/raw e registra data e hash em corpus.lock.

Usa HTTP/1.1 porque o Planalto derruba a conexão em HTTP/2. A falha de uma fonte
não interrompe as demais, e o arquivo só é regravado se o conteúdo mudou.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from pandora_rag.config import LOCK_PATH, RAW_DIR
from pandora_rag.ingest.fontes import Fonte, carregar_fontes

logger = logging.getLogger("pandora.collect")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) PANDORA-RAG/0.1 (projeto academico)"
EXTENSOES = {"html": "html", "pdf": "pdf", "bcb_api": "json"}
PAUSA_ENTRE_FONTES = 1.0


def caminho_bruto(fonte: Fonte, raiz: Path = RAW_DIR) -> Path:
    return raiz / f"{fonte.id}.{EXTENSOES[fonte.formato]}"


def baixar(cliente: httpx.Client, url: str, tentativas: int = 3) -> bytes:
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = cliente.get(url)
            resposta.raise_for_status()
            return resposta.content
        except httpx.HTTPError:
            if tentativa == tentativas:
                raise
            time.sleep(2**tentativa)
    raise AssertionError("inalcançável")


def ler_lock(caminho: Path = LOCK_PATH) -> dict:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {"fontes": {}}


def salvar_lock(lock: dict, caminho: Path = LOCK_PATH) -> None:
    lock["fontes"] = dict(sorted(lock["fontes"].items()))
    caminho.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def coletar(fontes: list[Fonte] | None = None, raiz: Path = RAW_DIR) -> dict[str, str]:
    """Baixa as fontes e devolve a situação de cada uma."""
    fontes = fontes if fontes is not None else carregar_fontes()
    raiz.mkdir(parents=True, exist_ok=True)
    lock = ler_lock()
    situacao: dict[str, str] = {}
    with httpx.Client(
        http1=True, http2=False, timeout=60, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as cliente:
        for fonte in fontes:
            try:
                conteudo = baixar(cliente, fonte.url)
            except httpx.HTTPError as erro:
                logger.warning("falha em %s: %s", fonte.id, erro)
                situacao[fonte.id] = f"falha: {erro}"
                continue
            sha = hashlib.sha256(conteudo).hexdigest()
            anterior = lock["fontes"].get(fonte.id, {})
            caminho = caminho_bruto(fonte, raiz)
            if anterior.get("sha256_bruto") == sha and caminho.exists():
                situacao[fonte.id] = "sem mudança"
            else:
                caminho.write_bytes(conteudo)
                lock["fontes"][fonte.id] = {
                    "url": fonte.url,
                    "sha256_bruto": sha,
                    "bytes": len(conteudo),
                    "coletado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                situacao[fonte.id] = "coletada"
            time.sleep(PAUSA_ENTRE_FONTES)
    salvar_lock(lock)
    return situacao
