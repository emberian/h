# h explorer (v1)

A local causal workbench for reading the small models that live in the library. Not a chat UI: a loom over
`/v1/completions` with every token shaded by its logprob, an exact-match provenance view over the training
corpus, a replay of the room proxy's observatory ledger, a side-by-side comparison of two checkpoints, a
counterfactual room editor with fixed-reply scoring, a branch debugger for the persistent-state room server on
hbox, a population grid over every checkpoint, and a failure-label ledger that turns what you see into training
records. Press `?` in the page for the keys.

```sh
python3 explorer/serve.py --port 8130      # stdlib only; no venv needed for the server itself
open http://127.0.0.1:8130
```

Options: `--server NAME@URL` (repeatable; default `http://127.0.0.1:8124` and `:8125`, names resolved from the
symlinks in `artifacts/serving/`), `--tokenizer`, `--haunt-index`, `--observatory`, `--verbose`.

## What it talks to

- **Model servers**: `mlx_lm.server` instances speaking the OpenAI completions API. `/api/servers` probes each
  URL's `/v1/models`, which reports the served checkpoint *path*; the request `model` name mlx-lm actually
  accepts is the `--model` argument it was started with, so the name is recovered by matching that path against
  `artifacts/serving/<name> -> <checkpoint>`. A server whose name cannot be recovered shows as `(name unknown)`
  and is disabled; pass `--server name@url` to name it. Right now `:8124` serves `h-05b-room-e2v3` and `:8125`
  serves `h-05b-room-e3` (the checkpoint dirs are listed in `/api/servers` under `checkpoints`).

  To serve another checkpoint on `:8125` (never touch `:8124`, `:8126`, or the tmux sessions `hghost-serve`,
  `hghost-proxy`, `hghost-chapterx`):

  ```sh
  ln -sfn /Users/ember/dev/h/artifacts/checkpoints/tpu/<kernel>/<run>/tokens-<n> artifacts/serving/<name>
  tmux new-session -d -s hghost-serve05b -c artifacts/serving \
    "$HOME/.cache/h1-distributed/venv/bin/python -m mlx_lm.server --model <name> --host 127.0.0.1 --port 8125"
  ```

  mlx-lm ignores `n`, so "expand N" is N sequential requests, streamed back one at a time. `logprobs` is sent as
  a JSON boolean (an integer crashes the request). The returned logprob list covers the sampled tokens exactly,
  including the leading-space token and the `\n\n` stop token that mlx strips from `text`; node text in the
  explorer is the join of the decoded tokens, so shading always aligns and a child's prompt continues the raw
  document.
- **Tokens**: ids are decoded by a pure-Python byte-level BPE decoder read from
  `kaggle/base_model_dataset_public/tokenizer.json` (verified identical to `tokenizers` on the live outputs).
  Re-tokenising text (only needed to shade observatory candidates, which store logprobs without ids) runs
  `explorer/tokenize_worker.py` under `.venv/bin/python`; without `tokenizers` those candidates show a bar strip.
- **Provenance**: `.venv/bin/hghost-haunt scan --index artifacts/haunting-index --tokenizer ... --decode`, one
  process per `/api/haunt` call with all uncached texts batched into it. Results are cached under
  `explorer/cache/haunt/<sha256(text)[:24]>.json`, so re-scanning a node is free.
- **Observatory**: `research/results/room-observatory/YYYY-MM-DD.jsonl` written by `chapterx/room_proxy.py`.

## Daily use

- **Keys** (loom): `← →` siblings, `↑ ↓` parent / first child, `Enter` expand the active node, `e` edit, `n` note,
  `l` label, `b` bookmark, `x` deactivate, `c` collapse, `h` haunt, `Delete` delete, `⌘Z`/`⇧⌘Z` undo/redo,
  `⌘S` save (also inside fields), `⌘⇧C` copy the active path as a transcript, `1…8` tabs, `Esc` cancel. Shortcuts
  are off while typing in a field.
- **Undo/redo** records a full snapshot (weave + collapsed set) before every mutation, mirroring the crate's
  action-queue wrapper at the granularity of one user action (an expand of N samples is one undo step).
- **Tidy**: on load, nodes below depth 2 that are not on the active path start collapsed; the tree panel's
  "tidy" button re-applies that; the active node scrolls into view.
- **Weaves**: name + save (server file under `explorer/weaves/`), picker with load and delete; the current weave
  also lives in `localStorage`. Per-node **notes** (`n`) and **labels** (`l`) are stored in the node contents
  (`note`, `labels`) and travel with the weave.
- **Node panel** (right column, under the reading): the reproducibility record of the active node: model,
  checkpoint path, server and backend, sampler (temperature, top_p, max_tokens, stop, repetition penalty), seed
  (none: mlx-lm has no seed), tokenizer hash, explorer git rev, proxy sha when the sample came through `:8126`
  (observatory nodes), note and labels.
- **Errors** surface as toasts and in the status line; with no live model server the expand buttons are disabled
  and a toast says which port to start.

## Panes

- **Loom** — prompt box edits the root node (the "frame" button inserts the bare room frame plus one turn).
  Every node shows its text with tokens shaded by logprob (hover for id / logprob / p), plus token count, mean
  logprob, and the entropy proxy (mean surprisal, nats; the header also shows ppl = exp of it). Per node:
  `+<model>` expands N continuations from that server (N, temperature, top_p, max_tokens, stop in the sampler
  panel), bookmark, activate / deactivate, edit, split (then click the token that starts the new child), merge
  into parent (only-children), haunt, delete. Clicking a node makes it the active tip; the right column shows
  the active path as one shaded reading. Weaves save to `explorer/weaves/<name>.json`; the current weave is
  also kept in `localStorage` so a reload does not lose it.
- **Provenance** — for the active node (or its whole path): longest exact match, coverage at 8/16/32 tokens,
  top documents (source, path, quoted tokens, offset) and the longest spans with their text. Matched token
  ranges are underlined in the node text when the scan's tokenisation has the same length as the sample's.
  "Scan all nodes" haunts the whole weave in one call and badges each node with `haunt <longest>/<tokens>`.
- **Observatory** — pick a day; the summary gives records, acceptance rate, mean candidates tried, mean
  seconds, mean chosen logprob, dropped echo turns. A record shows the raw prompt as blocks with the turns the
  proxy dropped struck through, the cleaned prompt, and every candidate with overlap score, accepted flag,
  logprob shading, and the chosen one outlined. "Open in loom" turns the record into a weave (prompt root,
  candidates as children, chosen bookmarked).
- **Compare** — one prompt, two servers, K samples each, streamed side by side with shading and per-side
  aggregates (mean logprob, surprisal, length, stop rate, seconds). "→ loom" files a sample under a root with
  that prompt in the current weave.
- **Counterfactual** — "from loom" (or "→ cf" on a node, or "→ counterfactual" on an observatory record) turns
  the active path into an editable list of room turns (frame blocks and `name: text` turns) and takes the active
  node's text as the fixed reply. Edit, delete, reorder (↑↓), or reassign a speaker (⇄) on the right, pick a
  scorer checkpoint, "score both": the reply's per-token logprob and rank under the true and the edited context,
  with Δ per token and the total. "re-run continuation" samples fresh continuations from the edited context with
  the loom sampler. Scoring runs `score_worker.py` in the JAX venv on CPU (float32, the evaluation pack's forward):
  the 91M leaf answers in ~0.3 s per item after a ~3 s compile per length bucket; the 0.5B takes seconds per item.
- **Room state** — the hbox persistent-cache server (`hbox_training/room_state_server.py`, reached through the
  ssh forward `hbox_training/run_room_state_server.sh forward`, `:8140`): rooms (create with the bare frame, open,
  delete), read an event into the committed state, fork N candidates (per-token logprobs, commit / silence), optional
  control arm (fresh re-render with the same seeds, first-token divergence), snapshots, and a per-turn plot of the
  mean per-layer SSM head norm with token count and state bytes. When the forward is down the pane says so and
  how to bring it up.
- **Population** — one prompt across the checkpoints you tick; each is served in turn on `:8125` (symlink under
  `artifacts/serving/` + restart of tmux `hghost-serve05b`; `:8124` is never touched), K samples per cell with
  shading, the judge's library-likeness (NLL under the 91M leaf minus NLL under the 91M base, per sample) and the
  haunt scan's longest match. "stop" ends the run after the current checkpoint.
- **Labels** — the ledger of failure labels (counts, recent records) and the blind pairwise sheets written by
  `hghost-roombank pairs` (items rebuilt from the key file's state ids and each model's `replies.jsonl`; the key
  itself is never sent to the page). Each pair takes the three questions (keep / want to answer / sounds like h) as
  A / B / tie / neither and records them; "label A/B" attaches a taxonomy label to one side.

## Failure label → training record

From any loom node (`l`), any observatory candidate ("label"), a pair side, or a room-state candidate, one action
records a label with an optional correction. Labels: `KEEP`, `echo`, `self-copy`, `false speak`, `missed
intervention`, `wrong addressee`, `missed callback`, `generic assistant`, `frame leak`, `OCR corruption`, `dead
strangeness`, `overquotation`, `proxy false positive`, `other`. Records append to
`research/results/room-labels/YYYY-MM-DD.jsonl`:

```json
{"time": "...", "who": "ember", "label": "echo", "correction": "what h should have said" | null, "note": null,
 "source": {"kind": "loom|observatory|pair|roomstate", ...},
 "context": "<rendered room text the candidate answered>", "candidate": "<the candidate text>",
 "checkpoint": "<path or null>", "model": "...", "server": "...", "sampler": {...}, "proxy_sha": "...", "explorer": "<git rev>"}
```


## Endpoints

| method | path | body / query | returns |
|---|---|---|---|
| GET | `/api/servers` | | `{servers:[{url,up,model,path}], serving:{name:path}, checkpoints:[dir]}` |
| POST | `/api/generate` | `{server, model, prompt, n, temperature, top_p, max_tokens, stop, repetition_penalty?}` | NDJSON: `start`, then one `sample` per completion (`text, tokens:[{id,text,logprob}], finish_reason, mean_logprob, seconds, sampler`), then `done` (or `error`) |
| POST | `/api/haunt` | `{items:[{id,text}], thresholds?}` | `{results:{id: record}, summary, scanned, cached, seconds}` — record fields as written by `hghost-haunt scan` (`tokens, longest_match, coverage, top_documents, longest_spans`) |
| GET | `/api/observatory` | | `{dates:[{date,records,bytes}]}` |
| GET | `/api/observatory?date=YYYY-MM-DD` | | `{summary, records}`; each record gains `blocks` (raw prompt blocks with `dropped`) and each candidate `tokens_text` (aligned token strings, or null) |
| GET | `/api/weaves` | | `{weaves:[{name,nodes,roots,modified}]}` |
| GET | `/api/weaves?name=` | | the weave JSON |
| POST | `/api/weaves` | `{name, weave}` | validates (see below) and writes `explorer/weaves/<name>.json` |
| POST | `/api/weaves/delete` | `{name}` | deletes a saved weave |
| GET | `/api/version` | | `{explorer: <git rev>, tokenizer_sha, proxy_sha, python}` (also under `version` in `/api/servers`, with the `:8125` switching state under `serve`) |
| GET | `/api/scorers` | | scorable checkpoint dirs (the two bases + every TPU checkpoint), the judge pair, worker status |
| POST | `/api/score` | `{checkpoint, items:[{id, context?, text}], ranks?}` | NDJSON: `start`, one `result` per item (`{n, nll_sum, nll_mean, context_tokens, bucket, tokens:[{id,text,logprob,rank}]}`, cached per checkpoint+context+text), `done` |
| GET / POST | `/api/labels` | POST body: the record above (`label`, `candidate` required) | GET: `{labels, counts, total, recent}` |
| GET | `/api/roombank[?sheet=]` | | pairwise sheets / one sheet's blind items |
| GET | `/api/roomstate/status` | | `{up, url, health}` for the hbox forward |
| GET / POST / DELETE | `/api/roomstate/<path>` | forwarded body | proxied to the room-state server (`/rooms`, `/rooms/<id>/events|candidates|commit|silence|snapshot|rollback|state|transcript`) |
| POST | `/api/serve` | `{checkpoint, name?}` | serves that checkpoint on `:8125` (symlink + tmux restart), blocks until it answers |

## Weave schema

The file is the serde shape of `universal_weave::dependent::DependentWeave<K, T, M>` from
`/Users/ember/src/universal-weave` (a tree where each node's contents depend on its ancestors), with concrete
`K`, `T`, `M`:

```json
{
  "nodes": {
    "<uuid>": {
      "id": "<uuid>",
      "from": "<uuid>" | null,
      "to": ["<uuid>", ...],
      "active": false,
      "bookmarked": false,
      "contents": { ... }
    }
  },
  "roots": ["<uuid>", ...],
  "active": "<uuid>" | null,
  "bookmarked": ["<uuid>", ...],
  "metadata": { "format": "h-explorer-weave", "schema": 1, "name": "...", "created": "...", "modified": "...", "ui": { "collapsed": [] } }
}
```

| Rust | here |
|---|---|
| `K: Hash + Copy + Eq + Ord` | UUID v4 strings (`uuid::Uuid` deserialises them; globally unique, so DAG-capable — the `IndependentNode` shape differs only in `from` being a list) |
| `DependentNode { id, from: Option<K>, to: IndexSet<K>, active, bookmarked, contents }` | the node objects above; `to` is ordered (insertion order = sibling order) |
| `DependentWeave { nodes: HashMap, roots: IndexSet, active: Option<K>, bookmarked: IndexSet, metadata: M }` | the top-level object (`scratchpad` is `serde(skip)`) |
| `T` (contents, `DiscreteContents`) | `{kind: "prompt"\|"sample"\|"edit"\|"merged", text, tokens: [{id, text, logprob}] \| null, model?, server?, sampler?, finish_reason?, seconds?, created?, edited?, observatory?, repro?, note?, labels?}`; when `tokens` is present `text == join(tokens.text)`; `repro` = `{server, model, checkpoint, backend, tokenizer_sha, explorer, stop, logprobs, seed, proxy_sha?}`; `labels` = `[{label, correction, note, time}]` |
| `M` (metadata) | the free-form `metadata` object |

Semantics mirrored from the crate (`src/dependent/mod.rs`):

- `active` on the weave is the tip of the active path; exactly that node carries `active: true`. `set_active(id,
  false)` on the tip moves the tip to its parent (the UI's "deactivate"); `set_active(id, true)` moves it.
- `insert` requires `to` empty and an existing parent (or none → root); `remove` drops the subtree, fixes the
  parent's `to`, bookmarks, and moves the tip to the parent if it was inside.
- `split(id, at, new_id)`: the left half keeps `id`, parent, active and bookmark flags; the right half gets
  `new_id`, the old children, and is inactive and unbookmarked. `at` is a token index when `tokens` exist,
  otherwise a character (code point) index; `0 < at < len` or the split fails (`DiscreteContentResult::One`).
- `merge_with_parent(id)`: only when the parent has exactly one child; text concatenates, tokens concatenate
  when both sides have them (else `null`), children re-parent, the tip and bookmark carry to the parent.
- `POST /api/weaves` re-validates the way `DependentWeave::validate` does (link symmetry, roots = parentless
  nodes, single active tip, bookmark consistency, acyclic and fully reachable) and rejects anything else.

## Verified 2026-09-02 (v1)

Headless (playwright driving the installed Chrome) through: keys `2…8,1`, frame + `Enter` expand on `:8124`,
arrow navigation, `b`, `n` note + undo + redo, `l` label to the ledger (chip on the node), `⌘⇧C`, node panel
with checkpoint, `c` collapse, counterfactual from a node with a reassigned speaker and a fixed reply scored on
the 91M trunk checkpoint (17 delta rows), observatory record with per-candidate label buttons, room state on
the live hbox forward (create, event, 2 candidates, commit, state plot), population with one checkpoint (served
on `:8125`, judge Δ per sample), labels tab with a 106-pair sheet, `⌘S` save from inside the name field, load,
`Delete` + undo; no console errors. The v0 checks below still hold.

## Verified 2026-09-02 (v0)

Against the live `:8124` (`h-05b-room-e2v3`) and `:8125` (`h-05b-room-e3`) servers: streaming `/api/generate`
(token join == text on every sample), `/api/haunt` (2 texts in 0.3 s, second call served from cache),
`/api/observatory?date=2026-09-02` (the day's candidate aligned 38/38 with its logprobs), weave save/load with
the four invalid shapes rejected, and a headless run (playwright driving the installed Chrome:
`NODE_PATH=/Users/ember/dev/booty-hunt/node_modules node <script>` with `chromium.launch({channel: 'chrome'})`)
through all four panes: expand, split, merge, bookmark, deactivate, save, provenance scan, observatory replay,
and a two-server compare, with no console errors.

## Limitations (v1)

- Tree only (`from` is a single parent); the schema is DAG-ready by id but no UI for multiple parents.
- Undo is snapshot-based (whole weave per step, capped at 200 steps), not a replayable action log.
- The scorer is CPU float32 through a single worker: fine for the 91M, seconds per item for the 0.5B; population
  judging uses the 91M pair only.
- Population switching restarts the `:8125` server, which anyone else using `:8125` (the room-reading scripts)
  will notice; the resident on `:8124` is never touched.
- Room-state candidates are labelled with a synthetic context (the room id), not the rendered transcript.
- Sampling is sequential per request (mlx-lm ignores `n`), and the model servers are shared with the Discord
  bot's proxy, so an expand of N=8 at 40 tokens takes roughly N × 0.5 s on the 0.5B checkpoints.
- Provenance highlighting inside a node needs the scan's tokenisation to be the same length as the sample's
  (it re-encodes the text); otherwise only the span list is shown.
- The proxy on `:8126` is deliberately not a default server: it strips logprobs and every request through it
  lands in the observatory ledger.
