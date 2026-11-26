# PANDORA

> Challenge 2 · CBL · Big Idea **Qualidade de Vida**: *"Empoderando pessoas com IA para compreender melhor, decidir melhor e viver melhor."*
> Tema do grupo: **Finanças**.

## Essential Question

> **Como agentes de IA, apoiados em evidências confiáveis, podem ajudar pessoas endividadas ou com comportamento financeiro compulsivo a recuperar o controle das finanças e, com isso, a qualidade de vida?**

## O problema em números

| Indicador | Valor | Fonte |
|---|---|---|
| Brasileiros inadimplentes | **81,7 milhões** (fev/2026) | [Serasa](https://www.serasa.com.br/imprensa/10-anos-do-mapa-de-inadimplencia/) |
| Famílias endividadas | **81,7%** (set/2026) | [CNC/Peic](https://portaldocomercio.org.br/acoes-institucionais/cnc-inadimplencia-e-endividamento-das-familias-brasileiras-recuam-em-setembro/) |
| Juros do rotativo do cartão | **435,9% a.a.** (fev/2026) | [Agência Brasil / BCB](https://agenciabrasil.ebc.com.br/economia/noticia/2026-03/juros-do-cartao-de-credito-pesam-mais-para-familias-em-fevereiro) |
| Pix para apostas online | **R$ 20,8 bilhões** em ago/2024 | [BCB, Estudo Especial 119/2024](https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf) |
| Vítimas de golpes com Pix ou boleto | **24 milhões**, quase R$ 29 bi (jul/2024–jun/2025) | [Datafolha/FBSP](https://www12.senado.leg.br/radio/1/noticia/2025/08/18/mais-de-24-milhoes-de-pessoas-foram-vitimas-de-golpes-pelo-pix) |

## Telas

Protótipo gerado pelo [design system](frontend/design-system/README.md): 7 telas e 2 estados, em 16 quadros.

### Versões das interfaces

| Versão | O que mudou | Onde ver |
|---|---|---|
| **3 · Responsiva** (10/11/2026, [#106](https://github.com/Andre-Atlas/PANDORA/pull/106)) | Layout para celular, tablet e desktop, em retrato e paisagem. Meandro no lugar da serra, navbar retrátil, mito em figura negra no tema claro e em figura vermelha no escuro, abertura com a cena esfumada. | [Figma: telas em 6 tamanhos e 2 temas](https://www.figma.com/design/g19U79NnQEMfGIXxPwgdDe) · [Prévia interativa](https://claude.ai/artifact/CrTqPZbKTiQSULhxNSWJLW) · [Design system](https://claude.ai/artifact/PiHQsMY79M1frKVo9tcNDX) · [capturas](frontend/design-system/assets/Telas/responsivo) |
| **2 · Ornamentos gregos** (05/11/2026, [#100](https://github.com/Andre-Atlas/PANDORA/pull/100) e [#101](https://github.com/Andre-Atlas/PANDORA/pull/101)) | Optima e Cinzel Decorative, ornamentos nos componentes, brasões na trilha. Só celular. | A grade abaixo · [código desta versão](https://github.com/Andre-Atlas/PANDORA/tree/a6b3970/frontend/design-system) |
| **1 · Identidade visual** (05/11/2026, [#2](https://github.com/Andre-Atlas/PANDORA/pull/2) e [#3](https://github.com/Andre-Atlas/PANDORA/pull/3)) | Primeira versão: tokens, componentes e galeria de 16 quadros. | [Telas desta versão](https://github.com/Andre-Atlas/PANDORA/tree/7219288/frontend/design-system/assets/Telas) · [código desta versão](https://github.com/Andre-Atlas/PANDORA/tree/7219288/frontend/design-system) |

Para ver a versão atual no navegador, abra [`frontend/design-system/index.html`](frontend/design-system/index.html) (a galeria completa), ou rode `node frontend/design-system/src/teste.js --saida <pasta>` e abra `tela.html` e `responsivo.html` dessa pasta. A Prévia interativa e o Design system ficam no claude.ai e só abrem para quem recebeu acesso.

<table>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/inicio-celular-claro.jpg" alt="Início no celular, tema claro" width="150"><br><sub>Início · celular · claro</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/inicio-celular-escuro.jpg" alt="Início no celular, tema escuro" width="150"><br><sub>Início · celular · escuro</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/navbar-recolhida-celular.jpg" alt="Início no celular com a navbar recolhida" width="150"><br><sub>Navbar recolhida · celular</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/responsivo/abertura-celular.jpg" alt="Abertura no celular" width="150"><br><sub>Abertura · celular</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/inicio-desktop-claro.jpg" alt="Início no desktop, tema claro, com o trilho lateral" width="320"><br><sub>Início · desktop · claro</sub></td>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/abertura-desktop.jpg" alt="Abertura no desktop com a cena esfumada" width="320"><br><sub>Abertura · desktop</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/dividas-tablet-escuro.jpg" alt="Dívidas no tablet deitado, tema escuro" width="320"><br><sub>Dívidas · tablet deitado · escuro</sub></td>
    <td align="center" valign="top" colspan="2"><img src="frontend/design-system/assets/Telas/responsivo/navbar-recolhida-desktop-escuro.jpg" alt="Início no desktop, tema escuro, com o trilho recolhido" width="320"><br><sub>Navbar recolhida · desktop · escuro</sub></td>
  </tr>
</table>

Versão 2, só celular:

<table>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-01.png" alt="1a · Abertura" width="200"><br><sub>1a · Abertura</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-02.png" alt="1b · Como se sente" width="200"><br><sub>1b · Como se sente</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-03.png" alt="1c · O que pesa" width="200"><br><sub>1c · O que pesa</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-04.png" alt="1d · Como começar" width="200"><br><sub>1d · Como começar</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-05.png" alt="2 · Início (Raio-X)" width="200"><br><sub>2 · Início (Raio-X)</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-06.png" alt="3 · Dívidas" width="200"><br><sub>3 · Dívidas</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-07.png" alt="4a · Elpis: resposta com fonte" width="200"><br><sub>4a · Elpis: resposta com fonte</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-08.png" alt="4b · Elpis: limites" width="200"><br><sub>4b · Elpis: limites</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-09.png" alt="4c · Elpis: voz" width="200"><br><sub>4c · Elpis: voz</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-10.png" alt="5a · Trilha" width="200"><br><sub>5a · Trilha</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-11.png" alt="5b · Trilha: lição" width="200"><br><sub>5b · Trilha: lição</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-12.png" alt="6a · Guardião: golpes" width="200"><br><sub>6a · Guardião: golpes</sub></td>
  </tr>
  <tr>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-13.png" alt="6b · Guardião: apostas" width="200"><br><sub>6b · Guardião: apostas</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-14.png" alt="7 · Metas e previsão" width="200"><br><sub>7 · Metas e previsão</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-15.png" alt="E1 · Fluxo de crise" width="200"><br><sub>E1 · Fluxo de crise</sub></td>
    <td align="center" valign="top"><img src="frontend/design-system/assets/Telas/tela-16.png" alt="E2 · Leitura ampliada" width="200"><br><sub>E2 · Leitura ampliada</sub></td>
  </tr>
</table>

## Identidade visual

<table>
  <tr>
    <td align="center"><img src="frontend/design-system/assets/Cena/pandora-cena-1600.webp" alt="Cena da abertura" width="200"><br><sub>Cena da abertura</sub></td>
    <td align="center"><img src="frontend/design-system/assets/Marca/caixa-esperanca.svg" alt="Marca: caixa da esperança" width="120"><br><sub>Marca: caixa da esperança</sub></td>
    <td align="center"><img src="frontend/design-system/assets/Marca/elpis-medalhao.svg" alt="Medalhão de Elpis" width="120"><br><sub>Medalhão de Elpis</sub></td>
  </tr>
</table>

<img src="frontend/design-system/assets/Ornamentos/meandro.svg" alt="Ornamento meandro" width="480">

<img src="frontend/design-system/assets/Ornamentos/serra.svg" alt="Ornamento serra" width="480">

## Primeiro Protótipo Multiagente (4º Desafio)

O sistema multiagente do PANDORA ([`docs/entregas/04-primeiro-prototipo-multiagente/`](docs/entregas/04-primeiro-prototipo-multiagente/README.md)) implementa um **grafo de estado compilado com `LangGraph` (`StateGraph(EstadoMultiagente)`)** e **Tool Calling nativo (`@tool` + `bind_tools` via `qwen2.5:7b` no Ollama local / Anthropic)** em **7 agentes especializados colaborativos**, integrados ao RAG híbrido (`BAAI/bge-m3` + `BM25` + `RRF`) e às travas de segurança (`RNF01`–`RNF05`):

1. **`OrquestradorAgent`** (*Orchestrator + Communication*): mascara PII (`CPF`, `CNPJ`, telefone, e-mail, cartão, chave Pix UUID), classifica intenções, roteia para os especialistas e adapta o tom da síntese final ao perfil da persona.
2. **`AnalistaAgent`** (*Analysis — Raio-X*): lê o extrato transacional da persona e calcula de forma determinística a renda, o **Mínimo Existencial**, a folga real e o comparativo com as séries SGS do Banco Central (`22022`, `25467`).
3. **`EstrategistaAgent`** (*Analysis — Dívidas*): blinda 100% do Mínimo Existencial, prioriza contas vitais em atraso, compara **Avalanche** vs. **Bola de Neve** e verifica o teto da **Lei nº 14.690/2023**.
4. **`CoachAgent`** (*Analysis + Communication — Bets*): detecta apostas (`MCC 7995`), calcula perda líquida real e concentração noturna (`23h–06h`) e traduz o impacto em custo de oportunidade sem julgamento moral.
5. **`GuardiaoAgent`** (*Analysis + Validation — Antifraude*): neutraliza tentativas de *prompt injection* em textos OCR de boletos, valida os 47 dígitos FEBRABAN (Módulo 10, banco e beneficiário PF) e gera o roteiro do **MED do Pix (80 dias)**.
6. **`EducadorAgent`** (*Research — RAG*): consome as sub-consultas geradas pelos especialistas, recupera trechos das 33 fontes oficiais com citações `[n]` e aplica o portão de abstenção para consultas fora de domínio.
7. **`ComplianceAgent`** (*Validation — Guardrails*): portão final *fail-closed* que verifica Protocolo de Crise (`CVV 188`, `CAPS AD`, `Jogadores Anônimos`), Trava CVM (Recusa Educativa com 3 critérios objetivos), consistência das citações `[n]` e ausência de PII — acionando revisão automática quando necessário.

## Organização das Pastas

```text
PANDORA/
├── README.md                                           # Visão geral, arquitetura, pastas e como rodar testes/demo
├── docs/
│   ├── entregas/
│   │   ├── 02-base-conhecimento-e-prototipo-rag/       # Entregável 02: Base de Conhecimento & RAG Híbrido
│   │   ├── 03-llm-x-rag/                               # Entregável 03: Benchmark LLM puro × RAG
│   │   └── 04-primeiro-prototipo-multiagente/          # Entregável 04: 7 Agentes LangGraph, executar_entrega.sh, diagramas e demos
│   ├── agentes/                                        # Docs 01–05 dos agentes (arquitetura, papéis, fluxo, demo e revisão humana)
│   ├── arquitetura-geral.md                            # Arquitetura unificada em 6 camadas do sistema PANDORA
│   ├── adr/                                            # ADRs formais (ADR-0001, ADR-0002, ADR-0003)
│   ├── rag/                                            # Documentação do RAG híbrido (v0.1.0)
│   ├── escopo/                                         # Escopo CBL, requisitos RF01–RF18 e RNF01–RNF09
│   ├── personas/                                       # Fichas individuais das 10 personas
│   └── evidencias/                                     # Artigos, notícias e dataset sintético (amostra_transacoes_sinteticas_personas.csv)
├── services/
│   └── rag/
│       ├── src/pandora_rag/
│       │   ├── agents/                                 # Código multiagente (LangGraph StateGraph, @tools, specialists, llm_provider)
│       │   ├── ingest/                                 # Coleta, extração e chunking estrutural
│       │   ├── index/                                  # Embeddings, pgvector e MemoryStore
│       │   ├── retrieve/                               # Busca híbrida (vetor + BM25 + RRF + reranker)
│       │   ├── generate/                               # Gateway LLM (Ollama/Anthropic), citação e máscara PII
│       │   └── cli.py                                  # CLI: coletar, extrair, indexar, buscar, ask, agent e demo
│       └── tests/                                      # Suíte automatizada pytest (65 testes: agentes + guardrails + RAG)
├── evals/                                              # Golden set, métricas e execuções de avaliação
└── frontend/design-system/                             # Design system e telas prototipadas
```

## Como Rodar os Testes e a Demonstração

Pré-requisito: [`uv`](https://docs.astral.sh/uv/) instalado (gerencia automaticamente Python `3.12` e as dependências de `services/rag/`).

```bash
# Atalho em 1 comando (na raiz do repositório: roda 65 testes + lint + demo offline)
sh docs/entregas/04-primeiro-prototipo-multiagente/executar_entrega.sh

# Ou etapa por etapa dentro de services/rag:
cd services/rag

# Rodar toda a suíte de testes automatizados (65 testes: agentes LangGraph + Tool Calling + guardrails + RAG)
uv run --extra dev pytest tests/ -v

# Rodar apenas os testes do sistema multiagente (28 testes)
uv run --extra dev pytest tests/test_agents_tools.py tests/test_agents_specialists.py tests/test_agents_graph.py -v

# Rodar verificação de lint (ruff) nos arquivos do sistema multiagente
uv run --extra dev ruff check src/pandora_rag/agents/ src/pandora_rag/cli.py tests/test_agents_*.py

# Executar a demonstração completa das 4 jornadas (gera Markdown + JSON com trace dos 7 agentes)
uv run pandora-rag demo --saida-dir ../../docs/entregas/04-primeiro-prototipo-multiagente/demo

# Executar a demonstração em modo 100% offline (sem Postgres, GPU ou API externa)
uv run pandora-rag demo --offline

# Executar uma consulta avulsa no sistema multiagente com saída JSON auditável
uv run pandora-rag agent \
  "Meu CPF 123.456.789-00. Estou no rotativo do cartão e a luz atrasou." \
  --persona carla_34 \
  --saida-json
```

> **Nota sobre testes de métricas (`evals/`):** para incluir também os testes de `evals/metrics/tests` (ROUGE/BLEU), rode `uv run --extra dev --extra eval pytest`.

## Documentação

| Documento | Conteúdo |
|---|---|
| [Entregável 02 · Base e RAG Híbrido](docs/entregas/02-base-conhecimento-e-prototipo-rag/README.md) | Base de conhecimento oficial, chunking, embeddings `bge-m3`, `pgvector` e demonstrações |
| [Entregável 03 · Benchmark LLM × RAG](docs/entregas/03-llm-x-rag/README.md) | Avaliação comparativa LLM puro vs. RAG híbrido no golden set |
| [Entregável 04 · Primeiro Protótipo Multiagente](docs/entregas/04-primeiro-prototipo-multiagente/README.md) | Pasta oficial do 4º Desafio: `executar_entrega.sh`, `montar_zip.sh`, diagramas `.mmd`, traces `qwen2.5:7b` e guia de testes |
| [Arquitetura Geral em 6 Camadas](docs/arquitetura-geral.md) | Visão canônica unificada entre Frontend, API Hexagonal, RAG Híbrido, LangGraph, ML e Banco Vetorial |
| [Problema e Essential Question](docs/01-problema-e-essential-question.md) | Contexto, stakeholders, personas e fontes |
| [Sistema Multiagente (Agentes + Revisão + Demo)](docs/agentes/README.md) | Docs 01–05 dos 7 agentes, responsabilidades, fluxo `LangGraph`, execução demonstrativa e revisão humana (`05-revisao-humana.md`) |
| [RAG Híbrido (v0.1.0)](docs/rag/README.md) | Arquitetura de ingestão, embeddings `bge-m3`, banco vetorial `pgvector` + BM25, golden set e decisão LLM |
| [Registros de Decisão Arquitetural (ADR)](docs/adr/README.md) | `ADR-0001` (estado tipado), `ADR-0002` (`LangGraph` + Tool Calling) e `ADR-0003` (arquitetura em 6 camadas) |
| [Escopo e Concepção (MD + PDF)](docs/escopo/README.md) | Cenário, 10 Guiding Questions, 6 Stakeholders, 5 Personas, RF/RNF (4 Graus), Riscos, Premissas, Métricas e [PDF (5 páginas)](docs/escopo/PANDORA-Documento-de-Escopo-CBL.pdf) |
| [Personas e Jornadas](docs/personas/README.md) | 5 personas exclusivas (fichas individuais, dores, casos de uso e barreiras) |
| [Evidências](docs/evidencias/README.md) | Visão geral do acervo |
| [Notícias](docs/evidencias/noticias/README.md) | Levantamentos e reportagens 2024–2026 |
| [Artigos](docs/evidencias/artigos/README.md) | Estudos, escalas de bem-estar financeiro e marcos legais |
| [Datasets](docs/evidencias/datasets/README.md) | Séries do BCB, bases públicas e amostra sintética |
