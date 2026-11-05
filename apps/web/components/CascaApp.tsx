import type { ReactNode } from "react";
import { NavegacaoInferior } from "./NavegacaoInferior";

/**
 * Estrutura de toda tela: conteúdo e, embaixo, a navegação.
 *
 * Usa a classe `.pd-tela` do design system para herdar fonte, cor e foco,
 * mas ocupa a tela inteira em vez da moldura de celular da galeria.
 * O conteúdo vem antes da navegação no DOM, então quem usa leitor de tela
 * ou teclado chega primeiro ao que importa.
 */
export function CascaApp({ children }: { children: ReactNode }) {
  return (
    <div className="pd-tela app-tela">
      <main className="app-conteudo">{children}</main>
      <NavegacaoInferior />
    </div>
  );
}
