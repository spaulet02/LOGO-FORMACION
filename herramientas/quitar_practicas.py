"""Saca los recuadros de práctica del manual y los guarda para el libro de prácticas.

condensado/cap_NN.md  ->  condensado/cap_NN.md (sin prácticas)
                      ->  practicas/cap_NN.md  (las prácticas, con el título del capítulo)
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APERTURA = re.compile(r"^(:{3,})\s*\{?\s*\.?practica\b.*$")
DIV = re.compile(r"^(:{3,})\s*(\S.*)?$")


def procesar(ruta):
    lineas = ruta.read_text(encoding="utf-8").split("\n")
    queda, fuera = [], []
    titulo = next((l for l in lineas if l.startswith("# ")), ruta.stem)
    i = 0
    while i < len(lineas):
        m = APERTURA.match(lineas[i])
        if not m:
            queda.append(lineas[i]); i += 1; continue
        prof = 1
        bloque = [lineas[i]]
        i += 1
        while i < len(lineas) and prof > 0:
            l = lineas[i]
            d = DIV.match(l)
            if d and d.group(2):        # apertura anidada
                prof += 1
            elif d:                     # cierre
                prof -= 1
            bloque.append(l)
            i += 1
        fuera.append("\n".join(bloque))
    if fuera:
        dst = RAIZ / "practicas" / ruta.name
        dst.parent.mkdir(exist_ok=True)
        dst.write_text(titulo + "\n\n" + "\n\n".join(fuera) + "\n", encoding="utf-8")
        texto = re.sub(r"\n{3,}", "\n\n", "\n".join(queda))
        ruta.write_text(texto, encoding="utf-8")
    return len(fuera)


if __name__ == "__main__":
    total = 0
    for r in sorted((RAIZ / "condensado").glob("*.md")):
        n = procesar(r)
        total += n
        if n:
            print(f"{r.name}: {n} práctica(s) movidas a practicas/")
    print("Total:", total)
