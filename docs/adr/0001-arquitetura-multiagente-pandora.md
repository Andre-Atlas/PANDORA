# ADR-0001: Arquitetura Multiagente em Grafo de Estado Tipado (`pandora_rag.agents`)

- **Status:** Aceito (Proposto para Gate 1)
- **Data:** 2026-11-17
- **Decisores:** Equipe PANDORA (RES IA ELD UNB — Turma 2)
- **Contexto Relacionado:** RF01–RF09, RNF01–RNF06 (`docs/escopo/04-requisitos-4-graus.md`), RAG base `rag-v0.1.0` (`services/rag/`)

---

## 1. Contexto

O entregável **Primeiro Protótipo Multiagente** (RES IA ELD UNB — Turma 2) exige a implementação de no mínimo 2 agentes especializados (podendo incluir adicionais conforme a complexidade do projeto), documentação da arquitetura, responsabilidades e fluxo de colaboração, além de demonstração executável end-to-end.

No projeto **PANDORA**, o escopo CBL prevê 7 papéis especializados operando sobre finanças pessoais, superendividamento (Lei nº 14.181/2021), compulsão por apostas (Lei nº 14.790/2023), prevenção a fraudes (MED Pix — Res. BCB nº 147/2021) e educação financeira sob guardrails regulatórios (Res. CVM nº 19 e 20/2021). Ao mesmo tempo, o repositório já conta com o serviço `services/rag` (`pandora_rag`), que implementa:
- Recuperação híbrida (`pgvector` / `MemoryStore` + `BM25` + `RRF` + `bge-reranker-v2-m3`);
- Portão de abstenção (`score_rerank < 0.02`);
- `Gateway` unificado para Ollama local e Anthropic;
- Mascarador de PII (`pandora_rag.generate.pii.mascarar`) atendendo à LGPD (RNF01).

Os requisitos não funcionais impõem restrições rígidas:
- **RNF01 (LGPD):** 0% de vazamento de PII antes de chamadas externas;
- **RNF02 (CVM):** bloqueio arquitetural contra recomendação específica de ativos;
- **RNF03 (Determinismo):** erro numérico de 0,00% — proibição de aritmética livre no LLM para juros, CET, amortização e mínimo existencial;
- **RNF04 (Anti-Alucinação):** citações `[n]` rastreáveis às fontes oficiais ou abstenção;
- **RNF05 (Segurança de IA):** isolamento estrutural contra *prompt injection* indireto em textos de boletos/extratos;
- **Protocolo de Crise:** disparo imediato de acolhimento (`CVV 188`, CAPS AD, Jogadores Anônimos) diante de sofrimento psíquico agudo.

---

## 2. Alternativas Consideradas

### Alternativa A — Agente Monolítico com Múltiplas Tools
Um único prompt de sistema com várias funções acopladas.
- **Prós:** Menor número de arquivos iniciais.
- **Contras:** Mistura raciocínio financeiro, normativo, antifraude e compliance em uma única chamada; impossibilita auditoria clara de handoffs e especialização de responsabilidade exigida pelo entregável; aumenta o risco de o modelo ignorar travas regulatórias ou realizar cálculos aritméticos livres.
- **Veredito:** Rejeitada.

### Alternativa B — Framework Externo Pesado em Serviço Separado (`CrewAI` ou `AutoGen` em `services/agents/`)
Criar um novo pacote Python separado orquestrado por framework opinativo externo.
- **Prós:** Abstrações prontas para prototipagem rápida.
- **Contras:** Introduz dependências pesadas e opacas; duplica ou contorna o `Gateway` (`pandora_rag.generate.gateway`) que já controla orçamento (`orcamento_usd`), logs JSONL e máscara de PII; dificulta execução determinística em suítes `pytest` offline e adiciona atrito de empacotamento sem ganho funcional.
- **Veredito:** Rejeitada.

### Alternativa C — Grafo de Estado Tipado (`Pydantic`) com 7 Agentes Especializados em `pandora_rag.agents` (Escolhida)
Implementar uma máquina de estados explícita em Python/Pydantic puro dentro de `services/rag/src/pandora_rag/agents/`, reutilizando diretamente `Gateway`, `mascarar` e `Retriever`, com nós especializados (`orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `compliance`).
- **Prós:**
  - **100% de reuso** da infraestrutura já validada em `services/rag` e no mesmo ambiente `uv`;
  - **Contratos explícitos e auditáveis:** cada colaboração entre agentes gera uma `MensagemAgente` tipada no `trace` do `EstadoMultiagente`;
  - **Determinismo e Segurança:** cálculos financeiros (Avalanche, Bola de Neve, Mínimo Existencial, perda líquida de apostas, validação FEBRABAN) rodam exclusivamente em funções Python testadas unitariamente (`tools.py`), enquanto o `ComplianceAgent` atua como portão final com ciclo de revisão (*validation loop*);
  - **Testabilidade:** permite rodar tanto com LLM real (via Ollama/Anthropic configurado no `Gateway`) quanto em modo determinístico/offline para CI e demonstrações reproduzíveis sem GPU/rede.
- **Contras / Trade-offs:**
  - Exige manutenção disciplinada dos modelos Pydantic compartilhados entre os nós (mitigado por testes de contrato e revisão de tipos).

---

## 3. Decisão

Adotar a **Alternativa C**: construir o módulo `pandora_rag.agents` dentro de `services/rag/src/pandora_rag/agents/` com **7 agentes especializados** coordenados por um **grafo de estado tipado (`GrafoPandora`)**, mantendo:
1. Fronteiras claras entre cálculo determinístico (`tools.py`), recuperação normativa (`Retriever`), geração de linguagem (`Gateway`) e validação regulatória/ética (`ComplianceAgent`);
2. Rastreabilidade completa de cada mensagem trocada entre agentes (`MensagemAgente`);
3. Interface CLI unificada (`pandora-rag agent` e `pandora-rag demo`).

---

## 4. Consequências

- **Positivas:**
  - Atende integralmente aos critérios do entregável (≥ 2 agentes, papéis claros, arquitetura documentada e execução demonstrável ponta a ponta);
  - Antecipa a topologia completa do sistema PANDORA prevista em `docs/escopo/documento-completo-cbl.md` sem retrabalho futuro;
  - Facilita a futura integração com `LangGraph` ou API `FastAPI` (RNF06), pois o estado `EstadoMultiagente` e os nós já seguem assinatura compatível (`EstadoMultiagente -> EstadoMultiagente`).
- **Riscos e Mitigações:**
  - *Risco de acoplamento entre nós:* mitigado centralizando os contratos em `agents/models.py` e validando cada transição com `pytest`.
  - *Risco de ausência de Ollama/Postgres no ambiente de avaliação da turma:* mitigado oferecendo suporte transparente a `MemoryStore` + `Gateway` local e modo determinístico auditável quando não houver LLM ativo.
