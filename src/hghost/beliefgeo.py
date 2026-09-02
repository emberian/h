"""Belief-geometry instrument: an authored HMM slice of the corpus and linear probes.

Shai, Riechers et al. (2024, arXiv 2405.15943) showed that a transformer trained on
sequences from a hidden Markov process linearly represents the Bayesian belief state
over the hidden states (the mixed-state presentation) in its residual stream. This
module makes that measurable for the `h` ghost by construction:

* ``generate`` samples the Mess3 process and computes the exact belief state after each
  symbol with the forward algorithm;
* ``tokens`` chooses three rare single-id Falcon-H1 tokens as emission symbols (plus a
  regime-marker prefix) and reports their corpus counts;
* ``build`` renders each Mess3 sequence as a document and weaves the documents into the
  v1 training stream at deterministic pseudo-random document boundaries so that the
  synthetic tokens are ~2% of the total, producing a Kaggle-uploadable corpus v1.1;
* ``probe`` runs a checkpoint on held-out sequences (in ``.venv-jax``, CPU, FP32),
  collects the residual stream after every layer and the Mamba SSM state, and fits
  linear maps from activations to the belief simplex, with a shuffled-target control.

Mess3 (Marzen & Crutchfield 2017; Shai et al. 2024, Appendix). Three hidden states,
three symbols. With ``y = 1 - 2x`` and ``b = (1 - alpha) / 2``, the joint
symbol-transition matrices ``T[a][i][j] = P(emit a, next state j | state i)`` are::

    T[A] = [[alpha*y, b*x,     b*x    ],   T[B] = [[b*y, alpha*x, b*x    ],
            [alpha*x, b*y,     b*x    ],           [b*x, alpha*y, b*x    ],
            [alpha*x, b*x,     b*y    ]]           [b*x, alpha*x, b*y    ]]
    T[C] = [[b*y,     b*x,     alpha*x],
            [b*x,     b*y,     alpha*x],
            [b*x,     b*x,     alpha*y]]

Equivalently: the hidden state stays with probability ``y`` and moves to each other
state with probability ``x``; the emitted symbol is the *destination* state's label
with probability ``alpha`` and each other symbol with probability ``b``. The paper's
figures use ``x = 0.05, alpha = 0.85`` (their printed ``T[A]`` has entries 0.765,
0.00375, 0.0425 and 0.0675, which are exactly ``alpha*y, b*x, alpha*x, b*y``); those are
the defaults here. ``x = 0.15, alpha = 0.6`` is the default of the authors' library and
gives a more contracted, noisier simplex.

Only numpy is imported at module level so that ``beliefgeo_jax`` (which runs inside the
h1jax virtualenv) can import the process and probe mathematics from here.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

import numpy as np

DEFAULT_X = 0.05
DEFAULT_ALPHA = 0.85
DEFAULT_EOS_TOKEN_ID = 11
DEFAULT_EMISSION_GLYPHS = ("∇", "∂", "←")
DEFAULT_PREFIX_GLYPH = "│"
DEFAULT_JAX_PYTHON = Path(".venv-jax/bin/python")
DEFAULT_RIDGES = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0)
KAGGLE_DATASET_ID = "emberian64/hghost-curated-tokens-v1-1-mess3"
KAGGLE_DATASET_TITLE = "H Ghost corpus v1.1 + Mess3 slice"
SQRT3_2 = float(np.sqrt(3.0) / 2.0)


def log(message: str) -> None:
    print(f"[beliefgeo] {message}", file=sys.stderr, flush=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------
# Hidden Markov processes with a known mixed-state presentation
# --------------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class HiddenProcess:
    """An edge-emitting HMM: ``transition[a, i, j] = P(emit a, next j | state i)``."""

    name: str
    transition: np.ndarray
    parameters: dict[str, float]

    def __post_init__(self) -> None:
        matrices = np.asarray(self.transition, dtype=np.float64)
        if matrices.ndim != 3 or matrices.shape[1] != matrices.shape[2]:
            raise ValueError("transition must have shape (symbols, states, states)")
        if np.any(matrices < 0):
            raise ValueError("transition probabilities must be non-negative")
        row_sums = matrices.sum(axis=(0, 2))
        if not np.allclose(row_sums, 1.0, atol=1e-12):
            raise ValueError(
                f"rows must sum to one over (symbol, next state): {row_sums}"
            )
        object.__setattr__(self, "transition", matrices)

    @property
    def symbol_count(self) -> int:
        return int(self.transition.shape[0])

    @property
    def state_count(self) -> int:
        return int(self.transition.shape[1])

    @property
    def state_transition(self) -> np.ndarray:
        """``sum_a T[a]``: the plain hidden-state Markov chain."""
        return self.transition.sum(axis=0)

    @property
    def stationary(self) -> np.ndarray:
        """Left eigenvector of the state chain with eigenvalue one, normalized."""
        values, vectors = np.linalg.eig(self.state_transition.T)
        index = int(np.argmin(np.abs(values - 1.0)))
        vector = np.real(vectors[:, index])
        vector = vector / vector.sum()
        if np.any(vector < -1e-12):
            raise ValueError("stationary distribution has negative entries")
        return np.clip(vector, 0.0, None) / np.clip(vector, 0.0, None).sum()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "parameters": dict(self.parameters),
            "symbols": self.symbol_count,
            "states": self.state_count,
            "transition": self.transition.tolist(),
            "stationary": self.stationary.tolist(),
        }


def mess3(x: float = DEFAULT_X, alpha: float = DEFAULT_ALPHA) -> HiddenProcess:
    """The Mess3 process: sticky three-state chain, destination-labelled emissions."""

    if not 0.0 < x < 0.5:
        raise ValueError("mess3 requires 0 < x < 0.5")
    if not 0.0 < alpha <= 1.0:
        raise ValueError("mess3 requires 0 < alpha <= 1")
    stay = 1.0 - 2.0 * x
    other = (1.0 - alpha) / 2.0
    states = 3
    move = np.full((states, states), x, dtype=np.float64)
    np.fill_diagonal(move, stay)
    emit = np.full(
        (states, states), other, dtype=np.float64
    )  # emit[j, a] = P(a | next j)
    np.fill_diagonal(emit, alpha)
    transition = np.einsum("ij,ja->aij", move, emit)
    return HiddenProcess("mess3", transition, {"x": float(x), "alpha": float(alpha)})


PROCESSES = {"mess3": mess3}


def sample_sequences(
    process: HiddenProcess,
    count: int,
    length: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample ``count`` sequences of ``length`` symbols; initial states from stationary.

    Returns ``(symbols[count, length], states[count, length + 1])`` as uint8; the state
    array includes the initial hidden state so the sampler can be checked empirically.
    """

    symbols_n, states_n = process.symbol_count, process.state_count
    joint = process.transition.transpose(1, 0, 2).reshape(
        states_n, symbols_n * states_n
    )
    cumulative = np.cumsum(joint, axis=1)
    cumulative[:, -1] = 1.0
    states = np.empty((count, length + 1), dtype=np.uint8)
    symbols = np.empty((count, length), dtype=np.uint8)
    states[:, 0] = rng.choice(states_n, size=count, p=process.stationary)
    uniforms = rng.random((length, count))
    for step in range(length):
        current = states[:, step]
        index = (uniforms[step][:, None] >= cumulative[current]).sum(axis=1)
        symbols[:, step] = index // states_n
        states[:, step + 1] = index % states_n
    return symbols, states


def belief_states(
    process: HiddenProcess,
    symbols: np.ndarray,
    initial: np.ndarray | None = None,
) -> np.ndarray:
    """Exact Bayesian belief over hidden states after each symbol (forward algorithm).

    ``eta' = eta T[x] / (eta T[x] 1)`` applied along every sequence, starting from the
    stationary distribution unless ``initial`` is given. Returns float64
    ``[count, length, states]``; entry ``t`` is the belief after observing symbol ``t``.
    """

    symbols = np.asarray(symbols)
    if symbols.ndim == 1:
        return belief_states(process, symbols[None, :], initial)[0]
    count, length = symbols.shape
    prior = process.stationary if initial is None else np.asarray(initial, np.float64)
    eta = np.broadcast_to(prior, (count, process.state_count)).astype(np.float64)
    beliefs = np.empty((count, length, process.state_count), dtype=np.float64)
    for step in range(length):
        eta = np.einsum("ni,nij->nj", eta, process.transition[symbols[:, step]])
        eta = eta / eta.sum(axis=1, keepdims=True)
        beliefs[:, step] = eta
    return beliefs


def next_symbol_distribution(process: HiddenProcess, beliefs: np.ndarray) -> np.ndarray:
    """``P(next symbol | belief)``: the prediction a Bayes-optimal model would make."""

    return np.einsum("...i,aij->...a", beliefs, process.transition)


# --------------------------------------------------------------------------------------
# generate
# --------------------------------------------------------------------------------------


def run_generate(args: argparse.Namespace) -> dict:
    process = PROCESSES[args.process](x=args.x, alpha=args.alpha)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    started = time.perf_counter()
    total = args.sequences + args.holdout
    symbols, states = sample_sequences(process, total, args.length, rng)
    beliefs = belief_states(process, symbols)
    files = {
        "symbols.npy": symbols[: args.sequences],
        "states.npy": states[: args.sequences],
        "beliefs.npy": beliefs[: args.sequences].astype(np.float32),
        "holdout-symbols.npy": symbols[args.sequences :],
        "holdout-states.npy": states[args.sequences :],
        "holdout-beliefs.npy": beliefs[args.sequences :].astype(np.float32),
    }
    for name, value in files.items():
        np.save(output / name, value)
    counts = np.bincount(symbols.ravel(), minlength=process.symbol_count)
    manifest = {
        "schema_version": 1,
        "process": process.to_dict(),
        "seed": int(args.seed),
        "sequences": int(args.sequences),
        "holdout_sequences": int(args.holdout),
        "length": int(args.length),
        "sampling": "initial state from the stationary distribution; joint (symbol, next "
        "state) draws from T[:, state, :]; symbols index the transition matrices",
        "beliefs": "forward algorithm from the stationary prior; float32 [N, L, states]; "
        "entry t is the belief after symbol t",
        "empirical_symbol_frequencies": (counts / counts.sum()).tolist(),
        "files": {
            name: {
                "sha256": sha256_file(output / name),
                "shape": list(value.shape),
                "dtype": str(value.dtype),
            }
            for name, value in files.items()
        },
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(output / "manifest.json", manifest)
    log(
        f"generated {total} x {args.length} {process.name} symbols in {manifest['seconds']}s"
    )
    return manifest


# --------------------------------------------------------------------------------------
# tokens
# --------------------------------------------------------------------------------------


def token_counts(train_bin: Path, vocab_size: int) -> np.ndarray:
    stream = np.memmap(train_bin, dtype="<u2", mode="r")
    return np.bincount(stream, minlength=vocab_size)


def candidate_tokens(
    tokenizer, special_ids: set[int], counts: np.ndarray
) -> list[dict]:
    """Single-id tokens that decode to one printable symbol glyph and round-trip.

    The rule: not a special/added token; decodes to exactly one character in a Unicode
    symbol category (``S*``: script-neutral, no natural-language morphology to teach the
    ghost); printable and not whitespace; re-encodes to the same single id alone and as
    a run of three (so a rendered document re-tokenizes to the ids we inserted).
    """

    candidates = []
    for token_id in range(int(counts.shape[0])):
        if token_id in special_ids:
            continue
        text = tokenizer.decode([token_id], skip_special_tokens=False)
        if len(text) != 1 or not text.isprintable() or text.isspace():
            continue
        category = unicodedata.category(text)
        if not category.startswith("S"):
            continue
        if tokenizer.encode(text, add_special_tokens=False).ids != [token_id]:
            continue
        if tokenizer.encode(text * 3, add_special_tokens=False).ids != [token_id] * 3:
            continue
        candidates.append(
            {
                "id": token_id,
                "text": text,
                "name": unicodedata.name(text, "?"),
                "category": category,
                "corpus_count": int(counts[token_id]),
            }
        )
    candidates.sort(key=lambda item: (item["corpus_count"], item["id"]))
    return candidates


def round_trip_check(tokenizer, ids: list[int], rng: np.random.Generator) -> dict:
    """Encode a random rendered document and require the exact id sequence back."""

    prefix, *emission = ids
    draw = rng.integers(0, len(emission), size=256)
    expected = [prefix] + [emission[int(index)] for index in draw]
    text = tokenizer.decode(expected, skip_special_tokens=False)
    actual = tokenizer.encode(text, add_special_tokens=False).ids
    return {"length": len(expected), "ok": actual == expected, "text_head": text[:24]}


def run_tokens(args: argparse.Namespace) -> dict:
    from tokenizers import Tokenizer

    tokenizer_dir = Path(args.tokenizer)
    tokenizer_file = tokenizer_dir / "tokenizer.json"
    tokenizer = Tokenizer.from_file(str(tokenizer_file))
    added = read_json(tokenizer_file).get("added_tokens", [])
    special_ids = {int(item["id"]) for item in added}
    vocab_size = tokenizer.get_vocab_size(with_added_tokens=True)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    counts = token_counts(Path(args.train_bin), vocab_size)
    np.save(output / "train-token-counts.npy", counts)
    candidates = candidate_tokens(tokenizer, special_ids, counts)
    by_text = {item["text"]: item for item in candidates}
    chosen = []
    for glyph in [args.prefix, *args.emission]:
        if glyph not in by_text:
            raise SystemExit(
                f"{glyph!r} is not a single-id symbol token that round-trips"
            )
        item = by_text[glyph]
        if item["corpus_count"] > args.max_count:
            raise SystemExit(
                f"{glyph!r} occurs {item['corpus_count']} times (> max-count)"
            )
        chosen.append(item)
    if len({item["id"] for item in chosen}) != len(chosen):
        raise SystemExit("prefix and emission tokens must be distinct")
    ids = [item["id"] for item in chosen]
    if args.eos_token_id in ids:
        raise SystemExit("the EOS token cannot be an emission token")
    check = round_trip_check(tokenizer, ids, np.random.default_rng(0))
    if not check["ok"]:
        raise SystemExit("a rendered document does not re-tokenize to its ids")
    mapping = {
        "schema_version": 1,
        "tokenizer": str(tokenizer_dir),
        "tokenizer_sha256": sha256_file(tokenizer_file),
        "train_bin": str(args.train_bin),
        "train_tokens": int(counts.sum()),
        "vocab_size": int(vocab_size),
        "eos_token_id": int(args.eos_token_id),
        "prefix": chosen[0],
        "emission": [dict(item, symbol=index) for index, item in enumerate(chosen[1:])],
        "document_format": "[prefix] + one emission token per symbol + [eos]",
        "selection_rule": candidate_tokens.__doc__.strip(),
        "round_trip": check,
        "candidates": candidates,
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(output / "mess3-tokens.json", mapping)
    for item in chosen:
        log(
            f"{item['text']} id={item['id']} {item['name']} count={item['corpus_count']}"
        )
    return mapping


# --------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------


def render_documents(
    symbols: np.ndarray, emission_ids: list[int], prefix_id: int, eos_id: int
) -> np.ndarray:
    """``[N, L] symbols -> [N, L + 2] uint16`` documents: prefix, tokens, EOS."""

    table = np.asarray(emission_ids, dtype=np.uint16)
    count, length = symbols.shape
    documents = np.empty((count, length + 2), dtype=np.uint16)
    documents[:, 0] = prefix_id
    documents[:, 1:-1] = table[symbols]
    documents[:, -1] = eos_id
    return documents


def document_bounds(stream: np.ndarray, eos_id: int) -> tuple[np.ndarray, np.ndarray]:
    """Start (inclusive) and end (exclusive, after EOS) of each document in a stream."""

    ends = np.flatnonzero(stream == eos_id) + 1
    if ends.size == 0 or ends[-1] != stream.shape[0]:
        raise ValueError("stream must end with EOS")
    starts = np.concatenate(([0], ends[:-1]))
    return starts, ends


def synthetic_document_count(
    corpus_tokens: int, tokens_per_document: int, fraction: float
) -> int:
    """Documents needed so that synthetic tokens are ``fraction`` of the mixed total."""

    if not 0.0 < fraction < 1.0:
        raise ValueError("fraction must be in (0, 1)")
    return round(fraction * corpus_tokens / ((1.0 - fraction) * tokens_per_document))


def plan_insertions(
    document_count: int, synthetic_count: int, rng: np.random.Generator
) -> np.ndarray:
    """Slot for each synthetic document: insert before v1 document ``k`` (``k == n`` appends)."""

    return rng.integers(0, document_count + 1, size=synthetic_count)


def weave_stream(
    stream: np.ndarray,
    documents: np.ndarray,
    slots: np.ndarray,
    output: Path,
    eos_id: int = DEFAULT_EOS_TOKEN_ID,
) -> dict:
    """Write ``stream`` with ``documents`` inserted at their slots; return the plan.

    The v1 documents keep their order and bytes; synthetic documents sharing a slot are
    written in index order before v1 document ``slot`` (or at the end). The returned
    dictionary lists every insertion group with its offsets in both streams and the
    SHA-256 of the written file.
    """

    starts, ends = document_bounds(stream, eos_id)
    order = np.argsort(slots, kind="stable")
    groups: dict[int, list[int]] = {}
    for index in order:
        groups.setdefault(int(slots[index]), []).append(int(index))
    digest = hashlib.sha256()
    insertions = []
    offset = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        for slot in range(starts.shape[0] + 1):
            members = groups.get(slot)
            if members:
                block = np.ascontiguousarray(documents[members]).astype("<u2").tobytes()
                handle.write(block)
                digest.update(block)
                v1_offset = (
                    int(starts[slot])
                    if slot < starts.shape[0]
                    else int(stream.shape[0])
                )
                insertions.append(
                    {
                        "slot": slot,
                        "v1_offset": v1_offset,
                        "v11_offset": offset,
                        "documents": members,
                        "tokens": int(documents.shape[1]) * len(members),
                    }
                )
                offset += int(documents.shape[1]) * len(members)
            if slot < starts.shape[0]:
                block = (
                    np.ascontiguousarray(stream[starts[slot] : ends[slot]])
                    .astype("<u2")
                    .tobytes()
                )
                handle.write(block)
                digest.update(block)
                offset += int(ends[slot] - starts[slot])
    os.replace(temporary, output)
    return {
        "tokens": offset,
        "sha256": digest.hexdigest(),
        "v1_documents": int(starts.shape[0]),
        "insertions": insertions,
    }


def verify_weave(
    stream: np.ndarray, documents: np.ndarray, plan: dict, output: Path
) -> dict:
    """Re-read the woven stream and check every v1 byte and every insertion."""

    woven = np.memmap(output, dtype="<u2", mode="r")
    if woven.shape[0] != plan["tokens"]:
        raise ValueError(
            f"woven stream has {woven.shape[0]} tokens, expected {plan['tokens']}"
        )
    inserted = 0
    for group in plan["insertions"]:
        start = group["v11_offset"]
        block = documents[group["documents"]].reshape(-1)
        if not np.array_equal(woven[start : start + block.shape[0]], block):
            raise ValueError(f"insertion at {start} does not match its documents")
        inserted += block.shape[0]
    # Walk both streams in step: every v1 segment between insertions must be identical.
    cursor_v1 = 0
    cursor_v11 = 0
    compared = 0
    for group in plan["insertions"] + [
        {"v1_offset": stream.shape[0], "v11_offset": plan["tokens"], "tokens": 0}
    ]:
        length = group["v1_offset"] - cursor_v1
        if length:
            if not np.array_equal(
                woven[cursor_v11 : cursor_v11 + length],
                stream[cursor_v1 : cursor_v1 + length],
            ):
                raise ValueError(f"v1 bytes differ at v1 offset {cursor_v1}")
            compared += length
        cursor_v1 = group["v1_offset"]
        cursor_v11 = group["v11_offset"] + group["tokens"]
    if compared != stream.shape[0] or compared + inserted != plan["tokens"]:
        raise ValueError("coverage mismatch while verifying the woven stream")
    return {
        "v1_tokens_identical": int(compared),
        "synthetic_tokens": int(inserted),
        "ok": True,
    }


def derive_validation_report(v1_report: dict, train: dict, synthetic: dict) -> dict:
    """The v1 validation report with the train split replaced by the woven stream."""

    report = json.loads(json.dumps(v1_report))
    split = report["splits"]["train"]
    added_documents = synthetic["documents"]
    added_source_tokens = synthetic["documents"] * (
        synthetic["tokens_per_document"] - 1
    )
    split["documents"] += added_documents
    for key in ("source_tokens", "dataset_source_tokens", "tokenized_source_tokens"):
        split[key] += added_source_tokens
    split["eos_tokens"] += added_documents
    split["tokens_including_eos"] = train["tokens"]
    split["bytes"] = train["tokens"] * 2
    split["sha256"] = train["sha256"]
    split["minimum_token_id"] = min(
        split["minimum_token_id"], synthetic["minimum_token_id"]
    )
    split["maximum_token_id"] = max(
        split["maximum_token_id"], synthetic["maximum_token_id"]
    )
    report["selected_documents"] += added_documents
    report["derived_from"] = {
        "corpus": "hghost curated tokens v1",
        "train_sha256": v1_report["splits"]["train"]["sha256"],
        "synthetic": synthetic,
    }
    return report


def run_build(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    generated = Path(args.generated)
    generated_manifest = read_json(generated / "manifest.json")
    mapping = read_json(args.tokens)
    eos_id = int(mapping["eos_token_id"])
    emission_ids = [int(item["id"]) for item in mapping["emission"]]
    prefix_id = int(mapping["prefix"]["id"])
    train_bin = Path(args.train_bin)
    validation_bin = (
        Path(args.validation_bin)
        if args.validation_bin
        else train_bin.with_name("validation.bin")
    )
    report_path = (
        Path(args.validation_report)
        if args.validation_report
        else train_bin.with_name("validation-report.json")
    )
    v1_report = read_json(report_path)
    stream = np.memmap(train_bin, dtype="<u2", mode="r")
    if stream.shape[0] != v1_report["splits"]["train"]["tokens_including_eos"]:
        raise SystemExit(
            "train.bin does not match the token count in its validation report"
        )

    pool = np.load(generated / "symbols.npy")
    length = int(pool.shape[1])
    tokens_per_document = length + 2
    count = synthetic_document_count(
        int(stream.shape[0]), tokens_per_document, args.fraction
    )
    if count > pool.shape[0]:
        raise SystemExit(
            f"need {count} synthetic documents but the pool has {pool.shape[0]}"
        )
    documents = render_documents(pool[:count], emission_ids, prefix_id, eos_id)
    slots = plan_insertions(
        int(np.count_nonzero(stream == eos_id)), count, np.random.default_rng(args.seed)
    )

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    log(f"weaving {count} documents x {tokens_per_document} tokens into {train_bin}")
    plan = weave_stream(stream, documents, slots, output / "train.bin", eos_id)
    verification = verify_weave(stream, documents, plan, output / "train.bin")
    log(
        f"verified {verification['v1_tokens_identical']} v1 tokens identical outside insertions"
    )

    validation_sha = sha256_file(validation_bin)
    if validation_sha != v1_report["splits"]["validation"]["sha256"]:
        raise SystemExit("validation.bin does not match the sha256 in the v1 report")
    shutil.copyfile(validation_bin, output / "validation.bin")

    holdout = np.load(generated / "holdout-symbols.npy")
    holdout_documents = render_documents(holdout, emission_ids, prefix_id, eos_id)
    (output / "mess3-validation.bin").write_bytes(
        holdout_documents.astype("<u2").tobytes()
    )
    np.save(output / "mess3-validation-symbols.npy", holdout)
    np.save(
        output / "mess3-validation-beliefs.npy",
        np.load(generated / "holdout-beliefs.npy"),
    )

    synthetic = {
        "process": generated_manifest["process"],
        "generated_manifest_sha256": sha256_file(generated / "manifest.json"),
        "generated_seed": generated_manifest["seed"],
        "documents": count,
        "pool_documents": int(pool.shape[0]),
        "symbols_per_document": length,
        "tokens_per_document": tokens_per_document,
        "tokens": count * tokens_per_document,
        "fraction_requested": float(args.fraction),
        "fraction_actual": count * tokens_per_document / plan["tokens"],
        "prefix_token_id": prefix_id,
        "emission_token_ids": emission_ids,
        "eos_token_id": eos_id,
        "minimum_token_id": int(min([prefix_id, eos_id, *emission_ids])),
        "maximum_token_id": int(max([prefix_id, eos_id, *emission_ids])),
        "insertion_seed": int(args.seed),
        "insertion_rule": "slot ~ Uniform{0..v1_documents} per synthetic document (seeded); "
        "documents sharing a slot are written in index order before v1 document slot",
    }
    report = derive_validation_report(v1_report, plan, synthetic)
    write_json(output / "validation-report.json", report)
    files = {
        name: {
            "sha256": sha256_file(output / name),
            "bytes": (output / name).stat().st_size,
        }
        for name in (
            "train.bin",
            "validation.bin",
            "mess3-validation.bin",
            "mess3-validation-symbols.npy",
            "mess3-validation-beliefs.npy",
            "validation-report.json",
        )
    }
    if files["train.bin"]["sha256"] != plan["sha256"]:
        raise SystemExit("train.bin hash changed between writing and hashing")
    manifest = {
        "schema_version": 1,
        "corpus": "hghost curated tokens v1.1: v1 train stream + Mess3 slice",
        "format": v1_report.get(
            "format", "contiguous token IDs; EOS after every document"
        ),
        "dtype": "little-endian uint16",
        "tokenizer": v1_report["tokenizer"],
        "vocab_size": v1_report["vocab_size"],
        "eos_token_id": eos_id,
        "v1": {
            "train_bin": str(train_bin),
            "train_sha256": v1_report["splits"]["train"]["sha256"],
            "train_tokens": int(stream.shape[0]),
            "train_documents": plan["v1_documents"],
            "validation_sha256": validation_sha,
            "validation_report": str(report_path),
        },
        "tokens_mapping": {
            "path": str(args.tokens),
            "sha256": sha256_file(Path(args.tokens)),
        },
        "synthetic": synthetic,
        "holdout": {
            "documents": int(holdout.shape[0]),
            "tokens": int(holdout_documents.size),
            "files": [
                "mess3-validation.bin",
                "mess3-validation-symbols.npy",
                "mess3-validation-beliefs.npy",
            ],
        },
        "splits": {
            "train": {
                "path": "train.bin",
                "tokens_including_eos": plan["tokens"],
                **files["train.bin"],
            },
            "validation": {
                "path": "validation.bin",
                "tokens_including_eos": v1_report["splits"]["validation"][
                    "tokens_including_eos"
                ],
                **files["validation.bin"],
            },
        },
        "files": files,
        "verification": verification,
        "insertions": plan["insertions"],
        "seconds": round(time.perf_counter() - started, 3),
    }
    write_json(output / "manifest.json", manifest)
    write_json(
        output / "dataset-metadata.json",
        {
            "title": KAGGLE_DATASET_TITLE,
            "id": args.kaggle_id,
            "subtitle": "v1 curated uint16 streams with a 2% authored Mess3 hidden-Markov slice",
            "description": (
                "The hghost curated token corpus v1 (train.bin) with synthetic documents from "
                "the Mess3 hidden Markov process (Shai, Riechers et al. 2024) woven in at "
                f"document boundaries so that {synthetic['fraction_actual'] * 100:.2f}% of the "
                "training tokens are synthetic; validation.bin is unchanged from v1. The "
                "synthetic slice, its held-out sequences (mess3-validation.bin) and their exact "
                "Bayesian belief states are CC0. The corpus portion carries the same caveats as "
                "v1: token streams only, no source text or paths, and mixed or unknown "
                "source-document licensing. manifest.json records the process parameters, the "
                "emission tokens, every insertion offset, and hashes."
            ),
            # Kaggle's license is dataset-wide and the bulk of this dataset is the v1
            # corpus, whose source-document licensing is mixed or unknown; only the
            # synthetic slice and the belief files are CC0 (stated in the description).
            "licenses": [{"name": "unknown"}],
        },
    )
    (output / "README.md").write_text(
        "# H Ghost corpus v1.1 + Mess3 slice\n\n"
        "- `train.bin`: v1 train stream with synthetic Mess3 documents inserted at document "
        "boundaries (uint16 little-endian, EOS after every document).\n"
        "- `validation.bin`: byte-identical to v1.\n"
        "- `validation-report.json`: v1 schema; `splits.train.sha256` and "
        "`splits.validation.sha256` are what the TPU kernels verify.\n"
        "- `mess3-validation.bin`: held-out synthetic documents (never in train.bin) with their "
        "symbols and exact belief states in `mess3-validation-{symbols,beliefs}.npy`.\n"
        "- `manifest.json`: process matrices, emission tokens, insertion offsets, hashes.\n\n"
        "Licensing: the synthetic Mess3 slice, `mess3-validation.bin` and the belief files "
        "are CC0-1.0. The corpus portion carries the same caveats as v1 (token streams "
        "only; mixed or unknown source-document licensing).\n",
        encoding="utf-8",
    )
    log(
        f"train.bin: {plan['tokens']} tokens, {count} synthetic documents "
        f"({synthetic['fraction_actual'] * 100:.3f}%), sha256 {plan['sha256']}"
    )
    return manifest


# --------------------------------------------------------------------------------------
# probe mathematics (numpy only; shared with beliefgeo_jax)
# --------------------------------------------------------------------------------------


class RidgeProbe:
    """Affine ridge regression ``Y ~ X W + c`` in the primal or dual form.

    The Gram matrix is independent of the targets, so one instance serves the real and
    the shuffled targets and every ridge strength. The ridge is relative to the mean
    eigenvalue of the Gram matrix (``trace / rank``).
    """

    def __init__(self, features: np.ndarray):
        features = np.asarray(features, dtype=np.float32)
        self.mean = features.mean(axis=0, dtype=np.float64).astype(np.float32)
        self.centered = features - self.mean
        count, width = self.centered.shape
        self.dual = width > count
        if self.dual:
            gram = self.centered @ self.centered.T
        else:
            gram = self.centered.T @ self.centered
        self.gram = gram.astype(np.float64)
        self.scale = float(np.trace(self.gram)) / max(1, min(count, width))

    def fit(self, targets: np.ndarray, ridge: float) -> tuple[np.ndarray, np.ndarray]:
        targets = np.asarray(targets, dtype=np.float64)
        target_mean = targets.mean(axis=0)
        centered = targets - target_mean
        regularized = self.gram + np.eye(self.gram.shape[0]) * (ridge * self.scale)
        if self.dual:
            alpha = np.linalg.solve(regularized, centered)
            weights = self.centered.T.astype(np.float64) @ alpha
        else:
            weights = np.linalg.solve(
                regularized, self.centered.T.astype(np.float64) @ centered
            )
        return weights, target_mean

    def predict(
        self, features: np.ndarray, weights: np.ndarray, target_mean: np.ndarray
    ) -> np.ndarray:
        centered = np.asarray(features, dtype=np.float32) - self.mean
        return centered.astype(np.float64) @ weights + target_mean


def r2_score(targets: np.ndarray, predictions: np.ndarray) -> tuple[float, list[float]]:
    """Pooled and per-component coefficient of determination on the given set."""

    residual = np.square(targets - predictions).sum(axis=0)
    total = np.square(targets - targets.mean(axis=0)).sum(axis=0)
    pooled = 1.0 - float(residual.sum()) / float(total.sum())
    per_component = (1.0 - residual / np.where(total > 0, total, np.nan)).tolist()
    return pooled, per_component


def probe_features(
    features: np.ndarray,
    targets: np.ndarray,
    groups: np.ndarray,
    test_mask: np.ndarray,
    *,
    ridges: tuple[float, ...] = DEFAULT_RIDGES,
    shuffle_seed: int = 0,
    validation_fraction: float = 0.2,
) -> dict:
    """Fit ``targets ~ features`` with the ridge chosen on held-out *sequences*.

    Rows belong to sequences (``groups``); ``test_mask`` marks test rows. The ridge
    strength is chosen on a validation subset of training sequences, the probe is refit
    on all training rows, and metrics are reported on the test rows. The shuffled
    control permutes the target rows (seeded) and runs the identical procedure.
    """

    train_rows = np.flatnonzero(~test_mask)
    test_rows = np.flatnonzero(test_mask)
    train_groups = np.unique(groups[train_rows])
    validation_count = max(1, round(validation_fraction * train_groups.shape[0]))
    validation_groups = train_groups[-validation_count:]
    validation_mask = np.isin(groups[train_rows], validation_groups)
    fit_rows = train_rows[~validation_mask]
    validation_rows = train_rows[validation_mask]

    selector = RidgeProbe(features[fit_rows])
    full = RidgeProbe(features[train_rows])
    permutation = np.random.default_rng(shuffle_seed).permutation(targets.shape[0])
    outcomes = {}
    for name, current in (("real", targets), ("shuffled", targets[permutation])):
        validation_scores = {}
        for ridge in ridges:
            weights, mean = selector.fit(current[fit_rows], ridge)
            predicted = selector.predict(features[validation_rows], weights, mean)
            validation_scores[ridge] = r2_score(current[validation_rows], predicted)[0]
        best = max(validation_scores, key=validation_scores.get)
        weights, mean = full.fit(current[train_rows], best)
        predicted = full.predict(features[test_rows], weights, mean)
        pooled, per_component = r2_score(current[test_rows], predicted)
        outcomes[name] = {
            "ridge": best,
            "validation_r2_by_ridge": {
                str(key): float(value) for key, value in validation_scores.items()
            },
            "r2": pooled,
            "r2_per_component": per_component,
            "mse": float(np.mean(np.square(current[test_rows] - predicted))),
            "predictions": predicted.astype(np.float32),
        }
    return {
        "rows": int(features.shape[0]),
        "width": int(features.shape[1]),
        "train_rows": int(train_rows.shape[0]),
        "test_rows": int(test_rows.shape[0]),
        "real": outcomes["real"],
        "shuffled": outcomes["shuffled"],
    }


def simplex_xy(beliefs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Barycentric ``(b0, b1, b2)`` to the plane: vertices (0,0), (1,0), (1/2, sqrt3/2)."""

    beliefs = np.asarray(beliefs, dtype=np.float64)
    return beliefs[..., 1] + 0.5 * beliefs[..., 2], SQRT3_2 * beliefs[..., 2]


# --------------------------------------------------------------------------------------
# probe (driver: prepares inputs, runs the JAX worker, plots)
# --------------------------------------------------------------------------------------


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def probe_inputs(
    symbols: np.ndarray,
    beliefs: np.ndarray,
    stationary: np.ndarray,
    mapping: dict,
    *,
    sequences: int,
    length: int,
    test_fraction: float,
) -> dict[str, np.ndarray]:
    """Token rows, per-position belief targets, validity and the sequence-level split."""

    if sequences > symbols.shape[0]:
        raise ValueError(f"only {symbols.shape[0]} held-out sequences are available")
    if length - 1 > symbols.shape[1]:
        raise ValueError(
            "probe length exceeds the generated sequence length plus prefix"
        )
    emission_ids = [int(item["id"]) for item in mapping["emission"]]
    rendered = render_documents(
        symbols[:sequences, : length - 1], emission_ids, int(mapping["prefix"]["id"]), 0
    )
    rows = rendered[:, :-1].astype(np.int32)
    targets = np.empty((sequences, length, beliefs.shape[-1]), dtype=np.float32)
    targets[:, 0] = stationary
    targets[:, 1:] = beliefs[:sequences, : length - 1]
    valid = np.ones((sequences, length), dtype=bool)
    valid[:, 0] = False
    test = np.zeros(sequences, dtype=bool)
    test[sequences - max(1, round(test_fraction * sequences)) :] = True
    return {"rows": rows, "targets": targets, "valid": valid, "test": test}


def recency_features(symbols: np.ndarray, k: int, symbol_count: int) -> np.ndarray:
    """One-hot of the last ``k`` symbols at every position: ``[N, L, k * (S + 1)]``.

    Lag ``j`` (0 = the current symbol) uses ``S + 1`` classes, the extra class marking
    lags that fall before the start of the sequence. A linear probe on these features
    is the pure-recency baseline for the belief state.
    """

    count, length = symbols.shape
    features = np.zeros((count, length, k, symbol_count + 1), dtype=np.float32)
    for lag in range(k):
        classes = np.full((count, length), symbol_count, dtype=np.int64)
        classes[:, lag:] = symbols[:, : length - lag]
        np.put_along_axis(features[:, :, lag, :], classes[..., None], 1.0, axis=-1)
    return features.reshape(count, length, k * (symbol_count + 1))


def recency_baselines(
    inputs: dict, mapping: dict, ks: tuple[int, ...], *, ridges, seed: int
) -> tuple[list[dict], dict[str, np.ndarray]]:
    """Linear probes from the last-k-symbol one-hot to the belief on the same split.

    Rows are ordered like the worker's (sequence-major over positions 1..T-1), so the
    returned ``truth`` must equal the worker's and is checked by the caller.
    """

    rows, targets, valid, test = (
        inputs["rows"],
        inputs["targets"],
        inputs["valid"],
        inputs["test"],
    )
    if valid[:, 0].any() or not valid[:, 1:].all():
        raise ValueError("expected exactly the prefix position to be invalid")
    lookup = np.full(int(rows.max()) + 1, -1, dtype=np.int64)
    for item in mapping["emission"]:
        lookup[int(item["id"])] = int(item["symbol"])
    symbols = lookup[rows[:, 1:]]
    if np.any(symbols < 0):
        raise ValueError("rows contain non-emission tokens after the prefix")
    count, length = symbols.shape
    groups = np.repeat(np.arange(count), length)
    test_rows = test[groups]
    flat_targets = targets[:, 1:].reshape(-1, targets.shape[-1])
    outcomes: list[dict] = []
    predictions = {"truth": flat_targets[test_rows]}
    for k in ks:
        features = recency_features(symbols, k, len(mapping["emission"]))
        outcome = probe_features(
            features.reshape(count * length, -1),
            flat_targets,
            groups,
            test_rows,
            ridges=ridges,
            shuffle_seed=seed,
        )
        predictions[f"recency/k{k}"] = outcome["real"].pop("predictions")
        outcome["shuffled"].pop("predictions")
        outcomes.append({"name": f"recency k={k}", "k": int(k), **outcome})
    return outcomes, predictions


def write_plots(results: dict, predictions: dict, output: Path) -> dict[str, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    truth = predictions["truth"]
    colors = np.clip(truth, 0.0, 1.0)
    layers = results["residual"]
    baselines = results.get("baselines", [])
    names = [entry["name"] for entry in layers]
    paths = {}

    def draw_simplex(axis, beliefs, title):
        axis.plot(
            [0, 1, 0.5, 0], [0, 0, SQRT3_2, 0], color="#C9CDD3", linewidth=0.8, zorder=0
        )
        x, y = simplex_xy(beliefs)
        axis.scatter(x, y, s=1.2, c=colors, alpha=0.7, linewidths=0, rasterized=True)
        axis.set_title(title, fontsize=8, pad=3)
        axis.set_aspect("equal")
        axis.set_xlim(-0.15, 1.15)
        axis.set_ylim(-0.15, SQRT3_2 + 0.15)
        axis.axis("off")

    panels = [("true belief (test)", truth)]
    panels += [
        (
            f"recency k={entry['k']}  R²={entry['real']['r2']:.2f}",
            predictions[f"recency/k{entry['k']}"],
        )
        for entry in baselines
    ]
    panels += [
        (
            f"{entry['name']}  R²={entry['real']['r2']:.2f}",
            predictions[f"residual/{entry['name']}"],
        )
        for entry in layers
    ]
    columns = 5
    rows_count = int(np.ceil(len(panels) / columns))
    figure, axes = plt.subplots(
        rows_count, columns, figsize=(2.4 * columns, 2.3 * rows_count)
    )
    axes = np.atleast_2d(axes).ravel()
    for axis, (title, beliefs) in zip(axes, panels):
        draw_simplex(axis, beliefs, title)
    for axis in axes[len(panels) :]:
        axis.axis("off")
    figure.suptitle(
        f"{results['checkpoint_name']}, {results.get('process_label', '')}: probe predictions on "
        "the belief simplex (colour = true belief as RGB)",
        fontsize=9,
    )
    figure.tight_layout()
    paths["simplex"] = str(output / "probe-simplex.png")
    figure.savefig(paths["simplex"], dpi=170)
    plt.close(figure)

    best = max(layers, key=lambda entry: entry["real"]["r2"])
    figure, axes = plt.subplots(1, 3, figsize=(13, 4.4))
    draw_simplex(axes[0], truth, "true belief (test sequences)")
    if baselines:
        top = max(baselines, key=lambda entry: entry["real"]["r2"])
        draw_simplex(
            axes[1],
            predictions[f"recency/k{top['k']}"],
            f"recency baseline k={top['k']}  R²={top['real']['r2']:.3f}",
        )
    else:
        axes[1].axis("off")
    draw_simplex(
        axes[2],
        predictions[f"residual/{best['name']}"],
        f"predicted from {best['name']}  R²={best['real']['r2']:.3f}",
    )
    figure.suptitle(
        f"{results['checkpoint_name']}, {results.get('process_label', '')}: best residual layer",
        fontsize=10,
    )
    figure.tight_layout()
    paths["simplex_best"] = str(output / "probe-simplex-best.png")
    figure.savefig(paths["simplex_best"], dpi=200)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8.5, 4))
    positions = np.arange(len(names))
    axis.plot(
        positions,
        [entry["real"]["r2"] for entry in layers],
        color="#2F6FBA",
        linewidth=2,
        marker="o",
        markersize=4,
        label="residual stream",
    )
    axis.plot(
        positions,
        [entry["shuffled"]["r2"] for entry in layers],
        color="#2F6FBA",
        linewidth=1.2,
        linestyle="--",
        marker="o",
        markersize=3,
        alpha=0.6,
        label="residual, shuffled targets",
    )
    if results.get("ssm"):
        ssm_positions = [names.index(entry["name"]) for entry in results["ssm"]]
        axis.plot(
            ssm_positions,
            [entry["real"]["r2"] for entry in results["ssm"]],
            color="#D9822B",
            linewidth=2,
            marker="s",
            markersize=4,
            label="Mamba SSM state",
        )
        axis.plot(
            ssm_positions,
            [entry["shuffled"]["r2"] for entry in results["ssm"]],
            color="#D9822B",
            linewidth=1.2,
            linestyle="--",
            marker="s",
            markersize=3,
            alpha=0.6,
            label="SSM state, shuffled targets",
        )
    for index, entry in enumerate(baselines):
        axis.axhline(
            entry["real"]["r2"], color="#8A8F98", linestyle=":", linewidth=1, zorder=0
        )
        axis.text(
            len(names) - 0.6 - 4.0 * index,
            entry["real"]["r2"] + 0.012,
            f"recency k={entry['k']}",
            fontsize=7,
            color="#8A8F98",
            ha="right",
        )
    axis.set_xticks(positions)
    axis.set_xticklabels(names, rotation=60, fontsize=7)
    axis.set_ylabel("test R² (pooled over the 3 belief components)")
    axis.set_ylim(min(-0.1, axis.get_ylim()[0]), 1.0)
    axis.axhline(0.0, color="#C9CDD3", linewidth=0.8, zorder=0)
    axis.grid(axis="y", color="#E6E8EB", linewidth=0.6)
    for side in ("top", "right"):
        axis.spines[side].set_visible(False)
    axis.legend(frameon=False, fontsize=8, loc="lower left")
    axis.set_title(
        f"{results['checkpoint_name']}, {results.get('process_label', '')}: belief-state probe by layer",
        fontsize=10,
    )
    figure.tight_layout()
    paths["r2"] = str(output / "probe-r2.png")
    figure.savefig(paths["r2"], dpi=170)
    plt.close(figure)
    return paths


def results_table(results: dict) -> str:
    lines = [
        "| features | R² | shuffled R² | MSE | SSM state R² | SSM shuffled R² |",
        "|---|---|---|---|---|---|",
    ]
    for entry in results.get("baselines", []):
        lines.append(
            f"| {entry['name']} (one-hot) | {entry['real']['r2']:.3f} | "
            f"{entry['shuffled']['r2']:.3f} | {entry['real']['mse']:.4f} | – | – |"
        )
    ssm = {entry["name"]: entry for entry in results.get("ssm", [])}
    for entry in results["residual"]:
        state = ssm.get(entry["name"])
        lines.append(
            f"| residual {entry['name']} | {entry['real']['r2']:.3f} | "
            f"{entry['shuffled']['r2']:.3f} | {entry['real']['mse']:.4f} | "
            + (
                f"{state['real']['r2']:.3f} | {state['shuffled']['r2']:.3f} |"
                if state
                else "– | – |"
            )
        )
    return "\n".join(lines) + "\n"


def run_probe(args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    generated = Path(args.generated)
    generated_manifest = read_json(generated / "manifest.json")
    mapping = read_json(args.tokens)
    process = HiddenProcess(
        generated_manifest["process"]["name"],
        np.asarray(generated_manifest["process"]["transition"]),
        generated_manifest["process"]["parameters"],
    )
    symbols = np.load(generated / "holdout-symbols.npy")
    beliefs = np.load(generated / "holdout-beliefs.npy")
    inputs = probe_inputs(
        symbols,
        beliefs,
        process.stationary,
        mapping,
        sequences=args.sequences,
        length=args.length,
        test_fraction=args.test_fraction,
    )
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    input_path = output / "probe-input.npz"
    np.savez(input_path, **inputs)
    results_path = output / "probe-results.json"
    predictions_path = output / "probe-predictions.npz"
    if not (results_path.is_file() and predictions_path.is_file()) or args.force:
        command = [
            str(args.jax_python),
            "-m",
            "hghost.beliefgeo_jax",
            "--checkpoint",
            str(args.checkpoint),
            "--input",
            str(input_path),
            "--output",
            str(output),
            "--batch",
            str(args.batch),
            "--ssm-stride",
            str(args.ssm_stride),
            "--ssm-layers",
            args.ssm_layers,
            "--ridges",
            ",".join(str(value) for value in args.ridges),
            "--seed",
            str(args.seed),
        ]
        env = dict(os.environ)
        env["PYTHONPATH"] = str(package_root()) + (
            os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
        )
        env.setdefault("JAX_PLATFORM_NAME", "cpu")
        log("run " + " ".join(command))
        subprocess.run(command, check=True, env=env)
    results = read_json(results_path)
    with np.load(predictions_path) as archive:
        predictions = {key: archive[key] for key in archive.files}
    baselines, baseline_predictions = recency_baselines(
        inputs, mapping, tuple(args.recency), ridges=tuple(args.ridges), seed=args.seed
    )
    if not np.allclose(baseline_predictions.pop("truth"), predictions["truth"]):
        raise SystemExit("baseline rows are not aligned with the worker's rows")
    predictions.update(baseline_predictions)
    results["baselines"] = baselines
    results["process"] = generated_manifest["process"]
    parameters = generated_manifest["process"]["parameters"]
    results["process_label"] = (
        generated_manifest["process"]["name"]
        + " "
        + ", ".join(f"{key}={value}" for key, value in parameters.items())
    )
    results["generated"] = str(generated)
    paths = write_plots(results, predictions, output)
    table = results_table(results)
    (output / "probe-table.md").write_text(table, encoding="utf-8")
    results["plots"] = paths
    results["driver_seconds"] = round(time.perf_counter() - started, 3)
    write_json(results_path, results)
    print(table)
    return results


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser(
        "generate", help="sample a hidden process and its exact beliefs"
    )
    generate.add_argument("--process", choices=sorted(PROCESSES), default="mess3")
    generate.add_argument(
        "--x", type=float, default=DEFAULT_X, help="state-change probability"
    )
    generate.add_argument(
        "--alpha",
        type=float,
        default=DEFAULT_ALPHA,
        help="P(symbol = destination label)",
    )
    generate.add_argument("--sequences", type=int, default=16000)
    generate.add_argument(
        "--holdout", type=int, default=256, help="extra held-out sequences for probing"
    )
    generate.add_argument("--length", type=int, default=512)
    generate.add_argument("--seed", type=int, default=0)
    generate.add_argument("--output", type=Path, required=True)

    tokens = commands.add_parser("tokens", help="choose rare single-id emission tokens")
    tokens.add_argument(
        "--tokenizer", type=Path, required=True, help="directory with tokenizer.json"
    )
    tokens.add_argument(
        "--train-bin", type=Path, default=Path("artifacts/tokenized/train.bin")
    )
    tokens.add_argument("--output", type=Path, required=True)
    tokens.add_argument(
        "--emission", nargs=3, default=list(DEFAULT_EMISSION_GLYPHS), metavar="GLYPH"
    )
    tokens.add_argument("--prefix", default=DEFAULT_PREFIX_GLYPH, metavar="GLYPH")
    tokens.add_argument(
        "--max-count", type=int, default=1000, help="maximum corpus count per token"
    )
    tokens.add_argument("--eos-token-id", type=int, default=DEFAULT_EOS_TOKEN_ID)

    build = commands.add_parser(
        "build", help="weave the synthetic documents into the v1 stream"
    )
    build.add_argument("--generated", type=Path, required=True)
    build.add_argument("--tokens", type=Path, required=True, help="mess3-tokens.json")
    build.add_argument(
        "--train-bin", type=Path, default=Path("artifacts/tokenized/train.bin")
    )
    build.add_argument(
        "--validation-bin",
        type=Path,
        help="defaults to validation.bin beside train.bin",
    )
    build.add_argument(
        "--validation-report",
        type=Path,
        help="defaults to validation-report.json beside train.bin",
    )
    build.add_argument(
        "--fraction",
        type=float,
        default=0.02,
        help="synthetic share of the mixed stream",
    )
    build.add_argument("--seed", type=int, default=0)
    build.add_argument(
        "--output", type=Path, default=Path("artifacts/beliefgeo/corpus-v1.1-mess3")
    )
    build.add_argument("--kaggle-id", default=KAGGLE_DATASET_ID)

    probe = commands.add_parser(
        "probe", help="linear probes from activations to the belief simplex"
    )
    probe.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
        help="Hugging Face checkpoint directory",
    )
    probe.add_argument("--generated", type=Path, required=True)
    probe.add_argument("--tokens", type=Path, required=True, help="mess3-tokens.json")
    probe.add_argument("--output", type=Path, required=True)
    probe.add_argument(
        "--sequences", type=int, default=64, help="held-out sequences to run"
    )
    probe.add_argument(
        "--length", type=int, default=512, help="tokens per row including the prefix"
    )
    probe.add_argument("--test-fraction", type=float, default=0.2)
    probe.add_argument("--batch", type=int, default=8)
    probe.add_argument(
        "--ssm-stride",
        type=int,
        default=16,
        help="probe the SSM state every N positions",
    )
    probe.add_argument(
        "--ssm-layers",
        default="all",
        help="comma-separated layer indices, 'all' or 'none'",
    )
    probe.add_argument("--ridges", type=float, nargs="+", default=list(DEFAULT_RIDGES))
    probe.add_argument(
        "--seed", type=int, default=0, help="shuffled-control permutation seed"
    )
    probe.add_argument("--jax-python", type=Path, default=DEFAULT_JAX_PYTHON)
    probe.add_argument(
        "--recency",
        type=int,
        nargs="+",
        default=[1, 4, 16],
        help="last-k-symbol one-hot baselines",
    )
    probe.add_argument(
        "--force", action="store_true", help="recompute even if worker outputs exist"
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    runners = {
        "generate": run_generate,
        "tokens": run_tokens,
        "build": run_build,
        "probe": run_probe,
    }
    runners[args.command](args)


if __name__ == "__main__":
    main()
