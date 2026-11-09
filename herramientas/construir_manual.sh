#!/usr/bin/env bash
# Construye el manual práctico de 20 horas (condensado/*.md) en dos pasadas.
set -euo pipefail
cd "$(dirname "$0")/.."
SOFFICE=${SOFFICE:-soffice}
PDFOPT='pdf:writer_pdf_Export:{"IsSkipEmptyPages":{"type":"boolean","value":"false"}}'
NOMBRE=salida/Manual_LOGO9
python3 herramientas/graficos.py
python3 herramientas/md2json.py condensado/*.md
rm -f trabajo/paginas_manual.json
for pasada in 1 2; do
  node herramientas/maquetar_manual.js --salida $NOMBRE.docx
  python3 herramientas/incrustar_fuentes.py $NOMBRE.docx
  $SOFFICE --headless --convert-to "$PDFOPT" --outdir salida $NOMBRE.docx >/dev/null
  python3 herramientas/paginar.py $NOMBRE.pdf trabajo/indice_manual.json trabajo/paginas_manual.json
done
echo "Manual: $NOMBRE.docx y $NOMBRE.pdf"
