# 📊 Datasets, Séries Temporais e Bases de Dados — PANDORA

Este diretório documenta as fontes de dados oficiais (APIs públicas), os datasets abertos de *benchmark* para Machine Learning e a amostra de dados sintéticos gerada a partir das personas do projeto.

> **Regra de Governança e Privacidade (LGPD):** Conforme definido em [`AGENTS.md`](../../../AGENTS.md) e [`docs/05-dados-e-integracoes.md`](../../05-dados-e-integracoes.md), **nenhum dado bancário real de pessoas físicas é armazenado no repositório**. O PANDORA utiliza exclusivamente APIs públicas de indicadores econômicos, datasets públicos anonimizados e geradores sintéticos baseados nas 4 personas.

---

## 1. APIs e Séries Temporais Oficiais — Banco Central do Brasil (SGS / Dados Abertos)

O **Estrategista de Dívidas** e os **Simuladores Educacionais** consomem diretamente o **Sistema Gerenciador de Séries Temporais (SGS)** do Banco Central para comparar a taxa de juros do contrato do usuário com a média praticada pelo mercado e calcular correções reais.

- **Endpoint padrão da API (JSON/CSV):**
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json`
- **Portal de Dados Abertos do BCB:** [dadosabertos.bcb.gov.br](https://dadosabertos.bcb.gov.br/)

| Código SGS | Nome da Série Oficial (BCB) | Unidade | Uso no PANDORA |
|---|---|---|---|
| **`25477`** | Taxa média mensal de juros — Pessoas físicas — Cartão de crédito rotativo total | % a.m. | Detectar juros abusivos no cartão da persona **Carla** e priorizar quitação/renegociação. |
| **`22022`** | Taxa média de juros — Pessoas físicas — Cartão de crédito rotativo | % a.a. | Exibir comparativo anualizado no **Raio-X Financeiro** (ex.: 451,71% a.a. em set/2026). |
| **`25463`** | Taxa média mensal de juros — Pessoas físicas — Cheque especial | % a.m. | Verificar conformidade com o teto regulatório de 8% a.m. (Resolução CMN 4.765/2019). |
| **`25464`** | Taxa média mensal de juros — Pessoas físicas — Crédito pessoal não consignado | % a.m. | Simular troca de dívida cara (rotativo) por linha de custo menor. |
| **`25467`** | Taxa média mensal de juros — Pessoas físicas — Crédito pessoal consignado INSS | % a.m. | Auditar contratos de consignado da persona **Sr. Antônio (67 anos)**. |
| **`432`** | Taxa de juros — Meta Selic definida pelo Copom | % a.a. | Simulador de Reserva de Emergência (Tesouro Selic) no **Módulo 6**. |
| **`433`** | Índice Nacional de Preços ao Consumidor Amplo (IPCA) — Variação mensal | % a.m. | Cálculo de ganho real e poder de compra no **Módulo 4 (Orçamento & Metas)**. |
| **`12`** | Taxa de juros — CDI | % a.d. | Comparador educacional de renda fixa (**Módulo 6**). |

---

## 2. Base Oficial de Operadoras de Apostas Autorizadas (SPA / Ministério da Fazenda)

Para que o **Módulo 2 (Detector de Compulsão)** identifique transações de apostas online com alta precisão (além do código MCC `7995` e padrões de descrição), o sistema cruza os destinatários de Pix/TED com a base pública da **Secretaria de Prêmios e Apostas (SPA/MF)**, instituída pela Lei 14.790/2023.

- **Fonte oficial:** [Ministério da Fazenda — Secretaria de Prêmios e Apostas (Lista de Empresas Autorizadas)](https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apostas)
- **Campos utilizados na tabela `BET_OPERATOR`:**
  - Razão Social e CNPJ da operadora autorizada
  - Marcas comerciais e domínios `.bet.br` registrados
  - Status de autorização (Nacional / Estadual / Não autorizada)
- **Valor de negócio e proteção:** Permite não apenas medir a frequência e a escalada de apostas (ex.: apostas noturnas ou logo após o recebimento de salário/repasse), como também alertar imediatamente o usuário caso ele esteja enviando dinheiro para uma plataforma **ilegal/não autorizada**, onde o risco de fraude e retenção indevida de saldo é total.

---

## 3. Datasets Públicos para Benchmark de Machine Learning (`services/ml`)

Os modelos de **Classificação de Transações**, **Detecção de Anomalias/Fraudes** (Isolation Forest / Gradient Boosting) e **Previsão de Fluxo de Caixa** (Prophet / ETS) utilizam os seguintes datasets públicos para validação de pipeline e *benchmarking*:

| Dataset | Fonte / Link | Escala e Características | Aplicação no PANDORA |
|---|---|---|---|
| **Credit Card Fraud Detection (ULB)** | [Kaggle — mlg-ulb/creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) / [OpenML](https://www.openml.org/d/1597) | 284.807 transações reais anonimizadas via PCA (`V1`–`V28`, `Time`, `Amount`), com 492 fraudes (0,172% — forte desbalanceamento). | Benchmark de calibração de *threshold* e avaliação de *Precision/Recall/PR-AUC* do pipeline de detecção de anomalias do **Guardião**. |
| **PaySim — Synthetic Financial Datasets For Fraud Detection** | [Kaggle — ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1) | 6,3 milhões de transações sintéticas de *mobile money* (`CASH-IN`, `CASH-OUT`, `TRANSFER`, `PAYMENT`) modeladas sobre logs reais. | Simulação de padrões de transferência instantânea (análogos ao Pix), esvaziamento de conta e transações atípicas para a persona **Sr. Antônio**. |
| **Sparkov Credit Card Transactions (Simulated)** | [GitHub — namebrandon/Sparkov_Data_Generation](https://github.com/namebrandon/Sparkov_Data_Generation) | Transações sintéticas multi-cliente com categorias (MCC), horários, valores e perfis demográficos distintos. | Pré-treinamento e validação da arquitetura de classificação de categorias de gastos e detecção de mudança de hábito de consumo. |
| **PEIC — Série Histórica de Endividamento (CNC)** | [Portal do Comércio — Pesquisas CNC (PEIC)](https://portaldocomercio.org.br/) | Indicadores mensais de percentual de famílias endividadas, com contas em atraso, sem condições de pagar e tipo de dívida (2010–2026). | Contextualização macroeconômica e validação dos pesos do **Score de Saúde Financeira** do Raio-X. |

---

## 4. Amostra de Dataset Sintético das Personas PANDORA

Para testar de ponta a ponta o fluxo de ingestão (`TRANSACTION`), classificação (`category`), detecção de apostas (`is_bet`) e anomalias (`anomaly_score`) definido em [`docs/05-dados-e-integracoes.md`](../../05-dados-e-integracoes.md), incluímos neste diretório o arquivo:

📄 **[`amostra_transacoes_sinteticas_personas.csv`](amostra_transacoes_sinteticas_personas.csv)**

### Esquema do Arquivo (`amostra_transacoes_sinteticas_personas.csv`)

| Coluna | Tipo | Descrição |
|---|---|---|
| `transaction_id` | `string (UUID)` | Identificador único da transação sintética |
| `persona_id` | `string` | `carla_34` (superendividada), `diego_24` (compulsão em bets), `antonio_67` (aposentado/alvo de golpe), `julia_29` (reconstrução/investimento) |
| `posted_at` | `datetime (ISO)` | Data e hora da transação (inclui horários de madrugada para capturar compulsão e anomalias) |
| `amount` | `decimal` | Valor em R$ (negativo para saídas, positivo para entradas) |
| `payment_method` | `string` | `PIX`, `CREDIT_CARD`, `DEBIT_CARD`, `BOLETO`, `DIRECT_DEBIT` |
| `description_masked` | `string` | Descrição normalizada e sem PII (conforme diretriz LGPD) |
| `mcc` | `string` | *Merchant Category Code* (ex.: `7995` para apostas, `5411` supermercado, `6012` instituições financeiras) |
| `category` | `string` | Categoria rotulada (`RENDA`, `MORADIA`, `ALIMENTACAO`, `DIVIDA_JUROS`, `APOSTAS_BETS`, `FRAUDE_SUSPEITA`, `INVESTIMENTO`, `TRANSPORTE`) |
| `is_bet` | `boolean` | `true` quando a transação é destinada a operadora de aposta |
| `anomaly_score` | `float (0..1)` | Score de anomalia/risco calculado (valores `>= 0.80` acionam alerta do **Guardião** ou **Detector de Compulsão**) |
| `ground_truth_note` | `string` | Explicação do comportamento representado para uso no *Golden Set* de avaliação |
