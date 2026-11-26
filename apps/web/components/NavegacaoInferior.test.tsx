import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { CHAVE_NAV_RECOLHIDA, NavegacaoInferior } from "./NavegacaoInferior";

const navegacao = vi.hoisted(() => ({ caminho: "/dividas", push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => navegacao.caminho,
  // O mesmo objeto a cada render, como o roteador do Next.
  useRouter: () => navegacao,
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
    navegacao.prefetch.mockClear();
  });

  it("mostra as 5 abas, todas com rótulo", async () => {
    const nav = await renderizar();
    // O primeiro botão é o de recolher; as abas vêm depois.
    const abas = within(nav).getAllByRole("button").filter((b) => !b.hasAttribute("aria-expanded"));
    expect(abas.map((b) => b.textContent?.trim())).toEqual(["Início", "Dívidas", "Elpis", "Trilha", "Guardião"]);
  });

  it("recolhe e lembra a escolha para a próxima tela", async () => {
    const nav = await renderizar();
    await userEvent.click(within(nav).getByRole("button", { name: "Recolher navegação" }));
    expect(nav).toHaveAttribute("data-recolhida", "sim");
    expect(localStorage.getItem(CHAVE_NAV_RECOLHIDA)).toBe("1");
    expect(within(nav).getByRole("button", { name: "Expandir navegação" })).toHaveAttribute("aria-expanded", "false");
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
