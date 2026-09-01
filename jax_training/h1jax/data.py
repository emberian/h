from __future__ import annotations

import math
from pathlib import Path

import numpy as np


class TokenStream:
    """Deterministic, epoch-shuffled traversal of a uint16 little-endian stream."""

    def __init__(self, path: str | Path, sequence_length: int, seed: int = 0):
        self.path = Path(path).expanduser().resolve()
        self.sequence_length = sequence_length
        self.tokens = np.memmap(self.path, dtype="<u2", mode="r")
        self.sequence_count = (len(self.tokens) - 1) // sequence_length
        if self.sequence_count < 1:
            raise ValueError(f"Token stream is too short for sequence length {sequence_length}")
        self.seed = int(seed)
        self.shift, self.stride = self._affine_permutation(epoch=0)

    def _affine_permutation(self, epoch: int) -> tuple[int, int]:
        # Keep epoch zero byte-for-byte compatible with the original traversal.
        # Later epochs get their own deterministic affine permutation. Advancing
        # the shift guarantees consecutive passes differ when more than one
        # sequence is available, even if the sampled stride happens to repeat.
        if epoch == 0:
            rng = np.random.default_rng(self.seed)
        else:
            rng = np.random.default_rng(np.random.SeedSequence([self.seed, epoch]))
        base_shift = int(np.random.default_rng(self.seed).integers(0, self.sequence_count))
        shift = (base_shift + epoch) % self.sequence_count
        if epoch == 0:
            # Consume the same first draw before sampling the stride below.
            shift = int(rng.integers(0, self.sequence_count))
        stride = int(rng.integers(1, self.sequence_count + 1))
        while math.gcd(stride, self.sequence_count) != 1:
            stride = stride % self.sequence_count + 1
        return shift, stride

    def batch(
        self,
        example_offset: int,
        *,
        device_count: int,
        accumulation_steps: int,
        per_device_batch: int,
    ) -> np.ndarray:
        count = device_count * accumulation_steps * per_device_batch
        order = np.arange(example_offset, example_offset + count, dtype=np.int64)
        epochs = order // self.sequence_count
        epoch_positions = order % self.sequence_count
        sequence_ids = np.empty_like(order)
        for epoch in np.unique(epochs):
            mask = epochs == epoch
            shift, stride = self._affine_permutation(int(epoch))
            sequence_ids[mask] = (
                shift + epoch_positions[mask] * stride
            ) % self.sequence_count
        result = np.empty((count, self.sequence_length + 1), dtype=np.int32)
        for row, sequence_id in enumerate(sequence_ids):
            start = int(sequence_id) * self.sequence_length
            result[row] = self.tokens[start : start + self.sequence_length + 1]
        return result.reshape(
            device_count,
            accumulation_steps,
            per_device_batch,
            self.sequence_length + 1,
        )


class ValidationStream(TokenStream):
    def __init__(self, path: str | Path, sequence_length: int):
        super().__init__(path, sequence_length, seed=0)

    def _affine_permutation(self, epoch: int) -> tuple[int, int]:
        return 0, 1
