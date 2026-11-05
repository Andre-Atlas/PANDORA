import { describe, expect, it } from "vitest";
import { ABAS, abaDaRota, rotaDaAba } from "./navegacao";

describe("navegação", () => {
  it("tem as 5 abas da NavBase, na ordem do design system", () => {
    expect(ABAS.map((a) => a.rotulo)).toEqual(["Início", "Dívidas", "Elpis", "Trilha", "Guardião"]);
  });

  it("acha a aba de cada rota, inclusive em subpáginas", () => {
    expect(abaDaRota("/dividas")).toBe("dividas");
    expect(abaDaRota("/inicio/metas")).toBe("inicio");
  });

  it("não confunde rotas com o mesmo começo", () => {
    expect(abaDaRota("/inicio-falso")).toBeUndefined();
    expect(abaDaRota(null)).toBeUndefined();
  });

  it("acha a rota de cada aba", () => {
    expect(rotaDaAba("guardiao")).toBe("/guardiao");
    expect(rotaDaAba("metas")).toBeUndefined();
  });
});
