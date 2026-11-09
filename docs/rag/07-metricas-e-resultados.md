# Métricas e resultados

## Métricas

| Grupo | Métrica | Meta do escopo | Situação |
|---|---|---|---|
| Recuperação | Recall@k, Precision@k, Hit@k, MRR, nDCG@10, acerto do artigo no top-3 | — (usadas para otimizar) | medidas |
| Resposta | Citação válida (marcador + norma + link) | 100% nas normativas | medida |
| Resposta | Abstenção correta / recusa indevida | ≥ 90% correta | medida, com amostra pequena |
| Resposta | Acerto de número (fração dos números da referência presentes) | — | medida |
| Referência | ROUGE-1/2/L, BLEU (`sacrebleu`, PT) | diagnóstico | medidas, não decidem aprovação |
| Operação | Latência média e p95 | p95 ≤ 8 s | medida |
| Fundamentação | Ragas: Faithfulness ≥ 0,90, Answer Relevancy ≥ 0,85, Context Precision ≥ 0,80 | — | **não medida**: exige juiz forte, e a API está fora |
| Fundamentação | Rubrica 0/1/2 do LLM × RAG, às cegas | ganho ≥ 25 p.p. | **não medida** |

Todo número sai com IC bootstrap de 95%. Comparações pareadas usam bootstrap pareado e McNemar exato.

## Dev: recuperação (46 perguntas respondíveis)

Melhor configuração: bge-m3, chunking estrutural com cabeçalho, híbrido, reranker bge-reranker-v2-m3.

| Métrica | Valor |
|---|---|
| Hit@1 | 0,57 |
| Hit@5 | 0,85 |
| Hit@10 | 0,89 |
| MRR | 0,67 |
| nDCG@10 | 0,72 |
| Acerto do artigo no top-3 | 0,80 |

Ablação completa: [08-treinamento](08-treinamento.md).

## Teste (golden.v1, 169 perguntas, rodada 1 de 3)

Configuração final: qwen2.5:14b, top-3, resposta de até 350 tokens, portão de abstenção com limiar 0,02. Recuperação: bge-m3 + bge-reranker.

| Métrica | Valor | Meta |
|---|---|---|
| Citação válida | 96,0% | 100% |
| Recusa indevida | 3,4% | — |
| Abstenção correta (20 fora de domínio) | 70% | ≥ 90% |
| Acerto de número | 0,60 | — |
| ROUGE-L | 0,29 | diagnóstico |
| BLEU | 10,4 | diagnóstico |
| Latência média | 7,5 s | — |
| Latência p95 | 14,4 s | ≤ 8 s |

**Leitura honesta.**
- Citação e abstenção ficam abaixo da meta. Na normativa, 4% das respostas não trazem fonte válida.
- O acerto de número caiu de 0,88 (dev) para 0,60 (teste). É a principal diferença entre os dois conjuntos e precisa ser investigada no segundo refinamento. Como o golden não foi revisado por humanos, parte dessa queda pode ser referência ruim e não resposta ruim.
- A latência média cumpre, mas o p95 não.
- Os números do teste não guiaram nenhuma escolha.

Registro completo das rodadas: [evals/test_log.md](../../evals/test_log.md).
