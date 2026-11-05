/** As 5 abas da `NavBase`, na ordem do design system. Metas abre a partir do Início. */
export const ABAS = [
  { id: "inicio", rotulo: "Início", rota: "/inicio" },
  { id: "dividas", rotulo: "Dívidas", rota: "/dividas" },
  { id: "elpis", rotulo: "Elpis", rota: "/elpis" },
  { id: "trilha", rotulo: "Trilha", rota: "/trilha" },
  { id: "guardiao", rotulo: "Guardião", rota: "/guardiao" },
] as const;

export type IdAba = (typeof ABAS)[number]["id"];

/** Aba ativa para uma rota. Subpáginas (ex.: /inicio/metas) mantêm a aba do pai. */
export function abaDaRota(caminho: string | null): IdAba | undefined {
  if (!caminho) return undefined;
  return ABAS.find((aba) => caminho === aba.rota || caminho.startsWith(`${aba.rota}/`))?.id;
}

export function rotaDaAba(id: string): string | undefined {
  return ABAS.find((aba) => aba.id === id)?.rota;
}
