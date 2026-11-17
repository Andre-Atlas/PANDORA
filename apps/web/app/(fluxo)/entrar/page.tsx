import type { Metadata } from "next";
import { Entrar } from "@/components/conta/Entrar";

export const metadata: Metadata = { title: "Entrar" };

export default function PaginaEntrar() {
  return <Entrar />;
}
