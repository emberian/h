# Optional fresh 10M + 20M TPU job

This is a parked optional wrapper for sequential random-init training of the
9,856,488-parameter and 19,511,990-parameter Falcon-H1-derived models. Both use
the same sealed 8,192-token corpus-native BPE stream and receive 300M token
exposures.

The primary production target is `kaggle/tpu_fresh_91m`. Do not push this
optional kernel until the final private corpus dataset has been
uploaded, downloaded again, hash-verified, and the CPU-mode wrapper preflight
has passed against that downloaded copy. A successful CPU preflight is not
authorization to launch the TPU kernel.
