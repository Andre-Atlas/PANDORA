# 📚 Artigos Científicos, Estudos Técnicos e Marcos Legais — PANDORA

Este documento organiza a literatura acadêmica, os estudos técnicos institucionais e os diplomas legais que sustentam a concepção do **PANDORA**, servindo tanto para a fundamentação teórica do Challenge (CBL) quanto como **Corpus Oficial para o RAG** (`services/agents` + `pgvector`).

---

## 1. Bem-Estar Financeiro, Estresse (*Financial Distress*) e Qualidade de Vida

### 1.1 *InCharge Financial Distress / Financial Well-Being Scale (IFDFW)*
- **Referência completa:** PRAWITZ, A. D.; GARMAN, E. T.; SORHAINDO, B.; O'NEILL, B.; KIM, J.; DRENTEA, P. *InCharge Financial Distress/Financial Well-Being Scale: Development, Administration, and Score Interpretation*. **Journal of Financial Counseling and Planning**, v. 17, n. 1, p. 34–50, 2006.
- **Link de referência:** [AFCPE / Journal of Financial Counseling and Planning (Prawitz et al., 2006)](https://www.afcpe.org/news-and-publications/journal-of-financial-counseling-and-planning/)
- **Síntese científica:** Introduz uma escala psicométrica validada de 8 itens (pontuação de 1 a 10) que mede o *continuum* entre o sofrimento financeiro severo (*overwhelming financial distress*) e o bem-estar financeiro pleno, correlacionando-o diretamente com indicadores de saúde física, sono, ansiedade e produtividade no trabalho.
- **Aplicação no PANDORA:** Fundamenta a resposta à **Essential Question**: o PANDORA não mede sucesso apenas pelo saldo em conta, mas pela redução do estresse percebido (check-ins periódicos inspirados na escala IFDFW antes e depois do plano de reestruturação).

### 1.2 *CFPB Financial Well-Being Scale*
- **Referência completa:** CONSUMER FINANCIAL PROTECTION BUREAU (CFPB). *Measuring financial well-being: A guide to using the CFPB Financial Well-Being Scale*. Washington, D.C.: CFPB, 2015 / 2017.
- **Link oficial:** [CFPB Financial Well-Being Scale Guide](https://www.consumerfinance.gov/data-research/research-reports/financial-well-being-scale/)
- **Síntese científica:** Define bem-estar financeiro em quatro dimensões temporais (presente e futuro) e funcionais (segurança e liberdade de escolha): (1) controle sobre as finanças do dia a dia, (2) capacidade de absorver um choque financeiro, (3) estar no caminho para atingir metas financeiras e (4) liberdade financeira para fazer escolhas que permitam aproveitar a vida.
- **Aplicação no PANDORA:** Estrutura os pilares do **Score de Saúde Financeira** do **Módulo 1 (Raio-X)** e a progressão da jornada do usuário até o **Módulo 6 (Educação & Investimento)**.

### 1.3 *The Economic Importance of Financial Literacy: Theory and Evidence*
- **Referência completa:** LUSARDI, Annamaria; MITCHELL, Olivia S. *The Economic Importance of Financial Literacy: Theory and Evidence*. **Journal of Economic Literature**, v. 52, n. 1, p. 5–44, 2014.
- **Link de referência:** [American Economic Association — Lusardi & Mitchell (2014)](https://www.aeaweb.org/articles?id=10.1257/jel.52.1.5)
- **Síntese científica:** Demonstra empiricamente que o desconhecimento sobre juros compostos, inflação e diversificação de risco leva indivíduos a tomarem empréstimos de alto custo, pagarem taxas excessivas em cartões de crédito e acumularem menor patrimônio ao longo da vida. Também evidencia que educação financeira genérica tem baixo efeito se não for contextualizada no momento da decisão (*just-in-time financial education*).
- **Aplicação no PANDORA:** Corrobora o diferencial do **Módulo 6** e do **Copiloto Multimodal**: em vez de aulas teóricas desconectadas, o agente explica conceitos (CET, juros compostos, inflação, reserva de emergência) usando **os próprios números e contratos reais do usuário**.

---

## 2. Estudos Técnicos sobre Apostas Online, Compulsão e Cidadania Financeira

### 2.1 Análise Técnica sobre o Mercado de Apostas Online no Brasil e o Perfil dos Apostadores
- **Referência completa:** BANCO CENTRAL DO BRASIL (BCB). *Estudo Especial nº 119/2024 — Análise técnica sobre o mercado de apostas online no Brasil e o perfil dos apostadores*. Brasília: BCB, set. 2024.
- **Link oficial (PDF):** [Estudo Especial nº 119/2024 — BCB](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf)
- **Síntese técnica:** Estudo institucional pioneiro que mapeou as transferências via Pix para plataformas de apostas, revelando fluxo bruto entre R$ 18 bi e R$ 21 bi mensais, retenção líquida estimada em ~15% pelas plataformas, participação de 24 milhões de cidadãos e severo comprometimento da renda de famílias vulneráveis.
- **Aplicação no PANDORA:** Serve de base estatística e empírica para o **Módulo 2 (Detector de Compulsão)**, calibrando as heurísticas e features de ML (concentração etária, frequência de Pix para *bets*, comprometimento de renda de subsistência).

### 2.2 Transtorno do Jogo (*Gambling Disorder*) e Arquitetura de Escolha (*Nudges*)
- **Referências completas:**
  - WORLD HEALTH ORGANIZATION (WHO). *International Classification of Diseases, 11th Revision (ICD-11)* — Código `6C50` (*Gambling disorder*, predominantemente online: `6C50.1`). Genebra: OMS, 2019/2022. Link: [ICD-11 Browser — 6C50 Gambling disorder](https://icd.who.int/browse/2024-01/mms/en#1041487064)
  - THALER, Richard H.; SUNSTEIN, Cass R. *Nudge: Improving Decisions About Health, Wealth, and Happiness*. New Haven: Yale University Press, 2008.
- **Síntese científica:** O jogo compulsivo caracteriza-se por perda de controle sobre o ato de apostar, priorização crescente do jogo sobre outras atividades vitais e continuação ou escalada mesmo diante de consequências financeiras e familiares negativas (*chasing losses*). Abordagens punitivas ou baseadas em vergonha agravam o isolamento; intervenções baseadas em **fricção positiva** (*cooling-off periods*, travas voluntárias com atraso de desbloqueio) e *nudges* empáticos têm eficácia superior.
- **Aplicação no PANDORA:** Define os guardrails de comunicação do **Detector de Compulsão** e do **Guardião** (linguagem livre de julgamento, oferta de travas voluntárias com janela de reflexão e encaminhamento seguro ao CVV `188`, CAPS e Jogadores Anônimos).

---

## 3. Marcos Legais e Regulatórios (Corpus Primário do RAG)

Para respeitar a **Regra Inviolável nº 7** de [`AGENTS.md`](../../../AGENTS.md) (*"Sem Conselho Regulado: toda afirmação sobre direitos ou normas cita a fonte"*), os agentes do PANDORA consultam via RAG os seguintes diplomas normativos oficiais:

| Norma / Diploma Legal | Tema Principal | Link Oficial | Como o Agente Utiliza |
|---|---|---|---|
| **Lei nº 14.181/2021** | **Lei do Superendividamento** (altera o CDC — arts. 54-A a 54-G e 104-A a 104-C) | [Planalto — Lei 14.181/2021](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm) | Orienta o usuário sobre o direito à **repactuação global de dívidas** em audiência conciliatória (plano de até 5 anos) com preservação do **mínimo existencial** (Procon / Defensoria / CEJUSC). |
| **Lei nº 14.690/2023** | **Teto dos Juros do Rotativo do Cartão de Crédito** (Programa Desenrola Brasil) | [Planalto — Lei 14.690/2023](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm) | Verifica se os juros e encargos cobrados no rotativo/parcelamento de fatura a partir de jan/2024 respeitam o limite legal de **100% do valor original da dívida**. |
| **Resolução CMN nº 4.765/2019** | **Teto de Juros do Cheque Especial para Pessoas Físicas** | [BCB — Resolução CMN 4.765/2019](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o&numero=4765) | Audita se a instituição financeira está respeitando o limite máximo de **8% ao mês** no cheque especial. |
| **Lei nº 14.790/2023** | **Marco Regulatório das Apostas de Quota Fixa (*Bets*)** | [Planalto — Lei 14.790/2023](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm) | Fundamenta os direitos do apostador: proibição de apostas com cartão de crédito/benefícios sociais, mecanismos obrigatórios de **autoexclusão**, limites de tempo/perda e alertas de jogo responsável. |
| **Resolução BCB nº 147/2021** (e atualizações do Regulamento do Pix) | **Mecanismo Especial de Devolução (MED) do Pix** | [BCB — Regulamento do Pix e MED](https://www.bcb.gov.br/estabilidadefinanceira/pix) | Orienta vítimas de golpes (como a persona **Sr. Antônio**) sobre o prazo de até 80 dias e o passo a passo imediato para solicitar o bloqueio cautelar e devolução de valores via MED junto ao banco e registro de B.O. |
| **Lei nº 8.009/1990** & **CPC art. 833** | **Impenhorabilidade do Bem de Família e de Salários/Aposentadorias** | [Planalto — Lei 8.009/1990](https://www.planalto.gov.br/ccivil_03/leis/l8009.htm) | Tranquiliza o usuário endividado que sofre ameaças abusivas de cobrança, explicando o que é legalmente impenhorável (moradia única da família, salários, proventos de aposentadoria, salvo exceções legais). |
| **Resoluções CVM nº 19/2021, 20/2021 e 30/2021** | **Consultoria, Análise de Valores Mobiliários e Suitability** | [CVM — Legislação e Normas](https://www.gov.br/cvm/pt-br/assuntos/normas) | Delimita a fronteira regulatória do **Módulo 6**: o PANDORA pode oferecer educação financeira e simuladores de classes de ativos, mas **jamais** recomenda títulos ou ativos mobiliários específicos. |
| **Lei nº 13.709/2018 (LGPD)** | **Lei Geral de Proteção de Dados Pessoais** | [Planalto — Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) | Rege o consentimento granular, mascaramento de PII antes de chamadas a LLMs externos e direito de exclusão integral (inclusive *embeddings* vetoriais). |
