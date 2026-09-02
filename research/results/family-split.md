# Corpus-v1 work/edition families and a family-disjoint split

Analysis only: nothing under `artifacts/dataset/`, `artifacts/extracted/` or
`artifacts/tokenized/` was touched. Outputs live in `artifacts/families/`
(gitignored, regenerable in ~90 s from the cached sketches, ~10.5 min cold).

```text
uv run hghost-families --dataset artifacts/dataset --records artifacts/extracted/records --output artifacts/families
# or: .venv/bin/python -m hghost.families ...
uvx ruff check src/hghost/families.py tests/test_families.py
.venv/bin/python -m pytest tests/test_families.py -q
```

## Why

Corpus-v1's split is a per-document hash of `content_sha256` (0.5 % to
validation) after the build removed exact duplicates, `_text.pdf` siblings and
near-duplicates at bottom-k resemblance >= 0.92 (k = 192, word 5-shingles,
min 500 words). That is document-disjoint, not work-disjoint: a second scan,
edition, part or excerpt of a work in validation can sit in train and inflate a
measured loss drop (the hbox 10M checkpoint's 3.46 %). This report measures
that, inventories families across the whole corpus, and proposes a clean split
for corpus-v2. Nothing is rebuilt or retokenized here.

## Method

Two signals per document, combined per pair, unioned into families.

**Path / title.** Filenames are normalised: extension, parenthesised and
bracketed groups, Anna's Archive `Title -- Author -- ... -- md5` tails, z-lib
suffixes, scan markers (`_text`, `.ocr`, `.ia`, `final`, `redacted`), stop
words, months and long hex ids are stripped. Numbers are classified: years
(`1[5-9]xx`/`20xx`) versus part/volume/issue-like numbers (digits, ordinals,
roman numerals, `v02n20`, and `vol/no/issue N` phrases, which also mark the
file as periodical). Within one directory, documents with the same non-empty
stem are:

| situation | relation | confidence |
|---|---|---|
| periodical context (`magazines/`, dir or stem matches journal/newsletter/..., issue codes) | `series` (tracked as `series_id`; every `magazines/<title>/` folder with 2+ documents is one series whatever its issues are called - `thviii01.txt`, `tt075.txt`, `Para10.pdf` - and a same-named folder elsewhere such as `pubs/bsrf/round_robin` joins it; elsewhere keyed by directory basename + stem) | not a family |
| any part-like number, or no numbers but a real title word (`.ia` vs `.ocr` scans) | `parts_or_editions` | medium |
| differ only by year (`suttles-1974` / `suttles-1980`) | `year_siblings` | low |
| identifier-only stem (`d4331c_<md5>`) | unrelated | – |

Across directories, the same *distinctive* stem (two or more title words) with
the same numbers is `same_title` (low); different issue numbers of a
periodical are series only.

**Content.** Word 5-shingles (same `canonical_words` as the build) hashed to
64 bits; a Broder MOD-8 sketch keeps every shingle whose top 3 bits are zero
(1/8 of them, 20.7 M sampled shingles corpus-wide, `sketches.npz`). Unlike the
build's bottom-k sketch this is a consistent sample of the *set*, so both
resemblance (Jaccard) and containment (share of the smaller document's
shingles found in the larger) are estimable. Candidate pairs come from an
inverted index over the sampled shingles (LSH with one row per band); hashes
present in more than 64 documents are boilerplate and ignored; pairs must share
>= 8 sampled shingles and each side must have >= 16 samples. Levels on
`max(jaccard, containment)`: high >= 0.70 (`near_duplicate` if Jaccard, else
`contained`), medium >= 0.35 (`overlapping`), low >= 0.15 (`weak_overlap`).
The build's 0.92 is far above all of these on purpose: two OCRs of one scan
with 8 % word error keep only ~0.92^5 = 66 % of their shingles, so a
same-work pair can legitimately score 0.3-0.5.

**Combination.** `parts_or_editions` + medium content -> high; + low content
-> high when the stem is distinctive, medium when it is a surname; path-only
stays medium. `same_title`/`year_siblings` + medium -> high, + low -> medium,
alone -> low. Two issues of one series need medium content to join a family.
Medium and high edges are unioned (`_DisjointSet`), low edges are recorded as
`weak_links` and still disqualify a document from the proposed split. Family
ids are `fam-` + sha256 of the sorted member ids, so they are stable across
reruns with the same membership.

## Counts

```text
documents                      4,868   (4,837 train, 31 validation)   376,780,808 tokens (no EOS)
families                       4,273
  multi-document families        244   839 documents, 65,364,602 tokens (17.3 % of corpus)
    by confidence                143 high, 101 medium
    by method                    206 content, 7 content+path, 31 path-only
    by size                      190 pairs, 42 of 3-5, 8 of 6-20, 4 of >20
periodical series                122   2,220 documents (45.6 % of documents)
  largest                        East Village Other 251, Journal of Borderland Research 204,
                                 Awareness 119, Thoth Catastrophics 110, Oak Leaves 91, October 69
scored pairs                     460 high, 935 medium, 521 low (+26,339 series-only pairs)
runtime                          626 s cold (549 s read+sketch, 77 s analysis), 91 s with sketches.npz
```

Sanity checks that the rules behave: `kvlt/golden_rosycross/d4331c_<md5>.pdf`
x 35 (2.08 M tokens) are singletons, `Animals and Men - No 01..18` are a
series, `magin-2004/2010/2016` are year siblings with no content overlap and
stay separate, `corpus_of_english.pdf` / `corpus_of_english.0.pdf` join at
containment 0.999, `the_canadian_alternative.ia` / `.ocr` join at Jaccard 0.30
(two OCRs of one scan), and the identical `round_robin_v7_n4_nov_dec_1956`
issue filed in two folders joins at Jaccard 0.53 while the other 400 cross-folder
issue pairs stay series-only.

## Leakage in the current validation split (31 documents, 2,380,433 tokens)

| level | docs | tokens | share | cumulative |
|---|---:|---:|---:|---:|
| high | 1 | 10,894 | 0.46 % | 0.46 % |
| medium | 2 | 107,562 | 4.52 % | 4.98 % |
| low | 3 | 62,773 | 2.64 % | 7.61 % |
| series only | 13 | 635,873 | 26.71 % | 34.33 % |
| clean | 12 | 1,563,331 | 65.67 % | |

Concrete cases (train partner in parentheses):

- **high** `the-cryptozoological-library/regusters-vandusen-1985.pdf` (10.9 k
  tokens): 83.4 % of its shingles are inside
  `magazines/pursuit/...PURSUIT-Newsletter-No-72-Fourth-Quarter-1985...pdf`
  (85 k). The article was reprinted in the newsletter issue. This is exactly the
  excerpt-inside-volume case document dedup cannot see.
- **medium** `people/michael_bertiaux/m7r.02.pdf` (101.6 k): parts `m7r.01`,
  `.03`, `.04` of the same work are in train (family 304 k tokens). Path
  evidence only; as expected for consecutive parts the text overlap is ~0.
- **medium** `the-cryptozoological-library/suttles-1974.pdf` (5.9 k): 22 % of
  its shingles recur in `suttles-1980.pdf`; same author, revised paper.
- **low** `magazines/hermetic_journal/13.pdf` (48.6 k): 15.9 % contained in
  `people/valdamar_valerian/matrix.iii.vol1.pdf` (1.07 M), a compilation that
  also reprints Hermetic Journal 08 and 11, several Borderland Research and
  Instrumentum issues and Isian News. Listed in the review queue.
- **low** `Proceedings.09.03` and `Proceedings.11.05` share 28 % / 19 % of the
  1.4 k-token sibling `Proceedings.10.02` - masthead boilerplate.
- **series only** 8 issues of *East Village Other* (240 sibling issues in
  train), plus one issue each of Journal of Borderland Research (178 siblings),
  Journal of Psychohistory, Georgian Monthly, Assembling, MagazineStudies and
  ISC Newsletter. Their best train neighbour is always another issue of the
  same title at 2-10 % containment: recurring mastheads, columns and ads.

The 12 clean documents have best-neighbour containment <= 1.5 % except
`richard_sylvan/1974.Another 'Fatal' Objection...` (13.5 % on 23 shared samples
with `routley2019.b.pdf`, quotation-level) and `math/from_onions_to_broccoli`
(6.8 %).

Reading: strict work-level leakage is small (7.6 % of validation tokens at low
or better, 5 % at medium or better), so the 3.46 % loss drop is mostly real.
The larger issue is that 61 % of validation documents and 34 % of its tokens
are periodical issues or work-parts whose siblings are heavily represented in
train; that measures memorised house style and page furniture as much as
generalisation, and corpus-v2 should not carry it.

## Largest families by token mass (`largest-families.jsonl`)

The top 40 families hold 62.7 M tokens (16.6 % of the corpus); 21 of them are
multi-document.

| tokens | size | conf | what |
|---:|---:|---|---|
| 4,711,179 | 8 | medium | Whole Earth Catalog editions 1968-71 (editions overlap J~0.4, C~0.6) |
| 3,259,432 | 2 | high | Jeziorski *Najważniejsza Książka...* two copies (J = 0.91) |
| 3,243,519 | 2 | high | Vollmann *Rising Up and Rising Down* epub + pdf |
| 3,156,498 | 1 | – | Auerbach *Wilderness Medicine* 5e |
| 3,038,261 | 6 | medium | *Investigations into Magic* vols 1-6 (shared front matter, C~0.16) |
| 2,967,005 | 36 | medium | Langman Lanza Docs, 36 Internet Archive page saves of one collection |
| 2,423,542 | 9 | medium | `people/jbg/postsSMALL.pdf` contains the other eight |
| 2,402,044 | 175 | medium | `art_n_language/pdf/wholething.pdf` plus 174 pieces it contains |
| 2,259,757 | 1 | – | *Book of Curiosities* |
| 2,096,506 | 1 | – | Moerman *Native American Ethnobotany* |
| 1,887,646 | 1 | – | Facciola *Cornucopia II* |
| 1,819,559 | 1 | – | Japanese War Crimes Guide |
| 1,810,822 | 8 | medium | Jeziorski *Luciferian Doctrine* variants |
| 1,474,457 | 1 | – | *The Realist* compilation |
| 1,227,243 | 3 | medium | *Study of Time* i-iii (path only; review) |
| 1,218,746 | 2 | high | `corpus_of_english.pdf` + `.0.pdf` (C = 0.999) |
| 1,187,495 | 2 | medium | Brouwer collected works vol 1, two scans |
| 1,178,891 | 2 | high | Priest/Routley/Norman *Paraconsistent Logic*, two copies |
| 1,114,632 | 2 | medium | Brouwer collected works vol 2, two folders |
| 1,040,539 | 5 | medium | Jane Lead *A Fountain of Gardens*, five EEBO scans |

Also notable: the *Cryptozoology* journal volumes (22 documents, 1.38 M) contain
the individually filed articles (`heuvelmans-1988` is 97 % inside `Vol 07 -
1988`, `mayor-1989` inside `Vol 08`), and `Pursuit-Magazine-No-1-5-Combined`
contains the separate issues 2-5 at C >= 0.99.

## Proposed family-disjoint split (`proposed-validation.jsonl`, `proposed-test.jsonl`)

Eligibility: singleton family, no weak link, not a member of any periodical
series, not in the review queue, >= 16 sampled shingles, 2,000-150,000 tokens.
That leaves 1,141 documents / 45.5 M tokens (ineligible: 1,924 periodical
siblings, 839 in multi-document families, 561 outside the size range, 400 with
weak links, 3 too short). Strata are (source, top-level directory) for
directories holding >= 1 % of corpus tokens, smaller ones pooled per source
into `other` (17 strata); each split's per-stratum target is proportional to
corpus token mass, filled in `blake2b("families-v1" + content_sha256)` order
with at most 37.5 k tokens of overshoot, then topped up. Clean documents of the
current validation set go first so checkpoints scored on corpus-v1 stay
comparable.

```text
validation   118 documents   2,956,654 tokens   cathedral 15 / rat_palace 103   median doc 15.0 k
test          72 documents   2,535,178 tokens   cathedral 11 / rat_palace  61   median doc 22.4 k
shared documents 0, shared families 0, no document has a series sibling anywhere
kept from current validation: NABR9, sylvan 1974 'Fatal' Objection, size_queen,
  sylvan UQFL291_b15_i1161x, from_onions_to_broccoli, heberle-2004
largest strata (validation / test tokens): magazines 698 k / 139 k, pubs 541 k / 540 k,
  people 476 k / 475 k, other(rat) 161 k / 161 k, arts 117 k / 117 k, culture 115 k / 115 k
```

The `magazines` stratum (27 % of the corpus) cannot be filled honestly: nearly
every document there is an issue of a multi-issue series, so only the ~30
standalone titles filed directly under `magazines/` (e.g. `2Outsider.pdf`,
`Telephone.15.pdf`, `witches_annual.1983.pdf`) qualify. Validation takes most
of them; test gets two and is topped up from `metaphysics` and others. A
corpus-v2 evaluation of periodical text therefore has to hold out *whole
titles* (say Thoth Catastrophics or Oak Leaves entirely), which is a curation
decision, not something this allocator should make silently.

Six clean current-validation documents above 150 k tokens (husserliana.06,
*Conspiracy Theory Discourses*, almsgiving, *exploring_inner_experience*,
*theoretical_geography.2nd.ocr*, *fiction_as_method*; 1.44 M tokens) are dropped
by the size rule; `--max-doc-tokens 400000` keeps them at the cost of half the
budget. `magazines/` documents in the proposal are standalone items filed there
(single-issue titles), not issues of a multi-issue series.

## Review queue (`review-queue.jsonl`, 44 entries)

42 families >= 100 k tokens (36.9 M tokens together) flagged for path-only
evidence, borderline overlap (< 0.6), no high edge, or size >= 6, plus the two
validation weak links (hermetic_journal/13 vs matrix.iii.vol1; Proceedings
masthead). The largest ones I checked by hand look like real families (Whole
Earth Catalog editions, Langman IA saves, jbg compilation, art_n_language
`wholething`, Jane Lead scans); the path-only ones are multi-volume works
(*Study of Time* i-iii, *Natural Genesis* 1-2, *Ancient Egypt* 1-2, 12-tribes
2-3, husserliana 05/15) where merging is conservative for splitting but wrong
for "same work" counts.

## Confidence and caveats

- Sampling at 1/8 makes small-document estimates noisy (a 500-word document
  has ~60 samples); the 8-shared / 16-sample floors keep them out of families
  but such documents could still be undetected excerpts.
- Different OCRs of one scan with heavy noise can fall under 0.15 Jaccard; the
  title-stem rule catches the same-folder cases, cross-folder ones with
  unrelated filenames would be missed. `theoretical_geography.2nd.ocr` has no
  partner anywhere by either signal.
- Periodical detection is heuristic (`magazines/<title>/` folders, directory/
  stem vocabulary, issue codes); a zine filed under `people/` with roman-numeral
  issues (`smoke_signal_i..vi`) is treated as parts of one work, which is the
  conservative direction, and a periodical folder outside `magazines/` whose
  issue names carry no stem or issue code would be missed.
- Series-level leakage (mastheads, columns) is reported, not modelled as a
  family; the proposed split simply excludes every document that has series
  siblings.

## Files

- `artifacts/families/families.jsonl` - one row per document: id, source,
  path, tokens, split, family_id, family_size, family_tokens, method,
  confidence, title_stem, series_id, weak_links, sampled_shingles.
- `artifacts/families/pairs.jsonl` - every scored pair (1,916 family-relevant
  plus 26,339 series pairs) with jaccard, containment, shared samples.
- `artifacts/families/leakage-report.json` - per validation document.
- `artifacts/families/largest-families.jsonl`, `review-queue.jsonl`,
  `proposed-validation.jsonl`, `proposed-test.jsonl`, `summary.json`,
  `sketches.npz` (cache, delete to recompute content sketches).
- Code: `src/hghost/families.py` (`hghost-families`), tests in
  `tests/test_families.py`.
