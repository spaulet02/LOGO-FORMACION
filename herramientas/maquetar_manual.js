// Maquetador del libro: JSON intermedio (trabajo/bN.final.json) -> salida/*.docx
// Uso: node herramientas/maquetar.js [--paginas trabajo/paginas.json] [--salida salida/libro.docx]
"use strict";
const fs = require("fs");
const path = require("path");
const d = require("docx");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, WidthType, BorderStyle, ShadingType, SectionType, PageNumber, LevelFormat,
  TabStopType, HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom, TextWrappingType,
  InternalHyperlink, Bookmark, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo,
  PositionalTabLeader, VerticalAlign, TableLayoutType, HeightRule,
} = d;

const RAIZ = path.resolve(__dirname, "..");
const args = process.argv.slice(2);
const opt = (k, def) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : def; };
const LIBRO = JSON.parse(fs.readFileSync(path.join(RAIZ, "libro_manual.json"), "utf8"));
const TAM = JSON.parse(fs.readFileSync(path.join(RAIZ, "trabajo/tam_imagenes.json"), "utf8"));
const PAGINAS = fs.existsSync(path.join(RAIZ, opt("--paginas", "trabajo/paginas_manual.json")))
  ? JSON.parse(fs.readFileSync(path.join(RAIZ, opt("--paginas", "trabajo/paginas_manual.json")), "utf8")) : {};
const SALIDA = path.join(RAIZ, opt("--salida", "salida/Manual_LOGO9.docx"));
const SUFIJO = opt("--fuente", "final"); // final | limpio

// ---------------------------------------------------------------- diseño
const C = {
  navy: "19233E", navy2: "2C3A5E", yellow: "F5C400", gris: "5F6676", grisClaro: "BFC5D2",
  fondo: "F3F4F7", fondoAzul: "EDF0F6", texto: "1E1E1E", blanco: "FFFFFF",
  aviso: "E0A100", fondoAviso: "FFF6DD", seg: "C8102E", fondoSeg: "FDEDEE",
  verde: "4F7F4E", fondoVerde: "EEF4EE",
};
const F = { cuerpo: "Montserrat", sans: "Montserrat", mono: "Consolas" };
const CM = 567;                              // dxa por cm
const PAG = { w: 11906, h: 16838 };          // A4
const MARG = { top: Math.round(2.5 * CM), bottom: Math.round(2.4 * CM), inside: Math.round(2.7 * CM),
  outside: Math.round(2.0 * CM), header: Math.round(1.2 * CM), footer: Math.round(1.1 * CM) };
const ANCHO = PAG.w - MARG.inside - MARG.outside;     // caja de texto en dxa
const PX = (dxa) => Math.round(dxa / 1440 * 96);      // dxa -> px (96 ppp)
const EMU = (cm) => Math.round(cm * 360000);

// ---------------------------------------------------------------- utilidades de texto
function runsDe(runs, base = {}) {
  const out = [];
  for (const r of runs || []) {
    let x = (r.x || "").replace(/\t/g, " ");
    const partes = x.split("\n");
    partes.forEach((p, i) => {
      const o = { text: p, font: base.font || F.cuerpo, size: base.size, color: base.color, bold: base.bold || !!r.b,
        italics: base.italics || !!r.i, break: i > 0 ? 1 : undefined };
      if (r.code) { o.font = F.mono; o.size = Math.max(13, (base.size || 19) - 2); o.shading = { type: ShadingType.CLEAR, fill: "EEF0F4", color: "auto" }; }
      if (r.sup) o.superScript = true;
      if (r.sub) o.subScript = true;
      out.push(new TextRun(o));
    });
  }
  return out;
}
const plano = (runs) => (runs || []).map((r) => r.x).join("");

function cortarTitulo(t, max = 62) {
  if (t.length <= max) return t;
  const i = t.indexOf(":");
  if (i > 10 && i <= max) return t.slice(0, i);
  return t.slice(0, max).replace(/\s+\S*$/, "") + "…";
}

// ---------------------------------------------------------------- numeración de listas
let instanciaLista = 0;
const numbering = {
  config: [
    { reference: "vinetas", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "▪", alignment: AlignmentType.LEFT,
        style: { run: { color: C.navy2, font: "Arial" }, paragraph: { indent: { left: 397, hanging: 255 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT,
        style: { run: { color: C.navy2 }, paragraph: { indent: { left: 794, hanging: 255 } } } } ] },
    { reference: "numeros", levels: [
      { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { run: { color: C.navy, bold: true, font: F.sans }, paragraph: { indent: { left: 397, hanging: 340 } } } },
      { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2)", alignment: AlignmentType.LEFT,
        style: { run: { color: C.navy2, font: F.sans }, paragraph: { indent: { left: 794, hanging: 340 } } } } ] },
  ],
};

// ---------------------------------------------------------------- imágenes
const cacheImg = new Map();
function leerImagen(rel) {
  const opt = rel.replace("trabajo/img/", "trabajo/img_opt/");
  if (!cacheImg.has(rel)) cacheImg.set(rel, fs.readFileSync(path.join(RAIZ, fs.existsSync(path.join(RAIZ, opt)) ? opt : rel)));
  return cacheImg.get(rel);
}
function tamPng(buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; }

function figura(el, anchoMax = ANCHO, altoMaxCm = 17.5) {
  const buf = leerImagen(el.file);
  const t0 = TAM[el.file] || [el.cx, el.cy];
  let wcm = t0[0] ? t0[0] / 360000 : 12, hcm = t0[1] ? t0[1] / 360000 : 8;
  if (!t0[0]) { const s = tamPng(buf); hcm = wcm * s.h / s.w; }
  const maxW = anchoMax / CM;
  if (wcm > maxW) { hcm *= maxW / wcm; wcm = maxW; }
  if (hcm > altoMaxCm) { wcm *= altoMaxCm / hcm; hcm = altoMaxCm; }
  return new Paragraph({
    alignment: AlignmentType.CENTER, keepNext: true, keepLines: true,
    spacing: { before: 160, after: 60 },
    children: [new ImageRun({ type: "png", data: buf,
      transformation: { width: Math.round(wcm / 2.54 * 96), height: Math.round(hcm / 2.54 * 96) } })],
  });
}

// ---------------------------------------------------------------- bloques de texto
function parrafo(el, ctx = {}) {
  const base = ctx.base || {};
  const o = {
    style: ctx.style || "Cuerpo",
    children: runsDe(el.runs, base),
    keepNext: !!ctx.keepNext,
  };
  if (el.list) {
    if (el.list.kind === "bullet") o.numbering = { reference: "vinetas", level: Math.min(el.list.lvl, 1) };
    else o.numbering = { reference: "numeros", level: Math.min(el.list.lvl, 1), instance: ctx.instancia };
    o.style = ctx.styleLista || "Lista";
  }
  if (el.center) o.alignment = AlignmentType.CENTER;
  return new Paragraph(o);
}

function pie(el, tipo) {
  // «Tabla 20.1.» / «Figura 20.1.» en negrita azul; resto en gris oscuro
  const txt = plano(el.runs);
  const m = txt.match(/^((Tabla|Figura|Fig\.)\s+[\dA-Z]+(\.\d+)*\.?)\s*/);
  const hijos = [];
  if (m) {
    hijos.push(new TextRun({ text: m[1] + " ", bold: true, color: C.navy, font: F.sans, size: 16 }));
    let resto = m[0].length;
    const runs = JSON.parse(JSON.stringify(el.runs));
    while (resto > 0 && runs.length) {
      if (runs[0].x.length <= resto) { resto -= runs[0].x.length; runs.shift(); }
      else { runs[0].x = runs[0].x.slice(resto); resto = 0; }
    }
    hijos.push(...runsDe(runs, { font: F.sans, size: 16, color: "3A3F4B" }));
  } else hijos.push(...runsDe(el.runs, { font: F.sans, size: 16, color: "3A3F4B" }));
  return new Paragraph({ style: tipo === "tabla" ? "PieTabla" : "PieFigura", children: hijos,
    keepNext: tipo === "tabla", keepLines: true });
}

// listas: una instancia nueva por cada lista numerada contigua
function bloques(lista, ctx = {}) {
  const out = [];
  let prevLista = false;
  let inst = 0;
  for (let i = 0; i < lista.length; i++) {
    const el = lista[i];
    const sig = lista[i + 1];
    if (el.t === "p" && el.list && el.list.kind === "num" && el.list.lvl === 0 && !prevLista) inst = ++instanciaLista;
    prevLista = el.t === "p" && !!el.list;
    switch (el.t) {
      case "h": out.push(...titulo(el, ctx)); break;
      case "p": out.push(parrafo(el, { ...ctx, instancia: inst, keepNext: sig && (sig.t === "img" || (sig.t === "p" && sig.list && !el.list && /:\s*$/.test(plano(el.runs)))) })); break;
      case "img": out.push(figura(el, ctx.ancho || ANCHO)); break;
      case "cap": {
        const esTabla = /^Tabla/i.test(plano(el.runs).trim());
        out.push(pie(el, esTabla ? "tabla" : "figura")); break;
      }
      case "box": out.push(recuadro(el, ctx)); out.push(new Paragraph({ style: "Separador" })); break;
      case "tbl": out.push(tabla(el, ctx)); out.push(new Paragraph({ style: "Separador" })); break;
      default: break;
    }
  }
  return out;
}

// ---------------------------------------------------------------- títulos
let marcadores = 0;
const indice = [];      // entradas del índice general
const practicas = [];   // índice de prácticas
let estado = { bloque: null, capitulo: null };

function idMarcador() { marcadores += 1; return `_t${String(marcadores).padStart(4, "0")}`; }

function titulo(el, ctx) {
  const lvl = el.lvl;
  if (lvl === 1) return []; // los capítulos se crean en apertura()
  const id = idMarcador();
  const estilo = lvl === 2 ? "Heading2" : lvl === 3 ? "Heading3" : "Heading4";
  if (lvl === 2) indice.push({ nivel: 3, texto: el.text, id });
  const m = el.text.match(/^((?:\d+|[A-Z])(?:\.\d+)+\.?)\s+(.*)$/);
  let hijos;
  if (m && lvl === 2) hijos = [new TextRun({ text: "\u00A0" + m[1] + "\u00A0", color: C.blanco, shading: { type: ShadingType.CLEAR, fill: C.navy, color: "auto" } }),
    new TextRun({ text: "\u2002" + m[2] })];
  else if (m) hijos = [new TextRun({ text: m[1] + "\u2002", color: C.navy }), new TextRun({ text: m[2] })];
  else hijos = [new TextRun({ text: el.text })];
  return [new Paragraph({ style: estilo, children: [new Bookmark({ id, children: hijos })] })];
}

// ---------------------------------------------------------------- recuadros
const ESTILO_RECUADRO = {
  objetivos: { barra: C.yellow, fondo: C.fondoAzul, etiqueta: null, color: C.navy },
  atencion:  { barra: C.aviso, fondo: C.fondoAviso, etiqueta: "ATENCIÓN", color: "8A6200" },
  ejemplo:   { barra: C.navy2, fondo: C.blanco, etiqueta: "EJEMPLO", color: C.navy2 },
  seguridad: { barra: C.seg, fondo: C.fondoSeg, etiqueta: "⚠ SEGURIDAD", color: C.seg },
  aviso:     { barra: C.aviso, fondo: C.fondoAviso, etiqueta: "ATENCIÓN", color: "8A6200" },
  nota:      { barra: C.grisClaro, fondo: C.fondo, etiqueta: null, color: C.navy2 },
  antes:     { barra: C.yellow, fondo: C.fondo, etiqueta: null, color: C.navy },
  pistas:    { barra: C.grisClaro, fondo: C.fondo, etiqueta: null, color: C.navy2 },
  comprueba: { barra: C.navy, fondo: C.fondoAzul, etiqueta: null, color: C.navy },
  soluciones:{ barra: C.verde, fondo: C.fondoVerde, etiqueta: null, color: C.verde },
  recuerda:  { barra: C.verde, fondo: C.fondoVerde, etiqueta: null, color: C.verde },
  registro:  { borde: C.grisClaro, fondo: C.blanco, etiqueta: null, color: C.navy2 },
  profesor:  { borde: C.gris, fondo: C.blanco, etiqueta: "PARA EL PROFESORADO", color: C.gris, discontinuo: true },
  practica:  { cabecera: true, fondo: C.fondoAzul, color: C.blanco },
};

const SIN = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function longitud(el) {
  if (el.t === "p" || el.t === "cap") return plano(el.runs).length;
  if (el.t === "img") return 1500;
  if (el.t === "tbl") return el.rows.length * 120;
  if (el.t === "box") return el.blocks.reduce((a, b) => a + longitud(b), 0);
  return 50;
}

function recuadro(el, ctx) {
  const tipo = el.tipo || "nota";
  const st = ESTILO_RECUADRO[tipo] || ESTILO_RECUADRO.nota;
  const bl = el.blocks.slice();
  // título: primer párrafo corto o totalmente en negrita
  let tit = null;
  if (bl.length > 1 && bl[0].t === "p" && !bl[0].list) {
    const t0 = plano(bl[0].runs);
    const todoNegrita = bl[0].runs.every((r) => r.b || !r.x.trim());
    if (todoNegrita || t0.length < 90) tit = bl.shift();
  }
  const anchoInt = ANCHO - 2 * 200 - 120;
  const cuerpo = bloques(bl, { ...ctx, style: "CuerpoRecuadro", styleLista: "ListaRecuadro", ancho: anchoInt,
    base: { font: F.sans, size: 17 } });
  const corto = longitud(el) < 1400;
  const filas = [];
  let idPract = null;
  if (tipo === "practica" && tit) { idPract = idMarcador(); practicas.push({ texto: plano(tit.runs).replace(/\s+/g, " ").trim(), id: idPract }); }
  const titPar = (color) => new Paragraph({ style: "TituloRecuadro", keepNext: true,
    children: idPract ? [new Bookmark({ id: idPract, children: [
      ...runsDe(tit.runs, { font: F.sans, bold: true, color, size: 20 })] })] : [
      ...(st.etiqueta ? [new TextRun({ text: st.etiqueta + (tit ? "  ·  " : ""), color: st.color, bold: true, size: 16, characterSpacing: 10 })] : []),
      ...(tit ? runsDe(tit.runs, { font: F.sans, bold: true, color, size: 20 }) : []),
    ] });

  const margenes = { top: 110, bottom: 110, left: 200, right: 200 };
  if (st.cabecera) {
    filas.push(new TableRow({ cantSplit: true, children: [new TableCell({
      width: { size: ANCHO, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: C.navy, color: "auto" },
      margins: { top: 90, bottom: 90, left: 200, right: 200 },
      borders: { top: SIN, bottom: SIN, left: SIN, right: SIN },
      children: [titPar(C.blanco)] })] }));
    filas.push(new TableRow({ cantSplit: corto, children: [new TableCell({
      width: { size: ANCHO, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: st.fondo, color: "auto" },
      margins: margenes, borders: { top: SIN, left: SIN, right: SIN, bottom: { style: BorderStyle.SINGLE, size: 12, color: C.navy } },
      children: cuerpo.length ? cuerpo : [new Paragraph("")] })] }));
    return new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [ANCHO], layout: TableLayoutType.FIXED, rows: filas });
  }
  const hijos = [];
  if (tit || st.etiqueta) hijos.push(titPar(st.color));
  hijos.push(...cuerpo);
  let bordes;
  if (st.barra) bordes = { top: SIN, bottom: SIN, right: SIN, left: { style: BorderStyle.SINGLE, size: 36, color: st.barra } };
  else {
    const b = { style: st.discontinuo ? BorderStyle.DASHED : BorderStyle.SINGLE, size: 6, color: st.borde };
    bordes = { top: b, bottom: b, left: b, right: b };
  }
  filas.push(new TableRow({ cantSplit: corto, children: [new TableCell({
    width: { size: ANCHO, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: st.fondo, color: "auto" },
    margins: margenes, borders: bordes, children: hijos.length ? hijos : [new Paragraph("")] })] }));
  return new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [ANCHO], layout: TableLayoutType.FIXED, rows: filas });
}

// ---------------------------------------------------------------- tablas
function tabla(el, ctx) {
  const ancho = ctx.ancho || ANCHO;
  const ncols = Math.max(el.grid.length, ...el.rows.map((f) => f.reduce((a, c) => a + (c.span || 1), 0)));
  let grid = el.grid.length === ncols ? el.grid.slice() : Array(ncols).fill(1);
  const suma = grid.reduce((a, b) => a + b, 0) || 1;
  grid = grid.map((g) => Math.floor(g / suma * ancho));
  grid[grid.length - 1] += ancho - grid.reduce((a, b) => a + b, 0);
  const tam = ncols >= 9 ? 13 : ncols >= 7 ? 14 : 15;          // medios puntos
  const borde = { style: BorderStyle.SINGLE, size: 4, color: C.grisClaro };
  const hdr = el.hdr || 0;
  const filas = el.rows.map((fila, ri) => {
    const esCab = ri < hdr;
    let col = 0;
    const celdas = fila.map((c) => {
      const span = c.span || 1;
      const w = grid.slice(col, col + span).reduce((a, b) => a + b, 0);
      col += span;
      const fill = esCab ? C.navy : (ri - hdr) % 2 === 1 ? C.fondo : C.blanco;
      const contenido = bloques(c.blocks, { ...ctx, style: esCab ? "CeldaCab" : "Celda", styleLista: "CeldaLista", ancho: w - 160,
        base: { font: F.sans, size: tam, color: esCab ? C.blanco : undefined, bold: esCab || undefined } });
      const o = { width: { size: w, type: WidthType.DXA }, columnSpan: span > 1 ? span : undefined,
        shading: { type: ShadingType.CLEAR, fill, color: "auto" }, verticalAlign: esCab ? VerticalAlign.CENTER : VerticalAlign.TOP,
        margins: { top: 50, bottom: 50, left: 80, right: 80 },
        borders: { top: borde, bottom: borde, left: SIN, right: SIN },
        children: contenido.length ? contenido : [new Paragraph({ style: "Celda" })] };
      if (c.vmerge) o.verticalMerge = c.vmerge === "restart" ? "restart" : "continue";
      return new TableCell(o);
    });
    return new TableRow({ children: celdas, tableHeader: esCab, cantSplit: true });
  });
  return new Table({ width: { size: ancho, type: WidthType.DXA }, columnWidths: grid, layout: TableLayoutType.FIXED, rows: filas,
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: C.navy }, bottom: { style: BorderStyle.SINGLE, size: 8, color: C.navy },
      left: SIN, right: SIN, insideHorizontal: borde, insideVertical: SIN } });
}

// ---------------------------------------------------------------- cabeceras y pies
function rotuloCab(texto, derecha) {
  return new Paragraph({ style: "Cabecera", alignment: derecha ? AlignmentType.RIGHT : AlignmentType.LEFT,
    children: [new TextRun({ text: texto })] });
}
function pieNum(derecha) {
  const num = new TextRun({ children: [PageNumber.CURRENT], bold: true, color: C.navy, size: 20, font: F.sans });
  const sep = new TextRun({ text: "   ■   ", color: C.yellow, size: 14 });
  const marca = new TextRun({ text: "ITECAM", color: C.gris, size: 15, font: F.sans, characterSpacing: 20 });
  return new Paragraph({ style: "Pie", alignment: derecha ? AlignmentType.RIGHT : AlignmentType.LEFT,
    children: derecha ? [marca, sep, num] : [num, sep, marca] });
}
function pestana(et, pos, lado) {
  const w = 1.2, h = 2.8;
  return new ImageRun({ type: "png", data: fs.readFileSync(path.join(RAIZ, `assets/generados/pestana_${et}_${lado}.png`)),
    transformation: { width: Math.round(w / 2.54 * 96), height: Math.round(h / 2.54 * 96) },
    floating: { horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: lado === "der" ? EMU(21 - w) : 0 },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: EMU(5.2 + (pos - 1) * 3.0) },
      behindDocument: false, allowOverlap: true, lockAnchor: true, layoutInCell: false, wrap: { type: TextWrappingType.NONE } } });
}
function cabecerasCapitulo(textoImpar, textoPar, tab) {
  const cab = (texto, der, conTab) => new Paragraph({ style: "Cabecera", alignment: der ? AlignmentType.RIGHT : AlignmentType.LEFT,
    children: [...(tab && conTab ? [pestana(tab.et, tab.pos, der ? "der" : "izq")] : []), new TextRun({ text: texto })] });
  return {
    headers: {
      default: new Header({ children: [cab(textoImpar, true, true)] }),
      even: new Header({ children: [cab(textoPar || LIBRO.cabecera_par, false, true)] }),
      first: new Header({ children: [new Paragraph({ children: tab ? [pestana(tab.et, tab.pos, "der")] : [] })] }),
    },
    footers: {
      default: new Footer({ children: [pieNum(true)] }),
      even: new Footer({ children: [pieNum(false)] }),
      first: new Footer({ children: [pieNum(true)] }),
    },
  };
}
const vacias = () => ({
  headers: { default: new Header({ children: [new Paragraph("")] }), even: new Header({ children: [new Paragraph("")] }), first: new Header({ children: [new Paragraph("")] }) },
  footers: { default: new Footer({ children: [new Paragraph("")] }), even: new Footer({ children: [new Paragraph("")] }), first: new Footer({ children: [new Paragraph("")] }) },
});

const propsPagina = (tipo, titlePage = true) => ({
  type: tipo,
  titlePage,
  page: { size: { width: PAG.w, height: PAG.h },
    margin: { top: MARG.top, bottom: MARG.bottom, left: MARG.inside, right: MARG.outside, header: MARG.header, footer: MARG.footer, gutter: 0 } },
});

function fondo(rel) {
  return new ImageRun({ type: "png", data: fs.readFileSync(path.join(RAIZ, rel)),
    transformation: { width: Math.round(21 / 2.54 * 96), height: Math.round(29.7 / 2.54 * 96) },
    floating: { horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: 0 },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: 0 },
      behindDocument: true, allowOverlap: true, lockAnchor: true, layoutInCell: false,
      wrap: { type: TextWrappingType.NONE } } });
}
const esp = (pt) => new Paragraph({ spacing: { before: 0, after: 0, line: Math.max(20, Math.round(pt * 20)), lineRule: "exact" }, children: [] });

// ---------------------------------------------------------------- páginas especiales
function portada() {
  return {
    properties: propsPagina(SectionType.NEXT_PAGE),
    ...vacias(),
    children: [new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: "exact" }, children: [fondo("assets/generados/portada_completa.png")] })],
  };
}

function creditos() {
  const lin = (t, o = {}) => new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: t, font: F.sans, size: 17, color: C.gris, ...o })] });
  return {
    properties: propsPagina(SectionType.NEXT_PAGE),
    ...vacias(),
    children: [
      esp(430),
      lin(LIBRO.titulo, { bold: true, color: C.navy, size: 19 }),
      lin(LIBRO.subtitulo),
      lin(LIBRO.tipo),
      esp(10),
      lin(LIBRO.edicion),
      esp(10),
      lin("LOGO!, LOGO!Soft Comfort y SIMATIC son marcas registradas de Siemens AG. Los datos técnicos proceden del manual de sistema de LOGO! 9 de Siemens; consúltalo siempre en la edición correspondiente a tu equipo."),
      lin("Este libro se ha preparado para la docencia. Ninguna práctica sustituye a las instrucciones del fabricante ni a las normas de seguridad del centro: trabaja siempre bajo la supervisión del profesorado."),
      lin("Queda prohibida la reproducción total o parcial de esta obra sin autorización del editor, salvo para uso docente en los centros asociados."),
    ],
  };
}

function entradaIndice(e) {
  const pag = PAGINAS[e.id] !== undefined ? String(PAGINAS[e.id]) : "000";
  const estilos = { 1: "Indice1", 2: "Indice2", 3: "Indice3" };
  const textoRuns = [];
  if (e.nivel === 1) textoRuns.push(new TextRun({ text: e.texto.toUpperCase() }));
  else {
    const m = e.texto.match(/^((?:\d+|[A-Z])(?:\.\d+)*\.?)\s+(.*)$/) || e.texto.match(/^(Anexo [A-Z]\.)\s+(.*)$/);
    if (m) { m[3] = m[m.length - 1]; }
    if (m) { textoRuns.push(new TextRun({ text: m[1], bold: e.nivel === 2 })); textoRuns.push(new TextRun({ text: "\t" + m[3] })); }
    else textoRuns.push(new TextRun({ text: (e.nivel === 3 ? "\t" : "") + e.texto }));
  }
  return new Paragraph({ style: estilos[e.nivel], tabStops: [
    ...(e.nivel === 2 ? [{ type: TabStopType.LEFT, position: 454 }] : e.nivel === 3 ? [{ type: TabStopType.LEFT, position: 1134 }] : []),
    { type: TabStopType.RIGHT, position: ANCHO, leader: e.nivel === 1 ? "none" : "dot" }], children: [
    new InternalHyperlink({ anchor: e.id, children: [...textoRuns,
      new TextRun({ text: "\t" + pag, bold: e.nivel <= 2 })] })] });
}

function paginaIndice(entradas) {
  return {
    properties: propsPagina(SectionType.ODD_PAGE),
    headers: { default: new Header({ children: [rotuloCab("Índice general", true)] }), even: new Header({ children: [rotuloCab(LIBRO.cabecera_par, false)] }), first: new Header({ children: [new Paragraph("")] }) },
    footers: { default: new Footer({ children: [pieNum(true)] }), even: new Footer({ children: [pieNum(false)] }), first: new Footer({ children: [pieNum(true)] }) },
    children: [
      new Paragraph({ style: "TituloEspecial", children: [new TextRun("Índice general")] }),
      ...entradas.map(entradaIndice),
      new Paragraph({ style: "TituloEspecial", pageBreakBefore: true, children: [new TextRun("Índice de prácticas")] }),
      ...practicas.map((p) => {
        const pag = PAGINAS[p.id] !== undefined ? String(PAGINAS[p.id]) : "000";
        const m = p.texto.match(/^(Práctica\s+[\d.]+\.?)\s*(.*)$/);
        return new Paragraph({ style: "Indice2", keepNext: false, tabStops: [{ type: TabStopType.LEFT, position: 1531 }, { type: TabStopType.RIGHT, position: ANCHO, leader: "dot" }],
          children: [new InternalHyperlink({ anchor: p.id, children: [
            new TextRun({ text: m ? m[1] : p.texto, bold: true }), new TextRun({ text: m ? "\t" + m[2] : "" }), new TextRun({ text: "\t" + pag, bold: true })] })] });
      }),
    ],
  };
}

function portadilla(b, capitulos) {
  const id = idMarcador();
  indice.push({ nivel: 1, texto: `Bloque ${b.romano}. ${b.titulo}`, id });
  return {
    properties: propsPagina(SectionType.ODD_PAGE),
    ...vacias(),
    children: [
      new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: "exact" }, children: [fondo("assets/generados/portadilla.png")] }),
      esp(40),
      new Paragraph({ spacing: { after: 0 }, children: [new Bookmark({ id, children: [new TextRun({ text: "BLOQUE", font: F.sans, size: 26, bold: true, color: C.yellow, characterSpacing: 60 })] })] }),
      new Paragraph({ spacing: { after: 120, line: 240, lineRule: "auto" }, children: [new TextRun({ text: b.romano, font: F.sans, size: 140, bold: true, color: C.blanco })] }),
      new Paragraph({ spacing: { after: 120, line: 240, lineRule: "auto" }, children: [new TextRun({ text: b.titulo, font: F.sans, size: 48, bold: true, color: C.blanco })] }),
      new Paragraph({ children: [new TextRun({ text: `${b.horas} horas · capítulos ${b.caps[0]} a ${b.caps[b.caps.length - 1]}`, font: F.sans, size: 22, color: "C9CFDD" })] }),
      esp(150),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "EN ESTE BLOQUE", font: F.sans, size: 18, bold: true, color: C.gris, characterSpacing: 40 })] }),
      ...capitulos.map((c) => {
        const m = c.match(/^(\d+)\.\s*(.*)$/);
        return new Paragraph({ spacing: { after: 90 }, indent: { left: 680, hanging: 680 }, tabStops: [{ type: TabStopType.LEFT, position: 680 }],
          children: [new TextRun({ text: m ? m[1] : "", font: F.sans, size: 26, bold: true, color: C.navy }),
            new TextRun({ text: "\t" + (m ? m[2] : c), font: F.sans, size: 22, color: C.texto })] });
      }),
    ],
  };
}

function apertura(el, etiqueta) {
  // apertura de capítulo: banda azul a sangre con número y título en blanco
  const id = idMarcador();
  indice.push({ nivel: 2, texto: el.text, id });
  const m = el.text.match(/^(\d+)\.\s*(.*)$/) || el.text.match(/^Anexo ([A-Z])\.\s*(.*)$/);
  const banda = new ImageRun({ type: "png", data: fs.readFileSync(path.join(RAIZ, "assets/generados/banda_capitulo.png")),
    transformation: { width: Math.round(21 / 2.54 * 96), height: Math.round(8.5 / 2.54 * 96) },
    floating: { horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: 0 },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: 0 },
      behindDocument: true, allowOverlap: true, lockAnchor: true, layoutInCell: false, wrap: { type: TextWrappingType.NONE } } });
  const celda = new TableCell({ width: { size: ANCHO, type: WidthType.DXA }, verticalAlign: VerticalAlign.BOTTOM,
    borders: { top: SIN, bottom: SIN, left: SIN, right: SIN }, margins: { top: 0, bottom: 120, left: 0, right: 0 },
    children: [
      new Paragraph({ spacing: { after: 60 }, children: [
        new TextRun({ text: (etiqueta || "CAPÍTULO") + "  ", font: F.sans, size: 20, bold: true, color: C.yellow, characterSpacing: 60 }),
        new TextRun({ text: m ? m[1] : "", font: F.sans, size: 20, bold: true, color: C.yellow, characterSpacing: 60 })] }),
      new Paragraph({ style: "Heading1", children: [new Bookmark({ id, children: [new TextRun({ text: m ? m[2] : el.text, color: C.blanco })] })] }),
    ] });
  return [
    new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: "exact" }, children: [banda] }),
    new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [ANCHO], layout: TableLayoutType.FIXED,
      borders: { top: SIN, bottom: SIN, left: SIN, right: SIN, insideHorizontal: SIN, insideVertical: SIN },
      rows: [new TableRow({ height: { value: Math.round(5.6 * CM), rule: HeightRule.EXACT }, children: [celda] })] }),
    esp(30),
  ];
}

// ---------------------------------------------------------------- montaje
function cargarCap(nombre) {
  return JSON.parse(fs.readFileSync(path.join(RAIZ, "trabajo", "manual", `${nombre}.json`), "utf8"));
}

function construir() {
  const secciones = [portada(), creditos()];
  const cuerpoSecciones = [];
  for (const b of LIBRO.bloques) {
    const caps = b.caps.map((n) => cargarCap(`cap_${String(n).padStart(2, "0")}`));
    const titulos = caps.map((els) => els.find((e) => e.t === "h" && e.lvl === 1).text);
    cuerpoSecciones.push(portadilla(b, titulos));
    caps.forEach((els, k) => {
      const h = els.find((e) => e.t === "h" && e.lvl === 1);
      const cuerpo = els.filter((e) => e !== h);
      cuerpoSecciones.push({ properties: propsPagina(SectionType.ODD_PAGE),
        ...cabecerasCapitulo(cortarTitulo(h.text), `Bloque ${b.romano} · ${b.titulo}`, { et: b.romano, pos: b.n }),
        children: [...apertura(h), ...bloques(cuerpo)] });
    });
  }
  for (const a of LIBRO.anexos) {
    const els = cargarCap(a.fichero);
    const h = els.find((e) => e.t === "h" && e.lvl === 1);
    const cuerpo = els.filter((e) => e !== h);
    cuerpoSecciones.push({ properties: propsPagina(SectionType.ODD_PAGE),
      ...cabecerasCapitulo(cortarTitulo(h.text), "Anexos", { et: a.letra, pos: LIBRO.bloques.length + 1 }),
      children: [...apertura(h, "ANEXO"), ...bloques(cuerpo)] });
  }
  cuerpoSecciones.push({ properties: propsPagina(SectionType.EVEN_PAGE), ...vacias(), children: [
    new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: "exact" }, children: [fondo("assets/generados/contraportada_completa.png")] }),
  ] });
  secciones.push(paginaIndice(indice));
  secciones.push(...cuerpoSecciones);
  return secciones;
}

const ESTILOS = {
  default: {
    document: { run: { font: F.cuerpo, size: 19, color: C.texto }, paragraph: { spacing: { line: 276, lineRule: "auto" } } },
    heading1: { run: { font: F.sans, size: 44, bold: true, color: C.blanco },
      paragraph: { spacing: { before: 0, after: 0, line: 240, lineRule: "auto" }, keepNext: true, keepLines: true, outlineLevel: 0 } },
    heading2: { run: { font: F.sans, size: 25, bold: true, color: C.navy },
      paragraph: { spacing: { before: 400, after: 140, line: 264, lineRule: "auto" }, keepNext: true, keepLines: true, outlineLevel: 1 } },
    heading3: { run: { font: F.sans, size: 20, bold: true, color: C.navy2 },
      paragraph: { spacing: { before: 260, after: 100, line: 264, lineRule: "auto" }, keepNext: true, keepLines: true, outlineLevel: 2 } },
    heading4: { run: { font: F.sans, size: 18, bold: true, italics: true, color: C.navy2 },
      paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, keepLines: true, outlineLevel: 3 } },
  },
  paragraphStyles: [
    { id: "Cuerpo", name: "Cuerpo", basedOn: "Normal", quickFormat: true,
      paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 288, lineRule: "auto" }, widowControl: true } },
    { id: "Lista", name: "Lista", basedOn: "Cuerpo", paragraph: { spacing: { after: 70, line: 276, lineRule: "auto" }, alignment: AlignmentType.LEFT } },
    { id: "CuerpoRecuadro", name: "Cuerpo recuadro", basedOn: "Normal",
      run: { font: F.sans, size: 17 }, paragraph: { spacing: { after: 80, line: 264, lineRule: "auto" }, widowControl: true } },
    { id: "ListaRecuadro", name: "Lista recuadro", basedOn: "CuerpoRecuadro", paragraph: { spacing: { after: 50 } } },
    { id: "TituloRecuadro", name: "Título recuadro", basedOn: "Normal", run: { font: F.sans, size: 20, bold: true },
      paragraph: { spacing: { after: 80 }, keepNext: true } },
    { id: "Celda", name: "Celda", basedOn: "Normal", run: { font: F.sans, size: 15 }, paragraph: { spacing: { after: 0, line: 240, lineRule: "auto" } } },
    { id: "CeldaLista", name: "Celda lista", basedOn: "Celda", paragraph: { spacing: { after: 0 } } },
    { id: "CeldaCab", name: "Celda cabecera", basedOn: "Celda", run: { bold: true, color: C.blanco } },
    { id: "PieTabla", name: "Pie de tabla", basedOn: "Normal", run: { font: F.sans, size: 17 },
      paragraph: { spacing: { before: 200, after: 80, line: 240, lineRule: "auto" }, keepNext: true } },
    { id: "PieFigura", name: "Pie de figura", basedOn: "Normal", run: { font: F.sans, size: 17 },
      paragraph: { spacing: { before: 40, after: 220, line: 240, lineRule: "auto" }, alignment: AlignmentType.CENTER, indent: { left: 400, right: 400 } } },
    { id: "Separador", name: "Separador", basedOn: "Normal", paragraph: { spacing: { before: 0, after: 0, line: 160, lineRule: "exact" } }, run: { size: 8 } },
    { id: "Cabecera", name: "Cabecera libro", basedOn: "Normal", run: { font: F.sans, size: 16, color: C.gris, smallCaps: true, characterSpacing: 10 },
      paragraph: { spacing: { after: 0 }, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.grisClaro, space: 4 } } } },
    { id: "Pie", name: "Pie libro", basedOn: "Normal", run: { font: F.sans, size: 16 }, paragraph: { spacing: { after: 0 } } },
    { id: "TituloEspecial", name: "Título especial", basedOn: "Normal", run: { font: F.sans, size: 40, bold: true, color: C.navy },
      paragraph: { spacing: { before: 600, after: 480 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: C.yellow, space: 10 } } } },
    { id: "Indice1", name: "Índice 1", basedOn: "Normal", run: { font: F.sans, size: 19, bold: true, color: C.navy },
      paragraph: { spacing: { before: 280, after: 80 }, keepNext: true, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.yellow, space: 2 } } } },
    { id: "Indice2", name: "Índice 2", basedOn: "Normal", run: { font: F.sans, size: 17, color: C.navy },
      paragraph: { spacing: { before: 100, after: 30 }, indent: { left: 0 }, tabStops: [{ type: TabStopType.LEFT, position: 454 }], keepNext: true } },
    { id: "Indice3", name: "Índice 3", basedOn: "Normal", run: { font: F.sans, size: 15, color: "3A3F4B" },
      paragraph: { spacing: { after: 10 }, indent: { left: 454 }, tabStops: [{ type: TabStopType.LEFT, position: 1134 }] } },
  ],
};

async function main() {
  const secciones = construir();
  const doc = new Document({
    creator: "ITECAM", title: LIBRO.titulo, subject: LIBRO.subtitulo, description: LIBRO.tipo,
    evenAndOddHeaderAndFooters: true,
    styles: ESTILOS, numbering, sections: secciones,
  });
  let buf = await Packer.toBuffer(doc);
  // ajustes que docx-js no expone: márgenes simétricos, guionado, idioma español, viudas
  let JSZip; try { JSZip = require("jszip"); } catch (e) { JSZip = require("/opt/node-tools/node_modules/jszip"); }
  const zip = await JSZip.loadAsync(buf);
  let settings = await zip.file("word/settings.xml").async("string");
  settings = settings.replace(/<w:mirrorMargins\/>|<w:autoHyphenation\/>/g, "")
    .replace(/(<w:settings[^>]*>)/, "$1<w:mirrorMargins/><w:autoHyphenation/><w:consecutiveHyphenLimit w:val=\"2\"/><w:hyphenationZone w:val=\"425\"/>");
  zip.file("word/settings.xml", settings);
  let styles = await zip.file("word/styles.xml").async("string");
  styles = styles.replace(/<w:rPrDefault>\s*<w:rPr>/, "<w:rPrDefault><w:rPr><w:lang w:val=\"es-ES\" w:eastAsia=\"es-ES\" w:bidi=\"ar-SA\"/>");
  if (!/<w:pPrDefault>/.test(styles)) styles = styles.replace("</w:rPrDefault>", "</w:rPrDefault><w:pPrDefault><w:pPr><w:widowControl/></w:pPr></w:pPrDefault>");
  zip.file("word/styles.xml", styles);
  // marcadores con id único (docx-js reinicia la numeración en cada sección)
  let docXml = await zip.file("word/document.xml").async("string");
  let nb = 0, ne = 0;
  docXml = docXml.replace(/(<w:bookmarkStart[^>]*?) w:id="\d+"/g, (m, a) => `${a} w:id="${++nb}"`)
    .replace(/<w:bookmarkEnd w:id="\d+"/g, () => `<w:bookmarkEnd w:id="${++ne}"`);
  zip.file("word/document.xml", docXml);
  buf = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
  fs.mkdirSync(path.dirname(SALIDA), { recursive: true });
  fs.writeFileSync(SALIDA, buf);
  fs.writeFileSync(path.join(RAIZ, "trabajo", "indice_manual.json"), JSON.stringify([...indice, ...practicas.map((p) => ({ nivel: 4, texto: p.texto, id: p.id }))], null, 1));
  console.log(`Escrito ${SALIDA} (${(buf.length / 1e6).toFixed(1)} MB), ${indice.length} entradas de índice`);
}
main().catch((e) => { console.error(e); process.exit(1); });
