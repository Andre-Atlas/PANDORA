"use client";

import { resumoContatos } from "@/lib/crise/contatos";
import { usePandora } from "@/lib/pandora/PandoraProvider";
import { useCrise } from "./CriseProvider";

/** Entrada para o fluxo de crise, como no Guardião da galeria. */
export function LinkApoio() {
  const { LinkCartao } = usePandora();
  const { abrirCrise } = useCrise();
  return (
    <LinkCartao
      icone="coracao"
      titulo="Precisa de apoio agora?"
      descricao={resumoContatos()}
      onClick={abrirCrise}
    />
  );
}
