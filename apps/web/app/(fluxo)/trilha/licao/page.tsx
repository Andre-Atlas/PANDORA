import type { Metadata } from "next";
import { Licao } from "@/components/telas/Licao";

export const metadata: Metadata = { title: "Lição: rotativo" };

export default function PaginaLicao() {
  return <Licao />;
}
