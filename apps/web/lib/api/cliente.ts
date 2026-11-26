import type { EtapaTrilha, LicaoTrilha, Problema, RespostaChat } from "./tipos";

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
  if (status === 422) return problema?.detail ?? "Não consegui entender o pedido. Confira e tente de novo.";
  return "Algo deu errado do nosso lado. Tente de novo em instantes.";
}

async function pedir<T>(caminho: string, init: RequestInit = {}, sinal?: AbortSignal): Promise<T> {
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), TEMPO_MAXIMO_MS);
  const cancelar = () => controle.abort();
  sinal?.addEventListener("abort", cancelar, { once: true });
  try {
    let resposta: Response;
    try {
      resposta = await fetch(`${URL_API}${caminho}`, {
        ...init,
        headers: { "Content-Type": "application/json", ...init.headers },
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
      throw new ErroApi(mensagemDoErro(resposta.status, problema), resposta.status, problema);
    }
    return (await resposta.json()) as T;
  } finally {
    clearTimeout(limite);
    sinal?.removeEventListener("abort", cancelar);
  }
}

const post = (corpo: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(corpo) });

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
