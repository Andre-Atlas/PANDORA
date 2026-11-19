# Entregável 04: Primeiro Protótipo Multiagente

**Quarto Desafio · RES IA ELD UNB · Turma 2 · PANDORA**  
Branch da entrega: `entrega/prototipo-multiagente-quarto-desafio`

---

## 1. O que foi feito

Construímos o **Primeiro Protótipo Multiagente do PANDORA** integrando **7 agentes especializados colaborativos** ao serviço de RAG híbrido (`pandora_rag`), atendendo integralmente aos requisitos do entregável:

- **Agentes Especializados (7 agentes, superando o mínimo de 2):** `orquestrador`, `analista`, `estrategista`, `coach`, `guardiao`, `educador` e `compliance` — cobrindo os papéis de *Research*, *Analysis*, *Validation* e *Communication*.
- **Orquestração Auditável em Grafo de Estado Tipado (`GrafoPandora`):** cada interação ou handoff entre agentes é gravado em `trace: list[MensagemAgente]` com ordem, origem, destino, tipo e dados-chave.
- **Segurança e Conformidade por Construção (`RNF01`–`RNF05`):**
  - **LGPD (`RNF01`):** mascaramento automático de PII (CPF, CNPJ, telefone, e-mail, cartão, chave Pix UUID) na entrada, nas consultas RAG, nos trechos citados e antes de chamadas externas.
  - **CVM (`RNF02`):** bloqueio de recomendações específicas de ações/CDBs/ativos com **Recusa Educativa** (Res. CVM 19 e 20/2021) ensinando os 3 critérios objetivos (Liquidez D+0, Tesouro/FGC e Pós-fixado Selic/CDI).
  - **Exatidão Matemática (`RNF03`):** 100% dos cálculos financeiros (Mínimo Existencial, Avalanche vs. Bola de Neve, perda líquida em *bets* e Módulo 10 FEBRABAN) rodam em funções Python determinísticas, sem aritmética livre no LLM.
  - **Anti-Alucinação (`RNF04`):** citações numeradas `[n]` vinculadas às 33 fontes oficiais (`BAAI/bge-m3` + `BM25` + `RRF`) e portão de abstenção para perguntas fora de domínio.
  - **Defesa Anti-*Prompt Injection* (`RNF05`) e Protocolo de Crise:** isolamento estrutural de textos OCR de boletos contra injeção (linha, multi-linha e caracteres invisíveis) e disparo obrigatório de `CVV 188`, `CAPS AD` e `Jogadores Anônimos` em sofrimento agudo.
- **CLI Executável + Demonstração Real:** comandos `pandora-rag demo` (4 jornadas completas das personas) e `pandora-rag agent` (consulta avulsa), com 58 testes automatizados passando.

---

## 2. Como funciona (passo a passo)

1. **Entrada e Triagem (`OrquestradorAgent`):** recebe a consulta, mascara dados pessoais (`mascarar()`), classifica as intenções (`dividas`, `bets`, `fraude`, `cvm`, `crise`, `educacao`) e monta a rota condicional de agentes.
2. **Raio-X Determinístico (`AnalistaAgent`):** lê o histórico transacional da persona (`amostra_transacoes_sinteticas_personas.csv`), apura renda, **Mínimo Existencial**, folga líquida e compara taxas contra as séries oficiais do Banco Central (SGS `22022` e `25467`).
3. **Especialistas de Domínio (execução condicional):**
   - `EstrategistaAgent`: blinda 100% do Mínimo Existencial, prioriza contas vitais em atraso, compara **Avalanche** vs. **Bola de Neve** e verifica o teto da Lei 14.690/2023.
   - `CoachAgent`: detecta apostas (`MCC 7995` / `.bet.br`), calcula perda líquida real e concentração noturna (`23h–06h`) e traduz o impacto em custo de oportunidade tangível (ex.: tanques de gasolina) com sugestão de *cooling-off* (24h–48h).
   - `GuardiaoAgent`: sanitiza texto OCR contra *prompt injection*, valida os 47 dígitos FEBRABAN (Módulo 10, banco alegado e beneficiário PF) e monta o roteiro do **MED do Pix (80 dias)**.
4. **Pesquisa Normativa (`EducadorAgent` — *Research Agent*):** recebe as sub-consultas geradas pelos especialistas, busca no RAG híbrido, aplica o portão de abstenção e devolve evidências numeradas `[1]..[k]`.
5. **Síntese Adaptada (`OrquestradorAgent` — *Communication Agent*):** compila os números exatos e as citações no tom adequado à persona (`acolhedor_simples`, `parceiro_sem_julgamento`, `acessivel_idoso`, `educativo_calmo`).
6. **Validação Final *Fail-Closed* (`ComplianceAgent` — *Validation Agent*):** audita os 4 invariantes (Protocolo de Crise `CVV 188`, Trava CVM, Consistência de Citações `[n]` e Zero PII). Se reprovar o rascunho, dispara ciclo de revisão automática no `OrquestradorAgent`; se ainda reprovar, aplica resposta segura *fail-closed*.

---

## 3. Mapa Rápido das Pastas e Documentos

### Pasta desta entrega (`docs/entregas/04-primeiro-prototipo-multiagente/`)

| Caminho | Conteúdo |
|---|---|
| [`README.md`](README.md) | Este guia consolidado do entregável (o que foi feito, como funciona, resultados e comandos) |
| [`diagramas/arquitetura.mmd`](diagramas/arquitetura.mmd) | Diagrama Mermaid da arquitetura dos 7 agentes e camadas de segurança |
| [`diagramas/fluxo-colaboracao.mmd`](diagramas/fluxo-colaboracao.mmd) | Diagrama de sequência da colaboração, handoffs e loop de revisão |
| [`demo/demonstracao_multiagente.md`](demo/demonstracao_multiagente.md) | Trace completo legível das 4 jornadas reais executadas sobre `corpus_local_bge_m3` |
| [`demo/demonstracao_multiagente.json`](demo/demonstracao_multiagente.json) | Saída estruturada em JSON com estado, evidências, veredito e mensagens de cada jornada |
| [`demo/abstencao-fora-de-dominio.json`](demo/abstencao-fora-de-dominio.json) | Prova executável do portão de abstenção (`RNF04`) em consulta fora de domínio |

### Documentação técnica detalhada e código-fonte

| Área | Caminho | Descrição |
|---|---|---|
| **Documentação dos Agentes** | [`docs/agentes/README.md`](../../agentes/README.md) | Capítulos dedicados: [01-arquitetura](../../agentes/01-arquitetura.md), [02-responsabilidades](../../agentes/02-responsabilidades.md), [03-fluxo-interacao](../../agentes/03-fluxo-interacao.md), [04-demonstracao](../../agentes/04-demonstracao.md) |
| **Decisão Arquitetural** | [`docs/adr/0001-arquitetura-multiagente-pandora.md`](../../adr/0001-arquitetura-multiagente-pandora.md) | ADR formal justificando o grafo de estado tipado em `pandora_rag.agents` |
| **Código dos Agentes** | [`services/rag/src/pandora_rag/agents/`](../../../services/rag/src/pandora_rag/agents/) | `models.py`, `personas_data.py`, `tools.py`, `specialists.py`, `graph.py`, `scenarios.py` |
| **CLI** | [`services/rag/src/pandora_rag/cli.py`](../../../services/rag/src/pandora_rag/cli.py) | Comandos `pandora-rag demo` e `pandora-rag agent` |
| **Testes Automatizados** | [`services/rag/tests/`](../../../services/rag/tests/) | `test_agents_tools.py`, `test_agents_specialists.py`, `test_agents_graph.py` + suíte RAG |

---

## 4. Resumo da Demonstração Real (`corpus_local_bge_m3`)

| Jornada | Persona | Agentes Acionados | Interações | Destaques Verificados |
|---|---|---|---|---|
| **1** | **Carla Mendes (`carla_34`)** | `orquestrador` → `analista` → `estrategista` → `educador` → `compliance` | 6 | Mínimo Existencial `R$ 2.100,00` blindado · SGS `22022` · Lei 14.181, Lei 14.690 e CPC art. 833 `[1][2][3]` |
| **2** | **Diego Oliveira (`diego_24`)** | `orquestrador` → `analista` → `coach` → `educador` → `compliance` | 6 | Perda líquida `R$ 700,00` (62,5%) · 10 tanques de gasolina · **Protocolo de Crise (`CVV 188`, CAPS AD, JA)** · Lei 14.790 |
| **3** | **Júlia Santos (`julia_31`)** | `orquestrador` → `analista` → `educador` → `compliance` | 5 | **Trava CVM (Res. 19/2021)** · Recusa Educativa com 3 critérios objetivos (Liquidez D+0, Tesouro/FGC, Selic/CDI) |
| **4** | **Sr. Antônio (`antonio_67`)** | `orquestrador` → `analista` → `estrategista` → `guardiao` → `educador` → `compliance` | 7 | **Anti-Injection neutralizado** · Boleto reprovado (DV inválido, banco `341` ≠ `001`, PF) · **MED Pix (Res. BCB 147)** |

---

## 5. Como Rodar a Demonstração e os Testes

Pré-requisito: `uv` instalado (Python `3.12` gerenciado automaticamente).

```bash
cd services/rag

# 1. Rodar toda a suíte de testes automatizados (58 testes)
uv run --extra dev pytest tests/ -v

# 2. Rodar apenas os testes do sistema multiagente (21 testes)
uv run --extra dev pytest tests/test_agents_tools.py tests/test_agents_specialists.py tests/test_agents_graph.py -v

# 3. Rodar lint (ruff) nos módulos multiagente
uv run --extra dev ruff check src/pandora_rag/agents/ src/pandora_rag/cli.py src/pandora_rag/config.py src/pandora_rag/generate/pii.py src/pandora_rag/index/store.py tests/test_agents_*.py

# 4. Executar a demonstração completa das 4 jornadas (gera Markdown + JSON)
uv run pandora-rag demo --saida-dir ../../docs/entregas/04-primeiro-prototipo-multiagente/demo

# 5. Executar a demonstração em modo 100% offline (sem Postgres, sem GPU e sem LLM externo)
uv run pandora-rag demo --offline

# 6. Executar uma consulta avulsa com inspeção de trace em JSON
uv run pandora-rag agent \
  "Meu CPF 123.456.789-00. Estou no rotativo do cartão e a luz atrasou." \
  --persona carla_34 \
  --saida-json
```
