"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { usePandora } from "@/lib/pandora/PandoraProvider";

export const ROTA_AUTOEXCLUSAO = "/guardiao/autoexclusao";

/**
 * Entrada do guia no Guardião. A galeria diz "Guia passo a passo para sites
 * .bet.br", mas esses sites foram proibidos (MP nº 1.394/2026): o texto
 * descreve o que o guia faz agora.
 */
export function LinkGuiaAutoexclusao() {
  const { LinkCartao } = usePandora();
  const router = useRouter();

  useEffect(() => {
    router.prefetch(ROTA_AUTOEXCLUSAO);
  }, [router]);

  return (
    <LinkCartao
      icone="pausa"
      titulo="Autoexclusão das apostas"
      descricao="Passo a passo para bloquear sites e pagamentos"
      onClick={() => router.push(ROTA_AUTOEXCLUSAO)}
    />
  );
}
