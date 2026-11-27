# 03 · Fluxo de Interação e Colaboração Entre Agentes (`StateGraph`)

A colaboração entre os 7 agentes do PANDORA acontece por meio de um **`StateGraph(EstadoMultiagente)` compilado no `LangGraph`** ([`graph.py`](../../services/rag/src/pandora_rag/agents/graph.py)), em que cada nó aciona seu LLM com **`bind_tools`** sobre sua `@tool` ([`langgraph_tools.py`](../../services/rag/src/pandora_rag/agents/langgraph_tools.py)) e registra cada handoff em **`MensagemAgente`** no `estado.trace`.

---

## 1. Estrutura da Mensagem e Observabilidade (`MensagemAgente` + `Tool Calls`)

Cada transição no `StateGraph` grava um registro sequencial em `estado.trace` ([`models.py#L30-L38`](../../services/rag/src/pandora_rag/agents/models.py#L30-L38)), incluindo os metadados de execução do LLM (`llm_modelo`), as `@tool`s efetivamente invocadas pelo modelo (`tool_calls`) e seus argumentos:

```json
{
  "ordem": 3,
  "origem": "estrategista",
  "destino": "educador",
  "tipo": "solicitacao_pesquisa",
  "resumo": "Plano Avalanche vs. Bola de Neve gerado blindando R$ 2.100,00; solicitando fundamentação na Lei 14.181/2021, Lei 14.690/2023 e CPC art. 833.",
  "dados_chave": {
    "ordem_avalanche": ["Concessionaria Energia (Luz)", "Cartao de Credito (Banco A)", "Emprestimo Pessoal (Financeira B)"],
    "alerta_lei_14690": true,
    "llm_modelo": "qwen2.5:7b",
    "tool_calls": [
      {
        "tool": "tool_simular_reestruturacao_dividas",
        "args": {
          "queries_normativas": ["Lei 14.181 minimo existencial", "Lei 14.690 teto juros rotativo"],
          "recomendacao_abertura": "Priorize o pagamento da conta de luz..."
        }
      }
    ]
  }
}
```

Os 8 tipos formais de interação (`TipoMensagem`) são: `roteamento`, `analise`, `solicitacao_pesquisa`, `evidencia`, `sintese`, `validacao`, `revisao` e `entrega`.

---

## 2. Diagramas de Sequência da Colaboração

### Cenário A · Superendividamento (`carla_34`) e Compulsão em *Bets* / Crise (`diego_24`)

```mermaid
sequenceDiagram
    actor U as Usuário (Carla / Diego)
    participant O as Orquestrador (planejar/sintetizar)
    participant AN as Analista (@tool Raio-X)
    participant SP as Estrategista / Coach (@tool)
    participant ED as Educador (@tool RAG)
    participant CG as Compliance (Judge + @tool)

    U->>O: Consulta financeira ou relato de crise/aposta
    O->>O: mascarar() PII + qwen2.5:7b -> tool_classificar_roteamento + sensores \b
    O->>AN: [roteamento] sequência condicional via add_conditional_edges
    AN->>AN: LLM invoca tool_calcular_raio_x_financeiro (SGS fev/2026)
    AN->>SP: [analise] DiagnosticoFinanceiro tipado
    SP->>SP: LLM invoca tool_simular_reestruturacao_dividas OU tool_analisar_compulsao_apostas
    SP->>ED: [solicitacao_pesquisa] Plano/Compulsão + queries normativas dinâmicas
    ED->>ED: LLM invoca tool_buscar_evidencias_rag (BGE-M3 + BM25 + RRF + filtro RNF04)
    ED->>O: [evidencia] até 4 citações oficiais substantivas [1]..[k]
    O->>O: sintetizar() (LLM desligado automaticamente se crise_ativa=True)
    O->>CG: [sintese] rascunho_resposta
    CG->>CG: LLM invoca tool_auditar_invariantes_compliance + 5 checagens duras
    CG-->>O: [entrega] APROVADO -> resposta_final
    O-->>U: Resposta segura, exata e citada
```

### Cenário B · Veto do *Compliance Judge* / Loop de Revisão (`julia_31`) e Defesa Anti-Injection (`antonio_67`)

```mermaid
sequenceDiagram
    actor U as Usuário (Júlia / Sr. Antônio)
    participant O as Orquestrador
    participant AN as Analista (@tool)
    participant GU as Guardião (@tool)
    participant ED as Educador (@tool RAG)
    participant CG as Compliance (Judge)

    U->>O: "Qual CDB comprar?" OU Boleto OCR com prompt injection
    O->>AN: [roteamento] plano condicional (CVM bloqueia texto livre do LLM na síntese)
    AN->>GU: [analise] contexto financeiro (se fraude)
    GU->>GU: documento_ocr NÃO vai para o LLM · tool_inspecionar_fraude_e_boleto isola injection + FEBRABAN
    GU->>ED: [solicitacao_pesquisa] injection_detectada=True + query Res. BCB 147
    ED->>O: [evidencia] Res. CVM 19/2021 OU Res. BCB 147/2021 (MED 80 dias)
    O->>CG: [sintese] rascunho inicial (ex.: veto do LLM-as-a-Judge ou recomendação CVM)
    CG-->>O: [validacao] REPROVADO (aciona aresta condicional preparar_revisao)
    O->>O: sintetizar(modo_revisao=True) removendo textos livres do LLM
    O->>CG: [revisao] rascunho determinístico saneado
    CG-->>O: [entrega] APROVADO (ou fail_closed se ainda reprovar)
    O-->>U: Resposta segura sem vazamento nem recomendação vedada
```

---

## 3. Como os Agentes Colaboram Sem Risco de Alucinação Numérica ou Bypass

1. **Delegação Cognitiva + Execução Matemática Determinística (`RNF03`):** O modelo `qwen2.5:7b` decide **quais ferramentas acionar**, interpreta o contexto em linguagem humana e **formula consultas jurídicas** para o `EducadorAgent`, mas **nunca executa contas no texto** — juros, mínimo existencial, perda líquida e Módulo 10 FEBRABAN retornam diretamente das `@tool`s Python.
2. **Isolamento de OCR e Bloqueio em Crise/CVM:** O conteúdo não confiável de `documento_ocr` nunca entra no prompt do `GuardiaoAgent`; e em qualquer cenário com crise emocional ou indução CVM, a síntese e pareceres livres do LLM são desligados por construção.
3. **Ciclo de Revisão Real no `StateGraph`:** O veredito semântico do *Compliance Judge* (`aprovado_semantico=False`, `contem_recomendacao_implicita_cvm=True` ou `contem_julgamento_moral=True`) é respeitado pelo grafo (`compliance -> preparar_revisao -> orquestrador_sintetizar -> compliance`), limpando qualquer texto inadequado antes da entrega final.
