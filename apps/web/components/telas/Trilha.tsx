"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErroApi, listarEtapas } from "@/lib/api/cliente";
import { usePandora } from "@/lib/pandora/PandoraProvider";
import { comEstado, lerConcluidas, type EtapaComEstado } from "@/lib/trilha/progresso";

export const ROTA_LICAO = "/trilha/licao";

/** Endereço da lição de uma etapa. O id vai na query: a tela da lição busca o conteúdo na API. */
export const rotaDaLicao = (licaoId: string) => `${ROTA_LICAO}?id=${encodeURIComponent(licaoId)}`;

type Situacao =
  | { tipo: "carregando" }
  | { tipo: "erro"; mensagem: string }
  | { tipo: "pronta"; etapas: EtapaComEstado[] };

/**
 * Tela 5a da galeria. As etapas vêm da API (conteúdo gerado pelo RAG, com fontes).
 * O progresso (concluídas, atual e próximas) fica só neste navegador.
 */
export function Trilha() {
  const { CabecalhoMito, TrilhaCaminho, Cartao, Botao } = usePandora();
  const router = useRouter();
  const [situacao, setSituacao] = useState<Situacao>({ tipo: "carregando" });

  const [tentativa, setTentativa] = useState(0);
  const tentarDeNovo = () => {
    setSituacao({ tipo: "carregando" });
    setTentativa((n) => n + 1);
  };

  useEffect(() => {
    router.prefetch(ROTA_LICAO);
  }, [router]);

  useEffect(() => {
    const controle = new AbortController();
    listarEtapas(controle.signal)
      .then((etapas) => setSituacao({ tipo: "pronta", etapas: comEstado(etapas, lerConcluidas()) }))
      .catch((erro: unknown) => {
        if (controle.signal.aborted) return;
        setSituacao({ tipo: "erro", mensagem: erro instanceof ErroApi ? erro.message : "Algo deu errado. Tente de novo." });
      });
    return () => controle.abort();
  }, [tentativa]);

  if (situacao.tipo !== "pronta") {
    return (
      <>
        <CabecalhoMito titulo="Da caixa à esperança">
          <p className="pd-mito-sub">Sem prazo, no seu ritmo</p>
        </CabecalhoMito>
        <div className="pd-corpo">
          {situacao.tipo === "carregando" ? (
            <p className="pd-apoio app-consultando" role="status">
              Carregando a trilha…
            </p>
          ) : (
            <Cartao tom="alerta" titulo="Não consegui abrir a trilha">
              <p role="alert">{situacao.mensagem}</p>
              <Botao variante="secundario" onClick={tentarDeNovo}>
                Tentar de novo
              </Botao>
            </Cartao>
          )}
        </div>
      </>
    );
  }

  const { etapas } = situacao;
  const feitas = etapas.filter((e) => e.estado === "feito").length;
  const atual = etapas.find((e) => e.estado === "atual");
  const marco = etapas.find((e) => e.estado === "proximo" && e.marco);

  return (
    <>
      <CabecalhoMito titulo="Da caixa à esperança">
        <p className="pd-mito-sub">
          {feitas} de {etapas.length} etapas concluídas · sem prazo, no seu ritmo
        </p>
      </CabecalhoMito>
      <div className="pd-corpo">
        <TrilhaCaminho etapas={etapas} />
        {atual ? (
          <Cartao sobre={`Etapa ${atual.n} · cerca de 4 minutos`} titulo={atual.t}>
            <p>Cada resposta vem com a fonte oficial. Você pode refazer qualquer lição quando quiser.</p>
            <Botao bloco seta onClick={() => router.push(rotaDaLicao(atual.licao_id))}>
              {feitas ? "Continuar lição" : "Começar lição"}
            </Botao>
          </Cartao>
        ) : (
          <Cartao tom="ok" titulo="Trilha concluída">
            <p>Você passou pelas seis etapas. Pode rever qualquer lição quando quiser.</p>
          </Cartao>
        )}
        {marco?.marco ? (
          <Cartao tom="apoio" marco sobre="Próximo marco" titulo={marco.marco.replace(/^Marco:\s*/, "")}>
            <p>
              Chega com a etapa {marco.n}, {marco.t}. Fica com você depois de conquistado.
            </p>
          </Cartao>
        ) : null}
      </div>
    </>
  );
}
