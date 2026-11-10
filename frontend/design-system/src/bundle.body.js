(function () {
  var React = window.React, h = React.createElement, useState = React.useState, useId = React.useId, useRef = React.useRef, useEffect = React.useEffect, Fragment = React.Fragment;
  var CENA_PADRAO = '/_blob/315e6beaff9ab6221886784cbff1e112';

  function cx() { return Array.prototype.filter.call(arguments, Boolean).join(' '); }

  /* Ícones: traço de 2px em grade de 24px */
  var ICONES = {
    casa: 'M3 11l9-7 9 7M5 10v10h14V10M10 20v-6h4v6',
    balanca: 'M12 4v16M7 20h10M4 7h16M6 7l-3 7a3.5 3.5 0 0 0 6 0L6 7zM18 7l-3 7a3.5 3.5 0 0 0 6 0l-3-7z',
    trilha: 'M6 20a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM18 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM8 18h7a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h7',
    escudo: 'M12 3l8 3v6c0 5-3.4 8-8 9-4.6-1-8-4-8-9V6l8-3zM9 12l2 2 4-4',
    microfone: 'M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM6 11a6 6 0 0 0 12 0M12 17v4M9 21h6',
    camera: 'M4 8h4l2-3h4l2 3h4v11H4V8zM12 16a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    clipe: 'M20 11l-8.5 8.5a5 5 0 0 1-7-7L13 4a3.5 3.5 0 0 1 5 5l-8.5 8.5a2 2 0 0 1-3-3L14 7',
    enviar: 'M12 19V5M6 11l6-6 6 6',
    voltar: 'M15 5l-7 7 7 7',
    seta: 'M5 12h14M13 6l6 6-6 6',
    avancar: 'M9 5l7 7-7 7',
    check: 'M5 12.5l4.5 4.5L19 7.5',
    x: 'M6 6l12 12M18 6L6 18',
    alerta: 'M12 4l9 16H3l9-16zM12 10v4.5M12 17.5v.01',
    info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v5M12 8v.01',
    sino: 'M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15L6 16zM10 21h4',
    telefone: 'M5 4h4l1.5 5-2.2 1.6a12 12 0 0 0 5.1 5.1L15 13.5l5 1.5v4a2 2 0 0 1-2 2C10 21 3 14 3 6a2 2 0 0 1 2-2z',
    documento: 'M6 3h9l4 4v14H6V3zM15 3v4h4M9 12h7M9 16h7',
    relogio: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3.5 2',
    copiar: 'M9 9h11v11H9V9zM5 15H4V4h11v1',
    som: 'M4 10v4h4l5 4V6L8 10H4zM16.5 9a4 4 0 0 1 0 6M19 6.5a8 8 0 0 1 0 11',
    livro: 'M4 5c3-1 6-1 8 1 2-2 5-2 8-1v14c-3-1-6-1-8 1-2-2-5-2-8-1V5zM12 6v14',
    lupa: 'M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4',
    pessoas: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M16 11a3 3 0 1 0-1.5-5.6M17 14c2.5.5 4 2.6 4 6',
    upload: 'M12 16V5M7 10l5-5 5 5M4 19h16',
    banco: 'M4 9l8-5 8 5v1H4V9zM6 10v7M10 10v7M14 10v7M18 10v7M4 20h16',
    pausa: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM10 9v6M14 9v6',
    coracao: 'M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.7A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z',
    alvo: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
    jarro: 'M9 3h6M10 3v3C7 8 5 11 5 14c0 4 3 7 7 7s7-3 7-7c0-3-2-6-5-8V3'
  };

  function Icone(p) {
    var t = p.tamanho || 24;
    return h('svg', { className: cx('pd-svg', p.className), width: t, height: t, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: p.traco || 2, strokeLinecap: 'round', strokeLinejoin: 'round', role: p.rotulo ? 'img' : undefined, 'aria-label': p.rotulo, 'aria-hidden': p.rotulo ? undefined : true },
      h('path', { d: ICONES[p.nome] || ICONES.info }));
  }

  /* Ornamentos */
  function Friso(p) {
    var tipo = p.tipo || 'meandro';
    if (p.grande) return h('div', { className: 'pd-' + tipo, 'aria-hidden': true });
    return h('div', { className: cx('pd-friso', 'pd-friso-' + tipo, p.tom && 'pd-friso-' + p.tom, p.curto && 'pd-friso-curto'), 'aria-hidden': true });
  }
  function Meandro(p) { return h('div', { className: cx('pd-meandro', p && p.posicao === 'baixo' && 'pd-meandro-baixo'), 'aria-hidden': true }); }
  /* Depreciado: a serra saiu do sistema. Mantido para quem já consome o bundle; desenha o meandro de baixo. */
  function Serra() { return h(Meandro, { posicao: 'baixo' }); }

  var ESPIRITOS = ['M48 46C40 34 58 28 50 16 46 10 38 12 40 18', 'M38 48C24 42 30 28 18 24 12 22 8 28 13 32', 'M60 46C74 40 66 26 78 20 84 18 88 24 83 28'];
  function CaixaMarca(p) {
    var t = p.tamanho || 96;
    function tracos(cor, largura) { return h('g', { stroke: cor, strokeWidth: largura, fill: 'none', strokeLinecap: 'round' }, ESPIRITOS.map(function (d, i) { return h('path', { key: i, d: d }); })); }
    return h('svg', { className: 'pd-svg', width: t, height: t, viewBox: '0 0 96 96', role: 'img', 'aria-label': p.rotulo || 'Caixa de Pandora aberta, com espíritos saindo' },
      tracos('#1a1410', 9), tracos('#fff8ec', 5),
      h('path', { d: 'M12 42L82 40 84 50 14 52Z', fill: '#1a1410' }),
      h('rect', { x: 18, y: 54, width: 60, height: 34, rx: 2, fill: '#1a1410' }),
      h('path', { d: 'M24 62H72M24 80H72', stroke: '#f0792b', strokeWidth: 2.5 }),
      h('path', { d: 'M32 76V67H42V73H37M56 76V67H66V73H61', fill: 'none', stroke: '#f0792b', strokeWidth: 2.5 }));
  }

  /* Anel de meandro compartilhado por Elpis, brasões e voz, numa caixa de 240×240. */
  function AnelMeandro(p) {
    var n = p.unidades || 24, unidades = [];
    for (var i = 0; i < n; i++) unidades.push(h('path', { key: i, d: p.chave || 'M111 24V9.5H129V20H118V14.5H124', transform: 'rotate(' + (i * 360 / n) + ' 120 120)' }));
    return h('g', { className: p.className, fill: 'none', style: { stroke: p.cor }, strokeWidth: p.largura || 2.8 }, h('circle', { cx: 120, cy: 120, r: 115.5 }), h('circle', { cx: 120, cy: 120, r: 92 }), unidades);
  }
  var CHAVE_LARGA = 'M105 24V9H135V20H114V14H126';

  /* Elpis: figura negra dentro do anel de meandro. Abaixo de 72px mostra só o busto. */
  var FIGURA_ELPIS = '__FIGURA_ELPIS__';
  function Elpis(p) {
    var t = p.tamanho || 64, pequeno = t < 72, ouvindo = p.estado === 'ouvindo', id = useId().replace(/:/g, '');
    var raio = pequeno ? 100 : 88;
    return h('svg', { className: cx('pd-svg', ouvindo && 'pd-elpis-ouvindo'), width: t, height: t, viewBox: '0 0 240 240', role: 'img', 'aria-label': p.rotulo || 'Elpis' },
      h('defs', null, h('clipPath', { id: id }, h('circle', { cx: 120, cy: 120, r: raio }))),
      h('circle', { cx: 120, cy: 120, r: 120, fill: '#1a1410' }),
      pequeno ? h('circle', { cx: 120, cy: 120, r: 109, fill: 'none', stroke: '#f0792b', strokeWidth: 7 }) :
        h(AnelMeandro, { className: 'pd-elpis-anel', cor: '#f0792b' }),
      h('circle', { cx: 120, cy: 120, r: raio, fill: '#f0792b' }),
      h('g', { clipPath: 'url(#' + id + ')' }, h('path', { d: FIGURA_ELPIS, fill: '#1a1410', fillRule: 'evenodd', transform: pequeno ? 'translate(-108 -74) scale(1.02)' : 'translate(53 1) scale(0.295)' })));
  }

  /* Brasões da trilha: mesmo medalhão de Elpis, com um emblema em figura negra. */
  var EMBLEMAS = __EMBLEMAS__;
  function ParteEmblema(p) {
    var e = p.parte, cor = p.apagado ? 'var(--texto-2)' : '#1a1410';
    if (e.tipo === 'inciso') return p.apagado ? null : h('path', { d: e.d, fill: 'none', stroke: '#f0792b', strokeWidth: 3.2, strokeLinecap: 'round' });
    if (e.tipo === 'traco') return h('path', { d: e.d, fill: 'none', style: { stroke: cor }, strokeWidth: p.apagado ? Math.min(e.largura, 6) : e.largura, strokeLinecap: 'round', strokeLinejoin: 'round' });
    return p.apagado ? h('path', { d: e.d, fill: 'none', style: { stroke: cor }, strokeWidth: 5, strokeLinejoin: 'round' }) : h('path', { d: e.d, fill: cor, fillRule: e.regra });
  }
  function Brasao(p) {
    var t = p.tamanho || 84, pequeno = t < 72, estado = p.estado || 'feito', apagado = estado === 'proximo';
    var raio = pequeno ? 100 : 88, fundo = apagado ? 'var(--cartao)' : '#1a1410', cor = apagado ? 'var(--linha-forte)' : '#f0792b';
    return h('svg', { className: 'pd-svg pd-brasao', width: t, height: t, viewBox: '0 0 240 240', role: p.rotulo ? 'img' : undefined, 'aria-label': p.rotulo, 'aria-hidden': p.rotulo ? undefined : true },
      h('circle', { cx: 120, cy: 120, r: 118, style: { fill: fundo, stroke: apagado ? 'var(--linha-forte)' : '#1a1410' }, strokeWidth: 4 }),
      pequeno ? h('circle', { cx: 120, cy: 120, r: 109, fill: 'none', style: { stroke: cor }, strokeWidth: 7 }) :
        h(AnelMeandro, { cor: cor, unidades: 16, chave: CHAVE_LARGA, largura: 4 }),
      h('circle', { cx: 120, cy: 120, r: raio, style: { fill: apagado ? 'var(--cartao)' : '#f0792b' } }),
      (EMBLEMAS[p.emblema] || []).map(function (e, i) { return h(ParteEmblema, { key: i, parte: e, apagado: apagado }); }),
      estado === 'feito' && !pequeno ? h('g', null, h('circle', { className: 'pd-brasao-selo', cx: 196, cy: 196, r: 38 }), h('path', { className: 'pd-brasao-check', d: 'M178 197l13 14 24-27' })) : null);
  }

  function Anfora(p) {
    var id = useId().replace(/:/g, ''), nivel = Math.max(0, Math.min(1, p.nivel || 0)), altura = p.altura || 92;
    var corpo = 'M22 6H38V14C38 20 50 24 50 42 50 60 38 72 34 78H26C22 72 10 60 10 42 10 24 22 20 22 14Z';
    var topo = 6 + 72 * (1 - nivel);
    return h('svg', { className: 'pd-svg', width: altura * 60 / 84, height: altura, viewBox: '0 0 60 84', role: 'img', 'aria-label': p.rotulo || (Math.round(nivel * 100) + '% cheia') },
      h('defs', null, h('clipPath', { id: id }, h('path', { d: corpo }))),
      h('rect', { x: 0, y: topo, width: 60, height: 84, fill: '#f0792b', clipPath: 'url(#' + id + ')' }),
      h('path', { d: corpo, fill: 'none', stroke: 'currentColor', strokeWidth: 3, strokeLinejoin: 'round' }),
      h('path', { d: 'M22 13C9 13 6 28 13 31M38 13C51 13 54 28 47 31M19 5H41', fill: 'none', stroke: 'currentColor', strokeWidth: 3, strokeLinecap: 'round' }));
  }

  /* Ações */
  function Botao(p) {
    var v = p.variante || 'primario';
    return h('button', { type: 'button', className: cx('pd-botao', 'pd-botao-' + v, p.bloco && 'pd-botao-bloco', p.ampliado && 'pd-botao-ampliado'), disabled: p.desativado, onClick: p.onClick },
      p.icone ? h(Icone, { nome: p.icone, tamanho: p.ampliado ? 30 : 22 }) : null, p.children,
      p.seta ? h(Icone, { nome: 'seta', tamanho: 22 }) : null);
  }
  function BotaoIcone(p) {
    return h('button', { type: 'button', className: cx('pd-botao-icone', p.tom && 'pd-botao-icone-' + p.tom), 'aria-label': p.rotulo, onClick: p.onClick }, h(Icone, { nome: p.icone }));
  }
  function BotaoVoz(p) {
    return h('button', { type: 'button', className: 'pd-botao-voz', 'aria-pressed': !!p.ativo, 'aria-label': p.rotulo || (p.ativo ? 'Parar de gravar' : 'Falar com Elpis'), onClick: p.onClick },
      h('svg', { className: 'pd-botao-voz-anel', viewBox: '0 0 240 240', 'aria-hidden': true }, h(AnelMeandro, { cor: 'currentColor', unidades: 16, chave: CHAVE_LARGA, largura: 4 })),
      h(Icone, { nome: 'microfone', tamanho: 40 }));
  }
  function Selo(p) {
    var tom = p.tom || 'neutro';
    var padrao = { ok: 'check', alerta: 'alerta', fonte: 'livro' }[tom];
    var icone = p.icone === undefined ? padrao : p.icone;
    return h('span', { className: cx('pd-selo', 'pd-selo-' + tom) }, icone ? h(Icone, { nome: icone, tamanho: 16, traco: 2.5 }) : null, p.children);
  }
  function SeloCalculado() { return h(Selo, { tom: 'fonte', icone: 'check' }, 'Calculado'); }

  /* Disco de ícone para estados: o ícone vem sempre com palavra ao lado. */
  function Disco(p) {
    return h('span', { className: cx('pd-disco', 'pd-disco-' + p.tom, p.tamanho && 'pd-disco-' + p.tamanho), 'aria-hidden': true }, h(Icone, { nome: p.icone, tamanho: p.tamanho === 'grande' ? 34 : p.tamanho === 'pequeno' ? 16 : 20, traco: 2.6 }));
  }

  /* Dados */
  function Cartao(p) {
    var disco = p.tom === 'alerta' ? 'alerta' : p.tom === 'ok' ? 'check' : null;
    var titulo = p.titulo ? h('h3', { className: p.marco ? 'pd-no-marco' : 'pd-cartao-titulo' }, p.titulo) : null;
    return h('section', { className: cx('pd-cartao', p.tom && 'pd-cartao-' + p.tom, p.className) },
      p.sobre ? h('p', { className: 'pd-cartao-sobre' }, p.sobre) : null,
      disco && titulo ? h('div', { className: 'pd-cartao-cabeca' }, h(Disco, { tom: p.tom, icone: disco }), titulo) : titulo, p.children);
  }
  function Trilho(p) {
    var total = p.total || p.partes.reduce(function (s, x) { return s + x.valor; }, 0);
    return h('div', { className: 'pd-trilho', role: 'img', 'aria-label': p.rotulo },
      p.partes.map(function (x, i) { return h('div', { key: i, className: cx('pd-trilho-parte', 'pd-tom-' + x.tom), style: { width: (x.valor / total * 100) + '%' } }); }));
  }
  function Insight(p) {
    return h('section', { className: 'pd-cartao pd-insight' }, h(Elpis, { tamanho: 48 }),
      h('div', { className: 'pd-insight-corpo' }, h('p', { className: 'pd-insight-sobre' }, p.sobre || 'Uma coisa que notei'), h('p', null, p.children),
        p.acao ? h(Botao, { variante: 'fantasma' }, p.acao) : null));
  }
  function LinkCartao(p) {
    return h('button', { type: 'button', className: 'pd-link-cartao', onClick: p.onClick }, h(Icone, { nome: p.icone, tamanho: 26 }),
      h('span', { className: 'pd-lista-texto' }, h('strong', null, p.titulo), p.descricao ? h('span', { className: 'pd-apoio' }, p.descricao) : null),
      h(Icone, { nome: 'avancar', tamanho: 20 }));
  }
  function CampoPergunta(p) {
    return h('div', { className: 'pd-pergunta' }, p.anexo === false ? null : h(BotaoIcone, { icone: 'clipe', rotulo: 'Enviar foto ou PDF' }),
      h('input', { className: 'pd-pergunta-texto', type: 'text', placeholder: p.placeholder || 'Pergunte à Elpis', 'aria-label': p.placeholder || 'Pergunte à Elpis', style: p.anexo === false ? { paddingLeft: 2 } : null }),
      h(BotaoIcone, { icone: 'microfone', tom: 'acao', rotulo: 'Falar com Elpis' }));
  }

  /* Formulários */
  function Progresso(p) {
    return h('div', { className: 'pd-progresso' }, p.voltar === false ? null : h(BotaoIcone, { icone: 'voltar', rotulo: 'Voltar' }),
      h('div', { className: 'pd-progresso-barra', role: 'progressbar', 'aria-valuenow': p.passo, 'aria-valuemin': 0, 'aria-valuemax': p.total, 'aria-label': 'Passo ' + p.passo + ' de ' + p.total },
        h('div', { className: 'pd-progresso-feito', style: { width: (p.passo / p.total * 100) + '%' } })),
      p.pular === false ? null : h(Botao, { variante: 'fantasma' }, 'Pular'));
  }
  function OpcaoCartao(p) {
    return h('button', { type: 'button', role: 'radio', 'aria-checked': !!p.marcada, className: 'pd-opcao', onClick: p.onClick },
      p.icone ? h(Icone, { nome: p.icone, tamanho: 28, className: 'pd-opcao-icone' }) : null,
      h('span', { className: 'pd-opcao-texto' }, h('strong', null, p.titulo), p.descricao ? h('span', { className: 'pd-apoio' }, p.descricao) : null),
      h('span', { className: 'pd-opcao-marca', 'aria-hidden': true }, p.marcada ? h(Icone, { nome: 'check', tamanho: 16, traco: 3 }) : null));
  }
  var NIVEIS = ['', 'No limite', 'No limite', 'Muito apertado', 'Muito apertado', 'Apertado, mas seguindo', 'Apertado, mas seguindo', 'Mais tranquilo', 'Mais tranquilo', 'Tranquilo', 'Tranquilo'];
  function EscalaSentimento(p) {
    var st = useState(p.valor || 3), v = st[0];
    return h('div', { className: 'pd-escala' },
      h('p', { className: 'pd-escala-nivel pd-num' }, 'Nível ' + v + ' de 10'),
      h('p', { className: 'pd-escala-rotulo', 'aria-live': 'polite' }, NIVEIS[v]),
      h('input', { type: 'range', min: 1, max: 10, step: 1, value: v, 'aria-label': 'Como você se sente sobre seu dinheiro', style: { '--pct': ((v - 1) / 9 * 100) + '%' }, onChange: function (e) { st[1](+e.target.value); } }),
      h('div', { className: 'pd-escala-pontas' }, h('span', null, 'No limite'), h('span', null, 'Tranquilo')));
  }
  function Consentimento(p) {
    var st = useState(!!p.marcado);
    return h('label', { className: 'pd-consentimento' }, h('input', { type: 'checkbox', checked: st[0], onChange: function (e) { st[1](e.target.checked); } }), h('span', null, p.children));
  }
  function Segmento(p) {
    return h('div', { className: 'pd-segmento', role: 'radiogroup', 'aria-label': p.rotulo },
      p.opcoes.map(function (o) { return h('button', { key: o, type: 'button', role: 'radio', 'aria-checked': o === p.valor, className: 'pd-segmento-item', onClick: function () { if (p.onChange) p.onChange(o); } }, o); }));
  }
  function Alternador(p) {
    var st = useState(!!p.ligado);
    return h('button', { type: 'button', role: 'switch', 'aria-checked': st[0], className: 'pd-alternador', onClick: function () { st[1](!st[0]); } },
      h('span', { className: 'pd-alternador-texto' }, h('strong', null, p.titulo), p.descricao ? h('span', { className: 'pd-apoio' }, p.descricao) : null),
      h('span', { className: 'pd-alternador-trilho', 'aria-hidden': true }));
  }

  /* Dívidas */
  function LinhaDivida(p) {
    return h('article', { className: 'pd-divida' },
      h('div', { className: 'pd-divida-cabeca' },
        h('span', { className: cx('pd-divida-ordem', p.protegida && 'pd-divida-ordem-ok') }, p.protegida ? h(Icone, { nome: 'escudo', tamanho: 20 }) : p.ordem),
        h('span', { className: 'pd-divida-nome' }, p.nome), h('span', { className: 'pd-valor-lg' }, p.valor)),
      p.children);
  }
  function DegrausProgresso(p) {
    var passos = p.passos, atual = p.atual;
    return h('div', { className: 'pd-degraus', role: 'img', 'aria-label': 'Etapa ' + atual + ' de ' + passos },
      Array.apply(null, Array(passos)).map(function (_, i) {
        var n = i + 1;
        return h('div', { key: n, className: cx('pd-degrau', n === atual && 'pd-degrau-atual', n > atual && 'pd-degrau-a-fazer'), style: { height: 24 + i * 14 } }, n);
      }));
  }

  /* Conversa */
  function Balao(p) {
    return h('div', { className: cx('pd-balao', 'pd-balao-' + (p.autor || 'elpis')) }, p.children);
  }
  function CitacaoCartao(p) {
    return h('div', { className: 'pd-citacao' }, h('div', null, h(Selo, { tom: 'fonte' }, 'Fonte oficial')),
      h('strong', null, p.norma), p.children ? h('span', { className: 'pd-apoio' }, p.children) : null,
      h('a', { className: 'pd-citacao-link', href: p.href, target: '_blank', rel: 'noreferrer' }, p.rotuloLink, h(Icone, { nome: 'seta', tamanho: 16 })));
  }
  function BlocoCalculado(p) {
    return h('div', { className: 'pd-calculo' }, h('div', { style: { marginBottom: 4 } }, h(SeloCalculado)),
      p.linhas.map(function (l, i) { return h('div', { key: i, className: 'pd-calculo-linha' }, h('span', null, l[0]), h('strong', null, l[1])); }));
  }
  function CabecalhoElpis(p) {
    return h('div', { className: 'pd-chat-cabeca' }, h(Elpis, { tamanho: 44 }),
      h('div', { className: 'pd-chat-identidade' }, h('strong', null, 'Elpis'), h('div', { className: 'pd-apoio' }, p.nota || 'Privado: nome e CPF ficam mascarados')),
      h(BotaoIcone, { icone: 'info', rotulo: 'Como Elpis usa seus dados' }));
  }

  /* Trilha */
  var ETAPAS = [
    { n: 1, t: 'Mínimo existencial', x: 70, lado: 'd', estado: 'feito', marco: null, emblema: 'templo' },
    { n: 2, t: 'Juros e CET', x: 200, lado: 'e', estado: 'feito', marco: null, emblema: 'balanca' },
    { n: 3, t: 'Rotativo', x: 288, lado: 'e', estado: 'atual', marco: null, emblema: 'espiral' },
    { n: 4, t: 'Repactuação', x: 200, lado: 'e', estado: 'proximo', marco: 'Marco: conheço meus direitos', emblema: 'oliveira' },
    { n: 5, t: 'Golpes e MED', x: 78, lado: 'd', estado: 'proximo', marco: 'Marco: sei me proteger', emblema: 'elmo' },
    { n: 6, t: 'Reserva de emergência', x: 200, lado: 'e', estado: 'proximo', marco: 'Marco: tenho um plano', emblema: 'anfora' }
  ];
  var PASSO_Y = 124, TOPO_Y = 54;
  function TrilhaCaminho(p) {
    var etapas = p.etapas || ETAPAS, altura = etapas.length * PASSO_Y;
    var d = etapas.reduce(function (s, e, i) {
      var y = TOPO_Y + i * PASSO_Y;
      if (i === 0) return 'M' + e.x + ' ' + y;
      var a = etapas[i - 1], ya = y - PASSO_Y, meio = ya + PASSO_Y / 2;
      return s + 'C' + a.x + ' ' + meio + ' ' + e.x + ' ' + meio + ' ' + e.x + ' ' + y;
    }, '');
    return h('div', { className: 'pd-trilha', style: { height: altura } },
      h('svg', { className: 'pd-trilha-rota', width: 358, height: altura, 'aria-hidden': true }, h('path', { d: d, fill: 'none', stroke: 'currentColor', strokeWidth: 3, strokeDasharray: '2 10', strokeLinecap: 'round' })),
      etapas.map(function (e, i) {
        var y = TOPO_Y + i * PASSO_Y;
        var estadoTexto = { feito: 'Concluída', atual: 'Você está aqui', proximo: 'A seguir' }[e.estado];
        var estiloRotulo = e.lado === 'd' ? { left: e.x + 54, top: y } : { right: 358 - e.x + 54, top: y };
        return h(Fragment, { key: e.n },
          h('button', { type: 'button', className: cx('pd-no', e.estado === 'atual' && 'pd-no-atual'), style: { left: e.x, top: y }, 'aria-label': 'Etapa ' + e.n + ': ' + e.t + '. ' + estadoTexto },
            h(Brasao, { emblema: e.emblema, estado: e.estado })),
          h('div', { className: cx('pd-no-rotulo', e.lado === 'e' && 'pd-no-rotulo-esq'), style: estiloRotulo },
            h('strong', null, e.t), h('span', { className: 'pd-apoio' }, e.marco || estadoTexto)));
      }));
  }
  function QuizOpcao(p) {
    return h('button', { type: 'button', className: 'pd-quiz-opcao', 'data-estado': p.estado || 'neutra', 'aria-pressed': p.estado === 'certa', onClick: p.onClick },
      h('span', { className: 'pd-quiz-letra', 'aria-hidden': true }, p.estado === 'certa' ? h(Icone, { nome: 'check', tamanho: 18, traco: 3 }) : p.letra),
      h('span', { className: 'pd-quiz-texto' }, p.children));
  }

  /* Moldura */
  /* A navegação sai do fluxo do conteúdo: embaixo no celular, trilho lateral em telas largas ou deitadas. */
  function Aparelho(p) {
    var filhos = React.Children.toArray(p.children);
    var nav = filhos.filter(function (c) { return c && c.type === NavBase; });
    var resto = filhos.filter(function (c) { return !(c && c.type === NavBase); });
    return h('div', { className: 'pd-aparelho' }, h('div', { className: 'pd-tela', 'data-topo': p.topo || 'leitura', 'data-nav': nav.length ? 'sim' : undefined, style: p.altura ? { height: p.altura, minHeight: 0 } : null },
      h('div', { className: 'pd-tela-interior' },
      h('div', { className: 'pd-tela-conteudo' },
      h('div', { className: 'pd-status' }, h('span', null, '9:41'), h('span', { className: 'pd-status-ilha', 'aria-hidden': true }),
        h('span', { className: 'pd-status-icones', 'aria-hidden': true },
          h('svg', { width: 18, height: 12, viewBox: '0 0 18 12', fill: 'currentColor' }, h('rect', { x: 0, y: 8, width: 3, height: 4, rx: 1 }), h('rect', { x: 5, y: 5, width: 3, height: 7, rx: 1 }), h('rect', { x: 10, y: 3, width: 3, height: 9, rx: 1 }), h('rect', { x: 15, y: 0, width: 3, height: 12, rx: 1 })),
          h('svg', { width: 26, height: 12, viewBox: '0 0 26 12' }, h('rect', { x: 0.5, y: 0.5, width: 22, height: 11, rx: 3, fill: 'none', stroke: 'currentColor' }), h('rect', { x: 2, y: 2, width: 17, height: 8, rx: 2, fill: 'currentColor' })))),
      resto), nav)));
  }
  function Rolagem(p) {
    var area = useRef(null), st = useState({ topo: 0, altura: 100, visivel: false });
    function mede() {
      var a = area.current;
      if (a) st[1]({ topo: a.scrollTop / a.scrollHeight * 100, altura: a.clientHeight / a.scrollHeight * 100, visivel: a.scrollHeight > a.clientHeight });
    }
    useEffect(mede, []);
    return h('div', { className: 'pd-rolagem' },
      h('div', { ref: area, className: 'pd-rolagem-area', onScroll: mede, tabIndex: 0, role: 'region', 'aria-label': p.rotulo || 'Conteúdo rolável' }, p.children),
      st[0].visivel ? h('div', { className: 'pd-rolagem-trilho', 'aria-hidden': true }, h('div', { className: 'pd-rolagem-polegar', style: { top: st[0].topo + '%', height: st[0].altura + '%' } })) : null);
  }
  function CabecalhoMito(p) {
    return h('header', { className: 'pd-mito' }, h(Meandro),
      h('div', { className: 'pd-mito-conteudo' },
        p.titulo || p.acao || p.voltar ? h('div', { className: 'pd-mito-topo' },
          p.voltar ? h(BotaoIcone, { icone: 'voltar', tom: 'mito', rotulo: 'Voltar' }) : null,
          h('h1', { className: 'pd-mito-titulo', style: { flex: 1 } }, p.titulo), p.acao) : null,
        p.subtitulo ? h('p', { className: 'pd-mito-sub' }, p.subtitulo) : null, p.children),
      h(Meandro, { posicao: 'baixo' }));
  }
  var ITENS_NAV = [['inicio', 'Início', 'casa'], ['dividas', 'Dívidas', 'balanca'], ['elpis', 'Elpis', null], ['trilha', 'Trilha', 'trilha'], ['guardiao', 'Guardião', 'escudo']];
  /* Base do vaso. Retrátil: embaixo recolhe para a faixa com Elpis; no trilho lateral alterna entre só ícones e ícones com rótulo. */
  function NavBase(p) {
    var st = useState(!!p.recolhida), recolhida = p.recolhida !== undefined && p.onAlternar ? p.recolhida : st[0];
    var id = useId();
    function alterna() { st[1](!recolhida); if (p.onAlternar) p.onAlternar(!recolhida); }
    return h('nav', { className: 'pd-nav', 'data-recolhida': recolhida ? 'sim' : undefined, 'aria-label': 'Navegação principal' },
      h('button', { type: 'button', className: 'pd-nav-alternar', 'aria-expanded': !recolhida, 'aria-controls': id, onClick: alterna },
        h('span', { className: 'pd-nav-alternar-chave', 'aria-hidden': true }),
        h('span', { className: 'pd-oculto' }, recolhida ? 'Expandir navegação' : 'Recolher navegação')),
      h('div', { className: 'pd-nav-itens', id: id }, ITENS_NAV.map(function (it) {
        var ativo = p.ativo === it[0], elpis = it[0] === 'elpis';
        return h('button', { key: it[0], type: 'button', className: cx('pd-nav-item', elpis && 'pd-nav-item-elpis'), 'aria-current': ativo ? 'page' : undefined, onClick: function () { if (p.onNavegar) p.onNavegar(it[0]); } },
          elpis ? h('span', { className: 'pd-nav-elpis-disco' }, h(Elpis, { tamanho: 60 })) : h(Icone, { nome: it[2], tamanho: 26 }), h('span', { className: 'pd-nav-rotulo' }, it[1]));
      })));
  }

  /* Telas */
  function TelaAbertura(p) {
    var passo = p.passo === undefined ? 0 : p.passo;
    var pesa = useState('Dívidas que não fecham');
    var inicio = useState('Enviar fatura ou extrato');
    if (passo === 0) return h(Aparelho, { topo: 'mito' },
      h('div', { className: 'pd-abertura pd-base' },
        h('img', { className: 'pd-abertura-fundo', src: p.cena || CENA_PADRAO, alt: '', 'aria-hidden': true }),
        h('img', { className: 'pd-abertura-cena', src: p.cena || CENA_PADRAO, alt: 'Pandora, em figura negra sobre fundo laranja, abre a caixa entre duas colunas. Espíritos brancos saem dela.' }),
        h('div', { className: 'pd-abertura-painel' },
          h('div', { className: 'pd-abertura-texto' },
            h('div', { className: 'pd-lancetas', 'aria-hidden': true }),
            h('h1', { className: 'pd-abertura-nome' }, 'PANDORA'),
            h('p', { className: 'pd-abertura-frase' }, 'Ainda há esperança…'),
            h(Friso, { tipo: 'ramo', tom: 'base', curto: true }),
            h(Botao, { variante: 'claro', bloco: true, seta: true }, 'Começar')))));
    if (passo === 1) return h(Aparelho, null, h('div', { className: 'pd-pergunta-tela' }, h(Progresso, { passo: 1, total: 3 }),
      h('h1', { className: 'pd-pergunta-titulo' }, 'Como você se sente sobre seu dinheiro hoje?'),
      h('p', { className: 'pd-pergunta-sub' }, 'Nenhuma resposta é errada. Isso só mostra de onde partimos.'),
      h('div', { className: 'pd-empurra' }), h(EscalaSentimento, { valor: 3 }), h('div', { className: 'pd-empurra' }),
      h(Botao, { bloco: true, seta: true }, 'Continuar')));
    if (passo === 2) {
      var ops = [['balanca', 'Dívidas que não fecham', 'Cartão, empréstimo, contas atrasadas'], ['pausa', 'Apostas fora de controle', 'Pix para bets que somem do mês'], ['escudo', 'Medo de golpes', 'Boletos, Pix e ligações suspeitas'], ['relogio', 'Renda que muda todo mês', 'Autônomo, MEI, aplicativo'], ['jarro', 'Quero guardar e não voltar', 'Saí das dívidas e quero segurança']];
      return h(Aparelho, null, h('div', { className: 'pd-pergunta-tela' }, h(Progresso, { passo: 2, total: 3 }),
        h('h1', { className: 'pd-pergunta-titulo' }, 'O que mais pesa hoje?'),
        h('div', { role: 'radiogroup', 'aria-label': 'O que mais pesa hoje', className: 'pd-demo-coluna' }, ops.map(function (o) { return h(OpcaoCartao, { key: o[1], icone: o[0], titulo: o[1], descricao: o[2], marcada: pesa[0] === o[1], onClick: function () { pesa[1](o[1]); } }); })),
        h('div', { className: 'pd-empurra' }), h(Botao, { bloco: true, seta: true }, 'Continuar')));
    }
    var modos = [['upload', 'Enviar fatura ou extrato', 'PDF ou foto. Nada é conectado ao seu banco.'], ['banco', 'Conectar pelo Open Finance', 'Ambiente de testes (sandbox), só leitura.']];
    return h(Aparelho, null, h('div', { className: 'pd-pergunta-tela' }, h(Progresso, { passo: 3, total: 3, pular: false }),
      h('h1', { className: 'pd-pergunta-titulo' }, 'Como quer começar?'),
      h('div', { role: 'radiogroup', 'aria-label': 'Como quer começar', className: 'pd-demo-coluna' }, modos.map(function (o) { return h(OpcaoCartao, { key: o[1], icone: o[0], titulo: o[1], descricao: o[2], marcada: inicio[0] === o[1], onClick: function () { inicio[1](o[1]); } }); })),
      h(Cartao, { tom: 'apoio', titulo: 'O combinado' }, h('ul', { className: 'pd-lista' },
        ['O PANDORA só lê. Nunca movimenta seu dinheiro.', 'Nome, CPF e conta são mascarados antes de qualquer IA.', 'Você apaga tudo quando quiser.'].map(function (t) { return h('li', { key: t }, h(Icone, { nome: 'check', tamanho: 20 }), h('span', { className: 'pd-lista-texto' }, t)); }))),
      h(Consentimento, { marcado: true }, 'Concordo com o uso dos meus dados para este diagnóstico.'),
      h('div', { className: 'pd-empurra' }), h(Botao, { bloco: true, seta: true }, 'Abrir minha caixa')));
  }

  function TelaInicio() {
    return h(Aparelho, { topo: 'mito' },
      h(CabecalhoMito, { titulo: 'Olá, Carla', acao: h(BotaoIcone, { icone: 'sino', tom: 'mito', rotulo: 'Avisos' }) },
        h('p', { className: 'pd-mito-sub', style: { fontWeight: 700 } }, 'Protegido este mês'),
        h('p', { className: 'pd-valor-xl' }, 'R$ 2.100,00'),
        h('p', { className: 'pd-mito-sub' }, 'Seu mínimo existencial: aluguel, mercado, contas e transporte. Nenhum plano mexe nesse valor.')),
      h('div', { className: 'pd-corpo' },
        h(CampoPergunta, { anexo: false, placeholder: 'Pergunte à Elpis' }),
        h(Insight, { acao: 'Entender esse valor' }, h('strong', { className: 'pd-num' }, 'R$ 342,18'), ' da sua fatura foram só juros e IOF. É metade do mercado do mês.'),
        h(Cartao, { sobre: 'Seu próximo passo', titulo: 'Regularizar a conta de luz' },
          h('p', null, 'R$ 360 em 2 faturas. Com 45 dias de atraso, há risco de corte.'), h(Botao, { bloco: true, seta: true }, 'Ver o plano')),
        h(Cartao, { sobre: 'Raio-X do mês', titulo: 'Renda de R$ 2.850' },
          h(Trilho, { partes: [{ valor: 2100, tom: 'ok' }, { valor: 750, tom: 'vaso' }], rotulo: 'R$ 2.100 protegidos e R$ 750 de folga real' }),
          h('div', { className: 'pd-legenda' },
            h('div', { className: 'pd-legenda-item' }, h('span', { className: 'pd-apoio' }, h('i', { className: 'pd-legenda-marca pd-tom-ok' }), 'Protegido'), h('strong', { className: 'pd-num' }, 'R$ 2.100')),
            h('div', { className: 'pd-legenda-item' }, h('span', { className: 'pd-apoio' }, h('i', { className: 'pd-legenda-marca pd-tom-vaso' }), 'Folga real'), h('strong', { className: 'pd-num' }, 'R$ 750'))),
          h('p', { className: 'pd-apoio' }, 'As parcelas de hoje somam cerca de R$ 1.110, mais do que a folga. O plano começa pela ordem certa.')),
        h(Cartao, { sobre: 'Saúde financeira' },
          h('div', { className: 'pd-linha' }, h('p', { className: 'pd-valor-lg' }, '31 de 100'), h(Selo, { tom: 'fonte', icone: 'check' }, 'Calculado')),
          h(Trilho, { total: 100, partes: [{ valor: 31, tom: 'acao' }], rotulo: 'Score de 31 em 100' }),
          h('ul', { className: 'pd-lista' }, [['Renda comprometida', 'Alta'], ['Custo médio das dívidas', 'Alto'], ['Reserva', 'Ainda não há'], ['Dias sem apostas', 'Não se aplica']].map(function (f) { return h('li', { key: f[0] }, h('span', { className: 'pd-lista-texto' }, f[0]), h('strong', null, f[1])); })),
          h(Botao, { variante: 'fantasma' }, 'Corrigir uma categoria')),
        h(LinkCartao, { icone: 'alvo', titulo: 'Metas e previsão', descricao: 'Próximos 30, 60 e 90 dias' })),
      h(NavBase, { ativo: 'inicio' }));
  }

  function TelaDividas() {
    var m = useState('Avalanche');
    return h(Aparelho, { topo: 'mito' },
      h(CabecalhoMito, { titulo: 'Suas dívidas', acao: h(BotaoIcone, { icone: 'info', tom: 'mito', rotulo: 'Como calculamos' }) },
        h('div', { className: 'pd-linha' }, h('div', null, h('p', { className: 'pd-valor-xl' }, 'R$ 10.360'), h('p', { className: 'pd-mito-sub' }, 'Total em 3 dívidas · R$ 750 de folga')),
          h('div', { style: { width: 132 } }, h(DegrausProgresso, { passos: 5, atual: 3 })))),
      h('div', { className: 'pd-corpo' },
        h('p', { style: { fontWeight: 700 } }, 'Etapa 3 de 5: conta de luz em dia'),
        h(Segmento, { rotulo: 'Método de priorização', opcoes: ['Avalanche', 'Bola de Neve'], valor: m[0], onChange: m[1] }),
        h('p', { className: 'pd-apoio' }, m[0] === 'Avalanche' ? 'Avalanche começa pelo maior custo total (CET).' : 'Bola de Neve começa pelo menor saldo.', ' Nos seus dados, os dois métodos chegam à mesma ordem.'),
        h(LinhaDivida, { protegida: true, nome: 'Mínimo existencial', valor: 'R$ 2.100' }, h('div', null, h(Selo, { tom: 'ok', icone: 'escudo' }, 'Intocável')), h('p', { className: 'pd-apoio' }, 'Fica fora de qualquer plano (Lei 14.181/2021).')),
        h(LinhaDivida, { ordem: 1, nome: 'Conta de luz', valor: 'R$ 360' }, h('div', null, h(Selo, { tom: 'alerta' }, 'Risco de corte')), h('p', { className: 'pd-apoio' }, 'Serviço essencial. 2 faturas, 45 dias em atraso.')),
        h(LinhaDivida, { ordem: 2, nome: 'Cartão · Banco A', valor: 'R$ 4.200' },
          h('p', null, h('strong', { className: 'pd-num' }, 'R$ 342,18 por mês'), ' só de juros e IOF.'),
          h('div', { className: 'pd-linha' }, h('span', { className: 'pd-apoio pd-num' }, 'CET 448,0% a.a. · média BCB 435,9% a.a.'), h(SeloCalculado)),
          h('div', null, h(Selo, { tom: 'neutro', icone: 'lupa' }, 'Conferir teto de 100%')), h('p', { className: 'pd-apoio' }, 'Lei 14.690/2023. São 7 meses no rotativo.')),
        h(LinhaDivida, { ordem: 3, nome: 'Empréstimo · Financeira B', valor: 'R$ 5.800' },
          h('p', null, h('strong', { className: 'pd-num' }, 'R$ 480 por mês'), ' em 18 parcelas.'), h('span', { className: 'pd-apoio pd-num' }, 'CET 112,0% a.a.')),
        h(Cartao, { sobre: 'Quando o banco não aceita', titulo: 'Dossiê de repactuação' },
          h('p', null, 'Reúne credores, mínimo existencial e proposta para levar ao Procon, à Defensoria ou ao CEJUSC. O plano pode ir até 5 anos.'),
          h(Botao, { variante: 'secundario', bloco: true, icone: 'documento' }, 'Gerar dossiê em PDF'))),
      h(NavBase, { ativo: 'dividas' }));
  }

  function TelaElpis(p) {
    var modo = p.modo || 'citacao';
    if (modo === 'voz') return h(Aparelho, null, h(CabecalhoElpis, { nota: 'Ouvindo · 0:12' }),
      h('div', { className: 'pd-voz' },
        h('h1', { className: 'pd-pergunta-titulo', style: { padding: 0 } }, 'Pode falar, Carla. Estou ouvindo.'),
        h(Elpis, { tamanho: 248, estado: 'ouvindo' }),
        h('p', { className: 'pd-apoio' }, 'Toque de novo para terminar. Você também pode enviar uma foto.'),
        h(BotaoVoz, { ativo: true })),
      h(NavBase, { ativo: 'elpis' }));
    if (modo === 'limites') return h(Aparelho, null, h(CabecalhoElpis, null),
      h('div', { className: 'pd-corpo pd-conversa' },
        h(Balao, { autor: 'voce' }, 'Qual ação ou CDB devo comprar com meus R$ 1.500?'),
        h(Balao, null, h('div', null, h(Selo, { tom: 'neutro', icone: 'info' }, 'Recusa educativa')),
          h('p', null, 'Não recomendo ações, fundos ou títulos específicos. Isso é consultoria regulada pela CVM. Posso te ensinar a avaliar qualquer opção para a reserva:'),
          h('ul', { className: 'pd-lista' }, [['Liquidez diária', 'resgatar no mesmo dia.'], ['Baixo risco de crédito', 'Tesouro Nacional ou FGC.'], ['Pós-fixado', 'acompanha a Selic ou o CDI.']].map(function (c) { return h('li', { key: c[0] }, h(Icone, { nome: 'check', tamanho: 20 }), h('span', { className: 'pd-lista-texto' }, h('strong', null, c[0] + ':'), ' ', c[1])); })),
          h(CitacaoCartao, { norma: 'Resoluções CVM 19 e 20/2021', href: 'https://www.gov.br/investidor/', rotuloLink: 'Portal do Investidor' })),
        h(Friso, { tipo: 'onda', curto: true }),
        h(Balao, { autor: 'voce' }, 'O banco pode cobrar essa tarifa nova da minha conta?'),
        h(Balao, null, h('div', null, h(Selo, { tom: 'neutro', icone: 'lupa' }, 'Sem fonte suficiente')),
          h('p', null, 'Não encontrei uma fonte oficial que responda isso com segurança, e prefiro não adivinhar.'),
          h('p', null, 'Se mandar uma foto do extrato com a tarifa, procuro de novo. O Procon também pode orientar você.'),
          h(Botao, { variante: 'secundario', icone: 'camera' }, 'Enviar foto'))),
      h('div', { className: 'pd-chat-rodape' }, h(CampoPergunta, { placeholder: 'Pergunte à Elpis' })),
      h(NavBase, { ativo: 'elpis' }));
    return h(Aparelho, null, h(CabecalhoElpis, null),
      h('div', { className: 'pd-corpo pd-conversa' },
        h(Balao, { autor: 'voce' }, 'Podem bloquear meu salário por causa do cartão?'),
        h(Balao, null,
          h('p', null, h('strong', null, 'Não.'), ' O salário é impenhorável para dívidas de cartão e de empréstimo. O que um cobrador diz por telefone não muda essa regra.'),
          h(CitacaoCartao, { norma: 'Código de Processo Civil, art. 833, IV', href: 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm', rotuloLink: 'Ler no Planalto' }, 'Consultei 3 trechos em fontes oficiais.')),
        h(Friso, { tipo: 'onda', curto: true }),
        h(Balao, { autor: 'voce' }, 'Então o que eu resolvo primeiro?'),
        h(Balao, null,
          h('p', null, 'Primeiro a comida e a casa das crianças. Depois a luz, para não haver corte. O que sobra vai para o cartão.'),
          h(BlocoCalculado, { linhas: [['1º Mínimo existencial', 'R$ 2.100'], ['2º Conta de luz', 'R$ 360'], ['Folga por mês', 'R$ 750']] })),
        h('div', { className: 'pd-sugestoes' }, h('button', { type: 'button', className: 'pd-sugestao' }, 'O que é repactuação?'), h('button', { type: 'button', className: 'pd-sugestao' }, 'Ver meu plano'))),
      h('div', { className: 'pd-chat-rodape' }, h(CampoPergunta, { placeholder: 'Pergunte à Elpis' })),
      h(NavBase, { ativo: 'elpis' }));
  }

  function TelaTrilha(p) {
    var r = useState(p.resposta === undefined ? 'b' : p.resposta);
    if (p.modo === 'licao') {
      var respondeu = !!r[0], certo = r[0] === 'b';
      var ops = [['a', 'Fica parado até a próxima fatura'], ['b', 'Entra no rotativo e continua gerando juros'], ['c', 'O banco cancela depois de 3 meses']];
      return h(Aparelho, null, h('div', { className: 'pd-pergunta-tela' }, h(Progresso, { passo: 2, total: 4, pular: false }),
        h('div', { className: 'pd-linha', style: { justifyContent: 'flex-start' } }, h(Brasao, { emblema: 'espiral', estado: 'atual', tamanho: 44 }), h('p', { className: 'pd-apoio', style: { fontWeight: 700 } }, 'Etapa 3 · Rotativo')),
        h('h1', { className: 'pd-cartao-titulo', style: { fontSize: 24, lineHeight: '30px' } }, 'Você pagou só o mínimo da fatura. O que acontece com o restante?'),
        ops.map(function (o) { return h(QuizOpcao, { key: o[0], letra: o[0].toUpperCase(), estado: !respondeu ? 'neutra' : o[0] === 'b' ? 'certa' : o[0] === r[0] ? 'revisar' : 'neutra', onClick: function () { r[1](o[0]); } }, o[1]); }),
        respondeu ? h(Cartao, { tom: certo ? 'ok' : 'apoio', titulo: certo ? 'Isso mesmo' : 'Vale rever este ponto' },
          h('p', null, 'O restante entra no rotativo. Na sua fatura, isso custou ', h('strong', { className: 'pd-num' }, 'R$ 342,18'), ' em um mês. Por lei, juros e encargos do rotativo não podem passar de 100% da dívida original.'),
          h('div', null, h(Selo, { tom: 'fonte' }, 'Lei 14.690/2023'))) : null,
        h('div', { className: 'pd-empurra' }), h(Botao, { bloco: true, seta: true, desativado: !respondeu }, 'Seguir')));
    }
    return h(Aparelho, { topo: 'mito' },
      h(CabecalhoMito, { titulo: 'Da caixa à esperança' }, h('p', { className: 'pd-mito-sub' }, '2 de 6 etapas concluídas · sem prazo, no seu ritmo')),
      h('div', { className: 'pd-corpo' }, h(TrilhaCaminho),
        h(Cartao, { sobre: 'Etapa 3 · cerca de 4 minutos', titulo: 'O rotativo e o teto de 100%' },
          h('p', null, 'Usa os números da sua fatura. Você pode refazer qualquer lição quando quiser.'),
          h('div', null, h(Selo, { tom: 'fonte' }, 'Banco Central do Brasil')),
          h(Botao, { bloco: true, seta: true }, 'Continuar lição')),
        h(Cartao, { tom: 'apoio', marco: true, sobre: 'Próximo marco', titulo: 'Conheço meus direitos' },
          h('p', null, 'Chega com a etapa 4, Repactuação. Fica com você depois de conquistado.'))),
      h(NavBase, { ativo: 'trilha' }));
  }

  function TelaGuardiao(p) {
    var inicial = p.modo === 'apostas' ? 'Apostas' : 'Golpes', aba = useState(inicial);
    var cabeca = h(CabecalhoMito, { titulo: 'Guardião' }, h('p', { className: 'pd-mito-sub' }, 'Confere antes de você decidir.'));
    var abas = h(Segmento, { rotulo: 'Área do Guardião', opcoes: ['Golpes', 'Apostas'], valor: aba[0], onChange: aba[1] });
    if (aba[0] === 'Apostas') return h(Aparelho, { topo: 'mito' }, cabeca, h('div', { className: 'pd-corpo' }, abas,
      h(Cartao, { sobre: 'Resultado real em outubro · Diego' },
        h('p', { className: 'pd-valor-xl' }, '− R$ 1.170'),
        h('ul', { className: 'pd-lista' }, [['Enviado para apostas', 'R$ 1.450'], ['Prêmios recebidos', 'R$ 280']].map(function (l) { return h('li', { key: l[0] }, h('span', { className: 'pd-lista-texto' }, l[0]), h('strong', { className: 'pd-num' }, l[1])); })),
        h('div', null, h(SeloCalculado))),
      h(Insight, null, h('strong', { className: 'pd-num' }, '82%'), ' disso aconteceu nas quartas depois do repasse e entre 23h e 03h. Saber o horário já ajuda a se preparar.'),
      h(Cartao, { titulo: 'Travas que você escolhe' },
        h(Alternador, { titulo: 'Pausa noturna', descricao: '23h às 03h. Para desligar, há 48h de espera.', ligado: true }),
        h(Alternador, { titulo: 'Aviso na quarta', descricao: 'Lembrete logo após o repasse.' }),
        h('p', { className: 'pd-apoio' }, 'O PANDORA avisa e cria espera. O bloqueio é feito no banco ou na plataforma.')),
      h(LinkCartao, { icone: 'pausa', titulo: 'Autoexclusão nas plataformas', descricao: 'Guia passo a passo para sites .bet.br' }),
      h(LinkCartao, { icone: 'coracao', titulo: 'Precisa de apoio agora?', descricao: 'CVV, CAPS AD e Jogadores Anônimos' })),
      h(NavBase, { ativo: 'guardiao' }));
    return h(Aparelho, { topo: 'mito' }, cabeca, h('div', { className: 'pd-corpo' }, abas,
      h(Botao, { bloco: true, icone: 'camera' }, 'Verificar boleto ou print'),
      h(Cartao, { tom: 'alerta', titulo: 'Não pague este boleto' },
        h('p', null, '“Quitação com 70% de desconto”, recebido por WhatsApp. ', h('strong', { className: 'pd-num' }, 'R$ 1.198,00'), '.'),
        h('ul', { className: 'pd-lista' }, [['check', 'Linha digitável', 'Lida e conferida'], ['x', 'Banco do boleto', 'Diferente do banco credor'], ['x', 'Quem recebe', 'Conta de pessoa física']].map(function (l) { return h('li', { key: l[1] }, h(Disco, { tom: l[0] === 'check' ? 'ok' : 'alerta', icone: l[0], tamanho: 'pequeno' }), h('span', { className: 'pd-lista-texto' }, h('strong', null, l[1]), h('br'), l[2])); })),
        h(Botao, { variante: 'secundario', bloco: true, icone: 'pessoas' }, 'Avisar pessoa de confiança')),
      h(Cartao, { titulo: 'Já fez o Pix?' },
        h('p', null, 'Dá para pedir a devolução pelo MED em até 80 dias.'),
        h('ol', { className: 'pd-lista' }, [['1', 'Acione o MED no seu banco', 'Quanto antes, melhor.'], ['2', 'Use os dados prontos', 'ID da transação, data, hora e valor.'], ['3', 'Registre a ocorrência', 'Boletim e registro no Banco Central.']].map(function (l) { return h('li', { key: l[0] }, h('span', { className: 'pd-divida-ordem', style: { width: 28, height: 28, fontSize: 14 } }, l[0]), h('span', { className: 'pd-lista-texto' }, h('strong', null, l[1]), h('br'), h('span', { className: 'pd-apoio' }, l[2]))); })),
        h(Botao, { variante: 'secundario', bloco: true, icone: 'copiar' }, 'Copiar dados do Pix'),
        h('div', null, h(Selo, { tom: 'fonte' }, 'Res. BCB 147/2021')))),
      h(NavBase, { ativo: 'guardiao' }));
  }

  function TelaGuardiaoAmpliada() {
    return h(Aparelho, null, h('div', { className: 'pd-ampliado pd-acessivel pd-contido' },
      h('div', { className: 'pd-ampliado-veredito' },
        h('span', { role: 'img', 'aria-label': 'Alerta' }, h(Disco, { tom: 'alerta', icone: 'alerta', tamanho: 'grande' })),
        h('h1', { className: 'pd-ampliado-titulo' }, 'PARE!'),
        h('p', { style: { fontWeight: 700 } }, 'Sr. Antônio, não pague este boleto.')),
      h('p', null, 'Ele tem o desenho do banco, mas o dinheiro vai para a conta de uma pessoa desconhecida.'),
      h('p', null, 'Nenhum banco pede Pix para liberar valores do INSS.'),
      h('div', { className: 'pd-empurra' }),
      h(Botao, { bloco: true, ampliado: true, icone: 'som' }, 'Ouvir de novo'),
      h(Botao, { bloco: true, ampliado: true, variante: 'secundario', icone: 'pessoas' }, 'Avisar meu filho'),
      h(Botao, { bloco: true, ampliado: true, variante: 'secundario', icone: 'microfone' }, 'Falar com Elpis')));
  }

  function TelaMetas() {
    var degraus = [['15 dias', 'R$ 1.400', 1], ['1 mês', 'R$ 2.800', 1500 / 2800], ['3 meses', 'R$ 8.400', 0], ['6 meses', 'R$ 16.800', 0]];
    return h(Aparelho, { topo: 'mito' },
      h(CabecalhoMito, { titulo: 'Metas e previsão', voltar: true }, h('p', { className: 'pd-mito-sub', style: { fontWeight: 700 } }, 'Reserva de emergência · Júlia'),
        h('p', { className: 'pd-valor-xl' }, 'R$ 1.500'), h('p', { className: 'pd-mito-sub' }, 'de R$ 16.800, ou 6 meses do seu custo essencial')),
      h('div', { className: 'pd-corpo' },
        h(Cartao, { titulo: 'Degraus da reserva' },
          h('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 4, textAlign: 'center' } }, degraus.map(function (d) {
            return h('div', { key: d[0], style: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 } }, h(Anfora, { nivel: d[2], altura: 84, rotulo: d[0] + ': ' + Math.round(d[2] * 100) + '% cheia' }), h('strong', { style: { fontSize: 14, lineHeight: '18px' } }, d[0]), h('span', { className: 'pd-apoio pd-num' }, d[1]));
          })),
          h('p', { className: 'pd-apoio' }, 'O primeiro degrau está completo. Faltam R$ 1.300 para 1 mês: com R$ 500 por mês, 3 meses.')),
        h(Cartao, { titulo: 'Próximos 90 dias' },
          h('div', null, h(Selo, { tom: 'ok' }, 'Sem furo de caixa previsto')),
          h('ul', { className: 'pd-lista' }, [['30 dias', 'R$ 1.200'], ['60 dias', 'R$ 2.400'], ['90 dias', 'R$ 3.600']].map(function (l) { return h('li', { key: l[0] }, h('span', { className: 'pd-lista-texto' }, l[0]), h('strong', { className: 'pd-num' }, l[1])); })),
          h('p', { className: 'pd-apoio' }, 'Sobra estimada depois dos essenciais e da reserva, se o mês se repetir.')),
        h(Cartao, { titulo: 'Simular R$ 500 por mês' },
          h('div', { className: 'pd-legenda' }, h('div', { className: 'pd-legenda-item' }, h('span', { className: 'pd-apoio' }, 'Em 1 ano'), h('strong', { className: 'pd-valor-lg' }, 'R$ 6.000')), h('div', { className: 'pd-legenda-item' }, h('span', { className: 'pd-apoio' }, 'Em 2 anos'), h('strong', { className: 'pd-valor-lg' }, 'R$ 12.000'))),
          h('p', { className: 'pd-apoio' }, 'Valor guardado, antes do rendimento.'),
          h('ul', { className: 'pd-lista' }, [['Títulos públicos Selic', 'Garantia do Tesouro Nacional'], ['Renda fixa 100% CDI', 'Cobertura do FGC até R$ 250 mil'], ['Poupança', 'Referência de comparação']].map(function (l) { return h('li', { key: l[0] }, h('span', { className: 'pd-lista-texto' }, h('strong', null, l[0]), h('br'), h('span', { className: 'pd-apoio' }, l[1]))); })),
          h(Botao, { variante: 'secundario', bloco: true, seta: true }, 'Comparar com as séries do BCB'),
          h('p', { className: 'pd-apoio' }, 'Conteúdo educativo sobre classes gerais. Não é recomendação de investimento.'))),
      h(NavBase, { ativo: 'inicio' }));
  }

  function TelaCrise() {
    return h(Aparelho, null, h('div', { className: 'pd-crise pd-acessivel pd-sem-ornamento' },
      h(Elpis, { tamanho: 120 }),
      h('h1', { className: 'pd-crise-titulo' }, 'Agora o dinheiro pode esperar.'),
      h('p', null, 'Parece que este momento está pesado. Pausei metas e avisos. Falar com alguém pode ajudar, e é de graça.'),
      h(Botao, { bloco: true, icone: 'telefone' }, 'Ligar para o CVV: 188'),
      h(Botao, { bloco: true, variante: 'secundario', icone: 'lupa' }, 'Encontrar um CAPS AD'),
      h(Botao, { bloco: true, variante: 'secundario', icone: 'pessoas' }, 'Jogadores Anônimos'),
      h('p', { className: 'pd-apoio' }, 'Elpis não substitui um profissional de saúde.'),
      h('div', { className: 'pd-empurra' }),
      h(Botao, { bloco: true, variante: 'fantasma' }, 'Voltar quando eu quiser')));
  }

  var TELAS = [
    ['1a', 'Abertura', function () { return h(TelaAbertura, { passo: 0 }); }],
    ['1b', 'Abertura: como se sente', function () { return h(TelaAbertura, { passo: 1 }); }],
    ['1c', 'Abertura: o que pesa', function () { return h(TelaAbertura, { passo: 2 }); }],
    ['1d', 'Abertura: como começar', function () { return h(TelaAbertura, { passo: 3 }); }],
    ['2', 'Início (Raio-X)', function () { return h(TelaInicio); }],
    ['3', 'Dívidas', function () { return h(TelaDividas); }],
    ['4a', 'Elpis: resposta com fonte', function () { return h(TelaElpis, { modo: 'citacao' }); }],
    ['4b', 'Elpis: limites', function () { return h(TelaElpis, { modo: 'limites' }); }],
    ['4c', 'Elpis: voz', function () { return h(TelaElpis, { modo: 'voz' }); }],
    ['5a', 'Trilha', function () { return h(TelaTrilha); }],
    ['5b', 'Trilha: lição', function () { return h(TelaTrilha, { modo: 'licao' }); }],
    ['6a', 'Guardião: golpes', function () { return h(TelaGuardiao, { modo: 'golpes' }); }],
    ['6b', 'Guardião: apostas', function () { return h(TelaGuardiao, { modo: 'apostas' }); }],
    ['7', 'Metas e previsão', function () { return h(TelaMetas); }],
    ['E1', 'Estado: fluxo de crise', function () { return h(TelaCrise); }],
    ['E2', 'Estado: leitura ampliada', function () { return h(TelaGuardiaoAmpliada); }]
  ];
  /* Uma tela do mapa pelo id, para páginas que ocupam a janela inteira (envolva em .pd-fluido). */
  function Tela(p) {
    var t = TELAS.filter(function (x) { return x[0] === p.id; })[0];
    return t ? t[2]() : null;
  }
  function Galeria(p) {
    var lista = p.ids ? TELAS.filter(function (t) { return p.ids.indexOf(t[0]) >= 0; }) : TELAS;
    return h('div', { className: 'pd-galeria' }, lista.map(function (t) {
      return h('figure', { key: t[0], className: 'pd-galeria-item', style: { margin: 0 } },
        h('figcaption', { className: 'pd-galeria-rotulo' }, h('span', { className: 'pd-galeria-num' }, t[0] + ' · '), t[1]), t[2]());
    }));
  }

  window.Pandora = {
    Icone: Icone, Disco: Disco, Friso: Friso, Meandro: Meandro, Serra: Serra, CaixaMarca: CaixaMarca, Elpis: Elpis, Brasao: Brasao, Anfora: Anfora,
    Botao: Botao, BotaoIcone: BotaoIcone, BotaoVoz: BotaoVoz, Selo: Selo, SeloCalculado: SeloCalculado,
    Cartao: Cartao, Trilho: Trilho, Insight: Insight, LinkCartao: LinkCartao, CampoPergunta: CampoPergunta,
    Progresso: Progresso, OpcaoCartao: OpcaoCartao, EscalaSentimento: EscalaSentimento, Consentimento: Consentimento, Segmento: Segmento, Alternador: Alternador,
    LinhaDivida: LinhaDivida, DegrausProgresso: DegrausProgresso,
    Balao: Balao, CitacaoCartao: CitacaoCartao, BlocoCalculado: BlocoCalculado, CabecalhoElpis: CabecalhoElpis,
    TrilhaCaminho: TrilhaCaminho, QuizOpcao: QuizOpcao,
    Aparelho: Aparelho, Tela: Tela, Rolagem: Rolagem, CabecalhoMito: CabecalhoMito, NavBase: NavBase,
    TelaAbertura: TelaAbertura, TelaInicio: TelaInicio, TelaDividas: TelaDividas, TelaElpis: TelaElpis, TelaTrilha: TelaTrilha, TelaGuardiao: TelaGuardiao, TelaGuardiaoAmpliada: TelaGuardiaoAmpliada, TelaMetas: TelaMetas, TelaCrise: TelaCrise, Galeria: Galeria
  };
})();
