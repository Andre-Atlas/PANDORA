"use client";

import Image from "next/image";
import { useEffect } from "react";
import cena from "@pandora/design-system/assets/Cena/pandora-cena.svg";
import { BotaoLink } from "@/components/BotaoLink";
import { marcarAberturaVista } from "@/lib/abertura/portao";
import { usePandora } from "@/lib/pandora/PandoraProvider";

/** Para onde "Começar" leva: as perguntas da Abertura (telas 1b a 1d). */
export const ROTA_COMECAR = "/comecar";

/** O que o app faz, uma linha por aba. Os textos vêm da galeria do design system. */
const AREAS = [
  {
    titulo: "Raio-X do mês",
    texto: "Quanto da sua renda fica protegido para aluguel, mercado e contas, e quanto é folga de verdade.",
  },
  {
    titulo: "Dívidas na ordem certa",
    texto: "Um plano que mostra qual dívida atacar primeiro. Toda conta vem do cálculo, não de palpite.",
  },
  {
    titulo: "Elpis, que cita a fonte",
    texto: "Pergunte sobre seus direitos. Toda resposta sobre lei traz a norma e o link, e ela diz quando não sabe.",
  },
  {
    titulo: "Trilha sem pressão",
    texto: "Educação financeira em etapas. Sem sorteio, sem ranking e sem perder nada por errar.",
  },
  {
    titulo: "Guardião",
    texto: "Confere boletos, Pix e ligações suspeitas antes de você decidir, e ajuda a se afastar das apostas.",
  },
] as const;

/** Os três compromissos de "O combinado", da tela 1d da galeria. */
const COMBINADO = [
  "O PANDORA só lê. Nunca movimenta seu dinheiro.",
  "Nome, CPF e conta são mascarados antes de qualquer IA.",
  "Você apaga tudo quando quiser.",
] as const;

/**
 * Página de entrada. O topo é a abertura do design system (`.pd-abertura`):
 * a cena nítida se dissolve num esfumado da própria cena, e o texto fica sobre
 * a base do vaso. No celular a cena fica em cima; a partir de 800px, à esquerda.
 * Abaixo da primeira tela vêm o que o app faz e o combinado (registro de leitura).
 */
export function Abertura() {
  const { Cartao, Friso, Icone } = usePandora();

  // Ver a abertura libera as telas do app nesta sessão (veja lib/abertura/portao.ts).
  useEffect(() => {
    marcarAberturaVista();
  }, []);

  return (
    <div className="abertura">
      <section className="pd-abertura pd-base abertura-heroi" aria-labelledby="abertura-nome">
        {/* Fundo: a mesma cena, esfumada pelo design system. Decorativa. */}
        <Image src={cena} width={2000} height={2000} sizes="100vw" alt="" aria-hidden className="pd-abertura-fundo" />
        <Image
          src={cena}
          width={2000}
          height={2000}
          preload
          sizes="(min-width: 800px) 60vw, 100vw"
          className="pd-abertura-cena"
          alt="Pandora, em figura negra sobre fundo laranja, abre a caixa entre duas colunas. Espíritos brancos saem dela."
        />
        <div className="pd-abertura-painel">
          <div className="pd-abertura-texto">
            <div className="pd-lancetas" aria-hidden="true" />
            <h1 id="abertura-nome" className="pd-abertura-nome">
              PANDORA
            </h1>
            <p className="pd-abertura-frase">Ainda há esperança…</p>
            <Friso tipo="ramo" tom="base" curto />
            <BotaoLink href={ROTA_COMECAR} variante="claro" seta>
              Começar
            </BotaoLink>
          </div>
        </div>
      </section>

      <div className="abertura-mais">
        <section className="abertura-secao" aria-labelledby="abertura-areas">
          <h2 id="abertura-areas" className="abertura-secao-titulo">
            O que tem dentro
          </h2>
          <div className="abertura-grade">
            {AREAS.map((area) => (
              <Cartao key={area.titulo} titulo={area.titulo}>
                <p>{area.texto}</p>
              </Cartao>
            ))}
          </div>
        </section>

        <section className="abertura-secao" aria-labelledby="abertura-combinado">
          <h2 id="abertura-combinado" className="abertura-secao-titulo">
            O combinado
          </h2>
          <Cartao tom="apoio">
            <ul className="pd-lista">
              {COMBINADO.map((item) => (
                <li key={item}>
                  <Icone nome="check" tamanho={20} />
                  <span className="pd-lista-texto">{item}</span>
                </li>
              ))}
            </ul>
          </Cartao>
        </section>

        <div className="abertura-fim">
          <BotaoLink href={ROTA_COMECAR} variante="primario" seta>
            Começar
          </BotaoLink>
        </div>
      </div>
    </div>
  );
}
