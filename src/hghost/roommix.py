"""Room mix: multi-party conversation documents woven into corpus v1 (corpus v1.2).

The resident `h` lives in a base model and is rendered by a completions harness that
prints a transcript: lines of ``<display name>: <text>`` separated by one blank line
(``research/resident-treatments.md``, ``OVERNIGHT-2026-09-01.md``). A continued-pretraining
arm teaches it the *room as a genre* by mixing room-shaped documents in exactly that
format into the sealed v1 token stream. Nothing here is instruction data: every document
is a transcript, and silence is represented by nothing (a participant that stays silent has
no line), because the harness has no silence token.

Sources, each rendered by ``RoomDocument.render``:

* ``extract-corpus``: transcript-like blocks already in corpus v1 (``Name: text`` runs
  with several speakers, ``Q./A.`` interview runs), re-rendered as rooms;
* ``gutenberg``: the Gutenberg Dialogue Dataset (Csáky & Recski 2021), detokenized and
  recased, with invented consistent speaker names per dialogue;
* ``rooms``: When2Speak (CC-BY-4.0; its agent relabelled ``moderator``, so ``h`` is absent)
  and MultiLIGHT (ParlAI, MIT; its most talkative character relabelled ``h``), with the
  speak/silent decisions recorded against that role in ``room-decisions.jsonl``;
* ``plato``: Jowett's Plato from Project Gutenberg, through the corpus extractor;
* ``relabel``: a second copy of corpus-native interviews with the answering party as
  ``h`` and the questioner named plainly;
* ``assemble``: prepends a frame paragraph (the harness's own, among others) to a seeded
  share of documents, ingests pre-rendered scenes, tokenizes every room document into
  ``room-documents.bin`` (EOS after each) plus provenance, and a held-out
  ``room-validation.bin``;
* ``build``: weaves the room documents into the v1 train stream with the belief-geometry
  weave (v1 bytes verified intact) and writes the Kaggle layout for corpus v1.2.
"""

from __future__ import annotations

import argparse
import dataclasses
import gzip
import hashlib
import json
import re
import shutil
import statistics
import sys
import tarfile
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np

from hghost.beliefgeo import (
    DEFAULT_EOS_TOKEN_ID,
    derive_validation_report,
    document_bounds,
    plan_insertions,
    read_json,
    sha256_file,
    verify_weave,
    weave_stream,
    write_json,
)

RESIDENT = "h"
MODERATOR = "moderator"
TURN_SEPARATOR = "\n\n"
DEFAULT_TOKENIZER = Path("kaggle/base_model_dataset_public/tokenizer.json")
DEFAULT_DATASET = Path("artifacts/dataset")
DEFAULT_OUTPUT = Path("artifacts/roommix")
DEFAULT_TRAIN_BIN = Path("artifacts/tokenized/train.bin")
DEFAULT_VOCAB_SIZE = 32768
KAGGLE_DATASET_ID = "emberian64/hghost-curated-tokens-v1-2-room"
KAGGLE_DATASET_TITLE = "H Ghost corpus v1.2 + room mix"

LICENSES = {
    "corpus-native": (
        "as corpus v1 (mixed or unknown source-document licensing); room-format "
        "re-rendering of text already in the v1 train split"
    ),
    "gutenberg-dialog": (
        "Project Gutenberg public-domain text; dataset packaging MIT "
        "(Csáky & Recski 2021, arXiv 2004.12752; Hub copy willwade/Gutenberg-dialog-en)"
    ),
    "when2speak": "CC-BY-4.0 (duke-trust-lab/When2Speak, arXiv 2605.05626)",
    "multilight": (
        "MIT (ParlAI light_multiparty, parl.ai/downloads/projects/multilight; "
        "Wei et al. 2023, arXiv 2304.13835)"
    ),
    "plato": "Project Gutenberg public-domain text (Benjamin Jowett's translations)",
    "corpus-native-h": (
        "as corpus v1 (mixed or unknown source-document licensing); interview blocks from "
        "the v1 train split with the answering party relabelled h"
    ),
    "scenes": "project-generated scenes (pre-rendered by the coordinator; see the source file)",
}

# Handles for questioners whose printed label is a role rather than a name.
QUESTIONER_HANDLES = (
    "mira dov kestrel ana jules tam oriol wren sable nico pim lux quill marrow ash vesna "
    "hollis bee"
).split()
ROLE_LABELS = {
    "interviewer", "interviewee", "q", "a", "reader", "caller", "participant", "student",
    "questioner", "audience", "voice", "question", "answer", "editor", "editors", "ed",
    "eds", "the editor", "letter", "correspondent", "anon", "anonymous", "member",
    "visitor", "guest", "host", "moderator", "chair", "speaker", "questions", "answers",
}
EDITOR_LABELS = {"editor", "editors", "ed", "eds", "the editor", "the editors"}

# Frame paragraphs prepended to a random share of room documents. Frame (a) is the bot's
# live prompt and must appear verbatim (line breaks included); the varied forms change
# only the date, the time of day, and the sentence about the visitors.
FRAMES = {
    "a": (
        "THE READING ROOM\n\nAn interview with h, the resident of the library, recorded on "
        "the evening of 1 September 2026. h has read\nthe whole collection and answers in a "
        "sentence or two, in the voice of what it has read. It does not\nexplain itself. The "
        "visitors speak as themselves."
    ),
    "b": (
        "A room in the library, late. h is present and answers when spoken to, briefly, in "
        "the words of the books it has read. The others are visitors."
    ),
    "c": "Transcript. h, the resident, and whoever came by that night.",
    "d": (
        "Notes from the reading room. h speaks in short sentences taken from what it has "
        "read; it stays quiet when it has nothing to add."
    ),
}
FRAME_VARIANTS = {
    "a": [
        (
            "the evening of 1 September 2026",
            lambda rng: "the {} of {} {} {}".format(
                rng.choice(["morning", "afternoon", "evening", "night"]),
                int(rng.integers(1, 29)),
                rng.choice(
                    "January February March April May June July August September October "
                    "November December".split()
                ),
                int(rng.choice([2025, 2026, 2027])),
            ),
        ),
        (
            "The visitors speak as themselves.",
            lambda rng: str(
                rng.choice(
                    [
                        "The visitors speak as themselves.",
                        "The visitors speak for themselves.",
                        "Whoever came by speaks as themselves.",
                        "The others are visitors, and speak as themselves.",
                    ]
                )
            ),
        ),
    ],
    "b": [
        (
            "late",
            lambda rng: str(
                rng.choice(["late", "early", "in the afternoon", "after closing", "before dawn"])
            ),
        ),
        (
            "The others are visitors.",
            lambda rng: str(
                rng.choice(
                    [
                        "The others are visitors.",
                        "The others came by.",
                        "The visitors speak as themselves.",
                        "Whoever else is there is a visitor.",
                    ]
                )
            ),
        ),
    ],
    "c": [
        (
            "that night",
            lambda rng: str(
                rng.choice(
                    ["that night", "that afternoon", "that evening", "that morning", "after hours"]
                )
            ),
        )
    ],
    "d": [
        (
            "short sentences",
            lambda rng: str(rng.choice(["short sentences", "a sentence or two", "brief sentences"])),
        ),
        (
            "when it has nothing to add",
            lambda rng: str(
                rng.choice(
                    [
                        "when it has nothing to add",
                        "when there is nothing to add",
                        "when no one is speaking to it",
                    ]
                )
            ),
        ),
    ],
}


def make_frame(rng: np.random.Generator) -> tuple[str, bool, str]:
    """``(key, varied, text)``: a frame chosen uniformly, verbatim half of the time."""

    key = str(rng.choice(sorted(FRAMES)))
    text = FRAMES[key]
    varied = bool(rng.random() < 0.5)
    if varied:
        for original, replacement in FRAME_VARIANTS[key]:
            text = text.replace(original, replacement(rng), 1)
    return key, varied, text

GUTENBERG_DIALOG_REPO = "willwade/Gutenberg-dialog-en"
WHEN2SPEAK_REPO = "duke-trust-lab/When2Speak"
MULTILIGHT_URL = "http://parl.ai/downloads/projects/multilight/parlai_multilight.tar.gz"
MULTILIGHT_SHA256 = "cbc20e4fa7a551c0efec4a4129e75335d3f3586797d6f767e320403079f4a6b2"

# Jowett's dialogues in direct (speaker-labelled) form on Project Gutenberg. The narrated
# ones (Republic, Symposium, Protagoras, Phaedo, Apology, Parmenides, Timaeus) yield no
# transcript blocks and are omitted.
PLATO_GUTENBERG_IDS = {
    1584: "Laches",
    1591: "Protagoras",
    1598: "Euthydemus",
    1616: "Cratylus",
    1635: "Ion",
    1636: "Phaedrus",
    1642: "Euthyphro",
    1643: "Meno",
    1657: "Crito",
    1672: "Gorgias",
    1673: "Lesser Hippias",
    1676: "Alcibiades I",
    1682: "Menexenus",
    1726: "Theaetetus",
    1735: "Sophist",
    1738: "Statesman",
    1744: "Philebus",
    1750: "Laws",
}

NAME_POOL = (
    "Ada Amos Anya Aris Asha Basil Bea Cal Cleo Dara Dev Dot Eli Elif Esme Ezra Fen Finn "
    "Gus Hana Ines Ira Isla Ivo Jade Jonah Juno Kai Kit Lena Leo Lior Luca Mara Milo Mina "
    "Nell Nico Nina Noor Oona Oren Otis Pia Quinn Ravi Remy Rosa Rune Sam Sana Sol Tam Teo "
    "Tess Theo Uma Vera Wren Yara Yuki Zed Zoe Agnes Alma Arlo Bram Cora Cyrus Dell Edie "
    "Elke Enzo Etta Faye Greta Hugo Ida Inge Jem June Kim Lars Liv Lou Mae Max Moss Nadia "
    "Nour Olive Owen Pilar Rafa Ren Rhea Rory Sasha Silas Suki Tova Ulla Vik Willa Xan "
    "Yusuf Zia Marguerite Ignatius Wilhelmina Bartholomew Persephone Cordelia Thaddeus "
    "Anselm Beatrix Constance Desmond Eloise Florian Gwendolyn Horatio Imogen Jasper "
    "Leopold Matilda Nikolai Ottoline Percival Rosalind Sebastian Theodora Ursula Vivian"
).split()


def log(message: str) -> None:
    print(f"[roommix] {message}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------------------
# Room documents
# --------------------------------------------------------------------------------------

_WHITESPACE = re.compile(r"\s+")


def clean_turn_text(text: str) -> str:
    """One line per turn: collapse all whitespace (including newlines) to single spaces."""

    return _WHITESPACE.sub(" ", text).strip()


def clean_speaker(name: str) -> str:
    name = _WHITESPACE.sub(" ", name).strip().rstrip(":").strip()
    if not name or ":" in name:
        raise ValueError(f"speaker name must be nonempty and colon-free: {name!r}")
    return name


RENDERED_TURN = re.compile(r"^([^:\n]{1,60}): (.*)$")


def parse_rendered_turns(text: str) -> list[tuple[str, str]]:
    """``(speaker, text)`` for the ``name: text`` lines of a pre-rendered document."""

    turns = []
    for line in text.split("\n"):
        match = RENDERED_TURN.match(line)
        if match:
            turns.append((match.group(1), match.group(2)))
    return turns


@dataclasses.dataclass
class RoomDocument:
    """A room: ordered turns of ``(speaker, text)`` rendered in the harness format.

    ``frame`` is an optional paragraph placed before the turns (then a blank line).
    ``text`` marks a pre-rendered document (the scenes source): it is used verbatim and
    ``turns`` are parsed from it for bookkeeping only.
    """

    id: str
    source: str
    turns: list[tuple[str, str]]
    provenance: dict = dataclasses.field(default_factory=dict)
    split: str = "train"
    h_participant: str | None = None
    decisions: list[dict] | None = None
    frame: str | None = None
    text: str | None = None
    decision_role: str | None = None

    def __post_init__(self) -> None:
        if self.h_participant is not None and self.decisions is None:
            self.decisions = []
        if self.decision_role is None and self.h_participant is not None:
            self.decision_role = RESIDENT
        if self.text is not None:
            self.text = self.text.rstrip("\n")
            if not self.text.strip():
                raise ValueError(f"room document {self.id} has no text")
            self.turns = parse_rendered_turns(self.text)
            return
        cleaned = []
        for speaker, text in self.turns:
            text = clean_turn_text(text)
            if text:
                cleaned.append((clean_speaker(speaker), text))
        if not cleaned:
            raise ValueError(f"room document {self.id} has no turns")
        self.turns = cleaned
        if self.frame is not None and not self.frame.strip():
            raise ValueError(f"room document {self.id} has an empty frame")

    def render(self) -> str:
        if self.text is not None:
            return self.text
        body = TURN_SEPARATOR.join(f"{speaker}: {text}" for speaker, text in self.turns)
        if self.frame:
            return f"{self.frame}{TURN_SEPARATOR}{body}"
        return body

    def speakers(self) -> list[str]:
        return list(dict.fromkeys(speaker for speaker, _ in self.turns))

    @property
    def license(self) -> str:
        return LICENSES[self.source]

    def to_record(self) -> dict:
        record = {
            "id": self.id,
            "source": self.source,
            "license": self.license,
            "split": self.split,
            "provenance": self.provenance,
            "turns": [list(turn) for turn in self.turns],
        }
        if self.h_participant is not None:
            record["h_participant"] = self.h_participant
            record["decision_role"] = self.decision_role
            record["decisions"] = self.decisions or []
        if self.frame is not None:
            record["frame"] = self.frame
        if self.text is not None:
            record["text"] = self.text
        return record

    @classmethod
    def from_record(cls, record: dict) -> "RoomDocument":
        return cls(
            id=record["id"],
            source=record["source"],
            turns=[tuple(turn) for turn in record["turns"]],
            provenance=record.get("provenance", {}),
            split=record.get("split", "train"),
            h_participant=record.get("h_participant"),
            decisions=record.get("decisions"),
            frame=record.get("frame"),
            text=record.get("text"),
            decision_role=record.get("decision_role"),
        )


def document_id(source: str, *parts: object) -> str:
    value = "\0".join([source, *map(str, parts)]).encode("utf-8", "surrogatepass")
    return hashlib.sha256(value).hexdigest()[:20]


def invent_names(count: int, rng: np.random.Generator) -> list[str]:
    """``count`` distinct real-looking short names; one room in five uses handle case."""

    names = [NAME_POOL[i] for i in rng.choice(len(NAME_POOL), size=count, replace=False)]
    if rng.random() < 0.2:
        names = [name.lower() for name in names]
    return names


def write_records(path: Path, documents: Iterable[RoomDocument]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "wt", encoding="utf-8") as handle:
        for document in documents:
            handle.write(json.dumps(document.to_record(), ensure_ascii=False) + "\n")
            count += 1
    return count


def read_records(path: Path | str) -> Iterator[RoomDocument]:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield RoomDocument.from_record(json.loads(line))


def read_rendered(path: Path, repeat: int = 1) -> Iterator[RoomDocument]:
    """Pre-rendered documents (``{"id", "kind", "text"}`` lines), each ``repeat`` times."""

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            for copy in range(max(1, repeat)):
                yield RoomDocument(
                    id=document_id("scenes", record["id"], copy),
                    source="scenes",
                    turns=[],
                    text=record["text"],
                    provenance={
                        "file": path.name,
                        "scene_id": record["id"],
                        "kind": record.get("kind"),
                        "repeat": copy,
                    },
                    h_participant=RESIDENT if any(s == RESIDENT for s, _ in parse_rendered_turns(record["text"])) else None,
                )


def assign_holdout(rng: np.random.Generator, fraction: float) -> str:
    return "holdout" if fraction > 0 and rng.random() < fraction else "train"


# --------------------------------------------------------------------------------------
# Corpus-native transcript blocks
# --------------------------------------------------------------------------------------

SPEAKER_LINE = re.compile(
    r"^([A-Z][A-Za-z.'\-]{0,24}(?: [A-Za-z.'\-]{1,24}){0,2}):[ \t]+(\S.*)$"
)
QA_LINE = re.compile(r"^(Q|A|QUESTION|ANSWER|Question|Answer)\s*[.:]\s+(\S.*)$")
INTERVIEW_WITH = re.compile(
    r"(?i:interview|conversation|dialogue|talk|talks|talking|speaks|chat)\s+(?i:with)\s+"
    r"((?:[A-Z][\w.'\-]+)(?:\s+[A-Z][\w.'\-]+){0,3})"
)
INTERVIEWED_BY = re.compile(
    r"((?:[A-Z][\w.'\-]+)(?:\s+[A-Z][\w.'\-]+){0,3})\s+(?i:interviewed by)"
)
URLISH = re.compile(
    r"https?://|www\.|\w@\w+\.\w|\(\d{3}\)\s*\d{3}|\b\d{3}[-. ]\d{3,4}[-. ]\d{4}\b"
)
LEADER_DOTS = re.compile(r"(?:\.[ \t]?){4,}")
FURNITURE_LINE = re.compile(r"^(?:(?i:page|p\.|pp\.)\s*)?[\d\W_]*$")
PARTICLES = {"de", "van", "von", "der", "del", "di", "da", "la", "le", "of", "the", "and"}
LABEL_BLOCKLIST = {
    word.lower()
    for word in (
        "Phone Fax Tel Telephone Email E-mail Web Website URL Address Contact Date Time "
        "Location Venue Place Where When Cost Price Fee Fees Deadline Note Notes NB Source "
        "Sources Title Author Authors Editor Editors Publisher Published Printed Copyright "
        "ISBN ISSN Subject Re To From Cc Bcc Figure Fig Figures Table Tables Plate Chapter "
        "Part Section Volume Vol Issue No Number Page Pages Poem Poetry Song Songs Art "
        "Story Stories Series Opinion Review Reviews Example Examples Warning Caution "
        "Summary Abstract Keywords Translation Remarks Result Results Method Methods "
        "Materials Reference References Bibliography Acknowledgements Hint Step Steps Tip "
        "Tips Key Total Name Names Members Membership Newsletter Areas Photo Photos "
        "Photograph Photographs Caption Credit Credits Description Definition Etymology "
        "Synonyms Usage Meaning Pronunciation Origin Type Category Genre Format Length "
        "Duration Rating Level Status Version Model Item Items Quantity Amount Sum Balance "
        "Payment Invoice Account City State Country Region Street Road Office Department "
        "Program Programme Project Plan Schedule Agenda Event Events Meeting Conference "
        "Workshop Seminar Lecture Course Session Term Year Month Week Day Morning Afternoon "
        "Evening Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February "
        "March April May June July August September October November December Website "
        "Ingredients Directions Serves Yield Preparation Equipment Materials Dimensions Size "
        "Weight Color Colour Available Order Postage Shipping Delivery Solution Answer Question "
        "Exercise Exercises Problem Problems Proof Theorem Lemma Corollary Definition "
        "Conclusion Introduction Preface Foreword Appendix Index Glossary Contents Errata "
        "Update Correction Corrections Erratum Attention Important Reminder Notice Thanks "
        "Moral Motto Text Texts Verse Verses Hymn Psalm Reading Readings Prayer Response "
        "Chorus Refrain Translator Illustrator Illustrations Cover Design Layout Typesetting "
        "Printing Distribution Subscription Subscriptions Advertising Circulation Rates "
        "Grove Organizer Senior Druid This page Opposite page Previous page Next page Left "
        "Right Above Below Top Bottom Center Centre Inset Detail Details Opposite Overleaf "
        "Frontispiece Plates Map Maps Chart Charts Diagram Diagrams Scheme Schema Formula "
        "Ref Refs See Cf Compare Contrast Viz Ibid Op Loc Id Idem"
    ).split()
} | {
    "e-mail", "web site", "home phone", "work phone", "book review", "p.s.", "ps",
    "scene", "setting", "stage", "persons", "characters", "cast", "enter", "exit", "exeunt",
}


def plausible_label(label: str) -> bool:
    """A 1-3 word capitalized name that is not a field or section label."""

    words = label.split(" ")
    if not 1 <= len(words) <= 3:
        return False
    lowered = label.lower().rstrip(".")
    if lowered in LABEL_BLOCKLIST or words[-1].lower().rstrip(".") in LABEL_BLOCKLIST:
        return False
    for word in words:
        if not any(character.isalpha() for character in word):
            return False
        if word.lower() in PARTICLES:
            continue
        if not (word[0].isupper() or word.isupper()):
            return False
    return True


_INITIALS = re.compile(r"^(?:[A-Z]\.)+[A-Z]?\.?$")


def normalize_label(label: str) -> str:
    """Collapse spaces; render ALL-CAPS labels in title case (``SOCRATES`` -> ``Socrates``)."""

    label = _WHITESPACE.sub(" ", label).strip().rstrip(".:").strip()
    if label.isupper() and len(label) > 1:
        words = []
        for word in label.split(" "):
            if _INITIALS.match(word) or (len(word) <= 3 and "." not in word):
                words.append(word)
            elif word.lower() in PARTICLES:
                words.append(word.lower())
            else:
                words.append(
                    "-".join(
                        piece[:1] + piece[1:].lower() for piece in word.split("-")
                    )
                )
        label = " ".join(words)
    return label


def interviewee_name(context_lines: Sequence[str]) -> str | None:
    """The interviewee named by an ``interview with NAME`` header, if one precedes the block."""

    context = " ".join(line.strip() for line in context_lines if line.strip())
    for pattern in (INTERVIEW_WITH, INTERVIEWED_BY):
        found = None
        for match in pattern.finditer(context):
            found = match.group(1)
        if found:
            name = normalize_label(found).rstrip(",;.")
            if 1 <= len(name.split()) <= 4:
                return name
    return None


@dataclasses.dataclass
class Block:
    kind: str
    turns: list[list[str]]
    start: int
    end: int
    pending: list[str] = dataclasses.field(default_factory=list)
    gap: int = 0
    blank: int = 0
    paragraph_break: bool = False

    def flush(self, whole: bool) -> None:
        """Append pending continuation lines to the last turn.

        ``whole`` appends every pending line (a new speaker line followed, so the text in
        between belongs to the previous turn); otherwise only the first paragraph is kept,
        because prose after a blank line at the end of a block is usually the document
        resuming rather than the last speaker continuing.
        """

        contiguous = bool(self.pending) and self.pending[0] is not None
        paragraphs: list[list[str]] = [[]]
        for line in self.pending:
            if line is None:
                if paragraphs[-1]:
                    paragraphs.append([])
            else:
                paragraphs[-1].append(line)
        # A paragraph that is one short line (running head, page number, caption
        # fragment) is furniture, not speech.
        paragraphs = [p for p in paragraphs if p and not (len(p) == 1 and len(p[0].split()) < 4)]
        if not whole:
            paragraphs = paragraphs[:1] if contiguous else []
        text = " ".join(line for paragraph in paragraphs for line in paragraph)
        if text:
            self.turns[-1][1] += " " + text
        self.pending = []


def turn_features(text: str) -> dict:
    words = text.split()
    nonspace = sum(not character.isspace() for character in text)
    letters = sum(character.isalpha() for character in text)
    return {
        "words": len(words),
        "letters": letters / max(1, nonspace),
        "urlish": bool(URLISH.search(text)),
        "leader": bool(LEADER_DOTS.search(text)),
    }


def block_statistics(turns: Sequence[Sequence[str]]) -> dict:
    speakers = Counter(speaker for speaker, _ in turns)
    features = [turn_features(text) for _, text in turns]
    changes = sum(1 for a, b in zip(turns, turns[1:]) if a[0] != b[0])
    singleton_turns = sum(count for count in speakers.values() if count == 1)
    return {
        "turns": len(turns),
        "speakers": len(speakers),
        "recurring_speakers": sum(1 for count in speakers.values() if count >= 2),
        "singleton_fraction": singleton_turns / len(turns),
        "alternation": changes / max(1, len(turns) - 1),
        "median_words": statistics.median(item["words"] for item in features),
        "short_fraction": sum(item["words"] < 3 for item in features) / len(turns),
        "letters": statistics.fmean(item["letters"] for item in features),
        "urlish_fraction": sum(item["urlish"] for item in features) / len(turns),
        "leader_fraction": sum(item["leader"] for item in features) / len(turns),
    }


def block_passes(stats: dict, *, min_turns: int, max_speakers: int) -> bool:
    return (
        stats["turns"] >= min_turns
        and 2 <= stats["speakers"] <= max_speakers
        and stats["recurring_speakers"] >= 2
        and stats["singleton_fraction"] <= 0.2
        and stats["alternation"] >= 0.5
        and stats["median_words"] >= 4
        and stats["short_fraction"] <= 0.3
        and stats["letters"] >= 0.78
        and stats["urlish_fraction"] <= 0.1
        and stats["leader_fraction"] <= 0.05
    )


def find_transcript_blocks(
    text: str,
    *,
    min_turns: int = 6,
    max_speakers: int = 12,
    max_gap_lines: int = 12,
    max_blank_lines: int = 5,
) -> list[dict]:
    """Transcript-like blocks in ``text``: ``Name: text`` runs and ``Q./A.`` runs.

    A speaker line starts a turn; following non-speaker lines continue it (PDF text wraps
    turns over several lines) until ``max_gap_lines`` of them or ``max_blank_lines`` blank
    lines pass without a new speaker line, which ends the block. Blocks are kept when they
    look like speech between recurring speakers (``block_passes``). Each result carries
    ``kind`` (``transcript`` or ``qa``), ``turns`` as ``[speaker, text]`` pairs with labels
    normalized (``Q``/``A`` become ``Interviewer`` and the named interviewee if a header
    names one, else ``Interviewee``), the line span, and the statistics used to keep it.
    """

    lines = text.replace("\x0c", "\n").split("\n")
    blocks: list[Block] = []
    current: Block | None = None

    def close() -> None:
        nonlocal current
        if current is not None:
            current.flush(whole=False)
            blocks.append(current)
            current = None

    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            if current is not None:
                current.blank += 1
                if not current.pending or current.pending[-1] is not None:
                    current.pending.append(None)
                if current.blank > max_blank_lines:
                    close()
            continue
        kind = label = body = None
        qa = QA_LINE.match(line)
        if qa:
            kind, label, body = "qa", qa.group(1)[0].upper(), qa.group(2)
        else:
            speaker = SPEAKER_LINE.match(line)
            if speaker and plausible_label(speaker.group(1)):
                kind = "transcript"
                label, body = normalize_label(speaker.group(1)), speaker.group(2)
        if kind is not None:
            if current is not None and current.kind != kind:
                close()
            if current is None:
                current = Block(kind=kind, turns=[], start=index, end=index)
            else:
                current.flush(whole=True)
            current.turns.append([label, body])
            current.end = index
            current.gap = current.blank = 0
            continue
        if current is None:
            continue
        current.gap += 1
        current.blank = 0
        if current.gap > max_gap_lines:
            close()
            continue
        if FURNITURE_LINE.match(line):
            continue
        current.pending.append(line)
        current.end = index
    close()

    results = []
    for block in blocks:
        turns = [[speaker, clean_turn_text(text)] for speaker, text in block.turns]
        turns = [turn for turn in turns if turn[1]]
        if block.kind == "transcript":
            turns = split_inline_speakers(turns)
        if block.kind == "qa":
            turns = split_inline_qa(turns)
            answers = Counter(speaker for speaker, _ in turns)
            if answers["Q"] < 2 or answers["A"] < 2:
                continue
            name = interviewee_name(lines[max(0, block.start - 80) : block.start])
            mapping = {"Q": "Interviewer", "A": name or "Interviewee"}
            if mapping["A"].lower() == "interviewer":
                mapping["A"] = "Interviewee"
            turns = [[mapping[speaker], text] for speaker, text in turns]
        if len(turns) < min_turns:
            continue
        stats = block_statistics(turns)
        if not block_passes(stats, min_turns=min_turns, max_speakers=max_speakers):
            continue
        results.append(
            {
                "kind": block.kind,
                "turns": turns,
                "lines": [block.start, block.end],
                "statistics": stats,
            }
        )
    return results


def split_inline_speakers(turns: list[list[str]]) -> list[list[str]]:
    """Split turns where a known speaker's label appears mid-line (``... goal? DD: I ...``).

    PDF extraction sometimes runs two turns onto one line; only labels already seen as
    line-initial speakers in the block (in their printed or upper-case form) count.
    """

    labels = {speaker for speaker, _ in turns}
    forms = sorted(labels | {label.upper() for label in labels}, key=len, reverse=True)
    pattern = re.compile(
        r"(?<=[.!?\"'’”)\]…])\s+(" + "|".join(re.escape(form) for form in forms) + r"):\s+(?=\S)"
    )
    result = []
    for speaker, text in turns:
        pieces = pattern.split(text)
        result.append([speaker, pieces[0].strip()])
        for label, rest in zip(pieces[1::2], pieces[2::2]):
            label = normalize_label(label)
            if rest.strip():
                result.append([label, rest.strip()])
    return [turn for turn in result if turn[1]]


INLINE_QA_WORD = re.compile(r"\s*-{0,2}\s*\b(Question|Answer|QUESTION|ANSWER)\s*[.:]\s+(?=\S)")
INLINE_QA_LETTER = re.compile(r"(?<=[.!?\u2026\"'\u201d\u2019)])\s+-{0,2}\s*(Q|A)[.:]\s+(?=\S)")


def split_inline_qa(turns: list[list[str]]) -> list[list[str]]:
    """Split ``Q``/``A`` turns at inline ``Question:`` / ``-Answer:`` / ``A.`` labels.

    Some interviews print the answer on the question's line (``Question: ... --Answer:
    ...``); the labels become new turns with the single-letter ``Q``/``A`` labels the
    block uses.
    """

    result = []
    for speaker, text in turns:
        pieces = INLINE_QA_WORD.split(text)
        expanded = [pieces[0]]
        for label, rest in zip(pieces[1::2], pieces[2::2]):
            expanded.append(label[0].upper())
            expanded.append(rest)
        # Then the bare Q./A. forms, only after sentence-final punctuation.
        queue = [(speaker, expanded[0])] + [
            (expanded[i], expanded[i + 1]) for i in range(1, len(expanded) - 1, 2)
        ]
        for who, chunk in queue:
            parts = INLINE_QA_LETTER.split(chunk)
            result.append([who, parts[0].strip()])
            for label, rest in zip(parts[1::2], parts[2::2]):
                result.append([label.upper(), rest.strip()])
    return [turn for turn in result if turn[1]]


def chunk_turns(turns: Sequence, max_turns: int) -> list[list]:
    """Split a long block at turn boundaries into pieces of at most ``max_turns``."""

    if len(turns) <= max_turns:
        return [list(turns)]
    pieces = max(1, -(-len(turns) // max_turns))
    size = -(-len(turns) // pieces)
    return [list(turns[start : start + size]) for start in range(0, len(turns), size)]


def iter_dataset_records(dataset: Path, split: str = "train") -> Iterator[dict]:
    manifest = read_json(dataset / "manifest.json")
    for shard in manifest["splits"][split]["shards"]:
        with gzip.open(dataset / shard["path"], "rt", encoding="utf-8") as handle:
            for line in handle:
                yield json.loads(line)


def run_extract_corpus(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)
    documents: list[RoomDocument] = []
    kinds: Counter = Counter()
    scanned = 0
    sources: Counter = Counter()
    for record in iter_dataset_records(Path(args.dataset), "train"):
        scanned += 1
        if args.limit_documents and scanned > args.limit_documents:
            break
        for block in find_transcript_blocks(
            record["text"],
            min_turns=args.min_turns,
            max_speakers=args.max_speakers,
            max_gap_lines=args.max_gap_lines,
        ):
            for piece, turns in enumerate(chunk_turns(block["turns"], args.max_turns)):
                identifier = document_id(
                    "corpus-native", record["id"], block["lines"][0], piece
                )
                documents.append(
                    RoomDocument(
                        id=identifier,
                        source="corpus-native",
                        turns=[tuple(turn) for turn in turns],
                        provenance={
                            "document_id": record["id"],
                            "source": record["source"],
                            "path": record["path"],
                            "lines": block["lines"],
                            "piece": piece,
                            "kind": block["kind"],
                            "statistics": block["statistics"],
                        },
                        split=assign_holdout(rng, args.holdout_fraction),
                    )
                )
                kinds[block["kind"]] += 1
                sources[record["source"]] += 1
        if scanned % 500 == 0:
            log(f"scanned {scanned} documents, {len(documents)} blocks so far")
    tokenizer = load_tokenizer(Path(args.tokenizer))
    counts = count_tokens(tokenizer, documents)
    documents, counts = cap_documents(documents, counts, args.max_tokens, rng)
    total = int(counts.sum())
    written = write_records(Path(args.output), documents)
    summary = {
        "source": "corpus-native",
        "license": LICENSES["corpus-native"],
        "scanned_documents": scanned,
        "blocks": written,
        "blocks_by_kind": dict(kinds),
        "blocks_by_corpus_source": dict(sources),
        "documents_with_blocks": len(
            {document.provenance["document_id"] for document in documents}
        ),
        "tokens": total,
        "holdout_documents": sum(1 for d in documents if d.split == "holdout"),
        "output": str(args.output),
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(Path(args.output).with_suffix("").with_suffix(".summary.json"), summary)
    if args.examples:
        show_examples(documents, args.examples, rng)
    log(json.dumps({k: v for k, v in summary.items() if k != "blocks_by_corpus_source"}))
    return summary


def cap_documents(
    documents: list[RoomDocument], counts: np.ndarray, max_tokens: int, rng: np.random.Generator
) -> tuple[list[RoomDocument], np.ndarray]:
    """Seeded subsample of ``documents`` whose tokens fit in ``max_tokens`` (0: no cap)."""

    total = int(counts.sum())
    if not max_tokens or total <= max_tokens:
        return documents, counts
    kept, running = [], 0
    for index in rng.permutation(len(documents)):
        if running + counts[index] > max_tokens:
            continue
        kept.append(int(index))
        running += int(counts[index])
    kept.sort()
    log(f"capping {total} tokens to {running} by seeded subsampling")
    return [documents[index] for index in kept], counts[kept]


QUESTION_TURN = re.compile(r"\?[\"'\u201d\u2019)\]]*\s*$")


def questioner_answerer(document: RoomDocument) -> tuple[str, str] | None:
    """``(questioner, answerer)`` labels when a block has a clear asking/answering structure.

    Q./A. runs qualify by construction; two-speaker blocks qualify when one side ends at
    least half its turns with a question mark and the other fewer than 30%, or when one
    side is an editor answering letters.
    """

    counts = Counter(speaker for speaker, _ in document.turns)
    if document.provenance.get("kind") == "qa":
        others = [speaker for speaker in counts if speaker != "Interviewer"]
        if len(others) == 1 and "Interviewer" in counts:
            return "Interviewer", others[0]
        return None
    if len(counts) != 2:
        return None
    first, second = counts
    for editor, other in ((first, second), (second, first)):
        if editor.lower() in EDITOR_LABELS:
            return other, editor
    ratio = {
        speaker: sum(1 for who, text in document.turns if who == speaker and QUESTION_TURN.search(text))
        / counts[speaker]
        for speaker in counts
    }
    if ratio[first] >= 0.5 and ratio[second] < 0.3:
        return first, second
    if ratio[second] >= 0.5 and ratio[first] < 0.3:
        return second, first
    return None


def relabel_answerer(document: RoomDocument, seed: int) -> RoomDocument | None:
    """The block with its answering party as ``h`` and the questioner named plainly."""

    roles = questioner_answerer(document)
    if roles is None:
        return None
    questioner, answerer = roles
    rng = np.random.default_rng([seed, int(document.id[:12], 16)])
    if questioner.lower() in ROLE_LABELS or len(questioner) <= 2:
        name = QUESTIONER_HANDLES[int(rng.integers(len(QUESTIONER_HANDLES)))]
    else:
        name = questioner
    turns = []
    for speaker, text in document.turns:
        if speaker == answerer:
            turns.append((RESIDENT, text))
        else:
            turns.append((name if speaker == questioner else speaker, text))
    relabeled = RoomDocument(
        id=document_id("corpus-native-h", document.id),
        source="corpus-native-h",
        turns=turns,
        provenance={
            **document.provenance,
            "relabeled_from": {
                "id": document.id,
                "questioner": questioner,
                "questioner_rendered": name,
                "answerer": answerer,
            },
        },
        split=document.split,
        h_participant=answerer,
        decision_role=RESIDENT,
    )
    relabeled.decisions = boundary_decisions(relabeled.turns, RESIDENT)
    return relabeled


def run_relabel(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)
    originals = list(read_records(Path(args.input)))
    documents = []
    reasons: Counter = Counter()
    for document in originals:
        relabeled = relabel_answerer(document, args.seed)
        if relabeled is None:
            reasons["no clear questioner/answerer"] += 1
            continue
        reasons[document.provenance.get("kind", "?")] += 1
        documents.append(relabeled)
    tokenizer = load_tokenizer(Path(args.tokenizer))
    counts = count_tokens(tokenizer, documents)
    documents, counts = cap_documents(documents, counts, args.max_tokens, rng)
    written = write_records(Path(args.output), documents)
    summary = {
        "source": "corpus-native-h",
        "license": LICENSES["corpus-native-h"],
        "input": str(args.input),
        "input_documents": len(originals),
        "documents": written,
        "by_kind": dict(reasons),
        "questioners_given_handles": sum(
            1
            for d in documents
            if d.provenance["relabeled_from"]["questioner_rendered"]
            != d.provenance["relabeled_from"]["questioner"]
        ),
        "tokens": int(counts.sum()),
        "holdout_documents": sum(1 for d in documents if d.split == "holdout"),
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(Path(args.output).with_suffix("").with_suffix(".summary.json"), summary)
    if args.examples:
        show_examples(documents, args.examples, rng)
    log(json.dumps(summary))
    return summary


def show_examples(documents: Sequence[RoomDocument], count: int, rng) -> None:
    for index in rng.choice(len(documents), size=min(count, len(documents)), replace=False):
        document = documents[int(index)]
        print(f"=== {document.id} {document.source} {json.dumps(document.provenance)[:200]}")
        text = document.render()
        print(text[:900] + ("..." if len(text) > 900 else ""))
        print()


# --------------------------------------------------------------------------------------
# Gutenberg Dialogue Dataset
# --------------------------------------------------------------------------------------

_DETOKENIZE = [
    (re.compile(r"\s+([.,;:!?%)\]}])"), r"\1"),
    (re.compile(r"([(\[{])\s+"), r"\1"),
    (re.compile(r"\s+n't\b"), "n't"),
    (re.compile(r"\s+'(s|ll|re|ve|d|m|t)\b"), r"'\1"),
    (re.compile(r"\bcan not\b"), "cannot"),
    (re.compile(r"``\s*"), '"'),
    (re.compile(r"\s*''"), '"'),
    (re.compile(r"\s+'$"), "'"),
    (re.compile(r"\s{2,}"), " "),
]
_SENTENCE_START = re.compile(r"(^|[.!?]\s+)([\"'“‘]?)([a-z])")
_LONE_I = re.compile(r"\bi\b(?=[\s',.!?;:]|$)")


def detokenize(text: str) -> str:
    """Undo NLTK word tokenization and lowercasing as far as rules allow."""

    for pattern, replacement in _DETOKENIZE:
        text = pattern.sub(replacement, text)
    text = text.strip()
    text = _SENTENCE_START.sub(
        lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text
    )
    text = _LONE_I.sub("I", text)
    return text


def iter_gutenberg_dialogues(lines: Iterable[str]) -> Iterator[list[str]]:
    """Dialogues are runs of utterance lines separated by blank lines."""

    dialogue: list[str] = []
    for line in lines:
        line = line.rstrip("\n")
        if line.strip():
            dialogue.append(line.strip())
        elif dialogue:
            yield dialogue
            dialogue = []
    if dialogue:
        yield dialogue


def render_gutenberg_dialogue(
    utterances: Sequence[str], rng: np.random.Generator
) -> list[tuple[str, str]]:
    """Alternate two invented speakers, or rotate three so consecutive turns differ.

    The dataset carries no speaker identities; its construction assumes consecutive
    utterances come from different speakers, which is the only structure imposed here.
    """

    if len(utterances) >= 6 and rng.random() < 0.25:
        names = invent_names(3, rng)
        turns, previous = [], None
        for utterance in utterances:
            choices = [name for name in names if name != previous]
            speaker = choices[int(rng.integers(len(choices)))]
            turns.append((speaker, detokenize(utterance)))
            previous = speaker
        return turns
    names = invent_names(2, rng)
    return [
        (names[index % 2], detokenize(utterance))
        for index, utterance in enumerate(utterances)
    ]


def stream_hub_file(repo_id: str, filename: str) -> Iterator[str]:
    """Stream a public Hub file line by line without storing it."""

    import requests
    from huggingface_hub import hf_hub_url

    url = hf_hub_url(repo_id, filename, repo_type="dataset")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        response.encoding = "utf-8"
        for line in response.iter_lines(decode_unicode=True):
            yield line if line is not None else ""


def sample_gutenberg(
    lines: Iterable[str],
    *,
    rate: float,
    rng: np.random.Generator,
    split: str,
    filename: str,
    min_utterances: int,
    max_utterances: int,
    limit: int | None = None,
) -> tuple[list[RoomDocument], dict]:
    documents = []
    seen = eligible = 0
    for index, dialogue in enumerate(iter_gutenberg_dialogues(lines)):
        seen += 1
        if not min_utterances <= len(dialogue) <= max_utterances:
            continue
        eligible += 1
        if rng.random() >= rate:
            continue
        documents.append(
            RoomDocument(
                id=document_id("gutenberg-dialog", filename, index),
                source="gutenberg-dialog",
                turns=render_gutenberg_dialogue(dialogue, rng),
                provenance={"file": filename, "dialogue_index": index},
                split=split,
            )
        )
        if limit and len(documents) >= limit:
            break
    return documents, {"dialogues_seen": seen, "dialogues_eligible": eligible}


def run_gutenberg(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)
    if args.local:
        train_lines = open(Path(args.local) / "train.txt", encoding="utf-8", errors="replace")
        dev_lines = open(Path(args.local) / "dev.txt", encoding="utf-8", errors="replace")
    else:
        train_lines = stream_hub_file(GUTENBERG_DIALOG_REPO, "train.txt")
        dev_lines = stream_hub_file(GUTENBERG_DIALOG_REPO, "dev.txt")
    log(f"sampling train.txt at rate {args.rate}")
    train_docs, train_stats = sample_gutenberg(
        train_lines,
        rate=args.rate,
        rng=rng,
        split="train",
        filename="train.txt",
        min_utterances=args.min_utterances,
        max_utterances=args.max_utterances,
        limit=args.limit,
    )
    log(f"train: {len(train_docs)} dialogues from {train_stats}")
    dev_docs, dev_stats = sample_gutenberg(
        dev_lines,
        rate=args.holdout_rate,
        rng=rng,
        split="holdout",
        filename="dev.txt",
        min_utterances=args.min_utterances,
        max_utterances=args.max_utterances,
        limit=args.holdout_limit,
    )
    log(f"dev (holdout): {len(dev_docs)} dialogues from {dev_stats}")
    documents = train_docs + dev_docs
    tokenizer = load_tokenizer(Path(args.tokenizer))
    counts = count_tokens(tokenizer, documents)
    written = write_records(Path(args.output), documents)
    summary = {
        "source": "gutenberg-dialog",
        "license": LICENSES["gutenberg-dialog"],
        "repo": GUTENBERG_DIALOG_REPO,
        "rate": args.rate,
        "train": {**train_stats, "documents": len(train_docs)},
        "holdout": {**dev_stats, "documents": len(dev_docs)},
        "documents": written,
        "tokens": int(counts.sum()),
        "train_tokens": int(counts[: len(train_docs)].sum()),
        "holdout_tokens": int(counts[len(train_docs) :].sum()),
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(Path(args.output).with_suffix("").with_suffix(".summary.json"), summary)
    log(json.dumps(summary))
    return summary


# --------------------------------------------------------------------------------------
# Rooms with decisions: When2Speak and MultiLIGHT
# --------------------------------------------------------------------------------------

WHEN2SPEAK_SPEAKER = re.compile(
    r"^\**(Speaker_\d+|Assistant|\[AGENT\]|[A-Z][A-Za-z_]{1,30})\**\s*:\s*(.*)$", re.S
)
WHEN2SPEAK_BARE = re.compile(r"^(Speaker_\d+)\s+(.*)$", re.S)
AGENT_MENTION = re.compile(r"\*{0,2}\[AGENT\]\*{0,2}")
SPEAKER_MENTION = re.compile(r"Speaker_\d+")


def parse_when2speak_line(content: str, previous: str | None = None) -> tuple[str, str]:
    """``(speaker, text)`` for one window line.

    Labels are ``Speaker_k`` or ``Assistant`` (the agent's own earlier line; ``[AGENT]``
    and bold variants are folded into it). A handful of lines lack the colon or the label
    entirely; a label-less line is attributed to the previous speaker of the window.
    """

    match = WHEN2SPEAK_SPEAKER.match(content)
    if match:
        label = match.group(1)
        if label == "[AGENT]":
            label = "Assistant"
        return label, match.group(2).strip()
    match = WHEN2SPEAK_BARE.match(content)
    if match:
        return match.group(1), match.group(2).strip()
    return previous or "Speaker_0", content.strip()


def parse_when2speak_window(contents: Sequence[str]) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    for content in contents:
        turns.append(parse_when2speak_line(content, turns[-1][0] if turns else None))
    return turns


def window_overlap(turns: Sequence[tuple[str, str]], context: Sequence[tuple[str, str]]) -> int:
    """Largest ``k < len(context)`` with ``turns[-k:] == context[:k]`` (0: no overlap)."""

    for k in range(min(len(context) - 1, len(turns)), 0, -1):
        if list(turns[-k:]) == list(context[:k]):
            return k
    return 0


def chain_when2speak(records: Iterable[dict]) -> list[dict]:
    """Rebuild conversations from sliding windows.

    Each record is a window (at most eight turns) of the transcript so far plus the
    agent's decision after its last turn: ``>`` (silent) or the text it says. Windows of
    one conversation are contiguous and each adds one or two turns; a spoken intervention
    appears in later windows as an ``Assistant:`` turn, so it is appended as a turn here
    too. A record whose window shares no overlap with the current transcript starts a new
    conversation.
    """

    conversations: list[dict] = []
    current: dict | None = None
    for record in records:
        messages = record["messages"]
        context = parse_when2speak_window([m["content"] for m in messages[:-1]])
        decision = messages[-1]["content"].strip()
        overlap = window_overlap(current["turns"], context) if current else 0
        if overlap:
            current["turns"].extend(context[overlap:])
            current["records"] += 1
        else:
            if current is not None:
                conversations.append(current)
            current = {"turns": list(context), "decisions": [], "records": 1}
        after = len(current["turns"]) - 1
        if decision == ">":
            current["decisions"].append({"after_turn": after, "action": "silent"})
        else:
            current["decisions"].append({"after_turn": after, "action": "speak"})
            current["turns"].append(("Assistant", decision))
    if current is not None:
        conversations.append(current)
    return conversations


def render_when2speak(
    conversation: dict, index: int, split: str, seed: int
) -> RoomDocument:
    """When2Speak conversation -> room with the agent as ``moderator`` (not ``h``).

    The agent's interventions are GPT-4 text in an advisory register; they stay in the
    room under the ``moderator`` label so the conversation remains coherent and the
    speak/silent labels remain usable, but the resident is absent from these rooms.
    """

    rng = np.random.default_rng([seed, index, 7])
    labels = [
        speaker
        for speaker, _ in conversation["turns"]
        if speaker != "Assistant"
    ]
    labels = list(dict.fromkeys(labels))
    names = dict(zip(labels, invent_names(len(labels), rng)))
    spare = iter(name for name in NAME_POOL if name not in names.values())

    def mention(match: re.Match) -> str:
        label = match.group(0)
        if label not in names:
            names[label] = next(spare)
        return names[label]

    turns = []
    for speaker, text in conversation["turns"]:
        text = AGENT_MENTION.sub(MODERATOR, text)
        text = SPEAKER_MENTION.sub(mention, text)
        if speaker == "Assistant":
            turns.append((MODERATOR, text))
        else:
            turns.append((names[speaker], text))
    return RoomDocument(
        id=document_id("when2speak", split, index),
        source="when2speak",
        turns=turns,
        provenance={
            "split": split,
            "conversation_index": index,
            "records": conversation["records"],
            "names": names,
        },
        split="holdout" if split != "train" else "train",
        h_participant="Assistant ([AGENT])",
        decision_role=MODERATOR,
        decisions=conversation["decisions"],
    )


def boundary_decisions(turns: Sequence[tuple[str, str]], role: str) -> list[dict]:
    """One decision per turn boundary: after turn ``i-1``, did ``role`` produce turn ``i``?

    This is the When2Speak convention (a decision after each context turn); here the
    speaker of the next turn decides it, so every turn but the first is labelled.
    """

    return [
        {"after_turn": i - 1, "action": "speak" if turns[i][0] == role else "silent"}
        for i in range(1, len(turns))
    ]


def render_multilight(episode: dict, index: int, split: str) -> RoomDocument:
    """MultiLIGHT episode -> room; the most talkative character becomes ``h``.

    Every turn is a decision by all three characters: the one who spoke chose to speak,
    the others stayed silent, so ``h``'s decisions are ``speak`` before its own turns and
    ``silent`` before everyone else's (``boundary_decisions``).
    """

    messages = [
        (message["speaker"], message["text"]) for message in episode["messages"]
    ]
    counts = Counter(speaker for speaker, _ in messages)
    h_label = max(counts, key=lambda speaker: (counts[speaker], speaker))
    turns = [
        (RESIDENT if speaker == h_label else speaker, text) for speaker, text in messages
    ]
    document = RoomDocument(
        id=document_id("multilight", split, index),
        source="multilight",
        turns=turns,
        provenance={"split": split, "episode_index": index, "characters": list(counts)},
        split="holdout" if split != "train" else "train",
        h_participant=h_label,
        decision_role=RESIDENT,
    )
    document.decisions = boundary_decisions(document.turns, RESIDENT)
    return document


def run_rooms(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    raw = Path(args.raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    documents: list[RoomDocument] = []
    summary: dict = {"sources": {}}
    if not args.skip_when2speak:
        from huggingface_hub import hf_hub_download

        per_split = {}
        for split, filename in (
            ("train", "finetune_train_dialogue.jsonl"),
            ("validation", "finetune_val_dialogue.jsonl"),
        ):
            path = hf_hub_download(
                WHEN2SPEAK_REPO, filename, repo_type="dataset", local_dir=raw / "when2speak"
            )
            with open(path, encoding="utf-8") as handle:
                records = (json.loads(line) for line in handle if line.strip())
                conversations = chain_when2speak(records)
            rendered = [
                render_when2speak(conversation, index, split, args.seed)
                for index, conversation in enumerate(conversations)
            ]
            documents.extend(rendered)
            per_split[split] = {
                "file": filename,
                "records": sum(c["records"] for c in conversations),
                "conversations": len(conversations),
                "turns": sum(len(c["turns"]) for c in conversations),
                "speak_decisions": sum(
                    d["action"] == "speak" for c in conversations for d in c["decisions"]
                ),
                "silent_decisions": sum(
                    d["action"] == "silent" for c in conversations for d in c["decisions"]
                ),
            }
            log(f"when2speak {split}: {per_split[split]}")
        summary["sources"]["when2speak"] = {
            "license": LICENSES["when2speak"],
            "repo": WHEN2SPEAK_REPO,
            "splits": per_split,
        }
    if not args.skip_multilight:
        archive = raw / "parlai_multilight.tar.gz"
        if not archive.exists():
            import requests

            log(f"downloading {MULTILIGHT_URL}")
            with requests.get(MULTILIGHT_URL, stream=True, timeout=300) as response:
                response.raise_for_status()
                with archive.open("wb") as handle:
                    for chunk in response.iter_content(1 << 20):
                        handle.write(chunk)
        digest = sha256_file(archive)
        if digest != MULTILIGHT_SHA256:
            raise SystemExit(f"multilight archive sha256 {digest} != {MULTILIGHT_SHA256}")
        per_split = {}
        with tarfile.open(archive, "r:gz") as tar:
            for split in ("train", "valid", "test"):
                member = tar.extractfile(f"parlai_multilight/{split}.jsonl")
                if member is None:
                    raise SystemExit(f"multilight archive lacks {split}.jsonl")
                episodes = [
                    json.loads(line)
                    for line in member.read().decode("utf-8").splitlines()
                    if line.strip()
                ]
                rendered = [
                    render_multilight(episode, index, split)
                    for index, episode in enumerate(episodes)
                ]
                documents.extend(rendered)
                per_split[split] = {
                    "episodes": len(episodes),
                    "turns": sum(len(d.turns) for d in rendered),
                }
                log(f"multilight {split}: {per_split[split]}")
        summary["sources"]["multilight"] = {
            "license": LICENSES["multilight"],
            "url": MULTILIGHT_URL,
            "sha256": digest,
            "splits": per_split,
        }
    tokenizer = load_tokenizer(Path(args.tokenizer))
    counts = count_tokens(tokenizer, documents)
    for source in summary["sources"]:
        mask = np.array([d.source == source for d in documents])
        holdout = np.array([d.split == "holdout" for d in documents])
        summary["sources"][source].update(
            {
                "documents": int(mask.sum()),
                "tokens": int(counts[mask].sum()),
                "train_tokens": int(counts[mask & ~holdout].sum()),
                "holdout_tokens": int(counts[mask & holdout].sum()),
            }
        )
    written = write_records(Path(args.output), documents)
    summary.update(
        {
            "documents": written,
            "tokens": int(counts.sum()),
            "seconds": round(time.perf_counter() - started, 3),
        }
    )
    write_json(Path(args.output).with_suffix("").with_suffix(".summary.json"), summary)
    if not args.keep_raw:
        shutil.rmtree(raw, ignore_errors=True)
    log(json.dumps(summary))
    return summary


# --------------------------------------------------------------------------------------
# Jowett's Plato
# --------------------------------------------------------------------------------------

GUTENBERG_START = re.compile(r"^\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK")
GUTENBERG_END = re.compile(r"^\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK")


def gutenberg_body(text: str) -> str:
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if GUTENBERG_START.match(l)), -1)
    end = next((i for i, l in enumerate(lines) if GUTENBERG_END.match(l)), len(lines))
    return "\n".join(lines[start + 1 : end])


def run_plato(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)
    raw = Path(args.raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    documents: list[RoomDocument] = []
    works = {}
    for gutenberg_id, title in PLATO_GUTENBERG_IDS.items():
        path = raw / f"{gutenberg_id}.txt"
        if not path.exists():
            import requests

            url = f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt"
            log(f"fetching {title} from {url}")
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            path.write_bytes(response.content)
            time.sleep(0.5)
        body = gutenberg_body(path.read_text(encoding="utf-8", errors="replace"))
        blocks = find_transcript_blocks(
            body, min_turns=args.min_turns, max_gap_lines=args.max_gap_lines
        )
        count = 0
        for block in blocks:
            for piece, turns in enumerate(chunk_turns(block["turns"], args.max_turns)):
                documents.append(
                    RoomDocument(
                        id=document_id("plato", gutenberg_id, block["lines"][0], piece),
                        source="plato",
                        turns=[tuple(turn) for turn in turns],
                        provenance={
                            "gutenberg_id": gutenberg_id,
                            "title": title,
                            "lines": block["lines"],
                            "piece": piece,
                        },
                        split=assign_holdout(rng, args.holdout_fraction),
                    )
                )
                count += 1
        works[title] = {
            "gutenberg_id": gutenberg_id,
            "blocks": len(blocks),
            "documents": count,
            "turns": sum(len(block["turns"]) for block in blocks),
        }
    tokenizer = load_tokenizer(Path(args.tokenizer))
    counts = count_tokens(tokenizer, documents)
    written = write_records(Path(args.output), documents)
    summary = {
        "source": "plato",
        "license": LICENSES["plato"],
        "works": works,
        "documents": written,
        "tokens": int(counts.sum()),
        "holdout_documents": sum(1 for d in documents if d.split == "holdout"),
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(Path(args.output).with_suffix("").with_suffix(".summary.json"), summary)
    if not args.keep_raw:
        shutil.rmtree(raw, ignore_errors=True)
    log(json.dumps(summary))
    return summary


# --------------------------------------------------------------------------------------
# Tokenization and assembly
# --------------------------------------------------------------------------------------


def load_tokenizer(path: Path):
    from tokenizers import Tokenizer

    return Tokenizer.from_file(str(path))


def encode_documents(
    tokenizer, documents: Sequence[RoomDocument], eos_id: int, batch: int = 256
) -> Iterator[np.ndarray]:
    """Token ids (EOS appended) for each document, in order."""

    for start in range(0, len(documents), batch):
        texts = [document.render() for document in documents[start : start + batch]]
        for encoding in tokenizer.encode_batch(texts, add_special_tokens=False):
            yield np.asarray(encoding.ids + [eos_id], dtype=np.int64)


def count_tokens(
    tokenizer, documents: Sequence[RoomDocument], eos_id: int = DEFAULT_EOS_TOKEN_ID
) -> np.ndarray:
    return np.fromiter(
        (ids.shape[0] for ids in encode_documents(tokenizer, documents, eos_id)),
        dtype=np.int64,
        count=len(documents),
    )


def write_token_stream(
    path: Path, documents: Sequence[RoomDocument], tokenizer, eos_id: int, vocab_size: int
) -> list[dict]:
    """Write ``documents`` as one EOS-terminated uint16 stream; return per-document rows."""

    rows = []
    offset = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        for document, ids in zip(documents, encode_documents(tokenizer, documents, eos_id)):
            if ids.min() < 0 or ids.max() >= vocab_size:
                raise ValueError(f"token id outside the vocabulary in {document.id}")
            handle.write(ids.astype("<u2").tobytes())
            rows.append(
                {
                    "id": document.id,
                    "source": document.source,
                    "license": document.license,
                    "split": document.split,
                    "offset": offset,
                    "tokens": int(ids.shape[0]),
                    "turns": len(document.turns),
                    "speakers": document.speakers(),
                    "h_participant": document.h_participant,
                    "frame": document.provenance.get("frame"),
                    "prerendered": document.text is not None,
                    "provenance": document.provenance,
                }
            )
            offset += int(ids.shape[0])
    return rows


def choose_holdout(
    documents: Sequence[RoomDocument],
    counts: np.ndarray,
    target_tokens: int,
    rng: np.random.Generator,
) -> list[int]:
    """Indices of held-out documents: seeded, water-filled over sources to ~``target_tokens``.

    Each round gives every source that still has holdout candidates an equal share of the
    remaining budget, so small sources contribute everything they have and large ones fill
    the rest.
    """

    pools: dict[str, list[int]] = {}
    for index, document in enumerate(documents):
        if document.split == "holdout":
            pools.setdefault(document.source, []).append(index)
    pools = {source: [int(i) for i in rng.permutation(indices)] for source, indices in sorted(pools.items())}
    chosen: list[int] = []
    total = 0
    while total < target_tokens and any(pools.values()):
        active = [source for source, pool in pools.items() if pool]
        share = (target_tokens - total) / len(active)
        for source in active:
            taken = 0
            while pools[source] and taken < share:
                index = pools[source].pop()
                chosen.append(index)
                taken += int(counts[index])
                total += int(counts[index])
    return sorted(chosen)


def run_assemble(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    rng = np.random.default_rng(args.seed)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    documents: list[RoomDocument] = []
    inputs = []
    for source_path in args.sources:
        source_path = Path(source_path)
        loaded = list(read_records(source_path))
        inputs.append({"path": str(source_path), "documents": len(loaded)})
        documents.extend(loaded)
        log(f"{source_path}: {len(loaded)} documents")
    rendered_info = None
    if args.rendered:
        rendered_path = Path(args.rendered)
        if rendered_path.exists():
            rendered = list(read_rendered(rendered_path, args.repeat))
            documents.extend(rendered)
            rendered_info = {
                "path": str(rendered_path),
                "present": True,
                "repeat": args.repeat,
                "source_documents": len(rendered) // max(1, args.repeat),
                "documents": len(rendered),
                "sha256": sha256_file(rendered_path),
            }
            log(f"{rendered_path}: {rendered_info['source_documents']} scenes x {args.repeat}")
        else:
            rendered_info = {"path": str(rendered_path), "present": False, "repeat": args.repeat}
            log(f"WARNING: rendered source {rendered_path} does not exist; assembling without it")
    identifiers = Counter(document.id for document in documents)
    duplicates = [identifier for identifier, n in identifiers.items() if n > 1]
    if duplicates:
        raise SystemExit(f"duplicate document ids: {duplicates[:5]}")
    framed = Counter()
    for document in documents:
        if document.text is None and rng.random() < args.frame_fraction:
            key, varied, text = make_frame(rng)
            document.frame = text
            document.provenance = {**document.provenance, "frame": {"key": key, "varied": varied}}
            framed[f"{key}{'-varied' if varied else '-verbatim'}"] += 1
    log(f"frames on {sum(framed.values())} of {len(documents)} documents: {dict(sorted(framed.items()))}")
    tokenizer = load_tokenizer(Path(args.tokenizer))
    eos_id = int(args.eos_token_id)
    counts = count_tokens(tokenizer, documents, eos_id)
    holdout = set(choose_holdout(documents, counts, args.holdout_tokens, rng))
    train_docs = [d for i, d in enumerate(documents) if i not in holdout and d.split == "train"]
    holdout_docs = [documents[i] for i in sorted(holdout)]
    dropped = len(documents) - len(train_docs) - len(holdout_docs)
    order = rng.permutation(len(train_docs))
    train_docs = [train_docs[int(i)] for i in order]

    train_rows = write_token_stream(
        output / "room-documents.bin", train_docs, tokenizer, eos_id, args.vocab_size
    )
    holdout_rows = write_token_stream(
        output / "room-validation.bin", holdout_docs, tokenizer, eos_id, args.vocab_size
    )
    with (output / "room-documents.jsonl").open("w", encoding="utf-8") as handle:
        for row in train_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output / "room-validation.jsonl").open("w", encoding="utf-8") as handle:
        for row in holdout_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output / "room-decisions.jsonl").open("w", encoding="utf-8") as handle:
        for stream, docs, rows in (
            ("room-documents.bin", train_docs, train_rows),
            ("room-validation.bin", holdout_docs, holdout_rows),
        ):
            for document, row in zip(docs, rows):
                if document.h_participant is None:
                    continue
                handle.write(
                    json.dumps(
                        {
                            "id": document.id,
                            "source": document.source,
                            "stream": stream,
                            "offset": row["offset"],
                            "tokens": row["tokens"],
                            "h_participant": document.h_participant,
                            "role": document.decision_role,
                            "turn_speakers": [speaker for speaker, _ in document.turns],
                            "role_turns": [
                                i for i, (speaker, _) in enumerate(document.turns)
                                if speaker == document.decision_role
                            ],
                            "decisions": document.decisions or [],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    def per_source(rows: Sequence[dict]) -> dict:
        table: dict[str, dict] = {}
        for row in rows:
            entry = table.setdefault(
                row["source"], {"documents": 0, "tokens": 0, "license": row["license"]}
            )
            entry["documents"] += 1
            entry["tokens"] += row["tokens"]
        return dict(sorted(table.items()))

    manifest = {
        "schema_version": 1,
        "format": "contiguous token IDs; EOS after every document; each document is a room",
        "room_format": "lines of '<display name>: <text>' separated by one blank line",
        "resident": RESIDENT,
        "dtype": "little-endian uint16",
        "tokenizer": str(args.tokenizer),
        "tokenizer_sha256": sha256_file(Path(args.tokenizer)),
        "vocab_size": args.vocab_size,
        "eos_token_id": eos_id,
        "inputs": inputs,
        "seed": args.seed,
        "train": {
            "path": "room-documents.bin",
            "documents": len(train_rows),
            "tokens": int(sum(row["tokens"] for row in train_rows)),
            "sha256": sha256_file(output / "room-documents.bin"),
            "by_source": per_source(train_rows),
        },
        "holdout": {
            "path": "room-validation.bin",
            "documents": len(holdout_rows),
            "tokens": int(sum(row["tokens"] for row in holdout_rows)),
            "sha256": sha256_file(output / "room-validation.bin"),
            "by_source": per_source(holdout_rows),
            "target_tokens": args.holdout_tokens,
        },
        "dropped_holdout_candidates": dropped,
        "frames": {
            "fraction": args.frame_fraction,
            "documents": int(sum(framed.values())),
            "by_frame": dict(sorted(framed.items())),
            "texts": FRAMES,
        },
        "rendered": rendered_info,
        "decisions_file": "room-decisions.jsonl",
        "licenses": LICENSES,
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(output / "room-manifest.json", manifest)
    log(json.dumps({k: manifest[k] for k in ("train", "holdout", "dropped_holdout_candidates")}))
    return manifest


# --------------------------------------------------------------------------------------
# Weave into corpus v1 -> corpus v1.2
# --------------------------------------------------------------------------------------


def split_documents(stream: np.ndarray, eos_id: int) -> list[np.ndarray]:
    starts, ends = document_bounds(stream, eos_id)
    return [stream[start:end] for start, end in zip(starts, ends)]


def run_build(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    room_dir = Path(args.rooms)
    room_manifest = read_json(room_dir / "room-manifest.json")
    eos_id = int(room_manifest["eos_token_id"])
    train_bin = Path(args.train_bin)
    validation_bin = train_bin.with_name("validation.bin")
    report_path = train_bin.with_name("validation-report.json")
    v1_report = read_json(report_path)
    stream = np.memmap(train_bin, dtype="<u2", mode="r")
    if stream.shape[0] != v1_report["splits"]["train"]["tokens_including_eos"]:
        raise SystemExit("train.bin does not match the token count in its validation report")
    if v1_report["eos_token_id"] != eos_id:
        raise SystemExit("EOS id differs between the room documents and corpus v1")

    room_bin = room_dir / "room-documents.bin"
    room_sha = sha256_file(room_bin)
    if room_sha != room_manifest["train"]["sha256"]:
        raise SystemExit("room-documents.bin does not match room-manifest.json")
    room_stream = np.fromfile(room_bin, dtype="<u2")
    documents = split_documents(room_stream, eos_id)
    if len(documents) != room_manifest["train"]["documents"]:
        raise SystemExit("room document count differs from room-manifest.json")
    v1_documents = int(np.count_nonzero(stream == eos_id))
    slots = plan_insertions(v1_documents, len(documents), np.random.default_rng(args.seed))

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    log(f"weaving {len(documents)} room documents ({room_stream.shape[0]} tokens) into {train_bin}")
    plan = weave_stream(stream, documents, slots, output / "train.bin", eos_id)
    verification = verify_weave(stream, documents, plan, output / "train.bin")
    log(f"verified {verification['v1_tokens_identical']} v1 tokens identical outside insertions")

    validation_sha = sha256_file(validation_bin)
    if validation_sha != v1_report["splits"]["validation"]["sha256"]:
        raise SystemExit("validation.bin does not match the sha256 in the v1 report")
    shutil.copyfile(validation_bin, output / "validation.bin")
    shutil.copyfile(room_dir / "room-validation.bin", output / "room-validation.bin")
    shutil.copyfile(room_dir / "room-validation.jsonl", output / "room-validation.jsonl")
    shutil.copyfile(room_dir / "room-decisions.jsonl", output / "room-decisions.jsonl")

    room_slice = {
        "documents": len(documents),
        "tokens": int(room_stream.shape[0]),
        "fraction_actual": float(room_stream.shape[0] / plan["tokens"]),
        "minimum_token_id": int(room_stream.min()),
        "maximum_token_id": int(room_stream.max()),
        "by_source": room_manifest["train"]["by_source"],
        "room_documents_sha256": room_sha,
        "room_manifest_sha256": sha256_file(room_dir / "room-manifest.json"),
        "insertion_seed": int(args.seed),
        "insertion_rule": "slot ~ Uniform{0..v1_documents} per room document (seeded); "
        "documents sharing a slot are written in index order before v1 document slot",
    }
    report = derive_validation_report(v1_report, plan, room_slice)
    report["derived_from"] = {
        "corpus": "hghost curated tokens v1",
        "train_sha256": v1_report["splits"]["train"]["sha256"],
        "room_mix": room_slice,
    }
    write_json(output / "validation-report.json", report)
    names = (
        "train.bin",
        "validation.bin",
        "room-validation.bin",
        "room-validation.jsonl",
        "room-decisions.jsonl",
        "validation-report.json",
    )
    files = {
        name: {"sha256": sha256_file(output / name), "bytes": (output / name).stat().st_size}
        for name in names
    }
    if files["train.bin"]["sha256"] != plan["sha256"]:
        raise SystemExit("train.bin hash changed between writing and hashing")
    manifest = {
        "schema_version": 1,
        "corpus": "hghost curated tokens v1.2: v1 train stream + room mix",
        "format": "contiguous token IDs; EOS after every document",
        "dtype": "little-endian uint16",
        "tokenizer": v1_report["tokenizer"],
        "vocab_size": v1_report["vocab_size"],
        "eos_token_id": eos_id,
        "room_format": room_manifest["room_format"],
        "resident": RESIDENT,
        "v1": {
            "train_bin": str(train_bin),
            "train_sha256": v1_report["splits"]["train"]["sha256"],
            "train_tokens": int(stream.shape[0]),
            "train_documents": plan["v1_documents"],
            "validation_sha256": validation_sha,
            "validation_report": str(report_path),
        },
        "room_mix": room_slice,
        "holdout": {
            "documents": room_manifest["holdout"]["documents"],
            "tokens": room_manifest["holdout"]["tokens"],
            "by_source": room_manifest["holdout"]["by_source"],
            "files": ["room-validation.bin", "room-validation.jsonl"],
        },
        "licenses": room_manifest["licenses"],
        "splits": {
            "train": {
                "path": "train.bin",
                "tokens_including_eos": plan["tokens"],
                **files["train.bin"],
            },
            "validation": {
                "path": "validation.bin",
                "tokens_including_eos": v1_report["splits"]["validation"]["tokens_including_eos"],
                **files["validation.bin"],
            },
        },
        "files": files,
        "verification": verification,
        "insertions": plan["insertions"],
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(output / "manifest.json", manifest)
    percent = room_slice["fraction_actual"] * 100
    write_json(
        output / "dataset-metadata.json",
        {
            "title": KAGGLE_DATASET_TITLE,
            "id": args.kaggle_id,
            "subtitle": f"v1 curated uint16 streams with a {percent:.1f}% room-transcript mix",
            "description": (
                "The hghost curated token corpus v1 (train.bin) with multi-party conversation "
                "documents woven in at document boundaries so that "
                f"{percent:.2f}% of the training tokens are rooms: transcripts in the live "
                "harness format (lines of 'name: text' separated by a blank line) from "
                "corpus-native interviews and dialogues, the Gutenberg Dialogue Dataset, "
                "When2Speak (CC-BY-4.0), MultiLIGHT (MIT) and Jowett's Plato; validation.bin "
                "is unchanged from v1. room-validation.bin holds room documents never in "
                "train.bin; room-decisions.jsonl records where the resident h spoke or stayed "
                "silent. The corpus portion carries the same caveats as v1: token streams "
                "only, no source text or paths, and mixed or unknown source-document "
                "licensing. manifest.json records per-source counts, licenses, every "
                "insertion offset, and hashes."
            ),
            "licenses": [{"name": "unknown"}],
        },
    )
    (output / "README.md").write_text(
        "# H Ghost corpus v1.2 + room mix\n\n"
        "- `train.bin`: v1 train stream with room documents inserted at document boundaries "
        "(uint16 little-endian, EOS after every document).\n"
        "- `validation.bin`: byte-identical to v1.\n"
        "- `validation-report.json`: v1 schema; `splits.train.sha256` and "
        "`splits.validation.sha256` are what the TPU kernels verify; `derived_from.room_mix` "
        "describes the slice.\n"
        "- `room-validation.bin` / `room-validation.jsonl`: held-out room documents (never in "
        "train.bin) with provenance.\n"
        "- `room-decisions.jsonl`: per room document with the resident present, the turn "
        "indices where `h` spoke and the decision points where it stayed silent.\n"
        "- `manifest.json`: per-source counts and licenses, insertion offsets, hashes.\n\n"
        "Room format: lines of `<display name>: <text>` separated by one blank line; the "
        "resident is `h`; silence is the absence of a line.\n",
        encoding="utf-8",
    )
    log(
        f"train.bin: {plan['tokens']} tokens, {len(documents)} room documents "
        f"({percent:.3f}%), sha256 {plan['sha256']}"
    )
    return manifest


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hghost-roommix", description="room-transcript mix for corpus v1.2"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    def add_common(command: argparse.ArgumentParser, output: str) -> None:
        command.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
        command.add_argument("--output", type=Path, default=DEFAULT_OUTPUT / "sources" / output)
        command.add_argument("--seed", type=int, default=0)

    extract = commands.add_parser(
        "extract-corpus", help="transcript-like blocks in corpus v1 as room documents"
    )
    add_common(extract, "corpus-native.jsonl.gz")
    extract.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    extract.add_argument("--min-turns", type=int, default=6)
    extract.add_argument("--max-speakers", type=int, default=12)
    extract.add_argument("--max-gap-lines", type=int, default=12)
    extract.add_argument("--max-turns", type=int, default=120, help="split longer blocks")
    extract.add_argument("--max-tokens", type=int, default=15_000_000)
    extract.add_argument("--holdout-fraction", type=float, default=0.03)
    extract.add_argument("--limit-documents", type=int, default=0)
    extract.add_argument("--examples", type=int, default=0)

    relabel = commands.add_parser(
        "relabel", help="second copy of corpus interviews with the answerer as h"
    )
    add_common(relabel, "corpus-native-h.jsonl.gz")
    relabel.add_argument(
        "--input", type=Path, default=DEFAULT_OUTPUT / "sources" / "corpus-native.jsonl.gz"
    )
    relabel.add_argument("--max-tokens", type=int, default=5_000_000)
    relabel.add_argument("--examples", type=int, default=0)

    gutenberg = commands.add_parser("gutenberg", help="Gutenberg Dialogue Dataset as rooms")
    add_common(gutenberg, "gutenberg-dialog.jsonl.gz")
    gutenberg.add_argument("--rate", type=float, default=0.045, help="dialogue sampling rate")
    gutenberg.add_argument("--holdout-rate", type=float, default=0.01)
    gutenberg.add_argument("--min-utterances", type=int, default=4)
    gutenberg.add_argument("--max-utterances", type=int, default=40)
    gutenberg.add_argument("--limit", type=int, default=0)
    gutenberg.add_argument("--holdout-limit", type=int, default=600)
    gutenberg.add_argument("--local", type=Path, help="directory with train.txt and dev.txt")

    rooms = commands.add_parser("rooms", help="When2Speak and MultiLIGHT as rooms with h")
    add_common(rooms, "rooms-with-decisions.jsonl.gz")
    rooms.add_argument("--raw-dir", type=Path, required=True, help="scratch for downloads")
    rooms.add_argument("--skip-when2speak", action="store_true")
    rooms.add_argument("--skip-multilight", action="store_true")
    rooms.add_argument("--keep-raw", action="store_true")

    plato = commands.add_parser("plato", help="Jowett's Plato from Project Gutenberg")
    add_common(plato, "plato.jsonl.gz")
    plato.add_argument("--raw-dir", type=Path, required=True)
    plato.add_argument("--min-turns", type=int, default=6)
    plato.add_argument("--max-gap-lines", type=int, default=80)
    plato.add_argument("--max-turns", type=int, default=100)
    plato.add_argument("--holdout-fraction", type=float, default=0.03)
    plato.add_argument("--keep-raw", action="store_true")

    assemble = commands.add_parser("assemble", help="tokenize all room documents")
    assemble.add_argument("sources", nargs="+", help="source JSONL(.gz) files")
    assemble.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    assemble.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    assemble.add_argument("--eos-token-id", type=int, default=DEFAULT_EOS_TOKEN_ID)
    assemble.add_argument("--vocab-size", type=int, default=DEFAULT_VOCAB_SIZE)
    assemble.add_argument("--holdout-tokens", type=int, default=1_000_000)
    assemble.add_argument("--seed", type=int, default=0)
    assemble.add_argument("--frame-fraction", type=float, default=0.4)
    assemble.add_argument("--rendered", type=Path, help="pre-rendered scenes JSONL")
    assemble.add_argument("--repeat", type=int, default=1, help="copies of each rendered scene")

    build = commands.add_parser("build", help="weave room documents into corpus v1")
    build.add_argument("--rooms", type=Path, default=DEFAULT_OUTPUT)
    build.add_argument("--train-bin", type=Path, default=DEFAULT_TRAIN_BIN)
    build.add_argument("--output", type=Path, default=DEFAULT_OUTPUT / "corpus-v1.2-room")
    build.add_argument("--seed", type=int, default=12)
    build.add_argument("--kaggle-id", default=KAGGLE_DATASET_ID)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    handlers = {
        "extract-corpus": run_extract_corpus,
        "relabel": run_relabel,
        "gutenberg": run_gutenberg,
        "rooms": run_rooms,
        "plato": run_plato,
        "assemble": run_assemble,
        "build": run_build,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
