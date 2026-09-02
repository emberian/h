#!/usr/bin/env python3
"""Export a Falcon-H1 checkpoint (Hugging Face layout) to ONNX for transformers.js.

    export_onnx.py <hf_checkpoint_dir> <output_dir> [--no-verify] [--no-q4] ...

Produces, in <output_dir>:

    config.json                 (+ "transformers.js_config": {"use_external_data_format": true})
    generation_config.json, tokenizer.json, tokenizer_config.json, special_tokens_map.json
    onnx/model.onnx     + onnx/model.onnx_data       fp32
    onnx/model_q4.onnx  + onnx/model_q4.onnx_data    4-bit MatMulNBits / GatherBlockQuantized, block 32 (Hub recipe)
    onnx/model_quantized.onnx + _data                8-bit MatMulNBits + 8-bit GatherBlockQuantized, block 32 (dtype "q8")
    export_report.json          parity numbers, timings, sizes, library versions

The graph has exactly the interface of onnx-community/Falcon-H1-Tiny-*-ONNX (what
transformers.js 4.x feeds a `falcon_h1` model): inputs `input_ids` [B,L] int64,
`attention_mask` [B,T] int64 (T = past + L), `num_logits_to_keep` [] int64 (0 = all), and per
layer `past_key_values.{i}.key|value` [B,kv_heads,past,head_dim], `past_conv.{i}`
[B,conv_dim,d_conv], `past_ssm.{i}` [B,n_heads,d_head,d_state]; outputs `logits`
[B,keep,vocab] and `present.{i}.key|value`, `present_conv.{i}`, `present_ssm.{i}`.

One graph serves prefill (past = 0, any L), decode (L = 1) and continued prefill (past > 0,
L > 1): the Mamba-2 scan is written in closed form over the whole incoming chunk with the
incoming state as its initial condition, and the causal conv reads its window from the conv
state. Only plain ONNX ops are used (no contrib ops in the fp32 graph) so the WebGPU and WASM
backends of onnxruntime-web both run it.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import platform
import shutil
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

MASK_NEG = -1e9      # additive attention bias for masked keys (finite: fully masked rows stay finite)
SEG_NEG = -1e30      # exp() of this is exactly 0 in fp32 (strictly-upper part of the decay matrix)


# --------------------------------------------------------------------------------------
# The export module: Falcon-H1 forward with a flat, ONNX-shaped cache.
# --------------------------------------------------------------------------------------
def rms_norm(x, weight, eps):
    var = x.pow(2).mean(-1, keepdim=True)
    return weight * (x * torch.rsqrt(var + eps))


def softplus_plain(x):
    # F.softplus would export the ONNX `Softplus` op; spell it with universally supported ops.
    return F.relu(x) + torch.log1p(torch.exp(-torch.abs(x)))


def rotate_half(x):
    h = x.shape[-1] // 2
    return torch.cat((-x[..., h:], x[..., :h]), dim=-1)


class FalconH1Layer(nn.Module):
    """One decoder layer with every scalar/vector multiplier folded into the weights."""

    def __init__(self, hf_layer, cfg, mup_vector):
        super().__init__()
        p = lambda t: nn.Parameter(t.detach().clone().float(), requires_grad=False)
        self.eps = cfg.rms_norm_eps
        self.ln1 = p(hf_layer.input_layernorm.weight)
        self.ln2 = p(hf_layer.pre_ff_layernorm.weight)

        # --- attention (attention_in_multiplier on the input, key_multiplier on k, out on o)
        a = hf_layer.self_attn
        ain, aout, km = cfg.attention_in_multiplier, cfg.attention_out_multiplier, cfg.key_multiplier
        self.n_heads, self.n_kv, self.head_dim = cfg.num_attention_heads, cfg.num_key_value_heads, a.head_dim
        self.scale = a.scaling
        self.wq = p(a.q_proj.weight * ain)
        self.wk = p(a.k_proj.weight * ain * km)
        self.wv = p(a.v_proj.weight * ain)
        self.wo = p(a.o_proj.weight * aout)
        self.bq = p(a.q_proj.bias) if a.q_proj.bias is not None else None
        self.bk = p(a.k_proj.bias * km) if a.k_proj.bias is not None else None
        self.bv = p(a.v_proj.bias) if a.v_proj.bias is not None else None
        self.bo = p(a.o_proj.bias * aout) if a.o_proj.bias is not None else None

        # --- mamba (ssm_in_multiplier on the input, mup vector on in_proj rows, ssm_out on out_proj)
        m = hf_layer.mamba
        self.d_inner, self.conv_dim, self.n_ssm_heads = m.intermediate_size, m.conv_dim, m.num_heads
        self.d_head, self.d_state, self.n_groups, self.d_conv = m.head_dim, m.ssm_state_size, m.n_groups, m.conv_kernel_size
        mup = mup_vector.reshape(-1).float()
        self.w_in = p(m.in_proj.weight * cfg.ssm_in_multiplier * mup[:, None])
        self.b_in = p(m.in_proj.bias * mup) if m.in_proj.bias is not None else None
        self.conv_w = p(m.conv1d.weight[:, 0, :])                     # [conv_dim, d_conv]
        self.conv_b = p(m.conv1d.bias) if m.conv1d.bias is not None else None
        self.dt_bias = p(m.dt_bias)
        self.A = p(-torch.exp(m.A_log.float()))                        # [n_heads], negative
        self.D = p(m.D)
        self.w_out = p(m.out_proj.weight * cfg.ssm_out_multiplier)
        self.b_out = p(m.out_proj.bias * cfg.ssm_out_multiplier) if m.out_proj.bias is not None else None
        self.time_step_limit = tuple(m.time_step_limit)
        if m.mamba_rms_norm:
            # tiiuae/Falcon-H1-Tiny-* have mamba_rms_norm=false; the gated norm is small to add.
            raise NotImplementedError("mamba_rms_norm=true is not implemented in this exporter")

        # --- mlp
        f = hf_layer.feed_forward
        gm, dm = cfg.mlp_multipliers
        self.w_gate = p(f.gate_proj.weight * gm)
        self.w_up = p(f.up_proj.weight)
        self.w_down = p(f.down_proj.weight * dm)
        self.b_gate = p(f.gate_proj.bias * gm) if f.gate_proj.bias is not None else None
        self.b_up = p(f.up_proj.bias) if f.up_proj.bias is not None else None
        self.b_down = p(f.down_proj.bias * dm) if f.down_proj.bias is not None else None

    # ---- mamba ---------------------------------------------------------------------
    def mamba(self, x, cur_mask, past_conv, past_ssm, causal_ll, strict_ll):
        B, L = x.shape[0], x.shape[1]
        H, P, N, G = self.n_ssm_heads, self.d_head, self.d_state, self.n_groups
        x = x * cur_mask[:, :, None]
        zxbcdt = F.linear(x, self.w_in, self.b_in)
        gate, xBC, dt = torch.split(zxbcdt, [self.d_inner, self.conv_dim, H], dim=-1)

        # causal depthwise conv over [state window | new tokens]; the state keeps the last d_conv inputs
        xBC_t = xBC.transpose(1, 2)                                             # [B, conv_dim, L]
        full = torch.cat([past_conv[:, :, 1:], xBC_t], dim=-1)                  # [B, conv_dim, d_conv-1+L]
        new_conv = full[:, :, -self.d_conv:]
        conv = self.conv_w[:, 0:1] * full[:, :, 0:L]
        for k in range(1, self.d_conv):
            conv = conv + self.conv_w[:, k:k + 1] * full[:, :, k:k + L]
        if self.conv_b is not None:
            conv = conv + self.conv_b[:, None]
        xBC = F.silu(conv).transpose(1, 2) * cur_mask[:, :, None]              # [B, L, conv_dim]
        xs, Bm, Cm = torch.split(xBC, [self.d_inner, G * N, G * N], dim=-1)

        dt = softplus_plain(dt + self.dt_bias)                                  # [B, L, H]
        if self.time_step_limit != (0.0, float("inf")):
            dt = torch.clamp(dt, self.time_step_limit[0], self.time_step_limit[1])
        xh = xs.reshape(B, L, H, P).transpose(1, 2)                             # [B, H, L, P]
        Bk = Bm.reshape(B, L, G, 1, N).expand(B, L, G, H // G, N).reshape(B, L, H, N).transpose(1, 2)  # [B, H, L, N]
        Cq = Cm.reshape(B, L, G, 1, N).expand(B, L, G, H // G, N).reshape(B, L, H, N).transpose(1, 2)  # [B, H, L, N]
        dtT = dt.transpose(1, 2)                                                # [B, H, L]
        a = dtT * self.A[None, :, None]                                         # [B, H, L]  (<= 0)
        cum = torch.cumsum(a, dim=-1)                                           # [B, H, L]

        # segment sum the way transformers does it: seg[t, s] = a_{s+1} + ... + a_t = cum_t - cum_s
        aE = torch.where(strict_ll, a[:, :, :, None], torch.zeros((), dtype=a.dtype))   # [B, H, L(t), L(s)] holds a_t where t > s
        seg = torch.cumsum(aE, dim=-2)
        seg = torch.where(causal_ll, seg, torch.full((), SEG_NEG, dtype=a.dtype))
        decay = torch.exp(seg)                                                  # [B, H, L, L], 0 above the diagonal

        Gm = torch.matmul(Cq, Bk.transpose(-1, -2))                             # [B, H, L, L]: C_t . B_s
        M = Gm * decay * dtT[:, :, None, :]
        y = torch.matmul(M, xh)                                                 # intra-chunk
        y = y + torch.matmul(Cq, past_ssm.transpose(-1, -2)) * torch.exp(cum)[..., None]   # incoming state
        y = y + self.D[None, :, None, None] * xh

        decay_to_end = torch.exp(cum[:, :, -1:] - cum)                          # [B, H, L]
        w = (decay_to_end * dtT)[..., None]                                     # [B, H, L, 1]
        new_ssm = past_ssm * torch.exp(cum[:, :, -1])[..., None, None] + torch.matmul((xh * w).transpose(-1, -2), Bk)

        y = y.transpose(1, 2).reshape(B, L, H * P)
        y = y * F.silu(gate)
        return F.linear(y, self.w_out, self.b_out), new_conv, new_ssm

    # ---- attention -----------------------------------------------------------------
    def attention(self, x, cos, sin, attn_bias, past_k, past_v):
        B, L = x.shape[0], x.shape[1]
        q = F.linear(x, self.wq, self.bq).reshape(B, L, self.n_heads, self.head_dim).transpose(1, 2)
        k = F.linear(x, self.wk, self.bk).reshape(B, L, self.n_kv, self.head_dim).transpose(1, 2)
        v = F.linear(x, self.wv, self.bv).reshape(B, L, self.n_kv, self.head_dim).transpose(1, 2)
        q = q * cos + rotate_half(q) * sin
        k = k * cos + rotate_half(k) * sin
        k = torch.cat([past_k, k], dim=2)                                       # [B, kv, T, hd]
        v = torch.cat([past_v, v], dim=2)
        T = k.shape[2]
        rep = self.n_heads // self.n_kv
        kr = k[:, :, None, :, :].expand(B, self.n_kv, rep, T, self.head_dim).reshape(B, self.n_heads, T, self.head_dim)
        vr = v[:, :, None, :, :].expand(B, self.n_kv, rep, T, self.head_dim).reshape(B, self.n_heads, T, self.head_dim)
        scores = torch.matmul(q, kr.transpose(-1, -2)) * self.scale + attn_bias
        attn = torch.matmul(torch.softmax(scores, dim=-1), vr)                 # [B, nH, L, hd]
        attn = attn.transpose(1, 2).reshape(B, L, self.n_heads * self.head_dim)
        return F.linear(attn, self.wo, self.bo), k, v

    def forward(self, h, cur_mask, cos, sin, attn_bias, causal_ll, strict_ll, past_k, past_v, past_conv, past_ssm):
        x = rms_norm(h, self.ln1, self.eps)
        m_out, new_conv, new_ssm = self.mamba(x, cur_mask, past_conv, past_ssm, causal_ll, strict_ll)
        a_out, new_k, new_v = self.attention(x, cos, sin, attn_bias, past_k, past_v)
        h = h + m_out + a_out
        x = rms_norm(h, self.ln2, self.eps)
        y = F.linear(x, self.w_up, self.b_up) * F.silu(F.linear(x, self.w_gate, self.b_gate))
        h = h + F.linear(y, self.w_down, self.b_down)
        return h, new_k, new_v, new_conv, new_ssm


class FalconH1Onnx(nn.Module):
    def __init__(self, hf):
        super().__init__()
        cfg = hf.config
        self.cfg = cfg
        self.embed = nn.Parameter(hf.model.embed_tokens.weight.detach().clone().float(), requires_grad=False)
        self.lm_head = nn.Parameter(hf.lm_head.weight.detach().clone().float(), requires_grad=False)
        self.embedding_multiplier = float(cfg.embedding_multiplier)
        self.lm_head_multiplier = float(cfg.lm_head_multiplier)
        self.final_norm = nn.Parameter(hf.model.final_layernorm.weight.detach().clone().float(), requires_grad=False)
        self.eps = cfg.rms_norm_eps
        rot = hf.model.rotary_emb
        self.inv_freq = nn.Parameter(rot.inv_freq.detach().clone().float(), requires_grad=False)
        self.attention_scaling = float(rot.attention_scaling)
        mup = hf.model.layers[0].mamba.mup_vector
        self.layers = nn.ModuleList(FalconH1Layer(l, cfg, mup) for l in hf.model.layers)

    def forward(self, input_ids, attention_mask, num_logits_to_keep, *cache):
        B, L = input_ids.shape[0], input_ids.shape[1]
        past_len = cache[0].shape[2]
        maskf = attention_mask.to(torch.float32)                                # [B, T]
        T = maskf.shape[1]

        # positions from the mask (left-padding safe), like the reference export
        pos = torch.clamp(torch.cumsum(maskf, dim=-1) - 1.0, min=0.0)[:, -L:]  # [B, L] float
        cur_mask = maskf[:, -L:]                                                # [B, L]
        freqs = pos[:, :, None] * self.inv_freq[None, None, :]
        emb = torch.cat((freqs, freqs), dim=-1)
        cos = (torch.cos(emb) * self.attention_scaling)[:, None]               # [B, 1, L, hd]
        sin = (torch.sin(emb) * self.attention_scaling)[:, None]

        # attention bias [B, 1, L, T]: key j visible to query i iff j <= past + i and mask[j]
        qi = torch.arange(L, dtype=torch.float32) + past_len                    # [L]
        kj = torch.arange(T, dtype=torch.float32)                               # [T]
        causal_lt = kj[None, :] <= qi[:, None]                                  # [L, T]
        allowed = causal_lt[None, None] & (maskf[:, None, None, :] > 0.5)
        attn_bias = torch.where(allowed, torch.zeros((), dtype=torch.float32), torch.full((), MASK_NEG, dtype=torch.float32))

        # [L, L] masks for the scan
        li = torch.arange(L, dtype=torch.float32)
        causal_ll = li[:, None] >= li[None, :]
        strict_ll = li[:, None] > li[None, :]

        h = self.embed[input_ids] * self.embedding_multiplier
        presents = []
        for i, layer in enumerate(self.layers):
            pk, pv, pc, ps = cache[4 * i:4 * i + 4]
            h, k, v, c, s = layer(h, cur_mask, cos, sin, attn_bias, causal_ll, strict_ll, pk, pv, pc, ps)
            presents += [k, v, c, s]
        h = rms_norm(h, self.final_norm, self.eps)

        start = torch.where(num_logits_to_keep == 0, torch.zeros_like(num_logits_to_keep), L - num_logits_to_keep)
        h = h[:, start:, :]
        logits = F.linear(h, self.lm_head) * self.lm_head_multiplier
        return (logits, *presents)


# --------------------------------------------------------------------------------------
# Names / shapes
# --------------------------------------------------------------------------------------
def cache_names(n_layers):
    names = []
    for i in range(n_layers):
        names += [f"past_key_values.{i}.key", f"past_key_values.{i}.value", f"past_conv.{i}", f"past_ssm.{i}"]
    return names


def present_names(n_layers):
    names = []
    for i in range(n_layers):
        names += [f"present.{i}.key", f"present.{i}.value", f"present_conv.{i}", f"present_ssm.{i}"]
    return names


def cache_shapes(cfg):
    d_inner = cfg.mamba_d_ssm if cfg.mamba_d_ssm is not None else int(cfg.mamba_expand * cfg.hidden_size)
    conv_dim = d_inner + 2 * cfg.mamba_n_groups * cfg.mamba_d_state
    head_dim = getattr(cfg, "head_dim", None) or cfg.hidden_size // cfg.num_attention_heads
    return dict(kv=(cfg.num_key_value_heads, head_dim), conv=(conv_dim, cfg.mamba_d_conv),
                ssm=(cfg.mamba_n_heads, cfg.mamba_d_head, cfg.mamba_d_state))


def zero_cache(cfg, batch, past=0, dtype=np.float32):
    s = cache_shapes(cfg)
    out = {}
    for i in range(cfg.num_hidden_layers):
        out[f"past_key_values.{i}.key"] = np.zeros((batch, s["kv"][0], past, s["kv"][1]), dtype)
        out[f"past_key_values.{i}.value"] = np.zeros((batch, s["kv"][0], past, s["kv"][1]), dtype)
        out[f"past_conv.{i}"] = np.zeros((batch, *s["conv"]), dtype)
        out[f"past_ssm.{i}"] = np.zeros((batch, *s["ssm"]), dtype)
    return out


# --------------------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------------------
def export_graph(hf, opset):
    import onnx
    cfg = hf.config
    module = FalconH1Onnx(hf).eval()
    n_layers = cfg.num_hidden_layers
    B, L, P = 2, 5, 3      # trace with a non-trivial past so the concat/state paths are real
    ids = torch.randint(0, cfg.vocab_size, (B, L), dtype=torch.int64)
    mask = torch.ones(B, P + L, dtype=torch.int64)
    keep = torch.tensor(1, dtype=torch.int64)
    cache = zero_cache(cfg, B, P)
    for k in cache:
        cache[k] = torch.from_numpy(np.random.randn(*cache[k].shape).astype(np.float32) * 0.1)
    in_names = ["input_ids", "attention_mask", "num_logits_to_keep", *cache_names(n_layers)]
    out_names = ["logits", *present_names(n_layers)]
    dyn = {"input_ids": {0: "batch_size", 1: "sequence_length"},
           "attention_mask": {0: "batch_size", 1: "total_sequence_length"},
           "logits": {0: "batch_size", 1: "num_logits_to_keep"}}
    for i in range(n_layers):
        dyn[f"past_key_values.{i}.key"] = {0: "batch_size", 2: "past_sequence_length"}
        dyn[f"past_key_values.{i}.value"] = {0: "batch_size", 2: "past_sequence_length"}
        dyn[f"past_conv.{i}"] = {0: "batch_size"}
        dyn[f"past_ssm.{i}"] = {0: "batch_size"}
        dyn[f"present.{i}.key"] = {0: "batch_size", 2: "total_sequence_length"}
        dyn[f"present.{i}.value"] = {0: "batch_size", 2: "total_sequence_length"}
        dyn[f"present_conv.{i}"] = {0: "batch_size"}
        dyn[f"present_ssm.{i}"] = {0: "batch_size"}

    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="h1onnx-")
    raw = os.path.join(tmpdir, "raw.onnx")
    # The TorchScript tracer allocates millions of small Python objects; with the cyclic GC enabled
    # the export spends nearly all its time in gc_collect_main. Pause it for the duration.
    import gc
    gc.disable()
    try:
        with torch.no_grad():
            torch.onnx.export(module, (ids, mask, keep, *[cache[n] for n in cache_names(n_layers)]), raw,
                              dynamo=False, opset_version=opset, input_names=in_names, output_names=out_names,
                              dynamic_axes=dyn, do_constant_folding=True)
    finally:
        gc.enable()
        gc.collect()
    model = onnx.load(raw, load_external_data=True)
    shutil.rmtree(tmpdir, ignore_errors=True)
    model.producer_name = "h-ghost export_onnx.py"
    return model


def slim(model):
    import onnxslim
    return onnxslim.slim(model)


def find_embedding_initializer(model):
    inits = {t.name: t for t in model.graph.initializer}
    for n in model.graph.node:
        if n.op_type == "Gather" and n.input[1] == "input_ids" and n.input[0] in inits:
            return n.input[0]
    return None


def dedupe_tied_head(model):
    """fp32 only: if the lm_head MatMul weight equals embed^T, feed it Transpose(embed) instead."""
    import onnx
    from onnx import numpy_helper
    emb_name = find_embedding_initializer(model)
    if emb_name is None:
        return False
    inits = {t.name: t for t in model.graph.initializer}
    emb = numpy_helper.to_array(inits[emb_name])
    for n in model.graph.node:
        if n.op_type != "MatMul" or n.input[1] not in inits or n.input[1] == emb_name:
            continue
        w = inits[n.input[1]]
        if tuple(w.dims) != (emb.shape[1], emb.shape[0]):
            continue
        if not np.array_equal(numpy_helper.to_array(w), emb.T):
            continue
        t_name = emb_name + "_T"
        tnode = onnx.helper.make_node("Transpose", [emb_name], [t_name], name="lm_head_tied_transpose", perm=[1, 0])
        old = n.input[1]
        n.input[1] = t_name
        model.graph.initializer.remove(inits[old])
        # insert before the consumer
        idx = list(model.graph.node).index(n)
        model.graph.node.insert(idx, tnode)
        return True
    return False


def save_external(model, path, threshold=1024):
    """Write `path` with every initializer >= threshold bytes in a single `<path>_data` file.

    Done by hand rather than with onnx.save_model(save_as_external_data=True): with the graph
    produced here that call wrote every tensor twice (offsets started at the file's midpoint),
    and tiny constants must stay inline or onnxruntime's shape inference cannot read Slice
    bounds. The data file is written once, sequentially, and its size is checked."""
    import onnx
    from onnx.external_data_helper import set_external_data
    m = copy.deepcopy(model)
    data_name = os.path.basename(path) + "_data"
    data_path = os.path.join(os.path.dirname(path), data_name)
    total = 0
    with open(data_path, "wb") as f:
        for t in m.graph.initializer:
            if t.data_location == onnx.TensorProto.EXTERNAL:
                raise RuntimeError(f"initializer {t.name} still points at external data")
            raw = t.raw_data if t.HasField("raw_data") else onnx.numpy_helper.to_array(t).tobytes()
            if len(raw) < threshold:
                continue
            if not t.HasField("raw_data"):
                t.raw_data = raw
                for field in ("float_data", "int32_data", "int64_data", "double_data", "uint64_data", "string_data"):
                    t.ClearField(field)
            f.write(raw)
            set_external_data(t, data_name, offset=total, length=len(raw))
            t.ClearField("raw_data")
            total += len(raw)
    onnx.save_model(m, path)
    if os.path.getsize(data_path) != total:
        raise RuntimeError(f"{data_path}: wrote {total} bytes but file is {os.path.getsize(data_path)}")


def quantize_q4(model, block_size=32, is_symmetric=False, accuracy_level=None, quantize_embedding=True):
    """Same recipe as the onnx-community Falcon-H1 q4 files: MatMulNBits (bits=4, block 32, with
    zero points) on every MatMul with a constant weight, GatherBlockQuantized on the embedding."""
    from onnxruntime.quantization.matmul_nbits_quantizer import MatMulNBitsQuantizer
    ops = ("MatMul", "Gather") if quantize_embedding else ("MatMul",)
    q = MatMulNBitsQuantizer(copy.deepcopy(model), bits=4, block_size=block_size, is_symmetric=is_symmetric,
                             accuracy_level=accuracy_level, op_types_to_quantize=ops)
    q.process()
    return q.model.model


def swap_embedding_fp16(model):
    """Store the embedding table as float16; cast the gathered rows back to fp32 in-graph."""
    import onnx
    from onnx import numpy_helper
    emb_name = find_embedding_initializer(model)
    if emb_name is None:
        return False
    inits = {t.name: t for t in model.graph.initializer}
    gather = next(n for n in model.graph.node if n.op_type == "Gather" and n.input[1] == "input_ids" and n.input[0] == emb_name)
    arr = numpy_helper.to_array(inits[emb_name]).astype(np.float16)
    model.graph.initializer.append(numpy_helper.from_array(arr, emb_name + "_fp16"))
    out = gather.output[0]
    gather.input[0] = emb_name + "_fp16"
    gather.output[0] = out + "_fp16"
    cast = onnx.helper.make_node("Cast", [out + "_fp16"], [out], name="embed_fp16_to_fp32", to=onnx.TensorProto.FLOAT)
    idx = list(model.graph.node).index(gather)
    model.graph.node.insert(idx + 1, cast)
    if not any(emb_name in n.input for n in model.graph.node):
        model.graph.initializer.remove(inits[emb_name])
    return True


def quantize_embedding_8bit(model, block_size=32):
    """Replace the embedding Gather with an 8-bit GatherBlockQuantized (com.microsoft).

    onnxruntime's MatMulNBitsQuantizer only emits the 4-bit form of this op, but the kernels in
    the onnxruntime-web build transformers.js 4.2.0 uses accept bits=8 with uint8 data on both
    the CPU/WASM EP (gather_axis 0, quantize_axis = last) and the WebGPU EP. Asymmetric,
    per block of `block_size` along the hidden dim: x ~ (q - zp) * scale."""
    import onnx
    from onnx import numpy_helper
    emb_name = find_embedding_initializer(model)
    if emb_name is None:
        return False
    inits = {t.name: t for t in model.graph.initializer}
    gather = next(n for n in model.graph.node if n.op_type == "Gather" and n.input[1] == "input_ids" and n.input[0] == emb_name)
    W = numpy_helper.to_array(inits[emb_name]).astype(np.float32)
    V, H = W.shape
    if H % block_size:
        raise ValueError(f"hidden size {H} is not a multiple of block_size {block_size}")
    blocks = W.reshape(V, H // block_size, block_size)
    mn, mx = blocks.min(-1, keepdims=True), blocks.max(-1, keepdims=True)
    scale = (mx - mn) / 255.0
    scale = np.where(scale == 0, np.float32(1.0), scale).astype(np.float32)
    zp = np.clip(np.round(-mn / scale), 0, 255)
    q = np.clip(np.round(blocks / scale) + zp, 0, 255).astype(np.uint8)
    model.graph.initializer.extend([
        numpy_helper.from_array(q.reshape(V, H), emb_name + "_Q8"),
        numpy_helper.from_array(scale.reshape(V, H // block_size).astype(np.float32), emb_name + "_scales"),
        numpy_helper.from_array(zp.reshape(V, H // block_size).astype(np.uint8), emb_name + "_zero_points"),
    ])
    node = onnx.helper.make_node("GatherBlockQuantized",
                                 [emb_name + "_Q8", gather.input[1], emb_name + "_scales", emb_name + "_zero_points"],
                                 [gather.output[0]], name=(gather.name or "embed_gather") + "_Q8", domain="com.microsoft",
                                 bits=8, block_size=block_size, gather_axis=0, quantize_axis=1)
    idx = list(model.graph.node).index(gather)
    model.graph.node.remove(gather)
    model.graph.node.insert(idx, node)
    if not any(emb_name in n.input for n in model.graph.node):
        model.graph.initializer.remove(inits[emb_name])
    if not any(o.domain == "com.microsoft" for o in model.opset_import):
        model.opset_import.append(onnx.helper.make_opsetid("com.microsoft", 1))
    return True


def quantize_q8(model, block_size=32, embedding="q8"):
    """8-bit MatMulNBits (block 32, zero points) on every MatMul with a constant weight.

    4-bit round-to-nearest wrecks tiiuae/Falcon-H1-Tiny-90M-Base (mean KL 0.46 nats to fp32 on
    every subset of matrices; see README); 8-bit is within 0.003 nats. The embedding table
    (18% of the parameters) is stored as 8-bit GatherBlockQuantized (`q8`, default), 4-bit
    GatherBlockQuantized (`q4`, ~0.017 nats, 9 MB smaller), fp16 with a Cast after the Gather
    (`fp16`: needs the WebGPU shader-f16 feature, which headless/SwiftShader adapters and some
    real devices lack, so generation fails there) or left in fp32."""
    from onnxruntime.quantization.matmul_nbits_quantizer import MatMulNBitsQuantizer
    q = MatMulNBitsQuantizer(copy.deepcopy(model), bits=8, block_size=block_size, is_symmetric=False,
                             accuracy_level=None, op_types_to_quantize=("MatMul",))
    q.process()
    m = q.model.model
    if embedding == "q8":
        quantize_embedding_8bit(m, block_size)
    elif embedding == "fp16":
        swap_embedding_fp16(m)
    elif embedding == "q4":
        q2 = MatMulNBitsQuantizer(m, bits=4, block_size=block_size, is_symmetric=False, op_types_to_quantize=("Gather",))
        q2.process()
        m = q2.model.model
    return m


# --------------------------------------------------------------------------------------
# onnxruntime driver (Python mirror of what transformers.js does)
# --------------------------------------------------------------------------------------
class OrtDecoder:
    def __init__(self, path, cfg, threads=None):
        import onnxruntime as ort
        so = ort.SessionOptions()
        if threads:
            so.intra_op_num_threads = threads
        self.sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        self.cfg = cfg
        self.n_layers = cfg.num_hidden_layers
        self.out_names = [o.name for o in self.sess.get_outputs()]

    def step(self, ids, mask, cache, keep):
        feeds = {"input_ids": ids.astype(np.int64), "attention_mask": mask.astype(np.int64),
                 "num_logits_to_keep": np.array(keep, dtype=np.int64), **cache}
        outs = self.sess.run(None, feeds)
        logits = outs[0]
        new_cache = {}
        for name, val in zip(self.out_names[1:], outs[1:]):
            new_cache[name.replace("present_conv", "past_conv").replace("present_ssm", "past_ssm").replace("present", "past_key_values")] = val
        return logits, new_cache

    def greedy(self, prompt_ids, n_new):
        B = prompt_ids.shape[0]
        cache = zero_cache(self.cfg, B)
        mask = np.ones((B, prompt_ids.shape[1]), np.int64)
        t0 = time.perf_counter()
        logits, cache = self.step(prompt_ids, mask, cache, 1)
        t_prefill = time.perf_counter() - t0
        out = []
        nxt = logits[:, -1].argmax(-1)
        t0 = time.perf_counter()
        for _ in range(n_new):
            out.append(nxt)
            mask = np.concatenate([mask, np.ones((B, 1), np.int64)], 1)
            logits, cache = self.step(nxt[:, None], mask, cache, 1)
            nxt = logits[:, -1].argmax(-1)
        t_decode = (time.perf_counter() - t0) / max(n_new, 1)
        return np.stack(out, 1), t_prefill, t_decode


# --------------------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------------------
def kl_from_logits(ref, other):
    """Mean over positions of KL(softmax(ref) || softmax(other)), in nats."""
    def lsm(x):
        x = x - x.max(-1, keepdims=True)
        return x - np.log(np.exp(x).sum(-1, keepdims=True))
    p = np.exp(lsm(ref))
    return float((p * (lsm(ref) - lsm(other))).sum(-1).mean())


def verify_quantized(tag, path, cfg, tok, ids, ref_logits, hf_new, n_new, report):
    dec = OrtDecoder(path, cfg)
    L = ids.shape[1]
    lg, _ = dec.step(ids.numpy(), np.ones((1, L), np.int64), zero_cache(cfg, 1), 0)
    err = np.abs(lg - ref_logits)
    r = report.setdefault(tag, {})
    r.update({"logits_max_abs_err": float(err.max()), "logits_mean_abs_err": float(err.mean()),
              "argmax_agree": float((lg.argmax(-1) == ref_logits.argmax(-1)).mean()),
              "mean_kl_nats": kl_from_logits(ref_logits, lg)})
    new, t_pre, t_dec = dec.greedy(ids.numpy(), n_new)
    new = new[0]
    n = min(len(new), len(hf_new))
    r["greedy_text"] = tok.decode(new)
    r["greedy_prefix_match_tokens"] = int(next((i for i in range(n) if new[i] != hf_new[i]), n))
    r["cpu_prefill_ms"] = round(t_pre * 1000, 1)
    r["cpu_decode_ms_per_token"] = round(t_dec * 1000, 1)
    print(f"[verify] {tag} vs PyTorch ({L} positions): mean KL {r['mean_kl_nats']:.4f} nats, argmax agree {r['argmax_agree']:.3f}, "
          f"logits max abs {err.max():.3e}, mean {err.mean():.3e}")
    print(f"         {tag} greedy: {tok.decode(new)!r}")
    print(f"         first {r['greedy_prefix_match_tokens']}/{n} tokens identical to PyTorch greedy; cpu prefill {t_pre * 1000:.0f} ms, decode {t_dec * 1000:.1f} ms/token")


def verify(hf, tok, out_dir, prompt, n_new, report, do_q4, do_q8):
    cfg = hf.config
    enc = tok(prompt, return_tensors="pt")
    ids = enc["input_ids"]
    L = ids.shape[1]
    with torch.no_grad():
        ref_logits = hf(input_ids=ids, use_cache=False).logits.float().numpy()
    fp32 = OrtDecoder(os.path.join(out_dir, "onnx", "model.onnx"), cfg)

    # (a) full-prompt logits, all positions
    logits, cache = fp32.step(ids.numpy(), np.ones((1, L), np.int64), zero_cache(cfg, 1), 0)
    err = np.abs(logits - ref_logits)
    report["prompt"] = prompt
    report["fp32_prompt_tokens"] = int(L)
    report["fp32_logits_max_abs_err"] = float(err.max())
    report["fp32_logits_mean_abs_err"] = float(err.mean())
    report["fp32_argmax_agree"] = float((logits.argmax(-1) == ref_logits.argmax(-1)).mean())
    report["fp32_mean_kl_nats"] = kl_from_logits(ref_logits, logits)
    print(f"[verify] fp32 logits vs PyTorch ({L} tokens, all positions): max abs {err.max():.3e}, mean {err.mean():.3e}, KL {report['fp32_mean_kl_nats']:.2e}")

    # (b) prefill split in two: the second half runs with the first half's state (incoming-state path)
    cut = max(1, L // 2)
    l1, c1 = fp32.step(ids[:, :cut].numpy(), np.ones((1, cut), np.int64), zero_cache(cfg, 1), 0)
    l2, c2 = fp32.step(ids[:, cut:].numpy(), np.ones((1, L), np.int64), c1, 0)
    err2 = np.abs(np.concatenate([l1, l2], 1) - ref_logits)
    report["fp32_split_prefill_max_abs_err"] = float(err2.max())
    cache_err = max(float(np.abs(cache[k] - c2[k]).max()) for k in cache)
    report["fp32_split_prefill_cache_max_abs_err"] = cache_err
    print(f"[verify] split prefill ({cut}+{L - cut}) vs PyTorch: max abs {err2.max():.3e}; cache one-shot vs split: max abs {cache_err:.3e}")

    # (c) greedy generation, ONNX with-past loop vs transformers generate()
    with torch.no_grad():
        gen = hf.generate(ids, attention_mask=torch.ones_like(ids), max_new_tokens=n_new, do_sample=False, num_beams=1)
    hf_new = gen[0, L:].numpy()
    ort_new, t_pre, t_dec = fp32.greedy(ids.numpy(), len(hf_new))
    ort_new = ort_new[0]
    match = bool(np.array_equal(hf_new, ort_new))
    report["greedy_new_tokens"] = int(len(hf_new))
    report["fp32_greedy_matches_pytorch"] = match
    report["fp32_greedy_text"] = tok.decode(ort_new)
    report["pytorch_greedy_text"] = tok.decode(hf_new)
    report["fp32_cpu_prefill_ms"] = round(t_pre * 1000, 1)
    report["fp32_cpu_decode_ms_per_token"] = round(t_dec * 1000, 1)
    print(f"[verify] greedy {len(hf_new)} tokens: {'IDENTICAL' if match else 'DIFFERENT'} to PyTorch")
    print(f"         pytorch: {tok.decode(hf_new)!r}")
    if not match:
        print(f"         onnx:    {tok.decode(ort_new)!r}")
    print(f"         onnx cpu: prefill {t_pre * 1000:.0f} ms, decode {t_dec * 1000:.1f} ms/token")

    # (d) batch>1 with left padding: the padded row must still match
    pad = 3
    ids2 = np.concatenate([np.full((1, pad), cfg.pad_token_id or 0, np.int64), ids.numpy()], 1)
    ids2 = np.concatenate([ids2, np.concatenate([ids.numpy(), ids.numpy()[:, :pad]], 1)], 0)
    mask2 = np.ones((2, L + pad), np.int64)
    mask2[0, :pad] = 0
    lg2, _ = fp32.step(ids2, mask2, zero_cache(cfg, 2), 0)
    err3 = float(np.abs(lg2[0, pad:] - ref_logits[0]).max())
    report["fp32_batch2_leftpad_row_max_abs_err"] = err3
    print(f"[verify] batch=2 left-padded row vs PyTorch: max abs {err3:.3e}")

    if do_q4:
        verify_quantized("q4", os.path.join(out_dir, "onnx", "model_q4.onnx"), cfg, tok, ids, ref_logits, hf_new, n_new, report)
    if do_q8:
        verify_quantized("q8", os.path.join(out_dir, "onnx", "model_quantized.onnx"), cfg, tok, ids, ref_logits, hf_new, n_new, report)


# --------------------------------------------------------------------------------------
def versions():
    import importlib.metadata as md
    out = {"python": platform.python_version(), "platform": platform.platform()}
    for p in ["torch", "transformers", "onnx", "onnxruntime", "onnxslim", "onnx-ir", "numpy", "safetensors", "tokenizers"]:
        try:
            out[p] = md.version(p)
        except md.PackageNotFoundError:
            out[p] = None
    return out


def copy_side_files(ckpt, out_dir, cfg_json_extra):
    with open(os.path.join(ckpt, "config.json")) as f:
        cfg = json.load(f)
    cfg["transformers.js_config"] = cfg_json_extra
    with open(os.path.join(out_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    for name in ["generation_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
                 "chat_template.jinja", "chat_template.json"]:
        src = os.path.join(ckpt, name)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(out_dir, name))
    if not os.path.exists(os.path.join(out_dir, "generation_config.json")):
        with open(os.path.join(out_dir, "generation_config.json"), "w") as f:
            json.dump({"bos_token_id": cfg.get("bos_token_id"), "eos_token_id": cfg.get("eos_token_id"),
                       "pad_token_id": cfg.get("pad_token_id")}, f, indent=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("checkpoint", help="HF checkpoint dir (config.json, model.safetensors, tokenizer files)")
    ap.add_argument("output", help="output model dir (transformers.js layout)")
    ap.add_argument("--opset", type=int, default=18, help="18+: ReduceMean takes axes as an input, which the q4 quantizer's forced bump to opset 21 requires")
    ap.add_argument("--no-slim", action="store_true", help="skip onnxslim")
    ap.add_argument("--no-q4", action="store_true", help="only write the fp32 model")
    ap.add_argument("--q4-block-size", type=int, default=32)
    ap.add_argument("--q4-symmetric", action="store_true", help="symmetric 4-bit (no zero points); the Hub export is asymmetric")
    ap.add_argument("--q4-accuracy-level", type=int, default=None, help="MatMulNBits accuracy_level (4 = int8 compute, faster on CPU/WASM)")
    ap.add_argument("--no-q4-embedding", action="store_true", help="leave the embedding Gather in fp32")
    ap.add_argument("--no-q8", action="store_true", help="skip the 8-bit model (model_quantized.onnx)")
    ap.add_argument("--q8-block-size", type=int, default=32)
    ap.add_argument("--q8-embedding", choices=["q8", "q4", "fp16", "fp32"], default="q8",
                    help="how the 8-bit model stores the embedding table (fp16 needs WebGPU shader-f16)")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--prompt", default="The letter h is the eighth letter of the Latin alphabet. In English it is usually "
                    "pronounced as a voiceless glottal fricative, a breath before the vowel, and")
    ap.add_argument("--new-tokens", type=int, default=20)
    ap.add_argument("--threads", type=int, default=0, help="torch CPU threads (0 = default)")
    args = ap.parse_args()

    torch.manual_seed(0)
    np.random.seed(0)
    if args.threads:
        torch.set_num_threads(args.threads)
    import onnx
    from transformers import AutoTokenizer, FalconH1ForCausalLM

    t_all = time.perf_counter()
    report = {"checkpoint": os.path.abspath(args.checkpoint), "versions": versions(), "opset": args.opset,
              "command": " ".join(sys.argv)}
    print(f"[load] {args.checkpoint}")
    hf = FalconH1ForCausalLM.from_pretrained(args.checkpoint, torch_dtype=torch.float32, attn_implementation="eager").eval()
    tok = AutoTokenizer.from_pretrained(args.checkpoint)
    cfg = hf.config
    n_params = sum(p.numel() for p in hf.parameters())
    report["parameters"] = int(n_params)
    print(f"[load] {cfg.model_type}, {cfg.num_hidden_layers} layers, hidden {cfg.hidden_size}, vocab {cfg.vocab_size}, {n_params:,} params")

    os.makedirs(os.path.join(args.output, "onnx"), exist_ok=True)

    t0 = time.perf_counter()
    model = export_graph(hf, args.opset)
    report["export_s"] = round(time.perf_counter() - t0, 1)
    print(f"[export] torch.onnx.export (TorchScript, opset {args.opset}): {report['export_s']} s, {len(model.graph.node)} nodes")

    if not args.no_slim:
        t0 = time.perf_counter()
        model = slim(model)
        report["slim_s"] = round(time.perf_counter() - t0, 1)
        print(f"[slim] onnxslim: {report['slim_s']} s, {len(model.graph.node)} nodes")
    onnx.checker.check_model(model)
    report["fp32_ops"] = sorted({n.op_type for n in model.graph.node})

    if not args.no_q4:
        t0 = time.perf_counter()
        q4 = quantize_q4(model, args.q4_block_size, args.q4_symmetric, args.q4_accuracy_level, not args.no_q4_embedding)
        report["quantize_s"] = round(time.perf_counter() - t0, 1)
        report["q4"] = {"bits": 4, "block_size": args.q4_block_size, "is_symmetric": args.q4_symmetric,
                        "accuracy_level": args.q4_accuracy_level, "embedding": "q4" if not args.no_q4_embedding else "fp32",
                        "file": "onnx/model_q4.onnx"}
        save_external(q4, os.path.join(args.output, "onnx", "model_q4.onnx"))
        del q4
        print(f"[q4] MatMulNBitsQuantizer 4-bit: {report['quantize_s']} s")

    if not args.no_q8:
        t0 = time.perf_counter()
        q8 = quantize_q8(model, args.q8_block_size, args.q8_embedding)
        report["quantize_q8_s"] = round(time.perf_counter() - t0, 1)
        report["q8"] = {"bits": 8, "block_size": args.q8_block_size, "is_symmetric": False, "accuracy_level": None,
                        "embedding": args.q8_embedding, "file": "onnx/model_quantized.onnx"}
        save_external(q8, os.path.join(args.output, "onnx", "model_quantized.onnx"))
        del q8
        print(f"[q8] MatMulNBitsQuantizer 8-bit + {args.q8_embedding} embedding: {report['quantize_q8_s']} s")

    report["fp32_tied_head_deduped"] = dedupe_tied_head(model)
    save_external(model, os.path.join(args.output, "onnx", "model.onnx"))
    del model

    copy_side_files(args.checkpoint, args.output, {"use_external_data_format": True})

    sizes = {}
    for f in sorted(os.listdir(os.path.join(args.output, "onnx"))):
        sizes[f] = os.path.getsize(os.path.join(args.output, "onnx", f))
    report["sizes_bytes"] = sizes
    for f, s in sizes.items():
        print(f"[size] onnx/{f}: {s / 1e6:.1f} MB")

    if not args.no_verify:
        verify(hf, tok, args.output, args.prompt, args.new_tokens, report, not args.no_q4, not args.no_q8)

    report["total_s"] = round(time.perf_counter() - t_all, 1)
    with open(os.path.join(args.output, "export_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(f"[done] {args.output} in {report['total_s']} s; report in export_report.json")


if __name__ == "__main__":
    main()
