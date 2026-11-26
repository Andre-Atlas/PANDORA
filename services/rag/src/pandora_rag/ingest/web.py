"""Acesso educado à web: só domínios oficiais, robots.txt, ritmo por domínio e limite de tamanho.

Toda requisição da coleta e do crawler passa por `ClienteEducado`. Ele nunca tenta contornar uma
verificação anti-robô: a página de desafio vira `AntiRobo` e a fonte é pulada.
"""
from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import httpx
import yaml

from pandora_rag.config import DOMINIOS_PATH

logger = logging.getLogger("pandora.web")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) PANDORA-RAG/0.1 (projeto academico)"
AGENTE_ROBOTS = "pandora-rag"
MAX_BYTES = 30 * 1024 * 1024
RASTREIO = re.compile(r"^(utm_.*|fbclid|gclid|mc_[a-z]+|_ga|ref|origem|source)$", re.IGNORECASE)
SESSAO = re.compile(r";jsessionid=[^/?#]*", re.IGNORECASE)
DESAFIO = re.compile(
    r"/_challenge|Verifica[çc][ãa]o de seguran[çc]a|cf-chl-|Just a moment\.\.\.|g-recaptcha|hcaptcha|"
    r"Attention Required! \| Cloudflare|captcha-delivery",
    re.IGNORECASE,
)


class AcessoRecusado(Exception):
    """A URL não pode ser acessada pelas regras do projeto."""


class ForaDaLista(AcessoRecusado):
    pass


class BloqueadoRobots(AcessoRecusado):
    pass


class AntiRobo(AcessoRecusado):
    pass


class GrandeDemais(AcessoRecusado):
    pass


# --- domínios ------------------------------------------------------------------------------

@dataclass(frozen=True)
class Dominio:
    host: str
    orgao: str
    caminhos: tuple[str, ...] = ()

    def aceita(self, host: str, caminho: str) -> bool:
        host = host.lower()
        if host != self.host and not host.endswith("." + self.host):
            return False
        return not self.caminhos or any(caminho.lower().startswith(c.lower()) for c in self.caminhos)


def carregar_dominios(caminho: Path = DOMINIOS_PATH) -> list[Dominio]:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    return [Dominio(d["host"].lower(), d["orgao"], tuple(d.get("caminhos") or ())) for d in dados["dominios"]]


def dominio_de(url: str, dominios: list[Dominio]) -> Dominio | None:
    partes = urlsplit(url)
    if partes.scheme != "https" or not partes.hostname:
        return None
    # o mais específico primeiro: www.gov.br/mj antes de um eventual gov.br
    for d in sorted(dominios, key=lambda d: (-len(d.host), -len(d.caminhos))):
        if d.aceita(partes.hostname, partes.path or "/"):
            return d
    return None


def canonica(url: str, base: str | None = None) -> str:
    """Endereço sem fragmento, parâmetros de rastreio e id de sessão, para deduplicar links."""
    url = urljoin(base, url) if base else url
    url = SESSAO.sub("", url)
    p = urlsplit(url)
    consulta = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not RASTREIO.match(k)])
    caminho = p.path or "/"
    if len(caminho) > 1 and caminho.endswith("/"):
        caminho = caminho[:-1]
    return urlunsplit((p.scheme.lower(), (p.hostname or "").lower() + (f":{p.port}" if p.port else ""), caminho, consulta, ""))


# --- robots.txt ----------------------------------------------------------------------------

@dataclass
class Robots:
    """robots.txt com curingas `*` e `$` (a biblioteca padrão não entende curinga)."""

    regras: list[tuple[bool, re.Pattern]] = field(default_factory=list)  # (permite, padrão)
    tudo_bloqueado: bool = False

    @classmethod
    def ler(cls, texto: str, agente: str = AGENTE_ROBOTS) -> Robots:
        grupos: list[tuple[list[str], list[tuple[bool, str]]]] = []
        agentes: list[str] = []
        regras: list[tuple[bool, str]] = []
        ultimo_era_regra = False
        for linha in texto.splitlines():
            linha = linha.split("#", 1)[0].strip()
            if ":" not in linha:
                continue
            chave, _, valor = linha.partition(":")
            chave, valor = chave.strip().lower(), valor.strip()
            if chave == "user-agent":
                if ultimo_era_regra:
                    grupos.append((agentes, regras))
                    agentes, regras = [], []
                agentes.append(valor.lower())
                ultimo_era_regra = False
            elif chave in ("allow", "disallow"):
                if valor or chave == "allow":
                    regras.append((chave == "allow", valor))
                ultimo_era_regra = True
        if agentes:
            grupos.append((agentes, regras))
        proprio = [r for a, r in grupos if any(x != "*" and x in agente.lower() for x in a)]
        geral = [r for a, r in grupos if "*" in a]
        escolhido = (proprio or geral or [[]])[0]
        return cls([(permite, cls._padrao(p)) for permite, p in escolhido if p])

    @staticmethod
    def _padrao(caminho: str) -> re.Pattern:
        fim = caminho.endswith("$")
        corpo = re.escape(caminho.rstrip("$")).replace(r"\*", ".*")
        return re.compile("^" + corpo + ("$" if fim else ""))

    def permite(self, url: str) -> bool:
        if self.tudo_bloqueado:
            return False
        p = urlsplit(url)
        alvo = (p.path or "/") + (f"?{p.query}" if p.query else "")
        melhor: tuple[int, bool] | None = None
        for permite, padrao in self.regras:
            if padrao.match(alvo):
                tamanho = len(padrao.pattern)
                # regra mais longa vence; no empate, Allow vence
                if melhor is None or tamanho > melhor[0] or (tamanho == melhor[0] and permite):
                    melhor = (tamanho, permite)
        return True if melhor is None else melhor[1]


# --- cliente -------------------------------------------------------------------------------

@dataclass
class Resposta:
    url: str
    status: int
    conteudo: bytes
    tipo: str
    cabecalhos: dict[str, str]


class ClienteEducado:
    def __init__(
        self,
        dominios: list[Dominio] | None = None,
        cliente: httpx.Client | None = None,
        intervalo: float = 1.0,
        dormir: Callable[[float], None] = time.sleep,
        relogio: Callable[[], float] = time.monotonic,
        max_bytes: int = MAX_BYTES,
        tentativas: int = 3,
    ):
        self.dominios = dominios if dominios is not None else carregar_dominios()
        self._proprio = cliente is None
        self.cliente = cliente or httpx.Client(
            http1=True, http2=False, timeout=60, follow_redirects=True, headers={"User-Agent": USER_AGENT}
        )  # HTTP/1.1: o Planalto derruba conexões HTTP/2
        self.intervalo, self.dormir, self.relogio = intervalo, dormir, relogio
        self.max_bytes, self.tentativas = max_bytes, tentativas
        self._ultimo: dict[str, float] = {}
        self._robots: dict[str, Robots] = {}

    def __enter__(self) -> ClienteEducado:
        return self

    def __exit__(self, *_) -> None:
        if self._proprio:
            self.cliente.close()

    def checar(self, url: str) -> Dominio:
        d = dominio_de(url, self.dominios)
        if d is None:
            raise ForaDaLista(f"fora de dominios.yaml: {url}")
        return d

    def _esperar(self, host: str) -> None:
        agora = self.relogio()
        falta = self._ultimo.get(host, -1e9) + self.intervalo - agora
        if falta > 0:
            self.dormir(falta)
        self._ultimo[host] = self.relogio()

    def robots(self, url: str) -> Robots:
        p = urlsplit(url)
        raiz = f"{p.scheme}://{p.hostname}"
        if raiz not in self._robots:
            self._esperar(p.hostname or "")
            try:
                r = self.cliente.get(raiz + "/robots.txt")
                if r.status_code in (401, 403):
                    rob = Robots(tudo_bloqueado=True)
                elif r.status_code >= 400 or DESAFIO.search(r.text[:20_000]):
                    rob = Robots()  # sem robots.txt legível: vale a regra geral de ritmo e domínio
                else:
                    rob = Robots.ler(r.text)
            except httpx.HTTPError as erro:
                logger.warning("robots.txt de %s indisponível: %s", raiz, erro)
                rob = Robots()
            self._robots[raiz] = rob
        return self._robots[raiz]

    def get(self, url: str, cabecalhos: dict[str, str] | None = None) -> Resposta:
        self.checar(url)
        if not self.robots(url).permite(url):
            raise BloqueadoRobots(f"robots.txt não permite: {url}")
        for tentativa in range(1, self.tentativas + 1):
            self._esperar(urlsplit(url).hostname or "")
            try:
                return self._baixar(url, cabecalhos or {})
            except (httpx.TransportError, _Temporario) as erro:
                if tentativa == self.tentativas:
                    raise httpx.HTTPError(str(erro)) from erro
                self.dormir(2**tentativa)
        raise AssertionError("inalcançável")

    def _baixar(self, url: str, cabecalhos: dict[str, str]) -> Resposta:
        with self.cliente.stream("GET", url, headers=cabecalhos) as r:
            for passo in [*r.history, r]:
                self.checar(str(passo.url))  # redirecionamento para fora da lista é recusado
            if r.status_code in (429, 500, 502, 503, 504):
                corpo = r.read()
                if DESAFIO.search(corpo[:50_000].decode("utf-8", "ignore")):
                    raise AntiRobo(f"verificação anti-robô em {r.url}; a fonte foi pulada")
                raise _Temporario(f"HTTP {r.status_code} em {r.url}")
            if r.status_code == 304:
                return Resposta(str(r.url), 304, b"", "", dict(r.headers))
            tamanho = int(r.headers.get("content-length") or 0)
            if tamanho > self.max_bytes:
                raise GrandeDemais(f"{tamanho} bytes em {r.url}")
            partes, total = [], 0
            for bloco in r.iter_bytes():
                total += len(bloco)
                if total > self.max_bytes:
                    raise GrandeDemais(f"mais de {self.max_bytes} bytes em {r.url}")
                partes.append(bloco)
            conteudo = b"".join(partes)
            tipo = r.headers.get("content-type", "").split(";")[0].strip().lower()
            if r.status_code >= 400:
                if DESAFIO.search(conteudo[:50_000].decode("utf-8", "ignore")):
                    raise AntiRobo(f"verificação anti-robô em {r.url}; a fonte foi pulada")
                raise httpx.HTTPStatusError(f"HTTP {r.status_code} em {r.url}", request=r.request, response=r)
            if "html" in tipo and DESAFIO.search(conteudo[:50_000].decode("utf-8", "ignore")):
                raise AntiRobo(f"verificação anti-robô em {r.url}; a fonte foi pulada")
            return Resposta(str(r.url), r.status_code, conteudo, tipo, dict(r.headers))


class _Temporario(Exception):
    pass


def formato_do_conteudo(conteudo: bytes, tipo: str) -> str | None:
    """Descobre o formato pelo próprio conteúdo; o Content-Type de órgão público às vezes mente."""
    inicio = conteudo[:2048].lstrip()
    if inicio.startswith(b"%PDF"):
        return "pdf"
    if inicio[:1] in (b"{", b"[") and "json" in tipo:
        return "json"
    if b"<" in inicio[:200] and ("html" in tipo or b"<html" in inicio.lower() or b"<!doctype" in inicio.lower()):
        return "html"
    return None
