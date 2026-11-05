import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CascaApp } from "@/components/CascaApp";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { CHAVE_CRISE, CriseProvider } from "./CriseProvider";
import { LinkApoio } from "./LinkApoio";

vi.mock("next/navigation", () => ({
  usePathname: () => "/guardiao",
  useRouter: () => ({ push: vi.fn(), prefetch: vi.fn() }),
}));

// App real: bundle do design system, casca e navegação.
async function renderizarGuardiao() {
  render(
    <PandoraProvider>
      <CriseProvider>
        <CascaApp>
          <h1>Guardião</h1>
          <p>Meta do mês: guardar R$ 200</p>
          <LinkApoio />
        </CascaApp>
      </CriseProvider>
    </PandoraProvider>,
  );
  await screen.findByRole("main");
}

const tituloCrise = { name: "Agora o dinheiro pode esperar." };

describe("fluxo de crise", () => {
  it("abre a partir do Guardião e cita só os contatos que aparecem", async () => {
    await renderizarGuardiao();
    const entrada = screen.getByRole("button", { name: /Precisa de apoio agora\?/ });
    expect(entrada).toHaveTextContent("CVV e CAPS AD");
  });

  it("substitui a tela e tira a navegação e as metas", async () => {
    await renderizarGuardiao();
    await userEvent.click(screen.getByRole("button", { name: /Precisa de apoio agora\?/ }));

    const titulo = screen.getByRole("heading", tituloCrise);
    expect(titulo).toHaveFocus();
    expect(document.title).toBe("Apoio · PANDORA");
    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
    expect(screen.queryByText(/Meta do mês/)).not.toBeInTheDocument();
  });

  it("liga para o CVV, abre a página oficial do CAPS e mostra a emergência", async () => {
    await renderizarGuardiao();
    await userEvent.click(screen.getByRole("button", { name: /Precisa de apoio agora\?/ }));

    expect(screen.getByRole("link", { name: /Ligar para o CVV: 188/ })).toHaveAttribute("href", "tel:188");
    const caps = screen.getByRole("link", { name: /Encontrar um CAPS AD/ });
    expect(caps).toHaveAttribute("href", expect.stringMatching(/^https:\/\/www\.gov\.br\/saude\//));
    expect(caps).toHaveAttribute("rel", "noopener noreferrer");
    expect(screen.getByRole("link", { name: "SAMU 192" })).toHaveAttribute("href", "tel:192");
    expect(screen.queryByRole("link", { name: /Jogadores Anônimos/ })).not.toBeInTheDocument();
  });

  it("volta quando a pessoa quiser, com tudo no lugar", async () => {
    await renderizarGuardiao();
    document.title = "Guardião · PANDORA";
    await userEvent.click(screen.getByRole("button", { name: /Precisa de apoio agora\?/ }));
    await userEvent.click(screen.getByRole("button", { name: "Voltar quando eu quiser" }));

    expect(screen.queryByRole("heading", tituloCrise)).not.toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Navegação principal" })).toBeInTheDocument();
    expect(screen.getByText(/Meta do mês/)).toBeInTheDocument();
    expect(sessionStorage.getItem(CHAVE_CRISE)).toBeNull();
    expect(document.title).toBe("Guardião · PANDORA");
  });

  it("recarregar a página não tira a pessoa da tela de apoio", async () => {
    sessionStorage.setItem(CHAVE_CRISE, "1");
    await renderizarGuardiao();
    await waitFor(() => expect(screen.getByRole("heading", tituloCrise)).toBeInTheDocument());
    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
  });
});
