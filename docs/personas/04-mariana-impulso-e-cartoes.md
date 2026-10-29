# Persona 04 · Mariana Costa (28 anos)

> **Arquétipo:** Renda Variável (MEI), Compras por Impulso (*BNPL*) e Fragmentação em 4 Cartões
> *"Cada compra parcelada parecia só R$ 50 por mês, mas quando juntei os 4 cartões vi que já comi a renda do mês que vem."*

[⬅️ Persona Anterior: Sr. Antônio (67)](03-antonio-golpes-e-consignado.md) · [Voltar ao índice](README.md) · [Próxima Persona: Júlia (31) ➡️](05-julia-reconstrucao-e-reserva.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 28 anos · Solteira · Divide apartamento alugado com uma amiga |
| **Profissão e Vínculo** | Designer gráfica e social media *freelancer* (MEI) |
| **Renda Mensal (Volátil)** | **R$ 3.200,00 (meses fracos) a R$ 5.800,00 (meses de pico)** |
| **Situação Financeira** | Fragmentada em **4 bancos digitais**; 22 parcelamentos ativos (R$ 2.150/mês); começou a pagar fatura de um cartão usando limite de outro |
| **Canal Preferido no PANDORA** | Conector Open Finance multi-banco (4 instituições) + Dashboard de Fluxo de Caixa |
| **ID no Dataset Sintético** | `mariana_28` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Modelos de ML)

- **Notícias e Estatísticas:** Representa o centro estatístico da **PEIC/CNC (jul–set/2026)**, na qual **85,3% das famílias endividadas possuem dívidas no cartão de crédito** ([`docs/evidencias/noticias/`](../evidencias/noticias/README.md)). Retrata o fenômeno de múltiplos cartões digitais, *Buy Now, Pay Later* (Pix Parcelado) e mistura entre caixa MEI e pessoa física.
- **Modelos de Machine Learning (`services/ml`):** Caso de uso principal para o detector de anomalias comportamentais (**`Isolation Forest`** para compras noturnas por impulso) e para o previsor de fluxo de caixa em renda sazonal (**`Prophet / ETS`** para 30, 60 e 90 dias).

---

## 3. Fotografia das Transações e Fragmentação

| Data / Horário | Instituição / Meio | Descrição e Categoria | Valor | Diagnóstico do Sistema (`Analista` + `ML`) |
|---|---|---|---|---|
| **08/10 · 15h10** | Conta Digital 1 (Pix) | Recebimento Projeto Design MEI | `+ R$ 3.200,00` | Entrada de receita variável (misturada na conta PF) |
| **09/10 · 23h48** | Cartão Digital 3 | Marketplace Fast Fashion (Parc. 01/10) | `- R$ 489,90` | **Impulso Noturno (`anomaly_score: 0.82`):** compra pós-estresse de trabalho |
| **10/10 · 00h35** | Cartão Digital 4 | Loja Eletrônicos Online (Parc. 01/12) | `- R$ 319,00` | **Escalada de Madrugada (`anomaly_score: 0.86`):** 22º parcelamento simultâneo |
| **14/10 · 11h20** | Cartão Digital 2 | Pagto Boleto Fatura Cartão 1 no Cartão 2 | `- R$ 980,00` | **Alerta Vermelho (`anomaly_score: 0.91`):** "rolo" de fatura com taxa de 4,99% a.m. |

---

## 4. Dores Profundas Contextualizadas

1. **Cegueira de Fluxo de Caixa Futuro:** Como cada compra é parcelada em 10x ou 12x em quatro aplicativos diferentes, Mariana olha o valor da parcela isolada ("só R$ 49,90") e não percebe que a soma das parcelas já contratadas consome **R$ 2.150,00 fixos todo mês** antes mesmo de ela pagar o aluguel.
2. **Gasto Emocional Noturno (*Dopamina de Consumo*):** Após virar noites entregando projetos para clientes difíceis, ela usa compras em *marketplaces* entre **22h e 01h** como recompensa emocional (*"eu trabalhei tanto, eu mereço"*).
3. **Abandono de Planilhas Manuais e Confusão MEI × PF:** Já tentou usar 3 aplicativos de controle manual e desistiu na primeira semana porque categorizar 4 bancos na mão é inviável e seu dinheiro pessoal vive misturado com o CNPJ MEI.

---

## 5. Casos de Uso: Como Mariana Utiliza o PANDORA

### Caso 1 · Consolidação Multi-Banco Automática e Separação MEI × PF (`Módulo 1: Raio-X`)
- **Como ela usa:** Mariana conecta suas 4 contas digitais de uma só vez pelo agregador Open Finance (Sandbox) do PANDORA.
- **O que o sistema faz:** O pipeline normaliza todas as transações (`BankDataPort`), separa automaticamente as entradas de clientes/imposto DAS-MEI dos gastos pessoais e consolida as 4 faturas em uma única linha do tempo, revelando que **68% do seu piso de renda do próximo mês já está comprometido com parcelas contratadas**.

### Caso 2 · Detecção de Impulso Noturno e "Regra das 48 Horas" (`Módulo 2 + Módulo 4`)
- **Como ela usa:** Abre o resumo semanal do PANDORA na sexta-feira.
- **O que o sistema faz:** O modelo `Isolation Forest` mostra que Mariana gastou R$ 940/mês em compras não essenciais concentradas entre **22h e 01h** nas quintas e sextas-feiras. O `Coach Comportamental` propõe ativar a **"Regra das 48 Horas"**: deixar itens no carrinho à noite e só concluir a compra 48h depois se não comprometer a meta do mês.

### Caso 3 · Previsão de Fluxo de Caixa 30/60/90 Dias e Alerta Anti-Rotativo (`Módulo 4 + Módulo 3`)
- **Como ela usa:** Consulta o painel de projeção antes de fechar o mês.
- **O que o sistema faz:** O modelo `Prophet / ETS` cruza a sazonalidade dos recebimentos MEI com as datas de vencimento dos 4 cartões e avisa com **25 dias de antecedência**:
  > *"Mariana, atenção: no dia 15 do próximo mês, o fechamento dos Cartões 1 e 3 vai gerar um furo de caixa de **R$ 620,00**. Para evitar que você pague uma fatura com outro cartão (juros de 4,99% a.m.) ou caia no rotativo (435,9% a.a.), sugerimos reservar R$ 620 do pagamento do Cliente A que entrou hoje."*

---

## 6. Dificuldades da Usuária vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Mariana | Como o PANDORA Resolve na Prática |
|---|---|
| **Insumos de trabalho classificados errado** (ex.: assinatura da Adobe marcada como "Lazer/Supérfluo"). | **Reclassificação em 1 toque (*Human-in-the-loop*):** Mariana marca a transação como *"Insumo MEI"* e o modelo de ML aprende imediatamente para os meses seguintes. |
| **Orçamentos tradicionais (50-30-20) não funcionam para renda variável.** | O `Planejador de Orçamento` cria um **Orçamento por Piso de Renda Base (R$ 3.200)**, direcionando o excedente dos meses de pico para um "Colchão de Estabilização MEI". |
| **Fadiga de notificações** (apps que apitam a cada café de R$ 10). | Alertas inteligentes acionados apenas em **anomalias reais de padrão** (parcelamentos noturnos cumulativos ou risco de rolo de fatura). |
