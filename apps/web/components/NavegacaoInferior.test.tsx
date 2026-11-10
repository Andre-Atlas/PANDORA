import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { NavegacaoInferior } from "./NavegacaoInferior";

const navegacao = vi.hoisted(() => ({ caminho: "/dividas", push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => navegacao.caminho,
  useRouter: () => ({ push: navegacao.push, prefetch: navegacao.prefetch }),
}));

// Usa o bundle.js real do design system, não um dublê.
async function renderizar() {
  render(
    <PandoraProvider>
      <NavegacaoInferior />
    </PandoraProvider>,
  );
  return screen.findByRole("navigation", { name: "Navegação principal" });
}

describe("NavegacaoInferior", () => {
  beforeEach(() => {
    navegacao.caminho = "/dividas";
    navegacao.push.mockClear();
  });

  it("mostra as 5 abas, todas com rótulo", async () => {
    const nav = await renderizar();
    const botoes = within(nav).getAllByRole("button");
    expect(botoes.map((b) => b.textContent?.trim())).toEqual(["Início", "Dívidas", "Elpis", "Trilha", "Guardião"]);
  });

  it("marca a aba da rota atual", async () => {
    navegacao.caminho = "/inicio/metas";
    const nav = await renderizar();
    const atual = within(nav).getAllByRole("button").filter((b) => b.getAttribute("aria-current") === "page");
    expect(atual.map((b) => b.textContent?.trim())).toEqual(["Início"]);
  });

  it("navega ao tocar numa aba", async () => {
    const nav = await renderizar();
    await userEvent.click(within(nav).getByRole("button", { name: /Trilha/ }));
    expect(navegacao.push).toHaveBeenCalledWith("/trilha");
  });

  it("faz prefetch de todas as abas", async () => {
    await renderizar();
    expect(navegacao.prefetch).toHaveBeenCalledTimes(5);
  });
});
