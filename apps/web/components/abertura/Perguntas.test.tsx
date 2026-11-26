import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { Perguntas, ROTA_DEPOIS_DAS_PERGUNTAS } from "./Perguntas";

const navegacao = vi.hoisted(() => ({ push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => "/comecar",
  useRouter: () => navegacao,
}));

async function renderizar() {
  render(
    <PandoraProvider>
      <Perguntas />
    </PandoraProvider>,
  );
  await screen.findByRole("heading", { name: "Como você se sente sobre seu dinheiro hoje?" });
}

describe("Perguntas da abertura", () => {
  beforeEach(() => navegacao.push.mockClear());

  it("passa pelas três perguntas e leva o foco a cada uma", async () => {
    await renderizar();
    await userEvent.click(screen.getByRole("button", { name: /Continuar/ }));
    const pesa = screen.getByRole("heading", { name: "O que mais pesa hoje?" });
    expect(pesa).toHaveFocus();

    await userEvent.click(screen.getByRole("radio", { name: /Medo de golpes/ }));
    expect(screen.getByRole("radio", { name: /Medo de golpes/ })).toHaveAttribute("aria-checked", "true");

    await userEvent.click(screen.getByRole("button", { name: /Continuar/ }));
    expect(screen.getByRole("heading", { name: "Como quer começar?" })).toHaveFocus();
  });

  it("só abre a caixa depois do aceite, que começa desmarcado", async () => {
    await renderizar();
    await userEvent.click(screen.getByRole("button", { name: "Pular" }));
    await userEvent.click(screen.getByRole("button", { name: "Pular" }));

    const abrir = screen.getByRole("button", { name: /Abrir minha caixa/ });
    const aceite = screen.getByRole("checkbox", { name: /Concordo com o uso dos meus dados/ });
    expect(aceite).not.toBeChecked();
    expect(abrir).toBeDisabled();

    await userEvent.click(aceite);
    expect(abrir).toBeEnabled();
    await userEvent.click(abrir);
    expect(navegacao.push).toHaveBeenCalledWith(ROTA_DEPOIS_DAS_PERGUNTAS);
  });

  it("volta para a abertura no primeiro passo", async () => {
    await renderizar();
    await userEvent.click(screen.getByRole("button", { name: "Voltar" }));
    expect(navegacao.push).toHaveBeenCalledWith("/");
  });
});
