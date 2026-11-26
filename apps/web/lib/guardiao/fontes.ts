/**
 * Fontes do guia de autoexclusão, conferidas no texto oficial.
 *
 * As regras de apostas mudaram em setembro de 2026 e ainda podem mudar: a
 * MP nº 1.394/2026 precisa ser votada pelo Congresso até `REVISAR_ATE`.
 * Depois dessa data, confira de novo cada fonte e o texto do guia, e atualize
 * `conferidoEm` e `REVISAR_ATE`. O teste de fontes falha para lembrar.
 */
export interface Fonte {
  /** Como a norma aparece na citação, ex.: "Resolução BCB nº 142/2021, art. 2º". */
  norma: string;
  href: string;
  rotuloLink: string;
  conferidoEm: string;
}

const CONFERIDO_EM = "2026-11-05";

/** Prazo de deliberação da MP no Congresso (página da MPV 1394/2026). */
export const REVISAR_ATE = "2026-11-23";

export const FONTES = {
  proibicao: {
    norma: "Medida Provisória nº 1.394/2026, art. 1º",
    href: "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/mpv/mpv1394.htm",
    rotuloLink: "Ler no Planalto",
    conferidoEm: CONFERIDO_EM,
  },
  pagamentosVedados: {
    norma: "Medida Provisória nº 1.394/2026, art. 14",
    href: "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/mpv/mpv1394.htm",
    rotuloLink: "Ler no Planalto",
    conferidoEm: CONFERIDO_EM,
  },
  pixBloqueado: {
    norma: "Resolução BCB nº 597/2026 (Pix). TED e boleto: Resoluções BCB nº 595 e 596/2026",
    href: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=597",
    rotuloLink: "Ler no Banco Central",
    conferidoEm: CONFERIDO_EM,
  },
  limiteNoturno: {
    norma: "Resolução BCB nº 142/2021, art. 2º",
    href: "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=142",
    rotuloLink: "Ler no Banco Central",
    conferidoEm: CONFERIDO_EM,
  },
  denuncia: {
    norma: "Ministério da Fazenda: como denunciar irregularidades com bets",
    href: "https://agenciagov.ebc.com.br/noticias/202610/saiba-como-denunciar-irregularidades-relacionadas-a-bets-pelo-fala.br",
    rotuloLink: "Ler na Agência Gov",
    conferidoEm: CONFERIDO_EM,
  },
} satisfies Record<string, Fonte>;

/** Links de ação (não são normas, mas também foram conferidos). */
export const LINKS = {
  betblocker: "https://betblocker.org/br/",
  falabr: "https://www.gov.br/falabr",
} as const;
