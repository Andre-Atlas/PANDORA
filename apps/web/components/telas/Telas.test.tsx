import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { StrictMode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AvisoDemoProvider } from "@/components/AvisoDemo";
import { CHAVE_CRISE, CriseProvider } from "@/components/crise/CriseProvider";
import { TemaProvider } from "@/components/TemaProvider";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { CHAVE_TRILHA } from "@/lib/trilha/progresso";
import { ETAPAS, json, LICAO, RESPOSTA, simularApi } from "@/test/apiFalsa";
import { Dividas } from "./Dividas";
import { Elpis } from "./Elpis";
import { Guardiao, ROTA_VERIFICACAO } from "./Guardiao";
import { Inicio, ROTA_METAS } from "./Inicio";
import { Licao } from "./Licao";
import { rotaDaLicao, Trilha } from "./Trilha";

const navegacao = vi.hoisted(() => ({ push: vi.fn(), prefetch: vi.fn() }));
const busca = vi.hoisted(() => ({ atual: "id=rotativo" }));
vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => navegacao,
  useSearchParams: () => new URLSearchParams(busca.atual),
}));

// jsdom não implementa scrollIntoView.
Element.prototype.scrollIntoView = vi.fn();

// Bundle real do design system, com os provedores que as telas usam.
async function renderizar(tela: ReactNode) {
  // StrictMode como no `next dev`: monta, desmonta e monta de novo, o que expõe efeitos mal limpos
  render(
    <StrictMode>
      <TemaProvider>
        <PandoraProvider>
          <CriseProvider>
            <AvisoDemoProvider>{tela}</AvisoDemoProvider>
          </CriseProvider>
        </PandoraProvider>
      </TemaProvider>
    </StrictMode>,
  );
  // Espera o bundle: enquanto carrega, "Carregando o PANDORA" também tem role="status".
  await waitFor(() => expect(screen.queryByText("Carregando o PANDORA")).not.toBeInTheDocument());
}

beforeEach(() => {
  navegacao.push.mockClear();
  busca.atual = "id=rotativo";
  localStorage.clear();
  sessionStorage.clear();
});
afterEach(() => vi.unstubAllGlobals());

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
  async function perguntar(texto: string) {
    const campo = screen.getByRole("textbox", { name: "Pergunte à Elpis" });
    await userEvent.type(campo, `${texto}{Enter}`);
    return campo;
  }

  it("responde com o texto, o marcador da fonte e o cartão com o link oficial", async () => {
    const api = simularApi({ "POST /chat": () => json(RESPOSTA) });
    await renderizar(<Elpis />);
    const campo = await perguntar("Qual o prazo do plano?");
    expect(screen.getByText("Qual o prazo do plano?")).toBeInTheDocument();
    expect(await screen.findByText(/O plano pode durar até cinco anos/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ver a fonte 1" })).toHaveAttribute("href", expect.stringContaining("-fonte-1"));
    expect(screen.getByText(/Lei 14.181\/2021, Art. 104-A/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Ler no Planalto/ })).toHaveAttribute("href", expect.stringContaining("planalto.gov.br"));
    expect(api.chamadas).toEqual([{ rota: "POST /chat", corpo: { pergunta: "Qual o prazo do plano?" } }]);
    expect(campo).toHaveValue("");
  });

  it("mostra 'Sem fonte suficiente' quando a Elpis se abstém", async () => {
    simularApi({ "POST /chat": () => json({ ...RESPOSTA, texto: "Não encontrei isso nas fontes oficiais.", abstencao: true, citacoes: [] }) });
    await renderizar(<Elpis />);
    await perguntar("Devo comprar bitcoin?");
    expect(await screen.findByText("Sem fonte suficiente")).toBeInTheDocument();
    expect(screen.getByText("Não encontrei isso nas fontes oficiais.")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Ler no/ })).not.toBeInTheDocument();
  });

  it("abre o fluxo de crise quando a resposta traz sinal de crise", async () => {
    simularApi({ "POST /chat": () => json({ ...RESPOSTA, texto: "Sinto muito que esteja tão pesado.", abstencao: true, citacoes: [], crise: true }) });
    await renderizar(<Elpis />);
    await perguntar("não aguento mais, quero sumir");
    expect(await screen.findByText("Apoio agora")).toBeInTheDocument();
    expect(sessionStorage.getItem(CHAVE_CRISE)).toBe("1");
  });

  it("bloqueia o campo enquanto espera e mostra que está consultando as fontes", async () => {
    let liberar: (r: Response) => void = () => {};
    simularApi({ "POST /chat": () => new Promise<Response>((ok) => (liberar = ok)) });
    await renderizar(<Elpis />);
    const campo = await perguntar("Qual o prazo?");
    expect(await screen.findByText(/Consultando as fontes oficiais/)).toBeInTheDocument();
    expect(campo).toBeDisabled();
    liberar(json(RESPOSTA));
    expect(await screen.findByText(/O plano pode durar/)).toBeInTheDocument();
    expect(campo).toBeEnabled();
  });

  it("explica a falha e deixa tentar de novo", async () => {
    let falhar = true;
    simularApi({ "POST /chat": () => (falhar ? json({ title: "x", status: 503 }, 503) : json(RESPOSTA)) });
    await renderizar(<Elpis />);
    await perguntar("Qual o prazo?");
    expect(await screen.findByRole("alert")).toHaveTextContent(/não está disponível/);
    falhar = false;
    await userEvent.click(screen.getByRole("button", { name: "Tentar de novo" }));
    expect(await screen.findByText(/O plano pode durar/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("uma sugestão envia a pergunta pronta", async () => {
    const api = simularApi({ "POST /chat": () => json(RESPOSTA) });
    await renderizar(<Elpis />);
    await userEvent.click(screen.getByRole("button", { name: "O que é o mínimo existencial?" }));
    expect(await screen.findByText(/O plano pode durar/)).toBeInTheDocument();
    expect(api.chamadas[0].corpo).toEqual({ pergunta: "O que é o mínimo existencial?" });
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
  const api = () =>
    simularApi({
      "GET /trilha/licoes/rotativo": () => json(LICAO),
      "GET /trilha": () => json(ETAPAS),
      "POST /trilha/licoes/rotativo/porque": () => json({ ...RESPOSTA, texto: "Porque a lei fixa esse teto [1]." }),
    });

  async function abrirPergunta() {
    await renderizar(<Licao />);
    await screen.findByRole("heading", { name: "Rotativo" });
    await userEvent.click(screen.getByRole("button", { name: /Começar as perguntas/ }));
  }

  it("mostra a explicação com a fonte antes das perguntas", async () => {
    api();
    await renderizar(<Licao />);
    expect(await screen.findByRole("heading", { name: "Rotativo" })).toBeInTheDocument();
    expect(screen.getByText(/não passam do valor original/)).toBeInTheDocument();
    expect(screen.getByText("Etapa 3 · Rotativo")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Ler no Planalto/ })).toBeInTheDocument();
  });

  it("só segue depois de responder, explica o erro com a fonte e permite trocar a resposta", async () => {
    api();
    await abrirPergunta();
    const seguir = screen.getByRole("button", { name: /Concluir lição/ });
    expect(seguir).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: /Não há teto/ }));
    expect(screen.getByRole("heading", { name: "Vale rever este ponto" })).toBeInTheDocument();
    expect(screen.getByText(/não pode exceder o valor original/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /O valor original da dívida/ }));
    expect(screen.getByRole("heading", { name: "Isso mesmo" })).toBeInTheDocument();
    expect(seguir).toBeEnabled();
  });

  it("'Por quê?' pede a explicação à Elpis com a opção escolhida", async () => {
    const simulada = api();
    await abrirPergunta();
    await userEvent.click(screen.getByRole("button", { name: /O dobro da dívida/ }));
    await userEvent.click(screen.getByRole("button", { name: "Por quê?" }));
    expect(await screen.findByRole("heading", { name: "A Elpis explica" })).toBeInTheDocument();
    expect(screen.getByText(/Porque a lei fixa esse teto/)).toBeInTheDocument();
    expect(simulada.chamadas.find((c) => c.rota.endsWith("/porque"))?.corpo).toEqual({ pergunta_idx: 0, opcao: 1 });
  });

  it("concluir guarda o progresso neste navegador e volta à trilha", async () => {
    api();
    await abrirPergunta();
    await userEvent.click(screen.getByRole("button", { name: /O valor original da dívida/ }));
    await userEvent.click(screen.getByRole("button", { name: /Concluir lição/ }));
    expect(JSON.parse(localStorage.getItem(CHAVE_TRILHA) ?? "[]")).toEqual(["rotativo"]);
    expect(navegacao.push).toHaveBeenCalledWith("/trilha");
  });

  it("avisa quando a lição não existe e oferece voltar", async () => {
    simularApi({ "GET /trilha/licoes/rotativo": () => json({ title: "x", status: 404 }, 404), "GET /trilha": () => json(ETAPAS) });
    await renderizar(<Licao />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/Não encontrei isso/);
    await userEvent.click(screen.getByRole("button", { name: "Voltar à trilha" }));
    expect(navegacao.push).toHaveBeenCalledWith("/trilha");
  });

  it("sem id na URL pede para escolher uma lição", async () => {
    busca.atual = "";
    api();
    await renderizar(<Licao />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/Escolha uma lição/);
  });
});

describe("Trilha", () => {
  it("carrega as etapas da API e continua da primeira pendente", async () => {
    localStorage.setItem(CHAVE_TRILHA, JSON.stringify(["minimo-existencial"]));
    simularApi({ "GET /trilha": () => json(ETAPAS) });
    await renderizar(<Trilha />);
    expect(await screen.findByText(/1 de 3 etapas concluídas/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Juros e CET" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Continuar lição/ }));
    expect(navegacao.push).toHaveBeenCalledWith(rotaDaLicao("juros-e-cet"));
    expect(screen.getByRole("heading", { name: "conheço meus direitos" })).toBeInTheDocument();
  });

  it("na primeira visita oferece 'Começar lição'", async () => {
    simularApi({ "GET /trilha": () => json(ETAPAS) });
    await renderizar(<Trilha />);
    expect(await screen.findByText(/0 de 3 etapas concluídas/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Começar lição/ })).toBeInTheDocument();
  });

  it("com tudo concluído mostra a trilha completa", async () => {
    localStorage.setItem(CHAVE_TRILHA, JSON.stringify(ETAPAS.map((e) => e.licao_id)));
    simularApi({ "GET /trilha": () => json(ETAPAS) });
    await renderizar(<Trilha />);
    expect(await screen.findByRole("heading", { name: "Trilha concluída" })).toBeInTheDocument();
  });

  it("explica a falha e deixa tentar de novo", async () => {
    let falhar = true;
    simularApi({ "GET /trilha": () => (falhar ? json({ title: "x", status: 500 }, 500) : json(ETAPAS)) });
    await renderizar(<Trilha />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/Algo deu errado/);
    falhar = false;
    await userEvent.click(screen.getByRole("button", { name: "Tentar de novo" }));
    expect(await screen.findByText(/0 de 3 etapas concluídas/)).toBeInTheDocument();
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
