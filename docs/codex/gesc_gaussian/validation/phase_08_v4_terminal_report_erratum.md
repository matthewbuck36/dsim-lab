# Phase 08.4 Terminal Report Erratum

The generated Phase 08.4 terminal artifacts correctly report:

- outcome `FAIL`;
- activation gate `0/10`;
- no frozen contract;
- development, holdout, validation, and reproducibility `NOT RUN`;
- `simulation_ready=false`.

Two generic-engine diagnostics in those immutable generated artifacts are
mislabelled:

1. missing-stage messages say `v3` although the selected workflow identity is
   `phase08-v4`;
2. the generic terminal checker expects a legacy `transaction_path` field in
   the V4 prepare state, although the separately validated V4 population
   adoption/prepare contract passed without that legacy field.

These reporting defects do not alter the terminal outcome. The independently
retained V4 states prove that prepare and qualification passed, while the
corrected activation failed its first predeclared lifecycle contract and
stopped before every later stage.

Authoritative evidence:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b/workflow_state/v4_prepare.json
  internal state SHA-256:
  0663ac27b7b4882dda4474600ff6e98d4170391f1197c40e943fd747f3225c5e

/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b/workflow_state/v4_qualification.json
  internal state SHA-256:
  8921133fd8aca49d83f9dcc51c02be441362dea2adcfcbc1927848fdbb8947ed

/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b/workflow_state/v4_activation.json
  internal state SHA-256:
  6d11fe4fa8013b83d663e40db3fbe2f4791b9c5af5d6ad1d6b6010196b1ecd3d
```

The generated artifacts remain byte-for-byte retained and are not rewritten
by this erratum.
