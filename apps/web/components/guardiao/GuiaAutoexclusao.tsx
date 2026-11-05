"use client";

import Link from "next/link";
import { BotaoLink } from "@/components/BotaoLink";
import { LinkApoio } from "@/components/crise/LinkApoio";
import { FONTES, LINKS, type Fonte } from "@/lib/guardiao/fontes";
import { usePandora } from "@/lib/pandora/PandoraProvider";

const dataPorExtenso = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric" });

function Citacao({ fonte }: { fonte: Fonte }) {
  const { CitacaoCartao } = usePandora();
  return <CitacaoCartao norma={fonte.norma} href={fonte.href} rotuloLink={fonte.rotuloLink} />;
}

/**
 * Guia de autoexclusão (#81, RF11).
 *
 * Desde a MP nº 1.394/2026 as bets são proibidas e a Plataforma Centralizada
 * de Autoexclusão saiu do ar. Mesmo assim, sites ilegais continuam aparecendo,
 * então o guia troca "se excluir das plataformas" por bloqueios que a pessoa
 * controla: no aparelho, no limite do Pix e na denúncia do site.
 * Toda afirmação sobre lei leva `CitacaoCartao`, como pede o design system.
 */
export function GuiaAutoexclusao() {
  const { CabecalhoMito, Cartao } = usePandora();

  return (
    <>
      <CabecalhoMito titulo="Autoexclusão" subtitulo="Passos para manter distância das apostas, no seu ritmo." />
      <div className="pd-corpo">
        <Cartao tom="apoio" sobre="O que mudou" titulo="As bets estão proibidas no Brasil">
          <p>
            Desde 25 de setembro de 2026, ninguém pode explorar, oferecer, intermediar ou divulgar apostas de quota fixa
            no país. Isso inclui apostas esportivas e jogos online.
          </p>
          <p>
            Por causa disso, a plataforma oficial de autoexclusão saiu do ar. Mesmo proibidos, alguns sites continuam
            aparecendo. Estes passos ajudam você a manter distância deles.
          </p>
          <Citacao fonte={FONTES.proibicao} />
        </Cartao>

        <Cartao sobre="Passo 1" titulo="Bloqueie os sites no celular e no computador">
          <p>
            O BetBlocker é gratuito, não pede cadastro e funciona em Android, iPhone, Windows e Mac. Ele é mantido por uma
            organização sem fins lucrativos.
          </p>
          <p>
            Você escolhe por quanto tempo bloquear, de 1 dia a 5 anos. Depois de começar, o bloqueio não pode ser
            desfeito antes do fim. Se preferir, comece por um prazo curto.
          </p>
          <BotaoLink href={LINKS.betblocker} icone="escudo">
            Abrir o BetBlocker
          </BotaoLink>
          <p className="pd-apoio">O PANDORA não tem ligação com o BetBlocker.</p>
        </Cartao>

        <Cartao sobre="Passo 2" titulo="Baixe o limite do Pix à noite">
          <p>
            Das 20h às 6h, o Pix entre pessoas já tem limite de <strong className="pd-num">R$ 1.000</strong>. No app do
            seu banco, na área de limites do Pix, você pode baixar esse valor.
          </p>
          <p>Para aumentar de novo, o banco só libera depois de pelo menos 24 horas. Esse tempo ajuda a decidir com calma.</p>
          <Citacao fonte={FONTES.limiteNoturno} />
        </Cartao>

        <Cartao tom="alerta" sobre="Passo 3" titulo="Não pague site de apostas">
          <p>
            Bancos e instituições de pagamento não podem fazer Pix, TED ou boleto para apostas. Se um site de apostas
            pedir pagamento, ele está fora da lei.
          </p>
          <Citacao fonte={FONTES.pagamentosVedados} />
          <Citacao fonte={FONTES.pixBloqueado} />
        </Cartao>

        <Cartao sobre="Passo 4" titulo="Denuncie o site">
          <ol className="pd-lista">
            {[
              "Entre em gov.br/falabr com sua conta gov.br.",
              "Toque em Nova manifestação e escolha Denúncia.",
              "Escolha o órgão Ministério da Fazenda (MF) e informe o endereço do site.",
            ].map((passo, i) => (
              <li key={passo}>
                <span className="pd-divida-ordem" style={{ width: 28, height: 28, fontSize: 14 }} aria-hidden="true">
                  {i + 1}
                </span>
                <span className="pd-lista-texto">{passo}</span>
              </li>
            ))}
          </ol>
          <p className="pd-apoio">
            A denúncia pode ser anônima. Nesse caso, você não recebe protocolo nem acompanha o andamento.
          </p>
          <BotaoLink href={LINKS.falabr} icone="alerta">
            Abrir o Fala.BR
          </BotaoLink>
          <Citacao fonte={FONTES.denuncia} />
        </Cartao>

        <LinkApoio />

        <p className="pd-apoio">
          Informações conferidas em {dataPorExtenso(FONTES.proibicao.conferidoEm)}. A medida provisória ainda está em
          análise no Congresso e pode mudar.
        </p>
        <Link href="/guardiao" className="pd-botao pd-botao-fantasma">
          Voltar ao Guardião
        </Link>
      </div>
    </>
  );
}
