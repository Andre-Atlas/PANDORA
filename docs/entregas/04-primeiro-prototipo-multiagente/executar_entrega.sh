#!/bin/sh
# Script único de execução para validar testes, lint e a demonstração completa do 4º Entregável.
# Uso a partir da raiz do repositório:
#   sh docs/entregas/04-primeiro-prototipo-multiagente/executar_entrega.sh            # modo rápido offline
#   sh docs/entregas/04-primeiro-prototipo-multiagente/executar_entrega.sh --com-llm  # usa Ollama (qwen2.5:7b)
set -e

RAIZ=$(git rev-parse --show-toplevel)
RAG_DIR="$RAIZ/services/rag"
MODO_DEMO="--offline"

if [ "${1:-}" = "--com-llm" ]; then
  MODO_DEMO="--llm qwen25-7b"
fi

echo "============================================================"
echo "PANDORA · Entregável 04: Sistema Multiagente (LangGraph)"
echo "============================================================"

echo "\n[1/3] Rodando suíte completa de testes automatizados (pytest)..."
(cd "$RAG_DIR" && uv run --extra dev pytest tests/ -v)

echo "\n[2/3] Rodando verificação estática de qualidade e lint (ruff)..."
(cd "$RAG_DIR" && uv run --extra dev ruff check src/pandora_rag/agents/ src/pandora_rag/cli.py tests/test_agents_*.py)

echo "\n[3/3] Executando demonstração ponta a ponta das 4 jornadas ($MODO_DEMO)..."
TMP_OUT=$(mktemp -d)
trap 'rm -rf "$TMP_OUT"' EXIT
(cd "$RAG_DIR" && uv run pandora-rag demo $MODO_DEMO --saida-dir "$TMP_OUT")

echo "\n============================================================"
echo "Tudo validado! Principais arquivos da entrega:"
echo "  - Guia executivo:      docs/entregas/04-primeiro-prototipo-multiagente/README.md"
echo "  - Diagramas Mermaid:   docs/entregas/04-primeiro-prototipo-multiagente/diagramas/"
echo "  - Traces reais demo:   docs/entregas/04-primeiro-prototipo-multiagente/demo/"
echo "  - Doc dos 7 agentes:   docs/agentes/README.md (01 a 05)"
echo "  - Arquitetura geral:   docs/arquitetura-geral.md"
echo "  - ADRs formais:        docs/adr/README.md (ADR-0001, ADR-0002, ADR-0003)"
echo "  - Código e testes:     services/rag/src/pandora_rag/agents/ e services/rag/tests/"
echo "============================================================"
