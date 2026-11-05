import type { Metadata } from "next";
import { LinkApoio } from "@/components/crise/LinkApoio";
import { TelaProvisoria } from "@/components/TelaProvisoria";

export const metadata: Metadata = { title: "Guardião" };

export default function PaginaGuardiao() {
  return (
    <TelaProvisoria titulo="Guardião" subtitulo="Confere antes de você decidir." issue={81}>
      <LinkApoio />
    </TelaProvisoria>
  );
}
