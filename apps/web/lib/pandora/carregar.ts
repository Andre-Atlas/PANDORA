import * as React from "react";
import type { Pandora } from "./tipos";

let carregamento: Promise<Pandora> | null = null;

/**
 * Carrega `bundle.js` do design system no navegador.
 *
 * O bundle foi feito para <script>: ele lê `window.React` ao rodar e publica
 * os componentes em `window.Pandora`. Por isso:
 * - só pode rodar no navegador (no servidor não há `window`);
 * - `window.React` precisa existir ANTES de o bundle rodar. Um `import`
 *   estático seria içado e rodaria primeiro, então usamos `import()`.
 */
export function carregarPandora(): Promise<Pandora> {
  if (typeof window === "undefined") {
    return Promise.reject(new Error("O design system só roda no navegador."));
  }
  if (window.Pandora) return Promise.resolve(window.Pandora);

  if (!carregamento) {
    window.React = React;
    carregamento = import("@pandora/design-system/components/bundle.js")
      .then(() => {
        if (!window.Pandora) throw new Error("bundle.js rodou, mas não publicou window.Pandora.");
        return window.Pandora;
      })
      .catch((erro: unknown) => {
        carregamento = null; // permite tentar de novo
        throw erro;
      });
  }
  return carregamento;
}
