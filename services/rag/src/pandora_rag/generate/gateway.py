"""LLM Gateway: interface única para modelos locais (Ollama) e da Anthropic.

- máscara de PII antes de qualquer chamada externa;
- custo acumulado com teto de orçamento;
- cada chamada registrada em JSONL (latência, tokens, custo).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import yaml

from pandora_rag.config import ROOT
from pandora_rag.generate.pii import mascarar

OLLAMA_URL = "http://localhost:11434"


class OrcamentoExcedido(RuntimeError):
    pass


@dataclass
class Completude:
    texto: str
    modelo: str
    tokens_in: int
    tokens_out: int
    custo_usd: float
    latencia_s: float
    pii_mascarada: dict


def carregar_modelos(caminho: Path = ROOT / "modelos.yaml") -> dict:
    return yaml.safe_load(caminho.read_text(encoding="utf-8"))


class Gateway:
    def __init__(self, config: dict | None = None, log: Path | None = None, orcamento_usd: float | None = None):
        self.config = config or carregar_modelos()
        self.orcamento = orcamento_usd if orcamento_usd is not None else self.config.get("orcamento_usd", 30.0)
        self.gasto = 0.0
        self.log = log
        self._anthropic = None

    def _cliente_anthropic(self):
        if self._anthropic is None:
            import anthropic

            self._anthropic = anthropic.Anthropic(max_retries=3, timeout=120)
        return self._anthropic

    def gerar(self, chave: str, sistema: str, usuario: str, max_tokens: int = 1024, json_modo: bool = False) -> Completude:
        m = self.config["modelos"][chave]
        mascarada: dict = {}
        if m.get("externo"):
            sistema, c1 = mascarar(sistema)
            usuario, c2 = mascarar(usuario)
            mascarada = {k: c1.get(k, 0) + c2.get(k, 0) for k in {*c1, *c2}}
            if self.gasto >= self.orcamento:
                raise OrcamentoExcedido(f"orçamento de US$ {self.orcamento:.2f} atingido (gasto US$ {self.gasto:.2f})")
        t0 = time.perf_counter()
        if m["provedor"] == "ollama":
            texto, tin, tout = self._ollama(m, sistema, usuario, max_tokens, json_modo)
        else:
            texto, tin, tout = self._anthropic_chamar(m, sistema, usuario, max_tokens)
        latencia = time.perf_counter() - t0
        custo = (tin * m.get("usd_in", 0) + tout * m.get("usd_out", 0)) / 1_000_000
        self.gasto += custo
        r = Completude(texto, m["id"], tin, tout, custo, latencia, mascarada)
        if self.log:
            self.log.parent.mkdir(parents=True, exist_ok=True)
            with self.log.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"chave": chave, **{k: v for k, v in r.__dict__.items() if k != "texto"}}, ensure_ascii=False) + "\n")
        return r

    def _ollama(self, m: dict, sistema: str, usuario: str, max_tokens: int, json_modo: bool = False) -> tuple[str, int, int]:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": m["id"], "stream": False, **({"format": "json"} if json_modo else {}),
                "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
                "options": {"temperature": 0, "seed": 7, "num_ctx": 8192, "num_predict": max_tokens},
            },
            timeout=600,
        )
        resp.raise_for_status()
        d = resp.json()
        return d["message"]["content"], d.get("prompt_eval_count", 0), d.get("eval_count", 0)

    def _anthropic_chamar(self, m: dict, sistema: str, usuario: str, max_tokens: int) -> tuple[str, int, int]:
        # Sem temperature: Sonnet 5.5 e Haiku 5.5 rejeitam valores fora do padrão.
        r = self._cliente_anthropic().messages.create(
            model=m["id"], max_tokens=max_tokens, system=sistema,
            messages=[{"role": "user", "content": usuario}],
            output_config={"effort": m.get("effort", "low")},
        )
        texto = "".join(b.text for b in r.content if b.type == "text")
        return texto, r.usage.input_tokens, r.usage.output_tokens
