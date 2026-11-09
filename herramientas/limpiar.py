"""Limpieza automática de las «zonas de IA» y del material de trabajo.

Retira del libro del alumno, y guarda en informe/retirado/*.json para ITECAM:
  - portadas de bloque de «documento de trabajo» (todo lo anterior al primer título 1)
  - secciones «Registro de verificación» y «Correcciones tras la auditoría»
  - párrafos sueltos «Correcciones tras la auditoría…» / «Revisión del auditor…»
  - etiquetas de procedencia al final de los pies ([ilustración propia], [recorte documental…])
Además clasifica cada recuadro por su título y genera vistas por capítulo
(trabajo/vista/cap_XX.txt) para la pasada editorial.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modelo import TIPOS_RECUADRO, plano, texto_de, vista  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RE_SECCION_IA = re.compile(r"registro de verificaci[oó]n|^correcciones (aplicadas )?tras la auditor", re.I)
RE_PARRAFO_IA = re.compile(r"^(correcciones (aplicadas )?tras la auditor|revisi[oó]n del auditor)", re.I)
RE_ETIQUETA = re.compile(r"\s*\[(ilustraci[oó]n propia|recorte documental[^\]]*|captura[^\]]*|esquema propio[^\]]*)\]\s*$", re.I)


def tipo_recuadro(box):
    primero = box["blocks"][0] if box["blocks"] else None
    titulo = plano(primero["runs"]).lower() if primero and "runs" in primero else ""
    if re.search(r"seguridad|emergencia|fuerza|no conectes|tensión de red|230 v|mando funcional", titulo):
        return "seguridad"
    if "profesor" in titulo or "material adicional" in titulo:
        return "profesor"
    if titulo.startswith(("comprueba lo que", "preguntas del cap")):
        return "comprueba"
    if titulo.startswith(("práctica", "diagnóstico p", "variante", "ejercicio")):
        return "practica"
    if titulo.startswith("antes de empezar"):
        return "antes"
    if titulo.startswith("registro de lo observado"):
        return "registro"
    if titulo.startswith("pistas"):
        return "pistas"
    if titulo.startswith("soluciones"):
        return "soluciones"
    base = TIPOS_RECUADRO.get(box.get("fill", ""), "info")
    return {"practica": "practica", "aviso": "aviso", "recuerda": "recuerda"}.get(base, "nota")


def limpiar(n):
    els = json.loads((RAIZ / "trabajo" / f"b{n}.json").read_text(encoding="utf-8"))
    retirado = []
    out = []
    capitulo = None

    # 1. portada de trabajo
    i0 = next(i for i, e in enumerate(els) if e["t"] == "h" and e["lvl"] == 1)
    if i0:
        retirado.append({"bloque": n, "capitulo": None, "tipo": "Portada de documento de trabajo",
                         "elementos": els[:i0]})
    i = i0
    while i < len(els):
        e = els[i]
        if e["t"] == "h" and e["lvl"] == 1:
            capitulo = e["text"]
        # 2. secciones completas
        if e["t"] == "h" and RE_SECCION_IA.search(e["text"]):
            j = i + 1
            while j < len(els) and not (els[j]["t"] == "h" and els[j]["lvl"] <= e["lvl"]):
                j += 1
            tipo = "Registro de verificación" if "registro" in e["text"].lower() else "Correcciones de auditoría"
            retirado.append({"bloque": n, "capitulo": capitulo, "tipo": tipo, "elementos": els[i:j]})
            i = j
            continue
        # 3. párrafos sueltos
        if e["t"] == "p" and RE_PARRAFO_IA.search(plano(e["runs"]).strip()):
            retirado.append({"bloque": n, "capitulo": capitulo, "tipo": "Correcciones de auditoría", "elementos": [e]})
            i += 1
            continue
        out.append(e)
        i += 1

    # 4. etiquetas de procedencia en pies + tipo de recuadro (recursivo)
    procedencia = []

    def recorrer(lista, cap):
        for e in lista:
            if e["t"] == "h" and e["lvl"] == 1:
                cap = e["text"]
            if e["t"] == "cap" and e["runs"]:
                m = RE_ETIQUETA.search(plano(e["runs"]))
                if m:
                    procedencia.append({"pie": plano(e["runs"])[: m.start()].strip(), "procedencia": m.group(1)})
                    # recorta la etiqueta del último tramo (o tramos) con texto
                    resto = len(m.group(0))
                    while resto > 0 and e["runs"]:
                        r = e["runs"][-1]
                        if len(r["x"]) <= resto:
                            resto -= len(r["x"])
                            e["runs"].pop()
                        else:
                            r["x"] = r["x"][: len(r["x"]) - resto]
                            resto = 0
                    if e["runs"]:
                        e["runs"][-1]["x"] = e["runs"][-1]["x"].rstrip()
            if e["t"] == "box":
                e["tipo"] = tipo_recuadro(e)
                recorrer(e["blocks"], cap)
            if e["t"] == "tbl":
                for fila in e["rows"]:
                    for c in fila:
                        recorrer(c["blocks"], cap)
        return cap

    recorrer(out, None)
    if procedencia:
        retirado.append({"bloque": n, "capitulo": None, "tipo": "Procedencia de las figuras", "procedencia": procedencia})

    (RAIZ / "trabajo" / f"b{n}.limpio.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    dir_inf = RAIZ / "informe" / "retirado"
    dir_inf.mkdir(parents=True, exist_ok=True)
    (dir_inf / f"auto_b{n}.json").write_text(json.dumps(retirado, ensure_ascii=False, indent=1), encoding="utf-8")

    # vistas por capítulo
    dir_v = RAIZ / "trabajo" / "vista"
    dir_v.mkdir(parents=True, exist_ok=True)
    cap_actual, buf = None, []

    def volcar():
        if cap_actual is not None and buf:
            m = re.match(r"(\d+)\.", cap_actual)
            nombre = f"cap_{int(m.group(1)):02d}.txt" if m else "cap_00_intro.txt"
            (dir_v / nombre).write_text("\n".join(vista(buf)), encoding="utf-8")

    for e in out:
        if e["t"] == "h" and e["lvl"] == 1:
            volcar()
            cap_actual, buf = e["text"], []
        buf.append(e)
    volcar()

    n_ret = sum(len(r.get("elementos", [])) for r in retirado)
    print(f"Bloque {n}: {len(out)} elementos quedan; {n_ret} elementos retirados; {len(procedencia)} etiquetas de pie")


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["1", "2", "3", "4", "5"]):
        limpiar(int(n))
