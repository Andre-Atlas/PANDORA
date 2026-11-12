import type { Citacao } from "./tipos";

const MAX_TRECHO = 220;

/** Só segue links web: o endereço vem da API e nunca deve virar `javascript:`. */
export function linkSeguro(url: string): string {
  return /^https?:\/\//i.test(url) ? url : "#";
}

export function rotuloDoLink(url: string): string {
  try {
    const host = new URL(url).hostname;
    if (host.endsWith("planalto.gov.br")) return "Ler no Planalto";
    if (host.endsWith("bcb.gov.br")) return "Ler no Banco Central";
    if (host.endsWith("cnj.jus.br")) return "Ler no CNJ";
    if (host.endsWith("cvm.gov.br") || host.endsWith("investidor.gov.br")) return "Ler na CVM";
  } catch {
    // endereço inválido: cai no rótulo genérico
  }
  return "Ler a fonte";
}

export function rotuloNorma(c: Pick<Citacao, "norma" | "artigo">): string {
  return c.artigo ? `${c.norma}, ${c.artigo}` : c.norma;
}

/** Primeiros caracteres do trecho, sem cortar no meio de uma palavra. */
export function resumoDoTrecho(trecho: string): string {
  const limpo = trecho.replace(/\s+/g, " ").trim();
  if (limpo.length <= MAX_TRECHO) return limpo;
  const corte = limpo.slice(0, MAX_TRECHO);
  return `${corte.slice(0, Math.max(corte.lastIndexOf(" "), 1))}…`;
}

/** Números citados no texto como [n], sem repetir e na ordem em que aparecem. */
export function numerosCitados(texto: string): number[] {
  const vistos: number[] = [];
  for (const m of texto.matchAll(/\[(\d+)\]/g)) {
    const n = Number(m[1]);
    if (!vistos.includes(n)) vistos.push(n);
  }
  return vistos;
}
