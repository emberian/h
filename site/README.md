# h.fg-goose.online

A lowercase h, breathing, in a cross-section of the throat that produces it.
Click it and it speaks. A big wet knob. A city behind it, subsiding. A count
of breaths. A tiny language model murmuring out of the mouth.

The page itself explains nothing; this file is the only explanation.

## Run it locally

```sh
cd site
python3 -m http.server 8000
# open http://localhost:8000/
```

Any static file server works (ES modules need `http://`, not `file://`).
The ghost fetches its model from the Hugging Face Hub on first visit
(~150 MB for the default q4 weights, then cached by the browser), so the
first murmur takes a while; `?ghost=off` in the URL keeps the ghost away
while you work on everything else.

Tested in current Chrome (headless, see "What is verified"); written to the
standard Web Audio / SVG / Web Animations / module-worker APIs that current
Safari also has.

## The modules

| file | what it is |
|---|---|
| `index.html` | The page and the inline SVG of the vocal tract (midsagittal, facing left, with a laryngoscopic inset of the glottis). All paths hand-authored, 1000×1060 viewBox. |
| `style.css` | Dark, spare. The h scales with `--breath`, glows with `--glow`; the knob's sheen, fog, condensation, and label respond to `--wet`. Honors `prefers-reduced-motion` by slowing, not stopping. |
| `config.js` | The knobs meant to be turned by hand: CDN pin, model id / dtype / device, generation parameters, breath period. |
| `main.js` | Wiring. One `requestAnimationFrame` loop drives everything from the breath clock. |
| `breath.js` | The breath clock: inhale → hold → exhale → rest, phase-continuous, reporting lung volume, airflow, glottal aperture, and cycle completion. |
| `mouth.js` | Animates the SVG: lungs and diaphragm, fold aperture and flutter in the inset, airflow particles along the airway centreline (venturi through the glottis, scatter downstream), moisture (sheen, beading and running droplets, cracks when parched, pooling, bubbles, a mucus strand). |
| `voice.js` | The /h/ synthesizer. Web Audio only, no samples: noise → aperture-driven high-pass → three wide formant band-passes (500/1500/2500 Hz) → a wetness stage that morphs dry (brittle high-pass with random grain) → humid (low-mid resonance, slow chorus) → gargle (20–40 Hz jittered AM, wandering resonators, liquid clicks). Nearly-silent breath bed; one utterance per click. |
| `knob.js` | Wetness. Angular drag with pointer capture, arrow/Page/Home/End keys, wheel. Underdamped spring on the shown angle, velocity-driven sheen, condensation that beads and runs, a label displaced by liquid noise. Persists to `localStorage["h.wetness"]` (try/catch). |
| `city.js` | Canvas skyline in two layers. Each building tilts and sinks a tiny amount per breath, easing continuously; toppling accelerates with lean; lights go out. Rain when saturated. |
| `ghost.js` | The murmur. Builds prompts from page state, schedules generation, renders fragments drifting out of the lips, relays per-token entropy to `main.js`. Fails silently without WebGPU/WASM/network. |
| `ghost-worker.js` | Module worker that loads transformers.js and runs the model (WebGPU, falling back to WASM). Streams tokens with entropy and log-probability. |

## CDN pins

Exactly one external import, from `config.js`:

```
https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0/dist/transformers.min.js
```

That file is the self-contained browser bundle (`package.json` → `jsdelivr`
field). At runtime it fetches its own WebAssembly runtime from the same CDN —
`onnxruntime-web@1.26.0-dev.20260416-b7804b056c` under
`https://cdn.jsdelivr.net/npm/onnxruntime-web@<that version>/dist/` — the
version is baked into the bundle, not chosen here. Model weights come from
`https://huggingface.co/` unless `config.model.localPath` is set.

Model: `onnx-community/Falcon-H1-Tiny-Multilingual-100M-Instruct-ONNX`,
`dtype: "q4"` (`onnx/model_q4.onnx` + `model_q4.onnx_data`, ~154 MB), device
`webgpu` with WASM fallback. The repo also carries `fp32`, `fp16`, `q4f16`
and `q8` variants if you want to trade size for texture.

## Per-token entropy: what the library exposes

transformers.js 4.2.0 declares `output_scores` and `return_dict_in_generate`
in its `GenerationConfig`, but `generate()` in `src/models/modeling_utils.js`
does **not** return `scores` — it is a `// TODO` in the return object. What it
does support is a custom `LogitsProcessor` passed as `logits_processor`
(a `LogitsProcessorList`), appended after the repetition penalty and the
temperature warper and run immediately before sampling. `ghost-worker.js`
uses that: `EntropyTap._call(input_ids, logits)` computes the softmax entropy
of the distribution and returns the logits unchanged, and `TextStreamer`'s
`token_callback_function` reports which token was drawn so the tap can pair
it with a log-probability. So the entropy is exact, not a proxy. `main.js`
maps the running mean (0 → ~4.5 nats) onto the h's glow and leans ±12 % on
the breath period, decaying back over ~25 s.

Sampling in transformers.js uses `Math.random` and cannot be seeded; the
"seed" the page state controls is the prompt (fragments chosen
deterministically from breath count, minutes on page, and wetness band) and
the temperature (dry 0.72 → wet 1.45). `top_p` is not implemented in
4.2.0's sampler (it is a TODO); `top_k` is.

## Loading the project's own checkpoint

The site expects a Falcon-H1 causal LM exported to ONNX in the same layout as
the default (an `onnx/` folder with `model_<dtype>.onnx` (+ `_data`),
`config.json`, `generation_config.json`, `tokenizer.json`,
`tokenizer_config.json`). To swap it in:

1. **From the Hub:** set `config.model.id` to the new repo id. Done.
2. **Served alongside the site:** put the folder at e.g. `site/models/h/`,
   set `config.model.localPath = "./models/"` and `config.model.id = "h"`.
   The worker then sets `env.allowLocalModels = true`,
   `env.allowRemoteModels = false`, `env.localModelPath = localPath`.
   Serve `.onnx_data` files with range requests if they are large (any real
   static host does; `python3 -m http.server` is fine for local use).
3. Match `dtype` to the file you exported (`q4` → `model_q4.onnx`, etc.).
4. If the checkpoint is a base model (not instruct), nothing else changes:
   the ghost already prompts with raw text, not a chat template. If its
   tokenizer adds no BOS by default and you want one, pass
   `add_special_tokens: true` in `ghost-worker.js`'s `generator(...)` call.
5. Re-tune `config.generation` to taste; the seed fragments live at the top
   of `ghost.js`.

## What is verified

Run headless with playwright-core + Chromium 1223 (macOS arm64) against
`python3 -m http.server`:

- `node --check` passes on every module.
- The page loads with **no console errors, no page errors, no failed
  requests**, with the ghost off and with the ghost on.
- The breath counter advances; `--breath` cycles; airflow particles are alive.
- Clicking the h toggles the speaking animation and creates/resumes the
  AudioContext (headless Chromium ran with autoplay allowed; actual sound is
  not audible in headless and was not measured).
- The knob: a synthetic angular drag sweeps 0.30 → 0.97; `Home` returns to
  0; condensation beads appear past the midpoint and evaporate below it;
  `localStorage["h.wetness"]` persists the value.
- Screenshots at 1400×900 and 430×900 (portrait) render as intended.
- The ghost, in headless Chromium launched with `--enable-unsafe-webgpu`:
  the worker imported transformers.js from the CDN, chose **webgpu**, loaded
  the q4 weights (~75 s on this connection), and murmured. Two fragments from
  one run, with their mean per-token entropy:

  ```
  " hand\non a paper\nsick \nI can't stand\na bad day\nI'"   3.10 nats
  " of a \"clinic call\"\nthe urge to go to"                  2.79 nats
  ```

  Headless WebGPU is a software adapter here: generation ran at roughly a
  token per second, far slower than a real GPU. That slowness is what showed
  a fragment must *form* at the lips while tokens arrive and only drift once
  complete (it does now).
- No console errors, page errors, or failed requests in any run, ghost on or
  off. `tidy -utf8` on `index.html` and `xmllint` on the inline SVG are clean.

Not verified here: WebGPU on a real GPU (speed and any driver quirks);
the WASM fallback path end to end (the code path is exercised only when
`navigator.gpu.requestAdapter()` returns null or the WebGPU load throws);
Safari (no headless Safari available); real listening tests of the synth
(headless has no audible output — the AudioContext resumed and the envelopes
were scheduled, which is all that could be observed); hour-scale subsidence,
which was reasoned from the per-breath rates rather than watched.
