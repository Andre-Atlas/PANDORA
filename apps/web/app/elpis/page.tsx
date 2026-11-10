import type { Metadata } from "next";
import { TelaProvisoria } from "@/components/TelaProvisoria";

export const metadata: Metadata = { title: "Elpis" };

export default function PaginaElpis() {
  return <TelaProvisoria titulo="Elpis" issue={80} />;
}
