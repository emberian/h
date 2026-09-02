# Room mix: corpus v1.2 (v1 + multi-party conversation documents)

Written 2026-09-02, 00:30, after the first hour of `h` in Discord (`OVERNIGHT-2026-09-01.md`) and the
treatment plan (`research/resident-treatments.md`). The aim: a continued-pretraining stream that teaches
the 91M Falcon-H1 the *room as a genre*, in the exact format the ChapterX completions harness renders, not
an assistant. Tooling: `src/hghost/roommix.py` (`hghost-roommix`), tests in `tests/test_roommix.py`
(30 tests, fast). Nothing here was uploaded to Kaggle.

## The format

Every room document is rendered exactly as the harness renders a channel: lines of `<display name>: <text>`
separated by one blank line, one line per turn, no turn marker, EOS (id 11) after the document, nothing
else. `RoomDocument.render` is the single renderer; the tokenizer round-trips it exactly (checked on 240
documents: decode(encode(text)) == text, EOS only at document ends). The resident is `h`. Silence is the
absence of a line: the harness has no silence token, so none was invented. Where a source carries
speak/silent labels they go to the companion `room-decisions.jsonl` (per document: the role whose
decisions are recorded, its turn indices, and one `{after_turn, action}` per decision point).

A frame paragraph precedes the turns in a seeded 40% of documents (all sources except the pre-rendered
scenes): one of four frames chosen uniformly, verbatim half the time and otherwise with the date, the time
of day, or the sentence about the visitors varied. Frame (a) is the bot's live `system_prompt`
(`~/dev/chapterx/config/bots/h.yaml`) and appears in training in that exact form, line breaks included:

```
THE READING ROOM

An interview with h, the resident of the library, recorded on the evening of 1 September 2026. h has read
the whole collection and answers in a sentence or two, in the voice of what it has read. It does not
explain itself. The visitors speak as themselves.
```

The other three: "A room in the library, late. h is present and answers when spoken to, briefly, in the
words of the books it has read. The others are visitors."; "Transcript. h, the resident, and whoever
came by that night."; "Notes from the reading room. h speaks in short sentences taken from what it has
read; it stays quiet when it has nothing to add." The frame goes on documents whether or not `h` is in
them (as asked); for Gutenberg, Plato and the un-relabeled corpus blocks the frame therefore announces a
resident who does not speak in that room.

## Sources and licenses

| source | what | license | rendering |
| --- | --- | --- | --- |
| `corpus-native` | transcript-like blocks in the v1 **train** shards: runs of `Name: text` lines with 2+ recurring speakers, and `Q./A.` / `Question:/Answer:` runs | as corpus v1 (mixed/unknown); this text is already in v1 as prose, re-rendered deliberately for format learning | speaker labels normalized (ALL-CAPS to title case, initials kept); PDF line wraps joined; inline second speakers on one line split; `Q` -> `Interviewer`, `A` -> the name from an "interview with NAME" header when one precedes the block, else `Interviewee` |
| `corpus-native-h` | a second copy of the corpus blocks with a clear asking/answering structure (all Q./A. runs; two-speaker blocks where one side ends >= 50% of its turns with `?` and the other < 30%; letters answered by an `Editor`) | as above | answerer -> `h`; questioner keeps its printed name, or a handle from the coordinator's list (mira, dov, kestrel, ana, jules, tam, oriol, wren, sable, nico, pim, lux, quill, marrow, ash, vesna, hollis, bee) when the label is a role (`Interviewer`, `Reader`, `Q`, ...); provenance `relabeled_from`; decisions recorded for `h`; cap 5M tokens (not reached) |
| `gutenberg-dialog` | the Gutenberg Dialogue Dataset, English (Csáky & Recski 2021, arXiv 2004.12752), Hub copy `willwade/Gutenberg-dialog-en` (`train.txt` 1.38 GB streamed, never stored; `dev.txt` for the holdout) | text is Project Gutenberg public domain; the dataset packaging is MIT | the Hub copy is lowercased and NLTK-tokenized, so each utterance is detokenized (punctuation, contractions, quotes) and recased (sentence starts, `I`); proper nouns stay lowercase. Dialogues of 4-40 utterances sampled uniformly at rate 0.08 over the whole file (books are contiguous in it, so uniform sampling spreads across works; the copy has no book ids, so per-book caps were not possible). Speakers are invented per dialogue: two names alternating, or three names in 25% of dialogues of 6+ utterances with consecutive turns always by different speakers (the only structure the dataset asserts); one room in five uses lowercase handle-style names |
| `when2speak` | `duke-trust-lab/When2Speak` (arXiv 2605.05626): 16,000 GPT-4-Turbo multi-party conversations released as 8-turn sliding windows with a SPEAK/SILENT decision after each window; conversations rebuilt by chaining overlapping windows (train 13,955, validation 1,711 = holdout) | CC-BY-4.0 | `Speaker_k` -> invented names (mentions in text too); the agent (`[AGENT]` / `Assistant`) -> **`moderator`**, per the coordinator's decision: its interventions are advisory GPT-4 text and are not attributed to `h`; `h` is absent from these rooms. The 173,325 train decisions (22,684 speak / 150,641 silent) are recorded against the `moderator` role |
| `multilight` | MultiLIGHT (Wei et al. 2023, arXiv 2304.13835), the original `parlai_multilight.tar.gz` from parl.ai (sha256 `cbc20e4f...` as in ParlAI's `light_multiparty/build.py`): 10,917 three-character role-play episodes (train 10,204; valid+test 713 = holdout) | MIT (ParlAI) | the most talkative character -> `h`, the other two keep their character names (`gamekeeper`, `young boy`); personas and location descriptions are not rendered; decisions: one per turn boundary, `speak` before `h`'s turns, `silent` before the others' |
| `plato` | Jowett's Plato, 18 dialogues in direct speaker-labelled form from Project Gutenberg (Laws, Sophist, Philebus, Gorgias, Theaetetus, Alcibiades I, Cratylus, Statesman, Meno, Phaedrus, Laches, Euthyphro, Lesser Hippias, Ion, Crito, Euthydemus, Menexenus, Protagoras) through the same extractor (long turns allowed; blocks chunked at 100 turns) | Project Gutenberg public domain | `SOCRATES:` -> `Socrates:` etc.; the narrated dialogues (Republic, Symposium, Phaedo, Apology, Parmenides, Timaeus, Protagoras's frame) yield nothing by design |
| `scenes` | pre-rendered scene documents produced in parallel by the coordinator (`sources/scenes-rendered.jsonl`, `{"id","kind","text"}`), ingested verbatim by `assemble --rendered PATH --repeat 6` | project-generated | not framed again (they carry their own frame); each copy is its own document at its own insertion slot |

## Corpus-native extraction

`find_transcript_blocks` walks a document's lines: a speaker line (`^[A-Z][A-Za-z.'-]{0,24}( [A-Za-z.'-]+){0,2}:\s`, label 1-3 words, not a field or section word from a blocklist of ~350 such as `Phone`, `Date`, `Figure`, `Scene`) or a `Q`/`A` line starts a turn; following non-speaker lines continue it (PDF wraps), a paragraph that is one short line (page number, running head) is dropped, and the block ends after 12 continuation lines or 5 blank lines without a new speaker. A block is kept when it looks like speech between recurring speakers: >= 6 turns, 2-12 speakers with at least two recurring, singleton speakers <= 20% of turns, speaker changes >= 50% of consecutive pairs, median >= 4 words per turn, <= 30% of turns under 3 words, letters >= 78% of non-space characters, URL/phone/email in <= 10% of turns, leader dots in <= 5%. The first naive regex pass matched grove directories (`SD:`/`Phone:`/`Email:`), tables of contents (`Poem:`/`Song:`) and photo credits (`This page:`); the content filters remove those and keep the interviews (October, System, Talisman, The Realist, ISC Newsletter, call-centre transcripts, seminar Q&A). Residual noise: captions and running text that share a page with a transcript occasionally ride along inside a turn; OCR artifacts (`be¬ fore`) are the corpus's and stay.

## Token counts (including one EOS per document)

| source | train documents | train tokens | share of room mix | holdout documents | holdout tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| `corpus-native` | 1,573 | 1,229,650 | 2.9% | 59 | 44,784 |
| `corpus-native-h` | 490 | 327,637 | 0.8% | 15 | 9,761 |
| `gutenberg-dialog` | 96,771 | 26,384,792 | 62.9% | 600 | 162,644 |
| `multilight` | 10,204 | 5,699,765 | 13.6% | 666 | 380,029 |
| `plato` | 123 | 436,168 | 1.0% | 6 | 23,313 |
| `when2speak` | 13,955 | 7,844,046 | 18.7% | 666 | 379,966 |
| **total** | **123,116** | **41,922,058** | 100% | **2,012** | **1,000,497** |

- corpus-native: 1,632 blocks (1,400 `Name:` transcripts, 232 Q./A. runs) from 424 of the 4,837 v1 train documents, 1,248,637 tokens before the holdout split; the 15M cap was not approached, this is what the corpus contains.
- corpus-native-h: 505 of the 1,632 blocks had a clear questioner/answerer (232 Q./A. runs, 273 two-speaker transcripts); 290 questioners got a handle, the rest keep their printed name; 329,672 tokens (cap 5M).
- gutenberg-dialog: 2,279,927 dialogues in `train.txt`, 1,210,512 with 4-40 utterances, 96,771 sampled at rate 0.08 = 24,910,713 tokens; 600 dialogues from `dev.txt` (153,669 tokens) as holdout candidates.
- when2speak: 173,325 train windows -> 13,955 conversations, 245,405 turns, 22,684 speak / 150,641 silent decisions (7,634,151 tokens); validation 1,711 conversations (948,402 tokens) as holdout candidates.
- multilight: 10,204 train episodes, 303,468 turns (5,545,921 tokens); valid+test 713 episodes (396,495 tokens) as holdout candidates.
- plato: 129 documents from 18 dialogues, 10,779 turns, 457,922 tokens.
- scenes: `artifacts/roommix/sources/scenes-rendered.jsonl` did not exist when `assemble` ran, so the stream carries no scenes; re-run `assemble` and `build` (commands below) once it is in place.
- frames: 50,389 documents framed (40% target): a-varied 6,293, a-verbatim 6,139, b-varied 6,341, b-verbatim 6,468, c-varied 6,254, c-verbatim 6,346, d-varied 6,307, d-verbatim 6,241.
- holdout (`room-validation.bin`): 1,000,497 tokens in 2,012 documents, water-filled across sources toward the 1M target; 1,092 further holdout candidates were dropped (neither in train nor in the holdout) so the held-out split stays clean.

`room-decisions.jsonl` (documents with a recorded role, both streams):

| source | role | documents | speak decisions | silent decisions |
| --- | --- | ---: | ---: | ---: |
| `corpus-native-h` | `h` | 505 | 3,728 | 3,406 |
| `multilight` | `h` | 10,870 | 123,737 | 188,410 |
| `when2speak` | `moderator` | 14,621 | 23,802 | 157,995 |

## The stream: `artifacts/roommix/corpus-v1.2-room/`

- `train.bin`: 416,327,270 tokens, 832,654,540 bytes, sha256 `bb2e391549a7143b3c66ea16715cf57addb74e713f4f04702661dc8e3f90d56d`; v1's 374,405,212 tokens (4,837 documents) plus 41,922,058 room tokens in 123,116 documents = 10.07% of the stream, i.e. 11.2% of v1.
- weave: each room document draws a slot uniformly from {0..4837} (seed 12); 4,838 insertion groups; `verify_weave` re-read the file and found 374,405,212 v1 tokens byte-identical outside the insertions and every inserted block equal to its document (`ok: True`).
- `validation.bin`: unchanged from v1, 2,380,464 tokens, sha256 `07bce22a3de6101d4d946d1592a500c30a3790afffdecb8da6bd99777b985928` (matches v1's report).
- `validation-report.json`: v1 schema (`schema_version` 1, `ok` True), train split updated to 127,953 documents / 416,327,270 tokens with the new sha256, `derived_from.room_mix` describing the slice; `splits.train.sha256` and `splits.validation.sha256` are what `kaggle/tpu_h1jax_cpt/run.py` verifies.
- `room-validation.bin`: 1,000,497 tokens / 2,012 documents, sha256 `46633162ba844025a559a800237060030763a869a39548d999d06bc29b2c4516`, with `room-validation.jsonl` provenance; never in `train.bin`.
- `room-decisions.jsonl`, `manifest.json` (per-source counts, licenses, every insertion offset, hashes), `dataset-metadata.json` (Kaggle id `emberian64/hghost-curated-tokens-v1-2-room`, license field `unknown` because the bulk is v1), `README.md`.
- `artifacts/roommix/room-documents.bin` (the un-woven room slice, sha256 `de38d99a801e1cac5dba58446bfe85d9119d94a0cc801270cd77e29b66967f25`) and `room-documents.jsonl` (one row per document: id, source, license, offset, tokens, speakers, frame, provenance).

## Five corpus-native examples (first turns; source path and line span in the v1 shard text)

### `rat_palace/magazines/east_village_other/East Village Other v05n40 (1970).pdf` lines 7068-7215 (qa, 27 turns, id `2a2fb63d85c0c9a7da40`)

```
Interviewee: | like movies better than | do tv

Interviewer: Because you've got more time to

Interviewee: If you goof in movies you can just go back and take it over and in tv,

Interviewer: | see what you mean. There’s no

Interviewer: It’s hard to keep track?

Interviewee: Yes, it is. In fact, | don’t know who sells the ‘I hate Elvis’ buttons.
```

### `rat_palace/celephaïs/Carlile.Manual_of_Freemasonry.pdf` lines 13632-13715 (qa, 40 turns, id `cf2c54e4c83334639e9f`)

```
Interviewer: In what manner do we enter the conclave at the time of

Interviewee: On the triangle, and with the pass-word, Constantine.

Interviewer: Why are we conducted round the conclave twelve times when we are exalted to this degree ?

Interviewee: In commemoration of Constantine’s going twelve times round the plot of ground at Rome set apart for the church that he commanded to be built for the use of the Christians, when he carried upon his imperial shoulders twelve baskets of earth for the foundation, in memory of the twelve apo…

Interviewer: Is there not a second reason ?

Interviewee: In allusion to the twelve great pillars that support the Church of Rome, on which was delineated an ahstract of the Acts of the Apostles.
```

### `rat_palace/technology/computational_cybernetics_and_simulation.pdf` lines 14191-14233 (transcript, 6 turns, id `c74d6c4db14f53b302d0`)

```
Room: Ft. Lauderdale Time:3:45 - 5:30 pm WQ7: Health Care and Medical Informatics

Room: Cocoa Time:3:45 - 5:30 pm

Chair: Alianna J. Maren, Accurate Automation Corp., USA.

Co-Chair: Alan Stokes, Florida Institute of Technology, USA.

Chair: Vincent Ng, Hong Kong Polytechnic University, Hong 1. Simulation of Dynamical Systems Using the Multibody

Co-Chair: Minghui Du, University of Hong Kong, Hong Kong.
```

### `rat_palace/pubs/jon_benjamin/The Language of Outsourced Call Centers_ A corpus-based study of cross-cultural interaction.pdf` lines 11467-11511 (transcript, 17 turns, id `34f0c070efcfc9ebc872`)

```
Caller: Uh Milton M-I-L-T-O-N [not the caller’s real name but sounds like Milton]  The language of outsourced call centers

Agent: Ok, ok so uh, uh what seems to be the issue of this Mr. Milton?

Caller: Alrighty I am, oh we got uh got a uh we’re here just sending to uhm, uh the drainamino over to Kale

Agent: Uh-huh?

Caller: Uh which his old employee said uh check our system and found out that nothing is received by Marshalltown yet so I’m I’m just guessing here, I guess this is some kind of a warranty claim uh that this person was supposed to send the DVC up to your guys

Agent: Uh, that uh, let me check [interruption]
```

### `rat_palace/magazines/east_village_other/East Village Other v05n08 (1970).pdf` lines 6342-6425 (transcript, 14 turns, id `1edde0b6ebe3ed0c9ec9`)

```
THE Court: Mr. Hayden, also. down—he has sat down now. Mr. Marshal, see that Mr. Weinglass remains in his chair while the Court is rendering a decision on this motion made by Mr. Weinglass. my left, over there, where the door after | urged you. is.

Mr. Weinglass: Your Honor, This morning Mr. Rubin flagrantly that is not a fair characterization.

THE Court: Wilk you sit down!! | violated the order, got up and started referred to not infrequently by counsel as —the bathroom.” | have never sat in a case where lawyers mention that word as often. | wonder if you, Mr. Marshal, can keep that man quiet while | am speaking! | am trying to decide his…

Mr. Weinglass: He sat down, © bathroon”’ in this case, went out into on both occasions, Your Honor. | conferences in the hall, to other rooms in the courthouse, even to must object to that. another courtroom, which is contrary

Mr. Kunstler: | sat down on to the order of the Court, and both occasions.

THE Court: (red with rage) | because of that, yesterday | entered an order directing that if the mean right now, in this decision. defendants had to make use of toilet
```

### relabeled copy: `rat_palace/celephaïs/crowley/Book_4.part_i.pdf` lines 1913-1989 (Interviewer -> marrow, Interviewee -> h)

```
marrow: What is genius, and how is it produced?

h: Let us take several specimens of the species, and try to find some one thing common to all which is not found in other species.

marrow: Is there any such thing?

h: Yes: all geniuses have the habit of concentration of thought, and usually need long periods of solitude to acquire this habit. In particular, the greatest religious geniuses have all retired from the world at one time or another in their lives, and begun to preach immediately on their return.

marrow: Of what advantage is such a retirement? One would expect that a man who so acted would find himself on his return out of touch with his civilization, and in every way less capable than when he left.

h: But each claims, though in different language, to have gained in his absence some superhuman power.
```

## Caveats

- The corpus has ~1.2M tokens of native dialogue, not 15M; the mix leans on Gutenberg (about 60% of it) to reach the 40M target. Gutenberg's copy is lowercased and tokenized; recasing restores sentence starts and `I` but not proper nouns (`cornelia`, `olaf`), and the upstream extraction dropped some hyphens (`dayold`). Its register is 19th-century fiction, older than most of the library.
- When2Speak conversations are GPT-4 synthetic and unpunctuated ("Sure what's on your mind"); they carry the only explicit speak/silent labels, now attached to `moderator`, not `h`.
- The frame paragraphs announce `h` on rooms where `h` never speaks (Gutenberg, Plato, un-relabeled corpus blocks), by the coordinator's instruction to frame all sources. If the arm learns "h is announced and then silent", that is arguably the intended lesson about staying quiet; if it instead learns to ignore the frame, restrict framing to documents with `h` (`--frame-fraction` applies uniformly today; a per-source rule is a small change in `run_assemble`).
- Holdout candidates beyond the ~1M target are dropped rather than trained on, so When2Speak's validation conversations and MultiLIGHT's test episodes are mostly unused; `room-validation.jsonl` says which made it.
- Known residual noise in `corpus-native`: 7 blocks (~1K tokens) are conference programs whose `Room:` / `Chair:` / `Co-Chair:` lines pass the speech filters (one is shown among the examples on purpose); a few OCR quirks (`|` for `I`, `be¬ fore`) are the corpus's own. The label blocklist was left as it ran so that the commands above reproduce the artifacts exactly; `Room`, `Chair`, `Co-Chair` belong in it for the next extraction.
- `corpus-native` re-renders text already in v1: those tokens now appear twice in the stream (as prose and as a room), deliberately.

## Commands (as run, from `/Users/ember/dev/h`, `.venv/bin/hghost-roommix`)

```
hghost-roommix extract-corpus --output artifacts/roommix/sources/corpus-native.jsonl.gz          # 3 min
hghost-roommix relabel --input artifacts/roommix/sources/corpus-native.jsonl.gz \
    --output artifacts/roommix/sources/corpus-native-h.jsonl.gz
hghost-roommix gutenberg --rate 0.08 --holdout-rate 0.01 --holdout-limit 600 \
    --output artifacts/roommix/sources/gutenberg-dialog.jsonl.gz                                  # 7 min, streams 1.38 GB
hghost-roommix rooms --raw-dir <scratch>/roommix-raw/rooms \
    --output artifacts/roommix/sources/rooms-with-decisions.jsonl.gz                              # downloads deleted after
hghost-roommix plato --raw-dir <scratch>/roommix-raw/plato --output artifacts/roommix/sources/plato.jsonl.gz
hghost-roommix assemble artifacts/roommix/sources/corpus-native.jsonl.gz \
    artifacts/roommix/sources/corpus-native-h.jsonl.gz artifacts/roommix/sources/gutenberg-dialog.jsonl.gz \
    artifacts/roommix/sources/rooms-with-decisions.jsonl.gz artifacts/roommix/sources/plato.jsonl.gz \
    --rendered artifacts/roommix/sources/scenes-rendered.jsonl --repeat 6 --output artifacts/roommix
hghost-roommix build --rooms artifacts/roommix --output artifacts/roommix/corpus-v1.2-room
```

All seeds default to 0 (`build` uses 12 for the insertion slots); every command writes a `*.summary.json`
or manifest beside its output. `assemble` takes the source files as they are, so re-running only
`assemble` and `build` (the last two commands) picks up `scenes-rendered.jsonl` when it exists; the room
slice and the woven stream get new hashes, recorded in `room-manifest.json` and `manifest.json`.
`tests/test_roommix.py` covers the rendering format, the `h`/`moderator` relabeling, chaining of
When2Speak windows, extraction on a synthetic shard, detokenization, the frames, the pre-rendered source,
holdout water-filling, and the weave preserving v1 bytes on a tiny stream.
