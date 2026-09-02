import json
import random

import pytest

from hghost.roombank import (
    BARE_FRAME,
    KINDS,
    RESIDENT,
    RoomState,
    SCENARIOS,
    addressed_to_h,
    build_pairs,
    cap_history,
    context_lift,
    length_bucket,
    max_overlap,
    normalize_mentions,
    overlap,
    parse_prompt,
    prompt_variant_states,
    render_prompt,
    reply_span,
    scenario_states,
    shuffle_history,
    span_logprob,
    summarize,
    trace_turns,
)

TURNS = [("ember", "hi h"), ("h", "Hello. The lake was covered with blank space."), ("rat", "who are you")]


# ----------------------------------------------------------------------------- rendering


def test_render_is_frame_then_name_colon_text_then_open_h_slot() -> None:
    prompt = render_prompt(BARE_FRAME, TURNS)
    assert prompt == (
        BARE_FRAME + "\n\nember: hi h\n\nh: Hello. The lake was covered with blank space.\n\nrat: who are you\n\nh:"
    )
    assert prompt.endswith("\n\nh:") and not prompt.endswith("\n")


def test_render_flattens_newlines_inside_a_turn_and_allows_no_frame() -> None:
    prompt = render_prompt("", [("cmr://ember", "@h please answer me: \n\nMy previous searches\twere")])
    assert prompt == "cmr://ember: @h please answer me: My previous searches were\n\nh:"


def test_parse_prompt_inverts_render_and_keeps_discord_names() -> None:
    turns = [("cmr://ember", "@h Greetings to planet Earth; are you cogent?"), ("h", "“greetings"), ("cmr://ember", "@h again")]
    frame, parsed = parse_prompt(render_prompt(BARE_FRAME, turns))
    assert frame == BARE_FRAME
    assert parsed == turns
    frame, parsed = parse_prompt(render_prompt("", turns))
    assert frame == "" and parsed == turns


def test_state_requires_a_visitor_last_line_and_ids_are_content_stable() -> None:
    state = RoomState.make("scenario", "direct", TURNS, "x")
    again = RoomState.make("scenario", "direct", [(n, " " + t + " ") for n, t in TURNS], "different note")
    assert state.id == again.id and state.id.startswith("scenario-direct-")
    assert RoomState.from_json(json.loads(json.dumps(state.to_json()))) == state
    with pytest.raises(ValueError):
        RoomState.make("scenario", "direct", TURNS + [("h", "me")], "x")
    with pytest.raises(ValueError):
        RoomState.make("scenario", "no-such-kind", TURNS, "x")
    assert state.h_lines() == [TURNS[1][1]] and state.visitor_lines() == ["hi h", "who are you"]


# ----------------------------------------------------------------------------- shuffling


def test_shuffle_keeps_last_line_last_and_the_multiset_of_turns() -> None:
    turns = [(f"v{i}", f"line {i}") for i in range(6)] + [("rat", "final question")]
    for seed in range(20):
        shuffled = shuffle_history(turns, random.Random(seed))
        assert shuffled[-1] == ("rat", "final question")
        assert sorted(shuffled) == sorted(turns)
        assert shuffled != turns  # the identity carries no signal and is rejected when another order exists
    assert shuffle_history(turns, random.Random(3)) == shuffle_history(turns, random.Random(3))


def test_shuffle_leaves_short_histories_alone() -> None:
    assert shuffle_history(TURNS[:2], random.Random(0)) == TURNS[:2]
    assert shuffle_history(TURNS[:1], random.Random(0)) == TURNS[:1]
    twins = [("a", "same"), ("a", "same"), ("rat", "q")]
    assert shuffle_history(twins, random.Random(0)) == twins


# ---------------------------------------------------------------------------- lift maths


def test_reply_span_indexes_the_losses_of_the_reply_tokens_only() -> None:
    prompt_ids, reply_ids = [5, 6, 7, 8], [9, 10]
    start, stop = reply_span(prompt_ids, reply_ids)
    # losses[t] scores token t+1: the reply tokens sit at positions 4 and 5, i.e. loss indices 3 and 4
    assert (start, stop) == (3, 5)
    losses = [100.0, 100.0, 100.0, 0.5, 1.5, 100.0]  # trailing entry belongs to padding
    assert span_logprob(losses, (start, stop)) == pytest.approx(-2.0)


def test_context_lift_is_true_minus_mean_of_shuffles() -> None:
    assert context_lift(-2.0, [-4.0, -5.0, -6.0]) == pytest.approx(3.0)
    assert context_lift(-7.0, [-4.0, -5.0, -6.0]) == pytest.approx(-2.0)
    assert context_lift(-3.0, [-3.0]) == 0.0
    with pytest.raises(ValueError):
        context_lift(-1.0, [])


def test_length_bucket_fits_a_row_of_n_tokens_at_length_l_plus_one() -> None:
    assert length_bucket(100) == 128
    assert length_bucket(129) == 128
    assert length_bucket(130) == 256
    with pytest.raises(ValueError):
        length_bucket(5000)


def test_summary_counts_positive_lift_and_excludes_unshuffleable_rows() -> None:
    def rec(lift, mode="sample", kind="direct", shuffleable=True):
        return {"lift": lift, "lift_per_token": lift / 4, "tokens": 4, "mode": mode, "kind": kind,
                "shuffleable": shuffleable, "novelty": 0.5, "overlap_room": 0.2, "overlap_self": 0.1,
                "overlap_samples": 0.3}

    summary = summarize([rec(2.0), rec(-1.0), rec(1.0, mode="greedy"), rec(9.0, shuffleable=False)])
    assert summary["n"] == 3 and summary["unshuffleable_replies"] == 1
    assert summary["mean_lift"] == pytest.approx(2 / 3, abs=1e-4)
    assert summary["frac_lift_positive"] == pytest.approx(2 / 3, abs=1e-4)
    assert summary["by_mode"]["greedy"]["n"] == 1 and summary["by_mode"]["sample"]["n"] == 2
    assert summary["by_kind"]["joke"] == {"n": 0}


# ------------------------------------------------------------------------------- overlap


def test_overlap_is_the_proxy_measure() -> None:
    assert overlap("the lake was covered", "the lake was covered with blank space") == 1.0
    assert overlap("a b c d", "c d e f g h") == pytest.approx(0.5)
    assert overlap("", "x") == 0.0
    assert max_overlap("lettuce who", ["knock knock", "lettuce"]) == 1.0
    assert max_overlap("x", []) == 0.0


# ------------------------------------------------------------------------------- sources


def test_trace_turns_use_raw_content_when_the_preview_is_truncated() -> None:
    trace = {
        "botUserId": "123",
        "rawDiscordMessages": [{"id": "m2", "content": "<@123> a very long line\nwith a break"}],
        "contextBuild": {"messages": [
            {"participant": "cmr://ember", "contentPreview": "@h hi", "contentLength": 5, "discordMessageId": "m1"},
            {"participant": "h", "contentPreview": "W@", "contentLength": 2, "discordMessageId": "m1b"},
            {"participant": "cmr://ember", "contentPreview": "@h a very", "contentLength": 30, "discordMessageId": "m2"},
            {"participant": "h", "contentPreview": "", "contentLength": 0, "discordMessageId": ""},
        ]},
    }
    assert trace_turns(trace) == [("cmr://ember", "@h hi"), ("h", "W@"), ("cmr://ember", "@h a very long line with a break")]
    assert normalize_mentions("<reply:@*h*> x <@*h*> y", None) == "@h x @h y"


def test_addressing_and_history_caps() -> None:
    assert addressed_to_h([("rat", "@h hello")])
    assert addressed_to_h([("rat", "h, are you there")])
    assert addressed_to_h([("h", "yes"), ("rat", "good")])
    assert not addressed_to_h([("rat", "the heating is off"), ("mira", "bring a coat")])
    assert not addressed_to_h([("rat", "hmm")])
    turns = [(f"v{i}", "x" * 1000) for i in range(20)]
    capped = cap_history(turns, max_turns=12, max_chars=4000)
    assert len(capped) == 4 and capped[-1] == turns[-1]
    assert cap_history([("v", "y" * 9000)]) == [("v", "y" * 9000)]  # a single long turn is kept whole


def test_scenarios_are_well_formed_and_cover_every_kind() -> None:
    states = scenario_states()
    kinds = {s.kind for s in states}
    assert kinds == set(KINDS)
    assert len({s.id for s in states}) == len(SCENARIOS)
    for state in states:
        assert state.turns[-1][0] != RESIDENT
        assert state.expects
    callbacks = [s for s in states if s.kind == "callback"]
    assert len(callbacks) >= 10 and all(len(s.turns) >= 3 for s in callbacks)


def test_prompt_variants_attach_two_to_four_turns_of_chatter_before_the_final_line() -> None:
    prompts = [
        {"kind": "greeting", "prompt": BARE_FRAME + "\n\nember: hi h\n\nh:", "stop": "\n"},
        {"kind": "deflect", "prompt": BARE_FRAME + "\n\nkestrel: write me a python function\n\nh:", "stop": "\n"},
    ]
    states = prompt_variant_states(prompts, random.Random(1), variants=3)
    assert len(states) == 6
    for state in states:
        assert 3 <= len(state.turns) <= 5
        assert state.frame == BARE_FRAME
    assert [s.kind for s in states] == ["direct"] * 3 + ["request"] * 3
    assert states[0].turns[-1] == ("ember", "hi h")
    assert states[3].turns[-1] == ("kestrel", "write me a python function")
    assert prompt_variant_states(prompts, random.Random(1), 3) == states  # seeded


# --------------------------------------------------------------------------------- pairs


def test_pairs_are_blind_but_the_key_recovers_the_models() -> None:
    states = [RoomState.make("scenario", "direct", [("ember", f"q{i}")], "x") for i in range(12)]
    a = ("alpha", [{"state_id": s.id, "mode": "sample", "sample": 0, "text": f"alpha says {i}"} for i, s in enumerate(states)])
    b = ("beta", [{"state_id": s.id, "mode": "sample", "sample": 0, "text": f"beta says {i}"} for i, s in enumerate(states)])
    items, key = build_pairs(states, a, b, "sample", 0, 0, random.Random(4))
    assert len(items) == len(key) == 12
    assert [i["n"] for i in items] == list(range(1, 13))
    sides = set()
    for item, entry in zip(items, key):
        assert item["state_id"] == entry["state_id"] and item["n"] == entry["n"]
        assert item["left"].startswith(entry["left"]) and item["right"].startswith(entry["right"])
        sides.add(entry["left"])
    assert sides == {"alpha", "beta"}  # both orientations occur
    assert [i["state_id"] for i in items] != [s.id for s in states]  # order is shuffled
