# ADR-0004 · Investimento apenas educacional + perfil

**Status:** Aceito · **Data:** 2026-10-27

## Contexto
Recomendar produtos ou carteiras de forma personalizada é atividade regulada pela CVM (consultoria de valores mobiliários, Resolução CVM 19/2021; análise, Resolução CVM 20/2021). Além disso, o público-alvo do PANDORA está endividado: para ele, a prioridade costuma ser quitar dívidas caras e formar reserva, não investir.

## Decisão
- O módulo de investimento é **educacional**: perfil de investidor (inspirado em suitability, Resolução CVM 30/2021), trilha de conteúdo por RAG sobre fontes oficiais e simuladores genéricos.
- **Nunca** indica ativo, produto, emissor ou corretora específicos.
- O módulo só é destacado depois que o usuário sai da fase de crise (sem dívidas caras em atraso, com reserva inicial).
- O guardrail de saída do Compliance Guard bloqueia recomendações; testes adversariais cobrem esse caso.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Recomendação de carteira | Risco regulatório e de responsabilidade; desalinhado ao público |
| Remover investimento do produto | Perde a "saída" da jornada, que dá sentido à recuperação |

## Consequências
- Disclaimers em todo conteúdo de investimento.
- Futuro: parceria com instituição autorizada, se o produto evoluir.
