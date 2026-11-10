"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

const MENSAGEM_PADRAO = "Demonstração: esta ação ainda não existe no protótipo.";

const ContextoAviso = createContext<(mensagem?: string) => void>(() => {});

/**
 * Aviso curto para botões de ações que ainda não existem (gerar PDF, copiar
 * dados do Pix, avisar alguém). Assim o botão responde ao toque e deixa claro
 * que é demonstração, em vez de não fazer nada.
 */
export function AvisoDemoProvider({ children }: { children: ReactNode }) {
  const [mensagem, setMensagem] = useState<string | null>(null);

  useEffect(() => {
    if (!mensagem) return;
    const tempo = setTimeout(() => setMensagem(null), 4000);
    return () => clearTimeout(tempo);
  }, [mensagem]);

  const avisar = useCallback((texto?: string) => setMensagem(texto ?? MENSAGEM_PADRAO), []);

  return (
    <ContextoAviso.Provider value={avisar}>
      {children}
      {/* A região existe desde o início para o leitor de tela anunciar a mensagem. */}
      <div role="status" aria-live="polite" className="app-aviso-demo">
        {mensagem ? <p className="app-aviso-demo-texto">{mensagem}</p> : null}
      </div>
    </ContextoAviso.Provider>
  );
}

export function useAvisoDemo(): (mensagem?: string) => void {
  return useContext(ContextoAviso);
}
