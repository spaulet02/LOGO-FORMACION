# Revisión final de capítulos del manual (sin prácticas)

Eres editor/a de mesa sénior (25 años en libros de FP). El manual de 20 horas ya está redactado en
`condensado/cap_NN.md` (formato y estilo: `herramientas/GUIA_CONDENSADO.md`, léela). Por decisión del
cliente **el manual no lleva prácticas**: irán en un libro de prácticas aparte. Los recuadros
`::: practica` ya se han sacado automáticamente a `practicas/cap_NN.md` (consúltalos). Tu trabajo,
capítulo a capítulo, editando directamente `condensado/cap_NN.md`:

## 1. Cerrar el hueco de las prácticas
- Quita toda remisión a prácticas («en la práctica 7.1», «lo comprobarás en la práctica», «paso 10»,
  «Material», «Resultado esperado»…) y los objetivos, preguntas y soluciones que dependan de una práctica
  (reescríbelos para que dependan de la teoría).
- Si la práctica contenía algo **imprescindible para saber programar o configurar** (p. ej. la tabla
  de configuración de las páginas de mensaje, la secuencia de bloques de un mando), recupéralo como un
  recuadro `::: ejemplo` breve (título `**Ejemplo N.M. …**`, como mucho 250 palabras, una tabla y/o una
  figura). Un ejemplo explica cómo se resuelve; no manda hacer nada al alumno en el banco.
- Las tablas o figuras que solo tenían sentido para la práctica (E/S de la práctica, secuencias de prueba)
  se eliminan o pasan al ejemplo.
- Capítulo 19: el proyecto integrado pasa a ser un **caso resuelto** (`::: ejemplo` largo o apartados
  normales) que muestra cómo se diseña y programa la aplicación completa; el método de localización de
  averías y la tabla síntoma → causa → comprobación se quedan como teoría.

## 2. Coherencia
- Renumera figuras y tablas de forma consecutiva dentro de cada capítulo (Figura N.1, N.2…; Tabla N.1…)
  y corrige todas las remisiones del texto.
- Remisiones solo a capítulos y apartados que existen en el plan nuevo (comprueba los títulos con
  `grep '^#' condensado/*.md`). Nada de numeración del libro fuente (P36, capítulo 25 antiguo, etc.).
- Estructura de cada capítulo: objetivos → entrada → apartados → (ejemplos) → recuerda →
  «Comprueba lo que has aprendido» → soluciones. Si un capítulo queda por debajo de unas 2 300 palabras,
  no lo rellenes: está bien más corto.
- Estilo de la guía: tuteo, frases claras, sin tics de texto generado, sin rastro de cómo se hizo el libro.

## 3. Auditoría de las imágenes que usa cada capítulo
Abre con la herramienta Read **cada imagen** referenciada en tus capítulos. Busca rótulos que no deben
verse en el libro del alumno: notas de trabajo («pendiente…», «propuesta del libro», «cálculo del libro»,
«F01 p. …», «criterio del libro», «†»), y numeraciones del libro fuente («P36», «figura 23.7»,
«capítulo 4» cuando ya no corresponde, «cap. 5»). Para cada imagen con problemas añade una entrada en
`trabajo/imagenes_revision/cap_NN.json`:

```json
[{"file": "trabajo/img/b3/image12.png", "texto": "propuesta del libro",
  "cajas": [[x0, y0, x1, y1]], "accion": "tapar"}]
```

- `cajas` en **píxeles de la imagen original** (la herramienta Read indica el factor de escala:
  multiplica las coordenadas que veas). Deja 4–6 px de margen alrededor del texto.
- `accion`: `tapar` (se rellena con el color de fondo; úsalo cuando el rótulo es prescindible),
  o `quitar` (la figura no sirve: elimínala del capítulo y renumera).
- Si no hay problemas, escribe `[]`.

## 4. Entrega
Comprueba con `pandoc condensado/cap_NN.md -t plain | wc -w` y que no queda ninguna «práctica» en el
texto (`grep -i práctica`). Responde con 4 líneas por capítulo: palabras, figuras, tablas y cambios
importantes; y el número de imágenes marcadas.
