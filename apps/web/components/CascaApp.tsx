"use client";

import type { ReactNode } from "react";
import { useCrise } from "./crise/CriseProvider";
import { TelaCrise } from "./crise/TelaCrise";
import { NavegacaoInferior } from "./NavegacaoInferior";

/**
 * Estrutura de toda tela: conteúdo e, embaixo, a navegação.
 *
 * Usa a classe `.pd-tela` do design system para herdar fonte, cor e foco,
 * mas ocupa a tela inteira em vez da moldura de celular da galeria.
 * O conteúdo vem antes da navegação no DOM, então quem usa leitor de tela
 * ou teclado chega primeiro ao que importa.
 *
 * Em crise, a tela de apoio substitui qualquer rota e a navegação some:
 * nada de metas, avisos ou cobranças até a pessoa escolher voltar.
 */
export function CascaApp({ children }: { children: ReactNode }) {
  const { ativa } = useCrise();

  return (
    <div className="pd-tela app-tela">
      <main className="app-conteudo">{ativa ? <TelaCrise /> : children}</main>
      {ativa ? null : <NavegacaoInferior />}
    </div>
  );
}
