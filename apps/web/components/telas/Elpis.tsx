"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { CampoPerguntaApp } from "@/components/Controlados";
import { CartoesDeFonte, TextoComCitacoes } from "@/components/CitacoesResposta";
import { useCrise } from "@/components/crise/CriseProvider";
import { ErroApi, perguntarElpis } from "@/lib/api/cliente";
import type { RespostaChat } from "@/lib/api/tipos";
import { PESSOA } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

/** Perguntas que mostram o que a Elpis sabe responder com fonte. */
export const SUGESTOES = [
  "Podem bloquear meu salário por dívida de cartão?",
  "O que é o mínimo existencial?",
  "Existe limite para os juros do rotativo?",
];

type Mensagem =
  | { id: number; autor: "voce"; texto: string }
  | { id: number; autor: "elpis"; estado: "enviando" }
  | { id: number; autor: "elpis"; estado: "erro"; erro: string; pergunta: string }
  | { id: number; autor: "elpis"; estado: "ok"; resposta: RespostaChat };

/**
 * Tela 4 da galeria. A Elpis responde de verdade: a pergunta vai ao RAG pela API,
 * e a resposta volta com as fontes oficiais ou com a abstenção "Sem fonte suficiente".
 * O microfone abre o modo voz (4c).
 */
export function Elpis() {
  const [ouvindo, setOuvindo] = useState(false);
  return ouvindo ? <ModoVoz onTerminar={() => setOuvindo(false)} /> : <Conversa onVoz={() => setOuvindo(true)} />;
}

function Conversa({ onVoz }: { onVoz: () => void }) {
  const { CabecalhoElpis, Balao, Friso, Selo, Botao } = usePandora();
  const avisar = useAvisoDemo();
  const { abrirCrise } = useCrise();
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const proximoId = useRef(0);
  const cancelar = useRef(new AbortController());
  const fim = useRef<HTMLDivElement>(null);

  const ocupada = mensagens.some((m) => m.autor === "elpis" && m.estado === "enviando");

  useEffect(() => {
    const controle = cancelar.current;
    return () => controle.abort();
  }, []);

  useEffect(() => {
    if (mensagens.length) fim.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mensagens]);

  const responder = useCallback(
    async (idElpis: number, pergunta: string) => {
      const trocar = (nova: Mensagem) => setMensagens((lista) => lista.map((m) => (m.id === idElpis ? nova : m)));
      try {
        const resposta = await perguntarElpis(pergunta, cancelar.current.signal);
        trocar({ id: idElpis, autor: "elpis", estado: "ok", resposta });
        if (resposta.crise) abrirCrise();
      } catch (erro) {
        if (cancelar.current.signal.aborted) return;
        const mensagem = erro instanceof ErroApi ? erro.message : "Algo deu errado. Tente de novo.";
        trocar({ id: idElpis, autor: "elpis", estado: "erro", erro: mensagem, pergunta });
      }
    },
    [abrirCrise],
  );

  const perguntar = (texto: string) => {
    if (ocupada) return;
    const idVoce = proximoId.current++;
    const idElpis = proximoId.current++;
    setMensagens((lista) => [
      ...lista,
      { id: idVoce, autor: "voce", texto },
      { id: idElpis, autor: "elpis", estado: "enviando" },
    ]);
    void responder(idElpis, texto);
  };

  const tentarDeNovo = (id: number, pergunta: string) => {
    if (ocupada) return;
    setMensagens((lista) => lista.map((m) => (m.id === id ? { id, autor: "elpis", estado: "enviando" } : m)));
    void responder(id, pergunta);
  };

  const anexar = () => avisar("Demonstração: o envio de foto ou PDF ainda não existe.");

  return (
    <>
      <CabecalhoElpis />
      <div className="pd-corpo pd-conversa" aria-live="polite">
        <Balao>
          <p>
            Oi! Eu sou a Elpis. Respondo com base em fontes oficiais, como a Lei do Superendividamento e as normas do
            Banco Central, e mostro de onde veio cada resposta.
          </p>
          <p>Não sou advogada nem consultora de investimentos. Quando eu não achar uma fonte, vou dizer.</p>
        </Balao>

        {mensagens.map((m) => (
          <div key={m.id} className="app-mensagem">
            <Friso tipo="onda" curto />
            {m.autor === "voce" ? (
              <Balao autor="voce">{m.texto}</Balao>
            ) : m.estado === "enviando" ? (
              <Balao>
                <p className="app-consultando" role="status">
                  Consultando as fontes oficiais…
                </p>
              </Balao>
            ) : m.estado === "erro" ? (
              <Balao>
                <p role="alert">{m.erro}</p>
                <Botao variante="secundario" onClick={() => tentarDeNovo(m.id, m.pergunta)}>
                  Tentar de novo
                </Botao>
              </Balao>
            ) : (
              <RespostaElpis id={m.id} resposta={m.resposta} Selo={Selo} Balao={Balao} />
            )}
          </div>
        ))}

        <div className="pd-sugestoes" ref={fim}>
          {SUGESTOES.map((s) => (
            <button key={s} type="button" className="pd-sugestao" disabled={ocupada} onClick={() => perguntar(s)}>
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="pd-chat-rodape">
        <CampoPerguntaApp onEnviar={perguntar} onVoz={onVoz} onAnexo={anexar} desativado={ocupada} />
      </div>
    </>
  );
}

type Pandora = ReturnType<typeof usePandora>;

function RespostaElpis({
  id,
  resposta,
  Selo,
  Balao,
}: {
  id: number;
  resposta: RespostaChat;
  Selo: Pandora["Selo"];
  Balao: Pandora["Balao"];
}) {
  const base = `elpis-${id}`;
  return (
    <Balao>
      {resposta.crise ? (
        <div>
          <Selo tom="alerta" icone="info">
            Apoio agora
          </Selo>
        </div>
      ) : resposta.abstencao ? (
        <div>
          <Selo tom="neutro" icone="lupa">
            Sem fonte suficiente
          </Selo>
        </div>
      ) : null}
      <TextoComCitacoes texto={resposta.texto} citacoes={resposta.citacoes} base={base} />
      <CartoesDeFonte citacoes={resposta.citacoes} base={base} />
    </Balao>
  );
}

/** Tela 4c. Não grava nada: mostra o estado de escuta e o tempo correndo. */
function ModoVoz({ onTerminar }: { onTerminar: () => void }) {
  const { CabecalhoElpis, Elpis: Medalhao, BotaoVoz } = usePandora();
  const [segundos, setSegundos] = useState(0);
  const titulo = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    titulo.current?.focus();
    const relogio = setInterval(() => setSegundos((s) => s + 1), 1000);
    return () => clearInterval(relogio);
  }, []);

  const tempo = `${Math.floor(segundos / 60)}:${String(segundos % 60).padStart(2, "0")}`;

  return (
    <>
      <CabecalhoElpis nota={`Ouvindo · ${tempo}`} />
      <div className="pd-voz">
        <h1 className="pd-pergunta-titulo" style={{ padding: 0 }} ref={titulo} tabIndex={-1}>
          Pode falar, {PESSOA.nome}. Estou ouvindo.
        </h1>
        <Medalhao tamanho={248} estado="ouvindo" />
        <p className="pd-apoio">Toque de novo para terminar. Você também pode enviar uma foto.</p>
        <BotaoVoz ativo onClick={onTerminar} />
      </div>
    </>
  );
}
