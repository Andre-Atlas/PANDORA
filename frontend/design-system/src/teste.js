// Monta uma página local de teste e checa contraste dos pares de tokens.
const fs = require('fs'), path = require('path');
const projeto = path.join(__dirname, '..', 'project'), noArtifact = fs.existsSync(projeto), raiz = noArtifact ? projeto : path.join(__dirname, '..'), t = JSON.parse(fs.readFileSync(path.join(raiz, 'tokens.json')));
const valorDe = (tok, tema) => { const v = typeof tok.value === 'string' ? tok.value : (tok.value[tema] ?? tok.value.light); return v; };
const hex = (nome, tema) => { let v = valorDe(t.color.tokens.find(x => x.name === nome), tema); const m = /^\{(.+)\}$/.exec(v); return m ? hex(m[1], tema) : v; };
const bloco = tema => t.color.tokens.map(k => `--${k.name}:${hex(k.name, tema)};`).join('') + t.shadow.tokens.map(k => `--${k.name}:${valorDe(k, tema)};`).join('');
const css = `:root,[data-theme="light"]{${bloco('light')}}[data-theme="dark"]{${bloco('dark')}}:root{` + ['spacing', 'radius', 'controle'].flatMap(f => t[f].tokens).map(k => `--${k.name}:${k.value};`).join('') + `--font-marca:${t.type.families.marca};--font-texto:${t.type.families.texto};--font-acessivel:${t.type.families.acessivel};}`;
const arg = process.argv.indexOf('--saida'), saida = arg > 0 ? path.resolve(process.argv[arg + 1]) : path.join(__dirname, '..', 'teste'); fs.mkdirSync(saida, { recursive: true });
fs.writeFileSync(path.join(saida, 'tokens.css'), css);
fs.copyFileSync(path.join(raiz, 'components/bundle.css'), path.join(saida, 'bundle.css'));
fs.copyFileSync(path.join(__dirname, '..', noArtifact ? 'assets-up/pandora-cena.png' : 'assets/Cena/pandora-cena.png'), path.join(saida, 'pandora-cena.png'));
fs.writeFileSync(path.join(saida, 'bundle.js'), fs.readFileSync(path.join(raiz, 'components/bundle.js'), 'utf8').replace(/'[^']*(_blob\/315e6beaff9ab6221886784cbff1e112|assets\/Cena\/pandora-cena\.png)'/, "'pandora-cena.png'"));
for (const tema of ['light', 'dark']) fs.writeFileSync(path.join(saida, tema + '.html'), `<!doctype html><html data-theme="${tema}"><head><meta charset="utf-8"><link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="bundle.css"></head><body style="margin:0"><div id="root" class="pd-demo"></div>
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script><script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script><script src="bundle.js"></script>
<script>ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(Pandora.Galeria));</script></body></html>`);

// Uma tela na janela inteira: tela.html?id=2&tema=dark
const REACT = '<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script><script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script><script src="bundle.js"></script>';
fs.writeFileSync(path.join(saida, 'tela.html'), `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>PANDORA · tela</title><link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="bundle.css"></head><body class="pd-fluido"><div id="root"></div>
${REACT}<script>var q=new URLSearchParams(location.search);document.documentElement.dataset.theme=q.get('tema')||'light';ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(Pandora.Tela,{id:q.get('id')||'2'}));if(q.get('semtexto')){var e=document.createElement('style');e.textContent='.pd-abertura-texto,.pd-abertura-texto *{color:transparent!important;text-shadow:none!important}';document.head.appendChild(e)}if(q.get('nav')==='recolhida')setTimeout(function(){var b=document.querySelector('.pd-nav-alternar');if(b)b.click()},300);</script></body></html>`);
// Matriz de viewports: responsivo.html?tema=dark&id=2
const VIEWPORTS = [[360, 740, 'Celular pequeno'], [390, 844, 'Celular'], [844, 390, 'Celular deitado'], [768, 1024, 'Tablet em pé'], [1024, 768, 'Tablet deitado'], [1440, 900, 'Desktop']];
fs.writeFileSync(path.join(saida, 'responsivo.html'), `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>PANDORA responsivo</title><style>body{margin:0;padding:24px;font-family:system-ui;background:#2a211a;color:#fbf5ea}figure{margin:0 0 32px}iframe{border:1px solid #857261;background:#fff;transform-origin:0 0}.caixa{overflow:hidden}</style></head><body><div id="m"></div>
<script>var q=new URLSearchParams(location.search),tema=q.get('tema')||'light',id=q.get('id')||'2',esc=+(q.get('escala')||0.5);var V=${JSON.stringify(VIEWPORTS)};document.getElementById('m').innerHTML=V.map(function(v){return '<figure><figcaption>'+v[2]+' · '+v[0]+'×'+v[1]+'</figcaption><div class="caixa" style="width:'+v[0]*esc+'px;height:'+v[1]*esc+'px"><iframe title="'+v[2]+'" src="tela.html?id='+id+'&tema='+tema+'" width="'+v[0]+'" height="'+v[1]+'" style="transform:scale('+esc+')"></iframe></div></figure>'}).join('');</script></body></html>`);

// Contraste
const L = h => { const c = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(x => x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; };
const R = (a, b) => { const [x, y] = [L(a), L(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
const texto = [['texto', 'superficie'], ['texto', 'superficie-2'], ['texto', 'cartao'], ['texto', 'selecao'], ['texto', 'ok-suave'], ['texto', 'alerta-suave'], ['texto', 'fonte-suave'], ['texto-2', 'superficie'], ['texto-2', 'superficie-2'], ['texto-2', 'cartao'], ['texto-2', 'fonte-suave'], ['texto-2', 'ok-suave'], ['acao', 'superficie'], ['acao', 'cartao'], ['acao', 'superficie-2'], ['on-acao', 'acao'], ['ok', 'ok-suave'], ['ok', 'superficie'], ['ok', 'cartao'], ['cartao', 'ok'], ['alerta', 'alerta-suave'], ['alerta', 'cartao'], ['fonte', 'fonte-suave'], ['fonte', 'cartao'], ['tinta', 'laranja-vaso'], ['papiro', 'base'], ['laranja-claro', 'base'], ['tinta', 'traco'], ['mito-figura', 'mito-fundo'], ['mito-destaque', 'mito-fundo'], ['mito-sobre-figura', 'mito-figura'], ['papiro', 'base']];
const grafico = [['linha-forte', 'superficie'], ['linha-forte', 'cartao'], ['linha-forte', 'superficie-2'], ['foco', 'superficie'], ['foco', 'cartao'], ['tinta', 'laranja-vaso'], ['acao', 'superficie-2'], ['ok', 'superficie-2'], ['ornamento-forte', 'superficie'], ['ornamento-forte', 'cartao'], ['mito-figura', 'mito-fundo'], ['laranja-vaso', 'base'], ['laranja-claro', 'base']];
let falhas = 0;
for (const tema of ['light', 'dark']) {
  for (const [a, b] of texto) { const r = R(hex(a, tema), hex(b, tema)); if (r < 4.5) { falhas++; console.log('TEXTO', tema, a, 'sobre', b, r.toFixed(2)); } }
  for (const [a, b] of grafico) { const r = R(hex(a, tema), hex(b, tema)); if (r < 3) { falhas++; console.log('GRAF', tema, a, 'sobre', b, r.toFixed(2)); } }
}
console.log('pares', 2 * (texto.length + grafico.length), 'falhas', falhas);
fs.writeFileSync(path.join(saida, 'elpis.html'), `<!doctype html><html data-theme="light"><head><meta charset="utf-8"><link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="bundle.css"></head><body style="margin:0"><div id="root" class="pd-demo"></div>
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script><script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script><script src="bundle.js"></script>
<script>var P=Pandora,h=React.createElement;ReactDOM.createRoot(document.getElementById('root')).render(h('div',{style:{display:'flex',gap:16,alignItems:'center',flexWrap:'wrap'}},[640,248,60,44].map(function(t){return h(P.Elpis,{key:t,tamanho:t})})));</script></body></html>`);
