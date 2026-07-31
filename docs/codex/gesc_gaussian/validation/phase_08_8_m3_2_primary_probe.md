# Phase 08.8 M3.2 Fixed Primary Visible Probe

Date: 2026-07-30
Scenario: `phase08_v8_2_primary_visible_probe.yaml`
Case: `v8_2_primary_probe_r1p5_a45_h25_19001`
Seed: `19001`
Profile: `phase08_v8_2_counted_open_field_basin_raw_rank_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, strict second-candidate raw ranking, Stage B pass, final-zero
pass, and cleanup pass.**

This was the one authorized execution of the fixed v8.2 visible probe. It was
run once from the isolated install with Gazebo GUI enabled and was not retried.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_probe/
  scenario_summaries/
  20260731T054259986753Z_phase08_v8_2_primary_visible_probe.yaml
SHA-256:
  1ed8e33fa7c2a026c4b6b4de8e1542287fccf9cba8b297a7b37188380218deb7
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_probe/
  2026-07-31/
  20260731T054300954593Z_simulation_phase08_v8_2_primary_visible_probe-v8_2_primary_probe_r1p5_a45_h25_19001-robust__7abc89e2
```

## Infrastructure and evidence

```text
record process return code: 0
record process timed out:   false
recording complete:         true
authoritative completeness: PASS
final readiness false:      PASS
final commands zero:        PASS
cleanup:                    PASS
remaining nodes:            none
remaining processes:        none
analyze_run:                complete
analysis failures:          none
raw bag SHA-256:
  abe644b2bded9ef86bcd99da286e0caf95bc13896e9d2d6aae4b0d5e751e5643
```

Evidence hashes:

```text
completeness.json:
  b28782e42ec6383b53dd79dcf6226a891db445e0a47d37e86759a81c3d01b5d4
scenario_result.yaml:
  3cb32ef9259c962f1e690c2dfd2706e0cd5892b44949bd6448e62b9e19a0a5ce
analysis/phase07/analysis_completeness.json:
  3c5178dd2cfaf3f8da07cde292ed2ca73b75e9c99c39221e3c94b10f8c01d17a
analysis/phase07/summary_metrics.json:
  c77cdf75c04e45138c01ff66828fdeb25b7badd1752d7dcf75b9410bbd4e7e68
```

The analyzer read 37,212 synchronized samples. Cost, source, control, and GESC
streams matched at `1.0`; pose matched at `1.0` within `35 ms`; state matched
at `0.999731`. No analysis failure was reported.

## Behavioral path

The exact required state path passed:

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

Required events included:

```text
CONVERGENCE_CONFIRMED x2
FILL_CREATED          x1
ESCAPE_STARTED        x1
ESCAPE_STALLED        x1
GOAL_REACHED          x1
```

No `RECENTER`, `FAILSAFE`, `TIMEOUT`, `FILL_MERGED`, `FILL_SUPERSEDED`,
`FILL_REJECTED`, or fill-design failure occurred.

## Stage A and fill cardinality

Stage A completed at simulation time `167.235 s`, within its fixed `360.0 s`
budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (0.981855, 1.297963) m
convergence point:            (1.169093, 1.370400) m
distance to declared local:   0.328172 m
fill-to-convergence distance: 0.200761 m
escape outcome:               success
repulse stalled:              true
outward assist used:          true
escape duration:              23.415567 s
maximum radial progress:      0.304727 m
approximate escape orbit:     0.592145
```

The one-fill topology contract passed without merge or supersession.

## Bounded raw ranking

Both candidates used the intended `6 + 3` evidence pool:

```text
frozen pretrigger rotations:  6
verification rotations:       3
available rotations:          9
selected repeated rotations:  3
```

Candidate one:

```text
ordinal:             1
raw estimate:        -2.8453728221821186
MAD:                  0.0
uncertainty:          0.0
decision:             create the required local fill
```

Candidate two:

```text
ordinal:             2
raw estimate:        -3.8372093023255816
MAD:                  0.0
uncertainty:          0.0
retained-local lower: -2.8453728221821186
strict margin:         0.9918364801434629
decision:             GOAL_REACHED
```

The second interval is strictly lower than the filled candidate. This is the
raw ordering that the failed v8.1 estimator missed. The v8.2 event proves the
correction retained the stronger repeated preconfirmation global-basin
samples while still completing all three verification rotations.

## Stage B and stop ordering

Stage B started only after Stage A at simulation time `167.235 s`. The ranked
goal event occurred at simulation time `289.700 s`, within the fixed `180.0 s`
post-Stage-A budget.

The later evaluator sample was:

```text
simulation time:       289.805 s
position:              (3.613913, 3.580459) m
declared global:       (3.5, 3.5) m
distance:              0.139463 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
ordering:              GOAL_REACHED before proximity sample
```

The final retained distance is `0.139441 m`. Proximity alone did not stop the
run when the robot first entered the radius earlier; the stop occurred only
after controller ranking. This coordinate-based stop is simulation-only.
Physical operation retains manual operator `Ctrl+C` termination.

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
path length:              17.075200 m
goal convergence time:    288.982975 s
readiness duration:       289.059479 s
terminal state:           GOAL_HOLD
```

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_probe/
  2026-07-31/
  20260731T054300954593Z_simulation_phase08_v8_2_primary_visible_probe-v8_2_primary_probe_r1p5_a45_h25_19001-robust__7abc89e2/
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

The trajectory plot visibly shows convergence around the local, one nearby
fill, outward departure, transit through the open field, and final convergence
around the global. The candidate plot visibly separates candidate two below
candidate one's retained lower bound. The state plot shows the complete staged
path and terminal `GOAL_HOLD`.

Machine-readable tables are beside the plots under:

```text
analysis/phase07/tables/
```

They include algorithm events/states, candidate ranking, control and GESC
diagnostics, cost breakdown, odometry, escape attempts, Gaussian history, and
synchronized samples.

## Non-gating runtime notes

Gazebo emitted its existing duplicate embedded-light visual warning, and the
sensor-pose owner emitted two transient square-root runtime warnings. They did
not produce invalid required messages, a controller fault, a failsafe, a
completeness warning, or an analysis failure. The authoritative
`console_clean` check passed.

The analyzer reported only its usual assumed-fallback annotations for channel
index, synchronization tolerance, and supervisor publish rate; analysis
status remained `complete`.

## Gate disposition

The fixed v8.2 visible primary probe passes M3.2 and authorizes the sealed ten
primary repeats only after this evidence is checkpointed and committed.

The pass is evidence for this fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility claim,
a secondary-layout claim, a three-light claim, or a broad arbitrary-layout
claim.
