import { describe, expect, it, vi } from "vitest";
import { dadosReais } from "./modo";
import {
  apagarSessao,
  CHAVE_SESSAO,
  consentimentoPendente,
  guardarSessao,
  lerToken,
  limparConsentimentoPendente,
  marcarConsentimentoPendente,
} from "./sessao";

describe("modo de dados", () => {
  it("começa na demonstração e só liga com a variável em 1", () => {
    expect(dadosReais()).toBe(false);
    vi.stubEnv("NEXT_PUBLIC_PANDORA_DADOS_REAIS", "true");
    expect(dadosReais()).toBe(false);
    vi.stubEnv("NEXT_PUBLIC_PANDORA_DADOS_REAIS", "1");
    expect(dadosReais()).toBe(true);
  });
});

describe("sessão", () => {
  it("guarda o token e o devolve enquanto vale", () => {
    guardarSessao({ token: "abc", expira_em: "2026-11-24T10:00:00Z" });
    expect(lerToken(new Date("2026-11-20T10:00:00Z"))).toBe("abc");
  });

  it("descarta o token vencido", () => {
    guardarSessao({ token: "abc", expira_em: "2026-11-24T10:00:00Z" });
    expect(lerToken(new Date("2026-11-25T10:00:00Z"))).toBeNull();
    expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull();
  });

  it("ignora o que estiver corrompido no armazenamento", () => {
    localStorage.setItem(CHAVE_SESSAO, "{não é json");
    expect(lerToken()).toBeNull();
  });

  it("sai apagando a sessão", () => {
    guardarSessao({ token: "abc", expira_em: "2099-01-01T00:00:00Z" });
    apagarSessao();
    expect(lerToken()).toBeNull();
  });

  it("lembra o aceite das perguntas até o login", () => {
    expect(consentimentoPendente()).toBe(false);
    marcarConsentimentoPendente();
    expect(consentimentoPendente()).toBe(true);
    limparConsentimentoPendente();
    expect(consentimentoPendente()).toBe(false);
  });
});
