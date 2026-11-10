import { describe, expect, it } from "vitest";
import { simularMatchMedia } from "@/test/matchMedia";
import { CHAVE_TEMA, lerPreferencia, resolverTema, salvarPreferencia, scriptTemaInicial } from "./tema";

const rodarScriptInicial = () => new Function(scriptTemaInicial)();

describe("resolverTema", () => {
  it("respeita a escolha explícita", () => {
    expect(resolverTema("claro", true)).toBe("light");
    expect(resolverTema("escuro", false)).toBe("dark");
  });

  it("segue o sistema em Sistema", () => {
    expect(resolverTema("sistema", true)).toBe("dark");
    expect(resolverTema("sistema", false)).toBe("light");
  });
});

describe("preferência salva", () => {
  it("começa em Sistema e ignora valores inválidos", () => {
    expect(lerPreferencia()).toBe("sistema");
    localStorage.setItem(CHAVE_TEMA, "roxo");
    expect(lerPreferencia()).toBe("sistema");
  });

  it("guarda Claro/Escuro e apaga a chave em Sistema", () => {
    salvarPreferencia("escuro");
    expect(lerPreferencia()).toBe("escuro");
    salvarPreferencia("sistema");
    expect(localStorage.getItem(CHAVE_TEMA)).toBeNull();
  });
});

describe("scriptTemaInicial", () => {
  it("aplica o tema do sistema quando não há escolha salva", () => {
    simularMatchMedia(true);
    rodarScriptInicial();
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("dá prioridade à escolha salva", () => {
    simularMatchMedia(true);
    localStorage.setItem(CHAVE_TEMA, "claro");
    rodarScriptInicial();
    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("concorda com resolverTema em todos os casos", () => {
    for (const salva of [null, "claro", "escuro"] as const) {
      for (const sistemaEscuro of [false, true]) {
        simularMatchMedia(sistemaEscuro);
        if (salva) localStorage.setItem(CHAVE_TEMA, salva);
        else localStorage.removeItem(CHAVE_TEMA);
        rodarScriptInicial();
        expect(document.documentElement.dataset.theme).toBe(resolverTema(salva ?? "sistema", sistemaEscuro));
      }
    }
  });
});
