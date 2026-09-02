import argparse
import gzip
import hashlib
import json
import random
from pathlib import Path

import numpy as np

from hghost.families import (
    CONTENT_THRESHOLDS,
    candidate_pairs,
    combine_confidence,
    path_signals,
    sampled_shingles,
    shingle_hashes,
)
from hghost.families import (
    run as run_families,
)


def test_path_signals_strip_edition_scan_and_archive_noise() -> None:
    first = path_signals("people/william_bunge/theoretical_geography.2nd.ocr.pdf")
    second = path_signals("people/william_bunge/theoretical_geography.pdf")
    assert first.stem == second.stem == "theoretical geography"
    assert first.author == "william_bunge"
    assert "2nd" in first.numbers
    annas = path_signals(
        "math/Mathematical logic_ -- Daniel Ponasse -- Notes on mathematics -- Gordon and Breach"
        " -- 9780677303901 -- d57a712a8dc4ddaef63bb54516ad4cdc -- Anna’s Archive.pdf"
    )
    assert annas.stem == "mathematical logic"
    zlib = path_signals(
        "pubs/x/At the Roots of Causality (Francesco Zamboni) (z-library.sk, 1lib.sk).pdf"
    )
    assert zlib.stem == "at roots causality"
    assert zlib.distinctive
    assert not path_signals("magazines/hermetic_journal/13.pdf").stem
    assert not path_signals("people/x/m7r.02.pdf").distinctive


def test_path_signals_numbers_years_and_identifiers() -> None:
    animals = path_signals("the-cryptozoological-library/Animals and Men - No 11.pdf")
    assert (
        animals.stem == "animals men"
        and animals.numbers == ("11",)
        and animals.periodical_hint
    )
    suttles = path_signals("the-cryptozoological-library/suttles-1974.pdf")
    assert (
        suttles.stem == "suttles"
        and suttles.numbers == ()
        and suttles.years == ("1974",)
    )
    site = path_signals(
        "kvlt/golden_rosycross/d4331c_b01e6a0e56ef4764b52dc6b377c97eb5.pdf"
    )
    assert site.stem == "d4331c" and not site.title_words
    roman = path_signals("people/sophia_johanson/smoke_signal_iv_1996-2002.pdf")
    assert roman.stem == "smoke signal" and roman.numbers == ("iv",)
    left = path_signals("pubs/bsrf/round_robin/round_robin_v7_n4_nov_dec_1956.pdf")
    right = path_signals("magazines/round_robin/round_robin_v7_n4_nov_dec_1956.pdf")
    assert left.stem == right.stem == "round robin"
    assert left.basename == right.basename == "round_robin"
    assert (
        (left.numbers, left.years)
        == (right.numbers, right.years)
        == (("v7", "n4"), ("1956",))
    )


def test_path_signals_periodical_hints() -> None:
    assert path_signals(
        "magazines/east_village_other/East Village Other v02n20 (1967).pdf"
    ).periodical_hint
    assert path_signals(
        "the-cryptozoological-library/ISC Newsletter - Vol 04 No 3 - 1985.pdf"
    ).periodical_hint
    assert not path_signals("people/michael_bertiaux/m7r.02.pdf").periodical_hint
    assert not path_signals(
        "people/riley_crabb/Riley Crabb - Psychic Self-Defense Part 2.pdf"
    ).periodical_hint


def test_combine_confidence_rules() -> None:
    assert combine_confidence("none", "parts_or_editions", "medium", False) == "medium"
    assert combine_confidence("low", "parts_or_editions", "medium", False) == "high"
    assert combine_confidence("none", "same_title", "low", False) == "low"
    assert combine_confidence("medium", "same_title", "low", False) == "high"
    assert combine_confidence("high", "none", "none", False) == "high"
    assert combine_confidence("low", "none", "none", True) == "low"
    assert combine_confidence("medium", "none", "none", True) == "medium"
    assert combine_confidence("none", "none", "none", True) == "none"
    assert (
        combine_confidence(
            "low", "parts_or_editions", "medium", False, distinctive=False
        )
        == "medium"
    )
    assert combine_confidence("none", "year_siblings", "low", False) == "low"
    assert combine_confidence("low", "year_siblings", "low", False) == "medium"
    assert combine_confidence("medium", "year_siblings", "low", False) == "high"


def _words(rng: random.Random, count: int) -> list[str]:
    vocabulary = [f"w{index}" for index in range(4000)]
    return [rng.choice(vocabulary) for _ in range(count)]


def test_sampled_shingles_are_deterministic_and_consistent() -> None:
    rng = random.Random(7)
    text = " ".join(_words(rng, 4000))
    first, positions = sampled_shingles(text)
    second, _ = sampled_shingles(text)
    assert positions == 4000 - 4
    assert np.array_equal(first, second)
    assert 250 < len(first) < 750  # 1/8 sampling of ~4000 shingles
    hashes = shingle_hashes(np.arange(10, dtype=np.uint64), 5)
    assert len(hashes) == 6 and len(set(hashes.tolist())) == 6


def test_candidate_pairs_count_shared_samples() -> None:
    a = np.array([1, 2, 3, 4], dtype=np.uint64)
    b = np.array([3, 4, 5], dtype=np.uint64)
    c = np.array([4, 9], dtype=np.uint64)
    left, right, shared, histogram = candidate_pairs([a, b, c])
    counts = {(int(x), int(y)): int(z) for x, y, z in zip(left, right, shared)}
    assert counts == {(0, 1): 2, (0, 2): 1, (1, 2): 1}
    assert histogram[3] == 1  # hash 4 appears in all three sketches


def _write_dataset(root: Path, documents: list[tuple[str, str, str]]) -> None:
    root.mkdir(parents=True)
    shards = {"train": [], "validation": []}
    for source, path, text in documents:
        split = "validation" if path.startswith("held/") else "train"
        document_id = hashlib.sha256(f"{source}\0{path}".encode()).hexdigest()[:24]
        shards[split].append(
            {
                "id": document_id,
                "source": source,
                "path": path,
                "content_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "tokens": len(text.split()),
                "text": text,
            }
        )
    manifest = {"splits": {}}
    for split, rows in shards.items():
        name = f"{split}-00000.jsonl.gz"
        with gzip.open(root / name, "wt", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row) + "\n")
        manifest["splits"][split] = {
            "documents": len(rows),
            "tokens": sum(row["tokens"] for row in rows),
            "shards": [{"path": name}],
        }
    (root / "manifest.json").write_text(json.dumps(manifest))


def test_end_to_end_families_and_family_disjoint_proposal(tmp_path: Path) -> None:
    rng = random.Random(11)
    book = " ".join(_words(rng, 6000))
    noisy_book = " ".join(
        word if rng.random() > 0.08 else "ocrnoise" for word in book.split()
    )  # a second, worse OCR of the same scan
    excerpt = " ".join(book.split()[1000:2200])
    documents = [
        ("rat", "people/author/great_work.pdf", book),
        ("rat", "held/great_work.ocr.pdf", noisy_book),
        ("cat", "lib/great-work-excerpt.pdf", excerpt),
        ("rat", "people/author/serial.01.pdf", " ".join(_words(rng, 3000))),
        ("rat", "people/author/serial.02.pdf", " ".join(_words(rng, 3000))),
        ("rat", "magazines/zine/zine.1990.01.pdf", " ".join(_words(rng, 3000))),
        ("rat", "magazines/zine/zine.1990.02.pdf", " ".join(_words(rng, 3000))),
        ("cat", "lib/smith-1974.pdf", " ".join(_words(rng, 2500))),
        ("cat", "lib/smith-1980.pdf", " ".join(_words(rng, 2500))),
        (
            "cat",
            "lib/d4331c_a1b2c3d4e5f60718293a4b5c6d7e8f90.pdf",
            " ".join(_words(rng, 2500)),
        ),
        (
            "cat",
            "lib/d4331c_b1b2c3d4e5f60718293a4b5c6d7e8f91.pdf",
            " ".join(_words(rng, 2500)),
        ),
        ("rat", "pubs/gazette/gazette_v3_n1_1950.pdf", " ".join(_words(rng, 2500))),
        (
            "rat",
            "magazines/gazette/gazette_v3_n2_1950.pdf",
            " ".join(_words(rng, 2500)),
        ),
        ("rat", "magazines/thoth/thviii01.txt", " ".join(_words(rng, 2500))),
        ("rat", "magazines/thoth/thovii03.txt", " ".join(_words(rng, 2500))),
        ("rat", "magazines/lone_issue.pdf", " ".join(_words(rng, 2500))),
    ]
    names = (
        "apple",
        "birch",
        "cedar",
        "dune",
        "ember",
        "fjord",
        "gale",
        "heath",
        "iris",
        "jade",
        "kelp",
        "loam",
    )
    for name in names:
        documents.append(
            ("rat", f"misc/{name}_essays.pdf", " ".join(_words(rng, 2500)))
        )
    for name in ("quiet_river", "salt_marsh", "winter_road"):
        documents.append(("cat", f"held/{name}.pdf", " ".join(_words(rng, 2500))))
    dataset = tmp_path / "dataset"
    _write_dataset(dataset, documents)
    output = tmp_path / "families"
    summary = run_families(
        argparse.Namespace(
            dataset=dataset,
            records=None,
            output=output,
            sketch_cache=None,
            target_tokens=5000,
            min_doc_tokens=100,
            max_doc_tokens=10_000,
            largest=10,
        )
    )
    rows = {
        row["path"]: row for row in map(json.loads, (output / "families.jsonl").open())
    }
    assert summary["documents"] == len(documents)
    same_work = {
        rows[p]["family_id"]
        for p in (
            "people/author/great_work.pdf",
            "held/great_work.ocr.pdf",
            "lib/great-work-excerpt.pdf",
        )
    }
    assert len(same_work) == 1
    assert rows["held/great_work.ocr.pdf"]["confidence"] == "high"
    assert rows["lib/great-work-excerpt.pdf"]["method"].startswith("content")
    assert (
        rows["people/author/serial.01.pdf"]["family_id"]
        == rows["people/author/serial.02.pdf"]["family_id"]
    )
    assert rows["people/author/serial.01.pdf"]["method"] == "path"
    assert rows["people/author/serial.01.pdf"]["confidence"] == "medium"
    assert (
        rows["magazines/zine/zine.1990.01.pdf"]["family_id"]
        != rows["magazines/zine/zine.1990.02.pdf"]["family_id"]
    )
    assert (
        rows["magazines/zine/zine.1990.01.pdf"]["series_id"]
        == rows["magazines/zine/zine.1990.02.pdf"]["series_id"]
    )
    assert rows["misc/apple_essays.pdf"]["family_size"] == 1
    assert (
        rows["lib/smith-1974.pdf"]["family_size"] == 1
    )  # year siblings: low, not unioned
    assert rows["lib/smith-1974.pdf"]["weak_links"] == 1
    assert rows["lib/d4331c_a1b2c3d4e5f60718293a4b5c6d7e8f90.pdf"]["family_size"] == 1
    assert rows["lib/d4331c_a1b2c3d4e5f60718293a4b5c6d7e8f90.pdf"]["weak_links"] == 0
    assert rows["pubs/gazette/gazette_v3_n1_1950.pdf"]["family_size"] == 1
    gazette = rows["pubs/gazette/gazette_v3_n1_1950.pdf"]["series_id"]
    assert gazette is not None
    assert rows["magazines/gazette/gazette_v3_n2_1950.pdf"]["series_id"] == gazette
    thoth = rows["magazines/thoth/thviii01.txt"]["series_id"]
    assert (
        thoth is not None and rows["magazines/thoth/thovii03.txt"]["series_id"] == thoth
    )
    assert rows["magazines/lone_issue.pdf"]["series_id"] is None

    report = json.loads((output / "leakage-report.json").read_text())
    leaked = {entry["path"]: entry for entry in report["documents"]}
    assert leaked["held/great_work.ocr.pdf"]["leakage_level"] == "high"
    contained = [
        edge
        for edge in leaked["held/great_work.ocr.pdf"]["train_edges"]
        if edge["other"]["path"].endswith("excerpt.pdf")
    ]
    # 8% OCR noise kills ~1/3 of five-word shingles: medium overlap, but the
    # matching title stem lifts the pair to high.
    assert contained and contained[0]["containment"] >= CONTENT_THRESHOLDS["medium"]
    assert contained[0]["confidence"] == "high" and contained[0]["contained"] == "other"
    pairs = [json.loads(line) for line in (output / "pairs.jsonl").open()]
    clean_excerpt = [
        pair
        for pair in pairs
        if {pair["left"]["path"], pair["right"]["path"]}
        == {"people/author/great_work.pdf", "lib/great-work-excerpt.pdf"}
    ]
    assert clean_excerpt and clean_excerpt[0]["containment"] >= 0.95
    assert clean_excerpt[0]["relation"] == "same_title+contained"
    assert leaked["held/quiet_river.pdf"]["leakage_level"] == "clean"
    assert report["summary"]["by_level"]["high"]["documents"] == 1

    proposed = {
        name: [json.loads(line) for line in (output / f"proposed-{name}.jsonl").open()]
        for name in ("validation", "test")
    }
    validation_ids = {row["id"] for row in proposed["validation"]}
    test_ids = {row["id"] for row in proposed["test"]}
    assert validation_ids and test_ids and not validation_ids & test_ids
    families_validation = {row["family_id"] for row in proposed["validation"]}
    families_test = {row["family_id"] for row in proposed["test"]}
    assert not families_validation & families_test
    chosen_paths = {row["path"] for split in proposed.values() for row in split}
    assert "held/great_work.ocr.pdf" not in chosen_paths
    assert "people/author/serial.01.pdf" not in chosen_paths
    assert "magazines/zine/zine.1990.01.pdf" not in chosen_paths
    assert "lib/smith-1974.pdf" not in chosen_paths
    assert "pubs/gazette/gazette_v3_n1_1950.pdf" not in chosen_paths
    assert "lib/d4331c_a1b2c3d4e5f60718293a4b5c6d7e8f90.pdf" in chosen_paths
    assert "magazines/thoth/thviii01.txt" not in chosen_paths
    assert "magazines/lone_issue.pdf" in chosen_paths
    for entry in report["documents"]:
        assert "best_train_neighbor" in entry
    assert {"held/quiet_river.pdf", "held/salt_marsh.pdf", "held/winter_road.pdf"} <= {
        row["path"] for row in proposed["validation"]
    }
    assert (output / "largest-families.jsonl").exists()
    assert (output / "review-queue.jsonl").exists()
    assert (output / "summary.json").exists()
