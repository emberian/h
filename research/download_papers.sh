#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
paper_dir="${script_dir}/papers"
mkdir -p "${paper_dir}"

download() {
  local arxiv_id="$1"
  local filename="$2"
  local target="${paper_dir}/${filename}"

  if [[ -s "${target}" ]]; then
    return
  fi

  curl --fail --location --retry 3 --retry-delay 2 \
    "https://arxiv.org/pdf/${arxiv_id}" \
    --output "${target}.partial"
  mv "${target}.partial" "${target}"
}

# Mainline architecture and finite-data training.
download 2507.22448 falcon_h1_2507.22448.pdf
download 2606.06888 masked_input_regularization_2606.06888.pdf

# Learning mechanics and post-training plasticity.
download 2604.19740 generalization_edge_of_stability_2604.19740.pdf
download 2502.19002 sharpness_disparity_2502.19002.pdf
download 2605.02105 sharpness_aware_pretraining_2605.02105.pdf
download 2604.13627 learning_rates_catastrophic_overtraining_2604.13627.pdf

# Activation steering, interpretability, and controlled internal-state tests.
download 2507.21509 persona_vectors_2507.21509.pdf
download 2509.06608 rl_trained_steering_vectors_2509.06608.pdf
download 2603.21396 introspective_awareness_2603.21396.pdf
download 2605.26242 introspection_reality_check_2605.26242.pdf

# Parameter reuse / recurrence research branch.
download 2604.21106 recurrence_equivalence_2604.21106.pdf
download 2608.18230 mixerloop_2608.18230.pdf
download 2608.15062 gated_recurrent_transformers_2608.15062.pdf

# Corpus-derived supervision, distillation, and evaluation signals.
download 2409.07431 synthetic_cpt_entigraph_2409.07431.pdf
download 2406.14491 instruction_pretraining_2406.14491.pdf
download 2608.03796 offline_topk_distillation_2608.03796.pdf
download 2602.04649 rationale_consistency_2602.04649.pdf

# Generation-two tokenizer research.
download 2605.01188 compute_optimal_tokenization_2605.01188.pdf

# Later-week multimodal grounding branch and its strongest caution.
download 2504.05299 smolvlm_2504.05299.pdf
download 2109.10246 visual_language_lexical_grounding_2109.10246.pdf
download 2103.13942 visual_grounding_text_only_nlp_2103.13942.pdf

# OpenAI's source is a stable primary-source PDF rather than an arXiv item.
weight_sparse_target="${paper_dir}/weight_sparse_transformers_openai_2025.pdf"
if [[ ! -s "${weight_sparse_target}" ]]; then
  curl --fail --location --retry 3 --retry-delay 2 \
    "https://cdn.openai.com/pdf/41df8f28-d4ef-43e9-aed2-823f9393e470/circuit-sparsity-paper.pdf" \
    --output "${weight_sparse_target}.partial"
  mv "${weight_sparse_target}.partial" "${weight_sparse_target}"
fi

(
  cd "${paper_dir}"
  shasum -a 256 ./*.pdf > SHA256SUMS
)
