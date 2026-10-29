# 📊 Datasets, Séries Temporais e Bases de Dados — PANDORA

Este diretório documenta as fontes de dados oficiais (APIs públicas), os datasets abertos de *benchmark* para Machine Learning e a amostra de dados sintéticos gerada a partir das personas do projeto.

> **Privacidade (LGPD):** nenhum dado bancário real de pessoas físicas é armazenado no repositório. Só há indicadores públicos, datasets públicos anonimizados e dados sintéticos baseados nas personas.

---

## 1. APIs e Séries Temporais Oficiais — Banco Central do Brasil (SGS / Dados Abertos)

Séries do **Sistema Gerenciador de Séries Temporais (SGS)** do Banco Central com as taxas médias de juros de mercado e os indicadores macroeconômicos de referência.

- **Endpoint padrão da API (JSON/CSV):**
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json`
- **Portal de Dados Abertos do BCB:** [dadosabertos.bcb.gov.br](https://dadosabertos.bcb.gov.br/)

| Código SGS | Nome da Série Oficial (BCB) | Unidade |
|---|---|---|
| **`25477`** | Taxa média mensal de juros — Pessoas físicas — Cartão de crédito rotativo total | % a.m. |
| **`22022`** | Taxa média de juros — Pessoas físicas — Cartão de crédito rotativo | % a.a. |
| **`25463`** | Taxa média mensal de juros — Pessoas físicas — Cheque especial | % a.m. |
| **`25464`** | Taxa média mensal de juros — Pessoas físicas — Crédito pessoal não consignado | % a.m. |
| **`25467`** | Taxa média mensal de juros — Pessoas físicas — Crédito pessoal consignado INSS | % a.m. |
| **`432`** | Taxa de juros — Meta Selic definida pelo Copom | % a.a. |
| **`433`** | Índice Nacional de Preços ao Consumidor Amplo (IPCA) — Variação mensal | % a.m. |
| **`12`** | Taxa de juros — CDI | % a.d. |

---

## 2. Base Oficial de Operadoras de Apostas Autorizadas (SPA / Ministério da Fazenda)

Base pública da **Secretaria de Prêmios e Apostas (SPA/MF)**, instituída pela Lei 14.790/2023, com as operadoras de apostas autorizadas a operar no Brasil.

- **Fonte oficial:** [Ministério da Fazenda — Secretaria de Prêmios e Apostas (Lista de Empresas Autorizadas)](https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apostas)
- **Campos disponíveis:**
  - Razão Social e CNPJ da operadora autorizada
  - Marcas comerciais e domínios `.bet.br` registrados
  - Status de autorização (Nacional / Estadual / Não autorizada)

---

## 3. Datasets Públicos de Transações e Fraude

Bases públicas de transações financeiras e fraude, usadas como referência de escala e características do problema.

| Dataset | Fonte / Link | Escala e Características |
|---|---|---|
| **Credit Card Fraud Detection (ULB)** | [Kaggle — mlg-ulb/creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) / [OpenML](https://www.openml.org/d/1597) | 284.807 transações reais anonimizadas via PCA (`V1`–`V28`, `Time`, `Amount`), com 492 fraudes (0,172% — forte desbalanceamento). |
| **PaySim — Synthetic Financial Datasets For Fraud Detection** | [Kaggle — ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1) | 6,3 milhões de transações sintéticas de *mobile money* (`CASH-IN`, `CASH-OUT`, `TRANSFER`, `PAYMENT`) modeladas sobre logs reais. |
| **Sparkov Credit Card Transactions (Simulated)** | [GitHub — namebrandon/Sparkov_Data_Generation](https://github.com/namebrandon/Sparkov_Data_Generation) | Transações sintéticas multi-cliente com categorias (MCC), horários, valores e perfis demográficos distintos. |
| **PEIC — Série Histórica de Endividamento (CNC)** | [Portal do Comércio — Pesquisas CNC (PEIC)](https://portaldocomercio.org.br/) | Indicadores mensais de percentual de famílias endividadas, com contas em atraso, sem condições de pagar e tipo de dívida (2010–2026). |

---

## 4. Amostra de Dataset Sintético das Personas PANDORA

Amostra de transações **fictícias** das quatro personas do problema, com rótulos de categoria, apostas e fraude:

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
| `anomaly_score` | `float (0..1)` | Score de anomalia/risco calculado (valores `>= 0.80` indicam comportamento de risco) |
| `ground_truth_note` | `string` | Explicação do comportamento representado |
