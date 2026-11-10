"use client";

import { useState } from "react";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { DIVIDAS } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

const METODOS = ["Avalanche", "Bola de Neve"];

/** Tela 3 da galeria: dívidas na ordem do plano e dossiê. Dados de demonstração. */
export function Dividas() {
  const { CabecalhoMito, BotaoIcone, DegrausProgresso, Segmento, LinhaDivida, Selo, SeloCalculado, Cartao, Botao } =
    usePandora();
  const avisar = useAvisoDemo();
  const [metodo, setMetodo] = useState(METODOS[0]);

  return (
    <>
      <CabecalhoMito
        titulo="Suas dívidas"
        acao={
          <BotaoIcone
            icone="info"
            tom="mito"
            rotulo="Como calculamos"
            onClick={() => avisar("Demonstração: a explicação do cálculo chega com o motor determinístico.")}
          />
        }
      >
        <div className="pd-linha">
          <div>
            <p className="pd-valor-xl">{DIVIDAS.total}</p>
            <p className="pd-mito-sub">{DIVIDAS.resumo}</p>
          </div>
          <div style={{ width: 132, flex: "none" }}>
            <DegrausProgresso passos={DIVIDAS.etapa.total} atual={DIVIDAS.etapa.atual} />
          </div>
        </div>
      </CabecalhoMito>

      <div className="pd-corpo">
        <p style={{ fontWeight: 700 }}>{DIVIDAS.etapa.texto}</p>
        <Segmento rotulo="Método de priorização" opcoes={METODOS} valor={metodo} onChange={setMetodo} />
        <p className="pd-apoio">
          {metodo === "Avalanche"
            ? "Avalanche começa pelo maior custo total (CET)."
            : "Bola de Neve começa pelo menor saldo."}{" "}
          Nos seus dados, os dois métodos chegam à mesma ordem.
        </p>

        <LinhaDivida protegida nome="Mínimo existencial" valor={DIVIDAS.minimoExistencial}>
          <div>
            <Selo tom="ok" icone="escudo">
              Intocável
            </Selo>
          </div>
          <p className="pd-apoio">Fica fora de qualquer plano (Lei 14.181/2021).</p>
        </LinhaDivida>

        <LinhaDivida ordem={1} nome="Conta de luz" valor="R$ 360">
          <div>
            <Selo tom="alerta">Risco de corte</Selo>
          </div>
          <p className="pd-apoio">Serviço essencial. 2 faturas, 45 dias em atraso.</p>
        </LinhaDivida>

        <LinhaDivida ordem={2} nome="Cartão · Banco A" valor="R$ 4.200">
          <p>
            <strong className="pd-num">R$ 342,18 por mês</strong> só de juros e IOF.
          </p>
          <div className="pd-linha">
            <span className="pd-apoio pd-num">CET 448,0% a.a. · média BCB 435,9% a.a.</span>
            <SeloCalculado />
          </div>
          <div>
            <Selo tom="neutro" icone="lupa">
              Conferir teto de 100%
            </Selo>
          </div>
          <p className="pd-apoio">Lei 14.690/2023. São 7 meses no rotativo.</p>
        </LinhaDivida>

        <LinhaDivida ordem={3} nome="Empréstimo · Financeira B" valor="R$ 5.800">
          <p>
            <strong className="pd-num">R$ 480 por mês</strong> em 18 parcelas.
          </p>
          <span className="pd-apoio pd-num">CET 112,0% a.a.</span>
        </LinhaDivida>

        <Cartao sobre="Quando o banco não aceita" titulo="Dossiê de repactuação">
          <p>
            Reúne credores, mínimo existencial e proposta para levar ao Procon, à Defensoria ou ao CEJUSC. O plano pode
            ir até 5 anos.
          </p>
          <Botao variante="secundario" bloco icone="documento" onClick={() => avisar()}>
            Gerar dossiê em PDF
          </Botao>
        </Cartao>
      </div>
    </>
  );
}
