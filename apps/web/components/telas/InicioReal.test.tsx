import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StrictMode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ROTA_ENTRAR } from "@/components/conta/PortaoConta";
import { TemaProvider } from "@/components/TemaProvider";
import { lerToken } from "@/lib/conta/sessao";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { json, ligarDadosReais, NAO_IMPLEMENTADO, pagina, RAIO_X, simularApi, TRANSACOES } from "@/test/apiFalsa";
import { Inicio } from "./Inicio";

const navegacao = vi.hoisted(() => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => "/inicio",
  useRouter: () => navegacao,
}));

async function renderizar() {
  render(
    <StrictMode>
      <TemaProvider>
        <PandoraProvider>
          <Inicio />
        </PandoraProvider>
      </TemaProvider>
    </StrictMode>,
  );
  await waitFor(() => expect(screen.queryByText("Carregando o PANDORA")).not.toBeInTheDocument());
}

/** API com um mês de transações; `transacoes` pode mudar durante o teste (envio, correção). */
function apiComMes(transacoes = TRANSACOES, extras: Parameters<typeof simularApi>[0] = {}) {
  return simularApi({
    "GET /transacoes": () => pagina(transacoes),
    "GET /raio-x": () => json(RAIO_X),
    "GET /score": NAO_IMPLEMENTADO,
    ...extras,
  });
}

beforeEach(() => {
  navegacao.push.mockClear();
  navegacao.replace.mockClear();
});
afterEach(() => vi.unstubAllGlobals());

describe("Início com dados reais", () => {
  it("sem a variável ligada, continua com a demonstração e não chama a API", async () => {
    const api = simularApi({});
    await renderizar();
    expect(screen.getByRole("heading", { level: 1, name: "Olá, Carla" })).toBeInTheDocument();
    expect(api.chamadas).toEqual([]);
  });

  it("mostra o Raio-X do mês da transação mais recente, com o selo Calculado", async () => {
    ligarDadosReais({ comSessao: true });
    const api = apiComMes();
    await renderizar();

    expect(await screen.findByRole("heading", { name: /Renda de R\$\s2\.850,00/ })).toBeInTheDocument();
    expect(screen.getByText("Protegido em outubro de 2026")).toBeInTheDocument();
    expect(screen.getAllByText("Calculado").length).toBeGreaterThan(0);
    expect(screen.getByText("Para onde foi o dinheiro")).toBeInTheDocument();
    expect(await screen.findByText(/O score ainda não está pronto/)).toBeInTheDocument();
    expect(screen.queryByText(/Carla/)).not.toBeInTheDocument();

    const raioX = api.pedidos.find((c) => c.rota === "GET /raio-x");
    expect(raioX?.busca).toBe("?mes=2026-10");
    expect(api.pedidos.filter((c) => c.rota === "GET /transacoes").map((c) => c.busca)).toContain(
      "?mes=2026-10&por_pagina=200",
    );
    const autorizacao = (api.pedidos[0].init?.headers as Record<string, string>).Authorization;
    expect(autorizacao).toBe("Bearer token-de-teste");
  });

  it("sem transações, pede o primeiro extrato e mostra o Raio-X depois do envio", async () => {
    ligarDadosReais({ comSessao: true });
    let transacoes: typeof TRANSACOES = [];
    const api = apiComMes(undefined, {
      "GET /transacoes": () => pagina(transacoes),
      "POST /extratos": () => {
        transacoes = TRANSACOES;
        return json(
          { id: "e-1", nome_arquivo: "outubro.csv", status: "concluido", transacoes_importadas: 3, avisos: [], recebido_em: "" },
          202,
        );
      },
    });
    await renderizar();

    expect(await screen.findByRole("heading", { name: "Envie um extrato ou fatura" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /Renda de/ })).not.toBeInTheDocument();

    const arquivo = new File(["data,valor,descricao\n2026-10-05,2850.00,SALARIO\n"], "outubro.csv", { type: "text/csv" });
    await userEvent.upload(screen.getByLabelText("Extrato ou fatura"), arquivo);

    expect(await screen.findByText(/outubro\.csv: 3 transações lidas/)).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: /Renda de R\$\s2\.850,00/ })).toBeInTheDocument();
    const envio = api.chamadas.find((c) => c.rota === "POST /extratos");
    expect((envio?.corpo as FormData).get("arquivo")).toBeInstanceOf(File);
  });

  it("mostra o erro do envio sem perder a tela", async () => {
    ligarDadosReais({ comSessao: true });
    apiComMes([], {
      "POST /extratos": () => json({ title: "Falta o seu consentimento.", status: 403 }, 403),
    });
    await renderizar();
    await screen.findByRole("heading", { name: "Envie um extrato ou fatura" });
    await userEvent.upload(screen.getByLabelText("Extrato ou fatura"), new File(["x"], "x.csv", { type: "text/csv" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Falta o seu consentimento.");
  });

  it("corrige a categoria com um toque e refaz o Raio-X", async () => {
    ligarDadosReais({ comSessao: true });
    const api = apiComMes(TRANSACOES, {
      "PATCH /transacoes/t-3/categoria": (corpo) =>
        json({ ...TRANSACOES[0], categoria: (corpo as { categoria: string }).categoria, origem_categoria: "pessoa" }),
    });
    await renderizar();

    const seletor = await screen.findByRole("combobox", { name: /Categoria de PARCELA EMPRESTIMO PESSOAL/ });
    expect(seletor).toHaveValue("TRANSFERENCIA");
    const antes = api.chamadas.filter((c) => c.rota === "GET /raio-x").length;

    await userEvent.selectOptions(seletor, "DIVIDA_JUROS");

    expect(seletor).toHaveValue("DIVIDA_JUROS");
    expect(await screen.findByText("PARCELA EMPRESTIMO PESSOAL: agora em Dívidas e juros.")).toBeInTheDocument();
    expect(api.chamadas.find((c) => c.rota === "PATCH /transacoes/t-3/categoria")?.corpo).toEqual({ categoria: "DIVIDA_JUROS" });
    await waitFor(() => expect(api.chamadas.filter((c) => c.rota === "GET /raio-x").length).toBeGreaterThan(antes));
  });

  it("desfaz a escolha quando a correção falha", async () => {
    ligarDadosReais({ comSessao: true });
    apiComMes(TRANSACOES, {
      "PATCH /transacoes/t-3/categoria": () => json({ title: "x", status: 500 }, 500),
    });
    await renderizar();
    const seletor = await screen.findByRole("combobox", { name: /Categoria de PARCELA EMPRESTIMO PESSOAL/ });
    await userEvent.selectOptions(seletor, "LAZER");
    expect(await screen.findByText(/Não consegui corrigir/)).toBeInTheDocument();
    expect(seletor).toHaveValue("TRANSFERENCIA");
  });

  it("com a sessão vencida, oferece entrar de novo", async () => {
    ligarDadosReais({ comSessao: true });
    simularApi({ "GET /transacoes": () => json({ title: "x", status: 401 }, 401), "GET /score": NAO_IMPLEMENTADO });
    await renderizar();
    const cartao = (await screen.findByText("Não consegui abrir o seu mês")).closest("section") as HTMLElement;
    await userEvent.click(within(cartao).getByRole("button", { name: "Entrar de novo" }));
    expect(navegacao.replace).toHaveBeenCalledWith(ROTA_ENTRAR);
  });

  it("sai da conta, apaga a sessão e volta ao login", async () => {
    ligarDadosReais({ comSessao: true });
    const api = apiComMes(TRANSACOES, { "DELETE /auth/sessoes/atual": () => new Response(null, { status: 204 }) });
    await renderizar();
    await screen.findByRole("heading", { name: /Renda de/ });
    await userEvent.click(screen.getByRole("button", { name: "Sair da conta" }));
    await waitFor(() => expect(navegacao.replace).toHaveBeenCalledWith(ROTA_ENTRAR));
    expect(api.chamadas.some((c) => c.rota === "DELETE /auth/sessoes/atual")).toBe(true);
    expect(lerToken()).toBeNull();
  });
});
