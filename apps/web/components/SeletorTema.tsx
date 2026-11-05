"use client";

import { ROTULOS_PREFERENCIA, type PreferenciaTema } from "@/lib/tema";
import { usePandora } from "@/lib/pandora/PandoraProvider";
import { useTema } from "./TemaProvider";

const PREFERENCIAS = Object.keys(ROTULOS_PREFERENCIA) as PreferenciaTema[];

export function SeletorTema() {
  const { Cartao, Segmento } = usePandora();
  const { preferencia, definirPreferencia } = useTema();

  return (
    <Cartao titulo="Aparência">
      <p>Escolha o tema da tela. Em Sistema, o PANDORA segue o seu aparelho.</p>
      <Segmento
        rotulo="Tema"
        opcoes={PREFERENCIAS.map((p) => ROTULOS_PREFERENCIA[p])}
        valor={ROTULOS_PREFERENCIA[preferencia]}
        onChange={(rotulo) => {
          const escolhida = PREFERENCIAS.find((p) => ROTULOS_PREFERENCIA[p] === rotulo);
          if (escolhida) definirPreferencia(escolhida);
        }}
      />
    </Cartao>
  );
}
