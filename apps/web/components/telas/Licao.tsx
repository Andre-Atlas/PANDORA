"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ProgressoFluxo } from "@/components/Controlados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

type Letra = "a" | "b" | "c";

const OPCOES: [Letra, string][] = [
  ["a", "Fica parado até a próxima fatura"],
  ["b", "Entra no rotativo e continua gerando juros"],
  ["c", "O banco cancela depois de 3 meses"],
];
const CERTA: Letra = "b";

/**
 * Tela 5b da galeria: uma pergunta da lição do rotativo. Errar não tira
 * nada: o retorno explica e a pessoa pode trocar a resposta.
 */
export function Licao() {
  const { Brasao, QuizOpcao, Cartao, Selo, Botao } = usePandora();
  const router = useRouter();
  const [resposta, setResposta] = useState<Letra | null>(null);
  const certo = resposta === CERTA;

  function estado(letra: Letra): "neutra" | "certa" | "revisar" {
    if (!resposta) return "neutra";
    if (letra === CERTA) return "certa";
    return letra === resposta ? "revisar" : "neutra";
  }

  return (
    <div className="pd-pergunta-tela">
      <ProgressoFluxo passo={2} total={4} onVoltar={() => router.push("/trilha")} />
      <div className="pd-linha" style={{ justifyContent: "flex-start" }}>
        <Brasao emblema="espiral" estado="atual" tamanho={44} />
        <p className="pd-apoio" style={{ fontWeight: 700 }}>
          Etapa 3 · Rotativo
        </p>
      </div>
      <h1 className="pd-cartao-titulo" style={{ fontSize: 24, lineHeight: "30px" }}>
        Você pagou só o mínimo da fatura. O que acontece com o restante?
      </h1>
      {OPCOES.map(([letra, texto]) => (
        <QuizOpcao key={letra} letra={letra.toUpperCase()} estado={estado(letra)} onClick={() => setResposta(letra)}>
          {texto}
        </QuizOpcao>
      ))}
      <div aria-live="polite">
        {resposta ? (
          <Cartao tom={certo ? "ok" : "apoio"} titulo={certo ? "Isso mesmo" : "Vale rever este ponto"}>
            <p>
              O restante entra no rotativo. Na sua fatura, isso custou <strong className="pd-num">R$ 342,18</strong> em
              um mês. Por lei, juros e encargos do rotativo não podem passar de 100% da dívida original.
            </p>
            <div>
              <Selo tom="fonte">Lei 14.690/2023</Selo>
            </div>
          </Cartao>
        ) : null}
      </div>
      <div className="pd-empurra" />
      <Botao bloco seta desativado={!resposta} onClick={() => router.push("/trilha")}>
        Seguir
      </Botao>
    </div>
  );
}
