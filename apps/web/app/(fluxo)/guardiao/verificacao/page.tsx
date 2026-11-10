import type { Metadata } from "next";
import { Verificacao } from "@/components/telas/Verificacao";

export const metadata: Metadata = { title: "Verificação do boleto" };

export default function PaginaVerificacao() {
  return <Verificacao />;
}
