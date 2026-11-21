#!/bin/sh
# Monta o zip do entregável, autocontido. Uso, na raiz do repositório:
#   sh docs/entregas/02-base-conhecimento-e-prototipo-rag/montar_zip.sh [SAIDA.zip]
set -e
RAIZ=$(git rev-parse --show-toplevel)
E="$RAIZ/docs/entregas/02-base-conhecimento-e-prototipo-rag"
SAIDA=${1:-"$RAIZ/PANDORA-entregavel-RAG.zip"}
T=$(mktemp -d); P="$T/PANDORA-entregavel-RAG"
mkdir -p "$P/base_de_conhecimento" "$P/codigo/training/abstencao" "$P/anexos"

# documentos do entregável (sem scripts de geração)
cp "$E"/README.md "$E"/0*.md "$E"/fontes.md "$P/"
cp -R "$E/diagramas" "$E/demo" "$P/"

# base de conhecimento
(cd "$RAIZ" && uv run --quiet --project services/rag python "$E/gerar_artefatos.py" --chunks "$P/base_de_conhecimento/chunks.jsonl" >/dev/null)
cp "$RAIZ/services/rag/fontes.yaml" "$RAIZ/services/rag/corpus.lock" "$P/base_de_conhecimento/"

# código do protótipo
mkdir -p "$P/codigo/services"
rsync -a --exclude data --exclude checkpoints --exclude .venv --exclude __pycache__ --exclude .pytest_cache --exclude .env \
  "$RAIZ/services/rag" "$P/codigo/services/"
cp "$RAIZ/training/abstencao/limiar.json" "$P/codigo/training/abstencao/"

# anexos: documentação técnica, golden set e registro de testes
cp -R "$RAIZ/docs/rag" "$P/anexos/docs-rag"
mkdir -p "$P/anexos/evals"
rsync -a --exclude runs --exclude __pycache__ "$RAIZ/evals/" "$P/anexos/evals/"

rm -f "$SAIDA"; (cd "$T" && zip -rq "$SAIDA" PANDORA-entregavel-RAG -x '*.DS_Store')
echo "$SAIDA"; unzip -l "$SAIDA" | tail -1
