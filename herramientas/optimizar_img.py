"""Reduce las imágenes a 1500 px de ancho como máximo (≈ 230 ppp a ancho de caja) y las optimiza."""
import glob
from pathlib import Path
from PIL import Image
for f in glob.glob("trabajo/img/b*/*.png"):
    dst = Path(f.replace("trabajo/img/", "trabajo/img_opt/"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(f)
    if im.width > 1500:
        im = im.resize((1500, round(im.height * 1500 / im.width)), Image.LANCZOS)
    if im.mode == "RGBA" and im.getextrema()[3][0] == 255:
        im = im.convert("RGB")
    im.save(dst, optimize=True)
