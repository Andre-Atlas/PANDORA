"use client";

import { useRouter } from "next/navigation";
import { useAvisoDemo } from "@/components/AvisoDemo";
import { CampoPerguntaApp, InsightAcao } from "@/components/Controlados";
import { SeletorTema } from "@/components/SeletorTema";
import { INICIO, PESSOA } from "@/lib/demo/dados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

export const ROTA_METAS = "/inicio/metas";

/** Tela 2 da galeria: Início com o Raio-X do mês. Dados de demonstração. */
export function Inicio() {
  const { CabecalhoMito, BotaoIcone, Cartao, Botao, Trilho, Selo, LinkCartao } = usePandora();
  const router = useRouter();
  const avisar = useAvisoDemo();
  const { raioX, saude } = INICIO;

  return (
    <>
      <CabecalhoMito
        titulo={`Olá, ${PESSOA.nome}`}
        acao={<BotaoIcone icone="sino" tom="mito" rotulo="Avisos" onClick={() => avisar("Demonstração: nenhum aviso novo.")} />}
      >
        <p className="pd-mito-sub" style={{ fontWeight: 700 }}>
          Protegido este mês
        </p>
        <p className="pd-valor-xl">{INICIO.protegido}</p>
        <p className="pd-mito-sub">
          Seu mínimo existencial: aluguel, mercado, contas e transporte. Nenhum plano mexe nesse valor.
        </p>
      </CabecalhoMito>

      <div className="pd-corpo">
        <CampoPerguntaApp anexo={false} onEnviar={() => router.push("/elpis")} onVoz={() => router.push("/elpis")} />

        <InsightAcao acao="Entender esse valor" onAcao={() => router.push("/dividas")}>
          <strong className="pd-num">{INICIO.insight.valor}</strong>
          {INICIO.insight.texto}
        </InsightAcao>

        <Cartao sobre="Seu próximo passo" titulo={INICIO.proximoPasso.titulo}>
          <p>{INICIO.proximoPasso.texto}</p>
          <Botao bloco seta onClick={() => router.push("/dividas")}>
            Ver o plano
          </Botao>
        </Cartao>

        <Cartao sobre="Raio-X do mês" titulo={`Renda de ${raioX.renda}`}>
          <Trilho
            partes={[
              { valor: raioX.protegido.valor, tom: "ok" },
              { valor: raioX.folga.valor, tom: "vaso" },
            ]}
            rotulo={`${raioX.protegido.rotulo} protegidos e ${raioX.folga.rotulo} de folga real`}
          />
          <div className="pd-legenda">
            <div className="pd-legenda-item">
              <span className="pd-apoio">
                <i className="pd-legenda-marca pd-tom-ok" />
                Protegido
              </span>
              <strong className="pd-num">{raioX.protegido.rotulo}</strong>
            </div>
            <div className="pd-legenda-item">
              <span className="pd-apoio">
                <i className="pd-legenda-marca pd-tom-vaso" />
                Folga real
              </span>
              <strong className="pd-num">{raioX.folga.rotulo}</strong>
            </div>
          </div>
          <p className="pd-apoio">{raioX.nota}</p>
        </Cartao>

        <Cartao sobre="Saúde financeira">
          <div className="pd-linha">
            <p className="pd-valor-lg">{saude.pontos} de 100</p>
            <Selo tom="fonte" icone="check">
              Calculado
            </Selo>
          </div>
          <Trilho total={100} partes={[{ valor: saude.pontos, tom: "acao" }]} rotulo={`Score de ${saude.pontos} em 100`} />
          <ul className="pd-lista">
            {saude.fatores.map(([fator, nivel]) => (
              <li key={fator}>
                <span className="pd-lista-texto">{fator}</span>
                <strong>{nivel}</strong>
              </li>
            ))}
          </ul>
          <Botao variante="fantasma" onClick={() => avisar()}>
            Corrigir uma categoria
          </Botao>
        </Cartao>

        <LinkCartao
          icone="alvo"
          titulo="Metas e previsão"
          descricao="Próximos 30, 60 e 90 dias"
          onClick={() => router.push(ROTA_METAS)}
        />

        {/* Provisório: o seletor de tema mora aqui até existir uma tela de ajustes. */}
        <SeletorTema />
      </div>
    </>
  );
}
