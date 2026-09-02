// breath.js — the clock everything else breathes to.
//
// One cycle: inhale → brief hold → exhale → brief rest. The clock is phase-
// continuous, so the period can change mid-cycle (the ghost nudges it) without
// a jump. It reports lung volume, airflow, and glottal aperture as smooth
// 0..1 signals, and tells you when a cycle completes so the counter and the
// city can react.

const SEG = {
  inhale: 0.40, // fraction of the cycle
  hold:   0.06,
  exhale: 0.46,
  rest:   0.08,
};

const smooth = (t) => t * t * (3 - 2 * t);          // smoothstep on 0..1
const clamp01 = (x) => Math.max(0, Math.min(1, x));

export function createBreath({ periodMs }) {
  let period = periodMs;      // ms per cycle
  let phase = 0.62;           // start mid-exhale: the page opens on a breath out
  let count = 0;

  function segment(p) {
    let a = 0;
    for (const [name, len] of Object.entries(SEG)) {
      if (p < a + len) return { name, t: (p - a) / len };
      a += len;
    }
    return { name: "rest", t: 1 };
  }

  return {
    get period() { return period; },
    set period(ms) { period = Math.max(1500, ms); },
    get count() { return count; },
    get phase() { return phase; },

    /** Advance by dt seconds. Returns the current breath state. */
    update(dt) {
      let completed = false;
      phase += (dt * 1000) / period;
      if (phase >= 1) {
        phase -= Math.floor(phase);
        count += 1;
        completed = true;
      }
      const { name, t } = segment(phase);

      // Lung volume 0..1 (1 = full).
      let volume, flow, aperture;
      switch (name) {
        case "inhale":
          volume = smooth(t);
          flow = -Math.sin(Math.PI * t);                       // negative = air in
          aperture = 0.62 + 0.38 * smooth(clamp01(t * 3));     // folds swing wide open
          break;
        case "hold":
          volume = 1;
          flow = 0;
          aperture = 1 - 0.45 * smooth(t);                     // begin to adduct
          break;
        case "exhale":
          volume = 1 - smooth(t);
          flow = Math.sin(Math.PI * t) ** 0.8;                 // positive = air out
          aperture = 0.55 - 0.22 * Math.sin(Math.PI * t);      // the /h/ aperture: partly adducted, turbulent
          break;
        default: // rest
          volume = 0;
          flow = 0;
          aperture = 0.33 + 0.29 * smooth(t);                  // relax open again
      }
      return { phase, segment: name, t, volume, flow, aperture, count, completed };
    },
  };
}
