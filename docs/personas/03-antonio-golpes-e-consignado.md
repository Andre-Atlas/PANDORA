# Persona 03 · Sr. Antônio Ferreira (67 anos)

> **Arquétipo:** Vulnerabilidade Digital, Golpes no Pix/Boleto e Proteção Previdenciária
> *"Tenho vergonha de contar pro meu filho que caí num golpe e agora tenho medo até de abrir o aplicativo do banco."*

[⬅️ Persona Anterior: Diego (24)](02-diego-compulsao-bets.md) · [Voltar ao índice](README.md) · [Próxima Persona: Mariana (28) ➡️](04-mariana-impulso-e-cartoes.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 67 anos · Viúvo · Mora sozinho no interior de São Paulo (filhos moram em outra cidade) |
| **Profissão e Vínculo** | Aposentado pelo INSS (ex-metalúrgico) |
| **Renda Líquida Mensal** | **R$ 2.412,00** (benefício previdenciário fixo) |
| **Comprometimento e Perdas** | **R$ 723,60/mês** (30% em consignado) + vítima de boleto falso (**R$ 1.198,00**) e golpe da falsa central (**R$ 1.800,00**) |
| **Canal Preferido no PANDORA** | **Voz (Áudio STT/TTS)** + **Câmera / Foto de Boleto e Print de WhatsApp** |
| **ID no Dataset Sintético** | `antonio_67` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** Representa os **24 milhões de brasileiros vítimas de golpes via Pix ou boleto falso** em 12 meses, que somaram **quase R$ 29 bilhões de prejuízo** — com perda média exata de **R$ 1.198,00 por vítima** ([Pesquisa Datafolha / FBSP / Rádio Senado, ago/2025](../evidencias/noticias/README.md)), apontando os **idosos como os principais alvos de boletos adulterados e falsas centrais telefônicas**.
- **Séries Oficiais do BCB:** Contratos de crédito auditados contra a **Série SGS `25467` (Taxa média mensal — Crédito pessoal consignado INSS)** ([`docs/evidencias/datasets/`](../evidencias/datasets/README.md)).
- **Marcos Legais:** Aplicação direta da **Resolução BCB nº 147/2021** (Mecanismo Especial de Devolução — **MED do Pix**), da **Lei nº 8.009/1990** (Impenhorabilidade do Bem de Família) e do **CPC, art. 833, IV** (Impenhorabilidade da aposentadoria).

---

## 3. Fotografia das Ocorrências Financeiras

| Evento / Transação | Modalidade | Valor | Diagnóstico do Sistema (`Guardião` + `Analista`) |
|---|---|---|---|
| **Empréstimo Consignado Contrato 04** | Desconto em folha INSS | `- R$ 723,60/mês` | Compromete 30% do benefício; alvo frequente de assédio de "refinanciamento com troco" |
| **Boleto de "Quitação com 70% de Desconto"** | Boleto enviado por WhatsApp | `- R$ 1.198,00` | **Fraude Detectada (`anomaly_score: 0.97`):** linha digitável aponta para conta de pessoa física ("laranja"), divergente do banco credor |
| **Transferência "Central de Segurança"** | Pix para conta desconhecida | `- R$ 1.800,00` | **Golpe da Falsa Central (`anomaly_score: 0.98`):** transferência atípica noturna sob coação telefônica |

---

## 4. Dores Profundas Contextualizadas

1. **Humilhação e Medo de Perder a Autonomia:** Depois de pagar o boleto falso, o Sr. Antônio escondeu o fato dos filhos por receio de que o achem incapaz de morar sozinho ou administrar o próprio dinheiro.
2. **Barreira Visual e Digital:** Tem presbiopia (dificuldade para enxergar letras miúdas e conferir os 47 dígitos de um boleto na tela do celular), digita devagar e sente ansiedade com menus cheios de gráficos.
3. **Vulnerabilidade ao Senso de Urgência (Engenharia Social):** Quando um golpista liga dizendo *"Aqui é do setor antifraude do seu banco, sua aposentadoria será bloqueada em 10 minutos"*, ele entra em pânico e segue as instruções sem ter a quem recorrer na hora.

---

## 5. Casos de Uso: Como o Sr. Antônio Utiliza o PANDORA

### Caso 1 · Inspeção de Boleto e Print de Conversa por Voz e Foto (`Módulo 5 + Módulo 7`)
- **Como ele usa:** Ao receber no WhatsApp um boleto prometendo quitar seu consignado ou um print pedindo um Pix para "liberar estorno do INSS", ele toca no **botão grande de microfone** do PANDORA, tira uma foto do documento e grava um áudio: *"Vê pra mim se esse papel aqui do banco é verdadeiro ou se tão querendo me passar pra trás de novo"*.
- **O que o sistema faz:**
  1. O `Agente Multimodal` transcreve o áudio (STT) e lê o boleto/print via OCR + Visão.
  2. O `Guardião` valida matematicamente a linha digitável (código FEBRABAN da instituição vs. logotipo impresso) e checa o CNPJ/CPF do beneficiário final.
  3. Responde em **letras grandes (alto contraste WCAG 2.2 AA)** e **em voz clara (TTS)**:
     > *"Sr. Antônio, PARE! Não pague este boleto. Apesar de ter o desenho do banco, o código mostra que o dinheiro vai para a conta de uma pessoa desconhecida. Nenhum banco pede Pix para liberar valores do INSS."*

### Caso 2 · Acionamento Guiado do MED (Mecanismo Especial de Devolução do Pix) (`Módulo 5 + RAG`)
- **Como ele usa:** Ele conta por áudio que já fez um Pix para o golpista ontem à noite e pergunta como recuperar o dinheiro.
- **O que o sistema faz:** O `Guardião` busca no RAG a **Resolução BCB nº 147/2021** e entrega um passo a passo falado e escrito em 3 etapas simples:
  1. **Acionar o MED no banco imediatamente** (prazo legal de até 80 dias) para bloquear cautelarmente a conta do golpista.
  2. **Dados prontos para copiar em 1 toque:** ID Fim-a-Fim (E2E) da transação, data, horário e valor exato.
  3. **Guia para Boletim de Ocorrência** e registro no Banco Central.

### Caso 3 · Auditoria de Consignado INSS e Proteção da Moradia (`Módulo 1 + Módulo 3`)
- **Como ele usa:** Pergunta por áudio se vale a pena aceitar uma ligação que ofereceu "R$ 2.000 de troco" para renovar o consignado.
- **O que o sistema faz:** O `Analista de Dados` compara a taxa proposta com a **Série SGS `25467` do BCB**, mostra em reais que ele pagaria mais 84 parcelas perdendo milhares de reais em juros e o tranquiliza citando a **impenhorabilidade da aposentadoria (CPC art. 833, IV)** e da **casa própria (Lei 8.009/1990)**.

---

## 6. Dificuldades do Usuário vs. Como o PANDORA Ajuda

| Dificuldade / Barreira do Sr. Antônio | Como o PANDORA Resolve na Prática |
|---|---|
| **Dificuldade de leitura e digitação no celular.** | Interface **Voice-First (STT/TTS)** com botões amplos, tipografia grande e envio direto de foto/áudio. |
| **Ataque de *Prompt Injection* embutido no boleto falso** (texto oculto tentando enganar a IA). | O `Compliance Guard` isola todo texto de OCR como dado não confiável e executa validação determinística na linha digitável do boleto. |
| **Isolamento na hora do golpe** (vergonha de pedir ajuda). | Botão opcional **"Avisar meu Contato de Confiança"** (opt-in explícito), que envia apenas o alerta de golpe ao filho sem expor o extrato bancário. |
