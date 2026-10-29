# Persona 07 · Rafael Martins (39 anos)

> **Arquétipo:** Cheque Especial Crônico, "Empréstimo para Pagar Empréstimo" e Troca de Dívida Cara por Barata
> *"Eu ensino juros compostos pros meus alunos e vivo 24 dias por mês no cheque especial. Nem eu entendo como cheguei aqui."*

[⬅️ Persona Anterior: Rosângela (43)](06-rosangela-beneficio-e-bets-na-familia.md) · [Voltar ao índice](README.md) · [Próxima Persona: Lucas (19) ➡️](08-lucas-primeiro-cartao-e-golpes-digitais.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 39 anos · Casado com Camila (manicure autônoma) · Uma filha de 4 anos · Mora em Campinas (SP) |
| **Profissão e Vínculo** | Professor de matemática da rede estadual (servidor estatutário) |
| **Renda Líquida Mensal** | **R$ 5.200,00** (fixa, creditada todo dia 10) + renda variável da esposa (~R$ 1.800) |
| **Comprometimento** | **R$ 1.365,00/mês** (26% da renda) entre consignado, empréstimo pessoal e juros do cheque especial |
| **Canal Preferido no PANDORA** | Open Finance (2 bancos) + Dashboard + Simuladores |
| **ID no Dataset Sintético** | `rafael_39` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** O **cheque especial** custa em torno de **130% ao ano**, mais que o dobro do crédito livre para pessoa física (**61,7% a.a.**, ago/2026 — [Agência Brasil / BCB](../evidencias/noticias/README.md)). Rafael faz parte dos **81,7% das famílias endividadas** ([CNC/Peic, set/2026](../evidencias/noticias/README.md)) que não se consideram "inadimplentes" porque nunca atrasam uma parcela.
- **Séries Oficiais do BCB:** Taxas contratadas auditadas contra a **Série SGS `25463` (cheque especial)** e a **Série SGS `25464` (crédito pessoal não consignado)** ([`docs/evidencias/datasets/`](../evidencias/datasets/README.md)).
- **Literatura Científica:** Ilustra o achado de **Lusardi & Mitchell (2014)**: saber a teoria não basta — a educação financeira só muda o comportamento quando aparece **no momento da decisão** (*just-in-time*).
- **Marcos Legais:** **Resolução CMN nº 4.765/2019** (teto de 8% a.m. no cheque especial) e **Resolução CMN nº 4.292/2013** (portabilidade de crédito entre instituições).

---

## 3. Fotografia das Dívidas Atuais

| Credor / Modalidade | Saldo Devedor | Parcela / Encargo Mensal | Taxa | Situação |
|---|---|---|---|---|
| **Cheque Especial (Banco A)** | R$ 2.600,00 (saldo médio negativo) | **~R$ 205,00/mês** de juros + IOF | **7,9% a.m.** (perto do teto de 8% a.m.) | Negativo **24 de 30 dias** do mês, há 14 meses |
| **Empréstimo Pessoal (Banco A)** | R$ 6.000,00 | R$ 520,00 | **5,2% a.m.** | Contratado "para zerar o cheque especial" — que voltou a ficar negativo em 40 dias |
| **Consignado Servidor (Banco B)** | R$ 18.000,00 | R$ 640,00 | **1,85% a.m.** | Em dia; ainda há **R$ 450/mês de margem consignável livre** |

---

## 4. Dores Profundas Contextualizadas

1. **Vergonha Profissional:** Por ser professor de matemática, sente que "deveria saber" e evita falar do assunto com a esposa e com colegas. Adia abrir o extrato para não confrontar o número.
2. **Ilusão do Limite como Renda:** O app do banco mostra "saldo disponível" somando o limite do cheque especial. Rafael enxerga os R$ 3.000 de limite como parte do salário, e não como dívida a 7,9% ao mês.
3. **Ciclo de Ofertas Pré-Aprovadas:** Toda vez que o saldo fica negativo, o app oferece um novo "empréstimo pré-aprovado em 1 clique". Ele já aceitou uma vez e a dívida total aumentou.

---

## 5. Casos de Uso: Como Rafael Utiliza o PANDORA

### Caso 1 · Raio-X do Ciclo do Cheque Especial (`Módulo 1: Raio-X`)
- **Como ele usa:** Conecta as contas dos Bancos A e B via Open Finance (Sandbox).
- **O que o sistema faz:** O `Analista de Dados` reconstrói o saldo diário dos últimos 12 meses e mostra:
  - **"Dias no vermelho": 24 de 30**, com o saldo zerando no dia 10 (salário) e voltando a ficar negativo no dia 18.
  - **Custo anual do cheque especial: ~R$ 2.460 + IOF**, comparado com a **Série SGS `25463`** e com o teto da **Res. CMN 4.765/2019**.
  - Um gráfico de "linha do saldo real", **sem o limite somado**, para desfazer a ilusão do "saldo disponível".

### Caso 2 · Troca de Dívida Cara por Dívida Barata (`Módulo 3: Reestruturação`)
- **Como ele usa:** Pergunta: *"Vale a pena pegar mais consignado pra quitar o cheque especial e o empréstimo pessoal?"*
- **O que o sistema faz:** O `Estrategista de Dívidas` executa um cálculo determinístico (Tabela Price):
  1. **Hoje:** R$ 520 (empréstimo pessoal) + ~R$ 205 (juros do cheque especial) = **R$ 725/mês** sem prazo para acabar.
  2. **Cenário de substituição:** novo consignado de **R$ 8.600 a 1,85% a.m. em 36 meses = ~R$ 329/mês**, dentro da margem livre de R$ 450 — economia de **~R$ 396/mês**.
  3. **Cenário alternativo:** **portabilidade (Res. CMN 4.292/2013)** do empréstimo pessoal para uma instituição com taxa menor, sem usar margem consignável.
  4. **Condição obrigatória exibida junto da simulação:** reduzir o limite do cheque especial para R$ 500 no mesmo dia. Sem isso, o sistema avisa que a troca tende a **dobrar a dívida** em poucos meses, como aconteceu da última vez.

### Caso 3 · Calendário Anti-Cheque-Especial (`Módulo 4: Orçamento e Previsão`)
- **Como ele usa:** Ativa o "Plano de Saída do Vermelho".
- **O que o sistema faz:** O `Planejador de Orçamento` sugere **mover os vencimentos** (escola da filha, internet, cartão) para os dias 11 a 15, logo após o salário, e projeta o saldo dia a dia. Quando a projeção indica saldo negativo, avisa **5 dias antes**:
  > *"Rafael, no dia 22 seu saldo deve ficar R$ 140 negativo. Se adiar a compra do mercado grande para o dia 23 (pagamento da Camila), você evita R$ 11 de juros e IOF."*

---

## 6. Dificuldades do Usuário vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Rafael | Como o PANDORA Resolve na Prática |
|---|---|
| **"Eu sei a fórmula, não preciso de aula."** | Nada de explicação teórica: o sistema mostra os juros **na conta real dele**, em reais por mês e por dia. |
| **Ofertas de crédito pré-aprovado em 1 clique.** | O `Guardião` aplica **fricção positiva**: antes de aceitar crédito novo, mostra o impacto na dívida total e pede um intervalo de 24h para confirmar. |
| **Dinheiro é tabu com a esposa.** | **Painel do Casal** opcional (opt-in de ambos), que mostra apenas metas e saldo projetado comuns, sem expor gastos individuais. |
