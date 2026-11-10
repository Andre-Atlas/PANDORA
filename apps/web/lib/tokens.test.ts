import { describe, expect, it } from "vitest";
import manifest from "@/app/manifest";
import { corDoToken } from "./tokens";

describe("corDoToken", () => {
  it("lê cores fixas", () => {
    expect(corDoToken("laranja-vaso")).toBe("#f0792b");
  });

  it("resolve referências por tema", () => {
    // superficie = {papiro} no claro e {tinta} no escuro
    expect(corDoToken("superficie", "light")).toBe(corDoToken("papiro"));
    expect(corDoToken("superficie", "dark")).toBe(corDoToken("tinta"));
  });

  it("falha alto com token que não existe", () => {
    expect(() => corDoToken("azul-qualquer")).toThrow(/desconhecido/);
  });
});

describe("manifesto do PWA", () => {
  const m = manifest();

  it("tem o mínimo para ser instalável", () => {
    expect(m).toMatchObject({ name: "PANDORA", start_url: "/", display: "standalone" });
    const tamanhos = m.icons?.map((i) => `${i.sizes} ${i.purpose}`);
    expect(tamanhos).toEqual(expect.arrayContaining(["192x192 any", "512x512 any", "512x512 maskable"]));
  });

  it("usa as cores dos tokens", () => {
    expect(m.theme_color).toBe(corDoToken("laranja-vaso"));
    expect(m.background_color).toBe(corDoToken("superficie", "light"));
  });
});
