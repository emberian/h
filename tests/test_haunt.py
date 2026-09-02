import gzip
import json
from pathlib import Path

import numpy as np
import pytest

from hghost.haunt import (
    DEFAULT_EOS_TOKEN_ID,
    HauntingIndex,
    build_index,
    build_parser,
    capped_lcp,
    coverage_fractions,
    find_furniture,
    maximal_spans,
    run_furniture,
    run_query,
    run_scan,
    scan_generation,
    suffix_order_violations,
)

EOS = DEFAULT_EOS_TOKEN_ID
FURNITURE = [900, 901, 902, 903, 904, 905, 906, 907, 908, 909]
FURNISHED = (0, 2, 3)
JUNK_BASE = 5000  # never occurs in the synthetic corpus


def make_documents() -> list[list[int]]:
    rng = np.random.default_rng(7)
    documents = []
    for number in range(6):
        body = rng.integers(20, 200, size=int(rng.integers(40, 90))).tolist()
        if number in FURNISHED:
            insert = int(rng.integers(5, len(body) - 5))
            # Distinct neighbours keep the shared run left-maximal and exactly ten tokens long.
            body[insert:insert] = [300 + number, *FURNITURE, 400 + number]
        documents.append(body)
    return documents


def write_corpus(root: Path, documents: list[list[int]], token_counts=None) -> tuple[Path, Path]:
    dataset = root / "dataset"
    dataset.mkdir()
    counts = token_counts or [len(body) for body in documents]
    shards = [(0, 4), (4, 6)]
    manifest = {"splits": {"train": {"documents": len(documents), "shards": []}}}
    for shard_number, (start, stop) in enumerate(shards):
        name = f"train-{shard_number:05d}.jsonl.gz"
        with gzip.open(dataset / name, "wt", encoding="utf-8") as stream:
            for number in range(start, stop):
                record = {
                    "id": f"doc{number}",
                    "source": "synthetic",
                    "path": f"book/{number}.txt",
                    "content_sha256": "0" * 64,
                    "tokens": counts[number],
                    "text": " ".join(map(str, documents[number])),
                }
                stream.write(json.dumps(record) + "\n")
        manifest["splits"]["train"]["shards"].append({"path": name, "documents": stop - start})
    (dataset / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    stream_values = [token for body in documents for token in [*body, EOS]]
    tokens_path = root / "train.bin"
    np.asarray(stream_values, dtype="<u2").tofile(tokens_path)
    return tokens_path, dataset


@pytest.fixture(scope="module")
def corpus(tmp_path_factory) -> dict:
    root = tmp_path_factory.mktemp("haunt")
    documents = make_documents()
    tokens_path, dataset = write_corpus(root, documents)
    output = root / "index"
    manifest = build_index(tokens_path, dataset, output, check_samples=10_000)
    stream = np.fromfile(tokens_path, dtype="<u2")
    return {
        "documents": documents,
        "stream": stream,
        "tokens_path": tokens_path,
        "dataset": dataset,
        "output": output,
        "manifest": manifest,
        "index": HauntingIndex.load(output),
    }


def brute_force_longest(stream: np.ndarray, query: np.ndarray) -> list[int]:
    lengths = []
    for start in range(len(query)):
        best = 0
        for position in range(len(stream)):
            length = 0
            while (
                start + length < len(query)
                and position + length < len(stream)
                and query[start + length] == stream[position + length]
            ):
                length += 1
            best = max(best, length)
        lengths.append(best)
    return lengths


def test_build_layout_and_suffix_array(corpus: dict) -> None:
    stream = corpus["stream"]
    manifest = corpus["manifest"]
    index = corpus["index"]
    assert manifest["token_count"] == len(stream)
    assert manifest["eos_count"] == len(corpus["documents"]) == manifest["documents"]
    assert manifest["suffix_array"]["order_check"]["violations"] == 0
    expected_offsets = np.cumsum([0, *[len(body) + 1 for body in corpus["documents"][:-1]]])
    assert index.offsets.tolist() == expected_offsets.tolist()
    assert [entry.id for entry in index.documents] == [f"doc{n}" for n in range(6)]
    suffix_array = np.asarray(index.suffix_array)
    assert np.array_equal(np.sort(suffix_array), np.arange(len(stream)))
    assert suffix_order_violations(stream, suffix_array, range(len(stream) - 1), len(stream)) == 0


def test_build_rejects_offset_mismatch(tmp_path: Path) -> None:
    documents = make_documents()
    counts = [len(body) for body in documents]
    counts[2] += 1
    tokens_path, dataset = write_corpus(tmp_path, documents, counts)
    with pytest.raises(ValueError, match="disagrees with the stream"):
        build_index(tokens_path, dataset, tmp_path / "index", check_samples=10)


def test_longest_match_agrees_with_brute_force(corpus: dict) -> None:
    stream = corpus["stream"]
    index = corpus["index"]
    rng = np.random.default_rng(3)
    mutated = stream[30:80].copy()
    mutated[[7, 23, 41]] = [JUNK_BASE, JUNK_BASE + 1, JUNK_BASE + 2]
    queries = [
        rng.integers(20, 200, size=40).astype(np.uint16),
        mutated,
        stream[index.documents[1].end - 6 : index.documents[1].end + 12].copy(),
        np.asarray(FURNITURE, dtype=np.uint16),
    ]
    for query in queries:
        lengths, offsets = index.match_lengths(query)
        assert lengths.tolist() == brute_force_longest(stream, query)
        for start, (length, offset) in enumerate(zip(lengths, offsets)):
            if length:
                assert (
                    stream[offset : offset + length].tolist()
                    == query[start : start + length].tolist()
                )


def test_maximal_spans_and_provenance(corpus: dict) -> None:
    stream = corpus["stream"]
    index = corpus["index"]
    document = index.documents[4]
    start = document.token_offset + 3
    junk = np.arange(JUNK_BASE, JUNK_BASE + 10, dtype=np.uint16)
    query = np.concatenate([junk, stream[start : start + 30], junk + 10])
    lengths, offsets = index.match_lengths(query)
    spans = maximal_spans(lengths, offsets, 16)
    assert [(span.query_offset, span.length, span.corpus_offset) for span in spans] == [
        (10, 30, start)
    ]
    record = index.describe_span(query, spans[0])
    assert record["document"]["id"] == "doc4"
    assert record["document_offset"] == 3
    assert record["occurrences"] == 1
    assert record["crosses_document_boundary"] is False
    assert "text" not in record

    furniture_query = np.asarray([JUNK_BASE, *FURNITURE, JUNK_BASE + 1], dtype=np.uint16)
    lengths, offsets = index.match_lengths(furniture_query)
    (span,) = maximal_spans(lengths, offsets, 8)
    record = index.describe_span(furniture_query, span)
    assert span.length == len(FURNITURE)
    assert record["occurrences"] == 3
    assert record["distinct_documents"] == 3
    assert record["documents"] == [f"doc{n}" for n in FURNISHED]


def test_coverage_fractions() -> None:
    lengths = np.array(
        [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0]
    )
    assert coverage_fractions(lengths, (8, 16, 32)) == {8: 20 / 22, 16: 20 / 22, 32: 0.0}
    overlapping = np.array([0, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 3, 2, 1, 0])
    assert coverage_fractions(overlapping, (8, 3)) == {8: 9 / 15, 3: 12 / 15}
    assert coverage_fractions(np.zeros(0, dtype=np.int64), (8,)) == {8: 0.0}


def test_scan_generation_reports_coverage(corpus: dict) -> None:
    stream = corpus["stream"]
    index = corpus["index"]
    document = index.documents[5]
    start = document.token_offset + 2
    junk = np.arange(JUNK_BASE, JUNK_BASE + 10, dtype=np.uint16)
    query = np.concatenate([junk, stream[start : start + 30], junk + 10])
    report = scan_generation(index, query, (8, 16, 32))
    assert report["tokens"] == 50
    assert report["longest_match"] == 30
    assert report["coverage"] == {"8": 0.6, "16": 0.6, "32": 0.0}
    assert report["span_count"] == 1
    assert report["top_documents"][0]["id"] == "doc5"
    assert report["top_documents"][0]["quoted_tokens"] == 30
    assert report["longest_spans"][0]["query_offset"] == 10


def test_capped_lcp_matches_reference(corpus: dict) -> None:
    stream = corpus["stream"]
    index = corpus["index"]
    lcp = capped_lcp(index, 16, chunk=64)
    suffix_array = np.asarray(index.suffix_array)
    assert lcp[0] == 0
    for rank in range(1, len(stream)):
        left, right = int(suffix_array[rank - 1]), int(suffix_array[rank])
        length = 0
        while (
            length < 16
            and left + length < len(stream)
            and right + length < len(stream)
            and stream[left + length] == stream[right + length]
        ):
            length += 1
        assert int(lcp[rank]) == length


def test_furniture_detects_shared_ngram(corpus: dict) -> None:
    index = corpus["index"]
    results = find_furniture(index, min_tokens=8, min_documents=3, max_tokens=16, top=10)
    assert results, "the shared ten-token run should be detected"
    top = results[0]
    assert top["documents"] == 3
    assert top["occurrences"] == 3
    assert top["length"] == len(FURNITURE)
    assert top["tokens"] == FURNITURE
    assert sorted(item["id"] for item in top["examples"]) == [f"doc{n}" for n in FURNISHED]
    assert all(item["length"] >= 8 for item in results)
    assert find_furniture(index, min_tokens=8, min_documents=4, max_tokens=16) == []


def test_cli_query_scan_and_furniture(corpus: dict, tmp_path: Path, capsys) -> None:
    stream = corpus["stream"]
    index = corpus["index"]
    output = corpus["output"]
    document = index.documents[2]
    start = document.token_offset + 1
    query_path = tmp_path / "query.json"
    query_path.write_text(json.dumps(stream[start : start + 24].tolist()), encoding="utf-8")
    parser = build_parser()

    run_query(parser.parse_args(["query", "--index", str(output), "--tokens", str(query_path)]))
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [line["type"] for line in lines] == ["span", "summary"]
    assert lines[0]["document"]["id"] == "doc2" and lines[0]["length"] == 24
    assert lines[1]["longest_match"] == 24

    generations = tmp_path / "generations.jsonl"
    generations.write_text(
        json.dumps({"id": "copy", "tokens": stream[start : start + 24].tolist()})
        + "\n"
        + json.dumps({"id": "junk", "tokens": list(range(JUNK_BASE, JUNK_BASE + 24))})
        + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "scan.jsonl"
    run_scan(
        parser.parse_args(
            [
                "scan",
                "--index",
                str(output),
                "--generations",
                str(generations),
                "--output",
                str(report_path),
            ]
        )
    )
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary["generations"] == 2 and summary["tokens"] == 48
    assert summary["token_weighted_coverage"] == {"8": 0.5, "16": 0.5, "32": 0.0}
    assert summary["generations_with_match_at_least"] == {"8": 1, "16": 1, "32": 0}
    reports = [json.loads(line) for line in report_path.read_text().splitlines()]
    assert [item["id"] for item in reports] == ["copy", "junk"]
    assert reports[1]["coverage"] == {"8": 0.0, "16": 0.0, "32": 0.0}

    furniture_path = tmp_path / "furniture.jsonl"
    run_furniture(
        parser.parse_args(
            [
                "furniture",
                "--index",
                str(output),
                "--min-documents",
                "3",
                "--max-tokens",
                "16",
                "--output",
                str(furniture_path),
            ]
        )
    )
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary["reported"] >= 1
    first = json.loads(furniture_path.read_text().splitlines()[0])
    assert first["tokens"] == FURNITURE and first["documents"] == 3
