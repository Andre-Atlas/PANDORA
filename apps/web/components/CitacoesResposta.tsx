"use client";

import type { ReactNode } from "react";
import { linkSeguro, resumoDoTrecho, rotuloDoLink, rotuloNorma } from "@/lib/api/citacoes";
import type { Citacao } from "@/lib/api/tipos";
import { usePandora } from "@/lib/pandora/PandoraProvider";

export function idDaFonte(base: string, n: number): string {
  return `${base}-fonte-${n}`;
}

/** Troca cada `[n]` por um link para o cartão da fonte. Marcador sem fonte correspondente some. */
function marcar(paragrafo: string, validas: Set<number>, base: string): ReactNode[] {
  return paragrafo.split(/(\[\d+\])/g).map((parte, i) => {
    const m = /^\[(\d+)\]$/.exec(parte);
    if (!m) return parte;
    const n = Number(m[1]);
    return validas.has(n) ? (
      <a key={i} className="app-ref" href={`#${idDaFonte(base, n)}`} aria-label={`Ver a fonte ${n}`}>
        [{n}]
      </a>
    ) : null;
  });
}

interface TextoProps {
  texto: string;
  citacoes: Citacao[];
  /** Prefixo único da mensagem, para os links não colidirem entre respostas. */
  base: string;
}

export function TextoComCitacoes({ texto, citacoes, base }: TextoProps) {
  const validas = new Set(citacoes.map((c) => c.n));
  return (
    <>
      {texto
        .split(/\n{2,}/)
        .filter((p) => p.trim())
        .map((paragrafo, i) => (
          <p key={i} className="app-texto-resposta">
            {marcar(paragrafo.trim(), validas, base)}
          </p>
        ))}
    </>
  );
}

interface CartoesProps {
  citacoes: Citacao[];
  base: string;
}

/** Uma fonte oficial por cartão: norma, artigo, trecho e link. O aviso de vigência vai junto. */
export function CartoesDeFonte({ citacoes, base }: CartoesProps) {
  const { CitacaoCartao } = usePandora();
  return (
    <>
      {citacoes.map((c) => (
        <div key={c.n} id={idDaFonte(base, c.n)} className="app-fonte">
          <CitacaoCartao norma={rotuloNorma(c)} href={linkSeguro(c.link)} rotuloLink={rotuloDoLink(c.link)}>
            <span className="app-trecho">“{resumoDoTrecho(c.trecho)}”</span>
            {c.ressalva ? (
              <span className="app-ressalva">
                <strong>Atenção:</strong> {c.ressalva}
              </span>
            ) : null}
          </CitacaoCartao>
        </div>
      ))}
    </>
  );
}
