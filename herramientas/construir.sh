#!/usr/bin/env bash
# Construye el libro completo en dos pasadas (la segunda con el índice paginado).
set -euo pipefail
cd "$(dirname "$0")/.."
SOFFICE=${SOFFICE:-soffice}
PDFOPT='pdf:writer_pdf_Export:{"IsSkipEmptyPages":{"type":"boolean","value":"false"}}'
NOMBRE=salida/Libro_LOGO9_ITECAM
python3 herramientas/graficos.py
for n in 1 2 3 4 5; do python3 herramientas/extraer.py originales/BLOQUE_$n.docx $n; done
python3 herramientas/limpiar.py
python3 herramientas/aplicar.py
rm -f trabajo/paginas.json
node herramientas/maquetar.js --salida $NOMBRE.docx
python3 herramientas/incrustar_fuentes.py $NOMBRE.docx
$SOFFICE --headless --convert-to "$PDFOPT" --outdir salida $NOMBRE.docx >/dev/null
python3 herramientas/paginar.py $NOMBRE.pdf
node herramientas/maquetar.js --salida $NOMBRE.docx
python3 herramientas/incrustar_fuentes.py $NOMBRE.docx
$SOFFICE --headless --convert-to "$PDFOPT" --outdir salida $NOMBRE.docx >/dev/null
python3 herramientas/paginar.py $NOMBRE.pdf   # comprobación: debe coincidir
echo "Libro: $NOMBRE.docx y $NOMBRE.pdf"
