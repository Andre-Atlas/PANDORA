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

### Elpis e Trilha com dados reais

O Elpis e a Trilha usam a API, que chama o RAG. Suba os três, cada um no seu terminal:

```bash
cd services/rag && uv run pandora-rag servir        # RAG em :8010 (carrega os modelos em ~1 min)
cd apps/api && uv run uvicorn pandora_api.principal:app --port 8000
npm run dev                                         # web em :3000
```

A URL da API vem de `NEXT_PUBLIC_PANDORA_API_URL` (padrão `http://localhost:8000`). O resto do app continua com dados de demonstração.

## Como está organizado

```
app/
  layout.tsx          tokens.css + bundle.css, tema e provedores
  manifest.ts         manifesto do PWA (cores lidas de tokens.json)
  page.tsx            Abertura, a página de entrada (sem navegação)
  (app)/layout.tsx    casca com navegação para as abas
  (app)/inicio/ dividas/ elpis/ trilha/ guardiao/   uma rota por aba
  (app)/inicio/metas/                 Metas e previsão (tela 7), aberta pelo Início
  (fluxo)/layout.tsx  casca de tela cheia, sem navegação
  (fluxo)/comecar/    perguntas da Abertura (telas 1b a 1d)
  (fluxo)/trilha/licao/        lição da trilha (tela 5b)
  (fluxo)/guardiao/verificacao/  veredito do boleto em leitura ampliada (E2)
components/
  CascaApp.tsx        conteúdo + navegação (ou a tela de crise)
  abertura/           página de entrada, perguntas e o portão da abertura
  telas/              uma tela por rota, montada com os componentes do design system
  Controlados.tsx     peças do design system que ainda não aceitam handlers, refeitas com as mesmas classes
  AvisoDemo.tsx       aviso "Demonstração" para ações que ainda não existem
  crise/              fluxo de crise: estado, tela e entrada pelo Guardião
  guardiao/           guia de autoexclusão e sua entrada no Guardião
  BotaoLink.tsx       link com a aparência do Botao (ligar, abrir página)
  NavegacaoInferior.tsx   NavBase ligada ao roteador
  TemaProvider.tsx    preferência de tema (Sistema, Claro, Escuro)
  SeletorTema.tsx     Segmento para trocar o tema
lib/
  api/                tipos do contrato da API (esquema.d.ts é gerado)
  pandora/            carregamento do bundle.js e usePandora()
  tema.ts             regras do tema e script que roda antes da pintura
  tokens.ts           leitura de tokens.json para onde CSS não chega
  navegacao.ts        abas e rotas
  abertura/portao.ts  a abertura aparece a cada sessão nova
  demo/dados.ts       dados de demonstração das telas (os da galeria), até a API entregar os reais
  crise/contatos.ts   contatos de apoio, cada um com a fonte oficial conferida
  guardiao/fontes.ts  normas e links do guia de autoexclusão, com data de revisão
scripts/gerar-icones.mjs  ícones do PWA a partir da marca
```

## Tipos da API

`lib/api/esquema.d.ts` é gerado de `apps/api/openapi.json` com `npm run api:tipos -w @pandora/web`. Não edite à mão. Use os nomes curtos de `lib/api/tipos.ts`:

```ts
import type { Transacao, RespostaChat } from "@/lib/api/tipos";
```

Se a API mudar e os tipos ficarem para trás, o teste `lib/api/esquema.test.ts` falha.

## Decisões

**O design system é um pacote do workspace.** `frontend/design-system` virou `@pandora/design-system`. O app importa tokens, CSS e componentes de lá, sem copiar nada. Quando o design system mudar, o app muda junto.

**O `bundle.js` é carregado só no navegador.** Ele foi feito para `<script>`: lê `window.React` ao rodar e publica os componentes em `window.Pandora`. Por isso `lib/pandora/carregar.ts` define `window.React` e só depois faz `import()` do bundle. Um `import` estático seria içado e rodaria antes. Em qualquer componente cliente:

```tsx
const { Cartao, Botao } = usePandora();
```

Os tipos vêm de `components/index.d.ts`. Enquanto o bundle carrega, o app mostra "Carregando o PANDORA". Por isso o HTML do servidor ainda não traz o conteúdo das telas.

**Cores nunca são redefinidas.** A interface usa só as variáveis de `tokens.css`. O manifesto e o `theme-color`, que não leem CSS, usam `corDoToken()`, que lê `tokens.json`. Os ícones também saem do token `laranja-vaso` (`npm run icones -w @pandora/web`).

**Tema.** O padrão é seguir o aparelho (`prefers-color-scheme`). A escolha Claro ou Escuro fica no `localStorage`. Um script no `<head>` aplica `data-theme` antes da primeira pintura, para não piscar. O seletor está provisoriamente no Início.

**Casca e layout responsivo.** O app usa a moldura fluida do design system (`docs/atlas/design-responsivo/design-brief.md`): `CascaApp` monta `.pd-fluido > .pd-tela > .pd-tela-interior > (main, NavBase)`. A `.pd-tela` mede a própria largura (container `pd-tela`), e o `bundle.css` decide as faixas. O app não redefine nenhuma:

- **até 599px:** uma coluna, navegação presa embaixo, com a área segura do aparelho;
- **600 a 1023px:** conteúdo numa coluna de até 720px, navegação embaixo com os itens em até 640px;
- **a partir de 1024px:** a navegação vira trilho lateral, com meandro de pé na borda, e os cartões vão para duas colunas até 1200px. A conversa da Elpis fica numa coluna de até 760px;
- **celular deitado (altura até 520px):** trilho lateral, para devolver a altura ao conteúdo.

O conteúdo vem antes da navegação no DOM: o trilho só muda a posição visual. A navegação é retrátil, e a escolha fica no `localStorage` (`pandora-nav-recolhida`) para não reabrir a cada tela. No tema escuro o cabeçalho do mito fica preto (figura vermelha), e `aplicarTema` troca o `theme-color` para a mesma cor.

**Abertura (página de entrada).** Fica em `/`, fora do grupo `(app)`, então não tem navegação. O topo é a `.pd-abertura` do design system, do tamanho da janela: a cena nítida se dissolve num esfumado da própria cena, com lancetas, nome, "Ainda há esperança…" e "Começar". No celular a cena fica em cima; a partir de 800px, à esquerda. Abaixo vêm "O que tem dentro" (uma linha por aba, com textos da galeria) e "O combinado" (da tela 1d). O fluxo de crise também cobre a abertura. "Começar" leva às perguntas (`/comecar`, telas 1b a 1d), e "Abrir minha caixa" leva ao Início.

**A abertura aparece toda vez que o site é aberto.** `/` sempre mostra a abertura, mesmo para quem já começou. Quem abre uma tela do app direto numa sessão nova (aba nova, PWA iniciado, link colado) volta para `/` (`PortaoAbertura`, nos layouts `(app)` e `(fluxo)`). Ver a abertura libera as telas para aquela sessão (`sessionStorage`), então recarregar a página na mesma aba não volta para a abertura. Sem `sessionStorage` disponível, o portão deixa passar.

**Telas com dados de demonstração.** Todas as abas reproduzem a galeria com os componentes do design system, não com as `Tela*` estáticas. Os números e textos de exemplo (Carla, Diego, Júlia, Sr. Antônio) ficam em `lib/demo/dados.ts`: troque cada bloco pela chamada da API quando ela existir. O que funciona de verdade: navegação entre as telas, as perguntas da Abertura, os segmentos (Avalanche/Bola de Neve, Golpes/Apostas), a lição, o modo voz da Elpis (sem gravar), "Ouvir de novo" (síntese de voz do navegador), o guia de autoexclusão e o fluxo de crise. Perguntas novas à Elpis recebem uma resposta de demonstração até o chat (#80). Botões de ações que ainda não existem (gerar dossiê, copiar dados do Pix, avisar alguém) mostram o aviso "Demonstração".

**Aceite começa desmarcado.** A galeria mostra o `Consentimento` marcado, mas a LGPD exige que a pessoa marque por conta própria. "Abrir minha caixa" fica desativado até o aceite.

**Fluxo de crise (#81, RF05).** Fica num contexto acima de todas as rotas (`useCrise()`). Quando está ativo, a casca troca qualquer tela pela de apoio e tira a navegação. Nada de metas, avisos ou cobranças até a pessoa tocar em "Voltar quando eu quiser". O estado fica no `sessionStorage`, então recarregar a página não tira a pessoa da tela de apoio. O foco vai para o título ao abrir.

- Hoje a tela abre pelo Guardião ("Precisa de apoio agora?"). O chat (#80) deve chamar `abrirCrise()` quando o classificador de crise (#64) disparar.
- Toda meta ou aviso que for criado (#87, notificações) precisa checar `useCrise().ativa` antes de aparecer, porque a tela promete "Pausei metas e avisos".
- Os contatos ficam em `lib/crise/contatos.ts`, cada um com a fonte oficial e a data em que foi conferido (5/11/2026). Os botões de contato são `<a>` com a aparência de `Botao`, porque o `Botao` do design system é sempre `<button>` e não aceita `href`.

**Guia de autoexclusão (#81, RF11).** Fica em `/guardiao/autoexclusao`. Com a MP nº 1.394/2026 as bets estão proibidas e a plataforma oficial de autoexclusão saiu do ar, mas sites ilegais continuam aparecendo. Por isso o guia mostra o que a pessoa ainda controla:

1. bloquear os sites no aparelho (BetBlocker, gratuito e sem fins lucrativos);
2. baixar o limite noturno do Pix (Resolução BCB nº 142/2021);
3. não pagar site de apostas, porque Pix, TED e boleto para apostas são proibidos (MP, art. 14, e Resoluções BCB nº 595, 596 e 597/2026);
4. denunciar o site no Fala.BR;
5. pedir apoio pelo fluxo de crise.

Toda afirmação sobre lei leva `CitacaoCartao`, e as fontes ficam em `lib/guardiao/fontes.ts`. A MP precisa ser votada até 23/11/2026 (`REVISAR_ATE`). Depois disso, um teste falha de propósito, pedindo para conferir de novo as fontes e o texto. Ficaram de fora os controles do iPhone: a página da Apple é para pais e não confirma o uso no aparelho do próprio adulto.

## Pendências conhecidas

- **Respostas da Abertura (#71):** as perguntas existem, mas as respostas não vão para lugar nenhum. O nível da `EscalaSentimento` nem pode ser lido, porque ela não tem `onChange`.

- **Contatos do fluxo de crise, para o grupo decidir:**
  - **Jogadores Anônimos** está fora da tela. Nenhuma fonte oficial confirmou o site: `jogadoresanonimos.com.br` responde, mas não deu para confirmar que é o JA Brasil. Quando alguém confirmar, basta preencher `href` e `fonte` em `contatos.ts`.
  - **"Encontrar um CAPS AD"** abre a página de CAPS do Ministério da Saúde, porque não há buscador nacional oficial confirmado. A página explica que o CAPS atende sem consulta marcada e como achar o mais próximo (UBS ou Secretaria de Saúde).
  - **SAMU 192** foi acrescentado para perigo imediato. Não está na galeria; o grupo deve validar.
- **Proibição das apostas (MP nº 1.394, de 25/9/2026):** proíbe as apostas de quota fixa no Brasil. Por causa dela, a Plataforma Centralizada de Autoexclusão está indisponível. O guia de autoexclusão foi adaptado (veja acima), e o texto da galeria ("Guia passo a passo para sites .bet.br") foi trocado. O grupo ainda precisa decidir como ficam a aba Apostas do Guardião, o RF04 e a lista de operadoras da SPA/MF (#59), que deixou de existir.

- **Componentes que ainda não podem ser controlados:** `CampoPergunta`, `Consentimento`, `Alternador` e `EscalaSentimento` não têm `onChange` nem `value`, e o `Alternador` guarda o próprio estado. `Progresso` (voltar e pular), `CabecalhoMito` (voltar), `Insight` (ação), `TrilhaCaminho` (etapas) e `CitacaoCartao` também não recebem handlers. Por isso `components/Controlados.tsx` refaz `Progresso`, `CabecalhoMito` com voltar, `Insight`, `CampoPergunta` e `Consentimento` com as mesmas classes. Quando o design system aceitar esses props, troque pelas originais. As travas do Guardião ainda não são salvas (#81).
- **Ordem dos títulos:** o `Cartao` sempre usa `<h3>`, então a página vai de `<h1>` direto para `<h3>`. É o único item que o Lighthouse aponta (acessibilidade 98). Resolver no design system, com um nível de título configurável.
- **Fontes vêm do Google Fonts** (`@import` no `bundle.css`), então não carregam sem internet. A demo sem internet (#94) vai precisar de fontes locais e de um service worker.
- **Bundle em ES module:** se o `src/build.js` gerar também uma versão ESM, o carregamento fica mais simples e o conteúdo pode vir já no HTML do servidor.
