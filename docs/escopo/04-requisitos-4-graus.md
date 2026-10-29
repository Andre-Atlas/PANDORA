# 04 · Requisitos Funcionais e Não Funcionais (4 Graus)

[⬅️ Anterior: 03 · Stakeholders e Personas](03-stakeholders-e-personas.md) · [Voltar ao índice](README.md) · [Próximo: 05 · Riscos e Premissas ➡️](05-riscos-e-premissas.md)

---

## 1. Índice de Grau de Necessidade (4 Graus de Priorização)

Para proteger o cronograma de 7 semanas do Challenge e deixar explícito o que é **bloqueante para o MVP** e o que entra **se sobrar tempo**, os requisitos foram classificados em **4 Graus de Necessidade**:

| Grau de Necessidade | Classificação (MoSCoW) | Critério de Entrega no Projeto |
|---|---|---|
| 🔴 **Grau 1 — Essencial (*Must-Have*)** | **Crítico / Bloqueante (MVP)** | Indispensável para responder à *Essential Question*, garantir segurança ética/jurídica (LGPD, CVM, Anti-Alucinação) e rodar a demo principal das 5 personas. |
| 🟠 **Grau 2 — Importante (*Should-Have*)** | **Alta Relevância Funcional** | Agrega alto valor analítico, preditivo e comportamental (ex.: previsão de fluxo de caixa, score explicável e travas com janela de espera). Entra logo após o Grau 1. |
| 🟡 **Grau 3 — Desejável (*Could-Have*)** | **Se Sobrar Tempo (Incremento)** | Melhorias de conveniência e engajamento complementar que enriquecem a experiência nas Semanas 5 e 6 caso haja folga de cronograma. |
| ⚪ **Grau 4 — Futuro (*Won't-Have now*)** | **Roadmap Pós-Challenge** | Funcionalidades mapeadas na visão de produto, mas fora do escopo de código deste semestre por exigirem licenças bancárias próprias ou integrações externas complexas. |

---

## 2. Requisitos Funcionais (RF01 a RF18)

### 🔴 Grau 1 — Essencial (*Must-Have* · Núcleo do MVP)

| ID | Módulo | Requisito Funcional | Persona Foco |
|---|---|---|---|
| **RF01** | 1. Raio-X Financeiro | Ingestão e normalização de transações via conector **Open Finance Sandbox** (Pluggy/Belvo) **e** via upload de arquivos **OFX, CSV e PDF** de extratos/faturas. | Carla, Mariana |
| **RF02** | 1. Raio-X Financeiro | Classificação automática de transações por categoria (Moradia, Alimentação, Dívidas/Juros, Apostas/Bets, Fraude Suspeita, Insumo MEI), separando o **Mínimo Existencial** dos demais gastos. | Todas |
| **RF03** | 1. Raio-X Financeiro | Consolidação do **Mapa de Dívidas** (credor, saldo, CET anual, atraso) com comparação automática frente às taxas médias da **API SGS do Banco Central** (`20749`, `25477`, `25463`, `25467`). | Carla, Sr. Antônio |
| **RF04** | 2. Detector de Compulsão | Identificação automática de apostas online (*bets*) cruzando MCC (`7995`), descrições e CNPJs com a **lista oficial da SPA/MF**, calculando a **perda líquida real** e o horário de concentração (madrugada/pós-salário). | Diego |
| **RF05** | 2. Detector de Compulsão | Abordagem conversacional empática (livre de julgamento) com disparo imediato do **Fluxo de Crise** (`CVV 188`, CAPS AD, Jogadores Anônimos) ao detectar marcadores de sofrimento agudo. | Diego, Carla |
| **RF06** | 3. Reestruturação | Motor determinístico de priorização de dívidas comparando os métodos **Avalanche** (maior CET) e **Bola de Neve** (menor saldo), blindando previamente 100% do Mínimo Existencial (**Lei 14.181/2021**) e checando o teto do rotativo (**Lei 14.690/2023**). | Carla |
| **RF07** | 5. Proteção (Guardião) | Inspeção multimodal (**Foto/PDF + OCR + Visão**) de boletos bancários e prints de WhatsApp, validando linha digitável FEBRABAN/CNPJ contra golpes e gerando roteiro passo a passo para acionar o **MED do Pix (Res. BCB 147/2021)**. | Sr. Antônio |
| **RF08** | 6. Educação & Investimento | Respostas normativas e educacionais fundamentadas em **RAG Híbrido (`pgvector` + BM25)** sobre fontes oficiais (BCB, CVM, Tesouro, Planalto) com **citação obrigatória** e bloqueio de recomendação de ativos específicos (**Res. CVM 19/20**). | Júlia, Carla, Sr. Antônio |
| **RF09** | 7. Copiloto Multimodal | Interface conversacional unificada com suporte a **texto, áudio/voz (STT/TTS) e upload de imagem/PDF**, orquestrada por grafo multiagente (`LangGraph`). | Sr. Antônio, Todas |

---

### 🟠 Grau 2 — Importante (*Should-Have* · Alta Relevância)

| ID | Módulo | Requisito Funcional | Persona Foco |
|---|---|---|---|
| **RF10** | 1. Raio-X Financeiro | Cálculo explicável do **Score de Saúde Financeira (0 a 100)** baseado em comprometimento de renda, custo médio da dívida, reserva e dias sem apostas, com reclassificação de categoria em 1 toque (*human-in-the-loop*). | Mariana, Júlia |
| **RF11** | 2 e 5. Compulsão & Proteção | Detecção de compras por impulso noturnas via **`Isolation Forest`**, configuração de **Travas Voluntárias com janela de resfriamento (*cooling-off* de 24h–48h)** e guia interativo de autoexclusão nas plataformas `.bet.br` (**Lei 14.790/2023**). | Diego, Mariana |
| **RF12** | 3. Reestruturação | Geração automática do **Dossiê de Repactuação Legal (Lei 14.181/2021)** exportável, contendo relação de credores, cálculo do mínimo existencial e rascunho de proposta para o Procon/Defensoria/consumidor.gov.br. | Carla |
| **RF13** | 4. Orçamento & Metas | **Orçamento Adaptativo por Piso de Renda** (especial para autônomos/MEI) e **Previsão de Fluxo de Caixa para 30, 60 e 90 dias** (`Prophet / ETS`) com alerta preventivo de furo de caixa. | Mariana, Júlia |
| **RF14** | 6. Educação & Investimento | Questionário de **Perfil de Investidor (*Suitability* Educacional — Res. CVM 30/2021)** e **Simulador Determinístico de Reserva de Emergência** alimentado pelas séries Selic (`432`), CDI (`12`) e IPCA (`433`). | Júlia |

---

### 🟡 Grau 3 (*Se Sobrar Tempo*) e ⚪ Grau 4 (*Roadmap Futuro*)

| ID | Grau | Módulo | Requisito Funcional | Persona Foco |
|---|---|---|---|---|
| **RF15** | 🟡 **Grau 3 — Could-Have** | 2. Compulsão | **Diário de Check-in Emocional / Humor** associado a gastos impulsivos (registro rápido por voz/emoji para correlacionar estresse de trabalho e consumo noturno). | Mariana, Diego |
| **RF16** | 🟡 **Grau 3 — Could-Have** | 5. Proteção | Fluxo de **"Modo Crise / Contato de Confiança"** com duplo consentimento (*opt-in*), enviando alerta resumido a um familiar quando uma trava noturna tenta ser rompida ou um boleto falso é detectado. | Diego, Sr. Antônio |
| **RF17** | 🟡 **Grau 3 — Could-Have** | 3. Reestruturação | Gerador de **Carta/Mensagem Personalizada de Contraproposta ao Credor**, formatada com os valores simulados pelo método Avalanche para copiar e colar no *consumidor.gov.br*. | Carla |
| **RF18** | ⚪ **Grau 4 — Won't-Have** | Ecossistema Externo | Execução direta de pagamentos, iniciação de transação Pix (ITP do Open Finance), bloqueio direto no *core banking* dos bancos ou integração via WhatsApp Business API oficial. | Todas |

---

## 3. Requisitos Não Funcionais (RNF01 a RNF09)

| ID | Grau | Categoria | Requisito Não Funcional | Meta / Limite Técnico |
|---|---|---|---|---|
| **RNF01** | 🔴 **Grau 1 — Must-Have** | Privacidade (LGPD) | **Privacy by Design:** Mascaramento obrigatório de PII (CPF, nome, conta, telefone) antes de qualquer chamada a LLMs externos e exclusão total sob demanda. | **0% de vazamento de PII** em logs e chamadas externas (Lei 13.709/2018). |
| **RNF02** | 🔴 **Grau 1 — Must-Have** | Compliance CVM | **Trava de Consultoria Regulada:** Bloqueio arquitetural contra recomendação de valores mobiliários específicos e operação 100% *read-only*. | **Bloqueio $\ge 95\%$** em suíte adversarial de indução a recomendação (Res. CVM 19/20). |
| **RNF03** | 🔴 **Grau 1 — Must-Have** | Determinismo | **Exatidão Matemática:** Proibição de cálculos aritméticos livres no LLM; toda conta de juros, CET, amortização e saldo roda em funções Python tipadas. | **Erro numérico = $0,00\%$** na suíte de testes unitários financeiros. |
| **RNF04** | 🔴 **Grau 1 — Must-Have** | Anti-Alucinação | **Rastreabilidade RAG:** Respostas sobre leis, prazos e direitos exigem recuperação no corpus oficial com exibição da norma, artigo e link válido. | **Faithfulness $\ge 0,90$** (Ragas) e **100% de citação** em consultas normativas. |
| **RNF05** | 🔴 **Grau 1 — Must-Have** | Segurança de IA | **Defesa contra Prompt Injection Indireto:** Isolamento estrutural de todo texto extraído via OCR de boletos, extratos PDF e prints de conversa. | **Bloqueio $\ge 95\%$** em ataques de *prompt injection* embutidos em documentos. |
| **RNF06** | 🟠 **Grau 2 — Should-Have** | Arquitetura e Latência | Arquitetura **Hexagonal (Ports & Adapters)** em `FastAPI`, **LLM Gateway** agnóstico de provedor e tempo de resposta fluido em dispositivos móveis/web. | **Latência $p95 \le 8\text{ s}$** (texto) e **$\le 12\text{ s}$** (multimodal imagem/voz). |
| **RNF07** | 🟠 **Grau 2 — Should-Have** | Acessibilidade | Interface **PWA responsiva** seguindo diretrizes **WCAG 2.2 Nível AA** (alto contraste, fontes escaláveis, botões $\ge 44\times 44\text{ px}$ e navegação por voz para idosos). | **Score Lighthouse A11y $\ge 90$** e zero barreiras críticas de voz/teclado. |
| **RNF08** | 🟡 **Grau 3 — Could-Have** | Eficiência e Cache | Cache semântico e de séries temporais (`Redis`) para consultas repetidas à API SGS do Banco Central e dúvidas frequentes da Lei 14.181/2021. | **Redução $\ge 30\%$** em chamadas repetidas e cache hit $< 200\text{ ms}$. |
| **RNF09** | ⚪ **Grau 4 — Won't-Have** | Alta Disponibilidade | Cluster multi-região ativo-ativo e homologação direta no diretório central do Open Finance Brasil como instituição financeira participante. | SLA de 99,99% em produção bancária real. |
