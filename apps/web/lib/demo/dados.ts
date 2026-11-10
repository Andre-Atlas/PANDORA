/**
 * Dados de demonstração, os mesmos da galeria do design system.
 *
 * Enquanto a API não entrega dados reais, as telas leem daqui. Cada bloco
 * corresponde a uma tela e deve ser trocado pela chamada da API correspondente
 * (`lib/api/tipos.ts`) quando ela existir. Nada aqui é calculado: os valores
 * marcados como "Calculado" nas telas viriam do motor determinístico.
 */

/** Persona usada no Início, nas Dívidas e na Elpis (Carla, superendividamento). */
export const PESSOA = { nome: "Carla" } as const;

export const INICIO = {
  protegido: "R$ 2.100,00",
  insight: { valor: "R$ 342,18", texto: " da sua fatura foram só juros e IOF. É metade do mercado do mês." },
  proximoPasso: {
    titulo: "Regularizar a conta de luz",
    texto: "R$ 360 em 2 faturas. Com 45 dias de atraso, há risco de corte.",
  },
  raioX: {
    renda: "R$ 2.850",
    protegido: { valor: 2100, rotulo: "R$ 2.100" },
    folga: { valor: 750, rotulo: "R$ 750" },
    nota: "As parcelas de hoje somam cerca de R$ 1.110, mais do que a folga. O plano começa pela ordem certa.",
  },
  saude: {
    pontos: 31,
    fatores: [
      ["Renda comprometida", "Alta"],
      ["Custo médio das dívidas", "Alto"],
      ["Reserva", "Ainda não há"],
      ["Dias sem apostas", "Não se aplica"],
    ],
  },
} as const;

export const DIVIDAS = {
  total: "R$ 10.360",
  resumo: "Total em 3 dívidas · R$ 750 de folga",
  etapa: { atual: 3, total: 5, texto: "Etapa 3 de 5: conta de luz em dia" },
  minimoExistencial: "R$ 2.100",
} as const;

/** Uma conversa já feita, para a tela da Elpis não abrir vazia. */
export const CONVERSA = {
  salario: {
    pergunta: "Podem bloquear meu salário por causa do cartão?",
    norma: "Código de Processo Civil, art. 833, IV",
    href: "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm",
  },
  ordem: {
    pergunta: "Então o que eu resolvo primeiro?",
    linhas: [
      ["1º Mínimo existencial", "R$ 2.100"],
      ["2º Conta de luz", "R$ 360"],
      ["Folga por mês", "R$ 750"],
    ] as [string, string][],
  },
  investimento: {
    pergunta: "Qual ação ou CDB devo comprar com meus R$ 1.500?",
    criterios: [
      ["Liquidez diária", "resgatar no mesmo dia."],
      ["Baixo risco de crédito", "Tesouro Nacional ou FGC."],
      ["Pós-fixado", "acompanha a Selic ou o CDI."],
    ],
  },
  tarifa: { pergunta: "O banco pode cobrar essa tarifa nova da minha conta?" },
  sugestoes: ["O que é repactuação?", "Ver meu plano"],
} as const;

/** Persona do Guardião, aba Apostas (Diego, compulsão por bets). */
export const APOSTAS = {
  sobre: "Resultado real em outubro · Diego",
  resultado: "− R$ 1.170",
  linhas: [
    ["Enviado para apostas", "R$ 1.450"],
    ["Prêmios recebidos", "R$ 280"],
  ],
} as const;

/** Boleto verificado no Guardião (aba Golpes) e na leitura ampliada (Sr. Antônio). */
export const BOLETO = {
  descricao: "“Quitação com 70% de desconto”, recebido por WhatsApp.",
  valor: "R$ 1.198,00",
  checagens: [
    { ok: true, titulo: "Linha digitável", texto: "Lida e conferida" },
    { ok: false, titulo: "Banco do boleto", texto: "Diferente do banco credor" },
    { ok: false, titulo: "Quem recebe", texto: "Conta de pessoa física" },
  ],
  pessoaAmpliada: "Sr. Antônio",
} as const;

/** Persona de Metas (Júlia, reconstrução e reserva). */
export const METAS = {
  sobre: "Reserva de emergência · Júlia",
  guardado: "R$ 1.500",
  meta: "de R$ 16.800, ou 6 meses do seu custo essencial",
  degraus: [
    { prazo: "15 dias", valor: "R$ 1.400", nivel: 1 },
    { prazo: "1 mês", valor: "R$ 2.800", nivel: 1500 / 2800 },
    { prazo: "3 meses", valor: "R$ 8.400", nivel: 0 },
    { prazo: "6 meses", valor: "R$ 16.800", nivel: 0 },
  ],
  previsao: [
    ["30 dias", "R$ 1.200"],
    ["60 dias", "R$ 2.400"],
    ["90 dias", "R$ 3.600"],
  ],
} as const;
