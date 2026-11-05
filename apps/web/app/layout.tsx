import type { Metadata, Viewport } from "next";
import "@pandora/design-system/tokens.css";
import "@pandora/design-system/components/bundle.css";
import "./globals.css";
import { CascaApp } from "@/components/CascaApp";
import { TemaProvider } from "@/components/TemaProvider";
import { PandoraProvider } from "@/lib/pandora/PandoraProvider";
import { scriptTemaInicial } from "@/lib/tema";
import { corDoToken } from "@/lib/tokens";

export const metadata: Metadata = {
  title: { default: "PANDORA", template: "%s · PANDORA" },
  description: "Copiloto financeiro com IA. Entenda suas dívidas e recupere o controle do seu dinheiro.",
  applicationName: "PANDORA",
  appleWebApp: { capable: true, title: "PANDORA", statusBarStyle: "default" },
  icons: {
    icon: [{ url: "/icons/icone-192.png", sizes: "192x192", type: "image/png" }],
    apple: "/icons/apple-touch-icon.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // Sem maximumScale: a pessoa precisa poder ampliar a tela (WCAG 1.4.4).
  viewportFit: "cover",
  // O topo das telas é o cabeçalho do mito, que tem a mesma cor nos dois temas.
  themeColor: corDoToken("laranja-vaso"),
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // data-theme é trocado por scriptTemaInicial antes da pintura.
    <html lang="pt-BR" data-theme="light" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: scriptTemaInicial }} />
      </head>
      <body>
        <TemaProvider>
          <PandoraProvider>
            <CascaApp>{children}</CascaApp>
          </PandoraProvider>
        </TemaProvider>
      </body>
    </html>
  );
}
