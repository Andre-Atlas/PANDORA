import { afterEach, describe, expect, it, vi } from "vitest";
import { ErroApi, explicarResposta, listarEtapas, obterLicao, perguntarElpis, URL_API } from "./cliente";

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
});
