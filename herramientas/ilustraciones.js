// Ilustraciones editoriales del manual (SVG propio → PNG con Chromium).
// Uso: node herramientas/ilustraciones.js   → assets/ilustraciones/*.png
"use strict";
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { ({ chromium } = require("/opt/node-tools/node_modules/playwright")); }

const OUT = path.resolve(__dirname, "..", "assets", "ilustraciones");
const N = "#19233E", N2 = "#2C3A5E", Y = "#F5C400", G = "#5F6676", GL = "#BFC5D2", F = "#EDF0F6", W = "#FFFFFF", R = "#C8102E";
const FONT = "Montserrat, sans-serif";

// ------------------------------------------------------------ primitivas
const t = (x, y, s, o = {}) => `<text x="${x}" y="${y}" font-family="${FONT}" font-size="${o.size || 22}" font-weight="${o.w || 500}" fill="${o.fill || N}" text-anchor="${o.a || "middle"}" ${o.extra || ""}>${s}</text>`;
const rect = (x, y, w, h, o = {}) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${o.r ?? 12}" fill="${o.fill || W}" stroke="${o.stroke || N}" stroke-width="${o.sw ?? 3}" ${o.extra || ""}/>`;
const line = (x1, y1, x2, y2, o = {}) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${o.stroke || N}" stroke-width="${o.sw || 3}" ${o.dash ? `stroke-dasharray="${o.dash}"` : ""} ${o.arrow ? 'marker-end="url(#fl)"' : ""} stroke-linecap="round"/>`;
const pathS = (d, o = {}) => `<path d="${d}" fill="${o.fill || "none"}" stroke="${o.stroke || N}" stroke-width="${o.sw || 3}" ${o.arrow ? 'marker-end="url(#fl)"' : ""} stroke-linejoin="round" stroke-linecap="round" ${o.dash ? `stroke-dasharray="${o.dash}"` : ""}/>`;
const circ = (x, y, r, o = {}) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${o.fill || W}" stroke="${o.stroke || N}" stroke-width="${o.sw ?? 3}"/>`;
const num = (x, y, n) => circ(x, y, 19, { fill: Y, stroke: Y }) + t(x, y + 8, n, { size: 22, w: 700 });
const defs = (color = N) => `<defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="${color}"/></marker></defs>`;
const svg = (w, h, body, color) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${defs(color)}${body}</svg>`;

// pequeño módulo LOGO! (vista frontal simplificada)
function modulo(x, y, s = 1, etiqueta = "LOGO!") {
  const g = [];
  g.push(rect(x, y, 170 * s, 140 * s, { r: 10 * s, fill: F }));
  for (let i = 0; i < 8; i++) g.push(circ(x + (18 + i * 19) * s, y + 14 * s, 5 * s, { sw: 2 }));
  for (let i = 0; i < 4; i++) g.push(circ(x + (30 + i * 36) * s, y + 126 * s, 5 * s, { sw: 2 }));
  g.push(rect(x + 22 * s, y + 34 * s, 80 * s, 54 * s, { r: 4 * s, fill: "#9DB8D6", sw: 2 }));
  g.push(t(x + 62 * s, y + 66 * s, etiqueta, { size: 15 * s, w: 700, fill: N }));
  g.push(rect(x + 116 * s, y + 40 * s, 36 * s, 16 * s, { r: 4 * s, fill: W, sw: 2 }));
  g.push(rect(x + 116 * s, y + 64 * s, 36 * s, 16 * s, { r: 4 * s, fill: W, sw: 2 }));
  return g.join("");
}
function portatil(x, y, s = 1) {
  return rect(x, y, 150 * s, 96 * s, { r: 8 * s, fill: F }) + rect(x + 10 * s, y + 10 * s, 130 * s, 76 * s, { r: 3 * s, fill: W, sw: 2 })
    + rect(x + 22 * s, y + 24 * s, 34 * s, 22 * s, { r: 3, fill: "#FFF3BF", sw: 2 }) + rect(x + 84 * s, y + 46 * s, 34 * s, 22 * s, { r: 3, fill: "#FFF3BF", sw: 2 })
    + line(x + 56 * s, y + 35 * s, x + 84 * s, y + 57 * s, { sw: 2 })
    + pathS(`M${x - 18 * s},${y + 104 * s} L${x + 168 * s},${y + 104 * s} L${x + 152 * s},${y + 96 * s} L${x - 2 * s},${y + 96 * s} Z`, { fill: F, sw: 3 });
}
function tde(x, y, s = 1) {
  return rect(x, y, 200 * s, 140 * s, { r: 12 * s, fill: "#2B2F36", stroke: N }) + rect(x + 14 * s, y + 14 * s, 172 * s, 96 * s, { r: 4 * s, fill: "#9DB8D6", sw: 2 })
    + [0, 1, 2, 3].map((i) => rect(x + (22 + i * 42) * s, y + 118 * s, 32 * s, 12 * s, { r: 3 * s, fill: "#D7DCE6", sw: 1.5 })).join("");
}
function conmutador(x, y) {
  return rect(x, y, 160, 54, { r: 8, fill: F }) + [0, 1, 2, 3, 4, 5].map((i) => rect(x + 14 + i * 23, y + 30, 16, 12, { r: 2, fill: W, sw: 2 })).join("")
    + t(x + 80, y + 22, "Conmutador", { size: 15, w: 600 });
}

// ------------------------------------------------------------ esquemas dentro del texto
const E = {};

E.ciclo_programa = () => {
  const w = 1000, h = 640, cx = 500, cy = 350, r = 190;
  const pasos = [
    { a: -90, n: "1", tit: "Lee las entradas", sub: "copia el estado de I1…I8" },
    { a: 30, n: "2", tit: "Ejecuta el programa", sub: "bloque a bloque, B001, B002…" },
    { a: 150, n: "3", tit: "Escribe las salidas", sub: "Q1…Q4 conmutan sus relés" },
  ];
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  // arcos con flecha entre pasos
  for (let i = 0; i < 3; i++) {
    const a1 = (pasos[i].a + 22) * Math.PI / 180, a2 = (pasos[(i + 1) % 3].a - 22) * Math.PI / 180;
    const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1), x2 = cx + r * Math.cos(a2), y2 = cy + r * Math.sin(a2);
    b += pathS(`M${x1},${y1} A${r},${r} 0 0 1 ${x2},${y2}`, { stroke: Y, sw: 7, arrow: true });
  }
  b += modulo(cx - 85, cy - 70, 1, "RUN");
  for (const p of pasos) {
    const a = p.a * Math.PI / 180, x = cx + (r + 0) * Math.cos(a), y = cy + r * Math.sin(a);
    const bx = x + (p.a === -90 ? -130 : p.a === 30 ? 20 : -280), by = y + (p.a === -90 ? -95 : 10);
    b += rect(bx, by, 260, 74, { r: 12, fill: W });
    b += num(bx + 2, by + 2, p.n);
    b += t(bx + 130, by + 32, p.tit, { size: 21, w: 700 }) + t(bx + 130, by + 58, p.sub, { size: 16, fill: G });
  }
  b += t(cx, h - 18, "Cada vuelta es un ciclo. Se repite mientras el módulo está en RUN.", { size: 18, fill: G });
  return svg(w, h, b, Y);
};

E.flujo_lsc = () => {
  const w = 1100, h = 330;
  const pasos = [
    ["1", "Programar", "LOGO!Soft Comfort", "prog"], ["2", "Simular", "en el PC, sin equipo", "sim"],
    ["3", "Transferir", "PC → LOGO!", "tra"], ["4", "Comprobar", "Test online y banco", "test"],
  ];
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  pasos.forEach((p, i) => {
    const x = 20 + i * 272;
    b += rect(x, 40, 230, 250, { r: 16, fill: i === 3 ? "#FFF8DB" : F });
    b += num(x + 26, 40 + 26, p[0]);
    if (p[3] === "prog" || p[3] === "sim") b += portatil(x + 42, 82, 0.95);
    if (p[3] === "sim") b += circ(x + 115, 112, 14, { fill: Y, stroke: N, sw: 2 }) + pathS(`M${x + 110},${105} L${x + 122},${112} L${x + 110},${119} Z`, { fill: N, sw: 1 });
    if (p[3] === "tra") b += portatil(x + 8, 96, 0.55) + line(x + 100, 128, x + 132, 128, { arrow: true, sw: 4 }) + modulo(x + 140, 92, 0.48);
    if (p[3] === "test") b += modulo(x + 30, 82, 0.62) + circ(x + 170, 108, 22, { fill: W, stroke: N }) + line(x + 186, 124, x + 202, 140, { sw: 5 });
    b += t(x + 115, 232, p[1], { size: 24, w: 700 }) + t(x + 115, 262, p[2], { size: 16, fill: G });
    if (i < 3) b += line(x + 236, 165, x + 266, 165, { stroke: Y, sw: 6, arrow: true });
  });
  return svg(w, h, b, Y);
};

E.red_aula = () => {
  const w = 1100, h = 520;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  b += portatil(70, 150, 1.05);
  b += conmutador(470, 190);
  b += modulo(820, 60, 1);
  b += tde(805, 280, 0.95);
  b += pathS("M245,220 L470,217", { stroke: "#2E8B57", sw: 5 });
  b += pathS("M630,205 L740,205 L740,130 L820,130", { stroke: "#2E8B57", sw: 5 });
  b += pathS("M630,228 L740,228 L740,345 L805,345", { stroke: "#2E8B57", sw: 5 });
  const etiqueta = (x, y, a, b2) => rect(x, y, 230, 64, { r: 10, fill: W, stroke: GL, sw: 2 }) + t(x + 115, y + 27, a, { size: 18, w: 700 }) + t(x + 115, y + 52, b2, { size: 17, fill: N2, extra: 'font-family="Consolas, monospace"' });
  b += etiqueta(30, 300, "PC del puesto", "192.168.0.55");
  b += etiqueta(860 - 20, 210, "Módulo base", "192.168.0.105");
  b += etiqueta(785, 430, "LOGO! TDE", "192.168.0.205");
  b += t(550, 290, "Cable Ethernet", { size: 16, fill: "#2E8B57", w: 600 });
  b += rect(330, 400, 420, 76, { r: 12, fill: "#FFF8DB", stroke: Y, sw: 2 });
  b += t(540, 432, "Puesto 05 · máscara 255.255.255.0", { size: 18, w: 700 });
  b += t(540, 460, "PC 50 + NN · módulo 100 + NN · TDE 200 + NN", { size: 16, fill: G });
  return svg(w, h, b);
};

function cronograma(x0, y0, wid, nombre, tramos, alto = 50) {
  // tramos: lista de [x_inicio, x_fin] en nivel 1 (coordenadas 0..1 del ancho)
  let d = `M${x0},${y0 + alto}`;
  for (const [a, b2] of tramos) d += ` L${x0 + a * wid},${y0 + alto} L${x0 + a * wid},${y0} L${x0 + b2 * wid},${y0} L${x0 + b2 * wid},${y0 + alto}`;
  d += ` L${x0 + wid},${y0 + alto}`;
  return t(x0 - 20, y0 + alto - 12, nombre, { a: "end", size: 22, w: 700 }) + line(x0, y0 + alto, x0 + wid, y0 + alto, { stroke: GL, sw: 2 })
    + pathS(d, { stroke: nombre === "Q" ? R : N, sw: 4 });
}
E.ton_tof = () => {
  const w = 1100, h = 600, x0 = 140, wid = 900;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  const panel = (y, titulo, trg, q, cotas) => {
    let s = t(40, y, titulo, { a: "start", size: 23, w: 700 }) + line(40, y + 10, 420, y + 10, { stroke: Y, sw: 4 });
    s += cronograma(x0, y + 40, wid, "Trg", trg) + cronograma(x0, y + 130, wid, "Q", q);
    for (const [a, b2] of cotas) {
      const xa = x0 + a * wid, xb = x0 + b2 * wid, yy = y + 228;
      s += line(xa, y + 40, xa, yy, { stroke: GL, sw: 2, dash: "6 6" }) + line(xb, y + 130, xb, yy, { stroke: GL, sw: 2, dash: "6 6" });
      s += pathS(`M${xa + 4},${yy} L${xb - 4},${yy}`, { stroke: N2, sw: 2, arrow: true }) + t((xa + xb) / 2, yy - 8, "T", { size: 20, w: 700, fill: N2 });
    }
    return s;
  };
  b += panel(40, "Retardo a la conexión", [[0.08, 0.42], [0.55, 0.64], [0.74, 0.97]], [[0.25, 0.42], [0.91, 0.97]], [[0.08, 0.25], [0.74, 0.91]]);
  b += panel(330, "Retardo a la desconexión", [[0.08, 0.30], [0.62, 0.68]], [[0.08, 0.47], [0.62, 0.85]], [[0.30, 0.47], [0.68, 0.85]]);
  b += t(x0 + wid / 2 + 30, h - 6, "Un impulso más corto que T no llega a activar el retardo a la conexión.", { size: 17, fill: G });
  return svg(w, h, b, N2);
};

E.escalado = () => {
  const w = 1100, h = 500, x0 = 250, wid = 760;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  const escala = (y, nombre, ini, fin, uni, marcas, color) => {
    let s = t(x0, y - 26, nombre, { a: "start", size: 20, w: 700 });
    s += rect(x0, y - 12, wid, 24, { r: 12, fill: F, stroke: GL, sw: 2 }) + rect(x0, y - 12, wid / 2, 24, { r: 12, fill: color, stroke: color, sw: 0 });
    marcas.forEach((m, i) => {
      const x = x0 + (i / (marcas.length - 1)) * wid;
      s += line(x, y + 16, x, y + 28, { stroke: G, sw: 2 }) + t(x, y + 52, m, { size: 17, fill: G });
    });
    s += t(x0 + wid + 20, y + 8, uni, { a: "start", size: 18, fill: G });
    return s;
  };
  b += escala(90, "Tensión en la entrada", 0, 10, "V", ["0", "2", "4", "6", "8", "10"], "#9DB8D6");
  b += escala(240, "Valor interno", 0, 1000, "", ["0", "200", "400", "600", "800", "1000"], "#C9D3E3");
  b += escala(390, "Nivel del depósito", 0, 200, "cm", ["0", "40", "80", "120", "160", "200"], "#FFE27A");
  const xm = x0 + wid / 2;
  b += line(xm, 60, xm, 420, { stroke: R, sw: 3, dash: "8 7" });
  b += [[90, "5 V"], [240, "500"], [390, "100 cm"]].map(([y, s]) => rect(xm + 12, y - 46, 110, 30, { r: 8, fill: R, stroke: R, sw: 0 }) + t(xm + 67, y - 25, s, { size: 18, w: 700, fill: W })).join("");
  b += t(160, 172, "conversión A/D", { size: 16, fill: N2, a: "end", extra: 'font-style="italic"' }) + line(185, 110, 185, 225, { arrow: true, sw: 3 });
  b += t(160, 322, "× Gain 0,20", { size: 16, fill: N2, a: "end", extra: 'font-style="italic"' }) + line(185, 260, 185, 375, { arrow: true, sw: 3 });
  return svg(w, h, b);
};

E.histeresis = () => {
  const w = 1100, h = 560, x0 = 120, wid = 920, yTop = 50, alto = 300;
  const on = 140, off = 60, vmax = 200;
  const Y_ = (v) => yTop + alto - (v / vmax) * alto;
  let pts = [], q = [], estado = 0;
  for (let i = 0; i <= 400; i++) {
    const s = i / 400;
    const v = 100 + 75 * Math.sin(s * Math.PI * 3.2 - 0.6) + 8 * Math.sin(s * 47);
    pts.push([x0 + s * wid, Y_(v)]);
    if (v > on) estado = 1; else if (v <= off) estado = 0;
    q.push([x0 + s * wid, estado]);
  }
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  b += rect(x0, Y_(on), wid, Y_(off) - Y_(on), { r: 0, fill: "#FFF8DB", stroke: "none", sw: 0 });
  b += line(x0, yTop + alto, x0 + wid, yTop + alto, { stroke: GL, sw: 2 }) + line(x0, yTop, x0, yTop + alto, { stroke: GL, sw: 2 });
  b += line(x0, Y_(on), x0 + wid, Y_(on), { stroke: Y, sw: 4, dash: "12 8" }) + line(x0, Y_(off), x0 + wid, Y_(off), { stroke: Y, sw: 4, dash: "12 8" });
  b += t(x0 - 14, Y_(on) + 7, "On", { a: "end", size: 20, w: 700 }) + t(x0 - 14, Y_(off) + 7, "Off", { a: "end", size: 20, w: 700 });
  b += t(x0 + wid - 10, Y_(on) + Y_(off) - Y_(on) / 1 - 0, "", {});
  b += pathS("M" + pts.map((p) => p.join(",")).join(" L"), { stroke: N, sw: 4 });
  b += t(x0 + 10, yTop - 14, "Valor medido", { a: "start", size: 18, w: 600, fill: G });
  b += t(x0 + wid - 6, (Y_(on) + Y_(off)) / 2 + 7, "Zona de histéresis: Q no cambia", { a: "end", size: 17, fill: N2, extra: 'font-style="italic"' });
  const yq = 440, aq = 60;
  let d = `M${q[0][0]},${yq + aq - q[0][1] * aq}`;
  for (let i = 1; i < q.length; i++) {
    if (q[i][1] !== q[i - 1][1]) d += ` L${q[i][0]},${yq + aq - q[i - 1][1] * aq} L${q[i][0]},${yq + aq - q[i][1] * aq}`;
  }
  d += ` L${q[q.length - 1][0]},${yq + aq - q[q.length - 1][1] * aq}`;
  b += line(x0, yq + aq, x0 + wid, yq + aq, { stroke: GL, sw: 2 }) + pathS(d, { stroke: R, sw: 4 }) + t(x0 - 14, yq + aq - 8, "Q", { a: "end", size: 22, w: 700 });
  return svg(w, h, b);
};

E.lazo_pi = () => {
  const w = 1100, h = 380;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  const caja = (x, y, ww, a, c, fill = F) => rect(x, y, ww, 92, { r: 14, fill }) + t(x + ww / 2, y + 40, a, { size: 21, w: 700 }) + t(x + ww / 2, y + 68, c, { size: 16, fill: G });
  b += t(70, 125, "Consigna", { size: 18, w: 700 }) + t(70, 150, "SP", { size: 18, fill: G });
  b += line(40, 170, 170, 170, { arrow: true });
  b += circ(200, 170, 28, { fill: W }) + t(200, 178, "Σ", { size: 24, w: 700 }) + t(170, 150, "+", { size: 18, w: 700 }) + t(222, 220, "−", { size: 22, w: 700 });
  b += line(228, 170, 290, 170, { arrow: true });
  b += caja(295, 124, 210, "Regulador PI", "KC · TI · Dir", "#FFF8DB");
  b += line(505, 170, 560, 170, { arrow: true }) + t(532, 158, "AQ", { size: 16, w: 700 });
  b += caja(565, 124, 210, "Actuador", "variador o válvula");
  b += line(775, 170, 830, 170, { arrow: true });
  b += caja(835, 124, 220, "Proceso", "el depósito");
  b += pathS("M945,216 L945,300 L200,300 L200,198", { arrow: true });
  b += t(570, 330, "Valor real PV que mide el sensor y vuelve al regulador", { size: 17, fill: G });
  return svg(w, h, b);
};

E.pagina_tde = () => {
  const w = 1100, h = 560;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  b += rect(60, 40, 620, 470, { r: 28, fill: "#2B2F36" });
  b += rect(95, 75, 550, 330, { r: 6, fill: "#F4F7FB", stroke: "#2B2F36", sw: 2 });
  b += rect(95, 75, 550, 52, { r: 6, fill: N, stroke: N, sw: 0 }) + t(370, 110, "NIVEL DEL DEPÓSITO", { size: 22, w: 700, fill: W });
  b += t(370, 215, "126 cm", { size: 64, w: 700, fill: N });
  b += rect(140, 255, 460, 34, { r: 6, fill: "#DDE3EE", stroke: GL, sw: 2 }) + rect(140, 255, 290, 34, { r: 6, fill: "#2E8B57", stroke: "#2E8B57", sw: 0 });
  b += t(140, 312, "0", { size: 15, fill: G, a: "start" }) + t(600, 312, "200", { size: 15, fill: G, a: "end" });
  b += rect(260, 335, 220, 52, { r: 10, fill: Y, stroke: N, sw: 2 }) + t(370, 369, "MARCHA", { size: 21, w: 700 });
  ["F1", "F2", "F3", "F4"].forEach((k, i) => { b += rect(120 + i * 130, 432, 100, 46, { r: 8, fill: "#D7DCE6", stroke: "#8B93A3", sw: 2 }) + t(170 + i * 130, 463, k, { size: 18, w: 700 }); });
  const llamada = (n, x, y, lx, ly, txt, sub) => line(x, y, lx - 26, ly, { stroke: Y, sw: 3 }) + num(lx, ly, n) + t(lx + 30, ly - 2, txt, { a: "start", size: 20, w: 700 }) + t(lx + 30, ly + 24, sub, { a: "start", size: 16, fill: G });
  b += llamada("1", 600, 101, 760, 100, "Título", "texto fijo de la página");
  b += llamada("2", 520, 200, 760, 190, "Valor con unidad", "dato del programa");
  b += llamada("3", 600, 272, 760, 280, "Barra", "el mismo dato en escala");
  b += llamada("4", 480, 361, 760, 370, "Botón", "petición al programa");
  b += llamada("5", 640, 455, 760, 460, "Teclas F1 a F4", "mandos de la TDE");
  return svg(w, h, b, Y);
};

E.mando_tde = () => {
  const w = 1150, h = 360;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  const pasos = [["Petición", "el operador pulsa", "la tecla F1 de la TDE"], ["Permiso", "el programa comprueba", "térmico y nivel en orden"],
    ["Orden", "se activa la salida", "Q1 alimenta KM1"], ["Retorno", "el campo confirma", "contacto auxiliar de KM1"]];
  pasos.forEach((p, i) => {
    const x = 20 + i * 285;
    b += rect(x, 70, 245, 150, { r: 16, fill: i === 2 ? "#FFF8DB" : F });
    b += num(x + 26, 96, String(i + 1));
    b += t(x + 132, 118, p[0], { size: 26, w: 700 }) + t(x + 122, 160, p[1], { size: 17, fill: N2 }) + t(x + 122, 188, p[2], { size: 16, fill: G });
    if (i < 3) b += line(x + 250, 145, x + 280, 145, { stroke: Y, sw: 6, arrow: true });
  });
  b += pathS("M1007,222 L1007,290 L760,290", { stroke: N2, sw: 3, arrow: true, dash: "10 8" });
  b += t(880, 320, "Si el retorno no llega a tiempo, el programa avisa del fallo", { size: 16, fill: G });
  return svg(w, h, b, Y);
};

E.registro_datos = () => {
  const w = 1150, h = 330;
  let b = rect(0, 0, w, h, { r: 0, fill: W, stroke: W, sw: 0 });
  const caja = (x, y, ww, a, c, fill = F) => rect(x, y, ww, 110, { r: 14, fill }) + t(x + ww / 2, y + 48, a, { size: 21, w: 700 }) + t(x + ww / 2, y + 80, c, { size: 16, fill: G });
  b += caja(20, 60, 230, "Bloque de registro", "se habilita con En");
  b += line(255, 115, 295, 115, { stroke: Y, sw: 6, arrow: true });
  b += caja(300, 20, 250, "Búfer del módulo", "últimos 4096 bytes") + caja(300, 160, 250, "Tarjeta micro SD", "si está insertada", "#FFF8DB");
  b += line(555, 75, 600, 105, { stroke: Y, sw: 6, arrow: true }) + line(555, 215, 600, 130, { stroke: Y, sw: 6, arrow: true });
  b += rect(605, 50, 150, 130, { r: 8, fill: W }) + pathS("M720,50 L755,85 L720,85 Z", { fill: F, sw: 3 }) + t(680, 135, ".CSV", { size: 26, w: 700 });
  b += line(760, 115, 800, 115, { stroke: Y, sw: 6, arrow: true });
  b += caja(805, 20, 320, "Navegador web", "servidor web del módulo") + caja(805, 160, 320, "LOGO!Soft Comfort", "descarga desde el PC");
  return svg(w, h, b, Y);
};

// ------------------------------------------------------------ ilustraciones de apertura (línea blanca)
const L = (d, o = {}) => pathS(d, { stroke: o.y ? Y : W, sw: o.sw || 6, fill: o.fill || "none" });
const LR = (x, y, w, h, o = {}) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${o.r ?? 14}" fill="${o.fill || "none"}" stroke="${o.y ? Y : W}" stroke-width="${o.sw || 6}"/>`;
const LC = (x, y, r, o = {}) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${o.fill || "none"}" stroke="${o.y ? Y : W}" stroke-width="${o.sw || 6}"/>`;
const LT = (x, y, s, o = {}) => `<text x="${x}" y="${y}" font-family="${FONT}" font-size="${o.size || 40}" font-weight="700" fill="${o.y ? Y : W}" text-anchor="middle">${s}</text>`;
const modL = (x, y, s = 1) => LR(x, y, 230 * s, 190 * s) + [...Array(8)].map((_, i) => LC(x + (24 + i * 26) * s, y + 20 * s, 6 * s, { sw: 4 })).join("")
  + [...Array(4)].map((_, i) => LC(x + (40 + i * 50) * s, y + 170 * s, 6 * s, { sw: 4 })).join("") + LR(x + 30 * s, y + 50 * s, 110 * s, 75 * s, { r: 6, y: true })
  + LR(x + 160 * s, y + 55 * s, 45 * s, 20 * s, { r: 5, sw: 4 }) + LR(x + 160 * s, y + 90 * s, 45 * s, 20 * s, { r: 5, sw: 4 });
const AP = {
  1: () => modL(160, 120, 1.2),
  2: () => L("M40,170 L560,170", { sw: 8 }) + L("M40,200 L560,200", { sw: 4 }) + modL(70, 90, 0.75) + LR(260, 90, 90, 142) + LR(370, 90, 90, 142) + L("M120,90 C120,20 300,30 300,90", { y: true }) + L("M200,90 C200,0 420,10 410,90", { y: true }),
  3: () => LR(150, 70, 300, 260, { r: 20 }) + LR(180, 100, 240, 160, { r: 6 }) + [0, 1, 2].map((i) => LR(200, 115 + i * 48, 200, 34, { r: 6, sw: 4, y: i === 1 })).join("") + LC(300, 295, 16),
  4: () => LR(40, 150, 150, 100) + L("M20,268 L210,268") + LR(240, 175, 130, 50, { r: 8 }) + modL(420, 110, 0.6) + L("M190,200 L240,200", { y: true }) + L("M370,200 L420,180", { y: true }) + L("M370,210 L420,270", { y: true }) + LR(420, 245, 120, 80, { r: 10 }),
  5: () => LR(110, 80, 380, 230) + L("M70,330 L530,330") + LR(150, 120, 90, 60, { r: 6, y: true }) + LR(330, 190, 90, 60, { r: 6, y: true }) + L("M240,150 L280,150 L280,220 L330,220"),
  6: () => L("M90,90 L170,90 C250,90 250,210 170,210 L90,210 Z") + L("M60,120 L90,120 M60,180 L90,180 M232,150 L290,150", { sw: 5 }) + L("M320,90 C380,90 430,120 460,150 C430,180 380,210 320,210 C350,150 350,150 320,90 Z", { y: true }) + L("M290,150 L340,150 M290,190 L330,190 M460,150 L540,150", { sw: 5 }) + LT(165, 165, "&", { size: 44 }) + LT(395, 165, "≥1", { size: 36, y: true }),
  7: () => LC(300, 210, 140) + L("M300,210 L300,120", { y: true, sw: 8 }) + L("M300,210 L370,250", { sw: 6 }) + LR(270, 30, 60, 30, { r: 6 }) + L("M300,60 L300,70") + [...Array(12)].map((_, i) => { const a = i * Math.PI / 6; return L(`M${300 + 120 * Math.cos(a)},${210 + 120 * Math.sin(a)} L${300 + 132 * Math.cos(a)},${210 + 132 * Math.sin(a)}`, { sw: 4 }); }).join(""),
  8: () => LR(70, 80, 260, 240) + L("M70,140 L330,140") + [0, 1, 2, 3].map((r) => [0, 1, 2, 3].map((c) => LR(90 + c * 58, 160 + r * 38, 40, 26, { r: 4, sw: 3, y: r === 1 && c === 2 })).join("")).join("") + LR(380, 140, 180, 120) + LT(470, 215, "0127", { size: 46, y: true }),
  9: () => modL(40, 120, 0.7) + LR(220, 120, 90, 133) + LR(330, 120, 90, 133) + LR(440, 120, 90, 133, { y: true }) + L("M70,320 L520,320", { y: true }) + L("M480,305 L520,320 L480,335", { y: true }),
  10: () => L("M120,300 A180,180 0 0 1 480,300") + [...Array(11)].map((_, i) => { const a = Math.PI + i * Math.PI / 10; return L(`M${300 + 160 * Math.cos(a)},${300 + 160 * Math.sin(a)} L${300 + 180 * Math.cos(a)},${300 + 180 * Math.sin(a)}`, { sw: 4 }); }).join("") + L("M300,300 L410,190", { y: true, sw: 9 }) + LC(300, 300, 18, { fill: W }),
  11: () => L("M60,330 L560,330 M60,330 L60,60", { sw: 4 }) + L("M60,140 L560,140 M60,230 L560,230", { y: true, sw: 4 }) + L("M60,280 C140,40 200,40 260,200 C320,340 380,330 440,120 C470,40 520,60 560,150", { sw: 6 }),
  12: () => L("M60,300 L200,300 L360,120 L540,120", { sw: 7 }) + L("M60,330 L560,330", { sw: 4 }) + L("M200,300 L200,330 M360,120 L360,330", { y: true, sw: 4 }) + LT(460, 100, "PI", { size: 50, y: true }),
  13: () => modL(130, 80, 1.4),
  14: () => LR(100, 70, 400, 280, { r: 26 }) + LR(130, 100, 340, 190, { r: 8, y: true }) + [0, 1, 2, 3].map((i) => LR(140 + i * 85, 305, 65, 28, { r: 6, sw: 4 })).join(""),
  15: () => LR(100, 70, 400, 280, { r: 26 }) + LR(130, 100, 340, 190, { r: 8 }) + LR(160, 125, 280, 30, { r: 4, sw: 4, y: true }) + LR(160, 185, 200, 26, { r: 4, sw: 4 }) + LR(160, 235, 120, 34, { r: 8, sw: 4, y: true }),
  16: () => L("M300,70 C220,70 200,140 200,200 L180,260 L420,260 L400,200 C400,140 380,70 300,70 Z") + L("M270,280 C270,310 330,310 330,280", { y: true }) + L("M150,120 C130,150 130,190 150,220 M450,120 C470,150 470,190 450,220", { y: true, sw: 5 }),
  17: () => modL(30, 140, 0.6) + modL(400, 140, 0.6) + L("M175,200 L400,200", { y: true, sw: 5 }) + LC(300, 90, 55, { sw: 5 }) + L("M245,90 L355,90 M300,35 C270,60 270,120 300,145 C330,120 330,60 300,35", { sw: 4 }) + LR(275, 260, 50, 45, { r: 6, sw: 5, y: true }) + L("M285,260 L285,240 C285,222 315,222 315,240 L315,260", { y: true, sw: 5 }),
  18: () => LR(70, 110, 200, 200) + LT(170, 225, "UDF", { size: 46, y: true }) + L("M30,160 L70,160 M30,260 L70,260 M270,210 L320,210", { sw: 5 }) + L("M350,90 L490,90 L540,140 L540,330 L350,330 Z") + L("M490,90 L490,140 L540,140", { sw: 4 }) + [0, 1, 2, 3].map((i) => L(`M380,${180 + i * 36} L510,${180 + i * 36}`, { sw: 4, y: i === 0 })).join(""),
  19: () => L("M150,80 L150,330 L400,330 L400,80", { sw: 7 }) + `<rect x="156" y="190" width="238" height="134" fill="${Y}" opacity="0.85"/>` + L("M150,190 L400,190", { y: true, sw: 4 }) + LC(480, 300, 40) + L("M400,300 L440,300 M480,260 L480,120 L400,120", { sw: 5 }),
  A: () => [0, 1, 2].map((r) => [0, 1, 2].map((c) => LR(90 + c * 150, 70 + r * 105, 110, 80, { r: 10, y: r === 1 && c === 1 }) + LT(145 + c * 150, 122 + r * 105, ["&", "≥1", "RS", "T", "C", "A", "PI", "≠", "Σ"][r * 3 + c], { size: 32, y: r === 1 && c === 1 })).join("")).join(""),
};

// ------------------------------------------------------------ iconos de recuadro
const IC = {
  objetivos: (c) => LC(60, 60, 40, { sw: 7 }).replace(/#FFFFFF/g, c) + LC(60, 60, 22, { sw: 7 }).replace(/#FFFFFF/g, c) + LC(60, 60, 6, { sw: 7, fill: c }).replace(/#FFFFFF/g, c),
  ejemplo: (c) => L("M60,18 C34,18 24,40 24,54 C24,70 38,78 42,92 L78,92 C82,78 96,70 96,54 C96,40 86,18 60,18 Z", { sw: 7 }).replace(/#FFFFFF/g, c) + L("M46,104 L74,104", { sw: 7 }).replace(/#FFFFFF/g, c),
  recuerda: (c) => L("M36,16 L84,16 L84,104 L60,84 L36,104 Z", { sw: 7 }).replace(/#FFFFFF/g, c),
  seguridad: (c) => L("M60,14 L108,100 L12,100 Z", { sw: 7 }).replace(/#FFFFFF/g, c) + L("M60,46 L60,72", { sw: 8 }).replace(/#FFFFFF/g, c) + LC(60, 86, 4, { sw: 5, fill: c }).replace(/#FFFFFF/g, c),
  atencion: (c) => LC(60, 60, 44, { sw: 7 }).replace(/#FFFFFF/g, c) + L("M60,34 L60,66", { sw: 8 }).replace(/#FFFFFF/g, c) + LC(60, 82, 4, { sw: 5, fill: c }).replace(/#FFFFFF/g, c),
  soluciones: (c) => LC(60, 60, 44, { sw: 7 }).replace(/#FFFFFF/g, c) + L("M38,62 L54,78 L84,44", { sw: 8 }).replace(/#FFFFFF/g, c),
  nota: (c) => LC(60, 60, 44, { sw: 7 }).replace(/#FFFFFF/g, c) + L("M60,54 L60,86", { sw: 8 }).replace(/#FFFFFF/g, c) + LC(60, 36, 4, { sw: 5, fill: c }).replace(/#FFFFFF/g, c),
};
const COLOR_IC = { objetivos: "#19233E", ejemplo: "#2C3A5E", recuerda: "#4F7F4E", seguridad: "#C8102E", atencion: "#8A6200", soluciones: "#4F7F4E", nota: "#2C3A5E" };

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  fs.mkdirSync(path.join(OUT, "apertura"), { recursive: true });
  fs.mkdirSync(path.join(OUT, "iconos"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  const render = async (svgTxt, dst, transparente = false) => {
    await page.setContent(`<html><head><style>body{margin:0;background:transparent}</style></head><body>${svgTxt}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    await page.locator("svg").screenshot({ path: dst, omitBackground: transparente });
  };
  for (const [nombre, f] of Object.entries(E)) await render(f(), path.join(OUT, `${nombre}.png`));
  for (const [k, f] of Object.entries(AP)) await render(svg(600, 400, f()), path.join(OUT, "apertura", `cap_${k}.png`), true);
  for (const [k, f] of Object.entries(IC)) await render(svg(120, 120, f(COLOR_IC[k])), path.join(OUT, "iconos", `${k}.png`), true);
  await browser.close();
  console.log("Ilustraciones en", OUT);
}
main().catch((e) => { console.error(e); process.exit(1); });
