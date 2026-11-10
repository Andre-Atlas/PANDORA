"use client";

import { useRouter } from "next/navigation";
import { Fragment, useEffect, useRef, useState } from "react";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { CampoPerguntaApp } from "@/components/Controlados";
import { CONVERSA, PESSOA } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

/** Até o chat de verdade (#80) chegar, toda pergunta nova recebe esta resposta. */
export const RESPOSTA_DEMO =
  "Esta é uma demonstração. A Elpis de verdade, que busca a resposta em fontes oficiais, chega com o chat (#80).";

/**
 * Tela 4 da galeria. A conversa começa com as trocas das telas 4a (resposta
 * com fonte) e 4b (limites). O microfone abre o modo voz (4c).
 */
export function Elpis() {
  const [ouvindo, setOuvindo] = useState(false);
  return ouvindo ? <ModoVoz onTerminar={() => setOuvindo(false)} /> : <Conversa onVoz={() => setOuvindo(true)} />;
}

function Conversa({ onVoz }: { onVoz: () => void }) {
  const { CabecalhoElpis, Balao, CitacaoCartao, BlocoCalculado, Friso, Selo, Icone, Botao } = usePandora();
  const router = useRouter();
  const avisar = useAvisoDemo();
  const [novas, setNovas] = useState<string[]>([]);
  const fim = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (novas.length) fim.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [novas]);

  const perguntar = (texto: string) => setNovas((lista) => [...lista, texto]);
  const anexar = () => avisar("Demonstração: o envio de foto ou PDF ainda não existe.");

  return (
    <>
      <CabecalhoElpis />
      <div className="pd-corpo pd-conversa" aria-live="polite">
        {/* 4a · Resposta com fonte */}
        <Balao autor="voce">{CONVERSA.salario.pergunta}</Balao>
        <Balao>
          <p>
            <strong>Não.</strong> O salário é impenhorável para dívidas de cartão e de empréstimo. O que um cobrador diz
            por telefone não muda essa regra.
          </p>
          <CitacaoCartao norma={CONVERSA.salario.norma} href={CONVERSA.salario.href} rotuloLink="Ler no Planalto">
            Consultei 3 trechos em fontes oficiais.
          </CitacaoCartao>
        </Balao>
        <Friso tipo="onda" curto />
        <Balao autor="voce">{CONVERSA.ordem.pergunta}</Balao>
        <Balao>
          <p>
            Primeiro a comida e a casa das crianças. Depois a luz, para não haver corte. O que sobra vai para o cartão.
          </p>
          <BlocoCalculado linhas={CONVERSA.ordem.linhas} />
        </Balao>

        {/* 4b · Limites: recusa educativa e falta de fonte */}
        <Friso tipo="onda" curto />
        <Balao autor="voce">{CONVERSA.investimento.pergunta}</Balao>
        <Balao>
          <div>
            <Selo tom="neutro" icone="info">
              Recusa educativa
            </Selo>
          </div>
          <p>
            Não recomendo ações, fundos ou títulos específicos. Isso é consultoria regulada pela CVM. Posso te ensinar a
            avaliar qualquer opção para a reserva:
          </p>
          <ul className="pd-lista">
            {CONVERSA.investimento.criterios.map(([criterio, explicacao]) => (
              <li key={criterio}>
                <Icone nome="check" tamanho={20} />
                <span className="pd-lista-texto">
                  <strong>{criterio}:</strong> {explicacao}
                </span>
              </li>
            ))}
          </ul>
          <CitacaoCartao
            norma="Resoluções CVM 19 e 20/2021"
            href="https://www.gov.br/investidor/"
            rotuloLink="Portal do Investidor"
          />
        </Balao>
        <Friso tipo="onda" curto />
        <Balao autor="voce">{CONVERSA.tarifa.pergunta}</Balao>
        <Balao>
          <div>
            <Selo tom="neutro" icone="lupa">
              Sem fonte suficiente
            </Selo>
          </div>
          <p>Não encontrei uma fonte oficial que responda isso com segurança, e prefiro não adivinhar.</p>
          <p>Se mandar uma foto do extrato com a tarifa, procuro de novo. O Procon também pode orientar você.</p>
          <Botao variante="secundario" icone="camera" onClick={anexar}>
            Enviar foto
          </Botao>
        </Balao>

        {/* Perguntas desta visita */}
        {novas.map((pergunta, i) => (
          <Fragment key={i}>
            <Friso tipo="onda" curto />
            <Balao autor="voce">{pergunta}</Balao>
            <Balao>
              <div>
                <Selo tom="neutro" icone="info">
                  Demonstração
                </Selo>
              </div>
              <p>{RESPOSTA_DEMO}</p>
            </Balao>
          </Fragment>
        ))}

        <div className="pd-sugestoes" ref={fim}>
          <button type="button" className="pd-sugestao" onClick={() => perguntar(CONVERSA.sugestoes[0])}>
            {CONVERSA.sugestoes[0]}
          </button>
          <button type="button" className="pd-sugestao" onClick={() => router.push("/dividas")}>
            {CONVERSA.sugestoes[1]}
          </button>
        </div>
      </div>
      <div className="pd-chat-rodape">
        <CampoPerguntaApp onEnviar={perguntar} onVoz={onVoz} onAnexo={anexar} />
      </div>
    </>
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
