import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ROTA_COMECAR } from "@/components/abertura/Abertura";
import { ROTA_DEPOIS_DAS_PERGUNTAS } from "@/components/abertura/Perguntas";
import { CHAVE_CONSENTIMENTO_PENDENTE, lerToken } from "@/lib/conta/sessao";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { CONSENTIMENTO, json, ligarDadosReais, SESSAO, simularApi, USUARIO } from "@/test/apiFalsa";
import { Entrar } from "./Entrar";
import { PortaoConta, ROTA_ENTRAR } from "./PortaoConta";

const navegacao = vi.hoisted(() => ({ replace: vi.fn(), push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => "/entrar",
  useRouter: () => navegacao,
}));

beforeEach(() => {
  navegacao.replace.mockClear();
  navegacao.push.mockClear();
});
afterEach(() => vi.unstubAllGlobals());

describe("PortaoConta", () => {
  const tela = () =>
    render(
      <PortaoConta>
        <p>Tela do app</p>
      </PortaoConta>,
    );

  it("deixa passar sem conta quando os dados reais estão desligados", () => {
    tela();
    expect(screen.getByText("Tela do app")).toBeInTheDocument();
    expect(navegacao.replace).not.toHaveBeenCalled();
  });

  it("com dados reais, manda para /entrar quem não tem sessão", () => {
    ligarDadosReais();
    tela();
    expect(navegacao.replace).toHaveBeenCalledWith(ROTA_ENTRAR);
    expect(screen.queryByText("Tela do app")).not.toBeInTheDocument();
  });

  it("com dados reais e sessão, deixa passar", () => {
    ligarDadosReais({ comSessao: true });
    tela();
    expect(screen.getByText("Tela do app")).toBeInTheDocument();
  });
});

describe("Entrar", () => {
  async function renderizar() {
    render(
      <PandoraProvider>
        <Entrar />
      </PandoraProvider>,
    );
    await screen.findByRole("heading", { name: "Crie a sua conta" });
  }

  async function preencher(email: string, senha: string) {
    await userEvent.type(screen.getByLabelText("E-mail"), email);
    await userEvent.type(screen.getByLabelText("Senha"), senha);
  }

  it("com os dados reais desligados, vai direto ao Início", async () => {
    render(
      <PandoraProvider>
        <Entrar />
      </PandoraProvider>,
    );
    await waitFor(() => expect(navegacao.replace).toHaveBeenCalledWith(ROTA_DEPOIS_DAS_PERGUNTAS));
  });

  it("cria a conta, entra e registra o aceite dado nas perguntas", async () => {
    ligarDadosReais();
    sessionStorage.setItem(CHAVE_CONSENTIMENTO_PENDENTE, "1");
    const api = simularApi({
      "POST /auth/cadastro": () => json(USUARIO, 201),
      "POST /auth/sessoes": () => json(SESSAO, 201),
      "GET /consentimentos": () => json([]),
      "POST /consentimentos": () => json(CONSENTIMENTO, 201),
    });
    await renderizar();
    await preencher("carla@exemplo.com", "senha-segura-1");
    await userEvent.click(screen.getByRole("button", { name: /Criar e entrar/ }));

    await waitFor(() => expect(navegacao.replace).toHaveBeenCalledWith(ROTA_DEPOIS_DAS_PERGUNTAS));
    expect(api.chamadas.map((c) => c.rota)).toEqual([
      "POST /auth/cadastro",
      "POST /auth/sessoes",
      "GET /consentimentos",
      "POST /consentimentos",
    ]);
    expect(api.chamadas[0].corpo).toEqual({ email: "carla@exemplo.com", senha: "senha-segura-1" });
    expect(lerToken()).toBe(SESSAO.token);
    expect(sessionStorage.getItem(CHAVE_CONSENTIMENTO_PENDENTE)).toBeNull();
  });

  it("quem já tem conta e consentimento vai ao Início sem registrar de novo", async () => {
    ligarDadosReais();
    const api = simularApi({
      "POST /auth/sessoes": () => json(SESSAO, 201),
      "GET /consentimentos": () => json([CONSENTIMENTO]),
    });
    await renderizar();
    await userEvent.click(screen.getByRole("radio", { name: "Já tenho conta" }));
    await preencher("carla@exemplo.com", "senha-segura-1");
    await userEvent.click(screen.getByRole("button", { name: /^Entrar/ }));

    await waitFor(() => expect(navegacao.replace).toHaveBeenCalledWith(ROTA_DEPOIS_DAS_PERGUNTAS));
    expect(api.chamadas.map((c) => c.rota)).toEqual(["POST /auth/sessoes", "GET /consentimentos"]);
  });

  it("sem consentimento nenhum, volta às perguntas para pedir o aceite", async () => {
    ligarDadosReais();
    simularApi({
      "POST /auth/sessoes": () => json(SESSAO, 201),
      "GET /consentimentos": () => json([{ ...CONSENTIMENTO, ativo: false }]),
    });
    await renderizar();
    await userEvent.click(screen.getByRole("radio", { name: "Já tenho conta" }));
    await preencher("carla@exemplo.com", "senha-segura-1");
    await userEvent.click(screen.getByRole("button", { name: /^Entrar/ }));
    await waitFor(() => expect(navegacao.replace).toHaveBeenCalledWith(ROTA_COMECAR));
  });

  it("mostra o erro do login sem sair da tela", async () => {
    ligarDadosReais();
    simularApi({ "POST /auth/sessoes": () => json({ title: "x", status: 401 }, 401) });
    await renderizar();
    await userEvent.click(screen.getByRole("radio", { name: "Já tenho conta" }));
    await preencher("carla@exemplo.com", "errada");
    await userEvent.click(screen.getByRole("button", { name: /^Entrar/ }));

    expect(await screen.findByRole("alert")).toHaveTextContent("E-mail ou senha não conferem.");
    expect(navegacao.replace).not.toHaveBeenCalled();
    expect(lerToken()).toBeNull();
  });
});
