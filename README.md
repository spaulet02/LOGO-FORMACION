# Libro LOGO! 9 · LOGO!Soft Comfort V9 · LOGO! TDE 9 — edición y maquetación

Herramientas para montar, editar y maquetar el libro del alumno (5 bloques, 33 capítulos)
en un único Word A4 con páginas enfrentadas, y para generar el informe de trazabilidad
para ITECAM y el profesorado.

## Resultado

| Fichero | Contenido |
|---|---|
| `salida/Libro_LOGO9_ITECAM.docx` / `.pdf` | Libro del alumno maquetado (772 páginas) |
| `salida/Informe_ITECAM_trazabilidad.docx` / `.pdf` | Todo lo retirado del libro: registros de verificación, auditorías, notas de trabajo, erratas, rótulos † y procedencia de figuras |

Los originales (`originales/`), el material intermedio (`trabajo/`) y los resultados
(`salida/`, `informe/`) no se suben al repositorio porque es público: contienen el texto del libro.

## Diseño

- A4, márgenes simétricos (interior 2,7 cm, exterior 2,0 cm, superior 2,5 cm, inferior 2,4 cm).
- Capítulos y portadillas en página impar; cabecera par con el título del libro, impar con el capítulo.
- Montserrat en todo el documento, incrustada en el .docx (licencia OFL, `assets/fuentes/OFL.txt`).
- Paleta del logotipo de ITECAM: azul `#19233E`, amarillo `#F5C400` y grises neutros.
- Recuadros tipificados: seguridad, atención, práctica, comprueba, antes de empezar, pistas, soluciones,
  registro, para el profesorado.
- Control de viudas y huérfanas, títulos unidos al texto siguiente, filas de tabla sin partir,
  cabecera de tabla repetida, figuras unidas a su pie, guionado automático en español.
- Índice general con números de página reales (dos pasadas) e hipervínculos.

## Proceso

```bash
herramientas/construir.sh
```

1. `extraer.py` lee cada bloque .docx (estilos, listas, tablas, recuadros, imágenes) a JSON.
2. `limpiar.py` retira automáticamente las zonas de trabajo (registros de verificación,
   correcciones de auditoría, portadas «documento de trabajo», etiquetas de procedencia).
3. Revisión editorial por capítulos según `herramientas/GUIA_EDITORIAL.md` y la skill
   `humanizer` (`.claude/skills/humanizer`, de github.com/blader/humanizer, MIT).
   Las decisiones quedan como operaciones en `trabajo/ops/cap_XX.json`.
4. `aplicar.py` aplica las operaciones, quita las marcas †, unifica la remisión de seguridad
   y renumera tablas y figuras.
5. `maquetar.js` (docx-js) compone el libro; `incrustar_fuentes.py` incrusta Montserrat;
   `paginar.py` calcula las páginas del índice a partir del PDF.
6. `informe.py` genera el informe para ITECAM.

Requisitos: Node con `docx`, Python 3 con `python-docx` y Pillow, LibreOffice y Poppler.
