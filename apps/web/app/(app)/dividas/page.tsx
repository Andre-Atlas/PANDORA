import type { Metadata } from "next";
import { Dividas } from "@/components/telas/Dividas";

export const metadata: Metadata = { title: "Dívidas" };

export default function PaginaDividas() {
  return <Dividas />;
}
