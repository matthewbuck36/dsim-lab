# R7 short visible C development02

Status: **ADOPTED**, prospectively2026-09-10 after [R7 source validation](r7_approach_runtime_handoff.md)
and its564-member verified source archive. Preparation, acquisition, analysis
and reference remain unstarted at adoption. The source receipt passed332 unique
checks with unchanged764 source pins and21 installed bindings. Source archive
manifest SHA256 `ba29d5b2dfe05166e1cc35fc740f93feb49cea5c67c0261ca15886963d7e0fae`.
Required source receipt is external
`development/20260910/r7_runtime_validation_v1/focused_v1/source_validation.json`.
Its successful result and unchanged source/installed bindings must be verified
by the retained preparation owner before acquisition. C01 and V10 remain failed.

## Hypothesis and exact exposed case

Fixed-center approach may improve the margin for reaching the unchanged 0.08 m
collection gate within eight seconds. The ideal model improved the C01 anchor's
admission from 5.75 s to 1.225 s, but its baseline also passed: it did not explain
the actual failure. This visible case tests real approach and subsequent
continuous verification, with R6's zero-only expiry policy and R5's bounded
activated-fill handoff preserved. No threshold, timeout or research gate changes.

Use new run/case ID `v2_method_development_C_20260910_02` and exclusive external
`development/20260910/visible_integrated_C_02/` under the V2 experiment root.
Copy [C01](r5_visible_c01_plan.md)'s scenario with the exact same exposed seed
26091011, source geometry, start, disturbances, costs, PDE detector,
rolling_gesc_v2, moving_cycle_coherence_v1, centered_tracking_v1, V6 half-gain
controller, fill and escape settings. Change only identity, paths, descriptions
and the source-validation receipt. The selected runtime source adds R6 and R7;
the scenario's scientific settings and budgets are unchanged.

Use one visible Gazebo acquisition, domain201/localhost1/DISPLAY:0, clean
PYTHONPATH and the existing `stationary_recurrent_pairing_v1/runtime_environment_v2.sh`.
No rebuild. Existing preparation has a 90 s inclusive cap. Preserve 45 s
preflight, 300 s run, 340 s wall, 30 s shutdown, and 180/120 simulation-second
local/post-recovery stages. The existing outer wrapper owns 420 s total with
30 s independent cleanup reserve; external SIGINT at 415 s plus 5 s kill grace.
Keep full recording, startup joins, final zero, typed outcomes and inner/outer
cleanup authoritative. Preserve any failure without an unchanged retry.

## Existing measurements and decision

Reuse C01's `prepare_attempt.py`, `run_attempt.py` and native
`analysis/run_analysis.py`, with identity/plan/source-receipt substitutions only.
Copy `analysis/run_direction_reference.py` unchanged. Preparation must bind the
actual selected launch, required recording topics, all validated source pins
and 21 installed entry points. The future source receipt is a prerequisite,
not evidence supplied by this draft.

After complete recording and cleanup, run native analysis once: 110 s work
within 120 s total, including hashes. Preserve its single captured BagData read
and native validator's second declared read, existing JSONL/CSV/figures, and
existing V10 motion/arrival metric calls on that captured data. No third decoder
or parallel analysis owner. Then allow the unchanged 24-target independent
direction-reference job, 38 s work within 45 s total, on saved normalized inputs.
Retain every exposed, unexposed, invalid and censored target and denominator.

Require recorded timely approach/admission, valid moving verification, one
committed fill with both registry ACKs, owned REPULSE (optional ASSIST), restored
SEARCH and actual evaluator-only global arrival within 0.5 m, without forbidden
safety events. Require complete native recording/lifecycle/analysis and measured
continuous VERIFY plus initial DESIGN through the existing fixed motion metric.
Keep exact command zero intervals, guidance reasons, rejection/cancellation
reasons and all direction errors/availability, including the unresolved outlier.
GOAL_HOLD, second ranking and direct exit-bearing alignment remain optional.

Source-test or ideal-model success is insufficient. Only usable complete native
analysis and all 24 reference outcomes permit assessing whether this exposed case
supports another comparison. A failed guard, partial analysis or poor direction
result remains visible and requires diagnosis. No V11/full-matrix release,
broad robustness or original paired 30% detector-latency claim follows here.
Simulation only; no physical, Pi, snapshot, V1, commit or push work.
