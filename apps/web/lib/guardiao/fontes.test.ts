import { describe, expect, it } from "vitest";
import { FONTES, LINKS, REVISAR_ATE } from "./fontes";

const DOMINIOS_OFICIAIS = ["www.planalto.gov.br", "www.bcb.gov.br", "agenciagov.ebc.com.br", "www.gov.br"];

describe("fontes do guia de autoexclusão", () => {
  it("toda norma aponta para um site oficial, em https", () => {
    for (const [chave, fonte] of Object.entries(FONTES)) {
      const url = new URL(fonte.href);
      expect(url.protocol, chave).toBe("https:");
      expect(DOMINIOS_OFICIAIS, `${chave}: ${url.hostname}`).toContain(url.hostname);
      expect(fonte.conferidoEm, chave).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    }
  });

  it("links de ação também são https", () => {
    for (const href of Object.values(LINKS)) expect(new URL(href).protocol).toBe("https:");
  });

  it("o guia ainda está dentro do prazo de revisão", () => {
    const hoje = new Date().toISOString().slice(0, 10);
    expect(
      hoje <= REVISAR_ATE,
      `Passou de ${REVISAR_ATE}, o prazo para o Congresso votar a MP nº 1.394/2026. ` +
        "Confira de novo as fontes e o texto do guia, e atualize conferidoEm e REVISAR_ATE em lib/guardiao/fontes.ts.",
    ).toBe(true);
  });
});
