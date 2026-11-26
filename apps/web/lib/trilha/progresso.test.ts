import { beforeEach, describe, expect, it, vi } from "vitest";
import type { EtapaTrilha } from "@/lib/api/tipos";
import { CHAVE_TRILHA, comEstado, concluirLicao, emblemaOuPadrao, lerConcluidas } from "./progresso";

const etapa = (n: number, licao_id: string): EtapaTrilha => ({
  n,
  t: licao_id,
  x: 100,
  lado: "d",
  marco: null,
  emblema: "templo",
  licao_id,
});
const ETAPAS = [etapa(1, "a"), etapa(2, "b"), etapa(3, "c")];

beforeEach(() => localStorage.clear());

describe("progresso da trilha", () => {
  it("começa vazio e guarda cada lição concluída uma única vez", () => {
    expect(lerConcluidas()).toEqual([]);
    concluirLicao("a");
    concluirLicao("a");
    concluirLicao("b");
    expect(lerConcluidas()).toEqual(["a", "b"]);
  });

  it("ignora conteúdo corrompido", () => {
    localStorage.setItem(CHAVE_TRILHA, "{quebrado");
    expect(lerConcluidas()).toEqual([]);
    localStorage.setItem(CHAVE_TRILHA, JSON.stringify(["a", 7, null]));
    expect(lerConcluidas()).toEqual(["a"]);
  });

  it("segue funcionando sem armazenamento", () => {
    const quebra = vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("bloqueado");
    });
    expect(lerConcluidas()).toEqual([]);
    quebra.mockRestore();
  });

  it("marca feitas, a atual e as próximas", () => {
    expect(comEstado(ETAPAS, ["a"]).map((e) => e.estado)).toEqual(["feito", "atual", "proximo"]);
    expect(comEstado(ETAPAS, []).map((e) => e.estado)).toEqual(["atual", "proximo", "proximo"]);
    expect(comEstado(ETAPAS, ["a", "b", "c"]).map((e) => e.estado)).toEqual(["feito", "feito", "feito"]);
  });

  it("a atual é a primeira pendente, mesmo com uma posterior já feita", () => {
    expect(comEstado(ETAPAS, ["b"]).map((e) => e.estado)).toEqual(["atual", "feito", "proximo"]);
  });
});

describe("emblemas", () => {
  it("aceita os seis emblemas do design system e cai no templo para o resto", () => {
    expect(emblemaOuPadrao("anfora")).toBe("anfora");
    expect(emblemaOuPadrao("elmo")).toBe("elmo");
    expect(emblemaOuPadrao("coruja")).toBe("templo");
    expect(emblemaOuPadrao(undefined)).toBe("templo");
  });
});
