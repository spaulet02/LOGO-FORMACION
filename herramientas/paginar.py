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


def main(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    texto = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    paginas = [norm(re.sub(r"-\n\s*", "", p)) for p in texto.split("\f")][:n]
    indice = json.loads((RAIZ / "trabajo" / "indice.json").read_text(encoding="utf-8"))
    # el índice general ocupa las primeras páginas: empezamos tras la última página con «Índice general»
    inicio = max(i for i, p in enumerate(paginas[:40]) if "indicegeneral" in p) + 1
    res, actual, perdidas = {}, inicio, []
    for e in indice:
        t = e["texto"]
        if e["nivel"] == 1:
            t = re.sub(r"^Bloque [IVX]+\.\s*", "", t)
        else:
            t = re.sub(r"^\d+(\.\d+)*\.?\s*", "", t)
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
    (RAIZ / "trabajo" / "paginas.json").write_text(json.dumps(res), encoding="utf-8")
    print(f"{len(res)} entradas paginadas; no localizadas: {len(perdidas)}", perdidas[:10])


if __name__ == "__main__":
    main(sys.argv[1])
