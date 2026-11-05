// Motivos gregos em vetor próprio. Cada um vira máscara CSS (--orn-nome) e arquivo em assets.
const svg = (l, a, corpo) => `<svg xmlns='http://www.w3.org/2000/svg' width='${l}' height='${a}' viewBox='0 0 ${l} ${a}'>${corpo}</svg>`;
const traco = (d, e) => `<path d='${d}' fill='none' stroke='#000' stroke-width='${e}'/>`;
const redondo = (d, e) => `<path d='${d}' fill='none' stroke='#000' stroke-width='${e}' stroke-linecap='round'/>`;
const n = v => +v.toFixed(2);

// Pétala em leque, com a base em (x, y)
function petala(x, y, ang, comp, larg) {
  const r = ang * Math.PI / 180, dx = Math.sin(r), dy = -Math.cos(r), px = -dy, py = dx;
  const p = (a, b) => `${n(x + dx * a + px * b)} ${n(y + dy * a + py * b)}`;
  return `M${p(0, 0)}C${p(comp * .35, larg)} ${p(comp * .85, larg)} ${p(comp, 0)}C${p(comp * .85, -larg)} ${p(comp * .35, -larg)} ${p(0, 0)}Z`;
}
function palmeta() {
  let d = '';
  for (const [a, c] of [[-72, 7.5], [-48, 9.5], [-24, 11], [0, 12], [24, 11], [48, 9.5], [72, 7.5]]) d += petala(11, 13, a, c, 1.5);
  d += 'M6.5 13.2H15.5V14H6.5Z';           // base da palmeta
  d += petala(28, 13.5, 0, 9, 2.1) + petala(28, 13.5, -24, 6, 1.1) + petala(28, 13.5, 24, 6, 1.1); // botão de lótus
  return svg(34, 14, `<path d='${d}'/>`);
}
function ramo() {
  let d = '';
  for (const [x, ang] of [[3, 58], [14, 122]]) d += petala(x, 5, ang, 8.5, 2.1);
  return svg(22, 10, `<path d='M0 5H22' stroke='#000' stroke-width='1'/><path d='${d}'/>`);
}
function rosacea() {
  let d = '';
  for (let i = 0; i < 8; i++) d += petala(12, 12, i * 45, 10, 2.8);
  return svg(24, 24, `<path d='${d}'/><circle cx='12' cy='12' r='2.2' fill='#000'/>`);
}
function fuste() { return svg(14, 6, `<path d='M1 0H3V6H1ZM4.5 0H6V6H4.5ZM8 0H9.5V6H8ZM11 0H13V6H11Z'/>`); }
function capitel() {
  return svg(20, 12, `<path d='M0 0H20V2.2H0Z'/>` + traco('M3.6 9.6C1.6 9.6 1.4 6.8 3.2 6.8 4.6 6.8 4.6 8.4 3.6 8.4M3.2 4.4H16.8M16.4 9.6C18.4 9.6 18.6 6.8 16.8 6.8 15.4 6.8 15.4 8.4 16.4 8.4', 1.2) + `<path d='M5 5.4H15V12H5Z' fill='#000' opacity='0'/>`);
}
function base() { return svg(20, 8, `<path d='M3 0H17V2.6H3ZM1 3.6H19V5.4H1ZM0 6.4H20V8H0Z'/>`); }

const motivos = {
  'chave-canto': svg(16, 16, traco('M.8 16V.8H16M4.6 16V4.6H12V10.4H8', 1.5)),
  'gancho': svg(14, 14, traco('M1.5 12.5V1.5H12.5V9.5H5.5V5.5H9', 1.7)),
  'gancho-espelho': svg(14, 14, traco('M12.5 12.5V1.5H1.5V9.5H8.5V5.5H5', 1.7)),
  'meandro-fino': svg(14, 8, traco('M.7 8V.7H11V6H4.6V3.2H7.8', 1.3)),
  'onda': svg(24, 12, redondo('M0 11H6.5C3.4 7.4 5.8 2 11.5 2 17 2 19 8.6 13.6 9 10.2 9.2 10.2 5.4 13 5.4M6.5 11H24', 1.5)),
  'palmeta': palmeta(),
  'serra-fina': svg(10, 7, `<path d='M0 0H10L5 7Z'/>`),
  'serra-alta': svg(10, 7, `<path d='M0 7L5 0L10 7Z'/>`),
  'ramo': ramo(),
  'voluta': svg(28, 23, redondo('M1.5 1.5C1.5 13 8.5 21.5 17.5 21.5 25.5 21.5 28 12.5 21.5 10 16.5 8.2 13 14.5 18.5 16', 2.4)),
  'rosacea': rosacea(),
  'capitel': capitel(),
  'fuste': fuste(),
  'base-coluna': base(),
  // Com cor própria: a barra nativa aceita imagem, mas não máscara
  'capitel-rolagem': svg(14, 8, `<path d='M0 0H14V3H0ZM2 3H12V5H2ZM4 5H10V8H4Z' fill='#1a1410'/>`),
  'base-rolagem': svg(14, 6, `<path d='M4 0H10V2H4ZM2 2H12V4H2ZM0 4H14V6H0Z' fill='#1a1410'/>`)
};
const url = s => 'url("data:image/svg+xml,' + s.replace(/%/g, '%25').replace(/#/g, '%23').replace(/</g, '%3C').replace(/>/g, '%3E') + '")';
const css = ':root {\n' + Object.entries(motivos).map(([k, v]) => `  --orn-${k}: ${url(v)};`).join('\n') + '\n}\n';
module.exports = { motivos, css };
