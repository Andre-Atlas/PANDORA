"""Leitura e validação do manifesto de fontes e do arquivo de candidatas do crawler."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, field_validator

from pandora_rag.config import CANDIDATAS_PATH, FONTES_PATH

# valores fechados do "Esquema Obrigatório de 5 Metadados" do catálogo (docs/evidencias/01-catalogo...)
CamadaDominio = Literal[
    "educacao_orcamento",
    "comportamental_vieses",
    "juridico_superendividamento",
    "regulatorio_bancario",
    "defesa_bens_servicos",
]
ModalidadeDivida = Literal[
    "cartao_credito", "cheque_especial", "emprestimo_pessoal", "credito_consignado", "financiamento_veiculo",
    "financiamento_imobiliario", "contas_consumo_luz_agua", "divida_prescrita", "geral",
]
NivelUrgencia = Literal["critico_imediato", "alto_atraso_90d", "moderado_reorganizacao", "preventivo"]
Tipo = Literal["lei", "decreto", "resolucao", "sumula", "jurisprudencia", "cartilha", "estudo"]
Formato = Literal["html", "pdf", "bcb_api"]

CAMADAS: tuple[str, ...] = CamadaDominio.__args__
MODALIDADES: tuple[str, ...] = ModalidadeDivida.__args__
URGENCIAS: tuple[str, ...] = NivelUrgencia.__args__
TIPOS: tuple[str, ...] = Tipo.__args__
DATA_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_VALIDO = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class Fonte(BaseModel):
    model_config = ConfigDict(extra="forbid")  # chave escrita errada no YAML é erro, não silêncio

    id: str
    titulo: str
    orgao: str
    tipo: Tipo
    formato: Formato
    url: str
    url_citacao: str | None = None
    camada_dominio: CamadaDominio
    modalidade_divida: ModalidadeDivida = "geral"
    elegivel_lei_14181: bool | None = None
    nivel_urgencia: NivelUrgencia = "moderado_reorganizacao"
    data_referencia_normativa: str
    itens: list[str] | None = None  # restringe a ingestão a estes artigos (ou súmulas)
    norma_alvo: str | None = None  # norma alterada, para artigos entre aspas em leis alteradoras
    ressalva: str | None = None  # nota de vigência exibida junto do trecho
    recorte_inicio: str | None = None  # páginas de notícia: começa no bloco com este texto
    recorte_fim: str | None = None  # e termina antes do bloco com este texto
    origem: str | None = None  # como a fonte entrou: None (curadoria), "crawler", "bcb_busca", "lacuna"

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        if not ID_VALIDO.match(v):
            raise ValueError(f"id inválido: {v!r} (use minúsculas, dígitos e hífen)")
        return v

    @field_validator("data_referencia_normativa")
    @classmethod
    def _data(cls, v: str) -> str:
        if not DATA_ISO.match(v):
            raise ValueError(f"data_referencia_normativa deve ser YYYY-MM-DD: {v!r}")
        return v

    @property
    def link(self) -> str:
        return self.url_citacao or self.url


class Candidata(Fonte):
    """Fonte achada pelo crawler, ainda fora do índice. Os campos extras explicam a sugestão."""

    confianca: Literal["alta", "media", "baixa"] = "baixa"
    motivos: list[str] = []
    sha256_texto: str | None = None
    palavras: int = 0
    descoberta_em: str | None = None
    achada_em: str | None = None  # página onde o link apareceu
    barrada_em: str | None = None  # última vez que a trava do golden a recusou (AAAA-MM-DD)

    def testavel(self, hoje: str, dias: int = 30) -> bool:
        """Confiança alta e não recusada pela trava nos últimos `dias`: entra no próximo teste."""
        if self.confianca != "alta":
            return False
        if not self.barrada_em:
            return True
        from datetime import date

        return (date.fromisoformat(hoje) - date.fromisoformat(self.barrada_em)).days >= dias

    def como_fonte(self) -> Fonte:
        dados = self.model_dump(exclude={"confianca", "motivos", "sha256_texto", "palavras", "descoberta_em", "achada_em",
                                         "barrada_em"})
        return Fonte(**{k: v for k, v in dados.items() if v is not None or k in ("elegivel_lei_14181",)})


def _ler(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    return dados.get("fontes") or []


def _sem_repetidos(itens: list[BaseModel], nome: str) -> None:
    ids = [f.id for f in itens]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    if repetidos:
        raise ValueError(f"{nome} tem ids repetidos: {repetidos}")


def carregar_fontes(caminho: Path = FONTES_PATH) -> list[Fonte]:
    fontes = [Fonte(**item) for item in _ler(caminho)]
    _sem_repetidos(fontes, caminho.name)
    return fontes


def carregar_candidatas(caminho: Path = CANDIDATAS_PATH) -> list[Candidata]:
    cands = [Candidata(**item) for item in _ler(caminho)]
    _sem_repetidos(cands, caminho.name)
    return cands


def _linha_yaml(dados: dict) -> str:
    """Uma fonte por linha, em mapa inline, como o fontes.yaml já é escrito à mão."""
    texto = yaml.safe_dump(dados, allow_unicode=True, default_flow_style=True, sort_keys=False, width=10_000).strip()
    return f"  - {texto}"


CABECALHO_CANDIDATAS = (
    "# Gerado por `pandora-rag descobrir` e `pandora-rag lacunas`. Não entra no índice até `pandora-rag reindexar`\n"
    "# promover a fonte (confiança alta, metadados válidos e trava de avaliação aprovada).\n"
)


def salvar_candidatas(cands: list[Candidata], caminho: Path = CANDIDATAS_PATH) -> None:
    linhas = [_linha_yaml(c.model_dump(exclude_none=True)) for c in sorted(cands, key=lambda c: c.id)]
    caminho.write_text(CABECALHO_CANDIDATAS + "fontes:\n" + ("\n".join(linhas) + "\n" if linhas else ""), encoding="utf-8")


def acrescentar_fontes(novas: list[Fonte], caminho: Path = FONTES_PATH) -> None:
    """Acrescenta fontes promovidas ao fim do fontes.yaml sem reescrever as linhas curadas à mão."""
    existentes = {f.id for f in carregar_fontes(caminho)}
    repetidas = [f.id for f in novas if f.id in existentes]
    if repetidas:
        raise ValueError(f"já estão em {caminho.name}: {repetidas}")
    if not novas:
        return
    texto = caminho.read_text(encoding="utf-8").rstrip("\n")
    if "# --- Promovidas pelo crawler ---" not in texto:
        texto += "\n  # --- Promovidas pelo crawler ---"
    texto += "\n" + "\n".join(_linha_yaml(f.model_dump(exclude_none=True)) for f in novas) + "\n"
    caminho.write_text(texto, encoding="utf-8")
    carregar_fontes(caminho)  # garante que o arquivo continua válido
