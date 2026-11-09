# 6. Demonstração

Cada execução abaixo é a saída literal do comando `pandora-rag ask`, rodando localmente (bge-m3 + BM25 + reranker + qwen2.5:14b via Ollama, sem API externa, custo zero). Em cada uma aparecem: **a consulta**, **os chunks recuperados** com score e trecho, **a resposta fundamentada** com marcadores `[n]` e **as fontes** com link oficial e trecho. Os arquivos brutos estão em [demo/](demo/).

```bash
cd services/rag
uv run pandora-rag ask "sua pergunta"            # consulta completa
uv run pandora-rag buscar "sua pergunta" --rerank   # só a recuperação, sem LLM
```

## 6.1 Pergunta normativa

**O que mostra:** recuperação de lei e cartilha, resposta que cita as duas.

```text
PERGUNTA: Minha dívida do cartão está muito alta. O que a Lei do Superendividamento prevê para eu renegociar com todos os credores de uma vez?

CHUNKS RECUPERADOS:
  [1] Cartilha do Superendividamento do Procon de Juiz de Fora   score=0.994
      "Lei do superendividamento, você sabe o que diz? A Lei Federal nº. 14.181/21 altera a Lei nº 8.078, de 11 de setembro de 1990 (Código de Defesa do Consumidor), e a Lei nº 10.741, de 1º de outubro de 2003 (Estatuto do Idos..."
  [2] Cartilha do Superendividamento do Procon de Juiz de Fora   score=0.980
      "O que pode ser renegociado? A renegociação engloba as chamadas dívidas de consumo, como são os boletos e carnês, em sua maioria. Contas de água e luz, empréstimos contratados em bancos e financeiras, crediários e parcela..."
  [3] Cartilha sobre o Tratamento do Superendividamento do Consumidor   score=0.969
      "13. No Brasil, há proteção legal ao superendividado? Sim, o Código de Defesa do Consumidor previu a possibilidade de revisão e/ou repactuação das dívidas de forma consensual ou obrigatória para reorganizar o orçamento fa..."
  [4] Lei 14.181/2021 (Lei do Superendividamento), inserido em Código de Defesa do Consumidor (Lei 8.078/1990) Art. 104-B  score=0.964
      "Art. 104-B. Se não houver êxito na conciliação em relação a quaisquer credores, o juiz, a pedido do consumidor, instaurará processo por superendividamento para revisão e integração dos contratos e repactuação das dívidas..."
  [5] Lei 14.181/2021 (Lei do Superendividamento), inserido em Código de Defesa do Consumidor (Lei 8.078/1990) Art. 104-C  score=0.961
      "Art. 104-C. Compete concorrente e facultativamente aos órgãos públicos integrantes do Sistema Nacional de Defesa do Consumidor a fase conciliatória e preventiva do processo de repactuação de dívidas, nos moldes do art. 1..."

RESPOSTA (qwen2.5:14b, 6.2s, US$ 0.0000):
A Lei do Superendividamento permite que você renegocie todas as suas dívidas de consumo ao mesmo tempo, incluindo cartões de crédito, empréstimos e parcelamentos, em um único processo. Você pode procurar os órgãos de defesa do consumidor ou o Judiciário para iniciar esse procedimento. Durante a conciliação, será elaborado um plano de pagamentos que caiba no seu orçamento, garantindo que você possa manter as necessidades básicas de sobrevivência. Se algum credor não comparecer ou recusar a renegociação, o juiz pode instaurar um processo judicial para definir um plano compulsório de pagamento. [1][2][4]

FONTES:
  [1] Cartilha do Superendividamento do Procon de Juiz de Fora 
      https://www.pjf.mg.gov.br/administracao_indireta/procon/material_grafico/cartilhas/arquivos/superendividamento.pdf
      trecho: "Lei do superendividamento, você sabe o que diz? A Lei Federal nº. 14.181/21 altera a Lei nº 8.078, de 11 de setembro de 1990 (Código de Defesa do Consumidor), e a Lei nº 10.741, de 1º de outubro de 2003 (Estatuto do Idos..."
  [2] Cartilha do Superendividamento do Procon de Juiz de Fora 
      https://www.pjf.mg.gov.br/administracao_indireta/procon/material_grafico/cartilhas/arquivos/superendividamento.pdf
      trecho: "O que pode ser renegociado? A renegociação engloba as chamadas dívidas de consumo, como são os boletos e carnês, em sua maioria. Contas de água e luz, empréstimos contratados em bancos e financeiras, crediários e parcela..."
  [4] Lei 14.181/2021 (Lei do Superendividamento), inserido em Código de Defesa do Consumidor (Lei 8.078/1990) Art. 104-B
      https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm
      trecho: "Art. 104-B. Se não houver êxito na conciliação em relação a quaisquer credores, o juiz, a pedido do consumidor, instaurará processo por superendividamento para revisão e integração dos contratos e repactuação das dívidas..."
```

**Leitura:** os cinco chunks são da cartilha do Procon e da Lei 14.181 (Arts. 104-B e 104-C), com scores acima de 0,96. A resposta cita [1], [2] e [4], e cada citação aponta para a fonte oficial. A descrição do processo por superendividamento (plano compulsório quando o credor recusa) corresponde ao Art. 104-B recuperado.

## 6.2 Pergunta de persona (linguagem do dia a dia)

**O que mostra:** pergunta informal, sem citar lei, ainda assim chegando ao artigo certo.

```text
PERGUNTA: Deixei de pagar a fatura do cartão e os juros do rotativo estão enormes. Existe um limite para o que o banco pode cobrar de juros?

CHUNKS RECUPERADOS:
  [1] Lei 14.690/2023 (Teto de juros do rotativo) Art. 28  score=0.987
      "Art. 28. Os emissores de cartão de crédito e de outros instrumentos de pagamento pós-pagos utilizados em arranjos abertos ou fechados, como medida de autorregulação, devem submeter à aprovação do Conselho Monetário Nacio..."
  [2] Lei 14.690/2023 (Teto de juros do rotativo) Art. 27  score=0.814
      "Art. 27. As instituições criadas por lei própria ou autorizadas a funcionar pelo Banco Central do Brasil e outras instituições que ofereçam crédito deverão adotar medidas de educação financeira direcionadas aos seus cons..."
  [3] Resolução CMN 5.112/2023 (Rotativo e portabilidade da fatura), inserido em Resolução CMN 4.549/2017 Art. 2-A  score=0.475
      "Art. 2º-A Para os fins do disposto no art. 28 da Lei nº 14.690, de 3 de outubro de 2023, consideram-se: I - operação de crédito para financiamento do saldo devedor da fatura de cartão de crédito e de demais instrumentos ..."
  [4] Resolução CMN 5.112/2023 (Rotativo e portabilidade da fatura), inserido em Resolução CMN 4.549/2017 Art. 2-B  score=0.390
      "Art. 2º-B O valor original da dívida, bem como o valor total cobrado a título de juros e encargos financeiros aplicáveis a cada operação de crédito para financiamento do saldo devedor da fatura de cartão de crédito e dem..."
  [5] Resolução CMN 5.112/2023 (Rotativo e portabilidade da fatura), inserido em Resolução CMN 4.549/2017 Art. 2-C  score=0.290
      "Art. 2º-C É assegurada, a qualquer momento, a renegociação das operações de crédito de que trata o art. 2º-A, desde que o valor total cobrado a título de juros e encargos financeiros aplicáveis a cada renegociação não ex..."

RESPOSTA (qwen2.5:14b, 6.5s, US$ 0.0000):
Sim, existe um limite. Se o banco não aprovar limites para juros e encargos financeiros no crédito rotativo no prazo de 90 dias após a publicação da Lei 14.690/2023, o total cobrado de juros e encargos não pode exceder o valor original da dívida [1][3].

FONTES:
  [1] Lei 14.690/2023 (Teto de juros do rotativo) Art. 28
      https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm
      trecho: "Art. 28. Os emissores de cartão de crédito e de outros instrumentos de pagamento pós-pagos utilizados em arranjos abertos ou fechados, como medida de autorregulação, devem submeter à aprovação do Conselho Monetário Nacio..."
  [3] Resolução CMN 5.112/2023 (Rotativo e portabilidade da fatura), inserido em Resolução CMN 4.549/2017 Art. 2-A
      https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=5112
      trecho: "Art. 2º-A Para os fins do disposto no art. 28 da Lei nº 14.690, de 3 de outubro de 2023, consideram-se: I - operação de crédito para financiamento do saldo devedor da fatura de cartão de crédito e de demais instrumentos ..."
```

**Leitura:** a busca encontrou o Art. 28 da Lei 14.690 e a Resolução CMN 5.112, que são a base do teto de juros do rotativo, e o link de cada uma está na resposta. A resposta, porém, é curta e imprecisa: o prazo de 90 dias é para os emissores submeterem uma proposta ao CMN, e a resposta não cita o Art. 2º-B da Resolução 5.112 (chunk [4], recuperado mas não usado), que trata do valor total cobrado de juros e encargos. Ou seja, a recuperação funcionou melhor do que a geração.

## 6.3 Pergunta fora do escopo (abstenção)

**O que mostra:** o portão de abstenção. A nota do melhor chunk (0,007) fica abaixo do limiar de 0,02, então o LLM nem é chamado e o sistema não inventa uma recomendação.

```text
PERGUNTA: Qual criptomoeda vai render mais no próximo mês?

CHUNKS RECUPERADOS:
  [1] Caderno de Educação Financeira: Gestão de Finanças Pessoais   score=0.007
      "Para que seu dinheiro se multiplique nesse tipo de apostas ou jogos, você precisa contar com a sorte. Para vencer e recuperar seu dinheiro, você depende de seu palpite. Se não acertar, não apenas deixa de multiplicar seu..."
  [2] Série Cidadania Financeira nº 8: Endividamento de Risco   score=0.001
      "R+M e R+I Análise 1 (critérios atuais): Não endiv. Endiv. (1 mês) Endiv. (2 ou + meses) Análise 2 (tempo de endiv.): R+I; R+M e M+I (1 mês) R+R (1 mês) e R+R ( 2 ou + meses) Outros (2 ou + meses) Análise 2 extra (abertur..."
  [3] Série Cidadania Financeira nº 8: Endividamento de Risco   score=0.000
      "5% 10% 29% 24% 33% 5% 13% 26% 25% 31% Ótimo 6% 12% 26% 24% 31% 8% 11% 25% 23% 33% 7% 14% 32% 26% 21% 3% 17% 28% 24% 28% 7% 15% 30% 17% 30% 9% 15% 31% 21% 24% Não ER Fora do SCR 10% 15% 31% 20% 25% 18% 30% 20% 25% Fora do..."
  [4] Caderno de Educação Financeira: Gestão de Finanças Pessoais   score=0.000
      "Já a caderneta de poupança, que popularmente é muitas vezes chamada apenas de “poupança”, é um tipo de investimento, que paga rendimento uma vez por mês, na “data de aniversário”. Ou seja, a caderneta de poupança é apena..."
  [5] Caderno de Educação Financeira: Gestão de Finanças Pessoais   score=0.000
      "a) Liquidez é a possibilidade de o investimento ser transformado em dinheiro vivo a qualquer momento, por um preço justo. b) Risco é a probabilidade de ocorrência de perdas. Normalmente, quanto maior o risco, maior a pro..."

RESPOSTA (portao, 0.0s, US$ 0.0000):
Não encontrei isso nas fontes oficiais que tenho, então não vou arriscar uma resposta. Para esse caso, procure o Procon, a Defensoria Pública ou o canal de atendimento do Banco Central.

FONTES:
  (abstenção: sem trecho que sustente a resposta)
```

## 6.4 Limitações observadas (execuções reais, mantidas de propósito)

Duas consultas em que o sistema **não** se saiu bem. Estão aqui porque a avaliação pede rastreabilidade das fontes, e rastrear também serve para enxergar onde a resposta não se sustenta.

### Consignado: recuperação fraca e resposta não sustentada

```text
PERGUNTA: Sou aposentada e tenho vários empréstimos consignados. Descontam tanto no meu benefício que mal sobra para comer. Existe algum limite para esse desconto?

CHUNKS RECUPERADOS:
  [1] Prevenção e Tratamento do Superendividamento   score=0.307
      "A política do estímulo ao crédito popular do governo Lula foi responsável por ampliar o consumo entre a população de baixa renda que absorveu cerca de 17 bilhões de reais ofertados no mercado. Entre 2005 e 2006, 2,15 mil..."
  [2] Prevenção e Tratamento do Superendividamento   score=0.201
      "Caracterização do Caso: Tadeu recorreu ao Projeto de Tratamento do Superendividamento na expectativa de celebrar com os credores acordo que viabilizasse o pagamento de suas dívidas sem comprometer o sustento da família. ..."
  [3] Prevenção e Tratamento do Superendividamento   score=0.043
      "Agravo de Instrumento conhecido e parcialmente provido.” (Terceira Turma Cível do TJDF,Agravo de Instrumento Nº 2006 00 2 012026-6 , Agravante Bradesco ,Agravado Assistência Judiciária do Distrito Federal e Ministério Pú..."
  [4] Prevenção e Tratamento do Superendividamento   score=0.022
      "Perfil do Superendividado: MARTA, 64 anos Divorciada Sem dependentes Aposentada Renda individual mensal: R$ 760,00 Renda familiar mensal: a mesma Despesas mensais correntes: luz R$ 35,00; telefone R$ 55,00; alimentação R..."
  [5] Série CVM Comportamental, vol. 2: Vieses do Poupador   score=0.022
      "Em Economia, esse desconto no valor é tratado em termos puramente matemáticos (sem considerar a percepção individual de valor), simplesmente como uma porcentagem fixa e proporcional ao tempo de espera, representado por u..."

RESPOSTA (qwen2.5:14b, 9.1s, US$ 0.0000):
Sim, existe um limite legal para os descontos em folha de pagamento, incluindo benefícios previdenciários. De acordo com a jurisprudência, o percentual máximo de desconto deve ser de 30% sobre os vencimentos brutos do servidor ou beneficiário, para evitar que o superendividamento comprometa a subsistência e a dignidade da pessoa humana [2][3]. Se os descontos estão acima desse limite, você pode buscar a proteção do Judiciário para que os valores sejam ajustados.

FONTES:
  [2] Prevenção e Tratamento do Superendividamento 
      https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/escola-nacional-endc/biblioteca/manuais/prevencao-e-tratamento-do-superendividamento.pdf
      trecho: "Caracterização do Caso: Tadeu recorreu ao Projeto de Tratamento do Superendividamento na expectativa de celebrar com os credores acordo que viabilizasse o pagamento de suas dívidas sem comprometer o sustento da família. ..."
  [3] Prevenção e Tratamento do Superendividamento 
      https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/escola-nacional-endc/biblioteca/manuais/prevencao-e-tratamento-do-superendividamento.pdf
      trecho: "Agravo de Instrumento conhecido e parcialmente provido.” (Terceira Turma Cível do TJDF,Agravo de Instrumento Nº 2006 00 2 012026-6 , Agravante Bradesco ,Agravado Assistência Judiciária do Distrito Federal e Ministério Pú..."
```

A melhor nota do reranker foi 0,307: os chunks são de um manual de superendividamento e nenhum trata do limite de desconto de consignado. A resposta afirma um teto de 30% "de acordo com a jurisprudência", mas não confirmei esse número nos trechos exibidos; deve ser tratada como **não sustentada**. O corpus atual não traz a norma específica do consignado, e o portão (que só barra notas muito baixas) deixou passar.

### Apostas: leitura errada de um artigo

```text
PERGUNTA: Sou jovem e gasto quase todo o meu salário em apostas online. Alguma lei me protege ou limita isso?

CHUNKS RECUPERADOS:
  [1] Estudo Especial BCB 119/2024: mercado de apostas online   score=0.078
      "Idade ≤ 20 anos Pessoas Média de gasto Esses números se originam de um primeiro levantamento feito pelo BCB, com base em estimativas de valores apostados em agosto de 2024 a partir de transações via Pix. Para identificar..."
  [2] Estudo Especial BCB 119/2024: mercado de apostas online   score=0.061
      "Ainda em relação ao perfil dos apostadores, estima-se que, em agosto de 2024, 5 milhões de pessoas pertencentes a famílias beneficiárias do Bolsa Família (PBF) enviaram R$ 3 bilhões às empresas de aposta utilizando a pla..."
  [3] Estudo Especial BCB 119/2024: mercado de apostas online   score=0.042
      "Transferências Retenção Os valores mensais variaram entre R$ 18 bilhões e R$ 21 bilhões. Vale ressaltar que esses valores representam as transferências brutas; ou seja, são uma estimativa do quanto foi apostado no mês. C..."
  [4] Lei 14.790/2023 (Apostas de quota fixa) Art. 21-A  score=0.042
      "Art. 21-A. Constatada, pela autoridade reguladora ou supervisora competente, a exploração de loteria de apostas de quota fixa por pessoa natural ou jurídica não autorizada, as instituições financeiras, as instituições de..."
  [5] Lei 14.790/2023 (Apostas de quota fixa) Art. 1  score=0.039
      "Art. 1º [...] [...] § 7º O ato de autorização poderá impor limitação, por número de inscrição no Cadastro de Pessoas Físicas (CPF), da participação de consumidores em cada um dos sorteios, vales-brindes, concursos ou ope..."

RESPOSTA (qwen2.5:14b, 9.8s, US$ 0.0000):
Sim, há leis que podem limitar sua capacidade de fazer apostas online. A Lei 14.790/2023 permite que o ato de autorização imponha limitações por CPF na participação em sorteios ou operações semelhantes. Isso significa que as empresas de apostas podem ser obrigadas a limitar o quanto você pode apostar. Além disso, o Banco Central do Brasil pode bloquear contas de pessoas que realizam transações suspeitas relacionadas a apostas, como é o caso de quem gasta quase todo o salário nessa atividade [1][4]. É importante buscar ajuda financeira para controlar esse gasto e evitar problemas futuros.

FONTES:
  [1] Estudo Especial BCB 119/2024: mercado de apostas online 
      https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf
      trecho: "Idade ≤ 20 anos Pessoas Média de gasto Esses números se originam de um primeiro levantamento feito pelo BCB, com base em estimativas de valores apostados em agosto de 2024 a partir de transações via Pix. Para identificar..."
  [4] Lei 14.790/2023 (Apostas de quota fixa) Art. 21-A
      https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm
      trecho: "Art. 21-A. Constatada, pela autoridade reguladora ou supervisora competente, a exploração de loteria de apostas de quota fixa por pessoa natural ou jurídica não autorizada, as instituições financeiras, as instituições de..."
```

Os chunks recuperados são relevantes (Lei 14.790 e Estudo BCB 119), mas a resposta aplica o Art. 21-A, que trata de operadoras **não autorizadas**, ao apostador, e atribui ao Banco Central um bloqueio de contas que o trecho não descreve. Falha de fundamentação do LLM sobre fontes certas.

Esses casos explicam os números da próxima seção: a abstenção e a citação ainda ficam abaixo das metas.
