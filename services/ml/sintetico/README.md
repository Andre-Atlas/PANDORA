# Gerador de dados sintéticos do PANDORA (#51)

Gera transações bancárias **fictícias** das 10 personas, com série mensal reconciliada, rótulos para os três modelos de `docs/ml/modelos-auxiliares.md` (classificador RF02, detector de apostas RF04, detector de anomalias RF11) e a série que o previsor de fluxo de caixa (RF13) precisa.

> **Aviso (LGPD).** Todos os dados são sintéticos (`sintetico = True` em toda linha). Não representam pessoas reais, e nenhum CPF, e-mail, telefone ou endereço real é usado. As marcas de apostas são fictícias. Os CNPJs têm formato e dígitos verificadores válidos sobre base aleatória, mas **não são consultados em nenhuma base**: a ausência de colisão com CNPJs reais não pode ser verificada offline. Mitigação: a filial fica entre 8000 e 9999, faixa praticamente inexistente no cadastro real.

## Como rodar

```bash
pip install -r requirements.txt
python gerar_dataset.py --piloto      # 5 personas, 6 meses (validar antes de escalar)
python gerar_dataset.py               # 10 personas, 12 meses
pytest -q                             # 8 testes
```

`SEED = 42` fica em `catalogo.py`. Todo sorteio deriva de `SeedSequence([SEED, crc32(persona), crc32(etapa)])`, então o resultado é idêntico a cada execução e não muda quando uma persona é adicionada ou removida. Código de saída ≠ 0 se a reconciliação, o PII ou o split falharem.

## Arquivos

| Arquivo | Função |
|---|---|
| `catalogo.py` | Premissas: personas, comerciantes fictícios, taxas, regras de essencialidade. |
| `gerar_dataset.py` | `gerar_personas`, `gerar_transacoes`, `rotular`, `dividir`, `exportar`, `validar`. |
| `test_gerador.py` | CNPJ, determinismo, reconciliação, negativos difíceis, essencialidade, PII. |
| `saida/transacoes.csv` | Dataset principal (colunas abaixo). Ignorado pelo Git. |
| `saida/rotulos_verdadeiros.csv` | Rótulos limpos, cenário gerador, subtipo e quais linhas tiveram ruído. **Só para avaliação.** |
| `saida/serie_mensal.csv` | Saldo inicial, créditos, débitos e saldo final por persona e mês. |
| `saida/regras_essencialidade.csv` | As regras que produziram `is_essential` (auditoria do RF02). |
| `saida/lista_spa_sintetica.csv` | Lista fictícia de operadoras autorizadas. Substituir pela lista real da #59. |
| `saida/split.json` | Treino, validação, teste, holdout e corte temporal. |
| `saida/personas.csv`, `metadata.json` | Atributos das personas e parâmetros da execução. |

## Classes (12) e por que há dois grupos

| Grupo | Classes |
|---|---|
| **Consumo** (alvo do F1 macro) | `MORADIA`, `UTILIDADES`, `ALIMENTACAO`, `SAUDE`, `TRANSPORTE`, `EDUCACAO`, `LAZER`, `COMPRAS_IMPULSO`, `INSUMO_MEI` |
| **Contexto** (existem, fora do F1 macro) | `RENDA`, `DIVIDA_JUROS`, `INVESTIMENTO`, `TRANSFERENCIA`, `APOSTAS_BETS`, `FRAUDE_SUSPEITA` |

O escopo (`06`) exige F1 macro ≥ 0,85. `RENDA` e `INVESTIMENTO` têm poucos eventos por persona (`INVESTIMENTO` só existe na `julia_31`), e misturá-las no F1 macro tornaria a meta matematicamente impossível. Separá-las torna o contrato auditável. `INSUMO_MEI` é classe própria (RF02 e #58), não subcategoria de `COMPRAS_IMPULSO`: a `mariana_28` é MEI e a distinção é o que o RF02 quer ensinar. Por isso `software_trabalho` (INSUMO_MEI) e `software_pessoal` (LAZER) compartilham o MCC 5734 e parte dos nomes de loja.

## Mecanismo de rótulo: cenário latente

`is_fraud`, `is_bet` e `anomaly_score` **não** são regras sobre as features. O gerador sorteia primeiro o evento (falsa central, boleto falso, sessão de aposta, viagem legítima…), e o rótulo é a causa.

- **Fraude e aposta:** vêm do cenário. Aposta via intermediador sem MCC 7995 continua sendo aposta. Uma lotérica com MCC 7995 continua sendo conta de luz.
- **`anomaly_score`:** é uma Beta por grupo de cenário, com efeito aleatório por persona e ruído em logit. É um **rótulo suave de risco** (fraude, aposta, compra noturna por impulso, rolagem de dívida), **não** a saída do Isolation Forest. O modelo calibra o score dele sobre o percentil dos normais (`ml/` §4).
- **Negativos difíceis** (cenários `hn_*`): lotérica que paga conta, loja de games, nomes com "BET" (BETANIA, BETEL), viagem de valor alto, Pix alto para prestador novo, Pix para contato novo.
- **Ruído de rótulo:** 8% dos positivos viram 0 e 8% dos negativos difíceis viram 1, **só nas colunas observadas** (`is_fraud`, `is_bet`). A verdade limpa fica em `rotulos_verdadeiros.csv`. **Treine com o observado, avalie contra o verdadeiro.**
- **Auditoria de circularidade** (`validar`, seção 7): AUC de cada feature isolada contra a fraude verdadeira, e recall e precision da regra "MCC == 7995" contra a aposta verdadeira.

## Essencialidade por transação

`is_essential` não vem de lista de categorias. As regras (primeira que casa vence) usam arquétipo da persona, categoria, subtipo, recorrência, faixa de horário, valor máximo e finalidade de trabalho. A regra aplicada fica em `regra_essencialidade_id`. Exemplos: combustível do entregador é essencial e app de transporte da Carla não; app de transporte às 22h–05h é essencial para a cuidadora em plantão; utensílio doméstico até R$ 150 é essencial, acima disso não.

## Série reconciliada

12 meses contínuos (nov/2025 a out/2026), mais 3 meses de aquecimento descartados, para que parcelas e faturas já estejam em curso no primeiro mês. Os saldos são em **centavos inteiros**:

```
saldo_inicial + total_credito - total_debito == saldo_final        (por persona e mês)
saldo_final(N) == saldo_inicial(N+1)
saldo_pos_transacao == saldo_inicial + soma acumulada
```

`saldo_pos_transacao` é o saldo **consolidado do caixa** da persona (as 4 contas da Mariana e a conta da mãe da Patrícia somam). Compra no cartão de crédito tem `afeta_caixa = False`: entra na fatura e sai do caixa no pagamento do dia 10 do mês seguinte. Pagamento integral é `TRANSFERENCIA`; pagamento mínimo é `DIVIDA_JUROS`; os encargos do rotativo são linhas do cartão. Parcelamentos geram uma linha por mês (`PARC 03/10`).

## Colunas de `transacoes.csv`

| Coluna | Descrição |
|---|---|
| `transaction_id` | UUID v5 determinístico. |
| `persona_id`, `posted_at`, `amount` | Persona, data e hora ISO, valor em R$ (saída negativa). |
| `payment_method`, `description_masked`, `mcc` | Forma de pagamento, texto sem PII (com grafias sujas, como `PAG*BETX`) e MCC. |
| `category` | Uma das 12 classes. |
| `cartao_ou_conta_id` | Conta ou cartão usado (a `mariana_28` tem 4 bancos). |
| `destinatario_id`, `cnpj_destinatario`, `destinatario_novo` | Hash do destinatário; CNPJ sintético quando é empresa; primeira vez que a persona o usa (calculado com o histórico do aquecimento). |
| `num_parcelas`, `valor_parcela` | Parcelamento no cartão. |
| `saldo_pos_transacao`, `afeta_caixa` | Saldo consolidado do caixa após a linha; se a linha mexe no caixa. |
| `hora_repasse`, `min_desde_repasse` | Último crédito de renda principal e minutos desde ele (detector pós-repasse, ≤ 120). |
| `horario_madrugada` | `true` entre 23:00 e 02:59. |
| `grafia_suja_bet`, `operadora_bet_autorizada`, `premio_recebido_bet` | Auditoria de apostas. `operadora_bet_autorizada` é vazio para o que não é aposta ou usa intermediador. |
| `is_bet`, `is_fraud`, `anomaly_score` | Alvos observados (com ruído). |
| `is_essential`, `regra_essencialidade_id` | Mínimo Existencial por transação e a regra que o produziu. |
| `ground_truth_note` | Texto do comportamento representado. |
| `sintetico` | Sempre `true`. |

> **Não use como feature:** `category`, `is_bet`, `is_fraud`, `anomaly_score`, `is_essential`, `regra_essencialidade_id`, `ground_truth_note`, `grafia_suja_bet`, `operadora_bet_autorizada`, `premio_recebido_bet`, `persona_id`, `sintetico`. A lista está em `split.json` (`colunas_nao_usar_como_feature`).

## Split (`split.json`)

- **Por persona**, nunca por transação. `antonio_67` e `rosangela_43` são o **holdout de generalização**: ficam fora do treino e da validação.
- As outras 8 personas são divididas minimizando o desvio de 70/15/15 em linhas, com cobertura mínima (treino ≥ 30 fraudes e ≥ 150 apostas; validação e teste ≥ 5 de cada). Com 8 pessoas o 70/15/15 exato é impossível.
- **Temporal (previsor RF13):** os últimos 3 meses são teste. Atenção: nesses meses há mudança de regime em duas personas (rescisão da `fernanda_46` em out/2026, fim do acordo de dívida e início do aporte de R$ 500 da `julia_31` em ago/2026). Isso é deliberado, mas torna o teste do previsor não estacionário para elas.
- O Isolation Forest de linha de base por pessoa (`ml/` §4) precisa dos primeiros meses de cada pessoa, inclusive das do holdout. Os dois recortes (por pessoa e por tempo) respondem a perguntas diferentes.

## Premissas e suas origens

1. **Perfis, rendas, dívidas e padrões de comportamento:** as fichas em `docs/personas/` (valores como R$ 723,60 de consignado, R$ 1.198 de boleto falso, 12 × R$ 690 do cartão da Patrícia).
2. **Taxas:** rotativo de 435,9% a.a. (≈ 15,0% a.m.) do `README.md` do repo; cheque especial de 7,9% a.m. da ficha 07. O IOF do rotativo (0,4%) é aproximação **a validar** com a Calculadora do Cidadão.
3. **Escolaridade e score de crédito:** `escolaridade` (1–5) segue as fichas onde há informação e é **suposta** nas demais (por exemplo, `antonio_67` = 2). `score_credito` é uma premissa por persona, **não medida**. As correlações com risco são checagem de consistência, não evidência.
4. **IBGE 2022, BCB/SGS e Nemotron-Brazil:** estão citados como origem das premissas por requisito do projeto, mas **nenhum dado foi importado delas** nesta versão. Faixas de renda, escolaridade e taxas são ordens de grandeza das fichas e do repo, e devem ser conferidas contra essas fontes antes de qualquer afirmação sobre representatividade.
5. **Operadoras de apostas:** 8 marcas autorizadas e 4 não autorizadas fictícias. A lista real da SPA/MF (#59) substitui `lista_spa_sintetica.csv`.
6. **Volume:** as sugestões de N somam 11.400, abaixo do piso de 15.000, então aplica-se `FATOR_VOLUME = 1,4`. Mas N não cabe igualmente em todas as rendas: com ~2.100 linhas/ano a `rosangela_43` (R$ 1.560/mês) teria ticket médio de centavos. Por isso cada persona tem uma **capacidade** (orçamento variável ÷ `TICKET_MEDIO_MIN` = R$ 8), há um **piso de ticket** por subtipo e o excedente é **redistribuído** às personas com folga, proporcionalmente ao N sugerido. O relatório `[0]` mostra sugerido × gerado por persona.
7. **Estabilizadores:** para manter saldos plausíveis, o gasto variável reage ao saldo e, em déficit grave, a persona contrata empréstimo pessoal (24 × 2,8% a.m.), com teto de 2. A dívida do rotativo fica limitada a 1,25 × o limite do cartão (premissa inspirada na Lei 14.690/2023, não uma implementação dela).

## Limitações conhecidas

- Fraude é rara (≈ 0,6% das linhas, ≈ 100 positivos) e concentrada em `antonio_67`, `patricia_53` e `lucas_19`. Validação e teste têm poucos positivos de fraude e de aposta. Intervalos de confiança de recall serão largos.
- O detector de apostas por regras simples não chega a 0,95: 15% das apostas passam por intermediadores sem nome de operadora. Esse resíduo é do classificador de apoio (`ml/` §3, passo 4).
- Os volumes por persona **diferem da sugestão** (`mariana_28`, `rosangela_43` e `lucas_19` abaixo; as demais acima). O total passa de 15.000, mas o teste do previsor e a cobertura de `APOSTAS_BETS` ficam mais concentrados em `diego_24`.
- Várias personas têm saldo médio negativo (`carla_34`, `mariana_28`, `diego_24`, `patricia_53`, `rosangela_43`, `lucas_19`). É coerente com as fichas (cheque especial, rotativo), mas confira se o previsor deve tratar isso como cheque especial.
- O valor relativo à mediana da pessoa sozinho já tem AUC ≈ 0,95 contra a fraude, porque golpes são maiores que a compra típica. Isso não é circularidade (o rótulo vem do cenário), mas significa que o detector de anomalias terá um sinal forte nessa feature.
- A amostra de 42 linhas em `docs/evidencias/datasets/` não é substituída por este gerador.
