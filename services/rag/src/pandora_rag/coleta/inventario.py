"""Tabela do inventário: os 31 itens, com formato, frequência e situação lida de catalogo.lock.json."""
from __future__ import annotations

from pandora_rag.coleta.catalogo import ItemCatalogo
from pandora_rag.coleta.executor import MANUAL, situacao_do_item

GRUPOS = {
    1: "Educação, comportamento e psicometria",
    2: "Superendividamento e defesa patrimonial",
    3: "Regulação bancária e jurisprudência",
    4: "APIs dinâmicas e bases abertas",
    5: "Datasets de QA, transações e avaliação",
}


def resumo(itens: list[ItemCatalogo], lock: dict) -> dict[str, int]:
    contagem: dict[str, int] = {}
    for item in itens:
        situacao = situacao_do_item(item, lock)
        contagem[situacao] = contagem.get(situacao, 0) + 1
    return contagem


def markdown(itens: list[ItemCatalogo], lock: dict) -> str:
    linhas = [
        "# Inventário das 31 fontes do catálogo",
        "",
        "Gerado por `uv run pandora-rag inventario --md ../../docs/rag/10-inventario-fontes.md`, a partir da seção "
        "`catalogo` de `services/rag/fontes.yaml` e da situação em `services/rag/catalogo.lock.json`. Não edite à mão.",
        "",
        "Situação do item: **coletada** (todos os alvos baixados), **mista** (parte baixada, parte manual), "
        "**manual** (nenhum alvo automático), **falha** (algum alvo falhou na última execução) ou **pendente** "
        "(ainda não coletado).",
        "",
    ]
    for grupo, titulo in GRUPOS.items():
        linhas += [f"## Grupo {grupo}: {titulo}", "", "| # | Fonte | Órgão | Formato | Frequência | Situação | Alvos |", "|---|---|---|---|---|---|---|"]
        for item in (i for i in itens if i.grupo == grupo):
            automaticos = [a for a in item.alvos if not a.manual]
            manuais = [a for a in item.alvos if a.manual]
            partes = [f"{len(automaticos)} automático(s)"] if automaticos else []
            if manuais:
                partes.append(f"{len(manuais)} manual(is)")
            linhas.append(
                f"| {item.numero} | {item.nome} | {item.orgao} | {', '.join(item.formatos)} | {item.frequencia} "
                f"| {situacao_do_item(item, lock)} | {', '.join(partes)} |"
            )
        linhas.append("")
    linhas += ["## Alvos de tratamento manual", "", "| Item | Alvo | Motivo |", "|---|---|---|"]
    for item in itens:
        for alvo in item.alvos:
            if alvo.manual:
                linhas.append(f"| {item.numero} | `{alvo.id}` | {alvo.manual} |")
    falhas = [(a.id, lock["alvos"][a.id]) for i in itens for a in i.alvos
              if lock["alvos"].get(a.id, {}).get("situacao") not in (None, MANUAL, "coletada")]
    if falhas:
        linhas += ["", "## Alvos com falha na última execução", "", "| Alvo | Situação | Erro |", "|---|---|---|"]
        linhas += [f"| `{i}` | {r['situacao']} | {r.get('erro', '')} |" for i, r in falhas]
    return "\n".join(linhas) + "\n"
