# LLM × RAG (semana 3)

**Decisão:** RAG + qwen2.5:14b (T3) continua como configuração do produto. O RAG sozinho (T2) vira o modo de contingência quando o LLM falha ou estoura o tempo. O qwen2.5:7b (T4) fica como plano B de latência.

## Testes

Mesmas 66 perguntas, corpus `515669eb8f54` (1.183 chunks, o mesmo da semana 2), mesma recuperação (bge-m3 + BM25 + RRF, bge-reranker-v2-m3, top-3, portão 0,02), Apple M4 24 GB, Ollama, temperatura 0.

| Teste | Execução | Como responde |
|---|---|---|
| T1 | `evals/runs/2026-11-12-s3-t1-llm-sozinho` | qwen2.5:14b sem fontes |
| T2 | `evals/runs/2026-11-12-s3-t2-rag-sozinho` | melhor trecho + fonte, sem LLM |
| T3 | `evals/runs/2026-11-12-s3-t3-rag-llm-14b` | RAG + qwen2.5:14b |
| T4 | `evals/runs/2026-11-12-s3-t4-rag-llm-7b` | RAG + qwen2.5:7b |

Conjunto: `dev.v1` (46 respondíveis + 5 fora de domínio) + `DEV_EXTRA` (15 fora de domínio novas, em `evals/golden/fora_de_dominio.py`). O golden não foi usado.

## Resultados

| Métrica | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Rubrica às cegas (0 a 1) | 0,11 | 0,41 | **0,96** | 0,86 |
| Citação válida | 0% | 100% | 100% | 96% |
| Recusa indevida | 28% | 0% | 0% | 4% |
| Abstenção correta (20) | 80% | 40% | 85% | 80% |
| Norma correta | 23% | 81% | 94% | 97% |
| Respostas com número sem suporte | 76% | 0% | 0% | 5% |
| Acerto de número | 0,07 | 0,79 | 0,88 | 0,71 |
| Latência média / p95 (ponta a ponta) | 13,1 / 27,7 s | 3,4 / 4,3 s | 30,8 / 56,2 s | 17,5 / 25,1 s |

Ganho na rubrica sobre o LLM sozinho: T3 +85 p.p. (IC 95% 76 a 92), T4 +75 p.p. T3 − T4: +10 p.p. (IC 1 a 18; McNemar nas notas máximas p = 0,11). Rubrica em `evals/runs/2026-11-12-s3-rubrica/` (folha, chave, notas, resultado).

## Mudanças nas métricas

- **Latência de ponta a ponta.** O `llm_run` só media o LLM; a busca custa 3,4 s por pergunta nesta máquina.
- **Números sem suporte** e **norma correta**, novas, valem também para o LLM sem fontes.
- **Abstenção com 20 exemplos** (antes 5).
- **Normalizador de números:** `50.000,00` e `50.000` agora são o mesmo valor (teste em `test_metricas.py`). Afeta o acerto de número de rodadas antigas só quando a referência tem milhar com centavos.
- **Rubrica 0/1/2 às cegas** (`evals/rubrica_cega.py`): avaliada por Claude, cego quanto ao rótulo. O estilo denuncia parte dos modos; falta revisão humana de uma amostra.

## Limitações

- Latência medida num M4 base (qwen2.5:14b a 8,4 tokens/s); compare os testes entre si, não com a semana 2.
- As referências do golden foram rascunhadas pelo qwen2.5:14b, o que favorece esse modelo no ROUGE.
- Acerto de número tem 5 a 8 perguntas por teste.
- Duas das três "falhas" de abstenção do T3 são negações corretas de promessa de resultado; a métrica conta só a mensagem padrão de recusa.

## Reproduzir

```bash
cd services/rag
uv sync --extra eval --extra dev
uv run pandora-rag coletar && uv run pandora-rag extrair
ollama pull qwen2.5:14b && ollama pull qwen2.5:7b
PYTHONPATH=../.. uv run python -m evals.llm_x_rag            # os 4 testes (~2 h num M4 base)
PYTHONPATH=../.. uv run python -m evals.rubrica_cega exportar  # folha às cegas
PYTHONPATH=../.. uv run python -m evals.rubrica_cega pontuar   # depois de preencher notas.csv
```
