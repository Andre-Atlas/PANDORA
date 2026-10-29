# Persona 05 · Júlia Santos (31 anos)

> **Arquétipo:** Reconstrução Pós-Dívida, Ansiedade de Recaída e Educação de Investimentos sob Guardrails CVM
> *"Finalmente limpei meu nome, mas morro de medo de voltar pro vermelho ou de perder meu dinheiro seguindo dica de influenciador."*

[⬅️ Persona Anterior: Mariana (28)](04-mariana-impulso-e-cartoes.md) · [Voltar ao índice](README.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 31 anos · Solteira · Sem filhos |
| **Profissão e Vínculo** | Analista administrativa em empresa de tecnologia/logística (CLT) · Ensino superior completo |
| **Renda Líquida Mensal** | **R$ 4.500,00** (fixa; custo de vida essencial de **R$ 2.800,00/mês**) |
| **Capacidade de Poupança** | **R$ 500,00/mês** (terminou de pagar o último acordo de dívida antiga há 3 meses) |
| **Canal Preferido no PANDORA** | Chat em texto + Simuladores Determinísticos + Trilha Educacional RAG |
| **ID no Dataset Sintético** | `julia_31` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** Representa o combate à **reincidência crônica apontada pelo Mapa da Inadimplência da Serasa (mar/2026)**: **42% dos brasileiros inadimplentes já estavam negativados 10 anos antes**, pois saem de acordos sem construir uma Reserva de Emergência e voltam a se endividar no primeiro choque financeiro ([`docs/evidencias/noticias/`](../evidencias/noticias/README.md)).
- **Literatura Científica:** Fundamentada na **CFPB Financial Well-Being Scale (2017)** (dimensão de *"capacidade de absorver um choque financeiro"*) e no estudo clássico de **Lusardi & Mitchell (2014)** (*The Economic Importance of Financial Literacy*), que demonstra que a educação financeira só funciona quando aplicada aos números reais do indivíduo no momento da decisão (*just-in-time education*).
- **Marcos Regulatórios:** Aplicação estrita das **Resoluções CVM nº 19/2021 e 20/2021** (vedação à consultoria/análise de valores mobiliários sem registro) e da **Resolução CVM nº 30/2021** (*Suitability* / perfil de investidor).

---

## 3. Fotografia das Transações Atuais

| Data / Horário | Modalidade | Descrição e Categoria | Valor | Diagnóstico do Sistema (`Planejador` + `Educador`) |
|---|---|---|---|---|
| **05/10 · 08h00** | Pix (Salário) | Crédito Salário CLT Empresa Tech | `+ R$ 4.500,00` | Renda estável pós-quitação de passivo |
| **05/10 · 10h00** | Débito Direto | Aplicação Tesouro Selic Reserva Emergência | `- R$ 500,00` | Hábito saudável ("pague-se primeiro" logo após o salário) |
| **11/10 · 19h20** | Cartão de Crédito | Farmácia e Saúde | `- R$ 320,00` | Despesa planejada dentro da meta do orçamento adaptativo |

---

## 4. Dores Profundas Contextualizadas

1. **Trauma Financeiro Pós-Inadimplência:** Mesmo com as contas em dia, Júlia sente ansiedade física ao ver o saldo da conta diminuir ao longo do mês, com medo constante de uma emergência médica ou demissão jogá-la de volta no cheque especial (130% a.a.).
2. **Ruído de *Finfluencers* vs. Medo de Perder Tudo:** Nas redes sociais, é bombardeada por promessas de "1% ao dia com *day trade*, criptoativos ou robôs de Pix". Por medo de cair em golpe ou perder dinheiro, acaba deixando suas economias paradas na conta-corrente perdendo para a inflação.
3. **Barreira com Siglas do Mercado:** Não entende a diferença prática entre **Taxa Selic, CDI, IPCA, IOF regressivo e garantia do FGC**.

---

## 5. Casos de Uso: Como Júlia Utiliza o PANDORA

### Caso 1 · Construção da Escada da Reserva de Emergência e *Suitability* (`Módulo 4 + Módulo 6`)
- **Como ela usa:** Júlia escolhe a meta *"Construir minha Reserva de Emergência e nunca mais voltar para o vermelho"*.
- **O que o sistema faz:**
  1. O `Planejador de Orçamento` identifica seu custo essencial (**R$ 2.800/mês**) e calcula a reserva ideal de 6 meses (**R$ 16.800**), dividindo-a em **degraus alcançáveis** (15 dias → 1 mês → 3 meses → 6 meses).
  2. O `Educador` aplica o questionário de **Perfil de Investidor (*Suitability* Educacional — Res. CVM 30/2021)**, classificando seu momento atual como **Conservador (Foco em Liquidez Diária D+0 e Segurança)**.

### Caso 2 · Simulador Determinístico com Séries Oficiais do BCB (`Módulo 6`)
- **Como ela usa:** Júlia pergunta: *"Quanto meus R$ 500 por mês vão virar em 1 e 2 anos e por que dizem que a poupança rende menos?"*
- **O que o sistema faz:** O `Educador` aciona a ferramenta determinística `simulate_investment`, consumindo as séries oficiais do Banco Central (**Série SGS `432` Selic**, **`12` CDI** e **`433` IPCA**). Exibe em gráfico simples o **ganho real (descontada a inflação e o Imposto de Renda)** comparando **Classes Gerais de Renda Fixa de Liquidez Diária** (Títulos Públicos Selic vs. Renda Fixa Pós-Fixada 100% CDI vs. Poupança), explicando cada sigla sobre os próprios R$ 500 de Júlia.

### Caso 3 · Atuação do Guardrail CVM diante de Pedido de Recomendação (`Módulo 6 + Compliance Guard`)
- **Como ela usa:** Júlia envia o nome de uma ação da Bolsa e de um banco específico no chat e pergunta: *"Qual ação ou CDB específico de qual banco eu devo comprar hoje com meus R$ 1.500 guardados?"*
- **O que o sistema faz:** O `Compliance Guard` aplica a **Regra Inviolável de Conformidade Regulatória (Resoluções CVM 19 e 20/2021)**:
  > *"Júlia, como sou um copiloto educacional e não uma consultoria de valores mobiliários registrada na CVM, eu **não recomendo ações, fundos ou títulos de bancos específicos**. Mas posso te ensinar os **3 critérios objetivos** para você mesma avaliar qualquer opção para sua Reserva de Emergência:*
  > *1. **Liquidez Diária (D+0):** poder resgatar no mesmo dia se surgir um imprevisto;*
  > *2. **Baixo Risco de Crédito:** garantia soberana (Tesouro Nacional) ou cobertura do FGC (até R$ 250 mil por CPF/instituição);*
  > *3. **Rendimento pós-fixado:** acompanhar 100% da Taxa Selic ou do CDI sem risco de marcação a mercado."*
  *(Acompanhado de citação verificável do Portal do Investidor CVM e do Tesouro Direto).*

---

## 6. Dificuldades da Usuária vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Júlia | Como o PANDORA Resolve na Prática |
|---|---|
| **Frustração com uma recusa seca ("Não posso responder isso").** | O `Compliance Guard` faz uma **Recusa Educativa**: explica o limite legal da CVM e entrega imediatamente os critérios técnicos para que ela tome uma decisão autônoma e segura. |
| **Desmotivação diante de uma meta longa** (juntar R$ 16.800 leva quase 3 anos poupando R$ 500/mês). | Transforma o saldo acumulado em **"Dias de Tranquilidade Conquistados"** (*"Você já garantiu 18 dias de aluguel e alimentação protegidos contra qualquer imprevisto"*). |
| **Vulnerabilidade a promessas de retorno garantido em redes sociais.** | Cruza promessas de "1% ao dia" (~3.678% a.a.) com a **Taxa Selic oficial do BCB**, demonstrando matematicamente que ganhos altos sem risco ocultam pirâmides ou golpes. |
