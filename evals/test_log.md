# Registro das rodadas no conjunto de teste (golden.v1)

O teste tem no máximo 3 rodadas: baseline, pós-treino e final. Cada rodada é registrada aqui antes de ser usada.

| # | Data | Execução | Configuração | Citação | Abstenção | Acerto de número | p95 | Observação |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-09 | `evals/runs/2026-11-09-llm-qwen25-14b-k3-portao-golden-teste` | qwen2.5:14b, top-3, portão 0,02, 350 tokens | 96,0% | 70% | 0,60 | 14,4 s | versão base; golden validado só automaticamente |

**Nota sobre a rodada 1 (2026-11-09).** Depois da rodada, o acerto de número foi investigado. Um defeito do normalizador (`600,00` ≠ `600`) foi corrigido com teste unitário. Valor corrigido do acerto de número: 0,70 (original: 0,60), registrado em `metrica_numero_corrigida.json`. As demais métricas não mudam, porque o normalizador só afeta números. Nenhum item foi reavaliado com o LLM.

**Rodadas restantes:** 2 (após a revisão humana do golden) e 3 (final).
