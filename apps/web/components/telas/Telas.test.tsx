import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AvisoDemoProvider } from "@/components/AvisoDemo";
import { CriseProvider } from "@/components/crise/CriseProvider";
import { TemaProvider } from "@/components/TemaProvider";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { Dividas } from "./Dividas";
import { Elpis, RESPOSTA_DEMO } from "./Elpis";
import { Guardiao, ROTA_VERIFICACAO } from "./Guardiao";
import { Inicio, ROTA_METAS } from "./Inicio";
import { Licao } from "./Licao";

const navegacao = vi.hoisted(() => ({ push: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => navegacao,
}));

// jsdom não implementa scrollIntoView.
Element.prototype.scrollIntoView = vi.fn();

// Bundle real do design system, com os provedores que as telas usam.
async function renderizar(tela: ReactNode) {
  render(
    <TemaProvider>
      <PandoraProvider>
        <CriseProvider>
          <AvisoDemoProvider>{tela}</AvisoDemoProvider>
        </CriseProvider>
      </PandoraProvider>
    </TemaProvider>,
  );
  // Espera o bundle: enquanto carrega, "Carregando o PANDORA" também tem role="status".
  await waitFor(() => expect(screen.queryByText("Carregando o PANDORA")).not.toBeInTheDocument());
}

beforeEach(() => navegacao.push.mockClear());

describe("Início", () => {
  it("mostra o Raio-X e abre Metas e previsão", async () => {
    await renderizar(<Inicio />);
    expect(screen.getByRole("heading", { level: 1, name: "Olá, Carla" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Renda de R$ 2.850" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Metas e previsão/ }));
    expect(navegacao.push).toHaveBeenCalledWith(ROTA_METAS);
  });
});

describe("Dívidas", () => {
  it("troca a explicação ao mudar o método", async () => {
    await renderizar(<Dividas />);
    expect(screen.getByText(/Avalanche começa pelo maior custo/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("radio", { name: "Bola de Neve" }));
    expect(screen.getByText(/Bola de Neve começa pelo menor saldo/)).toBeInTheDocument();
  });

  it("avisa que gerar o dossiê ainda é demonstração", async () => {
    await renderizar(<Dividas />);
    await userEvent.click(screen.getByRole("button", { name: /Gerar dossiê em PDF/ }));
    expect(screen.getByRole("status")).toHaveTextContent(/Demonstração/);
  });
});

describe("Elpis", () => {
  it("responde uma pergunta nova com o aviso de demonstração", async () => {
    await renderizar(<Elpis />);
    const campo = screen.getByRole("textbox", { name: "Pergunte à Elpis" });
    await userEvent.type(campo, "Posso parcelar a conta de luz?{Enter}");
    expect(screen.getByText("Posso parcelar a conta de luz?")).toBeInTheDocument();
    expect(screen.getByText(RESPOSTA_DEMO)).toBeInTheDocument();
    expect(campo).toHaveValue("");
  });

  it("o microfone abre o modo voz, e tocar de novo volta à conversa", async () => {
    await renderizar(<Elpis />);
    await userEvent.click(screen.getByRole("button", { name: "Falar com Elpis" }));
    expect(screen.getByRole("heading", { name: "Pode falar, Carla. Estou ouvindo." })).toHaveFocus();
    await userEvent.click(screen.getByRole("button", { name: "Parar de gravar" }));
    expect(screen.getByRole("textbox", { name: "Pergunte à Elpis" })).toBeInTheDocument();
  });
});

describe("Lição", () => {
  it("só segue depois de responder, e explica a resposta", async () => {
    await renderizar(<Licao />);
    const seguir = screen.getByRole("button", { name: /Seguir/ });
    expect(seguir).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: /Fica parado/ }));
    expect(screen.getByRole("heading", { name: "Vale rever este ponto" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Entra no rotativo/ }));
    expect(screen.getByRole("heading", { name: "Isso mesmo" })).toBeInTheDocument();
    expect(seguir).toBeEnabled();
  });
});

describe("Guardião", () => {
  it("abre a verificação do boleto pela aba Golpes", async () => {
    await renderizar(<Guardiao />);
    await userEvent.click(screen.getByRole("button", { name: /Verificar boleto ou print/ }));
    expect(navegacao.push).toHaveBeenCalledWith(ROTA_VERIFICACAO);
  });

  it("a aba Apostas mantém o guia de autoexclusão e o apoio", async () => {
    await renderizar(<Guardiao />);
    await userEvent.click(screen.getByRole("radio", { name: "Apostas" }));
    expect(screen.getByRole("heading", { name: "Travas que você escolhe" })).toBeInTheDocument();
    expect(screen.getAllByRole("switch").map((s) => s.getAttribute("aria-checked"))).toEqual(["true", "false"]);
    expect(screen.getByRole("button", { name: /Autoexclusão das apostas/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Precisa de apoio agora/ })).toBeInTheDocument();
  });
});
