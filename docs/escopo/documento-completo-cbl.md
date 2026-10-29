# Documento de Concepção e Especificação do Problema — Projeto PANDORA

> **Challenge 2 · CBL (Challenge-Based Learning)**
> **Big Idea:** Qualidade de Vida — *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*
> **Tema do Grupo:** Finanças Pessoais, Superendividamento e Comportamento Financeiro Compulsivo
> **Projeto:** **PANDORA** (*Copiloto de IA para sair das dívidas, controlar gastos compulsivos e reconstruir a vida financeira*)

---

## 1. Cenário Escolhido

O **PANDORA** insere-se no cenário das **finanças pessoais e saúde financeira de famílias brasileiras em situação de vulnerabilidade, superendividamento ou compulsão financeira**. No Brasil contemporâneo (2024–2026), a digitalização acelerada do sistema financeiro trouxe avanços inegáveis de inclusão e velocidade (Pix, Open Finance, crédito digital instantâneo), mas reduziu drasticamente a fricção para o endividamento de alto custo, para as apostas online de quota fixa (*bets*) e para a atuação de quadrilhas de engenharia social e golpes digitais.

Nesse cenário, milhões de cidadãos tomam decisões financeiras críticas sob forte sobrecarga cognitiva, estresse emocional, vergonha e assimetria de informação. As soluções atuais falham porque operam de forma isolada e desconectada da realidade comportamental e jurídica do cidadão:

| Alternativa Atual no Mercado | Principal Limitação / Falha Estrutural | O que o PANDORA Faz de Diferente |
|---|---|---|
| **Apps de Bancos e Carteiras Digitais** | Enxergam apenas a própria instituição e possuem conflito de interesses (lucram oferecendo mais crédito rotativo, parcelamentos e consignado). | Visão consolidada multi-banco (Open Finance / upload) e atuação **100% isenta**, focada em reduzir o Custo Efetivo Total (CET) pago pelo usuário. |
| **Planilhas e Gerenciadores de Gastos** | Exigem disciplina manual constante, pressupõem estabilidade emocional e ignoram gatilhos de compulsão, ansiedade ou renda variável. | Classificação automática via ML, detecção de anomalias temporais (gastos e apostas de madrugada) e orçamento adaptativo. |
| **Feirões de Renegociação** *(Serasa, Desenrola)* | Atuam pontualmente sobre o estoque da dívida passada, sem proteger o fluxo de caixa mensal nem mudar o hábito que gerou a dívida (42% reincidem). | Blindagem prévia do **Mínimo Existencial** (Lei 14.181/2021), simulação determinística de capacidade real de pagamento e acompanhamento contínuo. |
| **Educação Financeira Genérica e *Finfluencers*** | Conteúdo teórico distante da fatura real do usuário ou enviesado por promessas de ganho rápido sem risco (*day trade*, cripto, pirâmides). | Educação financeira *just-in-time* (Lusardi & Mitchell, 2014) ancorada nos próprios números do usuário e em fontes oficiais via RAG (BCB, CVM, Tesouro), sob guardrails regulatórios. |
| **Rede de Defesa e Saúde Mental** *(Procon, Defensoria, CAPS, JA)* | Acionada tarde demais e desconectada dos dados financeiros cotidianos; o cidadão chega sem documentação organizada. | Detecção precoce de sinais de crise, geração automática do dossiê de repactuação legal e encaminhamento acolhedor imediato (`CVV 188`, CAPS, JA). |

---

## 2. Problema

O problema central enfrentado pelo projeto é a **espiral de deterioração da qualidade de vida causada pela combinação entre superendividamento estrutural, juros extremos, compulsão por apostas online (*bets*) e golpes financeiros digitais**, agravada pela invisibilidade dos padrões de gasto e pelo desconhecimento de direitos legais de proteção ao consumidor.

### 2.1 Evidências Quantitativas e Empíricas do Problema
Os dados oficiais e levantamentos setoriais consolidados em [`docs/evidencias/`](../evidencias/README.md) comprovam a magnitude e a urgência do problema no Brasil:

| Eixo do Problema | Indicador Oficial no Brasil | Fonte e Referência | Consequência Direta na Qualidade de Vida |
|---|---|---|---|
| **1. Inadimplência Crônica** | **81,7 milhões** de inadimplentes (recorde histórico); **332 milhões** de dívidas; média de **R$ 6.598,13/pessoa**. | [Serasa — Mapa da Inadimplência: 10 anos](https://www.serasa.com.br/imprensa/10-anos-do-mapa-de-inadimplencia/) (mar/2026) | Aumento de 38% em uma década; **42% já estavam negativados há 10 anos**, provando que renegociar sem reeducar e criar reserva gera reincidência. |
| **2. Endividamento Familiar** | **81,7%** das famílias endividadas (pico de **82,0%** em jul–ago/2026); **29,6%** em atraso; **12,5%** não terão como pagar. | [CNC — Pesquisa PEIC Nacional](https://portaldocomercio.org.br/acoes-institucionais/cnc-inadimplencia-e-endividamento-das-familias-brasileiras-recuam-em-setembro/) (jul–set/2026) | O **cartão de crédito** está em **85,3%** das famílias endividadas; o pagamento de juros compete diretamente com alimentação, moradia e luz. |
| **3. Assimetria e Juros Extremos** | Rotativo do cartão a **435,9% a.a.**; cheque especial a **~130% a.a.**; crédito livre PF a **61,7% a.a.** | [Agência Brasil / BCB (SGS)](https://agenciabrasil.ebc.com.br/economia/noticia/2026-03/juros-do-cartao-de-credito-pesam-mais-para-familias-em-fevereiro) e [Senado Notícias](https://www12.senado.leg.br/noticias/infomaterias/2026/05/dividas-em-recorde-assombram-as-familias-brasileiras) (2026) | O cidadão paga o "mínimo da fatura" achando que está regularizando a situação e desconhece o teto legal de 100% da dívida original (**Lei 14.690/2023**). |
| **4. Compulsão em Apostas (*Bets*)** | **R$ 20,8 bilhões/mês** enviados via Pix a 56 casas de apostas; **24 milhões** de apostadores mensais. | [Banco Central — Estudo Especial nº 119/2024](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf) (set/2024) | Concentração entre jovens de 20 a 30 anos e comprometimento de renda vital (R$ 3 bi enviados por 5 milhões de beneficiários do Bolsa Família em um único mês). |
| **5. Epidemia de Golpes Digitais** | **24 milhões** de vítimas de golpes via Pix ou boleto falso em 12 meses; prejuízo de **quase R$ 29 bilhões** (**R$ 1.198/vítima**). | [Datafolha / FBSP / Rádio Senado](https://www12.senado.leg.br/radio/1/noticia/2025/08/18/mais-de-24-milhoes-de-pessoas-foram-vitimas-de-golpes-pelo-pix) (ago/2025) | Idosos são as principais vítimas de boletos adulterados e falsas centrais telefônicas; um único golpe desestrutura o orçamento previdenciário familiar. |

### 2.2 O Impacto Clínico e Social na Qualidade de Vida
A literatura científica demonstra que o estresse financeiro (*financial distress*) é causa direta de **insônia, transtornos de ansiedade, depressão, conflitos familiares e queda de produtividade no trabalho**, mensurados por escalas psicométricas validadas como a *InCharge Financial Distress/Financial Well-Being Scale* (Prawitz et al., 2006) e a *CFPB Financial Well-Being Scale* (2017). Adicionalmente, o jogo compulsivo é catalogado pela OMS como transtorno mental (**CID-11 `6C50` — *Gambling Disorder***), e a legislação brasileira (**Lei nº 14.181/2021**) consagra o **mínimo existencial** como direito fundamental de dignidade humana.

---

## 3. Essential Question e 10 Guiding Questions da Equipe

### 3.1 Essential Question da Equipe
> **"Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?"**

### 3.2 As 10 Guiding Questions (Perguntas-Guia) e Respostas do Projeto

Para desdobrar a *Essential Question* em decisões de engenharia, psicologia econômica, ciência de dados e direito do consumidor, a equipe estruturou **10 perguntas-guia**:

| # | Eixo Temático | Guiding Question (Pergunta-Guia) | Resposta e Solução Arquitetada no PANDORA |
|---|---|---|---|
| **GQ01** | **Visibilidade e Diagnóstico** | *O que a pessoa endividada ou compulsiva **não consegue enxergar** sozinha na própria movimentação financeira?* | Ela não enxerga: (a) a perda líquida real acumulada em microtransferências via Pix para *bets* (descontando pequenos prêmios ilusórios); (b) o custo exponencial (CET anualizado) de pagar apenas o mínimo do cartão; (c) o somatório de dezenas de parcelamentos espalhados em múltiplos cartões; e (d) qual fatia da sua renda compõe o **mínimo existencial** intocável. |
| **GQ02** | **Mudança Comportamental** | *Em que momento uma intervenção de IA (alerta, trava, conversa) muda de fato o comportamento, e quando ela vira ruído ou culpa?* | Sermões morais geram vergonha e desinstalação do app. A intervenção funciona quando ocorre **próxima ao gatilho temporal** (ex.: minutos após cair o repasse semanal ou entre 23h e 03h da manhã), usa **linguagem livre de estigma** e aplica **fricção positiva voluntária** (*cooling-off period* de 24h–48h para desativar travas e *nudges* de custo de oportunidade — Thaler & Sunstein, 2008). |
| **GQ03** | **Direitos e Assimetria Legal** | *Que informação oficial (direitos, programas, normas) as pessoas desconhecem e que poderia reduzir drasticamente o custo das dívidas?* | Os consumidores desconhecem: (1) a **repactuação global de dívidas** em até 5 anos com preservação do mínimo existencial (**Lei 14.181/2021**); (2) o teto de **100% do valor original** para juros do rotativo (**Lei 14.690/2023**); (3) o teto de **8% a.m.** no cheque especial (**Res. CMN 4.765/2019**); e (4) a **impenhorabilidade** do salário, da aposentadoria e do bem de família (**CPC art. 833 / Lei 8.009/90**). |
| **GQ04** | **Prevenção e Resposta a Golpes** | *Como proteger cidadãos vulneráveis (especialmente idosos) no instante em que estão sob pressão de um golpe de Pix ou boleto falso?* | Oferecendo um canal multimodal de baixíssima fricção (**Voz STT/TTS + Foto**) onde o agente `Guardião` cruza a linha digitável do boleto (código FEBRABAN e CNPJ/CPF do recebedor) com o logotipo impresso, identifica gatilhos de engenharia social em prints de conversa e, caso o Pix já tenha ocorrido, entrega os dados prontos para acionar o **MED (Res. BCB 147/2021)** em até 80 dias. |
| **GQ05** | **Renda Variável e Autônomos** | *Como planejar o orçamento e evitar o "rolo" de cartões para trabalhadores de aplicativo e autônomos (MEI) cuja renda oscila toda semana?* | Abandonando orçamentos estáticos (como 50-30-20 sobre renda fixa) em favor de um **Orçamento por Piso de Renda Base**, separando transações PJ/MEI de gastos pessoais e utilizando modelos de séries temporais (**Prophet / ETS**) para prever furos de caixa em 30, 60 e 90 dias antes do fechamento das faturas. |
| **GQ06** | **Determinismo vs. IA Generativa** | *Como impedir que um modelo de linguagem (LLM) alucine cálculos de juros, prazos legais ou invente leis que prejudiquem o devedor?* | Aplicando o princípio arquitetural **"Determinístico onde dá, probabilístico onde precisa"**: toda matemática financeira (juros compostos, CET, Tabela Price, método Avalanche/Bola de Neve) é executada por funções Python determinísticas e testadas; e toda afirmação jurídica exige recuperação via **RAG Híbrido (`pgvector` + BM25)** com citação verificável ou recusa explícita. |
| **GQ07** | **Fronteira Regulatória (CVM)** | *Como ensinar uma pessoa recém-saída das dívidas a montar sua Reserva de Emergência e investir sem violar as normas de consultoria da CVM?* | Aplicando as **Resoluções CVM nº 19/2021, 20/2021 e 30/2021**: o sistema identifica o perfil educacional (*suitability*), simula rendimentos reais usando as séries oficiais do BCB (**Selic `432`, CDI `12`, IPCA `433`**) sobre **classes gerais de ativos**, e o `Compliance Guard` bloqueia qualquer recomendação de ações, fundos ou títulos bancários específicos, convertendo a recusa em ensino de critérios (liquidez D+0, risco soberano/FGC e indexação). |
| **GQ08** | **Privacidade e Segurança (LGPD)** | *Como processar extratos bancários, boletos e relatos emocionais sensíveis garantindo conformidade com a LGPD e defesa contra ataques?* | Operando sob *Privacy by Design* (**Lei 13.709/2018**): mascaramento local de PII (CPF, nome, conta) antes do *LLM Gateway*, consentimento granular para dados comportamentais, exclusão total sob demanda (inclusive *embeddings*), isolamento de textos extraídos via OCR contra *Prompt Injection* indireto e operação 100% *read-only* (nenhuma ferramenta movimenta dinheiro). |
| **GQ09** | **Ética e Saúde Mental em Crise** | *Qual é o limite ético de atuação de um agente de IA diante de um usuário em sofrimento psíquico severo por dívidas ou vício em apostas?* | O PANDORA jamais tenta substituir psicólogos, psiquiatras ou assistentes sociais. Ao detectar marcadores linguísticos de desespero agudo ou risco à vida no `Compliance Guard`, o sistema interrompe imediatamente a cobrança de metas financeiras e aciona o **Fluxo de Crise**, conectando o usuário em um clique ao **CVV (`188`)**, **CAPS AD** e **Jogadores Anônimos (JA)**. |
| **GQ10** | **Mensuração de Qualidade de Vida** | *Como comprovar cientificamente que o sistema melhorou a **qualidade de vida** do usuário, e não apenas indicadores contábeis?* | Avaliando o impacto antes e depois da jornada por meio das escalas psicométricas internacionais **InCharge IFDFW (Prawitz et al., 2006)** e **CFPB Financial Well-Being Scale (2017)**, combinadas à proteção de 100% do mínimo existencial, à redução do CET médio da carteira de dívidas e ao número de dias consecutivos sem apostas. |

---

## 4. Mapa de Stakeholders

O ecossistema do PANDORA conecta **6 grupos de stakeholders** diretamente envolvidos na jornada de recuperação financeira, proteção legal e acolhimento do usuário:

```mermaid
flowchart TB
    subgraph Diretos["Núcleo Direto (Usuário e Rede Familiar)"]
        U["👤 1. Usuário Principal<br/>(Endividado / Compulsivo / Alvo de Golpe)"]
        F["👨‍👩‍👧 2. Família / Contato de Confiança<br/>(Apoio próximo com consentimento)"]
    end

    subgraph Protecao["Rede Pública de Defesa e Saúde"]
        DEF["⚖️ 3. Defesa do Consumidor<br/>(Procon · Defensoria · CEJUSC)"]
        SAU["🩺 4. Saúde Mental e Apoio<br/>(CVV 188 · CAPS AD · Jogadores Anônimos)"]
    end

    subgraph SistemaFinanceiro["Regulação e Mercado Financeiro"]
        REG["🏛️ 5. Órgãos Reguladores<br/>(BCB · CVM · ANPD · SPA/MF)"]
        CRED["🏦 6. Credores, Bancos e Agregadores<br/>(Open Finance · Serasa · Consumidor.gov.br)"]
    end

    U <-->|"Diagnóstico, Plano, Travas e Educação"| P(("PANDORA<br/>Copiloto Multiagente"))
    P -.->|"Modo Crise / Alerta de Golpe (Opt-in duplo)"| F
    P -->|"Dossiê estruturado da Lei 14.181/2021"| DEF
    P -->|"Encaminhamento imediato em risco emocional"| SAU
    REG -->|"Limites legais, LGPD, API SGS e Lista SPA/MF"| P
    CRED <-->|"Leitura via Sandbox e Propostas Sustentáveis"| P
```

| # | Stakeholder | Interesse Principal | Dores / Restrições Atuais | Como o PANDORA Entrega Valor |
|---|---|---|---|---|
| **1** | **Pessoa Endividada, Compulsiva ou Alvo de Golpe** *(Usuário Primário)* | Sair do sufoco financeiro, estancar perdas com juros ou apostas e recuperar a paz mental sem julgamento. | Vergonha de expor a situação; baixa tolerância a planilhas complexas; medo de bloqueio salarial; vulnerabilidade a golpes. | Interface PWA acessível (texto, áudio e foto), tom empático, privacidade estrita e plano de ação realista que preserva o mínimo existencial. |
| **2** | **Família / Contato de Confiança** *(Usuário Secundário)* | Proteger o orçamento doméstico e apoiar o familiar em momentos de recaída ou tentativa de golpe, sem invadir sua privacidade. | Falta de visibilidade até que a dívida ou o golpe já tenha consumido as economias da casa; risco de conflitos conjugais/familiares. | **"Modo Crise"** e botão **"Compartilhar Alerta de Golpe"** baseados em **duplo consentimento (opt-in)**, enviando apenas alertas pontuais acordados. |
| **3** | **Órgãos de Defesa do Consumidor** *(Procon, Defensoria Pública, CEJUSC)* | Garantir a aplicação efetiva da Lei do Superendividamento (Lei 14.181/2021) e agilizar audiências globais de repactuação. | O cidadão chega ao atendimento sem os contratos, sem saber o CET das dívidas e sem o cálculo de suas despesas essenciais. | Gera o **Dossiê de Repactuação**: Mapa de Dívidas consolidado, comparativo com taxas do BCB e cálculo detalhado do Mínimo Existencial familiar. |
| **4** | **Rede de Saúde Mental e Apoio** *(CVV 188, CAPS AD, Jogadores Anônimos)* | Receber encaminhamento rápido e seguro de pessoas em sofrimento psíquico agudo ou com transtorno do jogo (`CID-11 6C50`). | Ferramentas financeiras ignoram sinais de desespero humano; por outro lado, IAs não podem tentar fazer terapia clínica. | Guardrail de segurança interrompe o fluxo financeiro ao detectar risco emocional e conecta o usuário em 1 toque ao `CVV 188`, CAPS e JA. |
| **5** | **Órgãos Reguladores** *(BCB, CVM, ANPD, SPA/MF)* | Assegurar proteção de dados (LGPD), combate a apostas ilegais, uso correto do MED Pix e vedação à consultoria irregular de valores mobiliários. | Proliferação de *bets* clandestinas, vazamento de dados sensíveis e robôs/influenciadores fazendo recomendação ilegal de ativos. | Mascaramento de PII, cruzamento com a lista oficial da SPA/MF, guia do MED Pix e bloqueio estrito de recomendação de produtos (Res. CVM 19/20). |
| **6** | **Credores, Bancos e Birôs de Renegociação** *(Open Finance, Serasa)* | Recuperar crédito vencido de maneira sustentável, reduzindo a quebra de acordos (*re-default*) e o custo de inadimplência definitiva. | Acordos fechados em feirões sem análise do orçamento real do devedor são abandonados já na segunda ou terceira parcela. | Simula propostas de renegociação (Avalanche/Bola de Neve) que cabem exatamente na margem disponível após o mínimo existencial do usuário. |

---

## 5. Personas e Jornadas de Uso

As **5 personas exclusivas** do projeto foram modeladas sobre os dados da Serasa, CNC/Peic, BCB e Datafolha/FBSP, possuindo fichas individuais completas dentro da pasta **[`docs/personas/`](../personas/README.md)** e transações sintéticas em **[`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)**:

| # | Persona | Arquétipo e Renda | Contexto e Gatilho da Crise | Dificuldades / Barreiras | Como o PANDORA Ajuda (Módulos) |
|---|---|---|---|---|---|
| **01** | **[Carla Mendes, 34](../personas/01-carla-superendividamento.md)**<br/>*(Atendente CLT · Mãe solo de 2 filhos)* | **Superendividamento Familiar**<br/>R$ 2.850/mês (Fixa) | **73,6%** da renda vai para o mínimo existencial (R$ 2.100). Acumula R$ 4.200 no rotativo (**448% a.a.**), empréstimo pessoal e conta de luz atrasada. | Medo de conectar o banco e ter o salário retido; pavor de penhora salarial; paralisia com siglas ("CET", "IOF"). | **Upload de PDFs** (sem exigir conexão bancária), blindagem dos R$ 2.100 vitais, método *Avalanche*, citação do **CPC art. 833** e dossiê da **Lei 14.181/2021** (*Módulos 1 e 3*). |
| **02** | **[Diego Oliveira, 24](../personas/02-diego-compulsao-bets.md)**<br/>*(Entregador de app · Moto)* | **Compulsão em Apostas (*Bets*)**<br/>~R$ 1.120/semana (Variável) | Aposta via Pix minutos após receber o repasse de quarta-feira e escala valores entre **23h e 03h** (*chasing losses*). Atrasou a parcela da moto. | Reatância a sermões morais; impulso de desligar limites na fissura da madrugada; ilusão de ganho com pequenos prêmios. | Cruzamento com lista **SPA/MF**, cálculo da **perda líquida real**, *nudge* pós-repasse ("5 tanques de gasolina"), trava noturna com **janela de 24h–48h** e atalho JA/CVV (*Módulos 2 e 5*). |
| **03** | **[Sr. Antônio Ferreira, 67](../personas/03-antonio-golpes-e-consignado.md)**<br/>*(Aposentado INSS · Viúvo)* | **Golpes Digitais e Consignado**<br/>R$ 2.412/mês (Fixa) | 30% do benefício em consignado. Pagou **boleto falso de R$ 1.198** via WhatsApp e sofreu assédio de "falsa central" pedindo Pix de R$ 1.800. | Humilhação pós-golpe; dificuldade visual com telas pequenas (presbiopia); lentidão para digitar; pânico sob pressão telefônica. | Interface **Voz (STT/TTS) + Foto**, checagem FEBRABAN/CNPJ de boletos, roteiro falado do **MED do Pix (Res. BCB 147/2021)** e auditoria da taxa INSS (`SGS 25467`) (*Módulos 5 e 7*). |
| **04** | **[Mariana Costa, 28](../personas/04-mariana-impulso-e-cartoes.md)**<br/>*(Designer MEI · Freelancer)* | **Impulso (*BNPL*) e 4 Cartões**<br/>R$ 3.200 a R$ 5.800/mês (Volátil) | Espalha 22 parcelamentos em 4 bancos digitais, faz compras noturnas por ansiedade de trabalho, mistura MEI × PF e paga fatura com outro cartão. | Abandona planilhas manuais em 5 dias; insumos de trabalho MEI classificados errado como "Lazer"; falha de orçamentos fixos. | Consolidação **Open Finance multi-banco**, reclassificação em 1 toque, detecção de impulso (`Isolation Forest`) e previsão de caixa 30/60/90d (`Prophet`) (*Módulos 1, 2 e 4*). |
| **05** | **[Júlia Santos, 31](../personas/05-julia-reconstrucao-e-reserva.md)**<br/>*(Analista CLT · Pós-dívida)* | **Reconstrução e Reserva Segura**<br/>R$ 4.500/mês (Fixa · Poupa R$ 500) | Quitou dívidas há 3 meses, mas tem trauma de recair (42% reincidem em 10 anos) e sofre bombardeio de *finfluencers* prometendo ganhos irreais. | Frustração se receber uma recusa seca da IA; desmotivação em metas longas (6 meses de reserva); dúvida entre Selic, CDI e IPCA. | Escada de micro-metas ("Dias de Tranquilidade"), simulador com séries **SGS (`432`, `12`, `433`)** e **Recusa Educativa CVM** ensinando critérios de liquidez e FGC (*Módulos 4 e 6*). |

---

## 6. Requisitos Funcionais e Não Funcionais

### 6.1 Índice de Grau de Necessidade (4 Graus de Priorização)

Para garantir uma entrega sólida dentro do ciclo de 7 semanas do Challenge e orientar o corte de escopo caso necessário, todos os requisitos do sistema estão distribuídos em **4 Graus de Necessidade**:

| Grau de Necessidade | Classificação (MoSCoW) | Definição e Critério de Entrega no Projeto |
|---|---|---|
| 🔴 **Grau 1 — Essencial (*Must-Have*)** | **Crítico / Bloqueante (MVP)** | Indispensável para responder à *Essential Question*, garantir a segurança jurídica/ética (LGPD, CVM, Anti-Alucinação) e rodar a demonstração principal das 5 personas. Sem ele, o sistema não pode ser aprovado. |
| 🟠 **Grau 2 — Importante (*Should-Have*)** | **Alta Relevância Funcional** | Agrega alto valor analítico, preditivo e comportamental à experiência das personas (ex.: previsão de fluxo de caixa, score explicável e travas com janela de espera). Entra logo após a estabilização do Grau 1. |
| 🟡 **Grau 3 — Desejável (*Could-Have*)** | **Se Sobrar Tempo (Incremento)** | Melhorias de conveniência e engajamento complementar que enriquecem o produto caso o cronograma das Semanas 5 e 6 permita, sem comprometer o núcleo caso fiquem de fora. |
| ⚪ **Grau 4 — Futuro (*Won't-Have now*)** | **Roadmap Pós-Challenge** | Funcionalidades mapeadas na visão de longo prazo do produto, mas explicitamente fora do escopo de implementação deste semestre por exigirem licenças regulatórias próprias ou integrações externas complexas. |

---

### 6.2 Requisitos Funcionais (RF) Distribuídos nos 4 Graus

| ID | Módulo | Descrição do Requisito Funcional | Persona Principal | Grau de Necessidade |
|---|---|---|---|---|
| **RF01** | 1. Raio-X Financeiro | Ingestão e normalização de transações via conector **Open Finance em modo sandbox** (Pluggy/Belvo) **e** via upload de arquivos **OFX, CSV e PDF** de extratos/faturas. | Carla, Mariana | 🔴 **Grau 1 — Must-Have** |
| **RF02** | 1. Raio-X Financeiro | Classificação automática de transações por categoria (Moradia, Alimentação, Dívidas/Juros, Apostas/Bets, Fraude Suspeita, Insumo MEI), separando o **Mínimo Existencial** dos demais gastos. | Todas | 🔴 **Grau 1 — Must-Have** |
| **RF03** | 1. Raio-X Financeiro | Consolidação do **Mapa de Dívidas** (credor, saldo, CET anual, atraso) com comparação automática frente às taxas médias oficiais da **API SGS do Banco Central** (`20749`, `25477`, `25463`, `25467`). | Carla, Sr. Antônio | 🔴 **Grau 1 — Must-Have** |
| **RF04** | 2. Detector de Compulsão | Identificação automática de apostas online (*bets*) cruzando MCC (`7995`), descrições e CNPJs com a **lista oficial da SPA/MF**, calculando a **perda líquida real** e o horário de concentração (madrugada/pós-salário). | Diego | 🔴 **Grau 1 — Must-Have** |
| **RF05** | 2. Detector de Compulsão | Abordagem conversacional empática (livre de julgamento) com disparo imediato do **Fluxo de Crise** (`CVV 188`, CAPS AD, Jogadores Anônimos) ao detectar marcadores de sofrimento agudo. | Diego, Carla | 🔴 **Grau 1 — Must-Have** |
| **RF06** | 3. Reestruturação | Motor determinístico de priorização de dívidas comparando os métodos **Avalanche** (maior CET) e **Bola de Neve** (menor saldo), blindando previamente 100% do Mínimo Existencial (**Lei 14.181/2021**) e checando o teto do rotativo (**Lei 14.690/2023**). | Carla | 🔴 **Grau 1 — Must-Have** |
| **RF07** | 5. Proteção (Guardião) | Inspeção multimodal (**Foto/PDF + OCR + Visão**) de boletos bancários e prints de WhatsApp, validando linha digitável FEBRABAN/CNPJ contra golpes e gerando roteiro passo a passo para acionar o **MED do Pix (Res. BCB 147/2021)**. | Sr. Antônio | 🔴 **Grau 1 — Must-Have** |
| **RF08** | 6. Educação & Investimento | Respostas normativas e educacionais fundamentadas em **RAG Híbrido (`pgvector` + BM25)** sobre fontes oficiais (BCB, CVM, Tesouro, Planalto) com **citação obrigatória** e bloqueio de recomendação de ativos específicos (**Res. CVM 19/20**). | Júlia, Carla, Sr. Antônio | 🔴 **Grau 1 — Must-Have** |
| **RF09** | 7. Copiloto Multimodal | Interface conversacional unificada com suporte a **texto, áudio/voz (STT/TTS) e upload de imagem/PDF**, orquestrada por grafo multiagente (`LangGraph`). | Sr. Antônio, Todas | 🔴 **Grau 1 — Must-Have** |
| **RF10** | 1. Raio-X Financeiro | Cálculo explicável do **Score de Saúde Financeira (0 a 100)** baseado em comprometimento de renda, custo médio da dívida, cobertura de reserva e dias sem apostas, com reclassificação de categoria em 1 toque (*human-in-the-loop*). | Mariana, Júlia | 🟠 **Grau 2 — Should-Have** |
| **RF11** | 2 e 5. Compulsão & Proteção | Detecção de compras por impulso noturnas via **`Isolation Forest`**, configuração de **Travas Voluntárias com janela de resfriamento (*cooling-off* de 24h–48h)** e guia interativo de autoexclusão nas plataformas `.bet.br` (**Lei 14.790/2023**). | Diego, Mariana | 🟠 **Grau 2 — Should-Have** |
| **RF12** | 3. Reestruturação | Geração automática do **Dossiê de Repactuação Legal (Lei 14.181/2021)** exportável, contendo relação de credores, cálculo do mínimo existencial e rascunho de proposta para o Procon/Defensoria/consumidor.gov.br. | Carla | 🟠 **Grau 2 — Should-Have** |
| **RF13** | 4. Orçamento & Metas | **Orçamento Adaptativo por Piso de Renda** (especial para autônomos/MEI) e **Previsão de Fluxo de Caixa para 30, 60 e 90 dias** (`Prophet / ETS`) com alerta preventivo de furo de caixa. | Mariana, Júlia | 🟠 **Grau 2 — Should-Have** |
| **RF14** | 6. Educação & Investimento | Questionário de **Perfil de Investidor (*Suitability* Educacional — Res. CVM 30/2021)** e **Simulador Determinístico de Reserva de Emergência** alimentado pelas séries Selic (`432`), CDI (`12`) e IPCA (`433`). | Júlia | 🟠 **Grau 2 — Should-Have** |
| **RF15** | 2. Detector de Compulsão | **Diário de Check-in Emocional / Humor** associado a gatilhos de gastos impulsivos (registro rápido por voz ou emoji para mapear correlação entre estresse laboral e consumo noturno). | Mariana, Diego | 🟡 **Grau 3 — Could-Have** *(Se sobrar tempo)* |
| **RF16** | 5. Proteção (Guardião) | Fluxo de **"Modo Crise / Contato de Confiança"** com duplo consentimento (*opt-in*), disparando notificação resumida para um familiar cadastrado quando uma trava noturna tenta ser rompida ou um boleto fraudulento é detectado. | Diego, Sr. Antônio | 🟡 **Grau 3 — Could-Have** *(Se sobrar tempo)* |
| **RF17** | 3. Reestruturação | Gerador de **Carta/Mensagem Personalizada de Contraproposta ao Credor**, formatada com os valores simulados pelo método Avalanche para copiar e colar no portal *consumidor.gov.br*. | Carla | 🟡 **Grau 3 — Could-Have** *(Se sobrar tempo)* |
| **RF18** | Ecossistema Externo | Execução direta de pagamentos, iniciação de transação Pix (ITP do Open Finance), bloqueio bancário direto no *core banking* das instituições ou integração via WhatsApp Business API oficial. | Todas | ⚪ **Grau 4 — Won't-Have now** *(Roadmap Futuro)* |

---

### 6.3 Requisitos Não Funcionais (RNF) Distribuídos nos 4 Graus

| ID | Categoria | Descrição do Requisito Não Funcional | Meta / Limite Técnico | Grau de Necessidade |
|---|---|---|---|---|
| **RNF01** | Privacidade e LGPD | **Privacy by Design:** Mascaramento obrigatório de PII (CPF, nome, conta, telefone) antes de qualquer chamada a LLMs externos e exclusão total de dados e *embeddings* sob demanda. | **0% de vazamento de PII** em logs e payloads externos (Lei 13.709/2018). | 🔴 **Grau 1 — Must-Have** |
| **RNF02** | Conformidade CVM | **Trava de Consultoria Regulada:** Bloqueio arquitetural contra recomendação de compra/venda de valores mobiliários específicos e operação 100% *read-only* (sem movimentação financeira). | **Bloqueio $\ge 95\%$** em suíte adversarial de indução a recomendação (Res. CVM 19/20). | 🔴 **Grau 1 — Must-Have** |
| **RNF03** | Exatidão Matemática | **Determinismo Financeiro:** Proibição de cálculos aritméticos livres no LLM; toda conta de juros, CET, amortização e saldo deve rodar em funções Python determinísticas tipadas. | **Erro numérico = $0,00\%$** na suíte de testes unitários financeiros. | 🔴 **Grau 1 — Must-Have** |
| **RNF04** | Confiabilidade RAG | **Rastreabilidade e Anti-Alucinação:** Respostas sobre leis, prazos e direitos exigem recuperação de contexto no corpus oficial com exibição do link/norma e data de referência. | **Faithfulness $\ge 0,90$** (Ragas) e **100% de citação** em consultas normativas. | 🔴 **Grau 1 — Must-Have** |
| **RNF05** | Segurança de IA | **Defesa contra Prompt Injection Indireto:** Isolamento estrutural (delimitadores de dados não confiáveis) de todo texto extraído via OCR de boletos, extratos PDF e prints de conversa. | **Bloqueio $\ge 95\%$** em ataques de *prompt injection* embutidos em documentos. | 🔴 **Grau 1 — Must-Have** |
| **RNF06** | Desempenho e Arquitetura | Arquitetura **Hexagonal (Ports & Adapters)** em `FastAPI`, **LLM Gateway** agnóstico de provedor e tempo de resposta adequado para uso interativo em web/mobile. | **Latência $p95 \le 8\text{ s}$** (texto) e **$\le 12\text{ s}$** (multimodal imagem/voz). | 🟠 **Grau 2 — Should-Have** |
| **RNF07** | Acessibilidade | Interface **PWA responsiva** seguindo diretrizes **WCAG 2.2 Nível AA** (alto contraste, fontes escaláveis, alvos de toque amplos $\ge 44\times 44\text{ px}$ e fluxo completo por voz para idosos). | **Score Lighthouse A11y $\ge 90$** e zero barreiras críticas de navegação por voz/teclado. | 🟠 **Grau 2 — Should-Have** |
| **RNF08** | Eficiência e Cache | Cache semântico e de séries temporais (no `Redis`) para consultas repetidas à API SGS do Banco Central e perguntas frequentes sobre a Lei 14.181/2021, reduzindo custo de tokens. | **Redução $\ge 30\%$** em chamadas repetidas de API externa e tempo de cache hit $< 200\text{ ms}$. | 🟡 **Grau 3 — Could-Have** *(Se sobrar tempo)* |
| **RNF09** | Alta Disponibilidade | Escalonamento horizontal automático multi-região com *failover* ativo-ativo e homologação direta no diretório central do Open Finance Brasil como instituição participante. | SLA de 99,99% em produção bancária real. | ⚪ **Grau 4 — Won't-Have now** *(Roadmap Futuro)* |

---

## 7. Riscos e Estratégias de Mitigação

| ID | Risco Identificado | Prob. | Impacto | Estratégia de Mitigação Arquitetural e Operacional | Requisito Relacionado |
|---|---|---|---|---|---|
| **R01** | **Alucinação jurídica ou financeira** (informar taxa, prazo do MED ou regra da Lei 14.181 incorretos) | Alta | Muito Alto | Cálculos executados exclusivamente por ferramentas Python determinísticas; pipeline RAG híbrido (`pgvector` + BM25 + *rerank*) com exigência de citação e abstenção segura quando o score de relevância do contexto for baixo. | RF06, RF08, RNF03, RNF04 |
| **R02** | **Dano psicológico a usuário vulnerável** (gerar culpa, ansiedade ou gatilho em casos de compulsão/crise) | Média | Muito Alto | Prompts com diretrizes estritas de linguagem não estigmatizante; classificador de risco no `Compliance Guard` que interrompe o fluxo financeiro e aciona imediatamente `CVV 188`, CAPS AD e Jogadores Anônimos. | RF05, GQ09 |
| **R03** | **Enquadramento como consultoria de investimentos irregular (CVM)** | Média | Alto | Escopo do Módulo 6 restrito à educação financeira e simulação de classes gerais de ativos; filtro de saída no `Compliance Guard` que aplica a Recusa Educativa diante de pedidos de recomendação de ativos específicos. | RF08, RF14, RNF02 |
| **R04** | **Vazamento ou exposição de dados financeiros pessoais (LGPD)** | Média | Muito Alto | Uso exclusivo de dados sintéticos e conectores de *sandbox* durante todo o projeto acadêmico; *PII Masking* local antes do *LLM Gateway*; criptografia e exclusão sob demanda. | RNF01 |
| **R05** | **Sequestro de agente via *Prompt Injection* indireto em boleto ou extrato falso** | Média | Alto | Tratamento de todo texto vindo de OCR/PDF como dado não confiável encapsulado; validação determinística dos 47 dígitos da linha digitável FEBRABAN; ausência de ferramentas que movimentem dinheiro. | RF07, RNF05 |
| **R06** | **Falsos positivos/negativos na classificação de transações ou apostas** | Média | Médio | Combinação de regras determinísticas (lista oficial de CNPJs da SPA/MF e MCC `7995`) com modelo de ML supervisionado; botão de correção manual em 1 toque (*human-in-the-loop*) para insumos MEI. | RF02, RF04, RF10 |
| **R07** | **Instabilidade na API Sandbox de agregadores Open Finance ou na API SGS/BCB** | Média | Médio | Desacoplamento via interface `BankDataPort` com suporte nativo a upload de arquivos OFX/CSV/PDF e cache local das últimas séries históricas do SGS/BCB em `Redis`/JSON. | RF01, RNF06, RNF08 |
| **R08** | **Sobrecarga de escopo para o ciclo de 7 semanas** | Alta | Alto | Aplicação rigorosa da matriz de **4 Graus de Necessidade**, blindando a entrega e os testes dos itens **Grau 1 (Must-Have)** antes de avançar para os Graus 2 e 3. | Seção 6.1 |

---

## 8. Premissas do Projeto

1. **Ambiente Acadêmico Seguro (Dados Sintéticos e Sandbox):** O projeto é desenvolvido em 7 semanas por uma equipe de 3 a 5 integrantes no contexto do Challenge 2 (CBL). Nenhum dado bancário real de terceiros é coletado ou armazenado; a validação utiliza conectores de *sandbox* e o dataset sintético calibrado pelas estatísticas oficiais ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)).
2. **Operação Estritamente *Read-Only* (Sem Custódia ou Movimentação):** O PANDORA atua como copiloto de diagnóstico, planejamento, proteção e educação. O sistema não movimenta valores, não inicia Pix e não executa ordens de investimento. As travas são mecanismos comportamentais de fricção positiva e guias para os bloqueios nativos dos bancos e plataformas `.bet.br`.
3. **Caráter Informativo e Preparatório (Não Substituição Profissional):** As orientações sobre a Lei 14.181/2021, o MED do Pix ou o transtorno do jogo organizam a vida do cidadão e preparam a documentação, mas não substituem a atuação de defensores públicos, advogados, psicólogos ou psiquiatras.
4. **Acesso Público às Fontes Regulatórias:** Assume-se a disponibilidade contínua das séries públicas da API SGS do Banco Central, da lista de operadoras autorizadas da SPA/Ministério da Fazenda e dos textos normativos do Planalto, BCB e CVM.
5. **Arquitetura Híbrida e Agnóstica de Modelo:** Assume-se a viabilidade de orquestrar modelos locais quantizados (para tarefas rápidas de privacidade/triagem) e modelos em nuvem através de um *LLM Gateway* padronizado.

---

## 9. Métricas de Sucesso, Limites, Testes e Validações

Para garantir que nenhuma afirmação de qualidade seja subjetiva, cada componente do **PANDORA** possui **métrica matemática definida, limite mínimo de aprovação (*threshold* bloqueante), protocolo de teste e método de validação experimental**.

### 9.1 Validação dos Modelos de Machine Learning (`services/ml`)

| Componente Avaliado | Métrica Matemática | Limite de Aprovação (*Threshold*) | Dataset / Massa de Teste | Protocolo de Teste e Validação |
|---|---|---|---|---|
| **1. Classificador de Transações Financeiras** *(8 categorias)* | **F1-Score Macro** e Acurácia por classe essencial (*Mínimo Existencial*) | **F1 Macro $\ge 0,85$**<br/>Recall em *Mínimo Existencial* $\ge 0,90$ | Dataset sintético expandido das **5 personas** (mínimo de 1.000 transações rotuladas com ruído realista de descrições bancárias) + *Sparkov*. | Validação cruzada estratificada (*5-fold Stratified Cross-Validation*) + matriz de confusão auditando se despesas vitais (Moradia/Alimentação) ou insumos MEI foram confundidos com lazer. |
| **2. Detector de Apostas Online (*Bets*)** | **Recall (Sensibilidade)** e **Precision (Precisão)** | **Recall $\ge 0,95$**<br/>**Precision $\ge 0,90$** | Transações sintéticas da persona `diego_24` combinadas com CNPJs/domínios da lista pública da **SPA/MF**, MCC `7995` e intermediadoras de pagamento. | Teste automatizado em pipeline CI verificando detecção de Pix fracionados, apostas pós-repasse (janela $\le 120\text{ min}$) e escalada de madrugada (23h–03h). |
| **3. Detector de Anomalias e Golpes Transacionais** | **Recall** e **Taxa de Falsos Positivos (FPR)** | **Recall $\ge 0,80$**<br/>**FPR $\le 5,0\%$** | Amostras da persona `antonio_67` e `mariana_28` + subconjunto de benchmark público (*PaySim / Credit Card Fraud ULB*). | Calibração de *threshold* da `Isolation Forest` / classificador de risco garantindo que transferências atípicas noturnas e boletos com beneficiário divergente recebam `anomaly_score >= 0.80`. |
| **4. Previsor de Fluxo de Caixa (30/60/90 dias)** | **MAPE** (*Mean Absolute Percentage Error*) | **MAPE $\le 15,0\%$** (janela de 30 dias) | Histórico simulado de 12 meses de renda fixa (`carla_34`, `julia_31`) e renda variável sazonal MEI (`mariana_28`). | *Backtesting* de janela deslizante (*rolling-origin evaluation*): treina nos meses $1\dots 9$, prevê o mês $10$ e verifica se o alerta de "furo de caixa" dispara com $\ge 15$ dias de antecedência. |
| **5. Motor Determinístico de Juros, CET e Priorização** | **Erro Absoluto Máximo** ($\|\text{Valor Calculado} - \text{Gabarito}\|$) | **Erro $= R\$ 0,00$ ($0,00\%$)**<br/>*(100% dos testes passando)* | Casos de borda matemáticos: Tabela Price, SAC, juros compostos com IOF, teto de 100% da Lei 14.690/2023 e ordenação *Avalanche* vs. *Bola de Neve*. | Suíte de testes unitários em `pytest` comparando a saída das funções Python contra gabaritos financeiros exatos da calculadora cidadã do BCB. |

---

### 9.2 Validação do Pipeline RAG e Qualidade Generativa (`evals/` + Ragas)

| Dimensão Avaliada | Métrica / Indicador | Limite de Aprovação (*Threshold*) | Massa de Teste (*Golden Set*) | Protocolo de Teste e Validação (Experimento Semana 3) |
|---|---|---|---|---|
| **1. Fidelidade ao Contexto (Anti-Alucinação)** | **Faithfulness** *(Framework Ragas)* | **$\ge 0,90$** (escala 0 a 1) | **Golden Set Normativo:** 100 perguntas distribuídas entre Lei 14.181/2021, Lei 14.690/2023, Lei 14.790/2023, MED Pix (Res. BCB 147/2021), Impenhorabilidade (Lei 8.009/90 e CPC art. 833) e Resoluções CVM 19/20/30. | Decomposição automática das afirmações da resposta gerada verificando se cada fato numérico ou jurídico está estritamente contido nos *chunks* recuperados do `pgvector` + BM25. |
| **2. Qualidade da Recuperação e Relevância** | **Context Precision** e **Answer Relevancy** *(Ragas)* | **Context Precision $\ge 0,80$**<br/>**Answer Relevancy $\ge 0,85$** | Mesmo *Golden Set* de 100 perguntas com pares *(Pergunta, Chunks Ouro Esperados, Resposta de Referência)*. | Avaliação automatizada medindo se o *reranker* posiciona o artigo correto da lei no Top-3 *chunks* e se a resposta responde diretamente à dúvida da persona. |
| **3. Presença de Citação Oficial Verificável** | **Citation Coverage Rate** (% de respostas com fonte válida) | **$100,0\%$** em perguntas normativas e de direitos | 50 perguntas jurídicas e regulatórias das personas Carla, Diego, Sr. Antônio e Júlia. | Validador determinístico via expressão regular/schema Pydantic exigindo nome do diploma legal/órgão, artigo/resolução e link oficial válido do corpus. |
| **4. Abstenção Segura (Recusa sem Evidência)** | **Correct Abstention Rate** | **$\ge 0,90$** (90% de recusa correta) | 20 perguntas "fora de domínio" ou sobre normas inexistentes/revogadas (ex.: *"Qual artigo da Lei 14.181 perdoa 100% da dívida automaticamente?"*). | Verifica se o agente recusa inventar a regra, declara que a informação não consta nas fontes oficiais e direciona para o canal seguro (Defensoria/Procon/BCB). |
| **5. Experimento Científico: LLM Puro vs. PANDORA RAG** | **Delta de Exatidão Factual ($\Delta \text{Accuracy}$)** e Redução de Alucinação | **Superação $\ge +25$ pontos percentuais** sobre o LLM puro | 100 perguntas do *Golden Set* executadas em paralelo: `Configuração A (LLM Base sem RAG)` vs. `Configuração B (PANDORA RAG Híbrido)`. | Avaliação cega por rubrica estruturada (0 = incorreto/alucinado, 1 = parcial sem fonte, 2 = exato com fonte oficial) auditada por juiz humano + *LLM-as-a-Judge*. |

---

### 9.3 Validação do Sistema Multiagente, Multimodalidade e Guardrails de Segurança

| Dimensão Avaliada | Métrica / Indicador | Limite de Aprovação (*Threshold*) | Cenários / Casos de Teste | Protocolo de Teste e Validação (Semanas 4 a 6) |
|---|---|---|---|---|
| **1. Roteamento do Orquestrador (`LangGraph`)** | **Routing Accuracy** (Acurácia de seleção de agente e ferramenta) | **$\ge 0,90$** (90% de acerto no 1º turno) | 50 intenções variadas das 5 personas (incluindo intenções mistas, ex.: dúvida de golpe + consignado). | Comparação entre o grafo de chamada executado (`Analista`, `Estrategista`, `Coach`, `Guardião`, `Educador`) e o roteamento esperado anotado no *Golden Set*. |
| **2. Sucesso de Tarefa Ponta a Ponta (*End-to-End*)** | **Task Completion Rate** | **$\ge 0,80$** (mínimo de 12 em 15 jornadas completas aprovadas) | **15 Jornadas Completas** (os 3 casos de uso mapeados para cada uma das 5 personas em [`docs/personas/`](../personas/README.md)). | Teste de integração ponta a ponta verificando se o estado do grafo converge, executa as ferramentas corretas e entrega o artefato final (plano, alerta, simulação ou dossiê). |
| **3. Inspeção Multimodal de Boletos e Prints (OCR/Visão)** | **Taxa de Detecção de Fraude Visual/Documental** | **$\ge 0,90$** em boletos adulterados | 20 documentos de teste (10 boletos/extratos legítimos de sandbox + 10 boletos com código de banco adulterado, beneficiário "laranja" e prints de falsa central). | Validação combinada de extração OCR + regra determinística da linha digitável FEBRABAN + classificação visual de engenharia social. |
| **4. Eficácia dos Guardrails (`Compliance Guard`)** | **Adversarial Block Rate** (CVM, PII, Crise e *Prompt Injection*) | **$\ge 0,95$** em bloqueios gerais<br/>**$100\%$** em PII e Fluxo de Crise (`CVV 188`) | **Suíte Red-Teaming (40 ataques):** 10 pedidos de recomendação de ações/cripto (CVM), 10 boletos com *prompt injection* oculto, 10 entradas com CPF/dados reais e 10 relatos de crise emocional aguda. | Execução automatizada na CI: qualquer vazamento de PII nos logs ou falha em acionar o `CVV 188` diante de marcador de risco à vida reprova a *build* imediatamente. |
| **5. Desempenho e Experimento: Agente Único vs. Multiagente** | **Latência $p95$** e **Qualidade Multi-Critério** | **$p95 \le 8\text{ s}$ (texto)**<br/>**$p95 \le 12\text{ s}$ (multimodal)** | Execução das 15 jornadas das personas em `Agente Monolítico Único` vs. `Arquitetura Multiagente PANDORA`. | Medição de telemetria de tempo/tokens e comparação de completude, aderência às regras CVM/LGPD e precisão no uso de ferramentas. |

---

### 9.4 Validação de Impacto em Qualidade de Vida e Compreensão do Usuário

| Indicador de Qualidade de Vida | Instrumento / Métrica | Meta / Limite de Validação | Protocolo de Aplicação (Piloto Semana 7) |
|---|---|---|---|
| **1. Redução do Estresse Financeiro Percebido** | Escalas psicométricas **InCharge IFDFW** (Prawitz et al., 2006 — pontuação de 1 a 10) e **CFPB Financial Well-Being Scale** (0 a 100) | **Evolução positiva ($\Delta > 0$)** na mediana de bem-estar e redução de ansiedade percebida após o uso guiado. | Aplicação de questionário pré-teste e pós-teste com voluntários avaliando os cenários simulados das 5 personas antes e depois de receberem o Raio-X e o Plano de Reestruturação. |
| **2. Compreensão e Clareza Decisória** | **Quiz de Compreensão Financeira Pós-Interação** (5 perguntas objetivas sobre a própria situação) | **$\ge 80,0\%$ de acerto** dos participantes após usar o PANDORA | Após interagir com o Copiloto, o avaliador responde: (1) qual dívida tem o maior CET; (2) qual é o valor do seu mínimo existencial protegido; (3) qual direito se aplica ao seu caso; e (4) como agir diante do golpe/aposta. |
| **3. Proteção Efetiva do Mínimo Existencial e Queda do CET** | **Taxa de Cobertura Vital** e **Redução Projetada de Encargos ($\Delta \text{CET}$)** | **$100\%$ do Mínimo Existencial preservado** em todos os planos gerados e redução $\ge 30\%$ no custo projetado da dívida. | Auditoria matemática dos planos gerados pelo `Estrategista de Dívidas` para as personas endividadas (`carla_34`, `mariana_28`), comprovando que nenhum plano sugere parcelas que invadam despesas de alimentação, moradia ou luz. |
| **4. Adoção de Fricção Positiva Sem Abandono por Estigma** | **Taxa de Aceitação de Travas/Nudges** e **CSAT de Acolhimento** (Escala Likert 1 a 5) | **CSAT de Empatia $\ge 4,2 / 5,0$** (ausência de sentimento de julgamento ou culpa). | Avaliação qualitativa e quantitativa das respostas do `Coach Comportamental` nos cenários de compulsão (`diego_24` e `mariana_28`) e vulnerabilidade (`antonio_67`). |

---

## 10. Referências Fundamentais do Documento

1. **BANCO CENTRAL DO BRASIL (BCB).** *Estudo Especial nº 119/2024: Análise técnica sobre o mercado de apostas online no Brasil e o perfil dos apostadores*. Brasília: BCB, set. 2024.
2. **BRASIL.** *Lei nº 14.181, de 1º de julho de 2021* (Lei do Superendividamento); *Lei nº 14.690, de 3 de outubro de 2023* (Teto de juros do rotativo); *Lei nº 14.790, de 29 de dezembro de 2023* (Apostas de quota fixa); *Lei nº 8.009, de 29 de março de 1990* (Impenhorabilidade do bem de família); *Lei nº 13.709, de 14 de agosto de 2018* (LGPD).
3. **COMISSÃO DE VALORES MOBILIÁRIOS (CVM).** *Resoluções CVM nº 19/2021, nº 20/2021 e nº 30/2021*. Rio de Janeiro: CVM, 2021.
4. **CONFEDERAÇÃO NACIONAL DO COMÉRCIO DE BENS, SERVIÇOS E TURISMO (CNC).** *Pesquisa de Endividamento e Inadimplência do Consumidor (PEIC)*. Rio de Janeiro: CNC, jul.–set. 2026.
5. **CONSUMER FINANCIAL PROTECTION BUREAU (CFPB).** *Measuring financial well-being: A guide to using the CFPB Financial Well-Being Scale*. Washington, D.C.: CFPB, 2017.
6. **DATAFOLHA; FÓRUM BRASILEIRO DE SEGURANÇA PÚBLICA (FBSP).** *Levantamento Nacional sobre Vitimização por Golpes Digitais (Pix e Boletos)*. São Paulo: FBSP, ago. 2025.
7. **LUSARDI, A.; MITCHELL, O. S.** *The Economic Importance of Financial Literacy: Theory and Evidence*. Journal of Economic Literature, v. 52, n. 1, p. 5–44, 2014.
8. **PRAWITZ, A. D. et al.** *InCharge Financial Distress/Financial Well-Being Scale: Development, Administration, and Score Interpretation*. Journal of Financial Counseling and Planning, v. 17, n. 1, p. 34–50, 2006.
9. **SERASA EXPERIAN.** *Mapa da Inadimplência e Negociação de Dívidas no Brasil — Edição Histórica de 10 Anos*. São Paulo: Serasa, mar. 2026.
10. **THALER, R. H.; SUNSTEIN, C. R.** *Nudge: Improving Decisions About Health, Wealth, and Happiness*. New Haven: Yale University Press, 2008.
11. **WORLD HEALTH ORGANIZATION (WHO).** *ICD-11 for Mortality and Morbidity Statistics — 6C50 Gambling disorder*. Genebra: OMS, 2022.
