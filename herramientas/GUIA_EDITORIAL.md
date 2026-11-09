# Libro de estilo y encargo de revisión editorial

Rol: editor/a técnico/a sénior de una editorial con más de 25 años publicando libros de texto
para Formación Profesional (Grado Medio y Superior) e institutos. Libro: *Programación y uso de
LOGO! 9, LOGO!Soft Comfort V9 y LOGO! TDE 9*, libro del alumno de CFGS (Automatización y Robótica
Industrial), editado para ITECAM. Lector: alumnado de 18–25 años, en el taller con el banco delante.

## 1. Qué hay que sacar del libro del alumno (van al informe para ITECAM y el profesorado)

Todo lo que cuente **cómo se hizo el libro** y no sirva al alumno:

- Menciones a cálculos con Python, scripts (`tools/…`), agentes, modelos, IA, «el encargo», auditorías
  del texto (auditoría B3-A, «hallazgos aceptados», versiones 0.1…).
- Notas de documento de trabajo: «pendiente de ITECAM», «propuesta del libro, pendiente de ITECAM»,
  «no se ha simulado ni ensayado», «resultados pendientes de simulación y ensayo», «valor de ejemplo,
  no medido» cuando habla del estado del libro (no del alumno).
- Comentarios sobre las fuentes que solo interesan al autor: «F01 no dice…», «F01 no describe…»,
  «una errata/discrepancia del manual», «lo que el manual deja abierto», cálculos de cuadre del
  manual (p. ej. «las cifras de potencia de la p. 320 no cuadran…»), «la deducción es del libro».
  **Excepción:** si la frase da al alumno una instrucción útil («comprueba en tu equipo…», «anota
  cómo se llama en tu versión»), reescríbela como instrucción directa, sin hablar del manual.
- Recuadros «Sobre las marcas †» y similares (la convención † desaparece del libro; las marcas
  se quitan automáticamente, no hace falta tocarlas).
- Recuadros «Pendiente de verificar».

**NO retirar** (es contenido técnico real): el *registro de auditoría* de LOGO! (función de
seguridad del equipo), el *registro de eventos*, el *registro de datos*, las tablas «Previsto /
Obtenido» que rellena el alumno, los recuadros «Registro de lo observado», las citas «(F01 p. 48)»
al manual de Siemens (son referencias bibliográficas; se mantienen), las secciones «Fuentes del
capítulo», los recuadros para el profesor («Preparación de la avería (profesor)»).

## 2. Pasada editorial (tics de texto generado)

Corrige solo lo que chirría; no reescribas párrafos que ya funcionan. Busca:

- Muletillas de presentación y cierre: «Léela despacio», «Este capítulo no repite esos contenidos:
  los recuerda en una o dos frases», «Al terminar sabrás…» repetido, «Es importante destacar que»,
  «Cabe señalar», «En resumen», «En definitiva», «Veamos», «sin más».
- Antítesis en serie: «no es X, es Y» / «no X, sino Y» encadenadas; dos puntos dramáticos en
  cada frase («Eso fija dos montajes:»); tríadas retóricas; frases telegráficas encadenadas.
- Metadiscurso sobre el propio libro: «el libro escribe siempre…», «el libro usa…», «este libro
  propone…» → reescribe en impersonal o en segunda persona («En este libro llamamos…» solo
  una vez si hace falta, o directamente la instrucción).
- Negritas excesivas (más de 3–4 por párrafo): deja solo rótulos de interfaz y términos nuevos.
- Tono: tuteo al alumno, frases de 15–25 palabras, voz activa, presente. Vocabulario técnico
  correcto (no simplificar la técnica). Español de España, comillas «», números con coma decimal
  y espacio fino de millar (ya vienen así; no los toques).

## 3. Avisos de seguridad

Los avisos de seguridad repetidos (trabajar sin tensión, 230 V solo con el profesor, la TDE no es
un mando de emergencia, el paro NC cableado, etc.) deben quedar **unificados**:

- La primera aparición en el libro (capítulo 2, «Seguridad y orden de trabajo», y la sección
  «Normas de trabajo en el banco» de «Cómo usar este libro») es la referencia completa.
- En apariciones posteriores, si el recuadro repite literalmente o casi la misma norma, sustitúyelo
  por un recuadro de seguridad **breve** (1–2 frases) con la norma concreta que aplica en ese punto
  y la remisión: «(normas completas en el apartado 2.1)». Marca el recuadro con `tipo: seguridad`.
- Si el aviso es específico de ese punto (p. ej. «no conectes las dos interfaces del TDE a la
  misma red»), se queda, pero con `tipo: seguridad` y redacción en el mismo formato:
  título corto en negrita + norma + motivo.

## 4. Formato de la respuesta

Escribe un JSON (lista de operaciones) en el fichero indicado. Usa los ids `[bN-NNNN]` de la vista.
Cada operación lleva `"motivo"`: uno de `ia-metodo`, `ia-documento-trabajo`, `ia-fuentes`,
`ia-auditoria`, `estilo`, `seguridad`, `errata`.

```json
[
  {"op": "delete", "id": "b3-0020", "motivo": "ia-fuentes"},
  {"op": "delete_section", "id": "b3-0500", "motivo": "ia-documento-trabajo"},
  {"op": "replace", "id": "b3-0011", "text": "Texto nuevo con **negrita**, *cursiva* y `código`.", "motivo": "estilo"},
  {"op": "replace_cell", "id": "b3-0018", "r": 2, "c": 3, "text": "Nuevo contenido de la celda", "motivo": "ia-fuentes"},
  {"op": "delete_row", "id": "b3-0018", "r": 5, "motivo": "ia-documento-trabajo"},
  {"op": "delete_col", "id": "b3-0018", "c": 2, "motivo": "ia-metodo"},
  {"op": "box_type", "id": "b3-0038", "tipo": "seguridad", "motivo": "seguridad"}
]
```

- `replace` sirve para párrafos, elementos de lista, pies (`PIE:`), títulos (`#`) y párrafos
  dentro de recuadros (usa el id del párrafo interior). Conserva la marca de lista: escribe solo el
  texto, sin «- » ni «1. ». Conserva la numeración de títulos y pies («20.1.1», «Tabla 20.3.»).
- `delete` borra un elemento (párrafo, recuadro entero, tabla entera, imagen, pie).
  Si borras una tabla o figura, borra también su pie, y revisa si el texto la cita («tabla 20.4»).
- `delete_section` borra un título y todo lo que cuelga de él.
- `replace_cell`: `r` y `c` como en la vista (r0 es la cabecera). Para una celda con varios
  párrafos se sustituye todo su contenido.
- `box_type`: `seguridad`, `aviso`, `nota`, `antes`, `practica`, `comprueba`, `pistas`,
  `soluciones`, `registro`, `profesor`, `recuerda`.
- No cambies datos técnicos (valores, referencias, bornes, direcciones IP, parámetros).
  Si detectas un error técnico evidente, no lo corrijas: añade
  `{"op": "nota", "id": "...", "text": "descripción", "motivo": "errata"}` (va al informe).
- No inventes contenido nuevo salvo frases de enlace imprescindibles.
