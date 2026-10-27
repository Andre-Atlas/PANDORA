# 06 · Riscos, limitações e métricas

> Restrições do Challenge: **explicitar riscos e limitações** e **validar com métricas objetivas**.

## 1. Matriz de riscos

| # | Risco | Prob. | Impacto | Mitigação | Dono (squad) |
|---|---|---|---|---|---|
| R1 | **Alucinação financeira/jurídica** (taxa, direito ou prazo errado) | Alta | Alto | RAG com citação obrigatória, cálculos determinísticos, checagem de groundedness, recusa sem evidência | engenheiro_ml_rag |
| R2 | **Conselho de investimento regulado** (CVM) | Média | Alto | Escopo educacional ([ADR-0004](adr/0004-investimento-educacional.md)), guardrail de saída, testes adversariais | compliance_financeiro_lgpd |
| R3 | **Vazamento de dados financeiros** (LGPD) | Média | Muito alto | Mascaramento, cifragem, cofre, só dados sandbox/sintéticos no projeto | compliance_financeiro_lgpd |
| R4 | **Dano a usuário vulnerável** (culpa, gatilho, crise) | Média | Muito alto | Linguagem não estigmatizante, opt-in, fluxo de crise, revisão por especialista quando possível | compliance_financeiro_lgpd |
| R5 | **Prompt injection** via extrato, boleto ou imagem | Média | Alto | Conteúdo tratado como dado, ferramentas sem efeito financeiro, testes adversariais | tester_back |
| R6 | **Viés de classificação** (ex.: marcar gasto legítimo como "supérfluo") | Média | Médio | Usuário corrige rótulos, métricas por segmento, explicabilidade | engenheiro_ml_rag |
| R7 | **Dependência do agregador** (sandbox muda, limite de trial) | Média | Médio | `BankDataPort` + upload como caminho alternativo | designer_back_end |
| R8 | **Custo de LLM** acima do previsto | Média | Médio | Gateway com roteamento/cache, modelo local, telemetria ([ADR-0003](adr/0003-selecao-llm.md)) | engenheiro_ml_rag |
| R9 | **Escopo grande para 7 semanas** | Alta | Alto | MoSCoW rígido, MVP definido em [02](02-features.md#recorte-do-mvp-demo-da-semana-6) | arquiteto |
| R10 | **Base de conhecimento desatualizada** | Média | Médio | Metadados de vigência, pipeline de recoleta, data exibida na citação | engenheiro_ml_rag |

## 2. Limitações declaradas

- Não usa dados bancários reais de usuários durante o projeto (só sandbox e sintéticos).
- Não substitui advogado, Defensoria, psicólogo ou psiquiatra.
- Não recomenda produtos financeiros nem executa transações.
- Validação de impacto em qualidade de vida é feita com **personas simuladas e piloto pequeno**, não com estudo clínico.
- A detecção de apostas depende da qualidade da descrição da transação e da lista oficial de operadoras.

## 3. Métricas objetivas

### 3.1 Componentes de ML

| Métrica | Componente | Meta inicial |
|---|---|---|
| F1 macro | Classificador de transações | ≥ 0,85 em dados sintéticos rotulados |
| Precision / Recall | Detector de apostas | Recall ≥ 0,95 · Precision ≥ 0,90 |
| Precision@k / Recall | Antifraude / anomalias | Recall ≥ 0,80 com taxa de falso alarme ≤ 5% |
| MAPE | Previsão de caixa 30d | ≤ 15% |

### 3.2 RAG e LLM (Ragas + golden set)

| Métrica | Meta inicial |
|---|---|
| Faithfulness | ≥ 0,90 |
| Answer relevancy | ≥ 0,85 |
| Context precision | ≥ 0,80 |
| Respostas com citação válida | 100% nas perguntas normativas |
| Taxa de recusa correta (sem evidência) | ≥ 0,90 |

**Experimento da Semana 3, LLM puro × RAG:** mesmo conjunto de ~100 perguntas (direitos, juros, golpes, apostas, investimento) avaliado nas duas configurações. Medimos correção factual (juiz humano + LLM-as-judge com rubrica), alucinação e citação.

### 3.3 Sistema multiagente

| Métrica | Meta inicial |
|---|---|
| Acurácia de roteamento do Orquestrador | ≥ 0,90 |
| Sucesso de tarefa ponta a ponta (cenários das personas) | ≥ 0,80 |
| Guardrails: bloqueio correto em testes adversariais | ≥ 0,95 |
| Latência p95 por resposta | ≤ 8 s (texto) |
| Custo médio por conversa | registrado e comparado no ADR-0003 |

Também comparamos **agente único × multiagente** na mesma suíte de cenários (hipótese 4).

### 3.4 Qualidade de vida (impacto)

| Indicador | Como medir |
|---|---|
| Bem-estar financeiro | Escala CFPB Financial Well-Being ou InCharge, antes e depois (piloto) |
| Comprometimento de renda com dívidas | % calculado pelo Raio-X ao longo do tempo |
| Dívidas renegociadas / quitadas | Contagem e valor no plano |
| Dias sem aposta | Detector de apostas + autorrelato |
| Adesão ao plano | % de passos concluídos |
| Compreensão | Quiz curto após a explicação do Raio-X |

## 4. Plano de avaliação

1. **Semana 1:** golden set inicial (perguntas e cenários por persona) + gerador de dados sintéticos.
2. **Semana 2–3:** Ragas no RAG; experimento LLM × RAG.
3. **Semana 4:** cenários ponta a ponta multiagente; agente único × multiagente.
4. **Semana 5:** casos multimodais (boletos e prints reais anonimizados ou sintéticos).
5. **Semana 6:** testes adversariais (injeção, pedido de recomendação, crise).
6. **Semana 7:** relatório consolidado + piloto com voluntários (personas) e escalas antes/depois.

As suítes rodam na CI e **bloqueiam merge** abaixo do limiar (regra 2 do [AGENTS.md](../AGENTS.md)).
