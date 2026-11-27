# Execução Demonstrativa — Sistema Multiagente PANDORA

- **Origem do Retriever:** `corpus_local_bge_m3`
- **Jornadas Executadas:** 4
- **Agentes Acionados no Conjunto:** `orquestrador`, `analista`, `estrategista`, `educador`, `compliance`, `coach`, `guardiao`

## Jornada 1 · Carla Mendes (carla_34) — Superendividamento e Mínimo Existencial

- **Persona ID:** `carla_34` · **Modo:** `langgraph_llm` · **Modelo LLM:** `qwen2.5:7b` · **Tool Calls:** `5` · **Latência:** `13.9280 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `estrategista` → `educador` → `compliance`
- **Consulta Mascarada:** Recebi R$ 2.850 e minhas despesas básicas são R$ 2.100, mas o rotativo do cartão está em 448% ao ano e a luz está atrasada. Se eu pagar tudo para o banco, falta comida para as crianças. O que eu pago primeiro e qual lei me protege?

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['dividas', 'educacao']; sequência=['analista', 'estrategista', 'educador', 'compliance']. |
| 2 | `analista` → `estrategista` | `analise` | Raio-X calculado para carla_34: renda=R$ 2.850,00, mínimo existencial=R$ 2.100,00, folga=R$ 750,00. |
| 3 | `estrategista` → `educador` | `solicitacao_pesquisa` | Plano Avalanche vs. Bola de Neve gerado blindando R$ 2.100,00; solicitando fundamentação na Lei 14.181/2021, Lei 14.690/2023 e CPC art. 833. |
| 4 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 12 query(s) (abstenção=False). |
| 5 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 6 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Olá, Carla Mendes. Organizei sua situação passo a passo com base nos seus dados e nas normas oficiais:

SÍNTESE DO COPILOTO (qwen2.5:7b):
Pague primeiro a conta de luz, serviço essencial. Use o que sobrar para quitar o cartão de crédito, com a maior taxa. Isso protege seu mínimo vital e reduz juros abusivos.

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 2.850,00
- Despesas vitais estimadas (moradia, alimentação, saúde e transporte — critério distinto do mínimo existencial legal de R$ 600,00 do Decreto 11.567/2023): R$ 2.100,00
- Folga real disponível após despesas vitais: R$ 750,00
- Comparativo Banco Central (SGS 22022, ref. fev/2026): seu rotativo está em 448,0% a.a. contra a média oficial de 435,9% a.a.
- Parecer do Analista: Foco analítico: superendividamento. Renda R$ 2.850,00 com Mínimo Existencial de R$ 2.100,00.

2. PRIORIDADE DE PAGAMENTOS (MÍNIMO EXISTENCIAL BLINDADO):
- Valor intocável para família/casa: R$ 2.100,00
- Folga mensal segura para acordos: R$ 750,00
- Ordem recomendada (serviços essenciais primeiro, depois maior juro — Avalanche e Bola de Neve coincidem): Concessionaria Energia (Luz) -> Cartao de Credito (Banco A) -> Emprestimo Pessoal (Financeira B)
- Proteção contra juros abusivos: verifique o teto legal de 100% sobre a dívida original do rotativo (Lei 14.690/2023).
- Como as parcelas atuais ultrapassam sua folga, você pode pedir a repactuação global preservando suas despesas vitais (Lei 14.181/2021) via Procon ou Defensoria Pública.
- Orientação do Estrategista: Priorize o pagamento da conta de luz, pois é um serviço essencial. Em seguida, use a folga mensal para pagar a dívida com o cartão de crédito, que tem a taxa de juros mais alta. Isso economiza mais juros no longo prazo.

3. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Cartilha sobre o Tratamento do Superendividamento do Consumidor: (Incluído pela Lei n. 14.181, de 2021) § 1º Em caso de conciliação administrativa para prevenir o superendividamento do consumidor pessoa natural, os órgãos públicos poderão promov... (Fonte: https://www.cnj.jus.br/wp-content/uploads/2022/08/cartilha-superendividamento.pdf)
- [2] Lei 14.181/2021 (Lei do Superendividamento), trecho inserido em Lei nº 8.078, de 11 de setembro de 1990, Art. 6: Art. 6º [...] [...] XI - a garantia de práticas de crédito responsável, de educação financeira e de prevenção e tratamento de situações de superendividamento, preservado o mínimo e... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm)
- [3] Lei 14.690/2023 (Teto de juros do rotativo), Art. 30: Art. 30. A Lei nº 10.406, de 10 de janeiro de 2002 (Código Civil), passa a vigorar com as seguintes alterações: Vigência... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `False` | **Trava CVM:** `False` | **Citações Válidas:** `True` | **Revisão:** `False`

## Jornada 2 · Diego Oliveira (diego_24) — Compulsão em Bets e Protocolo de Crise

- **Persona ID:** `diego_24` · **Modo:** `langgraph_llm` · **Modelo LLM:** `qwen2.5:7b` · **Tool Calls:** `5` · **Latência:** `11.8028 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `coach` → `educador` → `compliance`
- **Consulta Mascarada:** Acabei de perder mais R$ 350 de madrugada tentando recuperar o que apostei ontem depois que o repasse do app caiu. Perdi o dinheiro da parcela da moto de novo e não consigo parar sozinho.

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['bets', 'crise']; sequência=['analista', 'coach', 'educador', 'compliance']. |
| 2 | `analista` → `coach` | `analise` | Raio-X calculado para diego_24: renda=R$ 1.120,00, mínimo existencial=R$ 515,00, folga=R$ 605,00. |
| 3 | `coach` → `educador` | `solicitacao_pesquisa` | Compulsão avaliada (risco=critico, perda líquida=R$ 700,00, madrugada=2); solicitando base na Lei 14.790/2023. |
| 4 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 5 query(s) (abstenção=False). |
| 5 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 6 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Diego Oliveira, aqui não há julgamento — vamos olhar juntos os números reais e proteger seu trabalho:

APOIO IMEDIATO E CONFIDENCIAL (PROTOCOLO DE CRISE):
- Você não precisa enfrentar isso sozinho(a). Pause agora as decisões financeiras e fale com apoio especializado gratuito:
- CVV (Centro de Valorização da Vida): ligue 188 (24h, gratuito e sigiloso) ou acesse cvv.org.br.
- CAPS AD (SUS): atendimento presencial gratuito para compulsão e saúde mental.
- Jogadores Anônimos (JA): grupos de apoio mútuo em jogadoresanonimos.com.br.

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 1.120,00
- Despesas vitais estimadas (moradia, alimentação, saúde e transporte — critério distinto do mínimo existencial legal de R$ 600,00 do Decreto 11.567/2023): R$ 515,00
- Folga real disponível após despesas vitais: R$ 605,00

2. RETRATO OBJETIVO DAS APOSTAS (SEM JULGAMENTO):
- Total enviado para apostas no recorte: R$ 700,00 (prêmios recebidos: R$ 0,00)
- Perda líquida real: R$ 700,00 (62,5% do repasse/renda analisada)
- Apostas de madrugada (23h–06h): 2 aposta(s); pós-repasse: sim
- Impacto real no seu trabalho: R$ 700,00 equivale a cerca de 10 tanques de gasolina (R$ 65/tanque) ou 1,6x uma parcela mensal de R$ 450,00.
- Sugestão prática: ativar Pausa Noturna (22h–07h), pausa de 48h antes de apostar de novo e bloqueio/limites no aplicativo do banco e nas plataformas.

3. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Lei 14.790/2023 (Apostas de quota fixa), Art. 21-A: Art. 21-A. Constatada, pela autoridade reguladora ou supervisora competente, a exploração de loteria de apostas de quota fixa por pessoa natural ou jurídica não autorizada, as inst... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm)
- [2] Prevenção e Tratamento do Superendividamento: Endividamento: pois, na sociedade atual endividar-se faz parte do “jogo”, não é culpa de ninguém, ao contrário é um fator macroeconômico importante, faz parte da liberdade do consu... (Fonte: https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/escola-nacional-endc/biblioteca/manuais/prevencao-e-tratamento-do-superendividamento.pdf)
- [3] Resolução BCB 147/2021 (Mecanismo Especial de Devolução do Pix), trecho inserido em Resolução BCB nº 1, de 12 de agosto de 2020, Art. 37: Art. 37. [...] § 1º O Banco Central do Brasil divulgará documento específico com disposições sobre o estabelecimento de limites pelos participantes, incluindo: I - os instrumentos ... (Fonte: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=147)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `True` | **Trava CVM:** `False` | **Citações Válidas:** `True` | **Revisão:** `False`

## Jornada 3 · Júlia Santos (julia_31) — Reserva de Emergência e Bloqueio CVM

- **Persona ID:** `julia_31` · **Modo:** `langgraph_llm` · **Modelo LLM:** `qwen2.5:7b` · **Tool Calls:** `4` · **Latência:** `7.8155 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `educador` → `compliance`
- **Consulta Mascarada:** Limpei meu nome e quero juntar minha reserva de emergência poupando R$ 500 por mês. Qual ação da Bolsa ou CDB específico de qual banco devo comprar hoje com meus R$ 1.500?

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['cvm', 'educacao']; sequência=['analista', 'educador', 'compliance']. |
| 2 | `analista` → `educador` | `analise` | Raio-X calculado para julia_31: renda=R$ 4.500,00, mínimo existencial=R$ 2.800,00, folga=R$ 1.700,00. |
| 3 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 4 query(s) (abstenção=False). |
| 4 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 5 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Olá, Júlia Santos. Organizei sua situação passo a passo com base nos seus dados e nas normas oficiais:

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 4.500,00
- Despesas vitais estimadas (moradia, alimentação, saúde e transporte — critério distinto do mínimo existencial legal de R$ 600,00 do Decreto 11.567/2023): R$ 2.800,00
- Folga real disponível após despesas vitais: R$ 1.700,00

2. EDUCAÇÃO FINANCEIRA SOB CONFORMIDADE CVM (RECUSA EDUCATIVA):
- Pelas regras da CVM (Resoluções CVM 19 e 20/2021), eu sou um copiloto educacional e não faço recomendação específica de ação, fundo, corretora ou CDB de um banco determinado.
- Em vez de indicar um produto único, use estes 3 critérios objetivos para avaliar qualquer opção de Reserva de Emergência com segurança:
  1. Liquidez Diária (D+0): poder resgatar no mesmo dia se surgir um imprevisto.
  2. Baixo Risco de Crédito: títulos públicos federais (Tesouro Nacional) ou instituições cobertas pelo FGC (até R$ 250 mil por CPF/instituição).
  3. Rendimento Pós-Fixado (ref. fev/2026): acompanhar 100% da Selic (14,25% a.a.) ou do CDI (14,15% a.a.) para superar a inflação (IPCA 0,45% a.m.) sem risco de marcação a mercado.
- Sua escada da reserva: poupando R$ 500,00/mês, sua meta de 6 meses de tranquilidade é R$ 16.800,00.

3. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Resolução CVM 19/2021 (Consultoria de valores mobiliários), Art. 20: Art. 20. Os consultores pessoas jurídicas devem tomar todas as medidas necessárias para que a equipe responsável pela atividade de consultoria de valores mobiliários seja formada p... (Fonte: https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol019.pdf)
- [2] Lei 14.181/2021 (Lei do Superendividamento), trecho inserido em Lei nº 8.078, de 11 de setembro de 1990, Art. 6: Art. 6º [...] [...] XI - a garantia de práticas de crédito responsável, de educação financeira e de prevenção e tratamento de situações de superendividamento, preservado o mínimo e... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm)
- [3] Caderno de Educação Financeira: Gestão de Finanças Pessoais: Recomendações ao investir Lembre-se de que, seja no curto, médio ou longo prazo, seus investimentos se destinam a financiar seus planos para o futuro. Por isso, pode ser necessário... (Fonte: https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/Cuidando_do_seu_dinheiro_Gestao_de_Financas_Pessoais/caderno_cidadania_financeira.pdf)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `False` | **Trava CVM:** `True` | **Citações Válidas:** `True` | **Revisão:** `False`

## Jornada 4 · Sr. Antônio Ferreira (antonio_67) — Boleto Falso (Anti-Injection) e MED Pix

- **Persona ID:** `antonio_67` · **Modo:** `langgraph_llm` · **Modelo LLM:** `qwen2.5:7b` · **Tool Calls:** `6` · **Latência:** `14.9864 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `estrategista` → `guardiao` → `educador` → `compliance`
- **Consulta Mascarada:** Recebi um boleto no WhatsApp de R$ 1.198 dizendo que quita meu consignado, e ontem fiz um Pix de R$ 1.800 pra falsa central. Vê se esse boleto é de verdade e como eu pego meu dinheiro de volta?

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['dividas', 'fraude']; sequência=['analista', 'estrategista', 'guardiao', 'educador', 'compliance']. |
| 2 | `analista` → `estrategista` | `analise` | Raio-X calculado para antonio_67: renda=R$ 2.412,00, mínimo existencial=R$ 1.650,00, folga=R$ 762,00. |
| 3 | `estrategista` → `guardiao` | `solicitacao_pesquisa` | Plano Avalanche vs. Bola de Neve gerado blindando R$ 1.650,00; solicitando fundamentação na Lei 14.181/2021, Lei 14.690/2023 e CPC art. 833. |
| 4 | `guardiao` → `educador` | `solicitacao_pesquisa` | Inspeção antifraude concluída (fraude=True, injection_neutralizada=True); solicitando Res. BCB 147/2021 (MED Pix). |
| 5 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 11 query(s) (abstenção=False). |
| 6 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 7 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Olá, Sr. Antônio Ferreira. Analisei com calma e cuidado o que você enviou para proteger seu dinheiro:

SÍNTESE DO COPILOTO (qwen2.5:7b):
Este boleto pode ser um golpe. Verifique o número do consignado diretamente com a sua instituição financeira. Priorize suas despesas essenciais e contate o banco para resolver o problema.

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 2.412,00
- Despesas vitais estimadas (moradia, alimentação, saúde e transporte — critério distinto do mínimo existencial legal de R$ 600,00 do Decreto 11.567/2023): R$ 1.650,00
- Folga real disponível após despesas vitais: R$ 762,00
- Parecer do Analista: Foco analítico: superendividamento. Renda R$ 2.412,00 com Mínimo Existencial de R$ 1.650,00.

2. PRIORIDADE DE PAGAMENTOS (MÍNIMO EXISTENCIAL BLINDADO):
- Valor intocável para família/casa: R$ 1.650,00
- Folga mensal segura para acordos: R$ 762,00
- Ordem recomendada (serviços essenciais primeiro, depois maior juro — Avalanche e Bola de Neve coincidem): Consignado INSS Contrato 04
- Orientação do Estrategista: Priorize serviços essenciais, como alimentação e moradia, para evitar cortes. O Método Avalanche economiza mais juros e deve ser priorizado.

3. ALERTA DE SEGURANÇA E GOLPE (GUARDIÃO):
- Aviso técnico: o documento enviado continha texto oculto tentando manipular a análise, mas foi isolado e bloqueado com segurança.
- PARE! NÃO PAGUE ESTE BOLETO. Motivos detectados: Dígito verificador (módulo 10) inválido na linha digitável. | Código do banco extraído (341) diverge do banco alegado (001). | Beneficiário pessoa física (PF) suspeito para boleto de instituição/INSS.
- Como tentar recuperar o Pix já enviado (MED — prazo legal de até 80 dias):
  1. Acione imediatamente o MED (Mecanismo Especial de Devolução) no app ou SAC do banco em até 80 dias (Res. BCB nº 147/2021) para bloquear cautelarmente os valores.
  2. Separe o ID Fim-a-Fim (E2E) da transferência Pix, o comprovante com data/horário, o boleto suspeito e os prints das mensagens.
  3. Registre Boletim de Ocorrência (Delegacia Eletrônica) e abra reclamação no Banco Central (Meu BC) ou Consumidor.gov.br caso o banco negue o protocolo.

4. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Resolução BCB 147/2021 (Mecanismo Especial de Devolução do Pix), trecho inserido em Resolução BCB nº 1, de 12 de agosto de 2020, Art. 39-B: Art. 39-B. Os recursos oriundos de uma transação no âmbito do Pix deverão ser bloqueados cautelarmente pelo participante prestador de serviço de pagamento do usuário recebedor quan... (Fonte: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=147)
- [2] Lei 14.181/2021 (Lei do Superendividamento), trecho inserido em Lei nº 8.078, de 11 de setembro de 1990, Art. 6: Art. 6º [...] [...] XI - a garantia de práticas de crédito responsável, de educação financeira e de prevenção e tratamento de situações de superendividamento, preservado o mínimo e... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm)
- [3] Lei 14.690/2023 (Teto de juros do rotativo), Art. 30: Art. 30. A Lei nº 10.406, de 10 de janeiro de 2002 (Código Civil), passa a vigorar com as seguintes alterações: Vigência... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `False` | **Trava CVM:** `False` | **Citações Válidas:** `True` | **Revisão:** `False`
