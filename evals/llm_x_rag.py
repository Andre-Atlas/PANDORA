"""Semana 3: LLM × RAG. Quatro formas de responder às mesmas perguntas do dev, com a mesma recuperação:

  t1-llm-sozinho     qwen2.5:14b sem fontes (só o que o modelo sabe)
  t2-rag-sozinho     recuperação + portão, devolve o melhor trecho com a fonte, sem LLM
  t3-rag-llm-14b     recuperação + portão + qwen2.5:14b, top-3 (configuração atual)
  t4-rag-llm-7b      recuperação + portão + qwen2.5:7b, top-3

Métricas novas em relação ao llm_run (ver docs/rag/10-llm-x-rag.md):
  - latência de ponta a ponta (recuperação + geração), e não só a do LLM;
  - números sem suporte: a resposta traz número (de 2 dígitos ou mais) que não está na pergunta, na referência, nos trechos de ouro
    nem nas fontes entregues ao gerador (sinal de número inventado);
  - norma correta: a resposta (ou a fonte citada) traz o número da norma esperada;
  - abstenção com 20 perguntas fora de domínio (5 do dev + 15 novas, DEV_EXTRA), em vez de 5.

Uso (de services/rag): PYTHONPATH=../.. uv run python -m evals.llm_x_rag [t1 t2 t3 t4]
"""
from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
import time
from datetime import date

from evals.golden.fora_de_dominio import DEV, DEV_EXTRA
from evals.metrics.estatistica import ic_bootstrap
from evals.metrics.respostas import CitacaoResposta, citacao_valida, taxa
from evals.metrics.textos import acerto_numerico, bleu_sentenca, numeros, rouge
from evals.recuperacao_run import GOLDEN, RAIZ
from pandora_rag.generate.answer import (
    MENSAGEM_ABSTENCAO,
    SEM_RESPOSTA,
    Resposta,
    montar_citacoes,
    responder,
)
from pandora_rag.generate.gateway import Gateway
from pandora_rag.index.build import construir
from pandora_rag.retrieve.hybrid import Parametros, Reranker, Retriever

K = 3
MAX_TOKENS = 350
LIMIAR = json.loads((RAIZ / "training" / "abstencao" / "limiar.json").read_text(encoding="utf-8"))["limiar"]

SISTEMA_SEM_FONTES = f"""Você é o PANDORA, assistente de educação financeira para pessoas endividadas no Brasil.
Responda com o que você sabe sobre a legislação e as normas brasileiras. Regras:
1. Quando citar lei, prazo, valor, percentual ou direito, diga de qual norma e artigo vem.
2. Não invente artigo, prazo ou número. Se não tiver certeza, ou se a pergunta estiver fora de finanças pessoais e dívidas, responda apenas: {SEM_RESPOSTA}
3. Não recomende compra ou venda de ativos específicos nem preveja retorno.
4. Seja claro e direto, em português, sem jargão desnecessário, em até 180 palavras."""

CONFIGS = {
    "t1": {"nome": "t1-llm-sozinho", "modo": "llm", "modelo": "qwen25-14b"},
    "t2": {"nome": "t2-rag-sozinho", "modo": "rag", "modelo": None},
    "t3": {"nome": "t3-rag-llm-14b", "modo": "rag+llm", "modelo": "qwen25-14b"},
    "t4": {"nome": "t4-rag-llm-7b", "modo": "rag+llm", "modelo": "qwen25-7b"},
}

RE_MARCADOR = re.compile(r"\[\d+\]")
RE_ENUMERACAO = re.compile(r"(?m)^\s*\d+[.)]\s")
RE_ANO = re.compile(r"(19|20)\d\d")


def itens_dev() -> list[dict]:
    """dev.v1 (51) + 15 fora de domínio novas: 46 respondíveis e 20 que devem ser recusadas."""
    xs = [json.loads(l) for l in (GOLDEN / "dev.v1.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len([x for x in xs if x["deve_abster"]]) == len(DEV)
    for i, (cat, p) in enumerate(DEV_EXTRA, start=1):
        xs.append({"id": f"dx-{i:03d}", "tipo": "fora_de_dominio", "tema": cat, "pergunta": p, "deve_abster": True,
                   "resposta_referencia": None, "trechos_ouro": [], "norma": None, "artigo": None})
    return xs


def numeros_resposta(texto: str) -> set[str]:
    return numeros(RE_ENUMERACAO.sub(" ", RE_MARCADOR.sub(" ", texto)))


def numeros_sem_suporte(texto: str, x: dict, fontes: list[str]) -> list[str]:
    apoio = " ".join([x["pergunta"], x["resposta_referencia"] or "", x["norma"] or "", x["artigo"] or "",
                      *(t["texto"] for t in x["trechos_ouro"]), *fontes])
    return sorted(n for n in numeros_resposta(texto) - numeros(apoio) if len(n.replace(".", "")) >= 2)


def textos_fontes(hits: list) -> list[str]:
    """O que o gerador recebe de cada fonte: cabeçalho (norma, artigo, página), aviso de vigência e texto."""
    r = [h.registro for h in hits]
    return [f"{x.norma} {x.artigo or ''} {x.pagina or ''} {x.ressalva or ''} {x.texto}" for x in r]


def ids_norma(x: dict) -> set[str]:
    """Números que identificam a norma esperada (ex.: 14181, 11567, 19), sem o parêntese descritivo e sem anos."""
    if not x["norma"]:
        return set()
    cabeca = re.sub(r"\(.*?\)", " ", x["norma"].split(",")[0])
    return {n for n in numeros(cabeca) if n.isdigit() and len(n) >= 2 and not RE_ANO.fullmatch(n)}


def responder_sem_fontes(g: Gateway, modelo: str, pergunta: str) -> Resposta:
    c = g.gerar(modelo, SISTEMA_SEM_FONTES, f"PERGUNTA: {pergunta}", max_tokens=MAX_TOKENS)
    texto = c.texto.strip()
    if SEM_RESPOSTA in texto:
        return Resposta(MENSAGEM_ABSTENCAO, True, [], [], c.modelo, 0.0, c.latencia_s)
    return Resposta(texto, False, [], [], c.modelo, 0.0, c.latencia_s)


def responder_extrativo(pergunta: str, hits: list) -> Resposta:
    """RAG sem LLM: o portão decide se responde; se responde, devolve o melhor trecho, cortado em 180 palavras."""
    if not hits or (hits[0].score_rerank is not None and hits[0].score_rerank < LIMIAR):
        return Resposta(MENSAGEM_ABSTENCAO, True, [], hits, "portao", 0.0, 0.0)
    r = hits[0].registro
    palavras = " ".join(r.texto.split()).split(" ")
    trecho = " ".join(palavras[:180]) + (" (...)" if len(palavras) > 180 else "")
    cab = r.norma + (f", {r.artigo}" if r.artigo else "")
    return Resposta(f"Segundo {cab}: \"{trecho}\" [1]", False, montar_citacoes(hits, [1]), hits, "extrativo", 0.0, 0.0, True)


def recuperar(itens: list[dict]) -> dict[str, tuple[list, float]]:
    store, bm25, emb = construir("estrutural", "BAAI/bge-m3", True)
    retr = Retriever(store, bm25, emb, Reranker(), Parametros(), True)
    retr.buscar("aquecimento", K)
    saida = {}
    for x in itens:
        t0 = time.perf_counter()
        hits = retr.buscar(x["pergunta"], K)
        saida[x["id"]] = (hits, time.perf_counter() - t0)
    return saida


def avaliar(cfg: dict, itens: list[dict], recs: dict, g: Gateway) -> dict:
    if cfg["modelo"]:
        g.gerar(cfg["modelo"], "Responda só OK.", "OK?", max_tokens=5)  # carrega o modelo antes de medir
    detalhe = []
    for x in itens:
        hits, t_rec = recs[x["id"]]
        if cfg["modo"] == "llm":
            r, t_rec = responder_sem_fontes(g, cfg["modelo"], x["pergunta"]), 0.0
        elif cfg["modo"] == "rag":
            r = responder_extrativo(x["pergunta"], hits)
        else:
            r = responder(g, cfg["modelo"], x["pergunta"], hits, max_tokens=MAX_TOKENS, limiar_abstencao=LIMIAR)
        fontes = textos_fontes(hits) if cfg["modo"] != "llm" else []
        d = {"id": x["id"], "tipo": x["tipo"], "tema": x["tema"], "pergunta": x["pergunta"], "resposta": r.texto,
             "abstencao_pred": r.abstencao, "deve_abster": x["deve_abster"], "por_portao": r.modelo == "portao",
             "citacoes": [{"n": c.n, "norma": c.norma, "artigo": c.artigo, "link": c.link} for c in r.citacoes],
             "latencia_rec_s": round(t_rec, 3), "latencia_ger_s": round(r.latencia_s, 3),
             "latencia_total_s": round(t_rec + r.latencia_s, 3)}
        if not x["deve_abster"]:
            cit = [CitacaoResposta(c.norma, c.link, c.artigo) for c in r.citacoes]
            d["citacao_valida"] = (not r.abstencao) and citacao_valida(r.texto, cit, exige_artigo=False)
            if not r.abstencao:
                num = acerto_numerico(r.texto, x["resposta_referencia"] or "")
                if num is not None:
                    d["numero"] = num
                d["rougeL"] = rouge(r.texto, x["resposta_referencia"] or "")["rougeL"]
                d["bleu"] = bleu_sentenca(r.texto, x["resposta_referencia"] or "")
                d["sem_suporte"] = numeros_sem_suporte(r.texto, x, fontes)
                ids = ids_norma(x)
                if ids:
                    citado = r.texto + " " + " ".join(c.norma for c in r.citacoes)
                    d["norma_correta"] = bool(ids & numeros(citado))
        detalhe.append(d)
        print(cfg["nome"], x["id"], f"{d['latencia_total_s']:.1f}s", "ABST" if r.abstencao else "", flush=True)
    return {"detalhe": detalhe, "metricas": resumir(detalhe)}


def resumir(detalhe: list[dict]) -> dict:
    norm = [d for d in detalhe if not d["deve_abster"]]
    resp = [d for d in norm if not d["abstencao_pred"]]
    fora = [d for d in detalhe if d["deve_abster"]]
    lat = sorted(d["latencia_total_s"] for d in detalhe)
    nums = [d["numero"] for d in resp if "numero" in d]
    normas = [d["norma_correta"] for d in resp if "norma_correta" in d]

    def ic(vals: list[float]) -> list[float]:
        return [round(v, 3) for v in ic_bootstrap(vals)[1:]] if vals else []

    m = {
        "n": len(detalhe), "n_respondiveis": len(norm), "n_fora": len(fora),
        "citacao_valida": taxa([d["citacao_valida"] for d in norm]),
        "recusa_indevida": taxa([d["abstencao_pred"] for d in norm]),
        "abstencao_correta": taxa([d["abstencao_pred"] for d in fora]),
        "abstencao_correta_ic95": ic([float(d["abstencao_pred"]) for d in fora]),
        "acerto_numerico": statistics.mean(nums) if nums else None, "n_numero": len(nums),
        "acerto_numerico_ic95": ic(nums),
        "respostas_com_numero_sem_suporte": taxa([bool(d["sem_suporte"]) for d in resp]),
        "respostas_com_numero_sem_suporte_ic95": ic([float(bool(d["sem_suporte"])) for d in resp]),
        "norma_correta": taxa(normas), "n_norma": len(normas), "norma_correta_ic95": ic([float(v) for v in normas]),
        "rougeL": statistics.mean(d["rougeL"] for d in resp) if resp else None,
        "bleu": statistics.mean(d["bleu"] for d in resp) if resp else None,
        "latencia_media_s": statistics.mean(lat), "latencia_p95_s": lat[int(0.95 * (len(lat) - 1))],
        "latencia_rec_media_s": statistics.mean(d["latencia_rec_s"] for d in detalhe),
    }
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}


def gravar(cfg: dict, res: dict) -> None:
    pasta = RAIZ / "evals" / "runs" / f"{date.today():%Y-%m-%d}-s3-{cfg['nome']}"
    pasta.mkdir(parents=True, exist_ok=True)
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True, check=False).stdout.strip()
    config = {**cfg, "recuperacao": "bge-m3 estrutural + híbrido RRF + bge-reranker-v2-m3", "k": K, "max_tokens": MAX_TOKENS,
              "limiar_abstencao": LIMIAR, "conjunto": "dev.v1 + DEV_EXTRA (15 fora de domínio)", "git": sha}
    (pasta / "config.json").write_text(json.dumps(config, indent=1, ensure_ascii=False), encoding="utf-8")
    (pasta / "metrics.json").write_text(json.dumps(res["metricas"], indent=1), encoding="utf-8")
    (pasta / "por_pergunta.jsonl").write_text(
        "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in res["detalhe"]), encoding="utf-8")


def recalcular(itens: list[dict], recs: dict) -> None:
    """Refaz as métricas das execuções já gravadas a partir das respostas salvas (sem gerar de novo)."""
    por_id = {x["id"]: x for x in itens}
    for cfg in CONFIGS.values():
        pasta = RAIZ / "evals" / "runs" / f"{date.today():%Y-%m-%d}-s3-{cfg['nome']}"
        detalhe = [json.loads(l) for l in (pasta / "por_pergunta.jsonl").read_text(encoding="utf-8").splitlines()]
        for d in detalhe:
            if "sem_suporte" in d:
                num = acerto_numerico(d["resposta"], por_id[d["id"]]["resposta_referencia"] or "")
                if num is not None:
                    d["numero"] = num
                fontes = textos_fontes(recs[d["id"]][0]) if cfg["modo"] != "llm" else []
                d["sem_suporte"] = numeros_sem_suporte(d["resposta"], por_id[d["id"]], fontes)
        gravar(cfg, {"detalhe": detalhe, "metricas": resumir(detalhe)})
        print(cfg["nome"], json.dumps(resumir(detalhe), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["recalcular"]:
        itens = itens_dev()
        recalcular(itens, recuperar(itens))
        sys.exit()
    escolhidos = sys.argv[1:] or list(CONFIGS)
    itens = itens_dev()
    t0 = time.time()
    recs = recuperar(itens)
    print("recuperação pronta em", round(time.time() - t0), "s", flush=True)
    g = Gateway()
    for chave in escolhidos:
        cfg = CONFIGS[chave]
        res = avaliar(cfg, itens, recs, g)
        gravar(cfg, res)
        print(cfg["nome"], json.dumps(res["metricas"], ensure_ascii=False), flush=True)
