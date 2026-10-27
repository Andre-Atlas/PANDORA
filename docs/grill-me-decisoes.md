# Registro de decisões · sessão grill-me

O planejamento seguiu o método **grill-me**: percorrer a árvore de decisões do projeto ramo a ramo, resolvendo dependências uma de cada vez. Cada pergunta veio com uma resposta recomendada, e o time aceitou, ajustou ou recusou cada recomendação.

**Data:** 2026-10-27 · **Entrada:** deck *Challenge 2 · CBL* + briefing do tema Finanças / projeto PANDORA.

## Briefing inicial

- **Objetivo:** ajudar pessoas em situação de dívidas e vícios financeiros com reestruturação, guia de investimentos, planejamento e medidas protetivas de ativos.
- **Funções base:** conexão com sistemas bancários para extrair os dados financeiros do usuário; LLM, RAG e modelos de ML para orquestrar tarefas; sistema multiagente e agentes multimodais.

## Rodada 1: escopo e fundações

| Pergunta | Recomendação | Decisão |
|---|---|---|
| Qual o núcleo da Essential Question? | Endividamento + vício | ✅ **Endividamento + vício**; planejamento, investimento e proteção são a "saída" da jornada |
| Como obter dados bancários? | Agregador sandbox + upload | ✅ **Agregador (Pluggy/Belvo) sandbox + upload OFX/CSV/PDF + imagem** → [ADR-0002](adr/0002-dados-bancarios-sandbox.md) |
| Provedor de LLM e privacidade? | Claude API + PII masking | ✏️ **Híbrido local + nuvem**, mas **provedor em aberto** até a análise de custo de implementação, facilidade de deploy e qualidade do modelo → [ADR-0003](adr/0003-selecao-llm.md) |
| Formato do documento? | README + docs/ estruturado | ✅ **README + docs/ + ADRs + AGENTS.md + .agents/** |

## Rodada 2: limites e arquitetura

| Pergunta | Recomendação | Decisão |
|---|---|---|
| Até onde vai o guia de investimentos? | Educacional + perfil | ✅ **Educacional + perfil**, sem recomendação de produto → [ADR-0004](adr/0004-investimento-educacional.md) |
| O que são "medidas protetivas de ativos"? | (múltipla escolha) | ✅ **Todas:** antifraude e golpes · autoexclusão e travas · reserva, seguros e impenhorabilidade · superendividamento legal (Lei 14.181) |
| Stack base? | Python API + Next.js | ✅ **FastAPI + LangGraph + Next.js PWA + Postgres/pgvector + Redis** → [ADR-0001](adr/0001-stack.md) |
| Time e deploy? | Grupo 3–5, deploy cloud | ✅ **Grupo de 3–5 pessoas, deploy em container na nuvem com dados sandbox** |

## Rodada 3: canal, squad e publicação

| Pergunta | Recomendação | Decisão |
|---|---|---|
| Canal principal do usuário? | Web app PWA + voz | ✅ **PWA com chat, dashboard, upload multimodal e voz** |
| Como adaptar o sistema Agents & Skills? | Squad + agentes de domínio | ✅ **7 agentes do squad + `engenheiro_ml_rag` + `compliance_financeiro_lgpd`**, versionando só as skills usadas |
| Como publicar no repositório? | Commit inicial na main | ✅ **Commit inicial direto na `main`** |

## Ajustes feitos ao adaptar o squad

- `designer_back_end`: skills de Prisma trocadas por `fastapi-patterns`, `python-patterns` e `database-migrations` (back-end em Python).
- `designer_front_end`: skills de 3D/animação (`img2threejs`, `hyperframes-animation`) trocadas por `dashboard-builder` e `nextjs-turbopack`; foco em dashboards financeiros legíveis e PWA.
- `tester_back`: adicionada `python-testing`. `auditor`: adicionada `docker-patterns`.
- Novas regras invioláveis: privacidade por padrão, sem conselho regulado, evidência antes de opinião.

## Pontos ainda em aberto

1. Provedor e modelos de LLM ([ADR-0003](adr/0003-selecao-llm.md)), com decisão prevista para a Semana 3.
2. Agregador definitivo (Pluggy × Belvo), conforme as condições de sandbox/trial disponíveis.
3. Provedor de nuvem para o deploy.
4. Possibilidade de validação do tom e do fluxo de crise com um profissional de saúde mental.
5. Conferência das estatísticas marcadas com 🔎 em [01](01-problema-e-essential-question.md).
