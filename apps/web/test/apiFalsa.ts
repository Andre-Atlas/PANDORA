import { vi } from "vitest";
import type { EtapaTrilha, LicaoTrilha, RaioX, RespostaChat, Transacao } from "@/lib/api/tipos";
import { CHAVE_SESSAO } from "@/lib/conta/sessao";

type Manipulador = (corpo: unknown, init?: RequestInit) => Response | Promise<Response>;

export const json = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });

/**
 * Troca o `fetch` por rotas combinadas ("POST /chat"); qualquer outra chamada falha o teste.
 * A rota ignora a query, que fica em `pedidos`. Corpos JSON chegam lidos; FormData chega como está.
 */
export function simularApi(rotas: Record<string, Manipulador>) {
  const chamadas: { rota: string; corpo: unknown }[] = [];
  /** As mesmas chamadas, com a query e o `init` (cabeçalhos), para quem precisa conferir. */
  const pedidos: { rota: string; busca: string; init?: RequestInit }[] = [];
  const falso = vi.fn(async (url: string, init?: RequestInit) => {
    const endereco = new URL(url);
    const rota = `${init?.method ?? "GET"} ${endereco.pathname}`;
    const corpo = typeof init?.body === "string" ? JSON.parse(init.body) : init?.body;
    chamadas.push({ rota, corpo });
    pedidos.push({ rota, busca: endereco.search, init });
    const manipulador = rotas[rota];
    if (!manipulador) throw new Error(`rota sem simulação: ${rota}`);
    return manipulador(corpo, init);
  });
  vi.stubGlobal("fetch", falso);
  return { chamadas, pedidos, fetch: falso };
}

export const FONTE = {
  n: 1,
  norma: "Lei 14.181/2021",
  artigo: "Art. 104-A",
  link: "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/L14181.htm",
  trecho: "O plano de pagamento pode ter prazo máximo de cinco anos.",
  pagina: null,
  ressalva: null,
};

export const RESPOSTA: RespostaChat = {
  texto: "O plano pode durar até cinco anos [1].",
  abstencao: false,
  citacoes: [FONTE],
  crise: false,
  modelo: "qwen2.5:14b",
};

export const ETAPAS: EtapaTrilha[] = [
  { n: 1, t: "Mínimo existencial", x: 70, lado: "d", marco: null, emblema: "templo", licao_id: "minimo-existencial" },
  { n: 2, t: "Juros e CET", x: 200, lado: "e", marco: null, emblema: "balanca", licao_id: "juros-e-cet" },
  { n: 3, t: "Rotativo", x: 288, lado: "e", marco: "Marco: conheço meus direitos", emblema: "espiral", licao_id: "rotativo" },
];

export const LICAO: LicaoTrilha = {
  id: "rotativo",
  titulo: "Rotativo",
  explicacao: "Sem limite aprovado, os juros do rotativo não passam do valor original da dívida [1].",
  citacoes_explicacao: [1],
  fontes: [FONTE],
  perguntas: [
    {
      enunciado: "Qual é o teto dos juros do rotativo sem limite aprovado?",
      opcoes: ["O valor original da dívida", "O dobro da dívida", "Não há teto"],
      certa: 0,
      feedback: "O total cobrado não pode exceder o valor original da dívida [1].",
      citacoes: [1],
    },
  ],
};

/* Dados reais (#71) */

/** Liga os dados reais neste teste; com `comSessao`, já entra com um token válido. */
export function ligarDadosReais({ comSessao = false } = {}) {
  vi.stubEnv("NEXT_PUBLIC_PANDORA_DADOS_REAIS", "1");
  if (comSessao) localStorage.setItem(CHAVE_SESSAO, JSON.stringify(SESSAO));
}

export const SESSAO = { token: "token-de-teste", tipo: "Bearer" as const, expira_em: "2099-01-01T00:00:00Z" };

export const USUARIO = { id: "u-1", email: "carla@exemplo.com", criado_em: "2026-11-17T10:00:00Z" };

export const CONSENTIMENTO = {
  id: "c-1",
  finalidade: "diagnostico_financeiro" as const,
  versao_termo: "2026-11",
  aceito_em: "2026-11-17T10:00:00Z",
  revogado_em: null,
  ativo: true,
};

const transacao = (id: string, data: string, valor: number, descricao: string, categoria: Transacao["categoria"]): Transacao => ({
  id,
  conta_id: "principal",
  data_hora: `${data}T00:00:00-03:00`,
  valor_centavos: valor,
  forma_pagamento: "PIX",
  descricao_mascarada: descricao,
  mcc: null,
  categoria,
  origem_categoria: "modelo",
  confianca_categoria: null,
  versao_modelo: "provisorio-regras-mcc",
  essencial: categoria === "MORADIA",
  parcela: null,
});

export const TRANSACOES: Transacao[] = [
  transacao("t-3", "2026-10-15", -48000, "PARCELA EMPRESTIMO PESSOAL", "TRANSFERENCIA"),
  transacao("t-2", "2026-10-06", -95000, "PAGAMENTO ALUGUEL RESIDENCIAL", "MORADIA"),
  transacao("t-1", "2026-10-05", 285000, "CREDITO SALARIO", "RENDA"),
];

export const RAIO_X: RaioX = {
  mes: "2026-10",
  renda_centavos: 285000,
  minimo_existencial_centavos: 95000,
  folga_centavos: 190000,
  gastos: [{ categoria: "MORADIA", total_centavos: 95000, essencial_centavos: 95000 }],
  calculo: {
    fonte: "motor_deterministico",
    entradas: [
      { nome: "Renda do mês", valor: "R$ 2.850,00" },
      { nome: "Gastos essenciais (Mínimo Existencial)", valor: "R$ 950,00" },
    ],
  },
};

export const pagina = (itens: Transacao[]) => json({ itens, total: itens.length, pagina: 1, por_pagina: 50 });

export const NAO_IMPLEMENTADO = () =>
  json({ type: "urn:pandora:erro:nao-implementado", title: "Ainda não implementado.", status: 501, issue: 72 }, 501);
