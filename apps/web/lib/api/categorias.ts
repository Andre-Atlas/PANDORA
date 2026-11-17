import type { Categoria } from "./tipos";

/**
 * Nome de cada categoria do contrato, como a pessoa lê na tela. O `Record`
 * obriga a cobrir todas: se a API ganhar uma categoria nova, o typecheck falha aqui.
 */
export const NOME_DA_CATEGORIA: Record<Categoria, string> = {
  MORADIA: "Moradia",
  UTILIDADES: "Contas da casa",
  ALIMENTACAO: "Alimentação",
  SAUDE: "Saúde",
  TRANSPORTE: "Transporte",
  EDUCACAO: "Educação",
  LAZER: "Lazer",
  COMPRAS_IMPULSO: "Compras por impulso",
  INSUMO_MEI: "Insumos do MEI",
  RENDA: "Renda",
  DIVIDA_JUROS: "Dívidas e juros",
  INVESTIMENTO: "Investimento",
  TRANSFERENCIA: "Transferência",
  APOSTAS_BETS: "Apostas",
  FRAUDE_SUSPEITA: "Suspeita de golpe",
};

export const CATEGORIAS = Object.keys(NOME_DA_CATEGORIA) as Categoria[];
