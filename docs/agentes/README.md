# Sistema Multiagente do PANDORA: documentação

Índice da documentação técnica do **Primeiro Protótipo Multiagente** do projeto PANDORA (Entregável **RES IA ELD UNB — Turma 2**), implementado em [`services/rag/src/pandora_rag/agents/`](../../services/rag/src/pandora_rag/agents/).

> **Visão executiva do entregável (pasta padronizada):** [`docs/entregas/04-primeiro-prototipo-multiagente/README.md`](../entregas/04-primeiro-prototipo-multiagente/README.md) — explica o que foi feito, como funciona, mapa de pastas, diagramas e evidências executáveis.

> **Estado desta versão (`agents-v0.2.0`):** `StateGraph(EstadoMultiagente)` compilado com **`LangGraph`** coordenando **7 agentes especializados** (`orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `compliance`) dotados de `System Prompt` próprio e **Tool Calling nativo (`@tool` + `bind_tools`)** via **`qwen2.5:7b` (Ollama local)** / Anthropic, integrados ao RAG híbrido (`BAAI/bge-m3` + `BM25` + `RRF`) e ao mascarador de PII (`RNF01–RNF05`).

## Documentos

| Documento | Conteúdo | Atendimento ao Entregável |
|---|---|---|
| [01-arquitetura](01-arquitetura.md) | Diagrama do `StateGraph` (`LangGraph`), camadas de isolamento e decisões (`ADR-0001`, `ADR-0002`, `ADR-0003`) | Diagrama da arquitetura dos agentes |
| [02-responsabilidades](02-responsabilidades.md) | Ficha detalhada dos 7 agentes, `System Prompts`, `@tool`s nativas e limites | Descrição das responsabilidades de cada agente |
| [03-fluxo-interacao](03-fluxo-interacao.md) | Protocolo `MensagemAgente`, `tool_calls` e loop de revisão com *LLM-as-a-Judge* | Fluxo de interação e colaboração entre os agentes |
| [04-demonstracao](04-demonstracao.md) | Execução ponta a ponta das 4 jornadas reais com `qwen2.5:7b` (`carla_34`, `diego_24`, `julia_31`, `antonio_67`) | Demonstração executável de colaboração completa |
| [05-revisao-humana](05-revisao-humana.md) | Auditoria adversarial humana e resolução pós-revisão dos guardrails Crise/CVM/Antifraude/RNF04 | Validação humana, sondagens e casos-limite |

## Como reproduzir a demonstração e os testes

A partir da raiz do repositório:

```bash
# Atalho em 1 comando (testes + lint + demonstração offline):
sh docs/entregas/04-primeiro-prototipo-multiagente/executar_entrega.sh

# Ou etapa por etapa em services/rag:
cd services/rag

# 1. Executar as 4 jornadas demonstrativas completas (LangGraph + qwen2.5:7b) e exportar traces
uv run pandora-rag demo --saida-dir ../../docs/agentes/runs

# 2. Executar uma consulta avulsa para qualquer persona (ou modo --offline)
uv run pandora-rag agent \
  "Recebi um boleto no WhatsApp e fiz um Pix para falsa central" \
  --persona antonio_67 \
  --linha-digitavel "34191.09008 61207.951301 70001.234560 8 99990000119800"

# 3. Rodar a suíte automatizada de testes (65 testes passando) e lint
uv run --extra dev pytest tests/ -v
uv run --extra dev ruff check src/pandora_rag/agents/ src/pandora_rag/cli.py tests/test_agents_*.py
```

Os artefatos gerados pela demonstração oficial estão versionados em [`runs/demonstracao_multiagente.md`](runs/demonstracao_multiagente.md) e [`runs/demonstracao_multiagente.json`](runs/demonstracao_multiagente.json).
