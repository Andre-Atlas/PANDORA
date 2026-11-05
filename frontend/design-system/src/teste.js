// Monta uma página local de teste e checa contraste dos pares de tokens.
const fs = require('fs'), path = require('path');
const projeto = path.join(__dirname, '..', 'project'), noArtifact = fs.existsSync(projeto), raiz = noArtifact ? projeto : path.join(__dirname, '..'), t = JSON.parse(fs.readFileSync(path.join(raiz, 'tokens.json')));
const valorDe = (tok, tema) => { const v = typeof tok.value === 'string' ? tok.value : (tok.value[tema] ?? tok.value.light); return v; };
const hex = (nome, tema) => { let v = valorDe(t.color.tokens.find(x => x.name === nome), tema); const m = /^\{(.+)\}$/.exec(v); return m ? hex(m[1], tema) : v; };
const bloco = tema => t.color.tokens.map(k => `--${k.name}:${hex(k.name, tema)};`).join('') + t.shadow.tokens.map(k => `--${k.name}:${valorDe(k, tema)};`).join('');
const css = `:root,[data-theme="light"]{${bloco('light')}}[data-theme="dark"]{${bloco('dark')}}:root{` + ['spacing', 'radius', 'controle'].flatMap(f => t[f].tokens).map(k => `--${k.name}:${k.value};`).join('') + `--font-marca:${t.type.families.marca};--font-texto:${t.type.families.texto};--font-acessivel:${t.type.families.acessivel};}`;
const saida = path.join(__dirname, '..', 'teste'); fs.mkdirSync(saida, { recursive: true });
fs.writeFileSync(path.join(saida, 'tokens.css'), css);
fs.copyFileSync(path.join(raiz, 'components/bundle.css'), path.join(saida, 'bundle.css'));
fs.copyFileSync(path.join(__dirname, '..', noArtifact ? 'assets-up/pandora-cena.png' : 'assets/Cena/pandora-cena.png'), path.join(saida, 'pandora-cena.png'));
fs.writeFileSync(path.join(saida, 'bundle.js'), fs.readFileSync(path.join(raiz, 'components/bundle.js'), 'utf8').replace(/'[^']*(_blob\/315e6beaff9ab6221886784cbff1e112|assets\/Cena\/pandora-cena\.png)'/, "'pandora-cena.png'"));
for (const tema of ['light', 'dark']) fs.writeFileSync(path.join(saida, tema + '.html'), `<!doctype html><html data-theme="${tema}"><head><meta charset="utf-8"><link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="bundle.css"></head><body style="margin:0"><div id="root" class="pd-demo"></div>
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script><script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script><script src="bundle.js"></script>
<script>ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(Pandora.Galeria));</script></body></html>`);

// Contraste
const L = h => { const c = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(x => x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; };
const R = (a, b) => { const [x, y] = [L(a), L(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
const texto = [['texto', 'superficie'], ['texto', 'superficie-2'], ['texto', 'cartao'], ['texto', 'selecao'], ['texto', 'ok-suave'], ['texto', 'alerta-suave'], ['texto', 'fonte-suave'], ['texto-2', 'superficie'], ['texto-2', 'superficie-2'], ['texto-2', 'cartao'], ['texto-2', 'fonte-suave'], ['texto-2', 'ok-suave'], ['acao', 'superficie'], ['acao', 'cartao'], ['acao', 'superficie-2'], ['on-acao', 'acao'], ['ok', 'ok-suave'], ['ok', 'superficie'], ['ok', 'cartao'], ['cartao', 'ok'], ['alerta', 'alerta-suave'], ['alerta', 'cartao'], ['fonte', 'fonte-suave'], ['fonte', 'cartao'], ['tinta', 'laranja-vaso'], ['papiro', 'base'], ['laranja-claro', 'base'], ['tinta', 'traco']];
const grafico = [['linha-forte', 'superficie'], ['linha-forte', 'cartao'], ['linha-forte', 'superficie-2'], ['foco', 'superficie'], ['foco', 'cartao'], ['tinta', 'laranja-vaso'], ['acao', 'superficie-2'], ['ok', 'superficie-2'], ['ornamento-forte', 'superficie'], ['ornamento-forte', 'cartao']];
let falhas = 0;
for (const tema of ['light', 'dark']) {
  for (const [a, b] of texto) { const r = R(hex(a, tema), hex(b, tema)); if (r < 4.5) { falhas++; console.log('TEXTO', tema, a, 'sobre', b, r.toFixed(2)); } }
  for (const [a, b] of grafico) { const r = R(hex(a, tema), hex(b, tema)); if (r < 3) { falhas++; console.log('GRAF', tema, a, 'sobre', b, r.toFixed(2)); } }
}
console.log('pares', 2 * (texto.length + grafico.length), 'falhas', falhas);
fs.writeFileSync(path.join(saida, 'elpis.html'), `<!doctype html><html data-theme="light"><head><meta charset="utf-8"><link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="bundle.css"></head><body style="margin:0"><div id="root" class="pd-demo"></div>
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script><script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script><script src="bundle.js"></script>
<script>var P=Pandora,h=React.createElement;ReactDOM.createRoot(document.getElementById('root')).render(h('div',{style:{display:'flex',gap:16,alignItems:'center',flexWrap:'wrap'}},[640,248,60,44].map(function(t){return h(P.Elpis,{key:t,tamanho:t})})));</script></body></html>`);
