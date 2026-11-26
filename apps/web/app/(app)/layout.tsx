import { PortaoAbertura } from "@/components/abertura/PortaoAbertura";
import { CascaApp } from "@/components/CascaApp";

/** Telas do app: todas com a navegação das 5 abas. Quem chega direto aqui volta para a abertura. */
export default function LayoutApp({ children }: LayoutProps<"/">) {
  return (
    <PortaoAbertura>
      <CascaApp>{children}</CascaApp>
    </PortaoAbertura>
  );
}
