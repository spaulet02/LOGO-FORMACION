"""Genera los fondos decorativos de portada y portadillas (PNG, A4 a 200 ppp).

Solo dibuja elementos gráficos; todo el texto se escribe en Word para que
siga siendo editable. Paleta tomada del logotipo de ITECAM.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

NAVY = (25, 35, 62)
NAVY_2 = (44, 58, 94)      # trazos del patrón sobre el azul
NAVY_3 = (60, 76, 116)
YELLOW = (245, 196, 0)
WHITE = (255, 255, 255)

W, H = 1654, 2339          # A4 a 200 ppp
OUT = Path(__file__).resolve().parent.parent / "assets" / "generados"
FONT = str(Path(__file__).resolve().parent.parent / "assets" / "fuentes" / "Montserrat-Bold.ttf")


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def bloque_funcion(d, x, y, w, h, etiqueta, color, grosor=4):
    """Dibuja un bloque de función (estilo diagrama FUP) con entradas y salida."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, outline=color, width=grosor)
    f = font(int(h * 0.32))
    tw = d.textlength(etiqueta, font=f)
    d.text((x + (w - tw) / 2, y + h * 0.30), etiqueta, font=f, fill=color)
    entradas = []
    for i in range(3):
        yy = y + h * (i + 1) / 4
        d.line([x - 40, yy, x, yy], fill=color, width=grosor)
        entradas.append((x - 40, yy))
    salida = (x + w + 40, y + h / 2)
    d.line([x + w, y + h / 2, *salida], fill=color, width=grosor)
    return entradas, salida


def patron_fup(d, x0, y0, x1, y1, color, color2):
    """Rejilla de bloques AND/OR/RS/temporizador unidos por conexiones ortogonales."""
    etiquetas = ["&", "≥1", "RS", "TON", "&", "=1", "≥1", "CTU", "&", "SF"]
    bw, bh = 170, 150
    cols = [x0 + 120, x0 + 520, x0 + 920, x0 + 1320]
    filas = list(range(int(y0) + 90, int(y1) - bh, 300))
    k = 0
    salidas_prev = []
    for ci, cx in enumerate(cols):
        salidas = []
        for fi, fy in enumerate(filas):
            if (ci + fi) % 3 == 2:
                continue
            c = color if (ci + fi) % 2 == 0 else color2
            ent, sal = bloque_funcion(d, cx, fy, bw, bh, etiquetas[k % len(etiquetas)], c)
            k += 1
            salidas.append(sal)
            if salidas_prev:
                src = salidas_prev[(fi) % len(salidas_prev)]
                dst = ent[1]
                mx = (src[0] + dst[0]) / 2
                d.line([src, (mx, src[1]), (mx, dst[1]), dst], fill=c, width=4)
                d.ellipse([mx - 7, src[1] - 7, mx + 7, src[1] + 7], fill=c)
        salidas_prev = salidas or salidas_prev


def portada():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    band = int(H * 0.56)
    d.rectangle([0, band, W, H], fill=NAVY)
    patron_fup(d, 0, band + 40, W, H - 260, NAVY_2, NAVY_3)
    # filete amarillo y punto (eco del logotipo)
    d.rectangle([0, band - 14, int(W * 0.34), band], fill=YELLOW)
    r = 70
    cx, cy = W - 210, band
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=YELLOW)
    # franja inferior más oscura para los créditos
    d.rectangle([0, H - 230, W, H], fill=(17, 25, 46))
    img.save(OUT / "portada.png", optimize=True)


def portadilla():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    band = int(H * 0.46)
    d.rectangle([0, 0, W, band], fill=NAVY)
    patron_fup(d, 300, 40, W, band - 40, NAVY_2, NAVY_3)
    d.rectangle([0, band, int(W * 0.34), band + 14], fill=YELLOW)
    r = 56
    d.ellipse([W - 200 - r, band - r, W - 200 + r, band + r], fill=YELLOW)
    img.save(OUT / "portadilla.png", optimize=True)


def contraportada():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    patron_fup(d, 0, int(H * 0.55), W, H - 120, NAVY_2, NAVY_3)
    d.rectangle([0, int(H * 0.52), int(W * 0.34), int(H * 0.52) + 14], fill=YELLOW)
    img.save(OUT / "contraportada.png", optimize=True)




# ---------------------------------------------------------------- portada completa (imagen)
def portada_completa(salida=None):
    """Portada final como imagen A4 a 300 ppp: logotipo, título y franja con patrón."""
    import json
    raiz = Path(__file__).resolve().parent.parent
    libro = json.loads((raiz / "libro.json").read_text(encoding="utf-8"))
    FD = raiz / "assets" / "fuentes"
    def mf(estilo, tam):
        return ImageFont.truetype(str(FD / f"Montserrat-{estilo}.ttf"), tam)
    W3, H3 = 2480, 3508
    k = W3 / W
    img = Image.new("RGB", (W3, H3), WHITE)
    d = ImageDraw.Draw(img)
    band = int(H3 * 0.60)
    d.rectangle([0, band, W3, H3], fill=NAVY)
    # patrón FUP escalado
    pat = Image.new("RGB", (W, int((H3 - band) / k)), NAVY)
    patron_fup(ImageDraw.Draw(pat), 0, 40, W, pat.height - 60, NAVY_2, NAVY_3)
    img.paste(pat.resize((W3, H3 - band), Image.LANCZOS), (0, band))
    d.rectangle([0, band - 22, int(W3 * 0.34), band], fill=YELLOW)
    r = 105
    d.ellipse([W3 - 320 - r, band - r, W3 - 320 + r, band + r], fill=YELLOW)
    # logotipo ITECAM (fondo blanco, se coloca sobre blanco)
    logo = Image.open(raiz / "assets" / "logo_itecam.jpg").convert("RGB")
    lw = 640
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    x0 = 300
    img.paste(logo, (x0, 300))
    y = 300 + logo.height + 260
    d.text((x0, y), libro["tipo"].upper(), font=mf("SemiBold", 46), fill=(95, 102, 118), spacing=0)
    y += 110
    d.text((x0, y), "LOGO! 9", font=mf("Bold", 230), fill=NAVY)
    y += 300
    d.text((x0, y), "LOGO!Soft Comfort V9", font=mf("SemiBold", 104), fill=NAVY)
    y += 140
    d.text((x0, y), "y LOGO! TDE 9", font=mf("SemiBold", 104), fill=NAVY)
    y += 190
    d.rectangle([x0, y, x0 + 180, y + 14], fill=YELLOW)
    y += 70
    d.text((x0, y), libro["subtitulo"], font=mf("Regular", 62), fill=(44, 58, 94))
    img.save(salida or (OUT / "portada_completa.png"), optimize=True)


def contraportada_completa():
    import json
    raiz = Path(__file__).resolve().parent.parent
    libro = json.loads((raiz / "libro.json").read_text(encoding="utf-8"))
    FD = raiz / "assets" / "fuentes"
    mf = lambda e, t: ImageFont.truetype(str(FD / f"Montserrat-{e}.ttf"), t)
    W3, H3 = 2480, 3508
    img = Image.new("RGB", (W3, H3), NAVY)
    d = ImageDraw.Draw(img)
    pat = Image.new("RGB", (W, int(H * 0.42)), NAVY)
    patron_fup(ImageDraw.Draw(pat), 0, 40, W, pat.height - 60, NAVY_2, NAVY_3)
    img.paste(pat.resize((W3, int(H3 * 0.42)), Image.LANCZOS), (0, int(H3 * 0.58)))
    x0, y = 300, 420
    d.rectangle([x0, y, x0 + 180, y + 14], fill=YELLOW)
    y += 80
    d.text((x0, y), "LOGO! 9", font=mf("Bold", 150), fill=WHITE)
    y += 200
    d.text((x0, y), "LOGO!Soft Comfort V9 y LOGO! TDE 9", font=mf("SemiBold", 70), fill=WHITE)
    y += 170
    texto = ("Cinco bloques de trabajo en el banco: del primer contacto con el módulo y los "
             "automatismos digitales a las señales analógicas, la pantalla LOGO! TDE 9, las "
             "comunicaciones y los proyectos integrados.")
    f = mf("Regular", 54)
    linea, lineas = "", []
    for p in texto.split():
        prueba = (linea + " " + p).strip()
        if d.textlength(prueba, font=f) > W3 - 2 * x0:
            lineas.append(linea); linea = p
        else:
            linea = prueba
    lineas.append(linea)
    for l in lineas:
        d.text((x0, y), l, font=f, fill=(201, 207, 221)); y += 84
    img.save(OUT / "contraportada_completa.png", optimize=True)


# ---------------------------------------------------------------- manual: banda de capítulo y pestañas
def banda_capitulo():
    """Banda superior de apertura de capítulo: 21 x 8,5 cm a 300 ppp."""
    W3, H3 = 2480, 1004
    img = Image.new("RGB", (W3, H3), NAVY)
    d = ImageDraw.Draw(img)
    # retícula de puntos muy suave, sin bloques: la ilustración del capítulo da el motivo
    for x in range(40, W3, 60):
        for y in range(40, H3 - 40, 60):
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(32, 44, 74))
    d.rectangle([0, H3 - 18, int(W3 * 0.34), H3], fill=YELLOW)
    img.save(OUT / "banda_capitulo.png", optimize=True)


def pestanas():
    """Pestañas de bloque para el borde exterior (izquierda y derecha)."""
    fnt = ImageFont.truetype(FONT, 78)
    for et in ["I", "II", "III", "IV", "V", "A"]:
        for lado in ("izq", "der"):
            w, h = 142, 330
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            r = 34
            if lado == "der":
                d.rounded_rectangle([0, 0, w + r, h], radius=r, fill=NAVY)
                d.rectangle([0, 0, 12, h], fill=YELLOW)
            else:
                d.rounded_rectangle([-r, 0, w, h], radius=r, fill=NAVY)
                d.rectangle([w - 12, 0, w, h], fill=YELLOW)
            tw = d.textlength(et, font=fnt)
            x = (w - tw) / 2 + (6 if lado == "der" else -6)
            d.text((x, h / 2 - 48), et, font=fnt, fill=WHITE)
            img.save(OUT / f"pestana_{et}_{lado}.png", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    portadilla()
    portada_completa()
    contraportada_completa()
    banda_capitulo()
    pestanas()
    print("Gráficos generados en", OUT)


def bandas_por_capitulo():
    """Une la banda azul con la ilustración de cada capítulo en una sola imagen."""
    base = Image.open(OUT / "banda_capitulo.png").convert("RGBA")
    ilus_dir = Path(__file__).resolve().parent.parent / "assets" / "ilustraciones" / "apertura"
    if not ilus_dir.exists():
        return
    W3, H3 = base.size                      # 21 x 8,5 cm a 300 ppp
    ppcm = W3 / 21
    for f in sorted(ilus_dir.glob("cap_*.png")):
        ilus = Image.open(f).convert("RGBA")
        w = int(6.6 * ppcm)
        h = int(ilus.height * w / ilus.width)
        ilus = ilus.resize((w, h), Image.LANCZOS)
        im = base.copy()
        im.alpha_composite(ilus, (int((21 - 1.9 - 6.6) * ppcm), int(1.3 * ppcm)))
        im.convert("RGB").save(OUT / f"banda_{f.stem}.png", optimize=True)


if __name__ == "__main__":
    bandas_por_capitulo()
