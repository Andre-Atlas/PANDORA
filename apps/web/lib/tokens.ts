import tokens from "@pandora/design-system/tokens.json";

export type Tema = "light" | "dark";

interface TokenCor {
  name: string;
  value: string | Record<Tema, string>;
}

const cores = tokens.color.tokens as unknown as TokenCor[];

/**
 * Lê uma cor de `tokens.json`, resolvendo referências como `{papiro}`.
 *
 * Use só onde CSS não chega (manifesto, meta theme-color, geração de ícones).
 * Na interface, use sempre as variáveis de `tokens.css`.
 */
export function corDoToken(nome: string, tema: Tema = "light"): string {
  const token = cores.find((t) => t.name === nome);
  if (!token) throw new Error(`Token de cor desconhecido: ${nome}`);

  const valor = typeof token.value === "string" ? token.value : token.value[tema];
  const referencia = /^\{(.+)\}$/.exec(valor);
  return referencia ? corDoToken(referencia[1], tema) : valor;
}
