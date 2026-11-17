"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { dadosReais } from "@/lib/conta/modo";
import { lerToken } from "@/lib/conta/sessao";

/** Tela de login e cadastro (só existe com os dados reais ligados). */
export const ROTA_ENTRAR = "/entrar";

/**
 * Com os dados reais ligados, as telas do app pedem uma sessão: quem não
 * tem vai para /entrar. Com eles desligados (o padrão), deixa tudo passar,
 * para testar o app sem conta.
 */
export function PortaoConta({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [liberado] = useState(() => !dadosReais() || lerToken() !== null);

  useEffect(() => {
    if (!liberado) router.replace(ROTA_ENTRAR);
  }, [liberado, router]);

  return liberado ? children : null;
}
