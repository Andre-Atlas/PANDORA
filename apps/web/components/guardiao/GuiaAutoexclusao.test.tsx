import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CriseProvider } from "@/components/crise/CriseProvider";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { GuiaAutoexclusao } from "./GuiaAutoexclusao";
import { LinkGuiaAutoexclusao, ROTA_AUTOEXCLUSAO } from "./LinkGuiaAutoexclusao";

const router = vi.hoisted(() => ({ push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({ usePathname: () => "/guardiao", useRouter: () => router }));

function renderizar(ui: React.ReactNode) {
  render(
    <PandoraProvider>
      <CriseProvider>{ui}</CriseProvider>
    </PandoraProvider>,
  );
}

describe("guia de autoexclusão", () => {
  it("toda citação mostra a norma e um link oficial", async () => {
    renderizar(<GuiaAutoexclusao />);
    await screen.findByRole("heading", { level: 1, name: "Autoexclusão" });

    const citacoes = document.querySelectorAll(".pd-citacao");
    expect(citacoes.length).toBe(5);
    for (const citacao of citacoes) {
      const link = within(citacao as HTMLElement).getByRole("link");
      expect(link.getAttribute("href")).toMatch(/^https:\/\/(www\.planalto|www\.bcb|agenciagov\.ebc)\./);
      expect(citacao).toHaveTextContent(/Fonte oficial/);
    }
  });

  it("traz os 4 passos, com o pagamento a site de apostas em alerta", async () => {
    renderizar(<GuiaAutoexclusao />);
    await screen.findByRole("heading", { level: 1 });
    for (const titulo of [
      "Bloqueie os sites no celular e no computador",
      "Baixe o limite do Pix à noite",
      "Não pague site de apostas",
      "Denuncie o site",
    ]) {
      expect(screen.getByRole("heading", { name: titulo })).toBeInTheDocument();
    }
    expect(screen.getByRole("heading", { name: "Não pague site de apostas" }).closest(".pd-cartao")).toHaveClass(
      "pd-cartao-alerta",
    );
  });

  it("abre BetBlocker e Fala.BR em outra aba, com segurança", async () => {
    renderizar(<GuiaAutoexclusao />);
    for (const [nome, href] of [
      [/Abrir o BetBlocker/, "https://betblocker.org/br/"],
      [/Abrir o Fala\.BR/, "https://www.gov.br/falabr"],
    ] as const) {
      const link = await screen.findByRole("link", { name: nome });
      expect(link).toHaveAttribute("href", href);
      expect(link).toHaveAttribute("target", "_blank");
      expect(link).toHaveAttribute("rel", "noopener noreferrer");
    }
  });

  it("diz quando foi conferido, oferece apoio e volta ao Guardião", async () => {
    renderizar(<GuiaAutoexclusao />);
    expect(await screen.findByText(/conferidas em 5 de novembro de 2026/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Precisa de apoio agora\?/ })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Voltar ao Guardião" })).toHaveAttribute("href", "/guardiao");
  });

  it("não fala em sites .bet.br, que foram proibidos", async () => {
    renderizar(<GuiaAutoexclusao />);
    await screen.findByRole("heading", { level: 1 });
    expect(document.body).not.toHaveTextContent(/\.bet\.br/);
  });
});

describe("entrada do guia no Guardião", () => {
  it("leva ao guia", async () => {
    renderizar(<LinkGuiaAutoexclusao />);
    await userEvent.click(await screen.findByRole("button", { name: /Autoexclusão das apostas/ }));
    expect(router.push).toHaveBeenCalledWith(ROTA_AUTOEXCLUSAO);
  });
});
