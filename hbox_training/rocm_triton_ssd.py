"""Opt-in Falcon-H1 Mamba-2 Triton scan path for PyTorch ROCm.

The official ``mamba-ssm`` source ships its Mamba-2 SSD kernels as Python/Triton,
but its package build also requires a ROCm development toolchain for unrelated
compiled extensions. This loader consumes an unpacked, pinned source tree and
uses the Triton SSD scan with PyTorch's ordinary depthwise Conv1d. It never
pretends that ``causal-conv1d`` is installed.

This is deliberately an explicit runtime patch. Call it before Falcon-H1's
modeling module is imported, and prove parity on the target machine before use.
"""

from __future__ import annotations

import importlib.machinery
import json
from pathlib import Path
import sys
import types

import torch


MINIMUM_MAMBA_VERSION = (2, 0, 4)


def _version_tuple(raw: str) -> tuple[int, ...]:
    values = []
    for component in raw.split("."):
        digits = "".join(character for character in component if character.isdigit())
        if not digits:
            break
        values.append(int(digits))
    return tuple(values)


def _inject_source_package(source_root: Path):
    package_root = source_root / "mamba_ssm"
    init_path = package_root / "__init__.py"
    ssd_path = package_root / "ops" / "triton" / "ssd_combined.py"
    if not init_path.is_file() or not ssd_path.is_file():
        raise FileNotFoundError(f"Not an unpacked mamba-ssm source root: {source_root}")

    version = None
    for line in init_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            version = line.split("=", 1)[1].strip().strip('"\'')
            break
    if version is None or _version_tuple(version) < MINIMUM_MAMBA_VERSION:
        raise RuntimeError(f"mamba-ssm {version!r} is older than 2.0.4")

    # The source distribution contains valid metadata beside the package. Put
    # it on sys.path so Transformers can verify the version without executing
    # mamba_ssm.__init__, which imports optional compiled extensions.
    sys.path.insert(0, str(source_root))
    package = types.ModuleType("mamba_ssm")
    package.__path__ = [str(package_root)]
    package.__version__ = version
    package.__spec__ = importlib.machinery.ModuleSpec(
        "mamba_ssm", loader=None, is_package=True
    )
    package.__spec__.submodule_search_locations = package.__path__
    sys.modules["mamba_ssm"] = package
    return package


def enable_rocm_triton_ssd(source_root: Path) -> dict:
    """Patch Falcon-H1 mixers to use Mamba-2's Triton scan on ROCm."""

    if torch.version.hip is None or not torch.cuda.is_available():
        raise RuntimeError("The ROCm Triton SSD path requires a visible PyTorch ROCm GPU")
    source_root = source_root.expanduser().resolve()
    existing = sys.modules.get("mamba_ssm")
    if existing is None:
        package = _inject_source_package(source_root)
    else:
        package = existing

    from mamba_ssm.ops.triton.ssd_combined import mamba_chunk_scan_combined

    import transformers.models.falcon_h1.modeling_falcon_h1 as falcon_h1

    falcon_h1.mamba_chunk_scan_combined = mamba_chunk_scan_combined
    mixer_class = falcon_h1.FalconH1Mixer
    if getattr(mixer_class, "_hghost_rocm_triton_enabled", False):
        return {
            "enabled": True,
            "already_enabled": True,
            "mamba_ssm": package.__version__,
            "source_root": str(source_root),
        }

    reference_forward = mixer_class.torch_forward

    def rocm_triton_forward(
        self,
        hidden_states,
        cache_params=None,
        cache_position=None,
        attention_mask=None,
    ):
        # The stepwise Triton path has no causal_conv1d_update replacement.
        # Preserve the reference implementation for one-token cached decoding.
        if (
            cache_params is not None
            and cache_params.has_previous_state
            and hidden_states.shape[1] == 1
        ):
            return reference_forward(
                self, hidden_states, cache_params, cache_position, attention_mask
            )

        # cuda_kernels_forward's non-training branch performs the ordinary
        # grouped Conv1d and calls mamba_chunk_scan_combined for SSD. Temporarily
        # selecting it avoids the fused split-conv kernel, which depends on the
        # unavailable causal-conv1d C++/HIP extension. This mixer contains no
        # dropout or other train/eval-dependent operation.
        was_training = self.training
        self.training = False
        try:
            return self.cuda_kernels_forward(
                hidden_states,
                cache_params=cache_params,
                cache_position=cache_position,
                attention_mask=attention_mask,
            )
        finally:
            self.training = was_training

    mixer_class.forward = rocm_triton_forward
    mixer_class._hghost_rocm_triton_enabled = True
    report = {
        "enabled": True,
        "already_enabled": False,
        "mamba_ssm": package.__version__,
        "source_root": str(source_root),
        "torch": torch.__version__,
        "hip": torch.version.hip,
        "triton": __import__("triton").__version__,
        "convolution": "torch grouped Conv1d",
        "scan": "mamba_ssm.ops.triton.ssd_combined.mamba_chunk_scan_combined",
    }
    print(json.dumps({"event": "rocm_triton_ssd_enabled", **report}), flush=True)
    return report
