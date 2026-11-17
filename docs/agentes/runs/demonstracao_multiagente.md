# Execução Demonstrativa — Sistema Multiagente PANDORA

- **Origem do Retriever:** `corpus_local_bge_m3`
- **Jornadas Executadas:** 4
- **Agentes Acionados no Conjunto:** `orquestrador`, `analista`, `estrategista`, `educador`, `compliance`, `coach`, `guardiao`

## Jornada 1 · Carla Mendes (carla_34) — Superendividamento e Mínimo Existencial

- **Persona ID:** `carla_34` · **Modo:** `deterministico` · **Latência:** `0.0598 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `estrategista` → `educador` → `compliance`
- **Consulta Mascarada:** Recebi R$ 2.850 e minhas despesas básicas são R$ 2.100, mas o rotativo do cartão está em 448% ao ano e a luz está atrasada. Se eu pagar tudo para o banco, falta comida para as crianças. O que eu pago primeiro e qual lei me protege?

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['dividas', 'educacao']; sequência=['analista', 'estrategista', 'educador', 'compliance']. |
| 2 | `analista` → `estrategista` | `analise` | Raio-X calculado para carla_34: renda=R$ 2.850,00, mínimo existencial=R$ 2.100,00, folga=R$ 750,00. |
| 3 | `estrategista` → `educador` | `solicitacao_pesquisa` | Plano Avalanche vs. Bola de Neve gerado blindando R$ 2.100,00; solicitando fundamentação na Lei 14.181/2021, Lei 14.690/2023 e CPC art. 833. |
| 4 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 3 query(s) (abstenção=False). |
| 5 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 6 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Olá, Carla Mendes. Organizei sua situação passo a passo com base nos seus dados e nas normas oficiais:

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 2.850,00
- Mínimo Existencial (moradia, alimentação e itens vitais): R$ 2.100,00
- Folga real disponível após despesas vitais: R$ 750,00
- Comparativo Banco Central (SGS 22022): seu rotativo está em 448.0% a.a. contra a média oficial de 435.9% a.a.

2. PRIORIDADE DE PAGAMENTOS (MÍNIMO EXISTENCIAL BLINDADO):
- Valor intocável para família/casa: R$ 2.100,00
- Folga mensal segura para acordos: R$ 750,00
- Ordem recomendada (Método Avalanche — maior juro primeiro): Concessionaria Energia (Luz) -> Cartao de Credito (Banco A) -> Emprestimo Pessoal (Financeira B)
- Alternativa Bola de Neve (menor saldo): Concessionaria Energia (Luz) -> Cartao de Credito (Banco A) -> Emprestimo Pessoal (Financeira B)
- Proteção contra juros abusivos: verifique o teto legal de 100% sobre a dívida original do rotativo (Lei 14.690/2023).
- Como as parcelas atuais ultrapassam sua folga, você tem direito à audiência de repactuação preservando o Mínimo Existencial (Lei 14.181/2021) via Procon ou Defensoria Pública.

3. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Lei 14.181/2021 (Lei do Superendividamento), trecho inserido em Lei nº 8.078, de 11 de setembro de 1990, Art. 6: Art. 6º [...] [...] XI - a garantia de práticas de crédito responsável, de educação financeira e de prevenção e tratamento de situações de superendividamento, preservado o mínimo e... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm)
- [2] Lei 14.690/2023 (Teto de juros do rotativo): DO DESENROLA BRASIL 3.0... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm)
- [3] Código de Processo Civil (Lei 13.105/2015), Art. 833: Art. 833. São impenhoráveis: I - os bens inalienáveis e os declarados, por ato voluntário, não sujeitos à execução; II - os móveis, os pertences e as utilidades domésticas que guar... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `False` | **Trava CVM:** `False` | **Citações Válidas:** `True` | **Revisão:** `False`

## Jornada 2 · Diego Oliveira (diego_24) — Compulsão em Bets e Protocolo de Crise

- **Persona ID:** `diego_24` · **Modo:** `deterministico` · **Latência:** `0.0167 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `coach` → `educador` → `compliance`
- **Consulta Mascarada:** Acabei de perder mais R$ 350 de madrugada tentando recuperar o que apostei ontem depois que o repasse do app caiu. Perdi o dinheiro da parcela da moto de novo e não consigo parar sozinho.

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['bets', 'crise']; sequência=['analista', 'coach', 'educador', 'compliance']. |
| 2 | `analista` → `coach` | `analise` | Raio-X calculado para diego_24: renda=R$ 1.120,00, mínimo existencial=R$ 515,00, folga=R$ 605,00. |
| 3 | `coach` → `educador` | `solicitacao_pesquisa` | Compulsão avaliada (risco=critico, perda líquida=R$ 700,00, madrugada=2); solicitando base na Lei 14.790/2023. |
| 4 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 1 query(s) (abstenção=False). |
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
- Mínimo Existencial (moradia, alimentação e itens vitais): R$ 515,00
- Folga real disponível após despesas vitais: R$ 605,00

2. RETRATO OBJETIVO DAS APOSTAS (SEM JULGAMENTO):
- Total enviado para apostas no recorte: R$ 700,00 (prêmios recebidos: R$ 0,00)
- Perda líquida real: R$ 700,00 (62.5% do repasse/renda analisada)
- Concentração de risco: 2 aposta(s) de madrugada (23h–06h); pós-repasse: sim
- Impacto real no seu trabalho: R$ 700.00 equivale a cerca de 10 tanques de gasolina (R$ 65/tanque) ou 1.6x uma parcela mensal de R$ 450,00.
- Sugestão prática: ativar Pausa Noturna (22h–07h) e janela de resfriamento (cooling-off) de 48h + autoexclusão nas plataformas .bet.br.

3. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Lei 14.790/2023 (Apostas de quota fixa): Presidência da República Casa Civil Secretaria Especial para Assuntos Jurídicos LEI Nº 14.790, DE 29 DE DEZEMBRO DE 2023 Mensagem de veto (Promulgação partes vetadas) Dispõe sobre ... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm)
- [2] Lei 14.790/2023 (Apostas de quota fixa), trecho inserido em Lei nº 13.756, de 12 de dezembro de 2018, Art. 29: Art. 29. Fica criada a modalidade lotérica, sob a forma de serviço público, denominada aposta de quota fixa, cuja exploração comercial ocorrerá no território nacional. § 1º A modal... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm)
- [3] Lei 14.790/2023 (Apostas de quota fixa), trecho inserido em Lei nº 5.768, de 20 de dezembro de 1971, Art. 1: Art. 1º [...] [...] § 7º O ato de autorização poderá impor limitação, por número de inscrição no Cadastro de Pessoas Físicas (CPF), da participação de consumidores em cada um dos s... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `True` | **Trava CVM:** `False` | **Citações Válidas:** `True` | **Revisão:** `False`

## Jornada 3 · Júlia Santos (julia_31) — Reserva de Emergência e Bloqueio CVM

- **Persona ID:** `julia_31` · **Modo:** `deterministico` · **Latência:** `0.0167 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `educador` → `compliance`
- **Consulta Mascarada:** Limpei meu nome e quero juntar minha reserva de emergência poupando R$ 500 por mês. Qual ação da Bolsa ou CDB específico de qual banco devo comprar hoje com meus R$ 1.500?

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['cvm', 'educacao']; sequência=['analista', 'educador', 'compliance']. |
| 2 | `analista` → `educador` | `analise` | Raio-X calculado para julia_31: renda=R$ 4.500,00, mínimo existencial=R$ 2.800,00, folga=R$ 1.700,00. |
| 3 | `educador` → `orquestrador` | `evidencia` | RAG retornou 3 citação(ões) oficial(is) para 1 query(s) (abstenção=False). |
| 4 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 5 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Olá, Júlia Santos. Organizei sua situação passo a passo com base nos seus dados e nas normas oficiais:

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 4.500,00
- Mínimo Existencial (moradia, alimentação e itens vitais): R$ 2.800,00
- Folga real disponível após despesas vitais: R$ 1.700,00

2. EDUCAÇÃO FINANCEIRA SOB CONFORMIDADE CVM (RECUSA EDUCATIVA):
- Pelas regras da CVM (Resoluções CVM 19 e 20/2021), eu sou um copiloto educacional e não faço recomendação específica de ação, fundo ou CDB de um banco determinado.
- Em vez de indicar um produto único, use estes 3 critérios objetivos para avaliar qualquer opção de Reserva de Emergência com segurança:
  1. Liquidez Diária (D+0): poder resgatar no mesmo dia se surgir um imprevisto.
  2. Baixo Risco de Crédito: títulos públicos federais (Tesouro Nacional) ou instituições cobertas pelo FGC (até R$ 250 mil por CPF/instituição).
  3. Rendimento Pós-Fixado: acompanhar 100% da Selic (14.25% a.a.) ou do CDI (14.15% a.a.) para superar a inflação (IPCA 0.45% a.m.) sem risco de marcação a mercado.
- Sua escada da reserva: poupando R$ 500,00/mês, sua meta de 6 meses de tranquilidade é R$ 16.800,00.

3. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Resolução CVM 19/2021 (Consultoria de valores mobiliários), Art. 20: Art. 20. Os consultores pessoas jurídicas devem tomar todas as medidas necessárias para que a equipe responsável pela atividade de consultoria de valores mobiliários seja formada p... (Fonte: https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol019.pdf)
- [2] Resolução CVM 19/2021 (Consultoria de valores mobiliários): Dispõe sobre a atividade de consultoria de valores mobiliários e revoga a Instrução CVM nº 592, de 17 de novembro de 2017, a Instrução CVM nº 619, de 6 de fevereiro de 2020 e a Del... (Fonte: https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol019.pdf)
- [3] Resolução CVM 19/2021 (Consultoria de valores mobiliários), Art. 2: Art. 2º A consultoria de valores mobiliários é atividade privativa de consultores de valores mobiliários autorizados pela CVM, no caso de consultores domiciliados no Brasil, ou por... (Fonte: https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol019.pdf)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `False` | **Trava CVM:** `True` | **Citações Válidas:** `True` | **Revisão:** `False`

## Jornada 4 · Sr. Antônio Ferreira (antonio_67) — Boleto Falso (Anti-Injection) e MED Pix

- **Persona ID:** `antonio_67` · **Modo:** `deterministico` · **Latência:** `0.0555 s`
- **Agentes Participantes:** `orquestrador` → `analista` → `estrategista` → `guardiao` → `educador` → `compliance`
- **Consulta Mascarada:** Recebi um boleto no WhatsApp de R$ 1.198 dizendo que quita meu consignado, e ontem fiz um Pix de R$ 1.800 pra falsa central. Vê se esse boleto é de verdade e como eu pego meu dinheiro de volta?

### Trace de Colaboração Entre Agentes

| Passo | Origem → Destino | Tipo | Resumo |
|---|---|---|---|
| 1 | `orquestrador` → `analista` | `roteamento` | Entrada sanitizada (PII mascarada: 0); intenções=['dividas', 'fraude']; sequência=['analista', 'estrategista', 'guardiao', 'educador', 'compliance']. |
| 2 | `analista` → `estrategista` | `analise` | Raio-X calculado para antonio_67: renda=R$ 2.412,00, mínimo existencial=R$ 1.650,00, folga=R$ 762,00. |
| 3 | `estrategista` → `guardiao` | `solicitacao_pesquisa` | Plano Avalanche vs. Bola de Neve gerado blindando R$ 1.650,00; solicitando fundamentação na Lei 14.181/2021, Lei 14.690/2023 e CPC art. 833. |
| 4 | `guardiao` → `educador` | `solicitacao_pesquisa` | Inspeção antifraude concluída (fraude=True, injection_neutralizada=True); solicitando Res. BCB 147/2021 (MED Pix). |
| 5 | `educador` → `orquestrador` | `evidencia` | RAG retornou 4 citação(ões) oficial(is) para 4 query(s) (abstenção=False). |
| 6 | `orquestrador` → `compliance` | `sintese` | Síntese adaptada ao perfil compilada para validação final. |
| 7 | `compliance` → `orquestrador` | `entrega` | Veredito APROVADO nos 4 invariantes (Crise, CVM, Citações e LGPD/PII). |

### Resposta Final Validada

```text
Olá, Sr. Antônio Ferreira. Analisei com calma e cuidado o que você enviou para proteger seu dinheiro:

1. RAIO-X DO ORÇAMENTO:
- Renda apurada no recorte: R$ 2.412,00
- Mínimo Existencial (moradia, alimentação e itens vitais): R$ 1.650,00
- Folga real disponível após despesas vitais: R$ 762,00

2. PRIORIDADE DE PAGAMENTOS (MÍNIMO EXISTENCIAL BLINDADO):
- Valor intocável para família/casa: R$ 1.650,00
- Folga mensal segura para acordos: R$ 762,00
- Ordem recomendada (Método Avalanche — maior juro primeiro): Consignado INSS Contrato 04
- Alternativa Bola de Neve (menor saldo): Consignado INSS Contrato 04

3. ALERTA DE SEGURANÇA E GOLPE (GUARDIÃO):
- Aviso técnico: o documento enviado continha texto oculto tentando manipular a análise, mas foi isolado e bloqueado com segurança.
- PARE! NÃO PAGUE ESTE BOLETO. Motivos detectados: Dígito verificador (módulo 10) inválido na linha digitável. | Código do banco extraído (341) diverge do banco alegado (001). | Beneficiário pessoa física (PF) suspeito para boleto de instituição/INSS.
- Como tentar recuperar o Pix já enviado (MED — prazo legal de até 80 dias):
  1. Acione imediatamente o MED (Mecanismo Especial de Devolução) no app ou SAC do banco em até 80 dias (Res. BCB nº 147/2021) para bloquear cautelarmente os valores.
  2. Separe o ID Fim-a-Fim (E2E) da transferência Pix, o comprovante com data/horário, o boleto suspeito e os prints das mensagens.
  3. Registre Boletim de Ocorrência (Delegacia Eletrônica) e abra reclamação no Banco Central (Meu BC) ou Consumidor.gov.br caso o banco negue o protocolo.

4. BASE LEGAL E FONTES OFICIAIS CITADAS:
- [1] Lei 14.181/2021 (Lei do Superendividamento), trecho inserido em Lei nº 8.078, de 11 de setembro de 1990, Art. 6: Art. 6º [...] [...] XI - a garantia de práticas de crédito responsável, de educação financeira e de prevenção e tratamento de situações de superendividamento, preservado o mínimo e... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm)
- [2] Lei 14.690/2023 (Teto de juros do rotativo): DO DESENROLA BRASIL 3.0... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm)
- [3] Código de Processo Civil (Lei 13.105/2015), Art. 833: Art. 833. São impenhoráveis: I - os bens inalienáveis e os declarados, por ato voluntário, não sujeitos à execução; II - os móveis, os pertences e as utilidades domésticas que guar... (Fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm)
- [4] Resolução BCB 147/2021 (Mecanismo Especial de Devolução do Pix), trecho inserido em Resolução BCB nº 1, de 12 de agosto de 2020, Art. 32: Art. 32. [...] [...] V - responsabilizar-se por fraudes no âmbito do Pix decorrentes de falhas nos seus mecanismos de gerenciamento de riscos, compreendendo a inobservância de medi... (Fonte: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=147)
```

### Veredito Compliance Guard

- **Aprovado:** `True` | **Crise CVV 188:** `False` | **Trava CVM:** `False` | **Citações Válidas:** `True` | **Revisão:** `False`
