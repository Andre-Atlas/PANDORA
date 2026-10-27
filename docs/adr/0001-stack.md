# ADR-0001 · Stack base

**Status:** Aceito · **Data:** 2026-10-27

## Contexto
O PANDORA combina ML clássico, RAG, orquestração multiagente e um app web usado no celular. O grupo tem 3–5 pessoas e 7 semanas. O squad de agentes de desenvolvimento já tem skills para Postgres, Redis, React/Next e arquitetura hexagonal.

## Decisão
- **Back-end:** Python + FastAPI + Pydantic, em arquitetura hexagonal.
- **Orquestração de agentes:** LangGraph (estado explícito, grafos com ciclos, checkpoints).
- **Front-end:** Next.js como PWA (instalável, com voz e câmera pelo navegador).
- **Dados:** Postgres + pgvector (relacional e vetorial no mesmo banco), Redis para cache e filas.
- **Infra:** Docker / docker-compose; deploy em container na nuvem.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Full TypeScript (Node + LangGraph.js/Mastra) | Ecossistema de ML/avaliação (scikit-learn, Ragas, Prophet) é mais maduro em Python |
| Python + Streamlit | Prototipa rápido, mas a UX fica limitada para um app de uso diário no celular |
| App nativo (React Native) | Custo alto para 7 semanas; o PWA cobre voz, câmera e notificações |
| Banco vetorial dedicado (Qdrant, Pinecone) | Mais um serviço para operar; pgvector basta no volume do projeto |

## Consequências
- Duas linguagens (Python e TS), com contrato OpenAPI entre elas gerando tipos no front.
- O agente `designer_back_end` foi adaptado de Prisma para FastAPI/Python.
