import math

import pytest

from evals.metrics import estatistica as est
from evals.metrics import recuperacao as rec
from evals.metrics import respostas as res
from evals.metrics import textos as tx

ART = "O consumidor superendividado pode pedir ao juiz a repactuação das dívidas com plano de pagamento em cinco anos"


def test_palavras_preserva_acentos_e_numeros():
    assert tx.palavras("Lei 14.181/2021: repactuação, R$ 1.000,50!") == ["lei", "14.181", "2021", "repactuação", "r", "1.000,50"]


def test_rouge_identico_e_disjunto():
    assert tx.rouge("a dívida prescreve em cinco anos", "a dívida prescreve em cinco anos") == {"rouge1": 1.0, "rouge2": 1.0, "rougeL": 1.0}
    assert tx.rouge("alfa beta gama", "um dois três")["rouge1"] == 0.0


def test_rouge1_valor_conhecido():
    # hip 4 palavras, ref 5, interseção 3 -> P=3/4, R=3/5, F=2PR/(P+R)=2/3
    r = tx.rouge("a dívida prescreve rápido", "a dívida prescreve em cinco")
    assert r["rouge1"] == pytest.approx(2 * 0.75 * 0.6 / (0.75 + 0.6))


def test_rouge_nao_descarta_acentos():
    assert tx.rouge("repactuação já", "repactuação já")["rouge1"] == 1.0


def test_bleu_identico_100_e_diferente_baixo():
    frase = "o prazo para a baixa do registro é de cinco dias úteis após o pagamento"
    assert tx.bleu([frase], [frase]) == pytest.approx(100.0)
    assert tx.bleu(["xyz abc def ghi jkl mno"], [frase]) < 5
    assert tx.bleu_sentenca(frase, frase) == pytest.approx(100.0)


def test_numeros_ignora_separador_de_milhar():
    assert tx.numeros("R$ 1.000 em 60 meses, 1,5%") == {"1000", "60", "1.5"}
    assert tx.acerto_numerico("pague 60 meses", "60 meses e R$ 600") == 0.5
    assert tx.acerto_numerico("qualquer", "sem números") is None


def test_cobertura_por_trigramas():
    assert rec.cobertura(ART, ART) == 1.0
    assert rec.cobertura(ART, "texto totalmente diferente sem relação alguma com o assunto") == 0.0
    assert 0.4 < rec.cobertura(ART, "o consumidor superendividado pode pedir ao juiz a repactuação das dívidas") < 1.0


OURO = [rec.Ouro("lei", ART, "Art. 104-A"), rec.Ouro("stj", "Incumbe ao credor a exclusão do registro da dívida em nome do devedor no cadastro de inadimplentes", "Súmula 548")]


def test_recall_e_mrr_com_ordem_conhecida():
    r = [("x", "irrelevante"), ("lei", ART), ("y", "outro"), ("stj", OURO[1].trecho)]
    m = rec.avaliar(r, OURO, ks=(1, 3, 5))
    assert m["recall@1"] == 0 and m["recall@3"] == 0.5 and m["recall@5"] == 1.0
    assert m["precision@3"] == pytest.approx(1 / 3) and m["hit@1"] == 0 and m["hit@3"] == 1
    assert m["mrr"] == 0.5


def test_ndcg_perfeito_e_pior_caso():
    perfeito = rec.avaliar([("lei", ART), ("stj", OURO[1].trecho)], OURO)
    assert perfeito["ndcg@10"] == pytest.approx(1.0)
    pior = rec.avaliar([("x", "a"), ("y", "b"), ("lei", ART)], OURO)
    ideal = 1 + 1 / math.log2(3)
    assert pior["ndcg@10"] == pytest.approx((1 / math.log2(4)) / ideal)


def test_chunk_repetido_do_mesmo_ouro_nao_conta_duas_vezes():
    m = rec.avaliar([("lei", ART), ("lei", ART + " parte dois")], OURO[:1])
    assert m["recall@5"] == 1.0 and m["ndcg@10"] == pytest.approx(1.0)


def test_artigo_dividido_em_duas_partes_marca_as_duas():
    meio = len(ART.split()) // 2
    p1, p2 = " ".join(ART.split()[: meio + 3]), " ".join(ART.split()[meio - 3 :])
    assert rec.cobre("lei", p1, OURO[0]) and rec.cobre("lei", p2, OURO[0])


def test_fonte_diferente_nao_cobre():
    assert not rec.cobre("outra", ART, OURO[0])


def test_acerto_artigo_top3():
    assert rec.acerto_artigo([("lei", "Art. 104-A"), ("x", None)], OURO) == 1.0
    assert rec.acerto_artigo([("x", None), ("y", None), ("z", None), ("lei", "Art. 104-A")], OURO) == 0.0
    assert math.isnan(rec.acerto_artigo([("x", None)], [rec.Ouro("x", "t")]))


def test_pergunta_sem_ouro_levanta():
    with pytest.raises(ValueError):
        rec.avaliar([("a", "b")], [])


def test_citacao_valida_exige_marcador_norma_link_e_artigo():
    ok = res.CitacaoResposta("Lei 14.181/2021", "https://planalto.gov.br/x", "Art. 54-A")
    assert res.citacao_valida("A regra existe [1].", [ok])
    assert not res.citacao_valida("A regra existe.", [ok])
    assert not res.citacao_valida("A regra existe [1].", [])
    assert not res.citacao_valida("A regra existe [1].", [res.CitacaoResposta("Lei", "sem-link", "Art. 1")])
    assert not res.citacao_valida("[1]", [res.CitacaoResposta("Lei", "https://x", None)])
    assert res.citacao_valida("[1]", [res.CitacaoResposta("Cartilha", "https://x", None)], exige_artigo=False)


def test_abstencao_correta_e_recusa_indevida():
    m = res.abstencao([True, True, False, False, False], [True, False, False, True, False])
    assert m["abstencao_correta"] == 0.5 and m["recusa_indevida"] == pytest.approx(1 / 3) and m["precisao_abstencao"] == 0.5


def test_ic_bootstrap_contem_a_media_e_e_reprodutivel():
    v = [1, 0, 1, 1, 0, 1, 1, 1, 0, 1] * 5
    m, lo, hi = est.ic_bootstrap(v)
    assert lo <= m <= hi and m == pytest.approx(0.7) and (m, lo, hi) == est.ic_bootstrap(v)


def test_diferenca_pareada_e_mcnemar():
    a = [1] * 30 + [0] * 10
    b = [1] * 10 + [0] * 30
    d, lo, hi = est.ic_diferenca_pareada(a, b)
    assert d == pytest.approx(0.5) and lo > 0
    assert est.mcnemar_exato([True] * 20 + [False] * 5, [False] * 20 + [True] * 5) < 0.01
    assert est.mcnemar_exato([True, False], [True, False]) == 1.0
