"use client";

import type { ReactNode } from "react";
import { usePandora } from "@/lib/pandora/PandoraProvider";

interface TelaProvisoriaProps {
  titulo: string;
  subtitulo?: string;
  /** Issue que vai implementar a tela de verdade. */
  issue: number;
  children?: ReactNode;
}

/** Ocupa a rota até a tela real chegar, para a navegação já funcionar. */
export function TelaProvisoria({ titulo, subtitulo, issue, children }: TelaProvisoriaProps) {
  const { CabecalhoMito, Cartao } = usePandora();

  return (
    <>
      <CabecalhoMito titulo={titulo} subtitulo={subtitulo} />
      <div className="pd-corpo">
        <Cartao tom="apoio" sobre="Em construção" titulo={`Esta tela chega na issue #${issue}`}>
          <p>Por enquanto ela existe para a navegação funcionar.</p>
        </Cartao>
        {children}
      </div>
    </>
  );
}
