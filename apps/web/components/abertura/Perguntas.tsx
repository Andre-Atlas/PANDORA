"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ConsentimentoControlado, ProgressoFluxo } from "@/components/Controlados";
import { usePandora } from "@/lib/pandora/PandoraProvider";

export const ROTA_DEPOIS_DAS_PERGUNTAS = "/inicio";

const PESOS = [
  ["balanca", "Dívidas que não fecham", "Cartão, empréstimo, contas atrasadas"],
  ["pausa", "Apostas fora de controle", "Pix para bets que somem do mês"],
  ["escudo", "Medo de golpes", "Boletos, Pix e ligações suspeitas"],
  ["relogio", "Renda que muda todo mês", "Autônomo, MEI, aplicativo"],
  ["jarro", "Quero guardar e não voltar", "Saí das dívidas e quero segurança"],
] as const;

const MODOS = [
  ["upload", "Enviar fatura ou extrato", "PDF ou foto. Nada é conectado ao seu banco."],
  ["banco", "Conectar pelo Open Finance", "Ambiente de testes (sandbox), só leitura."],
] as const;

const COMBINADO = [
  "O PANDORA só lê. Nunca movimenta seu dinheiro.",
  "Nome, CPF e conta são mascarados antes de qualquer IA.",
  "Você apaga tudo quando quiser.",
] as const;

/**
 * Telas 1b a 1d da galeria: as três perguntas depois de "Começar".
 *
 * As respostas ainda não vão para lugar nenhum (#71): o fluxo existe para
 * mostrar o caminho. O aceite começa desmarcado, porque a LGPD exige que a
 * pessoa marque por conta própria; sem ele, "Abrir minha caixa" fica desativado.
 */
export function Perguntas() {
  const { EscalaSentimento, OpcaoCartao, Cartao, Icone, Botao } = usePandora();
  const router = useRouter();
  const [passo, setPasso] = useState<1 | 2 | 3>(1);
  const [peso, setPeso] = useState<string>(PESOS[0][1]);
  const [modo, setModo] = useState<string>(MODOS[0][1]);
  const [aceite, setAceite] = useState(false);
  const titulo = useRef<HTMLHeadingElement>(null);
  const primeiraVez = useRef(true);

  // A cada passo, o foco vai para a pergunta (o primeiro passo segue o foco normal da página).
  useEffect(() => {
    if (primeiraVez.current) {
      primeiraVez.current = false;
      return;
    }
    titulo.current?.focus();
  }, [passo]);

  const abrirCaixa = () => router.push(ROTA_DEPOIS_DAS_PERGUNTAS);

  if (passo === 1) {
    return (
      <div className="pd-pergunta-tela">
        <ProgressoFluxo passo={1} total={3} onVoltar={() => router.push("/")} onPular={() => setPasso(2)} />
        <h1 className="pd-pergunta-titulo" ref={titulo} tabIndex={-1}>
          Como você se sente sobre seu dinheiro hoje?
        </h1>
        <p className="pd-pergunta-sub">Nenhuma resposta é errada. Isso só mostra de onde partimos.</p>
        <div className="pd-empurra" />
        <EscalaSentimento valor={3} />
        <div className="pd-empurra" />
        <Botao bloco seta onClick={() => setPasso(2)}>
          Continuar
        </Botao>
      </div>
    );
  }

  if (passo === 2) {
    return (
      <div className="pd-pergunta-tela">
        <ProgressoFluxo passo={2} total={3} onVoltar={() => setPasso(1)} onPular={() => setPasso(3)} />
        <h1 className="pd-pergunta-titulo" ref={titulo} tabIndex={-1}>
          O que mais pesa hoje?
        </h1>
        <div role="radiogroup" aria-label="O que mais pesa hoje" className="pd-demo-coluna">
          {PESOS.map(([icone, nome, descricao]) => (
            <OpcaoCartao
              key={nome}
              icone={icone}
              titulo={nome}
              descricao={descricao}
              marcada={peso === nome}
              onClick={() => setPeso(nome)}
            />
          ))}
        </div>
        <div className="pd-empurra" />
        <Botao bloco seta onClick={() => setPasso(3)}>
          Continuar
        </Botao>
      </div>
    );
  }

  return (
    <div className="pd-pergunta-tela">
      <ProgressoFluxo passo={3} total={3} onVoltar={() => setPasso(2)} />
      <h1 className="pd-pergunta-titulo" ref={titulo} tabIndex={-1}>
        Como quer começar?
      </h1>
      <div role="radiogroup" aria-label="Como quer começar" className="pd-demo-coluna">
        {MODOS.map(([icone, nome, descricao]) => (
          <OpcaoCartao
            key={nome}
            icone={icone}
            titulo={nome}
            descricao={descricao}
            marcada={modo === nome}
            onClick={() => setModo(nome)}
          />
        ))}
      </div>
      <Cartao tom="apoio" titulo="O combinado">
        <ul className="pd-lista">
          {COMBINADO.map((item) => (
            <li key={item}>
              <Icone nome="check" tamanho={20} />
              <span className="pd-lista-texto">{item}</span>
            </li>
          ))}
        </ul>
      </Cartao>
      <ConsentimentoControlado marcado={aceite} onChange={setAceite}>
        Concordo com o uso dos meus dados para este diagnóstico.
      </ConsentimentoControlado>
      <div className="pd-empurra" />
      <Botao bloco seta desativado={!aceite} onClick={abrirCaixa}>
        Abrir minha caixa
      </Botao>
    </div>
  );
}
