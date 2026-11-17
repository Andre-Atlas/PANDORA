import { apagarSessao, lerToken, VERSAO_TERMO } from "@/lib/conta/sessao";
import type {
  Categoria,
  Consentimento,
  EtapaTrilha,
  Extrato,
  LicaoTrilha,
  PaginaTransacoes,
  Problema,
  RaioX,
  RespostaChat,
  Score,
  Sessao,
  Transacao,
  Usuario,
} from "./tipos";

/** Base da API. Em produção, defina NEXT_PUBLIC_PANDORA_API_URL. */
export const URL_API = (process.env.NEXT_PUBLIC_PANDORA_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

/** A Elpis leva de 8 a 15 s; passado este tempo, a pessoa vê o erro em vez de esperar sem fim. */
const TEMPO_MAXIMO_MS = 75_000;

export class ErroApi extends Error {
  constructor(
    mensagem: string,
    readonly status: number | null,
    readonly problema?: Problema,
  ) {
    super(mensagem);
    this.name = "ErroApi";
  }
}

function mensagemDoErro(status: number, problema?: Problema): string {
  if (status === 503) return "A Elpis não está disponível agora. Tente de novo em instantes.";
  if (status === 404) return "Não encontrei isso. Volte e escolha de novo.";
  if (status === 401) return "Sua sessão terminou. Entre de novo.";
  if (status === 403) return problema?.title ?? "Falta a sua autorização para isso.";
  if (status === 413) return "O arquivo é grande demais. Tente um extrato de um mês só.";
  if (status === 501) return "Isso ainda não está pronto no PANDORA.";
  if (status === 409 || status === 422) {
    return problema?.detail ?? problema?.title ?? "Não consegui entender o pedido. Confira e tente de novo.";
  }
  return "Algo deu errado do nosso lado. Tente de novo em instantes.";
}

async function pedir<T>(caminho: string, init: RequestInit = {}, sinal?: AbortSignal): Promise<T> {
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), TEMPO_MAXIMO_MS);
  const cancelar = () => controle.abort();
  sinal?.addEventListener("abort", cancelar, { once: true });
  const token = lerToken();
  try {
    let resposta: Response;
    try {
      resposta = await fetch(`${URL_API}${caminho}`, {
        ...init,
        headers: {
          // FormData monta o próprio Content-Type, com o boundary do multipart.
          ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...init.headers,
        },
        signal: controle.signal,
      });
    } catch (erro) {
      if (sinal?.aborted) throw erro; // a tela cancelou: não é falha de rede
      throw new ErroApi("Não consegui falar com o servidor. Confira a conexão e tente de novo.", null);
    }
    if (!resposta.ok) {
      const problema = await resposta.json().then(
        (corpo: Problema) => corpo,
        () => undefined,
      );
      // Token vencido ou revogado: esquece a sessão para a próxima tela pedir o login.
      if (resposta.status === 401 && token) apagarSessao();
      throw new ErroApi(mensagemDoErro(resposta.status, problema), resposta.status, problema);
    }
    if (resposta.status === 204) return undefined as T;
    return (await resposta.json()) as T;
  } finally {
    clearTimeout(limite);
    sinal?.removeEventListener("abort", cancelar);
  }
}

const post = (corpo: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(corpo) });

const consulta = (parametros: Record<string, string | number | undefined>) => {
  const busca = new URLSearchParams();
  for (const [nome, valor] of Object.entries(parametros)) if (valor !== undefined) busca.set(nome, String(valor));
  const texto = busca.toString();
  return texto ? `?${texto}` : "";
};

/* Elpis e trilha: abertas, sem conta. */

export const perguntarElpis = (pergunta: string, sinal?: AbortSignal) =>
  pedir<RespostaChat>("/chat", post({ pergunta }), sinal);

export const listarEtapas = (sinal?: AbortSignal) => pedir<EtapaTrilha[]>("/trilha", {}, sinal);

export const obterLicao = (licaoId: string, sinal?: AbortSignal) =>
  pedir<LicaoTrilha>(`/trilha/licoes/${encodeURIComponent(licaoId)}`, {}, sinal);

export const explicarResposta = (licaoId: string, perguntaIdx: number, opcao: number, sinal?: AbortSignal) =>
  pedir<RespostaChat>(
    `/trilha/licoes/${encodeURIComponent(licaoId)}/porque`,
    post({ pergunta_idx: perguntaIdx, opcao }),
    sinal,
  );

/* Conta e consentimento (#71). */

export const cadastrar = (email: string, senha: string) => pedir<Usuario>("/auth/cadastro", post({ email, senha }));

/** Entra e devolve o token. Quem chama guarda a sessão (`guardarSessao`). */
export async function entrar(email: string, senha: string): Promise<Sessao> {
  try {
    return await pedir<Sessao>("/auth/sessoes", post({ email, senha }));
  } catch (erro) {
    if (erro instanceof ErroApi && erro.status === 401) {
      throw new ErroApi("E-mail ou senha não conferem.", 401, erro.problema);
    }
    throw erro;
  }
}

export const sair = () => pedir<void>("/auth/sessoes/atual", { method: "DELETE" });

export const quemSou = (sinal?: AbortSignal) => pedir<Usuario>("/eu", {}, sinal);

export const listarConsentimentos = (sinal?: AbortSignal) => pedir<Consentimento[]>("/consentimentos", {}, sinal);

export const registrarConsentimento = (versaoTermo: string = VERSAO_TERMO) =>
  pedir<Consentimento>("/consentimentos", post({ finalidade: "diagnostico_financeiro", versao_termo: versaoTermo }));

/* Extrato, transações e Raio-X (#72). */

export function enviarExtrato(arquivo: File, sinal?: AbortSignal): Promise<Extrato> {
  const corpo = new FormData();
  corpo.append("arquivo", arquivo);
  return pedir<Extrato>("/extratos", { method: "POST", body: corpo }, sinal);
}

export const situacaoExtrato = (extratoId: string, sinal?: AbortSignal) =>
  pedir<Extrato>(`/extratos/${encodeURIComponent(extratoId)}`, {}, sinal);

export interface FiltroTransacoes {
  mes?: string;
  categoria?: Categoria;
  pagina?: number;
  porPagina?: number;
}

export const listarTransacoes = ({ mes, categoria, pagina, porPagina }: FiltroTransacoes = {}, sinal?: AbortSignal) =>
  pedir<PaginaTransacoes>(`/transacoes${consulta({ mes, categoria, pagina, por_pagina: porPagina })}`, {}, sinal);

export const corrigirCategoria = (transacaoId: string, categoria: Categoria) =>
  pedir<Transacao>(`/transacoes/${encodeURIComponent(transacaoId)}/categoria`, {
    method: "PATCH",
    body: JSON.stringify({ categoria }),
  });

export const obterRaioX = (mes: string, sinal?: AbortSignal) => pedir<RaioX>(`/raio-x${consulta({ mes })}`, {}, sinal);

export const obterScore = (sinal?: AbortSignal) => pedir<Score>("/score", {}, sinal);
