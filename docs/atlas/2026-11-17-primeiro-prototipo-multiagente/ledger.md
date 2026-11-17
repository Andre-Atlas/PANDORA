# Ledger de Decisões — Primeiro Protótipo Multiagente PANDORA

- **Slug:** `2026-11-17-primeiro-prototipo-multiagente`
- **Classificação:** `ATLAS · feature · arquitetura+dados · large → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura`

## Decisões de Descoberta (Alinhadas com o Usuário)
1. **Topologia de 7 Agentes:** Adotar `orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador` e `compliance` (antecipando a arquitetura completa do escopo CBL).
2. **Localização e Stack:** Módulo `services/rag/src/pandora_rag/agents/` em Python + Pydantic puro, reutilizando `Gateway`, `mascarar` (PII), `Retriever` híbrido e `uv`.
3. **Demonstração Executável:** Comandos CLI `pandora-rag agent` e `pandora-rag demo` com registro completo do trace de colaboração em Markdown e JSON.
4. **Documentação Modular:** Diretório `docs/agentes/` com `README.md`, `01-arquitetura.md`, `02-responsabilidades.md`, `03-fluxo-interacao.md` e `04-demonstracao.md`.

## Rulings Durante a Execução
- Ruling: Incluir uma 4ª jornada na demonstração (`antonio_67` — Sr. Antônio com boleto adulterado contendo prompt injection + MED Pix) além das 3 sugeridas inicialmente (Carla, Diego, Júlia) — porque com 7 agentes selecionados, o `GuardiaoAgent` ficaria sem exercício na demo oficial se apenas 3 personas fossem executadas — custo baixo de adição (1 cenário + testes determinísticos) e cobre 100% dos 7 agentes na demonstração.
- Ruling: Resolver `DATA_DIR` em `services/rag/src/pandora_rag/config.py` com fallback para o repositório principal quando executado dentro de um git worktree sem cópia local de `services/rag/data` — evita duplicar ~100 MB de textos e embeddings pré-computados no worktree e permite que `pandora-rag demo` use o corpus oficial de 33 fontes reais quando disponível, além de prover um fallback leve em memória com trechos oficiais para CI/ambientes sem Postgres — reversível em 5 linhas de código.
- Ruling: Suportar execução em modo determinístico (`--offline` / sem LLM ativo) e modo completo com `Gateway` (`--llm <chave>`), mantendo os cálculos financeiros e travas de compliance sempre determinísticos — garante reprodutibilidade 100% em testes automatizados (`pytest`) e apresentações sem depender de servidor Ollama/API ativo, enquanto permite demonstrar síntese com LLM real quando disponível.
- Ruling: Executar Tasks 2, 3 e 4 diretamente nesta sessão (após Task 1 via subagente) seguindo estritamente TDD e reservando subagentes especializados (`code-reviewer`, `security-reviewer`) para a revisão final — evitou estouro do orçamento de 30 invocações com loops de espera e permitiu iterar rapidamente sobre o fallback sem Postgres e remoção de `consulta_usuario` não mascarada da saída JSON (`ResultadoMultiagente`) — totalmente auditável via commits granulares e revisão independente.
- Ruling: Remover `consulta_usuario` bruta de `ResultadoMultiagente` mantendo apenas `consulta_mascarada` — detectado no teste `test_cli_agent_e_demo_executam_com_sucesso` onde a saída `--saida-json` exporia o CPF original caso mantivesse o campo bruto; garante aderência estrita ao RNF01 (0% vazamento de PII em outputs externos).
- Ruling: Em `construir_retriever_padrao()`, testar conectividade Postgres com timeout de 2s antes de instanciar `Embedder` e preferir o cache `BAAI/bge-m3` pré-computado com `MemoryStore` + `BM25` quando `TEXT_DIR` e `.npy` existem localmente — permitiu rodar `pandora-rag demo` no corpus oficial completo de 33 fontes sem exigir container Postgres ativo.
- Ruling: Em `EducadorAgent.executar()`, garantir ao menos 1 chunk de topo por query antes de completar com os melhores escores globais — evitou que uma única query jurídica dominasse todas as citações quando o `GuardiaoAgent` e o `EstrategistaAgent` solicitam pesquisas simultâneas (garantindo a citação [4] da Res. BCB 147/2021 na Jornada 4).

## Progresso das Tarefas
- [x] **Task 1 `[arch]`:** Contratos Pydantic (`models.py`) e ferramentas determinísticas (`tools.py`) — commit `2317443`
- [x] **Task 2 `[core]`:** Implementação dos 7 agentes especializados (`specialists.py`) — commit `784abb1`
- [x] **Task 3 `[arch]`:** Grafo multiagente (`graph.py`), cenários (`scenarios.py`), fallback `DATA_DIR` (`config.py`) e CLI (`cli.py`) — commit `23f1d24` + `4b912c8`
- [x] **Task 4 `[core]`:** Execução real da demo (`docs/agentes/runs/`), documentação completa em `docs/agentes/` e atualização do `README.md`

