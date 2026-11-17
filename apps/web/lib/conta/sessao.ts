/**
 * Sessão da API, guardada neste navegador.
 *
 * O token dura o que a API definir (`expira_em`, 7 dias por padrão), então
 * fica no `localStorage`: fechar a aba não desconecta. Depois de vencido,
 * `lerToken()` o descarta. Sem armazenamento disponível, não há sessão.
 */
export const CHAVE_SESSAO = "pandora-sessao";

/** Aceite dado nas perguntas da Abertura, à espera do login para ser registrado na API. */
export const CHAVE_CONSENTIMENTO_PENDENTE = "pandora-consentimento-pendente";

/** Versão do termo que a pessoa aceita em "O combinado". Mude quando o texto mudar. */
export const VERSAO_TERMO = "2026-11";

interface SessaoGuardada {
  token: string;
  expira_em: string;
}

export function guardarSessao(sessao: SessaoGuardada): void {
  try {
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify({ token: sessao.token, expira_em: sessao.expira_em }));
  } catch {
    // Sem armazenamento: a pessoa entra de novo na próxima tela.
  }
}

export function lerToken(agora: Date = new Date()): string | null {
  try {
    const bruto = localStorage.getItem(CHAVE_SESSAO);
    if (!bruto) return null;
    const sessao = JSON.parse(bruto) as Partial<SessaoGuardada>;
    if (!sessao.token || !sessao.expira_em || new Date(sessao.expira_em) <= agora) {
      apagarSessao();
      return null;
    }
    return sessao.token;
  } catch {
    return null;
  }
}

export function apagarSessao(): void {
  try {
    localStorage.removeItem(CHAVE_SESSAO);
  } catch {
    // Nada guardado.
  }
}

export function marcarConsentimentoPendente(): void {
  try {
    sessionStorage.setItem(CHAVE_CONSENTIMENTO_PENDENTE, "1");
  } catch {
    // Sem armazenamento: as perguntas pedem o aceite de novo depois do login.
  }
}

export function consentimentoPendente(): boolean {
  try {
    return sessionStorage.getItem(CHAVE_CONSENTIMENTO_PENDENTE) === "1";
  } catch {
    return false;
  }
}

export function limparConsentimentoPendente(): void {
  try {
    sessionStorage.removeItem(CHAVE_CONSENTIMENTO_PENDENTE);
  } catch {
    // Nada guardado.
  }
}
