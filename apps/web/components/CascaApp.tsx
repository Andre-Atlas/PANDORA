"use client";

import type { ReactNode } from "react";
import { useCrise } from "./crise/CriseProvider";
import { TelaCrise } from "./crise/TelaCrise";
import { NavegacaoInferior } from "./NavegacaoInferior";

interface CascaAppProps {
  children: ReactNode;
  /**
   * `app`: telas do app, com a navegação (embaixo no celular, trilho lateral a partir de 1024px).
   * `abertura`: a página de entrada, sem navegação.
   * `fluxo`: passos de tela cheia (perguntas, lição, veredito), sem navegação.
   */
  variante?: "app" | "abertura" | "fluxo";
}

/**
 * Estrutura de toda tela, na moldura fluida do design system:
 * `.pd-fluido > .pd-tela > .pd-tela-interior > (conteúdo, navegação)`.
 *
 * A `.pd-tela` mede a própria largura (container `pd-tela`), e o design
 * system decide a partir dela: navegação embaixo até 1023px, trilho lateral
 * a partir de 1024px, coluna de 720px no médio e duas colunas no expandido.
 * O app não redefine nenhuma dessas faixas.
 *
 * O conteúdo vem antes da navegação no DOM, então quem usa leitor de tela
 * ou teclado chega primeiro ao que importa. O trilho só muda a posição visual.
 *
 * Em crise, a tela de apoio substitui qualquer rota, inclusive a abertura, e a
 * navegação some: nada de metas, avisos ou cobranças até a pessoa escolher voltar.
 */
export function CascaApp({ children, variante = "app" }: CascaAppProps) {
  const { ativa } = useCrise();
  const comNavegacao = variante === "app" && !ativa;

  return (
    <div className="pd-fluido">
      <div className={`pd-tela app-tela app-tela-${variante}`} data-nav={comNavegacao ? "sim" : undefined}>
        <div className="pd-tela-interior">
          <main className="pd-tela-conteudo app-conteudo">{ativa ? <TelaCrise /> : children}</main>
          {comNavegacao ? <NavegacaoInferior /> : null}
        </div>
      </div>
    </div>
  );
}
