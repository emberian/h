# Compute we can get (read 2026-09-03; prices and programs as found via Kagi and the providers' pages)

Ranked by how much they change what h can be, given a $100 budget on top.

1. **TPU Research Cloud (TRC), Google — free Cloud TPUs, apply.** sites.research.google/trc. Free TPU quota granted to
   a GCP project on a temporary (renewable) basis; requirements: share the work publicly (papers, open source, blog
   posts) and give feedback. Participants pay only the small driver VM (n1-standard-2) and storage: "generally minimal".
   Our JAX stack (h1jax) is exactly a TPU stack; a TRC v5e or v6e pod removes the 20 h/week cap and makes the 1.5B (and a
   3B/7B) trainable at full epochs. Application: a short form describing the research; approval is rolling.
   Also: the "2026 Google TPU Research & Education Awards" (funding + TPUs), announced on LinkedIn by Josh Gordon.
2. **Lightning AI free tier — up to 80 free GPU hours to start, then ~22 GPU-hours/month** (15 monthly credits) on
   T4/L4/A10G/L40S; no card. An L40S (48 GB) covers the 0.5B RL/self-distillation rounds and a 4-bit 27B QLoRA at seq
   1024. lightning.ai/pricing. Free Studios need a restart every 4 h.
3. **Modal — $30/month free credits, serverless**: H100 $3.95/h, A100 80 GB $2.50/h -> 8-12 free GPU hours a month, on
   demand, no instance babysitting; ideal for audits/rollouts as jobs. modal.com/pricing.
4. **Lambda research credits — up to $5,000 for "qualifying researchers", work showcased**: lambda.ai/research; an
   application with the h write-up, site and repo. Worth a try; the bar is a research narrative, which we have.
5. **CloudRift AI grant — $100-$1,000 GPU credits, rolling, for independent builders** (grantedai.com listing).
6. **Marketplaces for the H100 day**: Vast.ai (H100 SXM from $1.33/h, median $2.39), Lium ($1.30 confirmed in stock on
   2026-08-29 per gpufinder.dev), RunPod community (~$2.49; a 2026 review counted 227 outages in nine months), Spheron
   (A100 80 GB $1.07 on-demand). The $100 buys ~40-70 H100 hours here.
7. **What we already have**: Kaggle 30 GPU h/week (T4) + 20 TPU h/week (v5e-8, 9 h sessions); Colab free (T4, 12 h
   cap, dynamic); the Mac (103 GB, MLX serving; training blocked by the display watchdog); hbox (12 GB).
8. **Not useful for training**: HF ZeroGPU (inference demos, reservation-based minutes), Google Cloud $300 new-user
   credits (GPU/TPU quota approvals are slow and often denied for new projects), NAIRR/NSF (academic affiliation).

Plan: apply to TRC today (form + the h blog/site + repo as the public-sharing plan); sign up for Lightning and Modal
(free, immediate: covers RL rounds and audits); book one H100 SXM day on Vast/Lium (~$30) for the 1.5B epoch + the 27B
adapter once gpu/RUNBOOK.md's scripts pass their T4 tests; apply to Lambda credits with the same write-up.
