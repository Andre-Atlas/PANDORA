# 02 · Essential Question e 10 Guiding Questions

[⬅️ Anterior: 01 · Cenário e Problema](01-cenario-e-problema.md) · [Voltar ao índice](README.md) · [Próximo: 03 · Stakeholders e Personas ➡️](03-stakeholders-e-personas.md)

---

## 1. Essential Question da Equipe

> **Big Idea:** Qualidade de Vida — *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*
>
> **Essential Question:**
> ### *"Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?"*

---

## 2. As 10 Guiding Questions (Perguntas-Guia)

Para responder à *Essential Question* com rigor científico, técnico e jurídico, o projeto desdobrou a investigação em **10 perguntas-guia** organizadas em dois blocos: **Compreensão Humana & Jurídica (GQ01 a GQ05)** e **Engenharia de IA, Regulação & Impacto (GQ06 a GQ10)**.

### Bloco A · Compreensão Humana, Comportamental e Jurídica (GQ01–GQ05)

| # | Eixo | Guiding Question | Direcionamento e Resposta do PANDORA |
|---|---|---|---|
| **GQ01** | **Visibilidade** | *O que a pessoa endividada ou compulsiva **não consegue enxergar** sozinha na própria movimentação financeira?* | Ela não enxerga: (a) a perda líquida real acumulada em microtransferências via Pix para *bets* (descontando pequenos prêmios ilusórios); (b) o custo exponencial (CET anualizado) de pagar apenas o mínimo da fatura; (c) a soma de dezenas de parcelamentos espalhados em múltiplos cartões; e (d) qual fatia da renda compõe seu **mínimo existencial** intocável. |
| **GQ02** | **Mudança de Hábito** | *Em que momento uma intervenção de IA (alerta, trava, conversa) muda de fato o comportamento, e quando ela vira ruído ou culpa?* | Sermões morais geram vergonha e desinstalação. A mudança ocorre quando a IA atua **próxima ao gatilho temporal** (minutos após o repasse semanal ou entre 23h e 03h), com **linguagem não estigmatizante** e **fricção positiva voluntária** (*cooling-off period* de 24h–48h para desativar travas e *nudges* de custo de oportunidade — Thaler & Sunstein, 2008). |
| **GQ03** | **Direitos Legais** | *Que informação oficial (direitos, programas, normas) as pessoas desconhecem e que poderia reduzir drasticamente o custo das dívidas?* | Os cidadãos desconhecem: (1) a **repactuação global de dívidas** em até 5 anos preservando o mínimo existencial (**Lei 14.181/2021**); (2) o teto de **100% do valor original** para juros do rotativo (**Lei 14.690/2023**); (3) o teto de **8% a.m.** no cheque especial (**Res. CMN 4.765/2019**); e (4) a **impenhorabilidade** de salário, aposentadoria e bem de família (**CPC art. 833 / Lei 8.009/90**). |
| **GQ04** | **Prevenção a Golpes** | *Como proteger cidadãos vulneráveis (especialmente idosos) no instante em que estão sob pressão de um golpe de Pix ou boleto falso?* | Com um canal multimodal de baixíssima fricção (**Voz STT/TTS + Foto**) onde o agente `Guardião` cruza a linha digitável FEBRABAN e o CNPJ/CPF recebedor com o logotipo do boleto, detecta engenharia social em prints e, se o Pix já ocorreu, entrega os dados prontos para acionar o **MED (Res. BCB 147/2021)** em até 80 dias. |
| **GQ05** | **Renda Variável** | *Como planejar o orçamento e evitar o "rolo" de cartões para trabalhadores de app e autônomos (MEI) cuja renda oscila toda semana?* | Substituindo regras fixas (como 50-30-20) por um **Orçamento por Piso de Renda Base**, separando receitas PJ/MEI de gastos pessoais e usando séries temporais (**Prophet / ETS**) para prever furos de caixa em 30, 60 e 90 dias antes do vencimento das faturas. |

---

### Bloco B · Engenharia de IA, Regulação, Ética e Mensuração (GQ06–GQ10)

| # | Eixo | Guiding Question | Direcionamento e Resposta do PANDORA |
|---|---|---|---|
| **GQ06** | **Determinismo vs. LLM** | *Como impedir que um modelo de linguagem (LLM) alucine cálculos de juros, prazos legais ou invente leis que prejudiquem o devedor?* | Pelo princípio **"Determinístico onde dá, probabilístico onde precisa"**: toda matemática financeira (juros compostos, CET, Tabela Price, método Avalanche) roda em funções Python determinísticas (erro $0\%$), e toda afirmação normativa exige **RAG Híbrido (`pgvector` + BM25)** com citação obrigatória ou abstenção segura. |
| **GQ07** | **Fronteira CVM** | *Como ensinar uma pessoa recém-saída das dívidas a montar sua Reserva de Emergência e investir sem violar as normas de consultoria da CVM?* | Aplicando as **Resoluções CVM 19, 20 e 30/2021**: o sistema identifica o perfil educacional (*suitability*), simula rendimentos reais com as séries do BCB (**Selic `432`, CDI `12`, IPCA `433`**) em **classes gerais de ativos**, e o `Compliance Guard` aplica uma **Recusa Educativa** diante de pedidos de recomendação de ações ou títulos específicos. |
| **GQ08** | **Privacidade (LGPD)** | *Como processar extratos bancários, boletos e relatos emocionais garantindo conformidade com a LGPD e defesa contra ataques?* | Operando sob *Privacy by Design* (**Lei 13.709/2018**): mascaramento local de PII (CPF, nome, conta) antes do *LLM Gateway*, exclusão total sob demanda (incluindo *embeddings*), isolamento de OCR contra *Prompt Injection* indireto e operação 100% *read-only* (nenhuma ferramenta movimenta dinheiro). |
| **GQ09** | **Ética em Crise** | *Qual é o limite ético de atuação de um agente de IA diante de um usuário em sofrimento psíquico severo por dívidas ou vício em apostas?* | Jamais tentar atuar como psicólogo ou psiquiatra. Ao detectar marcadores de desespero agudo ou risco à vida no `Compliance Guard`, o sistema interrompe a cobrança de metas e aciona imediatamente o **Fluxo de Crise**, conectando o usuário em 1 clique ao **CVV (`188`)**, **CAPS AD** e **Jogadores Anônimos (JA)**. |
| **GQ10** | **Qualidade de Vida** | *Como comprovar cientificamente que o sistema melhorou a **qualidade de vida** do usuário, e não apenas indicadores contábeis?* | Avaliando a evolução antes e depois da jornada nas escalas psicométricas internacionais **InCharge IFDFW (Prawitz et al., 2006)** e **CFPB Financial Well-Being Scale (2017)**, combinadas à proteção de 100% do mínimo existencial, à queda do CET médio e aos dias consecutivos sem apostas. |
