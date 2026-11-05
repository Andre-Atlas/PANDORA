"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { ABAS, abaDaRota, rotaDaAba } from "@/lib/navegacao";
import { usePandora } from "@/lib/pandora/PandoraProvider";

/** A `NavBase` do design system ligada às rotas do app. */
export function NavegacaoInferior() {
  const { NavBase } = usePandora();
  const caminho = usePathname();
  const router = useRouter();

  // A NavBase usa <button>, não <Link>, então o prefetch é feito à mão.
  useEffect(() => {
    ABAS.forEach((aba) => router.prefetch(aba.rota));
  }, [router]);

  return (
    <NavBase
      ativo={abaDaRota(caminho)}
      onNavegar={(id) => {
        const rota = rotaDaAba(id);
        if (rota) router.push(rota);
      }}
    />
  );
}
