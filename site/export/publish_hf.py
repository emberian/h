"""Publish an exported ONNX model directory to the Hugging Face Hub for the site to load.

usage: .venv-onnx/bin/python site/export/publish_hf.py <exported dir> <repo id> [--private]

Uploads the directory produced by export_onnx.py (config, tokenizer files, onnx/*) together with the
Falcon license, acceptable-use policy, and redistribution notice from the public base-model staging
directory, plus a short model card naming the source checkpoint. The site then loads it with
`model.id = "<repo id>"`, `localPath: null`, `dtype: "q8"`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[2]
LICENSE_DIR = ROOT / "kaggle" / "base_model_dataset_public"
LICENSE_FILES = ("FALCON_LICENSE.html", "FALCON_ACCEPTABLE_USE_POLICY.html", "REDISTRIBUTION_NOTICE.md")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exported", type=Path)
    parser.add_argument("repo_id")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--source", default="", help="description of the source checkpoint for the card")
    args = parser.parse_args()

    exported = args.exported.resolve()
    if not (exported / "onnx").is_dir() or not (exported / "config.json").is_file():
        raise SystemExit(f"{exported} does not look like an export_onnx.py output")
    manifest = {}
    if (exported / "export_report.json").is_file():
        manifest = json.loads((exported / "export_report.json").read_text())

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "repo"
        shutil.copytree(exported, staging)
        for name in LICENSE_FILES:
            source = LICENSE_DIR / name
            if source.is_file():
                shutil.copy2(source, staging / name)
        card = f"""---
license: other
license_name: falcon-llm-license
license_link: https://falconllm.tii.ae/falcon-terms-and-conditions.html
base_model: tiiuae/Falcon-H1-Tiny-90M-Base
library_name: transformers.js
tags: [onnx, falcon-h1, h-ghost]
---

# {args.repo_id}

ONNX export of a Falcon-H1-Tiny checkpoint from the `h` project (https://github.com/emberian/h), produced by
`site/export/export_onnx.py` for transformers.js 4.x. Source checkpoint: {args.source or "see export_report.json"}.

Files: `onnx/model.onnx` (fp32) and `onnx/model_quantized.onnx` (8-bit MatMulNBits + 8-bit block-quantized
embedding; near-lossless for this model). The 4-bit variant, if present, is provided for comparison only:
4-bit round-to-nearest degrades this 90M model badly.

Derived from `tiiuae/Falcon-H1-Tiny-90M-Base` under the Falcon-LLM License; the license, acceptable-use
policy, and redistribution notice are included in this repository.

```js
const model = await AutoModelForCausalLM.from_pretrained("{args.repo_id}", {{ dtype: "q8", device: "webgpu" }});
```

Export manifest: `{json.dumps(manifest)[:800]}`
"""
        (staging / "README.md").write_text(card)
        api = HfApi()
        api.create_repo(args.repo_id, private=args.private, exist_ok=True)
        api.upload_folder(folder_path=str(staging), repo_id=args.repo_id, commit_message="Upload ONNX export")
        print(f"https://huggingface.co/{args.repo_id}")


if __name__ == "__main__":
    main()
