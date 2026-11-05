import { describe, expect, it } from "vitest";
import { CONTATOS_APOIO, EMERGENCIA, contatosVisiveis, resumoContatos } from "./contatos";

describe("contatos de apoio", () => {
  it("todo contato visível tem fonte oficial em https e data de conferência", () => {
    for (const contato of contatosVisiveis()) {
      expect(contato.fonte, contato.id).toMatch(/^https:\/\//);
      expect(contato.conferidoEm, contato.id).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    }
  });

  it("telefones são só dígitos, para o tel: funcionar em qualquer aparelho", () => {
    const telefones = [...CONTATOS_APOIO.map((c) => c.href), EMERGENCIA.href].filter((h) => h?.startsWith("tel:"));
    expect(telefones).toEqual(["tel:188", "tel:192"]);
  });

  it("o CVV é o primeiro e o principal", () => {
    expect(contatosVisiveis()[0]).toMatchObject({ id: "cvv", href: "tel:188", variante: "primario" });
  });

  it("contato sem endereço confirmado fica fora da tela", () => {
    expect(contatosVisiveis().map((c) => c.id)).not.toContain("jogadores-anonimos");
  });

  it("o resumo cita só o que aparece", () => {
    expect(resumoContatos()).toBe("CVV e CAPS AD");
  });
});
