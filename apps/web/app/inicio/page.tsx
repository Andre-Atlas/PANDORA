import type { Metadata } from "next";
import { SeletorTema } from "@/components/SeletorTema";
import { TelaProvisoria } from "@/components/TelaProvisoria";

export const metadata: Metadata = { title: "Início" };

export default function PaginaInicio() {
  return (
    <TelaProvisoria titulo="Início" issue={71}>
      {/* Provisório: o seletor de tema mora aqui até existir uma tela de ajustes. */}
      <SeletorTema />
    </TelaProvisoria>
  );
}
