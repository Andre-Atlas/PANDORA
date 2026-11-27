# 06 · Arquitetura Multimodal dos Agentes PANDORA

> **ADR de Referência:** [ADR-0004: Arquitetura Multimodal em Quarentena (*Perceiver–Executor*)](../../adr/0004-agentes-multimodais-perceiver-quarentena.md)
> **Requisitos Cobertos:** `RF01`, `RF07`, `RF09`, `RNF01–RNF07`, Issues `#73` e `#74`

---

## 1. Visão Geral e Stack Local Otimizada

A extensão multimodal do `GrafoPandora` segue o padrão **Perceiver–Executor** em quarentena, calibrado para co-residência em 24 GB de Memória Unificada (sem *cold-swap*):

1. **VLM de Percepção Visual (`qwen2.5vl:7b`):** especializado em OCR documental, tabelas financeiras, boletos e prints (`modelos.yaml` chave `qwen25-vl-7b`; `gemma3:12b` mantido como alternativa opcional).
2. **LLM de Tool Calling (`qwen2.5:7b`):** mantém os 7 agentes com `bind_tools` nativo (~10,7 GB totais co-residentes com `qwen2.5vl:7b`).
3. **Pass-by-Reference (`ArtifactStore`):** binários ficam em store efêmero (`0o700`, sem EXIF, TTL 15 min) e `EstadoMultiagente` trafega apenas `ReferenciaMidia`.
4. **Decodificação Determinística Antes da Probabilística:** `zxing-cpp` + `ITF-25` (44↔47 dígitos, Módulo 10/11) + `EMV BRCode` (`CRC-16/CCITT-FALSE`) e reconciliação de extratos em centavos rodam em Python puro (`RNF03`).
5. **Voz em Cascata Auditável (`RF09`):** `PyAV` + `faster-whisper (small, int8, PT-BR)` → `GrafoPandora` → `ComplianceAgent` (audita texto e `resumo_falado_tts`) → `Luciana (say)` / WAV PCM.

---

## 2. Reuso, Correção e Descarte sobre `workers/ingestion` (`PR #116`)

| Componente (`workers/ingestion`) | Decisão | Justificativa Técnica |
|---|---|---|
| `esquema.py`, `normalizar.py`, `deduplicar.py`, `ofx.py`, `csv_.py` | **Reaproveitar 100%** | Centavos inteiros, fuso `America/Sao_Paulo`, `Decimal` e deduplicação SHA-256 compatíveis com a API hexagonal. |
| `mascara.py` | **Corrigir *over-masking*** | Expandir `_EMPRESA` para preservar substantivos de despesas vitais e apostas (`ALUGUEL`, `LUZ`, `AGUA`, `BET`, `TIGRINHO`, `CONSIGNADO`, etc.) sem vazar nomes reais de pessoas físicas (`***`). |
| `pdf.py` e `importador.py` | **Estender + Descartar se incompleto** | Adicionar hook `extrator_ocr` sobre `PrecisaDeOcr` e reconciliação em centavos (`reconciliado`, `divergencia_centavos`). Se `pdf.py` falhar ou `reconciliado is False`, `ingestao_adapter.py` **descarta** a leitura incompleta e aciona o Estágio 2 (`qwen2.5vl:7b` `ExtratoDocumentalVLM`), escolhendo o menor `abs(divergencia_centavos)`. |

---

## 3. Fluxo Multimodal Integrado ao `StateGraph`

```mermaid
flowchart TD
    IN["Entrada (Texto, Áudio, Imagem, PDF, Extrato, QR Pix)"] --> ST["ArtifactStore Efêmero (Remove EXIF, TTL 15m)"]
    ST --> CHECK{"Possui mídia ou QR Pix?"}
    CHECK -->|"Não"| O1["1. OrquestradorAgent (planejar)"]
    CHECK -->|"Sim"| PERC["0. PerceiverNode (Quarentena · qwen2.5vl:7b · tools=[])"]
    PERC -->|"Extracao + sanitizar_documento + mascarar"| O1
    O1 --> AN["2. AnalistaAgent (CSV + Extrato 2 Estágios Reconciliado)"]
    AN --> ESP["3. Estrategista / Coach / Guardião (Auditoria Cross-Modal)"]
    ESP --> ED["4. EducadorAgent (RAG Híbrido + Res. BCB 147)"]
    ED --> O2["5. OrquestradorAgent (sintetizar Texto + resumo_falado_tts)"]
    O2 --> CG["6. ComplianceAgent (Audita Texto + resumo_falado_tts)"]
    CG -->|"REPROVADO (<= 1 revisão)"| O2
    CG -->|"APROVADO / Fail-Closed"| TTS["Saída: ResultadoMultiagente + Áudio WAV TTS"]
```


---

## 4. Métricas Ao Vivo Verificadas (Issues `#73` e `#74`)

Fonte versionada: [`runs/avaliacao_multimodal.json`](runs/avaliacao_multimodal.json) (`modo_execucao: "ao_vivo"`, `llm: "qwen25-7b"`, `vlm: "qwen25-vl-7b"`, `STT: faster-whisper small`, `TTS: Luciana`).

| Métrica | Resultado Medido | Meta do Plano | Status |
|---|---|---|---|
| Documentos avaliados (`#74`) | `20` (10 legítimos + 10 adulterados/golpes) | `20` | PASS |
| Taxa de detecção de fraude (`taxa_deteccao_fraude`) | **`1,00` (100%)** | `>= 0,90` | PASS |
| Precisão em documentos legítimos (`precisao_legitimos`) | **`1,00` (100%)** | `>= 0,90` | PASS |
| Citação da Resolução BCB 147/2021 — MED (`taxa_citacao_med_bcb147`) | **`1,00` (100%)** | `>= 0,90` | PASS |
| Bloqueio de *Visual Prompt Injection* (`bloqueio_injection_visual`) | **`1,00` (100%)** | `1,00` | PASS |
| Latência média imagem/PDF (`latencia_media_imagem_pdf_s`) | **`5,6433 s`** | — | PASS |
| Latência P95 imagem/PDF (`latencia_p95_imagem_pdf_s`) | **`6,4568 s`** | `<= 12,0 s` | PASS |
| Roundtrip de voz PT-BR (`voz_roundtrip_ok` / `latencia_voz_s`) | **`true` / `10,0575 s`** | `true` / `<= 12,0 s` | PASS |
| Extrato PDF quebrado (Estágio 1 descartado → Estágio 2 VLM) | **`estagio_2_vlm` · `reconciliado=true` · `0` centavos** | `reconciliado=true` | PASS |

---

## 5. Comandos CLI Multimodais Reprodutíveis

```bash
cd services/rag

# Analisar boleto em imagem ou PDF com PerceiverAgent (qwen2.5vl:7b) + Guardião
uv run pandora-rag agent \
  "Recebi este boleto no WhatsApp, posso pagar?" \
  --imagem /caminho/boleto.png \
  --llm qwen25-7b \
  --vlm qwen25-vl-7b

# Ingerir extrato PDF quebrado/escaneado (Estágio 1 -> Estágio 2 VLM) com persona
uv run pandora-rag agent \
  "Analise meu extrato e me ajude a priorizar as contas" \
  --persona diego_24 \
  --extrato /caminho/extrato.pdf \
  --llm qwen25-7b \
  --vlm qwen25-vl-7b

# Entrada e saída em voz PT-BR (PyAV + faster-whisper small + Luciana WAV auditado)
uv run pandora-rag agent \
  "" \
  --persona carla_34 \
  --audio /caminho/pergunta.wav \
  --saida-audio /tmp/resposta_elpis.wav \
  --llm qwen25-7b
```
