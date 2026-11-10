"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { InsightAcao } from "@/components/Controlados";
import { LinkApoio } from "@/components/crise/LinkApoio";
import { LinkGuiaAutoexclusao } from "@/components/guardiao/LinkGuiaAutoexclusao";
import { APOSTAS, BOLETO } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

export const ROTA_VERIFICACAO = "/guardiao/verificacao";

const ABAS = ["Golpes", "Apostas"];

const PASSOS_MED = [
  ["Acione o MED no seu banco", "Quanto antes, melhor."],
  ["Use os dados prontos", "ID da transação, data, hora e valor."],
  ["Registre a ocorrência", "Boletim e registro no Banco Central."],
] as const;

/**
 * Telas 6a e 6b da galeria. Os resultados (boleto, apostas do mês) são dados
 * de demonstração. Na aba Apostas, o guia de autoexclusão e o apoio são as
 * versões reais do app, já adaptadas à MP nº 1.394/2026 (veja o README).
 */
export function Guardiao() {
  const { CabecalhoMito, Segmento } = usePandora();
  const [aba, setAba] = useState(ABAS[0]);

  return (
    <>
      <CabecalhoMito titulo="Guardião">
        <p className="pd-mito-sub">Confere antes de você decidir.</p>
      </CabecalhoMito>
      <div className="pd-corpo">
        <Segmento rotulo="Área do Guardião" opcoes={ABAS} valor={aba} onChange={setAba} />
        {aba === "Golpes" ? <Golpes /> : <Apostas />}
      </div>
    </>
  );
}

function Golpes() {
  const { Botao, Cartao, Disco, Selo } = usePandora();
  const router = useRouter();
  const avisar = useAvisoDemo();

  useEffect(() => {
    router.prefetch(ROTA_VERIFICACAO);
  }, [router]);

  return (
    <>
      <Botao bloco icone="camera" onClick={() => router.push(ROTA_VERIFICACAO)}>
        Verificar boleto ou print
      </Botao>

      <Cartao tom="alerta" titulo="Não pague este boleto">
        <p>
          {BOLETO.descricao} <strong className="pd-num">{BOLETO.valor}</strong>.
        </p>
        <ul className="pd-lista">
          {BOLETO.checagens.map((c) => (
            <li key={c.titulo}>
              <Disco tom={c.ok ? "ok" : "alerta"} icone={c.ok ? "check" : "x"} tamanho="pequeno" />
              <span className="pd-lista-texto">
                <strong>{c.titulo}</strong>
                <br />
                {c.texto}
              </span>
            </li>
          ))}
        </ul>
        <Botao variante="secundario" bloco icone="pessoas" onClick={() => avisar()}>
          Avisar pessoa de confiança
        </Botao>
      </Cartao>

      <Cartao titulo="Já fez o Pix?">
        <p>Dá para pedir a devolução pelo MED em até 80 dias.</p>
        <ol className="pd-lista">
          {PASSOS_MED.map(([titulo, texto], i) => (
            <li key={titulo}>
              <span className="pd-divida-ordem app-ordem-pequena">{i + 1}</span>
              <span className="pd-lista-texto">
                <strong>{titulo}</strong>
                <br />
                <span className="pd-apoio">{texto}</span>
              </span>
            </li>
          ))}
        </ol>
        <Botao variante="secundario" bloco icone="copiar" onClick={() => avisar()}>
          Copiar dados do Pix
        </Botao>
        <div>
          <Selo tom="fonte">Res. BCB 147/2021</Selo>
        </div>
      </Cartao>
    </>
  );
}

function Apostas() {
  const { Cartao, SeloCalculado, Alternador } = usePandora();

  return (
    <>
      <Cartao sobre={APOSTAS.sobre}>
        <p className="pd-valor-xl">{APOSTAS.resultado}</p>
        <ul className="pd-lista">
          {APOSTAS.linhas.map(([rotulo, valor]) => (
            <li key={rotulo}>
              <span className="pd-lista-texto">{rotulo}</span>
              <strong className="pd-num">{valor}</strong>
            </li>
          ))}
        </ul>
        <div>
          <SeloCalculado />
        </div>
      </Cartao>

      <InsightAcao>
        <strong className="pd-num">82%</strong> disso aconteceu nas quartas depois do repasse e entre 23h e 03h. Saber o
        horário já ajuda a se preparar.
      </InsightAcao>

      {/* O Alternador guarda o próprio estado: as travas ainda não são salvas (#81). */}
      <Cartao titulo="Travas que você escolhe">
        <Alternador titulo="Pausa noturna" descricao="23h às 03h. Para desligar, há 48h de espera." ligado />
        <Alternador titulo="Aviso na quarta" descricao="Lembrete logo após o repasse." />
        <p className="pd-apoio">O PANDORA avisa e cria espera. O bloqueio é feito no banco ou na plataforma.</p>
      </Cartao>

      <LinkGuiaAutoexclusao />
      <LinkApoio />
    </>
  );
}
