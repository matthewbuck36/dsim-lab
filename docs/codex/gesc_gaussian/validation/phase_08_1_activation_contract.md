# Phase 08.1 Diagnostic Activation Contract

## Scope and provenance

This document is the reachability record for the schema-v3 development suite
`phase08_1_diagnostic_activation.yaml`. It is not a formal acceptance
denominator and does not reclassify historical evidence.

The historical `phase08_v2_activation.yaml` remains unchanged at SHA-256
`a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72`.
Its ten normalized case keys still match the sealed v2 manifest. No v1 or v2
run is resumed, overwritten, or counted by this contract.

## Corrected evidence semantics

Schema v3 closes four holes found in the v2 activation contract:

1. `contract_id` must equal the case ID, so a behavior contract cannot be
   inherited accidentally from another case.
2. `required_state_path` is contiguous and anchored to the first observed
   `VERIFY_EXTREMUM`. A later activation cycle cannot conceal a wrong first
   classification.
3. Required event membership, forbidden states/events, and an expected
   terminal state affect classification only through explicit matching
   predicates. Cross-producer events are not ordered by rosbag receipt;
   same-producer order is used only by an explicit sequence contract. The
   schema rejects declared evidence whose predicate is omitted.
4. Every goal or below-target classifier case states the live threshold,
   rotation period/count, applicable dwell, and verification timeout. Two
   3-second rotations plus a 3-second dwell require 9 seconds; the declared
   12-second timeout leaves a positive 3-second margin.

An intentionally insufficient timing budget is permitted only in a
`safe_timeout` contract that requires the direct
`VERIFY_EXTREMUM -> FAILSAFE` path and ordered `TIMEOUT`, `FAILSAFE` events.
The checked-in ten-case suite does not use that exception.

For lifecycle cases with a later stronger source, `GOAL_HOLD` is not forbidden
globally. The first-verification path proves that the local extremum was
classified below target, while reaching a legitimate goal later remains
desirable. This removes the former counterproductive rule under which later
success could invalidate an otherwise correct escape proof.

## Live source-score bounds

The live `Multi_Light_Source_Cost` model combines source contributions in
conductance space, converts the aggregate resistance to the configured
negative divider voltage, and normalizes that post-noise cost between the
model's dark and near endpoints. Relative lumen input scales conductance; it is
not lux or an absolute photometric calibration.

For one source at the most favorable model point, the live implementation and
focused regression produce:

| Relative input | Maximum `source_score` | Relation to 0.95 |
|---:|---:|---|
| 450 | 0.778503 | below |
| 700 | 0.909285 | below |
| 750 | 0.927992 | below |
| 800 | 0.945004 | below |
| 1200 | 1.000000 | reachable |
| 2500 | 1.000000 | reachable |

Therefore the noise-free isolated 450- and 800-input cases are analytically
guaranteed to enter the controller's below-target branch after a valid
rotation window. The historical 1200-input "medium" failure was not
mathematically impossible; it dynamically failed to sustain the threshold in
that run. The v2 wording is historical and is not reused.

The disturbed one-source case uses 700 input and bounded uniform voltage noise
of 0.001. The model endpoint span is about 3.832322 V, so the maximum normalized
score perturbation is about 0.000261. Even its most favorable perturbed score
remains below 0.95.

## Case-by-case reachability

The arguments below justify that each contract asks a reachable question.
They do not claim that every complex branch has already passed in the corrected
runtime; that is precisely what bounded development probes are for.

For multi-source cases, the numerical regression sweeps sensor angle at each
declared local-source center and proves only that the aggregate score there
stays below 0.95. It does not prove that the labeled center is a stationary
point of the realized aggregate field or that the controller will converge
there. Retained branch evidence and synthetic transitions justify a bounded
runtime question; only a fresh probe can establish the full route.

| Case | First verification outcome and path | Reachability basis |
|---|---|---|
| `activation_below_target_low` | `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL` | Isolated 450 input is analytically bounded at 0.778503. The sole source is still the realized global source; this is a controller-classified below-target extremum, not false simulation ground truth. |
| `activation_below_target_medium_fill` | Below target through `DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE` | Isolated 800 input is analytically bounded at 0.945004. Existing state-machine/fill integration covers the accepted-fill transition. |
| `activation_goal_high` | `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD` | The retained v2 high geometry sustained 1.0 and reached `GOAL_HOLD`. That is development evidence for geometry selection only; M6 must freshly prove two complete post-M3 rotations and dwell. |
| `activation_fill_create` | Initial below-target path through one accepted fill and repulse | Retained v2 evidence reached `DESIGN_OR_MERGE_FILL` and emitted `FILL_CREATED` only after its old timeout. M2 removed the measured 5.5–15.7-second synchronization defect without relaxing the timeout. |
| `activation_pure_escape` | Initial fill/repulse followed directly by `SEARCH` | The initial classifier/fill route has retained evidence, and the direct stable-exit transition is covered synthetically. Pure repulsion remains a testable policy, not an acceptance invariant. |
| `activation_stalled_assist` | Repulse, forced stall, one redesign, then `ESCAPE_ASSIST` | A 5 m radial-progress requirement cannot be met inside the bounded room during the 1-second window. Synthetic supervisor integration covers the one-redesign transition. Fresh runtime reachability remains a later targeted question. |
| `activation_fill_merge` | Forced nearby redesign with same-producer `FILL_SUPERSEDED` then `FILL_MERGED` ordering | Local inputs were reduced to 700/750, and the forced early redesign keeps centers inside the declared merge bandwidth. Existing fill-registry tests prove typed merge/revision semantics; the complete runtime branch is not presumed passed. |
| `activation_recenter_resume` | Fill/repulse, `RECENTER`, then `SEARCH` | The retained v2 disturbed case observed this exact lifecycle, while M4 corrected the startup race that invalidated the dedicated recenter attempt. This supports the route, not a fresh pass. |
| `activation_boundary_below_target` | Isolated 800-input below-target fill/escape near the wall | The threshold result is analytical. Retained boundary evidence reached the below-target design branch and recorded no collision; the new contract keeps collision evidence mandatory. |
| `activation_noise_delay_recenter` | Bounded-noise/delay below-target fill, repulse, recenter, resume | The 700-input plus bounded-noise score remains analytically below target. The retained delayed case observed the full lifecycle, and M4 verifies the delayed routes before authorization. |

Only the calibrated high case gates both `controller_goal` and terminal
simulation ground-truth proximity. All other cases retain ground-truth metrics
but do not confuse proximity to a manually labeled source with controller
target classification.

## Multi-source ground truth and future v3

In a multi-source field, contributions combine and the realized optimum may
lie between sources. A YAML `evaluation_role: goal` label is therefore not
proof that the labeled point is the global optimum. The closed v2 ordered-pair
matrix also assigned `source_b` as the goal and required `GOAL_HOLD` even when
that source was weaker or the realized target was below the absolute 0.95
controller threshold.

A future v3 acceptance contract must not copy that rule. It must either:

- compute and validate the realized field optimum before assigning ground
  truth and require a threshold-reachable target for end-to-end goal cases; or
- restrict geometry to a justified dominant target.

Sub-threshold global optima remain useful diagnostic classification/escape
cases, but they cannot be counted as failed calibrated-goal cases merely
because the absolute controller target is intentionally different.

## M6 boundary

M5 performs schema validation, model-bound tests, and dry-run expansion only.
It does not launch Gazebo. M6 begins with exactly two fresh, retained,
development-only probes:

1. `activation_goal_high`;
2. `activation_fill_create`, the local-extremum-plus-later-goal geometry.

Another probe is added only if those results leave a distinct readiness or
causality question. Complex assist, merge, and recenter contracts remain
declared for targeted future development; their provisional policy misses do
not reopen or weaken historical v2.
