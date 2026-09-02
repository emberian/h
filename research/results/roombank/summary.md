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
