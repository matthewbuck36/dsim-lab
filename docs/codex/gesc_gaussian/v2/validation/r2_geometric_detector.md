# R2 geometric circle/static prototype result

2026-09-10 UTC. The single offline prototype completed with terminal0 in
16.193012276s (16.066163757s numerical work) under its120s total allowance.
Artifact integrity PASS. **Prototype nomination FAILS:** one declared
moving-center negative produces a candidate. All26 circle/static positives
are detected. Oscillation recognition remains unsupported and unimplemented.
No runtime source, simulator, raw bag, field model or holdout was used.

Prospective method: [r2_geometric_detector_plan.md](../r2_geometric_detector_plan.md).
External directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/geometric_detector_v1/`.
The previously failed R1 stdout presentation and all historical results remain
unchanged. Root owns live status/handoff and any subsequent method adoption.

## Fixed-population findings

| Scope | Count | Result |
|---|---:|---|
| Fixed-center circles and static traces | 26 | All detected |
| Translating circles, straight progress and large loops | 38 | 37 rejected;1 false detection |
| Oscillations | 8 | Unsupported; no prototype trigger |
| .005m/s drift | 1 | Separate tolerated/gray diagnostic |

No positive or negative trace was removed. The circle positives include
periods12–72s, varying prescribed phases and .002/.01m position noise; detection
occurs after18–30s. Static detections occur at12s without noise/.002m noise and
30s with .01m noise. Their independent onset is known from construction.
This is development motion detection, not source/fill/goal validity.

The retained V5 B trajectory produces9 candidate endpoints and15 accepted
circle supports. First candidate is source87.8s,84s after readiness, through
the24/30/36s supports. There are126 competing-drift ambiguity rejections among
141 supports passing zero-drift geometry. No static candidate occurs.
B has no independent settling-entry label here:84s is observation-relative
candidate timing, not established detector latency. Replay cannot predict the
trajectory following an earlier actual intervention. V9's changed-gain B/D
exports completed after dispatch and were not added to this frozen population.

## One off-grid false detection and causal interpretation

The failed trace is
`new33_translating_circle_p60.0_v0.04_h0.39269908169872414_phase1.5707963267948966_sigma0.0`:
.25m circle, P60s, center drift .04m/s atpi/8, initial phasepi/2, no noise.
Its sole candidate is endpoint72s using the18s support. Other support lengths
at that endpoint fail zero-drift geometry.

The admitted zero-drift fit has radius .153679089m, radialRMS .006420281m,
actual trajectory radius .183659375m, angular span2.443022168rad, rank3 and
condition16.4406. Its competing-fit residual limit is .008420281m. The best
geometrically admitted appreciable-drift grid rival has .01m/s speed,
headingpi/2, residual .009898957m, so the fixed rule fails to veto.
Exact zero and all32 competing fits are retained, including rejected alternatives.

Two restrictions warrant a new prospective method correction; neither is fixed
inside this failed version:

1. The45-degree velocity-heading grid omits the actual22.5-degree drift.
   Its failure does not justify a general claim that all translating motion is
   excluded. A continuous/refined alternative search or explicit conservative
   uncertainty treatment is needed before broader claims.
2. The prototype requires competing fits to pass the same2*pi/3 angular-span
   criterion as the stable candidate. That is an acceptance test imposed on an
   alternative explanation. The actual moving-center circle covers only
   `2*pi*18/60=1.884956rad` over this support; its exact velocity would explain
   an ideal radius.25m circle but be discarded for insufficient alternative
   angular coverage. A plausible competing explanation can invalidate a stable
   claim even when it cannot independently establish stable motion. A new
   version should distinguish candidate acceptance from alternate-explanation
   plausibility; keep its span as diagnostic rather than automatically applying
   this candidate gate. This is an analytic/source interpretation, not an
   unrecorded re-evaluation or proof that one correction suffices.

The current failure was retained before these proposals. No threshold,
negative label or original result was changed to obtain a pass.

## Execution and audit

The plan/helper/argv were saved before the sole command:

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/geometric_detector_v1/run.py
```

`execution_receipt.json` retains exact argv, returncode0, inclusive time and log
hash. `prepared.json` pins the helper/plan before execution. The helper imports
only the R1 `weighted_lstsq` function through its AST; it does not execute the
old helper or re-run R1. Its centered coordinate algebra preserves that fit.

A single30s read-only output audit verifies13 published files, all7 selected
source/input/plan/helper pins and all73 control rows. No numerical model replay
occurred in that audit. `audit.json` retains the resulting hashes and population:

- `decisions.jsonl`:1445 complete endpoint rows, including58 B endpoints.
- `competing_velocity_fits.jsonl`:48864 alternative-fit rows.
- `added_control_samples.jsonl`:54045 prescribed new samples.
- `control_contract.json`, `control_results.json`:all73 traces.
- `b_result.json`, `result.json`, `pins_{before,after}.json`, `receipt.json`.

Result SHA256:
`a23dd50cb94c5b54323d37512b9dca1f6963c8a7dc9dc1f4393ca92c874408ee`.
Receipt SHA256:
`60a9a0140c9de42ec0de412629d88773c25b7c0117ed96cf67fe3ebb5ea4b1ab`.
The complete helper/plan/reused R1 input pins are in the before/after maps and
were unchanged at audit. There is no whole-tree stability claim while other
agents work on unrelated owners. Before edits, phase-context validation and
`git diff --check` passed.

The measurable advance is a responsive circle/static prototype with an exposed
false-positive mechanism. It is not nominated for runtime. The next bounded
version can correct alternative-explanation admission and test the unchanged
population plus fresh V9 development inputs. Oscillation needs its own
prospective method; a failed two-block fallback is not silently reinstated.
