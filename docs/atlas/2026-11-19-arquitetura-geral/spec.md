# Especificação: Documentação da Arquitetura Geral do Projeto PANDORA

> **ATLAS · feature · arquitetura+documentação · standard → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura**

## 1. Contexto e Problema

A inspeção completa do repositório `PANDORA` (incluindo o grafo completo de *branches* e *worktrees* ativas da equipe) revelou que **não existe um documento único de Arquitetura Geral do Sistema**. Atualmente, o conhecimento arquitetural encontra-se fragmentado em múltiplas pastas e *branches* de trabalho:

| Subsistema | Onde está documentado / implementado hoje | Branch / Estado |
|---|---|---|
| **Visão Científica, Requisitos (RF01–RF18, RNF01–RNF09) e Personas (P01–P10)** | `docs/escopo/` (`04-requisitos-4-graus.md`, `documento-completo-cbl.md`) e `docs/personas/` | `main`, `develop`, `analise_arquitetura_geral` |
| **Design System ("Dois Registros: Mito e Leitura")** | `frontend/design-system/README.md`, `tokens.json`, `tokens.css`, `components/bundle.js` | `main`, `develop`, `analise_arquitetura_geral` |
| **Frontend PWA (Next.js 16 + TypeScript + WCAG 2.2 AA)** | `apps/web/README.md`, `apps/web/app/`, `apps/web/components/`, `apps/web/lib/` | `origin/main`, `origin/develop` |
| **Backend API em Arquitetura Hexagonal (FastAPI + Ports & Adapters)** | `apps/api/README.md`, `apps/api/openapi.json`, `apps/api/src/pandora_api/` (`dominio`, `portas`, `aplicacao`, `adaptadores`) | `origin/main`, `origin/develop` |
| **Motor de RAG Híbrido (`rag-v0.1.0`) e Avaliação (`evals/`)** | `docs/rag/01-arquitetura.md` a `09-decisao-llm.md`, `services/rag/src/pandora_rag/`, `evals/`, `training/` | `origin/main`, `origin/develop`, `analise_arquitetura_geral` |
| **Sistema Multiagente (`LangGraph` + 7 Agentes + Tool Calling)** | `docs/adr/0001-*.md`, `docs/adr/0002-*.md`, `docs/agentes/01-arquitetura.md` a `04-demonstracao.md`, `services/rag/src/pandora_rag/agents/` | `entrega/prototipo-multiagente-quarto-desafio` |
| **Modelos Auxiliares de Machine Learning & Dados Sintéticos** | `docs/ml/modelos-auxiliares.md`, `services/ml/classificador/` (LightGBM), `services/ml/apostas/` (Detector SPA/MF + RapidFuzz), `services/ml/sintetico/` | `origin/develop`, `origin/dev/mariana`, `origin/dev/rayssa` |

## 2. Objetivo

Criar a documentação canônica de arquitetura geral do sistema em **`docs/arquitetura-geral.md`**, registrar a decisão arquitetural da topologia unificada em **`docs/adr/0003-arquitetura-geral-sistema-pandora.md`** (com índice em `docs/adr/README.md`) e referenciá-la na tabela principal do **`README.md`**, oferecendo uma visão ponta a ponta (C4 / camadas / contratos / fluxos de dados / garantias RNF01–RNF09 / matriz de estado por branch).

## 3. Alternativas Arquiteturais Consideradas (Fase 2 — Lane Arquitetura)

### Alternativa A — Apenas um índice de links (`docs/arquitetura-geral.md` curto)
- **Prós:** Rápido de escrever.
- **Contras:** Não resolve a fragmentação entre *branches* (`origin/develop`, `entrega/prototipo-multiagente-quarto-desafio`, `origin/dev/mariana`), nem explica como o Frontend PWA (`:3000`), a API Hexagonal (`:8000`), o Serviço RAG/Multiagente (`:8010`), os bancos PostgreSQL (`:5434` e `:5433`), o Ollama (`:11434`) e os modelos de ML se conectam por contratos explícitos.
- **Veredito:** Rejeitada.

### Alternativa B — Documento Canônico Unificado (`docs/arquitetura-geral.md`) + ADR de Topologia do Sistema (`docs/adr/0003-*.md`) + Teste de Integridade Documental (Escolhida)
- **Prós:**
  - Consolida a arquitetura macroscópica e microscópica dos **6 subsistemas** do PANDORA em um único ponto de entrada com diagramas Mermaid verificáveis;
  - Documenta explicitamente os contratos entre camadas (`openapi.json` → `esquema.d.ts`, `PortaAssistente` → `services/rag :8010`, `Portas de Ingestão/Classificação` → `services/ml`, `StateGraph(EstadoMultiagente)` → `@tool`s determinísticas);
  - Mapeia os invariantes arquiteturais (`RNF01` a `RNF09`) para seus mecanismos concretos no código;
  - Traz um mapa transparente do estado de integração no repositório (o que já está em `main`/`develop` vs. o que está nas branches de entrega `entrega/prototipo-multiagente-quarto-desafio` e `origin/dev/mariana`).
- **Contras:** Exige verificação automatizada para garantir que links locais, seções obrigatórias e blocos Mermaid estejam íntegros.

## 4. Estrutura Especificada para `docs/arquitetura-geral.md`

O documento `docs/arquitetura-geral.md` deve conter obrigatoriamente as seguintes 10 seções:

1. **Visão Geral e Princípios Arquiteturais:**
   - O princípio norteador *"Determinístico onde é possível, probabilístico onde é necessário"*;
   - Operação 100% *read-only* (sem custódia ou movimentação financeira);
   - *Privacy by Design* (LGPD) e acolhimento prioritário em crise (`CVV 188`).
2. **Diagrama de Contexto e Topologia Geral de Execução (Visão Macro):**
   - Diagrama Mermaid integrando Usuário/Persona, PWA Next.js (`apps/web`, porta `3000`), Design System (`@pandora/design-system`), API Hexagonal FastAPI (`apps/api`, porta `8000`), Banco Transacional (`postgres/pgvector`, porta `5434`), Serviço RAG & Multiagente (`services/rag`, porta `8010`), Banco Vetorial RAG (`pgvector`, porta `5433`), Modelos de ML (`services/ml`), Daemon de Inferência Local (`Ollama`, porta `11434`) e Fontes Externas Oficiais (SGS/BCB, SPA/MF, Planalto/CVM).
3. **Camada de Apresentação e Experiência (Frontend PWA & Design System):**
   - `frontend/design-system` (`@pandora/design-system`): princípio dos Dois Registros (*Registro do Mito* em figura negra/vermelha e *Registro de Leitura* com `Atkinson Hyperlegible Next`), tokens (`tokens.json`, `tokens.css`), componentes agnósticos (`bundle.js`) e gamificação sem mecânica de cassino;
   - `apps/web` (Next.js 16 + React 19 + TypeScript): grupos de rotas `(app)` e `(fluxo)`, `PortaoAbertura`, contexto global de crise (`CriseProvider` sobrepondo qualquer rota — RF05), geração automática de tipos a partir do contrato OpenAPI (`lib/api/esquema.d.ts`) e conformidade WCAG 2.2 AA (RNF07).
4. **Camada de Aplicação e Domínio (Backend API — Arquitetura Hexagonal):**
   - `apps/api` (`pandora_api`): separação estrita em 4 anéis (`dominio/`, `portas/`, `aplicacao/`, `adaptadores/`), garantida por teste arquitetural (`test_arquitetura.py` impedindo importação de FastAPI/Pydantic/psycopg no núcleo);
   - Convenções de contrato: centavos inteiros (`valor_centavos` — proibição de `float` para dinheiro, RNF03), erros RFC 9457 (`application/problem+json`), selo `"Calculado"`, autenticação via token opaco (`scrypt` + hash SHA-256) e exclusão total sob demanda (`DELETE /eu/dados` — RNF01);
   - Estado atual das rotas HTTP (`/saude`, `/auth/*`, `/consentimentos`, `/eu/dados`, `/extratos`, `/transacoes`, `/raio-x`, `/chat`, `/trilha*` e contratos 501 para `/dividas`, `/score`, `/plano`, `/previsao`).
5. **Camada de Conhecimento e Recuperação Normativa (`services/rag` — `rag-v0.1.0`):**
   - Pipeline de ingestão auditável (`fontes.yaml` → 33 fontes oficiais bloqueadas em `corpus.lock` com SHA-256 → extração HTML/PDF → chunking estrutural por artigo/seção com cabeçalho contextual `[Fonte | Norma | Seção]`);
   - Indexação e busca híbrida: `BAAI/bge-m3` (1024d, HNSW cosseno no `pgvector`) + `BM25` (`k1=1.5, b=0.75`) → fusão `RRF (k=60)` → reranker `BAAI/bge-reranker-v2-m3` (top-30) → **Portão de Abstenção** (`nota < 0.02` aborta chamada ao LLM) → geração top-3 com `qwen2.5:14b` via `Gateway` (com `pii.mascarar` e teto de orçamento US$ 30);
   - Suíte experimental `evals/` (ablação estágios 0 a 5, Golden Set e Dev Set) e `training/` (fine-tuning LoRA/MNRL e calibração de abstenção).
6. **Camada Cognitiva Multiagente (`pandora_rag.agents` — `LangGraph` + Tool Calling):**
   - Topologia do `StateGraph(EstadoMultiagente)` com **7 agentes especializados**:
     1. `OrquestradorAgent` (máscara PII, roteamento de intenções e síntese adaptada ao tom da persona);
     2. `AnalistaAgent` (Raio-X determinístico, Mínimo Existencial e comparativo com séries SGS/BCB);
     3. `EstrategistaAgent` (simulação determinística Avalanche vs. Bola de Neve blindando 100% do Mínimo Existencial — Lei 14.181/2021 e teto do rotativo Lei 14.690/2023);
     4. `CoachAgent` (detecção de *bets*, perda líquida real, concentração 23h–03h e *cooling-off* de 24h–48h — Lei 14.790/2023);
     5. `GuardiaoAgent` (sanitização de OCR contra *prompt injection* indireto `<documento_externo_nao_confiavel>`, validação Módulo 10 FEBRABAN e roteiro MED Pix 80 dias — Res. BCB 147/2021);
     6. `EducadorAgent` (pesquisa normativa orientada por `queries_normativas` no RAG híbrido);
     7. `ComplianceAgent` (portão final *fail-closed* com ciclo de revisão de até 1 turno para Protocolo de Crise `CVV 188`, Recusa Educativa CVM Res. 19/20, auditoria de citações `[n]` e zero PII);
   - Resiliência em 3 níveis de corpus (`pgvector` → `corpus_local_bge_m3` → `corpus_embutido_oficial`) e execução via `@tool` + `bind_tools` (`qwen2.5:7b` no Ollama / Anthropic / fallback determinístico offline).
7. **Camada de Aprendizado de Máquina Clássico e Motores Determinísticos (`services/ml`):**
   - Gerador de dados sintéticos (`services/ml/sintetico/`, `SEED=42`, 10 personas, 12 meses);
   - Classificador supervisionado de transações (`services/ml/classificador/`, TF-IDF de n-gramas de caracteres + One-Hot MCC + `LightGBM` calibrado com `CalibratedClassifierCV`, separando `CATEGORIAS_MINIMO_EXISTENCIAL`);
   - Detector híbrido de apostas (`services/ml/apostas/`, regra MCC `7995` + lista oficial de operadoras SPA/MF por CNPJ/domínio + correspondência aproximada `RapidFuzz` com evidência explicável);
   - Integração prevista via portas da API Hexagonal (`ClassificadorTransacoes`, `LeitorExtrato`).
8. **Matriz de Rastreabilidade Arquitetural (Requisitos Não Funcionais RNF01 a RNF09):**
   - Tabela relacionando cada RNF (RNF01 a RNF09) à sua meta quantitativa, camada responsável, módulo/arquivo concreto no código e teste automatizado que valida a garantia.
9. **Infraestrutura, Topologia de Portas e Fluxo de Execução Local (Docker & Host):**
   - Mapa de portas (`3000` Web, `8000` API, `8010` RAG Service, `5434` Postgres App, `5433` Postgres RAG, `11434` Ollama);
   - Explicação da divisão Container vs. Host (por que `services/rag` roda no host para acessar Apple Silicon MPS / GPU e Ollama enquanto `apps/api` e `pgvector` rodam via Docker Compose).
10. **Mapa do Repositório e Estado de Integração por Branch:**
    - Árvore unificada do monorepo e tabela clara indicando em qual branch cada componente reside atualmente (`main`, `origin/develop`, `entrega/prototipo-multiagente-quarto-desafio`, `origin/dev/mariana`, `origin/dev/rayssa`) e os próximos passos de convergência.

## 5. Critérios de Aceite e Verificação

1. `docs/arquitetura-geral.md` existe, cobre todas as 10 seções acima, utiliza diagramas Mermaid válidos e possui links relativos funcionais para os documentos existentes na branch atual;
2. `docs/adr/0003-arquitetura-geral-sistema-pandora.md` e `docs/adr/README.md` registram formalmente a decisão de arquitetura unificada do sistema;
3. `README.md` inclui o link para `[Arquitetura Geral do Sistema](docs/arquitetura-geral.md)` e `[Arquitetura e Pipeline do RAG](docs/rag/README.md)` na tabela de Documentação;
4. Um teste automatizado em `services/rag/tests/test_arquitetura_docs.py` verifica a existência dos documentos arquiteturais, a presença das 10 seções estruturais, a integridade dos diagramas Mermaid e a resolução dos links locais referenciados.
