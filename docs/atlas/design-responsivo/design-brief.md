# Design brief: design responsivo e temas do mito

Lane Design, modo brief. Base: `frontend/design-system` (README.md, tokens.json, src/bundle.src.css, src/bundle.body.js, src/ornamentos.js).

## 1. Direção visual

O vaso grego continua sendo a moldura, e a leitura continua sendo o centro. A mudança troca a serra pelo meandro, dá ao mito uma versão em figura vermelha para o tema escuro e faz o vaso caber de 320px a 1440px sem virar outra coisa. Em tela larga, a base preta do vaso vira um trilho lateral com Elpis no topo, como a faixa vertical de uma ânfora. O detalhe memorável é a faixa de lancetas com rosáceas, só no painel da abertura. Evite: ornamento atrás de texto, meandro girado em quatro sentidos, conteúdo esticado de ponta a ponta em monitor largo, cena ampliada e borrada, e tema escuro que apague o limite entre mito e leitura.

## 2. Tokens usados

Existentes: `tinta`, `papiro`, `laranja-vaso`, `laranja-claro`, `base`, `superficie`, `cartao`, `texto`, `texto-2`, `ornamento`, `foco`, `espaco-2` a `espaco-8`, `raio-md`, `raio-pilula`, `alvo-minimo`, `altura-botao`, `marca-xl`, `marca-lg`, `marca-md`, `corpo`, `apoio`, `valor-xl`, `valor-lg`, `--orn-meandro-fino`, `--orn-rosacea`.

Cores semânticas novas (o mito deixa de ter cor fixa; Elpis, brasões e a cena nunca recolorem):

| Token | Claro (figura negra) | Escuro (figura vermelha) | Motivo |
| --- | --- | --- | --- |
| `mito-fundo` | `#f0792b` (laranja-vaso) | `#0e0a07` (base) | Campo do vaso |
| `mito-figura` | `#1a1410` (tinta) | `#f0792b` (laranja-vaso) | Título, subtítulo, ícones, meandro, foco |
| `mito-destaque` | `#1a1410` (tinta) | `#ff9a55` (laranja-claro) | Número-herói |
| `mito-sobre-figura` | `#fbf5ea` (papiro) | `#1a1410` (tinta) | Texto em botão e selo mito |

Ornamentos novos em `ornamentos.js`: `meandro` (o ladrilho de 26x22 hoje fixo em `.pd-meandro`, convertido em máscara para aceitar `mito-figura`), `meandro-vertical` (a mesma faixa girada 90 graus, um só sentido) e `lanceta` (lingueta laranja apontando para baixo, ladrilho 14x12). A fileira de rosáceas reaproveita `--orn-rosacea` em 12px. `serra-alta` e `.pd-serra` saem do mito e da navegação. `serra-fina` fica no aviso de alerta, onde é forma de estado.

Layout e tipo fluido (novos, em `rem` para respeitar o zoom do sistema):

- `largura-conteudo-medio`: `clamp(40rem, 90cqi, 45rem)` (640 a 720px).
- `largura-conteudo-max`: `75rem` (1200px). `largura-chat`: `47.5rem` (760px). `largura-cena`: `25rem` (400px).
- `largura-trilho`: `6rem` (96px) no expandido, `5.5rem` (88px) na paisagem baixa.
- `marca-xl`: `clamp(2.5rem, 1.6rem + 3cqi, 3.5rem)`. `marca-lg`: `clamp(1.75rem, 1.3rem + 1.6cqi, 2.25rem)`. `marca-md` fica em 22px.
- `valor-xl`: `clamp(2.625rem, 2rem + 2.4cqi, 3.5rem)`, com `tabular-nums`.
- `corpo` fica em 17px (1.0625rem). O piso pedido é 16px; o README já exige 17px por causa da altura de x da Optima, e o mais rígido vale.

## 3. Telas e estados

Faixas: `.pd-tela` vira fluida (`width: 100%`, sem 390px nem raio de 44px fora da Galeria) e declara `container-type: inline-size`. As faixas usam `@container`, e a paisagem baixa usa `@media (max-height: 500px) and (orientation: landscape)`.

**CabecalhoMito.** Meandro em cima e embaixo, em `mito-figura` sobre `mito-fundo`. Estados: com número-herói; sem número (só título e subtítulo); título longo (quebra com `text-wrap: balance`, até cinco palavras); foco em botão interno. No escuro, o meandro de baixo é obrigatório: é o único limite visível entre o mito e a leitura. No expandido, o cabeçalho ocupa a largura do conteúdo, não a da janela.

**TelaAbertura (passos 0 a 3).** Compacta: cena em cima, meandro, painel preto com a faixa de lancetas no topo. Média: cena centrada até `largura-cena`, painel até 720px. Expandida: cena à esquerda até 400px sobre campo laranja, painel à direita, faixa de lancetas no topo do painel. Estados: imagem carregando (campo laranja reservado com `aspect-ratio: 400 / 413`, sem salto de layout); imagem com erro (campo laranja e `alt` atual, painel segue usável); passos 1 a 3 com o mesmo cabeçalho de lancetas; tema escuro (a cena e seu campo ficam laranja, como o medalhão).

**NavBase.**
- Compacta (<600px): barra inferior em `base`. No lugar da serra, um filete de meandro fino laranja de 8px na borda de cima, interrompido no arco do medalhão de Elpis.
- Média (600 a 1023px): a base preta segue de ponta a ponta, e a grade dos 5 itens fica contida em 560px, centrada, com o arco no centro.
- Paisagem baixa (altura até 500px): trilho à esquerda de 88px, Elpis no topo, itens de 48px de altura, rótulos sempre visíveis.
- Expandida (≥1024px): trilho à esquerda de 96px, Elpis no topo, meandro vertical laranja na borda direita do trilho.

Estados: item ativo, Elpis ativa, Elpis ouvindo, foco e toque.

**Conteúdo.** Média: coluna centrada de 640 a 720px. Expandida: grade de 2 colunas até 1200px, com cartões em `espaco-3`. Chat (TelaElpis): uma coluna de até 760px, balões até 70% dela.

**TelaCrise e TelaGuardiaoAmpliada.** `.pd-sem-ornamento` remove meandro, lanceta e meandro vertical. `.pd-contido` deixa só filetes, sem lanceta. Uma coluna em todas as faixas, com no máximo 720px.

Vazio, carregando e erro das listas e do chat não mudam. Esta entrega só troca moldura, tema e grade.

## 4. Acessibilidade

Contraste calculado (WCAG 2.x, luminância relativa):

| Par | Claro | Escuro | Exigido |
| --- | --- | --- | --- |
| `mito-figura` sobre `mito-fundo` (título, subtítulo de 17px) | 6,49:1 | 7,02:1 | 4,5:1 |
| `mito-destaque` sobre `mito-fundo` (número-herói) | 6,49:1 | 9,39:1 | 3:1 (texto grande) |
| `mito-sobre-figura` sobre `mito-figura` (botão e selo mito) | 16,81:1 | 6,49:1 | 4,5:1 |
| Foco `mito-figura` sobre `mito-fundo` | 6,49:1 | 7,02:1 | 3:1 |
| Meandro e lanceta `laranja-vaso` sobre `base` | 6,49:1 | 7,02:1 | decorativo |
| Rótulo da nav `papiro` sobre `base` | 16,81:1 | 18,17:1 | 4,5:1 |
| Item ativo `laranja-claro` sobre `base` | 8,69:1 | 9,39:1 | 4,5:1 |
| Limite `mito-fundo` x `superficie` | 2,59:1 | 1,08:1 | sem exigência; ver risco 1 |

Ordem de foco e marcos: `nav` vem antes de `main` no DOM em todas as faixas, para que o trilho visual à esquerda e o foco andem juntos. Um link "Ir para o conteúdo" é o primeiro foco. Ordem no trilho: Elpis, Início, Dívidas, Trilha, Guardião. Na barra inferior, o DOM segue a ordem visual (Início, Dívidas, Elpis, Trilha, Guardião), então a ordem do trilho é a mesma da barra com Elpis movida para o topo: manter um único DOM e reordenar com CSS fere 2.4.3. A solução é renderizar Elpis por primeiro no DOM só no trilho, ou aceitar Elpis no meio também no trilho. Decidir na spec.

Rótulos: `nav` mantém `aria-label="Navegação principal"`, item ativo com `aria-current="page"`. Meandro, lanceta e rosáceas são `aria-hidden` e ficam em pseudo-elemento ou `background`.

Alvos: itens de navegação com no mínimo 44x44px em todas as faixas, incluindo o trilho da paisagem baixa.

Zoom e reflow: tipo em `rem` e `clamp()`, sem `px` fixo nos títulos. A 320px de largura (zoom 400%) a faixa compacta vale, sem rolagem horizontal (1.4.10).

Movimento: nada novo se move. O giro do anel de Elpis e o pulso do `BotaoVoz` param com `prefers-reduced-motion`, como hoje. A troca de faixa não anima o trilho.

## 5. Fora do escopo

- Desenho de Elpis, dos brasões, dos emblemas e da cena. Nenhum deles recolore.
- Tokens do registro de leitura e seus valores nos dois temas.
- Formas de aviso (a serra fina continua no alerta), balões, botões, cartões e rolagem.
- Conteúdo, voz e fluxos das telas. Nova arte da cena em alta resolução, que é só pedida aqui.
- Qualquer pasta `teste/`.

## Riscos

1. **Mito escuro funde com a leitura.** `#0e0a07` sobre `#1a1410` dá 1,08:1. Sem o meandro de baixo, o cabeçalho some no corpo. O meandro laranja embaixo é obrigatório no escuro, inclusive em `.pd-contido` (como filete). Em `.pd-sem-ornamento`, usar uma linha de 2px em `mito-figura`.
2. **Cena ampliada e borrada.** `pandora-cena.png` tem 400x413px. Em tela 2x já sai ampliada no celular e no expandido. Pedir versão de 800 e 1200px com `srcset`, ou SVG. Até lá, nunca passar de 400px em CSS.
3. **Ordem de foco no trilho.** Elpis no topo do trilho e no meio da barra é ordem visual diferente da do DOM. Ver Acessibilidade.
4. **Foco invisível no mito escuro.** `.pd-mito :focus-visible` está fixo em `#1a1410`, que dá 1,08:1 sobre o fundo escuro. Trocar para `mito-figura`.
5. **Cores fixas no código.** `.pd-mito`, `.pd-status[data-topo="mito"]`, `.pd-botao-mito`, `.pd-selo-mito` e o SVG de `.pd-meandro` usam `#f0792b` e `#1a1410` direto. Precisam passar pelos tokens novos, ou o tema escuro do mito não acontece.
6. **Ruído na nav.** O filete de meandro na borda e o indicador de item ativo (também meandro laranja) ficam a 3px um do outro. Mover o indicador para baixo do rótulo ou trocar por barra lisa de 3px.
7. **Meandro vertical.** Girar a faixa inteira 90 graus, num só sentido. Nunca espelhar nem compor cantos, para não formar cruz gancheada.
8. **Paisagem baixa apertada.** Em 360px de altura, Elpis (60px) mais 5 itens de 48px mais respiros passa do limite. Reduzir Elpis para 48px no trilho (busto em anel simples) ou permitir rolagem do trilho.
9. **Campo laranja no escuro.** Na abertura expandida, a cena fica sobre campo laranja também no tema escuro. É coerente com "a cena não recolore", mas é uma área grande e clara. Confirmar com o usuário.
