# 05 · Riscos e Premissas do Projeto

[⬅️ Anterior: 04 · Requisitos (4 Graus)](04-requisitos-4-graus.md) · [Voltar ao índice](README.md) · [Próximo: 06 · Métricas e Validações ➡️](06-metricas-e-validacoes.md)

---

## 1. Matriz de Riscos e Estratégias de Mitigação

| ID | Risco Identificado | Prob. | Impacto | Estratégia de Mitigação no PANDORA | Requisitos Associados |
|---|---|---|---|---|---|
| **R01** | **Alucinação jurídica ou financeira** (informar taxa, prazo do MED ou regra da Lei 14.181 incorretos) | Alta | Muito Alto | Cálculos executados exclusivamente por ferramentas Python determinísticas; pipeline RAG híbrido (`pgvector` + BM25 + *rerank*) com exigência de citação e abstenção segura quando o score de contexto for baixo. | RF06, RF08, RNF03, RNF04 |
| **R02** | **Dano psicológico a usuário vulnerável** (gerar culpa, ansiedade ou gatilho em casos de compulsão/crise) | Média | Muito Alto | Prompts com diretrizes estritas de linguagem não estigmatizante; classificador de risco no `Compliance Guard` que interrompe o fluxo financeiro e aciona imediatamente `CVV 188`, CAPS AD e Jogadores Anônimos. | RF05, GQ09 |
| **R03** | **Enquadramento como consultoria de investimentos irregular (CVM)** | Média | Alto | Escopo do Módulo 6 restrito à educação financeira e simulação de classes gerais de ativos; filtro de saída no `Compliance Guard` que aplica a **Recusa Educativa** diante de pedidos de recomendação de ativos específicos. | RF08, RF14, RNF02 |
| **R04** | **Vazamento ou exposição de dados financeiros pessoais (LGPD)** | Média | Muito Alto | Uso exclusivo de dados sintéticos e conectores de *sandbox* durante todo o projeto acadêmico; *PII Masking* local antes do *LLM Gateway*; criptografia e exclusão sob demanda. | RNF01 |
| **R05** | **Sequestro de agente via *Prompt Injection* indireto em boleto ou extrato falso** | Média | Alto | Tratamento de todo texto vindo de OCR/PDF como dado não confiável encapsulado; validação determinística dos 47 dígitos da linha digitável FEBRABAN; ausência de ferramentas que movimentem dinheiro. | RF07, RNF05 |
| **R06** | **Falsos positivos/negativos na classificação de transações ou apostas** | Média | Médio | Combinação de regras determinísticas (lista oficial de CNPJs da SPA/MF e MCC `7995`) com modelo de ML supervisionado; botão de correção manual em 1 toque (*human-in-the-loop*) para insumos MEI. | RF02, RF04, RF10 |
| **R07** | **Instabilidade na API Sandbox de agregadores Open Finance ou na API SGS/BCB** | Média | Médio | Desacoplamento via interface `BankDataPort` com suporte nativo a upload de arquivos OFX/CSV/PDF e cache local das últimas séries históricas do SGS/BCB em `Redis`/JSON. | RF01, RNF06, RNF08 |
| **R08** | **Sobrecarga de escopo para o ciclo de 7 semanas** | Alta | Alto | Aplicação rigorosa da matriz de **4 Graus de Necessidade**, blindando a entrega e os testes dos itens **Grau 1 (Must-Have)** antes de avançar para os Graus 2 e 3. | Seção 04 |

---

## 2. Premissas do Projeto

1. **Ambiente Acadêmico Seguro (Dados Sintéticos e Sandbox):**
   O projeto é desenvolvido em 7 semanas por uma equipe de 3 a 5 integrantes no contexto do Challenge 2 (CBL). Nenhum dado bancário real de terceiros é coletado ou armazenado; a validação utiliza conectores de *sandbox* e o dataset sintético calibrado pelas estatísticas oficiais ([`amostra_transacoes_sinteticas_personas.csv`](../evidencias/datasets/amostra_transacoes_sinteticas_personas.csv)).
2. **Operação Estritamente *Read-Only* (Sem Custódia ou Movimentação):**
   O PANDORA atua exclusivamente como copiloto de diagnóstico, planejamento, proteção e educação. O sistema não movimenta valores, não inicia Pix e não executa ordens de investimento. As travas são mecanismos comportamentais de fricção positiva e guias para os bloqueios nativos dos bancos e plataformas `.bet.br`.
3. **Caráter Informativo e Preparatório (Não Substituição Profissional):**
   As orientações sobre a Lei 14.181/2021, o MED do Pix ou o transtorno do jogo organizam a vida do cidadão e preparam a documentação, mas não substituem a atuação de defensores públicos, advogados, psicólogos ou psiquiatras.
4. **Acesso Público às Fontes Regulatórias:**
   Assume-se a disponibilidade contínua das séries públicas da API SGS do Banco Central, da lista de operadoras autorizadas da SPA/Ministério da Fazenda e dos textos normativos do Planalto, BCB e CVM.
5. **Arquitetura Híbrida e Agnóstica de Modelo:**
   Assume-se a viabilidade de orquestrar modelos locais quantizados (para tarefas rápidas de privacidade/triagem) e modelos em nuvem através de um *LLM Gateway* padronizado.
