"""Utilidades comunes del modelo intermedio (tramos de texto <-> markdown ligero)."""
import re

MD_TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`|(?<![\w*])\*(?!\s).+?(?<!\s)\*(?![\w*])|\^[^^]+\^|~[^~]+~)")


def runs_a_md(runs):
    """Convierte tramos con formato a markdown ligero (**negrita**, *cursiva*, `código`, ^sup^, ~sub~)."""
    out = []
    for r in runs:
        x = r["x"]
        if not x:
            continue
        core = x.strip()
        if not core:
            out.append(x)
            continue
        pre = x[: len(x) - len(x.lstrip())]
        post = x[len(x.rstrip()):]
        if r.get("code"):
            core = f"`{core}`"
        else:
            if r.get("sup"):
                core = f"^{core}^"
            if r.get("sub"):
                core = f"~{core}~"
            if r.get("i"):
                core = f"*{core}*"
            if r.get("b"):
                core = f"**{core}**"
        out.append(pre + core + post)
    s = "".join(out)
    # fusiona marcas contiguas: **a****b** -> **ab**
    s = s.replace("****", "").replace("``", "")
    return s


def md_a_runs(texto):
    """Inverso de runs_a_md."""
    runs = []
    for parte in MD_TOKEN.split(texto):
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**") and len(parte) > 4:
            for r in md_a_runs(parte[2:-2]):
                r["b"] = 1
                runs.append(r)
        elif parte.startswith("`") and parte.endswith("`") and len(parte) > 2:
            runs.append({"x": parte[1:-1], "code": 1})
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            for r in md_a_runs(parte[1:-1]):
                r["i"] = 1
                runs.append(r)
        elif parte.startswith("^") and parte.endswith("^") and len(parte) > 2:
            runs.append({"x": parte[1:-1], "sup": 1})
        elif parte.startswith("~") and parte.endswith("~") and len(parte) > 2:
            runs.append({"x": parte[1:-1], "sub": 1})
        else:
            runs.append({"x": parte})
    return runs


def plano(runs):
    return "".join(r["x"] for r in runs)


def texto_de(el):
    """Texto plano de cualquier elemento (recursivo)."""
    t = el["t"]
    if t in ("h", "title"):
        return el["text"]
    if t in ("p", "cap"):
        return plano(el["runs"])
    if t == "box":
        return "\n".join(texto_de(b) for b in el["blocks"])
    if t == "tbl":
        return "\n".join(" | ".join(" ".join(texto_de(b) for b in c["blocks"]) for c in fila) for fila in el["rows"])
    return ""


def vista(elementos, sangria=""):
    """Vista legible con ids e inline markdown, para la revisión editorial."""
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
            lineas.append(f"{sangria}[{e['id']}] {pref}{runs_a_md(e['runs'])}")
        elif t == "cap":
            lineas.append(f"{sangria}[{e['id']}] PIE: {runs_a_md(e['runs'])}")
        elif t == "img":
            lineas.append(f"{sangria}[{e['id']}] (IMAGEN)")
        elif t == "box":
            lineas.append(f"{sangria}[{e['id']}] RECUADRO tipo={e.get('tipo', e['fill'])} >>>")
            lineas += vista(e["blocks"], sangria + "    ")
            lineas.append(f"{sangria}<<< fin recuadro {e['id']}")
        elif t == "tbl":
            lineas.append(f"{sangria}[{e['id']}] TABLA {len(e['rows'])}x{max(len(f) for f in e['rows'])} (fila r, columna c desde 0) >>>")
            for i, fila in enumerate(e["rows"]):
                celdas = []
                for c in fila:
                    celdas.append(" / ".join(
                        runs_a_md(b["runs"]) if b["t"] in ("p", "cap") else f"<{b['t']}>"
                        for b in c["blocks"]))
                lineas.append(f"{sangria}    r{i}: | " + " | ".join(celdas) + " |")
            lineas.append(f"{sangria}<<< fin tabla {e['id']}")
    return lineas


TIPOS_RECUADRO = {
    "FFF4E0": "aviso",      # naranja: precaución / seguridad
    "F4F4F4": "info",       # gris: antes de empezar, nota
    "EAF1F8": "practica",   # azul: enunciado de práctica
    "E8F3EA": "recuerda",   # verde: idea clave
}
