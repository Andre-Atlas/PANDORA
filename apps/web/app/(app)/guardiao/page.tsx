import type { Metadata } from "next";
import { Guardiao } from "@/components/telas/Guardiao";

export const metadata: Metadata = { title: "Guardião" };

export default function PaginaGuardiao() {
  return <Guardiao />;
}
