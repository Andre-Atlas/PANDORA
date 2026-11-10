"use client";

import { useRouter } from "next/navigation";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { CabecalhoMitoVoltar } from "@/components/Controlados";
import { METAS } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

const OPCOES_RESERVA = [
  ["Títulos públicos Selic", "Garantia do Tesouro Nacional"],
  ["Renda fixa 100% CDI", "Cobertura do FGC até R$ 250 mil"],
  ["Poupança", "Referência de comparação"],
] as const;

/** Tela 7 da galeria: reserva, previsão e simulador. Abre a partir do Início. */
export function Metas() {
  const { Cartao, Anfora, Selo, Botao } = usePandora();
  const router = useRouter();
  const avisar = useAvisoDemo();

  return (
    <>
      <CabecalhoMitoVoltar titulo="Metas e previsão" onVoltar={() => router.push("/inicio")}>
        <p className="pd-mito-sub" style={{ fontWeight: 700 }}>
          {METAS.sobre}
        </p>
        <p className="pd-valor-xl">{METAS.guardado}</p>
        <p className="pd-mito-sub">{METAS.meta}</p>
      </CabecalhoMitoVoltar>

      <div className="pd-corpo">
        <Cartao titulo="Degraus da reserva">
          <div className="app-degraus-reserva">
            {METAS.degraus.map((d) => (
              <div key={d.prazo} className="app-degrau-reserva">
                <Anfora nivel={d.nivel} altura={84} rotulo={`${d.prazo}: ${Math.round(d.nivel * 100)}% cheia`} />
                <strong>{d.prazo}</strong>
                <span className="pd-apoio pd-num">{d.valor}</span>
              </div>
            ))}
          </div>
          <p className="pd-apoio">
            O primeiro degrau está completo. Faltam R$ 1.300 para 1 mês: com R$ 500 por mês, 3 meses.
          </p>
        </Cartao>

        <Cartao titulo="Próximos 90 dias">
          <div>
            <Selo tom="ok">Sem furo de caixa previsto</Selo>
          </div>
          <ul className="pd-lista">
            {METAS.previsao.map(([prazo, valor]) => (
              <li key={prazo}>
                <span className="pd-lista-texto">{prazo}</span>
                <strong className="pd-num">{valor}</strong>
              </li>
            ))}
          </ul>
          <p className="pd-apoio">Sobra estimada depois dos essenciais e da reserva, se o mês se repetir.</p>
        </Cartao>

        <Cartao titulo="Simular R$ 500 por mês">
          <div className="pd-legenda">
            <div className="pd-legenda-item">
              <span className="pd-apoio">Em 1 ano</span>
              <strong className="pd-valor-lg">R$ 6.000</strong>
            </div>
            <div className="pd-legenda-item">
              <span className="pd-apoio">Em 2 anos</span>
              <strong className="pd-valor-lg">R$ 12.000</strong>
            </div>
          </div>
          <p className="pd-apoio">Valor guardado, antes do rendimento.</p>
          <ul className="pd-lista">
            {OPCOES_RESERVA.map(([nome, garantia]) => (
              <li key={nome}>
                <span className="pd-lista-texto">
                  <strong>{nome}</strong>
                  <br />
                  <span className="pd-apoio">{garantia}</span>
                </span>
              </li>
            ))}
          </ul>
          <Botao variante="secundario" bloco seta onClick={() => avisar()}>
            Comparar com as séries do BCB
          </Botao>
          <p className="pd-apoio">Conteúdo educativo sobre classes gerais. Não é recomendação de investimento.</p>
        </Cartao>
      </div>
    </>
  );
}
