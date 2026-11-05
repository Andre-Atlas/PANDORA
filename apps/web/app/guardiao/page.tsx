import type { Metadata } from "next";
import { TelaProvisoria } from "@/components/TelaProvisoria";

export const metadata: Metadata = { title: "Guardião" };

export default function PaginaGuardiao() {
  return <TelaProvisoria titulo="Guardião" issue={81} />;
}
