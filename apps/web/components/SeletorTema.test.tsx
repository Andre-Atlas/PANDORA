import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { CHAVE_TEMA } from "@/lib/tema";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { simularMatchMedia } from "@/test/matchMedia";
import { SeletorTema } from "./SeletorTema";
import { TemaProvider } from "./TemaProvider";

async function renderizar() {
  render(
    <TemaProvider>
      <PandoraProvider>
        <SeletorTema />
      </PandoraProvider>
    </TemaProvider>,
  );
  return screen.findByRole("radiogroup", { name: "Tema" });
}

describe("SeletorTema", () => {
  it("começa em Sistema", async () => {
    await renderizar();
    expect(screen.getByRole("radio", { name: "Sistema" })).toHaveAttribute("aria-checked", "true");
  });

  it("troca para Escuro e guarda a escolha", async () => {
    await renderizar();
    await userEvent.click(screen.getByRole("radio", { name: "Escuro" }));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(localStorage.getItem(CHAVE_TEMA)).toBe("escuro");
    expect(screen.getByRole("radio", { name: "Escuro" })).toHaveAttribute("aria-checked", "true");
  });

  it("em Sistema, acompanha quando o aparelho muda de tema", async () => {
    const trocarSistema = simularMatchMedia(false);
    await renderizar();
    expect(document.documentElement.dataset.theme).toBe("light");
    act(() => trocarSistema(true));
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("com escolha explícita, ignora o tema do aparelho", async () => {
    const trocarSistema = simularMatchMedia(false);
    localStorage.setItem(CHAVE_TEMA, "claro");
    await renderizar();
    act(() => trocarSistema(true));
    expect(document.documentElement.dataset.theme).toBe("light");
  });
});
