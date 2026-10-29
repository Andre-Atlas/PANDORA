# Persona 09 · Fernanda Rocha (46 anos)

> **Arquétipo:** Choque de Renda por Demissão, Gestão da Rescisão e Decisões Grandes sob Pressão
> *"Fui demitida depois de 12 anos. Tenho um dinheiro da rescisão na conta e todo mundo tem uma ideia do que eu devia fazer com ele. Eu só tenho medo de ele acabar."*

[⬅️ Persona Anterior: Lucas (19)](08-lucas-primeiro-cartao-e-golpes-digitais.md) · [Voltar ao índice](README.md) · [Próxima Persona: Patrícia (53) ➡️](10-patricia-cuidadora-e-financas-da-mae.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 46 anos · Divorciada · Mora com o filho de 20 anos (universitário) em Joinville (SC) |
| **Profissão e Vínculo** | Ex-supervisora administrativa de indústria têxtil · **Demitida sem justa causa em set/2026** após 12 anos de CLT |
| **Renda** | Antes: **R$ 4.800,00** líquidos · Agora: **5 parcelas de seguro-desemprego (~R$ 2.500)** |
| **Caixa Disponível** | **R$ 42.500,00** (R$ 13.600 de verbas rescisórias + R$ 28.900 de multa de 40% do FGTS) · Saldo do FGTS **bloqueado** pelo saque-aniversário |
| **Despesas Essenciais** | **R$ 5.590,00/mês** (financiamento do apartamento R$ 1.450, plano de saúde R$ 1.150, mercado R$ 1.100, mensalidade do filho R$ 890, condomínio R$ 520, contas R$ 480) |
| **Canal Preferido no PANDORA** | Upload de documentos (TRCT, extrato do FGTS, contrato do financiamento) + Chat + Simuladores |
| **ID no Dataset Sintético** | `fernanda_46` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** A dívida média do brasileiro inadimplente é de **R$ 6.598,13** e **42%** dos inadimplentes estão negativados há uma década ([Serasa, mar/2026](../evidencias/noticias/README.md)). Uma perda de emprego sem plano é um dos caminhos mais rápidos de uma família adimplente para esse grupo.
- **Literatura Científica:** O caso testa a segunda dimensão do **CFPB Financial Well-Being Scale (2017)**: a **capacidade de absorver um choque financeiro**. O estresse de Fernanda aparece como insônia e paralisia decisória, compatível com sofrimento moderado na escala **InCharge IFDFW (Prawitz et al., 2006)**.
- **Marcos Legais:** **Lei nº 12.506/2011** (aviso prévio proporcional), **Lei nº 8.036/1990** e **Lei nº 13.932/2019** (FGTS e saque-aniversário), **Lei nº 7.998/1990** (seguro-desemprego), **Lei nº 9.656/1998, art. 30** (manutenção do plano de saúde após demissão) e **Resoluções CVM 19, 20 e 30/2021** (limites para recomendação de investimentos).

---

## 3. Fotografia da Transição Financeira

| Item | Valor | Diagnóstico do Sistema (`Analista` + `Planejador`) |
|---|---|---|
| **Verbas rescisórias (TRCT)** | `+ R$ 13.600,00` | Conferência via OCR: **aviso prévio de 66 dias** (30 + 3 por ano trabalhado) calculado corretamente |
| **Multa de 40% do FGTS** | `+ R$ 28.900,00` | Liberada; é o principal colchão de caixa da transição |
| **Saldo do FGTS (R$ 72.400)** | `R$ 0,00` sacável | **Bloqueado:** Fernanda aderiu ao saque-aniversário em 2021 e **antecipou R$ 16.500** em um banco; na demissão, recebe só a multa |
| **Seguro-desemprego** | `+ ~R$ 2.500,00/mês × 5` | Cobre **45%** das despesas essenciais |
| **Fôlego financeiro (runway)** | **~9,8 meses** | Caixa + seguro-desemprego ÷ despesas essenciais, sem nenhum corte |

| Pressão / Oferta Recebida | Valor Envolvido | Risco Identificado |
|---|---|---|
| Gerente do banco sugere "aplicar a rescisão" em previdência com carência | R$ 30.000 | Perda de liquidez justamente quando ela mais precisa |
| Amiga convida para abrir uma franquia de cosméticos "juntas" | R$ 35.000 | Concentração de todo o caixa em um negócio sem histórico |
| Ideia própria: quitar parte do financiamento do apartamento | R$ 28.900 | Reduz a parcela, mas **corta o fôlego pela metade** |

---

## 4. Dores Profundas Contextualizadas

1. **Choque de Identidade e Etarismo:** Depois de 12 anos na mesma empresa, Fernanda sente que "perdeu o lugar no mundo" e teme não ser recontratada aos 46 anos. Isso a deixa ansiosa para "fazer o dinheiro render" rápido.
2. **Surpresa com o FGTS:** Contava com cerca de R$ 100 mil (saldo + multa) e só então descobriu que, por ter aderido ao saque-aniversário, o saldo ficou bloqueado. Sente culpa por ter antecipado valores anos atrás.
3. **Excesso de Conselhos Contraditórios:** Gerente, amigos, família e vídeos de internet dão sugestões opostas. Sem critério para comparar, ela não decide nada e o dinheiro fica parado na conta corrente, sem rendimento.

---

## 5. Casos de Uso: Como Fernanda Utiliza o PANDORA

### Caso 1 · Conferência da Rescisão e Entendimento do FGTS (`Módulo 1 + Módulo 6 + RAG`)
- **Como ela usa:** Envia em PDF o **Termo de Rescisão (TRCT)** e o **extrato do FGTS** e pergunta: *"Me pagaram tudo certo? E por que não consigo sacar o FGTS?"*
- **O que o sistema faz:**
  1. O `Agente Multimodal` extrai os campos do TRCT; o `Compliance Guard` mascara CPF e PIS.
  2. O `Analista de Dados` confere de forma determinística o **aviso prévio proporcional (Lei 12.506/2011)**, as férias proporcionais + 1/3 e o 13º proporcional.
  3. O `Educador` consulta no RAG a **Lei 13.932/2019** e explica que, no saque-aniversário, a demissão sem justa causa libera **apenas a multa de 40%**. Mostra também quanto do saldo está alienado à antecipação e como funciona o pedido de retorno à modalidade saque-rescisão (efeito só após o prazo de carência legal).

### Caso 2 · Mapa do Fôlego Financeiro (`Módulo 4: Orçamento e Previsão`)
- **Como ela usa:** Pergunta: *"Quantos meses eu aguento sem emprego?"*
- **O que o sistema faz:** O `Planejador de Orçamento` monta a **linha do tempo da transição**:
  - **Sem cortes:** ~9,8 meses de fôlego.
  - **Com 3 ajustes** sugeridos (trocar para um plano de saúde individual mais barato, R$ 650 em vez de manter o corporativo pelo **art. 30 da Lei 9.656/1998**; −R$ 150 no mercado; −R$ 80 em contas): **~11,3 meses**.
  - Sinaliza o **mês 6** como ponto de reavaliação, quando acaba o seguro-desemprego e o consumo de caixa dobra.

### Caso 3 · Decisões Grandes com Guardrails (`Módulo 3 + Módulo 6 + Compliance Guard`)
- **Como ela usa:** Pergunta: *"É melhor usar a multa do FGTS para abater o financiamento, colocar na previdência que o gerente ofereceu ou entrar na franquia?"*
- **O que o sistema faz:**
  1. **Simulação determinística do financiamento:** amortizar R$ 28.900 reduz a parcela em **~R$ 390/mês**, mas derruba o fôlego de **~9,8 para ~5 meses**. Recomendação de princípio: *primeiro garantir liquidez para o período sem emprego; amortização é uma decisão para depois da recolocação.*
  2. **Previdência e franquia:** o `Compliance Guard` aplica as **Resoluções CVM 19 e 20/2021** — o PANDORA **não recomenda produtos nem negócios específicos**. Em vez disso, entrega critérios objetivos: carência e liquidez, taxas de administração e carregamento, percentual do caixa comprometido e cenário de perda total.
  3. Sugere manter a reserva de transição em **aplicações de liquidez diária e baixo risco de crédito** (critérios gerais, sem indicar instituição).

---

## 6. Dificuldades da Usuária vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Fernanda | Como o PANDORA Resolve na Prática |
|---|---|
| **Paralisia diante de conselhos contraditórios.** | Uma **matriz de decisão única** (liquidez × risco × impacto no fôlego) aplicada igualmente a todas as opções, com números dela. |
| **Pressão de tempo** ("a oferta da franquia vence sexta"). | **Fricção positiva**: o `Coach Comportamental` sugere uma regra de *"nenhuma decisão acima de R$ 5.000 nos primeiros 60 dias"* e lembra que urgência artificial é sinal de alerta. |
| **Documentos trabalhistas incompreensíveis.** | Cada linha do TRCT e do extrato do FGTS é traduzida em linguagem simples, com a base legal citada. |
| **Ansiedade com o filho na faculdade.** | Simulação de cenários para a mensalidade (Fies, bolsa da própria instituição, trancamento) apresentada só quando ela pede, sem alarmismo. |
