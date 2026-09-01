#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_dir="${script_dir}/sources"
tiny_dir="${source_dir}/tiny_h1_blog"
model_dir="${source_dir}/model_configs"
mkdir -p "${tiny_dir}" "${model_dir}"

tiny_revision="481d65862cd636fad1b6696354e56febc89a8125"
tiny_root="https://huggingface.co/spaces/tiiuae/tiny-h1-blogpost/resolve/${tiny_revision}/app/src/content"

fetch() {
  local url="$1"
  local target="$2"
  if [[ -s "${target}" ]]; then
    return
  fi
  curl --fail --location --retry 3 --retry-delay 2 "${url}" --output "${target}.partial"
  mv "${target}.partial" "${target}"
}

fetch "${tiny_root}/article.mdx" "${tiny_dir}/article.mdx"
fetch "${tiny_root}/chapters/demo/introduction.mdx" "${tiny_dir}/introduction.mdx"
fetch "${tiny_root}/chapters/demo/data-strategy2.mdx" "${tiny_dir}/data_strategy.mdx"
fetch "${tiny_root}/chapters/demo/model-ablation.mdx" "${tiny_dir}/model_ablation.mdx"
fetch "${tiny_root}/chapters/demo/training-approach.mdx" "${tiny_dir}/training_approach.mdx"
fetch "${tiny_root}/chapters/demo/training_algorithm.mdx" "${tiny_dir}/training_algorithm.mdx"
fetch "${tiny_root}/chapters/demo/tiny-h1-sft.mdx" "${tiny_dir}/sft.mdx"
fetch "${tiny_root}/chapters/demo/tiny-h1-agentic.mdx" "${tiny_dir}/agentic.mdx"
fetch "${tiny_root}/chapters/demo/tiny-h1-coder.mdx" "${tiny_dir}/coder.mdx"
fetch "${tiny_root}/chapters/demo/future-work.mdx" "${tiny_dir}/future_work.mdx"
fetch "${tiny_root}/bibliography.bib" "${tiny_dir}/bibliography.bib"

tiny_model_revision="7994372e93b62822ae25f8bfb19f653649cea3a3"
large_model_revision="59fb76e8c5d3fc7441b062be638e1ba0afd5c687"
fetch \
  "https://huggingface.co/tiiuae/Falcon-H1-Tiny-90M-Base/resolve/${tiny_model_revision}/config.json" \
  "${model_dir}/falcon_h1_tiny_90m_base_config.json"
fetch \
  "https://huggingface.co/tiiuae/Falcon-H1-0.5B-Base/resolve/${large_model_revision}/config.json" \
  "${model_dir}/falcon_h1_0.5b_base_config.json"

(
  cd "${source_dir}"
  find . -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 shasum -a 256 \
    > SHA256SUMS
)
