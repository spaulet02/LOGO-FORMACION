"""Calcula el número de página de cada entrada del índice a partir del PDF de la primera pasada."""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def norm(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", t.lower())


def main(pdf, f_indice="trabajo/indice.json", f_salida="trabajo/paginas.json"):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    texto = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    paginas = [norm(re.sub(r"-\n\s*", "", p)) for p in texto.split("\f")][:n]
    indice = json.loads((RAIZ / f_indice).read_text(encoding="utf-8"))
    # el índice general ocupa las primeras páginas: empezamos tras la última página con «Índice general»
    inicio = max(i for i, p in enumerate(paginas[:40]) if "indicegeneral" in p) + 1
    res, actual, perdidas = {}, inicio, []
    res, actual, perdidas = {}, inicio, []
    secuencia = [e for e in indice if e["nivel"] < 4]
    sueltas = [e for e in indice if e["nivel"] == 4]
    for e in sueltas:   # prácticas: búsqueda independiente desde el inicio
        clave = norm(e["texto"])[:40]
        pag = next((i for i in range(inicio, len(paginas)) if clave and clave in paginas[i]), None)
        res[e["id"]] = (pag + 1) if pag is not None else 0
        if pag is None:
            perdidas.append(e["texto"])
    for e in secuencia:
        t = e["texto"]
        if e["nivel"] == 1:
            t = re.sub(r"^Bloque [IVX]+\.\s*", "", t)
        else:
            t = re.sub(r"^(Anexo [A-Z]\.|(\d+|[A-Z])(\.\d+)*\.?)\s*", "", t)
        clave = norm(t)[:40]
        encontrada = None
        for i in range(actual, len(paginas)):
            if clave and clave in paginas[i]:
                encontrada = i
                break
        if encontrada is None:
            perdidas.append(e["texto"])
            res[e["id"]] = actual + 1
        else:
            res[e["id"]] = encontrada + 1
            actual = encontrada
    (RAIZ / f_salida).write_text(json.dumps(res), encoding="utf-8")
    print(f"{len(res)} entradas paginadas; no localizadas: {len(perdidas)}", perdidas[:10])


if __name__ == "__main__":
    main(*sys.argv[1:])
