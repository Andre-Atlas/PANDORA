/** Formatos de dinheiro e data em português do Brasil. A API manda valores em centavos e meses como "2026-10". */

const REAIS = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

/** 285000 → "R$ 2.850,00" (o Intl usa espaço não separável depois do "R$"). */
export const reais = (centavos: number) => REAIS.format(centavos / 100);

const MES = new Intl.DateTimeFormat("pt-BR", { month: "long", year: "numeric", timeZone: "UTC" });

/** "2026-10" → "outubro de 2026". */
export function nomeDoMes(mes: string): string {
  const [ano, numero] = mes.split("-").map(Number);
  return MES.format(new Date(Date.UTC(ano, numero - 1, 1)));
}

/** Mês de uma data ISO da API, no fuso em que ela foi escrita: "2026-10-15T00:00:00-03:00" → "2026-10". */
export const mesDaData = (dataIso: string) => dataIso.slice(0, 7);

/** "2026-10-15T00:00:00-03:00" → "15/10". Lê o dia do próprio texto, sem converter fuso. */
export function diaEMes(dataIso: string): string {
  const [, mes, dia] = dataIso.slice(0, 10).split("-");
  return `${dia}/${mes}`;
}

/** Mês corrente no relógio do aparelho, no formato da API. */
export function mesAtual(agora: Date = new Date()): string {
  return `${agora.getFullYear()}-${String(agora.getMonth() + 1).padStart(2, "0")}`;
}
