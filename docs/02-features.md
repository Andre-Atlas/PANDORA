# 02 · Features

Prioridade **MoSCoW** pensada para 7 semanas e um grupo de 3–5 pessoas. **Must** = MVP da apresentação; **Should** = entra se o MVP estiver estável; **Could** = roadmap futuro.

## 1. Raio-X Financeiro

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Conexão bancária (sandbox) | Must | Conectar contas via agregador Open Finance (Pluggy/Belvo) em modo sandbox | Adapter `BankDataPort` ([ADR-0002](adr/0002-dados-bancarios-sandbox.md)) |
| Upload de extrato | Must | OFX, CSV e PDF de extrato/fatura | Parsers + OCR/LLM para PDF |
| Classificação de transações | Must | Categoria, recorrência, essencial × supérfluo | Regras → modelo ML → LLM fallback |
| Mapa de dívidas | Must | Credor, saldo, juros/CET, parcelas, atraso | Extração + formulário assistido |
| Score de saúde financeira | Should | Indicador 0–100: comprometimento de renda, reserva, atrasos | Fórmula explicável (não caixa-preta) |
| Mínimo existencial | Should | Quanto da renda está protegido segundo a Lei 14.181 | Regra de negócio + RAG |

**Histórias:**
- *Como Carla, quero ver todas as minhas dívidas num lugar só, com quanto cada uma me custa por mês, para saber qual atacar primeiro.*
- *Como usuário sem Open Finance, quero mandar a foto/PDF da fatura e ter o mesmo diagnóstico.*

## 2. Detector de Compulsão

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Detecção de apostas | Must | Identifica transações para bets (Pix/cartão) | Cruzamento com lista SPA/MF de operadoras autorizadas + descrição/CNPJ |
| Padrões de impulso | Should | Gastos noturnos, picos pós-salário, escalada de valores | Isolation Forest + features temporais |
| Check-in de humor | Could | Registro opcional de emoção associada ao gasto | Multimodal (texto/voz) |
| Conversa acolhedora | Must | Abordagem não estigmatizante, com opt-in | Agente Coach + guardrails |
| Encaminhamento | Must | CVV 188, CAPS, Jogadores Anônimos quando há sinal de risco | Regra + classificador de risco |

**Histórias:**
- *Como Diego, quero que o app perceba quando estou apostando mais e me ofereça ajuda sem me julgar.*

## 3. Plano de Reestruturação

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Priorização de dívidas | Must | Avalanche (maior juro) × bola de neve (menor saldo), com explicação | Otimizador determinístico |
| Simulador de renegociação | Must | Impacto de desconto, prazo e taxa no orçamento | Cálculo financeiro (PMT/CET) |
| Guia de canais | Should | Desenrola, Serasa Limpa Nome, consumidor.gov.br, Procon | RAG + links oficiais |
| Repactuação (Lei 14.181) | Should | Passo a passo e rascunho de pedido de conciliação | Agente Estrategista + template |
| Carta/proposta ao credor | Could | Texto gerado com valores do plano | LLM + revisão do usuário |

## 4. Orçamento e Metas

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Orçamento adaptativo | Must | Base-zero ou 50-30-20 ajustado à fase (crise → estabilidade) | Regras + sugestão do agente |
| Previsão de fluxo de caixa | Should | Saldo previsto para 30/60/90 dias | Prophet/ETS |
| Metas e nudges | Should | Metas pequenas, reforço positivo, sem gamificação viciante | Notificações PWA |

## 5. Proteção de Ativos

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Antifraude transacional | Should | Alerta de transação fora do padrão | Detecção de anomalia |
| Análise de golpe (multimodal) | Must | Usuário envia print/mensagem/boleto e recebe avaliação de risco | Visão + OCR + RAG de padrões de golpe |
| Travas e limites | Should | Limite de gasto por categoria, período de espera para desativar | Regra de negócio |
| Autoexclusão de bets | Should | Guia e atalho para os mecanismos oficiais de autoexclusão | RAG + links SPA/MF |
| Modo crise | Could | Contato de confiança notificado (opt-in) | Fluxo com consentimento duplo |
| Reserva e impenhorabilidade | Should | Meta de reserva + direitos sobre salário, poupança até 40 SM, bem de família | Cálculo + RAG (CPC art. 833, Lei 8.009/90) |

## 6. Educação e Investimento

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Perfil de investidor | Should | Questionário no estilo suitability (conservador/moderado/arrojado) | Formulário + regra |
| Trilha educacional | Must | Conteúdo progressivo conforme a fase da jornada | RAG sobre BCB/CVM/Tesouro |
| Simuladores | Should | Juros compostos, Tesouro × CDB × poupança, custo de oportunidade | Cálculo determinístico |
| Guardrail CVM | Must | Recusa recomendar produto/ativo específico | Compliance Guard ([ADR-0004](adr/0004-investimento-educacional.md)) |

## 7. Copiloto PANDORA (multimodal)

| Feature | MoSCoW | Descrição | Técnica |
|---|---|---|---|
| Chat com citações | Must | Respostas com fonte (trecho + link) | RAG + Orquestrador |
| Entrada por voz | Should | Falar em vez de digitar; resposta em áudio opcional | STT/TTS |
| Entrada por imagem/PDF | Must | Boleto, fatura, print de conversa, extrato | Agente Multimodal |
| Memória de contexto | Should | Lembra o plano e as metas do usuário | Estado persistido por usuário |

## Recorte do MVP (demo da Semana 6)

1. Conectar conta sandbox **ou** subir extrato → Raio-X com dívidas e categorias.
2. Detector de apostas sinaliza padrão → conversa acolhedora + oferta de trava.
3. Plano de reestruturação priorizado + simulação.
4. Enviar foto de boleto/print suspeito → avaliação de golpe.
5. Perguntar "quais meus direitos no superendividamento?" → resposta RAG com citação.
6. Tudo isso por chat, com pelo menos uma interação por voz.
