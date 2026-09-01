from pathlib import Path

from hghost.common import RootSpec, content_hash, normalize_text, parse_roots, size_stratum


def test_normalize_text_is_conservative() -> None:
    raw = "inter-\nnal  \r\n\r\n\r\n\r\nnext\x00"
    assert normalize_text(raw) == "internal\n\n\nnext"


def test_content_hash_ignores_case_and_whitespace() -> None:
    assert content_hash("The  H\n") == content_hash("the h")


def test_size_strata() -> None:
    assert size_stratum(0) == "00_lt_1MiB"
    assert size_stratum(1024 * 1024) == "01_1_to_10MiB"


def test_parse_roots(tmp_path: Path) -> None:
    roots = parse_roots([f"sample={tmp_path}"])
    assert roots == [RootSpec("sample", tmp_path.resolve())]

