import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]


def _slug_github(titulo: str) -> str:
    texto = titulo.strip().lower()
    texto = re.sub(r"[`*_~]", "", texto)
    texto = "".join(
        ch
        for ch in texto
        if unicodedata.category(ch)[0] in ("L", "N") or ch in (" ", "-")
    )
    return texto.replace(" ", "-")


def _ancoras_markdown(texto: str) -> set[str]:
    ancoras: set[str] = set()
    for linha in texto.splitlines():
        m = re.match(r"^#{1,6}\s+(.+)$", linha)
        if m:
            ancoras.add(_slug_github(m.group(1)))
    return ancoras


def _validar_links_locais(arquivo: Path) -> list[str]:
    texto = arquivo.read_text(encoding="utf-8")
    ancoras_locais = _ancoras_markdown(texto)
    padrao_md = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    padrao_img = re.compile(r'<img\s+[^>]*src="([^"]+)"')
    destinos = padrao_md.findall(texto) + padrao_img.findall(texto)
    quebrados = []
    for destino in destinos:
        if destino.startswith(("http://", "https://", "mailto:")):
            continue
        if destino.startswith("#"):
            slug = destino[1:]
            if slug not in ancoras_locais:
                quebrados.append(f"{arquivo.relative_to(RAIZ)} -> âncora inexistente {destino}")
            continue
        caminho_limpo, _, fragmento = destino.partition("#")
        if caminho_limpo.startswith("/"):
            quebrados.append(f"{arquivo.relative_to(RAIZ)} -> caminho absoluto proibido {destino}")
            continue
        alvo = (arquivo.parent / caminho_limpo).resolve()
        if not alvo.is_relative_to(RAIZ) or not alvo.exists():
            quebrados.append(f"{arquivo.relative_to(RAIZ)} -> {destino}")
            continue
        if fragmento and alvo.suffix == ".md":
            ancoras_alvo = _ancoras_markdown(alvo.read_text(encoding="utf-8"))
            if fragmento not in ancoras_alvo:
                quebrados.append(f"{arquivo.relative_to(RAIZ)} -> âncora remota inexistente {destino}")
    return quebrados


def _validar_blocos_mermaid(conteudo: str) -> list[str]:
    erros: list[str] = []
    aberturas = len(re.findall(r"^```mermaid\s*$", conteudo, flags=re.MULTILINE))
    blocos = re.findall(r"^```mermaid\n(.*?)^```$", conteudo, flags=re.DOTALL | re.MULTILINE)
    if aberturas != len(blocos):
        erros.append(f"Desbalanceamento de cercas Mermaid: {aberturas} aberturas vs {len(blocos)} fechados")
    if len(blocos) < 4:
        erros.append(f"Esperados ao menos 4 diagramas Mermaid, encontrados {len(blocos)}")
    for idx, bloco in enumerate(blocos, start=1):
        linhas = [ln.strip() for ln in bloco.strip().splitlines() if ln.strip()]
        if len(linhas) < 3:
            erros.append(f"Bloco Mermaid #{idx} vazio ou curto demais")
            continue
        if not linhas[0].startswith(("flowchart ", "sequenceDiagram", "graph ")):
            erros.append(f"Bloco Mermaid #{idx} com cabeçalho inválido: {linhas[0]}")
        n_subgraph = sum(1 for ln in linhas if ln.startswith("subgraph "))
        n_end = sum(1 for ln in linhas if ln == "end")
        if n_subgraph != n_end:
            erros.append(f"Bloco Mermaid #{idx} com subgraph/end desbalanceados ({n_subgraph} vs {n_end})")
        tags_html = re.findall(r"<(?!br\s*/?>)[a-zA-Z_][^>]*>", bloco)
        if tags_html:
            erros.append(f"Bloco Mermaid #{idx} contém tags HTML não escapadas que quebram o GitHub: {tags_html}")
    return erros


def test_adr_arquitetura_geral_existe_e_tem_secoes_obrigatorias():
    indice = RAIZ / "docs" / "adr" / "README.md"
    adr = RAIZ / "docs" / "adr" / "0003-arquitetura-geral-sistema-pandora.md"
    assert indice.exists(), "Índice docs/adr/README.md deve existir"
    assert adr.exists(), "ADR-0003 deve existir"
    texto_indice = indice.read_text(encoding="utf-8")
    for codigo in ("ADR-0001", "ADR-0002", "ADR-0003", "Proposto (Gate 1)"):
        assert codigo in texto_indice, f"Referência obrigatória ausente no índice de ADRs: {codigo}"
    conteudo = adr.read_text(encoding="utf-8")
    for secao in (
        "## 1. Contexto",
        "## 2. Alternativas Consideradas",
        "## 3. Decisão",
        "## 4. Consequências",
    ):
        assert secao in conteudo, f"Seção obrigatória ausente no ADR-0003: {secao}"
    quebrados_indice = _validar_links_locais(indice)
    assert not quebrados_indice, f"Links quebrados em docs/adr/README.md: {quebrados_indice}"
    quebrados_adr = _validar_links_locais(adr)
    assert not quebrados_adr, f"Links quebrados no ADR-0003: {quebrados_adr}"


def test_documento_arquitetura_geral_completo_e_integro():
    doc = RAIZ / "docs" / "arquitetura-geral.md"
    assert doc.exists(), "Documento canônico docs/arquitetura-geral.md deve existir"
    conteudo = doc.read_text(encoding="utf-8")

    secoes_obrigatorias = [
        "## 1. Visão Geral e Princípios Arquiteturais",
        "## 2. Topologia Geral de Execução e Diagrama de Contexto (Visão Macro)",
        "## 3. Camada 1 · Apresentação e Experiência (Frontend PWA & Design System)",
        "## 4. Camada 2 · Aplicação e Domínio (Backend API em Arquitetura Hexagonal)",
        "## 5. Camada 3 · Conhecimento e Recuperação Normativa (RAG Híbrido `rag-v0.1.0`)",
        "## 6. Camada 4 · Orquestração Cognitiva Multiagente (`LangGraph` + Tool Calling)",
        "## 7. Camada 5 · Aprendizado de Máquina Clássico e Motores Determinísticos (`services/ml`)",
        "## 8. Camada 6 · Infraestrutura, Topologia de Portas e Fontes Externas (Docker vs. Host)",
        "## 9. Matriz de Rastreabilidade dos Requisitos Não Funcionais (RNF01 a RNF09)",
        "## 10. Mapa Completo do Monorepo e Estado de Integração por Branch",
    ]
    for secao in secoes_obrigatorias:
        assert secao in conteudo, f"Seção obrigatória ausente em docs/arquitetura-geral.md: {secao}"

    termos_obrigatorios = [
        "Determinístico onde",
        "apps/web",
        "frontend/design-system",
        "apps/api",
        "services/rag",
        "pandora_rag.agents",
        "LangGraph",
        "services/ml",
        "LightGBM",
        "BAAI/bge-m3",
        "bge-reranker-v2-m3",
        "0,02",
        "0,76",
        "0,80",
        "0,67",
        "0,72",
        "70%",
        "96,0%",
        "14,4 s",
        "POST /responder",
        "host.docker.internal:8010",
        "AssistenteElpis",
        "AssistenteHttp",
        "RepositorioTrilha",
        "TrilhaEmArquivo",
        "tool_calcular_raio_x_financeiro",
        "tool_simular_reestruturacao_dividas",
        "tool_analisar_compulsao_apostas",
        "tool_inspecionar_fraude_e_boleto",
        "tool_buscar_evidencias_rag",
        "tool_auditar_invariantes_compliance",
        "RNF01",
        "RNF02",
        "RNF03",
        "RNF04",
        "RNF05",
        "RNF06",
        "RNF07",
        "RNF08",
        "RNF09",
        ":3000",
        ":8000",
        ":8010",
        ":5434",
        ":5433",
        ":11434",
    ]
    for termo in termos_obrigatorios:
        assert termo in conteudo, f"Termo arquitetural obrigatório ausente: {termo}"

    erros_mermaid = _validar_blocos_mermaid(conteudo)
    assert not erros_mermaid, f"Erros em blocos Mermaid: {erros_mermaid}"

    quebrados = _validar_links_locais(doc)
    assert not quebrados, f"Links locais quebrados em docs/arquitetura-geral.md: {quebrados}"


def test_readme_raiz_referencia_arquitetura_geral_e_rag():
    readme = RAIZ / "README.md"
    conteudo = readme.read_text(encoding="utf-8")
    assert "docs/arquitetura-geral.md" in conteudo
    assert "docs/rag/README.md" in conteudo
    assert "docs/adr/README.md" in conteudo
    quebrados = _validar_links_locais(readme)
    assert not quebrados, f"Links locais quebrados no README.md: {quebrados}"
