# Room bank results

Context lift per model and evaluator (`hghost-roombank lift`); rows are shuffleable replies only (states with at least two preceding turns; a state with exactly two has one alternative order, so its shuffles coincide). Per-reply tables, JSON, and scatters sit beside each model's `replies.jsonl`.

Commands (from the repo root, main venv):

- `hghost-roombank build [--seed N]` rebuilds the hidden bank and its public summary;
- `hghost-roombank sample --model h-05b-room-e2v3 --port 8124 --samples 4` samples a served model (resumable);
- `hghost-roombank lift --model h-05b-room-e2v3 --evaluator 91m` scores under the 91M library leaf (minutes);
- `hghost-roombank lift --model h-05b-room-e2v3 --evaluator 05b --batch 4` scores under the 0.5B room checkpoint (2 GB float32 on CPU; budget an hour or more, results cached per row);
- `hghost-roombank pairs --a <model> --b <model> --mode sample --sample-a 0 --sample-b 0` writes a blind sheet under `pairs/` with its answer key.

| model | evaluator | n | mean lift | median | lift>0 | lift/token | novelty | ov. samples | echo | greedy mean lift | sample mean lift |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h-05b-room-e2v3 | leaf-s1-e4-decay10 | 389 | +0.318 | +0.285 | 0.61 | +0.0252 | 0.470 | 0.478 | 0.34 | +0.391 | +0.300 |
| h-05b-room-e2v3 | room05b-e2-v3-decay10 | 389 | +2.458 | +1.803 | 0.77 | +0.1708 | 0.470 | 0.478 | 0.34 | +2.307 | +2.496 |
| h-05b-room-e2v4 | leaf-s1-e4-decay10 | 390 | +0.211 | +0.189 | 0.58 | +0.0263 | 0.451 | 0.447 | 0.39 | +0.004 | +0.262 |
| h-05b-room-e2v4 | room05b-e2-v3-decay10 | 390 | +0.469 | +0.497 | 0.59 | +0.0552 | 0.451 | 0.447 | 0.39 | +0.913 | +0.358 |
| h-05b-w-honly | leaf-s1-e4-decay10 | 390 | +0.363 | +0.232 | 0.60 | +0.0239 | 0.469 | 0.465 | 0.35 | +0.441 | +0.343 |
| h-05b-w-honly | room05b-e2-v3-decay10 | 390 | +0.639 | +0.802 | 0.66 | +0.0725 | 0.469 | 0.465 | 0.35 | +0.620 | +0.644 |
| h-05b-w-hup | leaf-s1-e4-decay10 | 390 | -5.956 | +0.108 | 0.53 | -0.3140 | 0.492 | 0.468 | 0.32 | -6.028 | -5.938 |
| h-05b-w-hup | room05b-e2-v3-decay10 | 390 | +1.056 | +1.083 | 0.70 | +0.0948 | 0.492 | 0.468 | 0.32 | +1.384 | +0.974 |
| h-05b-w-roomdown | leaf-s1-e4-decay10 | 390 | +0.520 | +0.347 | 0.64 | +0.0403 | 0.469 | 0.468 | 0.37 | +0.518 | +0.520 |
| h-05b-w-roomdown | room05b-e2-v3-decay10 | 390 | +1.146 | +0.872 | 0.67 | +0.0759 | 0.469 | 0.468 | 0.37 | +1.536 | +1.048 |
