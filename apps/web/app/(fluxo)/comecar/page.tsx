import type { Metadata } from "next";
import { Perguntas } from "@/components/abertura/Perguntas";

export const metadata: Metadata = { title: "Começar" };

export default function PaginaPerguntas() {
  return <Perguntas />;
}
