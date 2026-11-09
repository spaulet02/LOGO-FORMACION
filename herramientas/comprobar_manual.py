"""Comprobaciones editoriales del manual: figuras/tablas no citadas, remisiones rotas,
numeración, rutas de imagen, restos de prácticas o de notas de trabajo."""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TRABAJO = re.compile(r"pr[aá]ctica|(?<!la )(?<!está )(?<!Aviso )(?<!aviso )pendiente(?! de (la recta|AQ|rearme|reconocer|acuse|OK))|F01|propuesta del libro|Python|ITECAM decid|previst[oa]|†", re.I)
problemas = 0
caps = {}
for f in sorted((RAIZ / "condensado").glob("*.md")):
    t = f.read_text(encoding="utf-8")
    caps[f.stem] = t
titulos = {m.group(1) for t in caps.values() for m in re.finditer(r"^#{1,3} ((?:\d+|[A-Z])(?:\.\d+)*)[. ]", t, re.M)}
for nombre, t in caps.items():
    n = re.search(r"^# (?:Anexo )?(\w+)", t, re.M).group(1).rstrip(".")
    for tipo, patron in (("Figura", r"!\[Figura ([\dA-Z]+\.\d+)\."), ("Tabla", r"^: Tabla ([\dA-Z]+\.\d+)\.")):
        nums = re.findall(patron, t, re.M)
        esperado = [f"{n}.{i}" for i in range(1, len(nums) + 1)]
        if nums != esperado:
            print(f"{nombre}: numeración de {tipo.lower()}s {nums}"); problemas += 1
        cuerpo = re.sub(patron.replace("^", ""), "", t)
        for x in nums:
            if not re.search(rf"{tipo.lower()}s? (?:[\dA-Z.]+(?:,| y| e| o) )*{re.escape(x)}\b", cuerpo, re.I):
                print(f"{nombre}: {tipo} {x} no se cita en el texto"); problemas += 1
    for m in re.finditer(r"\((?:apartado|capítulo) ([\dA-Z]+(?:\.\d+)*)\)", t):
        if m.group(1) not in titulos and not m.group(1).isdigit():
            print(f"{nombre}: remisión rota «{m.group(0)}»"); problemas += 1
    for m in re.finditer(r"\]\(([^)]+\.png)\)", t):
        if not (RAIZ / m.group(1)).exists():
            print(f"{nombre}: no existe {m.group(1)}"); problemas += 1
    for i, linea in enumerate(t.split("\n"), 1):
        if TRABAJO.search(linea) and not linea.startswith("!["):
            print(f"{nombre}:{i}: posible nota de trabajo: {linea.strip()[:110]}"); problemas += 1
print("Problemas:", problemas)
sys.exit(0)
