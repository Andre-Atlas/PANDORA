# Evidências e Acervo de Referências — PANDORA

Este diretório consolida **notícias**, **datasets** e **artigos científicos/técnicos** que contextualizam o problema do endividamento, da compulsão financeira e dos golpes no Brasil.

> **Alinhamento CBL (Challenge-Based Learning):**
> - **Big Idea:** Qualidade de Vida (*"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*)
> - **Essential Question:** *Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?*

---

## 📂 Estrutura de Pastas

| Pasta | Conteúdo |
|---|---|
| [`noticias/`](noticias/README.md) | Reportagens, levantamentos setoriais (Serasa, CNC/Peic, Datafolha/FBSP) e comunicados oficiais (BCB, Senado, Agência Brasil). |
| [`datasets/`](datasets/README.md) | Séries temporais oficiais (API SGS/BCB), bases públicas abertas (SPA/MF, Dados Abertos BCB, Kaggle/OpenML) e amostra de dados sintéticos ([`amostra_transacoes_sinteticas_personas.csv`](datasets/amostra_transacoes_sinteticas_personas.csv)). |
| [`artigos/`](artigos/README.md) | Estudos técnicos do Banco Central, escalas psicométricas internacionais de bem-estar financeiro, literatura sobre transtorno do jogo e marcos jurídicos (Lei 14.181/2021). |

---

## 🔗 Matriz: Eixo do Problema → Evidências

| Eixo do Problema | Notícia / Fato Recente | Artigo / Estudo / Lei Base | Dataset / Fonte de Dados |
|---|---|---|---|
| **Superendividamento e Juros Abusivos** | 81,7 mi de inadimplentes (Serasa, 2026); 81,7% das famílias endividadas (CNC/Peic, 2026); rotativo a 435,9% a.a. | Lei 14.181/2021 (Superendividamento e Mínimo Existencial); Lei 14.690/2023 (Teto do Rotativo). | Séries SGS/BCB (`25477` rotativo, `25463` cheque especial, `432` Selic); Dados Abertos BCB. |
| **Compulsão em Apostas Online (*Bets*)** | R$ 20,8 bi/mês via Pix para *bets*; impacto em famílias vulneráveis e proibição pelo STF. | Estudo Especial BCB nº 119/2024; CID-11 `6C50` (*Gambling Disorder*); Lei 14.790/2023. | Lista pública de operadoras autorizadas (SPA/MF); Dataset sintético rotulado (`is_bet`). |
| **Golpes Financeiros (Pix e Boletos)** | 24 milhões de vítimas de golpes de Pix/boleto em 12 meses; R$ 29 bi de prejuízo (Datafolha/FBSP). | Resolução BCB nº 147/2021 (Mecanismo Especial de Devolução - MED); Guias Antifraude FEBRABAN. | Credit Card Fraud Detection (ULB/Kaggle); PaySim / BankSim; Amostra sintética (`anomaly_score`). |
| **Saúde Mental e Qualidade de Vida** | Estresse financeiro como principal causa de insônia, ansiedade e queda de produtividade no país. | Prawitz et al. (2006) — *IFDFW Scale*; CFPB (2017) — *Financial Well-Being Scale*; Lusardi & Mitchell (2014). | Questionários psicométricos estruturados (pré e pós-intervenção) e séries IPCA/CDI. |
