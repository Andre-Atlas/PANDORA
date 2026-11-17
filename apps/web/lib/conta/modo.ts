/**
 * Liga as telas com dados reais (#71): conta, consentimento, envio de extrato
 * e Raio-X vindos da API.
 *
 * Desligado (o padrão), o app usa os dados de demonstração e não pede login,
 * para testar as outras telas sem conta e sem enviar dados. Para ligar, crie
 * `apps/web/.env.local` com `NEXT_PUBLIC_PANDORA_DADOS_REAIS=1` e reinicie o
 * `npm run dev` (o Next fixa a variável no momento do build).
 */
export function dadosReais(): boolean {
  return process.env.NEXT_PUBLIC_PANDORA_DADOS_REAIS === "1";
}
