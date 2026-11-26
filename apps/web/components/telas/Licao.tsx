"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { CartoesDeFonte, TextoComCitacoes } from "@/components/CitacoesResposta";
import { ProgressoFluxo } from "@/components/Controlados";
import { ErroApi, explicarResposta, listarEtapas, obterLicao } from "@/lib/api/cliente";
import type { EtapaTrilha, LicaoTrilha, RespostaChat } from "@/lib/api/tipos";
import { usePandora } from "@/lib/pandora/PandoraProvider";
import { concluirLicao, emblemaOuPadrao } from "@/lib/trilha/progresso";

type Carga =
  | { tipo: "carregando" }
  | { tipo: "erro"; mensagem: string }
  | { tipo: "pronta"; licao: LicaoTrilha; etapa: EtapaTrilha | undefined };

type Porque = { tipo: "inicial" } | { tipo: "carregando" } | { tipo: "erro"; mensagem: string } | { tipo: "ok"; resposta: RespostaChat };

const LETRAS = ["A", "B", "C", "D"];

const mensagemDe = (erro: unknown) => (erro instanceof ErroApi ? erro.message : "Algo deu errado. Tente de novo.");

/**
 * Tela 5b da galeria. Passo 1: a explicação com fontes. Depois, uma pergunta por passo.
 * Errar não tira nada: o retorno explica, cita a fonte e a pessoa pode trocar a resposta.
 * "Por quê?" pede à Elpis uma explicação ao vivo da questão.
 */
export function Licao() {
  const { Brasao, QuizOpcao, Cartao, Botao } = usePandora();
  const router = useRouter();
  const id = useSearchParams().get("id");
  const [carga, setCarga] = useState<Carga>({ tipo: "carregando" });
  const [passo, setPasso] = useState(0); // 0 = explicação; 1.. = perguntas
  const [resposta, setResposta] = useState<number | null>(null);
  const [porque, setPorque] = useState<Porque>({ tipo: "inicial" });
  const cancelarPorque = useRef<AbortController | null>(null);

  const [tentativa, setTentativa] = useState(0);
  const tentarDeNovo = () => {
    setCarga({ tipo: "carregando" });
    setTentativa((n) => n + 1);
  };

  useEffect(() => {
    if (!id) return;
    const controle = new AbortController();
    Promise.all([obterLicao(id, controle.signal), listarEtapas(controle.signal).catch(() => [] as EtapaTrilha[])])
      .then(([licao, etapas]) => setCarga({ tipo: "pronta", licao, etapa: etapas.find((e) => e.licao_id === licao.id) }))
      .catch((erro: unknown) => {
        if (!controle.signal.aborted) setCarga({ tipo: "erro", mensagem: mensagemDe(erro) });
      });
    return () => controle.abort();
  }, [id, tentativa]);
  useEffect(() => () => cancelarPorque.current?.abort(), []);

  const voltar = () => router.push("/trilha");

  const situacao: Carga = id ? carga : { tipo: "erro", mensagem: "Escolha uma lição na trilha." };
  if (situacao.tipo !== "pronta") {
    return (
      <div className="pd-pergunta-tela">
        {situacao.tipo === "carregando" ? (
          <p className="pd-apoio app-consultando" role="status">
            Carregando a lição…
          </p>
        ) : (
          <Cartao tom="alerta" titulo="Não consegui abrir a lição">
            <p role="alert">{situacao.mensagem}</p>
            <Botao variante="secundario" onClick={tentarDeNovo}>
              Tentar de novo
            </Botao>
          </Cartao>
        )}
        <div className="pd-empurra" />
        <Botao bloco variante="fantasma" onClick={voltar}>
          Voltar à trilha
        </Botao>
      </div>
    );
  }

  const { licao, etapa } = situacao;
  const total = 1 + licao.perguntas.length;
  const pergunta = passo > 0 ? licao.perguntas[passo - 1] : undefined;
  const cabecalho = `Etapa ${etapa?.n ?? ""}${etapa ? " · " : ""}${licao.titulo}`;
  const fontesDe = (numeros: number[]) => licao.fontes.filter((f) => numeros.includes(f.n));

  function escolher(indice: number) {
    cancelarPorque.current?.abort();
    setResposta(indice);
    setPorque({ tipo: "inicial" });
  }

  function perguntarPorque() {
    if (resposta === null) return;
    cancelarPorque.current?.abort();
    const controle = new AbortController();
    cancelarPorque.current = controle;
    setPorque({ tipo: "carregando" });
    explicarResposta(licao.id, passo - 1, resposta, controle.signal)
      .then((r) => setPorque({ tipo: "ok", resposta: r }))
      .catch((erro: unknown) => {
        if (!controle.signal.aborted) setPorque({ tipo: "erro", mensagem: mensagemDe(erro) });
      });
  }

  function seguir() {
    if (passo < licao.perguntas.length) {
      setPasso(passo + 1);
      setResposta(null);
      setPorque({ tipo: "inicial" });
      return;
    }
    concluirLicao(licao.id);
    voltar();
  }

  function estado(indice: number): "neutra" | "certa" | "revisar" {
    if (resposta === null || !pergunta) return "neutra";
    if (indice === pergunta.certa) return "certa";
    return indice === resposta ? "revisar" : "neutra";
  }

  return (
    <div className="pd-pergunta-tela">
      <ProgressoFluxo passo={passo + 1} total={total} onVoltar={passo === 0 ? voltar : () => setPasso(passo - 1)} />
      <div className="pd-linha" style={{ justifyContent: "flex-start" }}>
        <Brasao emblema={emblemaOuPadrao(etapa?.emblema)} estado="atual" tamanho={44} />
        <p className="pd-apoio" style={{ fontWeight: 700 }}>
          {cabecalho}
        </p>
      </div>

      {!pergunta ? (
        <>
          <h1 className="pd-cartao-titulo" style={{ fontSize: 24, lineHeight: "30px" }}>
            {licao.titulo}
          </h1>
          <TextoComCitacoes texto={licao.explicacao} citacoes={licao.fontes} base="licao" />
          <CartoesDeFonte citacoes={fontesDe(licao.citacoes_explicacao)} base="licao" />
          <div className="pd-empurra" />
          <Botao bloco seta onClick={seguir}>
            Começar as perguntas
          </Botao>
        </>
      ) : (
        <>
          <h1 className="pd-cartao-titulo" style={{ fontSize: 24, lineHeight: "30px" }}>
            {pergunta.enunciado}
          </h1>
          {pergunta.opcoes.map((texto, i) => (
            <QuizOpcao key={texto} letra={LETRAS[i] ?? String(i + 1)} estado={estado(i)} onClick={() => escolher(i)}>
              {texto}
            </QuizOpcao>
          ))}
          <div aria-live="polite">
            {resposta !== null ? (
              <Cartao
                tom={resposta === pergunta.certa ? "ok" : "apoio"}
                titulo={resposta === pergunta.certa ? "Isso mesmo" : "Vale rever este ponto"}
              >
                <TextoComCitacoes texto={pergunta.feedback} citacoes={licao.fontes} base={`p${passo}`} />
                <CartoesDeFonte citacoes={fontesDe(pergunta.citacoes)} base={`p${passo}`} />
                {porque.tipo === "inicial" ? (
                  <Botao variante="secundario" onClick={perguntarPorque}>
                    Por quê?
                  </Botao>
                ) : null}
              </Cartao>
            ) : null}
            {porque.tipo === "carregando" ? (
              <p className="pd-apoio app-consultando" role="status">
                A Elpis está consultando as fontes…
              </p>
            ) : null}
            {porque.tipo === "erro" ? (
              <Cartao tom="alerta" titulo="Não consegui explicar agora">
                <p role="alert">{porque.mensagem}</p>
                <Botao variante="secundario" onClick={perguntarPorque}>
                  Tentar de novo
                </Botao>
              </Cartao>
            ) : null}
            {porque.tipo === "ok" ? (
              <Cartao titulo="A Elpis explica">
                <TextoComCitacoes texto={porque.resposta.texto} citacoes={porque.resposta.citacoes} base={`porque${passo}`} />
                <CartoesDeFonte citacoes={porque.resposta.citacoes} base={`porque${passo}`} />
              </Cartao>
            ) : null}
          </div>
          <div className="pd-empurra" />
          <Botao bloco seta desativado={resposta === null} onClick={seguir}>
            {passo === licao.perguntas.length ? "Concluir lição" : "Seguir"}
          </Botao>
        </>
      )}
    </div>
  );
}
