# ADR-0003 · Seleção de LLM (híbrido local + nuvem)

**Status:** **Proposto, em aberto** · **Data:** 2026-10-27 · **Decisão prevista:** fim da Semana 3

## Contexto
Os agentes precisam de bom raciocínio, uso de ferramentas e português fluente. Os dados são financeiros e sensíveis. O grupo quer decidir **com base em custo de implementação, facilidade de deploy e qualidade nas features reais**, e não por preferência prévia.

## Direção já definida
- Arquitetura **híbrida**: um modelo **local quantizado** (llama.cpp/Ollama) para tarefas sensíveis e baratas (mascaramento de PII, classificação, extração) e um **modelo mais capaz** para raciocínio e conversa.
- Acesso sempre via **LLM Gateway** (`LLMPort`), para que trocar o modelo não exija reescrever os agentes.

## Em aberto
Qual provedor/modelo ocupa cada papel. A escolha **não** está fixada em nenhum fornecedor.

## Candidatos
| Papel | Candidatos |
|---|---|
| Raciocínio / orquestração | Claude (Sonnet 5.5), GPT, Gemini, modelos abertos grandes via endpoint gerenciado |
| Classificação / extração barata | Claude Haiku 5.5, modelos "mini/flash", modelos abertos pequenos |
| Local (PII, classificação) | Qwen / Llama / Gemma quantizados (GGUF, Q4–Q8) |
| Embeddings | modelos multilíngues abertos × APIs de embedding |
| Visão / OCR | LLM multimodal × OCR dedicado |
| Voz | Whisper (local/API) × STT gerenciado |

## Matriz de decisão
Cada candidato roda **a mesma suíte de avaliação** ([06](../06-riscos-e-metricas.md)) nas features reais.

| Critério | Peso | Como medir |
|---|---|---|
| Qualidade nas tarefas do PANDORA | 35% | Ragas, sucesso de tarefa, acurácia de roteamento, tool calling |
| Custo | 25% | R$ por conversa típica (telemetria do gateway) |
| Facilidade de deploy/operação | 15% | Infra necessária, SDK, limites, tempo de integração |
| Privacidade / transferência de dados | 15% | Onde roda, política de retenção, suporte a PII mascarada |
| Latência | 10% | p95 por resposta |

## Consequências
- Até a decisão, o desenvolvimento usa o gateway com um modelo provisório.
- A decisão final será registrada aqui com os números medidos.
