import { afterEach, describe, expect, it, vi } from "vitest";
import { CHAVE_SESSAO, guardarSessao, lerToken } from "@/lib/conta/sessao";
import {
  corrigirCategoria,
  enviarExtrato,
  entrar,
  ErroApi,
  explicarResposta,
  listarEtapas,
  listarTransacoes,
  obterLicao,
  obterRaioX,
  perguntarElpis,
  registrarConsentimento,
  sair,
  URL_API,
} from "./cliente";

const json = (corpo: unknown, status = 200) => new Response(JSON.stringify(corpo), { status });

afterEach(() => vi.unstubAllGlobals());

describe("cliente da API", () => {
  it("envia a pergunta ao chat e devolve a resposta", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(json({ texto: "ok", abstencao: false, citacoes: [], crise: false, modelo: "m" }));
    vi.stubGlobal("fetch", fetchFalso);
    const r = await perguntarElpis("Posso?");
    expect(r.texto).toBe("ok");
    const [url, init] = fetchFalso.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`${URL_API}/chat`);
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string)).toEqual({ pergunta: "Posso?" });
  });

  it("monta as rotas da trilha e protege o id na URL", async () => {
    const fetchFalso = vi.fn().mockImplementation(() => Promise.resolve(json([])));
    vi.stubGlobal("fetch", fetchFalso);
    await listarEtapas();
    await obterLicao("a/b");
    await explicarResposta("rotativo", 1, 2);
    expect(fetchFalso.mock.calls.map((c) => c[0])).toEqual([
      `${URL_API}/trilha`,
      `${URL_API}/trilha/licoes/a%2Fb`,
      `${URL_API}/trilha/licoes/rotativo/porque`,
    ]);
    expect(JSON.parse((fetchFalso.mock.calls[2][1] as RequestInit).body as string)).toEqual({ pergunta_idx: 1, opcao: 2 });
  });

  it.each([
    [503, /não está disponível/],
    [404, /Não encontrei/],
    [500, /Algo deu errado/],
  ])("traduz o status %i em uma mensagem legível", async (status, mensagem) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(json({ title: "x", status }, status)));
    await expect(perguntarElpis("q")).rejects.toMatchObject({ status, message: expect.stringMatching(mensagem) });
  });

  it("explica a falha de rede sem expor o erro técnico", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    const erro = await perguntarElpis("q").catch((e: unknown) => e);
    expect(erro).toBeInstanceOf(ErroApi);
    expect((erro as ErroApi).status).toBeNull();
    expect((erro as ErroApi).message).toMatch(/servidor/);
  });

  it("repassa o cancelamento da tela como está", async () => {
    const controle = new AbortController();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((_u: string, init: RequestInit) => {
        return new Promise((_ok, falha) => init.signal?.addEventListener("abort", () => falha(new DOMException("x", "AbortError"))));
      }),
    );
    const pedido = perguntarElpis("q", controle.signal);
    controle.abort();
    await expect(pedido).rejects.toMatchObject({ name: "AbortError" });
  });

  describe("conta e dados (#71)", () => {
    const comSessao = () => guardarSessao({ token: "tk", expira_em: "2099-01-01T00:00:00Z" });
    const cabecalhos = (f: ReturnType<typeof vi.fn>, i = 0) => (f.mock.calls[i][1] as RequestInit).headers as Record<string, string>;

    it("manda o token quando há sessão, e não manda quando não há", async () => {
      const fetchFalso = vi.fn().mockImplementation(() => Promise.resolve(json([])));
      vi.stubGlobal("fetch", fetchFalso);
      await listarEtapas();
      expect(cabecalhos(fetchFalso).Authorization).toBeUndefined();
      comSessao();
      await listarEtapas();
      expect(cabecalhos(fetchFalso, 1).Authorization).toBe("Bearer tk");
    });

    it("envia o extrato como multipart, sem forçar JSON", async () => {
      comSessao();
      const fetchFalso = vi.fn().mockResolvedValue(json({ id: "e", nome_arquivo: "x.csv", status: "concluido", avisos: [], recebido_em: "" }));
      vi.stubGlobal("fetch", fetchFalso);
      await enviarExtrato(new File(["data,valor"], "x.csv", { type: "text/csv" }));
      const init = fetchFalso.mock.calls[0][1] as RequestInit;
      expect(init.body).toBeInstanceOf(FormData);
      expect((init.body as FormData).get("arquivo")).toBeInstanceOf(File);
      expect(cabecalhos(fetchFalso)["Content-Type"]).toBeUndefined();
    });

    it("monta a query das transações e do Raio-X", async () => {
      const fetchFalso = vi.fn().mockImplementation(() => Promise.resolve(json({})));
      vi.stubGlobal("fetch", fetchFalso);
      await listarTransacoes({ mes: "2026-10", porPagina: 200 });
      await listarTransacoes();
      await obterRaioX("2026-10");
      await corrigirCategoria("t/1", "MORADIA");
      expect(fetchFalso.mock.calls.map((c) => c[0])).toEqual([
        `${URL_API}/transacoes?mes=2026-10&por_pagina=200`,
        `${URL_API}/transacoes`,
        `${URL_API}/raio-x?mes=2026-10`,
        `${URL_API}/transacoes/t%2F1/categoria`,
      ]);
      expect((fetchFalso.mock.calls[3][1] as RequestInit).method).toBe("PATCH");
    });

    it("registra o consentimento com a finalidade e a versão do termo", async () => {
      const fetchFalso = vi.fn().mockResolvedValue(json({}, 201));
      vi.stubGlobal("fetch", fetchFalso);
      await registrarConsentimento();
      expect(JSON.parse((fetchFalso.mock.calls[0][1] as RequestInit).body as string)).toEqual({
        finalidade: "diagnostico_financeiro",
        versao_termo: "2026-11",
      });
    });

    it("aceita 204 sem corpo ao sair", async () => {
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 204 })));
      await expect(sair()).resolves.toBeUndefined();
    });

    it("esquece a sessão quando a API diz que ela venceu", async () => {
      comSessao();
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue(json({ title: "x", status: 401 }, 401)));
      await expect(listarTransacoes()).rejects.toMatchObject({ status: 401, message: expect.stringMatching(/Entre de novo/) });
      expect(lerToken()).toBeNull();
      expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull();
    });

    it("diz que e-mail ou senha não conferem no login recusado", async () => {
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue(json({ title: "x", status: 401 }, 401)));
      await expect(entrar("a@b.com", "errada")).rejects.toMatchObject({ message: "E-mail ou senha não conferem." });
    });

    it("mostra o título do problema quando falta consentimento", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue(json({ title: "Falta o seu consentimento.", status: 403, detail: "POST /consentimentos" }, 403)),
      );
      await expect(listarTransacoes()).rejects.toMatchObject({ message: "Falta o seu consentimento." });
    });
  });
});
