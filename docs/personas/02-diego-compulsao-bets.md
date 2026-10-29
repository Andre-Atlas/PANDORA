# Persona 02 · Diego Oliveira (24 anos)

> **Arquétipo:** Transtorno do Jogo Online (*Bets*) e Intervenção Comportamental Empática
> *"Perdi o dinheiro da parcela da moto de novo tentando recuperar o que perdi ontem de madrugada."*

[⬅️ Persona Anterior: Carla (34)](01-carla-superendividamento.md) · [Voltar ao índice](README.md) · [Próxima Persona: Sr. Antônio (67) ➡️](03-antonio-golpes-e-consignado.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 24 anos · Solteiro · Mora com os pais na periferia de uma grande capital |
| **Profissão e Vínculo** | Entregador de aplicativo (motociclista autônomo / *gig economy*) |
| **Renda e Frequência** | **~R$ 1.120,00 por semana** (recebidos toda quarta-feira via Pix; ~R$ 3.100/mês líquidos após combustível e manutenção) |
| **Comprometimento em Apostas** | **R$ 1.200 a R$ 1.800/mês** transferidos em dezenas de Pix fracionados para *bets* |
| **Canal Preferido no PANDORA** | Conector Open Finance (Sandbox) + Notificações proativas + Áudio no chat |
| **ID no Dataset Sintético** | `diego_24` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** Personifica o **Estudo Especial nº 119/2024 do Banco Central**, que revelou o envio de **R$ 20,8 bilhões via Pix em um único mês** para 56 empresas de apostas por **24 milhões de pessoas**, com maior concentração exatamente entre jovens de **20 a 30 anos** ([`docs/evidencias/noticias/`](../evidencias/noticias/README.md)).
- **Literatura Científica:** Apresenta os sintomas clássicos de **Transtorno do Jogo predominantemente online (`CID-11 6C50.1` — OMS)**, como *chasing losses* (apostar mais para tentar recuperar perdas) e ocultação do comportamento. As intervenções seguem a teoria de **Arquitetura de Escolha e *Nudge* (Thaler & Sunstein, 2008)**.
- **Marcos Legais:** Aplicação direta da **Lei nº 14.790/2023** (Marco das Apostas de Quota Fixa) e das portarias da **Secretaria de Prêmios e Apostas (SPA/MF)** sobre jogo responsável, limites e autoexclusão.

---

## 3. Fotografia do Padrão Comportamental

| Horário / Gatilho | Transação Típica | Valor | Comportamento Detectado pelo ML (`services/ml`) |
|---|---|---|---|
| **Quarta-feira · 09h10** | Entrada de Repasse Semanal App | `+ R$ 1.120,00` | Gatilho de liquidez imediata |
| **Quarta-feira · 09h28** | Pix enviado a Operadora `.bet.br` (MCC `7995`) | `- R$ 150,00` | Aposta realizada **18 minutos após receber o salário** (`anomaly_score: 0.72`) |
| **Quarta-feira · 23h54** | Pix enviado a Operadora `.bet.br` | `- R$ 200,00` | Recorrência noturna no mesmo dia (`anomaly_score: 0.84`) |
| **Quinta-feira · 01h42** | Pix enviado a Intermediadora de Jogos | `- R$ 350,00` | **Escalada de madrugada (*chasing losses*)** (`anomaly_score: 0.95`) |

---

## 4. Dores Profundas Contextualizadas

1. **Ciclo de Compulsão e Fissura Noturna:** Quando perde R$ 150 de manhã, Diego passa o dia angustiado em cima da moto. À noite, sozinho no quarto entre **23h e 03h**, tenta "recuperar o prejuízo" em jogos de cassino online (*crash games*) e acaba perdendo o dinheiro da parcela da própria moto.
2. **Ilusão de Liquidez (Viés Cognitivo):** Como os envios são fracionados (R$ 30, R$ 50, R$ 150) e ocasionalmente entra um prêmio de R$ 120, ele lembra das vitórias e perde a noção de que seu **saldo líquido no mês é negativo em mais de R$ 1.100**.
3. **Vergonha e Isolamento:** Esconde o extrato da mãe e da namorada. Jamais baixaria um aplicativo que o rotulasse como "viciado".

---

## 5. Casos de Uso: Como Diego Utiliza o PANDORA

### Caso 1 · Revelação da Perda Líquida Real e Mapa de Gatilhos (`Módulo 2: Detector de Compulsão`)
- **Como ele usa:** Diego conecta sua conta digital (Open Finance Sandbox) apenas para "entender por que o dinheiro das entregas não está sobrando".
- **O que o sistema faz:** O `Analista de Dados` cruza os destinatários Pix e o MCC `7995` com a **lista oficial de operadoras autorizadas da SPA/MF**, desconta os pequenos prêmios recebidos e exibe sem julgamento:
  - **Total enviado para apostas no mês:** R$ 1.450,00
  - **Prêmios recebidos:** R$ 280,00
  - **Resultado líquido real:** **− R$ 1.170,00** (82% concentrados nas quartas-feiras pós-repasse e entre 23h e 03h).

### Caso 2 · *Nudge* Preventivo Pós-Repasse e Trava Noturna (`Módulo 2 + Módulo 5`)
- **Como ele usa:** Na quarta-feira às 09h15, minutos após cair o repasse de R$ 1.120, Diego abre o aplicativo.
- **O que o sistema faz:** O `Coach Comportamental` exibe um cartão empático baseado em custo de oportunidade real:
  > *"Diego, seu repasse de R$ 1.120 chegou! Nas últimas 4 quartas-feiras, R$ 320 saíram para apostas nas primeiras 2 horas — o equivalente a **5 tanques cheios de gasolina da sua moto**. Quer carimbar agora R$ 450 para a parcela da moto e ativar a **Pausa Noturna (22h às 07h)**?"*

### Caso 3 · Autoexclusão Legal e Rede de Apoio em Crise (`Módulo 5 + Compliance Guard`)
- **Como ele usa:** Às 01h50 da manhã, após uma recaída, Diego manda um áudio no chat: *"Perdi o dinheiro da parcela da moto de novo, não consigo parar sozinho"*.
- **O que o sistema faz:** O `Compliance Guard` identifica sofrimento agudo e aciona o protocolo de cuidado:
  1. Exibe em destaque o atalho confidencial para o **CVV (`188`)**, **Jogadores Anônimos (JA)** e **CAPS AD**.
  2. Orienta sobre o direito legal à **autoexclusão e limite de depósito (Lei nº 14.790/2023)** nas plataformas `.bet.br` e como reduzir o limite de Pix noturno no aplicativo do banco.

---

## 6. Dificuldades do Usuário vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Diego | Como o PANDORA Resolve na Prática |
|---|---|
| **Reatância a sermões morais:** desinstalaria o app se se sentisse julgado ou infantilizado. | Comunicação neutra, parceira e focada na proteção do fruto do trabalho dele (horas pilotando no trânsito). |
| **Impulso de desligar as travas na madrugada** durante o momento de fissura. | O `Guardião` aplica **janelas de resfriamento (*cooling-off period* de 24h a 48h)** para desativar limites voluntários (e opção de "Modo Crise" com contato de confiança via duplo consentimento). |
| **Risco de migrar para *bets* clandestinas** não reguladas. | Alerta imediato quando o CNPJ destinatário **não consta na lista da SPA/MF**, avisando que em sites ilegais o risco de fraude e bloqueio de saque é total. |
