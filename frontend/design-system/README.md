PANDORA é um copiloto financeiro com IA para pessoas endividadas ou com comportamento compulsivo. No mito, o que fica na caixa é a esperança: o sistema visual leva essa ideia para um app que precisa ser lido por quem está cansado, ansioso ou com pouca visão.

## Princípio: dois registros

Toda tela combina dois registros. Nunca misture os dois no mesmo bloco.

**Registro do mito.** Laranja e preto de vaso grego. Use em `CabecalhoMito`, na abertura, nos marcos da trilha e no medalhão de Elpis. Fundo `mito-fundo`, texto e figuras em `mito-figura`, número-herói em `mito-destaque`, com `Meandro` em cima e embaixo. Comporta um título curto e um único número-herói. No tema claro é figura negra: tinta sobre laranja. No tema escuro é figura vermelha: laranja sobre o preto do vaso. O medalhão de Elpis, os brasões e a cena da abertura não mudam com o tema, porque são a pintura.

**Registro de leitura.** Tudo o que a pessoa precisa decidir: valores, listas, perguntas, respostas. Fundo `superficie`, cartões em `cartao`, texto em `texto` e `texto-2`, ações em `acao`.

## Conteúdo e voz

- Escreva em português do Brasil, com "você", frases curtas e voz ativa. Use o nome da pessoa quando houver.
- Acolha sem julgar. A culpa é dos juros, nunca da pessoa. Escreva "O plano começa pela ordem certa", nunca "Você gastou demais".
- Traduza toda sigla em reais por mês e, quando ajudar, em algo da vida real: "R$ 342,18 da sua fatura foram só juros e IOF. É metade do mercado do mês."
- Dê um único próximo passo por tela.
- Use sentence case em títulos e botões. PANDORA vai sempre em maiúsculas. Sem emoji.
- Botões dizem o que acontece: "Ver o plano", "Gerar dossiê em PDF". Nunca ofereça "Pagar", "Depositar" ou "Investir": o produto só lê e nunca movimenta dinheiro.
- Diante de golpe, seja direto: "Não pague este boleto." Em crise, retire toda meta e cobrança da tela.
- Elpis é o nome da assistente, a Esperança do mito. Ela diz quando não sabe: "prefiro não adivinhar". Nunca recomenda ação, fundo ou título específico.

## Cor

- `laranja-vaso` nunca é cor de texto sobre `superficie` (2,6:1). Texto branco sobre `laranja-vaso` também reprova (2,8:1): use `tinta`.
- Botões e links usam `acao` com `on-acao`. No tema escuro `acao` clareia e `on-acao` escurece.
- `ok`, `alerta` e `fonte` são estados. Nunca use como decoração nem como cor de série. Vêm sempre com ícone e palavra, porque verde e vermelho não se distinguem só pela cor.
- `fonte` também marca o que veio de fonte oficial ou de cálculo determinístico, para separar isso de texto gerado.
- A navegação e outros blocos sobre `base` usam `papiro`, e o item ativo usa `laranja-claro`.
- Anel de foco: 3px sólido em `foco`, com 2px de afastamento. Dentro de `.pd-mito`, `mito-figura`.
- No tema escuro, o mito e a leitura ficam quase do mesmo preto. O meandro de baixo, com o filete em `mito-figura`, é a divisa entre os dois: nunca o retire.

## Tipografia

- Use a família `texto` (Optima) para todo texto e número. Ela vem instalada em Mac e iPhone. Em Android e Windows entra Ysabeau Office, gratuita, e `font-size-adjust` iguala a altura de x das duas.
- Use a família `marca` (Cinzel Decorative) só em títulos importantes, marcos e Abertura: `marca-xl`, `marca-lg`, `marca-md`. Ela pede no mínimo 20px e até cinco palavras. Nunca vai em parágrafo, número ou botão.
- Use a família `acessivel` (Atkinson Hyperlegible Next) só em `TelaGuardiaoAmpliada` e `TelaCrise`, com a classe `.pd-acessivel`. Ali, ler sem esforço vem antes da marca.
- O corpo nunca fica abaixo de 17px (`corpo`), porque a Optima tem altura de x baixa. `apoio`, com 15px, serve só para metadados.
- A Optima só tem pesos 400, 700 e 900. Não peça 500 nem 800.
- Números usam `valor-xl` ou `valor-lg`, com algarismos tabulares e formato brasileiro: R$ 2.100,00.
- Nunca troque letras latinas por letras gregas para dar clima (Σ no lugar de E): isso destrói a leitura.

## Ornamentos

Os motivos gregos saem do vaso e entram no dia a dia da interface: meandro, lanceta, onda, palmeta, ramo, rosácea, coluna e voluta. A serra saiu das bordas: `Serra` continua exportado só por compatibilidade e desenha o meandro de baixo. Todos são vetores próprios. Use `Friso` para faixas soltas. Nas caixas e nos botões, eles já vêm no componente.

- **Caixas de texto:** `Cartao`, `LinhaDivida`, `LinkCartao` e `OpcaoCartao` têm corte de folha, com chave grega nos dois cantos retos.
- **Avisos:** cada estado tem sua forma. Alerta usa serra, ok usa ramo, insight usa palmeta, apoio usa meandro, e fonte oficial usa coluna jônica. A forma reforça o ícone e a palavra.
- **Conversa:** o balão de Elpis tem filete de meandro e cauda em voluta. O balão da pessoa tem linha incisa laranja, como figura negra. Turnos diferentes podem ser separados por `Friso tipo="onda" curto`.
- **Botões:** primário, mito e claro têm filete interno e chave nas pontas. Secundário tem borda dupla. Fantasma não tem ornamento.
- **Rolagem:** a barra é uma coluna com caneluras, capitel e base. Use `Rolagem`, que traz um trilho próprio no toque, onde o sistema ignora o estilo da barra.

Limites que mantêm o refino:

- Um ornamento por bloco, nunca atrás de texto.
- Ornamento decorativo usa `ornamento`. Ornamento que reforça estado ou ação usa `ornamento-forte` ou a cor do estado.
- Ornamento fica parado e escondido de leitores de tela.
- `.pd-contido` deixa só filetes, para a leitura ampliada. `.pd-sem-ornamento` tira todos, para o fluxo de crise.
- O meandro corre em um só sentido. Nunca gire o ladrilho em quatro direções nem use formas de cruz gancheada.
- Espadas, troféus e máscaras ficam de fora: não têm relação com o mito nem com um produto sem competição.

## Espaço, forma e sombra

- A margem lateral é `espaco-4`. Cartões ficam separados por `espaco-3`.
- Cartões usam corte de folha: `raio-md` em dois cantos e 2px nos dois com chave. Botões usam `raio-pilula`. A única sombra é `sombra-cartao`.
- Alvo de toque mínimo: `alvo-minimo` (44px). Botões têm `altura-botao`, ou `altura-botao-ampliado` em leitura ampliada.
- Uma decisão por tela nos fluxos de pergunta: título centrado, opções em cartão, CTA em pílula embaixo.
- A base preta do vaso vira a navegação: `NavBase` sobe no centro para acolher Elpis, com 5 itens sempre rotulados. A borda de cima leva uma faixa fina de meandro laranja, interrompida no arco de Elpis. O item ativo leva uma barra sob o rótulo.
- A navegação é retrátil. O botão de chave grega, num disco de anel duplo, recolhe e expande. Embaixo, recolhida fica só a faixa com Elpis. No trilho lateral, expandida mostra ícone e rótulo, e recolhida mostra só os ícones, com o nome lido pelo leitor de tela.

## Layout responsivo

As telas medem a própria largura (container `pd-tela`), então a mesma tela funciona numa moldura de celular ou na janela inteira. Para ocupar a janela, envolva a página em `.pd-fluido` e use `Tela` ou as telas direto.

- **Até 599px:** uma coluna, navegação fixa embaixo, com a área segura do aparelho.
- **De 600 a 1023px:** conteúdo centrado em coluna de até 720px. A navegação continua embaixo, com os itens em até 640px.
- **A partir de 1024px:** a navegação vira um trilho lateral preto, com o meandro de pé na borda. Os cartões vão para duas colunas, até 1200px. A conversa com Elpis fica em uma coluna de até 760px.
- **Celular deitado** (altura até 520px): o trilho lateral devolve a altura ao conteúdo.
- A abertura usa a cena inteira em primeiro plano, nítida, e a dissolve num esfumado da própria cena escurecido pela `base`. No celular a cena fica em cima e o texto embaixo. A partir de 800px a cena preenche a esquerda e o texto se centra à direita. O texto sobre o esfumado fica acima de 12:1.
- A cena tem só 400×413px e aparece ampliada em telas largas. Troque por uma versão de pelo menos 1600px quando houver.
- Títulos da marca e `valor-xl` crescem com a largura (`clamp`). O corpo fica em 17px em qualquer tela.
- O trilho muda só a posição visual. Na ordem de leitura e de foco, a navegação continua depois do conteúdo.

## Movimento

- Transições de 200 a 240ms, com saída suave. Nada pisca nem chacoalha.
- Elpis ouvindo: o anel de meandro gira devagar em torno dela e `BotaoVoz` pulsa.
- Respeite `prefers-reduced-motion`: os dois efeitos acima param.
- Na trilha, nada de sorteio, roleta, moedas caindo ou celebração que lembre cassino.

## Iconografia

- Ícones de `Icone`: traço de 2px, grade de 24px, pontas arredondadas, cor herdada do texto. Sem emoji.
- Os espíritos da caixa usam `traco` com contorno em `tinta`, como figura reservada em vaso.
- `Elpis` é um medalhão: mulher em figura negra sobre `laranja-vaso`, dentro do anel de meandro. A partir de 72px mostra a figura inteira. Abaixo disso, mostra o busto em anel simples. Não recolora, não recorte e não adicione expressões.
- `Brasao` leva o mesmo medalhão à trilha, com um emblema por etapa: templo, balança, espiral de onda, ramo de oliveira, elmo e ânfora. Etapas à frente aparecem em contorno, nunca com cadeado.
- `CaixaMarca` é a marca do produto. `Anfora` representa reserva guardada e enche conforme o valor.
- A cena da abertura é a ilustração do mito do grupo `Cena`. Não redesenhe a figura de Pandora à mão.

## Gamificação sem punição

Parte do público tem compulsão por apostas ou vive sob estresse financeiro. A trilha mostra progresso sem criar pressão.

- Use: caminho visível com brasões, marcos fixos e previsíveis, conquistas por competência demonstrada, refazer sem custo.
- Não use: recompensa aleatória, sorteio, ranking, contagem que zera, perda por erro, moeda virtual.
- Quando a pessoa erra, explique com os números dela e com a fonte. Escreva "Vale rever este ponto", nunca "Errado".

## Confiança no RAG

- Toda afirmação sobre lei, prazo ou direito leva `CitacaoCartao` com norma, artigo e link.
- Toda conta leva `BlocoCalculado` ou `SeloCalculado`: vem do motor determinístico, não do modelo.
- Sem fonte suficiente, Elpis se abstém com o selo "Sem fonte suficiente".
- Pedido de recomendação de ativo vira "Recusa educativa", com critérios para a pessoa avaliar.
- O modo de crise tem prioridade sobre qualquer tela.

## Telas

`Galeria` monta o mapa completo: 7 telas e 2 estados, em 16 quadros. A navegação inferior tem Início, Dívidas, Elpis, Trilha e Guardião. Metas e previsão abre a partir de Início.
