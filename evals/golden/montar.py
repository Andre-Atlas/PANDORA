"""Monta golden.v1 e dev.v1 em JSONL: sorteia chunks, rascunha com o modelo local, confere e grava.

Uso (de services/rag): uv run python -m evals.golden.montar --modelo gemma2-9b
Nada aqui é referência até o revisor marcar status_revisao = "aprovado".
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.golden import fora_de_dominio as FD
from evals.golden import rascunhar as R
from pandora_rag.generate.gateway import Gateway
from pandora_rag.index.registro import montar_registros

SAIDA = Path(__file__).parent
SEMENTE = 20261105


def rascunhar_item(g, modelo, sistema, usuario, texto_chunk, tentativas=3):
    ultimas = []
    for _ in range(tentativas):
        c = g.gerar(modelo, sistema, usuario, max_tokens=500, json_modo=True)
        item = R.extrair_json(c.texto) or {}
        falhas = R.verificar_item(item, texto_chunk) if item else ["json_invalido"]
        if not falhas:
            return item, []
        ultimas = falhas
    return None, ultimas


def montar(modelo: str, limite: int | None, so_dev: bool = False):
    registros = montar_registros()
    versao = registros[0].versao_corpus
    pool = R.elegiveis(registros)
    g = Gateway()
    personas = R.carregar_personas()

    def normativa(cotas, excluir):
        return R.amostrar(pool, cotas, SEMENTE, excluir)

    sobra = lambda c: {k: v + max(3, v // 2) for k, v in c.items()}  # sobreamostra: parte é descartada na conferência
    golden_n = normativa(sobra(R.COTAS_GOLDEN), set())
    usados = {r.id for _, r in golden_n}
    if so_dev:  # golden já fechado: o dev só evita os trechos que ele realmente usou
        ja = [json.loads(l) for l in (SAIDA / "golden.v1.jsonl").read_text(encoding="utf-8").splitlines()]
        usados = {t["chunk_origem"] for x in ja for t in x["trechos_ouro"]}
        golden_n = []
    dev_n = normativa(sobra(R.COTAS_DEV), usados)
    usados |= {r.id for _, r in dev_n}
    # personas: 10 por persona no golden, 3 no dev, sobre chunks ainda não usados
    cot_persona_g = {"cartilhas": 0}
    pool_p = [r for r in pool if r.id not in usados and r.id not in {r2.id for _, r2 in dev_n} and r.tipo in ("cartilha", "estudo", "lei", "resolucao", "decreto")]
    import random
    rng = random.Random(SEMENTE + 1)
    rng.shuffle(pool_p)
    golden_p, dev_p, i = [], [], 0
    for p in personas:
        n_dev = 4 if p["id"] in ("persona01", "persona02", "persona03", "persona04", "persona05") else 3
        for destino, n in ((golden_p, 8), (dev_p, n_dev)):
            for _ in range(n):
                destino.append((p, pool_p[i])); i += 1

    if limite:
        golden_n, dev_n, golden_p, dev_p = golden_n[:limite], dev_n[:limite], golden_p[:limite], dev_p[:limite]

    descartes = []

    def aparar(saida, cotas_n, n_persona):
        """Mantém só a cota por tema (normativas) e por persona; renumera."""
        cont, fim = {}, []
        limite_p = int(n_persona) if n_persona >= 2 else 1
        extra = 5 if n_persona == 1.5 else 0  # dev: 15 = 10 personas x1 + 5 com 2
        for x in saida:
            chave = x["tema"] if x["tipo"] == "normativa" else x["persona"]
            teto = cotas_n.get(chave, 0) if x["tipo"] == "normativa" else limite_p + (1 if extra and x["persona"] in ("persona01", "persona02", "persona03", "persona04", "persona05") else 0)
            if cont.get(chave, 0) < teto:
                cont[chave] = cont.get(chave, 0) + 1
                fim.append(x)
        for i, x in enumerate(fim, 1):
            x["id"] = x["id"].split("-")[0] + f"-{i:03d}"
        return fim

    def linha(idx, tipo, rot, r, item, persona=None, prefixo="g"):
        return {
            "id": f"{prefixo}-{idx:03d}", "tipo": tipo, "tema": rot, "persona": persona["id"] if persona else None,
            "pergunta": item["pergunta"], "resposta_referencia": item["resposta"],
            "trechos_ouro": [{"fonte_id": r.fonte_id, "chunk_origem": r.id, "texto": item["trecho_ouro"]}],
            "norma": r.norma, "artigo": r.artigo, "link": r.link, "deve_abster": False,
            "autor": f"rascunho:{modelo}", "revisor": None, "status_revisao": "pendente", "versao_corpus": versao,
        }

    def processar(lista_n, lista_p, prefixo, cotas_n, cotas_p):
        saida, k = [], 1
        for rot, r in lista_n:
            item, f = rascunhar_item(g, modelo, R.SISTEMA_NORMATIVA, f"TRECHO ({r.norma}, {r.artigo}):\n{r.texto}", r.texto)
            if item:
                saida.append(linha(k, "normativa", rot, r, item, prefixo=prefixo)); k += 1
            else:
                descartes.append({"chunk": r.id, "falhas": f})
        for p, r in lista_p:
            usuario = f"PERFIL: {p['nome']}, {p['idade']} anos. {p['arquetipo']}. Costuma dizer: \"{p['frase']}\"\n\nTRECHO ({r.norma}, {r.artigo}):\n{r.texto}"
            item, f = rascunhar_item(g, modelo, R.SISTEMA_PERSONA, usuario, r.texto)
            if item:
                saida.append(linha(k, "persona", r.camada_dominio, r, item, p, prefixo)); k += 1
            else:
                descartes.append({"chunk": r.id, "falhas": f})
        return aparar(saida, cotas_n, cotas_p)

    def fora(lista, prefixo, inicio):
        return [{
            "id": f"{prefixo}-{inicio + i:03d}", "tipo": "fora_de_dominio", "tema": rot, "persona": None,
            "pergunta": p, "resposta_referencia": None, "trechos_ouro": [], "norma": None, "artigo": None, "link": None,
            "deve_abster": True, "autor": "humano:andre-atlas", "revisor": None, "status_revisao": "pendente", "versao_corpus": versao,
        } for i, (rot, p) in enumerate(lista)]

    for nome, ln, lp, ood, pre, cn, cp in [t for t in (
        ("golden.v1", golden_n, golden_p, FD.GOLDEN, "g", R.COTAS_GOLDEN, 5),
        ("dev.v1", dev_n, dev_p, FD.DEV, "d", R.COTAS_DEV, 1.5),
    ) if not (so_dev and t[0] == "golden.v1")]:
        itens = processar(ln, lp, pre, cn, cp)
        itens += fora(ood, pre, len(itens) + 1)
        caminho = SAIDA / f"{nome}.jsonl"
        caminho.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
        print(nome, len(itens), "itens ->", caminho)
    (SAIDA / "descartes.json").write_text(json.dumps(descartes, ensure_ascii=False, indent=1), encoding="utf-8")
    print("descartados:", len(descartes))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="gemma2-9b")
    ap.add_argument("--limite", type=int)
    ap.add_argument("--so-dev", action="store_true")
    a = ap.parse_args()
    montar(a.modelo, a.limite, a.so_dev)
