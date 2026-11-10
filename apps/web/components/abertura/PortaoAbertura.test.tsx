import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CriseProvider } from "@/components/crise/CriseProvider";
import { aberturaVista, CHAVE_ABERTURA } from "@/lib/abertura/portao";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { Abertura } from "./Abertura";
import { PortaoAbertura } from "./PortaoAbertura";

const navegacao = vi.hoisted(() => ({ replace: vi.fn(), push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dividas",
  useRouter: () => navegacao,
}));

describe("PortaoAbertura", () => {
  beforeEach(() => navegacao.replace.mockClear());

  it("manda para a abertura quem abre o site direto numa tela do app", () => {
    render(
      <PortaoAbertura>
        <p>Tela de dívidas</p>
      </PortaoAbertura>,
    );
    expect(navegacao.replace).toHaveBeenCalledWith("/");
    expect(screen.queryByText("Tela de dívidas")).not.toBeInTheDocument();
  });

  it("deixa passar depois que a abertura foi vista nesta sessão", () => {
    sessionStorage.setItem(CHAVE_ABERTURA, "1");
    render(
      <PortaoAbertura>
        <p>Tela de dívidas</p>
      </PortaoAbertura>,
    );
    expect(screen.getByText("Tela de dívidas")).toBeInTheDocument();
    expect(navegacao.replace).not.toHaveBeenCalled();
  });

  it("a abertura marca a sessão como vista", async () => {
    expect(aberturaVista()).toBe(false);
    render(
      <PandoraProvider>
        <CriseProvider>
          <Abertura />
        </CriseProvider>
      </PandoraProvider>,
    );
    await screen.findByRole("heading", { level: 1, name: "PANDORA" });
    expect(aberturaVista()).toBe(true);
  });
});
