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

## Rulings Durante a Execução SDD

- `Ruling: Validar Módulo 11 (exigir_mod11=True) automaticamente apenas em leituras ópticas ITF-25 de 44 dígitos (mantendo dv_geral_mod11_valido sempre calculado para observabilidade)` — `por quê:` preserva 100% da compatibilidade com testes legados de linha digitável manual de 47 dígitos que usam DV10 válido e campo 4 fixo, enquanto impõe rigor total de Módulo 11 em códigos de barras de boletos reais/escaneados — `custo se errado:` baixo (basta passar exigir_mod11=True como padrão se todos os fixtures manuais forem atualizados).

- Ruling: Padronizar `num_ctx=2048` e `max_tokens=220` em `ChatOllama(qwen2.5:7b)` (`llm_provider.py`), `num_ctx=2048` + `num_predict=180` + `max_lado=640` em `perceiver.py`, e `num_ctx=2048` em `ingestao_adapter.py`, além de aquecer `_obter_whisper_model("small")` no `eval_multimodal.py` — porque com `8192/4096` o Ollama despejava `qwen2.5:7b` da memória unificada a cada chamada ao VLM (~4–5s por swap), elevando `p95` para `19,31s`; `ollama ps` confirmou co-residência simultânea em 100% GPU com `2048` — reversível alterando constantes de contexto sem impacto estrutural.
- Ruling: Aplicar `thumbnail((768, 768))` JPEG em `extrair_extrato_vlm_ollama` (`ingestao_adapter.py`) + `max_tokens=160` (`llm_provider.py`) + limite de 3 queries em `executar_busca_evidencias_rag` (`langgraph_tools.py`) + concisão nos prompts dos especialistas (`specialists.py`) — porque `150 dpi` sem redução excedia `num_ctx=2048` (`400 Bad Request` no VLM) e prompts longos elevavam o tempo de `estrategista`/`compliance`/`guardiao` para 15,89s na voz — reversível em 1 constante sem alterar contratos.
- Revisão ATLAS Fase 5 (5 subagentes em paralelo: `architect`, `type-design-analyzer`, `code-reviewer`, `python-reviewer`, `security-reviewer`):
  - Corrigido: corte `queries[:3]` ampliado para `queries[:6]` em `langgraph_tools.py` (evitando perda da Res. BCB 147 MED quando combinado com Estrategista);
  - Corrigido: estado mutável de instância em `GrafoPandora` substituído por `contextvars.ContextVar` + limpeza incondicional de `store_criado` no `finally` (`graph.py`);
  - Corrigido: dupla chamada VLM removida de `PerceiverAgent` (`extrator_ocr` no Estágio 1), desempate seguro no Estágio 2 (`ingestao_adapter.py`, impedindo promoção de `reconciliado=None`), bypass `eh_qr_pix_puro_decodificado` removido (`perceiver.py`), sanitização e truncamento em `documento_ocr` e campos visuais, proteção de mídia corrompida;
  - Corrigido: `ArtifactStore` com `fail-closed` no removedor de EXIF (`PNG`/`JPEG`/`WEBP`), `threading.Lock`, `stat().st_size` pré-leitura, `MAX_ARTEFATO_BYTES=25MB`, validação `artefato_id`;
  - Corrigido: `decodificar_pix_brcode` com redação de CPF/chave/nome no `payload_mascarado`, guarda de `Decimal.is_finite()` / negativo na tag `54` e `with Image.open`/`pymupdf.open` (`codecs_financeiros.py`);
  - Corrigido: `ComplianceAgent.validar` passa `rascunho[:900]` + `pareceres_agentes` ao LLM-as-a-Judge, `OrquestradorAgent.planejar` não faz curto-circuito de idioma quando há artefato suspeito (`specialists.py`).
