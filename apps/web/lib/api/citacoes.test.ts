import { describe, expect, it } from "vitest";
import { linkSeguro, numerosCitados, resumoDoTrecho, rotuloDoLink, rotuloNorma } from "./citacoes";

describe("citações", () => {
  it("só aceita links web", () => {
    expect(linkSeguro("https://www.planalto.gov.br/x")).toBe("https://www.planalto.gov.br/x");
    expect(linkSeguro("javascript:alert(1)")).toBe("#");
    expect(linkSeguro("")).toBe("#");
  });

  it("nomeia o link pelo órgão", () => {
    expect(rotuloDoLink("https://www.planalto.gov.br/ccivil_03/x")).toBe("Ler no Planalto");
    expect(rotuloDoLink("https://www.bcb.gov.br/content/y.pdf")).toBe("Ler no Banco Central");
    expect(rotuloDoLink("https://exemplo.com/z")).toBe("Ler a fonte");
    expect(rotuloDoLink("não é url")).toBe("Ler a fonte");
  });

  it("junta norma e artigo", () => {
    expect(rotuloNorma({ norma: "Lei 14.181/2021", artigo: "Art. 104-A" })).toBe("Lei 14.181/2021, Art. 104-A");
    expect(rotuloNorma({ norma: "Cartilha do CNJ", artigo: null })).toBe("Cartilha do CNJ");
  });

  it("resume o trecho sem cortar palavra", () => {
    expect(resumoDoTrecho("  curto \n texto ")).toBe("curto texto");
    const longo = "palavra ".repeat(60);
    const r = resumoDoTrecho(longo);
    expect(r.endsWith("palavra…")).toBe(true);
    expect(r.length).toBeLessThanOrEqual(221);
  });

  it("lista as citações sem repetir", () => {
    expect(numerosCitados("A [1] e [2][1], depois [3].")).toEqual([1, 2, 3]);
    expect(numerosCitados("sem citação")).toEqual([]);
  });
});
