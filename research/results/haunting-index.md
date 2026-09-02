# Haunting index: exact-match provenance over corpus-v1

Date: 2026-09-01

`hghost-haunt` (`src/hghost/haunt.py`) builds a token-aligned suffix array over the sealed
training stream and answers three questions with one structure: which corpus document a
generated span quotes (provenance), what fraction of a generation is covered by exact
8/16/32-gram matches (memorization scanner), and which token n-grams recur across many distinct
documents (page-furniture detector). The sealed inputs under `artifacts/tokenized/` and
`artifacts/dataset/` were read only; the index lives in `artifacts/haunting-index/` (not sealed,
rebuildable in six minutes). Raw outputs of every run below are in
`research/results/haunting-index/`.

## Index

| Item | Value |
|---|---|
| Stream | `artifacts/tokenized/train.bin`, sha256 `fdaa8b85…3124`, 374,405,212 tokens |
| Documents | 4,837 (`documents.jsonl`: id, source, path, token_offset, tokens) |
| EOS check | 4,837 EOS tokens; every EOS position equals the manifest-reconstructed document end (0 mismatches) |
| Suffix array | `suffix-array.npy`, int32, 374,405,212 entries, 1,497,620,976 bytes, memmapped at query time |
| Encoding | each uint16 token as a big-endian byte pair; `pydivsufsort` 0.0.20 (libdivsufsort 3.0.1) sorts the 748,810,424-byte string; only even byte offsets are kept |
| Order check | 20,000 random adjacent rows compared to depth 64: 0 violations |

Byte order equals token order under big-endian pairs, so the even-offset subsequence of the
byte suffix array is exactly the token suffix array. Every query path only ever sees token
offsets.

Build on the M2 Max (96 GB): 336.7 s wall, of which libdivsufsort 283.8 s and the even-offset
filter about 6 s; peak RSS 7.63 GB (`getrusage`; `/usr/bin/time -l` agrees, 5.60 GB "peak
memory footprint"). The process only used 98 s of CPU over those 337 s and was observed at
~37% of a core during the sort: it was launched from a background shell while three other
Python jobs were running, so macOS scheduled it as background work. A foreground build should
land near two minutes. The document-offset reconstruction disagreeing with the stream is a
hard build failure, not a silent fix (`tests/test_haunt.py::test_build_rejects_offset_mismatch`).

Query cost: a 2,000-token query is one lower-bound binary search per position (about 29
comparisons of numpy slices against the memmapped stream) plus two searches per emitted span
for the occurrence range; 0.66 s for the validation control, 1.2 s wall including index load.

## Sanity: positive control

2,000 tokens copied from the middle of `train.bin` (offset 187,202,606):

| Field | Value |
|---|---|
| Maximal spans ≥ 16 | 1 |
| Span | query offset 0, length **2,000**, corpus offset **187,202,606** |
| Document | `cbf08d75cc5236534b9a8833`, rat_palace, `people/andrzej_jeziorski/[THE#MY .FEMALE SLAVE @VOLUME-2.OF13.pdf`, document offset 53,168 |
| Occurrences of the span | 1 (one document) |
| Coverage ≥ 8 / 16 / 32 | 1.0 / 1.0 / 1.0 |

The match length equals the remaining copied span at every position (the per-position
longest-match array is 2000, 1999, …, 1), and the reported offset is the copy source.

## Sanity: validation head

First 2,000 tokens of `validation.bin`, i.e. the start of validation document
`1ddc8267e52f018daad9eca9` (rat_palace, `magazines/further_studies/MagazineStudies.2.pdf`, a
Reveal Digital / JSTOR scan):

| Field | Value |
|---|---|
| Maximal spans ≥ 16 | 26 (43 at ≥ 8) |
| Longest match | 197 tokens |
| Coverage ≥ 8 / 16 / 32 | **0.3425 / 0.2885 / 0.2045** |
| Top quoted training documents | `MagazineStudies.4.pdf` (238 tokens), `MagazineStudies.3.pdf` (193), `io/IOMagazine.4.pdf` (191), `EastVillage.Aug.1966.pdf` (180), `2Outsider.pdf` (148) |

Every one of the 26 spans is page furniture, none is prose:

- `This content downloaded from\n108.12.255.145 on Sat, 09 Nov 2024 09:14:5…` (up to 92
  corpus occurrences; the download IP and timestamp of the session that fetched the whole
  Reveal Digital batch)
- `:54 UTC\nAll use subject to https://about.jstor.org/terms\n\n\x0c` (121 occurrences)
- the 197-token JSTOR license paragraph (`Licenses: Creative Commons: Attribution-NonCommercial
  / JSTOR is a not-for-profit service that helps scholars…`), present in 2–3 training documents
- `Stable URL: https://www.jstor.org/stable/community.28040…` (4 documents; consecutive
  JSTOR community ids)
- `Source: Reveal Digital , 02-01-196…`

So a naive "fraction of validation covered by ≥ 32-gram training matches" reads 20% for a
document whose text is genuinely held out. The span records carry `occurrences` and
`distinct_documents`, which separate furniture (many documents, or many occurrences in a
sibling issue) from true quotation (one document, one occurrence); 17 of the 26 spans here have
`distinct_documents == 1` only because the sibling issue was scanned in the same session.
Any memorization number reported for the ghost must subtract furniture-covered positions, and
the validation split is not furniture-disjoint from train.

## Page furniture in corpus-v1

`hghost-haunt furniture` computes the adjacent-row LCP array capped at 64 tokens
(138 s, cached as a 374 MB `.npy`), then, at levels 8/16/32/64, groups suffix-array runs
sharing at least that many tokens, keeps left-maximal groups (the preceding token differs
somewhere, so the group is not merely the tail of a longer repeat), counts distinct documents
per group, and reports the common extension of the whole group. Whole run 171 s, peak RSS
6.4 GB; re-runs from the LCP cache take 4–9 s. Rank-500 document counts: 133 at ≥ 8 tokens,
41 at ≥ 16, 20 at ≥ 32.

### Top 30 by document count, n-grams ≥ 8 tokens (`furniture-8.jsonl`)

| # | docs | occurrences | len | text |
|---:|---:|---:|---:|---|
| 1 | 681 | 88,440 | 8 | ` . . . .` |
| 2 | 679 | 85,489 | 8 | `. . . . ` |
| 3 | 457 | 3,512 | 8 | `. . . .\n` |
| 4 | 451 | 2,246 | 8 | ` N.Y. 100` |
| 5 | 451 | 1,381 | 8 | `,000,000` |
| 6 | 446 | 2,001 | 8 | `, N.Y. 10` |
| 7 | 441 | 982 | 8 | ` 100,000` |
| 8 | 414 | 1,553 | 8 | ` York, N.Y. 1` |
| 9 | 368 | 1,162 | 8 | `.Y. 1001` |
| 10 | 357 | 1,482 | 8 | `. . . .\n\n` |
| 11 | 355 | 776 | 8 | `, New York, N.Y.` |
| 12 | 348 | 724 | 8 | ` New York, N.Y. ` |
| 13 | 316 | 622 | 8 | ` in the 1960s` |
| 14 | 293 | 672 | 8 | `\nP.O. Box 1` |
| 15 | 292 | 475 | 8 | ` in the 1950s` |
| 16 | 284 | 291 | 8 | ` of Congress Cataloging-in-Public` |
| 17 | 284 | 291 | 8 | ` Congress Cataloging-in-Publication` |
| 18 | 282 | 290 | 8 | ` Cataloging-in-Publication Data` |
| 19 | 279 | 958 | 8 | `, 101, 1` |
| 20 | 278 | 817 | 8 | `, 123, 1` |
| 21 | 273 | 583 | 8 | ` in the 1970s` |
| 22 | 272 | 817 | 8 | `, 109, 1` |
| 23 | 271 | 843 | 8 | `, 103, 1` |
| 24 | 271 | 811 | 8 | `, 104, 1` |
| 25 | 270 | 815 | 8 | `, 127, 1` |
| 26 | 270 | 285 | 8 | `https://archive.org/details/` |
| 27 | 269 | 64,440 | 16 | ` . . . . . . . .` |
| 28 | 269 | 62,518 | 16 | `. . . . . . . . ` |
| 29 | 267 | 802 | 8 | `, 111, 1` |
| 30 | 267 | 715 | 8 | `0,000,00` |

At eight tokens the ranking is dominated by dot leaders (tables of contents; 88k occurrences
in 681 of 4,837 documents), Manhattan address fragments (`New York, N.Y. 100xx`, mastheads and
imprints), back-of-book index page runs (`, 101, 1…`), Library of Congress CIP blocks (284
documents) and Internet Archive item URLs (270). Only 6 of the top 500 exceed 8 tokens of
common extension, because an 8-token group merges every longer string that shares its prefix.

### Longer furniture, n-grams ≥ 16 tokens (`furniture-16.jsonl`, top 30 by document count)

| # | docs | len | text |
|---:|---:|---:|---|
| 1–2 | 269 | 16 | ` . . . . . . . .` (dot leaders; 64k occurrences) |
| 3 | 161 | 17 | `Kahle/Austin Foundation\n\nhttps://archive.org/details/` |
| 4 | 147 | 19 | ` with funding from\nKahle/Austin Foundation\n\nhttps://archive.org/` |
| 5–6 | 140 | 32 | ` . . . . . . . . . . . . . . . .` |
| 7–12 | 130–111 | 16–23 | `No part of this book may be reproduced in any form, by print, photoprint, …` (John Benjamins B.V. copyright notice; 130 documents) |
| 13 | 110 | 47 | `<\|end_of_text\|>mirrored file at http://SaturnianCosmology.Org/\nFor complete access to all the files of this collection\n\tsee http://SaturnianCosmology.org/search.php\n=====…` (document head banner: the match begins at the previous EOS) |
| 14–15 | 101 | 26–29 | `\nhttp://www.flash.net/~cjransom/\nhttp://www.knowledge.co.uk/` (Kronia/Velikovskian link footer) |
| 16–17 | 99 | 16 | `- - - - - - - - ` |
| 18 | 90 | 33 | ` John Benjamins B.V.\nNo part of this book may be reproduced in any form, by print, photoprint, microfilm, or` |
| 19, 24, 26 | 89–82 | 16–18 | `1984.\n\nLibrary of Congress Cataloging-in-Publication Data` (ANSI Z39.48-1984 paper notice + CIP) |
| 20, 28 | 84–80 | 16 | `.\n2.\n3.\n4.\n5.\n6.` (numbered blank lists) |
| 21, 27 | 83 | 17–18 | `Other suggested Web site URL's for more information about\nCatastrophics:` |
| 22 | 82 | 27 | `JSTOR is a not-for-profit service that helps scholars, researchers, and students discover, use, and build upon a wide` |
| 23, 29 | 82 | 18–19 | `PLEASE VISIT THE KRONIA COMMUNICATIONS WEBSITE` |
| 25 | 82 | 16 | `, without written permission from the publisher.\nJohn Benjamins Publishing Co.` |
| 30 | 79 | 18 | `\nhttp://www.grazian-archive.com/\nhttp://www.` |

### Longest shared blocks, n-grams ≥ 32 tokens (`furniture-32.jsonl`, selected from the top 30)

| docs | len | text |
|---:|---:|---|
| 110 | 47 | SaturnianCosmology.Org mirror banner (above) |
| 90 / 71 / 64 | 33–37 | John Benjamins "No part of this book may be reproduced … without written permission from the publisher." |
| 66 | 32 | `EDITOR:  Amy Acheson\nPUBLISHER:  Michael Armstrong\nLIST MANAGER:  Brian Stewart` (THOTH newsletter masthead) |
| 63 / 62 | 64+ | JSTOR open-collection notice: `… For more information about JSTOR, please contact support@jstor.org.\nThis item is openly available as part of an Open JSTOR Collection…` and the `Licenses: Creative Commons: Attribution-NonCommercial\nJSTOR is a not-for-profit service…` paragraph |
| 63 | 36 | `Reveal Digital is collaborating with JSTOR to digitize, preserve and extend access to Reveal Digital\n\nThis content downloaded from\n108.12.2` |
| 55 / 50 | 34–51 | `Ár nDraiocht Féin: A Druid Fellowship\nP.O. Box 17874, Tucson, AZ 85731-7874` (ADF newsletter footer) |
| 54 / 53 | 42–64+ | `John Benjamins Publishing Co. · P.O. Box 36224 · 1020 me Amsterdam · The Netherlands\nJohn Benjamins North America · P.O. Box 27519 · Philadelphia pa 19118-0519 · usa\n\n\x0c` |
| 54 / 53 | 64+ | 32+ dot leaders (12k occurrences) |
| 53 | 42 | `Under 18 Membership Waiver\nIf you are under the age of 18, you must have a parent or guardian sign this waiver…` |
| 51 / 50 | 51–64+ | Kronia link block: `http://www.knowledge.co.uk/sis/ … /velikovskian/ … bearfabrique.org … grazian-archive.com` |
| 50 | 33 | `The THOTH electronic newsletter is an outgrowth of scientific and\nscholarly discussions in the emerging field of astral\ncatastrophics.` |
| 50 | 32 | `LONDON: MILES\nPARIS: J. J. LEBEL\nAMSTERDAM: SIMON VINKENOOG\n` (underground-press masthead) |

### What this says about corpus-v1

- Furniture is concentrated in a few families: JSTOR/Reveal Digital scan notices (with a
  download IP and timestamp that the model has no business learning), Internet Archive
  digitization credits, publisher copyright/CIP blocks (John Benjamins alone: 130 documents),
  newsletter mastheads and link footers (THOTH/Kronia, ADF), and typographic runs (dot
  leaders, dash rules, numbered blank lists).
- The SaturnianCosmology banner is a document *head* in 110 documents; every one of those
  documents begins with the same 46 tokens after EOS, which is the worst case for a causal
  model that conditions on document starts.
- For memorization scoring, treat a span as furniture when its `occurrences` or
  `distinct_documents` is large, or when it appears in `furniture-*.jsonl`; for corpus-v2,
  the same lists are the natural input to a furniture-stripping pass at extraction time.

## Commands

```sh
# build (about 6 min background / ~2 min foreground, 7.6 GB peak)
.venv/bin/hghost-haunt build --tokens artifacts/tokenized/train.bin \
    --dataset artifacts/dataset --output artifacts/haunting-index

# provenance for a token sequence (.bin uint16, .npy, .json list, or a JSON literal)
.venv/bin/hghost-haunt query --index artifacts/haunting-index \
    --tokens artifacts/tokenized/validation.bin --count 2000 --min-tokens 16 --decode
.venv/bin/hghost-haunt query --index artifacts/haunting-index --text "…" --decode

# memorization report over generations ({"tokens": [...]} or {"text": "..."} per line)
.venv/bin/hghost-haunt scan --index artifacts/haunting-index \
    --generations generations.jsonl --output scan.jsonl --thresholds 8,16,32 --decode

# page furniture (cache the LCP array; later passes at other lengths take seconds)
.venv/bin/hghost-haunt furniture --index artifacts/haunting-index --min-tokens 8 \
    --min-documents 5 --max-tokens 64 --top 500 --lcp-cache /tmp/lcp64.npy --output furniture.jsonl

.venv/bin/pytest -q tests/test_haunt.py
```
