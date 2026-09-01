import argparse
import array
import csv
import gzip
import hashlib
import json
import zipfile
from pathlib import Path

from hghost.build_dataset import (
    bottom_k_resemblance,
    bottom_k_word_shingles,
    run as build_dataset,
)
from hghost.census import TokenCounter
from hghost.extract import ExtractionJob, extract_one, is_redundant_text_pdf, read_epub_text
from hghost.common import Document
from hghost.ocr import languages_for
from hghost.paddle_ocr import discover as discover_paddle_jobs
from hghost.paddle_ocr import page_from_result, text_from_pages
from hghost.quality import quality_flags, recommended_exclusion_reasons, text_quality_metrics
from hghost.tokenize_dataset import write_split
from hghost.train_tokenizer import run as train_tokenizer
from hghost.validate_dataset import run as validate_dataset
from hghost.review_ocr import apply_sheet, make_sheet, records_by_id
from hghost.seal_corpus import run as seal_corpus


def make_document(root: Path, name: str, text: str) -> Document:
    path = root / name
    path.write_text(text, encoding="utf-8")
    return Document("sample", root, path, path.stat().st_size)


def test_extract_resume_and_exact_dedupe(tmp_path: Path) -> None:
    root = tmp_path / "source"
    output = tmp_path / "extracted"
    dataset = tmp_path / "dataset"
    root.mkdir()
    text = ("A sufficiently long haunted sentence about breath and language. " * 40).strip()
    documents = [
        make_document(root, "one.txt", text),
        make_document(root, "two.txt", text.upper()),
    ]
    counter = TokenCounter(None)
    for document in documents:
        result = extract_one(
            ExtractionJob(document, "plain_text"), output, counter, timeout=10, overwrite=False
        )
        assert result["status"] == "ready"
    resumed = extract_one(
        ExtractionJob(documents[0], "plain_text"), output, counter, timeout=10, overwrite=False
    )
    assert resumed["status"] == "skipped_existing"

    manifest = build_dataset(
        argparse.Namespace(
            records=output / "records",
            output=dataset,
            validation_fraction=0.5,
            tokens_per_shard=10_000,
        )
    )
    assert manifest["exact_duplicates_removed"] == 1
    assert sum(manifest["splits"][split]["documents"] for split in ("train", "validation")) == 1


def test_near_duplicate_sketch_tolerates_small_edits() -> None:
    common = " ".join(f"word{index}" for index in range(2_000))
    edited = common.replace("word950", "apparition").replace("word1200", "specter")
    left = bottom_k_word_shingles(common, 192)
    right = bottom_k_word_shingles(edited, 192)
    assert bottom_k_resemblance(left, right, 192) > 0.92


def test_quality_audit_flags_repetitive_noise() -> None:
    line = "THIS IS A REPEATED SCANNER WATERMARK WITH SYMBOLS @@@"
    text = "\n".join([line] * 100)
    record = {
        "tokens": 2_000,
        "words": 900,
        "alpha_ratio": 0.70,
        "replacement_ratio": 0.0,
    }
    metrics = text_quality_metrics(text, record)
    assert "repetitive_lines" in quality_flags(record, metrics)


def test_quality_audit_allows_structural_page_breaks() -> None:
    text = ("A normal page of prose.\n" * 50) + "\f" + ("Another normal page.\n" * 50)
    metrics = text_quality_metrics(text, {"tokens": 500})
    assert metrics["control_ratio"] == 0


def test_quality_audit_flags_credential_dump_without_retaining_values() -> None:
    hashes = "\n".join("*" + (f"{index:040X}") for index in range(4))
    text = "| Password |\n" + hashes
    metrics = text_quality_metrics(text, {"tokens": 20})
    assert metrics["credential_indicator_count"] == 1
    assert metrics["credential_dump_indicator_count"] == 1
    assert "credential_material" in quality_flags({}, metrics)
    assert recommended_exclusion_reasons({}, quality_flags({}, metrics), metrics) == [
        "credential_dump"
    ]


def test_quality_audit_does_not_exclude_incidental_token() -> None:
    text = "A security paper quoted sk-" + "a" * 30 + " as an example."
    metrics = text_quality_metrics(text, {"tokens": 20})
    flags = quality_flags({}, metrics)
    assert "credential_material" in flags
    assert metrics["credential_dump_indicator_count"] == 0
    assert recommended_exclusion_reasons({}, flags, metrics) == []


def test_paddle_page_text_uses_reading_order_and_ignores_images() -> None:
    pages = [
        {
            "page_index": 0,
            "width": 100,
            "height": 100,
            "blocks": [
                {"label": "text", "content": "second", "order": 2},
                {
                    "label": "image",
                    "content": "hallucinated image",
                    "order": None,
                    "bbox": [0, 0, 10, 10],
                },
                {"label": "paragraph_title", "content": "first", "order": 1},
            ],
        }
    ]
    assert text_from_pages(pages) == "first\n\nsecond"


def test_paddle_result_accepts_mapping_blocks_without_get() -> None:
    class PaddleBlock:
        def __init__(self) -> None:
            self.values = {
                "block_label": "text",
                "block_content": "a recovered sentence",
                "block_bbox": [1, 2, 3, 4],
                "block_order": 1,
                "group_id": 0,
            }

        def __getitem__(self, key: str):
            return self.values[key]

    page = page_from_result(
        {"parsing_res_list": [PaddleBlock()], "width": 100, "height": 200}, 0
    )
    assert page["blocks"][0]["content"] == "a recovered sentence"


def test_paddle_discovery_prefers_larger_bounded_documents(tmp_path: Path) -> None:
    records = tmp_path / "records" / "sample"
    records.mkdir(parents=True)
    from hghost.extract import atomic_json_gzip

    for pages in (1, 8, 24, 100):
        atomic_json_gzip(
            records / f"{pages}.json.gz",
            {
                "document_id": str(pages),
                "source": "sample",
                "relative_path": f"{pages}.pdf",
                "status": "needs_ocr",
                "pages": pages,
                "original_bytes": pages * 1_000,
            },
        )
    jobs = discover_paddle_jobs(tmp_path / "records", None, False, 4, 80)
    assert [record["pages"] for _, record in jobs] == [24, 8]


def test_token_stream_adds_document_eos(tmp_path: Path) -> None:
    class Encoding:
        def __init__(self, ids: list[int]) -> None:
            self.ids = ids

    class Tokenizer:
        def encode(self, text: str, add_special_tokens: bool = False) -> Encoding:
            assert not add_special_tokens
            return Encoding([len(word) for word in text.split()])

    source = tmp_path / "train-00000.jsonl.gz"
    records = [
        {"text": "one three", "tokens": 2},
        {"text": "seven", "tokens": 1},
    ]
    with gzip.open(source, "wt", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")
    output = tmp_path / "train.bin"
    result = write_split([source], output, Tokenizer(), eos_token_id=11)
    values = array.array("H")
    with output.open("rb") as stream:
        values.fromfile(stream, output.stat().st_size // 2)
    assert list(values) == [3, 5, 11, 5, 11]
    assert result["documents"] == 2


def test_corpus_tokenizer_has_fixed_special_ids_and_roundtrips(tmp_path: Path) -> None:
    from tokenizers import Tokenizer
    from tokenizers.decoders import ByteLevel as ByteLevelDecoder
    from tokenizers.models import BPE
    from tokenizers.pre_tokenizers import ByteLevel

    base = Tokenizer(BPE())
    base.pre_tokenizer = ByteLevel(add_prefix_space=False)
    base.decoder = ByteLevelDecoder()
    base_path = tmp_path / "base-tokenizer.json"
    base.save(str(base_path))

    dataset = tmp_path / "dataset"
    dataset.mkdir()
    shard = dataset / "train-00000.jsonl.gz"
    texts = [
        "A haunted archive remembers every page. " * 20,
        "Symbols survive: éther—ghost; Ω; 東京. " * 20,
    ]
    with gzip.open(shard, "wt", encoding="utf-8") as stream:
        for index, text in enumerate(texts):
            stream.write(json.dumps({"id": str(index), "text": text}) + "\n")
    dataset_manifest = {
        "splits": {
            "train": {
                "documents": len(texts),
                "tokens": 1234,
                "shards": [
                    {
                        "path": shard.name,
                        "compressed_bytes": shard.stat().st_size,
                        "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
                    }
                ],
            }
        }
    }
    (dataset / "manifest.json").write_text(json.dumps(dataset_manifest), encoding="utf-8")
    output = tmp_path / "tokenizer"
    result = train_tokenizer(
        argparse.Namespace(
            dataset=dataset,
            base_tokenizer=base_path,
            output=output,
            vocab_size=300,
            min_frequency=1,
            show_progress=False,
        )
    )
    trained = Tokenizer.from_file(str(output / "tokenizer.json"))
    assert result["special_token_ids"] == {
        "pad_token": 0,
        "bos_token": 1,
        "eos_token": 2,
    }
    assert trained.token_to_id("<|pad|>") == 0
    assert trained.token_to_id("<|begin_of_text|>") == 1
    assert trained.token_to_id("<|end_of_text|>") == 2
    for text in texts:
        ids = trained.encode(text, add_special_tokens=False).ids
        assert trained.decode(ids, skip_special_tokens=False) == text
    for name, specification in result["artifacts"].items():
        artifact = output / name
        assert artifact.stat().st_size == specification["bytes"]
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == specification["sha256"]


def test_dataset_validator_checks_shards_splits_and_binary_hashes(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    tokenized = tmp_path / "tokenized"
    dataset.mkdir()
    tokenized.mkdir()
    split_specs = {}
    token_specs = {}
    for split, document_id, content_hash in (
        ("train", "train-id", "a" * 64),
        ("validation", "validation-id", "b" * 64),
    ):
        shard = dataset / f"{split}-00000.jsonl.gz"
        with gzip.open(shard, "wt", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    {
                        "id": document_id,
                        "content_sha256": content_hash,
                        "tokens": 2,
                        "text": "one three",
                    }
                )
                + "\n"
            )
        shard_hash = hashlib.sha256(shard.read_bytes()).hexdigest()
        split_specs[split] = {
            "documents": 1,
            "tokens": 2,
            "shards": [
                {
                    "path": shard.name,
                    "documents": 1,
                    "tokens": 2,
                    "compressed_bytes": shard.stat().st_size,
                    "sha256": shard_hash,
                }
            ],
        }
        binary = tokenized / f"{split}.bin"
        packed = array.array("H", [3, 5, 11])
        with binary.open("wb") as stream:
            packed.tofile(stream)
        token_specs[split] = {
            "path": binary.name,
            "documents": 1,
            "tokens_including_eos": 3,
            "bytes": binary.stat().st_size,
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }
    dataset_manifest = {"splits": split_specs}
    dataset_manifest_path = dataset / "manifest.json"
    dataset_manifest_path.write_text(json.dumps(dataset_manifest), encoding="utf-8")
    (dataset / "duplicates.jsonl").write_text("", encoding="utf-8")
    (dataset / "exclusions_applied.jsonl").write_text("", encoding="utf-8")
    (tokenized / "manifest.json").write_text(
        json.dumps(
            {
                "dtype": "little-endian uint16",
                "tokenizer": "test",
                "vocab_size": 16,
                "eos_token_id": 11,
                "source_manifest_sha256": hashlib.sha256(
                    dataset_manifest_path.read_bytes()
                ).hexdigest(),
                "splits": token_specs,
            }
        ),
        encoding="utf-8",
    )
    report = validate_dataset(
        argparse.Namespace(
            dataset=dataset,
            tokenized=tokenized,
            output=tokenized / "validation-report.json",
        )
    )
    assert report["ok"] is True
    assert report["selected_documents"] == 2
    assert report["cross_split_content_hash_overlap"] == 0
    assert report["splits"]["train"]["dataset_source_tokens"] == 2
    assert report["splits"]["train"]["tokenized_source_tokens"] == 2
    assert report["splits"]["train"]["eos_tokens"] == 1
    bundle = tmp_path / "bundle"
    sealed = seal_corpus(argparse.Namespace(tokenized=tokenized, output=bundle))
    assert sealed["sealed"] is True
    assert set(sealed["files"]) == {
        "train.bin",
        "validation.bin",
        "manifest.json",
        "validation-report.json",
    }
    for name, specification in sealed["files"].items():
        path = bundle / name
        assert path.stat().st_size == specification["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == specification["sha256"]


def test_dataset_validator_allows_a_different_tokenizer_count(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    tokenized = tmp_path / "tokenized"
    dataset.mkdir()
    tokenized.mkdir()
    split_specs = {}
    token_specs = {}
    for split, content_hash in (("train", "a" * 64), ("validation", "b" * 64)):
        shard = dataset / f"{split}-00000.jsonl.gz"
        with gzip.open(shard, "wt", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    {
                        "id": f"{split}-id",
                        "content_sha256": content_hash,
                        "tokens": 2,
                        "text": "a differently tokenized document",
                    }
                )
                + "\n"
            )
        split_specs[split] = {
            "documents": 1,
            "tokens": 2,
            "shards": [
                {
                    "path": shard.name,
                    "documents": 1,
                    "tokens": 2,
                    "compressed_bytes": shard.stat().st_size,
                    "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
                }
            ],
        }
        binary = tokenized / f"{split}.bin"
        packed = array.array("H", [3, 4, 5, 6, 11])
        with binary.open("wb") as stream:
            packed.tofile(stream)
        token_specs[split] = {
            "path": binary.name,
            "documents": 1,
            "tokens_including_eos": 5,
            "bytes": binary.stat().st_size,
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "source_token_count_mismatches": 1,
        }
    dataset_manifest_path = dataset / "manifest.json"
    dataset_manifest_path.write_text(json.dumps({"splits": split_specs}), encoding="utf-8")
    (dataset / "duplicates.jsonl").write_text("", encoding="utf-8")
    (dataset / "exclusions_applied.jsonl").write_text("", encoding="utf-8")
    (tokenized / "manifest.json").write_text(
        json.dumps(
            {
                "dtype": "little-endian uint16",
                "tokenizer": "custom-test",
                "vocab_size": 16,
                "eos_token_id": 11,
                "source_manifest_sha256": hashlib.sha256(
                    dataset_manifest_path.read_bytes()
                ).hexdigest(),
                "splits": token_specs,
            }
        ),
        encoding="utf-8",
    )
    report = validate_dataset(
        argparse.Namespace(
            dataset=dataset,
            tokenized=tokenized,
            output=tokenized / "validation-report.json",
        )
    )
    assert report["splits"]["train"]["dataset_source_tokens"] == 2
    assert report["splits"]["train"]["tokenized_source_tokens"] == 4
    assert report["splits"]["train"]["source_token_count_mismatches"] == 1


def test_record_does_not_train_low_text(tmp_path: Path) -> None:
    root = tmp_path / "source"
    output = tmp_path / "extracted"
    root.mkdir()
    document = make_document(root, "tiny.txt", "not enough")
    result = extract_one(
        ExtractionJob(document, "plain_text"),
        output,
        TokenCounter(None),
        timeout=10,
        overwrite=False,
    )
    assert result["status"] == "rejected_low_text"
    record_path = output / result["record_path"]
    with gzip.open(record_path, "rt", encoding="utf-8") as stream:
        record = json.load(stream)
    assert record["text"] == ""


def test_redundant_ia_text_pdf_detection(tmp_path: Path) -> None:
    original = tmp_path / "book.pdf"
    derived = tmp_path / "book_text.pdf"
    original.touch()
    derived.touch()
    assert is_redundant_text_pdf(derived)
    original.unlink()
    assert not is_redundant_text_pdf(derived)


def test_ocr_language_routes_are_ordered() -> None:
    record = {"source": "rat", "relative_path": "magazines/ostara/one.pdf"}
    rules = [
        {"pattern": "rat/magazines/ostara/**", "languages": ["frk"]},
        {"pattern": "rat/**", "languages": ["deu"]},
    ]
    assert languages_for(record, rules, ["eng"]) == ["frk"]


def test_ocr_review_requires_explicit_decision(tmp_path: Path) -> None:
    records_root = tmp_path / "records" / "sample"
    records_root.mkdir(parents=True)
    record_path = records_root / "abc.json.gz"
    record = {
        "document_id": "abc",
        "source": "sample",
        "relative_path": "scan.pdf",
        "status": "ocr_unreviewed",
        "ocr_languages": ["eng"],
        "pages": 2,
        "tokens": 100,
        "chars": 500,
        "alpha_ratio": 0.8,
        "text": "recognizable text " * 20,
    }
    from hghost.extract import atomic_json_gzip

    atomic_json_gzip(record_path, record)
    records = records_by_id(tmp_path / "records")
    sheet = tmp_path / "review.csv"
    assert make_sheet(records, sheet) == 1
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    rows[0]["decision"] = "accept"
    with sheet.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    assert apply_sheet(records, sheet)["accept"] == 1
    with gzip.open(record_path, "rt", encoding="utf-8") as stream:
        assert json.load(stream)["status"] == "ready"


def test_epub_spine_order(tmp_path: Path) -> None:
    path = tmp_path / "book.epub"
    container = """<container><rootfiles><rootfile full-path="OPS/package.opf"/></rootfiles></container>"""
    package = """<package><manifest><item id="b" href="b.xhtml"/><item id="a" href="a.xhtml"/></manifest><spine><itemref idref="a"/><itemref idref="b"/></spine></package>"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OPS/package.opf", package)
        archive.writestr("OPS/a.xhtml", "<html><body><p>first</p></body></html>")
        archive.writestr("OPS/b.xhtml", "<html><body><p>second</p></body></html>")
    text = read_epub_text(path)
    assert text.index("first") < text.index("second")
