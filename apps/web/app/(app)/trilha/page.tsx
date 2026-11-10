import type { Metadata } from "next";
import { Trilha } from "@/components/telas/Trilha";

export const metadata: Metadata = { title: "Trilha" };

export default function PaginaTrilha() {
  return <Trilha />;
}
