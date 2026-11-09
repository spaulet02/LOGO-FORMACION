"""Convierte un capítulo en Markdown (pandoc) al modelo intermedio del maquetador.

Uso: python3 herramientas/md2json.py condensado/cap_07.md  -> trabajo/manual/cap_07.json
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONT = [0]


def nid(pref):
    CONT[0] += 1
    return f"{pref}-{CONT[0]:04d}"


def inlines(lst, fmt=None):
    fmt = dict(fmt or {})
    out = []

    def add(x, f):
        if not x:
            return
        if out and {k: v for k, v in out[-1].items() if k != "x"} == f:
            out[-1]["x"] += x
        else:
            out.append({"x": x, **f})

    for el in lst:
        t, c = el["t"], el.get("c")
        if t == "Str":
            add(c, fmt)
        elif t in ("Space", "SoftBreak"):
            add(" ", fmt)
        elif t == "LineBreak":
            add("\n", fmt)
        elif t == "Strong":
            for r in inlines(c, {**fmt, "b": 1}):
                add(r.pop("x"), r)
        elif t == "Emph":
            for r in inlines(c, {**fmt, "i": 1}):
                add(r.pop("x"), r)
        elif t == "Code":
            add(c[1], {**fmt, "code": 1})
        elif t == "Superscript":
            for r in inlines(c, {**fmt, "sup": 1}):
                add(r.pop("x"), r)
        elif t == "Subscript":
            for r in inlines(c, {**fmt, "sub": 1}):
                add(r.pop("x"), r)
        elif t == "Quoted":
            a, b = ("«", "»") if c[0]["t"] == "DoubleQuote" else ("‘", "’")
            add(a, fmt)
            for r in inlines(c[1], fmt):
                add(r.pop("x"), r)
            add(b, fmt)
        elif t in ("Link", "Span"):
            for r in inlines(c[1] if t == "Link" else c[1], fmt):
                add(r.pop("x"), r)
        elif t == "Math":
            add(c[1], fmt)
        elif t == "RawInline":
            add(c[1], fmt)
        elif t == "Strikeout":
            for r in inlines(c, fmt):
                add(r.pop("x"), r)
    return out


def bloques(lst, pref, lista=None):
    out = []
    for b in lst:
        t, c = b["t"], b.get("c")
        if t == "Header":
            nivel, _, ins = c
            txt = "".join(r["x"] for r in inlines(ins))
            out.append({"id": nid(pref), "t": "h", "lvl": nivel, "text": txt})
        elif t in ("Para", "Plain"):
            if len(c) == 1 and c[0]["t"] == "Image":
                attr, alt, (src, _) = c[0]["c"]
                out.append({"id": nid(pref), "t": "img", "file": src, "cx": 0, "cy": 0})
                cap = inlines(alt)
                if cap:
                    out.append({"id": nid(pref), "t": "cap", "runs": cap})
                continue
            runs = inlines(c)
            if not "".join(r["x"] for r in runs).strip():
                continue
            el = {"id": nid(pref), "t": "p", "runs": runs}
            if lista:
                el["list"] = dict(lista)
                lista = None  # solo el primer párrafo de un elemento lleva la viñeta
            out.append(el)
        elif t == "Figure":
            # pandoc >= 3: Figure attr caption blocks
            _, (_, capblocks), contenido = c
            for blk in contenido:
                for ins in (blk.get("c") or []):
                    if isinstance(ins, dict) and ins.get("t") == "Image":
                        out.append({"id": nid(pref), "t": "img", "file": ins["c"][2][0], "cx": 0, "cy": 0})
            cap = []
            for blk in capblocks:
                cap += inlines(blk["c"])
            if cap:
                out.append({"id": nid(pref), "t": "cap", "runs": cap})
        elif t in ("BulletList", "OrderedList"):
            items = c if t == "BulletList" else c[1]
            nivel = (lista or {}).get("lvl", -1) + 1 if lista else 0
            for it in items:
                out += bloques(it, pref, {"kind": "bullet" if t == "BulletList" else "num", "lvl": nivel})
        elif t == "Div":
            (_, clases, kv), contenido = c
            tipo = clases[0] if clases else "nota"
            out.append({"id": nid(pref), "t": "box", "fill": "", "tipo": tipo, "blocks": bloques(contenido, pref)})
        elif t == "BlockQuote":
            out.append({"id": nid(pref), "t": "box", "fill": "", "tipo": "nota", "blocks": bloques(c, pref)})
        elif t == "CodeBlock":
            for linea in c[1].split("\n"):
                out.append({"id": nid(pref), "t": "p", "runs": [{"x": linea or " ", "code": 1}]})
        elif t == "Table":
            out += tabla(c, pref)
        elif t == "HorizontalRule":
            continue
    return out


def tabla(c, pref):
    attr, caption, colspecs, thead, tbodies, tfoot = c
    cap = []
    for blk in caption[1]:
        cap += inlines(blk["c"])
    def filas(rows):
        res = []
        for _, celdas in rows:
            fila = []
            for cel in celdas:
                _, _, rs, cs, contenido = cel
                d = {"blocks": bloques(contenido, pref)}
                if cs > 1:
                    d["span"] = cs
                fila.append(d)
            res.append(fila)
        return res
    cab = filas(thead[1])
    cuerpo = []
    for tb in tbodies:
        cuerpo += filas(tb[3])
    n = len(colspecs)
    pesos = []
    for i in range(n):
        largo = max([len("".join(r["x"] for b in f[i]["blocks"] for r in b.get("runs", []))) for f in cab + cuerpo if i < len(f)] or [5])
        pesos.append(min(max(largo, 6), 60))
    out = []
    if cap:
        out.append({"id": nid(pref), "t": "cap", "runs": cap})
    out.append({"id": nid(pref), "t": "tbl", "grid": pesos, "hdr": len(cab), "rows": cab + cuerpo})
    return out


def convertir(ruta):
    ruta = Path(ruta)
    # una lista pegada a la línea anterior no la reconoce pandoc: se inserta una línea en blanco
    lineas = ruta.read_text(encoding="utf-8").split("\n")
    out = []
    for l in lineas:
        es_item = re.match(r"^\s*([-*+]|\d+[.)])\s+\S", l)
        if es_item and out and out[-1].strip() and not re.match(r"^\s*([-*+]|\d+[.)])\s+", out[-1]) \
                and not out[-1].startswith((":::", "|", "    ")):
            out.append("")
        out.append(l)
    ast = json.loads(subprocess.run(["pandoc", "-f", "markdown", "-t", "json"], input="\n".join(out),
                                    capture_output=True, text=True, check=True).stdout)
    els = bloques(ast["blocks"], ruta.stem)
    dst = RAIZ / "trabajo" / "manual" / (ruta.stem + ".json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(els, ensure_ascii=False), encoding="utf-8")
    return dst, els


if __name__ == "__main__":
    for r in sys.argv[1:]:
        d, els = convertir(r)
        print(d.name, len(els), "elementos")
