"""Acesso educado: domínios oficiais, robots.txt, ritmo, desafio anti-robô e coleta condicional (sem rede)."""
import json

import httpx
import pytest

from pandora_rag.ingest.collect import (
    NOVA,
    SEM_MUDANCA,
    SO_LAYOUT,
    TEXTO_MUDOU,
    coletar,
    mudaram,
)
from pandora_rag.ingest.fontes import Fonte
from pandora_rag.ingest.web import (
    AntiRobo,
    BloqueadoRobots,
    ClienteEducado,
    Dominio,
    ForaDaLista,
    GrandeDemais,
    Robots,
    canonica,
    dominio_de,
)

DOMINIOS = [Dominio("planalto.gov.br", "Presidência"), Dominio("www.gov.br", "Governo", ("/mj/",)),
            Dominio("bcb.gov.br", "BCB")]
HTML = "<html><body><p>Art. 1º Esta lei trata do superendividamento do consumidor pessoa natural.</p></body></html>"


def cliente(rotas, dominios=DOMINIOS, **kw):
    """`rotas`: url -> httpx.Response ou função(request) -> Response. Sem rota, 404."""
    chamadas = []

    def tratar(req):
        chamadas.append(req)
        r = rotas.get(str(req.url))
        if callable(r):
            return r(req)
        return r if r is not None else httpx.Response(404)

    http = httpx.Client(transport=httpx.MockTransport(tratar), follow_redirects=True)
    esperas = []
    return ClienteEducado(dominios, http, dormir=esperas.append, relogio=lambda: 0.0, **kw), chamadas, esperas


def test_dominio_respeita_host_subdominio_e_caminho():
    assert dominio_de("https://www.planalto.gov.br/ccivil_03/leis/l8078.htm", DOMINIOS).host == "planalto.gov.br"
    assert dominio_de("https://www.gov.br/mj/pt-br/x.pdf", DOMINIOS).orgao == "Governo"
    assert dominio_de("https://www.gov.br/saude/pt-br/x", DOMINIOS) is None
    assert dominio_de("https://planalto.gov.br.golpe.com/x", DOMINIOS) is None
    assert dominio_de("http://www.planalto.gov.br/x", DOMINIOS) is None  # só https


def test_canonica_tira_rastreio_fragmento_e_sessao():
    assert canonica("https://WWW.BCB.gov.br/a/b/?utm_source=x&id=3#topo") == "https://www.bcb.gov.br/a/b?id=3"
    assert canonica("../c.pdf;jsessionid=AB12", "https://www.bcb.gov.br/a/b/") == "https://www.bcb.gov.br/a/c.pdf"


def test_robots_com_curinga_e_regra_mais_longa():
    r = Robots.ler("User-agent: *\nDisallow: /*/Lists/\nDisallow: /privado\nAllow: /privado/aberto\n")
    assert not r.permite("https://x.gov.br/site/Lists/doc")
    assert not r.permite("https://x.gov.br/privado/x")
    assert r.permite("https://x.gov.br/privado/aberto/y")
    assert r.permite("https://x.gov.br/publico")


def test_robots_bloqueia_e_fora_da_lista_nem_chega_a_rede():
    c, chamadas, _ = cliente({
        "https://www.planalto.gov.br/robots.txt": httpx.Response(200, text="User-agent: *\nDisallow: /proibido\n"),
    })
    with pytest.raises(BloqueadoRobots):
        c.get("https://www.planalto.gov.br/proibido/lei.htm")
    with pytest.raises(ForaDaLista):
        c.get("https://blog.advogado.com.br/superendividamento")
    assert [str(r.url) for r in chamadas] == ["https://www.planalto.gov.br/robots.txt"]


def test_redirecionamento_para_fora_da_lista_e_recusado():
    c, _, _ = cliente({
        "https://www.planalto.gov.br/lei": httpx.Response(302, headers={"location": "https://encurtador.com/x"}),
        "https://encurtador.com/x": httpx.Response(200, text=HTML, headers={"content-type": "text/html"}),
    })
    with pytest.raises(ForaDaLista):
        c.get("https://www.planalto.gov.br/lei")


def test_pagina_de_desafio_anti_robo_nao_e_contornada():
    desafio = '<form method="post" action="/_challenge"><title>Verificação de segurança</title></form>'
    c, chamadas, _ = cliente({"https://www.bcb.gov.br/x": httpx.Response(200, text=desafio, headers={"content-type": "text/html"})})
    with pytest.raises(AntiRobo):
        c.get("https://www.bcb.gov.br/x")
    assert not any(r.method == "POST" for r in chamadas)


def test_ritmo_por_dominio_e_limite_de_tamanho():
    c, _, esperas = cliente({
        "https://www.bcb.gov.br/a": httpx.Response(200, text=HTML, headers={"content-type": "text/html"}),
        "https://www.bcb.gov.br/b": httpx.Response(200, content=b"x" * 500, headers={"content-length": "500"}),
    }, max_bytes=200)
    c.get("https://www.bcb.gov.br/a")
    assert esperas and esperas[-1] == pytest.approx(1.0)  # o relógio parado obriga a esperar 1 s entre pedidos
    with pytest.raises(GrandeDemais):
        c.get("https://www.bcb.gov.br/b")


def fonte(**kw):
    base = dict(id="lei-x", titulo="Lei X", orgao="Presidência", tipo="lei", formato="html",
                url="https://www.planalto.gov.br/lei-x.htm", camada_dominio="juridico_superendividamento",
                data_referencia_normativa="2021-07-01")
    return Fonte(**{**base, **kw})


def test_coleta_classifica_nova_layout_texto_e_304(tmp_path):
    estado = {"html": HTML, "etag": '"v1"'}

    def pagina(req):
        if req.headers.get("if-none-match") == estado["etag"]:
            return httpx.Response(304)
        return httpx.Response(200, text=estado["html"], headers={"content-type": "text/html", "etag": estado["etag"]})

    c, _, _ = cliente({"https://www.planalto.gov.br/lei-x.htm": pagina})
    kw = dict(raiz=tmp_path / "raw", texto_dir=tmp_path / "text", lock_path=tmp_path / "corpus.lock", cliente=c)
    assert coletar([fonte()], **kw) == {"lei-x": NOVA}
    assert coletar([fonte()], **kw) == {"lei-x": SEM_MUDANCA}  # 304
    estado.update(html=HTML.replace("<body>", "<body><div><script>x</script></div>"), etag='"v2"')
    assert coletar([fonte()], **kw) == {"lei-x": SO_LAYOUT}
    estado.update(html=HTML.replace("pessoa natural", "pessoa natural de boa-fé"), etag='"v3"')
    situacao = coletar([fonte()], **kw)
    assert situacao == {"lei-x": TEXTO_MUDOU} and mudaram(situacao) == ["lei-x"]
    lock = json.loads((tmp_path / "corpus.lock").read_text())["fontes"]["lei-x"]
    assert lock["etag"] == '"v3"' and len(lock["sha256_texto"]) == 64


def test_coleta_recusa_conteudo_de_outro_formato(tmp_path):
    c, _, _ = cliente({"https://www.planalto.gov.br/lei-x.htm": httpx.Response(200, content=b"%PDF-1.4 ...",
                                                                               headers={"content-type": "text/html"})})
    s = coletar([fonte()], raiz=tmp_path, texto_dir=tmp_path, lock_path=tmp_path / "l", cliente=c)
    assert s["lei-x"].startswith("falha: conteúdo não parece html")


def test_fonte_recusa_chave_desconhecida_e_valor_fora_da_lista():
    with pytest.raises(ValueError):
        fonte(camada="x")
    with pytest.raises(ValueError):
        fonte(modalidade_divida="cripto")
    with pytest.raises(ValueError):
        fonte(data_referencia_normativa="01/07/2021")
