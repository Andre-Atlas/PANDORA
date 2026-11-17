import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ROTA_ENTRAR } from "@/components/conta/PortaoConta";
import { CHAVE_CONSENTIMENTO_PENDENTE } from "@/lib/conta/sessao";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { CONSENTIMENTO, json, ligarDadosReais, simularApi } from "@/test/apiFalsa";
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

describe("Perguntas com os dados reais ligados", () => {
  beforeEach(() => navegacao.push.mockClear());
  afterEach(() => vi.unstubAllGlobals());

  async function aceitarEAbrir() {
    await renderizar();
    await userEvent.click(screen.getByRole("button", { name: "Pular" }));
    await userEvent.click(screen.getByRole("button", { name: "Pular" }));
    await userEvent.click(screen.getByRole("checkbox", { name: /Concordo com o uso dos meus dados/ }));
    await userEvent.click(screen.getByRole("button", { name: /Abrir minha caixa/ }));
  }

  it("sem sessão, guarda o aceite e leva ao login", async () => {
    ligarDadosReais();
    const api = simularApi({});
    await aceitarEAbrir();
    expect(navegacao.push).toHaveBeenCalledWith(ROTA_ENTRAR);
    expect(sessionStorage.getItem(CHAVE_CONSENTIMENTO_PENDENTE)).toBe("1");
    expect(api.chamadas).toEqual([]);
  });

  it("com sessão, registra o consentimento na API e abre o Início", async () => {
    ligarDadosReais({ comSessao: true });
    const api = simularApi({ "POST /consentimentos": () => json(CONSENTIMENTO, 201) });
    await aceitarEAbrir();
    await waitFor(() => expect(navegacao.push).toHaveBeenCalledWith(ROTA_DEPOIS_DAS_PERGUNTAS));
    expect(api.chamadas[0].corpo).toEqual({ finalidade: "diagnostico_financeiro", versao_termo: "2026-11" });
  });

  it("se o registro falhar, avisa e fica na tela", async () => {
    ligarDadosReais({ comSessao: true });
    simularApi({ "POST /consentimentos": () => json({ title: "x", status: 500 }, 500) });
    await aceitarEAbrir();
    expect(await screen.findByRole("alert")).toHaveTextContent(/Algo deu errado/);
    expect(navegacao.push).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: /Abrir minha caixa/ })).toBeEnabled();
  });
});
