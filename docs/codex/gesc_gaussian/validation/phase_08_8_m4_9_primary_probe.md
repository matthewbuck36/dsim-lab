# Phase 08.8 M4.9 v8.8 primary visible probe

Date: 2026-07-31
Committed dispatch boundary: `31bc585`
Scenario: `phase08_v8_8_primary_visible_probe.yaml`
Case: `v8_8_primary_probe_r1p5_a45_h25_19601`
Seed: `19601`
Profile: `robust_gaussian_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, schema-v12 causal assist-entry ownership pass, causal assist
exit pass, strict second-candidate raw ranking pass, Stage B pass,
final-zero pass, all nine plots retained, and uncontaminated cleanup pass.**

This was the one authorized execution of the fixed v8.8 visible primary
probe. It ran exactly once from the committed isolated install with Gazebo
GUI enabled. It was not retried, modified, or externally monitored through
ROS or DDS.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_8_primary_probe/
  scenario_summaries/
  20260731T150756478627Z_phase08_v8_8_primary_visible_probe.yaml
SHA-256:
  c494dc23589c47b363a1af5e8cc1a2b280c7499fb096ca10a3ad000d3d523526
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_8_primary_probe/
  2026-07-31/
  20260731T150757443879Z_simulation_phase08_v8_8_primary_visible_probe-
  v8_8_primary_probe_r1p5_a45_h25_19601-robust__5c73451a/
```

## Infrastructure and formal evidence

```text
scenario runner return code:      0
record process return code:       0
record process timed out:         false
graceful global-proximity stop:   true
recording complete:               true
authoritative completeness:       PASS
completeness failures:            none
completeness warnings:            none
final readiness false:            PASS
final commands zero:              PASS
read-only sqlite quick_check:      ok
cleanup:                          PASS
remaining new nodes:              none
remaining run-session processes:  none
formal scenario classification:   PASS
required predicates:              14/14
analyze_run executions:           exactly 1
analyze_run return code:          0
analysis status:                  partial
analysis failures:                none
critical analysis inputs:         all present
fresh Phase 05 validation:        PASS
plots produced:                   9/9
```

The analyzer's `partial` label is not a formal or behavioral failure. One
optional generic state-duration reconstruction gap exceeded the
`0.150000 s` limit, so only `state_durations` is invalid. Generic aggregate
target metrics are unavailable because this open-field scenario does not
declare that analyzer contract. The scenario evaluator independently proves
the declared-global geometry, and every formal predicate passes.

Evidence hashes:

```text
raw bag:
  fe09b9602375af52b372200961ad5e2af62f5e51b353ef4df4b97ba7a1cdba8c
completeness.json:
  a5a4e94003389d76487d583e403bbe4d2c502eb710b23eb168783f025f02d89a
scenario_result.yaml:
  8f47afb3730276b41a81163566719ce14fc9b8a790b108bb1c5799b8726cab9c
analysis/analysis_completeness.json:
  f1572482e85bb5b22398a24cf4918e68b06267bb2b33d9b68a1ab016d68d107e
analysis/summary_metrics.json:
  ecc153b302bc0a3b37971362f3b3a9c5ac4d31a8a7ef2fa51941eca9ddcef715
dispatch log:
  /tmp/phase08_8_m4_9_v8_8_primary_visible_probe_run.log
  d63d5ac024995e73a8aafdb3ea07638f4316c5493f39c730efccb933b0937d0e
analysis log:
  /tmp/phase08_8_m4_9_v8_8_primary_visible_analysis.log
  3a6575045d32df911c190b7ee3ef09bd5daaa6275c3967dd85dff55f2709c96e
```

The cleanup baseline contained only the runner-observed ROS daemon for
isolated domain `225`. No new node or run-session process remained.

## Behavioral path

The exact required path passed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Required event counts were:

```text
CONVERGENCE_CANDIDATE x2
CONVERGENCE_CONFIRMED x2
FILL_CREATED          x1
ESCAPE_STARTED        x1
ESCAPE_STALLED        x1
GOAL_REACHED          x1
```

No accepted-motion `RECENTER`, `FAILSAFE`, `TIMEOUT`, fill rejection, fill
merge, fill supersession, or fill-design failure occurred.

## Stage A and candidate-informed fill

Stage A completed at simulation time `222.212 s`, within its fixed
`360.0 s` budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (1.038667, 1.321887) m
convergence point:            (1.202823, 1.341585) m
distance to declared local:   0.314848 m
fill-to-convergence distance: 0.165334 m
fill merge/supersession:      none
```

Candidate one used the required bounded rotation evidence:

```text
raw estimate/lower/upper: -2.8453728221821186
MAD:                      0.0
uncertainty:              0.0
rotation count:           3
candidate ordinal:        1
```

## Assisted escape and schema-v12 entry ownership

The escape selected one revision-one onboard-history direction and followed
it with high measured alignment:

```text
selected direction:            (0.406061599, 0.913845708)
fill center:                   (1.038667, 1.321887) m
measured exit:                 (1.485387, 2.724966) m
fill-to-exit distance:          1.472478 m
selected/actual alignment:      0.993966806
escape duration:               23.644374 s
repulse stalled:               true
assisted:                      true
maximum radial progress:        0.307471 m
failsafe:                      false
timeout:                       false
```

The schema-v12 ownership predicate passed:

```text
assist state samples:                       410
assist control samples:                   2,652
entry transition diagnostics:                 0
entry handoff delay:                        0.011493195 s
entry handoff deadline:                     0.15 s
steady supervisor-owned diagnostics:      2,652
fresh matching supervisor commands:       2,652
nonzero GESC proposals suppressed:        2,652
positive supervisor linear samples:       2,031
entry evidence mode:                        bounded_causal_schema_v12
post-exit transition diagnostics:              1
post-exit handoff delay:                    0.012090783 s
post-exit handoff deadline:                 0.15 s
ordinary post-exit diagnostics:          14,040
post-exit evidence mode:                    bounded_causal_schema_v11
```

This fresh run did not need the newly admitted ordinary entry transition:
its first evaluated assist diagnostic was already supervisor-owned within
`11.493195 ms`. Every assist diagnostic then remained supervisor-only.
After escape, exactly one valid causal transition diagnostic preceded
ordinary GESC restoration within `12.090783 ms`, and all later diagnostics
remained ordinary.

Recorded state weights retain the intended contract:

```text
ESCAPE_REPULSE: (raw, Gaussian, affine) = (0, 1, 1)
ESCAPE_ASSIST:  (raw, Gaussian, affine) = (0, 1, 1)
SEARCH:         (raw, Gaussian, affine) = (1, 1, 0)
```

There is no persistent affine, supervisor, safe-direction, or
escape-geometry authority after recovery.

## Strict ranking and Stage B

Candidate two used the same fixed evidence policy:

```text
raw estimate/lower/upper:       -3.8372093023255816
retained candidate-one lower:   -2.8453728221821186
strict separation margin:        0.9918364801434629
candidate ordinal:               2
filled candidate count:          1
known source count:              2
decision:                        GOAL_REACHED
```

The first valid post-ranking evaluator sample was:

```text
simulation time:       339.818 s
position:              (3.574407, 3.611028) m
declared global:       (3.5, 3.5) m
distance:              0.133655 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
```

Stage B ran from `222.212 s` to `339.818 s`, or `117.606 s`, within its
simulation-only `300.0 s` budget. The final retained distance is
`0.133621 m`.

The evaluator coordinate did not direct motion. It stopped this simulation
only after the controller independently emitted strict raw-cost
`GOAL_REACHED`. Physical execution remains manually stopped by the operator
with `Ctrl+C`; no coordinate-distance stop is part of the physical
controller.

## Offline analysis

`analyze_run` executed exactly once after the sealed run and every descendant
closed. It returned zero, produced every expected table and plot, and
reported:

```text
analysis_status:       partial
analysis_failures:     []
recording validation:  PASS
controller_success:    true
counted ranked goal:   true
fill count:            1
escape attempts:       1
escape successes:      1
escape failures:       0
escape time:           23.644374 s
path length:           20.797138 m
goal convergence time: 339.658715 s
readiness duration:    339.811234 s
terminal state:        GOAL_HOLD
```

The sole invalid optional metric is:

```text
state_durations:
  1 state gap exceeded three periods (0.150000 s)
```

It does not remove a formal state, event, candidate, fill, control,
recording, final-zero, or cleanup observation.

## Plots and tables

Plot directory:

```text
<retained run>/analysis/plots/
```

Available plots:

```text
trajectory_sources_fills.png
candidate_ranking.png
cost.png
components.png
state_events.png
weights.png
command_saturation.png
radial_escape.png
gaussian_history.png
```

The trajectory visibly shows start-to-local capture, one nearby fill,
northeast assisted escape, ordinary open-field transit, and global capture.
The candidate plot shows candidate two strictly below candidate one's
retained lower bound. The other seven plots agree with the formal state,
weight, Gaussian, radial, cost, and command evidence.

Machine-readable tables are beside the plots under
`analysis/tables/`.

## Gate disposition

The v8.8 primary visible probe passes M4.9. It authorizes a separately
checkpointed and committed ten-run v8.8 primary-repeat dispatch boundary.

This is evidence for one fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility
claim, a secondary-layout claim, a three-light claim, or an arbitrary-layout
or intensity claim.
