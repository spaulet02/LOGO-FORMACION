"""Genera el informe para ITECAM y el profesorado con todo lo retirado del libro del alumno.

Entrada: informe/retirado/auto_bN.json (limpieza automática) y informe/retirado/editorial.json
Salida : salida/Informe_ITECAM_trazabilidad.docx
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modelo import plano, texto_de  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
NAVY = RGBColor(0x19, 0x23, 0x3E)
GRIS = RGBColor(0x5F, 0x66, 0x76)
FUENTE = "Montserrat"

MOTIVOS = {
    "ia-metodo": "Método de elaboración (cálculos con Python, scripts, modelos)",
    "ia-documento-trabajo": "Notas de documento de trabajo (pendientes, propuestas, estado de verificación)",
    "ia-fuentes": "Comentarios del autor sobre las fuentes (lo que el manual dice o no dice, discrepancias)",
    "ia-auditoria": "Auditorías del texto",
    "seguridad": "Unificación de avisos de seguridad",
    "errata": "Posibles erratas y puntos técnicos que revisar",
}


def sombrear(celda, color):
    tcpr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def repetir_cabecera(fila):
    trpr = fila._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); trpr.append(e)


class Informe:
    def __init__(self):
        self.doc = Document()
        st = self.doc.styles
        st["Normal"].font.name = FUENTE
        st["Normal"].font.size = Pt(9)
        st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
        st["Normal"].paragraph_format.space_after = Pt(4)
        for n, tam in (("Heading 1", 16), ("Heading 2", 12), ("Heading 3", 10)):
            h = st[n]; h.font.name = FUENTE; h.font.size = Pt(tam); h.font.color.rgb = NAVY; h.font.bold = True
            h.element.rPr.rFonts.set(qn("w:asciiTheme"), "") if False else None
            rf = h.element.rPr.find(qn("w:rFonts"))
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                if rf is not None and rf.get(qn(a)) is not None:
                    del rf.attrib[qn(a)]
            h.paragraph_format.keep_with_next = True
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2.2)
        sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.0)
        pie = sec.footer.paragraphs[0]
        pie.text = "ITECAM · Informe de trazabilidad del libro LOGO! 9 · Uso interno del profesorado"
        pie.runs[0].font.size = Pt(7); pie.runs[0].font.color.rgb = GRIS

    def p(self, texto, **kw):
        par = self.doc.add_paragraph()
        r = par.add_run(texto)
        if kw.get("b"): r.bold = True
        if kw.get("i"): r.italic = True
        if kw.get("color"): r.font.color.rgb = kw["color"]
        if kw.get("size"): r.font.size = Pt(kw["size"])
        return par

    def tabla(self, cab, filas, anchos):
        t = self.doc.add_table(rows=1, cols=len(cab))
        t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, c in enumerate(cab):
            cel = t.rows[0].cells[i]; cel.text = c
            cel.paragraphs[0].runs[0].bold = True
            cel.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            sombrear(cel, "19233E")
        repetir_cabecera(t.rows[0])
        for f in filas:
            cs = t.add_row().cells
            for i, v in enumerate(f):
                cs[i].text = str(v if v is not None else "")
        for fila in t.rows:
            for i, w in enumerate(anchos):
                fila.cells[i].width = Cm(w)
                for par in fila.cells[i].paragraphs:
                    par.paragraph_format.space_after = Pt(0)
                    for r in par.runs:
                        r.font.size = Pt(7.5)
        self.doc.add_paragraph()
        return t

    def elementos(self, els):
        """Vuelca elementos retirados (párrafos, pies, recuadros y tablas)."""
        for e in els:
            if e["t"] == "h":
                self.doc.add_heading(e["text"], level=3)
            elif e["t"] in ("p", "cap", "title"):
                txt = e.get("text") or plano(e.get("runs", []))
                if txt.strip():
                    self.p(txt, i=e["t"] == "cap", size=8.5)
            elif e["t"] == "box":
                self.elementos(e["blocks"])
            elif e["t"] == "tbl":
                filas = [[" ".join(texto_de(b) for b in c["blocks"]) for c in f] for f in e["rows"]]
                n = max(len(f) for f in filas)
                filas = [f + [""] * (n - len(f)) for f in filas]
                ancho = 16.6 / n
                self.tabla(filas[0], filas[1:], [ancho] * n)


def main():
    inf = Informe()
    d = inf.doc
    ed = json.loads((RAIZ / "informe" / "retirado" / "editorial.json").read_text(encoding="utf-8"))
    auto = []
    for n in range(1, 6):
        auto += json.loads((RAIZ / "informe" / "retirado" / f"auto_b{n}.json").read_text(encoding="utf-8"))

    # ---- portada
    t = d.add_paragraph(); t.paragraph_format.space_before = Pt(120)
    r = t.add_run("Informe de trazabilidad editorial"); r.bold = True; r.font.size = Pt(26); r.font.color.rgb = NAVY
    inf.p("Libro del alumno «LOGO! 9, LOGO!Soft Comfort V9 y LOGO! TDE 9»", size=13, color=NAVY)
    inf.p("Documento para ITECAM y el profesorado. No forma parte del libro del alumno.", i=True, color=GRIS)
    inf.p("Noviembre de 2026", color=GRIS)
    d.add_page_break()

    # ---- 1. resumen
    d.add_heading("1. Qué recoge este informe", level=1)
    inf.p("Durante la edición del libro del alumno se ha retirado todo el material que explica cómo se elaboró el texto "
          "y que no sirve al alumno: registros de verificación, tablas de correcciones de auditoría, portadas de "
          "«documento de trabajo», menciones a cálculos con Python, scripts, modelos o al encargo, notas «pendiente de "
          "ITECAM», la convención de marcas † y las etiquetas de procedencia de las figuras. Ese material no se pierde: "
          "se conserva íntegro en este informe, ordenado por capítulo, para que ITECAM y el profesorado puedan "
          "consultarlo, completar las comprobaciones pendientes en el banco y decidir sobre los puntos abiertos.")
    inf.p("Además se ha hecho una pasada editorial que elimina los tics de texto generado y unifica los avisos de "
          "seguridad repetidos: la referencia completa queda en «Normas de trabajo en el banco» y en el apartado 2.1, "
          "y los capítulos posteriores remiten a ellas con un aviso breve y la norma concreta de cada punto.")
    est = ed["estadisticas"]
    n_reg = sum(1 for a in auto if a["tipo"] == "Registro de verificación")
    n_cor = sum(1 for a in auto if a["tipo"] == "Correcciones de auditoría")
    n_pro = sum(len(a.get("procedencia", [])) for a in auto)
    filas = [
        ("Registros de verificación retirados (secciones completas)", n_reg),
        ("Correcciones de auditoría retiradas (tablas y párrafos)", n_cor),
        ("Portadas de «documento de trabajo» de los bloques", 5),
        ("Etiquetas de procedencia retiradas de los pies de figura", n_pro),
        ("Rótulos de LOGO!Soft Comfort marcados con † (distintos)", len(ed["rotulos_lsc_pendientes"])),
    ] + [(MOTIVOS.get(k, k), v) for k, v in est.items() if k in MOTIVOS] + [("Correcciones de estilo (tics de texto generado)", est.get("estilo", 0))]
    inf.tabla(["Intervención", "Nº"], filas, [14, 2.6])

    # ---- 2. erratas y puntos abiertos (lo más útil para ITECAM)
    d.add_heading("2. Puntos técnicos que conviene revisar", level=1)
    inf.p("Durante la revisión se han detectado posibles erratas o incoherencias. No se han corregido en el texto "
          "cuando afectan a datos técnicos: se dejan aquí para que el autor o el profesorado las confirmen en el equipo.")
    notas = [o for o in ed["operaciones"] if o["motivo"] == "errata"]
    inf.tabla(["Capítulo", "Observación", "Texto afectado"],
              [((o["capitulo"] or "")[:40], o["nota"] or ("Corregido: " + (o["despues"] or "")[:300]), (o["antes"] or "")[:300]) for o in notas],
              [3.4, 7, 6.2])

    # ---- 3. rótulos †
    d.add_heading("3. Rótulos de LOGO!Soft Comfort pendientes de confirmar", level=1)
    inf.p("El texto original marcaba con † los rótulos de LOGO!Soft Comfort V9 que el manual de sistema no cita "
          "literalmente. En el libro del alumno la marca se ha sustituido por una advertencia general en «Convenciones "
          "del libro». Esta es la lista de rótulos marcados, con su número de apariciones, para confirmarlos con "
          "capturas de la versión instalada en el aula.")
    rot = ed["rotulos_lsc_pendientes"]
    inf.tabla(["Rótulo (contexto)", "Apariciones"], [(r[0], r[1]) for r in rot[:250]], [14, 2.6])

    # ---- 4. cambios por motivo
    d.add_heading("4. Texto retirado o reescrito en la pasada editorial", level=1)
    inf.p("Para cada cambio se indica el texto original y, cuando se ha reescrito, el texto que queda en el libro.")
    por_mot = defaultdict(list)
    for o in ed["operaciones"]:
        if o["motivo"] != "errata":
            por_mot[o["motivo"]].append(o)
    for mot in ("ia-metodo", "ia-documento-trabajo", "ia-fuentes", "seguridad"):
        if not por_mot.get(mot):
            continue
        d.add_heading(MOTIVOS[mot], level=2)
        inf.tabla(["Capítulo", "Texto original", "Queda en el libro"],
                  [((o["capitulo"] or "")[:40], (o["antes"] or "")[:900], (o["despues"] or "— (retirado)")[:900]) for o in por_mot[mot]],
                  [3, 7, 6.6])

    # ---- 5. registros de verificación y auditorías
    d.add_heading("5. Registros de verificación y correcciones de auditoría", level=1)
    inf.p("Se reproducen tal como estaban al final de cada capítulo del original.")
    for a in auto:
        if a["tipo"] in ("Registro de verificación", "Correcciones de auditoría"):
            d.add_heading(f"{a['tipo']} · {a['capitulo']}", level=2)
            inf.elementos(a["elementos"])

    # ---- 6. portadas de trabajo
    d.add_heading("6. Portadas de «documento de trabajo» de los bloques", level=1)
    for a in auto:
        if a["tipo"] == "Portada de documento de trabajo":
            d.add_heading(f"Bloque {a['bloque']}", level=2)
            inf.elementos([e for e in a["elementos"] if e["t"] != "tbl"])

    # ---- 7. procedencia de figuras
    d.add_heading("7. Procedencia de las figuras", level=1)
    inf.p("Etiquetas retiradas de los pies de figura. Las figuras con «recorte documental» reproducen páginas del "
          "manual de Siemens: conviene confirmar los permisos de reproducción antes de la edición definitiva.")
    filas = []
    for a in auto:
        for pr in a.get("procedencia", []):
            filas.append((pr["pie"][:160], pr["procedencia"]))
    inf.tabla(["Pie de figura (numeración original)", "Procedencia"], filas, [12.6, 4])

    # ---- 8. operaciones no aplicadas
    if ed["fallidas"]:
        d.add_heading("8. Operaciones no aplicadas", level=1)
        inf.tabla(["Operación", "Elemento"], [(f["op"], f["id"]) for f in ed["fallidas"]], [6, 10.6])

    out = RAIZ / "salida" / "Informe_ITECAM_trazabilidad.docx"
    d.save(out)
    print("Informe:", out)


if __name__ == "__main__":
    main()
