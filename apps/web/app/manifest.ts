import type { MetadataRoute } from "next";
import { corDoToken } from "@/lib/tokens";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "PANDORA",
    short_name: "PANDORA",
    description: "Copiloto financeiro com IA. Entenda suas dívidas e recupere o controle do seu dinheiro.",
    lang: "pt-BR",
    dir: "ltr",
    start_url: "/",
    scope: "/",
    display: "standalone",
    orientation: "portrait",
    // O manifesto não lê variáveis CSS, então as cores vêm de tokens.json.
    background_color: corDoToken("superficie", "light"),
    theme_color: corDoToken("laranja-vaso"),
    icons: [
      { src: "/icons/icone-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icone-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icons/icone-mascaravel-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
