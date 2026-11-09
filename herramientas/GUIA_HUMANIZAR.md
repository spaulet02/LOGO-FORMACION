# Pasada de humanización del manual

El cliente dice que el manual «se nota demasiado que lo ha escrito una IA». Tu trabajo es reescribir
la prosa de tus capítulos (`condensado/cap_NN.md`) para que parezca escrita por un profesor de taller
con muchos años de FP que conoce el banco y a sus alumnos. **El contenido técnico no cambia**: valores,
bornes, parámetros, rótulos de menú, direcciones, números de bloque, numeración de apartados, figuras,
tablas y remisiones se conservan exactamente. Lee también `.claude/skills/humanizer/SKILL.md` (en
inglés; aplícalo al español).

## 1. Los dos puntos (petición expresa del cliente)

- **No uses «:» para presentar tablas, figuras, listas ni ejemplos.** Nada de «La tabla 4.2 resume los
  pasos:», «Hay dos casos:», «Fíjate en esto:». Escribe la frase completa y termínala con punto
  («La tabla 4.2 resume los pasos.») o integra la enumeración en la frase.
- **Nada de «Etiqueta: explicación»** ni en el texto ni en viñetas ni en celdas de tabla
  («Causa: el cable…», «Entradas: Trg y R»). Usa una frase normal o, en viñetas, **Etiqueta.** con punto
  solo si de verdad ayuda (como mucho una lista así por capítulo).
- Los dos puntos solo se admiten donde son notación: horas (`12:30`), formatos (`--:--`), relaciones
  (`1:1`), código y rótulos literales de la pantalla. Objetivo: casi cero «:» en la prosa.

## 2. Rasgos de texto generado que hay que quitar

- Frases todas de la misma longitud y párrafos todos con el mismo molde (afirmación + explicación +
  remate). Alterna frases cortas y largas; algún párrafo de una sola frase está bien.
- Antítesis en serie («no es X, es Y», «no solo… sino…»), tríadas forzadas, remates efectistas al final
  de párrafo, preguntas retóricas que se responden solas («¿Por qué? Porque…»).
- Muletillas: «Fíjate», «Recuerda que», «Es importante», «clave», «fundamental», «crucial»,
  «garantizar», «en definitiva», «de este modo», «así», «en la práctica», «la regla es», «la trampa»,
  «lo que importa es».
- Exceso de listas: si una lista explica ideas (no pasos), conviértela en uno o dos párrafos.
  Los pasos de un procedimiento sí van numerados.
- Exceso de negritas: como mucho dos por párrafo, solo para rótulos de interfaz y el término nuevo la
  primera vez que aparece.
- Metadiscurso («En este apartado veremos», «A continuación», «Como hemos visto»).
- Entradas de capítulo con plantilla («Al terminar sabrás…»): cada capítulo debe arrancar distinto,
  con una situación concreta del taller o de una instalación.

## 3. La voz

Tuteo, presente, claro y cercano, como un buen profesor que explica delante del banco. Puede dar un
consejo de oficio («Antes de transferir, guarda el proyecto con otro nombre; te ahorrará disgustos»),
pero nunca inventa datos, anécdotas con cifras ni nombres. Español de España, comillas «».

## 4. Ilustraciones nuevas

Hay esquemas nuevos de estilo editorial en `assets/ilustraciones/`. Coloca los de tus capítulos (lista
abajo) donde mejor expliquen el texto, como figuras normales, con su pie y citados en el texto, y
**renumera** las figuras del capítulo y sus remisiones. Ruta: `![Figura N.M. Pie.](assets/ilustraciones/nombre.png)`.
Los ficheros se están dibujando: no te preocupes si aún no existen.

| Capítulo | Fichero | Qué muestra |
|---|---|---|
| 1 | `ciclo_programa.png` | Ciclo del módulo en RUN: lee las entradas, ejecuta el programa, escribe las salidas y vuelve a empezar |
| 4 | `red_aula.png` | Red del puesto 05: PC 192.168.0.55, conmutador, módulo base 192.168.0.105 y TDE 192.168.0.205, máscara 255.255.255.0 |
| 5 | `flujo_lsc.png` | Programar en LSC → simular en el PC → transferir PC → LOGO! → comprobar con Test online |
| 7 | `ton_tof.png` | Cronogramas del retardo a la conexión y a la desconexión (Trg, Q y el tiempo T) |
| 10 | `escalado.png` | 0–10 V → valor interno 0–1000 → nivel 0–200 cm con Gain 0,20; ejemplo 5 V → 500 → 100 cm |
| 11 | `histeresis.png` | Nivel que oscila con los umbrales On y Off y la salida Q (Q = 1 por encima de On, Q = 0 por debajo de Off) |
| 12 | `lazo_pi.png` | Lazo de regulación: consigna SP, regulador PI, salida AQ, proceso y valor real PV que vuelve |
| 15 | `pagina_tde.png` | Partes de una página de la TDE: título, valor con unidad, barra y botón |
| 16 | `mando_tde.png` | Petición (tecla de la TDE) → permiso → orden (salida) → retorno (contacto del contactor) |
| 18 | `registro_datos.png` | Bloque de registro → búfer del módulo o tarjeta micro SD → fichero .CSV → navegador o LSC |

## 5. Entrega

Sobrescribe `condensado/cap_NN.md`. Después:
- `grep -c ':' condensado/cap_NN.md` antes y después (debe bajar mucho; revisa uno a uno los que queden),
- `pandoc condensado/cap_NN.md -t plain | wc -w` (puede bajar un 5–10 %, no subir),
- `python3 herramientas/comprobar_manual.py` sin errores nuevos en tus capítulos (las rutas de
  `assets/ilustraciones/` pueden aparecer como ausentes; ignóralo).
Responde con 3 líneas por capítulo: palabras antes/después, «:» antes/después, cambios principales.
