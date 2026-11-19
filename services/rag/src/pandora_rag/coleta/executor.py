"""Coleta o catálogo: bruto com data e hash, robots.txt, limite por origem e repetição.

Cada alvo é independente: uma falha vira situação `falha` e a execução segue. O bruto só é regravado
quando o hash muda, então rodar de novo sem mudanças não duplica nem altera arquivos.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

import httpx

from pandora_rag.coleta.catalogo import Alvo, ItemCatalogo, carregar_catalogo
from pandora_rag.coleta.coletores import ConteudoInvalido, coletor_para
from pandora_rag.coleta.robots import AGENTE, Robots, RobotsIndisponivel
from pandora_rag.config import CATALOGO_LOCK_PATH, RAW_DIR

logger = logging.getLogger("pandora.coleta")
USER_AGENT = f"Mozilla/5.0 (compatible; {AGENTE}/0.1; projeto academico)"
INTERVALO_POR_ORIGEM = 1.0  # segundos entre requisições à mesma origem
TENTATIVAS = 3
ESPERA_MAXIMA = 60.0

COLETADA, SEM_MUDANCA, MANUAL, FALHA, BLOQUEADA = "coletada", "sem mudança", "manual", "falha", "bloqueada_robots"


def caminho_bruto(alvo: Alvo, raiz: Path = RAW_DIR) -> Path:
    """Alvos do corpus usam o mesmo caminho do `coletar` do RAG; os demais ficam em catalogo/."""
    extensao = alvo.ext or coletor_para(alvo.formato or "html").extensao
    if alvo.fonte_id:
        return raiz / f"{alvo.fonte_id}.{extensao}"
    return raiz / "catalogo" / f"{alvo.id}.{extensao}"


def ler_lock(caminho: Path = CATALOGO_LOCK_PATH) -> dict:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {"alvos": {}}


def salvar_lock(lock: dict, caminho: Path = CATALOGO_LOCK_PATH) -> None:
    lock["alvos"] = dict(sorted(lock["alvos"].items()))
    texto = json.dumps(lock, ensure_ascii=False, indent=2) + "\n"
    if not caminho.exists() or caminho.read_text(encoding="utf-8") != texto:
        caminho.write_text(texto, encoding="utf-8")


def _gravar(caminho: Path, conteudo: bytes) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_bytes(conteudo)
    os.replace(temporario, caminho)


def _espera(resposta: httpx.Response, tentativa: int) -> float:
    pedido = resposta.headers.get("Retry-After", "")
    if pedido.isdigit():
        return min(float(pedido), ESPERA_MAXIMA)
    return float(min(2**tentativa, ESPERA_MAXIMA))


def baixar(
    cliente: httpx.Client, url: str, dormir: Callable[[float], None] = time.sleep, aceita_304: bool = False
) -> bytes | None:
    """GET com repetição em erro de rede, 429 e 5xx. Outros 4xx não adiantam repetir.

    A API do BCB responde 304 a pedidos repetidos sem cabeçalho condicional. Com bruto anterior em mãos
    (`aceita_304`), o 304 vale como "sem mudança" e devolve None; sem ele, repete como erro transitório.
    """
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = cliente.get(url)
        except httpx.TransportError:
            if tentativa == TENTATIVAS:
                raise
            dormir(float(min(2**tentativa, ESPERA_MAXIMA)))
            continue
        if resposta.status_code == 304 and aceita_304:
            return None
        if resposta.status_code in (429, 304) or resposta.status_code >= 500:
            if tentativa == TENTATIVAS:
                resposta.raise_for_status()
            dormir(_espera(resposta, tentativa))
            continue
        resposta.raise_for_status()
        return resposta.content
    raise AssertionError("inalcançável")


class _Limitador:
    """Garante um intervalo mínimo entre requisições à mesma origem."""

    def __init__(self, intervalo: float, dormir: Callable[[float], None], relogio: Callable[[], float]) -> None:
        self._intervalo, self._dormir, self._relogio = intervalo, dormir, relogio
        self._ultimo: dict[str, float] = {}

    def aguardar(self, url: str) -> None:
        origem = urlsplit(url).netloc
        faltam = self._ultimo.get(origem, float("-inf")) + self._intervalo - self._relogio()
        if faltam > 0:
            self._dormir(faltam)
        self._ultimo[origem] = self._relogio()


def _registro(situacao: str, url: str | None, anterior: dict, erro: str | None = None) -> dict:
    """Registro do lock em ordem fixa. Preserva o último bruto bom (arquivo, hash, data) do alvo."""
    registro = {"situacao": situacao, "url": url}
    registro.update({k: anterior[k] for k in ("arquivo", "sha256", "sha256_texto", "bytes", "coletado_em") if k in anterior})
    if erro:
        registro["erro"] = erro
    return registro


def coletar_alvo(
    alvo: Alvo, cliente: httpx.Client, robots: Robots, limitador: _Limitador, lock: dict, raiz: Path,
    dormir: Callable[[float], None], agora: Callable[[], datetime],
) -> str:
    anterior = lock["alvos"].get(alvo.id, {})
    if alvo.manual:
        registro = {"situacao": MANUAL, "motivo": alvo.manual}
        if alvo.url:
            registro["url"] = alvo.url
        lock["alvos"][alvo.id] = registro
        return MANUAL
    assert alvo.url and alvo.formato
    caminho = caminho_bruto(alvo, raiz)
    try:
        # robots.txt vale para páginas e PDFs; endpoints de API documentados para uso programático ficam de fora
        if alvo.formato != "api" and not robots.permitido(alvo.url):
            lock["alvos"][alvo.id] = _registro(BLOQUEADA, alvo.url, anterior, "proibido pelo robots.txt")
            return BLOQUEADA
        limitador.aguardar(alvo.url)
        coletor = coletor_para(alvo.formato, alvo.ext)
        conteudo = baixar(cliente, alvo.url, dormir, aceita_304=bool(anterior.get("sha256")) and caminho.exists())
        if conteudo is not None:
            coletor.validar(conteudo)
    except (httpx.HTTPError, RobotsIndisponivel, ConteudoInvalido) as erro:
        logger.warning("falha em %s: %s", alvo.id, erro)
        lock["alvos"][alvo.id] = _registro(FALHA, alvo.url, anterior, str(erro))
        return FALHA
    impressao = None if conteudo is None else coletor.impressao(conteudo)
    sha_texto = None if impressao is None else hashlib.sha256(impressao).hexdigest()
    # a mudança é medida no texto (HTML) ou no arquivo todo (PDF, API); 304 com bruto anterior = sem mudança
    mesmo = conteudo is None or (
        anterior.get("sha256_texto") == sha_texto if sha_texto else anterior.get("sha256") == hashlib.sha256(conteudo).hexdigest()
    )
    if mesmo and caminho.exists():
        lock["alvos"][alvo.id] = _registro(COLETADA, alvo.url, anterior)
        return SEM_MUDANCA
    assert conteudo is not None
    _gravar(caminho, conteudo)
    registro = {
        "situacao": COLETADA,
        "url": alvo.url,
        "arquivo": caminho.relative_to(raiz).as_posix(),
        "sha256": hashlib.sha256(conteudo).hexdigest(),
    }
    if sha_texto:
        registro["sha256_texto"] = sha_texto
    registro["bytes"] = len(conteudo)
    registro["coletado_em"] = agora().strftime("%Y-%m-%dT%H:%M:%SZ")
    lock["alvos"][alvo.id] = registro
    return COLETADA


def coletar_catalogo(
    itens: list[ItemCatalogo] | None = None,
    apenas: set[str] | None = None,
    raiz: Path = RAW_DIR,
    lock_path: Path = CATALOGO_LOCK_PATH,
    cliente: httpx.Client | None = None,
    intervalo: float = INTERVALO_POR_ORIGEM,
    dormir: Callable[[float], None] = time.sleep,
    relogio: Callable[[], float] = time.monotonic,
    agora: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> dict[str, str]:
    """Coleta os alvos (todos, ou só os ids em `apenas`) e devolve a situação de cada um."""
    itens = itens if itens is not None else carregar_catalogo()
    lock = ler_lock(lock_path)
    proprio = cliente is None
    cliente = cliente or httpx.Client(
        http1=True, http2=False, timeout=60, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    )
    robots, limitador = Robots(cliente), _Limitador(intervalo, dormir, relogio)
    situacao: dict[str, str] = {}
    try:
        for item in itens:
            for alvo in item.alvos:
                if apenas and alvo.id not in apenas:
                    continue
                try:
                    situacao[alvo.id] = coletar_alvo(alvo, cliente, robots, limitador, lock, raiz, dormir, agora)
                except Exception as erro:  # um alvo nunca derruba os demais
                    logger.exception("erro inesperado em %s", alvo.id)
                    lock["alvos"][alvo.id] = {"situacao": FALHA, "url": alvo.url, "erro": f"inesperado: {erro}"}
                    situacao[alvo.id] = FALHA
    finally:
        if proprio:
            cliente.close()
        salvar_lock(lock, lock_path)
    return situacao


def situacao_do_item(item: ItemCatalogo, lock: dict) -> str:
    """coletada | manual | mista (parte coletada, parte manual) | falha | pendente."""
    estados = {lock["alvos"].get(a.id, {}).get("situacao", "pendente") for a in item.alvos}
    if FALHA in estados or BLOQUEADA in estados:
        return FALHA
    if "pendente" in estados:
        return "pendente"
    if estados == {MANUAL}:
        return MANUAL
    return "mista" if MANUAL in estados else COLETADA
