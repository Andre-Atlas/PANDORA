# ADR-0004: Arquitetura Multimodal em Quarentena (*Perceiver–Executor*) e Otimização sobre `workers/ingestion`

- **Status:** Proposto (Gate 1)
- **Data:** 2026-11-26
- **Decisores:** Equipe PANDORA (RES IA ELD UNB — Turma 2)
- **Estende:** [ADR-0002](0002-orquestracao-langgraph-tool-calling.md) e [ADR-0003](0003-arquitetura-geral-sistema-pandora.md)
- **Contexto Relacionado:** `RF01`, `RF07`, `RF09`, `RNF01–RNF07` (`docs/escopo/04-requisitos-4-graus.md`), Issues `#73`, `#74`, `#57` e `#66` (`PR #116`)

---

## 1. Contexto

O sistema multiagente do PANDORA (`pandora_rag.agents`) opera hoje via `LangGraph` (`StateGraph(EstadoMultiagente)`) com 7 agentes especializados e `@tool` calling nativo sobre entradas textuais (`consulta_usuario`, `documento_ocr`, `linha_digitavel`). Para cumprir integralmente os requisitos de Grau 1/2 e as issues `#73` (Agente Multimodal com OCR, visão e voz) e `#74` (avaliação de boletos e roteiro do MED Pix) dentro do hardware local (Mac Apple Silicon `arm64`, 24 GB de Memória Unificada) e do limite `p95 <= 12 s` (`RNF06`), o grafo precisa suportar:

1. **Visão e Antifraude Documental (`RF07`, `RNF05`):** fotos/prints de boletos, QR Codes Pix e conversas suspeitas (WhatsApp/falsa central), validando código de barras `ITF-25` (44↔47 dígitos, Módulo 10 e Módulo 11), `EMV BRCode` (`CRC-16/CCITT-FALSE`), divergência cross-modal (logotipo/valor impresso vs. código codificado) e defesa contra *Visual/Typographic Prompt Injection*;
2. **Extratos e Faturas em OFX/CSV/PDF (`RF01`, `RNF03`):** o `PR #116` (branch `origin/dev/luana`, mergeado em `origin/develop`) introduziu `workers/ingestion` (`pandora_ingestion`), mas apresenta dois gargalos reais para o sistema: (a) *over-masking* em `mascara.py` que apaga palavras vitais (`"PIX ENVIADO ALUGUEL APARTAMENTO"` → `"PIX ENVIADO ***"`), e (b) descarte silencioso de linhas quebradas em `pdf.py` sem reconciliação de saldo;
3. **Voz PT-BR Acessível (`RF09`, `RNF07`):** entrada por áudio (`STT`) e saída falada (`TTS`) auditada para pessoas com baixa visão ou sobrecarga cognitiva (`Sr. Antônio`).

---

## 2. Alternativas Consideradas

### Alternativa A — Transformar Todos os 7 Agentes em VLMs Monolíticos ou usar `gemma3:12b` + `qwen2.5:7b`
Enviar imagens/áudios diretamente no `EstadoMultiagente` ou usar `gemma3:12b` (~8,2 GB) junto de `qwen2.5:7b` (~4,7 GB) + `BAAI/bge-m3` (~2,2 GB) + `Whisper` (~0,6 GB) em 24 GB RAM.
- **Prós:** Menor número de modelos distintos ou aproveitamento de `gemma3:12b` já listado em `modelos.yaml`.
- **Contras:** `base64` no estado gera *State Bloat*; VLM com `@tool`s fica vulnerável a *Visual Prompt Injection*; além disso, `gemma3:12b` + `qwen2.5:7b` + embeddings somam ~15,7 GB e provocam *cold-swap* de pesos na memória unificada (+4 a 7 s por turno), ameaçando o teto `p95 <= 12 s` da `#73`.
- **Veredito:** Rejeitada como padrão primário (mantendo `gemma3:12b` suportado opcionalmente em `modelos.yaml`).

### Alternativa B — RAG Visual Multivetorial (`ColPali` / `ColQwen`) + Voz *Native Speech-to-Speech* (`S2S`)
- **Prós:** Latência conversacional baixa em S2S.
- **Contras:** `ColPali` multiplica em 10x–50x o armazenamento fora do `pgvector` HNSW atual; modelos S2S operam como caixa-preta de áudio antes da auditoria de `ComplianceAgent` (`RNF01`, `RNF02`, `RNF03`).
- **Veredito:** Rejeitada.

### Alternativa C — *Perceiver–Executor* em Quarentena (`qwen2.5vl:7b` + `qwen2.5:7b` co-residentes) + Pipeline PDF em 2 Estágios com Descarte + Voz em Cascata Auditável (Escolhida)
1. **Co-residência Ótima em 24 GB (`qwen2.5vl:7b` ~6,0 GB + `qwen2.5:7b` ~4,7 GB = ~10,7 GB):** zero *cold-swap* entre percepção visual e raciocínio de ferramentas, com `qwen2.5vl:7b` especializado em documentos, tabelas e boletos.
2. **Armazenamento *Pass-by-Reference* (`ArtifactStore`):** mídias brutas ficam em store efêmero local (`0o700`, remoção EXIF, TTL); `EstadoMultiagente` trafega apenas `ReferenciaMidia`.
3. **Nó `perceiver_multimodal` em Quarentena (`tools=[]`, `externo=False`):**
   - Decodificadores exatos (`zxing-cpp` para `ITF-25` e `EMV BRCode` Pix);
   - `qwen2.5vl:7b` via Ollama com saída estruturada fechada (`ExtracaoVisualQuarantinada`) e zero ferramentas (*Dual-LLM* / *CaMeL*);
   - **Pipeline Híbrido de Extratos PDF em 2 Estágios:** Estágio 1 (`pandora_ingestion.importador.ler`, após corrigir o *over-masking* de despesas vitais/bets em `mascara.py` e adicionar reconciliação contábil em centavos em `pdf.py`); caso `pdf.py` falhe (`PrecisaDeOcr`/`ArquivoIlegivel`) **ou** `reconciliado is False`, descarta a leitura falha do Estágio 1 e aciona o **Estágio 2 Multimodal (`PyMuPDF` 200 DPI + `qwen2.5vl:7b` `ExtratoDocumentalVLM` + `normalizar.centavos` + `mascara.mascarar`)**, escolhendo o resultado com menor `abs(divergencia_centavos)`;
   - **Voz PT-BR Local:** decodificação via `PyAV` (`av`) em memória + `faster-whisper` (`small`, `int8`, PT-BR) + normalizador monetário.
4. **Auditoria Cross-Modal e TTS Pós-Compliance:** `GuardiaoAgent` confronta leitura visual vs. código de barras/QR; `ComplianceAgent` audita `rascunho_resposta` e `resumo_falado_tts` antes de sintetizar o áudio WAV (`say -v Luciana` no macOS / fallback PCM).

---

## 3. Decisão

Adotar a **Alternativa C**, mantendo compatibilidade 100% retroativa com chamadas textuais puras e preservando intactos os testes originais de `workers/ingestion` e `services/rag`.

---

## 4. Consequências

- **Positivas:** Co-residência sem *swap* em 24 GB RAM; eliminação do *over-masking* destrutivo sobre gastos vitais e bets; descarte automático de leituras PDF incompletas sem inventar valores; conformidade com `RNF01–RNF07`.
- **Riscos e Mitigações:** Indisponibilidade de Ollama/rede em CI mitigada com fallback determinístico offline e backend injetável para Whisper/TTS.
