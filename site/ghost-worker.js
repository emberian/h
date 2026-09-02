// ghost-worker.js — where the ghost actually runs.
//
// A module Web Worker so that generation (especially on the WASM fallback)
// never stalls the breathing on the main thread. It loads transformers.js
// from the CDN pinned in config.js, prefers WebGPU, falls back to WASM, and
// answers `generate` requests with a stream of tokens. For each token it also
// reports the entropy of the (temperature-warped) next-token distribution and
// the log-probability of the token that was drawn.
//
// How the entropy is obtained: transformers.js 4.2.0 declares
// `output_scores` / `return_dict_in_generate` in its GenerationConfig, but
// `generate()` does not return `scores` (it is a TODO in modeling_utils.js).
// What it does support is a custom `LogitsProcessor` appended to the processor
// list — run after repetition penalty and the temperature warper, right before
// sampling. Our EntropyTap is such a processor: it reads the logits, computes
// softmax entropy, and returns them unchanged. `TextStreamer`'s
// `token_callback_function` then tells us which token was drawn, in order.

import { config } from "./config.js";

let T = null;          // the transformers.js module
let generator = null;  // text-generation pipeline
let device = null;
let busy = false;

const post = (m) => self.postMessage(m);

async function pickDevice() {
  if (config.model.device !== "webgpu") return config.model.device;
  try {
    const adapter = await self.navigator?.gpu?.requestAdapter?.();
    return adapter ? "webgpu" : "wasm";
  } catch { return "wasm"; }
}

async function load() {
  try {
    T = await import(config.transformersUrl);
  } catch (e) {
    post({ type: "unavailable", reason: "could not import transformers.js: " + (e?.message || e) });
    return;
  }
  if (config.model.localPath) {
    T.env.allowLocalModels = true;
    T.env.allowRemoteModels = false;
    T.env.localModelPath = config.model.localPath;
  }

  const make = (dev, dtype) => T.pipeline("text-generation", config.model.id, {
    dtype, device: dev,
    progress_callback: (p) => {
      if (p.status === "progress") post({ type: "progress", file: p.file, progress: p.progress });
    },
  });

  device = await pickDevice();
  try {
    generator = await make(device, device === "wasm" ? config.model.wasmDtype : config.model.dtype);
  } catch (e) {
    if (device !== "wasm") {
      post({ type: "note", text: `webgpu load failed (${e?.message || e}); trying wasm` });
      try { device = "wasm"; generator = await make("wasm", config.model.wasmDtype); }
      catch (e2) { post({ type: "unavailable", reason: "model load failed: " + (e2?.message || e2) }); return; }
    } else {
      post({ type: "unavailable", reason: "model load failed: " + (e?.message || e) });
      return;
    }
  }
  try { await generator("h", { max_new_tokens: 1, do_sample: false }); } catch { /* warm-up only */ }
  post({ type: "ready", device });
}

/** A LogitsProcessor that measures instead of modifying. */
function makeEntropyTap() {
  return new (class EntropyTap extends T.LogitsProcessor {
    constructor() { super(); this.pending = []; }
    _call(input_ids, logits) {
      // logits: Tensor [batch=1, vocab], float32, already temperature-scaled.
      const d = logits.data, n = logits.dims.at(-1);
      let max = -Infinity;
      for (let i = 0; i < n; i++) if (d[i] > max) max = d[i];
      let sum = 0;
      for (let i = 0; i < n; i++) sum += Math.exp(d[i] - max);
      const logZ = Math.log(sum) + max;
      let H = 0, pmax = 0;
      for (let i = 0; i < n; i++) {
        const lp = d[i] - logZ, p = Math.exp(lp);
        if (p > 0) H -= p * lp;
        if (p > pmax) pmax = p;
      }
      this.pending.push({ entropy: H, pmax, logZ, logits: Float32Array.from(d.subarray(0, n)) });
      return logits;
    }
    /** Pair the next drawn token with the distribution it came from. */
    take(tokenId) {
      const s = this.pending.shift();
      if (!s) return { entropy: 0, pmax: 1, logprob: 0 };
      const id = Number(tokenId);
      const logprob = s.logits[id] - s.logZ;
      return { entropy: s.entropy, pmax: s.pmax, logprob };
    }
  })();
}

async function generate(req) {
  if (!generator || busy) { post({ type: "done", id: req.id, text: "", skipped: true }); return; }
  busy = true;
  try {
    const tap = makeEntropyTap();
    const processors = new T.LogitsProcessorList();
    processors.push(tap);
    const streamer = new T.TextStreamer(generator.tokenizer, {
      skip_prompt: true,
      skip_special_tokens: true,
      callback_function: (text) => post({ type: "text", id: req.id, text }),
      token_callback_function: (tokens) => post({ type: "token", id: req.id, ...tap.take(tokens[0]) }),
    });
    const out = await generator(req.prompt, {
      max_new_tokens: req.maxNewTokens,
      do_sample: true,
      temperature: req.temperature,
      top_k: req.topK,
      repetition_penalty: req.repetitionPenalty,
      return_full_text: false,
      streamer,
      logits_processor: processors,
    });
    post({ type: "done", id: req.id, reason: req.reason, text: out?.[0]?.generated_text ?? "" });
  } catch (e) {
    post({ type: "error", id: req.id, reason: e?.message || String(e) });
  } finally {
    busy = false;
  }
}

self.onmessage = (e) => {
  const m = e.data;
  if (m.type === "load") load();
  else if (m.type === "generate") generate(m);
};
