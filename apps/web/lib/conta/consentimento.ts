import { listarConsentimentos, registrarConsentimento } from "@/lib/api/cliente";
import { consentimentoPendente, limparConsentimentoPendente } from "./sessao";

export type Destino = "inicio" | "perguntas";

/**
 * Depois do login, decide para onde a pessoa vai.
 *
 * - Já tem consentimento ativo na API: Início.
 * - Aceitou "O combinado" nas perguntas antes de entrar: registra o aceite e vai ao Início.
 * - Nenhum dos dois: volta às perguntas, que pedem o aceite (a LGPD exige que ela marque).
 */
export async function destinoDepoisDeEntrar(): Promise<Destino> {
  const consentimentos = await listarConsentimentos();
  if (consentimentos.some((c) => c.ativo)) {
    limparConsentimentoPendente();
    return "inicio";
  }
  if (consentimentoPendente()) {
    await registrarConsentimento();
    limparConsentimentoPendente();
    return "inicio";
  }
  return "perguntas";
}
