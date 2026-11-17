# Sistema Multiagente do PANDORA: documentação

Índice da documentação do **Primeiro Protótipo Multiagente** do projeto PANDORA (Entregável **RES IA ELD UNB — Turma 2**), implementado em [`services/rag/src/pandora_rag/agents/`](../../services/rag/src/pandora_rag/agents/).

> **Estado desta versão (`agents-v0.1.0`):** Grafo de estado tipado em Python/Pydantic (`GrafoPandora`) coordenando **7 agentes especializados** (`orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador`, `compliance`) integrados diretamente ao RAG híbrido (`BAAI/bge-m3` + `BM25` + `RRF`) e ao mascarador de PII (`RNF01–RNF05`).

## Documentos

| Documento | Conteúdo | Atendimento ao Entregável |
|---|---|---|
| [01-arquitetura](01-arquitetura.md) | Diagrama da arquitetura dos agentes, camadas de isolamento e decisões (`ADR-0001`) | Diagrama da arquitetura dos agentes |
| [02-responsabilidades](02-responsabilidades.md) | Ficha detalhada dos 7 agentes especializados, contratos Pydantic, ferramentas e limites | Descrição das responsabilidades de cada agente |
| [03-fluxo-interacao](03-fluxo-interacao.md) | Protocolo `MensagemAgente`, diagramas de sequência e loop de validação/revisão | Fluxo de interação e colaboração entre os agentes |
| [04-demonstracao](04-demonstracao.md) | Execução ponta a ponta das 4 jornadas reais (`carla_34`, `diego_24`, `julia_31`, `antonio_67`) | Demonstração executável de colaboração completa |

## Como reproduzir a demonstração e os testes

A partir da raiz do repositório:

```bash
# 1. Executar as 4 jornadas demonstrativas completas e exportar traces em Markdown/JSON
cd services/rag
uv run pandora-rag demo --saida-dir ../../docs/agentes/runs

# 2. Executar uma consulta avulsa para qualquer persona (ou modo --offline)
uv run pandora-rag agent \
  "Recebi um boleto no WhatsApp e fiz um Pix para falsa central" \
  --persona antonio_67 \
  --linha-digitavel "34191.09008 61207.951301 70001.234560 8 99990000119800"

# 3. Rodar a suíte automatizada de testes (54 testes passando) e lint
uv run --extra dev pytest tests/ -v
uv run --extra dev ruff check src/pandora_rag/agents/ src/pandora_rag/config.py tests/test_agents_*.py
```

Os artefatos gerados pela demonstração oficial estão versionados em [`runs/demonstracao_multiagente.md`](runs/demonstracao_multiagente.md) e [`runs/demonstracao_multiagente.json`](runs/demonstracao_multiagente.json).
