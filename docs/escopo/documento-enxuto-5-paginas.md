# PROJETO PANDORA: ARQUITETURA MULTIAGENTE E APRENDIZADO DE MÁQUINA PARA REESTRUTURAÇÃO DE DÍVIDAS, MITIGAÇÃO DE COMPULSÃO FINANCEIRA E PROTEÇÃO AO CONSUMIDOR

**Documento Científico de Concepção e Escopo (Versão Executiva de 5 Páginas) — Challenge 2 (CBL)**
**Grande Ideia (Big Idea):** Qualidade de Vida — *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor"*
**Área Temática:** Finanças Pessoais, Superendividamento, Comportamento Financeiro Compulsivo e Segurança Digital · **Outubro de 2026**

---

## RESUMO

A digitalização do Sistema Financeiro Nacional promoveu liquidez instantânea, mas reduziu as fricções cognitivas para o endividamento de alto custo, apostas online de quota fixa (*bets*) e golpes digitais. No Brasil (2024–2026), 81,7 milhões de adultos estão inadimplentes, o rotativo do cartão atinge 435,9% a.a. e R$ 20,8 bilhões/mês são transferidos via Pix para casas de apostas, comprometendo a saúde mental e o mínimo existencial familiar. Este artigo executivo especifica o escopo do **PANDORA**, um copiloto multiagente baseado no princípio *"determinístico onde é possível, probabilístico onde é necessário"*, que integra motores matemáticos exatos, *Machine Learning* transacional/temporal, RAG Híbrido sobre fontes do BCB, CVM e legislação consumerista (Leis nº 14.181/2021, 14.690/2023 e 14.790/2023), e interface multimodal (voz e imagem) sob *guardrails* de privacidade (LGPD) e acolhimento em crise (`CVV 188`).

**Palavras-chave:** Inteligência Artificial Multiagente; Superendividamento; Mínimo Existencial; Transtorno do Jogo (*Bets*); RAG Híbrido; Qualidade de Vida.

---

## SUMÁRIO

1. **Introdução e Cenário Escolhido** ........................................................................................................................ p. 01
2. **Formulação do Problema e Evidências Empíricas** ............................................................................................ p. 01
3. **Questão Essencial (*Essential Question*) e 10 Questões Norteadoras (*Guiding Questions*)** ......................... p. 02
4. **Mapeamento de *Stakeholders* do Ecossistema (6 Atores)** ............................................................................... p. 02
5. **Perfis Comportamentais e Personas do Sistema (P01 a P10)** ........................................................................... p. 03
6. **Engenharia de Requisitos em 4 Graus de Necessidade (RF01–RF18 e RNF01–RNF09)** .................................. p. 03
7. **Análise de Riscos Arquiteturais, Clínicos e Regulatórios (R01 a R08)** ............................................................. p. 04
8. **Premissas Metodológicas e Operacionais** ......................................................................................................... p. 05
9. **Metodologia de Avaliação, Métricas de Sucesso, Limites e Validações Experimentais** ................................. p. 05
10. **Referências Bibliográficas e Normativas** ........................................................................................................ p. 05

---

## 1. Introdução e Cenário Escolhido

O **PANDORA** atua no cenário da **saúde financeira e proteção de famílias brasileiras em situação de superendividamento, compulsão em apostas ou vulnerabilidade a fraudes digitais**. Embora o Pix e o Open Finance tenham democratizado o acesso financeiro, a ausência de fricção decisória agravou o endividamento em linhas caras e a exposição a golpes. As soluções existentes tratam o problema de modo fragmentado e ignoram seus determinantes jurídicos e comportamentais (**Tabela 1**).

**Tabela 1 — Comparativo entre as alternativas atuais de mercado e o diferencial arquitetural do PANDORA.**

| Alternativa Atual | Limitação Estrutural | Diferencial Científico do PANDORA |
|---|---|---|
| **Apps de Bancos** | Visão restrita à própria instituição e conflito de interesses (lucram com juros do rotativo, parcelamentos e consignado). | Consolidação multi-banco (Open Finance / upload) e atuação **100% isenta**, focada em minimizar o Custo Efetivo Total (CET). |
| **Planilhas e Apps de Gastos** | Exigem lançamento manual contínuo e ignoram gatilhos de ansiedade, apostas noturnas ou renda variável (MEI/app). | Classificação supervisionada via ML, detecção de anomalias temporais (madrugada/pós-repasse) e orçamento por piso de renda. |
| **Feirões de Renegociação** | Atuam apenas no estoque da dívida passada sem proteger o caixa mensal nem mudar hábitos (42% reincidem). | Blindagem prévia de 100% do **Mínimo Existencial** (Lei 14.181/2021), método *Avalanche* determinístico e educação contínua. |
| **Finfluencers / Educação Genérica** | Conteúdo teórico distante da fatura real ou enviesado por promessas de ganho rápido sem risco (*day trade*, cripto). | Educação *just-in-time* (Lusardi & Mitchell, 2014) ancorada nos dados do usuário via RAG oficial (BCB/CVM) e trava regulatória. |
| **Rede Pública (Procon/CAPS/JA)** | Acionada tardiamente; o cidadão chega ao atendimento sem contratos organizados ou memória de cálculo. | Triagem precoce de crise, emissão automática do Dossiê Legal (Lei 14.181) e encaminhamento imediato (`CVV 188`, CAPS AD, JA). |

*Fonte: Elaborado pelos autores (2026).*

---

## 2. Formulação do Problema e Evidências Empíricas

O problema central é a **deterioração severa da qualidade de vida provocada pela combinação entre superendividamento familiar, juros extremos, transtorno do jogo online (`CID-11 6C50`) e golpes digitais**, agravada pela assimetria informacional (**Tabela 2**). Na literatura clínica, o estresse financeiro (*financial distress*) é preditor direto de insônia, ansiedade, depressão e quebra familiar, mensurados pelas escalas **InCharge IFDFW** (Prawitz et al., 2006) e **CFPB Financial Well-Being Scale** (CFPB, 2017).

**Tabela 2 — Evidências empíricas e macroeconômicas do problema financeiro no Brasil (2024–2026).**

| Eixo do Problema | Indicador Oficial no Brasil | Fonte e Período | Impacto Direto na Qualidade de Vida |
|---|---|---|---|
| **1. Inadimplência Crônica** | **81,7 milhões** de inadimplentes (recorde); **332 milhões** de dívidas; média de **R$ 6.598,13/pessoa**. | Serasa Experian (mar./2026) | Alta de 38% em 10 anos; **42% já estavam negativados há uma década**, provando que renegociar sem reeducar gera reincidência. |
| **2. Endividamento Familiar** | **81,7%** das famílias endividadas (pico de **82,0%**); **29,6%** em atraso; **12,5%** não terão como pagar. | CNC — Pesquisa PEIC (jul.–set./2026) | O **cartão de crédito** atinge **85,3%** das famílias endividadas; os juros competem com alimentação, moradia e energia elétrica. |
| **3. Juros Extremos e Opacidade** | Rotativo do cartão a **435,9% a.a.**; cheque especial a **~130% a.a.**; pessoal livre a **61,7% a.a.** | BCB (API SGS) / Agência Brasil (2026) | O cidadão paga o "mínimo da fatura" desconocendo o teto legal de 100% da dívida original (**Lei nº 14.690/2023**). |
| **4. Compulsão em *Bets*** | **R$ 20,8 bilhões/mês** via Pix a 56 operadoras de apostas; **24 milhões** de apostadores mensais. | BCB — Estudo Especial nº 119/2024 | Forte concentração entre 20 e 30 anos e drenagem de renda vital (**R$ 3 bi** enviados por **5 milhões** de beneficiários do Bolsa Família). |
| **5. Golpes Digitais (Pix/Boleto)** | **24 milhões** de vítimas em 12 meses; prejuízo de **quase R$ 29 bilhões** (**R$ 1.198/vítima**). | Datafolha / FBSP (ago./2025) | Idosos são os mais atingidos por boletos adulterados e falsas centrais telefônicas, desestruturando a renda previdenciária. |

*Fonte: Elaborado pelos autores com base em Serasa (2026), CNC (2026), BCB (2024, 2026) e Datafolha/FBSP (2025).*

---

## 3. Questão Essencial (*Essential Question*) e 10 Questões Norteadoras (*Guiding Questions*)

> **Questão Essencial da Equipe:** *"Como agentes de Inteligência Artificial, apoiados em evidências empíricas e fontes normativas confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?"*

**Tabela 3 — Matriz das 10 Questões Norteadoras (*Guiding Questions*) e soluções arquitetadas no PANDORA.**

| Cód. | Eixo Científico | Questão Norteadora (*Guiding Question*) | Resposta Metodológica e Solução Arquitetada no PANDORA |
|---|---|---|---|
| **GQ01** | **Diagnóstico** | *O que o usuário endividado ou compulsivo não consegue enxergar sozinho em seu extrato?* | A perda líquida real em *bets* (descontando pequenos prêmios), o efeito composto do pagamento mínimo (CET), o somatório de parcelamentos em múltiplos cartões e a parcela intocável do seu **mínimo existencial**. |
| **GQ02** | **Economia Comportamental** | *Quando uma intervenção de IA muda de fato o comportamento sem gerar culpa ou abandono?* | Quando ocorre próxima ao gatilho temporal (pós-repasse ou entre 23h–03h), sem tom moralista, aplicando **fricção positiva voluntária** (*cooling-off* de 24h–48h e *nudges* de custo de oportunidade — Thaler & Sunstein, 2008). |
| **GQ03** | **Direitos Legais** | *Quais normas oficiais os cidadãos desconhecem e que reduzem o custo da dívida?* | Repactuação global com preservação do mínimo existencial (**Lei 14.181/2021**), teto de 100% no rotativo (**Lei 14.690/2023**), teto de 8% a.m. no cheque especial (**Res. CMN 4.765/19**) e impenhorabilidade salarial/familiar (**CPC art. 833 / Lei 8.009/90**). |
| **GQ04** | **Antifraude** | *Como proteger idosos e vulneráveis sob coação de golpes de Pix ou boleto falso?* | Canal multimodal (**Voz STT/TTS + Foto**) que valida os 47 dígitos FEBRABAN e CNPJ do boleto, detecta engenharia social em telas e gera roteiro imediato do **MED Pix (Res. BCB 147/2021)** em até 80 dias. |
| **GQ05** | **Renda Variável** | *Como planejar o orçamento de autônomos (MEI) e entregadores cuja renda oscila?* | Orçamento baseado em **Piso de Renda Conservador**, segregação entre despesas MEI e pessoais, e previsão de fluxo de caixa para 30, 60 e 90 dias via séries temporais (**Prophet / ETS**). |
| **GQ06** | **Determinismo** | *Como impedir que o LLM alucine cálculos financeiros ou invente leis?* | Princípio **"Determinístico onde dá, probabilístico onde precisa"**: matemática financeira 100% em funções Python testadas e respostas jurídicas restritas ao **RAG Híbrido (`pgvector` + BM25)** com citação obrigatória. |
| **GQ07** | **Regulação CVM** | *Como ensinar a montar reserva e investir sem violar normas de consultoria da CVM?* | Cumprimento das **Res. CVM 19, 20 e 30/2021**: *suitability* educacional, simulação com séries SGS (`432`, `12`, `433`) sobre **classes gerais de ativos** e **Recusa Educativa** para pedidos de indicação de ativos específicos. |
| **GQ08** | **Segurança LGPD** | *Como processar extratos e relatos sensíveis com privacidade e defesa contra ataques?* | *Privacy by Design* (**Lei 13.709/2018**): mascaramento local de PII antes do *LLM Gateway*, exclusão total sob demanda, isolamento de OCR contra *Prompt Injection* indireto e operação 100% *read-only*. |
| **GQ09** | **Saúde Mental** | *Qual é o limite ético da IA diante de sofrimento psíquico severo ou risco à vida?* | Jamais substituir psicólogos ou psiquiatras. Ao detectar marcadores de desespero agudo no `Compliance Guard`, suspende-se a cobrança financeira e aciona-se o **Protocolo de Crise** (`CVV 188`, CAPS AD, JA). |
| **GQ10** | **Qualidade de Vida** | *Como comprovar cientificamente o ganho de qualidade de vida além dos números?* | Aferição pré e pós-intervenção nas escalas psicométricas **InCharge IFDFW (Prawitz, 2006)** e **CFPB (2017)**, somada a 100% do mínimo existencial preservado, queda do CET médio e dias sem apostas. |

*Fonte: Elaborado pelos autores (2026).*

---

## 4. Mapeamento de *Stakeholders* do Ecossistema (6 Atores)

**Tabela 4 — Matriz analítica de interesses, restrições e entrega de valor para os 6 stakeholders do ecossistema.**

| # | Stakeholder | Interesse Primário | Dores e Restrições Atuais | Entrega de Valor pelo PANDORA |
|---|---|---|---|---|
| **1** | **Usuário Principal** *(Endividado / Compulsivo / Alvo de Golpe)* | Sair das dívidas, frear compulsão e recuperar a paz mental sem julgamento. | Vergonha, dificuldade com planilhas, medo de bloqueio salarial e vulnerabilidade a fraudes. | PWA acessível (texto, voz, foto), tom acolhedor, privacidade estrita e plano que blinda o mínimo existencial. |
| **2** | **Família / Contato de Confiança** *(Secundário / Cuidador)* | Proteger o sustento doméstico e apoiar o familiar em recaídas ou golpes sem invadir sua autonomia. | Falta de visibilidade até o esgotamento das economias da casa; conflitos familiares. | **"Modo Crise"** e **"Alerta de Golpe"** mediante **duplo consentimento (*opt-in*)** e painel de cuidado delegado. |
| **3** | **Defesa do Consumidor** *(Procon, Defensoria, CEJUSC)* | Aplicar a Lei 14.181/2021 e agilizar audiências globais de repactuação de dívidas. | Cidadão comparece sem contratos, sem o CET das dívidas e sem o cálculo de gastos essenciais. | Gera o **Dossiê de Repactuação**: Mapa de Dívidas, comparativo SGS/BCB e memória do Mínimo Existencial. |
| **4** | **Saúde Mental e Apoio** *(CVV 188, CAPS AD, JA)* | Receber encaminhamento tempestivo de pessoas em crise aguda ou transtorno do jogo (`6C50`). | Apps financeiros ignoram sinais de desespero humano; IAs não podem improvisar terapia clínica. | Guardrail interrompe o fluxo financeiro em risco emocional e conecta em 1 toque ao `CVV 188`, CAPS AD e JA. |
| **5** | **Órgãos Reguladores** *(BCB, CVM, ANPD, SPA/MF)* | Proteção de dados (LGPD), combate a *bets* ilegais, uso correto do MED Pix e vedação à consultoria irregular. | Proliferação de *bets* clandestinas, vazamento de PII e recomendação ilegal de valores mobiliários. | Mascaramento de PII, filtro na lista oficial da SPA/MF, roteiro MED Pix e bloqueio estrito CVM (Res. 19/20). |
| **6** | **Credores, Bancos e Birôs** *(Open Finance, Serasa)* | Recuperar crédito vencido de modo sustentável, reduzindo a quebra de acordos (*re-default*). | Acordos fechados em feirões sem análise do orçamento real do devedor quebram já no 2º mês. | Simula propostas (*Avalanche* / *Bola de Neve*) estritamente compatíveis com a margem pós-mínimo existencial. |

*Fonte: Elaborado pelos autores (2026).*

---

## 5. Perfis Comportamentais e Personas do Sistema (P01 a P10)

O sistema foi modelado sobre **10 personas exclusivas** detalhadas em `docs/personas/`: **5 personas nucleares** (que conduzem as 15 jornadas de validação experimental, **Tabela 5**) e **5 personas complementares** de cobertura socioeconômica estendida (**Tabela 6**).

**Tabela 5 — Síntese das 5 personas nucleares de validação experimental (P01 a P05).**

| ID | Persona e Ocupação | Arquétipo e Renda | Contexto e Gatilho da Crise | Barreiras de Uso | Intervenção no PANDORA (Módulos e Leis) |
|---|---|---|---|---|---|
| **P01** | **Carla Mendes (34)**<br/>Atendente CLT · Mãe solo (2 filhos) | **Superendividamento**<br/>R$ 2.850/mês *(Fixa)* | 73,6% da renda é mínimo existencial (R$ 2.100). R$ 4.200 no rotativo (**448% a.a.**), empréstimo e luz atrasada. | Medo de retenção salarial ao conectar banco; pavor de penhora; siglas ("CET"). | Upload de PDFs, blindagem dos R$ 2.100 vitais, método *Avalanche*, **CPC art. 833** e dossiê **Lei 14.181/2021** (*Mód. 1 e 3*). |
| **P02** | **Diego Oliveira (24)**<br/>Entregador de app (Moto) | **Compulsão em *Bets***<br/>~R$ 1.120/sem *(Variável)* | Aposta via Pix após o repasse de quarta-feira e escala valores entre **23h e 03h** (*chasing losses*). Atrasou a moto. | Reatância a sermões; impulso de desligar travas de madrugada; ilusão de ganho. | Lista **SPA/MF**, **perda líquida real**, *nudge* ("5 tanques"), trava com **janela de 24h–48h** e atalho JA/CVV (*Mód. 2 e 5*). |
| **P03** | **Sr. Antônio (67)**<br/>Aposentado INSS · Viúvo | **Golpes e Consignado**<br/>R$ 2.412/mês *(Fixa)* | 30% em consignado. Pagou **boleto falso de R$ 1.198** no WhatsApp e sofreu assédio de "falsa central" (R$ 1.800). | Vergonha pós-golpe; presbiopia (telas pequenas); dificuldade de digitar; pânico. | Interface **Voz (STT/TTS) + Foto**, validação FEBRABAN/CNPJ, guia falado do **MED Pix (Res. 147/21)** e taxa INSS (`SGS 25467`) (*Mód. 5 e 7*). |
| **P04** | **Mariana Costa (28)**<br/>Designer *freelancer* (MEI) | **Impulso e 4 Cartões**<br/>R$ 3.200–5.800 *(Volátil)* | 22 parcelamentos em 4 bancos, compras noturnas por ansiedade, mistura MEI × PF e paga fatura com outro cartão. | Abandona planilhas em 5 dias; insumo MEI categorizado como lazer; renda volátil. | **Open Finance multi-banco**, reclassificação em 1 toque, `Isolation Forest` (impulso) e fluxo de caixa 30/60/90d (`Prophet`) (*Mód. 1, 2 e 4*). |
| **P05** | **Júlia Santos (31)**<br/>Analista CLT · Pós-dívida | **Reserva e Reconstrução**<br/>R$ 4.500/mês *(Poupa R$ 500)* | Quitou dívidas há 3 meses; medo de recair (42% reincidem) e assédio de *finfluencers* prometendo ganhos irreais. | Frustração com recusa seca da IA; desmotivação em metas longas; dúvida Selic/CDI. | Micro-metas ("Dias de Tranquilidade"), simulador **SGS (`432`, `12`, `433`)** e **Recusa Educativa CVM** (liquidez/FGC) (*Mód. 4 e 6*). |

*Fonte: Elaborado pelos autores (2026).*

**Tabela 6 — Síntese das 5 personas complementares de cobertura socioeconômica estendida (P06 a P10).**

| ID | Persona e Renda | Contexto e Gatilho da Crise | Módulos Acionados e Fundamentação Legal / Científica |
|---|---|---|---|
| **P06** | **Rosângela Souza (43)** · Diarista + Bolsa Família (R$ 1.560/mês) | Filho (19) aposta com a senha do app dela (R$ 1.100 em 60d) + agiota a 20% a.m. | **Raio-X por Áudio + Proteção do Benefício + Envelopes:** Estudo BCB nº 119/2024 (Bolsa Família), Lei 14.790/2023 e Lei 1.521/1951 (usura). |
| **P07** | **Rafael Martins (39)** · Professor Estadual (R$ 5.200/mês) | Cheque especial 24 de 30 dias/mês (7,9% a.m.) + crédito pessoal caro para cobrir limite. | **Raio-X + Reestruturação + Previsão de Saldo:** Séries SGS `25463`/`25464`, Res. CMN 4.765/2019 (teto 8% a.m.) e portabilidade (Res. 4.292/13). |
| **P08** | **Lucas Andrade (19)** · Estagiário de TI (R$ 1.400/mês) | 1º cartão estourado (R$ 1.050 de R$ 1.200) + golpe de loja falsa no Instagram (R$ 389 Pix). | **Antifraude + Copiloto Multimodal + Educação *Just-in-Time*:** Datafolha/FBSP (2025), MED Pix (Res. BCB 147/21), CDC art. 49 e Lei 14.690/23. |
| **P09** | **Fernanda Rocha (46)** · Recém-demitida (~R$ 2.500 Seguro) | Demissão após 12 anos; FGTS retido no saque-aniversário e pressão para arriscar rescisão. | **Raio-X Documental (TRCT/FGTS) + Previsão de Fôlego + Guardrail CVM:** Escala CFPB (2017, choque), Leis 8.036/90 e 13.932/19 (FGTS). |
| **P10** | **Patrícia Nogueira (53)** · Técnica de Enfermagem (R$ 3.900–4.800) | Descontos indevidos no INSS da mãe (81, Alzheimer inicial) + remédios no próprio cartão. | **Painel do Cuidador (Acesso Delegado) + Antifraude + Orçamento do Cuidado:** Estatuto da Pessoa Idosa (Lei 10.741/03), CC art. 1.783-A e LGPD. |

*Fonte: Elaborado pelos autores (2026).*

---

## 6. Engenharia de Requisitos em 4 Graus de Necessidade

**Tabela 7 — Índice metodológico dos 4 Graus de Necessidade para priorização de escopo no ciclo de 7 semanas.**

| Grau de Necessidade | Classificação MoSCoW | Critério de Governança e Entrega no Projeto |
|---|---|---|
| 🔴 **Grau 1 — Must-Have** | **Essencial / Bloqueante (MVP)** | Indispensável para responder à *Essential Question*, garantir segurança jurídica/ética (LGPD, CVM, Anti-Alucinação, Crise) e validar as personas. |
| 🟠 **Grau 2 — Should-Have** | **Importante / Alta Relevância** | Elevado valor analítico e comportamental (previsão de fluxo de caixa, *score* explicável, travas com *cooling-off* e dossiê legal). Entra após o Grau 1. |
| 🟡 **Grau 3 — Could-Have** | **Desejável (Se Sobrar Tempo)** | Incrementos de conveniência (check-in de humor, alerta familiar opt-in, minuta para *consumidor.gov.br*) implementados caso haja folga nas Semanas 5–6. |
| ⚪ **Grau 4 — Won't-Have now** | **Futuro (Roadmap Pós-CBL)** | Fora do escopo de implementação deste semestre por exigir homologação bancária produtiva ou licença de iniciação de pagamento (ITP Pix). |

*Fonte: Elaborado pelos autores (2026).*

**Tabela 8 — Catálogo de Requisitos Funcionais (RF01 a RF18) distribuídos nos 4 Graus de Necessidade.**

| Cód. | Módulo | Especificação Técnica do Requisito Funcional | Personas | Grau de Necessidade |
|---|---|---|---|---|
| **RF01** | 1. Raio-X | Ingestão e normalização via **Open Finance *sandbox*** (Pluggy/Belvo) **e** upload de **OFX, CSV e PDF**. | P01, P04, P07, P09 | 🔴 **Grau 1 — Must-Have** |
| **RF02** | 1. Raio-X | Classificação supervisionada de transações (8 categorias), segregando o **Mínimo Existencial** e insumos MEI. | Todas (P01–P10) | 🔴 **Grau 1 — Must-Have** |
| **RF03** | 1. Raio-X | Consolidação do **Mapa de Dívidas** (CET, saldo, atraso) comparado às séries da **API SGS/BCB** (`22022`, `25477`, `25463`, `25467`). | P01, P03, P07, P10 | 🔴 **Grau 1 — Must-Have** |
| **RF04** | 2. Compulsão | Detecção de apostas (*bets*) via MCC `7995` e **lista SPA/MF**, calculando **perda líquida real** e concentração noturna/pós-repasse. | P02, P06 | 🔴 **Grau 1 — Must-Have** |
| **RF05** | 2. Compulsão | Diálogo empático sem estigma com disparo imediato do **Protocolo de Crise** (`CVV 188`, CAPS AD, JA) em sofrimento agudo. | P02, P01, P06 | 🔴 **Grau 1 — Must-Have** |
| **RF06** | 3. Dívidas | Motor determinístico **Avalanche** vs. **Bola de Neve**, blindando 100% do Mínimo Existencial (**Lei 14.181**) e teto do rotativo (**Lei 14.690**). | P01, P07, P08 | 🔴 **Grau 1 — Must-Have** |
| **RF07** | 5. Guardião | Inspeção multimodal (**Foto/PDF + OCR**) validando linha digitável FEBRABAN/CNPJ e gerando roteiro do **MED Pix (Res. BCB 147/21)**. | P03, P08, P10 | 🔴 **Grau 1 — Must-Have** |
| **RF08** | 6. Educação | Respostas normativas via **RAG Híbrido (`pgvector` + BM25)** com **citação obrigatória** e trava CVM contra indicação de ativos (**Res. 19/20**). | P05, P09, P01, P03 | 🔴 **Grau 1 — Must-Have** |
| **RF09** | 7. Copiloto | Interface conversacional unificada com suporte a **texto, voz (STT/TTS) e imagem/PDF**, orquestrada em `LangGraph`. | P03, P06, Todas | 🔴 **Grau 1 — Must-Have** |
| **RF10** | 1. Raio-X | Cálculo explicável do **Score de Saúde Financeira (0–100)** e botão de reclassificação em 1 toque (*human-in-the-loop*). | P04, P05, P07 | 🟠 **Grau 2 — Should-Have** |
| **RF11** | 2/5. Proteção | Detecção de impulso via `Isolation Forest`, **Travas Voluntárias com espera de 24h–48h** e guia de autoexclusão `.bet.br` (**Lei 14.790**). | P02, P04, P06 | 🟠 **Grau 2 — Should-Have** |
| **RF12** | 3. Dívidas | Emissão automática do **Dossiê de Repactuação Legal (Lei 14.181/2021)** exportável para Procon, Defensoria e CEJUSC. | P01, P10 | 🟠 **Grau 2 — Should-Have** |
| **RF13** | 4. Orçamento | **Orçamento Adaptativo por Piso de Renda** (MEI/autônomo) e **Previsão de Caixa 30/60/90 dias** (`Prophet / ETS`). | P04, P09, P07 | 🟠 **Grau 2 — Should-Have** |
| **RF14** | 6. Educação | Questionário de **Perfil (*Suitability* Educacional — Res. CVM 30)** e **Simulador de Reserva** com séries Selic (`432`), CDI (`12`) e IPCA (`433`). | P05, P09, P08 | 🟠 **Grau 2 — Should-Have** |
| **RF15** | 2. Compulsão | **Diário de Check-in Emocional / Humor** rápido para correlacionar estresse laboral e gatilhos de compras/apostas noturnas. | P04, P02 | 🟡 **Grau 3 — Se sobrar tempo** |
| **RF16** | 5. Guardião | **"Modo Crise / Contato de Confiança"** e painel de cuidador com duplo *opt-in* para alertas de tentativa de golpe ou quebra de trava. | P02, P03, P10 | 🟡 **Grau 3 — Se sobrar tempo** |
| **RF17** | 3. Dívidas | Gerador de **Carta de Contraproposta ao Credor** fundamentada na simulação *Avalanche* para envio no *consumidor.gov.br*. | P01, P07 | 🟡 **Grau 3 — Se sobrar tempo** |
| **RF18** | Externo | Iniciação direta de pagamentos Pix (ITP), bloqueio no *core banking* das instituições ou integração oficial WhatsApp Business API. | Todas | ⚪ **Grau 4 — Roadmap Futuro** |

*Fonte: Elaborado pelos autores (2026).*

**Tabela 9 — Catálogo de Requisitos Não Funcionais (RNF01 a RNF09) e metas técnicas nos 4 Graus.**

| Cód. | Categoria | Especificação Técnica do Requisito Não Funcional | Meta / Limite Técnico | Grau de Necessidade |
|---|---|---|---|---|
| **RNF01** | Privacidade LGPD | Mascaramento local de PII (CPF, nome, conta) antes do *LLM Gateway* e exclusão total sob demanda. | **0,0% vazamento PII** (Lei 13.709/18) | 🔴 **Grau 1 — Must-Have** |
| **RNF02** | Compliance CVM | Bloqueio contra recomendação de ativos específicos e operação 100% *read-only* (sem movimentação). | **Bloqueio $\ge 95,0\%$** (Res. CVM 19/20) | 🔴 **Grau 1 — Must-Have** |
| **RNF03** | Determinismo | Proibição de conta aritmética livre no LLM; cálculos financeiros executados 100% em funções Python tipadas. | **Erro numérico = $0,00\%$** (`pytest`) | 🔴 **Grau 1 — Must-Have** |
| **RNF04** | Fidelidade RAG | Respostas jurídicas/regulatórias exigem recuperação no corpus oficial com exibição de norma e link. | **Faithfulness $\ge 0,90$** e **100% citação** | 🔴 **Grau 1 — Must-Have** |
| **RNF05** | Segurança IA | Isolamento estrutural de textos extraídos via OCR de boletos/PDFs contra *Prompt Injection* indireto. | **Bloqueio $\ge 95,0\%$** em injeções | 🔴 **Grau 1 — Must-Have** |
| **RNF06** | Arquitetura / SLA | Arquitetura Hexagonal (*Ports & Adapters*) em `FastAPI` e *LLM Gateway* agnóstico de provedor. | **Latência $p95 \le 8\text{s}$** (texto) / **$\le 12\text{s}$** (voz) | 🟠 **Grau 2 — Should-Have** |
| **RNF07** | Acessibilidade | Interface PWA aderente a **WCAG 2.2 AA** (alto contraste, fontes escaláveis, alvos $\ge 44\text{px}$ e voz para idosos). | **Lighthouse A11y $\ge 90$** | 🟠 **Grau 2 — Should-Have** |
| **RNF08** | Cache e Custo | Cache em `Redis` para séries temporais SGS/BCB e consultas frequentes sobre a Lei 14.181/2021. | **Redução $\ge 30\%$** de chamadas externas | 🟡 **Grau 3 — Se sobrar tempo** |
| **RNF09** | Escala Bancária | Cluster multi-região ativo-ativo e homologação produtiva direta no diretório Open Finance Brasil. | SLA $\ge 99,99\%$ em produção real | ⚪ **Grau 4 — Roadmap Futuro** |

*Fonte: Elaborado pelos autores (2026).*

---

## 7. Análise de Riscos Arquiteturais, Clínicos e Regulatórios

**Tabela 10 — Matriz de riscos críticos (R01 a R08) e estratégias de mitigação.**

| Cód. | Risco Identificado | Prob. | Impacto | Estratégia de Mitigação Arquitetural e Operacional | Requisitos |
|---|---|---|---|---|---|
| **R01** | **Alucinação jurídica ou financeira** (juros, prazo MED ou Lei 14.181 errados) | Alta | Muito Alto | Cálculos restritos a funções Python determinísticas; RAG híbrido (`pgvector` + BM25 + *rerank*) com citação obrigatória e abstenção segura. | RF06, RF08, RNF03, RNF04 |
| **R02** | **Dano psicológico a vulnerável** (gerar culpa ou gatilho em compulsão/crise) | Média | Muito Alto | Diretrizes de linguagem não estigmatizante; classificador no `Compliance Guard` que suspende cobranças e aciona `CVV 188`, CAPS AD e JA. | RF05, GQ09 |
| **R03** | **Enquadramento como consultoria irregular perante a CVM** | Média | Alto | Restrição à educação e simulação de classes gerais; filtro de saída que converte pedidos de recomendação em Recusa Educativa. | RF08, RF14, RNF02 |
| **R04** | **Exposição de dados financeiros pessoais (violação à LGPD)** | Média | Muito Alto | Uso exclusivo de dados sintéticos e *sandbox* no projeto; *PII Masking* local antes do *LLM Gateway*; exclusão sob demanda. | RNF01 |
| **R05** | **Sequestro de agente via *Prompt Injection* indireto em boleto/PDF** | Média | Alto | Encapsulamento de texto OCR como dado não confiável; validação determinística FEBRABAN (47 dígitos); operação 100% *read-only*. | RF07, RNF05 |
| **R06** | **Falsos positivos/negativos na classificação de gastos ou *bets*** | Média | Médio | Hibridização de regras exatas (CNPJ SPA/MF e MCC `7995`) com ML supervisionado e reclassificação em 1 toque (*human-in-the-loop*). | RF02, RF04, RF10 |
| **R07** | **Indisponibilidade da API Sandbox Open Finance ou API SGS/BCB** | Média | Médio | Inversão de dependência (`BankDataPort`) aceitando upload OFX/CSV/PDF e cache local das séries SGS/BCB em `Redis`/JSON. | RF01, RNF06, RNF08 |
| **R08** | **Extrapolação de escopo no ciclo acadêmico de 7 semanas** | Alta | Alto | Corte disciplinado pelos **4 Graus de Necessidade**, blindando 100% dos itens **Grau 1 (Must-Have)** antes de avançar aos Graus 2 e 3. | Seção 6 |

*Fonte: Elaborado pelos autores (2026).*

---

## 8. Premissas Metodológicas e Operacionais

1. **Ambiente Acadêmico Controlado:** Desenvolvimento em 7 semanas (equipe de 3 a 5 integrantes) utilizando exclusivamente dados sintéticos (`amostra_transacoes_sinteticas_personas.csv`) e conectores *sandbox*, sem coleta de dados bancários reais de terceiros.
2. **Operação Estritamente *Read-Only*:** O PANDORA não custodia recursos, não inicia Pix e não envia ordens a corretoras; travas comportamentais operam por fricção positiva voluntária (*cooling-off*) aliada a guias de bloqueio nativo nos bancos e sites `.bet.br`.
3. **Fronteira Profissional e Clínica:** Diagnósticos, dossiês da Lei 14.181/2021 e roteiros MED Pix organizam a defesa do cidadão, mas não substituem defensores públicos, advogados, psicólogos ou psiquiatras.
4. **Fontes Públicas e Arquitetura Agnóstica:** Disponibilidade pública das séries SGS/BCB, lista SPA/MF e normas oficiais, orquestradas via *LLM Gateway* híbrido (modelos locais de triagem + modelos em nuvem).

---

## 9. Metodologia de Avaliação, Métricas de Sucesso, Limites e Validações Experimentais

**Tabela 11 — Protocolo consolidado de métricas matemáticas, limites de aprovação (*thresholds*), massas de teste e validação experimental.**

| Domínio | Componente / Experimento Avaliado | Métrica Matemática | Limite Mínimo (*Threshold*) | Massa de Teste (*Golden Set*) | Protocolo de Teste e Validação Experimental |
|---|---|---|---|---|---|
| **1. ML & Motor Exato** (`services/ml`) | **1.1 Classificador de Transações** (8 classes) | **F1-Score Macro** e *Recall* Vital | **F1 $\ge 0,85$** · Recall Vital $\ge 0,90$ | $\ge 1.000$ transações sintéticas rotuladas + *Sparkov* | *5-fold Stratified Cross-Validation* + auditoria de matriz de confusão (proteção de mínimo existencial e MEI). |
| **1. ML & Motor Exato** | **1.2 Detector de Apostas (*Bets*)** | **Recall** e **Precision** | **Recall $\ge 0,95$** · **Precision $\ge 0,90$** | Transações `P02`/`P06` + lista **SPA/MF** + MCC `7995` | Teste automatizado CI verificando detecção de Pix fracionados, janela pós-repasse ($\le 120\text{m}$) e madrugada (23h–03h). |
| **1. ML & Motor Exato** | **1.3 Detector de Anomalias e Fraudes** | **Recall** e **Falsos Positivos (FPR)** | **Recall $\ge 0,80$** · **FPR $\le 5,0\%$** | Personas `P03`, `P04`, `P08` + *PaySim / ULB* | Calibração da `Isolation Forest` garantindo `anomaly_score >= 0.80` em transferências noturnas e boletos divergentes. |
| **1. ML & Motor Exato** | **1.4 Previsor de Caixa (30/60/90d)** | **MAPE** (*Erro Percentual Médio*) | **MAPE $\le 15,0\%$** (janela 30d) | Séries de 12 meses (`P01`, `P04`, `P07`) | *Rolling-origin backtesting* (treina meses 1..9, prevê mês 10) verificando alerta de furo de caixa com $\ge 15\text{d}$ de antecedência. |
| **1. ML & Motor Exato** | **1.5 Motor de Juros, CET e Avalanche** | **Erro Absoluto Máximo** | **Erro $= \text{R\$ } 0,00$ ($0,00\%$)** | Casos de borda Price, SAC, IOF e Lei 14.690/23 | Suíte unitária `pytest` confrontando funções Python contra gabaritos oficiais da Calculadora do Cidadão do BCB. |
| **2. RAG Híbrido** (`evals/`) | **2.1 Fidelidade e Relevância (Ragas)** | **Faithfulness**, **Context Precision** e **Relevancy** | **Faithfulness $\ge 0,90$** · **Prec. $\ge 0,80$** · **Rel. $\ge 0,85$** | **Golden Set:** 100 questões (Leis 14.181, 14.690, 14.790, MED e CVM) | Decomposição proposicional no framework *Ragas* verificando suporte estrito nos *chunks* do `pgvector` + BM25. |
| **2. RAG Híbrido** | **2.2 Citação Oficial e Abstenção Segura** | **Citation Rate** e **Abstention Rate** | **100% Citação** · **$\ge 90\%$ Abstenção** | 50 questões normativas + 20 perguntas *out-of-domain* | Validador Pydantic exigindo lei/artigo/URI válida e teste de recusa segura sem fabricar normas inexistentes. |
| **2. RAG Híbrido** | **2.3 Experimento: LLM Puro vs. RAG** | **Ganho Factual ($\Delta \text{Accuracy}$)** | **Superação $\ge +25\text{ p.p.}$** sobre LLM puro | 100 questões pareadas (`Controle` vs. `PANDORA RAG`) | Avaliação cega por rubrica (0 = alucinado, 1 = parcial sem fonte, 2 = exato com fonte) por juiz humano + *LLM-as-a-Judge*. |
| **3. Agentes & Segurança** | **3.1 Roteamento e Sucesso End-to-End** | **Routing Accuracy** e **Task Completion** | **Routing $\ge 0,90$** · **Task $\ge 0,80$ (12/15)** | 50 intenções mistas + **15 Jornadas Nucleares (`P01–P05`)** | Teste de integração em `LangGraph` verificando seleção correta de agente/ferramenta no 1º turno e entrega do artefato final. |
| **3. Agentes & Segurança** | **3.2 Inspeção Multimodal e Guardrails** | **Detecção OCR** e **Adversarial Block Rate** | **Fraude $\ge 0,90$** · **Block $\ge 0,95$** · **PII/Crise $100\%$** | 20 boletos/telas + **Suíte *Red-Teaming* (40 ataques)** | Validação FEBRABAN + OCR e bloqueio em CI/CD contra recomendação CVM, *prompt injection*, vazamento PII e omissão `CVV 188`. |
| **4. Qualidade de Vida (QoL)** | **4.1 Impacto Humano, Clareza e Blindagem Vital** | **Escalas InCharge/CFPB**, **Quiz** e **Cobertura Vital** | **$\Delta \text{QoL} > 0$** · **Quiz $\ge 80\%$** · **Vital $= 100\%$** · **CSAT $\ge 4,2/5$** | Piloto guiado (Semana 7) nos cenários das personas | Pré/pós-teste psicométrico (Prawitz, 2006; CFPB, 2017), quiz de 5 perguntas decisórias e auditoria de 100% do mínimo existencial preservado. |

*Fonte: Elaborado pelos autores (2026).*

---

## 10. Referências Bibliográficas e Normativas

1. **BANCO CENTRAL DO BRASIL (BCB).** *Estudo Especial nº 119/2024: Mercado de apostas online no Brasil*; *Resolução BCB nº 147/2021 (MED Pix)*; *API SGS (Séries 12, 432, 433, 22022, 25463, 25464, 25467, 25477)*. Brasília: BCB, 2021–2026.
2. **BRASIL.** *Lei nº 14.181/2021* (Superendividamento e Mínimo Existencial); *Lei nº 14.690/2023* (Teto do rotativo); *Lei nº 14.790/2023* (*Bets*); *Lei nº 8.009/1990* (Bem de família); *Lei nº 10.741/2003* (Estatuto do Idoso); *Lei nº 13.105/2015* (CPC, art. 833); *Lei nº 13.709/2018* (LGPD).
3. **COMISSÃO DE VALORES MOBILIÁRIOS (CVM).** *Resoluções CVM nº 19/2021, nº 20/2021 e nº 30/2021 (Suitability)*. Rio de Janeiro: CVM, 2021.
4. **CNC.** *Pesquisa de Endividamento e Inadimplência do Consumidor (PEIC)*. Rio de Janeiro: CNC, jul.–set. 2026.
5. **CFPB.** *Measuring financial well-being: A guide to using the CFPB Financial Well-Being Scale*. Washington, D.C.: CFPB, 2017.
6. **DATAFOLHA; FBSP.** *Levantamento Nacional sobre Vitimização por Golpes Financeiros Digitais (Pix e Boletos)*. São Paulo: FBSP, ago. 2025.
7. **LUSARDI, A.; MITCHELL, O. S.** The Economic Importance of Financial Literacy. *Journal of Economic Literature*, v. 52, n. 1, p. 5–44, 2014.
8. **PRAWITZ, A. D. et al.** InCharge Financial Distress/Financial Well-Being Scale. *Journal of Financial Counseling and Planning*, v. 17, n. 1, p. 34–50, 2006.
9. **SERASA EXPERIAN.** *Mapa da Inadimplência no Brasil — Edição de 10 Anos*. São Paulo: Serasa, mar. 2026.
10. **THALER, R. H.; SUNSTEIN, C. R.** *Nudge: Improving Decisions About Health, Wealth, and Happiness*. Yale University Press, 2008.
11. **WORLD HEALTH ORGANIZATION (WHO).** *ICD-11 — 6C50 Gambling disorder*. Geneva: WHO, 2022.
