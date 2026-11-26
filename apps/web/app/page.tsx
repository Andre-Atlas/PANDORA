import type { Metadata } from "next";
import { Abertura } from "@/components/abertura/Abertura";
import { CascaApp } from "@/components/CascaApp";

export const metadata: Metadata = {
  // Sem o modelo "%s · PANDORA": a página de entrada é a própria marca.
  title: { absolute: "PANDORA · Copiloto financeiro" },
};

/** Página de entrada (tela 1a da galeria). Fica fora do grupo (app), então não tem navegação. */
export default function PaginaAbertura() {
  return (
    <CascaApp variante="abertura">
      <Abertura />
    </CascaApp>
  );
}
