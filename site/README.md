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
The ghost loads the project's own checkpoint from `models/h1-tiny-90m-base/`
(125 MB of 8-bit weights, served with the site, then cached by the browser),
so the first murmur takes a while; `?ghost=off` in the URL keeps the ghost
away while you work on everything else. `models/` is gitignored: export it
with `export/export_onnx.py` (see "Loading the project's own checkpoint") or
point `config.js` back at the Hub model.

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
`config.model.localPath` (default `./models/`, i.e. this site) or, if that is
`null`, from `https://huggingface.co/`.

Model: `h1-tiny-90m-base` — the project's export of the exact
`tiiuae/Falcon-H1-Tiny-90M-Base` (`kaggle/base_model_dataset_public`),
`dtype: "q8"` (`onnx/model_quantized.onnx` + `_data`, 125 MB: 8-bit
MatMulNBits and an 8-bit block-quantized embedding), device `webgpu` with
WASM fallback. The same directory holds `fp32` (`model.onnx`, 365 MB, exact)
and `q4` (`model_q4.onnx`, 70 MB, the Hub recipe — which turns this 90M
checkpoint to mush; the numbers are in `export/README.md`). The Hub
alternative is `onnx-community/Falcon-H1-Tiny-Multilingual-100M-Instruct-ONNX`
with `localPath: null`, `dtype: "q4"` (~154 MB).

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

The site expects a Falcon-H1 causal LM exported to ONNX in the layout
transformers.js reads (an `onnx/` folder with `model_<dtype>.onnx` + `_data`,
`config.json`, `generation_config.json`, `tokenizer.json`,
`tokenizer_config.json`). `export/export_onnx.py` produces exactly that from
any Hugging Face Falcon-H1 checkpoint directory and proves it against PyTorch
with onnxruntime before you use it — `export/README.md` has the pipeline,
pinned versions and the numbers for the base checkpoint:

```sh
uv venv --python 3.12 .venv-onnx
uv pip install --python .venv-onnx/bin/python -r site/export/requirements.txt
.venv-onnx/bin/python site/export/export_onnx.py <hf checkpoint dir> site/models/<name>
```

To swap a checkpoint in:

1. **Served alongside the site (the default):** the export goes to
   `site/models/<name>/`; set `config.model.id = "<name>"` and keep
   `config.model.localPath = "./models/"`. The worker then sets
   `env.allowLocalModels = true`, `env.allowRemoteModels = false`,
   `env.localModelPath = localPath`, and transformers.js fetches
   `./models/<name>/{config.json, tokenizer.json, tokenizer_config.json,
   generation_config.json, onnx/model_quantized.onnx, onnx/model_quantized.onnx_data}`
   relative to the worker. Serve `.onnx_data` files with range requests if
   they are large (any real static host does; `python3 -m http.server` is
   fine for local use). `site/models/` is gitignored — deploy it next to the
   site.
2. **From the Hub:** set `config.model.localPath = null` and
   `config.model.id` to the repo id. Done.
3. Match `dtype` / `wasmDtype` to the file: `q8` → `model_quantized.onnx`
   (what the exporter's 8-bit file is called; use it), `fp32` → `model.onnx`,
   `q4` → `model_q4.onnx`. Do not ship `q4` for these 90M checkpoints:
   round-to-nearest 4-bit costs 0.6 nats of KL against fp32 and the greedy
   text falls apart after three tokens; 8-bit is 0.0014 nats.
4. If the checkpoint is a base model (not instruct), nothing else changes:
   the ghost already prompts with raw text, not a chat template. If its
   tokenizer adds no BOS by default and you want one, pass
   `add_special_tokens: true` in `ghost-worker.js`'s `generator(...)` call.
5. Re-tune `config.generation` to taste; the seed fragments live at the top
   of `ghost.js`.

Both configurations are verified below; `config.js` is committed pointing at
the local export.

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
- The same harness (`export/check_site.mjs`, playwright-core 1.58 driving the
  cached Chromium 1223 with `--enable-unsafe-webgpu`, page served by
  `python3 -m http.server 8765`) with the **local** `h1-tiny-90m-base` q8
  export and `config.js` as committed: the worker chose **webgpu**, fetched
  the six model files from `./models/…`, and murmured
  `" winter 04, 2015\nGermany and Sweden are the first two"` with **no
  console errors, no page errors, no failed requests**; a second fragment
  (`it nevertheless goes deep, dark, thin,`) was forming at the lips when the
  run's 900 s cap hit — the box was at load average ~200 that evening. With
  the model files removed the harness reports the 404s and exits 1.
- No console errors, page errors, or failed requests in any run, ghost on or
  off. `tidy -utf8` on `index.html` and `xmllint` on the inline SVG are clean.

Not verified here: WebGPU on a real GPU (speed and any driver quirks);
the WASM fallback path end to end (the code path is exercised only when
`navigator.gpu.requestAdapter()` returns null or the WebGPU load throws —
note the plain 8-bit MatMulNBits CPU kernel is slow, ~1 s per token in
Python's onnxruntime on this machine; `export_onnx.py --q8-accuracy-level 4`
is the knob if WASM matters);
Safari (no headless Safari available); real listening tests of the synth
(headless has no audible output — the AudioContext resumed and the envelopes
were scheduled, which is all that could be observed); hour-scale subsidence,
which was reasoned from the per-breath rates rather than watched.
