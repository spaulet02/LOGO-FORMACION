# Edición condensada: manual práctico de 20 horas

Rol: editor/a y autor/a técnico/a sénior de una editorial con más de 25 años haciendo libros de
FP. Rehacemos el libro (772 páginas) como **manual práctico para una formación de 20 horas**
en un CFGS (Automatización y Robótica Industrial). Destino: unas **220 páginas** en total.
El texto fuente ya está revisado (sin zonas de IA): **es la única fuente de datos técnicos**.

## 1. Plan del libro

| Cap. | Título | Fuentes (trabajo/fuente/cap_XX.txt) | Palabras |
|---|---|---|---|
| | **Bloque I. El equipo y su puesta en marcha (4 h)** | | |
| 1 | LOGO! 9 y el puesto de trabajo | 00_intro, 01 | 2 500 |
| 2 | Montaje, alimentación y cableado de entradas y salidas | 02 (+ 14: cableado analógico básico) | 3 200 |
| 3 | Configuración inicial del módulo base | 03 (sin la parte de red) | 3 000 |
| 4 | Red y comunicación con el PC | 03 (red), 04, 05 (conexión y transferencia), 25 (plan de direcciones) | 3 000 |
| | **Bloque II. Programación con LOGO!Soft Comfort (6 h)** | | |
| 5 | LOGO!Soft Comfort: del programa al equipo | 04 (proyecto), 05 | 3 200 |
| 6 | Funciones lógicas y mando marcha-paro | 06, 07 | 3 400 |
| 7 | Temporizadores | 08 | 3 400 |
| 8 | Contadores, reloj y calendario | 09, 10 | 3 200 |
| 9 | Ampliaciones, secuencias y remanencia | 11, 12 | 3 000 |
| | **Bloque III. Señales analógicas (4 h)** | | |
| 10 | Entradas analógicas y escalado | 14, 15 | 3 200 |
| 11 | Comparar, vigilar y filtrar señales | 16, 17 | 3 200 |
| 12 | Salidas analógicas, regulación y cálculo | 18, 19 | 3 200 |
| | **Bloque IV. Pantallas: módulo base y LOGO! TDE 9 (4 h)** | | |
| 13 | Mensajes y mandos en la pantalla del módulo | 13 | 2 600 |
| 14 | LOGO! TDE 9: instalación, conexión y configuración | 20, 24 | 3 000 |
| 15 | Diseño de páginas en la TDE | 21 | 3 000 |
| 16 | Mandos, alarmas y navegación desde la TDE | 22, 23 | 3 200 |
| | **Bloque V. Comunicación avanzada y proyecto final (2 h)** | | |
| 17 | Comunicación entre equipos, servidor web y seguridad | 25, 26, 27 | 3 200 |
| 18 | Funciones de usuario (UDF) y registro de datos | 28, 26 (registro de datos) | 2 600 |
| 19 | Proyecto integrado y localización de averías | 31 (proyecto base), 29, 30, 32 (variantes), 33 (mantenimiento y averías) | 3 400 |
| A | Anexo A. Referencia de bloques de función | todos | 6 000 |

Límites de cada capítulo: el número de palabras indicado (±10 %), **3 a 6 figuras**, **2 a 5 tablas**,
**1 práctica guiada** (como mucho 2 si son muy cortas). Lo que no cabe se deja fuera; prioriza lo que
el alumno necesita para **programar y poner en marcha** el equipo.

## 2. Estructura fija de cada capítulo

```
# 7. Temporizadores

::: objetivos
**En este capítulo aprenderás a**
- …(3 a 5 objetivos, verbos de acción)
:::

Párrafo de entrada (2–4 frases): para qué sirve en la industria, con un ejemplo real.

## 7.1 …  (3 a 6 apartados numerados de teoría aplicada)
### 7.1.1 … (solo si hace falta)

::: practica
**Práctica 7.1. Título**
**Objetivo.** …
**Material.** …
Tabla de E/S, pasos numerados (montaje → programa en LSC → simulación → transferencia → prueba).
**Resultado esperado.** …
:::

::: recuerda
**Ideas clave**
- 4 a 6 ideas en una línea cada una.
:::

## 7.N Comprueba lo que has aprendido
1. … (4 a 6 preguntas cortas y una de aplicación)

::: soluciones
**Soluciones**
1. … (respuestas breves)
:::
```

Recuadros disponibles (`::: tipo`): `objetivos`, `practica`, `recuerda`, `seguridad`, `atencion`,
`nota`, `ejemplo`, `soluciones`, `profesor`. La primera línea en negrita es el título del recuadro.
Usa `seguridad` solo cuando hay un riesgo real, en 1–3 frases, con remisión a las normas del
capítulo 1 si es una norma general.

## 3. Formato (Markdown de pandoc)

- Títulos numerados: `# 7. Título`, `## 7.1 Título`, `### 7.1.1 Título`.
- Figuras: solas en su párrafo, reutilizando imágenes del libro fuente (las líneas `IMAGEN:`
  de la vista dan la ruta) con su pie renumerado:
  `![Figura 7.2. Cronograma del retardo a la conexión.](trabajo/img/b1/image92.png)`
  Antes de usar una figura, comprueba en la vista (su pie, justo debajo) que muestra lo que dices.
  Puedes abrir la imagen con la herramienta Read si dudas. No inventes figuras.
- Tablas: tablas de tuberías (pipe tables) con el pie **debajo** en la forma de pandoc:
  ```
  | Entrada | Elemento | Función |
  |---|---|---|
  | I1 | S1, pulsador NA | Marcha |

  : Tabla 7.1. Entradas y salidas de la práctica.
  ```
  Celdas cortas (una línea). Máximo 5 columnas.
- Negrita para rótulos de la interfaz (**Herramientas > Transferir > PC → LOGO!**) y términos
  nuevos la primera vez; `código` para direcciones y valores (`I1`, `Q2`, `B003`, `192.168.0.105`).
- Remisiones: «(capítulo 5)», «(apartado 7.2)», «tabla 7.1», «figura 7.2». Solo a capítulos del
  plan nuevo (sección 1). Nunca a la numeración del libro fuente.
- Sin citas a páginas del manual en el texto corrido. Al final del capítulo, antes de
  «Comprueba…», una línea: `**Para saber más.** Manual de sistema de LOGO! 9 (Siemens), apartados …`
  si es útil.

## 4. Estilo

- Tuteo, presente, voz activa, frases de 12–22 palabras. Explica el *porqué* en una frase y pasa
  al *cómo*. Pasos numerados para todo procedimiento.
- Nada de tics de texto generado (lee `.claude/skills/humanizer/SKILL.md`): sin «no es X, es Y»
  en serie, sin cierres efectistas, sin tríadas forzadas, sin metadiscurso («en este apartado
  veremos…» solo en la entrada del capítulo).
- Ni rastro de cómo se hizo el libro: nada de «previsto», «pendiente», «el libro propone»,
  «F01 no dice», Python, auditorías, ITECAM como autor de decisiones.
- Datos técnicos exactamente como en la fuente (valores, bornes, parámetros, rótulos). Si un dato
  no está en la fuente, no lo pongas.
- Ejemplo conductor del libro: el banco con S1 (marcha, I1), S0 (paro NC, I2), relé térmico F2
  (I3), KM1 (Q1), pilotos H1/H2, potenciómetro P1 en I7 (nivel del depósito). Mantenlo.

## 5. Entrega

Escribe cada capítulo en `condensado/cap_NN.md` (NN con dos cifras; anexo: `condensado/anexo_a.md`).
Comprueba al terminar:
`pandoc condensado/cap_NN.md -t plain | wc -w` (palabras) y que cada ruta de imagen existe
(`ls`). Responde con un resumen de 5 líneas: palabras, figuras, tablas, qué has dejado fuera.
