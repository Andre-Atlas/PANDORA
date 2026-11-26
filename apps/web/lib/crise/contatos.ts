/**
 * Contatos do fluxo de crise (RF05).
 *
 * Cada número ou link foi conferido na fonte oficial indicada. Não adicione nem
 * troque um contato sem conferir de novo: um link errado aqui pode custar caro.
 * Contato com `href: null` não aparece na tela até alguém confirmar o endereço.
 */
export interface ContatoApoio {
  id: string;
  rotulo: string;
  /** Nome curto, para listas como "CVV e CAPS AD". */
  nome: string;
  href: string | null;
  icone: string;
  variante: "primario" | "secundario";
  /** Página oficial que confirma o contato. */
  fonte: string;
  /** Data da última conferência (AAAA-MM-DD). */
  conferidoEm: string;
  observacao?: string;
}

export const CONTATOS_APOIO: readonly ContatoApoio[] = [
  {
    id: "cvv",
    nome: "CVV",
    rotulo: "Ligar para o CVV: 188",
    href: "tel:188",
    icone: "telefone",
    variante: "primario",
    fonte: "https://cvv.org.br/",
    conferidoEm: "2026-11-05",
    observacao: "188 é gratuito e funciona 24h. O chat do CVV tem horário limitado, por isso não é o botão principal.",
  },
  {
    id: "caps",
    nome: "CAPS AD",
    rotulo: "Encontrar um CAPS AD",
    href: "https://www.gov.br/saude/pt-br/composicao/saes/desmad/raps/caps",
    icone: "lupa",
    variante: "secundario",
    fonte: "https://www.gov.br/saude/pt-br/composicao/saes/desmad/raps/caps",
    conferidoEm: "2026-11-05",
    observacao:
      "Não há buscador nacional oficial confirmado. A página do Ministério da Saúde explica que o CAPS atende sem consulta marcada e como achar o mais próximo (UBS ou Secretaria de Saúde).",
  },
  {
    id: "jogadores-anonimos",
    nome: "Jogadores Anônimos",
    rotulo: "Jogadores Anônimos",
    href: null,
    icone: "pessoas",
    variante: "secundario",
    fonte: "",
    conferidoEm: "2026-11-05",
    observacao:
      "Nenhuma fonte oficial confirmou o site. jogadoresanonimos.com.br responde, mas não deu para confirmar que é o JA Brasil.",
  },
];

/** Emergência com risco imediato. Fonte: página de CAPS do Ministério da Saúde. */
export const EMERGENCIA = {
  rotulo: "SAMU 192",
  href: "tel:192",
  fonte: "https://www.gov.br/saude/pt-br/composicao/saes/desmad/raps/caps",
  conferidoEm: "2026-11-05",
} as const;

export function contatosVisiveis(): ContatoApoio[] {
  return CONTATOS_APOIO.filter((c) => c.href !== null);
}

/** "CVV e CAPS AD", "CVV, CAPS AD e Jogadores Anônimos"… só com os contatos visíveis. */
export function resumoContatos(): string {
  const nomes = contatosVisiveis().map((c) => c.nome);
  return nomes.length <= 1 ? (nomes[0] ?? "") : `${nomes.slice(0, -1).join(", ")} e ${nomes.at(-1)}`;
}
