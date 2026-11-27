# Plano Ajustado: Modelos Locais + Otimização sobre `PR #116` + Agentes Multimodais (`#73` e `#74`)

- **Classificação ATLAS:** `ATLAS · feature · arquitetura+produto+dados · large → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura`
- **Spec:** [`docs/atlas/2026-11-26-agentes-multimodais/spec.md`](spec.md)
- **ADR:** [`docs/adr/0004-agentes-multimodais-perceiver-quarentena.md`](../../adr/0004-agentes-multimodais-perceiver-quarentena.md)

---

## Tarefas (com Tags de Lane ATLAS)

### Tarefa 1 · `[arch]` Merge de `origin/develop`, Pré-Cache `faster-whisper small` e Refinamento de `workers/ingestion`
- **Arquivos:** `services/rag/{modelos.yaml,pyproject.toml}`, `services/rag/src/pandora_rag/{config.py,cli.py}`, `workers/ingestion/src/pandora_ingestion/{mascara.py,esquema.py,pdf.py,importador.py}`, `workers/ingestion/tests/{test_ingestao.py,test_pdf.py}`.
- **Escopo:** Integrar `origin/develop` resolvendo conflitos em `config.py`, `cli.py` e `pyproject.toml`; registrar `qwen25-vl-7b` (`qwen2.5vl:7b`) em `modelos.yaml`; rodar `uv sync --extra dev` e pré-baixar `faster-whisper small (int8)`; corrigir *over-masking* em `mascara.py`; adicionar reconciliação em centavos e hook `extrator_ocr` em `pdf.py`/`importador.py`.

### Tarefa 2 · `[arch]` Contratos Multimodais (`models.py`), `ArtifactStore`, Codecs (`ITF-25` + `BRCode`) e `ingestao_adapter.py` (2 Estágios)
- **Arquivos:** `services/rag/src/pandora_rag/agents/{models.py,artifact_store.py,codecs_financeiros.py,ingestao_adapter.py}`, `services/rag/tests/test_agents_multimodal_codecs.py`.
- **Escopo:** `ReferenciaMidia` (*pass-by-reference*), `DadosPixBRCode`, `ExtracaoVisualQuarantinada`, `ExtratoDocumentalVLM`, `ArtifactStore` (remoção EXIF + TTL + resolução dupla), codecs `ITF-25` (Módulo 10/11) + `EMV BRCode` (`CRC-16`) + `zxing-cpp`, e adaptador de 2 estágios que descarta leituras PDF incompletas do Estágio 1 em favor de `qwen2.5vl:7b`.

### Tarefa 3 · `[core]` Pipeline de Voz PT-BR (`voz.py`) e `PerceiverNode` em Quarentena (`perceiver.py` com `qwen2.5vl:7b`)
- **Arquivos:** `services/rag/src/pandora_rag/agents/{voz.py,perceiver.py}`, `services/rag/tests/test_agents_voz_perceiver.py`.
- **Escopo:** Decodificação via `PyAV` (`av`), `TranscritorVoz` (`faster-whisper small` PT-BR + backend injetável), normalizador monetário PT-BR, `SintetizadorVoz` (`say -v Luciana` macOS + fallback WAV PCM), `compilar_resumo_falado_tts()`, e `PerceiverAgent` com `qwen2.5vl:7b` em quarentena (`tools=[]`, fallback determinístico offline).

### Tarefa 4 · `[arch]` Integração no `StateGraph` (`graph.py`), Auditoria Cross-Modal (`tools.py`, `specialists.py`) e CLI (`cli.py`)
- **Arquivos:** `services/rag/src/pandora_rag/agents/{tools.py,langgraph_tools.py,specialists.py,graph.py,__init__.py}`, `services/rag/src/pandora_rag/cli.py`.
- **Escopo:** Nó `perceiver_multimodal` condicional a partir de `START`, auditoria cross-modal (valor/banco impresso vs. barras/QR), alerta de reconciliação de extrato no `AnalistaAgent`, auditoria de `resumo_falado_tts` no `ComplianceAgent`, e flags multimodais em `pandora-rag agent` (VLM padrão `qwen25-vl-7b`).

### Tarefa 5 · `[core]` Benchmark Ao Vivo (`#74` 20 Docs + `#73` Voz/Visão/Extrato), Revisão por Lanes ATLAS e Gate 2
- **Arquivos:** `services/rag/src/pandora_rag/agents/eval_multimodal.py`, `services/rag/tests/test_agents_multimodal_graph.py`, `docs/agentes/{06-arquitetura-multimodal.md,README.md,runs/avaliacao_multimodal.json}`, `docs/adr/README.md`.
- **Escopo:** Rodar benchmark ao vivo com `qwen2.5vl:7b` + `qwen2.5:7b` + `faster-whisper small`, comprovar detecção `>= 0,90` (`#74`), bloqueio injection `100%` e latência `p95 <= 12,0 s` (`#73`), executar os 5 revisores (`architect`, `type-design-analyzer`, `code-reviewer`, `python-reviewer`, `security-reviewer`), rodar toda a suíte `pytest` + `ruff` e parar no **Gate 2**.
