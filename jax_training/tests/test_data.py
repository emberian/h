from __future__ import annotations

import numpy as np

from h1jax.data import TokenStream, ValidationStream


def _write_tokens(path, *, sequence_count: int, sequence_length: int) -> None:
    token_count = sequence_count * sequence_length + 1
    np.arange(token_count, dtype="<u2").tofile(path)


def _sequence_ids(batch: np.ndarray, sequence_length: int) -> list[int]:
    return (batch.reshape(-1, sequence_length + 1)[:, 0] // sequence_length).tolist()


def test_token_stream_reshuffles_each_epoch_without_replacement(tmp_path) -> None:
    sequence_count = 11
    sequence_length = 2
    path = tmp_path / "train.bin"
    _write_tokens(path, sequence_count=sequence_count, sequence_length=sequence_length)
    stream = TokenStream(path, sequence_length=sequence_length, seed=17)

    batches = [
        stream.batch(
            epoch * sequence_count,
            device_count=1,
            accumulation_steps=1,
            per_device_batch=sequence_count,
        )
        for epoch in range(2)
    ]
    epoch_ids = [_sequence_ids(batch, sequence_length) for batch in batches]

    assert sorted(epoch_ids[0]) == list(range(sequence_count))
    assert sorted(epoch_ids[1]) == list(range(sequence_count))
    assert epoch_ids[0] != epoch_ids[1]


def test_token_stream_resume_is_derived_from_absolute_offset(tmp_path) -> None:
    sequence_length = 3
    path = tmp_path / "train.bin"
    _write_tokens(path, sequence_count=13, sequence_length=sequence_length)

    first = TokenStream(path, sequence_length=sequence_length, seed=29).batch(
        11, device_count=1, accumulation_steps=1, per_device_batch=5
    )
    resumed = TokenStream(path, sequence_length=sequence_length, seed=29).batch(
        11, device_count=1, accumulation_steps=1, per_device_batch=5
    )

    np.testing.assert_array_equal(first, resumed)


def test_validation_stream_keeps_sequential_order_on_wrap(tmp_path) -> None:
    sequence_count = 7
    sequence_length = 2
    path = tmp_path / "validation.bin"
    _write_tokens(path, sequence_count=sequence_count, sequence_length=sequence_length)
    stream = ValidationStream(path, sequence_length=sequence_length)

    first = stream.batch(
        0,
        device_count=1,
        accumulation_steps=1,
        per_device_batch=sequence_count,
    )
    second = stream.batch(
        sequence_count,
        device_count=1,
        accumulation_steps=1,
        per_device_batch=sequence_count,
    )

    assert _sequence_ids(first, sequence_length) == list(range(sequence_count))
    np.testing.assert_array_equal(first, second)
