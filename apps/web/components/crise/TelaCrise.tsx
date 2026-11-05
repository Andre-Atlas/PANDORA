"use client";

import { useEffect, useRef } from "react";
import { EMERGENCIA, contatosVisiveis } from "@/lib/crise/contatos";
import { usePandora } from "@/lib/pandora/PandoraProvider";
import { useCrise } from "./CriseProvider";

/**
 * Tela de crise (galeria E1), montada com as peças do design system.
 *
 * Os contatos são <a> com a aparência de `Botao`, porque o `Botao` do design
 * system é sempre <button> e não aceita href. Ligar e abrir página são links.
 */
export function TelaCrise() {
  const { Elpis, Icone, Botao } = usePandora();
  const { fecharCrise } = useCrise();
  const titulo = useRef<HTMLHeadingElement>(null);

  // Leva o foco ao título, para leitor de tela e teclado começarem por aqui.
  useEffect(() => {
    titulo.current?.focus();
    const tituloAnterior = document.title;
    document.title = "Apoio · PANDORA";
    return () => {
      document.title = tituloAnterior;
    };
  }, []);

  return (
    <div className="pd-crise pd-acessivel pd-sem-ornamento">
      <Elpis tamanho={120} />
      <h1 className="pd-crise-titulo" ref={titulo} tabIndex={-1}>
        Agora o dinheiro pode esperar.
      </h1>
      <p>Parece que este momento está pesado. Pausei metas e avisos. Falar com alguém pode ajudar, e é de graça.</p>

      {contatosVisiveis().map((contato) => {
        const externo = contato.href!.startsWith("http");
        return (
          <a
            key={contato.id}
            href={contato.href!}
            className={`pd-botao pd-botao-${contato.variante} pd-botao-bloco`}
            {...(externo ? { target: "_blank", rel: "noopener noreferrer" } : {})}
          >
            <Icone nome={contato.icone} tamanho={22} />
            {contato.rotulo}
          </a>
        );
      })}

      <p className="pd-apoio">
        Se você corre perigo agora, ligue para o <a href={EMERGENCIA.href}>{EMERGENCIA.rotulo}</a>.
      </p>
      <p className="pd-apoio">Elpis não substitui um profissional de saúde.</p>
      <div className="pd-empurra" />
      <Botao bloco variante="fantasma" onClick={fecharCrise}>
        Voltar quando eu quiser
      </Botao>
    </div>
  );
}
