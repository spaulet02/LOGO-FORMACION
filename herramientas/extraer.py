"""Extrae un bloque .docx a una representación JSON intermedia y guarda sus imágenes.

Uso: python3 herramientas/extraer.py originales/BLOQUE_3.docx 3

Salida:
  trabajo/b3.json        lista de elementos con id estable (b3-0001, ...)
  trabajo/img/b3/...     imágenes del bloque
  trabajo/b3.txt         vista legible con ids (para la revisión editorial)
"""
import json
import sys
from pathlib import Path

import docx
from docx.oxml.ns import qn

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
R_EMBED = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"

RAIZ = Path(__file__).resolve().parent.parent


class Extractor:
    def __init__(self, ruta, n):
        self.doc = docx.Document(ruta)
        self.n = n
        self.cont = 0
        self.img_dir = RAIZ / "trabajo" / "img" / f"b{n}"
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.img_guardadas = {}
        self.formatos = self._formatos_numeracion()

    # ---------- numeración ----------
    def _formatos_numeracion(self):
        try:
            np = self.doc.part.numbering_part.element
        except Exception:
            return {}
        abstract = {}
        for a in np.findall(qn("w:abstractNum")):
            niveles = {}
            for l in a.findall(qn("w:lvl")):
                f = l.find(qn("w:numFmt"))
                niveles[int(l.get(qn("w:ilvl")))] = f.get(qn("w:val")) if f is not None else "decimal"
            abstract[a.get(qn("w:abstractNumId"))] = niveles
        res = {}
        for num in np.findall(qn("w:num")):
            aid = num.find(qn("w:abstractNumId")).get(qn("w:val"))
            res[num.get(qn("w:numId"))] = abstract.get(aid, {})
        return res

    def nid(self):
        self.cont += 1
        return f"b{self.n}-{self.cont:04d}"

    # ---------- texto ----------
    def runs(self, p):
        """Devuelve la lista de tramos con formato de un párrafo (incluye hipervínculos)."""
        salida = []
        for r in p.iter(qn("w:r")):
            rp = r.find(qn("w:rPr"))
            fmt = {}
            if rp is not None:
                def on(tag):
                    e = rp.find(qn(tag))
                    return e is not None and e.get(qn("w:val")) not in ("0", "false")
                if on("w:b"):
                    fmt["b"] = 1
                if on("w:i"):
                    fmt["i"] = 1
                f = rp.find(qn("w:rFonts"))
                if f is not None and (f.get(qn("w:ascii")) or "").lower() in ("consolas", "courier new", "courier"):
                    fmt["code"] = 1
                va = rp.find(qn("w:vertAlign"))
                if va is not None and va.get(qn("w:val")) in ("superscript", "subscript"):
                    fmt["sup" if va.get(qn("w:val")) == "superscript" else "sub"] = 1
                c = rp.find(qn("w:color"))
                if c is not None and c.get(qn("w:val")) not in (None, "auto", "000000", "1A1A1A"):
                    fmt["color"] = c.get(qn("w:val"))
            texto = ""
            for ch in r:
                tag = ch.tag.split("}")[1]
                if tag == "t":
                    texto += ch.text or ""
                elif tag == "tab":
                    texto += "\t"
                elif tag == "br" and ch.get(qn("w:type")) not in ("page", "column"):
                    texto += "\n"
                elif tag == "noBreakHyphen":
                    texto += "‑"
            if not texto:
                continue
            if salida and {k: v for k, v in salida[-1].items() if k != "x"} == fmt:
                salida[-1]["x"] += texto
            else:
                salida.append({"x": texto, **fmt})
        return salida

    @staticmethod
    def plano(runs):
        return "".join(r["x"] for r in runs)

    def estilo(self, p):
        ps = p.find(qn("w:pPr"))
        s = ps.find(qn("w:pStyle")) if ps is not None else None
        return s.get(qn("w:val")) if s is not None else ""

    def imagenes(self, p):
        res = []
        for drw in p.iter(qn("w:drawing")):
            blip = next(drw.iter(A + "blip"), None)
            if blip is None:
                continue
            rid = blip.get(R_EMBED)
            part = self.doc.part.related_parts.get(rid)
            if part is None:
                continue
            nombre = Path(part.partname).name
            destino = self.img_dir / nombre
            if nombre not in self.img_guardadas:
                destino.write_bytes(part.blob)
                self.img_guardadas[nombre] = 1
            ext = next(drw.iter(WP + "extent"), None)
            cx = int(ext.get("cx")) if ext is not None else 0
            cy = int(ext.get("cy")) if ext is not None else 0
            res.append({"file": f"trabajo/img/b{self.n}/{nombre}", "cx": cx, "cy": cy})
        return res

    # ---------- bloques ----------
    def parrafo(self, p):
        est = self.estilo(p)
        imgs = self.imagenes(p)
        rs = self.runs(p)
        txt = self.plano(rs).strip()
        out = []
        for im in imgs:
            out.append({"id": self.nid(), "t": "img", **im})
        if not txt:
            return out
        if est.startswith("Heading") and est[7:].isdigit():
            out.append({"id": self.nid(), "t": "h", "lvl": int(est[7:]), "text": txt})
            return out
        if est == "Title":
            out.append({"id": self.nid(), "t": "title", "text": txt})
            return out
        if est == "Caption":
            out.append({"id": self.nid(), "t": "cap", "runs": rs})
            return out
        el = {"id": self.nid(), "t": "p", "runs": rs}
        ps = p.find(qn("w:pPr"))
        if ps is not None:
            numpr = ps.find(qn("w:numPr"))
            if numpr is not None and numpr.find(qn("w:numId")) is not None:
                numid = numpr.find(qn("w:numId")).get(qn("w:val"))
                ilvl_e = numpr.find(qn("w:ilvl"))
                ilvl = int(ilvl_e.get(qn("w:val"))) if ilvl_e is not None else 0
                fmt = self.formatos.get(numid, {}).get(ilvl, "decimal")
                if numid != "0":
                    el["list"] = {"kind": "bullet" if fmt in ("bullet", "none") else "num", "lvl": ilvl, "numId": numid}
            jc = ps.find(qn("w:jc"))
            if jc is not None and jc.get(qn("w:val")) == "center":
                el["center"] = 1
        out.append(el)
        return out

    def celda_bloques(self, tc):
        bl = []
        for ch in tc:
            tag = ch.tag.split("}")[1]
            if tag == "p":
                bl += self.parrafo(ch)
            elif tag == "tbl":
                bl.append(self.tabla(ch))
        return bl

    def tabla(self, tbl):
        filas = tbl.findall(qn("w:tr"))
        celdas0 = filas[0].findall(qn("w:tc")) if filas else []
        if len(filas) == 1 and len(celdas0) == 1:
            shd = tbl.find(".//" + qn("w:shd"))
            fill = shd.get(qn("w:fill")) if shd is not None else ""
            return {"id": self.nid(), "t": "box", "fill": fill, "blocks": self.celda_bloques(celdas0[0])}
        grid = [int(g.get(qn("w:w")) or 0) for g in tbl.findall(qn("w:tblGrid") + "/" + qn("w:gridCol"))]
        rows = []
        cabecera = 0
        for i, tr in enumerate(filas):
            trpr = tr.find(qn("w:trPr"))
            if trpr is not None and trpr.find(qn("w:tblHeader")) is not None:
                cabecera = i + 1
            fila = []
            for tc in tr.findall(qn("w:tc")):
                tcpr = tc.find(qn("w:tcPr"))
                span = 1
                if tcpr is not None and tcpr.find(qn("w:gridSpan")) is not None:
                    span = int(tcpr.find(qn("w:gridSpan")).get(qn("w:val")))
                vm = None
                if tcpr is not None and tcpr.find(qn("w:vMerge")) is not None:
                    vm = tcpr.find(qn("w:vMerge")).get(qn("w:val")) or "continue"
                shd = tcpr.find(qn("w:shd")) if tcpr is not None else None
                c = {"blocks": self.celda_bloques(tc)}
                if span > 1:
                    c["span"] = span
                if vm:
                    c["vmerge"] = vm
                if shd is not None and shd.get(qn("w:fill")) not in (None, "auto", "FFFFFF"):
                    c["fill"] = shd.get(qn("w:fill"))
                fila.append(c)
            rows.append(fila)
        if cabecera == 0 and rows and all(c.get("fill") for c in rows[0]):
            cabecera = 1
        return {"id": self.nid(), "t": "tbl", "grid": grid, "hdr": cabecera, "rows": rows}

    def extraer(self):
        elementos = []
        for el in self.doc.element.body:
            tag = el.tag.split("}")[1]
            if tag == "p":
                elementos += self.parrafo(el)
            elif tag == "tbl":
                elementos.append(self.tabla(el))
            elif tag == "sdt":
                continue  # índice automático del original: se regenera
        return elementos


def texto_legible(elementos, sangria=""):
    """Vista de texto con ids para la revisión editorial."""
    lineas = []
    for e in elementos:
        t = e["t"]
        if t == "h":
            lineas.append(f"[{e['id']}] {'#' * e['lvl']} {e['text']}")
        elif t == "title":
            lineas.append(f"[{e['id']}] TÍTULO: {e['text']}")
        elif t == "p":
            pref = ""
            if "list" in e:
                pref = ("  " * e["list"]["lvl"]) + ("- " if e["list"]["kind"] == "bullet" else "1. ")
            lineas.append(f"{sangria}[{e['id']}] {pref}{Extractor.plano(e['runs'])}")
        elif t == "cap":
            lineas.append(f"{sangria}[{e['id']}] PIE: {Extractor.plano(e['runs'])}")
        elif t == "img":
            lineas.append(f"{sangria}[{e['id']}] IMAGEN {Path(e['file']).name}")
        elif t == "box":
            lineas.append(f"{sangria}[{e['id']}] RECUADRO (fondo {e['fill']}) >>>")
            lineas += texto_legible(e["blocks"], sangria + "    ")
            lineas.append(f"{sangria}<<< fin recuadro {e['id']}")
        elif t == "tbl":
            lineas.append(f"{sangria}[{e['id']}] TABLA {len(e['rows'])} filas >>>")
            for fila in e["rows"]:
                celdas = []
                for c in fila:
                    celdas.append(" / ".join(
                        Extractor.plano(b["runs"]) if b["t"] in ("p", "cap") else f"<{b['t']}>"
                        for b in c["blocks"]))
                lineas.append(f"{sangria}    | " + " | ".join(celdas) + " |")
            lineas.append(f"{sangria}<<< fin tabla {e['id']}")
    return lineas


if __name__ == "__main__":
    ruta, n = sys.argv[1], int(sys.argv[2])
    ex = Extractor(ruta, n)
    els = ex.extraer()
    (RAIZ / "trabajo").mkdir(exist_ok=True)
    (RAIZ / "trabajo" / f"b{n}.json").write_text(json.dumps(els, ensure_ascii=False), encoding="utf-8")
    (RAIZ / "trabajo" / f"b{n}.txt").write_text("\n".join(texto_legible(els)), encoding="utf-8")
    print(f"Bloque {n}: {len(els)} elementos, {len(ex.img_guardadas)} imágenes")
