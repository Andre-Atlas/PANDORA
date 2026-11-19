# ADR-0003: Topologia Geral e Arquitetura Unificada em 6 Camadas do Sistema PANDORA

- **Status:** Aceito
- **Data:** 2026-11-19
- **Decisores:** Equipe PANDORA (Challenge 2 · CBL — Qualidade de Vida / Finanças)
- **Relação com outros ADRs:** Consolida a topologia macro do sistema e engloba as decisões da Camada 4 definidas em `ADR-0001` (*Aceito*) e `ADR-0002` (*Proposto (Gate 1)*, que evolui o grafo manual para `LangGraph` com *Tool Calling* nativo na branch `entrega/prototipo-multiagente-quarto-desafio`).
- **Contexto Relacionado:** Requisitos `RF01–RF18` e `RNF01–RNF09` ([`docs/escopo/04-requisitos-4-graus.md`](../escopo/04-requisitos-4-graus.md)), RAG Híbrido `rag-v0.1.0` ([`docs/rag/01-arquitetura.md`](../rag/01-arquitetura.md)) e Design System ([`frontend/design-system/README.md`](../../frontend/design-system/README.md)).

---

## 1. Contexto

O **PANDORA** é um copiloto financeiro com Inteligência Artificial voltado para pessoas em situação de superendividamento, comportamento financeiro compulsivo (apostas online / *bets* e compras por impulso) ou vulnerabilidade a golpes digitais (Pix e boletos falsos).

Ao longo das sprints e entregas do Challenge-Based Learning (CBL), a equipe desenvolveu componentes que se organizam em **6 camadas arquiteturais** no monorepo:

1. **Camada 1 — Apresentação e Experiência (`frontend/design-system` + `apps/web`):** Design System `@pandora/design-system` estruturado em *Dois Registros* (*Mito* e *Leitura*) e aplicação PWA em Next.js 16 + React 19 + TypeScript (`:3000`) com conformidade WCAG 2.2 AA (`RNF07`), modo de crise prioritário (`CriseProvider` — `RF05`) e cliente HTTP tipado via OpenAPI;
2. **Camada 2 — Aplicação e Domínio (`apps/api` / `pandora_api`):** backend FastAPI (`:8000`) em Arquitetura Hexagonal (`dominio`, `portas`, `aplicacao`, `adaptadores` — `RNF06`), aritmética em centavos inteiros (`valor_centavos: int` — `RNF03`), erros RFC 9457 e exclusão total LGPD (`DELETE /eu/dados` — `RNF01`);
3. **Camada 3 — Conhecimento e Recuperação Normativa (`services/rag`, `evals/`, `training/`):** pipeline RAG híbrido `rag-v0.1.0` (`:8010`) sobre 33 fontes normativas oficiais (`corpus.lock` SHA-256), chunking estrutural por artigo/seção (`norma | seção | artigo`), busca híbrida `BAAI/bge-m3` (`pgvector` HNSW `:5433`) + `BM25` + `RRF (k=60)` + `BAAI/bge-reranker-v2-m3`, portão de abstenção (`score_rerank < 0,02`) e `Gateway` de LLM com mascaramento de PII (`RNF01`, `RNF04`);
4. **Camada 4 — Orquestração Cognitiva Multiagente (`pandora_rag.agents`):** grafo de estado tipado em `LangGraph` (`StateGraph(EstadoMultiagente)`) coordenando 7 agentes especializados (`orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `compliance`) com *Tool Calling* nativo (`@tool` + `bind_tools` em `qwen2.5:7b`) e validação *fail-closed* (`RNF01–RNF05`);
5. **Camada 5 — Aprendizado de Máquina Clássico e Motores Determinísticos (`services/ml`):** geração de dados sintéticos (`SEED=42`), classificador supervisionado de transações com `LightGBM` + TF-IDF (protegendo o *Mínimo Existencial* — `RF02`), detector híbrido de apostas (`MCC 7995` + lista oficial SPA/MF + `RapidFuzz` — `RF04`) e funções matemáticas determinísticas (`RNF03`);
6. **Camada 6 — Infraestrutura, Persistência Dual e Fontes Externas (`Docker Compose` + `Host MPS/Ollama`):** topologia híbrida separando o banco transacional de usuários (`pgvector :5434`), o banco vetorial normativo (`pgvector :5433`), o daemon de inferência local (`Ollama :11434`) e a coleta de fontes públicas oficiais (API SGS/BCB, Planalto, CVM, SPA/MF).

Até então, cada subsistema documentava apenas seu próprio escopo local, faltando uma especificação arquitetural unificada que definisse como as 6 camadas se integram, quais contratos governam as fronteiras entre serviços e qual é o estado real medido dos requisitos não funcionais (`RNF01–RNF09`).

---

## 2. Alternativas Consideradas

### Alternativa A — Acoplamento Monolítico em Processo Único (Next.js / FastAPI executando Torch, LightGBM, LangGraph e Banco no mesmo Container)
- **Prós:** Um único serviço para iniciar.
- **Contras:** Inviabiliza o uso de aceleração de hardware local (Apple Silicon MPS / GPU e daemon Ollama) quando empacotado em container Linux padrão; mistura regras de domínio puras com dependências pesadas de ML (`sentence-transformers`, `torch`, `lightgbm`, `langgraph`); viola a exigência de Arquitetura Hexagonal (`RNF06`) e dificulta testes unitários rápidos (`pytest` em memória).
- **Veredito:** Rejeitada.

### Alternativa B — Microsserviços Pulverizados por Agente/Modelo (Um container HTTP para cada Agente e cada Modelo de ML)
- **Prós:** Isolamento físico extremo entre componentes.
- **Contras:** Latência de rede proibitiva para o ciclo multiagente (agravando a latência $p95$, que no baseline local já é de $14,4\text{ s}$ frente à meta de $\le 8\text{ s}$ do `RNF06`); complexidade operacional incompatível com o ciclo acadêmico de 7 semanas (`R08`); duplicação de carregamento do modelo de embeddings `BAAI/bge-m3` na memória.
- **Veredito:** Rejeitada.

### Alternativa C — Arquitetura Modular nas 6 Camadas com Fronteiras Explícitas e Divisão Híbrida Docker + Host Cognitivo (Escolhida)
Organizar o monorepo nas **6 camadas arquiteturais** conectadas por **3 fronteiras de contrato**:
1. **Fronteira Camada 1 ↔ Camada 2 (`Contract-First OpenAPI`):** `apps/api` exporta `openapi.json` a partir dos esquemas Pydantic; `apps/web` gera `lib/api/esquema.d.ts` automaticamente e falha na CI se houver deriva (`test_contrato.py` e `esquema.test.ts`);
2. **Fronteira Camada 2 ↔ Camada 5 (`Ports & Adapters` no Domínio):** `apps/api/src/pandora_api/portas/` define protocolos Python puros (`AssistenteElpis`, `RepositorioTrilha`, `LeitorExtrato`, `ClassificadorTransacoes`, repositórios), mantendo `dominio` e `aplicacao` 100% livres de frameworks (`test_arquitetura.py`);
3. **Fronteira Camada 2 ↔ Camadas 3/4 (`HTTP :8000 -> :8010` via `PANDORA_RAG_URL`):** `services/rag` roda nativamente no host (`pandora-rag servir` na porta `8010`, expondo `GET /saude` e `POST /responder` tipados em Pydantic via `PerguntaEntrada` / `RespostaSaida`) para acesso direto a MPS/GPU e ao daemon `Ollama` (`:11434`). A API (`:8000`, em container ou host) comunica-se com ele através do adaptador `AssistenteHttp` (`PANDORA_RAG_URL=http://host.docker.internal:8010` no Docker Compose ou `http://localhost:8010` no host, com `httpx.Timeout(60.0, connect=3.0)`).

---

## 3. Decisão

Adotar a **Alternativa C** e instituir o documento canônico **[`docs/arquitetura-geral.md`](../arquitetura-geral.md)** como referência oficial da arquitetura de software, dados, ML e agentes do projeto PANDORA, estabelecendo os seguintes invariantes e decisões de governança:

1. **Princípio Fundamental (`RNF03`):** *"Determinístico onde é possível, probabilístico onde é necessário"*. Nenhuma conta financeira é realizada por LLM. Para eliminar qualquer risco de *split-brain* entre as fórmulas de `apps/api` (`dominio/raio_x.py`) e as `@tool`s do protótipo multiagente (`pandora_rag.agents.tools.py`), a API Hexagonal é a **dona canônica do estado transacional persistido (`:5434`)**, enquanto `tools.py` opera como motor puro sobre o snapshot de transações/diagnóstico fornecido ao grafo (atualmente lido do dataset sintético das personas por `persona_id` e, na convergência final, hidratado pelo payload da API).
2. **Isolamento de Dados, Bancos (`:5434` vs. `:5433`) e Logs (`RNF01`):**
   - Dados transacionais e contas de usuários vivem exclusivamente no PostgreSQL da aplicação (`porta 5434`), sujeitos a expurgo imediato via `DELETE /eu/dados`;
   - O serviço cognitivo (`:8010`) é **stateless por requisição** (não persiste histórico de conversas de usuários em banco); logs operacionais JSONL do `Gateway` registram apenas metadados de telemetria (`chave`, `modelo`, `tokens_in`, `tokens_out`, `custo_usd`, `latencia_s`, `pii_mascarada`), **omitindo explicitamente o campo `texto`** (`gateway.py`);
   - Enquanto no `Gateway` base (`rag-v0.1.0`) o mascaramento `pii.mascarar` é ativado obrigatoriamente para provedores externos (`externo: true`) e na ingestão CSV (`mascarar_descricao`), no grafo multiagente (`OrquestradorAgent`) `pii.mascarar` é aplicado incondicionalmente já na borda de entrada (`consulta_mascarada`), mesmo para modelos locais (`Ollama`).
3. **Decisão sobre Cache (`RNF08` — Ruling Arquitetural):** No MVP acadêmico, o cache de consultas frequentes e conteúdo educativo previsto no `RNF08` (Grau 3 — *Could-Have*) é atendido sem introduzir um container `Redis` adicional, utilizando pré-geração estática triada (`apps/api/src/pandora_api/dados/trilha.v1.json` via `TrilhaEmArquivo`), cache em disco dos embeddings `BAAI/bge-m3` e constantes locais das séries SGS/BCB, reduzindo a complexidade operacional. A adoção de `Redis` fica reservada para escala multi-instância.
4. **Transparência Científica sobre Métricas (`RNF04`, `RNF06`):** A documentação arquitetural deve sempre reportar tanto a **meta de escopo** quanto o **valor real medido** nas rodadas experimentais (`evals/runs/`), explicitando lacunas abertas (como abstenção de `70%` vs. meta $\ge 90\%$, citação de `96,0%` vs. meta `100%` e latência $p95 = 14,4\text{ s}$ vs. meta $\le 8\text{ s}$ no `golden.v1`).

---

## 4. Consequências

- **Positivas:**
  - Qualquer integrante da equipe ou avaliador externo possui um ponto único de verdade ([`docs/arquitetura-geral.md`](../arquitetura-geral.md)) alinhado com o código real e com os relatórios experimentais de `evals/`;
  - Os contratos explícitos entre `apps/web` (`esquema.d.ts`), `apps/api` (`openapi.json` e portas hexagonais), `services/rag` (`POST /responder`) e `services/ml` permitem evolução paralela segura;
  - A integridade estrutural, as 10 seções obrigatórias, os diagramas Mermaid e todos os links e âncoras locais são verificados automaticamente por [`services/rag/tests/test_arquitetura_docs.py`](../../services/rag/tests/test_arquitetura_docs.py).
- **Negativas / Riscos e Mitigações:**
  - *Acoplamento do runtime `:8010` ao host local (MPS/Ollama):* dificulta empacotamento 100% containerizado em CI Linux sem GPU. **Mitigação:** `services/rag` e `pandora_rag.agents` possuem fallback determinístico em memória (`MemoryStore` + `EmbedderHash` / modo `--offline`) que roda a suíte `pytest` completa em segundos sem GPU nem daemon Ollama.
  - *Operação de dois bancos PostgreSQL (`:5434` e `:5433`):* consome mais memória local quando ambos os containers estão ativos. **Mitigação:** isolar os volumes (`pandora_db` vs. `pandora_rag_db`) garante que `DELETE /eu/dados` nunca afete o corpus normativo e permite rodar `:8010` sobre artefatos locais pré-indexados mesmo com o container `:5433` desligado.
  - *Contrato HTTP `:8000 ↔ :8010` ainda não sincronizado por geração automática de código:* ao contrário de `apps/web ↔ apps/api`, os esquemas `PerguntaEntrada`/`RespostaSaida` (`services/rag`) e `AssistenteHttp` (`apps/api`) são mantidos manualmente em Python. **Mitigação:** cobertos por testes de contrato em ambos os lados (`test_servico.py` e `test_chat.py`) e mapeados para unificação quando `pandora_rag.agents` for exposto em `:8010`.
