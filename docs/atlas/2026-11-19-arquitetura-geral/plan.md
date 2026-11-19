# Documentação da Arquitetura Geral do PANDORA — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a documentação canônica da arquitetura geral do projeto PANDORA (`docs/arquitetura-geral.md`), o registro de decisão arquitetural correspondente (`docs/adr/0003-arquitetura-geral-sistema-pandora.md` e `docs/adr/README.md`), atualizar o índice do `README.md` e validar a integridade estrutural e de links com teste automatizado (`pytest`).

**Architecture:** Consolida os 6 subsistemas distribuídos no repositório e em suas branches ativas (Frontend PWA + Design System, Backend API Hexagonal, Motor RAG Híbrido `rag-v0.1.0`, Sistema Multiagente `LangGraph`, Modelos Auxiliares de ML Clássico e Infraestrutura Docker/Host) em uma referência arquitetural única com diagramas Mermaid, matriz de rastreabilidade RNF01–RNF09 e mapa de estado por branch.

**Tech Stack:** Markdown (GitHub Flavored Markdown), Mermaid (`flowchart`, `sequenceDiagram`), ADR (`docs/adr/`), Python 3.12 + `pytest` (`services/rag/tests/`).

**Spec:** `docs/atlas/2026-11-19-arquitetura-geral/spec.md`

## Global Constraints

- Todo conteúdo deve estar em português do Brasil, mantendo a terminologia oficial do projeto (`Mínimo Existencial`, `Registro do Mito`, `Registro de Leitura`, `Recusa Educativa CVM`, `Protocolo de Crise CVV 188`, `Portão de Abstenção`).
- Diagramas Mermaid devem usar exclusivamente tipos suportados (`flowchart TD`, `flowchart LR`, `sequenceDiagram`) e colocar rótulos com parênteses, colchetes ou dois-pontos entre aspas duplas (`id["Rótulo (Detalhe)"]`).
- Links Markdown relativos dentro de `docs/arquitetura-geral.md` e `README.md` que apontam para arquivos presentes na branch atual devem resolver para caminhos existentes no disco; referências a arquivos que existem apenas em outras branches (`origin/develop`, `entrega/prototipo-multiagente-quarto-desafio`, `origin/dev/mariana`) devem usar formatação inline code (`` `apps/api/...` ``) com indicação explícita da branch, evitando links quebrados (404).
- A suíte de testes existente em `services/rag/tests/` deve continuar 100% verde.

## Review Focus

1. **Links Markdown quebrados para arquivos de outras branches:** caminhos como `apps/api/README.md` ou `services/ml/classificador/` existem em `origin/develop` / `origin/dev/mariana`, mas não na árvore de trabalho atual (`analise_arquitetura_geral`); o teste em `test_arquitetura_docs.py` deve falhar se qualquer link Markdown `[texto](caminho_local)` apontar para um arquivo inexistente na worktree.
2. **Erros de sintaxe em diagramas Mermaid:** nós com parênteses ou barras sem aspas duplas quebram o renderizador do GitHub; o teste deve inspecionar blocos ```mermaid para garantir fechamento correto e ausência de blocos vazios.
3. **Omissão de subsistemas ou RNFs:** todos os 6 subsistemas e todos os 9 Requisitos Não Funcionais (`RNF01` a `RNF09`) devem estar explicitamente mapeados.
4. **Desalinhamento de portas e parâmetros técnicos:** portas (`3000`, `8000`, `8010`, `5434`, `5433`, `11434`) e hiperparâmetros (`BAAI/bge-m3`, `BM25 k1=1.5, b=0.75`, `RRF k=60`, `bge-reranker-v2-m3`, limiar de abstenção `0.02`, `qwen2.5:14b` / `qwen2.5:7b`) devem refletir fielmente o código real.
5. **Desatualização do `README.md` da raiz:** a seção `## Documentação` do `README.md` atual não lista nem a Arquitetura Geral nem a pasta `docs/rag/README.md`.

---

### Task 1: `[arch]` Registrar ADR-0003 da Topologia Geral Unificada e Teste de Contrato Documental

**Files:**
- Create: `services/rag/tests/test_arquitetura_docs.py`
- Create: `docs/adr/README.md`
- Create: `docs/adr/0003-arquitetura-geral-sistema-pandora.md`

**Interfaces:**
- Consumes: `docs/atlas/2026-11-19-arquitetura-geral/spec.md`
- Produces:
  - `docs/adr/README.md`
  - `docs/adr/0003-arquitetura-geral-sistema-pandora.md`
  - `services/rag/tests/test_arquitetura_docs.py` (valida ADR, `docs/arquitetura-geral.md` e `README.md`)

- [ ] **Step 1: Escrever o teste automatizado de contrato documental (`services/rag/tests/test_arquitetura_docs.py`)**

```python
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[3]


def _validar_links_locais(arquivo: Path) -> list[str]:
    texto = arquivo.read_text(encoding="utf-8")
    padrao = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    quebrados = []
    for destino in padrao.findall(texto):
        if destino.startswith(("http://", "https://", "mailto:", "#")):
            continue
        caminho_limpo = destino.split("#", 1)[0]
        if not caminho_limpo:
            continue
        alvo = (arquivo.parent / caminho_limpo).resolve()
        if not alvo.exists():
            quebrados.append(f"{arquivo.relative_to(RAIZ)} -> {destino}")
    return quebrados


def test_adr_arquitetura_geral_existe_e_tem_secoes_obrigatorias():
    indice = RAIZ / "docs" / "adr" / "README.md"
    adr = RAIZ / "docs" / "adr" / "0003-arquitetura-geral-sistema-pandora.md"
    assert indice.exists(), "Índice docs/adr/README.md deve existir"
    assert adr.exists(), "ADR-0003 deve existir"
    conteudo = adr.read_text(encoding="utf-8")
    for secao in ("## 1. Contexto", "## 2. Alternativas Consideradas", "## 3. Decisão", "## 4. Consequências"):
        assert secao in conteudo, f"Seção obrigatória ausente no ADR-0003: {secao}"
    assert not _validar_links_locais(indice)
    assert not _validar_links_locais(adr)


def test_documento_arquitetura_geral_completo_e_integro():
    doc = RAIZ / "docs" / "arquitetura-geral.md"
    assert doc.exists(), "Documento canônico docs/arquitetura-geral.md deve existir"
    conteudo = doc.read_text(encoding="utf-8")

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

    blocos_mermaid = re.findall(r"```mermaid\n(.*?)```", conteudo, flags=re.DOTALL)
    assert len(blocos_mermaid) >= 4, "Deve conter ao menos 4 diagramas Mermaid (topologia, hexagonal, RAG, multiagente/ML)"
    for bloco in blocos_mermaid:
        assert bloco.strip().startswith(("flowchart ", "sequenceDiagram", "graph ")), "Bloco Mermaid com tipo inválido"

    quebrados = _validar_links_locais(doc)
    assert not quebrados, f"Links locais quebrados em docs/arquitetura-geral.md: {quebrados}"


def test_readme_raiz_referencia_arquitetura_geral_e_rag():
    readme = RAIZ / "README.md"
    conteudo = readme.read_text(encoding="utf-8")
    assert "docs/arquitetura-geral.md" in conteudo
    assert "docs/rag/README.md" in conteudo
    quebrados = _validar_links_locais(readme)
    assert not quebrados, f"Links locais quebrados no README.md: {quebrados}"
```

- [ ] **Step 2: Rodar o teste para confirmar que falha inicialmente**

Run: `cd services/rag && uv run pytest tests/test_arquitetura_docs.py -v`
Expected: FAIL (`AssertionError: Índice docs/adr/README.md deve existir` / `Documento canônico docs/arquitetura-geral.md deve existir`)

- [ ] **Step 3: Escrever `docs/adr/0003-arquitetura-geral-sistema-pandora.md` e `docs/adr/README.md`**

Registrar no `ADR-0003` a decisão arquitetural da topologia unificada do sistema PANDORA em 6 camadas desacopladas por contratos verificáveis (PWA Next.js + Design System `@pandora/design-system` → API Hexagonal FastAPI `openapi.json` → Serviço Cognitivo `pandora_rag` + `LangGraph` 7 agentes + Motores Determinísticos/ML `LightGBM`/`RapidFuzz` + Bancos `pgvector` isolados `:5434` e `:5433`), referenciando também o contexto dos ADRs `0001` e `0002` da branch `entrega/prototipo-multiagente-quarto-desafio`.

---

### Task 2: `[arch]` Escrever o Documento Canônico `docs/arquitetura-geral.md` e Atualizar o `README.md`

**Files:**
- Create: `docs/arquitetura-geral.md`
- Modify: `README.md:65-75`
- Test: `services/rag/tests/test_arquitetura_docs.py`

**Interfaces:**
- Consumes: `docs/adr/0003-arquitetura-geral-sistema-pandora.md`, `docs/rag/01-arquitetura.md`, `docs/escopo/04-requisitos-4-graus.md`, `frontend/design-system/README.md`
- Produces: `docs/arquitetura-geral.md` (10 seções completas com diagramas Mermaid) e `README.md` atualizado

- [ ] **Step 1: Criar `docs/arquitetura-geral.md` cobrindo as 10 seções da especificação**

Incluir obrigatoriamente:
1. Visão Geral e Princípios Arquiteturais (*Determinístico onde dá, probabilístico onde precisa*, *Read-Only*, *Privacy by Design*, *Acolhimento em Crise*);
2. Diagrama Macro de Contexto e Topologia de Execução (`flowchart TB` com portas `:3000`, `:8000`, `:8010`, `:5434`, `:5433`, `:11434` e integrações externas);
3. Camada de Apresentação e Experiência (`frontend/design-system` — Dois Registros Mito/Leitura, tokens, acessibilidade — e `apps/web` — Next.js 16 PWA, rotas `(app)` e `(fluxo)`, `CriseProvider`, contrato tipado `esquema.d.ts`);
4. Camada de Aplicação e Domínio (`apps/api` — FastAPI em Arquitetura Hexagonal `dominio/`, `portas/`, `aplicacao/`, `adaptadores/`, diagrama Mermaid de Ports & Adapters, convenções `valor_centavos`, RFC 9457, selo Calculado, `DELETE /eu/dados` e tabela de endpoints);
5. Camada de Conhecimento e Recuperação Normativa (`services/rag` `rag-v0.1.0` — ingestão de 33 fontes com `corpus.lock` SHA-256, chunking estrutural, índice híbrido `BAAI/bge-m3` + `BM25` + `RRF k=60` + `bge-reranker-v2-m3` + portão de abstenção `0,02` + `Gateway` `qwen2.5:14b` com `pii.mascarar`, além de `evals/` e `training/`);
6. Camada Cognitiva Multiagente (`pandora_rag.agents` — grafo `LangGraph` `StateGraph(EstadoMultiagente)` com os 7 agentes especializados, Tool Calling `@tool` nativo com `qwen2.5:7b`, ciclo de revisão *fail-closed* do `ComplianceAgent` e 3 níveis de resolução de corpus);
7. Camada de Machine Learning Clássico e Motores Determinísticos (`services/ml` — dataset sintético `SEED=42`, classificador `LightGBM` calibrado com TF-IDF char n-grams e proteção do Mínimo Existencial, detector híbrido de *bets* MCC `7995` + SPA/MF + `RapidFuzz`, motor matemático Avalanche/Bola de Neve/FEBRABAN);
8. Matriz de Rastreabilidade dos Requisitos Não Funcionais (`RNF01` a `RNF09` mapeados para metas, código e testes);
9. Infraestrutura, Topologia de Portas e Divisão Docker vs. Host (tabela de serviços, portas, volumes e justificativa de aceleração MPS/GPU no host);
10. Mapa Completo do Monorepo e Estado de Integração por Branch (`main`, `origin/develop`, `entrega/prototipo-multiagente-quarto-desafio`, `origin/dev/mariana`, `origin/dev/rayssa`).

- [ ] **Step 2: Atualizar a tabela `## Documentação` em `README.md`**

Adicionar na tabela `## Documentação` do `README.md` os links para:
- `[Arquitetura Geral do Sistema](docs/arquitetura-geral.md)`
- `[Arquitetura e Pipeline do RAG](docs/rag/README.md)`
- `[Decisões Arquiteturais (ADRs)](docs/adr/README.md)`

- [ ] **Step 3: Executar a suíte de testes (`pytest`) para verificar que todos os testes passam**

Run: `cd services/rag && uv run pytest -v`
Expected: PASS em `tests/test_arquitetura_docs.py` e em todos os testes existentes (`test_busca.py`, `test_chunk.py`, `test_corpus.py`, `test_geracao.py`).
