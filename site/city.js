// city.js — the skyline behind everything, subsiding.
//
// Each building has its own tilt and sink rate. Every completed breath nudges
// its target; every frame the drawn pose eases toward the target, so the
// motion is continuous — pixel by pixel. Per breath the tilt is a few
// hundredths of a degree: nothing for thirty seconds, measurable after a
// minute, and after an hour (~700 breaths) the skyline is leaning hard and
// the lights have mostly gone out. Toppling accelerates once a lean starts.
//
// Buildings are pre-rendered to sprites (windows included); the frame loop
// only draws transformed images.

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function createCity(canvas) {
  const ctx = canvas.getContext("2d");
  const rng = mulberry32((Date.now() ^ 0x5eed) >>> 0);
  let W = 0, H = 0, dpr = 1;
  let layers = [];
  let rain = [];
  let breaths = 0;

  function gauss() { // Box–Muller
    const u = 1 - rng(), v = rng();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  function makeBuilding(x, w, h, layer) {
    const cols = Math.max(1, Math.floor(w / 9));
    const rows = Math.max(1, Math.floor(h / 12));
    const lit = new Uint8Array(cols * rows);
    const litP = 0.12 + rng() * 0.25;
    for (let i = 0; i < lit.length; i++) lit[i] = rng() < litP ? 1 : 0;
    const fast = rng() < 0.15 ? 3 : 1;             // a few go early
    return {
      x, w, h, layer, cols, rows, lit,
      tilt: 0, tiltT: 0,
      tiltRate: gauss() * 0.00055 * fast,           // radians per breath
      sink: 0, sinkT: 0,
      sinkRate: (0.0004 + rng() * 0.0005) * h,      // px per breath
      antenna: h > 120 && rng() < 0.3 ? 10 + rng() * 25 : 0,
      sprite: null, dirty: true,
    };
  }

  function layout() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = Math.floor(W * dpr); canvas.height = Math.floor(H * dpr);
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const old = layers;
    layers = [
      { alpha: 0.55, tint: "#0f1119", horizonLift: 26, spacing: 26, hMul: 0.55, list: [] }, // far
      { alpha: 1.0, tint: "#14161f", horizonLift: 0, spacing: 34, hMul: 1.0, list: [] },    // near
    ];
    layers.forEach((L, li) => {
      let x = -40 + rng() * 20;
      let i = 0;
      while (x < W + 40) {
        const w = L.spacing * (0.6 + rng() * 1.3);
        const tall = rng() < 0.12;
        const h = (tall ? 160 + rng() * 140 : 40 + rng() * 110) * L.hMul * Math.min(1, H / 700);
        // keep subsidence state across resizes where a building already exists
        const prev = old[li]?.list[i];
        const b = prev ? { ...prev, x, w, h: prev.h, sprite: null, dirty: true } : makeBuilding(x, w, h, li);
        if (prev) { b.cols = Math.max(1, Math.floor(w / 9)); if (b.cols * b.rows !== b.lit.length) b.lit = b.lit.slice(0, b.cols * b.rows); }
        L.list.push(b);
        x += w + 2 + rng() * 8;
        i++;
      }
    });
    rain = Array.from({ length: 160 }, () => ({ x: rng() * W, y: rng() * H, v: 400 + rng() * 300, l: 8 + rng() * 14 }));
  }

  function renderSprite(b, tint) {
    const pad = 2;
    const c = document.createElement("canvas");
    c.width = Math.ceil((b.w + pad * 2) * dpr);
    c.height = Math.ceil((b.h + b.antenna + pad * 2) * dpr);
    const g = c.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const top = pad + b.antenna;
    g.fillStyle = tint;
    g.fillRect(pad, top, b.w, b.h);
    g.fillStyle = "rgba(255,255,255,0.045)";
    g.fillRect(pad, top, b.w, 1);               // a lit roof edge
    if (b.antenna) { g.fillStyle = "rgba(180,180,200,0.35)"; g.fillRect(pad + b.w / 2, pad, 1, b.antenna); }
    const cw = b.w / b.cols, rh = b.h / b.rows;
    for (let r = 0; r < b.rows; r++) for (let col = 0; col < b.cols; col++) {
      if (!b.lit[r * b.cols + col]) continue;
      const warm = (r * 7 + col * 3) % 5 === 0;
      g.fillStyle = warm ? "rgba(255,196,120,0.42)" : "rgba(214,206,190,0.30)";
      g.fillRect(pad + col * cw + cw * 0.3, top + r * rh + rh * 0.3, Math.max(1, cw * 0.4), Math.max(1, rh * 0.45));
    }
    b.sprite = c; b.dirty = false;
  }

  /** Called once per completed breath. */
  function subside() {
    breaths++;
    for (const L of layers) for (const b of L.list) {
      // toppling: rate grows with the lean already present
      b.tiltT += b.tiltRate * (1 + 3 * Math.abs(Math.sin(b.tiltT)));
      b.sinkT += b.sinkRate * (1 + 2 * Math.abs(Math.sin(b.tiltT)));
      // wiring fails as the building goes: a light goes out now and then
      if (b.lit.length && rng() < 0.15 + Math.abs(b.tiltT) * 2) {
        const i = Math.floor(rng() * b.lit.length);
        if (b.lit[i]) { b.lit[i] = 0; b.dirty = true; }
        else if (rng() < 0.15) { b.lit[i] = 1; b.dirty = true; }  // someone comes home
      }
    }
  }

  function render(dt, wetness) {
    ctx.clearRect(0, 0, W, H);
    const horizon = H * 0.86;

    // haze on the horizon; warmer when dry, colder when wet
    const hz = ctx.createLinearGradient(0, horizon - 220, 0, horizon);
    hz.addColorStop(0, "rgba(0,0,0,0)");
    hz.addColorStop(1, wetness > 0.5 ? "rgba(70,90,120,0.10)" : "rgba(120,90,60,0.07)");
    ctx.fillStyle = hz; ctx.fillRect(0, horizon - 220, W, 220);

    for (const L of layers) {
      ctx.globalAlpha = L.alpha;
      const base = horizon - L.horizonLift;
      for (const b of L.list) {
        // ease toward the per-breath target: continuous motion
        b.tilt += (b.tiltT - b.tilt) * Math.min(1, dt * 0.9);
        b.sink += (b.sinkT - b.sink) * Math.min(1, dt * 0.9);
        if (b.dirty || !b.sprite) renderSprite(b, L.tint);
        // pivot on the corner it is sinking into
        const px = b.tilt > 0 ? b.x + b.w : b.x;
        ctx.save();
        ctx.translate(px, base + b.sink);
        ctx.rotate(b.tilt);
        ctx.drawImage(b.sprite, (b.tilt > 0 ? -b.w : 0) - 2, -(b.h + b.antenna) - 2, b.w + 4, b.h + b.antenna + 4);
        ctx.restore();
      }
    }
    ctx.globalAlpha = 1;

    // the ground swallows what sinks
    const gnd = ctx.createLinearGradient(0, horizon - 4, 0, H);
    gnd.addColorStop(0, "rgba(6,6,9,0)");
    gnd.addColorStop(0.08, "rgba(6,6,9,0.9)");
    gnd.addColorStop(1, "rgba(3,3,5,1)");
    ctx.fillStyle = gnd; ctx.fillRect(0, horizon - 4, W, H - horizon + 4);

    // rain, once the air is saturated
    const r = Math.max(0, (wetness - 0.6) / 0.4);
    if (r > 0) {
      ctx.strokeStyle = `rgba(170,200,230,${0.10 * r})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      const nR = Math.floor(rain.length * r);
      for (let i = 0; i < nR; i++) {
        const d = rain[i];
        d.y += d.v * dt; if (d.y > H) { d.y = -20; d.x = rng() * W; }
        ctx.moveTo(d.x, d.y); ctx.lineTo(d.x - 1.5, d.y + d.l);
      }
      ctx.stroke();
    }
  }

  layout();
  let resizeT = 0;
  window.addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(layout, 120); });

  return { subside, render, get breaths() { return breaths; } };
}
