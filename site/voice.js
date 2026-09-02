// voice.js — the sound of /h/, synthesized from the simulation's parameters.
//
// No samples. A looped white-noise source is the "lungs"; a high-pass whose
// cutoff follows glottal aperture is the turbulence at the folds; three wide
// band-passes (~500 / 1500 / 2500 Hz) are the open, passive vocal tract; and
// a wetness stage morphs continuously from dry aspiration (brittle, high-
// passed, with random grain) through humid (a low-mid resonance and a slow
// chorus, like fog on glass) to gargle (20–40 Hz amplitude modulation with
// jitter, bubbling resonators, liquid clicks).
//
// Browser autoplay policy: nothing is built until unlock() runs inside a user
// gesture — main.js calls it on the first click on the h.

const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

/** The three wetness regimes, each 0..1, overlapping so the morph is continuous. */
export function wetMix(w) {
  return {
    dry: smoothstep(0.5, 0.0, w),                       // 1 at bone-dry, gone by w≈0.5
    humid: clamp(1 - Math.abs(w - 0.5) / 0.4, 0, 1),    // peaks at the middle
    gargle: smoothstep(0.55, 1.0, w),                   // rises through the top half
  };
}

export function createVoice() {
  let ctx = null;
  let n = null;             // node graph, built on unlock
  let wet = 0.3;
  let unlocked = false;
  let utteranceEnd = 0;     // ctx time when the current utterance stops
  let lastBedUpdate = 0;
  let lastTick = 0;
  let clickTimer = 0;

  // ---- helpers -------------------------------------------------------------

  function noiseBuffer(seconds) {
    const len = Math.floor(ctx.sampleRate * seconds);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    return buf;
  }
  function noiseSource(buf, offset = 0) {
    const s = ctx.createBufferSource();
    s.buffer = buf; s.loop = true; s.start(0, offset);
    return s;
  }
  function biquad(type, frequency, Q, gain = 0) {
    const f = ctx.createBiquadFilter();
    f.type = type; f.frequency.value = frequency; f.Q.value = Q; f.gain.value = gain;
    return f;
  }
  function gain(v) { const g = ctx.createGain(); g.gain.value = v; return g; }
  function chain(...nodes) { for (let i = 0; i < nodes.length - 1; i++) nodes[i].connect(nodes[i + 1]); return nodes[nodes.length - 1]; }

  /** A slow random signal: white noise → very low lowpass → amplified. Drives jitter. */
  function wander(buf, cutoffHz, amount, offset) {
    const src = noiseSource(buf, offset);
    const lp = biquad("lowpass", cutoffHz, 0.5);
    const g = gain(amount);
    chain(src, lp, g);
    return g;
  }

  // ---- graph ---------------------------------------------------------------

  function build() {
    const AC = window.AudioContext || window.webkitAudioContext;
    ctx = new AC({ latencyHint: "interactive" });
    const buf = noiseBuffer(4);

    // Lungs → glottis
    const lungs = noiseSource(buf);
    const glottalHP = biquad("highpass", 300, 0.7);   // turbulence brightness follows aperture
    const glottal = gain(0);                          // the breath envelope
    chain(lungs, glottalHP, glottal);

    // The vocal tract: open, passive, a resonating chamber.
    const sum = gain(1);
    const direct = gain(0.32);
    glottal.connect(direct).connect(sum);
    const formants = [
      [500, 2.2, 1.0],
      [1500, 2.8, 0.7],
      [2500, 3.2, 0.5],
    ].map(([f, q, g]) => {
      const bp = biquad("bandpass", f, q); const out = gain(g);
      glottal.connect(bp).connect(out).connect(sum);
      return bp;
    });

    // Humid: a low-mid resonance, the tract lined with moisture.
    const humidRes = biquad("bandpass", 260, 5);
    const humidGain = gain(0);
    glottal.connect(humidRes).connect(humidGain).connect(sum);

    // Gargle: bubbling — three narrow resonators whose centers wander.
    const bubbleGain = gain(0);
    const bubbles = [420, 640, 900].map((f, i) => {
      const bp = biquad("bandpass", f, 14);
      wander(buf, 1.5, 26000, 0.7 + i * 0.9).connect(bp.frequency);
      glottal.connect(bp).connect(bubbleGain);
      return bp;
    });
    bubbleGain.connect(sum);

    // Wetness tone: dry = high-passed and brittle; gargle = dull, mouth full.
    const dryHP = biquad("highpass", 180, 0.8);
    const tractLP = biquad("lowpass", 7500, 0.6);

    // Dry grain: a random on/off flutter, the cracked throat.
    const crackle = gain(1);
    const crackleShape = ctx.createWaveShaper();
    { const c = new Float32Array(1024); for (let i = 0; i < 1024; i++) c[i] = (i / 1023) * 2 - 1 > 0.25 ? 1 : 0; crackleShape.curve = c; }
    const crackleDepth = gain(0);
    chain(wander(buf, 22, 40, 2.3), crackleShape, crackleDepth).connect(crackle.gain);

    // Gargle AM: 20–40 Hz, jittered.
    const am = gain(1);
    const lfo = ctx.createOscillator(); lfo.type = "sine"; lfo.frequency.value = 30; lfo.start();
    wander(buf, 2.5, 900, 3.1).connect(lfo.frequency);
    const amDepth = gain(0);
    lfo.connect(amDepth).connect(am.gain);

    // Chorus: moisture smearing the resonance.
    const chorusDry = gain(1);
    const delay = ctx.createDelay(0.05); delay.delayTime.value = 0.009;
    const chorusLFO = ctx.createOscillator(); chorusLFO.frequency.value = 0.55; chorusLFO.start();
    const chorusDepth = gain(0.0025);
    chorusLFO.connect(chorusDepth).connect(delay.delayTime);
    const chorusWet = gain(0);

    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -20; comp.ratio.value = 4; comp.attack.value = 0.004; comp.release.value = 0.15;
    const master = gain(0.7);

    chain(sum, dryHP, tractLP, crackle, am);
    am.connect(chorusDry).connect(comp);
    am.connect(delay).connect(chorusWet).connect(comp);
    chain(comp, master, ctx.destination);

    n = { glottalHP, glottal, formants, humidGain, bubbleGain, bubbles, dryHP, tractLP,
          crackle, crackleDepth, am, amDepth, chorusWet, master, comp };
    applyWetness(0);
  }

  /** Push the current wetness into every parameter, smoothly (τ seconds). */
  function applyWetness(tau = 0.08) {
    if (!n) return;
    const t = ctx.currentTime;
    const { dry, humid, gargle } = wetMix(wet);
    const set = (p, v) => p.setTargetAtTime(v, t, tau);
    set(n.dryHP.frequency, 180 + 1700 * dry);
    set(n.tractLP.frequency, 7500 - 4200 * gargle);
    set(n.humidGain.gain, 0.9 * humid);
    set(n.bubbleGain.gain, 1.6 * gargle);
    set(n.crackleDepth.gain, 0.8 * dry);
    set(n.crackle.gain, 1 - 0.8 * dry);
    const depth = 0.95 * gargle;
    set(n.amDepth.gain, 0.5 * depth);
    set(n.am.gain, 1 - 0.5 * depth);
    set(n.chorusWet.gain, 0.45 * humid + 0.35 * gargle);
    // moisture lowers and widens the formants a touch
    n.formants[0].frequency.setTargetAtTime(500 - 120 * gargle, t, tau);
    n.formants[1].frequency.setTargetAtTime(1500 - 250 * gargle, t, tau);
  }

  /** A liquid click: a sine that drops an octave-and-a-half in ~40 ms. */
  function plip(at, loud = 1) {
    const o = ctx.createOscillator(); o.type = "sine";
    const f0 = 900 + Math.random() * 1500;
    o.frequency.setValueAtTime(f0, at);
    o.frequency.exponentialRampToValueAtTime(f0 * 0.28, at + 0.03 + Math.random() * 0.03);
    const g = gain(0);
    g.gain.setValueAtTime(0.0001, at);
    g.gain.exponentialRampToValueAtTime(0.14 * loud, at + 0.004);
    g.gain.exponentialRampToValueAtTime(0.0001, at + 0.07);
    o.connect(g).connect(n.comp);
    o.start(at); o.stop(at + 0.09);
  }

  // ---- public --------------------------------------------------------------

  return {
    get unlocked() { return unlocked; },

    /** Must be called from a user gesture. Safe to call repeatedly. */
    async unlock() {
      if (!ctx) build();
      if (ctx.state !== "running") { try { await ctx.resume(); } catch { /* stays locked */ } }
      unlocked = ctx.state === "running";
      return unlocked;
    },

    setWetness(w) {
      wet = clamp(w, 0, 1);
      applyWetness();
    },

    /**
     * One utterance of /h/ at the current wetness. Returns its duration in
     * seconds so the mouth can animate the same breath.
     */
    speak() {
      const { dry, humid, gargle } = wetMix(wet);
      const D = 0.55 + 0.4 * wet + Math.random() * 0.15 + 0.15 * humid;
      if (!n || !unlocked) return { duration: D };
      const t0 = ctx.currentTime + 0.005;
      const attack = 0.03 + 0.06 * (1 - dry);
      const peak = 0.85 - 0.15 * gargle;
      const g = n.glottal.gain;
      g.cancelScheduledValues(t0);
      g.setValueAtTime(Math.max(g.value, 0.0005), t0);
      g.exponentialRampToValueAtTime(peak, t0 + attack);
      g.setValueAtTime(peak, t0 + D * 0.45);
      g.exponentialRampToValueAtTime(0.0008, t0 + D);
      // the utterance narrows the glottis: brighter, harder turbulence
      n.glottalHP.frequency.cancelScheduledValues(t0);
      n.glottalHP.frequency.setValueAtTime(n.glottalHP.frequency.value, t0);
      n.glottalHP.frequency.linearRampToValueAtTime(900 + 500 * dry, t0 + attack);
      n.glottalHP.frequency.setTargetAtTime(300, t0 + D * 0.6, 0.2);
      // gargle: deepen the modulation for the duration, and bubbles rise
      if (gargle > 0) {
        n.amDepth.gain.setTargetAtTime(0.5 * gargle, t0, 0.02);
        n.bubbleGain.gain.setTargetAtTime(2.4 * gargle, t0, 0.03);
        n.bubbleGain.gain.setTargetAtTime(1.6 * gargle, t0 + D, 0.3);
        const clicks = Math.floor(D * 14 * gargle * (0.6 + Math.random() * 0.8));
        for (let i = 0; i < clicks; i++) plip(t0 + Math.random() * D, 0.7 + 0.3 * Math.random());
      }
      utteranceEnd = t0 + D;
      return { duration: D };
    },

    /**
     * The nearly-silent breath bed. Called every frame with airflow (-1..1,
     * positive = out) and aperture (0..1). Cheap: only touches params ~20×/s.
     */
    breathe(flow, aperture) {
      if (!n || !unlocked) return;
      const t = ctx.currentTime;
      if (t < utteranceEnd || t - lastBedUpdate < 0.05) return;
      lastBedUpdate = t;
      const { gargle } = wetMix(wet);
      const level = flow > 0
        ? 0.028 * flow * (0.7 + 0.5 * wet)
        : 0.012 * -flow;
      n.glottal.gain.setTargetAtTime(level, t, 0.06);
      n.glottalHP.frequency.setTargetAtTime(flow > 0 ? 140 + 900 * (1 - aperture) : 90, t, 0.1);
      // at high wetness the exhale occasionally bubbles even at rest
      if (flow > 0.5 && gargle > 0 && t > clickTimer && Math.random() < 0.02) {
        clickTimer = t + 0.25;
        plip(t, 0.35 * gargle);
      }
    },

    /** Gratuitous: a tiny squelch (wet) or ratchet (dry) while the knob turns. */
    knobTick(w, velocity) {
      if (!n || !unlocked) return;
      const t = ctx.currentTime;
      if (t - lastTick < 0.045 || Math.abs(velocity) < 0.02) return;
      lastTick = t;
      const { gargle, dry } = wetMix(w);
      const s = ctx.createBufferSource(); s.buffer = n._tickBuf ??= noiseBuffer(0.2);
      const bp = biquad("bandpass", 500 + 3200 * dry + Math.random() * 300, 6 + 8 * gargle);
      const g = gain(0);
      const a = clamp(Math.abs(velocity) * 3, 0.15, 1) * 0.06;
      g.gain.setValueAtTime(a, t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.025 + 0.05 * gargle);
      s.connect(bp).connect(g).connect(n.comp);
      s.start(t, Math.random() * 0.1); s.stop(t + 0.1);
      if (gargle > 0.3 && Math.random() < 0.3 * gargle) plip(t, 0.4);
    },

    /** Tab hidden: fade out; shown: fade back in. */
    setMuted(m) {
      if (!n) return;
      n.master.gain.setTargetAtTime(m ? 0 : 0.7, ctx.currentTime, 0.1);
    },
  };
}
