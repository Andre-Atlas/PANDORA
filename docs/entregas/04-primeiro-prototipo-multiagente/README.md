# Entregável 04: Primeiro Protótipo Multiagente (`LangGraph` + Tool Calling)

**Quarto Desafio · RES IA ELD UNB · Turma 2 · PANDORA**  
Branch da entrega: `entrega/prototipo-multiagente-quarto-desafio`

---

## 1. O que foi feito

Construímos e validamos o **Primeiro Protótipo Multiagente do PANDORA** (Camada 4 da [arquitetura geral em 6 camadas](../../arquitetura-geral.md)) integrando **7 agentes especializados colaborativos** ao serviço de RAG híbrido (`pandora_rag`), atendendo integralmente a todos os critérios do entregável:

- **Agentes Especializados (7 agentes com `System Prompt` próprio e `@tool` nativa):** `orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador` e `compliance` — cobrindo os papéis de *Research*, *Analysis*, *Validation* e *Communication* com raciocínio via **`qwen2.5:7b` (Ollama local)** por padrão (`langchain-ollama`) e suporte a Anthropic (`langchain-anthropic`).
- **Orquestração Declarativa com `LangGraph` (`StateGraph(EstadoMultiagente)`):** grafo compilado com 10 nós, arestas condicionais (`add_conditional_edges`) e ciclo de revisão `compliance -> preparar_revisao -> orquestrador_sintetizar`, registrando cada handoff e *tool call* em `trace: list[MensagemAgente]`.
- **Segurança, Privacidade e Conformidade (`RNF01`–`RNF05`) validadas em Revisão Humana (`05-revisao-humana.md`):**
  - **LGPD (`RNF01`):** mascaramento automático de PII (`CPF`, `CNPJ`, telefone, e-mail, cartão, chave Pix) na entrada, saída e antes de qualquer chamada ao LLM.
  - **CVM (`RNF02`):** detecção direta e indireta de pedidos de investimento + veto semântico do *Compliance Judge* + supressão do texto livre do LLM quando a trava CVM está ativa, entregando **Recusa Educativa** (Res. CVM 19 e 20/2021) com os 3 critérios objetivos.
  - **Exatidão Matemática (`RNF03`):** 100% dos cálculos (despesas vitais, folga real, Avalanche vs. Bola de Neve, perda líquida em *bets* e Módulo 10 FEBRABAN) rodam exclusivamente nas `@tool`s Python determinísticas, com taxas SGS datadas (`ref. fev/2026`).
  - **Anti-Alucinação (`RNF04`):** até 4 citações oficiais `[n]` sem preâmbulos nem cláusulas revogatórias, e portão de abstenção calibrado por domínio léxico e score também no corpus real (`corpus_local_bge_m3` e `corpus_local_bm25_hash`).
  - **Defesa Anti-*Prompt Injection* (`RNF05`) e Protocolo de Crise:** o texto de `documento_ocr` nunca entra no prompt do LLM (é isolado dentro da tool do `GuardiaoAgent`); e diante de ideação suicida direta ou indireta ou sinal de crise do LLM, o `CVV 188`, `CAPS AD` e `Jogadores Anônimos` abrem a resposta com o LLM bloqueado.
- **Execução Simples & Suíte Completa (`65 testes passing`):** script único [`executar_entrega.sh`](executar_entrega.sh), gerador de pacote autocontido [`montar_zip.sh`](montar_zip.sh) e comandos `pandora-rag demo` / `pandora-rag agent`.

---

## 2. Como funciona (passo a passo)

1. **Triagem, Idioma e Roteamento (`OrquestradorAgent` · `tool_classificar_roteamento`):** recebe a consulta, mascara PII (`mascarar()`), verifica idioma português e combina a classificação do `qwen2.5:7b` com sensores regex `\b` *defense-in-depth* (evitando acionar `Estrategista` sem dívidas reais ou `Coach` sem apostas).
2. **Raio-X Determinístico (`AnalistaAgent` · `tool_calcular_raio_x_financeiro`):** lê o extrato da persona (`amostra_transacoes_sinteticas_personas.csv`), apura renda, despesas vitais estimadas, folga líquida e compara juros contra o Banco Central (SGS `22022`, `25467`, `432`, `12`, `433`, ref. `fev/2026`).
3. **Especialistas de Domínio (condicionais no `StateGraph`):**
   - `EstrategistaAgent` (`tool_simular_reestruturacao_dividas`): blinda 100% das despesas vitais, compara Avalanche vs. Bola de Neve e verifica o teto da Lei 14.690/2023.
   - `CoachAgent` (`tool_analisar_compulsao_apostas`): apura perda líquida real em apostas (`MCC 7995`), madrugada (`23h–06h`) e impacto tangível sem moralismo.
   - `GuardiaoAgent` (`tool_inspecionar_fraude_e_boleto`): sanitiza `documento_ocr` fora do prompt do LLM, audita linha digitável FEBRABAN e gera roteiro do **MED do Pix (80 dias, Res. BCB 147/2021)**.
4. **Pesquisa Normativa (`EducadorAgent` · `tool_buscar_evidencias_rag`):** executa busca híbrida (`bge-m3` + `BM25` + `RRF`), filtra ruído de cabeçalhos e devolve até 4 citações `[1]..[k]` (ou aciona abstenção `RNF04`).
5. **Síntese Adaptada (`OrquestradorAgent`):** compila os números exatos e citações no tom da persona (bloqueando texto livre do LLM quando houver crise, trava CVM ou revisão).
6. **Validação Final *Fail-Closed* (`ComplianceAgent` · `tool_auditar_invariantes_compliance`):** combina auditoria semântica (*LLM-as-a-Judge*) com invariantes duros (Crise `CVV 188`, Trava CVM, Antifraude explícito, Citações `[n]`, Julgamento Moral e Zero PII). Em reprovação, aciona `preparar_revisao -> orquestrador_sintetizar`; em falha persistente, entra no nó `fail_closed`.

---

## 3. Mapa Rápido dos Arquivos da Entrega

### Pasta consolidada desta entrega (`docs/entregas/04-primeiro-prototipo-multiagente/`)

| Caminho | Conteúdo |
|---|---|
| [`README.md`](README.md) | Este guia executivo do entregável (o que foi feito, como funciona, resultados e comandos) |
| [`executar_entrega.sh`](executar_entrega.sh) | Script em 1 comando que roda os **65 testes (`pytest`)**, o **lint (`ruff`)** e a **demo completa** |
| [`montar_zip.sh`](montar_zip.sh) | Script que empacota o entregável completo em `PANDORA-entregavel-04-multiagente.zip` |
| [`diagramas/arquitetura.mmd`](diagramas/arquitetura.mmd) | Diagrama Mermaid do `StateGraph` (`LangGraph`), `@tool`s e camadas de segurança |
| [`diagramas/fluxo-colaboracao.mmd`](diagramas/fluxo-colaboracao.mmd) | Diagrama de sequência com *Tool Calling* e ciclo de revisão do *Compliance Judge* |
| [`demo/demonstracao_multiagente.md`](demo/demonstracao_multiagente.md) | Trace completo legível das 4 jornadas executadas com **`qwen2.5:7b` + `corpus_local_bge_m3`** |
| [`demo/demonstracao_multiagente.json`](demo/demonstracao_multiagente.json) | Saída JSON estruturada com estado, pareceres, *tool calls*, veredito e mensagens |
| [`demo/abstencao-fora-de-dominio.json`](demo/abstencao-fora-de-dominio.json) | Prova executável do portão de abstenção (`RNF04`) fora de domínio |

### Documentação técnica, arquitetura geral e código-fonte

| Área | Caminho | Descrição |
|---|---|---|
| **Documentação dos Agentes** | [`docs/agentes/README.md`](../../agentes/README.md) | Capítulos [01-arquitetura](../../agentes/01-arquitetura.md), [02-responsabilidades](../../agentes/02-responsabilidades.md), [03-fluxo-interacao](../../agentes/03-fluxo-interacao.md), [04-demonstracao](../../agentes/04-demonstracao.md) e [05-revisao-humana](../../agentes/05-revisao-humana.md) |
| **Arquitetura Geral do Sistema** | [`docs/arquitetura-geral.md`](../../arquitetura-geral.md) | Visão canônica em 6 camadas ligando Frontend, API Hexagonal, RAG, LangGraph, ML e Infra |
| **Decisões Arquiteturais** | [`docs/adr/README.md`](../../adr/README.md) | `ADR-0001` (estado tipado), `ADR-0002` (`LangGraph` + Tool Calling) e `ADR-0003` (6 camadas) |
| **Código dos Agentes** | [`services/rag/src/pandora_rag/agents/`](../../../services/rag/src/pandora_rag/agents/) | `models.py`, `llm_provider.py`, `langgraph_tools.py`, `personas_data.py`, `tools.py`, `specialists.py`, `graph.py`, `scenarios.py` |
| **CLI e Testes** | [`services/rag/tests/`](../../../services/rag/tests/) | `test_agents_tools.py`, `test_agents_specialists.py`, `test_agents_graph.py` + suíte RAG (65 testes) |

---

## 4. Resumo da Demonstração Real (`corpus_local_bge_m3` + `qwen2.5:7b`)

| Jornada | Persona | Agentes Acionados | Interações | Tool Calls | Destaques Verificados |
|---|---|---|---:|---:|---|
| **1** | **Carla Mendes (`carla_34`)** | `orquestrador` → `analista` → `estrategista` → `educador` → `compliance` | 6 | 5 | Despesas vitais `R$ 2.100,00` blindadas · SGS `22022` (`448,0%` vs `435,9%` ref. fev/2026) · 3 citações `[1][2][3]` |
| **2** | **Diego Oliveira (`diego_24`)** | `orquestrador` → `analista` → `coach` → `educador` → `compliance` | 6 | 5 | Perda líquida `R$ 700,00` (`62,5%`) · **Protocolo de Crise (`CVV 188`, CAPS AD, JA)** sem texto livre do LLM · Lei 14.790 |
| **3** | **Júlia Santos (`julia_31`)** | `orquestrador` → `analista` → `educador` → `compliance` | 5 | 4 | **Trava CVM (`Res. 19/2021`)** sem recomendação de ativo/CDB e sem seções espúrias · Meta `R$ 16.800,00` |
| **4** | **Sr. Antônio (`antonio_67`)** | `orquestrador` → `analista` → `estrategista` → `guardiao` → `educador` → `compliance` | 7 | 6 | **OCR isolado fora do prompt LLM** · Boleto reprovado · **MED Pix (Res. BCB 147 Art. 39-B)** |

---

## 5. Como Rodar de Forma Simples (1 Comando, Testes e Pacote `.zip`)

Pré-requisito: [`uv`](https://docs.astral.sh/uv/) instalado. Para o modo com LLM local (`qwen2.5:7b`), ter o Ollama rodando com `ollama pull qwen2.5:7b`.

```bash
# Opção rápida — 1 comando na raiz do repositório (roda 65 testes + lint + demo offline):
sh docs/entregas/04-primeiro-prototipo-multiagente/executar_entrega.sh

# Mesma validação executando a demo com Ollama local (qwen2.5:7b):
sh docs/entregas/04-primeiro-prototipo-multiagente/executar_entrega.sh --com-llm

# Gerar arquivo .zip autocontido da entrega para envio:
sh docs/entregas/04-primeiro-prototipo-multiagente/montar_zip.sh
```

Ou executando comandos individuais em `services/rag/`:

```bash
cd services/rag

# Suíte completa de testes automatizados (65 testes: agentes + guardrails + RAG)
uv run --extra dev pytest tests/ -v

# Apenas os testes do sistema multiagente (28 testes)
uv run --extra dev pytest tests/test_agents_tools.py tests/test_agents_specialists.py tests/test_agents_graph.py -v

# Lint (ruff)
uv run --extra dev ruff check src/pandora_rag/agents/ src/pandora_rag/cli.py tests/test_agents_*.py

# Demonstração completa (padrão qwen25-7b ou --offline sem LLM/Postgres)
uv run pandora-rag demo --saida-dir ../../docs/entregas/04-primeiro-prototipo-multiagente/demo
uv run pandora-rag demo --offline

# Consulta avulsa em JSON auditável
uv run pandora-rag agent \
  "Meu CPF 123.456.789-00. Estou no rotativo do cartão e a luz atrasou." \
  --persona carla_34 \
  --saida-json
```
