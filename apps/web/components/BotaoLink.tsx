"use client";

import type { ReactNode } from "react";
import { usePandora } from "@/lib/pandora/PandoraProvider";

interface BotaoLinkProps {
  href: string;
  icone?: string;
  variante?: "primario" | "secundario" | "fantasma";
  children: ReactNode;
}

/**
 * Link com a aparência do `Botao`. O `Botao` do design system é sempre
 * <button> e não aceita href, mas ligar e abrir página são links.
 * Páginas de fora abrem em outra aba.
 */
export function BotaoLink({ href, icone, variante = "secundario", children }: BotaoLinkProps) {
  const { Icone } = usePandora();
  const externo = /^https?:\/\//.test(href);
  return (
    <a
      href={href}
      className={`pd-botao pd-botao-${variante} pd-botao-bloco`}
      {...(externo ? { target: "_blank", rel: "noopener noreferrer" } : {})}
    >
      {icone ? <Icone nome={icone} tamanho={22} /> : null}
      {children}
    </a>
  );
}
