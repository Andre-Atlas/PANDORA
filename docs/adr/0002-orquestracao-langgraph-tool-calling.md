# ADR-0002: Migração para Orquestração `LangGraph` com Tool Calling Nativo (`qwen2.5:7b` / Ollama + Anthropic)

- **Status:** Aceito
- **Data:** 2026-11-19 (revisado em 2026-11-21)
- **Decisores:** Equipe PANDORA (RES IA ELD UNB — Turma 2)
- **Substitui parcialmente:** ADR-0001 (evolui o motor do grafo manual para `langgraph.graph.StateGraph` e adiciona Tool Calling nativo em todos os 7 agentes)
- **Contexto Relacionado:** RF01–RF09, RNF01–RNF06 (`docs/escopo/04-requisitos-4-graus.md`)

---

## 1. Contexto

Na versão inicial (`ADR-0001`), o módulo `pandora_rag.agents` implementou os 7 agentes (`orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `compliance`) sobre um estado Pydantic (`EstadoMultiagente`), porém o roteamento de intenções, a seleção de ferramentas, a formulação de *queries* para o RAG e a síntese textual estavam fortemente baseados em regras imperativas hardcoded (`if/else`, listas estáticas de palavras-chave e templates `f-string`), acionando o LLM (`Gateway`) apenas opcionalmente na reescrita final.

Para que o **Primeiro Protótipo Multiagente** opere como um sistema multiagente cognitivo real — mantendo 0,00% de erro aritmético (`RNF03`) e 100% das travas ético-regulatórias (`RNF01–RNF05`) — cada agente precisa possuir:
1. **System Prompt especializado** com instruções, papel e fronteiras de atuação;
2. **Tool Calling nativo (`@tool` + `bind_tools`)** onde o LLM do agente invoca as ferramentas determinísticas (`tools.py` / `Retriever`), interpreta seus resultados estruturados e formula pareceres e *queries* normativas dinâmicas;
3. **Orquestração declarativa em grafo via `LangGraph` (`StateGraph`)**, com nós tipados, arestas condicionais (`add_conditional_edges`) e loop de revisão `compliance -> orquestrador_sintetizar -> compliance`.

---

## 2. Alternativas Consideradas

### Alternativa A — Manter Grafo Imperativo Manual e Adicionar Chamadas `Gateway` Ad-Hoc
- **Prós:** Sem novas dependências no `pyproject.toml`.
- **Contras:** Não utiliza o protocolo nativo de *Tool Calling* (`tools=[...]`, `tool_calls`) dos modelos modernos nem oferece a abstração declarativa de nós, arestas condicionais e *state reducers* de um framework multiagente padrão de mercado.
- **Veredito:** Rejeitada.

### Alternativa B — `CrewAI` (`Agent` / `Task` / `Crew`)
- **Prós:** Abstração de alto nível orientada a personas e tarefas.
- **Contras:** Dificulta o controle fino de grafos cíclicos condicionais com estado fortemente tipado (`EstadoMultiagente`), como o loop *fail-closed* de 1 ciclo entre `ComplianceAgent` e `OrquestradorAgent`, além de introduzir dependências pesadas e telemetria acoplada.
- **Veredito:** Rejeitada.

### Alternativa C — `LangGraph` (`StateGraph`) + `langchain-core` / `langchain-ollama` / `langchain-anthropic` com `@tool` Nativo (Escolhida)
- **Prós:**
  - **Alinhamento 1:1 com a arquitetura do PANDORA:** o `StateGraph(EstadoMultiagente)` aceita diretamente modelos `Pydantic v2` como schema de estado;
  - **Tool Calling nativo nos 7 agentes:** cada agente usa `ChatOllama(model="qwen2.5:7b", temperature=0).bind_tools([...])` (ou `ChatAnthropic` quando configurado para nuvem) para invocar `@tool`s determinísticas, interpretar os números sem errar contas (`RNF03`) e formular *queries* e análises contextualizadas;
  - **Arestas condicionais e loop de revisão explícitos:** `add_conditional_edges` modela com precisão o despacho seletivo dos especialistas e o loop `compliance -> orquestrador_sintetizar` (máximo 1 revisão antes do fallback *fail-closed*);
  - **Execução local gratuita por padrão:** utiliza `qwen2.5:7b` já instalado no Ollama local (`http://localhost:11434`), mantendo fallback resiliente caso o daemon LLM esteja offline em ambientes de CI sem GPU.

---

## 3. Decisão

Adotar a **Alternativa C**:
1. Adicionar `langgraph>=0.2`, `langchain-core>=0.3`, `langchain-ollama>=0.2` e `langchain-anthropic>=0.2` às dependências de `services/rag/pyproject.toml`.
2. Expor as funções de cálculo, antifraude, RAG e auditoria como `@tool`s tipadas do LangChain (`pandora_rag.agents.langgraph_tools`), garantindo que a aritmética continue 100% determinística (`RNF03`).
3. Dotar todos os **7 agentes** de `System Prompt` próprio e execução via LLM com `bind_tools` (`qwen2.5:7b` no Ollama por padrão), registrando no `trace` (`MensagemAgente.dados_chave`) o modelo utilizado, as *tool calls* realizadas pelo LLM e o parecer gerado.
4. Orquestrar o fluxo completo através de um `StateGraph(EstadoMultiagente)` compilado do `LangGraph` dentro de `GrafoPandora`.

---

## 4. Consequências

- **Positivas:**
  - Combina *Tool Calling* nativo (`qwen2.5:7b`) para raciocínio semântico, geração dinâmica de *queries* normativas, interpretação de ferramentas e *LLM-as-a-Judge* com sensores determinísticos *defense-in-depth* (fronteira `\b`, verificação contra cadastro/extrato, isolamento de OCR e bloqueio do LLM durante crise e trava CVM);
  - Mantém total determinismo matemático nas contas (`tools.py`) e *guardrails* regulatórios *fail-closed* (`RNF01–RNF05`);
  - Preserva retrocompatibilidade com a CLI (`pandora-rag agent`, `pandora-rag demo`) e com a suíte de testes `pytest`.
- **Riscos e Mitigações:**
  - *Latência maior em execução com LLM local (chamadas a `qwen2.5:7b`):* mitigado usando `temperature=0`, `num_predict` enxuto por nó especialista e modo `--offline` para CI e execução instantânea determinística.
  - *Indisponibilidade do Ollama em ambiente de CI:* se o endpoint Ollama estiver inacessível ou `llm="offline"`, o nó registra `modo="deterministico"` / `modelo_llm="offline"` com transparência e executa as funções determinísticas mantendo o contrato do `EstadoMultiagente`.
