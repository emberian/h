#!/usr/bin/env python3
"""Room state server: a Falcon-H1 model whose recurrent state persists per room across turns.

Runs on hbox inside ``/home/hbox/h1-ghost`` (``source env.sh`` first) and binds 127.0.0.1;
the Mac reaches it through the ssh port forward that ``run_room_state_server.sh`` sets up.
This is the substrate for the question whether a hybrid Mamba-2/attention model can be a
genuinely stateful resident: the room's committed state is the model's cache after reading
the transcript so far, h's turns are sampled as forks of that state, and the chosen fork
becomes the new committed state without the text ever being re-read.

HTTP API (JSON in, JSON out; every mutating call is serialized behind one lock):

* ``POST /rooms`` ``{"room": id, "frame": str|null, "replace": bool}``: create a room whose
  state is the model after reading ``frame + "\\n\\n"`` (no frame: an empty state).
* ``POST /rooms/<id>/events`` ``{"text": "name: text"}``: read the event plus the ``"\\n\\n"``
  separator into the committed state (no generation).
* ``POST /rooms/<id>/candidates`` ``{"n", "temperature", "top_p", "max_new_tokens", "seed",
  "control"}``: fork the committed state ``n`` ways, feed ``"h:"`` and sample continuations
  up to the blank line, one batched decode loop for all forks. Returns text, per-token model
  logprobs and a branch id per candidate; the forks stay in memory until commit or silence.
  ``"control": true`` also samples the same seeds from a fresh cache that re-read the whole
  transcript and reports the first-token divergence between the two arms.
* ``POST /rooms/<id>/commit`` ``{"branch": id}``: the branch's state (plus its last sampled
  token, plus a separator when the sample did not end on one) becomes the committed state.
* ``POST /rooms/<id>/silence``: discard the forks; the committed state stays as it was.
* ``POST /rooms/<id>/snapshot`` ``{"persist": bool}`` / ``POST /rooms/<id>/rollback``
  ``{"snapshot": id}``: save (CPU, optionally ``--snapshot-dir`` on disk) / restore the
  committed state. A rollback into a room that is not in memory restores it from disk.
* ``POST /rooms/<id>/check``: the correctness check. Replays the room's segments through the
  server's read paths into fresh caches and compares every position's logits and the final
  states with one fresh forward over the whole transcript (and with the live state).
* ``GET /rooms/<id>/state``: token count, snapshots, branches, per-layer SSM/conv state
  norms, bytes, latency summaries. ``GET /rooms/<id>/transcript``, ``GET /rooms``,
  ``DELETE /rooms/<id>``, ``GET /health``.

Cache and forking. The cache is Transformers' ``FalconHybridMambaAttentionDynamicCache``: a
plain object holding, per layer, the conv window ``[b, 1792, 4]`` and the SSM state
``[b, 24, 64, 128]`` (dicts) and the attention K/V ``[b, 2, t, 64]`` (lists). Forking is a
tensor-level copy of that object: ``repeat_cache`` expands the batch-1 committed state to
``n`` rows so all forks decode in one batch; ``select_rows`` (``index_select`` on every
tensor) peels a finished row off into its own batch-1 cache and shrinks the live batch.
Per state at this 0.5B config: SSM 28.3 MB (float32; 14.2 MB in bfloat16), conv 1.0 MB,
plus 18.4 KB of bfloat16 K/V per token, so a 2,000-token room is about 66 MB and four forks
of it about 265 MB, next to the 1.1 GB model.

Reading text into a non-empty cache. In Transformers 4.57.1 the reference Mamba path uses
the cached SSM/conv state only for single-token steps; a multi-token forward on a
non-empty cache silently restarts the scan from zero. Two read modes therefore exist:
``step`` feeds events token by token through that untouched single-token path (exactly what
generation does), and ``chunk`` runs one forward through ``continuation_forward``, the
reference chunked scan with the previous conv window prepended and the previous SSM state
as the initial chunk state (the dead ``previous_states`` branch of the reference code,
wired up). Generation itself always uses the untouched reference single-token path; the
check endpoint validates both read modes against the fresh forward.

The SSM/conv states are kept in float32 by default (``--state-dtype``): the recurrence
``s = s * dA + dBx`` loses precision every step when the state is stored in bfloat16, and a
resident accumulates thousands of steps. Attention K/V stay in the model dtype (bfloat16).

The ``smoke`` subcommand is a stdlib-only client (runs on the Mac); ``selftest`` runs the
same steps in-process on hbox without HTTP. PyTorch and Transformers are imported lazily.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_CHECKPOINT = Path("/othersys/h1-ghost/checkpoints/tpu/extra/room05b-e2-v3-final")
DEFAULT_SNAPSHOT_DIR = Path("/othersys/h1-ghost/rooms")
BARE_FRAME = (
    "A room in the library, late. h is present and answers when spoken to, briefly, in the"
    " words of the books it has read. The others are visitors."
)
SEPARATOR = "\n\n"
H_PREFIX = "h:"
TOP_K = 10
LOG_PREFIX = "[room-state]"


def log(message: str) -> None:
    print(f"{LOG_PREFIX} {time.strftime('%H:%M:%S')} {message}", file=sys.stderr, flush=True)


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


# --------------------------------------------------------------------------- cache helpers


def cache_map(cache, fn):
    """A new cache object whose tensors are ``fn(tensor)``; scalar attributes are copied."""
    new = copy.copy(cache)
    new.conv_states = {i: fn(t) for i, t in cache.conv_states.items()}
    new.ssm_states = {i: fn(t) for i, t in cache.ssm_states.items()}
    new.key_cache = [fn(t) if hasattr(t, "index_select") else list(t) for t in cache.key_cache]
    new.value_cache = [fn(t) if hasattr(t, "index_select") else list(t) for t in cache.value_cache]
    new.transformer_layers = list(cache.transformer_layers)
    return new


def clone_cache(cache):
    return cache_map(cache, lambda t: t.clone())


def repeat_cache(cache, n: int):
    """Batch-1 cache -> batch-n cache, every row a copy (the fork)."""
    return cache_map(cache, lambda t: t.repeat((n,) + (1,) * (t.dim() - 1)))


def select_rows(cache, rows: list[int]):
    import torch

    def pick(t):
        return t.index_select(0, torch.as_tensor(rows, device=t.device))

    return cache_map(cache, pick)


def cache_to(cache, device):
    return cache_map(cache, lambda t: t.to(device))


def cache_tensors(cache):
    yield from cache.conv_states.values()
    yield from cache.ssm_states.values()
    for t in cache.key_cache:
        if hasattr(t, "numel"):
            yield t
    for t in cache.value_cache:
        if hasattr(t, "numel"):
            yield t


def cache_bytes(cache) -> int:
    return sum(t.numel() * t.element_size() for t in cache_tensors(cache))


def cache_diagnostics(cache) -> dict:
    """Per-layer SSM per-head Frobenius norms (mean, max over heads) and conv window norms."""
    import torch

    layers = sorted(cache.ssm_states)
    means, maxes, totals, convs = [], [], [], []
    for i in layers:
        s = cache.ssm_states[i][0].float()
        head_norms = s.flatten(1).norm(dim=1)
        means.append(head_norms.mean())
        maxes.append(head_norms.max())
        totals.append(s.norm())
        convs.append(cache.conv_states[i][0].float().norm())
    stacked = torch.stack([torch.stack(x) for x in (means, maxes, totals, convs)]).cpu().tolist()
    means, maxes, totals, convs = stacked
    return {
        "layers": len(layers),
        "ssm_head_norm_mean": [round(v, 4) for v in means],
        "ssm_head_norm_max": [round(v, 4) for v in maxes],
        "ssm_norm": [round(v, 4) for v in totals],
        "conv_norm": [round(v, 4) for v in convs],
        "summary": {
            "ssm_head_norm_mean_over_layers": round(sum(means) / len(means), 4),
            "ssm_head_norm_max_over_layers": round(max(maxes), 4),
            "ssm_norm_mean_over_layers": round(sum(totals) / len(totals), 4),
            "conv_norm_mean_over_layers": round(sum(convs) / len(convs), 4),
        },
    }


def state_distance(a, b) -> dict:
    """Relative errors between two caches' states, per kind (max and mean over layers)."""
    import torch

    def rel(x, y):
        x, y = x.float(), y.float()
        return (x - y).norm() / y.norm().clamp_min(1e-12)

    out = {}
    for kind, xs, ys in (("ssm", a.ssm_states, b.ssm_states), ("conv", a.conv_states, b.conv_states)):
        errs = torch.stack([rel(xs[i], ys[i]) for i in sorted(xs)]).cpu().tolist()
        out[kind] = {"relative_error_max": max(errs), "relative_error_mean": sum(errs) / len(errs)}
    if a.key_cache and b.key_cache and a.key_cache[0].shape == b.key_cache[0].shape:
        kerrs = torch.stack([rel(x, y) for x, y in zip(a.key_cache, b.key_cache)]).cpu().tolist()
        verrs = torch.stack([rel(x, y) for x, y in zip(a.value_cache, b.value_cache)]).cpu().tolist()
        out["key"] = {"relative_error_max": max(kerrs), "relative_error_mean": sum(kerrs) / len(kerrs)}
        out["value"] = {"relative_error_max": max(verrs), "relative_error_mean": sum(verrs) / len(verrs)}
    return out


def logits_distance(a, b) -> dict:
    """``a``, ``b``: ``[T, V]`` float32 logits for the same positions."""
    import torch

    diff = (a - b).abs()
    la, lb = torch.log_softmax(a, -1), torch.log_softmax(b, -1)
    kl = (la.exp() * (la - lb)).sum(-1)
    agree = a.argmax(-1) == b.argmax(-1)
    entropy = -(lb.exp() * lb).sum(-1)
    disagreements = (~agree).nonzero().flatten().tolist()
    return {
        "positions": int(a.shape[0]),
        "max_abs_logit_diff": float(diff.max()),
        "mean_abs_logit_diff": float(diff.mean()),
        "mean_kl": float(kl.mean()),
        "max_kl": float(kl.max()),
        "max_kl_position": int(kl.argmax()),
        "argmax_agreement": float(agree.float().mean()),
        "argmax_disagreements": disagreements[:20],
        "last": {
            "max_abs_logit_diff": float(diff[-1].max()),
            "kl": float(kl[-1]),
            "argmax_equal": bool(agree[-1]),
            "entropy_nats": float(entropy[-1]),
        },
    }


# --------------------------------------------------------------------------- continuation


def make_continuation_forward(falcon_h1, reference_forward):
    """The reference chunked scan with the cache's conv window and SSM state as the start.

    Only the case ``has_previous_state and seq_len > 1`` differs from the reference
    ``torch_forward``; every other call is delegated to it untouched.
    """
    import torch
    from torch import nn

    def continuation_forward(self, input_states, cache_params=None, cache_position=None, attention_mask=None):
        batch_size, seq_len, _ = input_states.shape
        continuing = (
            cache_params is not None
            and cache_params.has_previous_state
            and seq_len > 1
            and cache_position is not None
            and int(cache_position[0]) > 0
            and cache_params.conv_states[self.layer_idx].shape[0] == batch_size
        )
        if not continuing:
            return reference_forward(self, input_states, cache_params, cache_position, attention_mask)
        layer = self.layer_idx
        dtype = input_states.dtype
        input_states = falcon_h1.apply_mask_to_padding_states(input_states, attention_mask)
        input_states = input_states * self.ssm_in_multiplier
        projected_states = self.in_proj(input_states) * self.mup_vector
        gate, hidden_states_B_C, dt = projected_states.split(
            [self.intermediate_size, self.conv_dim, self.num_heads], dim=-1
        )
        # Convolution over the previous window followed by the new tokens; the window
        # advances exactly as the single-token path rolls it.
        x = hidden_states_B_C.transpose(1, 2)
        previous = cache_params.conv_states[layer][:, :, 1:].to(device=x.device, dtype=x.dtype)
        window = torch.cat([previous, x], dim=-1)
        cache_params.conv_states[layer].copy_(window[:, :, -self.conv_kernel_size :])
        k = self.conv_kernel_size - 1
        hidden_states_B_C = self.act(self.conv1d(window)[..., k : k + seq_len].transpose(1, 2))
        hidden_states_B_C = falcon_h1.apply_mask_to_padding_states(hidden_states_B_C, attention_mask)
        hidden_states, B, C = torch.split(
            hidden_states_B_C,
            [self.intermediate_size, self.n_groups * self.ssm_state_size, self.n_groups * self.ssm_state_size],
            dim=-1,
        )
        A = -torch.exp(self.A_log.float())
        dt = nn.functional.softplus(dt + self.dt_bias)
        dt = torch.clamp(dt, self.time_step_limit[0], self.time_step_limit[1])
        hidden_states = hidden_states.reshape(batch_size, seq_len, -1, self.head_dim).float()
        B = B.reshape(batch_size, seq_len, -1, self.ssm_state_size).float()
        C = C.reshape(batch_size, seq_len, -1, self.ssm_state_size).float()
        B = B.repeat_interleave(self.num_heads // self.n_groups, dim=2, output_size=self.num_heads)
        C = C.repeat_interleave(self.num_heads // self.n_groups, dim=2, output_size=self.num_heads)
        pad_size = (self.chunk_size - seq_len % self.chunk_size) % self.chunk_size
        D_residual = self.D[..., None] * falcon_h1.pad_tensor_by_size(hidden_states, pad_size)
        hidden_states = hidden_states * dt[..., None]
        A = A.to(hidden_states.dtype) * dt
        hidden_states, A, B, C = [
            falcon_h1.reshape_into_chunks(t, pad_size, self.chunk_size) for t in (hidden_states, A, B, C)
        ]
        A = A.permute(0, 3, 1, 2)
        A_cumsum = torch.cumsum(A, dim=-1)
        L = torch.exp(falcon_h1.segment_sum(A))
        G = (C[:, :, :, None, :, :] * B[:, :, None, :, :, :]).sum(dim=-1)
        M = (G[..., None] * L.permute(0, 2, 3, 4, 1)[..., None]).sum(dim=-1)
        Y_diag = (M[..., None] * hidden_states[:, :, None]).sum(dim=3)
        decay_states = torch.exp(A_cumsum[:, :, :, -1:] - A_cumsum)
        B_decay = B * decay_states.permute(0, -2, -1, 1)[..., None]
        states = (B_decay[..., None, :] * hidden_states[..., None]).sum(dim=2)
        # The cached SSM state enters as the state before the first chunk.
        previous_states = cache_params.ssm_states[layer][:, None, ...].to(device=states.device, dtype=states.dtype)
        states = torch.cat([previous_states, states], dim=1)
        decay_chunk = torch.exp(falcon_h1.segment_sum(nn.functional.pad(A_cumsum[:, :, :, -1], (1, 0))))
        decay_chunk = decay_chunk.transpose(1, 3)
        new_states = (decay_chunk[..., None, None] * states[:, :, None, ...]).sum(dim=1)
        states, ssm_state = new_states[:, :-1], new_states[:, -1]
        state_decay_out = torch.exp(A_cumsum)
        C_times_states = C[..., None, :] * states[:, :, None, ...]
        Y_off = C_times_states.sum(-1) * state_decay_out.permute(0, 2, 3, 1)[..., None]
        y = (Y_diag + Y_off).reshape(batch_size, -1, self.num_heads, self.head_dim) + D_residual
        if pad_size > 0:
            y = y[:, :seq_len, :, :]
        y = y.reshape(batch_size, seq_len, -1)
        cache_params.ssm_states[layer].copy_(ssm_state)
        if self.mamba_rms_norm:
            scan_output = self.norm(y, gate)
        else:
            scan_output = y * nn.functional.silu(gate)
        return self.out_proj(scan_output.to(dtype))

    return continuation_forward


# --------------------------------------------------------------------------- engine


@dataclass
class Candidate:
    index: int
    tokens: list[int] = field(default_factory=list)
    logprobs: list[float] = field(default_factory=list)
    finish_reason: str | None = None
    state: object = None
    position: int = 0
    stop_logprobs: dict = field(default_factory=dict)

    @property
    def finished(self) -> bool:
        return self.finish_reason is not None


class Engine:
    """The model, the tokenizer and every cache operation; callers hold ``self.lock``."""

    def __init__(self, checkpoint: Path, device: str, state_dtype: str, read_mode: str) -> None:
        import torch
        import transformers.models.falcon_h1.modeling_falcon_h1 as falcon_h1
        from transformers import AutoTokenizer, FalconH1ForCausalLM

        started = time.perf_counter()
        self.torch = torch
        self.falcon_h1 = falcon_h1
        self.checkpoint = checkpoint
        self.device = device
        self.read_mode = read_mode
        self.state_dtype = {"float32": torch.float32, "bfloat16": torch.bfloat16}[state_dtype]
        self.model = FalconH1ForCausalLM.from_pretrained(checkpoint, dtype=torch.bfloat16, local_files_only=True)
        self.model.to(device)
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True)
        self.config = self.model.config
        self.devices = [layer.mamba.conv1d.weight.device for layer in self.model.model.layers]
        self.reference_forward = falcon_h1.FalconH1Mixer.torch_forward
        self.continuation_forward = make_continuation_forward(falcon_h1, self.reference_forward)
        self.separator_ids = self.encode(SEPARATOR)
        self.prefix_ids = self.encode(H_PREFIX)
        self.eos = self.tokenizer.eos_token_id
        self.lock = threading.RLock()
        self.warmup()
        self.load_seconds = time.perf_counter() - started
        log(
            f"loaded {checkpoint.name} on {device} in {self.load_seconds:.1f}s; states {state_dtype},"
            f" read mode {read_mode}, separator {self.separator_ids}, prefix {self.prefix_ids}"
        )

    # -- text
    def encode(self, text: str) -> list[int]:
        return [int(t) for t in self.tokenizer.encode(text, add_special_tokens=False)]

    def decode(self, ids: list[int]) -> str:
        return self.tokenizer.decode(ids, skip_special_tokens=False)

    # -- caches
    def new_cache(self, batch: int = 1):
        with self.torch.inference_mode():
            return self.falcon_h1.FalconHybridMambaAttentionDynamicCache(
                self.config, batch, self.state_dtype, devices=self.devices
            )

    def sync(self) -> None:
        if self.torch.cuda.is_available():
            self.torch.cuda.synchronize()

    @contextlib.contextmanager
    def continuation(self):
        self.falcon_h1.FalconH1Mixer.torch_forward = self.continuation_forward
        try:
            yield
        finally:
            self.falcon_h1.FalconH1Mixer.torch_forward = self.reference_forward

    def forward(self, cache, ids: list[list[int]], all_logits: bool = False):
        """One forward of ``ids`` ``[b, L]`` on top of ``cache``; float32 logits ``[b, L|1, V]``."""
        torch = self.torch
        past = cache.get_seq_length()
        input_ids = torch.as_tensor(ids, dtype=torch.long, device=self.device)
        batch, length = input_ids.shape
        cache_position = torch.arange(past, past + length, device=self.device)
        attention_mask = torch.ones(batch, past + length, dtype=torch.long, device=self.device)
        with torch.inference_mode():
            out = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                past_key_values=cache,
                use_cache=True,
                cache_position=cache_position,
                logits_to_keep=0 if all_logits else 1,
            )
            return out.logits.float()

    def read(self, cache, ids: list[int], mode: str | None = None, all_logits: bool = False):
        """Read ``ids`` into ``cache``; returns float32 logits ``[L|1, V]`` (next-token logits)."""
        if not ids:
            raise ApiError(400, "nothing to read")
        mode = mode or self.read_mode
        if not cache.has_previous_state:
            return self.forward(cache, [ids], all_logits)[0]
        if mode == "step":
            steps = [self.forward(cache, [[t]], True)[0] for t in ids]
            return self.torch.cat(steps, 0) if all_logits else steps[-1]
        with self.continuation():
            return self.forward(cache, [ids], all_logits)[0]

    def step(self, cache, tokens: list[int]):
        """One single-token step for every row; returns ``[b, V]`` float32 logits."""
        return self.forward(cache, [[t] for t in tokens], all_logits=True)[:, -1]

    # -- sampling
    def sample(self, logits, temperature: float, top_p: float, uniforms):
        torch = self.torch
        if temperature <= 0:
            return logits.argmax(-1)
        probs = torch.softmax(logits / temperature, dim=-1)
        sorted_probs, sorted_idx = probs.sort(dim=-1, descending=True)
        cumulative = sorted_probs.cumsum(-1)
        remove = (cumulative - sorted_probs) > top_p
        sorted_probs = sorted_probs.masked_fill(remove, 0.0)
        sorted_probs = sorted_probs / sorted_probs.sum(-1, keepdim=True)
        cumulative = sorted_probs.cumsum(-1)
        pick = (cumulative < uniforms[:, None]).sum(-1)
        pick = torch.minimum(pick, (~remove).sum(-1) - 1)
        return sorted_idx.gather(1, pick[:, None]).squeeze(1)

    def top_tokens(self, logits, k: int = TOP_K) -> list[dict]:
        logprobs = self.torch.log_softmax(logits, -1)
        values, ids = logprobs.topk(k)
        return [
            {"id": int(i), "text": self.decode([int(i)]), "logprob": round(float(v), 4)}
            for v, i in zip(values.tolist(), ids.tolist())
        ]

    def generate(
        self, base_cache, n: int, temperature: float, top_p: float, max_new_tokens: int, seed: int
    ) -> dict:
        """Fork ``base_cache`` ``n`` ways, feed ``h:``, sample to the blank line, batched.

        A candidate's ``state`` is its cache before its last sampled token was fed (the
        token is left pending for commit), so a finished row can leave the batch at once.
        The uniform draws are made for all ``n`` rows every step, so the same seed gives
        the same draws to candidate ``i`` whatever the other rows do (the control arm
        relies on this).
        """
        torch = self.torch
        self.sync()
        started = time.perf_counter()
        cache = repeat_cache(base_cache, n)
        steps = 0
        for token in self.prefix_ids:
            logits = self.step(cache, [token] * n)
            steps += 1
        first_logits = logits[0].clone()
        generator = torch.Generator(device=self.device)
        generator.manual_seed(seed)
        candidates = [Candidate(index=i) for i in range(n)]
        active = list(range(n))
        while True:
            uniforms = torch.rand(n, generator=generator, device=self.device)
            logprobs = torch.log_softmax(logits, -1)
            tokens = self.sample(logits, temperature, top_p, uniforms[active])
            token_logprobs = logprobs.gather(1, tokens[:, None]).squeeze(1).tolist()
            tokens = tokens.tolist()
            finished_rows = []
            for row, index in enumerate(active):
                candidate = candidates[index]
                token = tokens[row]
                if token == self.eos:
                    candidate.finish_reason = "eos"
                else:
                    candidate.tokens.append(token)
                    candidate.logprobs.append(token_logprobs[row])
                    if SEPARATOR in self.decode(candidate.tokens):
                        candidate.finish_reason = "stop"
                    elif len(candidate.tokens) >= max_new_tokens:
                        candidate.finish_reason = "length"
                if candidate.finished:
                    finished_rows.append(row)
                    candidate.stop_logprobs = {
                        "separator": round(float(logprobs[row, self.separator_ids[0]]), 4),
                        "eos": round(float(logprobs[row, self.eos]), 4),
                        "sampled": round(token_logprobs[row], 4),
                    }
            position = cache.get_seq_length()
            for row in finished_rows:
                candidates[active[row]].state = select_rows(cache, [row])
                candidates[active[row]].position = position
            remaining = [row for row in range(len(active)) if row not in finished_rows]
            if not remaining:
                break
            if finished_rows:
                cache = select_rows(cache, remaining)
            active = [active[row] for row in remaining]
            logits = self.step(cache, [candidates[i].tokens[-1] for i in active])
            steps += 1
        self.sync()
        seconds = time.perf_counter() - started
        return {
            "candidates": candidates,
            "first_logits": first_logits,
            "first_token_top": self.top_tokens(first_logits),
            "seconds": round(seconds, 4),
            "steps": steps,
            "seconds_per_step": round(seconds / steps, 4),
            "seed": seed,
        }

    def describe(self, candidate: Candidate, branch_id: str) -> dict:
        raw = self.decode(candidate.tokens)
        cut = raw.find(SEPARATOR)
        text = raw if cut < 0 else raw[:cut]
        overrun = "" if cut < 0 else raw[cut + len(SEPARATOR) :]
        return {
            "branch": branch_id,
            "text": text.strip(),
            "raw_text": raw,
            "tokens": list(candidate.tokens),
            "token_text": [self.decode([t]) for t in candidate.tokens],
            "logprobs": [round(v, 4) for v in candidate.logprobs],
            "logprob_sum": round(sum(candidate.logprobs), 4),
            "new_tokens": len(candidate.tokens),
            "finish_reason": candidate.finish_reason,
            "stopped": candidate.finish_reason == "stop",
            "clean_stop": candidate.finish_reason == "stop" and overrun == "",
            "overrun": overrun,
            "stop_logprobs": candidate.stop_logprobs,
        }

    def reply_logits(self, cache):
        """Logits for the first reply token: a clone of ``cache`` after reading ``h:``; ``[b, V]``."""
        clone = clone_cache(cache)
        batch = clone.conv_states[0].shape[0]
        for token in self.prefix_ids:
            logits = self.step(clone, [token] * batch)
        return logits

    def warmup(self) -> None:
        cache = self.new_cache()
        self.read(cache, self.separator_ids + self.prefix_ids)
        self.step(cache, self.prefix_ids[:1])
        self.sync()

    def memory(self) -> dict:
        torch = self.torch
        if not torch.cuda.is_available():
            return {"device": "cpu"}
        free, total = torch.cuda.mem_get_info()
        return {
            "device": torch.cuda.get_device_name(0),
            "allocated_bytes": int(torch.cuda.memory_allocated()),
            "reserved_bytes": int(torch.cuda.memory_reserved()),
            "max_allocated_bytes": int(torch.cuda.max_memory_allocated()),
            "free_bytes": int(free),
            "total_bytes": int(total),
        }


# --------------------------------------------------------------------------- rooms


@dataclass
class Branch:
    id: str
    candidate: Candidate
    description: dict


@dataclass
class Snapshot:
    id: str
    state_id: int
    token_count: int
    segments: list[dict]
    cache: object
    path: str | None = None


@dataclass
class Room:
    id: str
    frame: str | None
    cache: object
    segments: list[dict] = field(default_factory=list)
    token_count: int = 0
    state_id: int = 0
    branches: dict = field(default_factory=dict)
    snapshots: dict = field(default_factory=dict)
    branch_counter: int = 0
    snapshot_counter: int = 0
    timings: dict = field(default_factory=lambda: {"events": [], "candidates": [], "commits": []})
    created: float = field(default_factory=time.time)

    @property
    def token_ids(self) -> list[int]:
        return [t for segment in self.segments for t in segment["tokens"]]

    @property
    def transcript(self) -> str:
        return "".join(segment["text"] for segment in self.segments)


def timing_summary(records: list[dict]) -> dict:
    if not records:
        return {"count": 0}
    keys = [k for k in records[0] if isinstance(records[0][k], (int, float))]
    return {"count": len(records), **{f"mean_{k}": round(sum(r[k] for r in records) / len(records), 4) for k in keys}}


class Service:
    """Rooms and the request router shared by the HTTP handler and the in-process client."""

    def __init__(self, engine: Engine, snapshot_dir: Path | None, max_check_tokens: int) -> None:
        self.engine = engine
        self.snapshot_dir = snapshot_dir
        self.max_check_tokens = max_check_tokens
        self.rooms: dict[str, Room] = {}
        self.lock = engine.lock
        self.started = time.time()

    # -- routing
    ROUTES = [
        ("GET", r"^/health$", "health"),
        ("GET", r"^/rooms$", "list_rooms"),
        ("POST", r"^/rooms$", "create_room"),
        ("GET", r"^/rooms/([^/]+)/state$", "state"),
        ("GET", r"^/rooms/([^/]+)/transcript$", "transcript"),
        ("DELETE", r"^/rooms/([^/]+)$", "delete_room"),
        ("POST", r"^/rooms/([^/]+)/events$", "event"),
        ("POST", r"^/rooms/([^/]+)/candidates$", "candidates"),
        ("POST", r"^/rooms/([^/]+)/commit$", "commit"),
        ("POST", r"^/rooms/([^/]+)/silence$", "silence"),
        ("POST", r"^/rooms/([^/]+)/snapshot$", "snapshot"),
        ("POST", r"^/rooms/([^/]+)/rollback$", "rollback"),
        ("POST", r"^/rooms/([^/]+)/check$", "check"),
    ]

    def dispatch(self, method: str, path: str, body: dict | None) -> tuple[int, dict]:
        body = body or {}
        for verb, pattern, name in self.ROUTES:
            match = re.match(pattern, path)
            if match and verb == method:
                handler = getattr(self, name)
                started = time.perf_counter()
                try:
                    if name == "health":
                        result = handler()
                    else:
                        with self.lock:
                            result = handler(*match.groups(), **body) if match.groups() else handler(**body)
                except ApiError as error:
                    return error.status, {"error": str(error)}
                except TypeError as error:
                    return 400, {"error": f"bad request: {error}"}
                result.setdefault("seconds", round(time.perf_counter() - started, 4))
                return 200, result
        return 404, {"error": f"no route for {method} {path}"}

    # -- helpers
    def room(self, room_id: str) -> Room:
        if room_id not in self.rooms:
            raise ApiError(404, f"no room {room_id!r}")
        return self.rooms[room_id]

    def _read_segment(self, room: Room, kind: str, text: str, ids: list[int]) -> float:
        engine = self.engine
        engine.sync()
        started = time.perf_counter()
        engine.read(room.cache, ids)
        engine.sync()
        seconds = time.perf_counter() - started
        room.segments.append({"kind": kind, "text": text, "tokens": ids})
        room.token_count += len(ids)
        room.state_id += 1
        if room.cache.get_seq_length() != room.token_count:
            raise ApiError(500, f"cache length {room.cache.get_seq_length()} != token count {room.token_count}")
        return seconds

    def _discard_branches(self, room: Room) -> int:
        count = len(room.branches)
        room.branches.clear()
        return count

    # -- handlers
    def health(self) -> dict:
        engine = self.engine
        params = sum(p.numel() for p in engine.model.parameters())
        return {
            "ok": True,
            "host": socket.gethostname(),
            "checkpoint": str(engine.checkpoint),
            "device": engine.device,
            "state_dtype": str(engine.state_dtype).replace("torch.", ""),
            "read_mode": engine.read_mode,
            "parameters": params,
            "rooms": len(self.rooms),
            "uptime_seconds": round(time.time() - self.started, 1),
            "load_seconds": round(engine.load_seconds, 2),
            "gpu": engine.memory(),
            "state_bytes_empty": cache_bytes(engine.new_cache()),
            "kv_bytes_per_token": 2 * engine.config.num_hidden_layers * engine.config.num_key_value_heads
            * engine.config.head_dim * 2,
        }

    def list_rooms(self) -> dict:
        return {
            "rooms": [
                {"room": r.id, "state_id": r.state_id, "token_count": r.token_count,
                 "branches": len(r.branches), "snapshots": len(r.snapshots)}
                for r in self.rooms.values()
            ]
        }

    def create_room(self, room: str, frame: str | None = BARE_FRAME, replace: bool = False) -> dict:
        if not room or "/" in room:
            raise ApiError(400, "room id must be a non-empty string without '/'")
        if room in self.rooms and not replace:
            raise ApiError(409, f"room {room!r} exists (pass replace=true)")
        engine = self.engine
        new = Room(id=room, frame=frame, cache=engine.new_cache())
        seconds = 0.0
        tokens = 0
        if frame:
            text = frame.rstrip() + SEPARATOR
            ids = engine.encode(text)
            seconds = self._read_segment(new, "frame", text, ids)
            tokens = len(ids)
        self.rooms[room] = new
        log(f"room {room}: created, frame {tokens} tokens in {seconds:.3f}s")
        return {"room": room, "state_id": new.state_id, "token_count": new.token_count,
                "frame_tokens": tokens, "read_seconds": round(seconds, 4)}

    def delete_room(self, room_id: str) -> dict:
        self.room(room_id)
        del self.rooms[room_id]
        return {"deleted": room_id}

    def event(self, room_id: str, text: str, separator: bool = True) -> dict:
        room = self.room(room_id)
        if not isinstance(text, str) or not text.strip():
            raise ApiError(400, "text must be a non-empty string")
        rendered = text.rstrip() + SEPARATOR if separator else text
        ids = self.engine.encode(rendered)
        seconds = self._read_segment(room, "event", rendered, ids)
        discarded = self._discard_branches(room)
        record = {"tokens": len(ids), "seconds": round(seconds, 4),
                  "tokens_per_second": round(len(ids) / seconds, 2) if seconds else None}
        room.timings["events"].append(record)
        log(f"room {room_id}: event {len(ids)} tokens in {seconds:.3f}s ({self.engine.read_mode})")
        return {"room": room_id, "state_id": room.state_id, "token_count": room.token_count,
                "read_mode": self.engine.read_mode, "discarded_branches": discarded, **record}

    def _sample(self, cache, n, temperature, top_p, max_new_tokens, seed) -> dict:
        return self.engine.generate(cache, n, temperature, top_p, max_new_tokens, seed)

    def candidates(self, room_id: str, n: int = 4, temperature: float = 0.7, top_p: float = 0.9,
                   max_new_tokens: int = 64, seed: int | None = None, control: bool = False) -> dict:
        room = self.room(room_id)
        engine = self.engine
        if room.cache.get_seq_length() == 0:
            raise ApiError(409, "the room has read nothing yet")
        n = int(n)
        if not 1 <= n <= 32:
            raise ApiError(400, "n must be in 1..32")
        if seed is None:
            seed = int.from_bytes(os.urandom(4), "little")
        self._discard_branches(room)
        result = self._sample(room.cache, n, float(temperature), float(top_p), int(max_new_tokens), int(seed))
        listed = []
        for candidate in result["candidates"]:
            room.branch_counter += 1
            branch_id = f"b{room.branch_counter}"
            description = engine.describe(candidate, branch_id)
            room.branches[branch_id] = Branch(branch_id, candidate, description)
            listed.append(description)
        response = {
            "room": room_id, "state_id": room.state_id, "token_count": room.token_count, "seed": seed,
            "candidates": listed, "first_token_top": result["first_token_top"],
            "generation_seconds": result["seconds"], "steps": result["steps"],
            "seconds_per_step": result["seconds_per_step"],
            "seconds_per_candidate": round(result["seconds"] / n, 4),
            "settings": {"n": n, "temperature": temperature, "top_p": top_p, "max_new_tokens": max_new_tokens},
        }
        room.timings["candidates"].append({
            "n": n, "seconds": result["seconds"], "steps": result["steps"],
            "seconds_per_step": result["seconds_per_step"], "seconds_per_candidate": round(result["seconds"] / n, 4),
        })
        if control:
            engine.sync()
            started = time.perf_counter()
            fresh = engine.new_cache()
            engine.read(fresh, room.token_ids)
            engine.sync()
            rerender_seconds = time.perf_counter() - started
            other = self._sample(fresh, n, float(temperature), float(top_p), int(max_new_tokens), int(seed))
            response["control"] = {
                "arm": "rerender", "rerender_tokens": room.token_count,
                "rerender_seconds": round(rerender_seconds, 4),
                "candidates": [engine.describe(c, f"control-{c.index}") for c in other["candidates"]],
                "first_token_top": other["first_token_top"],
                "generation_seconds": other["seconds"], "steps": other["steps"],
                "seconds_per_step": other["seconds_per_step"],
            }
            a, b = result["first_logits"][None], other["first_logits"][None]
            distance = logits_distance(a, b)
            response["first_token_divergence"] = {
                "max_abs_logit_diff": distance["max_abs_logit_diff"], "kl_persistent_vs_control": distance["mean_kl"],
                "argmax_equal": distance["last"]["argmax_equal"],
            }
            response["identical_to_control"] = [
                x["tokens"] == y["tokens"] for x, y in zip(listed, response["control"]["candidates"])
            ]
        log(
            f"room {room_id}: {n} candidates in {result['seconds']:.2f}s ({result['steps']} steps,"
            f" {result['seconds_per_step'] * 1000:.0f} ms/step): "
            + " | ".join(repr(c["text"][:40]) for c in listed)
        )
        return response

    def commit(self, room_id: str, branch: str) -> dict:
        room = self.room(room_id)
        engine = self.engine
        if branch not in room.branches:
            raise ApiError(404, f"no branch {branch!r} in room {room_id!r} (have {sorted(room.branches)})")
        chosen = room.branches[branch]
        candidate, description = chosen.candidate, chosen.description
        engine.sync()
        started = time.perf_counter()
        cache = candidate.state
        pending = [] if candidate.finish_reason == "eos" else candidate.tokens[-1:]
        if pending:
            engine.read(cache, pending, mode="step")
        needs_separator = candidate.finish_reason in ("eos", "length")
        if needs_separator:
            engine.read(cache, engine.separator_ids, mode="step")
        engine.sync()
        seconds = time.perf_counter() - started
        tokens = engine.prefix_ids + list(candidate.tokens) + (engine.separator_ids if needs_separator else [])
        text = engine.decode(tokens)
        room.cache = cache
        room.segments.append({"kind": "h", "text": text, "tokens": tokens, "branch": branch,
                              "finish_reason": candidate.finish_reason})
        room.token_count += len(tokens)
        room.state_id += 1
        if room.cache.get_seq_length() != room.token_count:
            raise ApiError(500, f"cache length {room.cache.get_seq_length()} != token count {room.token_count}")
        discarded = self._discard_branches(room) - 1
        room.timings["commits"].append({"seconds": round(seconds, 4), "tokens": len(tokens)})
        log(f"room {room_id}: committed {branch} {description['text'][:60]!r} (+{len(tokens)} tokens)")
        return {"room": room_id, "state_id": room.state_id, "token_count": room.token_count, "branch": branch,
                "text": description["text"], "segment_text": text, "tokens": len(tokens),
                "added_separator": needs_separator, "discarded_branches": discarded,
                "finish_seconds": round(seconds, 4)}

    def silence(self, room_id: str) -> dict:
        room = self.room(room_id)
        discarded = self._discard_branches(room)
        return {"room": room_id, "state_id": room.state_id, "token_count": room.token_count,
                "discarded_branches": discarded}

    def snapshot(self, room_id: str, persist: bool = False) -> dict:
        room = self.room(room_id)
        engine = self.engine
        room.snapshot_counter += 1
        snapshot_id = f"s{room.snapshot_counter}"
        with engine.torch.inference_mode():
            cache = cache_to(room.cache, "cpu")
        snap = Snapshot(snapshot_id, room.state_id, room.token_count, copy.deepcopy(room.segments), cache)
        if persist:
            if self.snapshot_dir is None:
                raise ApiError(400, "the server has no --snapshot-dir")
            path = self.snapshot_dir / room_id / f"{snapshot_id}.pt"
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "room": room_id, "frame": room.frame, "snapshot": snapshot_id, "state_id": room.state_id,
                "token_count": room.token_count, "segments": snap.segments,
                "checkpoint": str(engine.checkpoint), "state_dtype": str(engine.state_dtype),
                "conv_states": {int(i): t for i, t in cache.conv_states.items()},
                "ssm_states": {int(i): t for i, t in cache.ssm_states.items()},
                "key_cache": list(cache.key_cache), "value_cache": list(cache.value_cache),
            }
            engine.torch.save(payload, path)
            snap.path = str(path)
        room.snapshots[snapshot_id] = snap
        return {"room": room_id, "snapshot": snapshot_id, "state_id": room.state_id,
                "token_count": room.token_count, "bytes": cache_bytes(cache), "path": snap.path}

    def _load_snapshot(self, room_id: str, snapshot_id: str) -> Snapshot:
        engine = self.engine
        path = (self.snapshot_dir or DEFAULT_SNAPSHOT_DIR) / room_id / f"{snapshot_id}.pt"
        if not path.is_file():
            raise ApiError(404, f"no snapshot {snapshot_id!r} for room {room_id!r} (memory or {path})")
        payload = engine.torch.load(path, map_location="cpu", weights_only=True)
        cache = engine.new_cache()
        with engine.torch.inference_mode():
            cache = cache_to(cache, "cpu")
            for i, t in payload["conv_states"].items():
                cache.conv_states[int(i)] = t
            for i, t in payload["ssm_states"].items():
                cache.ssm_states[int(i)] = t
            cache.key_cache = list(payload["key_cache"])
            cache.value_cache = list(payload["value_cache"])
        cache.has_previous_state = payload["token_count"] > 0
        return Snapshot(snapshot_id, payload["state_id"], payload["token_count"], payload["segments"], cache, str(path))

    def rollback(self, room_id: str, snapshot: str) -> dict:
        engine = self.engine
        if room_id in self.rooms and snapshot in self.rooms[room_id].snapshots:
            snap = self.rooms[room_id].snapshots[snapshot]
        else:
            snap = self._load_snapshot(room_id, snapshot)
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(id=room_id, frame=None, cache=engine.new_cache())
        room = self.rooms[room_id]
        with engine.torch.inference_mode():
            room.cache = cache_to(snap.cache, engine.device)
        room.segments = copy.deepcopy(snap.segments)
        room.token_count = snap.token_count
        room.state_id += 1
        room.snapshots.setdefault(snapshot, snap)
        discarded = self._discard_branches(room)
        log(f"room {room_id}: rolled back to {snapshot} ({snap.token_count} tokens)")
        return {"room": room_id, "snapshot": snapshot, "state_id": room.state_id,
                "token_count": room.token_count, "restored_state_id": snap.state_id,
                "discarded_branches": discarded}

    def state(self, room_id: str) -> dict:
        room = self.room(room_id)
        return {
            "room": room_id, "frame": room.frame, "state_id": room.state_id, "token_count": room.token_count,
            "cache_length": room.cache.get_seq_length(), "segments": len(room.segments),
            "turns": sum(1 for s in room.segments if s["kind"] != "frame"),
            "transcript_tail": [s["text"] for s in room.segments[-3:]],
            "branches": sorted(room.branches), "snapshots": len(room.snapshots),
            "snapshot_ids": sorted(room.snapshots), "state_bytes": cache_bytes(room.cache),
            "diagnostics": cache_diagnostics(room.cache),
            "timings": {k: timing_summary(v) for k, v in room.timings.items()},
            "read_mode": self.engine.read_mode, "gpu": self.engine.memory(),
        }

    def transcript(self, room_id: str) -> dict:
        room = self.room(room_id)
        return {"room": room_id, "text": room.transcript, "tokens": room.token_ids,
                "segments": room.segments, "state_id": room.state_id}

    def check(self, room_id: str, modes: list[str] | None = None, dtype: str | None = None) -> dict:
        """Cache-vs-text correctness: replay the segments as the server read them, compare."""
        room = self.room(room_id)
        engine = self.engine
        torch = engine.torch
        ids = room.token_ids
        if not ids:
            raise ApiError(409, "the room has read nothing yet")
        if len(ids) > self.max_check_tokens:
            raise ApiError(413, f"{len(ids)} tokens > --max-check-tokens {self.max_check_tokens}")
        modes = modes or ["step", "chunk"]
        saved_dtype = engine.state_dtype
        if dtype:
            engine.state_dtype = {"float32": torch.float32, "bfloat16": torch.bfloat16}[dtype]
        try:
            # The reference: one fresh forward over the whole transcript, then ``h:``.
            engine.sync()
            started = time.perf_counter()
            reference_cache = engine.new_cache()
            reference_logits = engine.read(reference_cache, ids, all_logits=True)
            reference_reply = engine.reply_logits(reference_cache)[0]
            engine.sync()
            rerender_seconds = time.perf_counter() - started
            result = {
                "room": room_id, "tokens": len(ids), "segments": len(room.segments),
                "state_dtype": str(engine.state_dtype).replace("torch.", ""),
                "rerender_seconds": round(rerender_seconds, 4), "baselines": {}, "modes": {},
            }
            # Baselines: the same forward again (determinism) and the same text as row 0 of a
            # batch of two (bf16 arithmetic noise with identical information).
            again_cache = engine.new_cache()
            again_logits = engine.read(again_cache, ids, all_logits=True)
            result["baselines"]["rerender_vs_rerender"] = {
                "logits": logits_distance(again_logits, reference_logits),
                "state": state_distance(again_cache, reference_cache),
                "reply_logits": logits_distance(engine.reply_logits(again_cache)[0][None], reference_reply[None])["last"],
            }
            pair_cache = engine.new_cache(2)
            pair_logits = engine.forward(pair_cache, [ids, ids], all_logits=True)[0]
            pair_reply = engine.reply_logits(pair_cache)[0]
            pair_row = select_rows(pair_cache, [0])
            result["baselines"]["batch2_vs_rerender"] = {
                "logits": logits_distance(pair_logits, reference_logits),
                "state": state_distance(pair_row, reference_cache),
                "reply_logits": logits_distance(pair_reply[None], reference_reply[None])["last"],
            }
            same_dtype = str(engine.state_dtype) == str(saved_dtype)
            if same_dtype:
                live_reply = engine.reply_logits(room.cache)[0]
                result["live"] = {
                    "state_vs_rerender": state_distance(room.cache, reference_cache),
                    "reply_logits_vs_rerender": logits_distance(live_reply[None], reference_reply[None])["last"],
                }
            replays = {}
            for mode in modes:
                engine.sync()
                started = time.perf_counter()
                cache = engine.new_cache()
                pieces = [engine.read(cache, seg["tokens"], mode=mode, all_logits=True) for seg in room.segments]
                engine.sync()
                seconds = time.perf_counter() - started
                replay_logits = torch.cat(pieces, 0)
                replay_reply = engine.reply_logits(cache)[0]
                replays[mode] = (replay_logits, replay_reply, cache)
                entry = {
                    "replay_seconds": round(seconds, 4),
                    "logits_vs_rerender": logits_distance(replay_logits, reference_logits),
                    "reply_logits_vs_rerender": logits_distance(replay_reply[None], reference_reply[None])["last"],
                    "state_vs_rerender": state_distance(cache, reference_cache),
                }
                if same_dtype:
                    entry["state_vs_live"] = state_distance(cache, room.cache)
                    entry["reply_logits_vs_live"] = logits_distance(replay_reply[None], live_reply[None])["last"]
                entry["ok"] = (
                    entry["logits_vs_rerender"]["last"]["argmax_equal"]
                    and entry["reply_logits_vs_rerender"]["argmax_equal"]
                    and entry["logits_vs_rerender"]["mean_kl"] < 0.02
                )
                result["modes"][mode] = entry
            if "step" in replays and "chunk" in replays:
                result["step_vs_chunk"] = {
                    "logits": logits_distance(replays["step"][0], replays["chunk"][0]),
                    "reply_logits": logits_distance(replays["step"][1][None], replays["chunk"][1][None])["last"],
                    "state": state_distance(replays["step"][2], replays["chunk"][2]),
                }
            return result
        finally:
            engine.state_dtype = saved_dtype


# --------------------------------------------------------------------------- http


class Handler(BaseHTTPRequestHandler):
    service: Service = None  # set by serve()
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler's signature
        return

    def _body(self) -> dict | None:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return None
        raw = self.rfile.read(length)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ApiError(400, f"invalid JSON body: {error}") from error
        if not isinstance(value, dict):
            raise ApiError(400, "the JSON body must be an object")
        return value

    def _respond(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle(self, method: str) -> None:
        try:
            body = self._body()
            status, payload = self.service.dispatch(method, self.path.split("?")[0], body)
        except ApiError as error:
            status, payload = error.status, {"error": str(error)}
        except Exception as error:  # noqa: BLE001 - report to the client, keep serving
            log(f"error on {method} {self.path}: {type(error).__name__}: {error}")
            status, payload = 500, {"error": f"{type(error).__name__}: {error}"}
        self._respond(status, payload)

    def do_GET(self):  # noqa: N802
        self._handle("GET")

    def do_POST(self):  # noqa: N802
        self._handle("POST")

    def do_DELETE(self):  # noqa: N802
        self._handle("DELETE")


def build_service(args) -> Service:
    import torch

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu" and os.environ.get("HGHOST_ALLOW_CPU") != "1":
        raise SystemExit("no ROCm/CUDA device visible; source env.sh or set HGHOST_ALLOW_CPU=1 for a rehearsal")
    engine = Engine(args.checkpoint, device, args.state_dtype, args.read_mode)
    return Service(engine, args.snapshot_dir, args.max_check_tokens)


def serve(args) -> None:
    service = build_service(args)
    Handler.service = service
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    log(f"listening on http://{args.host}:{args.port} (rooms in memory; snapshots -> {args.snapshot_dir})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


# --------------------------------------------------------------------------- smoke client


def http_call(url: str, timeout: float = 600.0):
    def call(method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            url.rstrip("/") + path, data=data, method=method,
            headers={"Content-Type": "application/json"} if data is not None else {},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            payload = error.read().decode("utf-8", "replace")
            raise RuntimeError(f"{method} {path} -> {error.code}: {payload}") from None

    return call


def in_process_call(service: Service):
    def call(method: str, path: str, body: dict | None = None) -> dict:
        status, payload = service.dispatch(method, path, body)
        if status != 200:
            raise RuntimeError(f"{method} {path} -> {status}: {payload}")
        return payload

    return call


def fmt_candidates(label: str, items: list[dict]) -> list[str]:
    lines = [f"  {label}:"]
    for c in items:
        lines.append(
            f"    [{c['branch']}] {c['text']!r}  (tokens {c['new_tokens']}, logprob {c['logprob_sum']},"
            f" {c['finish_reason']}{'' if c['clean_stop'] else ', not clean'})"
        )
    return lines


def smoke(call, room_id: str, frame: str | None, seed: int, n: int, out: Path | None) -> dict:
    """The end-to-end walk: frame, event, candidates, commit, event, candidates + control, check."""
    report: dict = {"room": room_id, "seed": seed, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    lines: list[str] = []
    health = call("GET", "/health")
    report["health"] = health
    lines.append(
        f"== server {health['host']} {Path(health['checkpoint']).name} on {health['device']}, states"
        f" {health['state_dtype']}, read mode {health['read_mode']}, {health['parameters'] / 1e6:.0f}M params,"
        f" empty state {health['state_bytes_empty'] / 2**20:.1f} MB + {health['kv_bytes_per_token'] / 1024:.1f} KB/token"
    )
    created = call("POST", "/rooms", {"room": room_id, "frame": frame, "replace": True})
    report["create"] = created
    lines.append(f"== room {room_id}: frame {created['frame_tokens']} tokens read in {created['read_seconds']}s")

    settings = {"n": n, "temperature": 0.7, "top_p": 0.9, "max_new_tokens": 64}
    event1 = call("POST", f"/rooms/{room_id}/events", {"text": "ember: hi h"})
    report["event1"] = event1
    lines.append(f"== event 'ember: hi h': {event1['tokens']} tokens in {event1['seconds']}s"
                 f" ({event1['tokens_per_second']} tok/s, {event1['read_mode']}); state {event1['state_id']},"
                 f" {event1['token_count']} tokens read")
    batch1 = call("POST", f"/rooms/{room_id}/candidates", {**settings, "seed": seed})
    report["candidates1"] = batch1
    lines.append(f"== candidates 1: {batch1['generation_seconds']}s for {n} ({batch1['steps']} steps,"
                 f" {batch1['seconds_per_step'] * 1000:.0f} ms/step, {batch1['seconds_per_candidate']}s/candidate)")
    lines += fmt_candidates("persistent", batch1["candidates"])
    lines.append("  first-token top: " + ", ".join(f"{t['text']!r} {t['logprob']}" for t in batch1["first_token_top"][:5]))

    chosen = batch1["candidates"][0]["branch"]
    committed = call("POST", f"/rooms/{room_id}/commit", {"branch": chosen})
    report["commit"] = committed
    lines.append(f"== committed {chosen}: {committed['text']!r} (+{committed['tokens']} tokens,"
                 f" separator added: {committed['added_separator']}, {committed['finish_seconds']}s);"
                 f" {committed['token_count']} tokens in memory")
    snap = call("POST", f"/rooms/{room_id}/snapshot", {})
    report["snapshot"] = snap
    lines.append(f"== snapshot {snap['snapshot']} at state {snap['state_id']} ({snap['bytes'] / 2**20:.1f} MB)")

    event2 = call("POST", f"/rooms/{room_id}/events", {"text": "ember: what did you just say?"})
    report["event2"] = event2
    lines.append(f"== event 'ember: what did you just say?': {event2['tokens']} tokens in {event2['seconds']}s"
                 f" ({event2['tokens_per_second']} tok/s)")
    batch2 = call("POST", f"/rooms/{room_id}/candidates", {**settings, "seed": seed + 1, "control": True})
    report["candidates2"] = batch2
    lines.append(f"== candidates 2 (same seed both arms): persistent {batch2['generation_seconds']}s,"
                 f" control re-render {batch2['control']['rerender_tokens']} tokens in"
                 f" {batch2['control']['rerender_seconds']}s + {batch2['control']['generation_seconds']}s")
    lines += fmt_candidates("persistent cache", batch2["candidates"])
    lines += fmt_candidates("fresh-context control (re-rendered transcript)", batch2["control"]["candidates"])
    divergence = batch2["first_token_divergence"]
    lines.append(f"  first-token divergence: max |dlogit| {divergence['max_abs_logit_diff']:.4f},"
                 f" KL {divergence['kl_persistent_vs_control']:.6f}, argmax equal {divergence['argmax_equal']};"
                 f" identical samples per candidate: {batch2['identical_to_control']}")
    lines.append("  persistent first-token top: " + ", ".join(f"{t['text']!r} {t['logprob']}" for t in batch2["first_token_top"][:5]))
    lines.append("  control    first-token top: " + ", ".join(f"{t['text']!r} {t['logprob']}" for t in batch2["control"]["first_token_top"][:5]))

    for c in batch2["candidates"]:
        lines.append(f"    {c['branch']} stop logprobs: {c['stop_logprobs']}")

    def logits_row(label: str, lv: dict, rv: dict, sv: dict | None = None, extra: str = "") -> str:
        text = (f"  {label:22s} all positions: mean KL {lv['mean_kl']:.2e} (max {lv['max_kl']:.2e} at {lv['max_kl_position']}),"
                f" max |dlogit| {lv['max_abs_logit_diff']:.3f}, argmax agreement {lv['argmax_agreement']:.4f}"
                f"{' at ' + str(lv['argmax_disagreements']) if lv['argmax_disagreements'] else ''};"
                f" reply position (entropy {rv['entropy_nats']:.2f} nats): KL {rv['kl']:.2e},"
                f" max |dlogit| {rv['max_abs_logit_diff']:.3f}, argmax equal {rv['argmax_equal']}")
        if sv:
            text += (f"; state rel err ssm {sv['ssm']['relative_error_max']:.2e} conv {sv['conv']['relative_error_max']:.2e}"
                     + (f" K {sv['key']['relative_error_max']:.2e} V {sv['value']['relative_error_max']:.2e}" if "key" in sv else ""))
        return text + extra

    check = call("POST", f"/rooms/{room_id}/check", {})
    report["check"] = check
    lines.append(f"== correctness check over {check['tokens']} tokens / {check['segments']} segments"
                 f" (states {check['state_dtype']}; fresh re-render {check['rerender_seconds']}s):")
    for name, entry in check["baselines"].items():
        lines.append(logits_row(f"baseline {name}", entry["logits"], entry["reply_logits"], entry["state"]))
    for mode, entry in check["modes"].items():
        lines.append(logits_row(f"{mode} vs re-render", entry["logits_vs_rerender"], entry["reply_logits_vs_rerender"],
                                entry["state_vs_rerender"], f"; replay {entry['replay_seconds']}s; ok={entry['ok']}"))
        if "state_vs_live" in entry:
            sl, rl = entry["state_vs_live"], entry["reply_logits_vs_live"]
            lines.append(f"  {mode + ' vs live state':22s} ssm rel err {sl['ssm']['relative_error_max']:.2e}, conv"
                         f" {sl['conv']['relative_error_max']:.2e}; reply KL {rl['kl']:.2e}, max |dlogit|"
                         f" {rl['max_abs_logit_diff']:.3f}, argmax equal {rl['argmax_equal']}")
    if "step_vs_chunk" in check:
        lines.append(logits_row("step vs chunk", check["step_vs_chunk"]["logits"], check["step_vs_chunk"]["reply_logits"],
                                check["step_vs_chunk"]["state"]))
    if "live" in check:
        lv, sv = check["live"]["reply_logits_vs_rerender"], check["live"]["state_vs_rerender"]
        lines.append(f"  {'live vs re-render':22s} reply KL {lv['kl']:.2e}, max |dlogit| {lv['max_abs_logit_diff']:.3f},"
                     f" argmax equal {lv['argmax_equal']}; state rel err ssm {sv['ssm']['relative_error_max']:.2e}"
                     f" conv {sv['conv']['relative_error_max']:.2e}")
    try:
        check_bf16 = call("POST", f"/rooms/{room_id}/check", {"dtype": "bfloat16"})
        report["check_bfloat16"] = check_bf16
        for mode, entry in check_bf16["modes"].items():
            lines.append(logits_row(f"bf16 states {mode}", entry["logits_vs_rerender"], entry["reply_logits_vs_rerender"],
                                    entry["state_vs_rerender"]))
    except RuntimeError as error:
        lines.append(f"  bfloat16 check skipped: {error}")

    # Commit a second-turn candidate (an EOS or length finish adds the separator), persist a
    # snapshot to disk, drop the room, restore it from the file and generate from it.
    second = batch2["candidates"][0]["branch"]
    committed2 = call("POST", f"/rooms/{room_id}/commit", {"branch": second})
    report["commit2"] = committed2
    lines.append(f"== committed {second}: {committed2['text'][:60]!r} (+{committed2['tokens']} tokens, separator added:"
                 f" {committed2['added_separator']}, {committed2['finish_seconds']}s); {committed2['token_count']} tokens")
    rolled = call("POST", f"/rooms/{room_id}/rollback", {"snapshot": snap["snapshot"]})
    report["rollback"] = rolled
    state = call("GET", f"/rooms/{room_id}/state")
    report["state"] = state
    summary = state["diagnostics"]["summary"]
    lines.append(f"== rollback to {snap['snapshot']}: {rolled['token_count']} tokens (snapshot had {snap['token_count']});"
                 f" state {state['state_bytes'] / 2**20:.1f} MB; ssm head-norm mean {summary['ssm_head_norm_mean_over_layers']},"
                 f" max {summary['ssm_head_norm_max_over_layers']}; conv norm mean {summary['conv_norm_mean_over_layers']}")
    lines.append(f"   per-layer ssm head-norm mean: {state['diagnostics']['ssm_head_norm_mean']}")
    timings = state["timings"]
    lines.append(f"== latency: events {timings['events']}, candidates {timings['candidates']}, commits {timings['commits']}")
    gpu = state["gpu"]
    if "allocated_bytes" in gpu:
        lines.append(f"== gpu: allocated {gpu['allocated_bytes'] / 2**30:.2f} GiB, peak {gpu['max_allocated_bytes'] / 2**30:.2f} GiB,"
                     f" free {gpu['free_bytes'] / 2**30:.2f} of {gpu['total_bytes'] / 2**30:.2f} GiB")
    try:
        persisted = call("POST", f"/rooms/{room_id}/snapshot", {"persist": True})
        report["snapshot_persisted"] = persisted
        call("DELETE", f"/rooms/{room_id}")
        restored = call("POST", f"/rooms/{room_id}/rollback", {"snapshot": persisted["snapshot"]})
        report["rollback_from_disk"] = restored
        after = call("POST", f"/rooms/{room_id}/candidates", {**settings, "n": 2, "seed": seed + 2})
        report["candidates_after_restore"] = after
        lines.append(f"== persisted {persisted['snapshot']} ({persisted['bytes'] / 2**20:.1f} MB -> {persisted['path']}),"
                     f" deleted the room, restored from disk: {restored['token_count']} tokens"
                     f" (expected {persisted['token_count']}); 2 candidates from the restored state in"
                     f" {after['generation_seconds']}s: " + " | ".join(repr(c["text"][:50]) for c in after["candidates"]))
    except RuntimeError as error:
        lines.append(f"== disk snapshot path skipped: {error}")
    report["summary_lines"] = lines
    print("\n".join(lines))
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"== wrote {out}")
    return report


# --------------------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command")

    def model_args(p):
        p.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
        p.add_argument("--device", default="auto", help="auto|cuda|cpu (cpu needs HGHOST_ALLOW_CPU=1)")
        p.add_argument("--state-dtype", choices=("float32", "bfloat16"), default="float32",
                       help="dtype of the cached SSM/conv states (K/V stay in the model dtype)")
        p.add_argument("--read-mode", choices=("chunk", "step"), default="chunk",
                       help="how events enter a non-empty state: one continuation forward or token by token")
        p.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOT_DIR)
        p.add_argument("--max-check-tokens", type=int, default=2048)

    s = sub.add_parser("serve", help="run the HTTP service")
    model_args(s)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8140)

    def smoke_args(p):
        p.add_argument("--room", default=None)
        p.add_argument("--frame", default=BARE_FRAME)
        p.add_argument("--no-frame", action="store_true")
        p.add_argument("--seed", type=int, default=20260902)
        p.add_argument("--n", type=int, default=4)
        p.add_argument("--out", type=Path, default=None)

    t = sub.add_parser("smoke", help="stdlib client: walk the API against a running server")
    t.add_argument("--url", default="http://127.0.0.1:8140")
    smoke_args(t)
    u = sub.add_parser("selftest", help="the smoke walk in-process, no HTTP (on hbox)")
    model_args(u)
    smoke_args(u)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "serve":
        serve(args)
    elif args.command in ("smoke", "selftest"):
        room_id = args.room or f"smoke-{time.strftime('%Y%m%d-%H%M%S')}"
        frame = None if args.no_frame else args.frame
        if args.command == "smoke":
            call = http_call(args.url)
        else:
            call = in_process_call(build_service(args))
        smoke(call, room_id, frame, args.seed, args.n, args.out)
    else:
        build_parser().print_help()


if __name__ == "__main__":
    main()
