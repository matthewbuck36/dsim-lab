# R1 measured-development boundary

2026-09-10 UTC. The strategy revision is implemented through usable retained-data
measurements and bounded analysis/observability corrections. Research qualification
and the integrated behavior goals remain open. Authority:
[method/development amendment](../method_development_20260910.md).

- **Detector:** [R1 measured result](r1_detector_diagnostic.md). Current W6
  two-block detects9/11 prescribed positives and1/17 negatives; W3 sensitivity
  detects7/11 positives and7/17 negatives. Both fail the fixed control set.
  Retained B has54 distinct complete supports and no eligible detection.
  Original command's final stdout serialization failed after all numerical
  artifacts were written; a separate read-only audit verifies those complete
  artifacts, with no numerical rerun or historical promotion.
- **Direction:** [R1 measured result](r1_direction_diagnostic.md). New diagnostic
  of saved V9 development C completes in11.944s:24 scheduled targets,12 exposed
  and informative,12 unexposed. Moving median/p90 error27.506842/31.614203deg,
  instantaneous48.505983/53.348200deg;12/12 paired improvements and12/12 averaging
  availability. This passes the development thresholds against the independent
  stationary-position observed-phase GESC reference. It is not a spatial-gradient
  accuracy result, holdout qualification or a completed historical V9 science job.
- **Verification:** retained conditional C/D reconstructions identify spatial,
  signal-repeatability and upper-cost-bound guards. New
  [recorded-reason observability](r1_verification_diagnostics.md) preserves the
  last guard details through cancellation; final54 focused checks and independent
  review pass. Fresh empirical use remains pending.
- **Analysis source:** D3 uses atomic-writer digests without immediate rereads,
  avoids a discarded objective conversion, and adds isolated labels output.
  Its original67+125 distinct source tests pass; six preedit/full-output parity
  fixtures pass. The subsequent [native-scalar correction](../m4_reference_scalar_amendment_20260910.md)
  converts completed reference rows through the existing `_q1_plain` owner
  before publication and summary. Its43-case focused suite overlaps earlier
  modules and adds two fixtures; it is not235 unique tests. Failed baselines and
  intermediate corrections remain. Exact commands/source receipts are in
  external `builds/m4_post_v9_analysis_v1/executed_commands_v1.txt` and
  `validation_summary_v1.json` (SHA256
  `f1a1d98426db54991306b3ab5faeb1881435e52d7b5d6abbd6c968e215626f09`).

Decision: retain the moving-cycle estimator for the next development iteration;
investigate geometric recurrence with explicit center-drift rejection and
spatially representative moving verification. Shorter two-block windows alone
are not nominated. V5 B gain1.0 differs from current gain.5, so acquire retained
V9 B/D development timelines before assigning their causes or nominating runtime
settings. This means selective existing-bag reads, not new simulations.

No expensive comparison is released. Full four-run analysis-budget feasibility,
credible visible integrated behavior, trustworthy fresh recording, and a
prospective freeze with untouched confirmation data remain prerequisites.
All V1/V2 historical experiments retain their recorded outcomes. Branch remains
`feature/gesc-gaussian-robustness-v2` at3369cfc; changes are uncommitted.
