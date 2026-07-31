# Phase 08.8 M4.3 Fixed V8.4 Primary Visible Probe

Date: 2026-07-30
Committed dispatch boundary: `8e9acef`
Scenario: `phase08_v8_4_primary_visible_probe.yaml`
Case: `v8_4_primary_probe_r1p5_a45_h25_19201`
Seed: `19201`
Profile: `robust_gaussian_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, approach-continuity escape pass, strict second-candidate raw
ranking pass, Stage B pass, final-zero pass, complete plot bundle, and cleanup
pass.**

This was the one authorized execution of the fixed v8.4 visible probe. It ran
once from the committed isolated install with Gazebo GUI enabled and was not
retried.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_probe/
  scenario_summaries/
  20260731T084941800046Z_phase08_v8_4_primary_visible_probe.yaml
SHA-256:
  0ffebd184a0df830568d3031853ac576eee920d1a3d1fc48d2ed8323721c6c9c
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_probe/
  2026-07-31/
  20260731T084942744556Z_simulation_phase08_v8_4_primary_visible_probe-v8_4_primary_probe_r1p5_a45_h25_19201-robust__c341bb3f
```

## Infrastructure and evidence

```text
record process return code: 0
record process timed out:   false
recording complete:         true
authoritative completeness: PASS
completeness failures:      none
final readiness false:      PASS
final commands zero:        PASS
cleanup:                    PASS
remaining nodes:            none
remaining processes:        none
analyze_run:                partial
analysis failures:          none
plots produced:             9/9
```

Evidence hashes:

```text
raw bag:
  5af1b2d8c53b51ae8e19946a3a93639582cc39c96a987eb6e546b4f681e6f3db
completeness.json:
  5bb9de40208460fed17e3aa381be983886fbfd51c52b29208ef8a3794d9b7f45
scenario_result.yaml:
  9677a65b30778f560bfc7ce07627e057d9296e0bb3710e189ba35b7beebf4e5a
analysis/phase07/analysis_completeness.json:
  73ecfacc0b83e439e97f25a755cf87f1fe498fb3bfc8af002d093ca8c25eed76
analysis/phase07/summary_metrics.json:
  8131fda72481894249e96721f6052c6781641723c87aa08a028ec902886c882d
```

The analyzer retained `45,207` synchronized samples. Cost, source, control,
and GESC streams matched at `1.0`; pose matched at `0.999889` within `17 ms`;
state matched at `0.999602`. Its fresh Phase 05 validation, critical inputs,
topic counts, typed timestamps, source-cost semantics, final-zero commands,
final readiness false, and console checks pass.

The analyzer's top-level status is honestly retained as `partial`, not
relabeled. There are no analysis failures and every standard plot and table
was produced. The partial status has three bounded causes:

- collision is unavailable because simulation contacts were intentionally
  disabled in this open-field, no-wall-claim scenario;
- generic aggregate-target and generic ground-truth metrics are unavailable
  because this counted-source scenario uses the authoritative staged scenario
  validator instead;
- state-duration reconstruction is invalid because one ordinary `SEARCH`
  sample gap is `0.20 s`, above the generic `0.15 s` limit.

The single gap is between source times `336.5 s` and `336.7 s`, during
post-recovery `SEARCH`. It does not cross a transition and does not affect the
recorded state sequence, event sequence, Stage A completion, Stage B ranking,
proximity ordering, or authoritative acceptance result.

## Behavioral path

The accepted complete path passed:

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

No in-readiness `RECENTER`, `FAILSAFE`, `TIMEOUT`, `FILL_REJECTED`,
`FILL_MERGED`, `FILL_SUPERSEDED`, or fill-design failure occurred. The
post-readiness explicit-stop transition is shutdown evidence outside the
accepted motion interval.

## Stage A and candidate-informed fill

Stage A completed at simulation time `236.127 s`, within its fixed `360.0 s`
budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (0.919344, 1.206038) m
convergence point:            (1.046297, 1.366194) m
distance to declared local:   0.305871 m
fill-to-convergence distance: 0.204369 m
fill merge/supersession:      none
```

Candidate one used the required bounded evidence pool:

```text
frozen pretrigger rotations:  6
verification rotations:       3
available rotations:          9
selected repeated rotations:  3
raw estimate:                 -2.193807968754815
MAD:                           0.08166948545710628
uncertainty:                   0.24500845637131885
lower bound:                  -2.438816425126134
```

The accepted typed fill retained the same raw interval:

```text
requested amplitude floor: 3.0485205314076675
accepted amplitude:        3.0485205314076675
amplitude cap reached:     false
sigma major/minor:         0.506211 / 0.506211 m
support radius:            1.518634 m
escape exit radius:        1.366771 m
design escalation count:   0
```

## V8.4 approach-continuity escape

The escape event proves the controller derived its direction from retained
odometry and fill geometry:

```text
history anchor:              (0.218839, 0.030111) m
history anchor source time:  7.6 s
history displacement:        1.368763 m
history age:                 199.4 s
frozen continuity direction: (0.511779, 0.859117)
selected safe direction:     (0.969370, 0.245605)
selected rotation:           -0.785398 rad
direction revision:          1
```

The measured radial-progress gate entered finite assist after the initial
repulsion stalled:

```text
escape outcome:           success
repulse stalled:          true
outward assist used:      true
escape duration:          29.193833 s
approximate escape orbit: 1.377530
maximum radial progress:  0.220345 m
```

The recorded weights match the v8.4 contract exactly:

```text
ESCAPE_REPULSE: (raw, Gaussian, affine) = (0, 1, 1)
ESCAPE_ASSIST:  (raw, Gaussian, affine) = (0, 1, 1)
SEARCH:         (raw, Gaussian, affine) = (1, 1, 0)
```

The safe direction is valid only in the two escape states. At the measured
`ESCAPE_ASSIST -> SEARCH` completion at source time `236.0 s`, affine weight
is zero and safe-direction validity is false on the first recorded `SEARCH`
sample. There is no persistent affine or route guidance after recovery.

## Strict ranking and Stage B

Candidate two used the same intended `6 + 3` evidence pool:

```text
raw estimate:                 -3.8372093023255816
MAD:                           0.0
uncertainty:                   0.0
lower/upper:                  -3.8372093023255816
retained candidate-one lower: -2.438816425126134
strict separation margin:      1.3983928771994476
candidate ordinal:             2
filled candidate count:        1
known source count:            2
decision:                      GOAL_REACHED
```

The controller ranked candidate two at simulation time `351.2 s`. The first
valid later evaluator sample was:

```text
simulation time:       351.217 s
position:              (3.572528, 3.626830) m
declared global:       (3.5, 3.5) m
distance:              0.146104 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
ordering:              GOAL_REACHED before proximity sample
```

Stage B completed `115.090 s` after Stage A, within its fixed `180.0 s`
budget. The final retained distance is `0.146083 m`.

The evaluator coordinate did not direct motion. It stopped this simulation
only after the controller independently emitted its strict raw-cost ranking
event. The physical contract remains manual operator `Ctrl+C`; no physical
coordinate-distance stop is introduced.

## Analysis metrics

```text
controller success:       true
counted ranked goal:      true
failsafe:                 false
timeout:                  false
fill count:               1
escape attempts:          1
escape successes:         1
escape failures:          0
path length:              21.179604 m
goal convergence time:    351.999080 s
readiness duration:       352.088109 s
terminal state:           GOAL_HOLD
```

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_probe/
  2026-07-31/
  20260731T084942744556Z_simulation_phase08_v8_4_primary_visible_probe-v8_4_primary_probe_r1p5_a45_h25_19201-robust__c341bb3f/
  analysis/phase07/plots/
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

The trajectory plot visibly shows local capture, one nearby fill, a
forward-side escape, open-field transit, and global capture. The candidate
plot shows candidate two strictly below candidate one's retained lower bound.
The radial plot shows the assisted measured exit, and the state plot shows the
complete staged path and terminal `GOAL_HOLD`.

Machine-readable tables are retained beside the plots under
`analysis/phase07/tables/`.

## Gate disposition

The fixed v8.4 primary visible probe passes M4.3. It authorizes the sealed
ten-run v8.4 primary repeat gate only after this immutable evidence, report,
and live status are checkpointed and committed, followed by a separate
checkpointed and committed repeat-dispatch boundary.

This pass is evidence for one fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility claim,
a secondary-layout claim, a three-light claim, or a broad arbitrary-layout or
intensity claim.
