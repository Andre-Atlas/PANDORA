import { PortaoAbertura } from "@/components/abertura/PortaoAbertura";
import { CascaApp } from "@/components/CascaApp";

/** Passos de tela cheia, sem a navegação das abas (perguntas, lição, veredito do boleto). */
export default function LayoutFluxo({ children }: LayoutProps<"/">) {
  return (
    <PortaoAbertura>
      <CascaApp variante="fluxo">{children}</CascaApp>
    </PortaoAbertura>
  );
}
