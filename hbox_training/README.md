# hbox production CPT

This production loop consumes the same hash-sealed `uint16` corpus bundle as
the JAX/Kaggle job. It trains the checkpoint in its native BF16 parameter dtype,
traverses aligned sequences in a deterministic permutation, evaluates a
disjoint document split, and writes atomic Hugging Face checkpoints with
resumable AdamW state. Layer rematerialization is available as an opt-in flag
for longer sequences; it is unnecessary at sequence 512 on this 90M model.

The final corpus is on the SSD at
`/othersys/h1-ghost/data/corpus-v1`; the bundle is under 1 GB and random reads
from `/tank` would unnecessarily bottleneck the GPU.

The copied bundle hashes match its sealed upload manifest:

```bash
source /home/hbox/h1-ghost/env.sh
python /home/hbox/h1-ghost/scripts/train_hbox.py \
  --model-dir "$H1_MODEL_DIR" \
  --corpus-dir /othersys/h1-ghost/data/corpus-v1 \
  --output /othersys/h1-ghost/checkpoints/full-cpt-v1 \
  --sequence-length 512 --batch-size 1 --accumulation-steps 4 \
  --total-tokens 374405120 --warmup-tokens 3000000 \
  --learning-rate 0.00006 \
  --save-tokens 10000000,30000000,100000000,300000000,374405120
```

The exact production loop held 484.7–486.4 tokens/s across nine warmed
sequence-512 updates, implying roughly 8.9 days for the sealed 374,405,120-token
pass before sparse evaluation and checkpoint overhead.
