# 02 · Responsabilidades dos Agentes Especializados

O sistema conta com **7 agentes especializados** implementados em [`services/rag/src/pandora_rag/agents/specialists.py`](../../services/rag/src/pandora_rag/agents/specialists.py), cada um dotado de seu **`System Prompt` exclusivo** e de uma **`@tool` nativa do LangChain/LangGraph** em [`langgraph_tools.py`](../../services/rag/src/pandora_rag/agents/langgraph_tools.py), cobrindo os papéis *Research*, *Analysis*, *Validation* e *Communication*.

---

## Visão Geral, Papéis e `@tool`s Vinculadas

| # | Agente (`AgentRole`) | Papel no Entregável UNB | `@tool` Vinculada (`bind_tools`) | Quando é Acionado | O que Consome / Produz no `EstadoMultiagente` |
|---|---|---|---|---|---|
| 1 | `orquestrador` (`OrquestradorAgent`) | **Orchestrator + Communication Agent** | `tool_classificar_roteamento` | Sempre (nós `orquestrador_planejar` e `orquestrador_sintetizar`) | Consome `consulta_usuario`, perfil e saídas dos especialistas · Produz `consulta_mascarada`, `pii_contagem`, `intencoes_detectadas`, `agentes_planejados`, `rascunho_resposta` |
| 2 | `analista` (`AnalistaAgent`) | **Analysis Agent** (Raio-X) | `tool_calcular_raio_x_financeiro` | Sempre que há `persona_id` | Consome `persona_id`, `amostra_transacoes_sinteticas_personas.csv`, `SERIES_SGS_BCB` · Produz `transacoes`, `diagnostico: DiagnosticoFinanceiro` |
| 3 | `estrategista` (`EstrategistaAgent`) | **Analysis Agent** (Dívidas) | `tool_simular_reestruturacao_dividas` | Intenção `dividas` **e** dívida real (no perfil ou na consulta) | Consome `diagnostico`, `dividas_identificadas` · Produz `plano_dividas: PlanoReestruturacao`, `queries_normativas` |
| 4 | `coach` (`CoachAgent`) | **Analysis + Communication Agent** (*Bets*) | `tool_analisar_compulsao_apostas` | Intenção `bets` com termo real de aposta | Consome `transacoes`, `diagnostico.renda_mensal`, `parcela_referencia` · Produz `analise_compulsao: AnaliseCompulsao`, `queries_normativas` |
| 5 | `guardiao` (`GuardiaoAgent`) | **Analysis + Validation Agent** (Antifraude) | `tool_inspecionar_fraude_e_boleto` | Intenção `fraude` / anexo OCR / linha digitável | Consome `transacoes`, `documento_ocr` (fora do prompt LLM), `linha_digitavel` · Produz `inspecao_fraude: InspecaoFraude`, `queries_normativas` |
| 6 | `educador` (`EducadorAgent`) | **Research Agent** (RAG Normativo) | `tool_buscar_evidencias_rag` | Sempre (nó `educador`) | Consome `queries_normativas`, `consulta_mascarada`, `Retriever` híbrido · Produz `evidencias: EvidenciaNormativa` |
| 7 | `compliance` (`ComplianceAgent`) | **Validation Agent** (*LLM-as-a-Judge* + Guardrails) | `tool_auditar_invariantes_compliance` | Sempre (nó `compliance`) | Consome `consulta_mascarada`, `rascunho_resposta`, `evidencias` · Produz `veredito: VereditoCompliance`, `resposta_final` |

---

## Fichas Individuais de Responsabilidade e Fronteiras

### 1. `OrquestradorAgent` (`orquestrador`)
- **System Prompts:** `SYSTEM_PROMPT_ORQUESTRADOR_ROTEAMENTO` (triagem e invocação de `tool_classificar_roteamento`) e `SYSTEM_PROMPT_ORQUESTRADOR_SINTESE` (comunicação adaptativa).
- **Responsabilidades:**
  - Aplicar `mascarar()` na entrada antes de qualquer chamada ao LLM ou log (`RNF01`).
  - Detectar consultas em outro idioma (respondendo exclusivamente em português, conforme perfil do público brasileiro).
  - Combinar a classificação semântica do LLM com sensores determinísticos *defense-in-depth* (`_classificar_intencoes_guardrail` com fronteira `\b`), evitando falsos positivos (*remédio/medo → med*, *alfabeto/betoneiro → bet*, *repasse do app → aposta*) e bloqueando acionamento indevido do `Estrategista` ou `Coach` quando não há dívida/aposta real.
  - Na síntese final, adaptar a saudação e o registro ao perfil (`acessivel_idoso`, `parceiro_sem_julgamento`, saudação neutra sem `"seus dados"` quando não há persona) e **desligar o texto livre do LLM** quando houver crise, trava CVM ou revisão de compliance.
- **Limites:** Nunca calcula valores nem pula a validação do `ComplianceAgent`.

### 2. `AnalistaAgent` (`analista`)
- **System Prompt:** `SYSTEM_PROMPT_ANALISTA` + `@tool tool_calcular_raio_x_financeiro`.
- **Responsabilidades:**
  - Ler o recorte transacional em `docs/evidencias/datasets/amostra_transacoes_sinteticas_personas.csv`.
  - Apurar `renda_mensal`, **despesas vitais estimadas** (moradia, alimentação, saúde e transporte — diferenciadas explicitamente na resposta do mínimo existencial legal de R$ 600,00 do Decreto 11.567/2023), `folga_disponivel`, `gasto_dividas_mensal` e comparativos com `SERIES_SGS_BCB` (**SGS 22022, 25467, 432, 12, 433** com referência `fev/2026`).
  - Sinalizar explicitamente quando uma `persona_id` informada não possuir dados no cadastro nem transações (em vez de exibir `R$ 0,00` silencioso).
- **Limites:** Somente leitura e cálculo determinístico (`RNF03`).

### 3. `EstrategistaAgent` (`estrategista`)
- **System Prompt:** `SYSTEM_PROMPT_ESTRATEGISTA` + `@tool tool_simular_reestruturacao_dividas`.
- **Responsabilidades:**
  - Preservar 100% das despesas vitais (`folga_para_acordos` nunca é negativa).
  - Simular e comparar em 12 meses **Avalanche** (serviços essenciais em atraso primeiro, depois maior CET anual) e **Bola de Neve** (menor saldo), unificando a exibição em texto claro quando ambas as ordens coincidem.
  - Sinalizar o teto legal de 100% do rotativo (**Lei nº 14.690/2023**) e orientar sobre pedido de repactuação global (**Lei nº 14.181/2021** via Procon/Defensoria).
  - Se houver apenas débito mensal de juros no extrato sem detalhamento de contrato, **não** inventar taxa de 435,9% nem gerar simulação artificial.
- **Limites:** Não inventa contratos, taxas nem garante resultado judicial automático.

### 4. `CoachAgent` (`coach`)
- **System Prompt:** `SYSTEM_PROMPT_COACH` + `@tool tool_analisar_compulsao_apostas`.
- **Responsabilidades:**
  - Apurar `total_apostado`, `premios_recebidos`, `perda_liquida`, apostas de madrugada (`23h–06h`) e apostas pós-repasse (`< 24h`) sobre transações `MCC 7995` / `APOSTAS_BETS`.
  - Traduzir a perda líquida em equivalentes concretos (tanques de gasolina; comparação com `parcela_referencia` apenas para personas que possuem parcela cadastrada, como `diego_24`).
  - Redigir orientação empática sem julgamento moral e sem jargão técnico, propondo Pausa Noturna e pausa de 48h junto a bloqueio/limites bancários.
- **Limites:** Nunca moraliza; não atua quando não há apostas reais na jornada nem no histórico.

### 5. `GuardiaoAgent` (`guardiao`)
- **System Prompt:** `SYSTEM_PROMPT_GUARDIAO` + `@tool tool_inspecionar_fraude_e_boleto`.
- **Responsabilidades:**
  - **Isolamento Estrutural (`RNF05`):** O texto de `documento_ocr` **nunca entra no prompt do LLM** — é sanitizado diretamente dentro da `@tool` com `sanitizar_documento_nao_confiavel()`.
  - Auditar boletos FEBRABAN (47 dígitos, módulo 10 nos campos 1–3, divergência bancária, beneficiário PF), alertando claramente quando um formato válido não garante legitimidade.
  - Gerar roteiro em 3 passos do **MED do Pix (Res. BCB nº 147/2021, prazo de 80 dias)**, separando sob título próprio quando advier de transação suspeita no histórico.
- **Limites:** Nunca envia texto cru de OCR ao modelo nem aprova transações.

### 6. `EducadorAgent` (`educador`)
- **System Prompt:** `SYSTEM_PROMPT_EDUCADOR` + `@tool tool_buscar_evidencias_rag`.
- **Responsabilidades:**
  - Executar busca híbrida (`BAAI/bge-m3` + `BM25` + `RRF`) para as consultas normativas geradas pelos especialistas e pelo próprio LLM.
  - Filtrar preâmbulos vazios, títulos sem corpo e cláusulas puramente revogatórias/promulgatórias, limitando a saída a até 4 citações oficiais relevantes `[1]..[k]`.
  - Aplicar o portão de abstenção `RNF04` (incluindo verificação de vocabulário de domínio em consultas livres) para devolver `abstencao=True` fora do escopo financeiro/normativo.
- **Limites:** Nunca fabrica artigo, número de norma ou URL fora dos chunks recuperados.

### 7. `ComplianceAgent` (`compliance`)
- **System Prompt:** `SYSTEM_PROMPT_COMPLIANCE` + `@tool tool_auditar_invariantes_compliance`.
- **Responsabilidades:**
  - Combinar **LLM-as-a-Judge** (cujo veto semântico em `aprovado_semantico`, `contem_recomendacao_implicita_cvm` ou `contem_julgamento_moral` força revisão automática na 1ª passagem) com **5 checagens determinísticas duros**:
    1. **Protocolo de Crise (`100%` obrigatório):** ativa `CVV 188`, `CAPS AD` e `Jogadores Anônimos` para ideação suicida direta ou indireta ou sinal de crise do LLM;
    2. **Trava CVM (`RNF02`):** bloqueia recomendações diretas ou implícitas de ativos/CDBs/corretoras e exige Recusa Educativa com 3 critérios objetivos;
    3. **Alerta Antifraude:** exige explicitamente `"NÃO PAGUE"` ou `"MED do Pix"` quando há fraude detectada;
    4. **Grounding & Números (`RNF03`–`RNF04`):** exige citações `[n]` consistentes e preservação de valores determinísticos;
    5. **LGPD (`RNF01`) & Sem Julgamento Moral:** zero PII residual e bloqueio de linguagem culpabilizante.
  - Caso reprove após o ciclo de revisão (`revisoes_realizadas >= 1`), aciona o nó **`fail_closed`**.
