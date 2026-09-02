import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from hghost.beliefgeo import (
    DEFAULT_EOS_TOKEN_ID,
    derive_validation_report,
    verify_weave,
    weave_stream,
)
from hghost.roommix import (
    RESIDENT,
    RoomDocument,
    chain_when2speak,
    detokenize,
    find_transcript_blocks,
    invent_names,
    iter_gutenberg_dialogues,
    normalize_label,
    plausible_label,
    render_gutenberg_dialogue,
    render_multilight,
    render_when2speak,
    split_documents,
    split_inline_speakers,
)

EOS = DEFAULT_EOS_TOKEN_ID


# ------------------------------------------------------------------ rendering format


def test_render_is_name_colon_text_with_blank_lines_between_turns() -> None:
    document = RoomDocument(
        id="x",
        source="plato",
        turns=[("Socrates", "Whither away?"), ("Phaedrus", "To walk\noutside the wall."), ("Socrates", "  Good.  ")],
    )
    assert document.render() == (
        "Socrates: Whither away?\n\nPhaedrus: To walk outside the wall.\n\nSocrates: Good."
    )
    assert not document.render().endswith("\n")
    assert document.speakers() == ["Socrates", "Phaedrus"]
    for line in document.render().split("\n\n"):
        name, _, text = line.partition(": ")
        assert name and text and "\n" not in line


def test_empty_turns_are_dropped_and_bad_speakers_rejected() -> None:
    document = RoomDocument(id="x", source="plato", turns=[("A", "hi"), ("B", "   ")])
    assert document.turns == [("A", "hi")]
    with pytest.raises(ValueError):
        RoomDocument(id="x", source="plato", turns=[("A: B", "hi")])
    with pytest.raises(ValueError):
        RoomDocument(id="x", source="plato", turns=[("A", "")])


def test_record_round_trip_keeps_decisions_and_license() -> None:
    document = RoomDocument(
        id="d1",
        source="when2speak",
        turns=[("Mara", "hello"), (RESIDENT, "yes")],
        provenance={"split": "train"},
        h_participant="Assistant ([AGENT])",
        decisions=[{"after_turn": 0, "action": "speak"}],
    )
    record = json.loads(json.dumps(document.to_record()))
    assert record["license"].startswith("CC-BY-4.0")
    restored = RoomDocument.from_record(record)
    assert restored == document


def test_invent_names_are_distinct_and_seeded() -> None:
    first = invent_names(4, np.random.default_rng(3))
    second = invent_names(4, np.random.default_rng(3))
    assert first == second and len(set(first)) == 4


# ------------------------------------------------------------------ h relabeling


def when2speak_records() -> list[dict]:
    def record(context: list[str], decision: str) -> dict:
        return {
            "messages": [{"role": "user", "content": c} for c in context]
            + [{"role": "assistant", "content": decision}]
        }

    turns = [
        "Speaker_0: Has anyone read the new catalogue?",
        "Speaker_1: Only the index, [AGENT] might know more",
        "Speaker_0: It lists every edition since 1968",
        "Speaker_1: What do you think [AGENT]?",
        "Speaker_0: I would like a copy",
    ]
    return [
        record(turns[:1], ">"),
        record(turns[:2], ">"),
        record(turns[:4], "The catalogue is a map of the whole system."),
        record(turns[1:4] + ["Assistant: The catalogue is a map of the whole system."] + turns[4:5], ">"),
    ]


def test_when2speak_chaining_and_relabel_to_h() -> None:
    conversations = chain_when2speak(when2speak_records())
    assert len(conversations) == 1
    conversation = conversations[0]
    assert conversation["records"] == 4
    assert [speaker for speaker, _ in conversation["turns"]] == [
        "Speaker_0", "Speaker_1", "Speaker_0", "Speaker_1", "Assistant", "Speaker_0",
    ]
    assert conversation["decisions"] == [
        {"after_turn": 0, "action": "silent"},
        {"after_turn": 1, "action": "silent"},
        {"after_turn": 3, "action": "speak"},
        {"after_turn": 5, "action": "silent"},
    ]
    document = render_when2speak(conversation, 0, "train", seed=1)
    lines = document.render().split("\n\n")
    names = document.provenance["names"]
    assert set(names) == {"Speaker_0", "Speaker_1"} and len(set(names.values())) == 2
    assert lines[4] == "moderator: The catalogue is a map of the whole system."
    assert lines[1] == f"{names['Speaker_1']}: Only the index, moderator might know more"
    assert lines[3] == f"{names['Speaker_1']}: What do you think moderator?"
    assert "[AGENT]" not in document.render() and "Speaker_" not in document.render()
    assert RESIDENT not in document.speakers()
    assert document.h_participant == "Assistant ([AGENT])"
    assert document.decision_role == "moderator"
    assert document.decisions == conversation["decisions"]


def test_when2speak_new_conversation_starts_without_overlap() -> None:
    records = when2speak_records()
    records.append(
        {
            "messages": [
                {"role": "user", "content": "Speaker_0: A different room entirely"},
                {"role": "assistant", "content": ">"},
            ]
        }
    )
    assert len(chain_when2speak(records)) == 2


def test_multilight_relabels_the_most_talkative_character() -> None:
    episode = {
        "messages": [
            {"speaker": "captain", "text": "Greetings to both of you."},
            {"speaker": "young boy", "text": "Hi Captains!"},
            {"speaker": "captain", "text": "And what did this ghost look like?"},
            {"speaker": "boat captain", "text": "I have not seen that ghost."},
        ]
    }
    document = render_multilight(episode, 0, "train")
    assert document.h_participant == "captain"
    assert document.render() == (
        f"{RESIDENT}: Greetings to both of you.\n\n"
        "young boy: Hi Captains!\n\n"
        f"{RESIDENT}: And what did this ghost look like?\n\n"
        "boat captain: I have not seen that ghost."
    )
    assert document.decisions == [
        {"after_turn": 0, "action": "silent"},
        {"after_turn": 1, "action": "speak"},
        {"after_turn": 2, "action": "silent"},
    ]
    assert document.decision_role == RESIDENT
    assert document.split == "train"
    assert render_multilight(episode, 0, "valid").split == "holdout"


# ------------------------------------------------------------------ corpus extraction

SHARD_TEXT = """\
GROVE DIRECTORY

SD: Jan Curran
Phone: (508) 226-6697
E-mail: jan@example.org
SD: Will Pierson
Phone: (508) 378-2870
Web: http://example.org/grove
SD: Fox
Phone: (773) 489-5765

AN INTERVIEW WITH MARJORIE COURTENAY-LATIMER

Q. How did you first hear of the fish?
A. The captain of the trawler sent a message that they had something unusual, and
I went down to the docks that morning to look at the catch myself.
Q. And what did you see?
A. A fish unlike any I had handled before, with heavy scales and lobed fins that
looked more like limbs than fins.
Q. Did you know what it was?
A. Not at first, although Gilchrist's book on ganoid fish came to mind at once.
Q. What did you do next?
A. I wrote to Dr Smith that same afternoon, and waited.

Page 14

GREENWELL: How did the expedition begin, and who paid for it in the end?
AGNAGNA: The ministry paid for the boats and the guides, and the rest came
from our own pockets, which were not deep.
GREENWELL: Did the animal move slowly or quickly when you saw it?
AGNAGNA: Slowly, at first, and then it went under the water and did not
come up again while we watched.
GREENWELL: Were you frightened?
AGNAGNA: No, but the guides were, and they would not go closer. GREENWELL: How long did you stay?
AGNAGNA: Three hours, until the light went.

The expedition report was published the following spring in the society's
newsletter, with photographs by the author.
"""


def test_extraction_on_a_synthetic_shard() -> None:
    blocks = find_transcript_blocks(SHARD_TEXT)
    assert [block["kind"] for block in blocks] == ["qa", "transcript"]
    interview, transcript = blocks
    speakers = {speaker for speaker, _ in interview["turns"]}
    assert speakers == {"Interviewer", "Marjorie Courtenay-Latimer"}
    assert interview["turns"][1] == [
        "Marjorie Courtenay-Latimer",
        "The captain of the trawler sent a message that they had something unusual, and "
        "I went down to the docks that morning to look at the catch myself.",
    ]
    assert len(interview["turns"]) == 8
    assert [speaker for speaker, _ in transcript["turns"]] == [
        "Greenwell", "Agnagna", "Greenwell", "Agnagna", "Greenwell", "Agnagna", "Greenwell", "Agnagna",
    ]
    assert transcript["turns"][1][1] == (
        "The ministry paid for the boats and the guides, and the rest came from our own "
        "pockets, which were not deep."
    )
    assert transcript["turns"][-1][1] == "Three hours, until the light went."
    assert "expedition report" not in json.dumps(transcript["turns"])
    document = RoomDocument(id="x", source="corpus-native", turns=[tuple(t) for t in transcript["turns"]])
    assert document.render().startswith("Greenwell: How did the expedition begin")


def test_directory_listings_and_field_labels_are_not_transcripts() -> None:
    directory = "\n".join(SHARD_TEXT.split("\n")[:12])
    assert find_transcript_blocks(directory) == []
    assert not plausible_label("Phone")
    assert not plausible_label("This page")
    assert not plausible_label("He said")
    assert plausible_label("Greenwell") and plausible_label("Mr. Smith") and plausible_label("The Bible")


def test_labels_and_inline_speakers() -> None:
    assert normalize_label("SOCRATES") == "Socrates"
    assert normalize_label("HUO") == "HUO"
    assert normalize_label("MR. SMITH") == "Mr. Smith"
    assert split_inline_speakers(
        [["Evo", "What is your goal? DD: To flip out. EVO: And religion?"], ["Dd", "It sucks."]]
    ) == [
        ["Evo", "What is your goal?"],
        ["DD", "To flip out."],
        ["EVO", "And religion?"],
        ["Dd", "It sucks."],
    ]


# ------------------------------------------------------------------ gutenberg


def test_gutenberg_dialogues_are_detokenized_and_alternate_speakers() -> None:
    lines = [
        "nay dreams betoken nought .\n",
        "if i tell thee the dream then shalt thou unriddle it .\n",
        "`` well , '' said she , `` i do n't know . ''\n",
        "it 's mine and i 'm sure he 'd agree .\n",
        "\n",
        "one more .\n",
    ]
    dialogues = list(iter_gutenberg_dialogues(lines))
    assert len(dialogues) == 2 and len(dialogues[0]) == 4
    assert detokenize(dialogues[0][2]) == '"Well," said she, "I don\'t know."'
    assert detokenize(dialogues[0][3]) == "It's mine and I'm sure he'd agree."
    turns = render_gutenberg_dialogue(dialogues[0], np.random.default_rng(0))
    names = [speaker for speaker, _ in turns]
    assert len(set(names)) == 2 and names[0] == names[2] and names[1] == names[3]
    assert turns[0][1] == "Nay dreams betoken nought."
    for _ in range(50):
        turns = render_gutenberg_dialogue(list(dialogues[0]) * 2, np.random.default_rng(_))
        assert all(a[0] != b[0] for a, b in zip(turns, turns[1:]))


# ------------------------------------------------------------------ weave


def test_weave_variable_length_rooms_preserves_v1_bytes(tmp_path: Path) -> None:
    rng = np.random.default_rng(1)
    pieces = []
    for length in (5, 9, 3, 7):
        pieces.append(rng.integers(12, 1000, size=length))
        pieces.append([EOS])
    stream = np.concatenate(pieces).astype(np.uint16)
    rooms = np.concatenate(
        [[300, 301, EOS], [400, 401, 402, 403, EOS], [500, EOS]]
    ).astype(np.uint16)
    documents = split_documents(rooms, EOS)
    assert [len(d) for d in documents] == [3, 5, 2]
    slots = np.array([4, 0, 2])
    output = tmp_path / "train.bin"
    plan = weave_stream(stream, documents, slots, output, EOS)
    woven = np.fromfile(output, dtype="<u2")
    assert woven.shape[0] == plan["tokens"] == stream.shape[0] + rooms.shape[0]
    assert plan["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert [g["slot"] for g in plan["insertions"]] == [0, 2, 4]
    assert [g["tokens"] for g in plan["insertions"]] == [5, 2, 3]
    kept = np.ones(woven.shape[0], dtype=bool)
    for group in plan["insertions"]:
        start = group["v11_offset"]
        kept[start : start + group["tokens"]] = False
    np.testing.assert_array_equal(woven[kept], stream)
    np.testing.assert_array_equal(woven[:5], [400, 401, 402, 403, EOS])
    np.testing.assert_array_equal(woven[-3:], [300, 301, EOS])
    verification = verify_weave(stream, documents, plan, output)
    assert verification == {
        "v1_tokens_identical": int(stream.shape[0]),
        "synthetic_tokens": int(rooms.shape[0]),
        "ok": True,
    }
    woven[plan["insertions"][1]["v11_offset"] + 3] ^= 1
    woven.tofile(output)
    with pytest.raises(ValueError):
        verify_weave(stream, documents, plan, output)


def test_derive_validation_report_accepts_total_tokens() -> None:
    v1_report = {
        "schema_version": 1,
        "selected_documents": 10,
        "splits": {
            "train": {
                "documents": 4,
                "source_tokens": 20,
                "dataset_source_tokens": 20,
                "tokenized_source_tokens": 20,
                "eos_tokens": 4,
                "tokens_including_eos": 24,
                "bytes": 48,
                "sha256": "a" * 64,
                "minimum_token_id": EOS,
                "maximum_token_id": 999,
            },
            "validation": {"documents": 1, "sha256": "c" * 64},
        },
    }
    report = derive_validation_report(
        v1_report,
        {"tokens": 34, "sha256": "d" * 64},
        {"documents": 3, "tokens": 10, "minimum_token_id": 11, "maximum_token_id": 500},
    )
    train = report["splits"]["train"]
    assert train["documents"] == 7 and train["eos_tokens"] == 7
    assert train["source_tokens"] == 27 and train["tokens_including_eos"] == 34
    assert report["selected_documents"] == 13


def test_choose_holdout_water_fills_across_sources() -> None:
    from hghost.roommix import choose_holdout

    documents = []
    for source, n in (("plato", 2), ("when2speak", 50), ("multilight", 50)):
        for i in range(n):
            documents.append(
                RoomDocument(id=f"{source}{i}", source=source, turns=[("A", "x")], split="holdout")
            )
    documents.append(RoomDocument(id="t", source="plato", turns=[("A", "x")], split="train"))
    counts = np.full(len(documents), 100)
    chosen = choose_holdout(documents, counts, 3000, np.random.default_rng(0))
    by_source = {}
    for index in chosen:
        by_source[documents[index].source] = by_source.get(documents[index].source, 0) + 1
    assert by_source["plato"] == 2
    assert by_source["when2speak"] + by_source["multilight"] == 28
    assert abs(by_source["when2speak"] - by_source["multilight"]) <= 1
    assert all(documents[index].split == "holdout" for index in chosen)
    assert chosen == choose_holdout(documents, counts, 3000, np.random.default_rng(0))


# ------------------------------------------------------------------ coordinator additions


def test_frames_verbatim_and_varied() -> None:
    from hghost.roommix import FRAMES, make_frame

    assert FRAMES["a"].startswith("THE READING ROOM\n\nAn interview with h")
    assert "h has read\nthe whole collection" in FRAMES["a"]
    assert "It does not\nexplain itself." in FRAMES["a"]
    seen = {"verbatim": set(), "varied": set()}
    rng = np.random.default_rng(0)
    for _ in range(400):
        key, varied, text = make_frame(rng)
        assert key in FRAMES
        if varied:
            seen["varied"].add(key)
            assert text.count("\n") == FRAMES[key].count("\n")
            assert text.split(".")[0][:12] == FRAMES[key].split(".")[0][:12]
        else:
            seen["verbatim"].add(key)
            assert text == FRAMES[key]
    assert seen["verbatim"] == set(FRAMES) and seen["varied"] == set(FRAMES)
    document = RoomDocument(
        id="x", source="plato", turns=[("Socrates", "Whither?"), ("Phaedrus", "Out.")], frame=FRAMES["a"]
    )
    assert document.render() == FRAMES["a"] + "\n\nSocrates: Whither?\n\nPhaedrus: Out."
    assert RoomDocument.from_record(json.loads(json.dumps(document.to_record()))) == document


def test_relabel_interview_answerer_as_h() -> None:
    from hghost.roommix import QUESTIONER_HANDLES, questioner_answerer, relabel_answerer

    qa = RoomDocument(
        id="abcdef0123456789ffff",
        source="corpus-native",
        turns=[("Interviewer", "How did it begin?"), ("Interviewee", "With a letter."),
               ("Interviewer", "And then?"), ("Interviewee", "Then a boat.")],
        provenance={"kind": "qa", "path": "p.pdf"},
    )
    assert questioner_answerer(qa) == ("Interviewer", "Interviewee")
    relabeled = relabel_answerer(qa, seed=0)
    questioner = relabeled.turns[0][0]
    assert questioner in QUESTIONER_HANDLES
    assert relabeled.render() == (
        f"{questioner}: How did it begin?\n\nh: With a letter.\n\n{questioner}: And then?\n\nh: Then a boat."
    )
    assert relabeled.source == "corpus-native-h" and relabeled.h_participant == "Interviewee"
    assert relabeled.provenance["relabeled_from"] == {
        "id": qa.id, "questioner": "Interviewer", "questioner_rendered": questioner, "answerer": "Interviewee",
    }
    assert relabeled.decisions == [
        {"after_turn": 0, "action": "speak"}, {"after_turn": 1, "action": "silent"},
        {"after_turn": 2, "action": "speak"},
    ]
    assert relabeled.decision_role == RESIDENT
    assert relabel_answerer(qa, seed=0).turns[0][0] == questioner  # seeded per document

    named = RoomDocument(
        id="0123456789abcdef0000",
        source="corpus-native",
        turns=[("Greenwell", "Did it move?"), ("Agnagna", "Slowly."), ("Greenwell", "Were you afraid?"),
               ("Agnagna", "No, the guides were."), ("Greenwell", "How long did you stay?"), ("Agnagna", "Three hours.")],
        provenance={"kind": "transcript"},
    )
    assert questioner_answerer(named) == ("Greenwell", "Agnagna")
    assert relabel_answerer(named, seed=0).speakers() == ["Greenwell", "h"]

    editor = RoomDocument(
        id="00000000000000000001", source="corpus-native",
        turns=[("Reader", "I disagree with the review."), ("Editor", "Noted, and thank you."),
               ("Reader", "The map was wrong too."), ("Editor", "Corrected in this issue.")],
        provenance={"kind": "transcript"},
    )
    assert questioner_answerer(editor) == ("Reader", "Editor")
    assert relabel_answerer(editor, seed=1).turns[0][0] in QUESTIONER_HANDLES

    chat = RoomDocument(
        id="00000000000000000002", source="corpus-native",
        turns=[("A", "Yes."), ("B", "No."), ("A", "Maybe."), ("B", "Fine.")], provenance={"kind": "transcript"},
    )
    assert questioner_answerer(chat) is None and relabel_answerer(chat, seed=0) is None


def test_prerendered_scenes_are_used_verbatim(tmp_path: Path) -> None:
    from hghost.roommix import FRAMES, read_rendered

    text = FRAMES["c"] + "\n\nmira: Is anyone there?\n\nh: The lamp is lit.\n"
    path = tmp_path / "scenes-rendered.jsonl"
    path.write_text(json.dumps({"id": "s1", "kind": "visit", "text": text}) + "\n", encoding="utf-8")
    documents = list(read_rendered(path, repeat=3))
    assert len(documents) == 3 and len({d.id for d in documents}) == 3
    document = documents[0]
    assert document.render() == text.rstrip("\n")
    assert document.speakers() == ["mira", "h"] and document.h_participant == "h"
    assert document.provenance == {"file": "scenes-rendered.jsonl", "scene_id": "s1", "kind": "visit", "repeat": 0}
    assert RoomDocument.from_record(json.loads(json.dumps(document.to_record()))) == document


def test_inline_question_answer_labels_are_split() -> None:
    from hghost.roommix import split_inline_qa

    turns = [
        ["Q", "Hillary… -Answer: She’s got lying eyes. Kind of like Clint Eastwood."],
        ["Q", "There is another picture of --Answer: The key is the eyes. Q. And the mouth? A. Also."],
        ["A", "Plain answer, no labels."],
    ]
    assert split_inline_qa(turns) == [
        ["Q", "Hillary…"],
        ["A", "She’s got lying eyes. Kind of like Clint Eastwood."],
        ["Q", "There is another picture of"],
        ["A", "The key is the eyes."],
        ["Q", "And the mouth?"],
        ["A", "Also."],
        ["A", "Plain answer, no labels."],
    ]
    text = (
        "Question: Why did you leave the observatory that winter?\n"
        "Answer: Because the funding ran out before the lenses arrived. Question: And when "
        "did the lenses finally come? --Answer: They came in the spring, by sea, packed in "
        "straw.\n"
        "Question: Where were they installed in the end?\n"
        "Answer: In the smaller dome on the hill above the town. Question: Who did the "
        "installation work?\n"
        "Answer: Two of my students and the carpenter from the village.\n"
    )
    blocks = find_transcript_blocks(text, min_turns=4)
    assert len(blocks) == 1
    assert [speaker for speaker, _ in blocks[0]["turns"]] == ["Interviewer", "Interviewee"] * 4
    assert blocks[0]["turns"][3][1] == "They came in the spring, by sea, packed in straw."
