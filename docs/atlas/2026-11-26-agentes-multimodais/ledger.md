# Ledger — Agentes Multimodais do PANDORA (`feat/agentes-multimodais`)

- **Classificação ATLAS:** `ATLAS · feature · arquitetura+produto+dados · large → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura`
- **Data de abertura:** 2026-11-26

## Decisões da Fase 2 (Descoberta) e Ajustes de Hardware/Qualidade

- Escopo selecionado: **Pacote Multimodal Completo** em `pandora_rag.agents` (`Visão/Boleto/Pix QR + Voz PT-BR STT/TTS + Extrato PDF em 2 Estágios`) + `ADR-0004`.
- Branch dedicada: **`feat/agentes-multimodais`** (preservando `entrega/prototipo-multiagente-quarto-desafio`).
- **Ruling (Ajuste de Modelo VLM):** Substituído o VLM primário de `gemma3:12b` para **`qwen2.5vl:7b`** (mantendo `gemma3:12b` suportado em `modelos.yaml`) — *por quê:* o host Apple Silicon tem 24 GB de RAM unificada; `qwen2.5vl:7b` (~6,0 GB) + `qwen2.5:7b` (~4,7 GB) permanecem co-residentes sem *cold-swap* de pesos (+4–7 s), protegendo `p95 <= 12 s` (`#73`).
- **Ruling (Otimização sobre PR #116):**
  1. Corrigir *over-masking* em `workers/ingestion/src/pandora_ingestion/mascara.py` para não apagar termos de despesas vitais e apostas (`ALUGUEL`, `LUZ`, `BET`, etc.) mantendo 100% da máscara de nomes reais.
  2. Implementar pipeline PDF em 2 estágios (`pdfplumber` → `qwen2.5vl:7b` `ExtratoDocumentalVLM`) que **descarta** leituras incompletas do `pdf.py` sempre que a reconciliação em centavos falhar (`reconciliado is False`).
