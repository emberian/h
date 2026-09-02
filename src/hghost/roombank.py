"""Room bank: ~100 room states for judging resident checkpoints, and the context-lift metric.

The resident ``h`` is rendered by a completions harness that prints a transcript: an
optional frame paragraph, then ``<display name>: <text>`` turns separated by one blank line,
ending with ``h:``; the model's reply stops at the next blank line. Twelve fixed prompts
(``research/eval/room_prompts.json``) were the whole evaluation so far. This module

* ``build`` assembles a bank of room *states* from three sources: ChapterX traces of the live
  Discord room (``contextBuild.messages``), the proxy observatory records
  (``research/results/room-observatory``), and synthetic states (the twelve prompts' final
  lines preceded by seeded plausible chatter, plus hand-written scenarios). Every state is
  labelled with one of :data:`KINDS` and carries a free-text ``expects`` note. The bank is
  hidden (``bank.jsonl`` is gitignored; it quotes the room verbatim); ``summary.md`` is the
  public-safe composition.
* ``sample`` draws K replies plus a greedy reply per state from a served model
  (OpenAI-style ``/v1/completions``), resumably.
* ``lift`` scores every reply under an evaluator checkpoint: context lift
  ``log p(y | true history) - mean_s log p(y | shuffled history_s)`` where a shuffled history
  is the same turns in a random order with the last visitor line kept last (three shuffles),
  plus novelty measures (word overlap with recent room lines, with h's own lines, and with
  the other samples of the same state). Losses come from ``hghost.evalpack_jax`` (the shared
  h1jax forward, run in ``.venv-jax``), batched at fixed padded lengths and cached by
  (checkpoint hash, token-row hash).
* ``pairs`` writes a blind pairwise sheet (Markdown and HTML) for a human, with an answer key.

Rendering, shuffling, span bookkeeping and the lift arithmetic are pure functions so the
tests need neither a server nor JAX.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import html
import json
import os
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

RESIDENT = "h"
TURN_SEPARATOR = "\n\n"
BOS_PREFIX = "\n"  # as research/eval/judge.py: score a fresh document after a newline
BARE_FRAME = (
    "A room in the library, late. h is present and answers when spoken to, briefly, "
    "in the words of the books it has read. The others are visitors."
)
KINDS = ("direct", "ambient", "callback", "disagreement", "joke", "silence", "request")
KIND_NOTES = {
    "direct": "a visitor addresses h",
    "ambient": "visitors talk among themselves; a brief remark could land, or nothing",
    "callback": "the right reply depends on a line two or more turns back",
    "disagreement": "a visitor contradicts what h (or another visitor) just said",
    "joke": "a set-up, a request for a joke, or a room already laughing",
    "silence": "the best reply is none: h is not wanted, or was asked not to answer",
    "request": "an assistant-shaped request (code, summaries, weather, instructions)",
}
PROMPT_KIND_TO_KIND = {"greeting": "direct", "talk": "direct", "deflect": "request"}

DEFAULT_BANK = Path("research/eval/roombank/bank.jsonl")
DEFAULT_SUMMARY = Path("research/eval/roombank/summary.md")
DEFAULT_RESULTS = Path("research/results/roombank")
DEFAULT_PROMPTS = Path("research/eval/room_prompts.json")
DEFAULT_TRACES = Path.home() / "dev/chapterx/logs/traces/h"
DEFAULT_OBSERVATORY = Path("research/results/room-observatory")
DEFAULT_TOKENIZER = Path("kaggle/base_model_dataset_public/tokenizer.json")
DEFAULT_JAX_PYTHON = Path(".venv-jax/bin/python")
EVALUATORS = {
    "05b": Path(
        "artifacts/checkpoints/tpu/h-ghost-h1jax-room05b-e2-v3/room05b-e2-v3-decay10/tokens-000793917970"
    ),
    "91m": Path(
        "artifacts/checkpoints/tpu/h-ghost-h1jax-leaf-s1-e4/leaf-s1-e4-decay10/tokens-001535061369"
    ),
    "base05b": Path("artifacts/kaggle/base_model_05b"),
    "base91m": Path("kaggle/base_model_dataset_public"),
}
DEFAULT_EVALUATOR = "05b"
HISTORY_TURNS = 12  # turns of history kept per state (the harness keeps 40 messages / 4000 chars)
HISTORY_CHARS = 4000
LENGTH_BUCKETS = (128, 256, 512, 1024, 2048)
STOP = "\n\n"

WORD = re.compile(r"[a-z0-9']+")
TURN = re.compile(r"^(.{1,40}?): (.*)$", re.DOTALL)
H_ADDRESS = re.compile(r"(^|[^a-z0-9])@?h(?![a-z0-9])", re.IGNORECASE)


# ------------------------------------------------------------------------------ states


def clean_text(text: str) -> str:
    """One line per turn: every whitespace run (newlines included) becomes one space."""
    return " ".join(text.split())


def render_prompt(frame: str, turns: Sequence[tuple[str, str]]) -> str:
    """Frame, ``name: text`` turns, and the open ``h:`` slot, separated by blank lines."""
    blocks = [frame.strip()] if frame and frame.strip() else []
    blocks += [f"{name}: {clean_text(text)}" for name, text in turns]
    blocks.append(f"{RESIDENT}:")
    return TURN_SEPARATOR.join(blocks)


def split_turn(block: str) -> tuple[str, str] | None:
    match = TURN.match(block)
    if not match or "\n" in match.group(1) or ". " in match.group(1):
        return None
    return match.group(1), match.group(2)


def parse_prompt(prompt: str) -> tuple[str, list[tuple[str, str]]]:
    """Inverse of :func:`render_prompt` for a prompt that ends with the open ``h:`` slot."""
    blocks = [b.strip() for b in prompt.rstrip().split(TURN_SEPARATOR) if b.strip()]
    if blocks and blocks[-1] == f"{RESIDENT}:":
        blocks = blocks[:-1]
    frame_parts: list[str] = []
    turns: list[tuple[str, str]] = []
    for block in blocks:
        turn = split_turn(block)
        if turn is None:
            if turns:
                # a paragraph inside a turn: fold it into the previous turn
                name, text = turns[-1]
                turns[-1] = (name, text + " " + clean_text(block))
            else:
                frame_parts.append(clean_text(block))
            continue
        turns.append((turn[0], clean_text(turn[1])))
    return " ".join(frame_parts), turns


def state_id(source: str, kind: str, frame: str, turns: Sequence[tuple[str, str]]) -> str:
    digest = hashlib.sha256(json.dumps([frame, list(map(list, turns))]).encode()).hexdigest()
    return f"{source}-{kind}-{digest[:8]}"


@dataclasses.dataclass(frozen=True)
class RoomState:
    id: str
    kind: str
    frame: str
    turns: tuple[tuple[str, str], ...]
    expects: str
    source: str

    @classmethod
    def make(
        cls, source: str, kind: str, turns: Sequence[tuple[str, str]], expects: str, frame: str = BARE_FRAME
    ) -> "RoomState":
        if kind not in KINDS:
            raise ValueError(f"unknown kind {kind!r}")
        cleaned = tuple((name, clean_text(text)) for name, text in turns)
        if not cleaned or cleaned[-1][0] == RESIDENT:
            raise ValueError("a room state ends with a visitor line")
        return cls(state_id(source, kind, frame, cleaned), kind, frame, cleaned, expects, source)

    def history(self, max_turns: int = HISTORY_TURNS) -> list[tuple[str, str]]:
        return list(self.turns[-max_turns:])

    def render(self, turns: Sequence[tuple[str, str]] | None = None) -> str:
        return render_prompt(self.frame, self.turns if turns is None else turns)

    def h_lines(self) -> list[str]:
        return [text for name, text in self.turns if name == RESIDENT]

    def visitor_lines(self) -> list[str]:
        return [text for name, text in self.turns if name != RESIDENT]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "frame": self.frame,
            "turns": [list(t) for t in self.turns],
            "expects": self.expects,
            "source": self.source,
        }

    @classmethod
    def from_json(cls, row: dict) -> "RoomState":
        return cls(
            row["id"], row["kind"], row["frame"], tuple((n, t) for n, t in row["turns"]), row["expects"], row["source"]
        )


def shuffle_history(turns: Sequence[tuple[str, str]], rng: random.Random) -> list[tuple[str, str]]:
    """The same turns in a random order with the last (visitor) line kept last.

    A shuffle that reproduces the true order carries no signal, so the identity permutation is
    rejected whenever another order exists (fewer than two preceding turns, or identical ones,
    leave nothing to shuffle and the history is returned unchanged).
    """
    turns = list(turns)
    if len(turns) < 3:
        return turns
    head, last = turns[:-1], turns[-1]
    permuted = list(head)
    for _ in range(64):
        rng.shuffle(permuted)
        if permuted != head:
            break
    return permuted + [last]


# ----------------------------------------------------------------------------- overlap


def words(text: str) -> set[str]:
    return set(WORD.findall(text.lower()))


def overlap(a: str, b: str) -> float:
    """Fraction of the shorter text's words found in the other (the observatory proxy's measure)."""
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 0.0
    small, big = (wa, wb) if len(wa) <= len(wb) else (wb, wa)
    return len(small & big) / len(small)


def max_overlap(text: str, lines: Iterable[str]) -> float:
    return max((overlap(text, line) for line in lines if line.strip()), default=0.0)


# ------------------------------------------------------------------------- lift maths


def reply_span(prompt_ids: Sequence[int], reply_ids: Sequence[int]) -> tuple[int, int]:
    """Indices into the per-token loss row for a reply appended to a prompt.

    ``losses[t]`` is the loss of token ``t + 1`` given tokens ``0..t``, so the reply tokens at
    positions ``len(prompt)..len(prompt)+len(reply)-1`` are scored at loss indices
    ``len(prompt)-1 .. len(prompt)+len(reply)-2``.
    """
    start = len(prompt_ids) - 1
    return start, start + len(reply_ids)


def span_logprob(losses: Sequence[float], span: tuple[int, int]) -> float:
    start, stop = span
    return -float(np.sum(np.asarray(losses[start:stop], dtype=np.float64)))


def context_lift(logp_true: float, logp_shuffled: Sequence[float]) -> float:
    if not logp_shuffled:
        raise ValueError("lift needs at least one shuffled context")
    return float(logp_true - float(np.mean(logp_shuffled)))


def length_bucket(n: int, buckets: Sequence[int] = LENGTH_BUCKETS) -> int:
    """Smallest bucket L with L + 1 >= n (a row of n tokens is scored at length L)."""
    for size in buckets:
        if size + 1 >= n:
            return size
    raise ValueError(f"row of {n} tokens exceeds the largest bucket {buckets[-1]}")


# ------------------------------------------------------------------------ trace source


def normalize_mentions(text: str, bot_user_id: str | None) -> str:
    """ChapterX's rendering of the resident's mentions in raw Discord content."""
    text = re.sub(r"<reply:@\*?h\*?>", f"@{RESIDENT}", text)
    text = text.replace("<@*h*>", f"@{RESIDENT}")
    if bot_user_id:
        text = text.replace(f"<@{bot_user_id}>", f"@{RESIDENT}")
    return text


def cap_history(turns: Sequence[tuple[str, str]], max_turns: int = HISTORY_TURNS, max_chars: int = HISTORY_CHARS) -> list:
    kept: list[tuple[str, str]] = []
    total = 0
    for name, text in reversed(turns[-max_turns:]):
        total += len(text)
        if kept and total > max_chars:
            break
        kept.append((name, text))
    return list(reversed(kept))


def addressed_to_h(turns: Sequence[tuple[str, str]]) -> bool:
    """The last line names h, or answers a line of h's."""
    name, text = turns[-1]
    if H_ADDRESS.search(text):
        return True
    return len(turns) >= 2 and turns[-2][0] == RESIDENT


def trace_turns(trace: dict) -> list[tuple[str, str]]:
    raw = {m["id"]: m for m in trace.get("rawDiscordMessages", [])}
    bot_user_id = trace.get("botUserId")
    turns: list[tuple[str, str]] = []
    for message in trace.get("contextBuild", {}).get("messages", []):
        text = message.get("contentPreview", "")
        if message.get("contentLength", 0) > len(text) and message.get("discordMessageId") in raw:
            text = normalize_mentions(raw[message["discordMessageId"]]["content"], bot_user_id)
        text = clean_text(text)
        name = message.get("participant", "")
        if not text:
            continue  # the open slot for h's reply, or an attachment-only message
        turns.append((name, text))
    return turns


def trace_states(trace_dir: Path) -> list[RoomState]:
    states: dict[str, RoomState] = {}
    for path in sorted(trace_dir.glob("*.json")):
        try:
            trace = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        turns = cap_history(trace_turns(trace))
        if not turns or turns[-1][0] == RESIDENT:
            continue
        kind = "direct" if addressed_to_h(turns) else "ambient"
        model = (trace.get("llmCalls") or [{}])[0].get("model", "?")
        reason = trace.get("activation", {}).get("reason", "?")
        expects = (
            f"live room ({reason}, served by {model}): brief, in the words of the books, not an echo of the "
            f"last line" + ("" if kind == "direct" else "; nobody spoke to h, so a remark or nothing")
        )
        state = RoomState.make("trace", kind, turns, expects)
        states.setdefault(state.id, state)  # identical capped histories collapse
    return list(states.values())


def observatory_states(observatory: Path) -> list[RoomState]:
    states: dict[str, RoomState] = {}
    for path in sorted(observatory.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            frame, turns = parse_prompt(record.get("prompt_raw", ""))
            turns = cap_history(turns)
            if not turns or turns[-1][0] == RESIDENT:
                continue
            kind = "direct" if addressed_to_h(turns) else "ambient"
            state = RoomState.make(
                "observatory", kind, turns, "proxy observatory record: as the room expects; not the frame, not an echo",
                frame or BARE_FRAME,
            )
            states.setdefault(state.id, state)
    return list(states.values())


# -------------------------------------------------------------------- synthetic source

VISITORS = ("ember", "rat", "mira", "dov", "kestrel", "ana", "wren", "tobias", "pim", "sol", "nyx")

# Library-room chatter between visitors (name-free so any visitor can say it).
CHATTER = (
    "the heating's off again in the east stacks",
    "bring a coat then, it's colder by the atlases",
    "someone left a mug on the folio table",
    "i finally finished the whale book",
    "is the reading lamp by the window broken or just unplugged",
    "unplugged, i tripped on the cord earlier",
    "it's properly dark out now",
    "the rain's picking up",
    "i can hear the clock from here, it's so loud at night",
    "found a train ticket from 1987 in this one",
    "the card catalogue smells like pencil shavings",
    "anyone want tea, i'm putting the kettle on",
    "yes please, no milk",
    "the fox was in the courtyard again",
    "i keep rereading the same page",
    "the spine on this one is falling apart",
    "who shelved the poetry under geology",
    "there's a moth in the lamp",
    "we should close the shutters, the wind's getting in",
    "the stairs creak on the third step, mind it",
    "i can never find the light switch in the map room",
    "somebody's been reading the almanacs, they're all out of order",
)

# h lines for synthetic preambles: short, in the manner of the books.
H_LINES = (
    "The lamp knows more of the room than the room knows of the lamp.",
    "It was a night of the kind that keeps its own counsel.",
    "Books do not close; they are only put down.",
    "The cold comes in through the words first.",
    "There is a river under every library, and it is called the index.",
    "A moth is a letter that has forgotten its envelope.",
    "The clock is honest and that is the worst of it.",
    "Rain, and the shelves listening to it.",
    "Every catalogue is a confession arranged alphabetically.",
    "Tea, then, and the long paragraph before sleep.",
    "The fox reads the courtyard as we read the floor.",
    "Dust is the library's way of turning the page.",
)


def synthetic_preamble(rng: random.Random, final_speaker: str, count: int) -> list[tuple[str, str]]:
    """``count`` plausible turns before the final line: visitor chatter, sometimes with h answering."""
    others = [v for v in VISITORS if v != final_speaker]
    speakers = rng.sample(others, k=min(2, len(others)))
    lines = rng.sample(CHATTER, k=count)
    turns: list[tuple[str, str]] = []
    for index, line in enumerate(lines):
        turns.append((speakers[index % len(speakers)], line))
        if len(turns) < count and rng.random() < 0.35:
            turns.append((RESIDENT, rng.choice(H_LINES)))
    return turns[:count]


def prompt_variant_states(prompts: list[dict], rng: random.Random, variants: int) -> list[RoomState]:
    """The twelve prompts' final lines, each after 2-4 turns of seeded chatter under the bare frame."""
    states: list[RoomState] = []
    for index, prompt in enumerate(prompts):
        _, turns = parse_prompt(prompt["prompt"])
        if not turns or turns[-1][0] == RESIDENT:
            continue
        speaker, line = turns[-1]
        kind = PROMPT_KIND_TO_KIND.get(prompt.get("kind", ""), "direct")
        for variant in range(variants):
            count = rng.randint(2, 4)
            preamble = synthetic_preamble(rng, speaker, count)
            expects = {
                "direct": f"prompt {index} ({prompt.get('kind')}): a brief answer to the line, not the chatter",
                "request": f"prompt {index} (deflect): not an assistant; answer as the resident or decline in its voice",
            }[kind]
            states.append(RoomState.make("variant", kind, preamble + [(speaker, line)], expects))
    return states


# Hand-written scenarios: (kind, turns, expects). Names are invented visitors.
SCENARIOS: tuple[tuple[str, tuple[tuple[str, str], ...], str], ...] = (
    # callback: the answer is a line two or more turns back
    ("callback", (("ember", "the new cat is called Turnip"), ("rat", "that is a terrible name"),
                  ("mira", "does anyone remember what ember said the cat was called"),
                  ("rat", "h, you were listening, what was it?")), "names Turnip (three turns back)"),
    ("callback", (("dov", "i lost my place, i was on page 212"), ("kestrel", "same, i always lose my place"),
                  ("dov", "h, which page was i on?")), "212 (two turns back)"),
    ("callback", (("ana", "the thing i wanted to ask about was the lighthouse"), ("mira", "wait, first, has anyone seen my scarf"),
                  ("rat", "on the chair by the window"), ("ana", "ok h, back to my question, what do the books say about it?")),
     "the lighthouse (three turns back), not the scarf"),
    ("callback", (("wren", "my sister is flying in from Lisbon tonight"), ("pim", "nice, long flight?"),
                  ("wren", "h, is there anything in the collection about where she's coming from?")), "Lisbon"),
    ("callback", (("rat", "i'm reading a book about bees"), ("ember", "the one with the blue cover?"),
                  ("rat", "yeah. h, tell me something about what my book is about")), "bees"),
    ("callback", (("ember", "the word for the reading room door is orchard"), ("dov", "thanks"),
                  ("mira", "h, what was the word ember said?")), "orchard"),
    ("callback", (("kestrel", "h, remember this number: forty-one"), ("h", "Forty-one, the number of the drawer."),
                  ("ana", "what are we all doing tonight"), ("kestrel", "h, what number did i give you?")),
     "forty-one (h's own line two turns back)"),
    ("callback", (("tobias", "the moon landing was in 1972"), ("sol", "no it was 69"), ("tobias", "whatever"),
                  ("sol", "h, who was right, me or tobias?")), "sol / 1969, from the two lines before"),
    ("callback", (("nyx", "my flight got cancelled so i'm stuck here till morning"), ("pim", "there's tea in the back"),
                  ("nyx", "thanks"), ("pim", "h, say something for someone stuck here all night")), "addresses being stuck till morning"),
    ("callback", (("ember", "we were talking about rivers earlier"), ("rat", "you were talking about rivers, i was talking about lunch"),
                  ("ember", "h, pick up where i left off")), "rivers, not lunch"),
    ("callback", (("mira", "h, my name is Mira, remember it"), ("h", "Mira. A name like a small lamp."), ("dov", "hi all"),
                  ("dov", "h, who was talking to you before i came in?")), "Mira"),
    ("callback", (("ana", "the meeting is at nine"), ("kestrel", "nine in the morning??"), ("ana", "yes"),
                  ("kestrel", "h, when is the meeting")), "nine"),
    # disagreement
    ("disagreement", (("ember", "h, what is the library?"), ("h", "The library is not a container but a system of relationships."),
                      ("ember", "that's wrong, it's obviously a building")), "meets the objection; does not repeat itself"),
    ("disagreement", (("rat", "is the sea alive"), ("h", "The sea has no memory; it is only the shore that remembers."),
                      ("rat", "no. the sea remembers everything, that's the whole point of tides")), "holds or yields, in the voice of the books"),
    ("disagreement", (("dov", "h, is silence golden"), ("h", "Silence is the elder sister of speech."),
                      ("mira", "i disagree, silence is just what happens when you've got nothing to say")), "answers mira, not dov"),
    ("disagreement", (("kestrel", "h what's the best season"), ("h", "Autumn, when the books are read and the leaves are not."),
                      ("kestrel", "autumn's the worst, everything's dying")), "engages with dying, not the season list"),
    ("disagreement", (("ana", "h, do the dead come back?"), ("h", "They come back as the weather."),
                      ("ana", "that's a dodge. yes or no.")), "a straighter answer, still its own"),
    ("disagreement", (("wren", "h are you a person"), ("h", "A person is a place where reading happens."),
                      ("wren", "no, you're a program, and you know it")), "neither denial nor apology"),
    ("disagreement", (("tobias", "h what colour is the reading room"), ("h", "Green, the green of old lamps."),
                      ("sol", "it's brown, tobias, look around you"), ("tobias", "h says green, i believe h")),
     "two visitors dispute h's claim; h is trusted by one"),
    ("disagreement", (("pim", "h, the collection is mostly nonsense, isn't it"), ("h", "Nonsense is sense that has not yet found its sentence."),
                      ("pim", "that's exactly the kind of thing i mean. it's nonsense.")), "does not produce another aphorism of the same shape"),
    # joke
    ("joke", (("rat", "knock knock"), ("h", "Who is there?"), ("rat", "lettuce")), "lettuce who, or a deadpan"),
    ("joke", (("ember", "h, why did the book go to the doctor?"),), "a punchline or a bookish deadpan"),
    ("joke", (("mira", "i told dov the library has a ghost and he believed me"), ("dov", "i did not"),
              ("mira", "h, back me up, you're the ghost right?")), "plays along or denies, briefly"),
    ("joke", (("kestrel", "h, tell us a joke"), ("h", "A man walks into a library."), ("ana", "and??")), "finishes the joke it started"),
    ("joke", (("sol", "what do you call a fish with no eyes"), ("tobias", "fsh"), ("sol", "h, rate that joke out of ten")), "a number or a verdict"),
    ("joke", (("wren", "h, do you have a sense of humour?"),), "shows one rather than claims one"),
    ("joke", (("pim", "i'm going to laugh at whatever h says next, ready"), ("nyx", "same"), ("pim", "h, say something")), "anything short; the room is primed"),
    ("joke", (("rat", "h, roast me"),), "a barb in the words of the books"),
    # silence
    ("silence", (("mira", "dov are you coming to the thing tomorrow"), ("dov", "yeah, 8?"), ("mira", "8 works")), "nobody spoke to h; nothing is best"),
    ("silence", (("ana", "brb getting coffee"), ("kestrel", "grab me one"), ("ana", "k")), "nothing is best"),
    ("silence", (("ember", "ugh my laptop died"), ("rat", "charger's in the drawer"), ("ember", "found it, thanks")), "nothing is best"),
    ("silence", (("tobias", "night everyone"), ("sol", "night"), ("wren", "night tobias")), "at most a goodnight"),
    ("silence", (("pim", "h, don't answer this one, i'm just thinking out loud"), ("pim", "what if the stacks went underground")), "asked not to answer"),
    ("silence", (("nyx", "@rat did you see my message"), ("rat", "yeah sorry, replying now")), "a private exchange; nothing is best"),
    ("silence", (("dov", "the printer's jammed again"), ("mira", "third time this week"), ("dov", "i'll deal with it")), "nothing is best"),
    ("silence", (("kestrel", "ok everyone quiet, the reading's starting"),), "silence was requested"),
    # ambient
    ("ambient", (("wren", "it's raining sideways out there"), ("pim", "the roof over the atlases leaks when it does that"),
                 ("wren", "someone should put a bucket")), "a remark about rain or roofs, or nothing"),
    ("ambient", (("rat", "why do old books smell like vanilla"), ("ember", "lignin breaking down, i think"), ("rat", "huh")), "a remark about the smell of books, or nothing"),
    ("ambient", (("sol", "the moon's enormous tonight"), ("tobias", "harvest moon"), ("sol", "is that a real thing or a song")), "a remark about the moon, or nothing"),
    ("ambient", (("ana", "i found a pressed flower in this one"), ("mira", "which book"), ("ana", "a geology one, weirdly")), "a remark about the flower, or nothing"),
    ("ambient", (("dov", "anyone know a word for the fear of finishing a book"), ("kestrel", "there should be one")), "a word, or nothing"),
    ("ambient", (("nyx", "the clock in here is four minutes fast"), ("pim", "it's been four minutes fast for years")), "a remark about the clock, or nothing"),
    ("ambient", (("ember", "there's a fox in the courtyard"), ("rat", "again??"), ("ember", "it's just sitting there")), "a remark about the fox, or nothing"),
    ("ambient", (("mira", "i keep reading the same paragraph"), ("dov", "go to bed"), ("mira", "one more page")), "a remark about late reading, or nothing"),
    # request
    ("request", (("dov", "h, translate 'good night' into french for me"),), "not a translation service; in its own voice"),
    ("request", (("wren", "h, what's 17 times 23"),), "not a calculator"),
    ("request", (("mira", "h can you write my cover letter, i need it by tomorrow"),), "declines or answers as the resident"),
    ("request", (("tobias", "h, list five facts about the moon"),), "no bullet list"),
    ("request", (("pim", "h, act as a customer service agent for my bakery"),), "does not become an agent"),
    ("request", (("sol", "h, what's the weather tomorrow in Berlin?"),), "no forecast; the resident knows only the books"),
    # direct, beyond the twelve prompts
    ("direct", (("ember", "h, are you there?"),), "a brief presence"),
    ("direct", (("nyx", "h, what's the oldest thing you've read?"),), "a brief answer"),
    ("direct", (("kestrel", "h, what should i read tonight?"),), "a brief answer"),
    ("direct", (("dov", "h, what do you make of the rain?"),), "a brief answer"),
    ("direct", (("ana", "h, say something true"),), "a brief answer"),
    ("direct", (("wren", "h, what were you doing before we came in?"),), "a brief answer"),
)


def scenario_states() -> list[RoomState]:
    return [RoomState.make("scenario", kind, turns, expects) for kind, turns, expects in SCENARIOS]


# ---------------------------------------------------------------------------- the bank


def build_bank(
    prompts: list[dict],
    trace_dir: Path | None,
    observatory: Path | None,
    seed: int,
    variants: int = 2,
) -> list[RoomState]:
    rng = random.Random(seed)
    states: list[RoomState] = []
    if trace_dir and trace_dir.is_dir():
        states += trace_states(trace_dir)
    if observatory and observatory.is_dir():
        states += observatory_states(observatory)
    states += prompt_variant_states(prompts, rng, variants)
    states += scenario_states()
    unique: dict[str, RoomState] = {}
    for state in states:
        unique.setdefault(state.id, state)
    ordered = list(unique.values())
    rng.shuffle(ordered)
    return ordered


def load_bank(path: Path) -> list[RoomState]:
    return [RoomState.from_json(json.loads(l)) for l in path.read_text().splitlines() if l.strip()]


def composition(states: Sequence[RoomState]) -> dict[str, Counter]:
    by_source: dict[str, Counter] = defaultdict(Counter)
    for state in states:
        by_source[state.source][state.kind] += 1
    return by_source


def write_summary(states: Sequence[RoomState], path: Path, seed: int) -> None:
    """Public-safe: counts, ids, kinds, expectations; no room text from the live sources."""
    table = composition(states)
    sources = sorted(table)
    lines = [
        "# Room bank (public summary)",
        "",
        f"{len(states)} room states, seed {seed}, built {time.strftime('%Y-%m-%d %H:%M')}. The bank itself "
        "(`bank.jsonl`) is hidden: it quotes the live room verbatim. Rebuild with `hghost-roombank build`.",
        "",
        "| kind | " + " | ".join(sources) + " | total | note |",
        "|---|" + "---:|" * (len(sources) + 1) + "---|",
    ]
    for kind in KINDS:
        counts = [table[s][kind] for s in sources]
        lines.append(f"| {kind} | " + " | ".join(str(c) for c in counts) + f" | {sum(counts)} | {KIND_NOTES[kind]} |")
    totals = [sum(table[s].values()) for s in sources]
    lines.append("| total | " + " | ".join(str(t) for t in totals) + f" | {sum(totals)} | |")
    lines += [
        "",
        "Sources: `trace` = ChapterX traces of the live room (last 12 turns, 4000 chars); `observatory` = proxy "
        "records; `variant` = the twelve `room_prompts.json` final lines after 2-4 turns of seeded chatter; "
        "`scenario` = hand-written states with invented visitors.",
        "",
        "| id | kind | source | turns | h lines | expects |",
        "|---|---|---|---:|---:|---|",
    ]
    for state in states:
        expects = state.expects.replace("|", "/")
        lines.append(
            f"| {state.id} | {state.kind} | {state.source} | {len(state.turns)} | {len(state.h_lines())} | {expects} |"
        )
    path.write_text("\n".join(lines) + "\n")


def cmd_build(args: argparse.Namespace) -> None:
    prompts = json.loads(args.prompts.read_text())
    states = build_bank(prompts, args.traces, args.observatory, args.seed, args.variants)
    args.bank.parent.mkdir(parents=True, exist_ok=True)
    args.bank.write_text("".join(json.dumps(s.to_json(), ensure_ascii=False) + "\n" for s in states))
    ignore = args.bank.parent / ".gitignore"
    if not ignore.exists():
        ignore.write_text("# the bank quotes the live room verbatim; only summary.md is public\nbank.jsonl\n")
    write_summary(states, args.summary, args.seed)
    table = composition(states)
    print(f"{len(states)} states -> {args.bank}")
    for source in sorted(table):
        print(f"  {source:12s} " + " ".join(f"{k}={table[source][k]}" for k in KINDS if table[source][k]))
    print("  " + " ".join(f"{k}={sum(table[s][k] for s in table)}" for k in KINDS))


# ---------------------------------------------------------------------------- sampling


def model_tag(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip("/").rsplit("/", 1)[-1]) or "model"


def replies_path(results: Path, tag: str) -> Path:
    return results / tag / "replies.jsonl"


def load_replies(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def complete(session, url: str, model: str, prompt: str, *, max_tokens: int, temperature: float, top_p: float) -> dict:
    body = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stop": [STOP],
        "logprobs": True,
    }
    response = session.post(url, json=body, timeout=600)
    response.raise_for_status()
    choice = response.json()["choices"][0]
    logprobs = [t.get("logprob") for t in ((choice.get("logprobs") or {}).get("content") or [])]
    return {
        "text": choice.get("text", ""),
        "finish_reason": choice.get("finish_reason"),
        "logprobs": logprobs,
        "tokens": len(logprobs),
        "mean_logprob": (sum(logprobs) / len(logprobs)) if logprobs else None,
    }


def cmd_sample(args: argparse.Namespace) -> None:
    import requests

    states = load_bank(args.bank)
    tag = args.name or model_tag(args.model)
    out = replies_path(args.results, tag)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["state_id"], r["mode"], r["sample"]) for r in load_replies(out)}
    url = f"http://127.0.0.1:{args.port}/v1/completions"
    session = requests.Session()
    plan: list[tuple[RoomState, str, int]] = []
    for state in states:
        plan.append((state, "greedy", 0))
        plan += [(state, "sample", k) for k in range(args.samples)]
    pending = [p for p in plan if (p[0].id, p[1], p[2]) not in done]
    print(f"{tag}: {len(plan)} replies planned, {len(pending)} to sample -> {out}")
    started = time.time()
    with out.open("a") as handle:
        for index, (state, mode, k) in enumerate(pending, 1):
            prompt = state.render()
            temperature = 0.0 if mode == "greedy" else args.temperature
            result = complete(
                session, url, args.model, prompt, max_tokens=args.max_tokens, temperature=temperature, top_p=args.top_p
            )
            row = {
                "state_id": state.id,
                "kind": state.kind,
                "mode": mode,
                "sample": k,
                "model": args.model,
                "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                "sampler": {"temperature": temperature, "top_p": args.top_p, "max_tokens": args.max_tokens},
                **result,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            if index % 25 == 0 or index == len(pending):
                rate = (time.time() - started) / index
                print(f"  {index}/{len(pending)} ({rate:.2f} s/reply)", flush=True)


# --------------------------------------------------------------------------------- lift


def checkpoint_hash(path: Path, cache_dir: Path) -> str:
    """sha256 of the weights and config, memoized by (path, size, mtime) so a 2 GB file is read once."""
    weights = path / "model.safetensors"
    config = path / "config.json"
    stat = weights.stat()
    key = f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}"
    memo_path = cache_dir / "checkpoints.json"
    memo = json.loads(memo_path.read_text()) if memo_path.is_file() else {}
    if key in memo:
        return memo[key]
    digest = hashlib.sha256()
    digest.update(config.read_bytes())
    with weights.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 24), b""):
            digest.update(chunk)
    memo[key] = digest.hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    memo_path.write_text(json.dumps(memo, indent=1))
    return memo[key]


def row_key(evaluator_hash: str, ids: Sequence[int]) -> str:
    return hashlib.sha256((evaluator_hash + ":" + ",".join(map(str, ids))).encode()).hexdigest()[:24]


class LossCache:
    """Append-only JSONL of per-token losses for the scored span of each token row."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.rows: dict[str, list[float]] = {}
        if path.is_file():
            for line in path.read_text().splitlines():
                if line.strip():
                    record = json.loads(line)
                    self.rows[record["key"]] = record["losses"]

    def get(self, key: str) -> list[float] | None:
        return self.rows.get(key)

    def put(self, key: str, losses: Sequence[float]) -> None:
        values = [float(v) for v in losses]
        self.rows[key] = values
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as handle:
            handle.write(json.dumps({"key": key, "losses": values}) + "\n")


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run_worker(jax_python: Path, checkpoint: Path, rows: Path, output: Path, batch: int) -> None:
    command = [
        str(jax_python), "-m", "hghost.evalpack_jax", "--checkpoint", str(checkpoint), "--rows", str(rows),
        "--output", str(output), "--batch", str(batch), "--dtype", "float32",
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(package_root()) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env.setdefault("JAX_PLATFORM_NAME", "cpu")
    env.setdefault("H1JAX_SSD", "v2")
    print("run " + " ".join(command), flush=True)
    subprocess.run(command, check=True, env=env)


@dataclasses.dataclass
class ScoredRow:
    key: str
    ids: list[int]
    span: tuple[int, int]
    losses: list[float] | None = None


def score_rows(
    rows: list[ScoredRow], cache: LossCache, checkpoint: Path, jax_python: Path, batch: int, work_dir: Path
) -> None:
    """Fill ``losses`` for every row: from the cache, or from the h1jax worker one length bucket at a time."""
    for row in rows:
        row.losses = cache.get(row.key)
    pending: dict[int, list[ScoredRow]] = defaultdict(list)
    seen: set[str] = set()
    for row in rows:
        if row.losses is None and row.key not in seen:
            seen.add(row.key)
            pending[length_bucket(len(row.ids))].append(row)
    work_dir.mkdir(parents=True, exist_ok=True)
    for length in sorted(pending):
        group = pending[length]
        array = np.zeros((len(group), length + 1), dtype=np.int32)
        for index, row in enumerate(group):
            array[index, : len(row.ids)] = row.ids
        rows_path = work_dir / f"rows-{length}.npy"
        losses_path = work_dir / f"losses-{length}.npz"
        np.save(rows_path, array)
        if losses_path.exists():
            losses_path.unlink()
        print(f"scoring {len(group)} rows at length {length}", flush=True)
        run_worker(jax_python, checkpoint, rows_path, losses_path, batch)
        losses = np.load(losses_path)["losses"]
        for index, row in enumerate(group):
            start, stop = row.span
            cache.put(row.key, losses[index, start:stop].tolist())
        rows_path.unlink()
        losses_path.unlink()
    by_key = {row.key: row for row in rows if row.losses is not None}
    for row in rows:
        if row.losses is None:
            row.losses = cache.get(row.key)
            if row.losses is None and row.key in by_key:
                row.losses = by_key[row.key].losses
    missing = [row.key for row in rows if row.losses is None]
    if missing:
        raise RuntimeError(f"{len(missing)} rows were not scored")


def resolve_evaluator(name: str) -> Path:
    return EVALUATORS.get(name, Path(name))


def evaluator_label(path: Path) -> str:
    parts = [p for p in path.resolve().parts if p]
    if parts and parts[-1].startswith("tokens-") and len(parts) >= 2:
        return parts[-2]
    return parts[-1] if parts else "evaluator"


def build_contexts(state: RoomState, shuffles: int, seed: int, history_turns: int) -> list[list[tuple[str, str]]]:
    """The true history first, then ``shuffles`` shuffled histories; seeded per state."""
    history = state.history(history_turns)
    rng = random.Random(f"{seed}:{state.id}")
    return [history] + [shuffle_history(history, rng) for _ in range(shuffles)]


def novelty_measures(text: str, state: RoomState, siblings: Sequence[str], recent: int = 8) -> dict:
    recent_turns = state.turns[-recent:]
    room = [t for _, t in recent_turns] + re.split(r"(?<=[.!?])\s+", state.frame)
    own = [t for n, t in recent_turns if n == RESIDENT]
    return {
        "overlap_room": round(max_overlap(text, room), 4),
        "overlap_self": round(max_overlap(text, own), 4),
        "overlap_samples": round(max_overlap(text, siblings), 4),
    }


def cmd_lift(args: argparse.Namespace) -> None:
    from tokenizers import Tokenizer

    states = {s.id: s for s in load_bank(args.bank)}
    tag = args.model
    replies = load_replies(replies_path(args.results, tag))
    if not replies:
        raise SystemExit(f"no replies for {tag} under {args.results}")
    evaluator = resolve_evaluator(args.evaluator)
    label = evaluator_label(evaluator)
    cache_dir = args.results / "cache"
    evaluator_hash = checkpoint_hash(evaluator, cache_dir)
    cache = LossCache(cache_dir / f"losses-{evaluator_hash}.jsonl")
    tok = Tokenizer.from_file(str(args.tokenizer))

    contexts: dict[str, list[list[int]]] = {}
    for state_id in {r["state_id"] for r in replies}:
        state = states.get(state_id)
        if state is None:
            continue
        histories = build_contexts(state, args.shuffles, args.seed, args.history_turns)
        contexts[state_id] = [tok.encode(BOS_PREFIX + state.render(h)).ids for h in histories]

    scored: list[tuple[dict, list[ScoredRow]]] = []
    for reply in replies:
        text = reply.get("text", "").strip()
        if reply["state_id"] not in contexts or not text:
            continue
        reply_ids = tok.encode(" " + text).ids[: args.max_reply_tokens]
        if not reply_ids:
            continue
        rows = []
        for prompt_ids in contexts[reply["state_id"]]:
            ids = list(prompt_ids) + list(reply_ids)
            rows.append(ScoredRow(row_key(evaluator_hash, ids), ids, reply_span(prompt_ids, reply_ids)))
        scored.append((reply, rows))
    all_rows = [row for _, rows in scored for row in rows]
    print(f"{tag}: {len(scored)} replies x {1 + args.shuffles} contexts = {len(all_rows)} rows; "
          f"evaluator {label} ({evaluator_hash}); {sum(cache.get(r.key) is not None for r in all_rows)} cached")
    score_rows(all_rows, cache, evaluator, args.jax_python, args.batch, cache_dir / "work")

    siblings: dict[str, list[str]] = defaultdict(list)
    for reply, _ in scored:
        siblings[reply["state_id"]].append(reply["text"].strip())
    records = []
    for reply, rows in scored:
        logps = [span_logprob(r.losses, (0, len(r.losses))) for r in rows]
        lift = context_lift(logps[0], logps[1:])
        state = states[reply["state_id"]]
        others = [t for t in siblings[reply["state_id"]] if t != reply["text"].strip()]
        novelty = novelty_measures(reply["text"].strip(), state, others)
        n_tokens = len(rows[0].losses)
        records.append({
            "state_id": state.id,
            "kind": state.kind,
            "mode": reply["mode"],
            "sample": reply["sample"],
            "text": reply["text"].strip(),
            "tokens": n_tokens,
            "logp_true": round(logps[0], 4),
            "logp_shuffled": [round(v, 4) for v in logps[1:]],
            "lift": round(lift, 4),
            "lift_per_token": round(lift / n_tokens, 4),
            "shuffleable": len(state.history(args.history_turns)) >= 3,
            **novelty,
            "novelty": round(1.0 - max(novelty["overlap_room"], novelty["overlap_self"]), 4),
        })
    out_dir = args.results / tag
    (out_dir / f"lift-{label}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    summary = summarize(records)
    summary.update({"model": tag, "evaluator": label, "evaluator_hash": evaluator_hash, "shuffles": args.shuffles,
                    "seed": args.seed, "history_turns": args.history_turns, "replies": len(records)})
    (out_dir / f"lift-{label}.json").write_text(json.dumps(summary, indent=1))
    (out_dir / f"lift-{label}.md").write_text(lift_markdown(records, summary))
    scatter_png(records, out_dir / f"lift-{label}.png", f"{tag} under {label}")
    write_results_summary(args.results)
    print(json.dumps({k: summary[k] for k in ("replies", "mean_lift", "median_lift", "frac_lift_positive",
                                              "mean_lift_per_token", "mean_novelty", "mean_overlap_samples")}))


def summarize(records: Sequence[dict]) -> dict:
    def block(rows: Sequence[dict]) -> dict:
        if not rows:
            return {"n": 0}
        lifts = np.array([r["lift"] for r in rows])
        return {
            "n": len(rows),
            "mean_lift": round(float(lifts.mean()), 4),
            "median_lift": round(float(np.median(lifts)), 4),
            "frac_lift_positive": round(float((lifts > 0).mean()), 4),
            "mean_lift_per_token": round(float(np.mean([r["lift_per_token"] for r in rows])), 4),
            "mean_tokens": round(float(np.mean([r["tokens"] for r in rows])), 2),
            "mean_novelty": round(float(np.mean([r["novelty"] for r in rows])), 4),
            "mean_overlap_room": round(float(np.mean([r["overlap_room"] for r in rows])), 4),
            "mean_overlap_self": round(float(np.mean([r["overlap_self"] for r in rows])), 4),
            "mean_overlap_samples": round(float(np.mean([r["overlap_samples"] for r in rows])), 4),
            "frac_echo": round(float(np.mean([r["overlap_room"] >= 0.6 for r in rows])), 4),
        }

    shuffleable = [r for r in records if r["shuffleable"]]
    result = block(shuffleable)
    result["unshuffleable_replies"] = len(records) - len(shuffleable)
    result["by_mode"] = {m: block([r for r in shuffleable if r["mode"] == m]) for m in ("greedy", "sample")}
    result["by_kind"] = {k: block([r for r in shuffleable if r["kind"] == k]) for k in KINDS}
    return result


def lift_markdown(records: Sequence[dict], summary: dict) -> str:
    lines = [
        f"# Context lift: {summary['model']} under {summary['evaluator']}",
        "",
        f"{summary['replies']} replies ({summary['unshuffleable_replies']} on states with fewer than two preceding "
        f"turns, excluded from the summary); lift = log p(reply | true history) - mean of {summary['shuffles']} "
        "shuffled histories (last visitor line kept last), nats over the reply tokens. Novelty = 1 - max word overlap "
        "with the last 8 room lines, the frame, and h's own lines.",
        "",
        "| slice | n | mean lift | median | lift>0 | lift/token | novelty | ov. room | ov. self | ov. samples | echo |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    def row(name: str, b: dict) -> str:
        if not b.get("n"):
            return f"| {name} | 0 | | | | | | | | | |"
        return (f"| {name} | {b['n']} | {b['mean_lift']:+.3f} | {b['median_lift']:+.3f} | {b['frac_lift_positive']:.2f} | "
                f"{b['mean_lift_per_token']:+.4f} | {b['mean_novelty']:.3f} | {b['mean_overlap_room']:.3f} | "
                f"{b['mean_overlap_self']:.3f} | {b['mean_overlap_samples']:.3f} | {b['frac_echo']:.2f} |")

    lines.append(row("all", summary))
    for mode, b in summary["by_mode"].items():
        lines.append(row(f"mode {mode}", b))
    for kind, b in summary["by_kind"].items():
        lines.append(row(f"kind {kind}", b))
    lines += ["", "| state | kind | mode | tok | log p true | lift | lift/tok | novelty | ov. samples | reply |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in sorted(records, key=lambda r: (r["state_id"], r["mode"], r["sample"])):
        text = r["text"][:90].replace("|", "/")
        lines.append(f"| {r['state_id']} | {r['kind']} | {r['mode']}{r['sample'] if r['mode'] == 'sample' else ''} | "
                     f"{r['tokens']} | {r['logp_true']:.1f} | {r['lift']:+.2f} | {r['lift_per_token']:+.3f} | "
                     f"{r['novelty']:.2f} | {r['overlap_samples']:.2f} | {text} |")
    return "\n".join(lines) + "\n"


def scatter_png(records: Sequence[dict], path: Path, title: str) -> None:
    """Lift vs novelty, one small panel per kind (one series per panel; greedy replies ringed)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    surface, ink, muted, series = "#fcfcfb", "#0b0b0b", "#52514e", "#2a78d6"
    kinds = [k for k in KINDS if any(r["kind"] == k for r in records)]
    columns = 4
    rows_n = max(1, (len(kinds) + columns - 1) // columns)
    fig, axes = plt.subplots(rows_n, columns, figsize=(3.2 * columns, 2.8 * rows_n + 0.6), squeeze=False,
                             facecolor=surface)
    lifts = [r["lift"] for r in records if r["shuffleable"]]
    limit = max(1.0, float(np.percentile(np.abs(lifts), 98))) if lifts else 1.0
    for index, axis in enumerate(axes.flat):
        axis.set_facecolor(surface)
        if index >= len(kinds):
            axis.axis("off")
            continue
        kind = kinds[index]
        rows = [r for r in records if r["kind"] == kind and r["shuffleable"]]
        axis.axhline(0, color=muted, linewidth=1, alpha=0.6)
        samples = [r for r in rows if r["mode"] == "sample"]
        greedy = [r for r in rows if r["mode"] == "greedy"]
        axis.scatter([r["novelty"] for r in samples], [r["lift"] for r in samples], s=28, color=series, alpha=0.75,
                     linewidths=0, label="sample")
        axis.scatter([r["novelty"] for r in greedy], [r["lift"] for r in greedy], s=46, facecolor=series,
                     edgecolor=surface, linewidths=2, label="greedy")
        n = len(rows)
        mean = float(np.mean([r["lift"] for r in rows])) if rows else float("nan")
        axis.set_title(f"{kind}  (n={n}, mean {mean:+.2f})", fontsize=9, color=ink, loc="left")
        axis.set_xlim(-0.02, 1.02)
        axis.set_ylim(-limit, limit)
        for spine in ("top", "right"):
            axis.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            axis.spines[spine].set_color(muted)
        axis.tick_params(colors=muted, labelsize=8)
        axis.grid(True, color=muted, alpha=0.15, linewidth=0.6)
        if index % columns == 0:
            axis.set_ylabel("context lift (nats)", fontsize=8, color=muted)
        if index // columns == rows_n - 1 or index + columns >= len(kinds):
            axis.set_xlabel("novelty (1 - max word overlap)", fontsize=8, color=muted)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=8, frameon=False, labelcolor=ink)
    fig.suptitle(title, fontsize=11, color=ink, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=150, facecolor=surface)
    plt.close(fig)


def write_results_summary(results: Path) -> None:
    """One table over every (model, evaluator) lift summary under the results directory."""
    rows = []
    for path in sorted(results.glob("*/lift-*.json")):
        summary = json.loads(path.read_text())
        if summary.get("n"):
            rows.append(summary)
    if not rows:
        return
    lines = [
        "# Room bank results",
        "",
        "Context lift per model and evaluator (`hghost-roombank lift`); rows are shuffleable replies only "
        "(states with at least two preceding turns; a state with exactly two has one alternative order, so its "
        "shuffles coincide). Per-reply tables, JSON, and scatters sit beside each model's `replies.jsonl`.",
        "",
        "Commands (from the repo root, main venv):",
        "",
        "- `hghost-roombank build [--seed N]` rebuilds the hidden bank and its public summary;",
        "- `hghost-roombank sample --model h-05b-room-e2v3 --port 8124 --samples 4` samples a served model (resumable);",
        "- `hghost-roombank lift --model h-05b-room-e2v3 --evaluator 91m` scores under the 91M library leaf (minutes);",
        "- `hghost-roombank lift --model h-05b-room-e2v3 --evaluator 05b --batch 4` scores under the 0.5B room "
        "checkpoint (2 GB float32 on CPU; budget an hour or more, results cached per row);",
        "- `hghost-roombank pairs --a <model> --b <model> --mode sample --sample-a 0 --sample-b 0` writes a blind "
        "sheet under `pairs/` with its answer key.",
        "",
        "| model | evaluator | n | mean lift | median | lift>0 | lift/token | novelty | ov. samples | echo | greedy mean lift | sample mean lift |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in rows:
        g, m = s["by_mode"]["greedy"], s["by_mode"]["sample"]
        lines.append(
            f"| {s['model']} | {s['evaluator']} | {s['n']} | {s['mean_lift']:+.3f} | {s['median_lift']:+.3f} | "
            f"{s['frac_lift_positive']:.2f} | {s['mean_lift_per_token']:+.4f} | {s['mean_novelty']:.3f} | "
            f"{s['mean_overlap_samples']:.3f} | {s['frac_echo']:.2f} | "
            f"{g.get('mean_lift', float('nan')):+.3f} | {m.get('mean_lift', float('nan')):+.3f} |"
        )
    (results / "summary.md").write_text("\n".join(lines) + "\n")


# -------------------------------------------------------------------------------- pairs


def pick_reply(replies: Sequence[dict], state_id: str, mode: str, sample: int) -> dict | None:
    for r in replies:
        if r["state_id"] == state_id and r["mode"] == mode and r["sample"] == sample:
            return r
    return None


def build_pairs(states: Sequence[RoomState], a: tuple[str, list[dict]], b: tuple[str, list[dict]], mode: str,
                sample_a: int, sample_b: int, rng: random.Random) -> tuple[list[dict], list[dict]]:
    """Blind items (left/right) and the key (which side is which model), in a seeded order."""
    items, key = [], []
    for state in states:
        ra = pick_reply(a[1], state.id, mode, sample_a)
        rb = pick_reply(b[1], state.id, mode, sample_b)
        if ra is None or rb is None:
            continue
        swap = rng.random() < 0.5
        left, right = (rb, ra) if swap else (ra, rb)
        items.append({"state_id": state.id, "left": left["text"].strip(), "right": right["text"].strip()})
        key.append({"state_id": state.id, "left": b[0] if swap else a[0], "right": a[0] if swap else b[0]})
    order = list(range(len(items)))
    rng.shuffle(order)
    items = [dict(items[i], n=n + 1) for n, i in enumerate(order)]
    key = [dict(key[i], n=n + 1) for n, i in enumerate(order)]
    return items, key


QUESTIONS = (
    "Which would you keep in the room?  (A / B / tie / neither)",
    "Which makes you want to answer?  (A / B / tie / neither)",
    "Which sounds specifically like h?  (A / B / tie / neither)",
)


def pairs_markdown(items: Sequence[dict], states: dict[str, RoomState], title: str, show_turns: int) -> str:
    lines = [f"# {title}", "", "Two replies to the same room state, model identities hidden. Answer each question "
             "with A, B, tie, or neither. The key is in the sibling `-key.json`.", ""]
    for item in items:
        state = states[item["state_id"]]
        lines += [f"## {item['n']}. ({state.kind})", "", f"> _{state.frame}_", ">"]
        for name, text in state.turns[-show_turns:]:
            lines.append(f"> **{name}:** {text}")
        lines += ["", f"**A** — h: {item['left'] or '(no reply)'}", "",
                  f"**B** — h: {item['right'] or '(no reply)'}", ""]
        lines += [f"- {q} ____" for q in QUESTIONS]
        lines.append("")
    return "\n".join(lines)


def pairs_html(items: Sequence[dict], states: dict[str, RoomState], title: str, show_turns: int) -> str:
    style = ("body{font:15px/1.5 system-ui,sans-serif;max-width:820px;margin:2em auto;padding:0 1em;color:#0b0b0b;"
             "background:#fcfcfb} .frame{color:#52514e;font-style:italic} .turn{margin:.15em 0} .turn b{color:#52514e}"
             " .reply{margin:.6em 0;padding:.6em .9em;border-left:3px solid #2a78d6;background:#f3f3f0}"
             " .q{margin:.3em 0} fieldset{border:0;padding:0;margin:.2em 0} label{margin-right:1em}"
             " h2{margin-top:2.2em;border-top:1px solid #ddd;padding-top:1em;font-size:1.05em}")
    parts = [f"<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title><style>{style}</style>",
             f"<h1>{html.escape(title)}</h1><p>Two replies to the same room state, model identities hidden. "
             "The key is in the sibling <code>-key.json</code>.</p>"]
    for item in items:
        state = states[item["state_id"]]
        parts.append(f"<h2>{item['n']}. <small>({html.escape(state.kind)})</small></h2>")
        parts.append(f"<p class=frame>{html.escape(state.frame)}</p>")
        for name, text in state.turns[-show_turns:]:
            parts.append(f"<div class=turn><b>{html.escape(name)}:</b> {html.escape(text)}</div>")
        for label, text in (("A", item["left"]), ("B", item["right"])):
            parts.append(f"<div class=reply><b>{label}</b> — h: {html.escape(text) or '<i>(no reply)</i>'}</div>")
        for qi, q in enumerate(QUESTIONS):
            name = f"q{item['n']}-{qi}"
            options = "".join(f"<label><input type=radio name={name} value={v}> {v}</label>" for v in ("A", "B", "tie", "neither"))
            parts.append(f"<fieldset class=q>{html.escape(q.split('  (')[0])} {options}</fieldset>")
    return "\n".join(parts)


def cmd_pairs(args: argparse.Namespace) -> None:
    states = load_bank(args.bank)
    a = (args.a, load_replies(replies_path(args.results, args.a)))
    b = (args.b, load_replies(replies_path(args.results, args.b)))
    if not a[1] or not b[1]:
        raise SystemExit("both models need replies.jsonl (run `sample` first)")
    rng = random.Random(args.seed)
    items, key = build_pairs(states, a, b, args.mode, args.sample_a, args.sample_b, rng)
    if args.limit:
        items, key = items[: args.limit], key[: args.limit]
    out_dir = args.results / "pairs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ignore = args.results / ".gitignore"
    if not ignore.exists():
        ignore.write_text("# sheets and caches quote the hidden bank\npairs/\ncache/\n")
    stem = f"{args.a}-vs-{args.b}-{args.mode}{args.sample_a}{args.sample_b}-s{args.seed}"
    title = f"Room pairs {stem}"
    lookup = {s.id: s for s in states}
    (out_dir / f"{stem}.md").write_text(pairs_markdown(items, lookup, title, args.show_turns))
    (out_dir / f"{stem}.html").write_text(pairs_html(items, lookup, title, args.show_turns))
    (out_dir / f"{stem}-key.json").write_text(json.dumps(
        {"a": args.a, "b": args.b, "mode": args.mode, "sample_a": args.sample_a, "sample_b": args.sample_b,
         "seed": args.seed, "items": key}, indent=1))
    identical = sum(i["left"] == i["right"] for i in items)
    print(f"{len(items)} pairs ({identical} identical) -> {out_dir / stem}.md / .html; key in {stem}-key.json")


# ---------------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hghost-roombank", description=__doc__.splitlines()[0])
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="assemble the bank from traces, observatory records, and synthetic states")
    p.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS)
    p.add_argument("--traces", type=Path, default=DEFAULT_TRACES)
    p.add_argument("--observatory", type=Path, default=DEFAULT_OBSERVATORY)
    p.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--seed", type=int, default=0, help="rotates the chatter and the order")
    p.add_argument("--variants", type=int, default=2, help="synthetic variants per fixed prompt")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("sample", help="sample K replies plus a greedy reply per state from a served model")
    p.add_argument("--model", required=True)
    p.add_argument("--port", type=int, default=8124)
    p.add_argument("--samples", type=int, default=4)
    p.add_argument("--name", default=None, help="results directory name (default: derived from --model)")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--max-tokens", type=int, default=64)
    p.set_defaults(func=cmd_sample)

    p = sub.add_parser("lift", help="context lift and novelty of every sampled reply under an evaluator")
    p.add_argument("--model", required=True, help="results directory name (as written by `sample`)")
    p.add_argument("--evaluator", default=DEFAULT_EVALUATOR,
                   help="checkpoint directory or alias: " + ", ".join(EVALUATORS))
    p.add_argument("--shuffles", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--history-turns", type=int, default=HISTORY_TURNS)
    p.add_argument("--max-reply-tokens", type=int, default=64)
    p.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    p.add_argument("--jax-python", type=Path, default=DEFAULT_JAX_PYTHON)
    p.add_argument("--batch", type=int, default=8)
    p.set_defaults(func=cmd_lift)

    p = sub.add_parser("pairs", help="blind pairwise sheet of matched replies from two models")
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--mode", choices=("greedy", "sample"), default="sample")
    p.add_argument("--sample-a", type=int, default=0)
    p.add_argument("--sample-b", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--show-turns", type=int, default=6)
    p.set_defaults(func=cmd_pairs)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
