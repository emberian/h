# h ghost

Dataset preparation and training support for a tiny Falcon-H1 model that will live at `h.fg-goose.online`.

The selected starting checkpoint is [`tiiuae/Falcon-H1-Tiny-90M-Base`](https://huggingface.co/tiiuae/Falcon-H1-Tiny-90M-Base). The primary experiment is full-weight causal-language-model continued pretraining, not instruction tuning and not LoRA. A LoRA-CPT run and a random-initialized H1 run can follow as controls.

**Status 2026-09-01 evening:** the exact `h1jax` port trains on Kaggle TPU v5e-8 at ~220K tokens/s (one
corpus pass in 28 minutes; `research/results/tpu-h1jax-gate.md`); a 4-epoch warmup-stable-decay trunk with
developmental checkpoints is running (`kaggle/TPU_LEDGER.md`, `OVERNIGHT-2026-09-01.md`). The review that led
there, including corrections to `CODEXOUT.md`, is `FABLETHOUGHT.md`. The exact-match provenance index over
corpus-v1 is `hghost-haunt` (`research/results/haunting-index.md`).

The 90M checkpoint remains the active baseline. The next accelerator gate compares it with the deployable
[`Falcon-H1-0.5B-Base`](https://huggingface.co/tiiuae/Falcon-H1-0.5B-Base) before assigning the remaining
TPU budget. The verified literature bundle, claims audit, and staged experiment plan are in
[`research/`](research/README.md). The integrated multi-week roadmap—including corpus quality, Kaggle quota,
ChapterX residency, continual learning, long context, and mechinterp—is in
[`FUTURETHOUGHT.md`](FUTURETHOUGHT.md).

## Current corpus census

The two read-only source roots are:

- `~/PARAHEPTARCH/interface.cathedral.bucket`
- `~/archive/rat-palace`

The September 1, 2026 census found:

| Measure | Result |
|---|---:|
| All source files | 19,245 |
| Source bytes | 314.14 GiB |
| PDFs | 7,168 |
| PDF bytes | 184.65 GiB |
| Sampled PDFs | 145 |
| Text-bearing samples | 111 |
| Existing-text token estimate | 267,473,546 H1 tokens |
| Indicative stratified range | 120,441,144–478,466,053 tokens |
| Projected OCR candidates | about 2,277 PDFs |

The completed first extraction pass supersedes that sample estimate: it produced
**405,318,669 exact Falcon-H1 tokens in 5,212 ready documents before curation or
deduplication**. Another 2,026 PDFs remain in the OCR queue. OCR candidates
contribute no training tokens until quality review accepts them.

See the generated [census report](artifacts/census/report.md) after running the census locally.

## Preparation stages

The stages intentionally retain provenance and intermediate results:

1. `hghost-census` inventories everything and samples each source × PDF-size stratum.
2. `hghost-extract` prefers Internet Archive `*_djvu.txt` sidecars, otherwise uses Poppler, and writes one resumable compressed record per document.
3. PDFs without a useful text layer receive `needs_ocr` status.
4. `hghost-paddle-ocr` uses the complete PaddleOCR-VL 1.6 layout + recognition pipeline through a persistent MLX server on Apple Silicon. It stores compact page/block provenance and marks volume-valid results `ocr_unreviewed`.
5. `hghost-audit` ranks suspicious existing and OCR text without mutating records. It also emits a value-free, high-confidence exclusion manifest for credential material and severely corrupt text layers; `hghost-review-ocr` applies explicit OCR accept/reject/retry decisions.
6. `hghost-build` applies that explicit exclusion manifest, exact- and near-deduplicates normalized documents, assigns a deterministic document-level validation split, and emits compressed JSONL shards.
7. `hghost-tokenize` writes deterministic little-endian uint16 Falcon token streams with an EOS boundary after every document.

Neither extraction nor OCR edits the source trees.

## Setup

macOS prerequisites:

```sh
brew install poppler
uv sync --extra dev --python 3.13
```

Run the statistically stratified census:

```sh
.venv/bin/hghost-census \
  --root cathedral="$HOME/PARAHEPTARCH/interface.cathedral.bucket" \
  --root rat_palace="$HOME/archive/rat-palace" \
  --output artifacts/census \
  --samples-per-stratum 20 \
  --workers 6
```

Extract all available text:

```sh
.venv/bin/hghost-extract \
  --root cathedral="$HOME/PARAHEPTARCH/interface.cathedral.bucket" \
  --root rat_palace="$HOME/archive/rat-palace" \
  --output artifacts/extracted \
  --workers 8
```

Set up PaddleOCR in an isolated Python 3.12 environment:

```sh
uv venv .venv-paddle --python 3.12
uv pip install --python .venv-paddle/bin/python \
  paddlepaddle==3.2.1 \
  --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
uv pip install --python .venv-paddle/bin/python \
  'paddleocr[doc-parser]>=3.6,<4' 'mlx-vlm>=0.3.11'
uv pip install --python .venv-paddle/bin/python --no-deps -e .
```

Start the persistent MLX model server:

```sh
.venv-paddle/bin/python -m mlx_vlm.server \
  --host 127.0.0.1 \
  --port 8111 \
  --model PaddlePaddle/PaddleOCR-VL-1.6 \
  --max-num-seqs 4 \
  --max-tokens 8192
```

In another shell, process a bounded OCR tranche. The default page bounds avoid
one-page flyers and enormous scans; this example prioritizes substantial but
bounded 8–40-page documents. The worker resumes at document boundaries and
never edits the source trees:

```sh
.venv-paddle/bin/hghost-paddle-ocr \
  --root cathedral="$HOME/PARAHEPTARCH/interface.cathedral.bucket" \
  --root rat_palace="$HOME/archive/rat-palace" \
  --records artifacts/extracted/records \
  --raw-output artifacts/paddle-ocr/raw \
  --server-url http://127.0.0.1:8111/ \
  --region-concurrency 8 \
  --min-pages 8 \
  --max-pages 40 \
  --limit 25
```

Paddle output is not admitted to training merely because it has enough characters. Old Fraktur and damaged scans can still produce plausible-looking substitutions or repetition, so OCR records remain quarantined until review.

Audit all currently ready text without changing it:

```sh
.venv/bin/hghost-audit \
  --records artifacts/extracted/records \
  --output artifacts/quality
```

Create and apply a review sheet:

```sh
.venv/bin/hghost-review-ocr \
  --records artifacts/extracted/records \
  --sheet artifacts/ocr-review.csv

# Fill the decision column with accept, reject, or retry, then:
.venv/bin/hghost-review-ocr \
  --records artifacts/extracted/records \
  --apply artifacts/ocr-review.csv
```

After review, build shards:

```sh
.venv/bin/hghost-build \
  --records artifacts/extracted/records \
  --output artifacts/dataset \
  --exclude-file artifacts/quality/recommended_exclusions.jsonl \
  --validation-fraction 0.005 \
  --tokens-per-shard 20000000

.venv/bin/hghost-tokenize \
  --dataset artifacts/dataset \
  --output artifacts/tokenized
```

The exclusion file contains document IDs, paths, reasons, and token counts—not
the credential values that triggered the audit. Build records every applied
exclusion in `exclusions_applied.jsonl`.

The measured multi-machine training assessment, Kaggle TPU v5e-8 gate, and
backend probes are documented in
[`distributed_training/README.md`](distributed_training/README.md). WAN DDP
across the home machines is not useful; the gate chooses between TPU v5e-8 and
native MLX as the homogeneous primary trainer.

## Record contract

Each extraction record is a deterministic `json.gz` object containing:

- stable document ID, source root, and relative source path;
- extraction method, status, page/character/word/token counts;
- tokenizer identity and basic quality metrics;
- normalized-content SHA-256 for exact deduplication;
- normalized text only when the current stage considers it usable.

The final shards preserve one JSON object per document. Training concatenates documents with Falcon-H1's EOS token and packs the token stream into fixed-length examples; document-level validation assignment prevents the same exact text from crossing the split.

## Known work before training

- Run the real-token Kaggle TPU v5e-8 gate before selecting TPU or MLX as the
  primary trainer.
- Add language/perplexity scoring to the existing structural OCR review gate.
- Inspect repeated page headers/footers and conservative dehyphenation on a sample.
- Review and tune the conservative near-duplicate threshold on the completed corpus.
- Decide whether any standalone non-hOCR HTML is meaningful enough to admit without web boilerplate.
- Record copyright/licensing decisions for any publicly redistributed derivative weights.
- Round-trip an MLX ↔ Hugging Face checkpoint conversion before cross-backend
  evaluation.

## Tests

```sh
.venv/bin/pytest -q
```

## License

The original code, documentation, and metadata in this repository are
dedicated to the public domain under [CC0 1.0 Universal](LICENSE).
Third-party models, source documents, and bundled notices retain their own
licenses and rights; CC0 does not override those terms.
