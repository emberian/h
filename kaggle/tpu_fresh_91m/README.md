# Fresh full-size 91M TPU job

This is the primary gated production wrapper. It trains the exact stock
91,131,072-parameter Falcon-H1 architecture from random initialization on the
stock-tokenized curated corpus for 300M token exposures.

All eight TPU v5e cores participate in synchronous data parallelism through
`jax.pmap`; each core receives distinct examples and gradients are averaged by
`jax.lax.pmean`. The initial production setting is four 512-token sequences per
core, giving a 16,384-token global batch and 18,311 optimizer steps.

Do not push a TPU kernel version until the final private corpus dataset and JAX
wheel have been uploaded, downloaded again, hash-verified, and all local/CPU
gates pass. A successful preflight is not authorization to launch the TPU.
