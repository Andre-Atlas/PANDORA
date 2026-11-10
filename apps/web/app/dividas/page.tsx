import type { Metadata } from "next";
import { TelaProvisoria } from "@/components/TelaProvisoria";

export const metadata: Metadata = { title: "Dívidas" };

export default function PaginaDividas() {
  return <TelaProvisoria titulo="Dívidas" issue={71} />;
}
