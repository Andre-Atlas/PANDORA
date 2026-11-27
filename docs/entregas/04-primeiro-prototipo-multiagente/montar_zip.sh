#!/bin/sh
# Monta o pacote .zip autocontido do 4º Entregável (Primeiro Protótipo Multiagente).
# Uso, na raiz do repositório:
#   sh docs/entregas/04-primeiro-prototipo-multiagente/montar_zip.sh [SAIDA.zip]
set -e

RAIZ=$(git rev-parse --show-toplevel)
E="$RAIZ/docs/entregas/04-primeiro-prototipo-multiagente"
SAIDA=${1:-"$RAIZ/PANDORA-entregavel-04-multiagente.zip"}
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

P="$T/PANDORA-entregavel-04-multiagente"
mkdir -p "$P/entregavel" "$P/documentacao/agentes" "$P/documentacao/adr" "$P/codigo/services" "$P/codigo/docs/evidencias/datasets"

# 1. Pasta oficial do entregável 04 (README, scripts, diagramas, evidências da demo)
cp "$E/README.md" "$E/executar_entrega.sh" "$P/entregavel/"
cp -R "$E/diagramas" "$E/demo" "$P/entregavel/"

# 2. Documentação técnica modular dos agentes, revisão humana, arquitetura geral e ADRs
cp "$RAIZ"/docs/agentes/*.md "$P/documentacao/agentes/"
cp -R "$RAIZ/docs/agentes/runs" "$P/documentacao/agentes/"
cp "$RAIZ"/docs/adr/*.md "$P/documentacao/adr/"
cp "$RAIZ/docs/arquitetura-geral.md" "$P/documentacao/"
cp "$RAIZ/README.md" "$P/"

# 3. Código-fonte e testes automatizados do sistema multiagente + RAG + dataset de personas
rsync -a --exclude data --exclude checkpoints --exclude .venv --exclude __pycache__ --exclude .pytest_cache --exclude .env \
  "$RAIZ/services/rag" "$P/codigo/services/"
cp "$RAIZ/docs/evidencias/datasets/amostra_transacoes_sinteticas_personas.csv" \
  "$P/codigo/docs/evidencias/datasets/"

rm -f "$SAIDA"
(cd "$T" && zip -rq "$SAIDA" PANDORA-entregavel-04-multiagente -x '*.DS_Store')
echo "$SAIDA"
unzip -l "$SAIDA" | tail -1
