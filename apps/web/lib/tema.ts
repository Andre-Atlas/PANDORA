import { corDoToken, type Tema } from "./tokens";

export type { Tema };
export type PreferenciaTema = "sistema" | "claro" | "escuro";

export const CHAVE_TEMA = "pandora-tema";
export const CONSULTA_ESCURO = "(prefers-color-scheme: dark)";

export const ROTULOS_PREFERENCIA: Record<PreferenciaTema, string> = {
  sistema: "Sistema",
  claro: "Claro",
  escuro: "Escuro",
};

export function ehPreferencia(valor: unknown): valor is PreferenciaTema {
  return valor === "sistema" || valor === "claro" || valor === "escuro";
}

export function resolverTema(preferencia: PreferenciaTema, sistemaEscuro: boolean): Tema {
  if (preferencia === "claro") return "light";
  if (preferencia === "escuro") return "dark";
  return sistemaEscuro ? "dark" : "light";
}

export function lerPreferencia(): PreferenciaTema {
  try {
    const salva = localStorage.getItem(CHAVE_TEMA);
    return ehPreferencia(salva) ? salva : "sistema";
  } catch {
    return "sistema";
  }
}

export function salvarPreferencia(preferencia: PreferenciaTema) {
  try {
    if (preferencia === "sistema") localStorage.removeItem(CHAVE_TEMA);
    else localStorage.setItem(CHAVE_TEMA, preferencia);
  } catch {
    // Sem armazenamento (modo privado): o tema vale só para esta visita.
  }
}

/** Cor da barra do sistema: a do cabeçalho do mito, que no escuro deixa de ser laranja. */
export const COR_DA_BARRA: Record<Tema, string> = {
  light: corDoToken("mito-fundo", "light"),
  dark: corDoToken("mito-fundo", "dark"),
};

export function aplicarTema(tema: Tema) {
  document.documentElement.dataset.theme = tema;
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", COR_DA_BARRA[tema]);
}

/**
 * Roda no <head>, antes da primeira pintura, para a tela não piscar no tema
 * errado. Repete `resolverTema` em JavaScript puro, sem depender do bundle.
 */
export const scriptTemaInicial = `(function(){try{var p=localStorage.getItem(${JSON.stringify(
  CHAVE_TEMA,
)});var e=p==="escuro"||(p!=="claro"&&window.matchMedia(${JSON.stringify(
  CONSULTA_ESCURO,
)}).matches);document.documentElement.dataset.theme=e?"dark":"light"}catch(_){}})()`;
