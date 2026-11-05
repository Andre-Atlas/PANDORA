# PANDORA · app web (PWA)

App em Next.js 16 e TypeScript, montado sobre o [design system](../../frontend/design-system/README.md). Issue de origem: #61.

## Como rodar

Na raiz do repositório:

```bash
npm install
npm run dev        # http://localhost:3000
npm test           # Vitest
npm run lint       # ESLint com as regras de acessibilidade (jsx-a11y)
npm run typecheck
npm run build
```

Para testar a instalação como PWA, rode `npm run build && npm start -w @pandora/web` e abra no Chrome ou Edge. Em DevTools → Application → Manifest, o app deve aparecer como instalável.

## Como está organizado

```
app/
  layout.tsx          tokens.css + bundle.css, tema, provedores e casca
  manifest.ts         manifesto do PWA (cores lidas de tokens.json)
  inicio/ dividas/ elpis/ trilha/ guardiao/   uma rota por aba
components/
  CascaApp.tsx        conteúdo + navegação inferior
  NavegacaoInferior.tsx   NavBase ligada ao roteador
  TemaProvider.tsx    preferência de tema (Sistema, Claro, Escuro)
  SeletorTema.tsx     Segmento para trocar o tema
  TelaProvisoria.tsx  ocupa cada rota até a tela real chegar
lib/
  pandora/            carregamento do bundle.js e usePandora()
  tema.ts             regras do tema e script que roda antes da pintura
  tokens.ts           leitura de tokens.json para onde CSS não chega
  navegacao.ts        abas e rotas
scripts/gerar-icones.mjs  ícones do PWA a partir da marca
```

## Decisões

**O design system é um pacote do workspace.** `frontend/design-system` virou `@pandora/design-system`. O app importa tokens, CSS e componentes de lá, sem copiar nada. Quando o design system mudar, o app muda junto.

**O `bundle.js` é carregado só no navegador.** Ele foi feito para `<script>`: lê `window.React` ao rodar e publica os componentes em `window.Pandora`. Por isso `lib/pandora/carregar.ts` define `window.React` e só depois faz `import()` do bundle. Um `import` estático seria içado e rodaria antes. Em qualquer componente cliente:

```tsx
const { Cartao, Botao } = usePandora();
```

Os tipos vêm de `components/index.d.ts`. Enquanto o bundle carrega, o app mostra "Carregando o PANDORA". Por isso o HTML do servidor ainda não traz o conteúdo das telas.

**Cores nunca são redefinidas.** A interface usa só as variáveis de `tokens.css`. O manifesto e o `theme-color`, que não leem CSS, usam `corDoToken()`, que lê `tokens.json`. Os ícones também saem do token `laranja-vaso` (`npm run icones -w @pandora/web`).

**Tema.** O padrão é seguir o aparelho (`prefers-color-scheme`). A escolha Claro ou Escuro fica no `localStorage`. Um script no `<head>` aplica `data-theme` antes da primeira pintura, para não piscar. O seletor está provisoriamente no Início.

**Casca.** O app usa a classe `.pd-tela` para herdar fonte, cor e foco do design system, mas ocupa a tela inteira em vez da moldura de 390×844 da galeria. A navegação fica presa ao rodapé e respeita a área segura do iPhone. O conteúdo vem antes da navegação no DOM.

## Pendências conhecidas

- **Componentes que ainda não podem ser controlados:** `CampoPergunta`, `Consentimento`, `Alternador` e `EscalaSentimento` não têm `onChange` nem `value`, e o `Alternador` guarda o próprio estado. A Abertura (#71), o chat (#80) e as travas (#81) precisam disso no design system.
- **As `Tela*` não recebem dados:** são as telas estáticas da galeria. As telas reais devem ser montadas com os componentes menores.
- **Ordem dos títulos:** o `Cartao` sempre usa `<h3>`, então a página vai de `<h1>` direto para `<h3>`. É o único item que o Lighthouse aponta (acessibilidade 98). Resolver no design system, com um nível de título configurável.
- **Fontes vêm do Google Fonts** (`@import` no `bundle.css`), então não carregam sem internet. A demo sem internet (#94) vai precisar de fontes locais e de um service worker.
- **Bundle em ES module:** se o `src/build.js` gerar também uma versão ESM, o carregamento fica mais simples e o conteúdo pode vir já no HTML do servidor.
