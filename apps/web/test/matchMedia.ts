import { vi } from "vitest";

type Ouvinte = (evento: { matches: boolean }) => void;

/**
 * O jsdom não implementa matchMedia. Simula `prefers-color-scheme` e devolve
 * uma função que troca o tema do sistema e avisa quem está ouvindo.
 */
export function simularMatchMedia(sistemaEscuro = false) {
  let escuro = sistemaEscuro;
  const ouvintes = new Set<Ouvinte>();

  window.matchMedia = vi.fn((query: string) => ({
    get matches() {
      return query.includes("dark") ? escuro : false;
    },
    media: query,
    onchange: null,
    addEventListener: (_tipo: string, ouvinte: Ouvinte) => ouvintes.add(ouvinte),
    removeEventListener: (_tipo: string, ouvinte: Ouvinte) => ouvintes.delete(ouvinte),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })) as unknown as typeof window.matchMedia;

  return (novoEscuro: boolean) => {
    escuro = novoEscuro;
    ouvintes.forEach((ouvinte) => ouvinte({ matches: novoEscuro }));
  };
}
