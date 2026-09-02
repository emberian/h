// main.js — wiring.
//
// One requestAnimationFrame loop drives the breath clock and hands its state
// to the mouth, the voice, the city, the knob, and the h itself. The ghost
// runs on its own cadence in a worker and only reaches in through CSS
// variables (--glow) and a lean on the breath's pace.

import { config } from "./config.js";
import { createBreath } from "./breath.js";
import { createMouth } from "./mouth.js";
import { createVoice } from "./voice.js";
import { createKnob, loadWetness } from "./knob.js";
import { createCity } from "./city.js";
import { createGhost } from "./ghost.js";

const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const root = document.documentElement;
const params = new URLSearchParams(location.search);

const reducedMQ = matchMedia("(prefers-reduced-motion: reduce)");
let reduced = reducedMQ.matches;
reducedMQ.addEventListener?.("change", (e) => { reduced = e.matches; });
const basePeriod = () => (reduced ? config.breath.reducedPeriodMs : config.breath.periodMs);

const svg = document.getElementById("tract");
const hEl = document.getElementById("h");
const countEl = document.getElementById("count");
const knobWrap = document.getElementById("knob-wrap");
const murmurLayer = document.getElementById("murmur");
const dot = document.getElementById("ghost-dot");

// ---- the parts ------------------------------------------------------------
const breath = createBreath({ periodMs: basePeriod() });
const mouth = createMouth(svg, { reducedMotion: reduced });
const voice = createVoice();
const city = createCity(document.getElementById("city"));

let wetness = loadWetness(0.3);
const knob = createKnob(knobWrap, {
  value: wetness,
  reducedMotion: reduced,
  onInput: (v, velocity) => { wetness = v; voice.setWetness(v); voice.knobTick(v, velocity); },
  onSettle: () => ghost.poke("knob"),
});
voice.setWetness(wetness);

const openedAt = performance.now();
let utterance = null;      // { start: ms, duration: s } while the h is speaking
let lean = 0;              // the ghost's entropy leaning on the breath's pace (-1..1)
let glow = 0.35, glowTarget = 0.35;

const ghost = createGhost({
  getState: () => ({ wetness, breathCount: breath.count, secondsOnPage: (performance.now() - openedAt) / 1000 }),
  mouthAnchor,
  layer: murmurLayer,
  dot,
  reducedMotion: reduced,
  onSignal: ({ ema }) => {
    // ~0 nats = certain, ~4.5 nats = diffuse. Diffuse → brighter, quicker breath.
    const norm = clamp(ema / 4.5, 0, 1);
    glowTarget = 0.2 + 0.8 * norm;
    lean = (norm - 0.5) * 2;
  },
});

/** Screen position of the lips, for the murmur to be born at. */
function mouthAnchor() {
  const m = svg.getScreenCTM();
  if (!m) return { x: innerWidth / 2, y: innerHeight / 2 };
  const pt = svg.createSVGPoint(); pt.x = 250; pt.y = 466;
  const p = pt.matrixTransform(m);
  return { x: p.x, y: p.y };
}

/** 0..1 envelope of the current utterance: quick rise, hold, long fall. */
function utteranceEnvelope(now) {
  if (!utterance) return 0;
  const t = (now - utterance.start) / 1000 / utterance.duration;
  if (t >= 1) { utterance = null; return 0; }
  if (t < 0.12) return t / 0.12;
  if (t < 0.5) return 1;
  return 1 - (t - 0.5) / 0.5;
}

// ---- the h speaks -----------------------------------------------------------
async function speak() {
  await voice.unlock();                       // first click unlocks audio (autoplay policy)
  const { duration } = voice.speak();
  utterance = { start: performance.now(), duration };
  hEl.style.setProperty("--speak-dur", `${duration}s`);
  hEl.classList.remove("is-speaking");
  void hEl.offsetWidth;                       // restart the animation
  hEl.classList.add("is-speaking");
  ghost.poke("speak");
}
hEl.addEventListener("click", speak);

document.addEventListener("visibilitychange", () => voice.setMuted(document.hidden));

// ---- the loop --------------------------------------------------------------
let last = performance.now();
function frame(now) {
  const dt = clamp((now - last) / 1000, 0, 0.1);   // a hidden tab does not breathe in bulk on return
  last = now;

  lean *= Math.exp(-dt / 25);                        // the ghost's influence fades back to baseline
  breath.period = basePeriod() * (1 - 0.12 * lean);
  const st = breath.update(dt);
  if (st.completed) {
    countEl.textContent = String(st.count);
    city.subside();
  }

  const utter = utteranceEnvelope(now);
  const flow = Math.max(st.flow, utter);
  const aperture = st.aperture + (0.2 - st.aperture) * utter;   // the utterance narrows the glottis

  knob.tick(dt, now);
  mouth.update({ flow, aperture, volume: st.volume, utter }, wetness, dt, now);
  city.render(dt, wetness);
  voice.breathe(st.flow, st.aperture);

  glow += (glowTarget - glow) * Math.min(1, dt * 2);
  root.style.setProperty("--breath", st.volume.toFixed(3));
  root.style.setProperty("--glow", (glow + 0.1 * st.volume + 0.5 * utter).toFixed(3));

  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

// The ghost arrives a moment after the page has started breathing.
// `?ghost=off` keeps it away (useful when working on everything else).
if (params.get("ghost") !== "off") setTimeout(() => ghost.start(), 1500);
