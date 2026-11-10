"use client";

import { useState, type FormEvent, type ReactNode } from "react";
import { usePandora } from "@/lib/pandora/PandoraProvider";

/*
 * Versões controláveis de peças do design system que ainda não aceitam
 * `onClick`, `value` ou `onChange` (veja "Pendências conhecidas" no README).
 * Usam exatamente as classes do design system, então a aparência é a mesma.
 * Quando o design system aceitar esses props, troque cada uma pela original.
 */

interface ProgressoFluxoProps {
  passo: number;
  total: number;
  onVoltar?: () => void;
  onPular?: () => void;
}

/** `Progresso` com voltar e pular funcionando. Sem o handler, o botão não aparece. */
export function ProgressoFluxo({ passo, total, onVoltar, onPular }: ProgressoFluxoProps) {
  const { BotaoIcone, Botao } = usePandora();
  return (
    <div className="pd-progresso">
      {onVoltar ? <BotaoIcone icone="voltar" rotulo="Voltar" onClick={onVoltar} /> : null}
      <div
        className="pd-progresso-barra"
        role="progressbar"
        aria-valuenow={passo}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-label={`Passo ${passo} de ${total}`}
      >
        <div className="pd-progresso-feito" style={{ width: `${(passo / total) * 100}%` }} />
      </div>
      {onPular ? (
        <Botao variante="fantasma" onClick={onPular}>
          Pular
        </Botao>
      ) : null}
    </div>
  );
}

interface CabecalhoMitoVoltarProps {
  titulo: string;
  onVoltar: () => void;
  children?: ReactNode;
}

/** `CabecalhoMito` com `voltar`, que no design system não recebe handler. */
export function CabecalhoMitoVoltar({ titulo, onVoltar, children }: CabecalhoMitoVoltarProps) {
  const { BotaoIcone, Meandro } = usePandora();
  return (
    <header className="pd-mito">
      <Meandro />
      <div className="pd-mito-conteudo">
        <div className="pd-mito-topo">
          <BotaoIcone icone="voltar" tom="mito" rotulo="Voltar" onClick={onVoltar} />
          <h1 className="pd-mito-titulo" style={{ flex: 1 }}>
            {titulo}
          </h1>
        </div>
        {children}
      </div>
      <Meandro posicao="baixo" />
    </header>
  );
}

interface InsightAcaoProps {
  sobre?: string;
  acao?: string;
  onAcao?: () => void;
  children: ReactNode;
}

/** `Insight` com o botão de ação funcionando. */
export function InsightAcao({ sobre = "Uma coisa que notei", acao, onAcao, children }: InsightAcaoProps) {
  const { Elpis, Botao } = usePandora();
  return (
    <section className="pd-cartao pd-insight">
      <Elpis tamanho={48} />
      <div className="pd-insight-corpo">
        <p className="pd-insight-sobre">{sobre}</p>
        <p>{children}</p>
        {acao ? (
          <Botao variante="fantasma" onClick={onAcao}>
            {acao}
          </Botao>
        ) : null}
      </div>
    </section>
  );
}

interface CampoPerguntaAppProps {
  placeholder?: string;
  anexo?: boolean;
  onEnviar: (texto: string) => void;
  onVoz?: () => void;
  onAnexo?: () => void;
}

/** `CampoPergunta` que envia o texto (Enter) e liga o microfone e o anexo. */
export function CampoPerguntaApp({
  placeholder = "Pergunte à Elpis",
  anexo = true,
  onEnviar,
  onVoz,
  onAnexo,
}: CampoPerguntaAppProps) {
  const { BotaoIcone } = usePandora();
  const [texto, setTexto] = useState("");

  function enviar(evento: FormEvent) {
    evento.preventDefault();
    const limpo = texto.trim();
    if (!limpo) return;
    onEnviar(limpo);
    setTexto("");
  }

  return (
    <form className="pd-pergunta" onSubmit={enviar}>
      {anexo ? <BotaoIcone icone="clipe" rotulo="Enviar foto ou PDF" onClick={onAnexo} /> : null}
      <input
        className="pd-pergunta-texto"
        type="text"
        placeholder={placeholder}
        aria-label={placeholder}
        enterKeyHint="send"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        style={anexo ? undefined : { paddingLeft: 2 }}
      />
      <BotaoIcone icone="microfone" tom="acao" rotulo="Falar com Elpis" onClick={onVoz} />
    </form>
  );
}

interface ConsentimentoControladoProps {
  marcado: boolean;
  onChange: (marcado: boolean) => void;
  children: ReactNode;
}

/** `Consentimento` controlado: o app precisa saber se a pessoa aceitou. */
export function ConsentimentoControlado({ marcado, onChange, children }: ConsentimentoControladoProps) {
  return (
    <label className="pd-consentimento">
      <input type="checkbox" checked={marcado} onChange={(e) => onChange(e.target.checked)} />
      <span>{children}</span>
    </label>
  );
}
