# 01 · Problema e Essential Question

> Restrição do Challenge: **entender o problema antes da solução** e **usar evidências confiáveis**.
> Números conferidos nas fontes em **27/10/2026**. Cada dado traz o mês de referência e o link; atualize antes do relatório final se sair uma edição mais recente.

## 1. Big Idea → Essential Question

**Big Idea:** Qualidade de Vida. *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*

**Essential Question:**
> Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?

**Perguntas-guia:**
- O que a pessoa endividada **não consegue enxergar** sozinha na própria movimentação financeira?
- Em que momento uma intervenção (alerta, trava, conversa) muda de fato o comportamento, e quando ela vira ruído ou culpa?
- Que informação oficial (direitos, programas, normas) as pessoas desconhecem e que poderia reduzir o custo das dívidas?
- Como medir a melhora de **qualidade de vida**, e não só a de saldo?

## 2. O problema

### 2.1 Endividamento e inadimplência
- **81,7 milhões de brasileiros inadimplentes** em fevereiro de 2026, recorde da série, com mais de 332 milhões de dívidas e dívida média de R$ 6.598,13. São 38% mais inadimplentes que em 2016, e cerca de 42% deles já estavam negativados dez anos antes ([Serasa, Mapa da Inadimplência: 10 anos](https://www.serasa.com.br/imprensa/10-anos-do-mapa-de-inadimplencia/), mar/2026).
- **81,7% das famílias endividadas** em setembro de 2026, depois do recorde de 82% em julho e agosto. **29,6%** têm contas em atraso e **12,5%** dizem que não vão conseguir pagá-las ([CNC/Peic, set/2026](https://portaldocomercio.org.br/acoes-institucionais/cnc-inadimplencia-e-endividamento-das-familias-brasileiras-recuam-em-setembro/)).
- O **cartão de crédito** aparece em **85,3%** das famílias endividadas, a principal modalidade de dívida ([CNC/Peic, jul/2026](https://portaldocomercio.org.br/diario-executivo/cnc-endividamento-das-familias-sobe-para-82-mas-inadimplencia-cai/)).
- O **rotativo do cartão** custou **435,9% ao ano** para pessoas físicas em fevereiro de 2026 ([Agência Brasil, com dados do BCB](https://agenciabrasil.ebc.com.br/economia/noticia/2026-03/juros-do-cartao-de-credito-pesam-mais-para-familias-em-fevereiro)). O **cheque especial** fica em torno de 130% ao ano ([Senado Notícias, mai/2026](https://www12.senado.leg.br/noticias/infomaterias/2026/05/dividas-em-recorde-assombram-as-familias-brasileiras)). Para comparação, o crédito livre para pessoas físicas custou em média 61,7% ao ano em agosto de 2026, com inadimplência das famílias em 6% ([Agência Brasil, set/2026](https://agenciabrasil.ebc.com.br/economia/noticia/2026-09/juros-para-familias-sobem-em-agosto-e-inadimplencia-chega-6)).
- Limites legais que o PANDORA deve explicar ao usuário: juros e encargos do rotativo não podem passar de 100% do valor original da dívida (Lei 14.690/2023, em vigor desde jan/2024), e o cheque especial tem teto de 8% ao mês (Resolução CMN 4.765/2019).
- No produto, as taxas de referência vêm direto das séries temporais do Banco Central (API SGS) para comparar a taxa do usuário com a média de mercado ([05](05-dados-e-integracoes.md#4-dados-externos-de-referência)).

### 2.2 Apostas online (bets) e compulsão
- Com a regulamentação das apostas de quota fixa (Lei 14.790/2023) e o mercado autorizado pela Secretaria de Prêmios e Apostas (SPA/MF), o volume de transferências para bets cresceu de forma expressiva.
- Segundo o Banco Central, **R$ 20,8 bilhões** foram enviados via Pix a 56 empresas de apostas só em agosto de 2024, com transferências mensais entre R$ 18 e 21 bilhões ao longo do ano. Cerca de **24 milhões de pessoas** fizeram ao menos um Pix para bets, a maioria entre 20 e 30 anos ([BCB, Estudo Especial nº 119/2024](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf)).
- No mesmo mês, cerca de **5 milhões de pessoas de famílias do Bolsa Família** enviaram aproximadamente **R$ 3 bilhões** a empresas de apostas (mesmo estudo). Depois disso, o STF confirmou a liminar que obriga o governo a impedir o uso de benefícios sociais em apostas.
- Limitações do estudo: considera só o Pix (cartão e TED ficam de fora), mede valores apostados e não perdas líquidas, e é uma estimativa inicial. O próprio BCB reconheceu que pode haver falhas. O setor de apostas contestou os números.
- O jogo compulsivo é reconhecido como transtorno (CID-11 6C50, "gambling disorder") e está associado a endividamento, ansiedade e depressão.

### 2.3 Golpes financeiros
- Cerca de **24 milhões de brasileiros** caíram em golpes com Pix ou boleto entre julho de 2024 e junho de 2025, com prejuízo estimado de **quase R$ 29 bilhões**, ou R$ 1.198 por vítima em média. Idosos são o principal alvo dos boletos falsos, e os mais jovens, das fraudes em compras online (pesquisa Datafolha / Fórum Brasileiro de Segurança Pública, ago/2025, com 2.007 entrevistas; [Rádio Senado](https://www12.senado.leg.br/radio/1/noticia/2025/08/18/mais-de-24-milhoes-de-pessoas-foram-vitimas-de-golpes-pelo-pix)).
- Para quem já está endividado, um golpe agrava a crise. Por isso o Guardião combina detecção de anomalias com análise de boletos e prints e com orientação sobre os mecanismos de devolução do Pix.

### 2.4 Por que é um problema de qualidade de vida
- O estresse financeiro está ligado a pior saúde mental, insônia e menor produtividade. Escalas validadas medem esse efeito: *InCharge Financial Distress/Financial Well-Being Scale* (Prawitz et al., 2006) e *CFPB Financial Well-Being Scale*.
- A Lei do Superendividamento (Lei 14.181/2021) reconhece a preservação do **mínimo existencial** como direito, o que mostra que o problema é social e não só individual.

### 2.5 O que já existe e onde falha

| Solução atual | Limitação |
|---|---|
| Apps de controle de gastos | Exigem disciplina manual. Não tratam compulsão nem dívida |
| Apps dos bancos | Visão de uma só instituição. Incentivo a oferecer mais crédito |
| Feirões de renegociação (Serasa, Desenrola) | Pontuais, sem plano nem acompanhamento comportamental |
| Educação financeira genérica | Não parte dos dados reais da pessoa |
| Grupos de apoio (Jogadores Anônimos, CAPS) | Desconectados da vida financeira do dia a dia |

**Lacuna:** nenhuma dessas soluções junta **dados reais multi-banco + entendimento comportamental + conhecimento jurídico/oficial + acompanhamento contínuo** em uma experiência única e acolhedora.

## 3. Stakeholders

| Stakeholder | Interesse | Como o PANDORA considera |
|---|---|---|
| Pessoa endividada / com compulsão | Sair do sufoco sem julgamento | Usuário principal, foco de UX acolhedora |
| Família / contato de confiança | Apoiar sem invadir | "Modo crise" opcional com consentimento |
| Credores e bancos | Recuperar crédito | Propostas de renegociação realistas |
| Órgãos de defesa do consumidor (Procon, Defensoria) | Cumprimento da Lei 14.181 | Encaminhamento e geração de documentação |
| Reguladores (BCB, CVM, ANPD, SPA/MF) | Segurança, privacidade, limites | Guardrails, LGPD, sem conselho regulado |
| Profissionais de saúde mental | Encaminhamento adequado | Sinais de risco levam a CVV/CAPS/JA |
| Equipe acadêmica / banca | Rigor, métricas, justificativas | ADRs, avaliação objetiva |

## 4. Personas

| Persona | Contexto | Dor principal | O que o PANDORA faz por ela |
|---|---|---|---|
| **Carla, 34**, atendente, 2 filhos | Rotativo do cartão + empréstimo pessoal, renda comprometida em ~60% | "Não sei por onde começar" | Raio-X + plano de reestruturação + guia da Lei 14.181 |
| **Diego, 24**, entregador de app | Apostas diárias depois do repasse semanal, esconde da família | Vergonha, perda de controle | Detector de compulsão + travas + apoio especializado |
| **Sr. Antônio, 67**, aposentado | Consignado + foi vítima de golpe da falsa central | Medo e desconfiança | Guardião antifraude + análise de prints + proteção de benefício |
| **Júlia, 29**, CLT, recém-quitou dívidas | Quer não voltar ao vermelho e começar a investir | Insegurança, excesso de informação | Orçamento, metas, perfil e trilha educacional |

As personas também são usadas para gerar **dados sintéticos** e o **golden set** de avaliação ([06](06-riscos-e-metricas.md)).

## 5. Hipóteses a validar

1. Ver a própria situação consolidada e explicada em linguagem simples reduz a ansiedade e aumenta a adesão ao plano.
2. Detectar padrões de aposta automaticamente, com abordagem não estigmatizante, aumenta a adoção de travas voluntárias.
3. Respostas ancoradas em RAG sobre fontes oficiais são mais corretas e confiáveis que um LLM puro (comparação na Semana 3).
4. Um sistema multiagente especializado supera um agente único em qualidade e segurança das respostas em cenários financeiros complexos.

## 6. Fontes de evidência (corpus inicial)

- Banco Central do Brasil: estatísticas de juros (API SGS), Estudo Especial nº 119/2024 (apostas), Relatório de Cidadania Financeira, estudos especiais, Open Finance Brasil.
- CVM: Portal do Investidor, Resoluções 19/2021 e 20/2021 (consultoria e análise), 30/2021 (suitability).
- Tesouro Nacional: Tesouro Direto.
- Legislação: Lei 14.181/2021 (Superendividamento), Lei 14.690/2023 (teto do rotativo), Resolução CMN 4.765/2019 (teto do cheque especial), Decretos do mínimo existencial, Lei 14.790/2023 (apostas), CPC art. 833 (impenhorabilidade), Lei 8.009/1990 (bem de família), LGPD (Lei 13.709/2018).
- SPA/MF: lista de operadoras de apostas autorizadas e regras de jogo responsável.
- Serasa (Mapa da Inadimplência), CNC (Peic), Datafolha/Fórum Brasileiro de Segurança Pública (golpes), Procon, consumidor.gov.br, FEBRABAN.
- Literatura: escalas de bem-estar financeiro (CFPB, InCharge), estudos sobre jogo compulsivo.
