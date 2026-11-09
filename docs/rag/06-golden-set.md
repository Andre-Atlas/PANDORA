# Golden set, dev e treino

Três conjuntos, sempre separados por chunk de origem:

| Conjunto | Tamanho | Uso | Revisão |
|---|---|---|---|
| `golden.v1` | 169 (100 normativas, 49 de persona, 20 fora de domínio) | teste, no máximo 3 vezes | **pendente, validado automaticamente** |
| `dev.v1` | 51 (31 normativas, 15 de persona, 5 fora de domínio) | ajuste e escolha | automática |
| treino | 478 (410 treino + 68 hold-out) | ajuste fino e limiares | sem revisão, só automática |

**Como foram feitos.** O rascunho é gerado com `qwen2.5:14b` a partir de um chunk, com pergunta, resposta de referência e trecho-ouro. Cada item passa por checagens automáticas (`evals/golden/rascunhar.py`): o trecho-ouro precisa ser cópia literal do chunk, número da resposta precisa estar no trecho, pergunta com tamanho mínimo, e não pode ser cópia do trecho. Descartes: 53 no golden e 26 no dev, quase todos por trecho não literal.

**Fora de domínio.** 20 perguntas escritas à mão: premissas falsas, normas inexistentes, assuntos alheios, pedido de recomendação de ativo, promessa de resultado. Estão em `evals/golden/fora_de_dominio.py`.

**Persona.** 5 perguntas por persona das 10 de `docs/personas`, em primeira pessoa.

**Treino.** Uma pergunta por chunk fora do teste. Removidas as com similaridade ≥ 0,85 com qualquer pergunta de teste ou entre si (nenhuma restante acima de 0,85). 10% dos artigos viram hold-out e nunca entram no treino.

**Status.** Nenhum item foi revisado por humanos. A revisão das 170 perguntas do golden e de 15 do dev fica para o segundo refinamento. `evals/golden/golden.lock` guarda o SHA-256 de `golden.v1.jsonl` e `dev.v1.jsonl`.
