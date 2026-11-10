// Gera os ícones do PWA a partir da marca do design system.
// Rode de novo (`npm run icones -w @pandora/web`) se a marca ou a cor mudarem.
import { mkdir, readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const require = createRequire(import.meta.url);
const ds = path.dirname(require.resolve("@pandora/design-system/package.json"));
const saida = fileURLToPath(new URL("../public/icons/", import.meta.url));

const tokens = JSON.parse(await readFile(path.join(ds, "tokens.json"), "utf8"));
// Registro do mito: marca em tinta sobre laranja-vaso, igual nos dois temas.
const fundo = tokens.color.tokens.find((t) => t.name === "laranja-vaso").value;
const marca = await readFile(path.join(ds, "assets/Marca/caixa-esperanca.svg"));
const LADO_SVG = 96; // viewBox da marca

// [arquivo, lado em px, fração ocupada pela marca]
// O ícone mascarável deixa a marca dentro da zona segura (círculo de 80%).
const ICONES = [
  ["icone-192.png", 192, 0.72],
  ["icone-512.png", 512, 0.72],
  ["icone-mascaravel-512.png", 512, 0.56],
  ["apple-touch-icon.png", 180, 0.72],
];

await mkdir(saida, { recursive: true });
for (const [arquivo, lado, fracao] of ICONES) {
  const ladoMarca = Math.round(lado * fracao);
  const marcaPng = await sharp(marca, { density: Math.ceil((72 * ladoMarca) / LADO_SVG) })
    .resize(ladoMarca, ladoMarca)
    .png()
    .toBuffer();
  await sharp({ create: { width: lado, height: lado, channels: 4, background: fundo } })
    .composite([{ input: marcaPng, gravity: "centre" }])
    .png()
    .toFile(path.join(saida, arquivo));
  console.log(`${arquivo} (${lado}px)`);
}
