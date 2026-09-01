# hbox production CPT

> **Status, September 1, 2026:** interrupted after the first durable 10M-token checkpoint. The checkpoint
> is scientifically useful, but this exact recipe should not be resumed: Transformers used the naive Mamba
> fallback, while model parameters and both AdamW moments were BF16. See the
> [10M comparison](../research/results/hbox-cpt-10m.md) for validation, generation, and parameter-delta
> evidence. The replacement path must use an independently parity-tested SSD kernel and FP32 master
> parameters/moments with BF16 compute.

The experimental replacement is isolated and opt-in:

- [`rocm_triton_ssd.py`](rocm_triton_ssd.py) loads the pinned upstream Mamba-2 Python/Triton SSD scan while
  retaining PyTorch's grouped Conv1d;
- [`validate_rocm_triton.py`](validate_rocm_triton.py) compares mixer outputs, input gradients, and every
  parameter gradient with Transformers' reference implementation before training;
- `train_hbox.py` defaults to FP32 master parameters/moments and requires an explicit
  `--rocm-triton-mamba-root` to select the experimental scan.

On the first hbox probe, the standalone SSD forward/backward took 395 seconds to compile and autotune, then
2.8 ms warm. The layer-level reference comparison at sequence 256 had 0.266% relative mean output error,
0.235% input-gradient error, matching gradient keys, and at most 0.374% relative mean error among parameter
gradients. Full-model real-token smokes then reached 2,259–2,365 tokens/s at batch 1 × sequence 512, with
2.20 GiB peak allocated memory. See the [ROCm Triton report](../research/results/hbox-rocm-triton.md).

This production loop consumes the same hash-sealed `uint16` corpus bundle as
the JAX/Kaggle job. It keeps model parameters and AdamW moments in FP32 while
running forward/backward compute under BF16 autocast, traverses aligned
sequences in a deterministic permutation, evaluates a disjoint document split,
and writes atomic Hugging Face checkpoints with resumable AdamW state. Layer
rematerialization is available as an opt-in flag for longer sequences; it is
unnecessary at sequence 512 on this 90M model.

The final corpus is on the SSD at
`/othersys/h1-ghost/data/corpus-v1`; the bundle is under 1 GB and random reads
from `/tank` would unnecessarily bottleneck the GPU.

The copied bundle hashes match its sealed upload manifest:

```bash
source /home/hbox/h1-ghost/env.sh
python /home/hbox/h1-ghost/scripts-v2/train_hbox.py \
  --model-dir "$H1_MODEL_DIR" \
  --corpus-dir /othersys/h1-ghost/data/corpus-v1 \
  --output /othersys/h1-ghost/checkpoints/full-cpt-triton-fp32-v1 \
  --parameter-dtype float32 \
  --rocm-triton-mamba-root \
    /othersys/h1-ghost/kernel-test/mamba-source/mamba_ssm-2.3.2.post1 \
  --sequence-length 512 --batch-size 1 --accumulation-steps 4 \
  --total-tokens 374405120 --warmup-tokens 3000000 \
  --learning-rate 0.00006 \
  --save-tokens 10000000,30000000,100000000,300000000,374405120
```

The best corrected smoke held 2,259–2,365 tokens/s, projecting roughly 44–46
compute hours for the sealed 374,405,120-token pass before sparse evaluation
and checkpoint overhead. Treat that command as a reproducible proposed branch,
not an instruction to launch it unattended yet: first pass checkpoint
save/reload parity and a longer finite-loss smoke. The old `full-cpt-v1`
checkpoint remains intact as the 10M-token developmental specimen.
