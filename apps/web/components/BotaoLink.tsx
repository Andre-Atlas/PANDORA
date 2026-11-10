"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { usePandora } from "@/lib/pandora/PandoraProvider";

interface BotaoLinkProps {
  href: string;
  icone?: string;
  variante?: "primario" | "secundario" | "fantasma" | "claro";
  /** Seta no fim, como o `seta` do `Botao`: indica que a pessoa segue em frente. */
  seta?: boolean;
  children: ReactNode;
}

/**
 * Link com a aparência do `Botao`. O `Botao` do design system é sempre
 * <button> e não aceita href, mas ligar e abrir página são links.
 * Rotas do app usam o `Link` do Next. Páginas de fora abrem em outra aba.
 */
export function BotaoLink({ href, icone, variante = "secundario", seta = false, children }: BotaoLinkProps) {
  const { Icone } = usePandora();
  const conteudo = (
    <>
      {icone ? <Icone nome={icone} tamanho={22} /> : null}
      {children}
      {seta ? <Icone nome="seta" tamanho={22} /> : null}
    </>
  );
  const className = `pd-botao pd-botao-${variante} pd-botao-bloco`;

  if (href.startsWith("/")) {
    return (
      <Link href={href} className={className}>
        {conteudo}
      </Link>
    );
  }

  const externo = /^https?:\/\//.test(href);
  return (
    <a href={href} className={className} {...(externo ? { target: "_blank", rel: "noopener noreferrer" } : {})}>
      {conteudo}
    </a>
  );
}
