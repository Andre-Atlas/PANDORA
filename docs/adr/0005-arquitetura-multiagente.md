# ADR-0005 · Arquitetura multiagente supervisor + especialistas

**Status:** Aceito · **Data:** 2026-10-27

## Contexto
As conversas misturam domínios (dívida + aposta + golpe + direitos), com níveis de risco diferentes. O Challenge pede um sistema multiagente (Semana 4) e agentes multimodais (Semana 5).

## Decisão
- **Supervisor (Orquestrador)** com especialistas: Analista de Dados, Coach Comportamental, Estrategista de Dívidas, Planejador de Orçamento, Guardião, Educador e Agente Multimodal.
- **Compliance Guard transversal** na entrada e na saída.
- Implementação em **LangGraph**, com estado explícito e ferramentas tipadas; cálculos financeiros são ferramentas determinísticas.
- Nenhuma ferramenta movimenta dinheiro; ações com efeito exigem confirmação.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Agente único com muitas ferramentas | Prompt gigante, guardrails difusos, difícil de avaliar por domínio. Vai ser mantido como **baseline** de comparação |
| Agentes em rede (peer-to-peer) | Fluxo imprevisível e difícil de auditar em um domínio sensível |
| Pipeline fixo sem LLM no roteamento | Rígido demais para conversa livre |

## Consequências
- Mais chamadas de LLM por interação, mitigadas pelo roteamento do gateway e pelo modelo local.
- A avaliação mede tanto o roteamento quanto o sucesso ponta a ponta, comparando com o baseline de agente único.
