# Persona 01 · Carla Mendes (34 anos)

> **Arquétipo:** Superendividamento Estrutural Familiar e Defesa do Mínimo Existencial
> *"Não sei por onde começar. Se eu pagar o banco todo, falta dinheiro para o mercado das crianças."*

[⬅️ Voltar ao índice de Personas](README.md) · [Próxima Persona: Diego (24) ➡️](02-diego-compulsao-bets.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 34 anos · Mãe solo de duas crianças (6 e 9 anos) |
| **Profissão e Vínculo** | Atendente de rede de farmácias (CLT) · Ensino médio completo |
| **Renda Líquida Mensal** | **R$ 2.850,00** (fixa, recebida todo 5º dia útil) |
| **Despesas Vitais (Mínimo Existencial)** | **R$ 2.100,00/mês** (73,6% da renda: aluguel R$ 950, mercado R$ 680, luz/água/gás R$ 240, transporte/escola R$ 230) |
| **Canal Preferido no PANDORA** | Upload de faturas em PDF/foto + Chat em texto simples |
| **ID no Dataset Sintético** | `carla_34` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** Representa os **81,7 milhões de brasileiros inadimplentes** ([Serasa, mar/2026](../evidencias/noticias/README.md)) e os **12,5% das famílias que declaram não ter condições de pagar suas contas em atraso** ([CNC/Peic, set/2026](../evidencias/noticias/README.md)). O uso do cartão para itens básicos colocou Carla no **rotativo do cartão**, cuja taxa média atingiu **435,9% ao ano** em fev/2026 ([Agência Brasil / BCB, Série SGS `20749`](../evidencias/datasets/README.md)).
- **Literatura Científica:** Apresenta pontuação crítica de estresse financeiro (*overwhelming financial distress*) na escala **InCharge IFDFW (Prawitz et al., 2006)**, com reflexos diretos em insônia e ansiedade.
- **Marcos Legais:** Caso clássico de aplicação da **Lei do Superendividamento (Lei nº 14.181/2021)**, do teto de 100% sobre o valor original da dívida do rotativo (**Lei nº 14.690/2023**) e da impenhorabilidade salarial (**CPC, art. 833, IV**).

---

## 3. Fotografia das Dívidas Atuais

| Credor / Modalidade | Saldo Devedor | Parcela / Encargo Mensal | Taxa (CET Anual) | Situação |
|---|---|---|---|---|
| **Cartão de Crédito (Banco A)** | R$ 4.200,00 | Paga o mínimo (~R$ 630), gerando **R$ 342,18/mês só de juros + IOF** | **448,0% a.a.** | 7 meses rolando no rotativo |
| **Empréstimo Pessoal (Financeira B)** | R$ 5.800,00 | 18 parcelas restantes de **R$ 480,00** | **112,0% a.a.** | Desconto em conta; atraso iminente |
| **Concessionária de Energia (Luz)** | R$ 360,00 | 2 faturas vencidas | Multa + 1% a.m. | **45 dias em atraso** (risco de corte) |

---

## 4. Dores Profundas Contextualizadas

1. **Dor Psicológica (Assédio e Culpa Materna):** Recebe mais de 15 ligações diárias de escritórios de cobrança ameaçando "bloquear seu CPF e seu salário". Sente culpa intensa quando precisa negar um item simples aos filhos no mercado.
2. **Dor Cognitiva (A Armadilha do Pagamento Mínimo):** Carla acredita que pagar o "valor mínimo" da fatura mantém sua situação sob controle, sem perceber que os juros compostos de 448% a.a. fazem a dívida dobrar em poucos meses.
3. **Desconhecimento de Direitos:** Não sabe que a lei brasileira proíbe que o pagamento de dívidas de consumo comprometa o valor necessário para alimentar e abrigar sua família (**Mínimo Existencial**).

---

## 5. Casos de Uso: Como Carla Utiliza o PANDORA

### Caso 1 · Diagnóstico Seguro via Upload de Faturas em PDF (`Módulo 1: Raio-X`)
- **Como ela usa:** Com medo de conectar o banco via Open Finance e ter o salário retido pelo credor, Carla escolhe **"Enviar fatura ou extrato em PDF/Foto"**.
- **O que o sistema faz:** O `Agente Multimodal` extrai os dados via OCR; o `Compliance Guard` mascara seu CPF; o `Analista de Dados` identifica que o CET de 448% a.a. está acima da média oficial do Banco Central (**Série SGS `20749`**) e mostra que R$ 342 do que ela pagou no mês foram apenas encargos.

### Caso 2 · Blindagem do Mínimo Existencial e Priorização (`Módulo 3: Reestruturação`)
- **Como ela usa:** Carla pergunta no chat: *"Se eu pagar a fatura inteira e o empréstimo, meus filhos ficam sem comer. O que eu pago primeiro?"*
- **O que o sistema faz:** O `Estrategista de Dívidas` calcula de forma determinística:
  1. **1º Lugar (Intocável):** Preserva os **R$ 2.100,00** de despesas vitais (aluguel, alimentação e transporte).
  2. **2º Lugar (Serviço Essencial):** Prioriza quitar a conta de luz atrasada (R$ 360) para evitar corte de fornecimento.
  3. **3º Lugar (Método Avalanche):** Com os R$ 750/mês de folga real do orçamento, simula o estancamento do rotativo (maior CET) e verifica se a dívida já atingiu o teto legal de 100% da **Lei 14.690/2023**.

### Caso 3 · Preparação do Dossiê para a Lei do Superendividamento (`Módulo 3 + RAG`)
- **Como ela usa:** Como os bancos se recusam a dar um desconto que caiba nos R$ 750/mês, Carla pede ajuda para negociar pelos meios oficiais.
- **O que o sistema faz:** Consulta no RAG a **Lei nº 14.181/2021** (arts. 54-A a 54-G e 104-A do CDC), explica como funciona a audiência global de conciliação no **Procon, Defensoria Pública ou CEJUSC** (plano de até 5 anos) e gera um **Relatório Consolidado de Dívidas e Mínimo Existencial** pronto para impressão.

---

## 6. Dificuldades da Usuária vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Carla | Como o PANDORA Resolve na Prática |
|---|---|
| **Medo de julgamento moral** (ex.: ser criticada por gastar R$ 25 num lanche para os filhos). | Linguagem 100% acolhedora e não punitiva; foca no impacto estrutural dos juros bancários, nunca em culpar a vítima. |
| **Pavor de bloqueio de salário** diante de ameaças de cobradores. | O agente `Educador` cita o **art. 833, IV do CPC**, explicando com fonte oficial que o salário é legalmente **impenhorável** para dívidas de cartão/empréstimo. |
| **Paralisia diante de jargões técnicos** ("CET", "IOF", "Tabela Price"). | Cada sigla é traduzida automaticamente em **reais por mês** e em **impacto no carrinho de supermercado** da família. |
