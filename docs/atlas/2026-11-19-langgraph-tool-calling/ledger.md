# Ledger de Execução: `LangGraph` + Tool Calling Nativo (`qwen2.5:7b`)

- **Data:** 2026-11-19
- **Gate 1:** Aprovado pelo usuário (`2026-11-19T11:26:29-03:00`).

## Rulings

- **Ruling 1:** Manter `EstadoMultiagente` (`Pydantic BaseModel`) como schema de estado do `StateGraph(EstadoMultiagente)` do `LangGraph` e retornar dicionários parciais ou `EstadoMultiagente` atualizado em cada nó — porque o `LangGraph >= 0.2` suporta nativamente schemas `Pydantic v2` como `state_schema`, preservando 100% de compatibilidade com os testes de contrato existentes — custo se errado: baixo (basta converter nos nós).
- **Ruling 2:** Padronizar `llm="qwen25-7b"` (`qwen2.5:7b` via `ChatOllama`) como default em `GrafoPandora.executar()` e na CLI (`pandora-rag agent` e `pandora-rag demo`), mas aceitar `llm=None` ou `llm="offline"` para execução rápida em testes unitários puramente determinísticos, e se o `ChatOllama` estiver ativo com `llm="qwen25-7b"`, executar o ciclo completo de `bind_tools` + `@tool` nos 7 agentes — porque concilia execução real de Tool Calling via LLM com velocidade de suíte unitária quando desejado — custo se errado: zero.
