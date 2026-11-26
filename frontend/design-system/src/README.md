Código-fonte do design system.

```bash
node src/build.js
node src/teste.js
```

- `build.js` gera `components/bundle.js`, `components/bundle.css`, `components/index.d.ts`, `tokens.css` e os SVGs de `assets/`.
- `teste.js` monta páginas locais em `teste/` (ou na pasta de `--saida <pasta>`) e confere o contraste dos pares de tokens. `tela.html?id=2&tema=dark` abre uma tela na janela inteira, e `responsivo.html` mostra a mesma tela em seis tamanhos.
- `ornamentos.js` guarda os motivos gregos, e `emblemas.js`, os emblemas dos brasões.
- `elpis.d` é o traçado da figura de Elpis. Não edite à mão.
