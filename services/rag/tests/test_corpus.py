"""Verifica o corpus real, quando data/text já foi gerado (uv run pandora-rag extrair)."""
import collections

import pytest

from pandora_rag.config import TEXT_DIR
from pandora_rag.index.registro import montar_registros

pytestmark = pytest.mark.skipif(not TEXT_DIR.exists(), reason="corpus não extraído")


@pytest.fixture(scope="module")
def registros():
    return montar_registros()


def test_ids_unicos(registros):
    repetidos = [k for k, v in collections.Counter(r.id for r in registros).items() if v > 1]
    assert not repetidos, repetidos


def test_minimo_de_20_documentos_fonte(registros):
    assert len({r.fonte_id for r in registros}) >= 20


def test_todo_chunk_tem_link_e_data(registros):
    assert all(r.link.startswith("http") and r.data_referencia_normativa and r.texto.strip() for r in registros)


def test_artigos_centrais_do_superendividamento_existem(registros):
    base = {r.id.split("-p")[0] if r.id.rsplit("-p", 1)[-1].isdigit() else r.id for r in registros}
    assert {"lei-14181#c54-A", "lei-14181#c104-A", "lei-14181#c104-B", "lei-14181#c104-C"} <= base
    assert {"stj-sumulas#548", "stj-sumulas#385", "cpc#833"} <= base


def test_sem_lixo_de_cabecalho(registros):
    # a página de contato das cartilhas da CVM é conteúdo; o timbre repetido das resoluções não
    assert not [r.id for r in registros if r.tipo != "cartilha" and "Rua Sete de Setembro" in r.texto]
    assert not [r.id for r in registros if "Vigência encerrada" in r.texto]
