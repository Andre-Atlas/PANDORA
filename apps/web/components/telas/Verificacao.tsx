"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { BOLETO } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

const EXPLICACAO = [
  "Ele tem o desenho do banco, mas o dinheiro vai para a conta de uma pessoa desconhecida.",
  "Nenhum banco pede Pix para liberar valores do INSS.",
];

/**
 * Estado E2 da galeria: o veredito de um boleto em leitura ampliada, com voz.
 * É o resultado de demonstração de "Verificar boleto ou print": a leitura
 * do boleto de verdade ainda não existe.
 */
export function Verificacao() {
  const { Disco, Botao } = usePandora();
  const router = useRouter();
  const avisar = useAvisoDemo();
  const titulo = useRef<HTMLHeadingElement>(null);
  const frase = `${BOLETO.pessoaAmpliada}, não pague este boleto.`;

  useEffect(() => {
    titulo.current?.focus();
    return () => window.speechSynthesis?.cancel();
  }, []);

  // A síntese de voz do próprio navegador lê o veredito: funciona sem a API.
  function ouvir() {
    const sintese = typeof window !== "undefined" ? window.speechSynthesis : undefined;
    if (!sintese || typeof SpeechSynthesisUtterance === "undefined") {
      avisar("Este navegador não lê texto em voz alta.");
      return;
    }
    sintese.cancel();
    const fala = new SpeechSynthesisUtterance(["Pare!", frase, ...EXPLICACAO].join(" "));
    fala.lang = "pt-BR";
    fala.rate = 0.9;
    sintese.speak(fala);
  }

  return (
    <div className="pd-ampliado pd-acessivel pd-contido">
      <div className="pd-ampliado-veredito">
        <span role="img" aria-label="Alerta">
          <Disco tom="alerta" icone="alerta" tamanho="grande" />
        </span>
        <h1 className="pd-ampliado-titulo" ref={titulo} tabIndex={-1}>
          PARE!
        </h1>
        <p style={{ fontWeight: 700 }}>{frase}</p>
      </div>
      {EXPLICACAO.map((texto) => (
        <p key={texto}>{texto}</p>
      ))}
      <div className="pd-empurra" />
      <Botao bloco ampliado icone="som" onClick={ouvir}>
        Ouvir de novo
      </Botao>
      <Botao bloco ampliado variante="secundario" icone="pessoas" onClick={() => avisar()}>
        Avisar meu filho
      </Botao>
      <Botao bloco ampliado variante="secundario" icone="microfone" onClick={() => router.push("/elpis")}>
        Falar com Elpis
      </Botao>
      {/* Fora da galeria: sem navegação nesta tela, a pessoa precisa de um caminho de volta. */}
      <Botao bloco variante="fantasma" onClick={() => router.push("/guardiao")}>
        Voltar ao Guardião
      </Botao>
    </div>
  );
}
