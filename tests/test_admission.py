import json
from pathlib import Path

import pytest

from hghost.admission import (
    FORM_FEED,
    Dictionary,
    FurnitureCatalogue,
    cell_for,
    column_layout,
    column_order_phrases,
    evaluate_check,
    fidelity_score,
    furniture_line_kinds,
    guess_year,
    gutter_line_count,
    gutter_line_count_text,
    inner_caps_count,
    inner_caps_count_text,
    language_guess,
    longest_valid_run,
    mixed_token_count,
    noisy_or,
    page_checks,
    parse_bbox_layout,
    phrase_precedes,
    ramp,
    reading_view,
    restore,
    running_heads,
    single_char_line_stats,
    spaced_letter_count,
    stratified_pick,
    table_row_count,
    text_layer_origin,
    text_signals,
    tier_for,
    typography_guess,
    value_score,
)

CLEAN = (
    "The library keeps its own hours. Visitors arrive after dark and read until the lamps are "
    "turned down, and the books answer in the words they already contain. Nobody has counted the "
    "rooms; the catalogue lists more than the building holds.\n\n"
) * 12

NOISY = (
    "jijicaiSflii ! ! i\nBS\n7\n*\n\nE\nL\nA\nD\nK\nO\n\nEdit oriel A d d r e s s\n"
    "!li!li�.N���\n(fl Contact (UK) publicati on)\n"
    "Coo6wenue o ecmpere cmernepogott rKopossi\n"
) * 20


def test_ramp_and_noisy_or_are_monotone():
    assert ramp(0.0, 0.1, 0.5) == 0.0
    assert ramp(0.3, 0.1, 0.5) == pytest.approx(0.5)
    assert ramp(0.9, 0.1, 0.5) == 1.0
    with pytest.raises(ValueError):
        ramp(0.1, 0.5, 0.1)
    assert noisy_or([]) == 0.0
    assert noisy_or([(1.0, 1.0)]) == 1.0
    assert noisy_or([(0.5, 0.5)]) == pytest.approx(0.25)
    assert noisy_or([(0.5, 0.5), (0.5, 0.5)]) > noisy_or([(0.5, 0.5)])


def test_single_char_line_stats_counts_runs():
    lines = ["Title", "E", "L", "A", "D", "", "K", "text here", "x", "y"]
    count, longest, nonblank = single_char_line_stats(lines)
    assert (count, longest, nonblank) == (7, 5, 9)


def test_spaced_letters_and_inner_caps_and_mixed_tokens():
    assert spaced_letter_count("the e d i t i o n of the N i g h t") == 12
    assert spaced_letter_count("a b c") == 0  # runs shorter than four letters are not counted
    words = ["jijicaiSflii", "McDonald", "HELLO", "walked", "iPhone"]
    assert inner_caps_count(words) == 3
    text = "jijicaiSflii McDonald HELLO walked iPhone"
    assert inner_caps_count_text(text) == inner_caps_count(words)
    assert mixed_token_count(["!li!li�.N", "Coo6wenue1", "word,", "(word)", "12,000", "abc-def", "x9y"]) == 3


def test_gutter_lines_agree_between_implementations_and_stay_linear():
    text = "left column text    right column text\nplain line\n" + "a" * 50000 + "   bb\n"
    assert gutter_line_count(text.split("\n")) == gutter_line_count_text(text) == 2


def test_language_guess():
    assert language_guess(CLEAN.split())[0] == "en"
    german = ["Der", "Mann", "und", "die", "Frau", "sind", "nicht", "mit", "dem", "Kind", "auf", "der", "Straße,", "das", "ist", "eine", "Sache"]
    assert language_guess(german)[0] == "de"
    assert language_guess(["Слово", "и", "дело", "русский"])[0] == "ru"
    assert language_guess(["円盤", "のことなど", "知", "らなか"])[0] == "ja"
    assert language_guess(["الحكم", "منصب", "على"])[0] == "ar"
    assert language_guess([])[0] == "unknown"


def test_running_heads_are_page_edge_lines_repeated_across_pages():
    pages = []
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]
    for number in range(6):
        pages.append(f"THE JOURNAL OF THINGS\nbody text about {words[number]} with enough words to matter\n"
                     f"and another line of the body on {words[number]}\n{number + 10}")
    heads, pages_with = running_heads(pages)
    assert heads == ["the journal of things"]  # page numbers are not running heads
    assert pages_with == 6
    assert running_heads(pages[:2]) == ([], 0)


def test_furniture_patterns():
    assert furniture_line_kinds("This content downloaded from 108.12.255.145 on Sat, 09 Nov 2024") == ["jstor_download"]
    assert furniture_line_kinds("All use subject to https://about.jstor.org/terms") == ["jstor_terms"]
    assert furniture_line_kinds("108.12.255.145 on Sat, 09 Nov 2024 09:14:54 UTC") == ["jstor_ip_timestamp"]
    assert furniture_line_kinds("Digitized by the Internet Archive") == ["ia_digitized"]
    assert furniture_line_kinds("mirrored file at http://SaturnianCosmology.Org/") == ["saturnian_mirror"]
    assert furniture_line_kinds("The visitors read until the lamps were turned down.") == []


def test_furniture_catalogue_loads_lines_from_haunting_index_records(tmp_path: Path):
    path = tmp_path / "furniture.jsonl"
    rows = [
        {"documents": 130, "text": "No part of this book may be reproduced in any form, by print\nphotoprint, microfilm, or any other means"},
        {"documents": 3, "text": "a rare sentence shared by three volumes of one work only here"},
        {"documents": 269, "text": " . . . . . . . ."},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows))
    catalogue = FurnitureCatalogue.load([path])
    assert "No part of this book may be reproduced in any form, by print" in catalogue
    assert "photoprint, microfilm, or any other means" in catalogue
    assert "a rare sentence shared by three volumes of one work only here" not in catalogue
    assert len(catalogue) == 2


def test_reading_view_strips_furniture_and_is_reversible():
    catalogue = FurnitureCatalogue({"no part of this book may be reproduced in any form": 130})
    text = (
        "RUNNING HEAD\n"
        "12\n"
        "The first paragraph of the work, which must survive.\n"
        "Contents . . . . . . . . . . 7\n"
        "This content downloaded from 108.12.255.145 on Sat, 09 Nov 2024 09:14:54 UTC\n"
        "All use subject to https://about.jstor.org/terms\n"
        "No part of this book may be reproduced in any form\n"
        "E\nL\nA\nD\nK\n"
        "----------------\n"
        "The second paragraph, also kept.\n"
        "13\n"
        f"{FORM_FEED}RUNNING HEAD\n"
        "Third paragraph on the next page.\n"
    )
    view, transforms = reading_view(text, heads=["running head"], catalogue=catalogue)
    assert "must survive" in view and "also kept" in view and "Third paragraph" in view
    assert "downloaded from" not in view and "jstor" not in view
    assert "No part of this book" not in view
    assert "RUNNING HEAD" not in view
    assert "\n12\n" not in view and "\n13\n" not in view
    assert "----" not in view
    assert "Contents … 7" in view
    assert "\nE\nL\nA\n" not in view
    assert FORM_FEED in view  # page structure is kept
    kinds = {t.kind for t in transforms}
    assert {"running_head", "page_number", "furniture:jstor_download", "furniture:catalogue", "dot_leader", "single_char_run", "rule"} <= kinds
    # The transform log restores the original exactly.
    kept_lines = []
    lines = text.split("\n")
    removed = {t.line for t in transforms if t.replacement is None}
    replaced = {t.line: t.replacement for t in transforms if t.replacement is not None}
    for index, line in enumerate(lines):
        if index in removed:
            continue
        kept_lines.append(replaced.get(index, line))
    assert restore(kept_lines, transforms) == lines


def test_reading_view_keeps_prose_untouched():
    view, transforms = reading_view(CLEAN)
    assert view == CLEAN.strip("\n") or view == CLEAN
    assert transforms == []


def test_text_signals_separate_clean_from_noisy():
    dictionary = Dictionary(["library", "keep", "hour", "visitor", "arrive", "dark", "read", "lamp", "turn", "book", "answer", "word", "contain", "count", "room", "catalogue", "list", "more", "than", "building", "hold", "after", "until", "down", "already", "nobody"])
    df = {"library": 50, "visitors": 20, "lamps": 5, "catalogue": 40, "building": 60, "jijicaisflii": 1, "coo6wenue": 1}
    clean = text_signals(CLEAN, tokens=int(len(CLEAN.split()) * 1.3), df=df, dictionary=dictionary)
    noisy = text_signals(NOISY, tokens=int(len(NOISY.split()) * 2.4), df=df, dictionary=dictionary)
    assert clean["language"] == "en"
    assert clean["single_char_line_ratio"] == 0 and noisy["single_char_line_ratio"] > 0.2
    assert noisy["spaced_letter_ratio"] > clean["spaced_letter_ratio"]
    assert noisy["inner_caps_ratio"] > clean["inner_caps_ratio"]
    assert noisy["mixed_token_ratio"] > clean["mixed_token_ratio"]
    assert noisy["replacement_ratio"] > 0 == clean["replacement_ratio"]
    assert clean["dictionary_ratio"] > 0.9
    assert clean["hapax_ratio"] < 0.05  # "they" is the one word outside the toy dictionary and df
    clean_fidelity, _ = fidelity_score(clean)
    noisy_fidelity, badness = fidelity_score(noisy)
    assert clean_fidelity > 0.9
    assert noisy_fidelity < 0.3
    assert badness["single_char_line_ratio"] == 1.0


def test_value_score_tiers_and_penalties():
    signals = {"rare_valid_ratio": 0.0, "numeric_ratio": 0.0, "repeated_line_ratio": 0.0, "type_token_ratio_20k": 0.3, "alpha_words": 5000}
    library, _ = value_score(signals, "A", 10_000)
    mirror, _ = value_score(signals, "B", 10_000)
    dump, parts = value_score({**signals, "credential_dump_indicators": 2}, "A", 10_000)
    assert library > mirror > dump
    assert parts["credential_dump"] < 0
    table, parts = value_score({**signals, "numeric_ratio": 0.5}, "A", 10_000)
    assert table < library and parts["numeric"] < 0
    judged, parts = value_score(signals, "B", 10_000, judge_delta=-0.3)
    assert judged > mirror and parts["judge"] > 0


def test_cell_table():
    assert cell_for(0.9, 0.9) == "main"
    assert cell_for(0.9, 0.2) == "specialist"
    assert cell_for(0.2, 0.9) == "quarantine"
    assert cell_for(0.2, 0.2) == "drop"


def test_tier_year_and_typography_guesses():
    assert tier_for("rat_palace", "magazines/october/october.1977.003.pdf")[0] == "A"
    assert tier_for("cathedral", "the-cryptozoological-library/ISC Newsletter - Vol 05 No 1 - 1986.pdf")[0] == "B"
    assert tier_for("rat_palace", "culture/thegame23/kVYSHbe1.txt")[0] == "C"
    assert tier_for("cathedral", "illinois-patch-2024-flag-design-submissions-foia_redacted/x.pdf")[0] == "C"
    assert guess_year("magazines/october/october.1977.003.pdf") == 1977
    assert guess_year("magazines/awareness/Awareness_1975_Vol_04_No_4_Winter.pdf") == 1975
    assert guess_year("people/steen/Epstein files 04.01.2024.pdf") == 2024
    assert guess_year("arts/de sculptura.pdf") is None
    assert typography_guess(1890, False) == "letterpress"
    assert typography_guess(1977, False) == "phototypeset"
    assert typography_guess(None, True) == "digital"
    assert text_layer_origin("ABBYY FineReader 11", None) == "ocr_layer"
    assert text_layer_origin("pdfTeX-1.40", "LaTeX with hyperref") == "born_digital"
    assert text_layer_origin("pikepdf 10.2.0", "OCRmyPDF 16.13.0 / Tesseract OCR-hOCR 5.5.2") == "ocr_layer"
    assert text_layer_origin(None, None) == "unknown"


def test_dictionary_suffix_stripping():
    dictionary = Dictionary(["house", "walk", "happy", "city"])
    for word in ("house", "houses", "walked", "walking", "happily", "cities", "Walks"):
        assert word in dictionary, word
    assert "jijicaisflii" not in dictionary


def bbox_xml(blocks):
    """Minimal pdftotext -bbox-layout output: blocks are ((x0, y0, x1, y1), [line words...])."""
    parts = ['<?xml version="1.0"?>\n<html><body><doc><page width="612" height="792">']
    for (x0, y0, x1, y1), lines in blocks:
        parts.append(f'<flow><block xMin="{x0}" yMin="{y0}" xMax="{x1}" yMax="{y1}">')
        for number, line in enumerate(lines):
            y = y0 + 12 * number
            words = "".join(f'<word xMin="{x0 + 30 * i}" yMin="{y}" xMax="{x0 + 30 * i + 28}" yMax="{y + 10}">{w}</word>' for i, w in enumerate(line.split()))
            parts.append(f'<line xMin="{x0}" yMin="{y}" xMax="{x1}" yMax="{y + 10}">{words}</line>')
        parts.append("</block></flow>")
    parts.append("</page></doc></body></html>")
    return "\n".join(parts)


BBOX = bbox_xml([
    ((50, 60, 290, 400), ["left column opens here", "with a second line of text", "and a third line follows", "and the left column ends"]),
    ((320, 60, 560, 400), ["right column begins now", "with its own second line", "and a third line too", "and continues to the end"]),
    ((50, 700, 560, 712), ["a full width footer"]),
])


def test_bbox_layout_columns_and_order_check():
    width, height, blocks = parse_bbox_layout(BBOX)
    assert (width, height) == (612.0, 792.0)
    assert len(blocks) == 3
    columns = column_layout(width, blocks)
    assert len(columns) == 2  # the full-width footer is not a column
    order = column_order_phrases(columns)
    assert order == ("and the left column ends", "right column begins now")
    good = "left column opens here ... and the left column ends\nright column begins now ... and continues to the end"
    scrambled = "left column opens here right column begins now\nand the left column ends and continues to the end"
    assert phrase_precedes(good, *order) is True
    assert phrase_precedes(scrambled, *order) is False
    assert phrase_precedes("nothing here", *order) is None


def test_longest_valid_run_and_table_rows():
    valid = {"the", "library", "keeps", "its", "own", "hours", "visitors", "arrive", "after", "dark"}
    text = "jijicai The library keeps its own hours. Visitors arrive after dark xqzt and more"
    assert longest_valid_run(text, lambda w: w.casefold() in valid) == "The library keeps its own hours. Visitors arrive after dark"
    assert longest_valid_run("xq zz yy", lambda w: False) is None
    assert longest_valid_run("one two three\n\nfour five six seven", lambda w: True, min_words=4) == "four five six seven"
    assert table_row_count(["Item 1 2 3", "1970 12.5 40%", "just words", "9 8"]) == 2


def test_page_checks_and_evaluation():
    width, _, blocks = parse_bbox_layout(BBOX)
    page = ("THE JOURNAL\nleft column opens here\nwith a second line of text\nand a third line follows\nand the left column ends\n"
            "right column begins now\nwith its own second line\nand a third line too\nand continues to the end\n"
            "This content downloaded from 1.2.3.4 on Sat\nE\nL\nA\nD\nK\n")
    valid = {"left", "column", "opens", "here", "with", "a", "second", "line", "of", "text", "and", "third", "follows", "the", "ends", "right", "begins", "now", "its", "own", "too", "continues", "to", "end", "journal"}
    checks = page_checks(page, blocks=blocks, width=width, heads=["the journal"], is_valid=lambda w: w.casefold() in valid, catalogue=None)
    kinds = [check["kind"] for check in checks]
    assert kinds == ["must_contain", "must_not_contain", "must_not_contain", "column_order", "no_single_letter_run", "no_invented_text", "page_alignment"]
    view, _ = reading_view(page, heads=["the journal"])
    results = {check["kind"] + str(i): evaluate_check(check, page, view) for i, check in enumerate(checks)}
    assert results["must_contain0"] == {"raw": True, "view": True}
    assert results["must_not_contain1"]["raw"] is False and results["must_not_contain1"]["view"] is True
    assert results["column_order3"]["raw"] is True
    assert results["no_single_letter_run4"] == {"raw": False, "view": True}
    assert results["page_alignment6"]["raw"] is True


def test_stratified_pick_covers_every_stratum_once_before_repeating():
    candidates = []
    for number in range(40):
        candidates.append({"id": f"d{number}", "strata": {"noise": ["clean", "noisy"][number % 2], "source": ["a", "b"][(number // 2) % 2]}})
    chosen = stratified_pick(candidates, 8, ("noise", "source"), seed=1)
    assert len(chosen) == 8
    from collections import Counter
    assert Counter((c["strata"]["noise"], c["strata"]["source"]) for c in chosen) == Counter({("clean", "a"): 2, ("clean", "b"): 2, ("noisy", "a"): 2, ("noisy", "b"): 2})
    assert len({c["id"] for c in chosen}) == 8
