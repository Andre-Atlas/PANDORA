"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

/** Guardado por sessão: recarregar a página não joga a pessoa de volta nas metas. */
export const CHAVE_CRISE = "pandora-crise";

interface ValorCrise {
  ativa: boolean;
  abrirCrise: () => void;
  fecharCrise: () => void;
}

const ContextoCrise = createContext<ValorCrise | null>(null);

function lerCrise(): boolean {
  try {
    return sessionStorage.getItem(CHAVE_CRISE) === "1";
  } catch {
    return false;
  }
}

function salvarCrise(ativa: boolean) {
  try {
    if (ativa) sessionStorage.setItem(CHAVE_CRISE, "1");
    else sessionStorage.removeItem(CHAVE_CRISE);
  } catch {
    // Sem armazenamento: o modo vale até fechar a aba.
  }
}

/**
 * Estado do fluxo de crise para o app inteiro.
 *
 * Quem abre: o Guardião ("Precisa de apoio agora?") e, quando existir, o
 * classificador de crise do chat (#64, #80). Quem respeita: a casca, que
 * troca qualquer tela pela de crise, e toda meta ou aviso futuro (#87),
 * que deve checar `ativa` antes de aparecer.
 */
export function CriseProvider({ children }: { children: ReactNode }) {
  // Só renderiza no navegador (fica dentro do PandoraProvider), então dá para
  // ler o sessionStorage já no primeiro render.
  const [ativa, setAtiva] = useState(() => typeof window !== "undefined" && lerCrise());

  const abrirCrise = useCallback(() => {
    salvarCrise(true);
    setAtiva(true);
  }, []);
  const fecharCrise = useCallback(() => {
    salvarCrise(false);
    setAtiva(false);
  }, []);

  const valor = useMemo(() => ({ ativa, abrirCrise, fecharCrise }), [ativa, abrirCrise, fecharCrise]);
  return <ContextoCrise.Provider value={valor}>{children}</ContextoCrise.Provider>;
}

export function useCrise(): ValorCrise {
  const valor = useContext(ContextoCrise);
  if (!valor) throw new Error("useCrise precisa estar dentro de <CriseProvider>.");
  return valor;
}
