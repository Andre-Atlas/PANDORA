// Gera bundle.js, index.d.ts, README e preview de cada componente a partir desta tabela.
const fs = require('fs'), path = require('path');
// No repositório não há pasta project/: a saída é a própria pasta do design system.
const noArtifact = fs.existsSync(path.join(__dirname, '..', 'project'));
const raiz = noArtifact ? path.join(__dirname, '..', 'project') : path.join(__dirname, '..');
const ornamentos = require('./ornamentos.js'), emblemas = require('./emblemas.js');
const FONTES = 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;500;700;800&family=Cinzel+Decorative:wght@400;700;900&family=Ysabeau+Office:wght@400;700;900&display=swap';
const coluna = '{className:"pd-demo-coluna"}', linha = '{className:"pd-demo-linha"}';

// nome, grupo, altura, largura, resumo, orientação, props, código da prévia
const C = [
  ['Icone', 'Marca', 90, 0, 'Ícone de traço em grade de 24px, com a cor herdada do texto.', 'Use sempre com rótulo visível ou passe `rotulo`. O consumidor informa `nome`.', 'nome: string; tamanho?: number; traco?: number; rotulo?: string; className?: string', `h("div",${linha},["casa","balanca","trilha","escudo","microfone","camera","alerta","check","livro","documento","telefone","som"].map(function(n){return h(P.Icone,{key:n,nome:n,tamanho:28})}))`],
  ['Friso', 'Marca', 170, 0, 'Faixa fina de ornamento grego para o registro de leitura.', 'Um por bloco, nunca atrás de texto. `curto` centraliza 120px, para separar turnos de conversa. Decorativo, escondido de leitores de tela.', 'tipo?: "meandro" | "onda" | "palmeta" | "serra" | "ramo"; tom?: "forte" | "vaso" | "base"; curto?: boolean; grande?: boolean', `h("div",${coluna},["meandro","onda","palmeta","serra","ramo"].map(function(t){return h(P.Friso,{key:t,tipo:t,tom:"forte"})}))`],
  ['Disco', 'Marca', 90, 0, 'Disco de ícone para estados, com anel duplo como os botões redondos.', 'Use em avisos e listas de checagem. O ícone nunca vem sozinho: sempre há uma palavra ao lado. `Cartao` com `tom` alerta ou ok já inclui um.', 'tom: "alerta" | "ok"; icone: string; tamanho?: "pequeno" | "grande"', `h("div",${linha},h(P.Disco,{tom:"ok",icone:"check",tamanho:"pequeno"}),h(P.Disco,{tom:"ok",icone:"check"}),h(P.Disco,{tom:"alerta",icone:"alerta"}),h(P.Disco,{tom:"alerta",icone:"alerta",tamanho:"grande"}))`],
  ['Meandro', 'Marca', 60, 0, 'Friso grego que abre e fecha todo cabeçalho do mito.', 'Assume as cores do mito no tema: tinta sobre laranja no claro, laranja sobre preto no escuro. `posicao="baixo"` fecha o cabeçalho na transição para a leitura. Decorativo, escondido de leitores de tela.', 'posicao?: "cima" | "baixo"', `h("div",${coluna},h(P.Meandro),h(P.Meandro,{posicao:"baixo"}))`],
  ['Serra', 'Marca', 70, 0, '@deprecated Use `Meandro` com `posicao="baixo"`.', 'Saiu do sistema: a serra foi trocada pelo meandro. Mantido só para quem já consome o bundle, e desenha o meandro de baixo.', '', `h(P.Serra)`],
  ['CaixaMarca', 'Marca', 150, 0, 'Marca do produto: a caixa aberta com os espíritos saindo.', 'Use sobre `laranja-vaso`, com pelo menos 48px. Não recolora.', 'tamanho?: number; rotulo?: string', `h("div",{style:{background:"#f0792b",padding:16,display:"inline-block",borderRadius:16}},h(P.CaixaMarca,{tamanho:112}))`],
  ['Elpis', 'Marca', 260, 0, 'Elpis, a assistente: a esperança que ficou na caixa, em medalhão de figura negra.', 'Aparece onde a IA fala. A partir de 72px mostra a figura inteira e o anel de meandro; abaixo disso, o busto em anel simples. Use `estado="ouvindo"` na voz: o anel gira devagar.', 'tamanho?: number; estado?: "normal" | "ouvindo"; rotulo?: string', `h("div",${linha},h(P.Elpis,{tamanho:220}),h(P.Elpis,{tamanho:120}),h(P.Elpis,{tamanho:72}),h(P.Elpis,{tamanho:60}),h(P.Elpis,{tamanho:44}))`],
  ['Brasao', 'Marca', 130, 0, 'Brasão de etapa da trilha: emblema em figura negra no medalhão de meandro.', 'A partir de 72px mostra o anel de meandro; abaixo disso, anel simples. `proximo` é contorno, nunca bloqueio. O estado sempre vem acompanhado de texto.', 'emblema: "templo" | "balanca" | "espiral" | "oliveira" | "elmo" | "anfora"; estado?: "feito" | "atual" | "proximo"; tamanho?: number; rotulo?: string', `h("div",${linha},["templo","balanca","espiral","oliveira","elmo","anfora"].map(function(e,i){return h(P.Brasao,{key:e,emblema:e,estado:i<2?"feito":i===2?"atual":"proximo"})}))`],
  ['Anfora', 'Marca', 130, 0, 'Ânfora que enche conforme a reserva cresce.', 'Use para valor guardado, nunca para dívida. Sempre com valor em texto ao lado.', 'nivel: number; altura?: number; rotulo?: string', `h("div",${linha},[1,.54,.2,0].map(function(n,i){return h(P.Anfora,{key:i,nivel:n})}))`],

  ['Botao', 'Ações', 240, 0, 'Botão em pílula com altura mínima de 52px.', 'Um `primario` por tela. Use `mito` sobre laranja e `claro` sobre `base`. Primário, mito e claro levam filete e chave grega nas pontas; `secundario` tem borda dupla; `fantasma` não tem ornamento. O texto diz o que acontece, e nunca oferece movimentar dinheiro.', 'variante?: "primario" | "secundario" | "fantasma" | "mito" | "claro"; bloco?: boolean; ampliado?: boolean; icone?: string; seta?: boolean; desativado?: boolean; onClick?: () => void; children: React.ReactNode', `h("div",${coluna},h(P.Botao,{bloco:true,seta:true},"Ver o plano"),h(P.Botao,{variante:"secundario",bloco:true,icone:"documento"},"Gerar dossiê em PDF"),h(P.Botao,{variante:"fantasma"},"Corrigir uma categoria"),h(P.Botao,{bloco:true,desativado:true},"Seguir"))`],
  ['BotaoIcone', 'Ações', 80, 0, 'Botão redondo de 44px só com ícone.', '`rotulo` é obrigatório: é o nome lido pelo leitor de tela.', 'icone: string; rotulo: string; tom?: "mito" | "acao"; onClick?: () => void', `h("div",${linha},h(P.BotaoIcone,{icone:"voltar",rotulo:"Voltar"}),h(P.BotaoIcone,{icone:"microfone",tom:"acao",rotulo:"Falar"}),h(P.BotaoIcone,{icone:"sino",tom:"mito",rotulo:"Avisos"}))`],
  ['BotaoVoz', 'Ações', 130, 0, 'Botão grande de microfone, canal principal de quem digita com dificuldade.', 'Use `ativo` enquanto grava. O pulso para com movimento reduzido.', 'ativo?: boolean; rotulo?: string; onClick?: () => void', `h("div",${linha},h(P.BotaoVoz),h("span",{style:{width:16}}),h(P.BotaoVoz,{ativo:true}))`],
  ['Segmento', 'Ações', 90, 0, 'Alternância entre duas ou três visões da mesma tela.', 'O consumidor controla `valor` e `onChange`.', 'opcoes: string[]; valor: string; rotulo: string; onChange?: (v: string) => void', `h("div",${coluna},h(P.Segmento,{rotulo:"Método",opcoes:["Avalanche","Bola de Neve"],valor:"Avalanche"}))`],
  ['Alternador', 'Ações', 110, 0, 'Liga e desliga uma trava voluntária.', 'Explique na `descricao` a espera para desligar.', 'titulo: string; descricao?: string; ligado?: boolean', `h("div",${coluna},h(P.Alternador,{titulo:"Pausa noturna",descricao:"23h às 03h. Para desligar, há 48h de espera.",ligado:true}),h(P.Alternador,{titulo:"Aviso na quarta",descricao:"Lembrete logo após o repasse."}))`],

  ['Progresso', 'Formulários', 80, 0, 'Barra de progresso de fluxo com voltar e pular.', 'Passe `pular={false}` em passos obrigatórios, como o de consentimento.', 'passo: number; total: number; voltar?: boolean; pular?: boolean', `h("div",${coluna},h(P.Progresso,{passo:1,total:3}))`],
  ['OpcaoCartao', 'Formulários', 190, 0, 'Opção em cartão para perguntas de escolha única.', 'Coloque dentro de um `role="radiogroup"`. Marcada leva borda, fundo e ícone, nunca só cor.', 'titulo: string; descricao?: string; icone?: string; marcada?: boolean; onClick?: () => void', `h("div",${coluna},h(P.OpcaoCartao,{icone:"balanca",titulo:"Dívidas que não fecham",descricao:"Cartão, empréstimo, contas atrasadas",marcada:true}),h(P.OpcaoCartao,{icone:"escudo",titulo:"Medo de golpes",descricao:"Boletos, Pix e ligações suspeitas"}))`],
  ['EscalaSentimento', 'Formulários', 220, 0, 'Escala de 1 a 10 sobre como a pessoa se sente com o dinheiro.', 'Linha de base da jornada, inspirada na escala IFDFW. Nenhum nível é errado, por isso a barra usa uma só cor.', 'valor?: number', `h("div",${coluna},h(P.EscalaSentimento,{valor:3}))`],
  ['Consentimento', 'Formulários', 90, 0, 'Caixa de aceite com texto claro, para LGPD.', 'Nunca venha marcada em produção sem ação da pessoa.', 'marcado?: boolean; children: React.ReactNode', `h("div",${coluna},h(P.Consentimento,null,"Concordo com o uso dos meus dados para este diagnóstico."))`],

  ['Cartao', 'Dados', 210, 0, 'Contêiner do registro de leitura.', 'Use `tom` para apoio, alerta ou ok: cada tom tem friso próprio. `marco` põe o título em Cinzel Decorative. Evite cartão dentro de cartão.', 'titulo?: string; sobre?: string; tom?: "apoio" | "alerta" | "ok"; marco?: boolean; className?: string; children?: React.ReactNode', `h("div",${coluna},h(P.Cartao,{sobre:"Seu próximo passo",titulo:"Regularizar a conta de luz"},h("p",null,"R$ 360 em 2 faturas.")),h(P.Cartao,{tom:"alerta",titulo:"Não pague este boleto"}))`],
  ['Selo', 'Dados', 80, 0, 'Etiqueta curta de estado, sempre com ícone e palavra.', 'Use `ok`, `alerta` e `fonte` só para estado.', 'tom?: "neutro" | "ok" | "alerta" | "fonte" | "mito"; icone?: string | null; children: React.ReactNode', `h("div",${linha},h(P.Selo,{tom:"ok"},"Protegido"),h(P.Selo,{tom:"alerta"},"Risco de corte"),h(P.Selo,{tom:"fonte"},"Res. BCB 147/2021"),h(P.Selo,null,"Neutro"))`],
  ['SeloCalculado', 'Dados', 70, 0, 'Marca um número que veio do motor determinístico.', 'Use ao lado de todo valor calculado, para separá-lo de texto gerado por IA.', '', `h(P.SeloCalculado)`],
  ['Trilho', 'Dados', 70, 0, 'Barra de proporção com até duas partes.', 'Uma parte é medidor; duas são divisão. Sempre com valores em texto e `rotulo`.', 'partes: {valor: number; tom: "acao" | "ok" | "vaso"}[]; total?: number; rotulo: string', `h("div",${coluna},h(P.Trilho,{partes:[{valor:2100,tom:"ok"},{valor:750,tom:"vaso"}],rotulo:"R$ 2.100 protegidos e R$ 750 de folga"}))`],
  ['Insight', 'Dados', 150, 0, 'A única coisa que Elpis notou e vale dizer agora.', 'No máximo um por tela. Traga número, tradução em vida real e, se houver, uma ação.', 'sobre?: string; acao?: string; children: React.ReactNode', `h("div",${coluna},h(P.Insight,{acao:"Entender esse valor"},"R$ 342,18 da sua fatura foram só juros e IOF."))`],
  ['LinkCartao', 'Dados', 100, 0, 'Atalho em cartão para outra área do app.', 'Use para áreas fora da navegação, como Metas e previsão.', 'icone: string; titulo: string; descricao?: string; onClick?: () => void', `h("div",${coluna},h(P.LinkCartao,{icone:"alvo",titulo:"Metas e previsão",descricao:"Próximos 30, 60 e 90 dias"}))`],
  ['LinhaDivida', 'Dados', 180, 0, 'Uma dívida na ordem do plano.', 'Use `protegida` para o mínimo existencial. Em `children`, entra o custo em reais e o CET.', 'nome: string; valor: string; ordem?: number; protegida?: boolean; children?: React.ReactNode', `h("div",${coluna},h(P.LinhaDivida,{ordem:2,nome:"Cartão · Banco A",valor:"R$ 4.200"},h("p",null,"R$ 342,18 por mês só de juros e IOF.")),h(P.LinhaDivida,{protegida:true,nome:"Mínimo existencial",valor:"R$ 2.100"}))`],
  ['DegrausProgresso', 'Dados', 110, 0, 'Degraus de templo com as etapas do plano.', 'Use sobre `laranja-vaso`, com o nome da etapa em texto por perto.', 'passos: number; atual: number', `h("div",{style:{background:"#f0792b",padding:16,maxWidth:170}},h(P.DegrausProgresso,{passos:5,atual:3}))`],

  ['Balao', 'Conversa', 130, 0, 'Balão de conversa de Elpis ou da pessoa.', 'Conteúdo de Elpis pode levar citação e cálculo.', 'autor?: "elpis" | "voce"; children: React.ReactNode', `h("div",{className:"pd-conversa",style:{maxWidth:358}},h(P.Balao,{autor:"voce"},"Podem bloquear meu salário?"),h(P.Balao,null,"O salário é impenhorável para dívidas de cartão."))`],
  ['CitacaoCartao', 'Conversa', 170, 0, 'Fonte oficial de uma resposta: norma, artigo e link.', 'Obrigatório em toda resposta sobre lei, prazo ou direito.', 'norma: string; href: string; rotuloLink: string; children?: React.ReactNode', `h("div",${coluna},h(P.CitacaoCartao,{norma:"Código de Processo Civil, art. 833, IV",href:"https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm",rotuloLink:"Ler no Planalto"},"Consultei 3 trechos em fontes oficiais."))`],
  ['BlocoCalculado', 'Conversa', 150, 0, 'Resultado do motor determinístico dentro da conversa.', 'Os valores vêm de ferramentas tipadas, nunca do modelo de linguagem.', 'linhas: [string, string][]', `h("div",${coluna},h(P.BlocoCalculado,{linhas:[["1º Mínimo existencial","R$ 2.100"],["2º Conta de luz","R$ 360"]]}))`],
  ['CampoPergunta', 'Conversa', 90, 0, 'Campo de conversa com anexo e microfone.', 'Em Início, use `anexo={false}` e deixe o foco abrir Elpis.', 'placeholder?: string; anexo?: boolean', `h("div",${coluna},h(P.CampoPergunta,{placeholder:"Pergunte à Elpis"}))`],
  ['CabecalhoElpis', 'Conversa', 90, 0, 'Cabeçalho da conversa com a nota de privacidade.', 'A nota fica sempre visível, para lembrar que os dados estão mascarados.', 'nota?: string', `h(P.CabecalhoElpis)`],

  ['TrilhaCaminho', 'Trilha', 780, 420, 'Caminho com as seis etapas de educação financeira.', 'Mostra etapas concluída, atual e a seguir, cada uma com seu brasão. Todas abrem, sem bloqueio nem contagem que zera. Marcos são fixos e conhecidos.', 'etapas?: {n: number; t: string; x: number; lado: "d" | "e"; estado: "feito" | "atual" | "proximo"; marco: string | null; emblema: string}[]', `h(P.TrilhaCaminho)`],
  ['QuizOpcao', 'Trilha', 170, 0, 'Resposta de quiz com retorno que explica.', 'Use `revisar` para o erro: o tom é neutro, sem vermelho e sem punição.', 'letra: string; estado?: "neutra" | "certa" | "revisar"; onClick?: () => void; children: React.ReactNode', `h("div",${coluna},h(P.QuizOpcao,{letra:"A",estado:"revisar"},"Fica parado até a próxima fatura"),h(P.QuizOpcao,{letra:"B",estado:"certa"},"Entra no rotativo e continua gerando juros"))`],

  ['Rolagem', 'Moldura', 540, 460, 'Área rolável com a barra em forma de coluna.', 'No desktop a barra nativa vira coluna. No toque, onde o sistema ignora esse estilo, entra um trilho próprio e decorativo. Passe `rotulo`.', 'rotulo?: string; children?: React.ReactNode', `h(P.Aparelho,{altura:480},h(P.Rolagem,{rotulo:"Lista de exemplo"},h("div",{className:"pd-corpo"},[1,2,3,4,5,6].map(function(n){return h(P.Cartao,{key:n,sobre:"Item "+n,titulo:"Cartão de exemplo"},h("p",null,"Conteúdo para rolar."))}))))`],
  ['Aparelho', 'Moldura', 250, 460, 'Moldura de celular com 390px de tela para mostrar telas.', 'Serve só para apresentação. `topo` define a cor da barra de status. Passe `altura` para uma tela fixa com rolagem.', 'topo?: "leitura" | "mito" | "base"; altura?: number; children?: React.ReactNode', `h("div",{style:{height:240,overflow:"hidden"}},h(P.Aparelho,{topo:"mito"},h(P.CabecalhoMito,{titulo:"Suas dívidas"})))`],
  ['CabecalhoMito', 'Moldura', 240, 460, 'Cabeçalho do registro do mito, com meandro e serra.', 'Comporta um título, um número-herói e uma frase. Nada de listas aqui.', 'titulo?: string; subtitulo?: string; voltar?: boolean; acao?: React.ReactNode; children?: React.ReactNode', `h("div",{style:{maxWidth:390}},h(P.CabecalhoMito,{titulo:"Da caixa à esperança",subtitulo:"2 de 6 etapas concluídas"}))`],
  ['NavBase', 'Moldura', 140, 460, 'Navegação na base preta do vaso, com Elpis ao centro. Retrátil.', 'Cinco itens, sempre com rótulo. Passe `ativo` e `onNavegar`. O botão de chave grega recolhe e expande: embaixo, recolhida mostra só a faixa e Elpis; no trilho lateral, recolhida mostra só os ícones, com o nome no leitor de tela. Para guardar a escolha, controle com `recolhida` e `onAlternar`.', 'ativo?: "inicio" | "dividas" | "elpis" | "trilha" | "guardiao"; onNavegar?: (id: string) => void; recolhida?: boolean; onAlternar?: (recolhida: boolean) => void', `h("div",{style:{maxWidth:390,paddingTop:16}},h(P.NavBase,{ativo:"trilha"}))`],

  ['Galeria', 'Telas', 3600, 2240, 'Mapa completo do app: 7 telas e 2 estados.', 'Passe `ids` para mostrar só alguns quadros.', 'ids?: string[]', `h(P.Galeria)`, 'page'],
  ['Tela', 'Telas', 900, 460, 'Uma tela do mapa pelo id, para ocupar a janela inteira.', 'Envolva em `.pd-fluido` para a tela ocupar a janela, sem moldura de celular: a navegação fica embaixo no celular e vira trilho lateral a partir de 1024px ou com o aparelho deitado.', 'id: string', `h(P.Tela,{id:"2"})`],
  ['TelaAbertura', 'Telas', 1800, 900, 'Tela 1: abertura, sentimento, o que pesa e como começar.', 'Cobre RF01, RNF01 e a linha de base da GQ10. Dados da persona Carla. Passe `passo` de 0 a 3 e, se quiser, `cena`.', 'passo?: 0 | 1 | 2 | 3; cena?: string', `h(P.Galeria,{ids:["1a","1b","1c","1d"]})`],
  ['TelaInicio', 'Telas', 1500, 460, 'Tela 2: início com o Raio-X do mês.', 'Cobre RF02, RF03 e RF10. Dados de Carla. O score 31 é ilustrativo: a fórmula do RF10 ainda não foi definida.', '', `h(P.TelaInicio)`],
  ['TelaDividas', 'Telas', 1500, 460, 'Tela 3: dívidas na ordem do plano e dossiê.', 'Cobre RF03, RF06 e RF12. Dados de Carla. Em Avalanche e Bola de Neve a ordem coincide, e a tela diz isso.', '', `h(P.TelaDividas)`],
  ['TelaElpis', 'Telas', 1100, 1360, 'Tela 4: assistente RAG com fonte, limites e voz.', 'Cobre RF08, RF09, RNF02 e RNF04. Passe `modo`: citacao, limites ou voz.', 'modo?: "citacao" | "limites" | "voz"', `h(P.Galeria,{ids:["4a","4b","4c"]})`],
  ['TelaTrilha', 'Telas', 1100, 900, 'Tela 5: trilha gamificada de educação financeira e lição.', 'Cobre RF08 e RF14. Progresso sem punição. Passe `modo="licao"` para o quiz.', 'modo?: "licao"; resposta?: "a" | "b" | "c" | null', `h(P.Galeria,{ids:["5a","5b"]})`],
  ['TelaGuardiao', 'Telas', 1300, 900, 'Tela 6: proteção contra golpes e apostas.', 'Cobre RF04, RF07 e RF11. Golpes usa dados do Sr. Antônio, Apostas usa dados do Diego.', 'modo?: "golpes" | "apostas"', `h(P.Galeria,{ids:["6a","6b"]})`],
  ['TelaMetas', 'Telas', 1500, 460, 'Tela 7: reserva, previsão e simulador.', 'Cobre RF13 e RF14. Dados de Júlia. A sobra de 90 dias é estimada e o simulador só compara classes gerais.', '', `h(P.TelaMetas)`],
  ['TelaCrise', 'Telas', 900, 460, 'Estado: fluxo de crise.', 'Cobre RF05. Sobrepõe qualquer tela e pausa metas e avisos. Usa Atkinson, sem ornamento além do medalhão de Elpis.', '', `h(P.TelaCrise)`],
  ['TelaGuardiaoAmpliada', 'Telas', 900, 460, 'Estado: leitura ampliada com voz.', 'Cobre RNF07 para o Sr. Antônio: Atkinson, corpo de 24px, botões de 72px e áudio.', '', `h(P.TelaGuardiaoAmpliada)`]
];

let corpo = fs.readFileSync(path.join(__dirname, 'bundle.body.js'), 'utf8').replace('__FIGURA_ELPIS__', fs.readFileSync(path.join(__dirname, 'elpis.d'), 'utf8').trim()).replace('__EMBLEMAS__', JSON.stringify(emblemas));
if (!noArtifact) corpo = corpo.replace("'/_blob/315e6beaff9ab6221886784cbff1e112'", "'./assets/Cena/pandora-cena.png'");
fs.writeFileSync(path.join(raiz, 'components/bundle.css'), fs.readFileSync(path.join(__dirname, 'bundle.src.css'), 'utf8').replace('/*__ORNAMENTOS__*/', ornamentos.css));
const cab = '/* @ds-bundle: ' + JSON.stringify({ format: 4, namespace: 'Pandora', components: C.map(c => ({ name: c[0] })) }) + ' */\n';
if (/<\/script|<!--/i.test(corpo)) throw new Error('termo proibido no bundle');
fs.writeFileSync(path.join(raiz, 'components/bundle.js'), cab + corpo);

// Ornamentos e brasões também como arquivos soltos
const pastaAssets = noArtifact ? path.join(__dirname, '..', 'assets-up') : path.join(raiz, 'assets');
const pastaBrasoes = noArtifact ? pastaAssets : path.join(pastaAssets, 'Marca', 'brasoes');
const pastaOrnamentos = noArtifact ? pastaAssets : path.join(pastaAssets, 'Ornamentos');
fs.mkdirSync(pastaBrasoes, { recursive: true }); fs.mkdirSync(pastaOrnamentos, { recursive: true });
for (const [nome, s] of Object.entries(ornamentos.motivos)) if (!nome.endsWith('-rolagem')) fs.writeFileSync(path.join(pastaOrnamentos, nome + '.svg'), s.replace(/'/g, '"').replace(/<path d="([^"]+)"\/>/g, '<path d="$1" fill="#1a1410"/>').replace(/#000/g, '#1a1410'));
for (const [nome, partes] of Object.entries(emblemas)) {
  const chaves = Array.from({ length: 16 }, (_, i) => `<path d="M105 24V9H135V20H114V14H126" transform="rotate(${i * 22.5} 120 120)"/>`).join('');
  const figura = partes.map(e => e.tipo === 'cheio' ? `<path d="${e.d}" fill="#1a1410"${e.regra ? ` fill-rule="${e.regra}"` : ''}/>` : e.tipo === 'traco' ? `<path d="${e.d}" fill="none" stroke="#1a1410" stroke-width="${e.largura}" stroke-linecap="round" stroke-linejoin="round"/>` : `<path d="${e.d}" fill="none" stroke="#f0792b" stroke-width="3.2" stroke-linecap="round"/>`).join('');
  fs.writeFileSync(path.join(pastaBrasoes, 'brasao-' + nome + '.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240"><circle cx="120" cy="120" r="118" fill="#1a1410"/><g fill="none" stroke="#f0792b" stroke-width="4"><circle cx="120" cy="120" r="115.5"/><circle cx="120" cy="120" r="92"/>${chaves}</g><circle cx="120" cy="120" r="88" fill="#f0792b"/>${figura}</svg>\n`);
}

let dts = 'import * as React from "react";\n\n';
for (const [nome, grupo, altura, largura, resumo, guia, props, codigo, marca] of C) {
  const dir = path.join(raiz, 'components', nome);
  if (noArtifact) fs.mkdirSync(dir, { recursive: true });
  const lista = props ? props.split(/;\s(?![^{]*})/).map(p => '- `' + p.trim() + '`').join('\n') : 'Sem propriedades.';
  if (noArtifact) fs.writeFileSync(path.join(dir, 'README.md'), `${resumo}\n\n${guia}\n\n## O que o consumidor fornece\n\n${lista}\n`);
  const attrs = `group="${grupo}" height=${altura}` + (largura ? ` width=${largura}` : '') + (marca ? ' page' : '');
  if (noArtifact) fs.writeFileSync(path.join(dir, 'preview.html'), `<!-- @dsCard ${attrs} -->\n<!doctype html>\n<html>\n<head><meta charset="utf-8"><title>${nome}</title><link rel="stylesheet" href="${FONTES.replace(/&/g, '&amp;')}"></head>\n<body style="margin:0">\n<div id="root" class="pd-demo"></div>\n<script>\n  var P = window.Pandora, h = React.createElement;\n  ReactDOM.createRoot(document.getElementById('root')).render(${codigo});\n</script>\n</body>\n</html>\n`);
  dts += `/** ${resumo} */\nexport interface ${nome}Props { ${props} }\nexport function ${nome}(props: ${nome}Props): React.ReactElement;\n\n`;
}
fs.writeFileSync(path.join(raiz, 'components/index.d.ts'), dts);

if (!noArtifact) {
  // Tokens em CSS para quem usa o sistema fora do artifact
  const t = JSON.parse(fs.readFileSync(path.join(raiz, 'tokens.json')));
  const val = (k, tema) => typeof k.value === 'string' ? k.value : (k.value[tema] ?? k.value.light);
  const hex = (nome, tema) => { const v = val(t.color.tokens.find(x => x.name === nome), tema), m = /^\{(.+)\}$/.exec(v); return m ? hex(m[1], tema) : v; };
  const bloco = tema => t.color.tokens.map(k => `  --${k.name}: ${hex(k.name, tema)};`).concat(t.shadow.tokens.map(k => `  --${k.name}: ${val(k, tema)};`)).join('\n');
  const fixos = ['spacing', 'radius', 'controle'].flatMap(f => t[f].tokens).map(k => `  --${k.name}: ${k.value};`).join('\n');
  const familias = Object.entries(t.type.families).map(([k, v]) => `  --font-${k}: ${v};`).join('\n');
  fs.writeFileSync(path.join(raiz, 'tokens.css'), `/* Gerado a partir de tokens.json. Não edite à mão. */\n:root,\n[data-theme="light"] {\n${bloco('light')}\n}\n\n[data-theme="dark"] {\n${bloco('dark')}\n}\n\n:root {\n${fixos}\n${familias}\n}\n`);
  console.log(C.length, 'componentes');
  process.exit(0);
}

// Capa
const meandro = [];
for (let lin = 0; lin < 3; lin++) for (let col = 0; col < 5; col++) {
  const x = 512 + col * 64, y = 32 + lin * 64;
  meandro.push(`<path class="mea" d="M${x} ${y + 52}V${y}H${x + 52}V${y + 36}H${x + 16}V${y + 18}H${x + 34}"/>`);
}
fs.mkdirSync(path.join(raiz, 'components/Cover'), { recursive: true });
fs.writeFileSync(path.join(raiz, 'components/Cover/preview.html'), `<!-- @dsCard height=288 -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Capa</title><link rel="stylesheet" href="${FONTES.replace(/&/g, '&amp;')}">
<style>
html,body{margin:0;background:var(--superficie)}
.capa{position:relative;width:960px;height:288px;overflow:hidden;background:var(--superficie)}
.nome{position:absolute;left:32px;bottom:64px;font-family:var(--font-marca);font-size:76px;line-height:80px;font-weight:700;color:var(--texto)}
.frase{position:absolute;left:32px;bottom:32px;width:440px;font-family:var(--font-texto);font-size:14px;line-height:20px;color:var(--texto-2)}
.vaso{fill:var(--laranja-vaso)}.tinta{fill:var(--tinta)}.terra{fill:#a8430f}.papiro{fill:var(--superficie-2)}.egeu{fill:#1f5c7a}
.mea{fill:none;stroke:var(--tinta);stroke-width:8}
</style></head>
<body>
<div class="capa">
<!-- blocos: laranja-vaso 352×224, tinta 96×288, terracota 128×64, superficie-2 224×64, egeu 16×64 -->
<!-- arranjo: placa larga de vaso com faixa inferior e coluna de tinta sangrando à direita -->
<!-- padrão: linha do motivo literal, o meandro do vaso; escolhido porque o friso é a assinatura do sistema -->
<!-- escalas: passo de 64px (espaco-4 × 4), traço de 8px (espaco-2), cantos retos como o friso -->
<svg width="960" height="288" viewBox="0 0 960 288" style="position:absolute;inset:0" aria-hidden="true">
<rect class="vaso" x="480" y="0" width="352" height="224"/>
<rect class="tinta" x="864" y="0" width="96" height="288"/>
<rect class="terra" x="480" y="224" width="128" height="64"/>
<rect class="papiro" x="608" y="224" width="224" height="64"/>
<rect class="egeu" x="832" y="224" width="16" height="64"/>
${meandro.slice(0, 15).filter((_, i) => (i % 5) < 5).join('\n').replace(/x="\d+"/g, '')}
</svg>
<div class="nome">PANDORA</div>
<div class="frase">Finanças com fonte, sem culpa. O que fica na caixa é a esperança.</div>
</div>
</body>
</html>
`);

const grupos = {
  Marca: { name: 'Marca', tile: 'm', order: ['caixa-esperanca.svg', 'elpis-medalhao.svg'], files: { 'caixa-esperanca.svg': { name: 'caixa-esperanca.svg', blob: '86f10cd9ea86d85a9b6060cfcc2c96e6', size: 875, type: 'image/svg+xml' }, 'elpis-medalhao.svg': { name: 'elpis-medalhao.svg', blob: '4c233c2b4601fff8c187c72af61ebf88', size: 53770, type: 'image/svg+xml' } } },
  Ornamentos: { name: 'Ornamentos', tile: 's', order: ['meandro.svg', 'serra.svg'], files: { 'meandro.svg': { name: 'meandro.svg', blob: 'c8337248cf4dc253593dd047ac939368', size: 234, type: 'image/svg+xml' }, 'serra.svg': { name: 'serra.svg', blob: '91d5d66b5d7558aefee615a1ae6cfad6', size: 118, type: 'image/svg+xml' } } },
  Cena: { name: 'Cena', tile: 'l', order: ['pandora-cena.png'], files: { 'pandora-cena.png': { name: 'pandora-cena.png', blob: '315e6beaff9ab6221886784cbff1e112', size: 181965, type: 'image/png' } } }
};
const leia = {
  Marca: '`caixa-esperanca.svg` usa tinta `#1a1410`, traço `#fff8ec` e laranja-vaso. `elpis-medalhao.svg` usa tinta e laranja-vaso e tem fundo próprio. Use a caixa sobre `laranja-vaso` e o medalhão sobre qualquer superfície.\n',
  Ornamentos: 'Módulos do vaso em tinta `#1a1410`, desenhados em vetor próprio. `meandro` e `serra` repetem sobre `laranja-vaso`. Os demais servem de máscara nas caixas, nos avisos e nos botões.\n',
  'Brasões': 'Um brasão por etapa da trilha, com o anel de meandro de Elpis. Use a partir de 72px.\n',
  Cena: 'Ilustração do mito usada na abertura. Tem 400×413px: não amplie além de 400px de largura.\n'
};
for (const g of Object.keys(leia)) { fs.mkdirSync(path.join(raiz, 'assets', g), { recursive: true }); fs.writeFileSync(path.join(raiz, 'assets', g, 'README.md'), leia[g]); }
// Lista para o envio
const arquivos = [];
(function anda(d) { for (const f of fs.readdirSync(d)) { const c = path.join(d, f); if (fs.statSync(c).isDirectory()) anda(c); else arquivos.push(path.relative(path.join(raiz, '..'), c)); } })(raiz);
fs.writeFileSync(path.join(__dirname, 'arquivos.json'), JSON.stringify(Object.fromEntries(arquivos.filter(a => a !== 'project/design-system.json').map(a => [a, a])), null, 0));
console.log(C.length, 'componentes,', arquivos.length, 'arquivos');
