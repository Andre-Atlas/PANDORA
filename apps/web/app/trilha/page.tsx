import type { Metadata } from "next";
import { TelaProvisoria } from "@/components/TelaProvisoria";

export const metadata: Metadata = { title: "Trilha" };

export default function PaginaTrilha() {
  return <TelaProvisoria titulo="Trilha" issue={81} />;
}
