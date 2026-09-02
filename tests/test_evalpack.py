import argparse
import gzip
import json
from pathlib import Path

import numpy as np
import pytest

from hghost.evalpack import (
    Checkpoint,
    clean_sequence_ids,
    contiguous_runs,
    coverage_mask,
    evenly_spaced,
    haunt_masks,
    label_masks,
    parse_checkpoint,
    parse_int_list,
    render_report,
    scan_generation_text,
    sequence_rows,
    summarize_losses,
    summarize_memorization,
)
from hghost.haunt import DEFAULT_EOS_TOKEN_ID, DocumentEntry, coverage_fractions

EOS = DEFAULT_EOS_TOKEN_ID
FURNITURE = list(range(900, 910))  # 10 tokens shared by six documents
QUOTE = list(range(1000, 1020))  # 20 tokens in exactly one document
TAIL = list(range(1100, 1112))  # follows FURNITURE in exactly one document


def make_documents() -> list[list[int]]:
    rng = np.random.default_rng(11)
    documents = []
    for number in range(8):
        body = rng.integers(20, 200, size=int(rng.integers(50, 80))).tolist()
        insert = int(rng.integers(5, len(body) - 5))
        if number < 6:
            body[insert:insert] = [300 + number, *FURNITURE, 400 + number]
        elif number == 6:
            body[insert:insert] = QUOTE
        else:
            body[insert:insert] = [*FURNITURE, *TAIL]
        documents.append(body)
    return documents


def write_corpus(root: Path, documents: list[list[int]]) -> tuple[Path, Path]:
    dataset = root / "dataset"
    dataset.mkdir()
    manifest = {"splits": {"train": {"documents": len(documents), "shards": []}}}
    name = "train-00000.jsonl.gz"
    with gzip.open(dataset / name, "wt", encoding="utf-8") as stream:
        for number, body in enumerate(documents):
            record = {
                "id": f"doc{number}",
                "source": "synthetic",
                "path": f"book/{number}.txt",
                "content_sha256": "0" * 64,
                "tokens": len(body),
                "text": " ".join(map(str, body)),
            }
            stream.write(json.dumps(record) + "\n")
    manifest["splits"]["train"]["shards"].append(
        {"path": name, "documents": len(documents)}
    )
    (dataset / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    stream_values = [token for body in documents for token in [*body, EOS]]
    tokens_path = root / "train.bin"
    np.asarray(stream_values, dtype="<u2").tofile(tokens_path)
    return tokens_path, dataset


@pytest.fixture(scope="module")
def index(tmp_path_factory):
    pytest.importorskip("pydivsufsort")
    from hghost.haunt import HauntingIndex, build_index

    root = tmp_path_factory.mktemp("evalpack")
    tokens_path, dataset = write_corpus(root, make_documents())
    output = root / "index"
    build_index(tokens_path, dataset, output, check_samples=1_000)
    return HauntingIndex.load(output, tokens_path)


def junk(seed: int, count: int) -> list[int]:
    return np.random.default_rng(seed).integers(5000, 6000, size=count).tolist()


def test_coverage_mask_agrees_with_coverage_fractions() -> None:
    lengths = np.array(
        [0, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 8, 8, 6, 5, 4, 3, 2, 1, 0],
        dtype=np.int64,
    )
    for threshold in (8, 9, 16):
        mask = coverage_mask(lengths, threshold)
        assert mask.shape == lengths.shape
        assert mask.mean() == coverage_fractions(lengths, (threshold,))[threshold]
    assert (
        coverage_mask(lengths, 8).tolist()
        == [False] + [True] * 9 + [False] * 5 + [True] * 9
    )
    assert coverage_mask(lengths, 9).tolist() == [False] + [True] * 9 + [False] * 14
    assert not coverage_mask(lengths, 16).any()


def test_haunt_masks_separate_furniture_from_quotation(index) -> None:
    query = np.asarray(
        [
            *junk(1, 6),
            *FURNITURE,
            *junk(2, 5),
            *QUOTE,
            *junk(3, 4),
            *FURNITURE,
            *TAIL,
            *junk(4, 3),
        ],
        dtype=np.uint16,
    )
    masks = haunt_masks(index, query, min_tokens=8, min_documents=5)
    expected_matched = np.zeros(len(query), dtype=bool)
    expected_furniture = np.zeros(len(query), dtype=bool)
    first = 6
    expected_matched[first : first + 10] = True
    expected_furniture[first : first + 10] = True
    quote = first + 10 + 5
    expected_matched[quote : quote + 20] = True
    quoted_furniture = quote + 20 + 4
    expected_matched[quoted_furniture : quoted_furniture + 22] = True
    expected_furniture[quoted_furniture : quoted_furniture + 10] = True
    assert masks.matched.tolist() == expected_matched.tolist()
    assert masks.furniture.tolist() == expected_furniture.tolist()
    assert masks.lengths[quoted_furniture] == 22
    assert [span.length for span in masks.spans] == [10, 20, 22]


def test_label_masks_align_with_stream_positions(index) -> None:
    length = 16
    stream = np.asarray(
        [
            *junk(5, 9),
            *FURNITURE,
            *junk(6, 20),
            *QUOTE,
            *junk(7, 30),
            *FURNITURE,
            *TAIL,
            *junk(8, 15),
        ],
        dtype=np.uint16,
    )
    sequence_ids = np.array([0, 2, 3, 5], dtype=np.int64)
    matched, furniture = label_masks(
        index, stream, sequence_ids, length, min_tokens=8, min_documents=5
    )
    whole = haunt_masks(index, stream, min_tokens=8, min_documents=5)
    for row, sequence in enumerate(sequence_ids):
        labels = slice(sequence * length + 1, sequence * length + length + 1)
        assert matched[row].tolist() == whole.matched[labels].tolist()
        assert furniture[row].tolist() == whole.furniture[labels].tolist()
    assert matched.any() and furniture.any()
    assert contiguous_runs(sequence_ids) == [(0, 1), (2, 4), (5, 6)]


def test_scan_generation_text_reports_furniture_and_quotation(index) -> None:
    tokens = [*junk(9, 4), *FURNITURE, *junk(10, 2), *QUOTE]
    scan = scan_generation_text(index, tokens, thresholds=(8, 16), min_documents=5)
    assert scan["tokens"] == len(tokens)
    assert scan["longest_match"] == 20
    assert scan["coverage"]["8"] == pytest.approx(30 / len(tokens))
    assert scan["coverage"]["16"] == pytest.approx(20 / len(tokens))
    assert scan["furniture_fraction"] == pytest.approx(10 / len(tokens))
    assert scan["quotation"]["8"] == pytest.approx(20 / len(tokens))
    assert scan["longest_span"]["length"] == 20
    assert scan["longest_span"]["distinct_documents"] == 1
    assert scan["longest_span"]["furniture"] is False
    summary = summarize_memorization([scan, scan], (8, 16))
    assert summary["generations"] == 2
    assert summary["coverage"]["8"] == pytest.approx(scan["coverage"]["8"])
    assert summary["generations_with_quotation_at_least"] == {"8": 2, "16": 2}
    assert summary["longest_match"] == 20


def test_summarize_losses_with_furniture_mask() -> None:
    losses = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
    correct = np.array([[True, False, True, False], [False, False, True, True]])
    furniture = np.array([[False, True, True, False], [False, False, False, True]])
    matched = furniture | np.array(
        [[True, False, False, False], [False, False, False, False]]
    )
    summary = summarize_losses(losses, correct, matched, furniture)
    assert summary["sequences"] == 2
    assert summary["tokens"] == 8
    assert summary["loss"] == pytest.approx(4.5)
    assert summary["accuracy"] == pytest.approx(0.5)
    assert summary["furniture_fraction"] == pytest.approx(3 / 8)
    assert summary["furniture_free_loss"] == pytest.approx((1 + 4 + 5 + 6 + 7) / 5)
    assert summary["furniture_loss"] == pytest.approx((2 + 3 + 8) / 3)
    assert summary["furniture_free_accuracy"] == pytest.approx(2 / 5)
    assert summary["matched_fraction"] == pytest.approx(4 / 8)
    assert summary["unseen_loss"] == pytest.approx((4 + 5 + 6 + 7) / 4)
    plain = summarize_losses(losses, correct)
    assert "furniture_free_loss" not in plain and plain["loss"] == pytest.approx(4.5)


def test_sequence_rows_follow_file_order() -> None:
    tokens = np.arange(100, dtype=np.uint16)
    rows = sequence_rows(tokens, np.array([0, 3]), 8)
    assert rows.shape == (2, 9)
    assert rows[0].tolist() == list(range(9))
    assert rows[1].tolist() == list(range(24, 33))


def test_clean_sequence_ids_use_whole_windows_inside_clean_documents() -> None:
    entries = [
        DocumentEntry("a", "s", "a.txt", 0, 20),  # stream 0..20 (EOS at 20)
        DocumentEntry("b", "s", "b.txt", 21, 30),  # 21..51
        DocumentEntry("c", "s", "c.txt", 52, 12),  # 52..64
    ]
    levels = {"a": "clean", "b": "series_only", "c": "clean"}
    ids, per_document = clean_sequence_ids(entries, levels, 8, 65)
    # sequence s spans tokens [8s, 8s + 9): s=0,1 lie inside a, s=2 crosses into b,
    # s=3..5 lie in b (not clean), s=6 crosses into c, s=7 is c's tail up to its EOS.
    assert ids.tolist() == [0, 1, 7]
    assert per_document == {"a": 2, "c": 1}
    assert evenly_spaced(np.arange(10), 4).tolist() == [0, 3, 6, 9]
    assert evenly_spaced(np.arange(3), 5).tolist() == [0, 1, 2]


def test_parse_helpers(tmp_path: Path) -> None:
    assert parse_int_list("512,32,32") == (32, 512)
    with pytest.raises(argparse.ArgumentTypeError):
        parse_int_list("0")
    with pytest.raises(argparse.ArgumentTypeError):
        parse_checkpoint(str(tmp_path))
    (tmp_path / "config.json").write_text("{}")
    checkpoint = parse_checkpoint(f"name={tmp_path}")
    assert checkpoint == Checkpoint("name", tmp_path.resolve())
    assert len(checkpoint.blind_id) == 12
    assert checkpoint.name not in checkpoint.blind_id


def test_render_report_tables() -> None:
    def losses(value: float) -> dict:
        return {
            "sequences": 2,
            "tokens": 8,
            "loss": value,
            "perplexity": 2.0,
            "accuracy": 0.5,
            "furniture_fraction": 0.25,
            "furniture_free_loss": value - 0.1,
            "furniture_free_accuracy": 0.5,
            "furniture_loss": value + 0.3,
            "matched_fraction": 0.5,
            "unseen_loss": value - 0.2,
            "unseen_accuracy": 0.5,
        }

    report = {
        "generated": "2026-09-01T00:00:00+00:00",
        "settings": {
            "dtype": "float32",
            "sequence_length": 4,
            "min_tokens": 8,
            "min_documents": 5,
            "thresholds": [8, 16, 32],
        },
        "slices": {
            "first-2": {
                "sequences": 2,
                "tokens": 8,
                "furniture_fraction": 0.25,
                "matched_fraction": 0.5,
            }
        },
        "retention": {
            "path": "r.txt",
            "bytes": 10,
            "tokens": 9,
            "sequences": 2,
            "coverage": {"8": 0.0, "16": 0.0, "32": 0.0},
        },
        "checkpoints": [
            {
                "name": "base",
                "path": "/x/base",
                "blind_id": "aaa",
                "losses": {"first-2": losses(3.5)},
                "retention": {"loss": 3.0, "perplexity": 20.1, "accuracy": 0.4},
                "memorization": {
                    "generations": 2,
                    "tokens": 100,
                    "coverage": {"8": 0.2, "16": 0.1, "32": 0.05},
                    "quotation": {"8": 0.1, "16": 0.05, "32": 0.0},
                    "furniture_fraction": 0.1,
                    "longest_match": 40,
                    "generations_with_match_at_least": {"8": 2, "16": 1, "32": 1},
                    "generations_with_quotation_at_least": {"8": 1, "16": 1, "32": 0},
                },
                "memorization_records": [],
            },
            {
                "name": "cpt",
                "path": "/x/cpt",
                "blind_id": "bbb",
                "losses": {"first-2": losses(3.0)},
                "retention": {"loss": 3.2, "perplexity": 24.5, "accuracy": 0.4},
            },
        ],
    }
    text = render_report(report)
    assert "## Loss (plain, all positions)" in text
    assert "| cpt | 3.0000 (-0.5000) |" in text
    assert "| base | 3.5000 |" in text
    assert "## Loss (furniture-subtracted)" in text
    assert "| cpt | 2.9000 (-0.5000) |" in text
    assert "## Retention proxy" in text
    assert "| cpt | 3.2000 (+0.2000) | 24.50 | 40.00% |" in text
    assert "## Generation memorization" in text
    assert (
        "| base | 20.00% | 10.00% | 5.00% | 10.00% | 10.00% | 5.00% | 0.00% | 40 | 0/2 |"
        in text
    )
    assert "| cpt | - | - | - | - | - | - | - | - | - |" in text
    assert "aaa" in text and "/x/base" in text


def tiny_config():
    from h1jax.config import FalconH1Config

    return FalconH1Config(
        vocab_size=128,
        hidden_size=64,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        head_dim=16,
        intermediate_size=96,
        mamba_d_ssm=96,
        mamba_d_state=8,
        mamba_d_head=16,
        mamba_n_heads=6,
        mamba_n_groups=1,
        mamba_d_conv=4,
        mamba_chunk_size=4,
        rope_theta=10000.0,
    )


def test_per_token_losses_match_h1jax_loss_on_tiny_model() -> None:
    pytest.importorskip("jax")
    pytest.importorskip("h1jax")
    import jax.numpy as jnp
    from h1jax.model import causal_lm_loss, init_params

    from hghost.evalpack_jax import per_token_losses

    cfg = tiny_config()
    params = init_params(cfg, seed=3)
    rng = np.random.default_rng(0)
    rows = rng.integers(0, cfg.vocab_size, size=(5, 9)).astype(np.int32)
    seen: list[tuple[int, int]] = []
    losses, correct = per_token_losses(
        params,
        cfg,
        rows,
        batch_size=2,
        compute_dtype=jnp.float32,
        progress=lambda d, t: seen.append((d, t)),
    )
    assert losses.shape == (5, 8) and correct.shape == (5, 8)
    assert seen == [(2, 5), (4, 5), (5, 5)]
    for row in range(5):
        reference, metrics = causal_lm_loss(
            params,
            jnp.asarray(rows[row : row + 1]),
            cfg,
            compute_dtype=jnp.float32,
            gradient_checkpointing=False,
            layer_scan=True,
        )
        assert losses[row].mean() == pytest.approx(float(reference), abs=1e-5)
        assert correct[row].mean() == pytest.approx(
            float(metrics["accuracy"]), abs=1e-6
        )
    furniture = np.zeros_like(correct)
    furniture[:, :3] = True
    summary = summarize_losses(losses, correct, furniture, furniture)
    assert summary["loss"] == pytest.approx(float(losses.mean()), rel=1e-6)
    assert summary["furniture_free_loss"] == pytest.approx(
        float(losses[:, 3:].mean()), rel=1e-6
    )
    assert summary["furniture_fraction"] == pytest.approx(3 / 8)


def test_config_repairs_only_touch_h1jax_float_expand() -> None:
    from hghost.evalpack_mlx import config_repairs

    assert config_repairs({"mamba_expand": 2, "mamba_d_ssm": 768}) == {}
    assert config_repairs({"mamba_expand": 1.5, "mamba_d_ssm": 768}) == {
        "mamba_expand": 2
    }
    assert config_repairs({"mamba_expand": 1.0}) == {"mamba_expand": 1}
    assert config_repairs({}) == {}
