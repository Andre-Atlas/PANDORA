import type { Metadata } from "next";
import { Elpis } from "@/components/telas/Elpis";

export const metadata: Metadata = { title: "Elpis" };

export default function PaginaElpis() {
  return <Elpis />;
}
