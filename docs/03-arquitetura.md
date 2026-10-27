# 03 · Arquitetura

## 1. Princípios

1. **Hexagonal (ports & adapters):** regras financeiras e de domínio não conhecem banco, framework, agregador ou provedor de LLM.
2. **Determinístico onde dá, probabilístico onde precisa:** cálculos financeiros (juros, CET, priorização) são código testável; LLM só interpreta, explica e conversa.
3. **Evidência rastreável:** toda afirmação normativa vem do RAG com citação.
4. **Privacidade por padrão:** PII mascarada antes de sair do perímetro; o modelo local cuida do que é sensível.
5. **Provider-agnostic:** a escolha de LLM ([ADR-0003](adr/0003-selecao-llm.md)) pode mudar sem reescrever os agentes.

## 2. Contexto (C4 · Nível 1)

```mermaid
flowchart LR
    U["👤 Usuário"] -->|"PWA: chat, voz, upload"| P["PANDORA"]
    P -->|"consentimento + leitura"| AG["Agregador Open Finance<br/>(Pluggy/Belvo, sandbox)"]
    AG --> B["Bancos / instituições"]
    P -->|"inferência"| LLM["LLM em nuvem<br/>(ADR-0003)"]
    P -->|"ingestão periódica"| SRC["Fontes oficiais<br/>BCB · CVM · Tesouro · Leis · SPA/MF"]
    P -.->|"encaminhamento"| APOIO["CVV · CAPS · JA · Procon"]
```

## 3. Containers (C4 · Nível 2)

```mermaid
flowchart TB
    subgraph Cliente
        WEB["apps/web<br/>Next.js PWA<br/>chat · dashboard · voz · upload"]
    end
    subgraph Backend
        API["apps/api · FastAPI<br/>auth · consentimento · domínio financeiro"]
        AGT["services/agents · LangGraph<br/>Orquestrador + especialistas"]
        MLS["services/ml<br/>classificador · anomalia · forecast"]
        ING["workers/ingestion<br/>extratos · OCR · corpus RAG"]
        GW["LLM Gateway<br/>roteamento · PII masking · cache · custo"]
        LOC["Modelo local quantizado<br/>(llama.cpp / Ollama)"]
    end
    subgraph Dados
        PG[("Postgres<br/>+ pgvector")]
        RD[("Redis<br/>cache · filas · sessões")]
        OBJ[("Object storage<br/>arquivos cifrados")]
    end
    WEB -->|"REST + SSE/WebSocket"| API
    API --> AGT
    API --> MLS
    API --> ING
    AGT --> GW
    GW --> LOC
    GW -->|"PII mascarada"| CLOUD["LLM nuvem"]
    AGT --> PG
    API --> PG
    API --> RD
    ING --> OBJ
    ING --> PG
    API --> AGG["Agregador Open Finance"]
```

### Estrutura do monorepo (proposta)

```
apps/
  web/                 # Next.js PWA
  api/                 # FastAPI
    domain/            # entidades e regras (Dívida, Transação, Plano, Meta)
    ports/             # BankDataPort, LLMPort, VectorStorePort, NotificationPort
    adapters/          # pluggy/, belvo/, ofx/, pgvector/, llm_gateway/
    application/       # casos de uso
services/
  agents/              # grafo LangGraph, ferramentas, prompts, guardrails
  ml/                  # treino, avaliação, artefatos versionados
workers/
  ingestion/           # parsers, OCR, pipeline do corpus RAG
evals/                 # golden sets, Ragas, testes adversariais
infra/                 # docker-compose, IaC, CI
docs/
```

## 4. Sistema multiagente (produto)

Padrão **supervisor + especialistas** com um **guardião transversal**. Detalhes de cada agente estão em [04-agentes-ia.md](04-agentes-ia.md).

```mermaid
flowchart TB
    IN["Mensagem do usuário<br/>(texto · voz · imagem)"] --> MM["Agente Multimodal<br/>STT · OCR · visão"]
    MM --> CG1["Compliance Guard (entrada)<br/>PII · injeção · sinal de risco"]
    CG1 --> ORQ{"Orquestrador<br/>intenção · plano · roteamento"}
    ORQ --> AD["Analista de Dados"]
    ORQ --> CC["Coach Comportamental"]
    ORQ --> ED["Estrategista de Dívidas"]
    ORQ --> PO["Planejador de Orçamento"]
    ORQ --> GU["Guardião (fraude · travas)"]
    ORQ --> EDU["Educador (RAG)"]
    AD & CC & ED & PO & GU & EDU --> ORQ
    ORQ --> CG2["Compliance Guard (saída)<br/>CVM · citações · tom · disclaimers"]
    CG2 --> OUT["Resposta + fontes + ações sugeridas"]
    CG1 -- "risco à vida" --> SOS["Fluxo de crise<br/>CVV 188 / CAPS"]
```

- **Estado explícito** (LangGraph): perfil do usuário, fase da jornada, plano ativo, histórico resumido.
- **Ferramentas tipadas** (Pydantic): `get_transactions`, `get_debts`, `simulate_renegotiation`, `search_knowledge`, `check_bet_operator`, `analyze_scam_image`, `set_spending_lock`…
- **Nenhuma ferramenta movimenta dinheiro.** Ações com efeito (trava, notificação ao contato) exigem confirmação do usuário.
- As ferramentas podem ser expostas também via **MCP** para reuso e testes.

## 5. Pipeline RAG

```mermaid
flowchart LR
    S["Fontes oficiais<br/>PDF · HTML · leis"] --> C["Coleta versionada<br/>(data, URL, hash)"]
    C --> P["Parsing + limpeza"]
    P --> K["Chunking por estrutura<br/>(artigo, seção)"]
    K --> E["Embeddings"]
    E --> V[("pgvector")]
    K --> BM[("Índice BM25")]
    Q["Pergunta"] --> QR["Reescrita da consulta"]
    QR --> V & BM
    V & BM --> F["Fusão (RRF)"]
    F --> RR["Reranking"]
    RR --> G["Geração com citações"]
    G --> CHK["Checagem de groundedness"]
```

- **Corpus:** BCB, CVM, Tesouro, Lei 14.181/2021, Lei 14.790/2023, CPC, LGPD, SPA/MF, Procon, padrões de golpe (FEBRABAN).
- **Metadados por chunk:** fonte, URL, data de coleta, vigência, tipo (lei/norma/guia).
- **Política de recusa:** se o contexto não sustenta a resposta, o agente diz que não sabe e indica o canal oficial.
- **Semana 3:** a mesma suíte de perguntas roda em *LLM puro* × *RAG* para medir o ganho ([06](06-riscos-e-metricas.md)).

## 6. LLM Gateway (híbrido local + nuvem)

```mermaid
flowchart LR
    REQ["Chamada de agente"] --> MASK["Mascaramento de PII<br/>(modelo local + regex)"]
    MASK --> RT{"Roteador<br/>tarefa · custo · sensibilidade"}
    RT -->|"classificação, extração, PII"| L["Modelo local quantizado"]
    RT -->|"raciocínio, conversa longa"| N["LLM nuvem (ADR-0003)"]
    L & N --> CACHE["Cache semântico + log de custo/latência"]
    CACHE --> UNMASK["Reidentificação local"]
```

- Interface única (`LLMPort`), implementada com LiteLLM ou uma camada própria.
- Telemetria por chamada: tokens, custo, latência, modelo, tarefa. Esses dados alimentam a decisão do ADR-0003.
- **A escolha final de provedor/modelo está em aberto** e será decidida por uma matriz de custo × facilidade de deploy × qualidade nas features reais.

## 7. ML clássico

| Modelo | Entrada | Saída | Baseline → evolução |
|---|---|---|---|
| Classificador de transações | descrição, valor, MCC, horário | categoria + confiança | regras/regex → gradient boosting/embeddings → LLM fallback |
| Detector de apostas | CNPJ/descrição, destino Pix | flag + evidência | lista SPA/MF → fuzzy match → classificador |
| Anomalia / impulso / fraude | série de transações | score + explicação | z-score → Isolation Forest |
| Previsão de caixa | histórico de saldo | saldo previsto 30/60/90d | média móvel → Prophet/ETS |

## 8. Segurança e LGPD

- Consentimento granular e revogável por fonte, com registro de finalidade.
- Tokens do agregador em cofre de segredos. Arquivos e campos sensíveis cifrados em repouso. TLS em trânsito.
- PII mascarada antes de qualquer chamada externa. Logs sem PII.
- Retenção mínima, exclusão sob demanda e trilha de auditoria de acessos.
- Testes de prompt injection via conteúdo de extratos, boletos e imagens.
- Detalhes em [05-dados-e-integracoes.md](05-dados-e-integracoes.md) e no agente [`compliance_financeiro_lgpd`](../.agents/agents/compliance_financeiro_lgpd.md).

## 9. Deploy

- **Local:** `docker-compose` (web, api, agents, ml, postgres+pgvector, redis, modelo local).
- **Nuvem:** containers em um provedor gerenciado (AWS/Render/Fly). O modelo local roda em uma instância dedicada ou é substituído por um endpoint gerenciado de modelo aberto, conforme o ADR-0003.
- **CI:** lint, testes, suíte de avaliação de IA com limiares bloqueantes, scan de segredos.
