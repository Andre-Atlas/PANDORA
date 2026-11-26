import re, sys, resvg_py
from pathlib import Path
src, out, w = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
t = re.sub(r'var\(--[\w-]+,\s*(#[0-9a-fA-F]+)\)', r'\1', src.read_text())
png = resvg_py.svg_to_bytes(svg_string=t, width=w, height=w)
Path(out).write_bytes(bytes(png))
