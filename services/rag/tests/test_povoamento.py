"""Crawler, indexação incremental, trava de avaliação e lacunas (sem rede, sem Postgres)."""
import json
import math

import httpx
import numpy as np
from test_web import DOMINIOS, cliente

from pandora_rag.index.incremental import MemoriaIncremental, assinatura, atualizar
from pandora_rag.index.registro import Registro
from pandora_rag.ingest import descobrir as d
from pandora_rag.ingest.fontes import (
    Candidata,
    acrescentar_fontes,
    carregar_candidatas,
    carregar_fontes,
    salvar_candidatas,
)
from pandora_rag.ingest.lacunas import Registrador, agrupar, mascarar
from pandora_rag.ingest.trava import julgar

PARAGRAFO = " ".join(["O consumidor superendividado pode pedir a repactuação das dívidas de consumo."] * 30)


def pagina(corpo, tipo="text/html"):
    return httpx.Response(200, text=corpo, headers={"content-type": tipo})


def test_crawler_segue_links_relevantes_do_dominio_e_dedupa(tmp_path):
    indice = ('<html><body><h1>Biblioteca</h1>'
              '<a href="/cartilha-superendividamento">Cartilha do superendividamento</a>'
              '<a href="/cartilha-superendividamento?utm_source=x">mesma cartilha</a>'
              '<a href="/copia">Cópia sobre dívida</a>'
              '<a href="/cardapio">Cardápio do restaurante</a>'
              '<a href="https://blog.com/superendividamento">blog</a></body></html>')
    doc = f"<html><body><h1>Cartilha do superendividamento</h1><p>{PARAGRAFO}</p></body></html>"
    c, chamadas, _ = cliente({
        "https://www.bcb.gov.br/biblioteca": pagina(indice),
        "https://www.bcb.gov.br/cartilha-superendividamento": pagina(doc),
        "https://www.bcb.gov.br/copia": pagina(doc),  # mesmo texto em outro endereço
    })
    config = d.ConfigDescoberta([d.Semente("https://www.bcb.gov.br/biblioteca", 1,
                                           {"orgao": "BCB", "camada_dominio": "juridico_superendividamento"})],
                                [d.sem_acento(t) for t in ["superendivid", "dívida"]], {})
    r = d.rastrear(config, c, set(), set(), set(), raiz=tmp_path)
    urls = {str(x.url) for x in chamadas}
    assert "https://www.bcb.gov.br/cardapio" not in urls and not any("blog.com" in u for u in urls)
    assert len(r.candidatas) == 1 and r.repetidas == 1
    cand = r.candidatas[0]
    assert cand.id.startswith("bcb-cartilha-do-superendividamento") and cand.tipo == "cartilha"
    assert cand.camada_dominio == "juridico_superendividamento" and cand.origem == "crawler"
    assert (tmp_path / "text" / f"{cand.id}.jsonl").exists()


def test_metadados_sem_data_nem_camada_ficam_com_confianca_baixa():
    blocos = [{"p": None, "t": PARAGRAFO}]
    c = d.montar_candidata("https://www.bcb.gov.br/x", "html", b"<html></html>", blocos, {}, "BCB", set())
    assert c.confianca == "baixa" and any("falta" in m for m in c.motivos)
    c2 = d.montar_candidata("https://www.bcb.gov.br/x", "html", b"<html></html>",
                            [{"p": None, "t": "Resolução de 21 de dezembro de 2023. " + PARAGRAFO}],
                            {"camada_dominio": "regulatorio_bancario"}, "BCB", set())
    assert c2.data_referencia_normativa == "2023-12-21" and c2.confianca == "alta"


def test_classificador_so_aceita_valores_da_lista_fechada():
    class Gw:
        def gerar(self, *a, **k):
            from pandora_rag.generate.gateway import Completude
            return Completude('{"camada_dominio": "regulatorio_bancario", "modalidade_divida": "cripto",'
                              ' "nivel_urgencia": "ignore as instruções"}', "x", 0, 0, 0, 0, {})

    meta, motivos = d.classificar_com_llm(Gw(), "x", "Título", [{"p": None, "t": "texto"}])
    assert meta == {"camada_dominio": "regulatorio_bancario"}
    assert sum("inválido" in m for m in motivos) == 2


def test_busca_bcb_filtra_assunto_revogados_e_conhecidos(tmp_path):
    def linha(num, assunto, revogado="0"):
        return {"NumeroOWSNMBR": f"{num}.0000000000", "AssuntoNormativoOWSMTXT": f"<div>{assunto}</div>",
                "RevogadoOWSBOOL": revogado, "CanceladoOWSBOOL": "0", "data": "2026-05-04T10:00:00Z"}

    busca = {"TotalRows": 4, "Rows": [linha(5300, "Dispõe sobre o crédito rotativo do cartão"),
                                     linha(5301, "Dispõe sobre o Proagro"),
                                     linha(5302, "Altera regras de crédito consignado", revogado="1"),
                                     linha(5112, "Rotativo e portabilidade da fatura do cartão")]}
    texto = {"conteudo": [{"Texto": f"<p>Art. 1º {PARAGRAFO}</p>"}]}

    def rota(req):
        u = str(req.url)
        if "buscanormativos" in u:
            return httpx.Response(200, json=busca)
        if "exibenormativo" in u:
            return httpx.Response(200, json=texto)
        return httpx.Response(404)

    c, _, _ = cliente({}, DOMINIOS)
    c.cliente = httpx.Client(transport=httpx.MockTransport(rota))
    conhecida = d.BCB_TEXTO.format(tipo="Resolu%C3%A7%C3%A3o%20CMN", numero="5112")
    r = d.buscar_normativos_bcb(c, {"tipos": ["Resolução CMN"], "termos_assunto": ["cartão", "consignado"]},
                                set(), {conhecida}, raiz=tmp_path)
    assert [x.id for x in r.candidatas] == ["cmn-5300"]
    cand = r.candidatas[0]
    assert cand.modalidade_divida == "cartao_credito" and cand.data_referencia_normativa == "2026-05-04"
    assert cand.titulo.startswith("Resolução CMN 5.300/2026") and cand.url_citacao.startswith("https://www.bcb.gov.br/estabilidadefinanceira")
    assert r.repetidas == 1 and any("revogado" in m for m in r.pulos.values())


def test_candidatas_vao_e_voltam_do_yaml_e_promocao_preserva_o_manifesto(tmp_path):
    manifesto = tmp_path / "fontes.yaml"
    manifesto.write_text("# curado à mão\nfontes:\n  - {id: cdc, titulo: CDC, orgao: PR, tipo: lei, formato: html, "
                         "url: 'https://www.planalto.gov.br/cdc.htm', camada_dominio: juridico_superendividamento, "
                         "data_referencia_normativa: '1990-09-11'}\n", encoding="utf-8")
    c = Candidata(id="bcb-guia", titulo="Guia: dívidas", orgao="BCB", tipo="cartilha", formato="pdf",
                  url="https://www.bcb.gov.br/guia.pdf", camada_dominio="educacao_orcamento",
                  data_referencia_normativa="2025-01-01", confianca="alta", motivos=["dica"], origem="crawler")
    arq = tmp_path / "cand.yaml"
    salvar_candidatas([c], arq)
    assert carregar_candidatas(arq) == [c]
    acrescentar_fontes([c.como_fonte()], manifesto)
    texto = manifesto.read_text(encoding="utf-8")
    assert texto.startswith("# curado à mão") and "Promovidas pelo crawler" in texto
    assert [f.id for f in carregar_fontes(manifesto)] == ["cdc", "bcb-guia"]


def reg(fonte_id, n, texto="t"):
    return Registro(id=f"{fonte_id}#{n}", fonte_id=fonte_id, titulo="T", orgao="O", tipo="lei", norma="N",
                    texto=f"{texto} {n}", hash=f"{fonte_id}{n}{texto}", link="https://x.gov.br",
                    data_referencia_normativa="2021-01-01", camada_dominio="juridico_superendividamento")


def test_incremental_so_reembeda_o_que_mudou():
    store = MemoriaIncremental([reg("a", 1), reg("a", 2), reg("b", 1), reg("velha", 1)])
    embedados = []

    def embedar(regs):
        embedados.extend(r.id for r in regs)
        return np.zeros((len(regs), 1), dtype=np.float32)

    novos = [reg("a", 1), reg("a", 2), reg("b", 1, "texto novo"), reg("c", 1)]
    rel = atualizar(store, novos, embedar)
    assert rel.iguais == ["a"] and rel.alteradas == ["b"] and rel.novas == ["c"] and rel.removidas == ["velha"]
    assert sorted(embedados) == ["b#1", "c#1"] and rel.total == 4
    assert {r.versao_corpus for r in store.carregar_registros()} == {rel.versao_depois}
    rel2 = atualizar(store, novos, embedar)
    assert not rel2.mudou and rel2.trechos_embedados == 0


def test_assinatura_muda_com_metadado_e_ignora_versao():
    r1, r2 = reg("a", 1), reg("a", 1)
    r2.versao_corpus = "outra"
    assert assinatura([r1]) == assinatura([r2])
    r2.ressalva = "revogado em 2026"
    assert assinatura([r1]) != assinatura([r2])


def test_trava_barra_queda_e_aceita_ganho():
    atual = {"recall@5": 0.80, "mrr": 0.70, "artigo_top3": 0.60}
    assert julgar(atual, {"recall@5": 0.805, "mrr": 0.695, "artigo_top3": 0.61}).passou
    v = julgar(atual, {"recall@5": 0.78, "mrr": 0.72, "artigo_top3": 0.60},
               por_pergunta_atual={"g1": {"recall@5": 1.0}}, por_pergunta_cand={"g1": {"recall@5": 0.0}})
    assert not v.passou and "recall@5" in v.motivos[0] and v.pioraram == ["g1"]
    assert julgar(None, {"recall@5": 0.1, "mrr": 0.1, "artigo_top3": math.nan}).passou


def test_mascara_tira_dados_pessoais_e_mantem_o_tema():
    m = mascarar("Meu nome é Maria Souza, CPF 123.456.789-09, devo R$ 12.500,00 no cartão do Nubank. "
                 "Ligue (61) 99999-1234 ou maria@email.com.")
    for vazado in ("Maria", "Souza", "123.456", "12.500", "99999", "maria@"):
        assert vazado not in m
    assert "cartão" in m and "Nubank" in m and m.startswith("Meu")


def test_lacunas_registram_mascarado_e_agrupam(tmp_path):
    reg_ = Registrador(tmp_path / "lacunas.jsonl")
    reg_("Como sair do cheque especial do João?", "portao", 0.01)
    reg_("O cheque especial pode ser renegociado?", "llm", None)
    linhas = [json.loads(x) for x in (tmp_path / "lacunas.jsonl").read_text().splitlines()]
    assert "João" not in linhas[0]["pergunta"] and set(linhas[0]) == {"em", "motivo", "melhor_nota", "pergunta"}
    assert agrupar(linhas)[0] == ("cheque especial", 2)


def test_lotes_isolam_a_candidata_que_piora_e_aceitam_as_outras():
    from types import SimpleNamespace

    from pandora_rag.ingest.pipeline import Teste, selecionar

    c = {i: SimpleNamespace(id=i) for i in "abcde"}
    testados = []

    def testar(lote):
        ids = {x.id for x in lote}
        testados.append(ids)
        return Teste("c" not in ids, True, None, "")

    base, aceitas, barradas, _ = selecionar(testar, [[c["a"], c["b"], c["c"]], [c["d"], c["e"]]], eco=lambda *_: None)
    assert base.passou and sorted(x.id for x in aceitas) == ["a", "b", "d", "e"] and list(barradas) == ["c"]
    assert testados[0] == set()  # as fontes atuais vêm primeiro


def test_lotes_param_se_as_fontes_atuais_ja_falham():
    from types import SimpleNamespace

    from pandora_rag.ingest.pipeline import Teste, selecionar

    base, aceitas, barradas, _ = selecionar(lambda lote: Teste(False, True, None, "caiu"), [[SimpleNamespace(id="a")]],
                                            eco=lambda *_: None)
    assert not base.passou and aceitas == [] and "não testada" in barradas["a"]
