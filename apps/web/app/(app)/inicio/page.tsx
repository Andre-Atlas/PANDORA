import type { Metadata } from "next";
import { Inicio } from "@/components/telas/Inicio";

export const metadata: Metadata = { title: "Início" };

export default function PaginaInicio() {
  return <Inicio />;
}
