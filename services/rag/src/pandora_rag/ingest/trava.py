"""Avaliação como trava da reindexação: nenhuma troca de índice piora o que já funcionava.

O fluxo de `reindexar`:
1. monta os registros do corpus atual mais as candidatas promovíveis;
2. confere o corpus (ids únicos, link, data, artigos centrais, sem cabeçalho vazado);
3. copia a tabela atual para `chunks_candidato` e atualiza só as fontes que mudaram;
4. roda o golden nas duas tabelas e compara as métricas;
5. se passar, promove as candidatas, troca as tabelas e pede ao serviço para recarregar.
Se falhar em qualquer passo, a tabela atual e o fontes.yaml ficam como estavam.
"""
from __future__ import annotations

import collections
import json
import math
import shutil
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from pandora_rag.config import CRAWL_DIR, RAW_DIR, REPO_ROOT, TEXT_DIR
from pandora_rag.index.registro import Registro

METRICAS = ("recall@5", "mrr", "artigo_top3")
TOLERANCIA = 0.01  # 1 ponto percentual
ARTIGOS_CENTRAIS = {"lei-14181#c54-A", "lei-14181#c104-A", "lei-14181#c104-B", "lei-14181#c104-C",
                    "stj-sumulas#548", "stj-sumulas#385", "cpc#833"}
GOLDEN = REPO_ROOT / "evals" / "golden"
RUNS = REPO_ROOT / "evals" / "runs"


def checar_corpus(registros: list[Registro]) -> list[str]:
    """As mesmas garantias de tests/test_corpus.py, em forma de lista de problemas."""
    problemas = []
    repetidos = [k for k, v in collections.Counter(r.id for r in registros).items() if v > 1]
    if repetidos:
        problemas.append(f"ids repetidos: {repetidos[:5]}")
    if len({r.fonte_id for r in registros}) < 20:
        problemas.append("menos de 20 documentos-fonte")
    ruins = [r.id for r in registros if not (r.link.startswith("https://") and r.data_referencia_normativa and r.texto.strip())]
    if ruins:
        problemas.append(f"trechos sem link https, data ou texto: {ruins[:5]}")
    base = {r.id.split("-p")[0] if r.id.rsplit("-p", 1)[-1].isdigit() else r.id for r in registros}
    faltam = sorted(ARTIGOS_CENTRAIS - base)
    if faltam:
        problemas.append(f"artigos centrais ausentes: {faltam}")
    lixo = [r.id for r in registros if (r.tipo != "cartilha" and "Rua Sete de Setembro" in r.texto) or "Vigência encerrada" in r.texto]
    if lixo:
        problemas.append(f"cabeçalho vazado: {lixo[:5]}")
    return problemas


# --- avaliação -----------------------------------------------------------------------------

def _evals():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from evals.metrics import recuperacao

    return recuperacao


def carregar_golden(conjunto: str = "golden.v1") -> list[dict]:
    linhas = (GOLDEN / f"{conjunto}.jsonl").read_text(encoding="utf-8").splitlines()
    return [x for x in map(json.loads, linhas) if x and not x.get("deve_abster")]


def avaliar_retriever(retriever, itens: list[dict], k: int = 10) -> tuple[dict[str, float], dict[str, dict]]:
    rec = _evals()
    linhas, por_pergunta = [], {}
    for x in itens:
        hits = retriever.buscar(x["pergunta"], k)
        ouros = [rec.Ouro(t["fonte_id"], t["texto"], x.get("artigo")) for t in x["trechos_ouro"]]
        m = rec.avaliar([(h.registro.fonte_id, h.registro.texto) for h in hits], ouros)
        m["artigo_top3"] = rec.acerto_artigo([(h.registro.fonte_id, h.registro.artigo) for h in hits], ouros, 3)
        linhas.append(m)
        por_pergunta[x["id"]] = {c: m[c] for c in METRICAS}
    return rec.media(linhas), por_pergunta


@dataclass
class Veredito:
    passou: bool
    motivos: list[str] = field(default_factory=list)
    atual: dict[str, float] | None = None
    candidata: dict[str, float] | None = None
    pioraram: list[str] = field(default_factory=list)


def julgar(atual: dict[str, float] | None, candidata: dict[str, float], tolerancia: float = TOLERANCIA,
           por_pergunta_atual: dict | None = None, por_pergunta_cand: dict | None = None) -> Veredito:
    """Passa se nenhuma métrica cair mais que `tolerancia`. Sem tabela atual, não há com o que comparar."""
    v = Veredito(True, atual=atual, candidata=candidata)
    if atual is None:
        v.motivos.append("sem índice atual para comparar: vale só a conferência do corpus")
        return v
    for m in METRICAS:
        a, c = atual.get(m, float("nan")), candidata.get(m, float("nan"))
        if math.isnan(a):
            continue
        if math.isnan(c) or c < a - tolerancia:
            v.passou = False
            v.motivos.append(f"{m} caiu de {a:.4f} para {c:.4f} (tolerância {tolerancia:.2f})")
    if por_pergunta_atual and por_pergunta_cand:
        v.pioraram = sorted(q for q, m in por_pergunta_atual.items()
                            if q in por_pergunta_cand and por_pergunta_cand[q]["recall@5"] < m["recall@5"])
    if v.passou:
        v.motivos.append("nenhuma métrica caiu além da tolerância")
    return v


# --- candidatas ----------------------------------------------------------------------------

def preparar_candidatas(cands, raiz_crawl: Path = CRAWL_DIR, raw_dir: Path = RAW_DIR, texto_dir: Path = TEXT_DIR) -> list:
    """Copia bruto e texto das candidatas para data/, onde montar_registros os procura."""
    from pandora_rag.ingest.collect import caminho_bruto

    prontas = []
    for c in cands:
        bruto, texto = caminho_bruto(c, raiz_crawl / "raw"), raiz_crawl / "text" / f"{c.id}.jsonl"
        if not (bruto.exists() and texto.exists()):
            continue
        raw_dir.mkdir(parents=True, exist_ok=True)
        texto_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bruto, caminho_bruto(c, raw_dir))
        shutil.copy2(texto, texto_dir / f"{c.id}.jsonl")
        prontas.append(c)
    return prontas


def desfazer_candidatas(cands, raw_dir: Path = RAW_DIR, texto_dir: Path = TEXT_DIR) -> None:
    from pandora_rag.ingest.collect import caminho_bruto

    for c in cands:
        caminho_bruto(c, raw_dir).unlink(missing_ok=True)
        (texto_dir / f"{c.id}.jsonl").unlink(missing_ok=True)


def entrada_lock(c, agora: str) -> dict:
    import hashlib

    from pandora_rag.ingest.collect import caminho_bruto

    bruto = caminho_bruto(c, RAW_DIR).read_bytes()
    return {"url": c.url, "sha256_bruto": hashlib.sha256(bruto).hexdigest(), "bytes": len(bruto),
            "sha256_texto": c.sha256_texto, "coletado_em": agora, "verificado_em": agora, "origem": c.origem}


# --- relatório -----------------------------------------------------------------------------

def salvar_relatorio(dados: dict, nome: str = "reindexacao") -> Path:
    pasta = RUNS / f"{date.today():%Y-%m-%d}-{nome}"
    n = 2
    while pasta.exists():
        pasta = RUNS / f"{date.today():%Y-%m-%d}-{nome}-{n}"
        n += 1
    pasta.mkdir(parents=True)

    def serial(o):
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        return str(o)

    (pasta / "relatorio.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1, default=serial) + "\n", encoding="utf-8")
    return pasta
