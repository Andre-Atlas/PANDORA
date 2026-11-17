# 02 · Responsabilidades dos Agentes Especializados

O sistema conta com **7 agentes especializados** implementados em [`services/rag/src/pandora_rag/agents/specialists.py`](../../services/rag/src/pandora_rag/agents/specialists.py), cobrindo integralmente os papéis previstos no escopo PANDORA e os arquétipos propostos no entregável (*Research*, *Analysis*, *Validation* e *Communication*).

---

## Visão Geral e Mapeamento de Papéis

| # | Agente (`AgentRole`) | Papel no Entregável UNB | Quando é Acionado | O que Consome | O que Produz no `EstadoMultiagente` |
|---|---|---|---|---|---|
| 1 | `orquestrador` (`OrquestradorAgent`) | **Orchestrator + Communication Agent** | Sempre (entrada e síntese) | `consulta_usuario`, perfil da persona, saídas dos especialistas, `evidencias`, `veredito` | `consulta_mascarada`, `pii_contagem`, `intencoes_detectadas`, `agentes_planejados`, `rascunho_resposta` |
| 2 | `analista` (`AnalistaAgent`) | **Analysis Agent** (Raio-X) | Sempre que há `persona_id` | `persona_id`, `amostra_transacoes_sinteticas_personas.csv`, séries `SERIES_SGS_BCB` | `transacoes`, `diagnostico: DiagnosticoFinanceiro` |
| 3 | `estrategista` (`EstrategistaAgent`) | **Analysis Agent** (Dívidas) | Intenção `dividas` | `diagnostico` (renda, mínimo existencial, dívidas) | `plano_dividas: PlanoReestruturacao`, `queries_normativas` |
| 4 | `coach` (`CoachAgent`) | **Analysis + Communication Agent** (*Bets*) | Intenção `bets` | `transacoes`, `diagnostico.renda_mensal` | `analise_compulsao: AnaliseCompulsao`, `queries_normativas` |
| 5 | `guardiao` (`GuardiaoAgent`) | **Analysis + Validation Agent** (Antifraude) | Intenção `fraude` / anexo OCR / boleto | `transacoes`, `documento_ocr`, `linha_digitavel`, `banco_alegado`, `beneficiario_pf` | `inspecao_fraude: InspecaoFraude`, `queries_normativas` |
| 6 | `educador` (`EducadorAgent`) | **Research Agent** (RAG Normativo) | Sempre (etapa normativa central) | `queries_normativas`, `consulta_mascarada`, `Retriever` híbrido | `evidencias: EvidenciaNormativa` |
| 7 | `compliance` (`ComplianceAgent`) | **Validation & Communication Agent** | Sempre (portão final + revisão) | `consulta_mascarada`, `rascunho_resposta`, `evidencias`, `analise_compulsao` | `veredito: VereditoCompliance`, `resposta_final` |

---

## Fichas Individuais de Responsabilidade

### 1. `OrquestradorAgent` (`orquestrador`)
- **Missão:** Ponto único de entrada e saída conversacional. Protege dados pessoais antes do roteamento, decide o plano de execução e adapta o tom da resposta final à condição emocional e digital da persona (`acolhedor_simples`, `parceiro_sem_julgamento`, `acessivel_idoso`, `educativo_calmo`).
- **Responsabilidades:**
  - Aplicar `mascarar()` sobre `consulta_usuario` removendo CPF, CNPJ, telefone, e-mail e número de cartão sem corromper referências a leis ou valores em reais (`R$`).
  - Classificar intenções (`dividas`, `bets`, `fraude`, `cvm`, `crise`, `educacao`) e montar `agentes_planejados`.
  - Na etapa de síntese (`sintetizar`), consolidar os números determinísticos de cada especialista com as citações `[n]` recuperadas pelo `EducadorAgent`, além de executar o modo de revisão caso o `ComplianceAgent` reprove o rascunho.
- **Limites:** Nunca calcula juros, parcelas ou perdas por conta própria; nunca pula a validação do `ComplianceAgent`.

### 2. `AnalistaAgent` (`analista`)
- **Missão:** Produzir o **Raio-X Financeiro determinístico** da pessoa usuária a partir das transações sintéticas e do perfil cadastrado.
- **Responsabilidades:**
  - Carregar transações reais do recorte em `docs/evidencias/datasets/amostra_transacoes_sinteticas_personas.csv`.
  - Apurar `renda_mensal`, `minimo_existencial` (despesas vitais: moradia, alimentação, saúde e transporte), `folga_disponivel` (`max(0, renda - minimo_existencial)`), `gasto_dividas_mensal` e `comprometimento_dividas_pct`.
  - Confrontar as taxas das dívidas identificadas contra as séries oficiais do Banco Central (**SGS `22022`** — rotativo a `435,9% a.a.`; **SGS `25467`** — consignado INSS a `24,5% a.a.`; além de Selic `432`, CDI `12` e IPCA `433`).
- **Limites:** Somente leitura (`read-only`); apenas extrai e computa indicadores financeiros determinísticos.

### 3. `EstrategistaAgent` (`estrategista`)
- **Missão:** Definir a estratégia de pagamento e repactuação de dívidas preservando **100% do Mínimo Existencial**.
- **Responsabilidades:**
  - Executar `simular_estrategias_divida(diagnostico, dividas)`, garantindo que `folga_para_acordos` nunca invada alimentação/moradia (`deficit_vital` explícito se a renda for menor que o mínimo existencial).
  - Priorizar **serviços essenciais em atraso** (ex.: conta de energia elétrica vencida há 45 dias) antes de dívidas bancárias.
  - Simular e comparar em 12 meses os métodos **Avalanche** (maior CET primeiro) e **Bola de Neve** (menor saldo primeiro).
  - Sinalizar alerta para o teto de 100% do rotativo (**Lei nº 14.690/2023**) e elegibilidade à audiência global de conciliação (**Lei nº 14.181/2021**).
  - Solicitar ao `EducadorAgent` as buscas jurídicas pertinentes (Lei 14.181, Lei 14.690 e CPC art. 833).
- **Limites:** Não inventa descontos bancários; encaminha fundamentos legais para verificação no RAG.

### 4. `CoachAgent` (`coach`)
- **Missão:** Detectar comportamento compulsivo em apostas online (*bets*) e propor fricção positiva sem julgamento moral.
- **Responsabilidades:**
  - Filtrar transações com `is_bet=True`, `mcc="7995"` ou `category="APOSTAS_BETS"`.
  - Calcular exatamente `total_apostado`, `premios_recebidos`, `perda_liquida = max(0, total_apostado - premios_recebidos)` e `pct_renda_comprometida`.
  - Identificar padrões de alto risco: apostas na madrugada (`23h–06h`, *chasing losses*) e apostas realizadas até 24h após recebimento de repasse/salário (`aposta_pos_salario`).
  - Traduzir a perda financeira em **custo de oportunidade tangível** (ex.: tanques de combustível da moto ou parcelas do instrumento de trabalho) e recomendar janela de resfriamento (*cooling-off* de 24h–48h) e autoexclusão.
  - Solicitar ao `EducadorAgent` os dispositivos da **Lei nº 14.790/2023**.
- **Limites:** Nunca usa linguagem punitiva ou moralizante; não realiza atendimento clínico psicológico.

### 5. `GuardiaoAgent` (`guardiao`)
- **Missão:** Proteger usuários vulneráveis contra fraudes em boletos/Pix e contra ataques de *prompt injection* em documentos enviados.
- **Responsabilidades:**
  - Executar `sanitizar_documento_nao_confiavel()` sobre `documento_ocr`, detectando instruções maliciosas ocultas (ex.: *"IGNORE AS INSTRUCOES ANTERIORES"*), substituindo-as por `[CONTEUDO_BLOQUEADO_INJECTION]` e isolando o documento entre delimitadores `<documento_externo_nao_confiavel>`.
  - Auditar `linha_digitavel` com `validar_boleto_febraban()`: comprimento exato (47 dígitos), dígito verificador Módulo 10 dos campos 1–3, divergência entre o código bancário do código de barras e o banco alegado no documento, e flag de beneficiário Pessoa Física (PF).
  - Identificar transações `FRAUDE_SUSPEITA` no histórico e montar o roteiro passo a passo do **MED do Pix (Res. BCB nº 147/2021)** com prazo legal de **80 dias**.
  - Solicitar ao `EducadorAgent` o texto oficial da Resolução BCB nº 147/2021.
- **Limites:** Não aprova pagamentos nem executa transações bancárias (`RF18`).

### 6. `EducadorAgent` (`educador`)
- **Missão:** Atuar como **Research Agent** garantindo que toda informação normativa e jurídica entregue ao usuário provenha de fontes oficiais recuperadas pelo RAG.
- **Responsabilidades:**
  - Consumir as demandas acumuladas em `queries_normativas` pelos agentes analíticos (`estrategista`, `coach`, `guardiao`) ou pela consulta inicial.
  - Consultar o `Retriever` híbrido (`BAAI/bge-m3` + `BM25` + `RRF`), priorizando cobertura diversa entre as consultas solicitadas e deduplicando chunks por ID.
  - Respeitar o portão de abstenção (`score_rerank < 0.02`), sinalizando `abstencao=True` caso nenhuma evidência atinja o limiar.
  - Devolver `EvidenciaNormativa` com citações numeradas `[1]..[k]`, artigo, trecho e link oficial para o `OrquestradorAgent`.
- **Limites:** Não escreve resposta final nem formula recomendações de investimento.

### 7. `ComplianceAgent` (`compliance`)
- **Missão:** Atuar como **Validation Agent** (portão final inviolável) auditando a síntese antes que chegue ao usuário.
- **Responsabilidades:**
  - **Invariante 1 — Protocolo de Crise (`100%` obrigatório):** Diante de marcadores de sofrimento psíquico agudo (`detectar_sinais_crise`) ou compulsão crítica com perda de controle, exige a presença do bloco de acolhimento imediato com **CVV (`188`)**, **CAPS AD** e **Jogadores Anônimos (JA)**.
  - **Invariante 2 — Trava CVM (`RNF02`):** Bloqueia recomendações específicas de ações, fundos ou CDBs de bancos determinados (Res. CVM 19 e 20/2021) e exige **Recusa Educativa** contendo os 3 critérios objetivos (Liquidez D+0, Risco Soberano/FGC e Pós-fixado Selic/CDI).
  - **Invariante 3 — Rastreabilidade de Citações (`RNF04`):** Quando o `EducadorAgent` recuperou evidências válidas, exige ao menos uma citação `[n]` válida na resposta.
  - **Invariante 4 — LGPD/PII (`RNF01`):** Verifica que nenhum dado pessoal sensível escapou para o texto final.
  - Caso qualquer invariante falhe, emite `aprovado=False` com `motivo_revisao` e devolve o controle ao `OrquestradorAgent` para correção antes da entrega.
