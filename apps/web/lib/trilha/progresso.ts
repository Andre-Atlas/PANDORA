import type { EtapaTrilha } from "@/lib/api/tipos";

/** O progresso fica só no navegador: a trilha não pede login nem guarda nada no servidor. */
export const CHAVE_TRILHA = "pandora-trilha";

/** Emblemas que o `Brasao` do design system sabe desenhar. */
export const EMBLEMAS = ["templo", "balanca", "espiral", "oliveira", "elmo", "anfora"] as const;
export type Emblema = (typeof EMBLEMAS)[number];

export function emblemaOuPadrao(valor: string | undefined): Emblema {
  return EMBLEMAS.find((e) => e === valor) ?? "templo";
}

export type EstadoEtapa = "feito" | "atual" | "proximo";
export type EtapaComEstado = EtapaTrilha & { estado: EstadoEtapa };

export function lerConcluidas(): string[] {
  try {
    const valor: unknown = JSON.parse(localStorage.getItem(CHAVE_TRILHA) ?? "[]");
    return Array.isArray(valor) ? valor.filter((v): v is string => typeof v === "string") : [];
  } catch {
    return [];
  }
}

export function concluirLicao(licaoId: string): void {
  try {
    const atuais = lerConcluidas();
    if (!atuais.includes(licaoId)) localStorage.setItem(CHAVE_TRILHA, JSON.stringify([...atuais, licaoId]));
  } catch {
    // Sem armazenamento: o progresso vale até recarregar a página.
  }
}

/** Feitas ficam como `feito`; a primeira que falta é a `atual`; o resto é `proximo`. */
export function comEstado(etapas: EtapaTrilha[], concluidas: string[]): EtapaComEstado[] {
  const primeiraPendente = etapas.findIndex((e) => !concluidas.includes(e.licao_id));
  return etapas.map((e, i) => ({
    ...e,
    estado: concluidas.includes(e.licao_id) ? "feito" : i === primeiraPendente ? "atual" : "proximo",
  }));
}
