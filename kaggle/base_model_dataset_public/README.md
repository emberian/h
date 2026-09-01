---
library_name: transformers
tags:
- falcon-h1
- edge
license: other
license_name: falcon-llm-license
license_link: https://falconllm.tii.ae/falcon-terms-and-conditions.html
---

<img src="https://cdn-uploads.huggingface.co/production/uploads/62441d1d9fdefb55a0b7d12c/l1du02RjuAZJcksI5tQ-F.png" alt="drawing" width="800"/>

#  Table of Contents

0. [TL;DR](#TL;DR)
1. [Model Details](#model-details)
2. [Training Details](#training-details)
3. [Usage](#usage)
4. [Evaluation](#evaluation)
5. [Citation](#citation)

# TL;DR

# Model Details

## Model Description

- **Developed by:** [https://www.tii.ae](https://www.tii.ae)
- **Model type:** Causal decoder-only
- **Architecture:** Hybrid Transformers + Mamba architecture
- **Language(s) (NLP):** English
- **Number of Parameters:** 90M
- **License:** Falcon-LLM License

# Training details

For more details about the training protocol of this model, please refer to the [Falcon-H1-Tiny technical blogpost](https://huggingface.co/spaces/tiiuae/tiny-h1-blogpost).

# Usage

Currently to use this model you can either rely on Hugging Face `transformers`, `vLLM`, `sglang`, `llama.cpp`, `ollama` or `mlx` library.

## Inference

### 🤗 transformers

Refer to the snippet below to run H1 models using 🤗 transformers:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "tiiuae/Tiny-H1-SFT"

model = AutoModelForCausalLM.from_pretrained(
  model_id,
  torch_dtype=torch.bfloat16,
  device_map="auto"
)

# Perform text generation
```

or

```bash
transformers serve tiiuae/Tiny-H1-SFT
```

### `llama.cpp`

You can find all GGUF files compatible with `llama.cpp` under [our official collection]() - an example setup could be:

```bash
brew install llama.cpp 
pip install huggingface_hub 
hf download tiiuae/Tiny-H1-SFT tiny-h1-sft-pretrain-Q8_0.gguf --local-dir ./ 
llama-cli ./ Tiny-H1-SFT-Q8_0.gguf -cnv 
```

### `ollama`

```bash
ollama run hf.co/tiiuae/Tiny-H1-SFT:Q8_0 
```

### Apple `mlx` 

```bash
mlx_lm.chat --model tiiuae/Tiny-H1-SF 
```

### vLLM

For vLLM, simply start a server by executing the command below:

```bash
# pip install vllm>=0.9.0
vllm serve tiiuae/Tiny-H1-SFT --tensor-parallel-size 2 --data-parallel-size 1
```

### sglang

```bash
python -m sglang.launch_server \
  --model ttiiuae/Tiny-H1-SFT \
  --tensor-parallel-size 1 
```

# Evaluation

For detailed evaluation of Falcon-H1-Tiny series, please refer to our [technical blogpost](https://huggingface.co/spaces/tiiuae/tiny-h1-blogpost)

# Useful links

- View [our release blogpost](https://huggingface.co/spaces/tiiuae/tiny-h1-blogpost).
- Feel free to join [our discord server](https://discord.gg/trwMYP9PYm) if you have any questions or to interact with our researchers and developers.

# Citation

If the Falcon-H1-Tiny family of models were helpful to your work, feel free to give us a cite.

```
@misc{falcon_h1_tiny,
  title={Falcon-H1-Tiny: A series of extremely small, yet powerful language models redefining capabilities at small scale},
  author={Falcon-LLM Team},
  year={2026}, 
}
```