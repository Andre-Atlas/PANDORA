/**
 * A abertura aparece toda vez que o site é aberto.
 *
 * "Aberto" quer dizer uma sessão nova do navegador: uma aba nova, o PWA
 * iniciado do zero ou um link colado. Quem cai direto numa tela do app
 * (ex.: /dividas) volta para a abertura. Recarregar a página na mesma aba
 * não volta, porque o `sessionStorage` sobrevive ao recarregamento.
 */
export const CHAVE_ABERTURA = "pandora-abertura-vista";

export function aberturaVista(): boolean {
  try {
    return sessionStorage.getItem(CHAVE_ABERTURA) === "1";
  } catch {
    // Sem armazenamento (modo privado restrito): não prende a pessoa na abertura.
    return true;
  }
}

export function marcarAberturaVista(): void {
  try {
    sessionStorage.setItem(CHAVE_ABERTURA, "1");
  } catch {
    // Sem armazenamento: aberturaVista() já libera as telas.
  }
}
