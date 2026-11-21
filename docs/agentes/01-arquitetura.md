# 01 · Arquitetura do Sistema Multiagente (`LangGraph` + Tool Calling)

O sistema multiagente do **PANDORA** ocupa a **Camada 4 (Orquestração Cognitiva)** da arquitetura geral em 6 camadas ([`docs/arquitetura-geral.md`](../arquitetura-geral.md) e [`ADR-0003`](../adr/0003-arquitetura-geral-sistema-pandora.md)). Internamente, adota um **`StateGraph(EstadoMultiagente)` compilado com `LangGraph`** e **Tool Calling nativo (`@tool` + `bind_tools`)** sobre o serviço `pandora_rag` ([`ADR-0001`](../adr/0001-arquitetura-multiagente-pandora.md) e [`ADR-0002`](../adr/0002-orquestracao-langgraph-tool-calling.md)).

Cada competência crítica do domínio financeiro, comportamental, antifraude, normativo e regulatório é isolada em um dos **7 agentes especializados**, combinando raciocínio semântico em modelo local (**`qwen2.5:7b` via `ChatOllama`**, padrão; com suporte a Anthropic via `ChatAnthropic`), ferramentas matemáticas determinísticas (`RNF03`) e travas *fail-closed* (`RNF01–RNF05`).

---

## 1. Diagrama da Arquitetura dos Agentes (`StateGraph` + `@tool`)

```mermaid
flowchart TD
    IN["Entrada do Usuário<br/>(Consulta + Persona ID + OCR / Linha Digitável)"] --> O1["1. Nó orquestrador_planejar<br/>ChatOllama qwen2.5:7b + @tool tool_classificar_roteamento<br/>Mascara PII (RNF01) · Sensores Crise/CVM (defense-in-depth)"]

    O1 -->|"add_conditional_edges (se há persona_id)"| AN["2. Nó analista<br/>LLM + @tool tool_calcular_raio_x_financeiro<br/>Despesas Vitais · Folga Real · SGS BCB (ref. fev/2026)"]

    AN -->|"intenção dividas + dívida real"| ES["3a. Nó estrategista<br/>LLM + @tool tool_simular_reestruturacao_dividas<br/>Avalanche vs. Bola de Neve · Lei 14.690/2023"]
    AN -->|"intenção bets + termos de aposta"| CO["3b. Nó coach<br/>LLM + @tool tool_analisar_compulsao_apostas<br/>Perda Líquida · Madrugada · Pausa 48h"]
    AN -->|"intenção fraude / OCR / boleto"| GU["3c. Nó guardiao<br/>LLM + @tool tool_inspecionar_fraude_e_boleto<br/>OCR isolado fora do prompt · FEBRABAN Mod 10 · MED Pix"]

    O1 -.->|"consulta geral / outro idioma"| ED
    AN -->|"sem especialista analítico adicional"| ED

    ES --> ED["4. Nó educador (Research Agent)<br/>LLM + @tool tool_buscar_evidencias_rag<br/>RAG Híbrido (BGE-M3 + BM25 + RRF) + Portão RNF04"]
    CO --> ED
    GU --> ED

    ED -->|"evidências [1]..[k] ou abstenção"| O2["5. Nó orquestrador_sintetizar<br/>Compila números exatos + tom da persona<br/>(LLM bloqueado em crise, CVM e revisão)"]
    O2 --> CG["6. Nó compliance (Validation Agent / LLM-as-a-Judge)<br/>LLM + @tool tool_auditar_invariantes_compliance<br/>Veto semântico + CVV 188 + CVM + Antifraude + Citações + Zero PII"]

    CG -->|"REPROVADO e revisoes < 1"| REV["preparar_revisao"] --> O2
    CG -->|"REPROVADO após revisão"| FC["fail_closed (contenção RNF01–RNF05)"] --> OUT
    CG -->|"APROVADO"| OUT["ResultadoMultiagente<br/>(Resposta Final + Fontes + Trace + Tool Calls)"]
```

---

## 2. Arquitetura em Camadas e Invariantes (`RNF01–RNF05`)

| Camada | Componentes / Arquivos | Garantia Arquitetural |
|---|---|---|
| **1. Fronteira de Privacidade & Segurança** | `pandora_rag.generate.pii.mascarar` + `sanitizar_documento_nao_confiavel()` | **RNF01 (LGPD) & RNF05 (Anti-Injection):** PII (`CPF`, `CNPJ`, e-mail, cartão, telefone) é mascarada na entrada, saída e antes de prompts externos. O texto de `documento_ocr` **nunca entra no prompt enviado ao LLM**; é sanitizado e auditado isoladamente dentro da tool do `GuardiaoAgent`. |
| **2. Orquestração Cognitiva (`LangGraph`)** | [`agents/graph.py`](../../services/rag/src/pandora_rag/agents/graph.py), [`agents/llm_provider.py`](../../services/rag/src/pandora_rag/agents/llm_provider.py) | **`StateGraph(EstadoMultiagente)`:** 10 nós registrados (`orquestrador_planejar`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `orquestrador_sintetizar`, `compliance`, `preparar_revisao`, `fail_closed`) conectados por `add_conditional_edges`. Cada agente recebe `System Prompt` próprio e vincula sua `@tool` com `bind_tools`. |
| **3. Núcleo Determinístico e `@tool`s** | [`agents/tools.py`](../../services/rag/src/pandora_rag/agents/tools.py), [`agents/langgraph_tools.py`](../../services/rag/src/pandora_rag/agents/langgraph_tools.py) | **RNF03 (0,00% de erro matemático):** Raio-X financeiro, simulação Avalanche vs. Bola de Neve, perda líquida em *bets* e dígito verificador Módulo 10 FEBRABAN rodam exclusivamente em funções Python testadas unitariamente expostas como `@tool`s LangChain. |
| **4. Recuperação Normativa (RAG)** | `EducadorAgent` + `executar_busca_evidencias_rag()` (`pgvector` → `corpus_local_bge_m3` → `corpus_local_bm25_hash` → `corpus_embutido_oficial`) | **RNF04 (Anti-Alucinação):** Busca híbrida `bge-m3` + `BM25` + `RRF`, filtrando preâmbulos vazios e cláusulas puramente revogatórias/promulgatórias (limite máximo de 4 citações relevantes `[1]..[k]`) e portão de abstenção validado por domínio léxico e score. |
| **5. Governança Ético-Regulatória** | `ComplianceAgent` + `tool_auditar_invariantes_compliance` | **RNF02 (CVM) & Protocolo de Crise:** Combina auditoria semântica (*LLM-as-a-Judge*) com invariantes duros (ideação suicida direta/indireta `CVV 188`, trava CVM 19/20, julgamento moral, checagem exata antifraude, zero PII, citações consistentes). Em crise ou trava CVM, a geração livre de texto do LLM é desligada por segurança. |
| **6. Auditoria e Contratos** | [`agents/models.py`](../../services/rag/src/pandora_rag/agents/models.py) (`EstadoMultiagente`, `MensagemAgente`, `ResultadoMultiagente`) | Cada colaboração, *tool call* e decisão de revisão fica registrada em `trace: list[MensagemAgente]` e consolidada em JSON/Markdown. |

---

## 3. Resolução de Corpus e Modos de Execução

O `GrafoPandora` opera com degradação transparente de infraestrutura:

1. **Recuperação (`Retriever`):**
   - `pgvector` (PostgreSQL vetorial ativo com índice `HNSW`);
   - `corpus_local_bge_m3` (33 fontes extraídas + embeddings `BAAI/bge-m3` em cache local + `BM25`);
   - `corpus_local_bm25_hash` (33 fontes extraídas + `BM25` + hash vetorial, sem GPU);
   - `corpus_embutido_oficial` (`--offline` / CI sem corpus baixado).
2. **Modelo de Linguagem (`--llm` / `--offline`):**
   - `langgraph_llm` (**padrão** quando o daemon Ollama local está ativo com `qwen2.5:7b` — `llm="qwen25-7b"`);
   - `deterministico` (quando passado `--offline`, `llm=None` ou quando o daemon Ollama local não está rodando — registrando explicitamente `modo="deterministico"` e `modelo_llm="offline"` sem rótulos enganosos).
