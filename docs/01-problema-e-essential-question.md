# 01 · Problema e Essential Question

> Restrição do Challenge: **entender o problema antes da solução** e **usar evidências confiáveis**.
> Os números marcados com 🔎 devem ser conferidos e atualizados na fonte original durante a Semana 1, antes de entrarem no relatório final.

## 1. Big Idea → Essential Question

**Big Idea:** Qualidade de Vida. *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*

**Essential Question:**
> Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?

**Perguntas-guia:**
- O que a pessoa endividada **não consegue enxergar** sozinha na própria movimentação financeira?
- Em que momento uma intervenção (alerta, trava, conversa) muda de fato o comportamento, e quando ela vira ruído ou culpa?
- Que informação oficial (direitos, programas, normas) as pessoas desconhecem e que poderia reduzir o custo das dívidas?
- Como medir a melhora de **qualidade de vida**, e não só a de saldo?

## 2. O problema

### 2.1 Endividamento e inadimplência
- Uma parcela muito grande dos adultos brasileiros está inadimplente (Mapa da Inadimplência, Serasa 🔎).
- A maioria das famílias tem algum tipo de dívida, com o cartão de crédito como principal modalidade (Pesquisa de Endividamento e Inadimplência do Consumidor, PEIC/CNC 🔎).
- Rotativo do cartão e cheque especial estão entre as linhas de crédito mais caras do país (Estatísticas de juros, Banco Central 🔎).

### 2.2 Apostas online (bets) e compulsão
- Com a regulamentação das apostas de quota fixa (Lei 14.790/2023) e o mercado autorizado pela Secretaria de Prêmios e Apostas (SPA/MF), o volume de transferências para bets cresceu de forma expressiva.
- O Banco Central publicou estudo sobre transferências via Pix para empresas de apostas, inclusive por beneficiários de programas sociais (Estudo Especial BCB sobre apostas, 2024 🔎).
- O jogo compulsivo é reconhecido como transtorno (CID-11 6C50, "gambling disorder") e está associado a endividamento, ansiedade e depressão.

### 2.3 Golpes financeiros
- Golpes via Pix, falsa central de atendimento e boleto falso atingem sobretudo quem já está em situação de fragilidade financeira (FEBRABAN / Fórum Brasileiro de Segurança Pública 🔎).

### 2.4 Por que é um problema de qualidade de vida
- O estresse financeiro está ligado a pior saúde mental, insônia e menor produtividade. Escalas validadas medem esse efeito: *InCharge Financial Distress/Financial Well-Being Scale* (Prawitz et al., 2006) e *CFPB Financial Well-Being Scale*.
- A Lei do Superendividamento (Lei 14.181/2021) reconhece a preservação do **mínimo existencial** como direito, o que mostra que o problema é social e não só individual.

### 2.5 O que já existe e onde falha

| Solução atual | Limitação |
|---|---|
| Apps de controle de gastos | Exigem disciplina manual. Não tratam compulsão nem dívida |
| Apps dos bancos | Visão de uma só instituição. Incentivo a oferecer mais crédito |
| Feirões de renegociação (Serasa, Desenrola) | Pontuais, sem plano nem acompanhamento comportamental |
| Educação financeira genérica | Não parte dos dados reais da pessoa |
| Grupos de apoio (Jogadores Anônimos, CAPS) | Desconectados da vida financeira do dia a dia |

**Lacuna:** nenhuma dessas soluções junta **dados reais multi-banco + entendimento comportamental + conhecimento jurídico/oficial + acompanhamento contínuo** em uma experiência única e acolhedora.

## 3. Stakeholders

| Stakeholder | Interesse | Como o PANDORA considera |
|---|---|---|
| Pessoa endividada / com compulsão | Sair do sufoco sem julgamento | Usuário principal, foco de UX acolhedora |
| Família / contato de confiança | Apoiar sem invadir | "Modo crise" opcional com consentimento |
| Credores e bancos | Recuperar crédito | Propostas de renegociação realistas |
| Órgãos de defesa do consumidor (Procon, Defensoria) | Cumprimento da Lei 14.181 | Encaminhamento e geração de documentação |
| Reguladores (BCB, CVM, ANPD, SPA/MF) | Segurança, privacidade, limites | Guardrails, LGPD, sem conselho regulado |
| Profissionais de saúde mental | Encaminhamento adequado | Sinais de risco levam a CVV/CAPS/JA |
| Equipe acadêmica / banca | Rigor, métricas, justificativas | ADRs, avaliação objetiva |

## 4. Personas

| Persona | Contexto | Dor principal | O que o PANDORA faz por ela |
|---|---|---|---|
| **Carla, 34**, atendente, 2 filhos | Rotativo do cartão + empréstimo pessoal, renda comprometida em ~60% | "Não sei por onde começar" | Raio-X + plano de reestruturação + guia da Lei 14.181 |
| **Diego, 24**, entregador de app | Apostas diárias depois do repasse semanal, esconde da família | Vergonha, perda de controle | Detector de compulsão + travas + apoio especializado |
| **Sr. Antônio, 67**, aposentado | Consignado + foi vítima de golpe da falsa central | Medo e desconfiança | Guardião antifraude + análise de prints + proteção de benefício |
| **Júlia, 29**, CLT, recém-quitou dívidas | Quer não voltar ao vermelho e começar a investir | Insegurança, excesso de informação | Orçamento, metas, perfil e trilha educacional |

As personas também são usadas para gerar **dados sintéticos** e o **golden set** de avaliação ([06](06-riscos-e-metricas.md)).

## 5. Hipóteses a validar

1. Ver a própria situação consolidada e explicada em linguagem simples reduz a ansiedade e aumenta a adesão ao plano.
2. Detectar padrões de aposta automaticamente, com abordagem não estigmatizante, aumenta a adoção de travas voluntárias.
3. Respostas ancoradas em RAG sobre fontes oficiais são mais corretas e confiáveis que um LLM puro (comparação na Semana 3).
4. Um sistema multiagente especializado supera um agente único em qualidade e segurança das respostas em cenários financeiros complexos.

## 6. Fontes de evidência (corpus inicial)

- Banco Central do Brasil: estatísticas de juros, Relatório de Cidadania Financeira, estudos especiais, Open Finance Brasil.
- CVM: Portal do Investidor, Resoluções 19/2021 e 20/2021 (consultoria e análise), 30/2021 (suitability).
- Tesouro Nacional: Tesouro Direto.
- Legislação: Lei 14.181/2021 (Superendividamento), Decretos do mínimo existencial, Lei 14.790/2023 (apostas), CPC art. 833 (impenhorabilidade), Lei 8.009/1990 (bem de família), LGPD (Lei 13.709/2018).
- SPA/MF: lista de operadoras de apostas autorizadas e regras de jogo responsável.
- Serasa, CNC/PEIC, Procon, consumidor.gov.br, FEBRABAN.
- Literatura: escalas de bem-estar financeiro (CFPB, InCharge), estudos sobre jogo compulsivo.
