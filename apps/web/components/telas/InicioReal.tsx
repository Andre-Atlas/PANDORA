"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { ROTA_ENTRAR } from "@/components/conta/PortaoConta";
import { CampoPerguntaApp } from "@/components/Controlados";
import { SeletorTema } from "@/components/SeletorTema";
import { CATEGORIAS, NOME_DA_CATEGORIA } from "@/lib/api/categorias";
import {
  corrigirCategoria,
  enviarExtrato,
  ErroApi,
  listarTransacoes,
  obterRaioX,
  obterScore,
  sair,
  situacaoExtrato,
} from "@/lib/api/cliente";
import type { Categoria, Extrato, RaioX, Score, Transacao } from "@/lib/api/tipos";
import { apagarSessao } from "@/lib/conta/sessao";
import { diaEMes, mesDaData, nomeDoMes, reais } from "@/lib/formato";
import { ROTA_METAS } from "@/lib/navegacao";
import { usePandora } from "@/lib/pandora/PandoraProvider";

type Situacao =
  | { tipo: "carregando" }
  | { tipo: "erro"; mensagem: string; status: number | null }
  | { tipo: "vazio" }
  | { tipo: "pronto"; raioX: RaioX; transacoes: Transacao[] };

const mensagem = (erro: unknown) => (erro instanceof ErroApi ? erro.message : "Algo deu errado. Tente de novo.");

/**
 * O mês mostrado é o da transação mais recente, não o do relógio: quem envia
 * o extrato de outubro em novembro quer ver outubro.
 */
async function carregarMes(sinal: AbortSignal): Promise<Situacao> {
  const recente = await listarTransacoes({ porPagina: 1 }, sinal);
  if (recente.itens.length === 0) return { tipo: "vazio" };
  const mes = mesDaData(recente.itens[0].data_hora);
  const [raioX, doMes] = await Promise.all([obterRaioX(mes, sinal), listarTransacoes({ mes, porPagina: 200 }, sinal)]);
  return { tipo: "pronto", raioX, transacoes: doMes.itens };
}

/**
 * Início com os dados da API (#71): Raio-X do mês, envio de extrato e
 * correção de categoria. Só aparece com os dados reais ligados.
 *
 * O que a API ainda não calcula (insight de juros, próximo passo, score)
 * não aparece com valor fixo: o score mostra que ainda não está pronto.
 */
export function InicioReal() {
  const { CabecalhoMito, Cartao, Botao, LinkCartao } = usePandora();
  const router = useRouter();
  const [situacao, setSituacao] = useState<Situacao>({ tipo: "carregando" });
  const [versao, setVersao] = useState(0);
  // Recarrega sem voltar a "carregando": a tela atual fica até os dados novos chegarem.
  const recarregar = () => setVersao((n) => n + 1);

  useEffect(() => {
    const controle = new AbortController();
    carregarMes(controle.signal).then(setSituacao, (erro: unknown) => {
      if (controle.signal.aborted) return;
      setSituacao({ tipo: "erro", mensagem: mensagem(erro), status: erro instanceof ErroApi ? erro.status : null });
    });
    return () => controle.abort();
  }, [versao]);

  async function sairDaConta() {
    try {
      await sair();
    } catch {
      // Mesmo sem resposta da API, a sessão some deste aparelho.
    } finally {
      apagarSessao();
      router.replace(ROTA_ENTRAR);
    }
  }

  const raioX = situacao.tipo === "pronto" ? situacao.raioX : null;

  return (
    <>
      <CabecalhoMito titulo="Olá">
        {raioX ? (
          <>
            <p className="pd-mito-sub" style={{ fontWeight: 700 }}>
              Protegido em {nomeDoMes(raioX.mes)}
            </p>
            <p className="pd-valor-xl">{reais(raioX.minimo_existencial_centavos)}</p>
            <p className="pd-mito-sub">
              Seu mínimo existencial: aluguel, mercado, contas e transporte. Nenhum plano mexe nesse valor.
            </p>
          </>
        ) : (
          <p className="pd-mito-sub">O seu Raio-X aparece aqui depois do primeiro extrato.</p>
        )}
      </CabecalhoMito>

      <div className="pd-corpo">
        {situacao.tipo === "carregando" ? (
          <p className="pd-apoio app-consultando" role="status">
            Carregando o seu mês…
          </p>
        ) : null}

        {situacao.tipo === "erro" ? (
          <Cartao tom="alerta" titulo="Não consegui abrir o seu mês">
            <p role="alert">{situacao.mensagem}</p>
            {situacao.status === 401 ? (
              <Botao variante="secundario" onClick={() => router.replace(ROTA_ENTRAR)}>
                Entrar de novo
              </Botao>
            ) : (
              <Botao
                variante="secundario"
                onClick={() => {
                  setSituacao({ tipo: "carregando" });
                  recarregar();
                }}
              >
                Tentar de novo
              </Botao>
            )}
          </Cartao>
        ) : null}

        {situacao.tipo !== "erro" ? (
          <CampoPerguntaApp anexo={false} onEnviar={() => router.push("/elpis")} onVoz={() => router.push("/elpis")} />
        ) : null}

        {situacao.tipo === "vazio" || situacao.tipo === "pronto" ? (
          <EnvioExtrato primeiro={situacao.tipo === "vazio"} onConcluido={recarregar} />
        ) : null}

        {situacao.tipo === "pronto" ? (
          <>
            <CartaoRaioX raioX={situacao.raioX} />
            <TransacoesDoMes mes={situacao.raioX.mes} transacoes={situacao.transacoes} onCorrigida={recarregar} />
            <CartaoScore />
          </>
        ) : null}

        <LinkCartao
          icone="alvo"
          titulo="Metas e previsão"
          descricao="Próximos 30, 60 e 90 dias"
          onClick={() => router.push(ROTA_METAS)}
        />

        {/* Provisório: o seletor de tema e a saída moram aqui até existir uma tela de ajustes. */}
        <SeletorTema />
        <Botao variante="fantasma" onClick={sairDaConta}>
          Sair da conta
        </Botao>
      </div>
    </>
  );
}

function CartaoRaioX({ raioX }: { raioX: RaioX }) {
  const { Cartao, Trilho, SeloCalculado, BlocoCalculado } = usePandora();
  const protegido = raioX.minimo_existencial_centavos;
  const folga = raioX.folga_centavos;
  const temValores = protegido > 0 || folga > 0;

  return (
    <Cartao sobre={`Raio-X de ${nomeDoMes(raioX.mes)}`} titulo={`Renda de ${reais(raioX.renda_centavos)}`}>
      <SeloCalculado />
      {temValores ? (
        <Trilho
          partes={[
            { valor: protegido / 100, tom: "ok" },
            { valor: Math.max(folga, 0) / 100, tom: "vaso" },
          ]}
          rotulo={`${reais(protegido)} protegidos e ${reais(Math.max(folga, 0))} de folga real`}
        />
      ) : null}
      <div className="pd-legenda">
        <div className="pd-legenda-item">
          <span className="pd-apoio">
            <i className="pd-legenda-marca pd-tom-ok" />
            Protegido
          </span>
          <strong className="pd-num">{reais(protegido)}</strong>
        </div>
        <div className="pd-legenda-item">
          <span className="pd-apoio">
            <i className="pd-legenda-marca pd-tom-vaso" />
            Folga real
          </span>
          <strong className="pd-num">{reais(folga)}</strong>
        </div>
      </div>
      {folga < 0 ? (
        <p className="pd-apoio">
          O essencial passou da renda em {reais(-folga)}. Não é falha sua: é o ponto de partida do plano.
        </p>
      ) : null}

      {raioX.gastos.length > 0 ? (
        <>
          <h3 className="app-subtitulo">Para onde foi o dinheiro</h3>
          <ul className="pd-lista">
            {raioX.gastos.map((gasto) => (
              <li key={gasto.categoria}>
                <span className="pd-lista-texto">
                  {NOME_DA_CATEGORIA[gasto.categoria]}
                  {gasto.essencial_centavos > 0 ? (
                    <span className="pd-apoio"> · {reais(gasto.essencial_centavos)} essencial</span>
                  ) : null}
                </span>
                <strong className="pd-num">{reais(gasto.total_centavos)}</strong>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className="pd-apoio">Nenhum gasto classificado neste mês.</p>
      )}

      <details className="app-detalhes">
        <summary>Como foi calculado</summary>
        <BlocoCalculado linhas={raioX.calculo.entradas.map((e): [string, string] => [e.nome, e.valor])} />
      </details>
    </Cartao>
  );
}

type EstadoEnvio =
  | { tipo: "parado" }
  | { tipo: "enviando"; nome: string }
  | { tipo: "pronto"; extrato: Extrato }
  | { tipo: "erro"; mensagem: string };

/** Quantas vezes perguntar pela situação de um extrato ainda em processamento, uma por segundo. */
const CONSULTAS_DO_EXTRATO = 10;
const esperar = (ms: number) => new Promise((pronto) => setTimeout(pronto, ms));

function EnvioExtrato({ primeiro, onConcluido }: { primeiro: boolean; onConcluido: () => void }) {
  const { Cartao, Botao } = usePandora();
  const entrada = useRef<HTMLInputElement>(null);
  const idEntrada = useId();
  const [estado, setEstado] = useState<EstadoEnvio>({ tipo: "parado" });

  async function enviar(arquivo: File) {
    setEstado({ tipo: "enviando", nome: arquivo.name });
    try {
      let extrato = await enviarExtrato(arquivo);
      for (let i = 0; i < CONSULTAS_DO_EXTRATO && (extrato.status === "recebido" || extrato.status === "processando"); i++) {
        await esperar(1000);
        extrato = await situacaoExtrato(extrato.id);
      }
      if (extrato.status === "falhou") {
        setEstado({ tipo: "erro", mensagem: extrato.avisos?.[0] ?? "Não consegui ler esse arquivo." });
        return;
      }
      setEstado({ tipo: "pronto", extrato });
      if (extrato.status === "concluido") onConcluido();
    } catch (erro) {
      setEstado({ tipo: "erro", mensagem: mensagem(erro) });
    } finally {
      // Permite enviar o mesmo arquivo de novo.
      if (entrada.current) entrada.current.value = "";
    }
  }

  return (
    <Cartao
      sobre={primeiro ? "Para começar" : "Mais um mês"}
      titulo={primeiro ? "Envie um extrato ou fatura" : "Enviar outro extrato"}
    >
      <p>Por enquanto, em CSV. Nome, CPF e conta são mascarados antes de qualquer análise.</p>
      <label htmlFor={idEntrada} className="pd-oculto">
        Extrato ou fatura
      </label>
      <input
        id={idEntrada}
        ref={entrada}
        className="pd-oculto"
        type="file"
        accept=".csv,.ofx,.pdf,text/csv,application/pdf"
        tabIndex={-1}
        onChange={(e) => {
          const arquivo = e.target.files?.[0];
          if (arquivo) void enviar(arquivo);
        }}
      />
      <Botao
        variante={primeiro ? "primario" : "secundario"}
        icone="upload"
        desativado={estado.tipo === "enviando"}
        onClick={() => entrada.current?.click()}
      >
        {estado.tipo === "enviando" ? "Enviando…" : "Escolher arquivo"}
      </Botao>
      <div role="status" aria-live="polite">
        {estado.tipo === "enviando" ? <p className="pd-apoio app-consultando">Lendo {estado.nome}…</p> : null}
        {estado.tipo === "pronto" ? <ResultadoExtrato extrato={estado.extrato} /> : null}
      </div>
      {estado.tipo === "erro" ? (
        <p role="alert" className="app-erro">
          {estado.mensagem}
        </p>
      ) : null}
    </Cartao>
  );
}

function ResultadoExtrato({ extrato }: { extrato: Extrato }) {
  if (extrato.status !== "concluido") {
    return <p className="pd-apoio">{extrato.nome_arquivo} ainda está sendo lido. Volte em instantes.</p>;
  }
  const n = extrato.transacoes_importadas ?? 0;
  const avisos = extrato.avisos ?? [];
  return (
    <>
      <p className="pd-apoio">
        {extrato.nome_arquivo}: {n} {n === 1 ? "transação lida" : "transações lidas"}.
      </p>
      {avisos.length > 0 ? (
        <ul className="pd-lista">
          {avisos.map((aviso) => (
            <li key={aviso}>
              <span className="pd-lista-texto pd-apoio">{aviso}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </>
  );
}

/** Quantas transações aparecem antes de "Ver todas". */
const VISIVEIS = 8;

function TransacoesDoMes({
  mes,
  transacoes,
  onCorrigida,
}: {
  mes: string;
  transacoes: Transacao[];
  onCorrigida: () => void;
}) {
  const { Cartao, Botao } = usePandora();
  const [todas, setTodas] = useState(false);
  // Escolha feita agora, mostrada antes de a API confirmar; some se a correção falhar.
  const [escolhas, setEscolhas] = useState<Record<string, Categoria>>({});
  const [aviso, setAviso] = useState<string | null>(null);
  const visiveis = todas ? transacoes : transacoes.slice(0, VISIVEIS);

  async function corrigir(transacao: Transacao, categoria: Categoria) {
    setEscolhas((atual) => ({ ...atual, [transacao.id]: categoria }));
    setAviso(null);
    try {
      await corrigirCategoria(transacao.id, categoria);
      setAviso(`${transacao.descricao_mascarada}: agora em ${NOME_DA_CATEGORIA[categoria]}.`);
      onCorrigida();
    } catch (erro) {
      setEscolhas((atual) => {
        const resto = { ...atual };
        delete resto[transacao.id];
        return resto;
      });
      setAviso(`Não consegui corrigir. ${mensagem(erro)}`);
    }
  }

  return (
    <Cartao sobre={`Transações de ${nomeDoMes(mes)}`} titulo="Alguma categoria errada?">
      <p className="pd-apoio">Troque a categoria e o Raio-X se refaz. A sua escolha vale mais que a do modelo.</p>
      <ul className="app-transacoes">
        {visiveis.map((t) => (
          <li key={t.id} className="app-transacao">
            <div className="app-transacao-texto">
              <span>{t.descricao_mascarada}</span>
              <span className="pd-apoio">
                {diaEMes(t.data_hora)}
                {t.origem_categoria === "pessoa" ? " · corrigida por você" : null}
              </span>
            </div>
            <strong className="pd-num app-transacao-valor">{reais(t.valor_centavos)}</strong>
            <select
              className="app-campo app-transacao-categoria"
              aria-label={`Categoria de ${t.descricao_mascarada}, ${diaEMes(t.data_hora)}`}
              value={escolhas[t.id] ?? t.categoria}
              onChange={(e) => void corrigir(t, e.target.value as Categoria)}
            >
              {CATEGORIAS.map((c) => (
                <option key={c} value={c}>
                  {NOME_DA_CATEGORIA[c]}
                </option>
              ))}
            </select>
          </li>
        ))}
      </ul>
      <p role="status" className="pd-apoio">
        {aviso}
      </p>
      {transacoes.length > VISIVEIS ? (
        <Botao variante="fantasma" onClick={() => setTodas((t) => !t)}>
          {todas ? "Mostrar menos" : `Ver todas as ${transacoes.length}`}
        </Botao>
      ) : null}
    </Cartao>
  );
}

const NOME_DO_COMPONENTE: Record<Score["componentes"][number]["nome"], string> = {
  comprometimento_renda: "Renda comprometida",
  custo_medio_divida: "Custo médio das dívidas",
  reserva: "Reserva",
  dias_sem_apostas: "Dias sem apostas",
};

type EstadoScore = { tipo: "carregando" } | { tipo: "pronto"; score: Score } | { tipo: "indisponivel"; mensagem: string };

/** Score de saúde financeira. Enquanto o motor (#65) não existe, a API responde 501 e o cartão diz isso. */
function CartaoScore() {
  const { Cartao, Trilho, SeloCalculado } = usePandora();
  const [estado, setEstado] = useState<EstadoScore>({ tipo: "carregando" });

  useEffect(() => {
    const controle = new AbortController();
    obterScore(controle.signal).then(
      (score) => setEstado({ tipo: "pronto", score }),
      (erro: unknown) => {
        if (controle.signal.aborted) return;
        const aindaNao = erro instanceof ErroApi && erro.status === 501;
        setEstado({
          tipo: "indisponivel",
          mensagem: aindaNao ? "O score ainda não está pronto. Ele aparece aqui assim que for calculado." : mensagem(erro),
        });
      },
    );
    return () => controle.abort();
  }, []);

  if (estado.tipo !== "pronto") {
    return (
      <Cartao sobre="Saúde financeira">
        <p className={estado.tipo === "carregando" ? "pd-apoio app-consultando" : "pd-apoio"} role="status">
          {estado.tipo === "carregando" ? "Calculando o score…" : estado.mensagem}
        </p>
      </Cartao>
    );
  }

  const { score } = estado;
  return (
    <Cartao sobre="Saúde financeira">
      <div className="pd-linha">
        <p className="pd-valor-lg">{score.valor} de 100</p>
        <SeloCalculado />
      </div>
      <Trilho total={100} partes={[{ valor: score.valor, tom: "acao" }]} rotulo={`Score de ${score.valor} em 100`} />
      <ul className="pd-lista">
        {score.componentes.map((c) => (
          <li key={c.nome}>
            <span className="pd-lista-texto">{NOME_DO_COMPONENTE[c.nome]}</span>
            <strong>{c.valor} de 100</strong>
          </li>
        ))}
      </ul>
    </Cartao>
  );
}
