# Persona 10 · Patrícia Nogueira (53 anos)

> **Arquétipo:** Geração Sanduíche, Gestão Financeira Delegada de Pessoa Idosa e Sobrecarga do Cuidador
> *"Cuido do dinheiro da minha mãe, do meu e da minha filha. Descobri um desconto no benefício dela que ninguém pediu, e meu cartão está pagando os remédios."*

[⬅️ Persona Anterior: Fernanda (46)](09-fernanda-demissao-e-rescisao.md) · [Voltar ao índice](README.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 53 anos · Divorciada · Mora em Goiânia (GO) com a mãe, **Dona Lurdes (81)**, e a filha (17, em ano de vestibular) |
| **Profissão e Vínculo** | Técnica de enfermagem hospitalar (CLT, plantões 12×36) + plantões extras |
| **Renda Mensal** | **R$ 3.900,00** líquidos + **~R$ 900,00** de plantões extras (variável) |
| **Renda da Mãe** | **R$ 1.850,00** de pensão por morte (INSS) · Dona Lurdes tem **diagnóstico inicial de Alzheimer** |
| **Situação Financeira** | Fatura do cartão parcelada (**12× R$ 690**) para cobrir remédios, fraldas e cuidadora · **R$ 1.100** em descontos não autorizados no benefício da mãe em 8 meses |
| **Canal Preferido no PANDORA** | **Painel do Cuidador** (acesso delegado com consentimento) + Chat · Dona Lurdes usa o **modo voz** |
| **ID no Dataset Sintético** | `patricia_53` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** **Idosos são as principais vítimas de boletos adulterados e falsas centrais telefônicas** entre os **24 milhões de brasileiros** que sofreram golpes via Pix ou boleto em 12 meses ([Datafolha / FBSP, ago/2025](../evidencias/noticias/README.md)). O consignado do INSS segue como alvo frequente de contratações e descontos que o beneficiário não reconhece.
- **Séries Oficiais do BCB:** Descontos e contratos do benefício comparados com a **Série SGS `25467` (consignado INSS)** ([`docs/evidencias/datasets/`](../evidencias/datasets/README.md)).
- **Literatura Científica:** Sobrecarga financeira e emocional do cuidador medida pela **InCharge IFDFW (Prawitz et al., 2006)**; a dimensão de **"controle sobre as finanças do dia a dia"** do **CFPB (2017)** está comprometida nas duas gerações.
- **Marcos Legais:** **Estatuto da Pessoa Idosa (Lei nº 10.741/2003)**, **Tomada de Decisão Apoiada (Código Civil, art. 1.783-A)**, **LGPD (Lei nº 13.709/2018)** para o consentimento do acesso delegado e **Resolução BCB nº 147/2021** (MED do Pix).

---

## 3. Fotografia das Ocorrências Financeiras

**Conta de Dona Lurdes (visão delegada, somente leitura):**

| Evento / Transação | Valor | Diagnóstico do Sistema (`Guardião` + `Analista`) |
|---|---|---|
| **Pensão por morte (INSS)** | `+ R$ 1.850,00` | Renda fixa mensal da mãe |
| **Desconto "Cartão Consignado — RMC"** | `- R$ 92,50/mês` | **Contrato não reconhecido (`anomaly_score: 0.91`):** reserva de 5% da margem sem nenhum cartão em uso |
| **Desconto "Contribuição Associativa"** | `- R$ 45,00/mês` | **Desconto não autorizado (`anomaly_score: 0.89`):** associação desconhecida pela família |
| **Ligação da "central do INSS" + pedido de Pix** | `R$ 0,00` (interceptado) | Tentativa de golpe bloqueada pelo modo voz e pela palavra-código da família |

**Conta de Patrícia:**

| Despesa / Dívida | Valor Mensal | Situação |
|---|---|---|
| **Parcelamento da fatura do cartão** | R$ 690,00 (12×, **8,0% a.m.**) | Saldo de R$ 5.200 acumulado com gastos de cuidado |
| **Cuidadora diarista (2×/semana)** | R$ 960,00 | Paga no Pix, sem divisão com os irmãos |
| **Medicamentos para Alzheimer** | R$ 310,00 | Comprados na farmácia, embora possam ser obtidos pelo SUS |
| **Fraldas geriátricas e insumos** | R$ 280,00 | Recorrente |

---

## 4. Dores Profundas Contextualizadas

1. **Sobrecarga Invisível:** Patrícia cuida da mãe, da filha e trabalha em plantões. Os gastos com a mãe saem do cartão dela, e os dois irmãos "ajudam quando podem". Ninguém sabe quanto o cuidado custa de verdade.
2. **Dilema entre Autonomia e Proteção:** Dona Lurdes ainda quer controlar o próprio dinheiro e fica ofendida quando a filha "mexe nas coisas dela". Patrícia teme tanto humilhar a mãe quanto deixá-la exposta a golpes.
3. **Descontos Silenciosos:** Os descontos indevidos no benefício passaram 8 meses sem ser notados porque ninguém conferia o extrato do INSS, apenas o valor que caía na conta.

---

## 5. Casos de Uso: Como Patrícia Utiliza o PANDORA

### Caso 1 · Painel do Cuidador com Consentimento Registrado (`Módulo 5 + Módulo 1`)
- **Como ela usa:** Senta com a mãe e, juntas, ativam o **acesso delegado somente leitura** à conta de Dona Lurdes.
- **O que o sistema faz:**
  1. O `Compliance Guard` registra o **consentimento explícito e revogável da titular (LGPD)**, explicado em voz e letras grandes. Dona Lurdes continua dona da conta e pode desligar o acesso a qualquer momento. A ficha menciona a **Tomada de Decisão Apoiada (CC, art. 1.783-A)** como caminho formal, caso a família queira.
  2. O `Analista de Dados` faz o Raio-X do benefício e encontra os **dois descontos não reconhecidos** (R$ 137,50/mês, **R$ 1.100** em 8 meses).
  3. O `Guardião` gera o passo a passo: contestar os descontos pelo **Meu INSS ou Central 135**, pedir ao banco a cópia do contrato do cartão consignado, ativar o **bloqueio do benefício para novos empréstimos** no Meu INSS e, se não houver solução, registrar reclamação no **consumidor.gov.br** e no Procon.

### Caso 2 · Escudo contra Golpes para Dona Lurdes (`Módulo 7 + Módulo 5`)
- **Como ela usa:** Patrícia configura as regras de proteção; a mãe usa o **modo voz**, como o Sr. Antônio (Persona 03).
- **O que o sistema faz:**
  - Dona Lurdes pergunta em áudio: *"Ligaram do INSS dizendo que minha pensão vai ser cortada se eu não fizer um Pix. É verdade?"* — o sistema responde com voz calma e frases curtas que **é golpe** e pede que ela desligue.
  - **Palavra-código da família:** qualquer pedido de dinheiro "em nome da Patrícia" precisa dela; o PANDORA lembra a mãe disso quando detecta um pedido urgente.
  - **Alerta para a cuidadora:** Pix acima de R$ 200 para destinatário novo, ou qualquer Pix entre 20h e 6h, gera aviso para Patrícia **sem expor o restante do extrato**. O sistema também orienta a reduzir o **limite noturno do Pix** no app do banco da mãe.

### Caso 3 · Orçamento do Cuidado e Saúde Financeira da Cuidadora (`Módulo 4 + Módulo 3 + RAG`)
- **Como ela usa:** Pergunta: *"Quanto custa cuidar da minha mãe e como eu saio do parcelamento do cartão?"*
- **O que o sistema faz:**
  1. O `Planejador de Orçamento` separa os **"custos do cuidado" (R$ 1.550/mês)** dos gastos da casa e gera um **relatório para dividir com os irmãos**, com valores e comprovantes, para a conversa em família.
  2. O `Educador` consulta no RAG e informa que os medicamentos para Alzheimer da mãe podem ser obtidos gratuitamente pelo **Componente Especializado da Assistência Farmacêutica (CEAF/SUS)**, com laudo médico: **−R$ 310/mês**.
  3. O `Estrategista de Dívidas` mostra que, com essa economia e o ressarcimento dos descontos indevidos, Patrícia pode **antecipar parcelas** do parcelamento da fatura (8% a.m.) e reduzir os juros totais.

---

## 6. Dificuldades da Usuária vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Patrícia | Como o PANDORA Resolve na Prática |
|---|---|
| **Pouco tempo (plantões de 12h).** | **Resumo semanal único** com só o que exige ação, e alertas imediatos apenas para risco real de golpe. |
| **Medo de tirar a autonomia da mãe.** | Acesso **somente leitura**, com consentimento registrado e revogável; nenhuma transação é feita em nome de Dona Lurdes. |
| **Conflito familiar sobre quem paga o quê.** | **Relatório de Custos do Cuidado** neutro e com comprovantes, para os irmãos dividirem as despesas com base em números. |
| **Esgotamento emocional (*burnout* do cuidador).** | O `Coach Comportamental` acompanha a escala de estresse financeiro e indica a rede de apoio (CRAS, grupos de cuidadores) sem tratar o tema como fraqueza. |
