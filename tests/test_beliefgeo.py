import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from hghost.beliefgeo import (
    DEFAULT_EOS_TOKEN_ID,
    HiddenProcess,
    belief_states,
    derive_validation_report,
    document_bounds,
    mess3,
    next_symbol_distribution,
    plan_insertions,
    probe_features,
    probe_inputs,
    recency_features,
    render_documents,
    sample_sequences,
    simplex_xy,
    synthetic_document_count,
    verify_weave,
    weave_stream,
)

EOS = DEFAULT_EOS_TOKEN_ID


def test_mess3_matches_the_paper_matrices() -> None:
    transition = mess3(0.05, 0.85).transition
    expected = np.array(
        [
            [
                [0.765, 0.00375, 0.00375],
                [0.0425, 0.0675, 0.00375],
                [0.0425, 0.00375, 0.0675],
            ],
            [
                [0.0675, 0.0425, 0.00375],
                [0.00375, 0.765, 0.00375],
                [0.00375, 0.0425, 0.0675],
            ],
            [
                [0.0675, 0.00375, 0.0425],
                [0.00375, 0.0675, 0.0425],
                [0.00375, 0.00375, 0.765],
            ],
        ]
    )
    np.testing.assert_allclose(transition, expected, atol=1e-15)


def test_mess3_is_stochastic_and_symmetric() -> None:
    process = mess3(0.15, 0.6)
    np.testing.assert_allclose(process.transition.sum(axis=(0, 2)), 1.0)
    np.testing.assert_allclose(process.stationary, np.full(3, 1 / 3), atol=1e-12)
    np.testing.assert_allclose(
        next_symbol_distribution(process, process.stationary).sum(), 1.0
    )
    with pytest.raises(ValueError):
        HiddenProcess("bad", np.ones((3, 3, 3)), {})


def brute_force_beliefs(process: HiddenProcess, symbols: np.ndarray) -> np.ndarray:
    """eta = pi T[x0] T[x1] ... T[xt], normalized, with explicit matrix products."""

    beliefs = []
    for sequence in symbols:
        product = np.eye(process.state_count)
        row = []
        for symbol in sequence:
            product = product @ process.transition[int(symbol)]
            unnormalized = process.stationary @ product
            row.append(unnormalized / unnormalized.sum())
        beliefs.append(row)
    return np.asarray(beliefs)


def test_belief_update_matches_brute_force_forward_algorithm() -> None:
    process = mess3()
    symbols, _ = sample_sequences(process, 6, 40, np.random.default_rng(3))
    fast = belief_states(process, symbols)
    np.testing.assert_allclose(fast, brute_force_beliefs(process, symbols), atol=1e-12)
    np.testing.assert_allclose(fast.sum(axis=-1), 1.0, atol=1e-12)
    run = belief_states(process, np.full(60, 2, dtype=np.uint8))
    assert run[-1, 2] > 0.98  # the fixed point of repeated C is ~0.989
    assert run[0, 2] == pytest.approx(run[0].max())


def test_sampler_frequencies_match_the_matrices() -> None:
    process = mess3()
    symbols, states = sample_sequences(process, 3000, 200, np.random.default_rng(11))
    assert symbols.shape == (3000, 200) and states.shape == (3000, 201)
    joint = np.zeros((3, 3, 3))
    np.add.at(
        joint, (symbols.ravel(), states[:, :-1].ravel(), states[:, 1:].ravel()), 1
    )
    empirical = joint / joint.sum(axis=(0, 2), keepdims=True)
    np.testing.assert_allclose(empirical, process.transition, atol=0.01)
    initial = np.bincount(states[:, 0], minlength=3) / states.shape[0]
    np.testing.assert_allclose(initial, process.stationary, atol=0.05)


def make_v1_stream(rng: np.random.Generator, documents: int) -> np.ndarray:
    parts = []
    for _ in range(documents):
        body = rng.integers(20, 100, size=int(rng.integers(3, 12)))
        parts.append(np.concatenate([body, [EOS]]))
    return np.concatenate(parts).astype("<u2")


def test_weave_preserves_v1_bytes_outside_insertions(tmp_path: Path) -> None:
    rng = np.random.default_rng(5)
    stream = make_v1_stream(rng, 5)
    starts, ends = document_bounds(stream, EOS)
    assert starts.shape == (5,) and ends[-1] == stream.shape[0]
    symbols = rng.integers(0, 3, size=(4, 6)).astype(np.uint8)
    documents = render_documents(symbols, [200, 201, 202], 199, EOS)
    assert (
        documents.shape == (4, 8) and documents[0, 0] == 199 and documents[0, -1] == EOS
    )
    slots = np.array([2, 0, 5, 2])
    output = tmp_path / "train.bin"
    plan = weave_stream(stream, documents, slots, output, EOS)
    woven = np.fromfile(output, dtype="<u2")
    assert woven.shape[0] == plan["tokens"] == stream.shape[0] + documents.size
    assert plan["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert [group["slot"] for group in plan["insertions"]] == [0, 2, 5]
    assert plan["insertions"][1]["documents"] == [0, 3]
    kept = np.ones(woven.shape[0], dtype=bool)
    for group in plan["insertions"]:
        start = group["v11_offset"]
        kept[start : start + group["tokens"]] = False
        np.testing.assert_array_equal(
            woven[start : start + group["tokens"]],
            documents[group["documents"]].ravel(),
        )
    np.testing.assert_array_equal(woven[kept], stream)
    verification = verify_weave(stream, documents, plan, output)
    assert verification == {
        "v1_tokens_identical": int(stream.shape[0]),
        "synthetic_tokens": int(documents.size),
        "ok": True,
    }
    woven[plan["insertions"][1]["v11_offset"] + 9] ^= 1
    woven.tofile(output)
    with pytest.raises(ValueError):
        verify_weave(stream, documents, plan, output)


def test_plan_insertions_is_seeded_and_in_range() -> None:
    first = plan_insertions(4837, 100, np.random.default_rng(1))
    second = plan_insertions(4837, 100, np.random.default_rng(1))
    np.testing.assert_array_equal(first, second)
    assert first.min() >= 0 and first.max() <= 4837


def test_synthetic_document_count_targets_the_fraction() -> None:
    count = synthetic_document_count(374_405_212, 514, 0.02)
    assert count == 14866
    total = 374_405_212 + count * 514
    assert abs(count * 514 / total - 0.02) < 1e-4


def test_derive_validation_report_keeps_the_schema() -> None:
    v1_report = json.loads(
        json.dumps(
            {
                "schema_version": 1,
                "ok": True,
                "dataset_manifest_sha256": "a" * 64,
                "tokenizer": "tiiuae/Falcon-H1-Tiny-90M-Base",
                "vocab_size": 32768,
                "eos_token_id": EOS,
                "selected_documents": 36,
                "excluded_documents": 5,
                "duplicate_documents": 3,
                "cross_split_content_hash_overlap": 0,
                "splits": {
                    "train": {
                        "documents": 5,
                        "source_tokens": 95,
                        "dataset_source_tokens": 95,
                        "tokenized_source_tokens": 95,
                        "source_token_count_mismatches": 0,
                        "eos_tokens": 5,
                        "tokens_including_eos": 100,
                        "bytes": 200,
                        "sha256": "b" * 64,
                        "minimum_token_id": EOS,
                        "maximum_token_id": 32767,
                    },
                    "validation": {"documents": 31, "sha256": "c" * 64},
                },
            }
        )
    )
    synthetic = {
        "documents": 4,
        "tokens_per_document": 8,
        "minimum_token_id": 199,
        "maximum_token_id": 202,
    }
    report = derive_validation_report(
        v1_report, {"tokens": 132, "sha256": "d" * 64}, synthetic
    )
    assert set(report) == set(v1_report) | {"derived_from"}
    assert set(report["splits"]["train"]) == set(v1_report["splits"]["train"])
    train = report["splits"]["train"]
    assert train["documents"] == 9 and train["eos_tokens"] == 9
    assert train["source_tokens"] == 95 + 4 * 7
    assert train["tokens_including_eos"] == 132 and train["bytes"] == 264
    assert train["sha256"] == "d" * 64 and train["minimum_token_id"] == EOS
    assert report["selected_documents"] == 40
    assert report["splits"]["validation"] == v1_report["splits"]["validation"]
    assert report["derived_from"]["train_sha256"] == "b" * 64


def test_probe_inputs_align_targets_with_tokens() -> None:
    process = mess3()
    symbols, _ = sample_sequences(process, 10, 20, np.random.default_rng(2))
    beliefs = belief_states(process, symbols).astype(np.float32)
    mapping = {
        "prefix": {"id": 199},
        "emission": [{"id": 200}, {"id": 201}, {"id": 202}],
    }
    inputs = probe_inputs(
        symbols,
        beliefs,
        process.stationary,
        mapping,
        sequences=8,
        length=16,
        test_fraction=0.25,
    )
    assert inputs["rows"].shape == (8, 16) and inputs["targets"].shape == (8, 16, 3)
    assert np.all(inputs["rows"][:, 0] == 199)
    np.testing.assert_array_equal(inputs["rows"][:, 1:], 200 + symbols[:8, :15])
    np.testing.assert_allclose(
        inputs["targets"][:, 0], np.broadcast_to(process.stationary, (8, 3)), atol=1e-7
    )
    np.testing.assert_array_equal(inputs["targets"][:, 1:], beliefs[:8, :15])
    assert not inputs["valid"][:, 0].any() and inputs["valid"][:, 1:].all()
    assert inputs["test"].tolist() == [False] * 6 + [True] * 2


def test_probe_recovers_a_linear_map_and_the_shuffled_control_is_null() -> None:
    rng = np.random.default_rng(0)
    groups = np.repeat(np.arange(30), 40)
    test = groups >= 24
    features = rng.normal(size=(groups.shape[0], 12)).astype(np.float32)
    weights = rng.normal(size=(12, 3))
    targets = (
        features @ weights
        + np.array([0.2, -0.1, 0.5])
        + 0.01 * rng.normal(size=(groups.shape[0], 3))
    )
    outcome = probe_features(features, targets, groups, test, shuffle_seed=1)
    assert outcome["train_rows"] == 960 and outcome["test_rows"] == 240
    assert outcome["real"]["r2"] > 0.99 and outcome["real"]["mse"] < 1e-3
    assert abs(outcome["shuffled"]["r2"]) < 0.1
    assert outcome["real"]["predictions"].shape == (240, 3)
    wide = rng.normal(size=(groups.shape[0], 1500)).astype(np.float32)
    wide_targets = wide[:, :4] @ rng.normal(size=(4, 3)) + 0.01 * rng.normal(
        size=(groups.shape[0], 3)
    )
    dual = probe_features(wide, wide_targets, groups, test, shuffle_seed=1)
    assert dual["real"]["r2"] > 0.5 > dual["shuffled"]["r2"]


def test_simplex_projection_puts_vertices_on_the_triangle() -> None:
    x, y = simplex_xy(np.eye(3))
    np.testing.assert_allclose(x, [0.0, 1.0, 0.5])
    np.testing.assert_allclose(y, [0.0, 0.0, np.sqrt(3) / 2])


def test_recency_features_one_hot_the_last_k_symbols() -> None:
    symbols = np.array([[0, 2, 1, 1]], dtype=np.uint8)
    features = recency_features(symbols, 2, 3)
    assert features.shape == (1, 4, 8)
    np.testing.assert_array_equal(features[0, 0], [1, 0, 0, 0, 0, 0, 0, 1])
    np.testing.assert_array_equal(features[0, 2], [0, 1, 0, 0, 0, 0, 1, 0])
    np.testing.assert_array_equal(features.sum(axis=-1), [[2, 2, 2, 2]])
