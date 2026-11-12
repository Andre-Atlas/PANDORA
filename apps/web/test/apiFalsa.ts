import { vi } from "vitest";
import type { EtapaTrilha, LicaoTrilha, RespostaChat } from "@/lib/api/tipos";

type Manipulador = (corpo: unknown) => Response | Promise<Response>;

export const json = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });

/** Troca o `fetch` por rotas combinadas ("POST /chat"); qualquer outra chamada falha o teste. */
export function simularApi(rotas: Record<string, Manipulador>) {
  const chamadas: { rota: string; corpo: unknown }[] = [];
  const falso = vi.fn(async (url: string, init?: RequestInit) => {
    const caminho = new URL(url).pathname;
    const rota = `${init?.method ?? "GET"} ${caminho}`;
    const corpo = init?.body ? JSON.parse(init.body as string) : undefined;
    chamadas.push({ rota, corpo });
    const manipulador = rotas[rota];
    if (!manipulador) throw new Error(`rota sem simulação: ${rota}`);
    return manipulador(corpo);
  });
  vi.stubGlobal("fetch", falso);
  return { chamadas, fetch: falso };
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
