# Ledger: Documentação da Arquitetura Geral do PANDORA

- **Classificação:** `ATLAS · feature · arquitetura+documentação · standard → pesquisa, descoberta, plano, G1, SDD, revisão, verificação, G2 · lanes: arquitetura`
- **Data:** 2026-11-19
- **Branch / Worktree:** `analise_arquitetura_geral` (`/Users/andreatlas/.gemini/antigravity/worktrees/PANDORA/analise_arquitetura_geral`)

## Rulings e Decisões

- `Ruling: Documentar toda a arquitetura unificada do monorepo (incluindo subsistemas presentes em origin/develop, entrega/prototipo-multiagente-quarto-desafio e origin/dev/mariana) usando links Markdown ativos para arquivos na branch atual e referências em código com indicação de branch para arquivos de outras branches — garante visão 100% completa do sistema sem gerar links 404 na worktree atual — custo baixo (apenas converter referências inline em links quando as branches forem mescladas).`
- `Ruling: Formalizar no ADR-0003 e na Matriz RNF08 que o cache do MVP substitui um container Redis dedicado por pré-geração estática triada (trilha.v1.json via TrilhaEmArquivo), cache em disco de embeddings bge-m3 e constantes locais das séries SGS/BCB — evita complexidade operacional extra no ciclo acadêmico de 7 semanas atendendo à redução >= 30% de chamadas repetidas — custo baixo (plugar adaptador Redis futuro caso a API escale para múltiplas réplicas).`
- `Ruling: Reportar na Seção 5.2 e na Matriz RNF01–RNF09 tanto as metas do escopo quanto os valores reais medidos em evals/runs/ (Hit@5 de 0,76 para 0,80 com cabeçalho, MRR 0,67 e nDCG@10 0,72 no dev; 96,0% de citação, 70% de abstenção e p95 = 14,4 s no golden.v1) — preserva o rigor científico e auditável da documentação e evita falsa garantia sobre o baseline rag-v0.1.0 — custo zero.`
