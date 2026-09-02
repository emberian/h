// config.js — the few things that are meant to be changed by hand.
//
// Everything else on the page derives from these. The ghost (ghost.js /
// ghost-worker.js) reads `model` and `generation`; main.js reads `breath`.

export const config = {
  // Exact CDN pin for transformers.js. This is the ONLY external dependency.
  // (At runtime the library fetches its own onnxruntime-web WASM binaries from
  // the same CDN; see README "CDN pins".)
  transformersUrl:
    "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0/dist/transformers.min.js",

  model: {
    // A Hugging Face Hub id (default) or, if `localPath` is set, a folder name
    // under that path. The project's own checkpoint — a Falcon-H1 causal LM
    // exported to ONNX in the same layout — drops in here.
    id: "emberian/h-leaf-e1-decay10-onnx",

    // Weight file variant: "q8" → onnx/model_quantized.onnx (+ _data). Others in
    // the same layout: "fp32" (model.onnx), "q4" (model_q4), "fp16", "q4f16".
    // The project's own 90M checkpoints fall apart at 4 bits (see
    // site/export/README.md); their 8-bit export is near-lossless and ~140 MB.
    dtype: "q8",
    // Variant to use if we end up on WASM (no WebGPU).
    wasmDtype: "q8",

    // "webgpu" with automatic fallback to "wasm"; set "wasm" to force CPU.
    device: "webgpu",

    // Set to e.g. "./models/" to serve the checkpoint from this site instead of
    // the Hub (then `id` is the folder name, e.g. "h"). null = use the Hub.
    localPath: null,
  },

  generation: {
    // Fragment length, sampled uniformly per utterance (tokens).
    minNewTokens: 8,
    maxNewTokens: 24,
    // Temperature sweeps with wetness: dry is cool and terse, wet is feverish.
    temperature: { dry: 0.72, wet: 1.45 },
    repetitionPenalty: 1.3,
    topK: 50,
    // Idle murmur cadence (ms) — jittered uniformly in this range.
    idleInterval: { min: 11000, max: 24000 },
  },

  breath: {
    // One full breath cycle, in ms. Reduced-motion users get the slow one.
    periodMs: 5200,
    reducedPeriodMs: 9000,
  },
};
