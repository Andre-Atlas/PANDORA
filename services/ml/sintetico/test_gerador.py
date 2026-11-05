"""Testes do gerador sintetico. Rodar: pytest services/ml/sintetico -q  (ou python test_gerador.py)."""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo as K  # noqa: E402
import gerar_dataset as G  # noqa: E402

PILOTO = ["carla_34", "diego_24", "mariana_28"]


def _gerar(meses=3):
    p = G.gerar_personas(PILOTO, meses)
    df, serie = G.gerar_transacoes(p, meses)
    return p, G.rotular(df, p), serie


def test_cnpj_sintetico_valido_e_filial_alta():
    for chave in ["BET:BETX", "M:MERCADO BOM PRECO", "x", "y"]:
        c = G.cnpj_para(chave)
        assert G.cnpj_valido(c)
        assert int(re.sub(r"\D", "", c)[8:12]) >= 8000


def test_cnpj_invalido_e_rejeitado():
    c = G.cnpj_para("abc")
    ruim = c[:-1] + str((int(c[-1]) + 1) % 10)
    assert not G.cnpj_valido(ruim)


def test_determinismo_com_seed_fixa():
    _, a, _ = _gerar()
    _, b, _ = _gerar()
    pd.testing.assert_frame_equal(a[["ts", "cents", "cat", "desc"]], b[["ts", "cents", "cat", "desc"]])


def test_reconciliacao_em_centavos():
    _, df, serie = _gerar()
    cx = df[df["afeta"]]
    for pid, g in serie.groupby("persona_id"):
        for _, r in g.iterrows():
            tot = cx[(cx.persona_id == pid) & (cx.mes_idx == r.mes_idx)].cents
            assert round(r.saldo_inicial * 100) + tot.sum() == round(r.saldo_final * 100)
        assert (g.saldo_final.shift(1).iloc[1:].round(2) == g.saldo_inicial.iloc[1:].round(2)).all()


def test_todo_evento_cai_no_mes_da_serie():
    _, df, serie = _gerar()
    m = df.merge(serie[["persona_id", "mes_idx", "ano_mes"]], on=["persona_id", "mes_idx"])
    assert (m.ts.dt.strftime("%Y-%m") == m.ano_mes).all()


def test_nome_de_bet_nao_e_aposta_e_loterica_7995_nao_e_aposta():
    _, df, _ = _gerar(6)
    assert not df[df.cenario == "hn_loterica"].is_bet_verdadeiro.any()
    assert not df[df.cenario == "hn_nome_bet"].is_bet_verdadeiro.any()


def test_essencialidade_depende_de_persona_e_contexto():
    _, df, _ = _gerar(6)
    t = df[df.cat == "TRANSPORTE"]
    assert t[t.persona_id == "diego_24"].is_essential.mean() > .9          # entregador
    app = t[(t.persona_id == "carla_34") & (t["sub"] == "app_transporte")]
    assert not app.is_essential.any()                                         # app de fim de semana
    assert df[df["sub"] == "software_trabalho"].is_essential.all()
    assert not df[df["sub"] == "software_pessoal"].is_essential.any()          # mesmo MCC 5734, uso pessoal


def test_sem_pii_nas_descricoes():
    _, df, _ = _gerar()
    txt = df["desc"]
    assert not txt.str.contains(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|@", regex=True).any()


if __name__ == "__main__":
    for nome, fn in list(globals().items()):
        if nome.startswith("test_"):
            fn()
            print("ok", nome)
