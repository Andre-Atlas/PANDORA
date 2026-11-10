# Treinamento e otimização

Cada estágio foi escolhido no dev, sem ver o teste.

## Estágios 0 a 4: recuperação (dev, 46 perguntas)

| Estágio | Configuração | Hit@5 | nDCG@10 |
|---|---|---|---|
| 0 | baseline: chunk fixo, MiniLM, só vetor | 0,15 | 0,09 |
| 1 | chunk fixo, bge-m3 híbrido | 0,67 | 0,58 |
| 1 | estrutural, sem cabeçalho | 0,76 | 0,62 |
| 1 | **estrutural, com cabeçalho** | **0,80** | **0,69** |
| 2 | e5-large | 0,76 | 0,66 |
| 2 | Legal-BERTimbau | 0,59 | 0,49 |
| 2 | Qwen3-Embedding-4B | 0,74 | 0,67 |
| 3 | BM25 puro | 0,65 | 0,58 |
| 3 | fusão com pesos 2:1 | 0,78 | 0,71 |
| 3 | `k1` ou `b` diferentes, `rrf_k=30` | 0,78 a 0,80 | 0,66 a 0,70 |
| 4 | **+ bge-reranker-v2-m3** | **0,85** | **0,72** |
| 4 | + Qwen3-Reranker-4B | não concluído | latência média 33 s, inviável |

Os ajustes de peso, `k1`, `b` e `rrf_k` ficam dentro do ruído, e por isso não foram usados. Com 46 perguntas, uma pergunta vale ~2 p.p.

## Ajuste fino do embedding

Bge-m3 ajustado com 410 pares (pergunta, chunk certo, negativo difícil escolhido entre o 2º e o 30º do próprio modelo, com filtro para não usar chunk que cubra o trecho-ouro). Perda: MultipleNegativesRankingLoss. 1 época, lote 4, lr 1e-5, camada de embeddings congelada (a primeira tentativa, com lote 8, estourou a memória do MPS).

| | Base | Ajustado |
|---|---|---|
| Hit@5 | 0,80 | 0,76 |
| MRR | 0,64 | 0,67 |
| nDCG@10 | 0,69 | 0,71 |
| Artigo no top-3 | 0,83 | 0,80 |

Melhora em MRR e nDCG, piora em Hit@5, dentro do ruído. **Não adotado.** Não foi avaliado no hold-out.

## Abstenção (estágio 6)

Sinal: nota do reranker do melhor chunk. Limiar escolhido no dev: **0,02**, o maior sem recusa indevida (0 de 46). Pega 2 de 5 fora de domínio. As outras 3 têm nota alta (0,33, 0,90, 0,98) e ficam para o LLM. O limiar está em `training/abstencao/limiar.json`.

## LLM (estágios 7 a 9)

- Estágio 7 (escolha): [09-decisao-llm](09-decisao-llm.md).
- Estágio 8 (otimização de prompt com DSPy): **não feito**.
- Estágio 9 (LoRA com MLX): **não feito**. É o primeiro corte previsto, por prazo.
