# H-Ghost research bundle

This directory turns the September 2026 literature sweep into a reproducible reading bundle and an
experiment queue. It deliberately separates evidence from extrapolation: most of the interesting papers
were not run on Falcon-H1, on continued pretraining, or on a 90M model.

## Contents

- [`plan.md`](plan.md): the staged project plan and decision gates.
- [`claims_audit.md`](claims_audit.md): what the cited work actually supports, and what remains a hypothesis.
- [`bibliography.json`](bibliography.json): machine-readable metadata for the selected references.
- [`papers/`](papers/): 22 primary-source PDFs plus SHA-256 checksums.
- [`sources/`](sources/): pinned official Falcon-H1 model configs and the source chapters of TII's Tiny-H1 blog.
- [`results/hbox-cpt-10m.md`](results/hbox-cpt-10m.md): first-checkpoint validation, generations, and BF16 update-resolution diagnosis.
- [`results/hbox-rocm-triton.md`](results/hbox-rocm-triton.md): parity and full-model throughput evidence for the experimental AMD Triton SSD path.
- [`download_papers.sh`](download_papers.sh): idempotent paper downloader.
- [`download_primary_sources.sh`](download_primary_sources.sh): idempotent official-source downloader.

The two download scripts pin arXiv IDs and Hugging Face revisions. Verify the bundle with:

```bash
(cd research/papers && shasum -a 256 -c SHA256SUMS)
(cd research/sources && shasum -a 256 -c SHA256SUMS)
```

## Source pins

- Falcon-H1-Tiny-90M-Base: `7994372e93b62822ae25f8bfb19f653649cea3a3`
- Falcon-H1-0.5B-Base: `59fb76e8c5d3fc7441b062be638e1ba0afd5c687`
- Tiny-H1 official blog source: `481d65862cd636fad1b6696354e56febc89a8125`
- Local GLaDOS source: `/Users/ember/dev/clairnets`, inspected at
  `ffe2faef5e0c29a78e711c7f97c13d97435ad9be` on branch `dev`

The local `clairnets` checkout has user changes. This project treats it as read-only and does not vendor or
modify it.
