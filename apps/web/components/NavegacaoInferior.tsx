"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ABAS, abaDaRota, rotaDaAba } from "@/lib/navegacao";
import { usePandora } from "@/lib/pandora/PandoraProvider";

/** Guarda se a pessoa recolheu a navegação, para ela não reabrir a cada tela. */
export const CHAVE_NAV_RECOLHIDA = "pandora-nav-recolhida";

function lerRecolhida(): boolean {
  try {
    return localStorage.getItem(CHAVE_NAV_RECOLHIDA) === "1";
  } catch {
    return false;
  }
}

function salvarRecolhida(recolhida: boolean) {
  try {
    if (recolhida) localStorage.setItem(CHAVE_NAV_RECOLHIDA, "1");
    else localStorage.removeItem(CHAVE_NAV_RECOLHIDA);
  } catch {
    // Sem armazenamento: vale até sair da tela.
  }
}

/**
 * A `NavBase` do design system ligada às rotas do app. Embaixo no celular,
 * trilho lateral a partir de 1024px. É retrátil: o botão de chave grega
 * recolhe para a faixa com Elpis (embaixo) ou para só os ícones (no trilho).
 */
export function NavegacaoInferior() {
  const { NavBase } = usePandora();
  const caminho = usePathname();
  const router = useRouter();
  // Só renderiza no navegador (fica dentro do PandoraProvider): pode ler o localStorage já aqui.
  const [recolhida, setRecolhida] = useState(lerRecolhida);

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
      recolhida={recolhida}
      onAlternar={(nova) => {
        setRecolhida(nova);
        salvarRecolhida(nova);
      }}
    />
  );
}
