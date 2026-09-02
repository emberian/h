// mouth.js — animating the cross-section.
//
// The SVG in index.html is static line work; this module moves it. Per frame
// it takes the breath state (airflow, glottal aperture, lung volume, and the
// utterance envelope while the h is speaking) plus wetness, and:
//   • scales the lungs and drops the diaphragm with volume;
//   • narrows the folds in the laryngoscopic inset toward the /h/ aperture on
//     exhale, with a turbulent flutter that grows as the gap closes;
//   • runs airflow particles along the airway centreline (#airway-path),
//     accelerating through the glottis and scattering downstream of it;
//   • sets the moisture: sheen on the mucosa, droplets that bead and run,
//     cracks when parched, pooling and bubbles in the glottis when soaked.
//
// Nothing here is physically simulated in earnest; it is drawn to be read.

const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const gauss = (x) => Math.exp(-x * x);
const NS = "http://www.w3.org/2000/svg";

const GLOTTIS = { x: 592, y: 738 };                          // where the folds are, in the sagittal view
const INSET = { cx: 340, cy: 830, apexY: 760, L: 135 };      // laryngoscopic view: anterior commissure at the top

// Where moisture collects. (x, y) in SVG units; th = wetness at which the
// drop appears; run = how far it travels once it is heavy enough to fall.
const DROP_ANCHORS = [
  { x: 350, y: 462, th: 0.15, size: 3.0 },                        // tongue dorsum
  { x: 410, y: 445, th: 0.25, size: 4.0 },
  { x: 470, y: 448, th: 0.35, size: 3.4 },
  { x: 520, y: 463, th: 0.45, size: 4.4 },
  { x: 302, y: 490, th: 0.55, size: 2.8 },                        // tongue tip
  { x: 360, y: 386, th: 0.40, size: 2.8, run: { dx: 2, dy: 60 } },  // palate → falls onto the tongue
  { x: 440, y: 380, th: 0.50, size: 2.4, run: { dx: 0, dy: 58 } },
  { x: 631, y: 520, th: 0.30, size: 3.0, run: { dx: 4, dy: 90 } },  // pharyngeal wall, running down
  { x: 636, y: 600, th: 0.50, size: 3.4, run: { dx: 4, dy: 110 } },
  { x: 592, y: 444, th: 0.60, size: 3.6, run: { dx: 12, dy: 150 } }, // hanging from the uvula
  { x: 604, y: 604, th: 0.55, size: 2.8 },                        // epiglottis
  { x: 588, y: 746, th: 0.20, size: 2.4 },                        // the fold itself
  { x: 262, y: 444, th: 0.30, size: 3.0 },                        // lips
  { x: 266, y: 492, th: 0.35, size: 2.6, run: { dx: -10, dy: 34 } },
  { x: 560, y: 520, th: 0.70, size: 3.8, run: { dx: 14, dy: 70 } }, // tongue root
];
// Drops on the folds in the inset: t = position along the medial edge (0 = commissure).
const INSET_DROPS = [
  { side: -1, t: 0.35, th: 0.12, size: 3.2 }, { side: -1, t: 0.60, th: 0.30, size: 2.6 }, { side: -1, t: 0.82, th: 0.50, size: 3.6 },
  { side: 1, t: 0.28, th: 0.22, size: 2.8 }, { side: 1, t: 0.55, th: 0.40, size: 3.4 }, { side: 1, t: 0.78, th: 0.58, size: 2.4 },
];

export function createMouth(svg, { reducedMotion = false } = {}) {
  const $ = (id) => svg.querySelector("#" + id);
  const el = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    parent.appendChild(e);
    return e;
  };

  const lungs = $("lungs"), diaphragm = $("diaphragm"), uvula = $("uvula"), foldSag = $("fold-sag");
  const cracks = $("cracks"), sheens = [$("sheen-tongue"), $("sheen-palate"), $("sheen-pharynx")];
  const poolVallecula = $("pool-vallecula"), poolVentricle = $("pool-ventricle");
  const chink = $("chink"), chinkClip = $("chink-clip-poly"), foldL = $("fold-l"), foldR = $("fold-r");
  const aryL = $("ary-l"), aryR = $("ary-r"), poolInset = $("pool-inset"), strand = $("strand");
  const particlesG = $("particles"), dropletsG = $("droplets"), insetDropsG = $("inset-drops"), bubblesG = $("bubbles");

  // ---- the airway, as a lookup table along #airway-path --------------------
  const airway = $("airway-path");
  const total = airway.getTotalLength();
  const N = 600;
  const px = new Float32Array(N), py = new Float32Array(N), nx = new Float32Array(N), ny = new Float32Array(N);
  for (let i = 0; i < N; i++) { const p = airway.getPointAtLength((i / (N - 1)) * total); px[i] = p.x; py[i] = p.y; }
  for (let i = 0; i < N; i++) {
    const a = Math.max(0, i - 1), b = Math.min(N - 1, i + 1);
    const tx = px[b] - px[a], ty = py[b] - py[a], len = Math.hypot(tx, ty) || 1;
    nx[i] = -ty / len; ny[i] = tx / len;
  }
  let sGlottis = 0;
  { let best = Infinity; for (let i = 0; i < N; i++) { const d = Math.hypot(px[i] - GLOTTIS.x, py[i] - GLOTTIS.y); if (d < best) { best = d; sGlottis = (i / (N - 1)) * total; } } }
  const halfWidth = (s) => (s < sGlottis ? 13 : 15) * (1 - 0.7 * gauss((s - sGlottis) / 28));

  // ---- pools of elements ---------------------------------------------------
  const MAXP = reducedMotion ? 40 : 90;
  const particles = Array.from({ length: MAXP }, () => ({
    el: el("circle", { r: 0, opacity: 0 }, particlesG), alive: false, s: 0, off: 0, dir: 1, life: 0, maxLife: 1, speed: 1, r: 1,
  }));
  let spawnAcc = 0;

  const drops = DROP_ANCHORS.map((a) => ({ ...a, prog: Math.random(), el: el("ellipse", { cx: a.x, cy: a.y, rx: 0, ry: 0, opacity: 0 }, dropletsG) }));
  const insetDrops = INSET_DROPS.map((a) => ({ ...a, el: el("circle", { r: 0, opacity: 0 }, insetDropsG) }));

  const MAXB = 16;
  const bubbles = Array.from({ length: MAXB }, () => ({ el: el("circle", { r: 0, opacity: 0 }, bubblesG), alive: false, x: 0, y: 0, r: 1, v: 20, seed: Math.random() * 7 }));
  let bubbleAcc = 0;
  let glisten = 0;

  const fmt = (n) => n.toFixed(1);

  function spawnParticle(dir, flow, utter, wet) {
    const p = particles.find((q) => !q.alive);
    if (!p) return;
    p.alive = true; p.dir = dir;
    p.s = dir > 0 ? Math.random() * total * 0.22 : total * (0.86 + Math.random() * 0.14);
    p.off = Math.random() * 2 - 1;
    p.life = 0; p.maxLife = 2.2 + Math.random() * 2.2;
    p.speed = (170 + Math.random() * 90) * (0.25 + Math.abs(flow)) * (1 + utter * 0.9);
    p.r = 1.2 + Math.random() * 1.0;
  }

  function update({ flow, aperture, volume, utter }, wet, dt, now) {
    const turb = (1 - aperture) ** 2 * (0.45 + 0.55 * Math.max(0, flow));   // turbulence at the folds
    const gargle = smoothstep(0.55, 1, wet);

    // ---- lungs, diaphragm, uvula, fold ---------------------------------------
    lungs.setAttribute("transform", `translate(596 915) scale(${1 + 0.05 * volume} ${1 + 0.11 * volume}) translate(-596 -915)`);
    diaphragm.setAttribute("transform", `translate(0 ${fmt(26 * volume)})`);
    uvula.setAttribute("transform", `rotate(${fmt(7 * Math.max(0, flow) + 2 * wet * Math.sin(now / 700))} 596 406)`);
    foldSag.setAttribute("transform", `translate(560 740) scale(${1 + 0.16 * (1 - aperture)} 1) translate(-560 -740)`);

    // ---- airflow -------------------------------------------------------------
    if (Math.abs(flow) > 0.05) {
      spawnAcc += (8 + 40 * Math.abs(flow)) * (1 + utter * 2.5) * dt;
      while (spawnAcc >= 1) { spawnAcc -= 1; spawnParticle(flow > 0 ? 1 : -1, flow, utter, wet); }
    }
    for (const p of particles) {
      if (!p.alive) continue;
      p.life += dt;
      const venturi = 1 + 1.6 * gauss((p.s - sGlottis) / 45);
      p.s += p.dir * p.speed * venturi * dt;
      if (p.dir > 0 && p.s > sGlottis) {
        // downstream of the constriction: the jet breaks up
        p.off += (Math.random() - 0.5) * turb * 34 * dt * Math.exp(-(p.s - sGlottis) / 260);
        p.off = clamp(p.off, -1.5, 1.5);
      }
      if (p.s < 0 || p.s > total || p.life > p.maxLife) {
        p.alive = false; p.el.setAttribute("opacity", 0); continue;
      }
      const f = (p.s / total) * (N - 1), i = Math.floor(f), j = Math.min(N - 1, i + 1), t = f - i;
      const hw = halfWidth(p.s);
      const x = (px[i] + (px[j] - px[i]) * t) + (nx[i] + (nx[j] - nx[i]) * t) * p.off * hw;
      const y = (py[i] + (py[j] - py[i]) * t) + (ny[i] + (ny[j] - ny[i]) * t) * p.off * hw;
      const vapor = p.dir > 0 && p.s > sGlottis ? 1 + 1.8 * smoothstep(0.2, 0.75, wet) : 1;
      p.el.setAttribute("cx", fmt(x)); p.el.setAttribute("cy", fmt(y));
      p.el.setAttribute("r", fmt(p.r * vapor));
      p.el.setAttribute("opacity", (Math.sin(Math.PI * p.life / p.maxLife) * (0.5 + 0.5 * Math.abs(flow)) * (0.9 - 0.3 * smoothstep(0.4, 1, wet))).toFixed(2));
    }

    // ---- moisture in the sagittal view --------------------------------------
    glisten -= dt * (25 + 40 * wet);
    const sheenOp = 0.9 * smoothstep(0.08, 0.6, wet);
    for (const s of sheens) { s.setAttribute("opacity", sheenOp.toFixed(2)); s.setAttribute("stroke-dashoffset", fmt(glisten)); }
    cracks.setAttribute("opacity", (0.7 * smoothstep(0.32, 0.03, wet)).toFixed(2));
    const pooling = smoothstep(0.62, 0.9, wet);
    for (const pool of [poolVallecula, poolVentricle]) {
      pool.setAttribute("opacity", pooling.toFixed(2));
      pool.setAttribute("transform", `translate(${pool.getAttribute("cx")} ${pool.getAttribute("cy")}) scale(${1 + 0.4 * pooling} ${1 + 1.4 * pooling}) translate(-${pool.getAttribute("cx")} -${pool.getAttribute("cy")})`);
    }
    for (const d of drops) {
      const k = smoothstep(d.th, d.th + 0.25, wet);
      if (k <= 0) { if (d.el.getAttribute("rx") !== "0") { d.el.setAttribute("rx", 0); d.el.setAttribute("ry", 0); d.el.setAttribute("opacity", 0); } continue; }
      let x = d.x, y = d.y, stretch = 1, fade = 1;
      if (d.run && wet > d.th + 0.4) {
        d.prog += dt * (0.12 + 0.35 * (wet - d.th - 0.4));
        if (d.prog >= 1) d.prog = 0;
        const e = d.prog * d.prog;                 // eases in: it hangs, then goes
        x += d.run.dx * e; y += d.run.dy * e;
        stretch = 1 + d.prog * 0.9; fade = 1 - d.prog ** 3;
      } else { d.prog = 0; }
      const r = d.size * k * (1 + 0.06 * Math.sin(now / 300 + d.x));
      d.el.setAttribute("cx", fmt(x)); d.el.setAttribute("cy", fmt(y));
      d.el.setAttribute("rx", fmt(r)); d.el.setAttribute("ry", fmt(r * stretch));
      d.el.setAttribute("opacity", (0.9 * k * fade).toFixed(2));
    }

    // ---- the glottis from above ---------------------------------------------
    const { cx, apexY, L } = INSET;
    const flutter = (Math.random() - 0.5) * turb * (reducedMotion ? 0.02 : 0.06);
    const theta = 0.05 + 0.55 * aperture + flutter;
    const sx = L * Math.sin(theta), sy = L * Math.cos(theta);
    const mlx = cx - sx, mrx = cx + sx, my = apexY + sy;
    const tri = `${cx},${apexY} ${fmt(mlx)},${fmt(my)} ${fmt(mrx)},${fmt(my)}`;
    chink.setAttribute("points", tri); chinkClip.setAttribute("points", tri);
    foldL.setAttribute("points", `${cx},${apexY} ${fmt(mlx)},${fmt(my)} ${cx - 86},${INSET.cy + 66} ${cx - 80},${INSET.cy - 20}`);
    foldR.setAttribute("points", `${cx},${apexY} ${fmt(mrx)},${fmt(my)} ${cx + 86},${INSET.cy + 66} ${cx + 80},${INSET.cy - 20}`);
    aryL.setAttribute("cx", fmt(mlx)); aryL.setAttribute("cy", fmt(my));
    aryR.setAttribute("cx", fmt(mrx)); aryR.setAttribute("cy", fmt(my));

    for (const d of insetDrops) {
      const k = smoothstep(d.th, d.th + 0.25, wet);
      d.el.setAttribute("cx", fmt(cx + d.side * (sx * d.t + 11)));
      d.el.setAttribute("cy", fmt(apexY + sy * d.t));
      d.el.setAttribute("r", fmt(d.size * k));
      d.el.setAttribute("opacity", (0.9 * k).toFixed(2));
    }

    // pooling in the chink, with a surface that trembles when the h gargles
    const level = smoothstep(0.5, 1.0, wet);
    let surface = apexY + L + 6;
    if (level > 0) {
      surface = (apexY + L) - level * L * 0.85;
      const amp = 2.2 * (1 + utter * 4 * gargle);
      let d = `M ${cx - 90} ${fmt(surface + amp * Math.sin(now / 170 + (cx - 90) / 11))}`;
      for (let x = cx - 70; x <= cx + 90; x += 20) d += ` L ${x} ${fmt(surface + amp * Math.sin(now / 170 + x / 11))}`;
      d += ` L ${cx + 90} 910 L ${cx - 90} 910 Z`;
      poolInset.setAttribute("d", d);
      poolInset.setAttribute("opacity", "1");
    } else {
      poolInset.setAttribute("opacity", "0");
    }
    bubbleAcc += (Math.max(0, wet - 0.62) * 10 + utter * 30 * gargle) * dt;
    while (bubbleAcc >= 1) {
      bubbleAcc -= 1;
      const b = bubbles.find((q) => !q.alive);
      if (!b || level <= 0) break;
      b.alive = true; b.x = mlx + 6 + Math.random() * Math.max(4, mrx - mlx - 12); b.y = my - 6;
      b.r = 1.2 + Math.random() * 2.6; b.v = 18 + Math.random() * 22;
    }
    for (const b of bubbles) {
      if (!b.alive) continue;
      b.y -= b.v * dt; b.x += Math.sin(now / 120 + b.seed) * 6 * dt;
      if (b.y - b.r < surface + 1) { b.alive = false; b.el.setAttribute("opacity", 0); continue; }
      b.el.setAttribute("cx", fmt(b.x)); b.el.setAttribute("cy", fmt(b.y)); b.el.setAttribute("r", fmt(b.r));
      b.el.setAttribute("opacity", "0.8");
    }

    // a strand of mucus bridging the folds, once things are properly wet
    const strandOp = smoothstep(0.66, 0.92, wet);
    if (strandOp > 0) {
      const t = 0.62;
      const lx = cx - sx * t + 2, rx = cx + sx * t - 2, y = apexY + sy * t;
      strand.setAttribute("d", `M ${fmt(lx)} ${fmt(y)} Q ${cx} ${fmt(y + 9 + 3 * Math.sin(now / 300) + utter * 6)} ${fmt(rx)} ${fmt(y)}`);
    }
    strand.setAttribute("opacity", strandOp.toFixed(2));
  }

  return { update, get glottis() { return GLOTTIS; } };
}
