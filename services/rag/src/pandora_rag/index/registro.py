"""Registro de chunk com todos os metadados que o banco vetorial guarda."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from pandora_rag.config import LOCK_PATH, TEXT_DIR
from pandora_rag.ingest.chunk import dividir
from pandora_rag.ingest.collect import ler_lock
from pandora_rag.ingest.extract import carregar_texto
from pandora_rag.ingest.fontes import Fonte, carregar_fontes


class Registro(BaseModel):
    id: str
    fonte_id: str
    titulo: str
    orgao: str
    tipo: str
    norma: str
    artigo: str | None = None
    secao: str | None = None
    pagina: int | None = None
    ordem: int = 0
    texto: str
    hash: str
    citado: bool = False
    estrategia: str = "estrutural"
    link: str
    data_coleta: str | None = None
    data_referencia_normativa: str
    camada_dominio: str
    modalidade_divida: str = "geral"
    elegivel_lei_14181: bool | None = None
    nivel_urgencia: str = "moderado_reorganizacao"
    ressalva: str | None = None
    versao_corpus: str = ""

    def cabecalho(self) -> str:
        partes = [self.norma, self.secao, self.artigo]
        return " | ".join(p for p in partes if p)

    def texto_indexado(self, com_cabecalho: bool = True) -> str:
        return f"{self.cabecalho()}\n{self.texto}" if com_cabecalho else self.texto


def versao_do_corpus(hashes: list[str]) -> str:
    return hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest()[:12]


def montar_registros(
    estrategia: str = "estrutural",
    fontes: list[Fonte] | None = None,
    texto_dir: Path = TEXT_DIR,
    lock_path: Path = LOCK_PATH,
) -> list[Registro]:
    fontes = fontes if fontes is not None else carregar_fontes()
    lock = ler_lock(lock_path)["fontes"]
    registros: list[Registro] = []
    for fonte in fontes:
        for c in dividir(fonte, carregar_texto(fonte.id, texto_dir), estrategia):
            norma = fonte.titulo
            if c.citado:
                alvo = c.alvo or fonte.norma_alvo or "outra norma"
                norma = f"{fonte.titulo}, trecho inserido em {alvo}"
            registros.append(
                Registro(
                    id=c.id, fonte_id=fonte.id, titulo=fonte.titulo, orgao=fonte.orgao, tipo=fonte.tipo, norma=norma,
                    artigo=c.artigo, secao=c.secao, pagina=c.pagina, ordem=c.ordem, texto=c.texto, hash=c.hash,
                    citado=c.citado, estrategia=c.estrategia, link=fonte.link,
                    data_coleta=lock.get(fonte.id, {}).get("coletado_em"),
                    data_referencia_normativa=fonte.data_referencia_normativa, camada_dominio=fonte.camada_dominio,
                    modalidade_divida=fonte.modalidade_divida, elegivel_lei_14181=fonte.elegivel_lei_14181,
                    nivel_urgencia=fonte.nivel_urgencia, ressalva=fonte.ressalva,
                )
            )
    versao = versao_do_corpus([r.hash for r in registros])
    for r in registros:
        r.versao_corpus = versao
    return registros


def hoje() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def salvar_jsonl(registros: list[Registro], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(r.model_dump_json() for r in registros) + "\n", encoding="utf-8")


def ler_jsonl(caminho: Path) -> list[Registro]:
    return [Registro(**json.loads(x)) for x in caminho.read_text(encoding="utf-8").splitlines() if x]
