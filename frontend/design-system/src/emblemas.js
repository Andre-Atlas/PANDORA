// Emblemas dos brasões em figura negra, numa caixa de 240×240 com o disco interno de raio 88.
// cheio: silhueta. traco: linha grossa da figura. inciso: linha fina riscada em laranja.
const n = v => +v.toFixed(1);
function folha(x, y, ang, comp, larg) {
  const r = ang * Math.PI / 180, dx = Math.cos(r), dy = Math.sin(r), px = -dy, py = dx;
  const p = (a, b) => `${n(x + dx * a + px * b)} ${n(y + dy * a + py * b)}`;
  return { d: `M${p(0, 0)}C${p(comp * .3, larg)} ${p(comp * .75, larg)} ${p(comp, 0)}C${p(comp * .75, -larg)} ${p(comp * .3, -larg)} ${p(0, 0)}Z`, nervura: `M${p(4, 0)}L${p(comp - 6, 0)}` };
}
function oliveira() {
  const bez = t => { const a = [58, 186], b = [104, 170], c = [186, 60], u = 1 - t; return [u * u * a[0] + 2 * u * t * b[0] + t * t * c[0], u * u * a[1] + 2 * u * t * b[1] + t * t * c[1]]; };
  let cheio = '', inciso = '';
  [.12, .26, .4, .54, .68, .82].forEach((t, i) => {
    const [x, y] = bez(t), [x2, y2] = bez(t + .02), ang = Math.atan2(y2 - y, x2 - x) * 180 / Math.PI;
    for (const lado of [-1, 1]) {
      const f = folha(x, y, ang + lado * 42, 42 - i * 2.5, 10); cheio += f.d; inciso += f.nervura;
    }
  });
  const fim = folha(186, 60, -52, 26, 7); cheio += fim.d;
  return [{ tipo: 'traco', d: 'M58 186Q104 170 186 60', largura: 7 }, { tipo: 'cheio', d: cheio }, { tipo: 'inciso', d: inciso }];
}
function espiral() {
  // Crista da onda: a espiral fecha à direita e o rabo desce em curva até a base.
  const cx = 126, cy = 104, r0 = 7, rf = 52, voltas = 2.1, passos = 110;
  const ponto = t => { const a = -Math.PI / 2 + t * voltas * 2 * Math.PI, r = r0 + t * (rf - r0); return [cx + Math.cos(a) * r, cy + Math.sin(a) * r, a]; };
  let d = '';
  for (let i = 0; i <= passos; i++) { const [x, y] = ponto(i / passos); d += (i ? 'L' : 'M') + n(x) + ' ' + n(y); }
  const [xf, yf, af] = ponto(1), tx = -Math.sin(af), ty = Math.cos(af);
  d += `C${n(xf + tx * 34)} ${n(yf + ty * 34)} 124 184 52 180`;
  return [{ tipo: 'traco', d, largura: 11 }, { tipo: 'traco', d: 'M70 196H176', largura: 6 }];
}
module.exports = {
  templo: [
    { tipo: 'cheio', d: 'M120 58L190 98H50ZM58 103H182V113H58ZM62 118H82V158H62ZM94 118H114V158H94ZM126 118H146V158H126ZM158 118H178V158H158ZM52 162H188V172H52ZM44 176H196V188H44Z' },
    { tipo: 'inciso', d: 'M66 124V154M72 124V154M78 124V154M98 124V154M104 124V154M110 124V154M130 124V154M136 124V154M142 124V154M162 124V154M168 124V154M174 124V154M120 76A8 8 0 1 0 120.1 76' }
  ],
  balanca: [
    { tipo: 'cheio', d: 'M116 62H124V168H116ZM120 44A10 10 0 1 1 120 64 10 10 0 1 1 120 44ZM96 180Q120 160 144 180ZM84 182H156V192H84ZM46 136H94Q90 160 70 160 50 160 46 136ZM146 136H194Q190 160 170 160 150 160 146 136Z' },
    { tipo: 'traco', d: 'M66 78Q120 62 174 78', largura: 8 },
    { tipo: 'traco', d: 'M70 78L48 136M70 78L92 136M170 78L148 136M170 78L192 136', largura: 3 },
    { tipo: 'inciso', d: 'M56 144Q70 150 84 144M156 144Q170 150 184 144' }
  ],
  espiral: espiral(),
  oliveira: oliveira(),
  elmo: [
    { tipo: 'cheio', d: 'M78 128C74 78 112 56 142 58 172 60 190 88 188 122L184 170C176 182 164 186 152 186L152 152 138 140 122 142 122 184C104 182 90 172 82 154ZM140 112C150 106 170 108 178 118L176 128C166 122 152 124 142 128Z', regra: 'evenodd' },
    { tipo: 'cheio', d: 'M64 134C44 88 76 34 136 36 164 37 182 48 192 64L180 72C168 56 152 50 136 50 96 50 72 90 80 128Z' },
    { tipo: 'inciso', d: 'M84 134C100 128 118 126 134 130M98 76Q118 64 142 66M100 150Q106 164 116 172' }
  ],
  anfora: [
    { tipo: 'cheio', d: 'M96 44H144V54H134V74C134 84 172 92 172 128 172 160 142 172 132 186H140V198H100V186H108C98 172 68 160 68 128 68 92 106 84 106 74V54H96Z' },
    { tipo: 'traco', d: 'M108 62C76 56 58 84 78 104M132 62C164 56 182 84 162 104', largura: 8 },
    { tipo: 'inciso', d: 'M72 116H168M71 144H169M78 138L90 122 102 138 114 122 126 138 138 122 150 138 162 122' }
  ]
};
