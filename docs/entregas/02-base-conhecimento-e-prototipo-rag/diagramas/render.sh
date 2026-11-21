#!/bin/sh
# Renderiza os .mmd em SVG e PNG (mermaid 11.4.0 via jsDelivr + Chrome headless; precisa de internet).
# Uso: sh render.sh   (dentro desta pasta)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in arquitetura pipeline-ingestao; do
  T=$(mktemp -d)
  { echo '<html><body style="margin:0;background:#fff"><pre class="mermaid">'; cat "$f.mmd"; echo '</pre>'
    echo '<script type="module">import m from "https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.esm.min.mjs";m.initialize({startOnLoad:true,theme:"neutral"});</script></body></html>'; } > "$T/p.html"
  "$CHROME" --headless=new --disable-gpu --virtual-time-budget=15000 --dump-dom "file://$T/p.html" 2>/dev/null > "$T/dom.html"
  python3 - "$T" "$f" <<'PY'
import re, sys
t, f = sys.argv[1], sys.argv[2]
dom = open(f"{t}/dom.html", encoding="utf-8").read()
svg = re.search(r"<svg.*?</svg>", dom, re.S).group(0)
vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
svg = re.sub(r'style="max-width:[^"]*"', "", svg, count=1)
svg = re.sub(r'<svg ', f'<svg width="{int(vb[2])}" height="{int(vb[3])}" xmlns:xlink="http://www.w3.org/1999/xlink" ', svg, count=1) if 'width=' not in svg.split(">")[0] else svg
open(f"{f}.svg", "w", encoding="utf-8").write(svg)
open(f"{t}/size", "w").write(f"{int(vb[2])+20},{int(vb[3])+20}")
open(f"{t}/v.html", "w", encoding="utf-8").write(f'<html><body style="margin:10px;background:#fff">{svg}</body></html>')
PY
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size="$(cat $T/size)" --screenshot="$PWD/$f.png" "file://$T/v.html" 2>/dev/null
  echo "$f: $(cat $T/size)"
done
