"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { ROTA_COMECAR } from "@/components/abertura/Abertura";
import { ROTA_DEPOIS_DAS_PERGUNTAS } from "@/components/abertura/Perguntas";
import { BotaoEnviar } from "@/components/Controlados";
import { cadastrar, entrar, ErroApi } from "@/lib/api/cliente";
import { destinoDepoisDeEntrar } from "@/lib/conta/consentimento";
import { dadosReais } from "@/lib/conta/modo";
import { guardarSessao } from "@/lib/conta/sessao";
import { usePandora } from "@/lib/pandora/PandoraProvider";

const CRIAR = "Criar conta";
const ENTRAR = "Já tenho conta";
const MODOS = [CRIAR, ENTRAR];

/**
 * Login e cadastro (#71). Só existe com os dados reais ligados; com eles
 * desligados, a rota manda direto para o Início, que usa a demonstração.
 */
export function Entrar() {
  const { Segmento } = usePandora();
  const router = useRouter();
  const [modo, setModo] = useState(CRIAR);
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const titulo = useRef<HTMLHeadingElement>(null);
  const idEmail = useId();
  const idSenha = useId();
  const idDica = useId();
  const criando = modo === CRIAR;

  useEffect(() => {
    if (!dadosReais()) router.replace(ROTA_DEPOIS_DAS_PERGUNTAS);
  }, [router]);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    if (enviando) return;
    setEnviando(true);
    setErro(null);
    try {
      if (criando) await cadastrar(email, senha);
      guardarSessao(await entrar(email, senha));
      const destino = await destinoDepoisDeEntrar();
      router.replace(destino === "inicio" ? ROTA_DEPOIS_DAS_PERGUNTAS : ROTA_COMECAR);
    } catch (falha) {
      setErro(falha instanceof ErroApi ? falha.message : "Algo deu errado. Tente de novo.");
      setEnviando(false);
      titulo.current?.focus();
    }
  }

  if (!dadosReais()) return null;

  return (
    <div className="pd-pergunta-tela">
      <h1 className="pd-pergunta-titulo" ref={titulo} tabIndex={-1}>
        {criando ? "Crie a sua conta" : "Entre na sua conta"}
      </h1>
      <p className="pd-pergunta-sub">
        A conta guarda o seu Raio-X. O PANDORA só lê, e você apaga tudo quando quiser.
      </p>
      <Segmento
        rotulo="Criar conta ou entrar"
        opcoes={MODOS}
        valor={modo}
        onChange={(valor) => {
          setModo(valor);
          setErro(null);
        }}
      />
      <form className="app-formulario" onSubmit={enviar}>
        <div className="app-campo-grupo">
          <label className="app-rotulo" htmlFor={idEmail}>
            E-mail
          </label>
          <input
            id={idEmail}
            className="app-campo"
            type="email"
            autoComplete="email"
            inputMode="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="app-campo-grupo">
          <label className="app-rotulo" htmlFor={idSenha}>
            Senha
          </label>
          <input
            id={idSenha}
            className="app-campo"
            type="password"
            autoComplete={criando ? "new-password" : "current-password"}
            required
            minLength={criando ? 8 : undefined}
            maxLength={128}
            aria-describedby={criando ? idDica : undefined}
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />
          {criando ? (
            <p id={idDica} className="pd-apoio">
              Pelo menos 8 caracteres.
            </p>
          ) : null}
        </div>
        {erro ? (
          <p role="alert" className="app-erro">
            {erro}
          </p>
        ) : null}
        <BotaoEnviar desativado={enviando}>{enviando ? "Entrando…" : criando ? "Criar e entrar" : "Entrar"}</BotaoEnviar>
      </form>
    </div>
  );
}
