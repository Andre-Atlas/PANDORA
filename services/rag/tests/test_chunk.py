from pandora_rag.ingest.chunk import dividir, fixo, limpar_anotacoes, numero_artigo, por_artigo, por_secao, por_sumula
from pandora_rag.ingest.fontes import Fonte


def fonte(**kw):
    base = dict(id="x", titulo="Lei X", orgao="O", tipo="lei", formato="html", url="http://x",
                camada_dominio="juridico_superendividamento", data_referencia_normativa="2021-07-01")
    base.update(kw)
    return Fonte(**base)


def blocos(*textos, pagina=None):
    return [{"p": pagina, "t": t} for t in textos]


def test_numero_artigo_formatos():
    assert numero_artigo("Art. 54-A. Este Capítulo") == "54-A"
    assert numero_artigo("Art. 1º A Lei") == "1"
    assert numero_artigo("‘Art. 104-C. Compete") == "104-C"
    assert numero_artigo("“ Art. 2º-A O valor") == "2-A"
    assert numero_artigo("Art. 1.015. Cabe") == "1015"
    assert numero_artigo("O art. 5º dispõe") is None
    assert numero_artigo("Artigo único") is None


def test_artigo_mantem_caput_paragrafos_e_incisos_juntos():
    ch = por_artigo(fonte(), blocos("CAPÍTULO I", "Das Disposições", "Art. 1º Fica criado:", "I - um;", "II - dois;",
                                    "§ 1º Algo.", "Art. 2º Outro."))
    assert [c.artigo for c in ch] == ["Art. 1", "Art. 2"]
    assert "II - dois;" in ch[0].texto and "§ 1º Algo." in ch[0].texto
    assert ch[0].secao == "Capítulo I — Das Disposições"


def test_artigo_citado_entre_aspas_vira_chunk_proprio_sem_aspas():
    ch = por_artigo(fonte(), blocos("Art. 1º A Lei passa a vigorar:", "‘Art. 54-A. Este Capítulo dispõe.", "§ 1º Texto.’"))
    citado = [c for c in ch if c.artigo == "Art. 54-A"][0]
    assert citado.citado and citado.texto.startswith("Art. 54-A.") and not citado.texto.endswith("’")


def test_artigo_revogado_e_marcadores_sao_descartados():
    ch = por_artigo(fonte(), blocos("Art. 1º Vale.", "(Revogado pela MP 1.394, de 2026)", "Art. 2º (Revogado pela Lei 14.430, de 2022)",
                                    "Art. 3º (VETADO).", "Art. 4º Também vale."))
    assert [c.artigo for c in ch] == ["Art. 1", "Art. 4"]
    assert ch[0].descartes["marcadores"] == 1 and ch[0].descartes["artigos_revogados"] == 2


def test_anotacoes_de_redacao_saem_do_texto():
    assert limpar_anotacoes("O prazo é de 5 dias. (Redação dada pela Lei nº 1, de 2015) (Vigência)") == "O prazo é de 5 dias."
    assert limpar_anotacoes("Texto (Vide Lei 2) seguinte") == "Texto seguinte"


def test_restricao_por_itens():
    ch = por_artigo(fonte(itens=["833"]), blocos("Art. 832. Não.", "Art. 833. São impenhoráveis:", "I - os bens.", "Art. 834. Não."))
    assert [c.artigo for c in ch] == ["Art. 833"] and ch[0].descartes["fora_da_lista"] == 2


def test_artigo_longo_divide_em_paragrafos_e_repete_cabecalho():
    corpo = ["Art. 9º Caput."] + [f"§ {i}º " + "palavra " * 120 for i in range(1, 7)]
    ch = por_artigo(fonte(), blocos(*corpo))
    assert len(ch) > 1 and all(c.palavras <= 600 for c in ch)
    assert ch[1].texto.startswith("Art. 9 (continuação)") and ch[1].id.endswith("-p2")


def test_sumula_filtra_cancelada_e_lista():
    f = fonte(id="stj", tipo="sumula", formato="pdf", itens=["548", "385"])
    b = blocos("Enunciados das Súmulas do STJ", "SÚMULA 548 VEJA MAIS", "Incumbe ao credor excluir o registro.", "em cinco dias.",
               "SÚMULA 603 (SÚMULA CANCELADA) VEJA MAIS", "Texto cancelado.", "SÚMULA 385 VEJA MAIS", "Da anotação irregular.",
               "SÚMULA 100 VEJA MAIS", "Fora da lista.", pagina=1)
    ch = por_sumula(f, b)
    assert sorted(c.artigo for c in ch) == ["Súmula 385", "Súmula 548"]
    assert [c for c in ch if c.artigo == "Súmula 548"][0].texto == "Súmula 548 do STJ: Incumbe ao credor excluir o registro. em cinco dias."


def test_secao_de_cartilha_agrupa_por_titulo():
    f = fonte(tipo="cartilha")
    par = "palavra " * 60
    ch = por_secao(f, blocos("1 ORÇAMENTO", par, par, "2 DÍVIDAS", par, par, pagina=3))
    assert len(ch) == 2 and ch[0].secao == "1 Orçamento" and ch[1].secao == "2 Dívidas" and ch[0].pagina == 3


def test_fixo_janela_e_sobreposicao():
    f = fonte()
    b = blocos(" ".join(f"w{i}" for i in range(1000)))
    ch = fixo(f, b, janela=100, sobreposicao=20)
    assert ch[0].palavras == 100 and ch[1].texto.split()[0] == "w80" and all(c.estrategia == "fixo" for c in ch)


def test_hash_estavel_e_sensivel_ao_texto():
    f = fonte()
    a = por_artigo(f, blocos("Art. 1º Texto A."))[0]
    b = por_artigo(f, blocos("Art. 1º Texto A."))[0]
    c = por_artigo(f, blocos("Art. 1º Texto B."))[0]
    assert a.hash == b.hash != c.hash


def test_dividir_despacha_pela_tipologia():
    assert dividir(fonte(tipo="resolucao"), blocos("Art. 1º X."))[0].estrategia == "estrutural"
    assert dividir(fonte(), blocos("Art. 1º " + "p " * 40), "fixo")[0].estrategia == "fixo"


def test_bloco_longo_de_cartilha_e_partido_em_frases():
    f = fonte(tipo="cartilha")
    frase = "Esta é uma frase de teste com algumas palavras para contar. "
    ch = por_secao(f, blocos(frase * 80))
    assert len(ch) > 1 and all(c.palavras <= 330 for c in ch)


def test_ids_unicos_com_artigo_citado_e_anexo_repetido():
    b = blocos("Art. 1º A Lei passa a vigorar:", "‘Art. 2º ..........................................’", "Art. 2º Esta Lei vigora.", "ANEXO", "Art. 2º Outro anexo.")
    ids = [c.id for c in por_artigo(fonte(), b)]
    from pandora_rag.ingest.chunk import garantir_ids_unicos
    assert "x#c2" in ids and "x#2" in ids
    assert len(set(c.id for c in garantir_ids_unicos(por_artigo(fonte(), b)))) == len(ids)


def test_texto_de_preenchimento_e_vigencia_encerrada_saem():
    assert limpar_anotacoes("Art. 4º ........................ § 2º Novo.") == "Art. 4º [...] § 2º Novo."
    assert limpar_anotacoes("Texto Vigência encerrada") == "Texto"


def test_artigo_citado_guarda_a_norma_alterada():
    b = blocos("Art. 30. A Lei nº 10.406, de 10 de janeiro de 2002 (Código Civil), passa a vigorar com as seguintes alterações:",
               "“Art. 1.368-B. A alienação fiduciária confere ao credor.”", "Art. 31. Esta Lei entra em vigor.")
    c = [x for x in por_artigo(fonte(), b) if x.citado][0]
    assert c.alvo == "Lei nº 10.406, de 10 de janeiro de 2002"
