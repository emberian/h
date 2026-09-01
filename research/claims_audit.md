# Claims audit

The status labels mean:

- **direct**: the cited primary source tests substantially the stated claim;
- **extrapolation**: real result, but the H-Ghost application changes model, objective, scale, or regime;
- **open**: a worthwhile hypothesis with no direct evidence yet;
- **correction**: the synthesis needs a factual or operational adjustment.

| Claim | Status | Audit and project decision |
|---|---|---|
| Falcon-H1-0.5B fits a 500 MB deployment budget. | direct | Official Instruct GGUF files are 315 MB Q4_K_M, 371 MB Q5_K_M, and 430 MB Q6_K. A new CPT checkpoint still needs conversion and browser profiling. |
| The 0.5B model has 0.52B parameters, 36 layers, width 1024, 16K base context, and 2.5T pretraining tokens. | direct | The 2025 technical report gives these values. The pinned Base config agrees on shape and 16K context. |
| The 0.5B vocabulary is 32,778. | correction | The report table says 32,778 and its tokenizer table says 32,768, while the pinned official Base config currently says 32,784. Use the pinned executable config for code and record the mismatch. |
| Tiny inherited about 800B tokens. | direct | TII's pinned blog source specifies an 800 GT training duration for the main 90M Base/Instruct recipe. |
| TII's Tiny scratch hyperparameters should be reused for CPT. | correction | The 0.00256 LR, 4M-token batch, Muon/LRM, and 800B-token WSD schedule are a from-scratch recipe. They are not safe defaults for short CPT. |
| MIR is worth about 1.3× unique data. | direct with narrow scope | SoftQ estimates 1.28×–1.34× in the paper's 200M–400M from-scratch regime. It is not a demonstrated H1 CPT multiplier. |
| MIR has no inference overhead. | direct | It does not alter the inference architecture. Training adds a masked auxiliary loss and roughly doubles model arithmetic if clean and masked copies are both evaluated. |
| MIR should be the main TPU run. | extrapolation | The smallest 72M models gained only about 0.006 validation loss on average; downstream gains were shown at 1.4B. Run a bounded wall-clock A/B after baseline CPT. |
| Sharpness-disparity blockwise LR can nearly double training speed. | direct for GPT/LLaMA scratch training | The paper reports about 1.9×–2× fewer steps to matched loss. It does not study H1's SSM/conv groups or CPT. Measure H1 group geometry before changing the optimizer. |
| Edge-of-stability theory tells us the optimal H1 learning rate. | correction | The paper supplies a dynamical/generalization analysis and sharpness dimension, not an AdamW-H1 tuning recipe. Use it to motivate measurements, not instability-seeking. |
| Flatter pretraining checkpoints can retain capabilities better after posttraining and quantization. | direct, then extrapolation | Demonstrated on 20M–150M OLMo-style models and an OLMo-2-1B midtraining branch. Preserve flat-candidate versus cooled H1 checkpoints for a cheap replication. |
| Late SAM is almost free. | correction | SAM roughly doubles the steps on which it is used. Restricting it to a 10% anneal adds about 10% total compute in the cited setup; it is cheap relative to full-run SAM, not free. |
| Four recurrences turn 30M stored parameters into a free 120M model. | correction | The recurrence-equivalence exponent is about 0.46 in the cited sweep. Recurrence trades training/inference compute for storage and can lose at iso-FLOPs. |
| Gated recurrence can match GPT-2 Small with about 35M parameters. | direct but very fresh | The August 2026 preprint reports 3.14 versus 3.15 validation loss at iso-FLOPs after about 9.8B tokens. It needs independent replication and is not an H1 result. |
| MixerLoop is the compute-rational recurrence variant. | extrapolation | Its very recent 15M/110M experiments show useful gains with fewer recurrent projection FLOPs, but it uses Gated DeltaNet rather than Falcon-H1. |
| Bulk synthetic prose should expand this high-quality corpus. | correction | EntiGraph and instruction pretraining are real, but wholesale rewriting risks teacher-style contamination. Use source-grounded labels, relations, tasks, and small separately measured mixtures. |
| Tiny-H1 responds strongly to DPO. | direct | TII reports a large IFEval gain and degradation after more than one epoch even as DPO reward rises. Aesthetic DPO is still an extrapolation requiring H-Ghost preferences. |
| Persona or emotion vectors are likely discoverable in a 90M domain model. | open | Persona vectors causally steer larger models. A developmental 90M replication is attractive and cheap, but neither scale transfer nor vector identifiability is guaranteed. |
| DPO can induce introspection. | disputed/extrapolation | The positive paper finds internal-perturbation detection after DPO in much larger models. The Reality Check shows anomaly/input-cue and relabeling confounds. Use the stronger controls and call it internal-state monitoring. |
| RL-trained steering vectors can replace full fine-tuning. | direct in tested reasoning settings, extrapolation here | The cited work matches full fine-tuning in its tasks with tiny additive interventions. H-Ghost needs a meaningful aesthetic or source-grounded reward first. |
| Offline top-K KD makes 0.5B→90M cheap. | correction | It removes the online teacher and improves step throughput, but top-100 caches are storage-heavy. The full corpus is roughly 224.6 GB at six bytes per retained entry before overhead. |
| GLaDOS already supports H1. | correction | The local repo proves a model-agnostic residual graft on seven hosts, including a Mamba-2 hybrid, but Falcon-H1 itself is not in the matrix. An H1 no-op/parity smoke is required. |
| A GLaDOS verifier can guarantee philosophical argument correctness. | correction | It can certify operations relative to compiled formal structure. It cannot guarantee that α compiled the correct claim graph from prose; the local docs explicitly identify that boundary. |
| Weight-sparse Transformers are a near-term better ghost. | extrapolation | OpenAI shows much more legible controlled-task circuits with a capability/interpretability tradeoff. This is a later interpretability sibling, not the main language model. |
| A model this small can accept visual input. | direct | SmolVLM-256M is an existence proof and uses a 93M SigLIP encoder; the official release includes WebGPU/ONNX and MLX paths. H1 integration is still new work. |
| Visual input necessarily improves language generalization and concept acquisition. | open/mixed | Some studies report text-only gains from visual grounding; controlled lexical-grounding work finds no significant advantage. Use caption-only and unrelated-image controls and test text-only transfer. |
