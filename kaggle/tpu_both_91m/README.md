# H Ghost 91M TPU experiments

One Kaggle TPU v5e-8 allocation executes three fail-closed phases in order:

1. exact 91,131,072-parameter, two-update hardware smoke;
2. Falcon-H1 91M continued pretraining over one 374,405,120-token pass;
3. Falcon-H1 91M random-init pretraining over two passes (748,810,240 tokens).

Every phase requires eight TPU devices and sealed/hash-verified inputs. The CPT
phase also runs the pinned checkpoint-parity fixture at high SSD precision.
Training uses native TPU BF16 contractions with FP32 accumulation. Any failure
prevents later phases from starting.
