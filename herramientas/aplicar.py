"""Aplica las operaciones editoriales (trabajo/ops/cap_XX.json) al texto limpio.

Entrada : trabajo/bN.limpio.json + trabajo/ops/*.json
Salida  : trabajo/bN.final.json y informe/retirado/editorial.json (todo lo retirado o
          cambiado por motivos «ia-*», «seguridad» y las notas de errata, con el texto original).
Además:
  - quita la marca † (convención de rótulos no verificados) y registra dónde estaba;
  - unifica la remisión de los avisos de seguridad;
  - renumera tablas y figuras de cada capítulo si se ha borrado alguna y actualiza las remisiones.
"""
import copy
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modelo import md_a_runs, plano, runs_a_md, texto_de  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
REMISION_SEG = "(normas completas en «Normas de trabajo en el banco», al principio del libro, y en el apartado 2.1)"


def cargar_ops():
    ops = []
    for f in sorted(glob.glob(str(RAIZ / "trabajo" / "ops" / "cap_*.json"))):
        for o in json.load(open(f, encoding="utf-8")):
            o["_fichero"] = Path(f).name
            ops.append(o)
    return ops


def indexar(lista, idx, padre=None):
    for i, e in enumerate(lista):
        idx[e["id"]] = (lista, e)
        if e["t"] == "box":
            indexar(e["blocks"], idx)
        elif e["t"] == "tbl":
            for fila in e["rows"]:
                for c in fila:
                    indexar(c["blocks"], idx)


def main():
    bloques = {n: json.loads((RAIZ / "trabajo" / f"b{n}.limpio.json").read_text(encoding="utf-8")) for n in range(1, 6)}
    idx = {}
    for n, els in bloques.items():
        indexar(els, idx)
    capitulo_de = {}
    for n, els in bloques.items():
        cap = None
        def marcar(lista):
            nonlocal cap
            for e in lista:
                if e["t"] == "h" and e["lvl"] == 1:
                    cap = e["text"]
                capitulo_de[e["id"]] = cap
                if e["t"] == "box":
                    marcar(e["blocks"])
                if e["t"] == "tbl":
                    for f in e["rows"]:
                        for c in f:
                            marcar(c["blocks"])
        marcar(els)

    ops = cargar_ops()
    informe = []
    fallos = []
    stats = Counter()

    def registrar(o, antes, despues=None):
        mot = o.get("motivo", "")
        stats[mot] += 1
        if mot.startswith("ia-") or mot in ("seguridad", "errata") or o["op"] == "nota":
            informe.append({"capitulo": capitulo_de.get(o["id"]), "motivo": mot, "op": o["op"], "id": o["id"],
                            "antes": antes, "despues": despues, "nota": o.get("text") if o["op"] == "nota" else None})

    # 1) operaciones de contenido
    for o in ops:
        if o["op"] not in ("replace", "replace_cell", "box_type", "nota"):
            continue
        if o["id"] not in idx:
            fallos.append(o); continue
        lista, e = idx[o["id"]]
        if o["op"] == "replace":
            if e["t"] in ("h", "title"):
                antes = e["text"]; e["text"] = o["text"]
            elif e["t"] in ("p", "cap"):
                antes = runs_a_md(e["runs"]); e["runs"] = md_a_runs(o["text"])
            else:
                fallos.append(o); continue
            registrar(o, antes, o["text"])
        elif o["op"] == "replace_cell":
            try:
                celda = e["rows"][o["r"]][o["c"]]
            except (IndexError, KeyError):
                fallos.append(o); continue
            antes = " / ".join(texto_de(b) for b in celda["blocks"])
            celda["blocks"] = [{"id": f"{o['id']}-r{o['r']}c{o['c']}", "t": "p", "runs": md_a_runs(o["text"])}] if o["text"].strip() else []
            registrar(o, antes, o["text"])
        elif o["op"] == "box_type":
            e["tipo"] = o["tipo"]; stats[o.get("motivo", "")] += 1
        elif o["op"] == "nota":
            registrar(o, texto_de(e)[:600])

    # 2) filas y columnas (de mayor a menor índice)
    por_tabla = defaultdict(list)
    for o in ops:
        if o["op"] in ("delete_row", "delete_col"):
            por_tabla[o["id"]].append(o)
    for tid, lst in por_tabla.items():
        if tid not in idx:
            fallos += lst; continue
        _, t = idx[tid]
        for o in sorted([x for x in lst if x["op"] == "delete_col"], key=lambda x: -x["c"]):
            antes = " | ".join(texto_de(b) for f in t["rows"] if o["c"] < len(f) for b in f[o["c"]]["blocks"])
            for f in t["rows"]:
                if o["c"] < len(f):
                    f.pop(o["c"])
            if o["c"] < len(t["grid"]):
                t["grid"].pop(o["c"])
            registrar(o, antes)
        for o in sorted([x for x in lst if x["op"] == "delete_row"], key=lambda x: -x["r"]):
            if o["r"] < len(t["rows"]):
                antes = " | ".join(" ".join(texto_de(b) for b in c["blocks"]) for c in t["rows"][o["r"]])
                t["rows"].pop(o["r"])
                registrar(o, antes)
            else:
                fallos.append(o)

    # 3) borrados
    for o in ops:
        if o["op"] not in ("delete", "delete_section"):
            continue
        if o["id"] not in idx:
            fallos.append(o); continue
        lista, e = idx[o["id"]]
        if e not in lista:
            continue  # ya borrado por una sección
        i = lista.index(e)
        if o["op"] == "delete_section" and e["t"] == "h":
            j = i + 1
            while j < len(lista) and not (lista[j]["t"] == "h" and lista[j]["lvl"] <= e["lvl"]):
                j += 1
            antes = "\n".join(texto_de(x) for x in lista[i:j])
            del lista[i:j]
        else:
            antes = texto_de(e)
            lista.pop(i)
        registrar(o, antes)

    # 4) marcas †, remisión de seguridad
    dagas = Counter()

    def limpiar_runs(runs):
        for r in runs:
            if "†" in r["x"]:
                for m in re.finditer(r"([^\s«»()]{1,40}(?: [^\s«»()]{1,25}){0,3})†", r["x"]):
                    dagas[m.group(1).strip("*> ")] += 1
                if r.get("b") and r["x"].strip() == "†":
                    pass
                r["x"] = r["x"].replace(" †", "").replace("†", "")
            r["x"] = re.sub(r"\(normas completas en el apartado 2\.1\)", REMISION_SEG, r["x"])
            r["x"] = re.sub(r"\s*Ilustración propia\.?(?=\s*$)", "", r["x"])
        return [r for r in runs if r["x"]]

    def recorrer(lista):
        for e in lista:
            if e["t"] in ("p", "cap"):
                e["runs"] = limpiar_runs(e["runs"])
            elif e["t"] in ("h", "title"):
                e["text"] = e["text"].replace("†", "")
            elif e["t"] == "box":
                recorrer(e["blocks"])
            elif e["t"] == "tbl":
                for f in e["rows"]:
                    for c in f:
                        recorrer(c["blocks"])

    for els in bloques.values():
        recorrer(els)

    # 5) renumeración de tablas y figuras por capítulo
    mapa = {"tabla": {}, "figura": {}}
    re_pie = re.compile(r"^(Tabla|Figura)\s+(\d+)\.(\d+)\.")
    for els in bloques.values():
        cap_n, cont = None, {"tabla": 0, "figura": 0}

        def numerar(lista):
            nonlocal cap_n, cont
            for e in lista:
                if e["t"] == "h" and e["lvl"] == 1:
                    m = re.match(r"(\d+)\.", e["text"])
                    cap_n = m.group(1) if m else "0"
                    cont = {"tabla": 0, "figura": 0}
                if e["t"] == "cap" and e["runs"]:
                    m = re_pie.match(plano(e["runs"]))
                    if m and m.group(2) == cap_n:
                        tipo = m.group(1).lower()
                        cont[tipo] += 1
                        viejo, nuevo = f"{m.group(2)}.{m.group(3)}", f"{cap_n}.{cont[tipo]}"
                        if viejo != nuevo:
                            mapa[tipo][viejo] = nuevo
                            r0 = e["runs"][0]
                            r0["x"] = r0["x"].replace(viejo, nuevo, 1)
                if e["t"] == "box":
                    numerar(e["blocks"])
        numerar(els)

    renum = 0
    re_ref = re.compile(r"\b(tablas?|figuras?|Tablas?|Figuras?|fig\.)(\s+)((?:\d+\.\d+)(?:(?:,\s*|\s+[yeoa]\s+|\s*[–-]\s*)\d+\.\d+)*)")

    def ajustar(texto):
        nonlocal renum
        def sub(m):
            nonlocal renum
            tipo = "tabla" if m.group(1).lower().startswith("tabla") else "figura"
            def num(mm):
                nonlocal renum
                v = mm.group(0)
                if v in mapa[tipo]:
                    renum += 1
                    return mapa[tipo][v]
                return v
            return m.group(1) + m.group(2) + re.sub(r"\d+\.\d+", num, m.group(3))
        return re_ref.sub(sub, texto)

    def recorrer_refs(lista):
        for e in lista:
            if e["t"] == "p" or (e["t"] == "cap" and not re_pie.match(plano(e["runs"]))):
                for r in e["runs"]:
                    r["x"] = ajustar(r["x"])
            elif e["t"] == "box":
                recorrer_refs(e["blocks"])
            elif e["t"] == "tbl":
                for f in e["rows"]:
                    for c in f:
                        recorrer_refs(c["blocks"])

    if mapa["tabla"] or mapa["figura"]:
        for els in bloques.values():
            recorrer_refs(els)

    # 6) ajustes manuales de remisiones señalados en la revisión
    MANUALES = [("tabla 19.20", "tabla 19.19")]
    def manual(lista):
        for e in lista:
            if e["t"] in ("p", "cap"):
                for r in e["runs"]:
                    for a, b in MANUALES:
                        r["x"] = r["x"].replace(a, b)
            elif e["t"] == "box":
                manual(e["blocks"])
            elif e["t"] == "tbl":
                for f in e["rows"]:
                    for c in f:
                        manual(c["blocks"])
    manual(bloques[5])

    for n, els in bloques.items():
        (RAIZ / "trabajo" / f"b{n}.final.json").write_text(json.dumps(els, ensure_ascii=False), encoding="utf-8")
    salida = {"estadisticas": dict(stats), "operaciones": informe, "fallidas": fallos,
              "rotulos_lsc_pendientes": dagas.most_common(), "renumeracion": mapa}
    (RAIZ / "informe" / "retirado" / "editorial.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Operaciones:", len(ops), dict(stats))
    print("Fallidas:", len(fallos), [(f["op"], f["id"], f["_fichero"]) for f in fallos][:20])
    print("Marcas † retiradas (rótulos distintos):", len(dagas))
    print("Renumeración:", {k: len(v) for k, v in mapa.items()}, "remisiones ajustadas:", renum)


if __name__ == "__main__":
    main()
