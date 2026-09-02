// knob.js — Wetness.
//
// Oversized, continuous, no detents, no numbers. Drag it round with a mouse
// or a finger (angular drag about its center), nudge it with arrow keys, or
// spin the wheel over it. The shown angle chases the true value through an
// underdamped spring, so it overshoots and wobbles; the sheen swings with
// drag velocity; condensation beads on the face past the midpoint and runs
// once it is soaked; the word underneath is displaced by liquid noise until
// it is barely legible. The value persists in localStorage.
//
// The knob knows nothing about sound or anatomy: it reports value changes via
// `onInput` (every change) and `onSettle` (~350 ms after the last change).

const STORAGE_KEY = "h.wetness";
const SWEEP = 270;                                 // degrees of travel
const clamp01 = (x) => Math.max(0, Math.min(1, x));

const WORDS = ["parched", "dry", "dew", "humid", "fog", "rain", "dripping", "soaked", "gargling"];

export function loadWetness(fallback = 0.3) {
  try {
    const v = parseFloat(localStorage.getItem(STORAGE_KEY));
    return Number.isFinite(v) ? clamp01(v) : fallback;
  } catch { return fallback; }
}

export function createKnob(root, { value = 0.3, onInput, onSettle, reducedMotion = false }) {
  const el = root.querySelector(".knob");
  const tilt = root.querySelector(".knob-tilt");
  const body = root.querySelector(".knob-body");
  const dropsLayer = root.querySelector(".knob-drops");
  const label = root.querySelector(".knob-label");
  const displace = label.querySelector("feDisplacementMap");
  const turb = label.querySelector("feTurbulence");

  let target = clamp01(value);
  let shown = target;          // what is drawn (spring-lagged)
  let springV = 0;             // spring velocity (value units / s)
  let inputV = 0;              // user's turning speed, EMA (value units / s)
  let lastInputT = 0;
  let settleTimer = 0;
  let sheen = 0;               // 0..1, decays
  let sheenDir = 1;
  let dragging = false, lastAngle = 0, lastMoveT = 0;
  let dropCooldown = 0;
  let drops = [];              // { el, x, y, r, running }
  let seedT = 0;

  const angleOf = (v) => -SWEEP / 2 + v * SWEEP;

  function persist() {
    try { localStorage.setItem(STORAGE_KEY, target.toFixed(4)); } catch { /* private mode etc. */ }
  }

  function announce() {
    el.setAttribute("aria-valuenow", Math.round(target * 100));
    el.setAttribute("aria-valuetext", WORDS[Math.min(WORDS.length - 1, Math.floor(target * WORDS.length))]);
  }

  function set(v, now = performance.now()) {
    const next = clamp01(v);
    const dt = Math.max(0.008, (now - lastInputT) / 1000);
    const rate = (next - target) / dt;
    inputV = inputV * 0.6 + rate * 0.4;
    lastInputT = now;
    if (next === target) return;
    sheenDir = Math.sign(next - target) || sheenDir;
    sheen = Math.min(1, sheen + Math.abs(next - target) * 6);
    target = next;
    announce();
    onInput?.(target, inputV);
    clearTimeout(settleTimer);
    settleTimer = setTimeout(() => { persist(); onSettle?.(target); }, 350);
  }

  // ---- pointer: angular drag about the center -----------------------------
  function pointerAngle(e) {
    const r = el.getBoundingClientRect();
    return Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2)) * 180 / Math.PI;
  }
  el.addEventListener("pointerdown", (e) => {
    if (e.button !== undefined && e.button !== 0) return;
    el.setPointerCapture(e.pointerId);
    dragging = true;
    lastAngle = pointerAngle(e);
    lastMoveT = performance.now();
    el.classList.add("is-dragging");
    el.focus({ preventScroll: true });
    e.preventDefault();
  });
  el.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const a = pointerAngle(e);
    let d = a - lastAngle;
    if (d > 180) d -= 360; else if (d < -180) d += 360;
    lastAngle = a;
    set(target + d / SWEEP, e.timeStamp || performance.now());
  });
  const release = () => { if (!dragging) return; dragging = false; el.classList.remove("is-dragging"); };
  el.addEventListener("pointerup", release);
  el.addEventListener("pointercancel", release);
  el.addEventListener("lostpointercapture", release);

  // ---- keyboard & wheel ---------------------------------------------------
  el.addEventListener("keydown", (e) => {
    const step = (e.shiftKey ? 0.05 : 0.01);
    const map = { ArrowUp: step, ArrowRight: step, ArrowDown: -step, ArrowLeft: -step, PageUp: 0.1, PageDown: -0.1 };
    if (e.key in map) { set(target + map[e.key]); e.preventDefault(); }
    else if (e.key === "Home") { set(0); e.preventDefault(); }
    else if (e.key === "End") { set(1); e.preventDefault(); }
  });
  el.addEventListener("wheel", (e) => {
    set(target - e.deltaY * 0.0008);
    e.preventDefault();
  }, { passive: false });

  // ---- condensation -------------------------------------------------------
  function spawnDrop() {
    const R = el.clientWidth / 2;
    const a = Math.random() * Math.PI * 2;
    const rr = R * (0.15 + Math.sqrt(Math.random()) * 0.72);
    const d = {
      el: document.createElement("i"),
      x: R + Math.cos(a) * rr, y: R + Math.sin(a) * rr,
      r: 1.5 + Math.random() * Math.random() * 6,
      running: false,
    };
    d.el.className = "drop";
    d.el.style.cssText = `left:${d.x}px;top:${d.y}px;width:${d.r * 2}px;height:${d.r * 2}px`;
    dropsLayer.appendChild(d.el);
    drops.push(d);
  }
  function evaporate(d) {
    d.el.classList.add("is-gone");
    setTimeout(() => d.el.remove(), 900);
  }
  function run(d) {
    d.running = true;
    const R = el.clientWidth / 2;
    const dy = Math.min(R * 1.9 - d.y, 18 + Math.random() * 50);
    const anim = d.el.animate(
      [
        { transform: "translate(-50%,-50%) scale(1,1)" },
        { transform: "translate(-50%,-30%) scale(0.85,1.5)", offset: 0.3 },
        { transform: `translate(-50%, calc(-50% + ${dy}px)) scale(0.6,1.2)`, opacity: 0.2 },
      ],
      { duration: (1400 + Math.random() * 1600) * (reducedMotion ? 2 : 1), easing: "cubic-bezier(.5,0,.9,.6)", fill: "forwards" },
    );
    anim.onfinish = () => { d.el.remove(); drops = drops.filter((x) => x !== d); };
  }

  // ---- per-frame ----------------------------------------------------------
  function tick(dt, now) {
    // spring: underdamped unless the user prefers reduced motion
    const k = reducedMotion ? 120 : 260, c = reducedMotion ? 22 : 9;
    springV += (-k * (shown - target) - c * springV) * dt;
    shown += springV * dt;

    // decay of the user's turning speed and the sheen it throws
    inputV *= Math.exp(-dt * 4);
    sheen *= Math.exp(-dt * 2.2);

    const ang = angleOf(shown);
    body.style.transform = `rotate(${ang}deg)`;
    const v = Math.max(-1, Math.min(1, springV * 0.8));
    tilt.style.setProperty("--wob-y", `${v * 9}deg`);
    tilt.style.setProperty("--wob-x", `${-Math.abs(v) * 3}deg`);
    tilt.style.setProperty("--wob-s", `${1 + Math.abs(v) * 0.035}`);
    el.style.setProperty("--sheen-a", `${ang + 90 + sheenDir * 38}deg`);
    el.style.setProperty("--sheen-s", `${(0.08 + sheen * 0.9).toFixed(3)}`);
    root.style.setProperty("--wet", clamp01(shown).toFixed(4));

    // the word gets wetter
    displace.setAttribute("scale", (shown * 16 + sheen * 6).toFixed(2));
    seedT += dt * (0.4 + shown * 1.5);
    turb.setAttribute("seed", String(Math.floor(seedT) % 100));

    // condensation count follows wetness past the midpoint; runs when soaked
    const wanted = Math.round(Math.max(0, (shown - 0.5) / 0.5) * 42 * (1 + Math.min(1, Math.abs(inputV)) * 0.6));
    dropCooldown -= dt;
    const still = drops.filter((d) => !d.running);
    if (still.length < wanted && dropCooldown <= 0) { spawnDrop(); dropCooldown = 0.05; }
    else if (still.length > wanted + 3 && dropCooldown <= 0) { const d = still[0]; drops = drops.filter((x) => x !== d); evaporate(d); dropCooldown = 0.12; }
    if (shown > 0.78) {
      const p = dt * (shown - 0.78) * 0.7;
      for (const d of still) if (d.r > 3 && Math.random() < p) run(d);
    }
  }

  announce();
  root.style.setProperty("--wet", shown.toFixed(4));
  return {
    get value() { return target; },
    set value(v) { set(v); },
    tick,
  };
}
