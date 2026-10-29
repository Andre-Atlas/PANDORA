# Persona 08 · Lucas Andrade (19 anos)

> **Arquétipo:** Primeiro Cartão de Crédito, Golpes em Compras Digitais e Educação Financeira *Just-in-Time*
> *"O tênis tava 60% mais barato no anúncio do Instagram. Paguei no Pix, a loja sumiu e a fatura do cartão chegou maior que meu estágio."*

[⬅️ Persona Anterior: Rafael (39)](07-rafael-cheque-especial-cronico.md) · [Voltar ao índice](README.md) · [Próxima Persona: Fernanda (46) ➡️](09-fernanda-demissao-e-rescisao.md)

---

## 1. Resumo do Perfil

| Atributo | Detalhe |
|---|---|
| **Idade e Família** | 19 anos · Solteiro · Mora com os pais em Contagem (MG) |
| **Profissão e Vínculo** | Estudante de Análise e Desenvolvimento de Sistemas (noturno) · Estagiário em uma empresa de logística |
| **Renda Mensal** | **R$ 1.400,00** de bolsa-estágio + auxílio-transporte |
| **Situação Financeira** | Primeiro cartão de crédito há 3 meses (limite **R$ 1.200**) · Fatura atual de **R$ 1.050** · Vítima de loja falsa (**R$ 389** via Pix) |
| **Canal Preferido no PANDORA** | Chat em texto + **Compartilhar link/print** direto do Instagram e WhatsApp |
| **ID no Dataset Sintético** | `lucas_19` ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)) |

---

## 2. Ancoragem nas Evidências (Notícias, Artigos e Leis)

- **Notícias e Estatísticas:** Entre os **24 milhões de vítimas de golpes via Pix ou boleto** em 12 meses, os **jovens são os que mais sofrem com fraudes em compras digitais** ([Datafolha / FBSP, ago/2025](../evidencias/noticias/README.md)). O cartão de crédito está presente em **85,3% das famílias endividadas** ([CNC/Peic, set/2026](../evidencias/noticias/README.md)) e costuma ser a porta de entrada do jovem no crédito.
- **Literatura Científica:** **Lusardi & Mitchell (2014)** mostram que a baixa alfabetização financeira sobre juros compostos leva ao uso caro do cartão e que a educação é mais eficaz quando aparece **no momento da decisão** — o padrão de intervenção usado com Lucas.
- **Marcos Legais:** **Resolução BCB nº 147/2021** (MED do Pix), **CDC, art. 49** (direito de arrependimento em compras fora do estabelecimento, válido para lojas reais) e **Lei nº 14.690/2023** (teto de juros do rotativo).

---

## 3. Fotografia das Transações

| Data / Horário | Meio | Descrição | Valor | Diagnóstico do Sistema (`Guardião` + `Analista`) |
|---|---|---|---|---|
| **03/10 · 21h15** | Cartão de Crédito | Smartphone em loja online (Parc. 01/12) | `- R$ 159,00` | Primeira compra parcelada; **12 meses** de compromisso para quem tem estágio de 1 ano |
| **09/10 · 22h47** | Pix | "Outlet tênis" — anúncio patrocinado no Instagram | `- R$ 389,00` | **Golpe de loja falsa (`anomaly_score: 0.93`):** Pix para pessoa física, CNPJ do site inexistente, domínio criado há 6 dias |
| **12/10 · 14h00** | Cartão de Crédito | Assinaturas (streaming, jogos, música) | `- R$ 118,70` | 4 assinaturas recorrentes; 2 sem uso nos últimos 30 dias |
| **21/10 · 19h30** | Pix | "Taxa de nível VIP" — tarefa paga de curtir vídeos | `- R$ 120,00` | **Golpe da tarefa paga (`anomaly_score: 0.96`):** pagamento para "liberar saque" de comissões |

---

## 4. Dores Profundas Contextualizadas

1. **Vergonha de Contar aos Pais:** Lucas queria mostrar independência com o primeiro estágio. Depois do golpe, esconde o prejuízo e pensa em pagar só o mínimo da fatura para "ganhar tempo".
2. **Limite Visto como Dinheiro Disponível:** Entende o limite de R$ 1.200 como "mais um salário", sem perceber que as parcelas do celular já ocupam 11% da bolsa pelos próximos 11 meses.
3. **Exposição a Golpes Sofisticados:** Anúncios patrocinados com fotos de influenciadores, perfis com milhares de seguidores e grupos de WhatsApp com "provas de saque" fazem os golpes parecerem legítimos.

---

## 5. Casos de Uso: Como Lucas Utiliza o PANDORA

### Caso 1 · Verificador de Loja e Link antes de Pagar (`Módulo 5 + Módulo 7`)
- **Como ele usa:** No Instagram, toca em "Compartilhar → PANDORA" num anúncio de console com 55% de desconto e pergunta: *"Essa loja é confiável?"*
- **O que o sistema faz:** O `Agente Multimodal` lê o print e o link; o `Guardião` avalia **sinais objetivos** e responde com uma lista de verificação:
  - Pagamento **somente via Pix para pessoa física** · CNPJ ausente ou divergente na consulta pública da Receita Federal · domínio recém-registrado · desconto acima de 50% com contagem regressiva.
  - **Veredito:** *"Alto risco de golpe (4 de 4 sinais). Se mesmo assim quiser comprar, use o cartão de crédito: no cartão você pode contestar a compra; no Pix para pessoa física, recuperar é bem mais difícil."*
- **Segurança:** todo texto extraído do anúncio é tratado pelo `Compliance Guard` como **dado não confiável** (proteção contra *prompt injection* em páginas de golpe).

### Caso 2 · Pós-Golpe: MED e Registro (`Módulo 5 + RAG`)
- **Como ele usa:** Conta que já pagou os R$ 389 do tênis há 2 dias.
- **O que o sistema faz:** O `Guardião` consulta a **Resolução BCB nº 147/2021** e orienta:
  1. **Acionar o MED no banco** com urgência (quanto antes, maior a chance de haver saldo bloqueável na conta do golpista).
  2. Copiar em 1 toque o **ID Fim-a-Fim (E2E)**, data, hora e valor do Pix.
  3. Registrar **Boletim de Ocorrência online** e denunciar o anúncio na plataforma.
  4. Explica que o **direito de arrependimento (CDC, art. 49)** vale para lojas reais, mas não resolve um golpe — por isso o MED é o caminho.

### Caso 3 · Primeira Fatura com Educação *Just-in-Time* (`Módulo 6 + Módulo 4`)
- **Como ele usa:** Antes de pagar, pergunta: *"Se eu pagar só o mínimo esse mês, qual o problema?"*
- **O que o sistema faz:** O `Educador` roda a simulação determinística sobre a fatura real de **R$ 1.050**:
  - **Pagando o mínimo:** o saldo vai para o rotativo (**435,9% a.a.** na média de mercado) — com limite legal de encargos em 100% do valor original (**Lei 14.690/2023**), mas ainda assim a dívida pode **dobrar**.
  - **Alternativa:** cancelar as 2 assinaturas sem uso (R$ 54/mês), pagar a fatura integral com a bolsa deste mês e montar um orçamento de **"Estágio 50/30/20"** para os próximos meses.
  - Também identifica o padrão da **"tarefa paga"** e explica por que *"pagar para começar a ganhar"* é sempre golpe.

---

## 6. Dificuldades do Usuário vs. Como o PANDORA Ajuda

| Dificuldade / Barreira de Lucas | Como o PANDORA Resolve na Prática |
|---|---|
| **Não lê textos longos nem "aulas" de finanças.** | Respostas em formato de **checklist curto** e simulações sobre os números dele, dentro do fluxo de compra. |
| **Confia em perfis com muitos seguidores.** | O `Guardião` explica **por que** cada sinal indica golpe, criando critério próprio em vez de só bloquear. |
| **Medo de contar aos pais.** | Plano de recuperação sem julgamento; ele decide se e quando envolver a família. |
| **Não percebe o peso das parcelas futuras.** | **Linha do tempo de parcelas**: mostra quanto da bolsa de cada mês já está comprometido antes de uma nova compra parcelada. |
