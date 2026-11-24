"""Coleta as fontes para data/raw e registra data e hashes em corpus.lock.

Toda requisição passa por `ClienteEducado` (domínios oficiais, robots.txt, ritmo por domínio).
A coleta é condicional (ETag e Last-Modified) e guarda dois hashes:
- `sha256_bruto`, do arquivo baixado;
- `sha256_texto`, do texto extraído. É ele que diz se a fonte mudou de verdade, porque uma página
  pode mudar só o layout e manter o mesmo texto.
A falha de uma fonte não interrompe as demais.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import httpx

from pandora_rag.config import LOCK_PATH, RAW_DIR, TEXT_DIR
from pandora_rag.ingest.fontes import Fonte, carregar_fontes
from pandora_rag.ingest.web import (  # noqa: F401
    USER_AGENT,
    AcessoRecusado,
    ClienteEducado,
    formato_do_conteudo,
)

logger = logging.getLogger("pandora.collect")
EXTENSOES = {"html": "html", "pdf": "pdf", "bcb_api": "json"}
ESPERADO = {"html": "html", "pdf": "pdf", "bcb_api": "json"}

# situações devolvidas por `coletar`
NOVA, TEXTO_MUDOU, SO_LAYOUT, SEM_MUDANCA = "nova", "texto mudou", "só layout", "sem mudança"


def caminho_bruto(fonte: Fonte, raiz: Path = RAW_DIR) -> Path:
    return raiz / f"{fonte.id}.{EXTENSOES[fonte.formato]}"


def ler_lock(caminho: Path = LOCK_PATH) -> dict:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {"fontes": {}}


def salvar_lock(lock: dict, caminho: Path = LOCK_PATH) -> None:
    lock["fontes"] = dict(sorted(lock["fontes"].items()))
    caminho.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def agora() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _condicionais(anterior: dict, existe: bool) -> dict[str, str]:
    if not existe:
        return {}
    cab = {}
    if anterior.get("etag"):
        cab["If-None-Match"] = anterior["etag"]
    if anterior.get("last_modified"):
        cab["If-Modified-Since"] = anterior["last_modified"]
    return cab


def coletar_uma(fonte: Fonte, cliente: ClienteEducado, lock: dict, raiz: Path = RAW_DIR, texto_dir: Path = TEXT_DIR) -> str:
    """Coleta uma fonte, atualiza a entrada dela em `lock` e devolve a situação."""
    from pandora_rag.ingest.extract import (
        blocos_de,
        carregar_texto,
        hash_texto,
        salvar_texto,
    )

    anterior = lock["fontes"].get(fonte.id, {})
    caminho = caminho_bruto(fonte, raiz)
    texto_salvo = (texto_dir / f"{fonte.id}.jsonl").exists()
    resp = cliente.get(fonte.url, _condicionais(anterior, caminho.exists() and texto_salvo))
    entrada = {**anterior, "url": fonte.url, "verificado_em": agora()}
    if resp.status == 304:
        lock["fontes"][fonte.id] = entrada
        return SEM_MUDANCA
    formato = formato_do_conteudo(resp.conteudo, resp.tipo)
    if formato != ESPERADO[fonte.formato]:
        raise ValueError(f"conteúdo não parece {fonte.formato} (veio {resp.tipo or 'sem tipo'})")
    for chave, cab in (("etag", "etag"), ("last_modified", "last-modified")):
        if resp.cabecalhos.get(cab):
            entrada[chave] = resp.cabecalhos[cab]
    sha_bruto = hashlib.sha256(resp.conteudo).hexdigest()
    if anterior.get("sha256_bruto") == sha_bruto and caminho.exists() and texto_salvo and anterior.get("sha256_texto"):
        lock["fontes"][fonte.id] = entrada
        return SEM_MUDANCA
    blocos = blocos_de(fonte.formato, resp.conteudo, fonte.recorte_inicio, fonte.recorte_fim)
    if not blocos:
        raise ValueError("nenhum texto extraído")
    sha_texto = hash_texto(blocos)
    # lock antigo, sem sha256_texto: o texto já extraído em data/text é a referência
    texto_antes = anterior.get("sha256_texto") or (hash_texto(carregar_texto(fonte.id, texto_dir)) if texto_salvo else None)
    if texto_antes is None:
        situacao = NOVA
    elif texto_antes != sha_texto:
        situacao = TEXTO_MUDOU
    else:
        situacao = SEM_MUDANCA if anterior.get("sha256_bruto") == sha_bruto else SO_LAYOUT
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(resp.conteudo)
    salvar_texto(fonte, blocos, texto_dir)
    entrada.update(sha256_bruto=sha_bruto, bytes=len(resp.conteudo), sha256_texto=sha_texto)
    if situacao in (NOVA, TEXTO_MUDOU) or "coletado_em" not in entrada:
        entrada["coletado_em"] = agora()
    lock["fontes"][fonte.id] = entrada
    return situacao


def coletar(
    fontes: list[Fonte] | None = None,
    raiz: Path = RAW_DIR,
    texto_dir: Path = TEXT_DIR,
    lock_path: Path = LOCK_PATH,
    cliente: ClienteEducado | None = None,
) -> dict[str, str]:
    """Baixa as fontes e devolve a situação de cada uma."""
    fontes = fontes if fontes is not None else carregar_fontes()
    lock = ler_lock(lock_path)
    situacao: dict[str, str] = {}
    cli = cliente or ClienteEducado()
    try:
        for fonte in fontes:
            try:
                situacao[fonte.id] = coletar_uma(fonte, cli, lock, raiz, texto_dir)
            except (httpx.HTTPError, AcessoRecusado, ValueError) as erro:
                logger.warning("falha em %s: %s", fonte.id, erro)
                situacao[fonte.id] = f"falha: {erro}"
    finally:
        if cliente is None:
            cli.__exit__()
        salvar_lock(lock, lock_path)
    return situacao


def mudaram(situacao: dict[str, str]) -> list[str]:
    """Fontes cujo texto é novo ou mudou: só elas precisam ser reindexadas."""
    return [f for f, s in situacao.items() if s in (NOVA, TEXTO_MUDOU)]
