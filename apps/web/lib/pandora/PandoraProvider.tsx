"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { carregarPandora } from "./carregar";
import type { Pandora } from "./tipos";

const ContextoPandora = createContext<Pandora | null>(null);

type Estado = { fase: "carregando" } | { fase: "pronto"; ds: Pandora } | { fase: "erro" };

/**
 * Carrega o design system e só então mostra o app. Até lá (e no HTML do
 * servidor) aparece uma tela simples, já com as cores e fontes dos tokens.
 */
export function PandoraProvider({ children }: { children: ReactNode }) {
  const [estado, setEstado] = useState<Estado>({ fase: "carregando" });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    carregarPandora().then(
      (ds) => ativo && setEstado({ fase: "pronto", ds }),
      (erro: unknown) => {
        console.error("Falha ao carregar o design system", erro);
        if (ativo) setEstado({ fase: "erro" });
      },
    );
    return () => {
      ativo = false;
    };
  }, [tentativa]);

  if (estado.fase === "pronto") {
    return <ContextoPandora.Provider value={estado.ds}>{children}</ContextoPandora.Provider>;
  }

  return (
    <div className="pd-tela app-tela app-carregando">
      {estado.fase === "carregando" ? (
        <p role="status">Carregando o PANDORA</p>
      ) : (
        <div role="alert" className="app-carregando-erro">
          <p>A tela não carregou. Confira a conexão e tente de novo.</p>
          <button
            type="button"
            className="pd-botao pd-botao-primario"
            onClick={() => {
              setEstado({ fase: "carregando" });
              setTentativa((n) => n + 1);
            }}
          >
            Tentar de novo
          </button>
        </div>
      )}
    </div>
  );
}

/** Os componentes do design system. Só funciona dentro de <PandoraProvider>. */
export function usePandora(): Pandora {
  const ds = useContext(ContextoPandora);
  if (!ds) throw new Error("usePandora precisa estar dentro de <PandoraProvider>.");
  return ds;
}
