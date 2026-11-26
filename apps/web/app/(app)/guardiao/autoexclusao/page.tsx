import type { Metadata } from "next";
import { GuiaAutoexclusao } from "@/components/guardiao/GuiaAutoexclusao";

export const metadata: Metadata = { title: "Autoexclusão" };

export default function PaginaAutoexclusao() {
  return <GuiaAutoexclusao />;
}
