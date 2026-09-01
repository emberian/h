# persvati LoRA control

This job applies rank-16, alpha-32 LoRA adapters to every PEFT-compatible linear
projection inside Falcon-H1's 24 hybrid blocks while excluding the tied
language-model head. That covers attention q/k/v/o, Mamba input, and all MLP
projections: 3,597,312 trainable parameters, about 3.95% of the 91M base. PEFT
explicitly rejects Mamba's `out_proj` for this model type, so it remains frozen
with the rest of the base. Base and adapter parameters remain BF16. The job
consumes exactly the same sealed stock-tokenizer stream and checkpoints at the
same token exposures as hbox full CPT.

The sealed bundle is installed and SHA-256 verified on Persvati:

```bash
source /home/ember/h1-distributed/env.sh
python /home/ember/h1-distributed/scripts/train_lora.py \
  --model-dir "$H1_MODEL_DIR" \
  --corpus-dir /home/ember/h1-distributed/data/corpus-v1 \
  --output /home/ember/h1-distributed/checkpoints/lora-v1 \
  --rank 16 --alpha 32 --sequence-length 512 \
  --batch-size 1 --accumulation-steps 4 --total-tokens 374405120 \
  --warmup-tokens 3000000 --learning-rate 0.0003 \
  --save-tokens 10000000,30000000,100000000,300000000,374405120
```

The LR is provisional until a short real-data loss/throughput pilot is complete.
