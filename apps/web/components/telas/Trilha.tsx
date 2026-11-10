"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { usePandora } from "@/lib/pandora/PandoraProvider";

export const ROTA_LICAO = "/trilha/licao";

/**
 * Tela 5a da galeria. O caminho usa as seis etapas padrão do `TrilhaCaminho`
 * (2 concluídas, a 3ª em andamento): são dados de demonstração.
 */
export function Trilha() {
  const { CabecalhoMito, TrilhaCaminho, Cartao, Selo, Botao } = usePandora();
  const router = useRouter();

  useEffect(() => {
    router.prefetch(ROTA_LICAO);
  }, [router]);

  return (
    <>
      <CabecalhoMito titulo="Da caixa à esperança">
        <p className="pd-mito-sub">2 de 6 etapas concluídas · sem prazo, no seu ritmo</p>
      </CabecalhoMito>
      <div className="pd-corpo">
        <TrilhaCaminho />
        <Cartao sobre="Etapa 3 · cerca de 4 minutos" titulo="O rotativo e o teto de 100%">
          <p>Usa os números da sua fatura. Você pode refazer qualquer lição quando quiser.</p>
          <div>
            <Selo tom="fonte">Banco Central do Brasil</Selo>
          </div>
          <Botao bloco seta onClick={() => router.push(ROTA_LICAO)}>
            Continuar lição
          </Botao>
        </Cartao>
        <Cartao tom="apoio" marco sobre="Próximo marco" titulo="Conheço meus direitos">
          <p>Chega com a etapa 4, Repactuação. Fica com você depois de conquistado.</p>
        </Cartao>
      </div>
    </>
  );
}
