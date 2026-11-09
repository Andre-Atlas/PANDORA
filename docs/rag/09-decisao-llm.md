# Decisão do LLM (#53)

**Regra do plano:** primeiro passar nas metas de citação, abstenção e Faithfulness; entre os que passam, o menor custo com p95 ≤ 8 s; depois, o menor esforço de deploy.

**Resultado:** nenhum candidato passa todas as metas. A escolha da versão base é provisória.

## Dev (51 perguntas, recuperação fixa)

| Modelo | Citação | Recusa indevida | Abstenção correta | Acerto de número | ROUGE-L | Latência média / p95 |
|---|---|---|---|---|---|---|
| qwen2.5:14b, top-5 | 100% | 0% | 40% | 0,88 | 0,30 | 8,6 s / 13,8 s |
| gemma3:12b, top-5 | 100% | 0% | 80% | 0,83 | 0,18 | 11,0 s / 15,1 s |
| llama3.1:8b, top-5 | 87% | 2% | 100% | 0,79 | 0,26 | 5,3 s / 9,6 s |
| **qwen2.5:14b, top-3, portão** | 98% | 0% | 80% | 0,88 | 0,32 | 7,0 s / 12,5 s |

O portão de abstenção (ver [08](08-treinamento.md)) e o top-3 melhoraram o qwen sem perder citação de forma relevante.

## Teste (golden.v1, 169 perguntas, rodada 1 de 3)

Só o qwen2.5:14b com top-3 e portão foi rodado no teste.

| Métrica | Valor | Meta | Passa? |
|---|---|---|---|
| Citação válida | 96% | 100% | não |
| Abstenção correta | 70% | ≥ 90% | não |
| p95 | 14,4 s | ≤ 8 s | não |

## Candidatos não avaliados

- **Claude Haiku 5.5 e Sonnet 5.5:** dependem de chave de API, que não será usada nesta versão. Ficam para o refinamento, se o orçamento e a decisão permitirem.
- **Qwen3 14B:** não baixado.

## Limitações

- Faithfulness (Ragas) e a rubrica LLM × RAG não foram medidas.
- Abstenção tem poucos exemplos no dev (5) e no teste (20 no golden, não revisados).
- Sem revisão humana, o acerto de número no teste (0,60) pode refletir referência ruim.

## Próximos passos

1. Revisão humana do golden (170) e do dev (15 de cada).
2. Diagnóstico da queda de acerto de número entre dev e teste.
3. Abstenção: mais exemplos fora de domínio e, se preciso, um classificador treinado.
4. Latência: p95 acima de 8 s. Testar um modelo menor ou resposta mais curta.
