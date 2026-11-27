# Plano de Implementação: `LangGraph` (`StateGraph`) + Tool Calling Nativo nos 7 Agentes

- **Classificação ATLAS:** `ATLAS · refactor · arquitetura+produto · standard → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura`
- **Spec:** [`docs/atlas/2026-11-19-langgraph-tool-calling/spec.md`](spec.md)
- **ADR:** [`docs/adr/0002-orquestracao-langgraph-tool-calling.md`](../../adr/0002-orquestracao-langgraph-tool-calling.md)

---

## Tarefas (com Tags de Lane ATLAS)

### Tarefa 1 · `[arch]` Dependências `LangGraph`, Provedor LLM (`ChatOllama`/`ChatAnthropic`) e Contratos de Tool Calling
- **Arquivos:**
  - `services/rag/pyproject.toml`
  - `services/rag/src/pandora_rag/agents/models.py`
  - `services/rag/src/pandora_rag/agents/llm_provider.py` (novo)
  - `services/rag/tests/test_agents_tools.py`
- **O que fazer:**
  1. Adicionar `langgraph>=0.2`, `langchain-core>=0.3`, `langchain-ollama>=0.2` e `langchain-anthropic>=0.2` em `services/rag/pyproject.toml` e sincronizar o ambiente (`uv sync --extra dev`).
  2. Estender `models.py` para incluir metadados de observabilidade de LLM/Tool Calling em `EstadoMultiagente` e `ResultadoMultiagente` (ex.: `modelo_llm: str`, `pareceres_agentes: dict[str, str]`, `total_tool_calls: int`).
  3. Criar `llm_provider.py` que resolve qualquer chave de `modelos.yaml` (padrão `"qwen25-7b"` → `ChatOllama(model="qwen2.5:7b", temperature=0)` ou `"haiku"`/`"sonnet"` → `ChatAnthropic`), verifica conectividade e oferece helper `invocar_agente_com_tools(llm, system_prompt, user_prompt, tools)` que executa o ciclo `bind_tools` → `AIMessage.tool_calls` → execução da `@tool` → captura estruturada de argumentos, saída da tool e parecer do agente (com sanitização de PII antes de qualquer envio).

### Tarefa 2 · `[core]` Camada de `@tool`s Nativas do LangChain (`langgraph_tools.py`) e Refatoração dos 7 Agentes (`specialists.py`)
- **Arquivos:**
  - `services/rag/src/pandora_rag/agents/langgraph_tools.py` (novo)
  - `services/rag/src/pandora_rag/agents/specialists.py`
  - `services/rag/tests/test_agents_specialists.py`
- **O que fazer:**
  1. Criar `langgraph_tools.py` expondo as ferramentas determinísticas como `@tool`s fortemente tipadas do `langchain_core.tools`:
     - `tool_classificar_roteamento` (Orquestrador)
     - `tool_calcular_raio_x_financeiro` (Analista)
     - `tool_simular_reestruturacao_dividas` (Estrategista)
     - `tool_analisar_compulsao_apostas` (Coach)
     - `tool_inspecionar_fraude_e_boleto` (Guardião)
     - `tool_buscar_evidencias_rag` (Educador)
     - `tool_auditar_invariantes_compliance` (Compliance)
  2. Refatorar os 7 agentes em `specialists.py` para que cada um tenha seu `SYSTEM_PROMPT_<AGENTE>` dedicado, chame o LLM com `bind_tools` sobre sua `@tool`, gere pareceres e *queries* normativas dinâmicas a partir do raciocínio do LLM e grave no `trace` (`dados_chave`) as `tool_calls` invocadas, o modelo utilizado e o parecer do agente, mantendo os invariantes de segurança (`RNF01–RNF05`) inquebráveis.

### Tarefa 3 · `[arch]` Orquestração `StateGraph` (`LangGraph`) em `graph.py` e CLI com `qwen25-7b` Padrão
- **Arquivos:**
  - `services/rag/src/pandora_rag/agents/graph.py`
  - `services/rag/src/pandora_rag/cli.py`
  - `services/rag/tests/test_agents_graph.py`
- **O que fazer:**
  1. Refatorar `GrafoPandora` em `graph.py` para construir e compilar um `StateGraph(EstadoMultiagente)` do `LangGraph` com os nós (`orquestrador_planejar`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `orquestrador_sintetizar`, `compliance`, `fail_closed`) e arestas condicionais (`add_conditional_edges`) para roteamento dinâmico entre especialistas e loop de revisão `compliance -> orquestrador_sintetizar` (máx. 1 revisão).
  2. Definir `llm="qwen25-7b"` como modelo padrão na CLI (`pandora-rag agent` e `pandora-rag demo`) e em `GrafoPandora.executar()`, permitindo `--llm offline` quando o usuário quiser rodar sem daemon LLM.
  3. Escrever testes em `test_agents_graph.py` e `test_agents_specialists.py` validando a compilação e execução do `StateGraph`, o acionamento real de `tool_calls` nos 7 agentes com `qwen2.5:7b` e os cenários de revisão e *fail-closed*.

### Tarefa 4 · `[core]` Atualização da Demonstração Ao Vivo (`qwen2.5:7b`) e Documentação da Arquitetura `LangGraph`
- **Arquivos:**
  - `docs/agentes/{README.md,01-arquitetura.md,02-responsabilidades.md,03-fluxo-interacao.md,04-demonstracao.md}`
  - `docs/entregas/04-primeiro-prototipo-multiagente/README.md`
  - `docs/entregas/04-primeiro-prototipo-multiagente/demo/{demonstracao_multiagente.md,demonstracao_multiagente.json,abstencao-fora-de-dominio.json}`
  - `README.md`
- **O que fazer:**
  1. Executar `pandora-rag demo` e `pandora-rag agent` usando o `StateGraph` do `LangGraph` + `qwen2.5:7b` no Ollama local para regenerar os artefatos de demonstração com traces reais de Tool Calling.
  2. Atualizar a documentação técnica (`docs/agentes/` e `docs/entregas/04-primeiro-prototipo-multiagente/`) e o `README.md` explicando a arquitetura `LangGraph`, os `System Prompts` e as `@tool`s de cada agente.
