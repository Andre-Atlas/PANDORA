"""Vetoriza a cena da Pandora em camadas: fundo, textura, tinta (preto) e fumaça (creme)."""
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import vtracer

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
OUT.mkdir(parents=True, exist_ok=True)

CORES = {
    "laranja": ("--cena-fundo", "#ec7333"),
    "textura": ("--cena-textura", "#d9612a"),
    "tinta": ("--cena-tinta", "#1a0d12"),
    "creme": ("--cena-fumaca", "#fbe3d1"),
}

im = cv2.imread(str(SRC))
im = cv2.bilateralFilter(im, 7, 40, 7)
h, w = im.shape[:2]
if ESCALA != 1:
    im = cv2.resize(im, None, fx=ESCALA, fy=ESCALA, interpolation=cv2.INTER_CUBIC)
H, W = im.shape[:2]
rgb = im[..., ::-1].astype(np.float32)
cent = np.array([(236, 115, 51), (26, 13, 18), (251, 227, 209)], np.float32)
d = ((rgb[None] - cent[:, None, None]) ** 2).sum(-1)
cls = d.argmin(0)


def limpar(m, k=3):
    m = m.astype(np.uint8) * 255
    m = cv2.medianBlur(m, k)
    return m


tinta = limpar(cls == 1, 3)
creme = limpar(cls == 2, 3)
L = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)[..., 0].astype(np.float32)
Lb = cv2.GaussianBlur(L, (0, 0), 3 * ESCALA)
# longe das bordas: o escurecimento do antialiasing não é textura
perto = cv2.dilate(((cls != 0).astype(np.uint8)) * 255, np.ones((int(15 * ESCALA),) * 2, np.uint8))
textura = ((cls == 0) & (Lb < 155) & (perto == 0)).astype(np.uint8) * 255
textura = cv2.morphologyEx(textura, cv2.MORPH_OPEN, np.ones((int(3 * ESCALA),) * 2, np.uint8))
textura = cv2.medianBlur(textura, 7)


def tracar(nome, mask, speckle):
    png = OUT / f"_{nome}.png"
    # vtracer binary: preto = forma
    cv2.imwrite(str(png), 255 - mask)
    svg = OUT / f"_{nome}.svg"
    vtracer.convert_image_to_svg_py(
        str(png), str(svg), colormode="binary", mode="spline",
        filter_speckle=speckle, corner_threshold=60, length_threshold=4.0,
        splice_threshold=45, path_precision=1,
    )
    txt = svg.read_text()
    paths = re.findall(r"<path[^>]*?d=\"([^\"]+)\"[^>]*?transform=\"translate\(([-\d.]+),([-\d.]+)\)\"", txt)
    if not paths:
        paths = [(dd, "0", "0") for dd in re.findall(r"<path[^>]*?d=\"([^\"]+)\"", txt)]
    return paths


s = 1 / ESCALA
camadas = []
for nome, mask, speck in (("textura", textura, int(20 * ESCALA)), ("tinta", tinta, int(2 * ESCALA)), ("creme", creme, int(3 * ESCALA))):
    ps = tracar(nome, mask, speck)
    var, cor = CORES[nome]
    corpo = "".join(
        f'<path d="{dd}" transform="translate({tx},{ty})"/>' if (tx, ty) != ("0", "0") else f'<path d="{dd}"/>'
        for dd, tx, ty in ps
    )
    gid = {"textura": "textura", "tinta": "tinta", "creme": "fumaca"}[nome]
    camadas.append(f'<g id="{gid}" fill="var({var}, {cor})" fill-rule="evenodd">{corpo}</g>')
    print(nome, len(ps), "paths")

var, cor = CORES["laranja"]
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
    f'aria-labelledby="t"><title id="t">Pandora abre a caixa entre duas colunas</title>'
    f'<rect id="fundo" width="{w}" height="{h}" fill="var({var}, {cor})"/>'
    f'<g transform="scale({s})">{"".join(camadas)}</g></svg>'
)
(OUT / "pandora-cena.raw.svg").write_text(svg)
print("bytes", len(svg))
