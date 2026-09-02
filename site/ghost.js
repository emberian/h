// ghost.js — the h's murmur.
//
// A tiny causal language model lives in the page (see ghost-worker.js). It
// does not chat. Every so often — and whenever the knob settles somewhere new
// — it is handed a prompt stitched from fragments chosen by the page's state
// (wetness band, breath count, time on page) and asked for 8–24 tokens at a
// temperature that rises with wetness. The tokens drift out of the mouth as
// faint text and fade. Per-token entropy comes back too, and main.js lets it
// tint the h's glow and lean on the breath's pace.
//
// If there is no WebGPU, no WASM, no network, or the worker dies, the ghost is
// simply absent: the page breathes and speaks without it.

import { config } from "./config.js";

const SEEDS = {
  dry: [
    "dust", "parchment", "a cracked throat", "desert air", "whisper",
    "the breath before the word", "nothing happens in the mouth",
    "candlelight, Königsberg, winter", "the letter that barely exists",
    "bone dry", "chalk", "the aspiration", "paper", "h",
  ],
  mid: [
    "dew", "humidity", "fog on the inside of the window", "condensation",
    "the mouth is open, passive", "a resonating chamber", "rain beginning",
    "the wet pop of a consonant", "breath on glass", "mist", "h",
    "the glottis narrows", "everything happens in the throat",
  ],
  wet: [
    "saliva", "the glottis drowning in its own production", "gargle",
    "mucus", "the letter soaked", "obscene and alive", "rain", "drowning",
    "a wet mouth", "the breath catches fluid", "bubbles", "h", "gurgle",
    "the body that produces", "swallow",
  ],
};
const TAILS = [",", " —", "", ";", ",", "\n"];

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Build the prompt from page state. Deterministic in (count, minutes, wetness band). */
export function buildPrompt({ wetness, breathCount, secondsOnPage }) {
  const minutes = Math.floor(secondsOnPage / 60);
  const rng = mulberry32((breathCount * 7919 + minutes * 104729 + Math.floor(wetness * 9)) >>> 0);
  const band = wetness < 0.33 ? "dry" : wetness < 0.66 ? "mid" : "wet";
  // lean into the neighbouring band sometimes, so the edges blur
  const pool = SEEDS[band].concat(rng() < 0.35 ? SEEDS[wetness < 0.5 ? "mid" : band === "wet" ? "mid" : "dry"] : []);
  const n = 1 + Math.floor(rng() * 2.4);       // 1–3 fragments
  const picks = [];
  for (let i = 0; i < n; i++) picks.push(pool[Math.floor(rng() * pool.length)]);
  if (minutes >= 60) picks.push("an hour of breathing");
  else if (minutes >= 10) picks.push("still here");
  if (breathCount > 0 && breathCount % 100 === 0) picks.push(`the ${breathCount}th breath`);
  return picks.join("\n") + TAILS[Math.floor(rng() * TAILS.length)];
}

export function createGhost({ getState, mouthAnchor, layer, dot, onSignal, reducedMotion = false }) {
  let worker = null;
  let status = "idle";           // idle | loading | ready | unavailable
  let busy = false;
  let reqId = 0;
  let current = null;            // { id, el }
  let idleTimer = 0;
  let lastWetSpoken = null;
  let ema = null;                // running mean of per-token entropy (nats)
  const gen = config.generation;

  function setDot(state) { if (dot) dot.dataset.state = state; }

  function schedule(ms) {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => speak("idle"), ms);
  }
  function jitter() { return gen.idleInterval.min + Math.random() * (gen.idleInterval.max - gen.idleInterval.min); }

  function speak(reason) {
    if (status !== "ready" || busy) return;
    const state = getState();
    busy = true;
    setDot("thinking");
    const id = ++reqId;
    const w = state.wetness;
    lastWetSpoken = w;
    const maxNewTokens = gen.minNewTokens + Math.floor(Math.random() * (gen.maxNewTokens - gen.minNewTokens + 1));
    worker.postMessage({
      type: "generate", id,
      prompt: buildPrompt(state),
      maxNewTokens,
      temperature: gen.temperature.dry + (gen.temperature.wet - gen.temperature.dry) * w,
      topK: gen.topK,
      repetitionPenalty: gen.repetitionPenalty,
      reason,
    });
    current = { id, el: null };
  }

  /**
   * A fragment forms at the lips while its tokens arrive (hovering, so a slow
   * ghost is not outrun by its own animation), then drifts out and fades.
   */
  function birth() {
    const { x, y } = mouthAnchor();
    const el = document.createElement("span");
    el.className = "murmur";
    el.style.right = `${Math.round(window.innerWidth - x)}px`;
    el.style.top = `${Math.round(y - 8)}px`;
    layer.appendChild(el);
    el._hover = el.animate(
      [
        { transform: "translate(0,0)", opacity: 0 },
        { transform: "translate(-2px,-3px)", opacity: 0.6, offset: 0.15 },
        { transform: "translate(-4px,-1px)", opacity: 0.55, offset: 0.55 },
        { transform: "translate(-2px,-4px)", opacity: 0.6 },
      ],
      { duration: 6000 * (reducedMotion ? 2 : 1), iterations: Infinity, direction: "alternate", easing: "ease-in-out" },
    );
    return el;
  }

  function release(el) {
    if (!el) return;
    el._hover?.cancel();
    if (!el.textContent.trim()) { el.remove(); return; }
    const dx = -(80 + Math.random() * 140), dy = -(10 + Math.random() * 110);
    const rot = (Math.random() - 0.5) * 6;
    const dur = (9000 + Math.random() * 5000) * (reducedMotion ? 1.8 : 1);
    el.animate(
      [
        { transform: "translate(-2px,-3px) rotate(0deg)", opacity: 0.6 },
        { opacity: 0.5, offset: 0.65 },
        { transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg)`, opacity: 0 },
      ],
      { duration: dur, easing: "cubic-bezier(.2,.5,.4,1)", fill: "forwards" },
    ).onfinish = () => el.remove();
  }

  function onMessage(e) {
    const m = e.data;
    switch (m.type) {
      case "progress":
        setDot("loading");
        break;
      case "ready":
        status = "ready";
        setDot("ready");
        console.info("[ghost] present, on", m.device);
        schedule(2500);
        break;
      case "unavailable":
        status = "unavailable";
        setDot("off");
        console.info("[ghost] absent:", m.reason);
        break;
      case "note":
        console.info("[ghost]", m.text);
        break;
      case "text":
        if (!current || m.id !== current.id) return;
        if (!current.el) current.el = birth();
        current.el.textContent += m.text.replace(/\s+/g, " ");
        break;
      case "token":
        if (!current || m.id !== current.id) return;
        ema = ema === null ? m.entropy : ema * 0.8 + m.entropy * 0.2;
        onSignal?.({ entropy: m.entropy, logprob: m.logprob, pmax: m.pmax, ema });
        break;
      case "done":
      case "error":
        if (m.type === "error") console.info("[ghost] generation error:", m.reason);
        else if (!m.skipped) console.debug(`[ghost] ${m.reason ?? ""} ${JSON.stringify(m.text)} · mean entropy ${ema?.toFixed(2)} nats`);
        if (current && m.id === current.id) release(current.el);
        busy = false;
        current = null;
        setDot("ready");
        schedule(jitter());
        break;
    }
  }

  return {
    get status() { return status; },
    get entropy() { return ema; },

    start() {
      if (status !== "idle") return;
      try {
        worker = new Worker(new URL("./ghost-worker.js", import.meta.url), { type: "module" });
      } catch (e) {
        status = "unavailable"; setDot("off");
        console.info("[ghost] absent: no module workers:", e?.message || e);
        return;
      }
      worker.onmessage = onMessage;
      worker.onerror = (e) => {
        if (status !== "ready") { status = "unavailable"; setDot("off"); }
        console.info("[ghost] worker error:", e?.message || e);
      };
      status = "loading";
      setDot("loading");
      worker.postMessage({ type: "load" });
    },

    /** The page changed in a way the ghost might notice. */
    poke(reason) {
      if (status !== "ready" || busy) return;
      const w = getState().wetness;
      if (reason === "knob") {
        if (lastWetSpoken !== null && Math.abs(w - lastWetSpoken) < 0.08) return;
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => speak("knob"), 600);
      } else if (reason === "speak") {
        if (Math.random() < 0.4) { clearTimeout(idleTimer); idleTimer = setTimeout(() => speak("speak"), 900); }
      }
    },
  };
}
