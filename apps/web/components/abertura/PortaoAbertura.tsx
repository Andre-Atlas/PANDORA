"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { aberturaVista } from "@/lib/abertura/portao";

/**
 * Manda para a abertura quem abre o site direto numa tela do app.
 * Só roda no navegador (fica dentro do PandoraProvider), então dá para ler
 * o `sessionStorage` já no primeiro render, sem piscar a tela de destino.
 */
export function PortaoAbertura({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [liberado] = useState(aberturaVista);

  useEffect(() => {
    if (!liberado) router.replace("/");
  }, [liberado, router]);

  return liberado ? children : null;
}
