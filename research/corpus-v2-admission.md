# Corpus-v2 admission: fidelity apart from value

Date: 2026-09-02. Code: `src/hghost/admission.py` (`hghost-admission`), tests
`tests/test_admission.py`. Outputs under `artifacts/corpus-v2/` (gitignored, regenerable: scores
in ~9 min, gold set in ~15 min). Nothing under `artifacts/{dataset,extracted,tokenized,...}` was
modified; corpus-v1 stays sealed beside this.

## 1. Why two axes

Corpus-v1 admitted a document with one gate: `chars >= max(200, 40 * pages)` and
`alpha_ratio >= 0.25` (`extract.py`). That gate conflates two different questions:

* **Fidelity** — does the text we hold say what the page image says? A failure here is an
  extraction or OCR failure: garbage characters, one letter per line, scrambled columns,
  invented words, page furniture (JSTOR stamps, running heads) interleaved with the prose.
  The fix is a better extraction of the *same* document (re-OCR, layout repair, stripping).
* **Value** — do we want this text in the library at all, faithful or not? A court docket, a
  credential dump, a 1 M-token FOIA release, a survival checklist can be extracted perfectly and
  still belong somewhere other than the main stream. The fix is a curatorial decision, not an
  engine.

The night-2026-09-02 result is the reason to separate them now: the third epoch memorized OCR
noise first (`"the e d i t i o n of the N ig h t M a s t e r s"`), the ghost learned single-letter
columns as a *style*, and 20 % of a genuinely held-out validation document was "covered" by
32-gram training matches that were all page furniture. Every one of those is a fidelity problem
in a high-value document. Treating them as "low quality, drop" would throw away the library to
cure the scanner.

## 2. What is actually recorded (ground truth)

| Source of text | Documents | Page breaks | Positions | Engine confidence |
|---|---:|---|---|---|
| `pdftotext` text layer (origin unknown: publisher, ABBYY, IA, Tesseract…) | 6,316 records / 4,1xx in v1 | `\f` per page | recoverable: `pdftotext -bbox-layout` (poppler 26.06, ≤ 0.1 s/page) | none |
| Internet Archive `_djvu.txt` sidecar | 564 | **none** (one page in the text) | in the IA hOCR, not fetched | none |
| IA `_hocr_searchtext.txt.gz` | 24 | none | as above | none |
| PaddleOCR-VL 1.6 (mlx) raw pages, `artifacts/paddle-ocr/raw` | 141 (101 `ocr_unreviewed`, 3,749 pages) | per page | block bbox + label + reading order | **none** — blocks carry `label, content, bbox, order, group_id` only |
| plain text / epub / docx | 242 | epub: `\f` per chapter | n/a | n/a |

So "engine confidence if recorded" is: not recorded anywhere. The closest thing is the
**text-layer origin** from PDF metadata (`pdfinfo` Producer/Creator, cached in
`artifacts/corpus-v2/pdfinfo.jsonl`, 4,744 PDFs): 2,756 name an OCR product (ABBYY, Paper Capture,
LuraDocument, OCRmyPDF/Tesseract…), 1,285 a born-digital producer (LaTeX, InDesign, Word, cairo…),
703 nothing. Born-digital layers have near-perfect character fidelity and only layout risk; OCR
layers of unknown vintage are where character noise lives. This is a prior, and the scores treat
it as one (it is a column, not a term in the score).

Source PDFs resolve (200/200 sampled) under `~/archive/rat-palace` and
`~/PARAHEPTARCH/interface.cathedral.bucket`, so page images are available for every PDF document
(`pdftoppm`, 0.1–7 s per page).

## 3. Fidelity signals available now

All computed from the record text alone (`text_signals`), so they apply uniformly to
pdftotext, IA sidecars and Paddle output. Ratios are over non-blank lines, whitespace tokens or
alphabetic words as noted. Each is mapped to a badness in [0, 1] by a linear ramp `(lo, hi)`
and combined by a **noisy-OR** with a per-signal weight: `p_corrupt = 1 - Π(1 - w·b)`,
`fidelity = 1 - p_corrupt`. Noisy-OR rather than a sum because one strong symptom is enough to
condemn an extraction; the ramps are set so clean prose sits at 0 on every term (§10 has the
corpus distributions the ramps were read from).

| Signal | Definition | Catches | lo | hi | w |
|---|---|---|---:|---:|---:|
| `hapax_ratio` | share of ≥4-letter words with corpus document-frequency 1 and not in the dictionary | garbage words (`jijicaiSflii`), language-agnostic | 0.06 | 0.30 | 0.9 |
| `unknown_ratio` | same with df ≤ 2 | as above, softer | 0.10 | 0.40 | 0.9 |
| `inner_caps_ratio` | words with a lowercase→uppercase switch inside (`rKopossi`), not all-caps | case-confused OCR | 0.006 | 0.05 | 0.8 |
| `mixed_token_ratio` | tokens with ≥3 alternating letter/digit/symbol runs (`Coo6wenue1`, `!li!li�.N`); hyphenated words exempt | Cyrillic-as-Latin, symbol soup | 0.02 | 0.12 | 0.8 |
| `single_char_line_ratio` | lines that are one character | one-letter-per-line spines, captions, vertical text | 0.03 | 0.20 | 0.6 |
| `spaced_letter_ratio` | letters in `e d i t i o n` runs (≥ 4) / alphabetic words | letter-spaced titles read as words | 0.004 | 0.04 | 0.5 |
| `replacement_ratio` | U+FFFD per character | encoding damage | 0.0005 | 0.02 | 0.7 |
| `non_alpha_excess` | 1 − alphabetic-character ratio | symbol/number soup | 0.30 | 0.55 | 0.7 |
| `fragmentation_excess` | Falcon tokens per whitespace word minus the expectation for the guessed language (en 1.35, de 1.9, pl/hu 2.4, ru 2.6…) | the tokenizer's own verdict on wordness, language-corrected | 0.35 | 1.2 | 0.7 |
| `dictionary_miss` | 1 − share of ASCII words in `/usr/share/dict/words` (with suffix stripping); English documents only, ≥ 50 words | misreads in English text | 0.28 | 0.60 | 0.6 |

The document-frequency table (`vocab-df.json.gz`, 630 k words with df ≥ 2 out of 2.38 M distinct)
is what makes `hapax_ratio` work across the library's languages: a Polish or Latin word that
appears in three documents is "valid" without a Polish dictionary; an OCR misread almost never
recurs across documents.

**Layout signals** (`layout_score`, kept separate because they are reading-view problems, not
character problems):

| Signal | Definition | lo | hi | w |
|---|---|---:|---:|---:|
| `gutter_line_ratio` | lines with a ≥3-space gap between words (column gutter preserved as whitespace: two columns interleaved on one line) | 0.03 | 0.25 | 0.8 |
| `single_char_line_max_run` | longest run of consecutive one-character lines | 4 | 20 | 0.5 |
| `running_head_page_ratio` | pages whose first/last two lines repeat (digits collapsed) on ≥ 3 pages | 0.3 | 0.9 | 0.3 |
| `furniture_hits_per_10k` | pattern hits (JSTOR/Reveal Digital stamps, IA credits, Google notice, SaturnianCosmology banner, Benjamins notice, Kronia footers) + exact lines from the haunting-index catalogue (`furniture-16/32.jsonl`, ≥ 8 documents, ≥ 20 chars) per 10 k lines | 2 | 20 | 0.4 |
| `dot_leader_lines_per_10k` | lines with ≥ 5 leader dots | 5 | 40 | 0.3 |

**Sibling-edition agreement.** From `artifacts/families/pairs.jsonl`: for every document, the
best non-series partner (`near_duplicate`, `contained`, `parts_or_editions`…) and
`max(jaccard, containment)` are carried as `sibling_id`, `sibling_relation`,
`sibling_agreement`. Two OCRs of one scan with 8 % word error keep ~66 % of their 5-shingles,
so agreement below ~0.3 between a `parts_or_editions` pair with the same title means at least
one of them is bad; which one, the hapax ratio says. This is a column for the re-OCR queue
(prefer the sibling with higher fidelity; the family-split report already lists the pairs), not
a term in the score — only 839 documents have any sibling.

**Column/reading-order heuristics** at corpus scale are limited to `gutter_line_ratio`. The
real column test needs geometry and is done per page in the gold set (§7): `pdftotext
-bbox-layout` blocks are clustered into columns by x-overlap (blocks wider than 60 % of the page
are not columns), and the last phrase of column 1 must precede the first phrase of column 2 in
the record's text. Paddle pages use their block boxes the same way.

## 4. Value signals

**Curatorial tier** (`DEFAULT_TIERS`, override with `--tiers file.json`; first match wins). This
table is a proposal for ember to edit, not a measurement:

| Pattern | Tier | Prior |
|---|---|---:|
| `thegame23/` pastes, `gov.uscourts`, `foia`/`_redacted`, `people/steen/Epstein files` | C | 0.25 |
| `rat_palace/{milshit,technology,tech}/` (manuals, military documents) | B | 0.62 |
| `cathedral/*` (Internet Archive collection mirrors) | B | 0.62 |
| `rat_palace/*` (the library) | A | 0.85 |

Adjustments on top of the prior (`value_score`): `+0.12·ramp(rare_valid_ratio, 0.04, 0.16)` —
share of *valid* words (df ≥ 3 or dictionary) that occur in ≤ 30 documents, i.e. distinctive
vocabulary (Latin, occult, technical) rather than noise; `−0.25·ramp(numeric_ratio, 0.15, 0.40)`
(tables, indexes, price lists); `−0.30·ramp(repeated_line_ratio, 0.10, 0.40)` (catalogues,
dumps); `−0.25·ramp(0.12 − TTR₂₀ₖ, 0, 0.06)` for documents ≥ 2,000 words with a type-token ratio
under 0.12 (lists); `−0.60` on a credential-dump indicator (`privacy.py`); `−0.10` under 500
tokens; and, when a judge file is given (`--judge`, JSONL `{id, delta}` with delta = NLL under a
library checkpoint minus NLL under base, `research/eval/judge.py`), `±0.20` by the sign and size
of the delta. The judge is the "library-vs-base likelihood": it is *not* cheap at 374 M tokens
(it is a forward pass of the 91M over a 2 k-token sample per document, ~1 h on hbox) so the
column exists and is empty in this run.

`quality_flags` from `artifacts/quality-v2/flagged.jsonl` is carried as a column for
cross-reference; the five recommended exclusions there (UFO Researcher corrupt text layers, one
credential dump) are already outside corpus-v1 and go to `drop` in the manifest.

## 5. The 2×2 and its actions

Thresholds `fidelity ≥ 0.60`, `value ≥ 0.50` (`FIDELITY_THRESHOLD`, `VALUE_THRESHOLD`).

| | **high value** | **low value** |
|---|---|---|
| **high fidelity** | **main** — the reading view goes into the resident's stream; the diplomatic view is available for the 90M ghost-noise stream. | **specialist** — kept, faithful, but sampled at reduced temperature or held for a specialist arm (tables, manuals, court text, code). Tier C documents here are candidates to drop by hand. |
| **low fidelity** | **quarantine** — re-OCR. Priority = `p_corrupt × tokens × value` (`reocr-priority.jsonl`). Text stays out of the main stream until a second extraction passes the gold checks; the diplomatic view may still feed the ghost-noise stream on purpose. | **drop** — not worth an engine's time. |

The proposed v2 validation and test sets are the family-clean sets from `artifacts/families/`
(118 + 72 documents) regardless of cell; a low-fidelity validation document is a measurement of
the reading view, and the manifest flags it.

## 6. Three representations per page

1. **Diplomatic (raw)** — exactly what the engine produced for that page, never edited: for
   pdftotext the `\f`-delimited page text; for Paddle the block list (label, content, bbox,
   order). This is the ghost-noise stream and the audit trail.
2. **Reading view** — the training text: catalogue and pattern furniture lines removed, running
   heads and feet removed (lines that open or close ≥ 3 pages, digits collapsed), bare page
   numbers at page edges removed, dash rules removed, runs of ≥ 4 one-character lines removed,
   dot leaders collapsed to `…`, form feeds kept (page structure is information). Dehyphenation
   is already in `normalize_text`. `reading_view()` implements this now; column re-flow and
   caption/footnote demotion need the geometry and are a v2-build task.
3. **Provenance** — `{document_id, source, path, page_index, engine, engine_version,
   text_layer_origin, transforms: [{line, kind, original, replacement}]}`. The transform log is
   exact: `restore(view_lines, transforms)` reproduces the raw lines
   (`test_reading_view_strips_furniture_and_is_reversible`). A training example can therefore
   name its page, and a generated span found by the haunting index can be traced to the page
   image.

On MagazineStudies.2 (JSTOR/Reveal Digital, the validation head in the haunting-index report)
the reading view removes 138 lines: 41 `All use subject to…`, 40 `This content downloaded
from`, 41 download-IP/timestamp lines, the license paragraph, `Stable URL`, `Source: Reveal
Digital` — 38,774 → 32,937 characters, 15 % of the document was furniture.

## 7. The gold set

`hghost-admission gold sample` draws ~300 pages from PDF documents whose `\f` page count agrees
with the record's page count (IA sidecars are excluded: no page breaks), skipping covers and
last pages, oversampling 3× and then filling strata round-robin over (noise band × source ×
columns × era) so every cell that exists is represented. Noise band is the document's fidelity
(`clean ≥ 0.85`, `mid`, `noisy < 0.60`); era is the year in the filename (pre-1950 / 1950-89 /
1990+ / unknown) with a typography guess (letterpress, letterpress-typewriter, phototypeset,
digital-era scan, born-digital); columns are measured on the sampled page from
`-bbox-layout` (or Paddle boxes). Paddle `ocr_unreviewed` documents are in the universe so the
admission candidates get checked by the same rules.

Each page gets unit-test style checks (`page_checks`), each phrased as one yes/no question a
human answers from the page image in seconds:

| Check | Auto-generated from | Passes when |
|---|---|---|
| `must_contain` | the longest run of ≥ 6 valid words on the page's reading view (≤ 14 words) | the phrase is in the text (raw and view); the human confirms it is on the image. **Fails at generation if no such run exists** — the page is unreadable |
| `must_not_contain` | up to 3 furniture lines found on the page (pattern, catalogue, running head) | the line is absent — fails on the raw text by construction, passes on the reading view; the human confirms the line is furniture |
| `column_order` | last phrase of column 1 / first phrase of column 2 from geometry | phrase 1 precedes phrase 2 in the text |
| `no_single_letter_run` | a run of ≥ 4 one-character lines | no such run; the human says whether the image really has a letter column |
| `no_invented_text` | the ≥4-letter words that are neither dictionary nor df ≥ 3, listed (≤ 12) | suspicious share < 5 %; the human confirms the listed words are on the page |
| `table_rows` | ≥ 3 lines with ≥ 3 numeric fields (or Paddle `table` blocks: `<tr>` count) | the count matches what the image shows |
| `page_alignment` | any 6-word window of the must-contain phrase vs the `-bbox-layout` dump of the same PDF page | the record's page N is the PDF's page N |

`gold check` evaluates every check against the **current extraction** (raw page text) and against
the reading view, writes `check-results.jsonl`, `check-summary.json`, and the review sheet
`review.html` (page image beside the text, each check with its auto result and
confirm/deny/skip radios; verdicts persist in the browser and export as JSONL). The human pass is
the calibration set for the ramps in §3 and the acceptance test for any new engine.

## 8. Second-engine bake-off on Kaggle GPU (specified, not run)

Candidates: **olmOCR-2** (7B, allenai; trained with unit-test rewards on exactly the checks
above — reading order, no invented text, table structure), **LightOnOCR-2** (1B; fast enough
for the whole quarantine on a T4/L4 budget), and PaddleOCR-VL 1.6 as the incumbent (its mlx
port produced the 141 raw documents). What the kernel needs:

* **Input**: the gold pages as images (`artifacts/corpus-v2/gold/pages/*.jpg`, ~300 files,
  ~25 MB) plus 20–30 whole documents from the top of `reocr-priority.jsonl` rendered at 150 dpi
  (a Kaggle dataset, private). Page images, not PDFs: the PDFs are 100–750 MB scans.
* **Output**: the raw page schema of `paddle_ocr.py` (`pages[].blocks[{label, content, bbox,
  order}]`) per engine, so `text_from_pages` and `page_checks` apply unchanged, plus per-page
  wall time and, where the engine exposes them, token log-probs (olmOCR-2 does; this would be
  the first recorded engine confidence in the corpus).
* **Scoring**: the gold checks (pass rate per check kind and per stratum), the human-confirmed
  `must_contain` phrases as a CER/WER reference (only confirmed phrases count), and the
  document-level fidelity score of the new text vs the old. The decision rule: an engine is
  adopted for a stratum when it passes ≥ 90 % of confirmed checks there and beats the incumbent
  on `no_invented_text` (the failure mode that matters most for a model that quotes).
* **Budget**: 300 pages × 3 engines is under an hour on a T4 for the 1B model and ~2 h for the
  7B; the quarantine cell (§10) is the real bill and is priced by the priority list.
* **Not**: no engine output enters the corpus without passing `gold check` on its pages and a
  family/near-duplicate check against v1 (`hghost-families`).

## 9. Commands

```sh
.venv/bin/hghost-admission pdfinfo --workers 8            # ~1 min, pdfinfo.jsonl
.venv/bin/hghost-admission score --workers 6              # ~9 min: vocab-df, scores.jsonl, summary.{json,md}, reocr-priority.jsonl
.venv/bin/hghost-admission gold sample --size 300         # ~15 min: gold/gold.jsonl, gold/pages/*.jpg
.venv/bin/hghost-admission gold check                     # seconds: gold/check-*.json*, gold/review.html
.venv/bin/hghost-admission manifest                       # proposed-manifest.json
.venv/bin/hghost-admission reading-view --id <doc> [--log]
.venv/bin/python -m pytest tests/test_admission.py -q     # 19 tests, < 1 s
```

## 10. Results on corpus-v1 (+ the 101 Paddle candidates)

Universe: 4,969 documents, 378.8 M tokens = 4,837 train + 31 validation (corpus-v1) + 101
`ocr_unreviewed` PaddleOCR-VL records (1.8 M tokens, not in v1). `artifacts/corpus-v2/scores.jsonl`
carries every signal as a column; `summary.md` is the readable version.

### Signal distributions (documents; the ramps in §3 were read from these)

| signal | p50 | p75 | p90 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| hapax_ratio | 0.010 | 0.021 | 0.052 | 0.096 | 0.334 |
| unknown_ratio | 0.014 | 0.028 | 0.067 | 0.119 | 0.395 |
| inner_caps_ratio | 0.002 | 0.005 | 0.012 | 0.022 | 0.088 |
| mixed_token_ratio | 0.005 | 0.009 | 0.020 | 0.035 | 0.098 |
| single_char_line_ratio | 0.019 | 0.043 | 0.090 | 0.145 | 0.272 |
| spaced_letter_ratio | 0.000 | 0.000 | 0.004 | 0.040 | 0.487 |
| replacement_ratio | 0 | 0 | 0 | 0.0005 | 0.0046 |
| non_alpha_excess | 0.229 | 0.252 | 0.293 | 0.343 | 0.464 |
| tokens per word (English) | 1.72 | | | | |
| dictionary_miss (English) | 0.076 | 0.111 | 0.204 | 0.291 | 0.513 |
| gutter_line_ratio | 0 | 0 | 0 | 0 | 0 |
| single_char_line_max_run | 4 | 9 | 18 | 27 | 65 |
| running_head_page_ratio | 0.059 | 0.730 | 0.922 | 0.994 | 1.0 |
| furniture_hits_per_10k lines | 0 | 2.4 | 31 | 160 | 998 |
| dot_leader_lines_per_10k | 0 | 12.6 | 58 | 105 | 287 |
| rare_valid_ratio | 0.031 | 0.051 | 0.101 | 0.169 | 0.378 |
| numeric_ratio | 0.027 | 0.042 | 0.065 | 0.086 | 0.158 |

Two calibration lessons paid for in the first pass: (1) English in this library tokenizes at
1.72 Falcon tokens/word, not web English's 1.35 — with the naive expectation `fragmentation`
condemned 63 M tokens of Brill/Eisenbrauns scholarship, plant catalogues and transliteration; the
expectations are now corpus medians per language plus 3.0 per unit of non-Latin letter share, and
the term's weight is 0.5. (2) The vocabulary terms are Latin-script instruments: an Arabic edition
(`Amad al-Wallī`, the *Book of Curiosities*), the Japanese *Cosmo* issues and a near-duplicate pair
(every word at df = 2) all scored as noise. Character terms are now scaled by `1 − non_latin_ratio`
and by 0.5 for born-digital layers, and a document with a near-duplicate uses true hapaxes only.
`gutter_line_ratio` never fires: `pdftotext` without `-layout` does not preserve gutters, so
column damage is invisible at corpus scale and only the gold set's geometry check sees it.

### The 2×2

| cell | fidelity | value | documents | tokens | share of tokens |
|---|---|---|---:|---:|---:|
| main | ≥ 0.60 | ≥ 0.50 | 4,374 (4,290 in v1) | 334,865,479 | 88.4 % |
| quarantine (re-OCR) | < 0.60 | ≥ 0.50 | 536 (520 in v1) | 41,252,043 | 10.9 % |
| specialist | ≥ 0.60 | < 0.50 | 31 | 1,161,853 | 0.3 % |
| drop | < 0.60 | < 0.50 | 28 | 1,547,367 | 0.4 % |

Fidelity is bimodal: 4,000 documents (302.6 M tokens) sit at ≥ 0.9 and 574 (42.8 M) below 0.6,
with only 405 (33.4 M) in between. Mean fidelity by text-layer origin: IA djvu sidecars 0.967,
born-digital 0.944, unknown producer 0.89, OCR-layer producers 0.86, PaddleOCR-VL candidates
0.86 (18 of the 101 candidates fall below 0.6; 83 would be admitted on fidelity). The badness
terms that fire (≥ 0.5) most by token mass: spaced letters 17.9 M (Vollmann *Rising Up and Rising
Down*, Valerian *Matrix III/IV*, Ted Nelson *Computer Lib* — letter-spaced text layers, a
re-extraction rather than a re-OCR), fragmentation 16.0 M, single-character lines 11.1 M, hapax
10.7 M, inner caps 8.2 M.

Value is, by design, mostly the curatorial tier (p5 = 0.62, p50 = 0.85): rat_palace is tier A and
dominates. Only 59 documents score below 0.5 — the thegame23 pastes, the Epstein file dump (also
fidelity 0.01), the Illinois flag FOIA release (748 k tokens, faithful, repetition 0.17), court
dockets, two East Village Other `pull.txt` index files. The judge column is empty (§4).

### Proposed manifest (`proposed-manifest.json`, status `proposed`)

| stream | documents | tokens |
|---|---:|---:|
| main (train) | 4,220 | 330,002,671 |
| specialist (train, reduced weight) | 35 | 5,165,276 |
| quarantine (re-OCR before use) | 499 | 36,637,915 |
| drop | 25 | 1,529,048 |
| validation (family-clean, from `artifacts/families`) | 118 | 2,956,654 |
| test (family-clean) | 72 | 2,535,178 |

Routing on top of the cell: quality-v2 recommended exclusions and credential dumps → drop;
quarantine documents with ≥ 30 % non-Latin letters → specialist (script is not an extraction
failure; 4.0 M tokens: the Arabic and Japanese editions above); the family-clean splits are
taken whole. Every document carries its reasons, its top badness terms, its running heads and
the text-layer origin.

### Re-OCR priority (`reocr-priority.jsonl`, 510 Latin-script quarantine documents, 36.6 M tokens)

| # | priority | tokens | p_corrupt | origin | document | why |
|---:|---:|---:|---:|---|---|---|
| 1 | 1,750,722 | 2,259,757 | 0.86 | unknown | pubs/bwill *Book of Curiosities* (Yossef Rapoport ed.) | Arabic half emitted one character per line; English half fine |
| 2 | 957,798 | 988,309 | 1.00 | ocr_layer | people/heinz_von_foerster/cybernetics_of_cybernetics.pdf | rotated/mirrored OCR: `uoT}eztuebro`, `apew ere` |
| 3 | 630,088 | 850,373 | 0.85 | unknown | corpus_of_english.pdf | phonetic transcription corpus (`Jall ‘these rodd PEOPLEm 613`); faithful but not prose — a value call |
| 4 | 568,402 | 1,112,984 | 0.60 | unknown | culture/vollmannrisingupanddownmerged.pdf | letter-spaced text layer (epub sibling is clean: use it) |
| 5 | 567,935 | 1,071,459 | 0.61 | ocr_layer | people/valdamar_valerian/matrix.iii.vol1.pdf | spaced letters + misreads (`maoipulation`, `prinapk`) |
| 6 | 508,104 | 800,613 | 0.88 | born_digital | pubs/bwill *Ancient Magic and Divination 8* (van Buylaere et al.) | non-alpha 1.0: cuneiform sign lists / transliteration; inspect |
| 7 | 439,805 | 862,363 | 0.60 | ocr_layer | people/valdamar_valerian/matrix.iv.the_equivideum.pdf | spaced letters |
| 8 | 405,245 | 525,262 | 0.84 | born_digital | pubs/bwill/abusch2015.pdf | Akkadian tablet edition: `D qq k2 jj ii obv rev` columns; specialist, inspect |
| 9 | 400,134 | 773,136 | 0.58 | unknown | pubs/bwill *Apocalypse of Paul in Sahidic Coptic* | Coptic tokenization; inspect |
| 10 | 368,796 | 679,158 | 0.66 | ocr_layer | people/ted_nelson *Computer Lib / Dream Machines* | letter-spaced: `th e o b viou s s o lu tio n` |
| 11 | 336,858 | 474,180 | 0.96 | ia_ocr_sidecar | cathedral Badiny Jós Ferenc *Jézus király a pártus herceg* (Hungarian) | hapax 1.0: the only Hungarian document; likely faithful — the df instrument has no Hungarian |
| 12 | 319,084 | 404,398 | 0.86 | ocr_layer | pubs/sbl/flavius_philostratus.heroikos.pdf | Greek apparatus read as Latin letters: `Suvic0our FAPCD` |
| 13 | 316,777 | 603,236 | 0.57 | born_digital | pubs/bwill *Magico-medical means… ghost-induced illness* | transliteration; inspect |
| 14 | 301,252 | 567,000 | 0.63 | ocr_layer | people/ted_nelson *Computer Lib* (1974 scan) | letter-spaced |
| 15 | 279,661 | 296,195 | 0.97 | ocr_layer | arts/sean_landers.art_life_and_god.pdf | handwritten pages: `Ktk ASS SHow CR THED'D` — a VLM engine's case |
| 16 | 278,804 | 615,915 | 0.47 | ocr_layer | math/brouwer.works.vol1.pdf | dictionary miss 0.58 + spaced letters (Dutch/German mathematics) |
| 17 | 271,608 | 368,373 | 0.84 | ocr_layer | corpus_of_english.0.pdf | as #3 |
| 18 | 266,849 | 743,006 | 0.56 | ia_ocr_sidecar | cathedral *UFOs and the Extraterrestrial Contact Movement* v1 | fragmentation 1.0: a bibliography (names, numbers) |
| 19 | 257,406 | 514,213 | 0.83 | unknown | math/introduction_to_geonometry.pdf | tables as symbol soup: `EcaRIAl2BgVeR8ElRNg` |
| 20 | 224,312 | 539,422 | 0.43 | unknown | arts/circa_1968.pdf | dictionary miss 0.52, hapax 0.19: exhibition catalogue OCR |

Reading the list: about half are engine failures (#2, #5, #7, #10, #12, #14, #15, #19, #20) — the
re-OCR bake-off's real targets; a quarter are *specialist* scholarly editions whose
transliteration and apparatus look like noise to text-only instruments (#6, #8, #9, #13; the
gold set has to adjudicate them); the rest are value or format calls (#3/#17 transcription
corpus, #18 bibliography, #4 has a clean epub sibling) that a human should route by hand. A
priority list is a reading order, not a verdict.

### The gold set and its baseline (`artifacts/corpus-v2/gold/`)

300 pages from 300 documents (297 rat_palace, 3 cathedral: nearly every cathedral PDF is an IA
djvu sidecar with no page breaks and so ineligible), 1,442 candidate pages measured for columns
before the stratified pick; 54 distinct (noise × source × columns × era) strata. Noise bands:
116 clean / 84 mid / 100 noisy. Columns: 161 single / 135 multi / 4 no text layer. Era: 27
pre-1950, 95 1950–89, 79 1990+, 99 unknown; typography: 11 letterpress, 55
letterpress-typewriter, 72 phototypeset, 35 digital-era scan, 49 born-digital, 78 unknown.
Page images: 300 JPEGs at 1000 px, 30 MB. Review sheet: `gold/review.html` (open locally: each
page's image beside its text, every check with its auto result and confirm/deny/skip radios;
verdicts persist in the browser and export as JSONL for `gold/verdicts.jsonl`).

1,168 checks; baseline against the **current extraction** (raw) and the **reading view**:

| check | applicable | raw pass | view pass | what a failure means |
|---|---:|---:|---:|---|
| must_contain | 300 | 96.7 % | 96.7 % | 10 pages have no run of six valid words: unreadable as extracted |
| must_not_contain | 139 | 0 % | 71.9 % | 139 furniture lines on 300 pages; the reading view removes 100, 39 survive (running heads below the 3-line edge window, notices not in the catalogue) — the review says which |
| column_order | 89 | 43.8 % | 43.8 % | on 56 % of measured multi-column pages the text's order disagrees with the geometric column order; the human check decides whether the geometry or pdftotext is right |
| no_single_letter_run | 32 | 0 % | 100 % | 32 pages carry a run of ≥ 4 one-character lines; the view strips them all; the human says which were real (vertical captions) |
| no_invented_text | 300 | 65.3 % | 65.3 % | 104 pages have ≥ 5 % suspicious words (names, foreign words and misreads alike): the listed words are what the human checks against the image |
| page_alignment | 285 | 84.9 % | 84.9 % | 43 pages where no 6-word window of the phrase is found in the PDF page's own layout dump: page-split drift, or `-bbox-layout` reading order differing from raw mode; the image settles it |
| table_rows | 23 | 100 % | 95.7 % | the view's dot-leader collapse changed one table's numeric row count |
| **all** | **1,168** | **67.6 %** | **78.9 %** | pages passing every applicable check: 73 raw → 120 view (clean 37 → 65, mid 22 → 32, noisy 14 → 23) |

Read as a baseline: the current extraction fails a third of unit tests it can be given, and the
reading view alone (no re-OCR) recovers a third of those failures — all of them furniture and
letter-column removals. What it cannot recover is what the bake-off is for: column order,
invented or misread words, unreadable pages. The human pass turns these auto results into labels;
until then the per-band pass rates (clean 56 % of pages all-pass on the view, noisy 23 %) are the
only evidence that the fidelity score orders pages the way the checks do.

## 11. What could not be done here, and what is next

* **No engine confidence exists** in any recorded output; the text-layer origin prior is the
  substitute. The first recorded confidences will come from the bake-off (olmOCR-2 log-probs).
* **The library-vs-base judge** was not run (an hour of hbox for 4,969 × 2 k-token samples);
  `--judge` accepts its output and the value score has the slot.
* **IA djvu sidecars** (564 documents, 19.6 M tokens, the cleanest text in the corpus at 0.967
  mean fidelity) have no page breaks, so they get document-level scores but no page-level gold
  checks; the IA hOCR files would give positions and running heads.
* **Column repair** is measured (56 % of multi-column gold pages disagree with geometry) but not
  implemented: the reading view strips, it does not re-flow. `pdftotext -bbox-layout` per page
  is cheap enough to re-flow the quarantine documents at v2 build time.
* **The tier table is a proposal**; the value axis is ~90 % tier prior. Ember's edits to
  `DEFAULT_TIERS` (or a `--tiers` file) are the real value signal.
* **Language labels**: the scoring pass ran before CJK/Arabic/Hebrew labels were added to
  `language_guess`; those documents show `unknown` in `scores.jsonl` but are routed correctly by
  `non_latin_ratio`. The next `score` pass labels them.
* **The human verdicts** are the deliverable this pipeline is waiting on: with ~1,200 labelled
  checks the ramps in §3 become a fitted classifier instead of hand-set lines, and the bake-off has
  its acceptance test.
