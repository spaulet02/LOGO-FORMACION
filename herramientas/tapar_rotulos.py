"""Tapa en las imágenes los rótulos marcados en trabajo/imagenes_revision/*.json.

Cada caja se rellena con el color dominante de su borde (el fondo local), de modo que el
rótulo desaparece sin dejar un parche visible. Resultado en trabajo/img_manual/…
"""
import glob
import json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent


def color_fondo(im, caja):
    x0, y0, x1, y1 = caja
    px = []
    for x in range(max(0, x0 - 3), min(im.width, x1 + 3)):
        for y in (max(0, y0 - 3), min(im.height - 1, y1 + 2)):
            px.append(im.getpixel((x, y)))
    for y in range(max(0, y0 - 3), min(im.height, y1 + 3)):
        for x in (max(0, x0 - 3), min(im.width - 1, x1 + 2)):
            px.append(im.getpixel((x, y)))
    return Counter(px).most_common(1)[0][0] if px else (255, 255, 255)


def main():
    marcas = []
    for f in sorted(glob.glob(str(RAIZ / "trabajo" / "imagenes_revision" / "*.json"))):
        marcas += [m for m in json.load(open(f, encoding="utf-8")) if m.get("accion") == "tapar"]
    por_img = {}
    for m in marcas:
        por_img.setdefault(m["file"], []).extend(m["cajas"])
    for rel, cajas in por_img.items():
        im = Image.open(RAIZ / rel).convert("RGB")
        d = ImageDraw.Draw(im)
        for c in cajas:
            c = [int(round(v)) for v in c]
            d.rectangle(c, fill=color_fondo(im, c))
        dst = RAIZ / rel.replace("trabajo/img/", "trabajo/img_manual/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, optimize=True)
    print(f"{len(por_img)} imágenes retocadas, {sum(len(c) for c in por_img.values())} rótulos tapados")


if __name__ == "__main__":
    main()
