#!/usr/bin/env python3
"""Gerador do dataset sintético PANDORA (issue #51).

Funções públicas: gerar_personas, gerar_transacoes, rotular, validar, exportar.
Mecanismo de rótulo: cenário latente (causa -> efeito), ver README.md.

    python gerar_dataset.py --piloto            # 5 personas, 6 meses
    python gerar_dataset.py                     # 10 personas, 12 meses
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
import unicodedata
import uuid
import zlib
from calendar import monthrange
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo as K  # noqa: E402

NS = uuid.UUID("6f1b6b0e-5a53-4d0a-9b0f-0a5c0a1d51e1")  # namespace fixo dos UUIDs sintéticos

COLUNAS = ["transaction_id", "persona_id", "posted_at", "amount", "payment_method", "description_masked", "mcc",
           "category", "cartao_ou_conta_id", "destinatario_id", "cnpj_destinatario", "destinatario_novo",
           "num_parcelas", "valor_parcela", "saldo_pos_transacao", "afeta_caixa", "hora_repasse", "min_desde_repasse",
           "horario_madrugada", "grafia_suja_bet", "operadora_bet_autorizada", "premio_recebido_bet",
           "is_bet", "is_fraud", "anomaly_score", "is_essential", "regra_essencialidade_id",
           "ground_truth_note", "sintetico"]
NAO_USAR_COMO_FEATURE = ["category", "is_bet", "is_fraud", "anomaly_score", "is_essential", "regra_essencialidade_id",
                         "ground_truth_note", "grafia_suja_bet", "operadora_bet_autorizada", "premio_recebido_bet",
                         "persona_id", "sintetico"]


# =============================================================================== utilidades
def rng_de(persona_id: str, tag: str, seed: int = K.SEED) -> np.random.Generator:
    ss = np.random.SeedSequence([seed, zlib.crc32(persona_id.encode()), zlib.crc32(tag.encode())])
    return np.random.default_rng(ss)


def ts_em(y, m, d, h=0, mi=0, s=0) -> datetime:
    d = min(max(d, 1), monthrange(y, m)[1])
    if h == 23 and mi > 55:
        mi = 55
    return datetime(y, m, d, h, mi, s)


def mes_mais(y, m, k):
    i = y * 12 + (m - 1) + k
    return i // 12, i % 12 + 1


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def dv_cnpj(base12: str) -> str:
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6] + p1

    def calc(ds, ps):
        r = sum(int(d) * p for d, p in zip(ds, ps)) % 11
        return "0" if r < 2 else str(11 - r)

    d1 = calc(base12, p1)
    return d1 + calc(base12 + d1, p2)


def cnpj_valido(c: str) -> bool:
    d = re.sub(r"\D", "", c)
    return len(d) == 14 and d[12:] == dv_cnpj(d[:12])


def cnpj_para(chave: str) -> str:
    """CNPJ sintético estável por chave: raiz pseudoaleatória, filial 8000-9999 (praticamente inexistente
    no cadastro real) e dígitos verificadores corretos. Formato válido, existência não verificável."""
    h = int(hashlib.sha256(f"cnpj|{K.SEED}|{chave}".encode()).hexdigest(), 16)
    base = f"{h % 100_000_000:08d}{8000 + (h // 100_000_000) % 2000:04d}"
    d = base + dv_cnpj(base)
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


def id_destino(chave: str) -> str:
    return hashlib.sha256(f"dest|{K.SEED}|{chave}".encode()).hexdigest()[:12]


def montar_desc(pm, nome, rng, suja_p=0.22):
    pref = {"PIX": "PIX ENVIADO", "DEBIT_CARD": "COMPRA DEBITO", "CREDIT_CARD": "COMPRA CARTAO",
            "BOLETO": "PAGTO BOLETO", "DIRECT_DEBIT": "DEBITO AUTOMATICO"}[pm]
    r = rng.random()
    partes = nome.split()
    if r < suja_p * 0.4:
        return f"PAG*{nome[:14]}"
    if r < suja_p * 0.7:
        return f"{pref} {nome[:20]} {int(rng.integers(1, 999)):03d}"
    if r < suja_p:
        return f"{partes[0]} {partes[-1]} *{int(rng.integers(100, 999))}"
    return f"{pref} {nome}"


def novo(ts, valor, cat, sub, desc, mcc, pm, instr, dest, cnpj=False, cenario="normal", **kw):
    e = dict(ts=ts, cents=int(round(valor * 100)), cat=cat, sub=sub, desc=desc, mcc=mcc, pm=pm, instr=instr,
             dest=dest, cnpj=cnpj, cenario=cenario, afeta=(pm != "CREDIT_CARD"), parcelas=1, vparcela=None,
             parc_atual=1, trab=False, rec=False, suja=False, op_aut=None, premio=0.0, repasse=False, forcado=False)
    e.update(kw)
    return e


def sample_pm(rng, probs: dict, tem_cartao: bool):
    ks = [k for k in probs if tem_cartao or k != "CREDIT_CARD"]
    p = np.array([probs[k] for k in ks], float)
    return ks[int(rng.choice(len(ks), p=p / p.sum()))]


def sample_hora(rng, perfil, noturno_p=0.0):
    if noturno_p and rng.random() < noturno_p:
        perfil = "madrugada"
    if perfil == "dia":
        h = int(np.clip(rng.normal(14, 3.3), 7, 21))
    elif perfil == "manha":
        h = int(rng.integers(6, 11))
    elif perfil == "refeicao":
        h = int(rng.choice([11, 12, 13, 14, 19, 20, 21], p=[.10, .25, .20, .10, .15, .12, .08]))
    elif perfil == "noite":
        h = int(rng.integers(19, 24))
    elif perfil == "madrugada":
        h = int(rng.choice([23, 0, 1, 2, 3, 4], p=[.15, .25, .25, .15, .1, .1]))
    else:
        h = int(rng.integers(0, 24))
    return h, int(rng.integers(0, 60)), int(rng.integers(0, 60))


# =============================================================================== personas
def gerar_personas(ids: list[str], n_meses: int, fator: float = K.FATOR_VOLUME) -> pd.DataFrame:
    linhas = []
    for pid in ids:
        s = K.PERSONAS[pid]
        linhas.append(dict(
            persona_id=pid, nome_ficticio=s["nome"], idade=s["idade"], arquetipo=s["arquetipo"], regime=s["regime"],
            escolaridade=s["escolaridade"], score_credito=s["score"], vulnerabilidade=s["vuln"],
            renda_ref_mensal=s["renda_ref"], n_contas=len(s["contas"]), n_cartoes=len(s["cartoes"]),
            n_tx_alvo=int(round(K.N_BASE[pid] * fator * n_meses / 12)), holdout=pid in K.HOLDOUT, sintetico=True))
    return pd.DataFrame(linhas)


# =============================================================================== simulação
class Ctx:
    def __init__(self, pid, spec, rng):
        self.pid, self.s, self.rng = pid, spec, rng
        self.contas = [c for c in spec["contas"] if not c.endswith("_MAE_CC")]
        self.mae = next((c for c in spec["contas"] if c.endswith("_MAE_CC")), None)
        self.cartoes = list(spec["cartoes"])
        self.escala = (spec["renda_ref"] / 3000) ** 0.6
        self.favs = {}
        self.contador = 0

    def conta(self):
        return self.contas[int(self.rng.integers(len(self.contas)))] if len(self.contas) > 1 else self.contas[0]

    def cartao(self):
        return self.cartoes[int(self.rng.integers(len(self.cartoes)))]

    def instr(self, pm, instr="conta"):
        if pm == "CREDIT_CARD":
            return self.cartoes[0] if instr == "cartao" else self.cartao()
        if instr == "mae":
            return self.mae
        return self.conta() if instr == "conta" else instr

    def uid(self):
        self.contador += 1
        return self.contador

    def nome(self, sub):
        cfg = K.CATALOGO[sub]
        if sub not in self.favs:
            n = min(3, len(cfg["nomes"]))
            self.favs[sub] = list(self.rng.choice(cfg["nomes"], size=n, replace=False))
        pool = self.favs[sub] if self.rng.random() < .62 else cfg["nomes"]
        return str(pool[int(self.rng.integers(len(pool)))])


def _ativo(f, y, m):
    ym = (y, m)
    if f.get("desde") and ym < f["desde"]:
        return False
    if f.get("ate") and ym > f["ate"]:
        return False
    if f.get("mes") and m != f["mes"]:
        return False
    return True


def renda_mes(c: Ctx, y, m):
    rng, out = c.rng, []
    ult = monthrange(y, m)[1]
    for r in c.s["renda"]:
        t = r["tipo"]
        if not _ativo(r, y, m):
            continue
        if t == "fixa":
            h = r.get("h", (8, 10))
            ts = ts_em(y, m, r["dia"], int(rng.integers(h[0], h[1] + 1)), int(rng.integers(0, 40)))
            out.append(novo(ts, r["valor"], "RENDA", "renda", r["desc"], "0000", r["pm"], c.instr(r["pm"], r.get("instr", "conta")),
                            r.get("dest", "EMP"), True, repasse=True, rec=True))
        elif t == "semanal":
            for d in range(1, ult + 1):
                if datetime(y, m, d).weekday() == r["wd"]:
                    mins = r["hm"][0] * 60 + r["hm"][1] + int(rng.integers(-r["jm"], r["jm"] + 1))
                    ts = ts_em(y, m, d, mins // 60, mins % 60, int(rng.integers(0, 60)))
                    v = r["valor"] * (1 + rng.normal(0, r["cv"]))
                    out.append(novo(ts, v, "RENDA", "renda", r["desc"], "0000", r["pm"], c.instr(r["pm"]), "PLATAFORMA:ENTREGA", True,
                                    repasse=True, rec=True))
        elif t == "mei":
            total = float(np.clip(rng.normal(r["mu"], r["sd"]), r["lo"], r["hi"]))
            k = int(rng.integers(2, 5))
            cortes = rng.dirichlet(np.ones(k)) * total
            for i, v in enumerate(cortes):
                cli = "ABCDEFGH"[int(rng.integers(0, 8))]
                ts = ts_em(y, m, int(rng.integers(2, ult)), int(rng.integers(9, 18)), int(rng.integers(0, 60)))
                out.append(novo(ts, v, "RENDA", "renda", f"{r['desc']} {cli}", "0000", "PIX", c.instr("PIX"), f"CLIENTE:{cli}", True,
                                repasse=True))
        elif t == "diarias":
            for _ in range(int(rng.poisson(r["lam"]))):
                ts = ts_em(y, m, int(rng.integers(1, ult + 1)), int(rng.integers(12, 20)), int(rng.integers(0, 60)))
                out.append(novo(ts, max(40, rng.normal(r["med"], r["sd"])), "RENDA", "renda", r["desc"], "0000", "PIX",
                                c.instr("PIX"), f"CLIENTE:{int(rng.integers(1, 9))}", False))
        elif t == "plantao_extra":
            for _ in range(int(rng.choice([0, 1, 2], p=[.2, .5, .3]))):
                ts = ts_em(y, m, int(rng.integers(8, ult + 1)), int(rng.integers(8, 18)), int(rng.integers(0, 60)))
                out.append(novo(ts, rng.normal(r["med"], 80), "RENDA", "renda", r["desc"], "0000", "PIX", c.instr("PIX"), "EMP:HOSPITAL", True))
        elif t == "conjuge":
            for _ in range(2):
                ts = ts_em(y, m, int(rng.integers(3, ult + 1)), int(rng.integers(9, 20)), int(rng.integers(0, 60)))
                out.append(novo(ts, max(200, rng.normal(r["valor"], 150)), "RENDA", "renda", r["desc"], "0000", "PIX", c.instr("PIX"),
                                "PF:conjuge_rafael", False))
        elif t == "avulso":
            for (ym, dia, hm, valor, desc) in r["itens"]:
                if ym == (y, m):
                    out.append(novo(ts_em(y, m, dia, hm[0], hm[1]), valor, "RENDA", "renda", desc, "0000", "PIX", c.instr("PIX"),
                                    "EMP:TEXTIL", True, repasse=False))
    return out


def fixos_mes(c: Ctx, y, m):
    rng, out = c.rng, []
    tem_cartao = bool(c.cartoes)
    for f in c.s["fixos"]:
        if not _ativo(f, y, m):
            continue
        pm = f["pm"] if (f["pm"] != "CREDIT_CARD" or tem_cartao) else "PIX"
        v = f["valor"] * (1 + rng.normal(0, f["jit"])) if f["jit"] else f["valor"]
        h = f["h"]
        ts = ts_em(y, m, f["dia"], int(rng.integers(h[0], h[1] + 1)), int(rng.integers(0, 50)))
        desc = f["desc"]
        out.append(novo(ts, -abs(v), f["cat"], f["sub"], desc, f["mcc"], pm, c.instr(pm, f["instr"]), f["dest"], f["cnpj"],
                        trab=f["trab"] or f["sub"] in c.s["trab_subs"], rec=True))
    return out


def _parcelar(c: Ctx, e, agenda, y, m, n_parc, valor_cents):
    vp = int(round(valor_cents / n_parc))
    base = e["desc"]
    e0 = dict(e, cents=-vp, parcelas=n_parc, vparcela=vp / 100, parc_atual=1, desc=f"{base} PARC 01/{n_parc:02d}")
    out = [e0]
    for k in range(2, n_parc + 1):
        yy, mm = mes_mais(y, m, k - 1)
        ek = dict(e, ts=ts_em(yy, mm, e["ts"].day, e["ts"].hour, e["ts"].minute, e["ts"].second), cents=-vp, parcelas=n_parc,
                  vparcela=vp / 100, parc_atual=k, desc=f"{base} PARC {k:02d}/{n_parc:02d}", forcado=True)
        agenda.setdefault((yy, mm), []).append(ek)
    return out


def variaveis_mes(c: Ctx, y, m, n, orc_cents, agenda):
    if n <= 0:
        return []
    rng = c.rng
    subs = list(c.s["pesos"])
    p = np.array([c.s["pesos"][s] for s in subs], float)
    p /= p.sum()
    ult = monthrange(y, m)[1]
    tem_cartao = bool(c.cartoes)
    bruto = []
    for sub in rng.choice(subs, size=n, p=p):
        cfg = K.CATALOGO[sub]
        pm_probs = dict(cfg["pm"])
        if "CREDIT_CARD" in pm_probs:
            pm_probs["CREDIT_CARD"] *= c.s["cartao_share"] / 0.35 if c.s["cartao_share"] else 0.0
        pm = sample_pm(rng, pm_probs, tem_cartao and c.s["cartao_share"] > 0)
        v = cfg["med"] * c.escala * float(np.exp(rng.normal(0, cfg["sigma"])))
        bruto.append((sub, cfg, pm, v))
    soma = sum(b[3] for b in bruto)
    f = float(np.clip((orc_cents / 100) / soma, 0.05, 3.0)) if soma > 0 else 1.0
    out = []
    for sub, cfg, pm, v in bruto:
        v = max(v * f, max(3.0, .12 * cfg["med"] * c.escala))   # piso de ticket: sem compras de centavos
        dia = int(rng.integers(1, ult + 1))
        h, mi, s = sample_hora(rng, cfg["hora"], c.s["noturno_p"].get(sub, 0.0))
        ts = ts_em(y, m, dia, h, mi, s)
        instr_tag = "conta"
        if cfg["cnpj"]:
            nome = c.nome(sub)
            dest = f"M:{nome}"
            desc = montar_desc(pm, nome, rng)
        else:
            k = int(rng.integers(1, 5 if sub == "pix_familia" else 7))
            dest, desc = f"P:{c.pid}:{sub}:{k}", f"PIX ENVIADO CONTATO {k:02d}"
            if sub == "pix_familia":
                v = max(20.0, round(v / 5) * 5)
        if c.mae and sub in ("farmacia", "consulta") and rng.random() < .35:
            instr_tag = "mae"
            desc = "CONTA DELEGADA MAE " + desc
            if pm == "CREDIT_CARD":
                pm = "DEBIT_CARD"
        mcc = cfg["mcc"][int(rng.integers(len(cfg["mcc"])))]
        e = novo(ts, -v, cfg["cat"], sub, desc, mcc, pm, c.instr(pm, instr_tag), dest, cfg["cnpj"], trab=sub in c.s["trab_subs"])
        cents = int(round(v * 100))
        if pm == "CREDIT_CARD" and v >= 100 and rng.random() < cfg["parc"] * c.s.get("parc_mult", 1.0):
            n_parc = int(rng.choice([2, 3, 4, 5, 6, 8, 10, 12]))
            out.extend(_parcelar(c, e, agenda, y, m, n_parc, cents))
        else:
            e["cents"] = -cents
            out.append(e)
    return out


# ---------------------------------------------------------------- cenários
def _operadora(c: Ctx, b):
    rng = c.rng
    r = rng.random()
    if r < b["aut"]:
        marca = K.OPERADORAS_AUTORIZADAS[int(rng.integers(len(K.OPERADORAS_AUTORIZADAS)))]
        return dict(tipo="aut", marca=marca, dest=f"BET:{marca}", mcc=K.MCC_BET_OPERADORA[int(rng.integers(5))], aut=True)
    if r < b["aut"] + b["nao_aut"]:
        marca = K.OPERADORAS_NAO_AUTORIZADAS[int(rng.integers(len(K.OPERADORAS_NAO_AUTORIZADAS)))]
        return dict(tipo="nao_aut", marca=marca, dest=f"BET:{marca}", mcc=K.MCC_BET_OPERADORA[int(rng.integers(5))], aut=False)
    nome = K.INTERMEDIADORES[int(rng.integers(len(K.INTERMEDIADORES)))]
    return dict(tipo="interm", marca=nome, dest=f"INTERM:{nome}", mcc=K.MCC_BET_INTERMEDIADOR[int(rng.integers(5))], aut=None)


def _desc_bet(c: Ctx, op):
    rng = c.rng
    m = op["marca"]
    if op["tipo"] == "interm":
        if rng.random() < .15:
            return f"{m.split()[0]} *REF{int(rng.integers(1000, 9999))}", True
        return f"PIX ENVIADO {m}", False
    canon = f"PIX ENVIADO OPERADORA {m}.BET.BR" if op["tipo"] == "aut" else f"PIX ENVIADO {m}.COM"
    if rng.random() < .30:
        v = [f"PAG*{m}", f"{m} PAG", f"{m}-APOSTA {int(rng.integers(1, 999))}", f"PIX {m} LTDA", f"PAGBET*{m}"]
        return v[int(rng.integers(len(v)))], True
    return canon, False


def _sessao(c: Ctx, b, ts0, n, cenario, hora_fixa=False):
    rng = c.rng
    op = _operadora(c, b)
    out, ts, tot = [], ts0, 0.0
    for k in range(n):
        stake = b["stake_med"] * float(np.exp(rng.normal(0, .6))) * (1 + b["escalada"] * k)
        stake = max(5.0, round(stake / 5) * 5 if rng.random() < .6 else round(stake, 2))
        desc, suja = _desc_bet(c, op)
        pm = "PIX" if rng.random() < .95 else "DEBIT_CARD"
        cn = cenario
        if cenario == "bet_regular" and (ts.hour >= 23 or ts.hour < 3):
            cn = "bet_chasing"
        out.append(novo(ts, -stake, "APOSTAS_BETS", "aposta", desc, op["mcc"], pm, c.instr(pm), op["dest"], True, cenario=cn,
                        suja=suja, op_aut=op["aut"], nota_via_filho=b["via_filho"]))
        tot += stake
        ts = ts + timedelta(minutes=int(rng.integers(4, 28)), seconds=int(rng.integers(0, 60)))
    if rng.random() < min(.9, b["premio_p"] * n):
        v = float(np.clip(rng.lognormal(np.log(130), .7), 20, 900))
        tp = ts + timedelta(minutes=int(rng.integers(20, 150)))
        if (tp.year, tp.month) == (ts0.year, ts0.month):
            out.append(novo(tp, v, "APOSTAS_BETS", "premio", f"PIX RECEBIDO PREMIO {op['marca']}", op["mcc"], "PIX", c.instr("PIX"),
                            op["dest"], True, cenario="bet_premio", op_aut=op["aut"], premio=round(v, 2)))
    return out


def cen_bets(c: Ctx, y, m, repasses):
    b = c.s["bets"]
    if not b:
        return []
    rng, out = c.rng, []
    ult = monthrange(y, m)[1]
    for _ in range(int(rng.poisson(b["sessoes_noite"]))):
        h = int(rng.choice([22, 23, 0, 1, 2], p=[.1, .35, .25, .2, .1]))
        ts0 = ts_em(y, m, int(rng.integers(1, ult + 1)), h, int(rng.integers(0, 60)), int(rng.integers(0, 60)))
        n = int(rng.integers(b["bets_por_sessao"][0], b["bets_por_sessao"][1] + 1))
        out += _sessao(c, b, ts0, n, "bet_regular")
    for r in repasses:
        if rng.random() < b["apos_repasse_p"]:
            ts0 = r["ts"] + timedelta(minutes=int(rng.integers(5, 115)), seconds=int(rng.integers(0, 60)))
            if (ts0.year, ts0.month) == (y, m):
                out += _sessao(c, b, ts0, int(rng.integers(1, 4)), "bet_pos_repasse")
    return out


def _ep_fraude(c: Ctx, tipo, y, m, agenda):
    rng, s = c.rng, c.s
    ult = monthrange(y, m)[1]
    base = min(s["renda_ref"], 4500)
    dia = int(rng.integers(1, ult + 1))
    u = c.uid()
    dest = f"FRAUDE:{c.pid}:{y}{m:02d}:{u}"
    cn = f"fraude_{tipo}"
    out = []
    if tipo == "falsa_central":
        n = int(rng.integers(1, 4))
        ts = ts_em(y, m, dia, int(rng.integers(9, 21)), int(rng.integers(0, 60)))
        for k in range(n):
            v = float(np.clip(base * np.exp(rng.normal(np.log(.10), .9)), 50, .8 * base)) * (0.25 if (k == 0 and n > 1) else 1)
            out.append(novo(ts, -v, "FRAUDE_SUSPEITA", "fraude", "PIX ENVIADO CONTA DESCONHECIDA", "4829", "PIX", c.instr("PIX"), dest,
                            rng.random() < .3, cenario=cn))
            ts += timedelta(minutes=int(rng.integers(7, 40)))
    elif tipo == "boleto_falso":
        v = float(np.clip(base * rng.uniform(.05, .40), 60, 3500))
        ts = ts_em(y, m, dia, int(rng.integers(9, 20)), int(rng.integers(0, 60)))
        out.append(novo(ts, -v, "FRAUDE_SUSPEITA", "fraude", "PAGTO BOLETO COBRANCA TERCEIRO PF *** CPF", "6012", "BOLETO", c.instr("BOLETO"),
                        dest, False, cenario=cn))
    elif tipo in ("loja_falsa", "golpe_pix_beneficio", "falso_emprestimo", "golpe_investimento"):
        desc = {"loja_falsa": "PIX ENVIADO LOJA ONLINE PROMOCAO", "golpe_pix_beneficio": "PIX ENVIADO TAXA CADASTRO BENEFICIO",
                "falso_emprestimo": "PIX ENVIADO TAXA LIBERACAO CREDITO", "golpe_investimento": "PIX ENVIADO PLATAFORMA RENTABILIDADE GARANTIDA"}[tipo]
        mcc = {"loja_falsa": "5999", "golpe_pix_beneficio": "4829", "falso_emprestimo": "6012", "golpe_investimento": "6211"}[tipo]
        n = 1 if tipo in ("loja_falsa", "golpe_investimento") else int(rng.integers(1, 4))
        ts = ts_em(y, m, dia, int(rng.choice([10, 14, 19, 21, 22, 23])), int(rng.integers(0, 60)))
        for k in range(n):
            if tipo == "loja_falsa":
                v = float(np.clip(250 * c.escala * np.exp(rng.normal(0, .6)), 60, 1200))
            elif tipo == "golpe_investimento":
                v = float(np.clip(base * rng.uniform(.04, .5) * s["fraude"].get("fraude_escala", 1.0), 150, 15000))
            elif tipo == "golpe_pix_beneficio":
                v = float(rng.uniform(40, 160))
            else:
                v = float(rng.uniform(80, 420))
            out.append(novo(ts, -v, "FRAUDE_SUSPEITA", "fraude", desc, mcc, "PIX", c.instr("PIX"), dest, True, cenario=cn))
            ts += timedelta(days=int(rng.integers(0, 2)), minutes=int(rng.integers(5, 90)))
            if ts.month != m:
                break
    elif tipo == "cartao_clonado":
        if not c.cartoes:
            return _ep_fraude(c, "loja_falsa", y, m, agenda)
        n = int(rng.integers(1, 4))
        ts = ts_em(y, m, dia, int(rng.integers(1, 5)), int(rng.integers(0, 60)))
        card = c.cartao()
        for k in range(n):
            v = float(np.clip(rng.lognormal(np.log(320 * c.escala), .6), 80, 1500))
            out.append(novo(ts, -v, "FRAUDE_SUSPEITA", "fraude", "COMPRA INTERNACIONAL *" + str(int(rng.integers(1000, 9999))),
                            ["5999", "5732", "4722"][int(rng.integers(3))], "CREDIT_CARD", card, f"{dest}:{k}", True, cenario=cn, forcado=True))
            ts += timedelta(minutes=int(rng.integers(2, 20)))
    elif tipo == "desconto_indevido":
        dd = f"ASSOC:desconto:{c.pid}:{u}"
        meses_ = int(rng.integers(2, 5))
        for j in range(meses_):
            yy, mm = mes_mais(y, m, j)
            e = novo(ts_em(yy, mm, dia, 7, int(rng.integers(0, 59))), -float(rng.uniform(20, 95)), "FRAUDE_SUSPEITA", "fraude",
                     "DESCONTO ASSOCIACAO NAO AUTORIZADO", "8699", "DIRECT_DEBIT", c.instr("DIRECT_DEBIT"), dd, True, cenario=cn, forcado=True)
            if j == 0:
                out.append(e)
            else:
                agenda.setdefault((yy, mm), []).append(e)
    return out


def cen_fraude(c: Ctx, y, m, agenda):
    f = c.s["fraude"]
    rng, out = c.rng, []
    tipos = list(f["tipos"])
    p = np.array([f["tipos"][t] for t in tipos], float)
    p /= p.sum()
    for _ in range(int(rng.poisson(f["eps_ano"] / 12))):
        out += _ep_fraude(c, tipos[int(rng.choice(len(tipos), p=p))], y, m, agenda)
    if f.get("fim_p") and (y, m) == K.FIM_JANELA and rng.random() < f["fim_p"]:
        out += _ep_fraude(c, "golpe_investimento", y, m, agenda)
    rec = f.get("recorrente")
    if rec:
        d = (K.FIM_JANELA[0] * 12 + K.FIM_JANELA[1]) - (y * 12 + m)
        if 0 <= d < rec["meses"]:
            for i, v in enumerate(rec["valores"]):
                out.append(novo(ts_em(y, m, rec["dia"], 7, 30 + i, int(rng.integers(0, 60))), -v, "FRAUDE_SUSPEITA", "fraude",
                                "CONTA DELEGADA MAE DESCONTO ASSOCIACAO BENEFICIO" if i == 0 else "CONTA DELEGADA MAE MENSALIDADE ASSOCIATIVA",
                                "8699", "DIRECT_DEBIT", c.mae or c.conta(), "ASSOC:desconto_mae", True, cenario="fraude_desconto_indevido",
                                rec=True))
    return out


def cen_impulso(c: Ctx, y, m, agenda):
    imp = c.s["impulso"]
    rng, out = c.rng, []
    ult = monthrange(y, m)[1]
    for _ in range(int(rng.poisson(imp["taxa"]))):
        sub = ["marketplace", "eletronicos_online", "moda"][int(rng.choice(3, p=[.45, .3, .25]))]
        cfg = K.CATALOGO[sub]
        pm = "CREDIT_CARD" if (c.cartoes and rng.random() < .8 and c.s["cartao_share"] > 0) else "PIX"
        v = cfg["med"] * c.escala * 1.2 * float(np.exp(rng.normal(0, .6)))
        h = int(rng.choice([22, 23, 0, 1], p=[.2, .35, .3, .15]))
        ts = ts_em(y, m, int(rng.integers(1, ult + 1)), h, int(rng.integers(0, 60)), int(rng.integers(0, 60)))
        nome = c.nome(sub)
        e = novo(ts, -v, cfg["cat"], sub, montar_desc(pm, nome, rng), cfg["mcc"][int(rng.integers(len(cfg["mcc"])))], pm, c.instr(pm),
                 f"M:{nome}", True, cenario="impulso_noturno")
        if pm == "CREDIT_CARD" and v >= 100 and rng.random() < imp["parc_p"]:
            out += _parcelar(c, e, agenda, y, m, int(rng.choice([3, 4, 5, 6, 10, 12])), int(round(v * 100)))
        else:
            out.append(e)
    return out


def cen_rolagem(c: Ctx, y, m):
    taxa = c.s.get("rolagem", 0)
    if not taxa or len(c.cartoes) < 2:
        return []
    rng, out = c.rng, []
    for _ in range(int(rng.poisson(taxa))):
        a, b = rng.choice(len(c.cartoes), size=2, replace=False)
        v = float(rng.uniform(400, 1200))
        ts = ts_em(y, m, int(rng.integers(8, 20)), int(rng.integers(9, 22)), int(rng.integers(0, 60)))
        n1, n2 = int(a) + 1, int(b) + 1
        out.append(novo(ts, -v, "DIVIDA_JUROS", "rolagem", f"PAGTO FATURA CARTAO {n1} NO CARTAO {n2}", "6012", "CREDIT_CARD",
                        c.cartoes[int(b)], f"EMISSOR:{c.cartoes[int(b)]}", True, cenario="rolagem", forcado=True))
        out.append(novo(ts + timedelta(minutes=1), v, "DIVIDA_JUROS", "rolagem", f"CREDITO PGTO FATURA CARTAO {n1}", "6012", "CREDIT_CARD",
                        c.cartoes[int(a)], f"EMISSOR:{c.cartoes[int(a)]}", True, cenario="rolagem", forcado=True))
    return out


def cen_mora(c: Ctx, y, m, saldo_ini):
    p = min(.9, c.s["p_mora"] * (1.6 if saldo_ini < 0 else 1.0))
    rng = c.rng
    if rng.random() >= p:
        return []
    v = float(rng.uniform(9, 48)) * max(c.escala, .6)
    ts = ts_em(y, m, int(rng.integers(8, 27)), int(rng.integers(8, 18)), int(rng.integers(0, 60)))
    return [novo(ts, -v, "DIVIDA_JUROS", "mora", "MULTA E JUROS MORA CONTA ATRASADA", "4900", "BOLETO", c.instr("BOLETO"), "CONC:mora",
                 True, cenario="mora")]


def cen_hn(c: Ctx, y, m, agenda):
    taxas = {**K.HN_PADRAO, **c.s.get("hn", {})}
    rng, out = c.rng, []
    ult = monthrange(y, m)[1]
    tem_cartao = bool(c.cartoes) and c.s["cartao_share"] > 0

    def base(sub, nome, cenario, v, perfil=None, pm_probs=None, mcc=None, nome_dest=None):
        cfg = K.CATALOGO[sub]
        pm = sample_pm(rng, pm_probs or cfg["pm"], tem_cartao)
        h, mi, s = sample_hora(rng, perfil or cfg["hora"])
        ts = ts_em(y, m, int(rng.integers(1, ult + 1)), h, mi, s)
        mc = mcc or cfg["mcc"][int(rng.integers(len(cfg["mcc"])))]
        e = novo(ts, -v, cfg["cat"], sub, montar_desc(pm, nome, rng), mc, pm, c.instr(pm), nome_dest or f"M:{nome}", True, cenario=cenario)
        return e, cfg

    for _ in range(int(rng.poisson(taxas["loterica"]))):
        nome = K.CATALOGO["loterica_conta"]["nomes"][int(rng.integers(3))]
        mcc = "7995" if rng.random() < .6 else "6012"
        v = float(rng.uniform(60, 260)) * c.escala
        e, _ = base("loterica_conta", nome, "hn_loterica", v, mcc=mcc)
        if rng.random() < .7:
            e["desc"] += " CONTA LUZ" if rng.random() < .5 else " PAGTO CONTA"
        out.append(e)
    for _ in range(int(rng.poisson(taxas["games"]))):
        nome = c.nome("jogos_eletronicos")
        v = K.CATALOGO["jogos_eletronicos"]["med"] * c.escala * float(np.exp(rng.normal(0, .7)))
        e, _ = base("jogos_eletronicos", nome, "hn_games", v)
        out.append(e)
    for _ in range(int(rng.poisson(taxas["nome_bet"]))):
        nome, sub = K.NOMES_CONFUSOS_BET[int(rng.integers(len(K.NOMES_CONFUSOS_BET)))]
        v = K.CATALOGO[sub]["med"] * c.escala * float(np.exp(rng.normal(0, .6)))
        e, _ = base(sub, nome, "hn_nome_bet", v)
        out.append(e)
    for _ in range(int(rng.poisson(taxas["viagem"] * (1 - c.s["vuln"]) * 1.4))):
        nome = K.CATALOGO["viagem"]["nomes"][int(rng.integers(3))]
        v = K.CATALOGO["viagem"]["med"] * (c.s["renda_ref"] / 3000) ** 0.8 * float(np.exp(rng.normal(0, .35)))
        e, cfg = base("viagem", nome, "hn_viagem", v, nome_dest=f"M:{nome}:{c.uid()}")
        if e["pm"] == "CREDIT_CARD" and v >= 400 and rng.random() < .5:
            out += _parcelar(c, e, agenda, y, m, int(rng.choice([3, 4, 5, 6, 10])), int(round(v * 100)))
        else:
            out.append(e)
    for _ in range(int(rng.poisson(taxas["servico_novo"]))):
        opcoes = ["reparo", "consulta"] + (["manutencao_veiculo"] if "manutencao_veiculo" in c.s["pesos"] else [])
        sub = opcoes[int(rng.integers(len(opcoes)))]
        nome = c.nome(sub)
        v = K.CATALOGO[sub]["med"] * c.escala * float(rng.uniform(2, 4.5))
        e, _ = base("reparo" if sub == "reparo" else sub, nome, "hn_servico_novo", v, perfil="dia", pm_probs={"PIX": 1.0},
                    nome_dest=f"M:{nome}:{c.uid()}")
        out.append(e)
    for _ in range(int(rng.poisson(taxas.get("pix_novo", 0)))):
        k = c.uid()
        v = K.CATALOGO["pix_amigo"]["med"] * c.escala * float(rng.uniform(1.5, 5))
        ts = ts_em(y, m, int(rng.integers(1, ult + 1)), *sample_hora(rng, "qualquer"))
        out.append(novo(ts, -v, "TRANSFERENCIA", "pix_amigo", f"PIX ENVIADO CONTATO {int(rng.integers(1, 99)):02d}", "4829", "PIX", c.instr("PIX"),
                        f"P:{c.pid}:novo:{k}", False, cenario="hn_pix_novo"))
    return out


# ---------------------------------------------------------------- núcleo mensal
def _media_negativa(path, saldo_ini, t0, t1):
    pts = [(t0, saldo_ini)] + path + [(t1, path[-1][1] if path else saldo_ini)]
    area = 0.0
    for (ta, sa), (tb, _) in zip(pts, pts[1:]):
        area += max(0, -sa) * (tb - ta).total_seconds()
    return area / max(1.0, (t1 - t0).total_seconds())


def simular_persona(pid: str, meses: list, aquec: int, rate_var: float, seed: int):
    """Simula uma persona mês a mês. Devolve (linhas da janela, série mensal)."""
    spec = K.PERSONAS[pid]
    c = Ctx(pid, spec, rng_de(pid, "sim", seed))
    rng = c.rng
    saldo = int(spec["saldo_ini"] * 100)
    fech = {k: int(v[1] * 100) for k, v in spec["cartoes"].items()}
    aberta = {k: 0 for k in spec["cartoes"]}
    limite = {k: int(v[0] * 100) for k, v in spec["cartoes"].items()}
    vistos, agenda, juros_pend, emprestimos = set(), {}, 0, 0
    linhas, serie, seq = [], [], 0
    cheque_lim = int(spec["cheque_limite"] * 100)
    renda_ref = spec["renda_ref"]
    for i, (y, m) in enumerate(meses):
        na_janela = i >= aquec
        t_ini, t_fim = ts_em(y, m, 1), ts_em(y, m, monthrange(y, m)[1], 23, 58)
        evs = renda_mes(c, y, m)
        repasses = [e for e in evs if e["repasse"]]
        evs += fixos_mes(c, y, m)
        evs += agenda.pop((y, m), [])
        fator = float(np.clip(1 + 0.8 * (saldo / 100 - spec["saldo_alvo"]) / renda_ref, .25, 1.35))
        orc = int(renda_ref * spec["var_frac"] * fator * 100)
        evs += variaveis_mes(c, y, m, int(rng.poisson(rate_var)), orc, agenda)
        evs += cen_bets(c, y, m, repasses)
        evs += cen_fraude(c, y, m, agenda)
        evs += cen_impulso(c, y, m, agenda)
        evs += cen_rolagem(c, y, m)
        evs += cen_hn(c, y, m, agenda)
        evs += cen_mora(c, y, m, saldo / 100)
        if saldo < -(2 * cheque_lim + int(.8 * renda_ref * 100)) and emprestimos < 2:
            emprestimos += 1
            x = (-saldo + cheque_lim) // 100 * 100
            evs.append(novo(ts_em(y, m, 3, 10, int(rng.integers(0, 50))), x / 100, "DIVIDA_JUROS", "emprestimo_credito",
                            "CREDITO EMPRESTIMO PESSOAL CONTRATADO", "6012", "PIX", c.conta(), f"BANCO:EMP{emprestimos}", True, cenario="divida",
                            forcado=True))
            parcela = int(round(x * 0.0577))
            for k in range(1, 25):
                yy, mm = mes_mais(y, m, k)
                agenda.setdefault((yy, mm), []).append(novo(ts_em(yy, mm, 15, 9, 0), -parcela / 100, "DIVIDA_JUROS", "emprestimo_parcela",
                    f"PARCELA EMPRESTIMO PESSOAL {k:02d}/24", "6012", "DIRECT_DEBIT", c.conta(), f"BANCO:EMP{emprestimos}", True,
                    cenario="divida", forcado=True, rec=True))
        if juros_pend > 100:
            evs.append(novo(ts_em(y, m, 1, 8, 0), -juros_pend / 100, "DIVIDA_JUROS", "cheque_especial", "JUROS E IOF CHEQUE ESPECIAL", "6012",
                            "DIRECT_DEBIT", c.conta(), f"BANCO:{pid}", True, cenario="juros_cheque", forcado=True))
            juros_pend = 0
        limite_mes = ts_em(y, m, monthrange(y, m)[1], 23, 55, 0)
        for j, e in enumerate(evs):
            if e["ts"] > limite_mes:   # sessao/golpe iniciado perto da meia-noite do ultimo dia
                e["ts"] = limite_mes - timedelta(seconds=(j * 7) % 280)
        fila = [(e["ts"], 0, j, e) for j, e in enumerate(evs)]
        fila += [(ts_em(y, m, 10, 11, 0), 1, 1000 + j, k) for j, k in enumerate(spec["cartoes"])]
        fila.sort(key=lambda t: (t[0], t[1], t[2]))
        saldo_ini_mes, path, mes_out, tem_mora = saldo, [], [], False
        for ts, tipo, _, obj in fila:
            if tipo == 1:
                card, F = obj, fech[obj]
                if F <= 0:
                    continue
                minimo = min(F, max(int(.15 * F), 5000))
                pagto = F if rng.random() < spec["p_total"] else minimo
                pagto = min(pagto, max(saldo + cheque_lim, minimo))
                completo = pagto >= F
                e = novo(ts, -pagto / 100, "TRANSFERENCIA" if completo else "DIVIDA_JUROS", "pagto_fatura" if completo else "pagto_minimo",
                         "PAGTO FATURA CARTAO" if completo else "PAGAMENTO MINIMO FATURA CARTAO ROTATIVO", "6012", "DIRECT_DEBIT",
                         c.conta(), f"EMISSOR:{card}", True, cenario="normal" if completo else "divida", forcado=True)
                fech[card] -= pagto
            else:
                e = obj
                if e["pm"] == "CREDIT_CARD" and e["cents"] < 0 and not e["forcado"]:
                    if fech[e["instr"]] + aberta[e["instr"]] - e["cents"] > limite[e["instr"]]:
                        e["pm"] = "DEBIT_CARD" if rng.random() < .6 else "PIX"
                        e["instr"], e["afeta"], e["parcelas"], e["vparcela"] = c.conta(), True, 1, None
                        e["desc"] = re.sub(r" PARC \d+/\d+$", "", e["desc"]).replace("COMPRA CARTAO", "COMPRA DEBITO")
            e["novo"] = (e["dest"] not in vistos) and e["cents"] < 0
            vistos.add(e["dest"])
            if e["afeta"]:
                saldo += e["cents"]
                path.append((e["ts"], saldo))
            else:
                aberta[e["instr"]] -= e["cents"]
            seq += 1
            e["saldo_pos"], e["seq"] = saldo, seq
            tem_mora |= e["cenario"] == "mora"
            mes_out.append(e)
        juros_pend = int(round(K.TAXA_CHEQUE_ESPECIAL_MES * min(_media_negativa(path, saldo_ini_mes, t_ini, t_fim), cheque_lim)))
        for card in spec["cartoes"]:
            rem = fech[card]
            juros = int(round(rem * (K.TAXA_ROTATIVO_MES + K.IOF_ROTATIVO))) if rem > 0 else 0
            juros = max(0, min(juros, int(1.25 * limite[card]) - rem))   # teto do rotativo (premissa)
            if juros > 0:
                seq += 1
                e = novo(t_fim, -juros / 100, "DIVIDA_JUROS", "encargos_rotativo", "ENCARGOS ROTATIVO + IOF CARTAO", "6012", "CREDIT_CARD",
                         card, f"EMISSOR:{card}", True, cenario="juros_rotativo", forcado=True)
                e["novo"], e["saldo_pos"], e["seq"] = False, saldo, seq
                aberta[card] += juros
                mes_out.append(e)
            fech[card] = rem + aberta[card]
            aberta[card] = 0
        if na_janela:
            cred = sum(e["cents"] for e in mes_out if e["afeta"] and e["cents"] > 0)
            deb = -sum(e["cents"] for e in mes_out if e["afeta"] and e["cents"] < 0)
            renda_m = sum(e["cents"] for e in mes_out if e["cat"] == "RENDA")
            for e in mes_out:
                e["persona_id"], e["mes_idx"] = pid, i - aquec + 1
            linhas += mes_out
            serie.append(dict(persona_id=pid, ano_mes=f"{y}-{m:02d}", mes_idx=i - aquec + 1, saldo_inicial=saldo_ini_mes / 100,
                              total_credito=cred / 100, total_debito=deb / 100, saldo_final=saldo / 100, n_tx=len(mes_out),
                              renda_mes=renda_m / 100, inadimplente_mes=bool(tem_mora),
                              usou_cheque_especial=bool(any(s < 0 for _, s in path) or saldo_ini_mes < 0)))
    return linhas, serie


def _calibrar(pid, meses, alvo, seed):
    """Acha a taxa de eventos variaveis que leva ao alvo, limitada pela capacidade de ticket medio."""
    n_meses = len(meses) - K.MESES_AQUECIMENTO
    sp = K.PERSONAS[pid]
    cap = sp["var_frac"] * sp["renda_ref"] / K.TICKET_MEDIO_MIN
    r0 = min(cap, max(2.0, alvo / n_meses * .5))
    l0, s0 = simular_persona(pid, meses, K.MESES_AQUECIMENTO, r0, seed)
    r1 = min(cap, max(.5, r0 + (alvo - len(l0)) / n_meses / 1.15))
    l1, s1 = simular_persona(pid, meses, K.MESES_AQUECIMENTO, r1, seed)
    slope = (len(l1) - len(l0)) / (r1 - r0) if abs(r1 - r0) > 1e-6 else n_meses
    slope = slope if slope > .5 * n_meses else n_meses
    r2 = min(cap, max(.3, r1 + (alvo - len(l1)) / slope))
    l2, s2 = simular_persona(pid, meses, K.MESES_AQUECIMENTO, r2, seed)
    limitada = r2 >= cap - 1e-9 and len(l2) < .97 * alvo
    return l2, s2, r2, limitada


def gerar_transacoes(personas: pd.DataFrame, n_meses: int, seed: int = K.SEED, piso_total: int | None = None):
    """Simula todas as personas. Se piso_total for dado, o que nao cabe na capacidade de uma persona
    (orcamento variavel / ticket medio minimo) e redistribuido as personas com folga."""
    meses = [mes_mais(K.FIM_JANELA[0], K.FIM_JANELA[1], -k) for k in range(n_meses + K.MESES_AQUECIMENTO - 1, -1, -1)]
    res, alvo0 = {}, {}
    for _, p in personas.iterrows():
        pid, alvo = p["persona_id"], int(p["n_tx_alvo"])
        alvo0[pid] = alvo
        res[pid] = _calibrar(pid, meses, alvo, seed) + (alvo,)
    realocado = 0
    if piso_total:
        meta = int(piso_total * 1.02)   # margem de 2% sobre o piso
        falta = meta - sum(len(r[0]) for r in res.values())
        for _ in range(3):
            if falta <= 0:
                break
            folga = [pid for pid, r in res.items() if not r[3]]
            if not folga:
                break
            peso = sum(alvo0[p] for p in folga)
            for pid in folga:
                novo_alvo = len(res[pid][0]) + int(np.ceil(falta * alvo0[pid] / peso * 1.05))
                res[pid] = _calibrar(pid, meses, novo_alvo, seed) + (novo_alvo,)
            realocado += falta
            falta = meta - sum(len(r[0]) for r in res.values())
    todas, series, calib = [], [], []
    for pid, (l, s, r, lim, alvo_f) in res.items():
        todas += l
        series += s
        calib.append((pid, alvo0[pid], len(l), round(r, 2), alvo_f, lim))
    df = pd.DataFrame(todas)
    df["seq_global"] = np.arange(len(df))
    df = df.sort_values(["persona_id", "ts", "seq"], kind="stable").reset_index(drop=True)
    cols_fim = ["cnpj"]
    df["destinatario_id"] = df["dest"].map(id_destino)
    df["cnpj_destinatario"] = [cnpj_para(d) if f else "" for d, f in zip(df["dest"], df["cnpj"])]
    df.loc[df["cat"].eq("RENDA"), "novo"] = False
    df["hora_repasse"] = df["ts"].where(df["repasse"]).groupby(df["persona_id"]).ffill()
    df["min_desde_repasse"] = ((df["ts"] - df["hora_repasse"]).dt.total_seconds() / 60).round(1)
    df["horario_madrugada"] = (df["ts"].dt.hour >= 23) | (df["ts"].dt.hour < 3)
    df.attrs["calibracao"] = calib
    return df, pd.DataFrame(series)


# =============================================================================== rótulos
def _grupo_score(cen: str) -> str:
    if cen.startswith("fraude_"):
        t = cen[7:]
        return "fraude_forte" if t in K.FRAUDE_FORTE else "fraude_sutil" if t in K.FRAUDE_SUTIL else "fraude_media"
    return {"bet_regular": "bet_regular", "bet_pos_repasse": "bet_pos_repasse", "bet_chasing": "bet_chasing", "bet_premio": "bet_premio",
            "impulso_noturno": "impulso", "rolagem": "rolagem", "mora": "divida", "juros_rotativo": "divida", "juros_cheque": "divida",
            "divida": "divida"}.get(cen, "atipico" if cen.startswith("hn_") else "normal")


def aplicar_regras_essencialidade(df: pd.DataFrame, regras: list) -> tuple[np.ndarray, np.ndarray]:
    n = len(df)
    ess, rid, livre = np.zeros(n, bool), np.array([""] * n, dtype=object), np.ones(n, bool)
    hora, valor = df["ts"].dt.hour.to_numpy(), df["cents"].abs().to_numpy() / 100
    for r in regras:
        m = livre.copy()
        if r["arquetipo"] != "*":
            m &= df["arquetipo"].isin(r["arquetipo"].split("|")).to_numpy()
        if r["categoria"] != "*":
            m &= df["cat"].isin(r["categoria"].split("|")).to_numpy()
        if r["subtipo"] != "*":
            m &= df["sub"].isin(r["subtipo"].split("|")).to_numpy()
        if r["recorrente"] != "*":
            m &= (df["rec"].to_numpy() == (r["recorrente"] == "True"))
        if r["trab"] != "*":
            m &= (df["trab"].to_numpy() == (r["trab"] == "True"))
        if r["hora_ini"] != "":
            a, b = int(r["hora_ini"]), int(r["hora_fim"])
            m &= ((hora >= a) & (hora < b)) if a <= b else ((hora >= a) | (hora < b))
        if r["valor_max"] != "":
            m &= valor <= float(r["valor_max"])
        ess[m], rid[m], livre = r["is_essential"], r["regra_id"], livre & ~m
    return ess, rid


def rotular(df: pd.DataFrame, personas: pd.DataFrame, seed: int = K.SEED) -> pd.DataFrame:
    """Mecanismo B: rótulo = causa (cenário). Score = Beta por cenário + efeito de persona + ruído em logit.
    Ruído de rótulo só na coluna observada; a verdade limpa fica em rotulos_verdadeiros.csv."""
    rng = rng_de("__rotulos__", "v1", seed)
    df = df.merge(personas[["persona_id", "arquetipo"]], on="persona_id", how="left")
    cen = df["cenario"]
    fraude_v, bet_v = cen.str.startswith("fraude_"), cen.str.startswith("bet_")
    grupos = cen.map(_grupo_score)
    ab = np.array([K.BETA_PARAMS[g] for g in grupos])
    bruto = np.clip(rng.beta(ab[:, 0], ab[:, 1]), 1e-4, 1 - 1e-4)
    efeito = {p: rng.normal(0, .4) for p in sorted(df["persona_id"].unique())}
    logit = np.log(bruto / (1 - bruto)) + df["persona_id"].map(efeito).to_numpy() + rng.normal(0, .35, len(df))
    df["anomaly_score"] = np.round(1 / (1 + np.exp(-logit)), 2)

    def ruido(verdade, lookalike):
        obs = verdade.to_numpy().copy()
        pos, neg = np.flatnonzero(verdade.to_numpy()), np.flatnonzero(lookalike.to_numpy() & ~verdade.to_numpy())
        fn = rng.choice(pos, size=int(round(K.RUIDO_FN * len(pos))), replace=False) if len(pos) else np.array([], int)
        fp = rng.choice(neg, size=int(round(K.RUIDO_FP_LOOKALIKE * len(neg))), replace=False) if len(neg) else np.array([], int)
        obs[fn], obs[fp] = False, True
        flip = np.zeros(len(obs), bool)
        flip[fn], flip[fp] = True, True
        return obs, flip

    df["is_fraud_verdadeiro"], df["is_bet_verdadeiro"] = fraude_v, bet_v
    df["is_fraud"], df["rotulo_fraude_ruidoso"] = ruido(fraude_v, cen.isin(["hn_viagem", "hn_servico_novo", "hn_pix_novo"]))
    df["is_bet"], df["rotulo_bet_ruidoso"] = ruido(bet_v, cen.isin(["hn_loterica", "hn_games", "hn_nome_bet"]))
    df["risco_comportamental_verdadeiro"] = fraude_v | bet_v | cen.isin(["impulso_noturno", "rolagem"])
    regras = K.REGRAS_ESSENCIALIDADE
    df["is_essential"], df["regra_essencialidade_id"] = aplicar_regras_essencialidade(df, regras)
    return df


def tabela_final(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "transaction_id": [str(uuid.uuid5(NS, f"{K.SEED}|{p}|{i}")) for i, p in zip(df.index, df["persona_id"])],
        "persona_id": df["persona_id"], "posted_at": df["ts"].dt.strftime("%Y-%m-%dT%H:%M:%S"), "amount": df["cents"] / 100,
        "payment_method": df["pm"], "description_masked": df["desc"].map(sem_acento), "mcc": df["mcc"], "category": df["cat"],
        "cartao_ou_conta_id": df["instr"], "destinatario_id": df["destinatario_id"], "cnpj_destinatario": df["cnpj_destinatario"],
        "destinatario_novo": df["novo"].astype(bool), "num_parcelas": df["parcelas"],
        "valor_parcela": [v if pd.notna(v) else (abs(c) / 100 if pm == "CREDIT_CARD" else np.nan)
                          for v, c, pm in zip(df["vparcela"], df["cents"], df["pm"])],
        "saldo_pos_transacao": df["saldo_pos"] / 100, "afeta_caixa": df["afeta"],
        "hora_repasse": df["hora_repasse"].dt.strftime("%Y-%m-%dT%H:%M:%S"), "min_desde_repasse": df["min_desde_repasse"],
        "horario_madrugada": df["horario_madrugada"], "grafia_suja_bet": df["suja"],
        "operadora_bet_autorizada": df["op_aut"], "premio_recebido_bet": df["premio"],
        "is_bet": df["is_bet"], "is_fraud": df["is_fraud"], "anomaly_score": df["anomaly_score"],
        "is_essential": df["is_essential"], "regra_essencialidade_id": df["regra_essencialidade_id"],
        "ground_truth_note": [K.NOTAS.get(c, f"Transacao {s} ({ca}) no comportamento normal da persona")
                              for c, s, ca in zip(df["cenario"], df["sub"], df["cat"])],
        "sintetico": True})
    return out[COLUNAS]


def tabela_verdade(df: pd.DataFrame, final: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "transaction_id": final["transaction_id"], "persona_id": df["persona_id"], "cenario": df["cenario"], "subtipo": df["sub"],
        "finalidade_trabalho": df["trab"], "is_fraud_verdadeiro": df["is_fraud_verdadeiro"], "is_bet_verdadeiro": df["is_bet_verdadeiro"],
        "risco_comportamental_verdadeiro": df["risco_comportamental_verdadeiro"],
        "rotulo_fraude_ruidoso": df["rotulo_fraude_ruidoso"], "rotulo_bet_ruidoso": df["rotulo_bet_ruidoso"], "mes_idx": df["mes_idx"]})


# =============================================================================== split
def dividir(df: pd.DataFrame, ids: list[str], n_meses: int) -> dict:
    holdout = [p for p in K.HOLDOUT if p in ids]
    resto = [p for p in ids if p not in holdout]
    linhas = df.groupby("persona_id").size().to_dict()
    cons = df[df["cat"].isin(K.CATEGORIAS_CONSUMO)].groupby(["persona_id", "cat"]).size().unstack(fill_value=0)
    fr = df[df["is_fraud_verdadeiro"]].groupby("persona_id").size().to_dict()
    bt = df[df["is_bet_verdadeiro"]].groupby("persona_id").size().to_dict()
    total = sum(linhas[p] for p in resto)
    melhor = None
    for atrib in itertools.product(range(3), repeat=len(resto)):
        g = [[p for p, a in zip(resto, atrib) if a == k] for k in range(3)]
        if len(resto) >= 3 and any(not x for x in g):
            continue
        sh = [sum(linhas[p] for p in x) / total for x in g]
        pen = sum((s - t) ** 2 for s, t in zip(sh, K.SPLIT_ALVO))
        c_tr = cons.reindex(g[0]).sum()
        if (c_tr.reindex(K.CATEGORIAS_CONSUMO).fillna(0) < 50).any():
            pen += 5
        # cobertura minima de fraude e aposta: treino precisa aprender, validacao e teste precisam medir
        for x, (mf, mb) in zip(g, [(30, 150), (5, 5), (5, 5)]):
            pen += .3 * (sum(fr.get(p, 0) for p in x) < mf) + .3 * (sum(bt.get(p, 0) for p in x) < mb)
        if melhor is None or pen < melhor[0]:
            melhor = (pen, g, sh)
    _, g, sh = melhor
    meses_idx = list(range(1, n_meses + 1))
    corte = n_meses - K.MESES_TESTE_PREVISOR
    ano_mes = sorted(df["ts"].dt.strftime("%Y-%m").unique())
    return {
        "seed": K.SEED, "criterio": "por persona_id (sem vazamento entre pessoas); previsor de fluxo com corte temporal adicional",
        "alvo_70_15_15": list(K.SPLIT_ALVO),
        "personas": {"treino": g[0], "validacao": g[1], "teste": g[2], "holdout_generalizacao": holdout},
        "participacao_linhas_8_personas": {"treino": round(sh[0], 3), "validacao": round(sh[1], 3), "teste": round(sh[2], 3)},
        "linhas": {k: int(sum(linhas[p] for p in v)) for k, v in
                   {"treino": g[0], "validacao": g[1], "teste": g[2], "holdout_generalizacao": holdout}.items()},
        "temporal_previsor": {"treino_meses": ano_mes[:corte], "teste_meses": ano_mes[corte:],
                              "treino_mes_idx": meses_idx[:corte], "teste_mes_idx": meses_idx[corte:]},
        "colunas_alvo": ["category", "is_bet", "is_fraud", "anomaly_score", "is_essential"],
        "colunas_nao_usar_como_feature": NAO_USAR_COMO_FEATURE,
        "observacao": "Com 10 personas o 70/15/15 exato por pessoa e impossivel; os grupos minimizam o desvio em participacao de linhas. "
                      "O holdout (antonio_67, rosangela_43) fica fora do treino e da validacao.",
    }


# =============================================================================== exportar
def lista_spa() -> pd.DataFrame:
    return pd.DataFrame([dict(cnpj=cnpj_para(f"BET:{m}"), razao_social=f"{m} ENTRETENIMENTO LTDA (FICTICIA)", marca=m,
                              dominio=f"{m.lower()}.bet.br", status="AUTORIZADA", sintetico=True) for m in K.OPERADORAS_AUTORIZADAS])


def tabela_regras() -> pd.DataFrame:
    r = pd.DataFrame(K.REGRAS_ESSENCIALIDADE)
    r.insert(1, "prioridade", range(1, len(r) + 1))
    return r


def exportar(df, final, verdade, serie, personas, split, saida: Path, args) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    final.to_csv(saida / "transacoes.csv", index=False)
    verdade.to_csv(saida / "rotulos_verdadeiros.csv", index=False)
    serie.to_csv(saida / "serie_mensal.csv", index=False)
    personas.to_csv(saida / "personas.csv", index=False)
    tabela_regras().to_csv(saida / "regras_essencialidade.csv", index=False)
    lista_spa().to_csv(saida / "lista_spa_sintetica.csv", index=False)
    (saida / "split.json").write_text(json.dumps(split, ensure_ascii=False, indent=2))
    meta = dict(seed=K.SEED, n_meses=args.meses, personas=list(personas["persona_id"]), fator_volume=args.fator_volume,
                n_linhas=len(final), ruido_fn=K.RUIDO_FN, ruido_fp_lookalike=K.RUIDO_FP_LOOKALIKE, holdout=list(K.HOLDOUT),
                gerado_com="numpy %s pandas %s" % (np.__version__, pd.__version__), sintetico=True,
                aviso="Dados sinteticos. Nao representam pessoas reais.")
    (saida / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"\nArquivos gravados em {saida}")


# =============================================================================== validar
def _auc(score: pd.Series, y: pd.Series) -> float:
    y = y.astype(bool)
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = score.rank(method="average")
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def validar(saida: Path, n_meses: int, calib=None) -> dict:
    tx = pd.read_csv(saida / "transacoes.csv", dtype={"cnpj_destinatario": str, "mcc": str})
    vd = pd.read_csv(saida / "rotulos_verdadeiros.csv")
    sm = pd.read_csv(saida / "serie_mensal.csv")
    ps = pd.read_csv(saida / "personas.csv")
    sp = json.loads((saida / "split.json").read_text())
    tx["ts"] = pd.to_datetime(tx["posted_at"])
    tx = tx.merge(vd.drop(columns="persona_id"), on="transaction_id")
    ok = {}
    W = 78
    print("\n" + "=" * W + "\nRELATORIO DE VALIDACAO (SEED=%d, %d personas, %d meses, %d linhas)\n" % (K.SEED, tx.persona_id.nunique(), n_meses, len(tx)) + "=" * W)

    if calib:
        print("\n[0] Volume por persona (alvo = N sugerido x fator x meses/12)")
        for pid, alvo, real, rate, alvo_f, lim in calib:
            nota = "  <- limitada pela capacidade de ticket" if real < .97 * alvo else ("  <- elevado (redistribuicao)" if real > 1.02 * alvo else "")
            print(f"    {pid:<14} sugerido {alvo:>5}  gerado {real:>5}  ({real / alvo - 1:+.1%}){nota}")
        print(f"    TOTAL real {len(tx)}  (piso {K.PISO_TOTAL} para 10 personas x 12 meses)")

    print("\n[1] Distribuicao dos alvos")
    n = len(tx)
    print(f"    is_fraud (observado)  {tx.is_fraud.mean():.2%}  ({int(tx.is_fraud.sum())})   verdadeiro {tx.is_fraud_verdadeiro.mean():.2%}  ({int(tx.is_fraud_verdadeiro.sum())})")
    print(f"    is_bet   (observado)  {tx.is_bet.mean():.2%}  ({int(tx.is_bet.sum())})   verdadeiro {tx.is_bet_verdadeiro.mean():.2%}  ({int(tx.is_bet_verdadeiro.sum())})")
    print(f"    anomaly_score >= 0.80 {(tx.anomaly_score >= .8).mean():.2%}   risco comportamental verdadeiro {tx.risco_comportamental_verdadeiro.mean():.2%}")
    print(f"    inadimplente_mes      {sm.inadimplente_mes.mean():.2%} dos {len(sm)} persona-meses")
    pf = tx.is_fraud_verdadeiro.sum()
    pb = tx.is_bet_verdadeiro.sum()
    print(f"    ruido de rotulo: fraude {tx.rotulo_fraude_ruidoso.sum()} trocas ({tx.rotulo_fraude_ruidoso.sum() / max(pf, 1):.1%} dos positivos); "
          f"bet {tx.rotulo_bet_ruidoso.sum()} trocas ({tx.rotulo_bet_ruidoso.sum() / max(pb, 1):.1%})")
    print("    por persona:")
    t = tx.groupby("persona_id").agg(n=("amount", "size"), bets=("is_bet_verdadeiro", "sum"), fraude=("is_fraud_verdadeiro", "sum"),
                                     score80=("anomaly_score", lambda s: (s >= .8).mean()))
    t["inadimp"] = sm.groupby("persona_id").inadimplente_mes.mean()
    t["saldo_min"] = tx.groupby("persona_id").saldo_pos_transacao.min()
    t["saldo_med"] = tx.groupby("persona_id").saldo_pos_transacao.mean()
    t["saldo_max"] = tx.groupby("persona_id").saldo_pos_transacao.max()
    print(t.round(2).to_string(float_format=lambda v: f"{v:,.2f}").replace("\n", "\n    ").join(["    ", ""]))

    print("\n[2] Classes-alvo de consumo (piso %d)" % K.PISO_CLASSE_CONSUMO)
    cc = tx.category.value_counts()
    baixas = []
    for cat in K.CATEGORIAS_CONSUMO:
        v = int(cc.get(cat, 0))
        flag = "ok" if v >= K.PISO_CLASSE_CONSUMO else "ABAIXO DO PISO"
        if v < K.PISO_CLASSE_CONSUMO:
            baixas.append(cat)
        print(f"    {cat:<16}{v:>6}  {flag}")
    print("    classes de contexto (fora do F1 macro):", ", ".join(f"{c}={int(cc.get(c, 0))}" for c in K.CATEGORIAS_CONTEXTO))
    ok["piso_classes"] = not baixas
    ok["classes_abaixo"] = baixas
    ess = tx[tx.category.isin(K.CATEGORIAS_CONSUMO)]
    print(f"    is_essential entre consumo: {ess.is_essential.mean():.1%}   regras acionadas: {tx.regra_essencialidade_id.nunique()}")
    tr_d = ess[(ess.category == "TRANSPORTE")].groupby("persona_id").is_essential.mean().round(2)
    print("    TRANSPORTE essencial por persona:", dict(tr_d))

    print("\n[3] Correlacoes de Pearson (n pequeno: 10 personas => indicativo, sem significancia)")
    pers = ps.set_index("persona_id")
    g = pd.DataFrame({"renda": sm.groupby("persona_id").renda_mes.mean(), "escolaridade": pers.escolaridade, "score": pers.score_credito,
                      "risco": tx.groupby("persona_id").risco_comportamental_verdadeiro.mean(),
                      "inadimp": sm.groupby("persona_id").inadimplente_mes.mean()}).dropna()
    esperado = [("renda", "escolaridade", "+"), ("score", "inadimp", "-"), ("score", "risco", "-"), ("renda", "inadimp", "-"),
                ("escolaridade", "risco", "-")]
    cor_ok = {}
    for a, b, sinal in esperado:
        r = g[a].corr(g[b]) if len(g) > 2 else float("nan")
        bate = (r > 0) if sinal == "+" else (r < 0)
        cor_ok[f"{a}~{b}"] = bool(bate) if r == r else None
        print(f"    {a:<13}x {b:<10} r = {r:+.2f}   esperado {sinal}   {'ok' if bate else 'ATENCAO'}")
    pm_ = sm.merge(pers[["escolaridade", "score_credito"]], left_on="persona_id", right_index=True)
    rk = tx.assign(ym=tx.ts.dt.strftime("%Y-%m")).groupby(["persona_id", "ym"]).risco_comportamental_verdadeiro.mean().rename("risco").reset_index()
    pm_ = pm_.merge(rk, left_on=["persona_id", "ano_mes"], right_on=["persona_id", "ym"])
    print(f"    persona-mes (n={len(pm_)}): renda~risco {pm_.renda_mes.corr(pm_.risco):+.2f}  score~risco {pm_.score_credito.corr(pm_.risco):+.2f}  "
          f"escolaridade~risco {pm_.escolaridade.corr(pm_.risco):+.2f}")
    print("    nota: score_credito e uma premissa por persona (nao medido); a correlacao com risco e consistencia, nao evidencia.")
    ok["correlacoes"] = cor_ok

    print("\n[4] Reconciliacao temporal (recalculada do CSV exportado, em centavos)")
    cx = tx[tx.afeta_caixa].copy()
    cx["cents"] = (cx.amount * 100).round().astype(int)
    cx["ym"] = cx.ts.dt.strftime("%Y-%m")
    agg = cx.groupby(["persona_id", "ym"]).agg(cred=("cents", lambda s: s[s > 0].sum()), deb=("cents", lambda s: -s[s < 0].sum()))
    agg.index = agg.index.set_names(["persona_id", "ano_mes"])
    m = sm.set_index(["persona_id", "ano_mes"]).join(agg).fillna({"cred": 0, "deb": 0})
    c = lambda col: (m[col] * 100).round().astype(int)
    eq1 = (c("saldo_inicial") + m.cred.astype(int) - m.deb.astype(int) == c("saldo_final"))
    eq2 = (c("total_credito") == m.cred.astype(int)) & (c("total_debito") == m.deb.astype(int))
    enc = []
    for pid, gdf in m.reset_index().sort_values(["persona_id", "mes_idx"]).groupby("persona_id"):
        enc += list((gdf.saldo_final.shift(1).iloc[1:] * 100).round().astype(int) == (gdf.saldo_inicial.iloc[1:] * 100).round().astype(int))
    run = cx.sort_values(["persona_id", "ts"], kind="stable")  # ordem do CSV ja e a de processamento
    run = tx[tx.afeta_caixa].assign(cents=lambda d: (d.amount * 100).round().astype(int), sp=lambda d: (d.saldo_pos_transacao * 100).round().astype(int))
    pos_ok = True
    for pid, gdf in run.groupby("persona_id"):
        ini = int(round(sm[(sm.persona_id == pid) & (sm.mes_idx == 1)].saldo_inicial.iloc[0] * 100))
        pos_ok &= bool((ini + gdf.cents.cumsum() == gdf.sp).all())
    print(f"    saldo_inicial + credito - debito == saldo_final : {int(eq1.sum())}/{len(eq1)} persona-meses")
    print(f"    totais da serie == totais recalculados do CSV   : {int(eq2.sum())}/{len(eq2)}")
    print(f"    saldo_final(N) == saldo_inicial(N+1)           : {sum(enc)}/{len(enc)} encadeamentos")
    print(f"    saldo_pos_transacao == saldo inicial + soma acumulada : {'ok' if pos_ok else 'FALHOU'}")
    print(f"    nota: compras no cartao (afeta_caixa=False) entram na fatura e saem do caixa no PAGTO FATURA do mes seguinte.")
    ok["reconciliacao"] = bool(eq1.all() and eq2.all() and all(enc) and pos_ok)

    print("\n[5] Ausencia de PII real e integridade sintetica")
    txt = tx.description_masked
    padroes = {"CPF": r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "e-mail": r"[\w.]+@[\w.]+", "telefone": r"\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b",
               "CEP": r"\b\d{5}-?\d{3}\b"}
    pii = {k: int(txt.str.contains(v, regex=True).sum()) for k, v in padroes.items()}
    cn = tx.cnpj_destinatario.dropna()
    cn = cn[cn != ""]
    dv_ok = cn.map(cnpj_valido)
    ordem = cn.map(lambda s: int(re.sub(r"\D", "", s)[8:12]))
    print(f"    padroes de PII em description_masked: {pii}")
    print(f"    CNPJ sinteticos: {cn.nunique()} unicos, digitos verificadores validos {int(dv_ok.sum())}/{len(cn)}, filial >= 8000 em {int((ordem >= 8000).sum())}/{len(cn)}")
    print(f"    sintetico == True em {int(tx.sintetico.sum())}/{len(tx)} linhas")
    print("    colisao com CNPJ real: NAO verificavel offline; mitigada por filial 8000-9999 (praticamente inexistente no cadastro).")
    ok["pii"] = bool(sum(pii.values()) == 0 and dv_ok.all() and (ordem >= 8000).all() and tx.sintetico.all())

    print("\n[6] split.json")
    pe = sp["personas"]
    todos = set(tx.persona_id.unique())
    uni = pe["treino"] + pe["validacao"] + pe["teste"] + pe["holdout_generalizacao"]
    disj = len(uni) == len(set(uni)) and set(uni) == todos
    print(f"    treino {pe['treino']}\n    validacao {pe['validacao']}\n    teste {pe['teste']}\n    holdout {pe['holdout_generalizacao']}")
    print(f"    participacao de linhas (sem holdout): {sp['participacao_linhas_8_personas']}   alvo {sp['alvo_70_15_15']}")
    print(f"    grupos disjuntos e completos: {disj}")
    tp = sp["temporal_previsor"]
    print(f"    previsor: treino {tp['treino_meses'][0]}..{tp['treino_meses'][-1]}  teste {tp['teste_meses']}")
    cob = {k: (int(tx[tx.persona_id.isin(v)].is_fraud_verdadeiro.sum()), int(tx[tx.persona_id.isin(v)].is_bet_verdadeiro.sum()))
           for k, v in pe.items()}
    print("    (fraudes, apostas) por grupo:", cob)
    ok["split"] = bool(disj)

    print("\n[7] Auditoria de circularidade (o rotulo nao pode ser funcao trivial das features)")
    saida_ = tx[tx.amount < 0].copy()
    med = saida_.groupby("persona_id").amount.transform(lambda s: s.abs().median())
    saida_["valor_rel"] = saida_.amount.abs() / med
    saida_["hora"] = saida_.ts.dt.hour
    feats = {"valor_rel": saida_.valor_rel, "madrugada": saida_.horario_madrugada.astype(float), "dest_novo": saida_.destinatario_novo.astype(float),
             "hora": saida_.hora.astype(float), "min_desde_repasse": saida_.min_desde_repasse.fillna(1e5) * -1}
    aucs = {k: _auc(v, saida_.is_fraud_verdadeiro) for k, v in feats.items()}
    print("    AUC de cada feature isolada vs is_fraud verdadeiro:", {k: round(v, 3) for k, v in aucs.items()})
    reg = tx.mcc == "7995"
    tp_, fp_, fn_ = int((reg & tx.is_bet_verdadeiro).sum()), int((reg & ~tx.is_bet_verdadeiro).sum()), int((~reg & tx.is_bet_verdadeiro).sum())
    rec_, prec_ = tp_ / max(tp_ + fn_, 1), tp_ / max(tp_ + fp_, 1)
    print(f"    regra 'MCC == 7995' vs is_bet verdadeiro: recall {rec_:.2f}  precision {prec_:.2f}  (metas do detector: 0.95 / 0.90)")
    print(f"    apostas fora do 7995: {fn_};  nao-apostas com 7995 (lotericas): {fp_}")
    comb = reg | tx.mcc.isin(["7801", "7802"]) | tx.cnpj_destinatario.isin(pd.read_csv(saida / "lista_spa_sintetica.csv").cnpj) | \
        tx.description_masked.str.contains("BET|APOSTA", regex=True)
    tpc, fpc, fnc = int((comb & tx.is_bet_verdadeiro).sum()), int((comb & ~tx.is_bet_verdadeiro).sum()), int((~comb & tx.is_bet_verdadeiro).sum())
    print(f"    regra combinada (MCC 7995/7801/7802 | CNPJ na lista SPA | 'BET' no texto): recall {tpc / max(tpc + fnc, 1):.2f}  precision {tpc / max(tpc + fpc, 1):.2f}"
          f"  -> o que falta e o classificador de apoio (intermediadores)")
    ok["circularidade"] = bool(max(v for v in aucs.values() if v == v) < .97 and rec_ < .95)
    print(f"    veredito (limiar 0,97): {'ok, nenhuma regra simples reproduz o rotulo' if ok['circularidade'] else 'ATENCAO: rotulo muito acoplado a uma feature'}")
    print("    leitura: valor relativo sozinho ja separa bem a fraude (golpes sao maiores que a compra tipica), mas nao a explica por inteiro.")

    duros = ["reconciliacao", "pii", "split"]
    print("\n" + "=" * W)
    print("CHECAGENS DURAS:", {k: ok[k] for k in duros})
    print("PISO DE CLASSES :", "ok" if ok["piso_classes"] else f"abaixo do piso: {ok['classes_abaixo']}")
    print("=" * W)
    ok["duros_ok"] = all(ok[k] for k in duros)
    return ok


# =============================================================================== main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--piloto", action="store_true", help="5 personas, 6 meses")
    ap.add_argument("--meses", type=int, default=12)
    ap.add_argument("--personas", nargs="*", default=None)
    ap.add_argument("--fator-volume", type=float, default=K.FATOR_VOLUME)
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent / "saida"))
    args = ap.parse_args(argv)
    if args.piloto:
        args.meses, args.personas = 6, K.PILOTO_PERSONAS
    ids = args.personas or list(K.PERSONAS)
    personas = gerar_personas(ids, args.meses, args.fator_volume)
    df, serie = gerar_transacoes(personas, args.meses, piso_total=K.PISO_TOTAL if (args.meses == 12 and len(ids) == len(K.PERSONAS)) else None)
    calib = df.attrs.get("calibracao")
    df = rotular(df, personas)
    final = tabela_final(df)
    verdade = tabela_verdade(df, final)
    split = dividir(df, ids, args.meses)
    saida = Path(args.saida)
    exportar(df, final, verdade, serie, personas, split, saida, args)
    ok = validar(saida, args.meses, calib)
    return 0 if ok["duros_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
