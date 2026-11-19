# Índice de Registros de Decisão Arquitetural (ADR)

Decisões arquiteturais formais do projeto **PANDORA**, seguindo o padrão `docs/adr/`.

| ID | Título | Status | Data | Documento / Branch |
|---|---|---|---|---|
| **ADR-0001** | Arquitetura Multiagente em Grafo de Estado Tipado (`pandora_rag.agents`) | Aceito | 2026-11-17 | `docs/adr/0001-arquitetura-multiagente-pandora.md` *(branch `entrega/prototipo-multiagente-quarto-desafio`)* |
| **ADR-0002** | Migração para Orquestração `LangGraph` com Tool Calling Nativo (`qwen2.5:7b` / Ollama + Anthropic) | Proposto (Gate 1) | 2026-11-19 | `docs/adr/0002-orquestracao-langgraph-tool-calling.md` *(branch `entrega/prototipo-multiagente-quarto-desafio`, substitui parcialmente o motor do `ADR-0001`)* |
| **ADR-0003** | Topologia Geral e Arquitetura Unificada em 6 Camadas do Sistema PANDORA | Aceito | 2026-11-19 | [0003-arquitetura-geral-sistema-pandora.md](0003-arquitetura-geral-sistema-pandora.md) *(consolida a visão macro do sistema e engloba os ADRs `0001` e `0002` na Camada 4)* |
