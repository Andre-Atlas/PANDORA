import zlib

import numpy as np
import pytest

from pandora_rag.index.registro import Registro
from pandora_rag.index.store import MemoryStore, mascara
from pandora_rag.index.tokenizer import tokenizar
from pandora_rag.retrieve.hybrid import IndiceBM25, Parametros, Retriever, rrf


def reg(i, texto, artigo=None, camada="juridico_superendividamento", **kw):
    base = dict(id=i, fonte_id=i.split("#")[0], titulo="T", orgao="O", tipo="lei", norma="Lei X", artigo=artigo, texto=texto,
                hash=i, link="http://x", data_referencia_normativa="2021-07-01", camada_dominio=camada)
    base.update(kw)
    return Registro(**base)


class EmbedderFalso:
    """Bag-of-words em hash: determinístico e sem download de modelo."""

    dim = 64

    def _vec(self, t):
        v = np.zeros(self.dim, dtype=np.float32)
        for tok in tokenizar(t):
            v[zlib.crc32(tok.encode()) % self.dim] += 1
        n = np.linalg.norm(v)
        return v / n if n else v

    def passagens(self, ts):
        return np.stack([self._vec(t) for t in ts])

    consultas = passagens


def test_tokenizador_preserva_numeros_de_norma():
    assert tokenizar("Lei 14.181/2021") == ["lei", "14181", "2021"]
    assert tokenizar("art. 54-A") == ["54-a"]
    assert tokenizar("Resolução CMN nº 5.112") == ["resoluc", "cmn", "n", "5112"] or "5112" in tokenizar("Resolução CMN nº 5.112")


def test_tokenizador_normaliza_plural_e_acento():
    assert tokenizar("comissões") == tokenizar("comissão")
    assert tokenizar("dívidas") == tokenizar("dívida")
    assert tokenizar("o a de da") == []


def test_rrf_soma_contribuicoes_e_respeita_pesos():
    f = rrf([([1, 2, 3], 1.0), ([3, 2, 1], 1.0)], k=60)
    assert f[2] == pytest.approx(2 / 62) and f[1] == f[3]
    g = rrf([([1, 2], 2.0), ([2, 1], 1.0)], k=60)
    assert g[1] > g[2]


def test_filtro_por_metadado_na_memoria():
    regs = [reg("a#1", "x", camada="educacao_orcamento"), reg("b#1", "y"), reg("c#1", "z", elegivel_lei_14181=False)]
    assert mascara(regs, {"camada_dominio": "educacao_orcamento"}).tolist() == [True, False, False]
    assert mascara(regs, {"camada_dominio": ["educacao_orcamento", "juridico_superendividamento"]}).tolist() == [True, True, True]
    assert mascara(regs, {"elegivel_lei_14181": False}).tolist() == [False, False, True]


@pytest.fixture
def retriever():
    regs = [
        reg("lei#54-A", "Art. 54-A. Este Capítulo dispõe sobre a prevenção do superendividamento da pessoa natural.", "Art. 54-A"),
        reg("lei#104-A", "Art. 104-A. O juiz poderá instaurar processo de repactuação de dívidas com plano de pagamento em cinco anos.", "Art. 104-A"),
        reg("stj#548", "Súmula 548: incumbe ao credor excluir o registro da dívida em cinco dias úteis.", "Súmula 548"),
        reg("cvm#1", "Consultor de valores mobiliários deve verificar a adequação do produto ao perfil.", camada="regulatorio_bancario"),
    ]
    emb = EmbedderFalso()
    store = MemoryStore(regs, emb.passagens([r.texto_indexado() for r in regs]))
    return Retriever(store, IndiceBM25(regs), emb)


def test_busca_exata_por_numero_vem_do_bm25(retriever):
    hits = retriever.buscar("o que diz o artigo 104-A", k=2, params=Parametros(usar_vetor=False))
    assert hits[0].registro.id == "lei#104-A" and hits[0].score_bm25 > 0 and hits[0].score_vetor is None


def test_fusao_traz_o_artigo_certo_no_topo(retriever):
    hits = retriever.buscar("prazo para o credor excluir o registro da dívida", k=3)
    assert hits[0].registro.id == "stj#548" and hits[0].rank_vetor and hits[0].rank_bm25


def test_busca_respeita_filtro(retriever):
    hits = retriever.buscar("dívida", k=5, filtro={"camada_dominio": "regulatorio_bancario"})
    assert [h.registro.id for h in hits] == ["cvm#1"]


def test_consulta_sem_termos_conhecidos_nao_quebra(retriever):
    assert retriever.buscar("xyzzy qwerty", k=3, params=Parametros(usar_vetor=False)) == []
