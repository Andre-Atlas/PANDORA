import type { Metadata } from "next";
import { Suspense } from "react";
import { Licao } from "@/components/telas/Licao";

export const metadata: Metadata = { title: "Lição da trilha" };

export default function PaginaLicao() {
  // `useSearchParams` na tela da lição pede uma fronteira de Suspense (docs do Next 16).
  return (
    <Suspense fallback={<p className="pd-apoio app-consultando" role="status">Carregando a lição…</p>}>
      <Licao />
    </Suspense>
  );
}
