"""Coleta do catálogo (#54): idempotência, isolamento de falhas, robots.txt, repetição e inventário."""
import hashlib
import json
from datetime import datetime, timezone

import httpx
import pytest

from pandora_rag.coleta.catalogo import Alvo, ItemCatalogo, carregar_catalogo
from pandora_rag.coleta.executor import coletar_catalogo, situacao_do_item
from pandora_rag.coleta.inventario import markdown
from pandora_rag.ingest.fontes import carregar_fontes

HTML = b"<!doctype html><html><body>lei</body></html>"
PDF = b"%PDF-1.7 conteudo"
API = b'[{"data": "01/11/2026", "valor": "10.5"}]'


def item(*alvos: Alvo, numero: int = 1) -> ItemCatalogo:
    return ItemCatalogo(numero=numero, nome="x", grupo=1, orgao="o", frequencia="mensal", alvos=list(alvos))


def alvo(id_: str, formato: str = "html", ext: str | None = None, **kw) -> Alvo:
    return Alvo(id=id_, formato=formato, ext=ext, url=f"https://exemplo.gov.br/{id_}", **kw)


class Servidor:
    """Transporte falso: respostas por caminho, com contagem de pedidos."""

    def __init__(self, rotas: dict, robots: str | None = None, robots_status: int = 200) -> None:
        self.rotas, self.robots, self.robots_status, self.pedidos = dict(rotas), robots, robots_status, []

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.pedidos.append(req.url.path)
        if req.url.path == "/robots.txt":
            if self.robots_status >= 500:
                return httpx.Response(self.robots_status)
            return httpx.Response(404) if self.robots is None else httpx.Response(200, text=self.robots)
        resposta = self.rotas.get(req.url.path, httpx.Response(404))
        if callable(resposta):
            return resposta()
        return resposta


def rodar(tmp_path, itens, servidor, **kw):
    cliente = httpx.Client(transport=httpx.MockTransport(servidor))
    return coletar_catalogo(
        itens, raiz=tmp_path / "raw", lock_path=tmp_path / "catalogo.lock.json", cliente=cliente,
        dormir=lambda s: None, agora=lambda: datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc), **kw,
    )


def lock(tmp_path) -> dict:
    return json.loads((tmp_path / "catalogo.lock.json").read_text(encoding="utf-8"))


def test_um_coletor_por_tipo_grava_bruto_com_data_e_hash(tmp_path):
    itens = [item(alvo("a"), alvo("b", "pdf"), alvo("c", "api", "json"))]
    srv = Servidor({"/a": httpx.Response(200, content=HTML), "/b": httpx.Response(200, content=PDF),
                    "/c": httpx.Response(200, content=API)})
    assert rodar(tmp_path, itens, srv) == {"a": "coletada", "b": "coletada", "c": "coletada"}
    assert (tmp_path / "raw/catalogo/a.html").read_bytes() == HTML
    assert (tmp_path / "raw/catalogo/b.pdf").read_bytes() == PDF
    assert (tmp_path / "raw/catalogo/c.json").read_bytes() == API
    reg = lock(tmp_path)["alvos"]["b"]
    assert reg["sha256"] == hashlib.sha256(PDF).hexdigest()
    assert reg["coletado_em"] == "2026-11-17T12:00:00Z" and reg["bytes"] == len(PDF)


def test_alvo_do_corpus_usa_o_caminho_do_rag(tmp_path):
    srv = Servidor({"/a": httpx.Response(200, content=HTML)})
    rodar(tmp_path, [item(alvo("a", fonte_id="cdc"))], srv)
    assert (tmp_path / "raw/cdc.html").exists()


def test_rodar_de_novo_sem_mudancas_nao_duplica_nem_altera(tmp_path):
    itens = [item(alvo("a"), alvo("b", "pdf"))]
    srv = Servidor({"/a": httpx.Response(200, content=HTML), "/b": httpx.Response(200, content=PDF)})
    rodar(tmp_path, itens, srv)
    arquivos = sorted(p.relative_to(tmp_path) for p in (tmp_path / "raw").rglob("*"))
    texto_lock = (tmp_path / "catalogo.lock.json").read_text(encoding="utf-8")
    mtimes = {p: p.stat().st_mtime_ns for p in (tmp_path / "raw").rglob("*") if p.is_file()}

    segunda = rodar(tmp_path, itens, srv)

    assert segunda == {"a": "sem mudança", "b": "sem mudança"}
    assert sorted(p.relative_to(tmp_path) for p in (tmp_path / "raw").rglob("*")) == arquivos
    assert {p: p.stat().st_mtime_ns for p in (tmp_path / "raw").rglob("*") if p.is_file()} == mtimes
    assert (tmp_path / "catalogo.lock.json").read_text(encoding="utf-8") == texto_lock


def test_ruido_de_pagina_web_nao_conta_como_mudanca(tmp_path):
    def pagina(token: str, contador: int, texto: str = "lei"):
        corpo = (f'<html><body><p>{texto}</p><script id="f5_cspm">var f5_p="{token}";</script>'
                 f'<script>{{"key":"{token}"}}</script><!-- Recuperados {contador} objetos do Redis --></body></html>')
        return Servidor({"/a": httpx.Response(200, content=corpo.encode())})

    itens = [item(alvo("a"))]
    assert rodar(tmp_path, itens, pagina("AAAA", 1983)) == {"a": "coletada"}
    primeiro = (tmp_path / "raw/catalogo/a.html").read_bytes()
    assert rodar(tmp_path, itens, pagina("BBBB", 1963)) == {"a": "sem mudança"}
    assert (tmp_path / "raw/catalogo/a.html").read_bytes() == primeiro
    assert rodar(tmp_path, itens, pagina("CCCC", 1963, texto="lei alterada")) == {"a": "coletada"}
    reg = lock(tmp_path)["alvos"]["a"]
    assert reg["sha256"] == hashlib.sha256((tmp_path / "raw/catalogo/a.html").read_bytes()).hexdigest()
    assert reg["sha256_texto"] != hashlib.sha256(b"lei").hexdigest()


def test_conteudo_novo_atualiza_hash_sem_criar_outro_arquivo(tmp_path):
    itens = [item(alvo("a"))]
    rodar(tmp_path, itens, Servidor({"/a": httpx.Response(200, content=HTML)}))
    novo = HTML.replace(b"lei", b"lei alterada")
    assert rodar(tmp_path, itens, Servidor({"/a": httpx.Response(200, content=novo)})) == {"a": "coletada"}
    assert (tmp_path / "raw/catalogo/a.html").read_bytes() == novo
    assert lock(tmp_path)["alvos"]["a"]["sha256"] == hashlib.sha256(novo).hexdigest()
    assert [p.name for p in (tmp_path / "raw/catalogo").iterdir()] == ["a.html"]


def test_falha_em_uma_fonte_nao_derruba_as_demais(tmp_path):
    itens = [item(alvo("ruim"), alvo("boa", "pdf"), alvo("html-de-erro", "pdf"))]
    srv = Servidor({"/ruim": httpx.Response(404), "/boa": httpx.Response(200, content=PDF),
                    "/html-de-erro": httpx.Response(200, content=HTML)})
    sit = rodar(tmp_path, itens, srv)
    assert sit == {"ruim": "falha", "boa": "coletada", "html-de-erro": "falha"}
    alvos = lock(tmp_path)["alvos"]
    assert "404" in alvos["ruim"]["erro"] and "PDF" in alvos["html-de-erro"]["erro"]
    assert not (tmp_path / "raw/catalogo/html-de-erro.pdf").exists()


def test_erro_inesperado_tambem_fica_isolado(tmp_path):
    def explode():
        raise RuntimeError("bug")

    sit = rodar(tmp_path, [item(alvo("a"), alvo("b"))],
                Servidor({"/a": explode, "/b": httpx.Response(200, content=HTML)}))
    assert sit == {"a": "falha", "b": "coletada"}


def test_falha_preserva_o_ultimo_bruto_bom(tmp_path):
    itens = [item(alvo("a"))]
    rodar(tmp_path, itens, Servidor({"/a": httpx.Response(200, content=HTML)}))
    assert rodar(tmp_path, itens, Servidor({})) == {"a": "falha"}
    reg = lock(tmp_path)["alvos"]["a"]
    assert reg["situacao"] == "falha" and reg["sha256"] == hashlib.sha256(HTML).hexdigest()
    assert (tmp_path / "raw/catalogo/a.html").read_bytes() == HTML


def test_respeita_robots_txt_em_html_e_pdf(tmp_path):
    srv = Servidor({"/a": httpx.Response(200, content=HTML), "/privado/b": httpx.Response(200, content=PDF)},
                   robots="User-agent: *\nDisallow: /privado/")
    itens = [item(alvo("a"), Alvo(id="b", formato="pdf", url="https://exemplo.gov.br/privado/b"))]
    assert rodar(tmp_path, itens, srv) == {"a": "coletada", "b": "bloqueada_robots"}
    assert "/privado/b" not in srv.pedidos


def test_robots_com_erro_de_servidor_nao_coleta_a_origem(tmp_path):
    srv = Servidor({"/a": httpx.Response(200, content=HTML)}, robots_status=503)
    assert rodar(tmp_path, [item(alvo("a"))], srv) == {"a": "falha"}
    assert "/a" not in srv.pedidos


def test_api_documentada_nao_consulta_robots(tmp_path):
    srv = Servidor({"/c": httpx.Response(200, content=API)}, robots="User-agent: *\nDisallow: /")
    assert rodar(tmp_path, [item(alvo("c", "api", "json"))], srv) == {"c": "coletada"}
    assert "/robots.txt" not in srv.pedidos


def test_repete_em_503_e_429_e_depois_segue(tmp_path):
    respostas = iter([httpx.Response(503), httpx.Response(429, headers={"Retry-After": "2"}),
                      httpx.Response(200, content=HTML)])
    esperas: list[float] = []
    cliente = httpx.Client(transport=httpx.MockTransport(
        lambda req: httpx.Response(404) if req.url.path == "/robots.txt" else next(respostas)))
    sit = coletar_catalogo([item(alvo("a"))], raiz=tmp_path / "raw", lock_path=tmp_path / "l.json",
                           cliente=cliente, dormir=esperas.append)
    assert sit == {"a": "coletada"}
    assert 2.0 in esperas  # respeitou o Retry-After


def test_304_com_bruto_anterior_vale_como_sem_mudanca(tmp_path):
    itens = [item(alvo("c", "api", "json"))]
    rodar(tmp_path, itens, Servidor({"/c": httpx.Response(200, content=API)}))
    assert rodar(tmp_path, itens, Servidor({"/c": httpx.Response(304)})) == {"c": "sem mudança"}
    assert lock(tmp_path)["alvos"]["c"]["sha256"] == hashlib.sha256(API).hexdigest()


def test_304_sem_bruto_anterior_e_falha(tmp_path):
    srv = Servidor({"/c": httpx.Response(304)})
    assert rodar(tmp_path, [item(alvo("c", "api", "json"))], srv) == {"c": "falha"}
    assert srv.pedidos.count("/c") == 3


def test_desiste_depois_de_3_tentativas(tmp_path):
    srv = Servidor({"/a": httpx.Response(503)})
    assert rodar(tmp_path, [item(alvo("a"))], srv) == {"a": "falha"}
    assert srv.pedidos.count("/a") == 3


def test_nao_repete_em_404(tmp_path):
    srv = Servidor({})
    rodar(tmp_path, [item(alvo("a"))], srv)
    assert srv.pedidos.count("/a") == 1


def test_limite_de_requisicoes_por_origem(tmp_path):
    esperas: list[float] = []
    srv = Servidor({"/a": httpx.Response(200, content=HTML), "/b": httpx.Response(200, content=HTML)})
    cliente = httpx.Client(transport=httpx.MockTransport(srv))
    coletar_catalogo([item(alvo("a"), alvo("b"))], raiz=tmp_path / "raw", lock_path=tmp_path / "l.json",
                     cliente=cliente, intervalo=1.0, dormir=esperas.append, relogio=lambda: 100.0)
    assert esperas == [1.0]  # a 2ª requisição à mesma origem espera o intervalo


def test_manual_fica_registrado_sem_baixar(tmp_path):
    manual = Alvo(id="m", manual="sem URL estável")
    srv = Servidor({})
    assert rodar(tmp_path, [item(manual, alvo("a"))], srv) == {"m": "manual", "a": "falha"}
    assert lock(tmp_path)["alvos"]["m"] == {"situacao": "manual", "motivo": "sem URL estável"}


def test_situacao_do_item(tmp_path):
    it = item(alvo("a"), Alvo(id="m", manual="x"))
    assert situacao_do_item(it, {"alvos": {}}) == "pendente"
    assert situacao_do_item(it, {"alvos": {"a": {"situacao": "coletada"}, "m": {"situacao": "manual"}}}) == "mista"
    assert situacao_do_item(it, {"alvos": {"a": {"situacao": "falha"}, "m": {"situacao": "manual"}}}) == "falha"
    assert situacao_do_item(item(Alvo(id="m", manual="x")), {"alvos": {"m": {"situacao": "manual"}}}) == "manual"
    assert situacao_do_item(item(alvo("a")), {"alvos": {"a": {"situacao": "coletada"}}}) == "coletada"


def test_alvo_automatico_exige_url_e_formato():
    with pytest.raises(ValueError):
        Alvo(id="x", url="https://x")


# --- o inventário real em fontes.yaml ---


def test_catalogo_tem_os_31_itens_com_frequencia_e_alvos():
    itens = carregar_catalogo()
    assert [i.numero for i in itens] == list(range(1, 32))
    assert all(i.alvos and i.frequencia and i.orgao for i in itens)


def test_todo_alvo_automatico_tem_url_https_e_todo_manual_tem_motivo():
    for i in carregar_catalogo():
        for a in i.alvos:
            assert a.manual or a.url.startswith("https://"), a.id
            assert not a.manual or len(a.manual) > 20, a.id


def test_todas_as_fontes_do_corpus_estao_no_inventario_com_a_mesma_url():
    por_id = {f.id: f for f in carregar_fontes()}
    ligados = {a.fonte_id: a for i in carregar_catalogo() for a in i.alvos if a.fonte_id}
    assert set(ligados) == set(por_id)
    assert all(ligados[k].url == por_id[k].url for k in por_id)


def test_markdown_lista_os_31_itens():
    texto = markdown(carregar_catalogo(), {"alvos": {}})
    assert all(f"| {n} |" in texto for n in range(1, 32))
    assert "Alvos de tratamento manual" in texto
