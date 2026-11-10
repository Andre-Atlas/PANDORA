import type { Metadata } from "next";
import { Metas } from "@/components/telas/Metas";

export const metadata: Metadata = { title: "Metas e previsão" };

export default function PaginaMetas() {
  return <Metas />;
}
