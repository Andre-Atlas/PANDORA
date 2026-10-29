# Persona 06 · Rosângela Souza (43 anos)

> **Arquétipo:** Proteção do Benefício Social e Dano Colateral das *Bets* no Orçamento Familiar
> *"O dinheiro do Bolsa Família sumia da conta e eu achava que era tarifa do banco. Era meu filho apostando de madrugada."*

[⬅️ Persona Anterior: Júlia (31)](05-julia-reconstrucao-e-reserva.md) · [Voltar ao índice](README.md) · [Próxima Persona: Rafael (39) ➡️](07-rafael-cheque-especial-cronico.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 43 anos · Separada · Mora com os 3 filhos (8, 14 e 19 anos) na periferia de Salvador (BA) |
| **Profissão e Vínculo** | Diarista informal (2 a 3 faxinas por semana) · Ensino fundamental incompleto |
| **Renda Mensal** | **R$ 860,00** de diárias (variável) + **R$ 700,00** de Bolsa Família = **R$ 1.560,00** |
| **Situação Financeira** | **R$ 1.100,00** enviados a *bets* em 60 dias a partir da conta dela (pelo filho de 19 anos) + empréstimo com agiota + conta de água atrasada |
| **Canal Preferido no PANDORA** | **Áudio** + **Print do extrato** · Modo leve (celular simples, plano de dados pré-pago) |
| **ID no Dataset Sintético** | `rosangela_43` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** Representa os cerca de **5 milhões de beneficiários do Bolsa Família que enviaram aproximadamente R$ 3 bilhões a plataformas de apostas em um único mês** ([BCB, Estudo Especial nº 119/2024](../evidencias/noticias/README.md)), dado que motivou a decisão do STF para bloquear o uso de recursos de benefícios sociais em apostas. O estudo também aponta a concentração de apostadores entre **20 e 30 anos** — faixa do filho mais velho.
- **Literatura Científica:** O comportamento de Kauã (19) segue o padrão de **perda de controle e *chasing losses*** descrito no **CID-11 `6C50`**; para Rosângela, o dano é indireto (*affected other*), com estresse financeiro severo na escala **InCharge IFDFW (Prawitz et al., 2006)**.
- **Marcos Legais:** **Lei nº 14.790/2023** (regras de jogo responsável e autoexclusão nas operadoras autorizadas pela SPA/MF), **Lei nº 1.521/1951, art. 4º** (agiotagem como crime contra a economia popular) e **Lei nº 14.181/2021** (mínimo existencial).

---

## 3. Fotografia das Ocorrências Financeiras

| Data / Horário | Meio | Descrição | Valor | Diagnóstico do Sistema (`Analista` + `Coach`) |
|---|---|---|---|---|
| **17/10 · 06h40** | Conta Digital (crédito) | Bolsa Família — parcela de outubro | `+ R$ 700,00` | Entrada de benefício social (renda protegida) |
| **17/10 · 23h12** | Pix | Pix enviado operadora `bet.br` | `- R$ 120,00` | **Aposta pós-crédito do benefício (`anomaly_score: 0.88`)**, no mesmo dia do depósito |
| **18/10 · 02h05** | Pix | Pix enviado intermediadora de jogos online | `- R$ 200,00` | **Escalada de madrugada (`anomaly_score: 0.94`):** horário incompatível com a rotina da titular |
| **20/10 · 09h30** | Pix | Pagamento a pessoa física (agiota) | `- R$ 160,00` | **Juros de 20% a.m.** sobre R$ 800 emprestados — só encargos, sem amortização |

| Dívida / Pendência | Saldo | Encargo | Situação |
|---|---|---|---|
| **Empréstimo informal (agiota)** | R$ 800,00 | **20% a.m.** (R$ 160/mês só de juros) | 3 meses pagando juros; cobranças com intimidação |
| **Conta de água (Embasa)** | R$ 190,00 | Multa + juros | 2 faturas vencidas (risco de corte) |
| **Fiado no mercadinho do bairro** | R$ 420,00 | Sem juros formais | Limite de crédito com o comerciante esgotado |

---

## 4. Dores Profundas Contextualizadas

1. **Invisibilidade do Problema:** O filho conhece a senha do aplicativo dela (foi ele quem instalou o app). Rosângela não lê o extrato e atribuía os sumiços a "tarifa do banco" ou a erro no benefício.
2. **Conflito entre Proteger e Denunciar:** Ela tem medo de "perder o filho para o vício", mas também de que alguém descubra o uso do benefício em apostas e o Bolsa Família seja cortado. Não sabe a quem pedir ajuda sem expor a família.
3. **Crédito Informal e Medo Físico:** Sem acesso a crédito bancário barato, recorreu a um agiota do bairro. Paga os juros com o dinheiro do mercado por medo de represálias.

---

## 5. Casos de Uso: Como Rosângela Utiliza o PANDORA

### Caso 1 · Raio-X por Áudio e Print do Extrato (`Módulo 1 + Módulo 7`)
- **Como ela usa:** Grava um áudio: *"Meu dinheiro tá sumindo e eu não sei pra onde vai. Vou mandar a foto do extrato."* e envia 3 prints da tela do banco.
- **O que o sistema faz:**
  1. O `Agente Multimodal` transcreve o áudio (STT) e extrai as transações dos prints via OCR, em **modo leve** (imagens comprimidas, respostas curtas para economizar dados).
  2. O `Analista de Dados` cruza os destinatários dos Pix com a **lista pública de operadoras autorizadas da SPA/MF** e encontra **9 transferências para *bets*** em 60 dias (**R$ 1.100,00**), todas entre 22h e 03h.
  3. Responde em áudio, sem acusar ninguém: *"Rosângela, encontrei 9 Pix para sites de aposta, quase todos de madrugada. Foram R$ 1.100 em dois meses. Você reconhece esses envios?"*

### Caso 2 · Blindagem da Conta do Benefício (`Módulo 5: Guardião`)
- **Como ela usa:** Confirma que não fez os Pix e pergunta: *"Como eu faço pra ele não mexer mais no meu dinheiro sem brigar com ele?"*
- **O que o sistema faz:** O `Guardião` entrega um passo a passo em áudio e texto:
  1. **Trocar a senha e a biometria do app** e remover o aparelho do filho da lista de dispositivos confiáveis.
  2. **Reduzir o limite de Pix** (diurno e noturno) para um valor compatível com o orçamento dela.
  3. Usar o "**Cofre do Benefício**" do PANDORA: alerta imediato a qualquer saída acima de R$ 50 nas 48h seguintes ao crédito do Bolsa Família.
- **Limite ético:** o PANDORA **não monitora nem bloqueia a conta do filho**. O `Coach Comportamental` prepara um roteiro de conversa não punitiva e explica que o próprio Kauã pode ativar a **autoexclusão nas operadoras autorizadas (Lei 14.790/2023)** e buscar atendimento gratuito no **CAPS (SUS)**.

### Caso 3 · Orçamento do Mês e Saída do Agiota (`Módulo 4 + Módulo 3`)
- **Como ela usa:** Pergunta: *"Com R$ 1.560 eu pago o quê primeiro?"*
- **O que o sistema faz:**
  1. O `Planejador de Orçamento` monta um **orçamento em envelopes** (alimentação, água/luz, gás, escola, transporte) que preserva o mínimo existencial antes de qualquer dívida.
  2. O `Estrategista de Dívidas` prioriza a **conta de água** (risco de corte) e mostra que, em 3 meses, ela já pagou **R$ 480 só em juros** ao agiota — 60% do valor emprestado — sem reduzir a dívida.
  3. Consulta o RAG e explica, em linguagem simples, que **agiotagem é crime (Lei 1.521/1951)** e indica a **Defensoria Pública** para orientação. Em caso de ameaça, orienta registrar ocorrência. O sistema **nunca sugere confrontar o credor sozinha**.

---

## 6. Dificuldades da Usuária vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Rosângela | Como o PANDORA Resolve na Prática |
|---|---|
| **Baixa escolaridade e dificuldade de leitura.** | Fluxo **voice-first**: perguntas e respostas em áudio curto, com ícones grandes para cada envelope do orçamento. |
| **Celular simples e pacote de dados limitado.** | **Modo leve**: sem gráficos pesados, compressão de imagens no envio e resumo semanal em uma única mensagem. |
| **Medo de perder o Bolsa Família ou de "entregar" o filho.** | Linguagem acolhedora e sigilosa; o sistema não reporta nada a órgãos públicos e trata o caso como **proteção da família**, não como culpa. |
| **Celular compartilhado com os filhos.** | Acesso ao PANDORA com **PIN próprio** e notificações sem valores na tela de bloqueio. |
