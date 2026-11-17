# Ledger de Decisões — Primeiro Protótipo Multiagente PANDORA

- **Slug:** `2026-11-17-primeiro-prototipo-multiagente`
- **Classificação:** `ATLAS · feature · arquitetura+dados · large → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura`

## Decisões de Descoberta (Alinhadas com o Usuário)
1. **Topologia de 7 Agentes:** Adotar `orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador` e `compliance` (antecipando a arquitetura completa do escopo CBL).
2. **Localização e Stack:** Módulo `services/rag/src/pandora_rag/agents/` em Python + Pydantic puro, reutilizando `Gateway`, `mascarar` (PII), `Retriever` híbrido e `uv`.
3. **Demonstração Executável:** Comandos CLI `pandora-rag agent` e `pandora-rag demo` com registro completo do trace de colaboração em Markdown e JSON.
4. **Documentação Modular:** Diretório `docs/agentes/` com `README.md`, `01-arquitetura.md`, `02-responsabilidades.md`, `03-fluxo-interacao.md` e `04-demonstracao.md`.

## Rulings Iniciais (Fase de Planejamento)
- Ruling: Incluir uma 4ª jornada na demonstração (`antonio_67` — Sr. Antônio com boleto adulterado contendo prompt injection + MED Pix) além das 3 sugeridas inicialmente (Carla, Diego, Júlia) — porque com 7 agentes selecionados, o `GuardiaoAgent` ficaria sem exercício na demo oficial se apenas 3 personas fossem executadas — custo baixo de adição (1 cenário + testes determinísticos) e cobre 100% dos 7 agentes na demonstração.
- Ruling: Resolver `DATA_DIR` em `services/rag/src/pandora_rag/config.py` com fallback para o repositório principal quando executado dentro de um git worktree sem cópia local de `services/rag/data` — evita duplicar ~100 MB de textos e embeddings pré-computados no worktree e permite que `pandora-rag demo` use o corpus oficial de 33 fontes reais quando disponível, além de prover um fallback leve em memória com trechos oficiais para CI/ambientes sem Postgres — reversível em 5 linhas de código.
- Ruling: Suportar execução em modo determinístico (`--offline` / sem LLM ativo) e modo completo com `Gateway` (`--llm <chave>`), mantendo os cálculos financeiros e travas de compliance sempre determinísticos — garante reprodutibilidade 100% em testes automatizados (`pytest`) e apresentações sem depender de servidor Ollama/API ativo, enquanto permite demonstrar síntese com LLM real quando disponível.
