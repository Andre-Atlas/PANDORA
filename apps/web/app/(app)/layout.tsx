import { PortaoAbertura } from "@/components/abertura/PortaoAbertura";
import { CascaApp } from "@/components/CascaApp";
import { PortaoConta } from "@/components/conta/PortaoConta";

/**
 * Telas do app: todas com a navegação das 5 abas. Quem chega direto aqui volta para a abertura.
 * Com os dados reais ligados, também é preciso ter entrado na conta.
 */
export default function LayoutApp({ children }: LayoutProps<"/">) {
  return (
    <PortaoAbertura>
      <PortaoConta>
        <CascaApp>{children}</CascaApp>
      </PortaoConta>
    </PortaoAbertura>
  );
}
