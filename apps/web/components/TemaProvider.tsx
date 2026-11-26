"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  CONSULTA_ESCURO,
  aplicarTema,
  lerPreferencia,
  resolverTema,
  salvarPreferencia,
  type PreferenciaTema,
} from "@/lib/tema";

interface ValorTema {
  preferencia: PreferenciaTema;
  definirPreferencia: (preferencia: PreferenciaTema) => void;
}

const ContextoTema = createContext<ValorTema | null>(null);

/**
 * Guarda a preferência de tema e mantém `data-theme` no <html> em dia.
 * O primeiro valor já foi aplicado por `scriptTemaInicial`, antes da pintura.
 */
export function TemaProvider({ children }: { children: ReactNode }) {
  const [preferencia, setPreferencia] = useState<PreferenciaTema>(() =>
    typeof window === "undefined" ? "sistema" : lerPreferencia(),
  );

  useEffect(() => {
    const consulta = window.matchMedia(CONSULTA_ESCURO);
    const atualizar = () => aplicarTema(resolverTema(preferencia, consulta.matches));
    atualizar();
    if (preferencia !== "sistema") return;
    consulta.addEventListener("change", atualizar);
    return () => consulta.removeEventListener("change", atualizar);
  }, [preferencia]);

  const definirPreferencia = useCallback((nova: PreferenciaTema) => {
    salvarPreferencia(nova);
    setPreferencia(nova);
  }, []);

  const valor = useMemo(() => ({ preferencia, definirPreferencia }), [preferencia, definirPreferencia]);
  return <ContextoTema.Provider value={valor}>{children}</ContextoTema.Provider>;
}

export function useTema(): ValorTema {
  const valor = useContext(ContextoTema);
  if (!valor) throw new Error("useTema precisa estar dentro de <TemaProvider>.");
  return valor;
}
