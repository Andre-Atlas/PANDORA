# Inventário das 31 fontes do catálogo

Gerado por `uv run pandora-rag inventario --md ../../docs/rag/10-inventario-fontes.md`, a partir da seção `catalogo` de `services/rag/fontes.yaml` e da situação em `services/rag/catalogo.lock.json`. Não edite à mão.

Situação do item: **coletada** (todos os alvos baixados), **mista** (parte baixada, parte manual), **manual** (nenhum alvo automático), **falha** (algum alvo falhou na última execução) ou **pendente** (ainda não coletado).

## Grupo 1: Educação, comportamento e psicometria

| # | Fonte | Órgão | Formato | Frequência | Situação | Alvos |
|---|---|---|---|---|---|---|
| 1 | Caderno de Educação Financeira: Gestão de Finanças Pessoais (2ª ed., 2026) | Banco Central do Brasil | pdf | anual | coletada | 1 automático(s) |
| 2 | Série Cidadania Financeira nº 8 (Endividamento de Risco) e RCF 2025 | Banco Central do Brasil | pdf | anual | mista | 1 automático(s), 1 manual(is) |
| 3 | Guia de Boas Práticas em Educação e Saúde Financeira (v7, 2025) e acervo Meu Bolso em Dia | Febraban e Banco Central do Brasil | manual | anual | manual | 1 manual(is) |
| 4 | Série CVM Comportamental, vols. 1 a 3 | Comissão de Valores Mobiliários | pdf | estatica | mista | 2 automático(s), 1 manual(is) |
| 5 | Livro TOP: Planejamento Financeiro Pessoal e Mercado de Valores Mobiliários (cap. 12) | CVM e Planejar | manual | estatica | manual | 1 manual(is) |
| 6 | Estudo Especial BCB 119/2024 e Raio X do Investidor Brasileiro (7ª a 9ª ed.) | Banco Central do Brasil e ANBIMA | pdf | semestral | mista | 1 automático(s), 1 manual(is) |
| 7 | Escalas psicométricas (IFDFW, CFPB, ICD-11 6C50) e Nudge | Prawitz et al.; CFPB; OMS; Thaler e Sunstein | manual | estatica | manual | 1 manual(is) |

## Grupo 2: Superendividamento e defesa patrimonial

| # | Fonte | Órgão | Formato | Frequência | Situação | Alvos |
|---|---|---|---|---|---|---|
| 8 | Lei 14.181/2021 (Superendividamento), CDC e decretos do mínimo existencial | Presidência da República | html | eventual | coletada | 4 automático(s) |
| 9 | Julgamento do STF nas ADPFs 1005, 1006 e 1097 (23/04/2026) | Supremo Tribunal Federal e Ministério Público Federal | html | eventual | mista | 2 automático(s), 1 manual(is) |
| 10 | Cartilha do Superendividamento do CNJ (2022) e Recomendação CNJ 125/2021 | Conselho Nacional de Justiça | pdf | estatica | mista | 1 automático(s), 1 manual(is) |
| 11 | Manual do TJSP, Programa de Apoio ao Superendividado (Procon-SP) e cartilha do Procon de Juiz de Fora | TJSP, Procon-SP e Procon Juiz de Fora | pdf | estatica | coletada | 3 automático(s) |
| 12 | Cenário do Superendividamento (SENACON/PNUD) e cartilhas das Defensorias e do MPCE | SENACON, PNUD e Defensorias Públicas | pdf | estatica | mista | 1 automático(s), 2 manual(is) |
| 13 | Defesa de bens e serviços: veículo (DL 911/69), imóvel (Lei 9.514/97), bem de família, penhora e serviços essenciais | Presidência da República e ANEEL | html | eventual | mista | 5 automático(s), 2 manual(is) |

## Grupo 3: Regulação bancária e jurisprudência

| # | Fonte | Órgão | Formato | Frequência | Situação | Alvos |
|---|---|---|---|---|---|---|
| 14 | Lei 14.690/2023 e Resolução CMN 5.112/2023 (teto do rotativo) | Presidência da República e Conselho Monetário Nacional | api, html | eventual | coletada | 2 automático(s) |
| 15 | Resoluções CMN 5.057/2022 e 5.265/2025 e Resolução Conjunta 15/2025 (portabilidade) | Conselho Monetário Nacional e Banco Central do Brasil | api | eventual | mista | 1 automático(s), 2 manual(is) |
| 16 | Resolução CMN 4.881/2020 (CET) e Resolução BCB 365/2023 (fatura de cartão) | Conselho Monetário Nacional e Banco Central do Brasil | api | eventual | mista | 1 automático(s), 1 manual(is) |
| 17 | Resoluções CMN 4.558/2017, 4.882/2020 e 4.655/2018 (comissão de permanência e encargos de atraso) | Conselho Monetário Nacional e Banco Central do Brasil | api | eventual | mista | 2 automático(s), 1 manual(is) |
| 18 | Tema Repetitivo 27 do STJ, Súmula 596/STF e Súmulas 283, 381, 382, 539 e 541/STJ | Superior Tribunal de Justiça e Supremo Tribunal Federal | pdf | eventual | mista | 1 automático(s), 2 manual(is) |
| 19 | Súmulas 359, 385, 479 e 548/STJ, Código Civil art. 206, Tema 1.264/STJ e Resolução BCB 147/2021 (MED) | STJ, Presidência da República e Banco Central do Brasil | api | eventual | mista | 1 automático(s), 2 manual(is) |
| 20 | Resoluções CVM 19, 20 e 30/2021 e Lei 13.709/2018 (LGPD) | Comissão de Valores Mobiliários e Presidência da República | pdf | eventual | mista | 3 automático(s), 1 manual(is) |

## Grupo 4: APIs dinâmicas e bases abertas

| # | Fonte | Órgão | Formato | Frequência | Situação | Alvos |
|---|---|---|---|---|---|---|
| 21 | API Olinda / OData: taxas de juros de operações de crédito (TaxaJuros v2) | Banco Central do Brasil | api | diaria | coletada | 1 automático(s) |
| 22 | Webservice SGS: séries temporais do Banco Central | Banco Central do Brasil | api | diaria | coletada | 13 automático(s) |
| 23 | SCR.data: base aberta de operações de crédito (v2) | Banco Central do Brasil | manual | mensal | manual | 1 manual(is) |
| 24 | Base aberta do Consumidor.gov.br, SINDEC e ranking de reclamações do BCB | SENACON/MJ e Banco Central do Brasil | manual | mensal | manual | 2 manual(is) |
| 25 | Série histórica da PEIC (CNC) e Mapa da Inadimplência (Serasa) | CNC e Serasa | manual | mensal | manual | 2 manual(is) |
| 26 | Lista oficial de operadoras de apostas autorizadas (.bet.br) | Secretaria de Prêmios e Apostas (SPA/MF) | html | mensal | mista | 1 automático(s), 1 manual(is) |

## Grupo 5: Datasets de QA, transações e avaliação

| # | Fonte | Órgão | Formato | Frequência | Situação | Alvos |
|---|---|---|---|---|---|---|
| 27 | Personal-Finance-Queries e personal-finance-advice-qa | Hugging Face (comunidade) | api | eventual | coletada | 2 automático(s) |
| 28 | cfpb-consumer-complaints e relatos-consumidor-gov-br | Hugging Face e Kaggle (comunidade) | api | eventual | mista | 1 automático(s), 1 manual(is) |
| 29 | fiqa-personal-finance-dataset, reclamacao-agua-e-saneamento, juris-tcu e normas-tcu | Hugging Face (comunidade e UFCA) | api | eventual | coletada | 4 automático(s) |
| 30 | brazilian-real-bank-dataset, ULB Credit Card Fraud, PaySim e amostra sintética das personas | Kaggle, OpenML e PANDORA | manual | estatica | manual | 4 manual(is) |
| 31 | FinQA, TAT-QA e ConvFinQA (benchmarks de avaliação, fora do banco vetorial) | Hugging Face (IBM Research, NExT, TheFinAI) | api | estatica | coletada | 3 automático(s) |

## Alvos de tratamento manual

| Item | Alvo | Motivo |
|---|---|---|
| 2 | `bcb-rcf-2025` | Relatório de Cidadania Financeira 2025: o catálogo não traz o link do PDF; localizar na página de Cidadania Financeira do BCB e incluir em fontes.yaml. |
| 3 | `febraban-guia-isfb` | Guia e acervo ficam em páginas da Febraban sem URL de arquivo estável; baixar o PDF à mão e registrar o hash. |
| 4 | `cvm-vieses-1` | Volume 1 (Vieses do Investidor) ainda não tem URL confirmada no manifesto; os volumes 2 e 3 já são coletados. |
| 5 | `livro-top-cvm-planejar` | Livro com direitos autorais e distribuição por cadastro; usar só o capítulo autorizado, obtido à mão. |
| 6 | `anbima-raio-x` | Edições do Raio X ficam em página da ANBIMA sem URL estável de arquivo; baixar cada edição à mão. |
| 7 | `escalas-psicometricas` | Instrumentos publicados em artigos e normas; não há feed. Os itens das escalas são transcritos à mão para o esquema do formulário. |
| 9 | `stf-acordao-adpfs` | Acórdão ainda não coletado: o portal do STF exige consulta por número do processo; acompanhar a publicação e incluir o PDF. |
| 10 | `cnj-rec-125` | Recomendação 125/2021 (Anexo II, formulário-padrão) está no sistema de atos normativos do CNJ; baixar o PDF à mão. |
| 12 | `senacon-pnud-produto-2` | Produto 2 (SENACON/PNUD) sem URL confirmada no catálogo; localizar e baixar à mão. |
| 12 | `defensorias-cartilhas` | Cartilhas de DPDF, DPRJ, DPES e MPCE vêm de quatro sites diferentes, cada um com seu link; baixar à mão. |
| 13 | `lei-14711` | Lei 14.711/2023 ainda fora do manifesto do corpus; confirmar a URL no Planalto e incluir em fontes. |
| 13 | `aneel-ren-1000` | REN ANEEL 1.000/2021 fora do manifesto; o texto compilado fica no sistema de legislação da ANEEL, sem URL de arquivo estável. |
| 15 | `cmn-5265` | Resolução CMN 5.265/2025 fora do manifesto; testar a URL da API de normativos do BCB (mesmo padrão da 5.057) e incluir em fontes. |
| 15 | `bcb-resolucao-conjunta-15` | Resolução Conjunta 15/2025 fora do manifesto; o parâmetro da API de normativos para atos conjuntos não foi confirmado. |
| 16 | `bcb-365` | Resolução BCB 365/2023 fora do manifesto; testar a URL da API de normativos (padrão da Res. BCB 147) e incluir em fontes. |
| 17 | `cmn-4655` | Resolução CMN 4.655/2018 fora do manifesto; testar a URL da API de normativos e incluir em fontes. |
| 18 | `stj-tema-27` | Tema 27 (REsp 1.061.530/RS) é consultado por número no portal de repetitivos do STJ, sem URL de arquivo estável. |
| 18 | `stf-sumula-596` | Súmula 596/STF é consultada por número no portal do STF, sem URL de arquivo estável. |
| 19 | `stj-tema-1264` | Tema 1.264 é consultado por número no portal de repetitivos do STJ, sem URL de arquivo estável. |
| 19 | `codigo-civil` | Código Civil compilado (art. 206, § 5º, I) fora do manifesto; confirmar a URL no Planalto e incluir em fontes. As súmulas 359, 385, 479 e 548 já vêm do PDF do STJ (item 18). |
| 20 | `lgpd` | Lei 13.709/2018 fora do manifesto do corpus; confirmar a URL no Planalto e incluir em fontes. |
| 23 | `scr-data` | Arquivos CSV/ZIP mensais de grande volume (mais de 700 mil séries); a carga em DuckDB/Parquet é tarefa do pipeline analítico, não da coleta bruta. |
| 24 | `consumidor-gov-br` | Base publicada no portal de dados abertos, com um arquivo por período e links que mudam; baixar à mão até haver URL estável. |
| 24 | `bcb-ranking-reclamacoes` | Ranking trimestral publicado como planilha em página do BCB sem URL fixa; baixar à mão. |
| 25 | `cnc-peic` | Séries publicadas em páginas e relatórios sem API nem URL estável. |
| 25 | `serasa-mapa-inadimplencia` | Mapa publicado em página institucional, sem API nem URL estável. |
| 26 | `spa-lista-bets` | Lista em página do Ministério da Fazenda, sem URL de arquivo confirmada; a normalização é a issue #59 (modelos auxiliares). |
| 28 | `kaggle-relatos-consumidor-gov-br` | Kaggle exige login e chave de API; baixar à mão. |
| 30 | `kaggle-brazilian-real-bank` | Kaggle exige login e chave de API; baixar à mão. |
| 30 | `ulb-credit-card-fraud` | Distribuído no Kaggle e no OpenML, com login; baixar à mão. |
| 30 | `kaggle-paysim` | Kaggle exige login e chave de API; baixar à mão. |
| 30 | `amostra-personas` | Já versionada no repositório (docs/evidencias/datasets/amostra_transacoes_sinteticas_personas.csv); não há o que coletar. |
