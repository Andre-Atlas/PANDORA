import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CascaApp } from "@/components/CascaApp";
import { CHAVE_CRISE, CriseProvider } from "@/components/crise/CriseProvider";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { Abertura, ROTA_COMECAR } from "./Abertura";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: vi.fn(), prefetch: vi.fn() }),
}));

// Monta a página de entrada como no app: bundle real, crise e casca sem navegação.
async function renderizar() {
  render(
    <PandoraProvider>
      <CriseProvider>
        <CascaApp variante="abertura">
          <Abertura />
        </CascaApp>
      </CriseProvider>
    </PandoraProvider>,
  );
  await screen.findByRole("main");
}

describe("Abertura", () => {
  beforeEach(() => sessionStorage.clear());

  it("mostra a marca, a frase e a cena com texto alternativo", async () => {
    await renderizar();
    expect(screen.getByRole("heading", { level: 1, name: "PANDORA" })).toBeInTheDocument();
    expect(screen.getByText("Ainda há esperança…")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Pandora, em figura negra/ })).toBeInTheDocument();
  });

  it("leva ao app pelos dois botões Começar", async () => {
    await renderizar();
    const links = screen.getAllByRole("link", { name: "Começar" });
    expect(links).toHaveLength(2);
    links.forEach((link) => expect(link).toHaveAttribute("href", ROTA_COMECAR));
  });

  it("não tem a navegação das abas", async () => {
    await renderizar();
    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
  });

  it("não pula nível de título", async () => {
    await renderizar();
    const niveis = screen.getAllByRole("heading").map((t) => Number(t.tagName.slice(1)));
    niveis.forEach((nivel, i) => {
      if (i > 0) expect(nivel - niveis[i - 1]).toBeLessThanOrEqual(1);
    });
    expect(niveis[0]).toBe(1);
  });

  it("mostra o combinado de privacidade", async () => {
    await renderizar();
    const secao = screen.getByRole("region", { name: "O combinado" });
    expect(within(secao).getAllByRole("listitem").map((li) => li.textContent)).toEqual([
      "O PANDORA só lê. Nunca movimenta seu dinheiro.",
      "Nome, CPF e conta são mascarados antes de qualquer IA.",
      "Você apaga tudo quando quiser.",
    ]);
  });

  it("dá lugar ao fluxo de crise quando ele está aberto", async () => {
    sessionStorage.setItem(CHAVE_CRISE, "1");
    await renderizar();
    expect(await screen.findByRole("heading", { name: "Agora o dinheiro pode esperar." })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "PANDORA" })).not.toBeInTheDocument();
  });
});
