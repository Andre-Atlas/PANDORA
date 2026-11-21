# 7. Qualidade da recuperação e da fundamentação

O desafio pede foco em recuperação, fundamentação e rastreabilidade. Esta seção resume o que foi medido, com as metas ainda não atingidas expostas. O detalhe está em `docs/rag/07-metricas-e-resultados.md` (anexos) e em `evals/test_log.md`.

## Como foi avaliado

- **Golden set**: 169 perguntas de teste (100 normativas, 49 de persona, 20 fora de domínio), cada uma com trecho-ouro copiado literalmente da fonte; 51 perguntas de desenvolvimento (separadas, usadas para ajustar); 478 perguntas sintéticas de treino. Tudo separado por chunk de origem.
- **Validação**: automática (trecho literal, números conferidos contra o trecho, perguntas sem cópia do texto). **A revisão humana do golden ainda não foi feita**, e está planejada para a próxima etapa.
- **Teste**: no máximo 3 rodadas; esta é a rodada 1. Nenhuma escolha de configuração usou o teste.

## Recuperação (desenvolvimento, 46 perguntas respondíveis)

Bge-m3 + chunking estrutural com cabeçalho + busca híbrida + reranker:

| Métrica | Valor |
|---|---|
| Hit@1 | 0,57 |
| Hit@5 | 0,85 |
| Hit@10 | 0,89 |
| MRR | 0,67 |
| nDCG@10 | 0,72 |
| Artigo certo no top-3 | 0,80 |

## Respostas (teste, 169 perguntas, qwen2.5:14b com portão de abstenção)

| Métrica | Valor | Meta do escopo |
|---|---|---|
| Citação válida (normativas) | 96,0% | 100% |
| Abstenção correta (20 fora de domínio) | 70% | ≥ 90% |
| Recusa indevida | 3,4% | n/a |
| Acerto de número | 0,70 (0,60 antes de corrigir a métrica) | n/a |
| ROUGE-L / BLEU | 0,29 / 10,4 | diagnóstico |
| Latência média / p95 | 7,5 s / 14,4 s | p95 ≤ 8 s |

O acerto de número subiu de 0,60 para 0,70 porque `600,00` e `600` eram contados como diferentes. A correção foi feita depois de ver o teste; é um defeito do normalizador (com teste unitário), e o valor original está preservado no registro da execução.

## O que não foi atingido ou não foi medido

- **Metas abaixo do escopo**: citação (96% contra 100%), abstenção (70% contra ≥ 90%) e p95 de latência (14,4 s contra ≤ 8 s). Os exemplos 6.4 mostram como isso aparece na prática.
- **Não medido**: Ragas (Faithfulness, Answer Relevancy, Context Precision) e a rubrica LLM × RAG, porque ambos exigem um juiz forte e a API externa ficou fora do escopo desta etapa.
- **BLEU e ROUGE** entram só como diagnóstico, porque medem sobreposição de palavras e não decidem se a resposta está certa.
- **Amostras pequenas**: com 8 perguntas com número no dev e 10 no teste, uma pergunta muda o resultado em 10 a 12 p.p.

## Próximos passos

Revisão humana do golden, medição de fundamentação com juiz, ampliação do corpus (por exemplo, normas de consignado) e rodadas 2 e 3 do teste.
