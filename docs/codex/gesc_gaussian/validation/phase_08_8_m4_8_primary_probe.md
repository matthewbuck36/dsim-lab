# Phase 08.8 M4.8 v8.7 primary visible probe

Date: 2026-07-31
Committed dispatch boundary: `0b0fb68`
Scenario: `phase08_v8_7_primary_visible_probe.yaml`
Case: `v8_7_primary_probe_r1p5_a45_h25_19501`
Seed: `19501`
Profile: `robust_gaussian_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, supervisor-owned assisted escape pass, schema-v11 causal
handoff pass, strict second-candidate raw ranking pass, Stage B pass,
final-zero pass, complete analysis, all nine plots, and uncontaminated
cleanup pass.**

This was the one authorized execution of the fixed v8.7 visible primary
probe. It ran once from the committed isolated install with Gazebo GUI
enabled. It was not retried, modified, or externally monitored through ROS or
DDS.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_7_primary_probe/
  scenario_summaries/
  20260731T133024465291Z_phase08_v8_7_primary_visible_probe.yaml
SHA-256:
  9dc51574b5a372ff8b6d04da73af91cf90672d28333efd6e7e1637c0e0a9d50f
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_7_primary_probe/
  2026-07-31/
  20260731T133025467173Z_simulation_phase08_v8_7_primary_visible_probe-
  v8_7_primary_probe_r1p5_a45_h25_19501-robust__4b9033ba
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
cleanup:                          PASS
remaining new nodes:              none
remaining run-session processes:  none
formal scenario classification:   PASS
required predicates:              14/14
analyze_run executions:           exactly 1
analyze_run return code:          0
analysis status:                  complete
analysis failures:                none
plots produced:                   9/9
```

Evidence hashes:

```text
raw bag:
  8a96d5313ddbfbbbc41a3ac733046211bf3537c3cb2b18010cff4e2194e799d2
completeness.json:
  227e6e5cc9b9ad95c12d751fd40e889ba9edccaffa82f43776cba004058b7136
scenario_result.yaml:
  4cc01a82c52b99a7669dd6a8f4f8b4e8b0855221e336ee835d29c3286f787e32
analysis/phase07/analysis_completeness.json:
  aa73f013a9839cb32b5be24a017c67356c6ed5434c0542425fdf3a49427e05de
analysis/phase07/summary_metrics.json:
  2cc72690cee86b4b80ea6eb54e0e8941473cbe2d1e167fdb72df68ffb84f20db
dispatch log:
  /tmp/phase08_8_m4_8_v8_7_primary_probe_dispatch.log
  d1873135a09287d83fbabf40c43352f2459a84a15bbdc3a394a3fa770c0a078f
analysis log:
  /tmp/phase08_8_m4_8_v8_7_primary_probe_analyze.log
  87d0e655405b5b2f42535c2e0eaf0dc6600b6358f04ddb44fde289bca22c258e
```

The cleanup baseline contained only the runner-observed ROS daemon for
isolated domain `231`. No new node or run-session process remained.

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

No accepted-motion `RECENTER`, `FAILSAFE`, `TIMEOUT`, fill rejection,
fill merge, fill supersession, or fill-design failure occurred.

## Stage A and candidate-informed fill

Stage A completed at simulation time `118.409 s`, within its fixed `360.0 s`
budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (1.331634, 1.073696) m
convergence point:            (1.201810, 1.046505) m
distance to declared local:   0.141858 m
fill-to-convergence distance: 0.132641 m
fill merge/supersession:      none
```

Candidate one used the required bounded `6 + 3` rotation evidence:

```text
raw estimate:       -2.521479059943976
MAD:                 0.12028547400633416
uncertainty:         0.3608564220190025
lower bound:        -2.8823354819629783
upper bound:        -2.1606226379249733
candidate ordinal:   1
```

## Assisted escape and causal handoff

The escape selected one revision-one onboard-history direction and followed
it almost exactly:

```text
selected direction:            (0.677977943, 0.735082246)
fill center:                   (1.331634, 1.073696) m
measured exit:                 (2.368352, 2.115668) m
fill-to-exit distance:          1.469860 m
selected/actual alignment:      0.999283312
escape duration:               17.863802 s
repulse stalled:               true
assisted:                      true
maximum radial progress:        0.309666 m
failsafe:                      false
timeout:                       false
```

The schema-v11 ownership predicate passed:

```text
assist state samples:                     292
assist control samples:                 1,889
fresh matching supervisor commands:     1,889
nonzero GESC proposals suppressed:      1,889
positive supervisor linear samples:     1,889
post-exit supervisor zero:                PASS
recognized transition tail samples:         0
handoff delay:                            0.005919394 s
handoff deadline:                         0.15 s
ordinary post-exit control samples:     13,316
later supervisor authority:               none
evidence mode:                            bounded_causal_schema_v11
```

This fresh run needed no held-assist or zero/failsafe transition sample. The
first recorded post-exit diagnostic was already ordinary GESC ownership
within `5.919394 ms`, and every later diagnostic through the next state
remained ordinary.

Recorded state weights retain the intended contract:

```text
ESCAPE_REPULSE: (raw, Gaussian, affine) = (0, 1, 1)
ESCAPE_ASSIST:  (raw, Gaussian, affine) = (0, 1, 1)
SEARCH:         (raw, Gaussian, affine) = (1, 1, 0)
```

There is no persistent affine, supervisor, safe-direction, or escape-geometry
authority after recovery.

## Strict ranking and Stage B

Candidate two used the same fixed evidence policy:

```text
raw estimate/lower/upper:       -3.8372093023255816
retained candidate-one lower:   -2.8823354819629783
strict separation margin:        0.9548738203626033
candidate ordinal:               2
filled candidate count:          1
known source count:              2
decision:                        GOAL_REACHED
```

The first valid post-ranking evaluator sample was:

```text
simulation time:       230.405 s
position:              (3.521410, 3.610254) m
declared global:       (3.5, 3.5) m
distance:              0.112314 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
```

Stage B ran from `118.409 s` to `230.405 s`, or `111.996 s`, within its
simulation-only `300.0 s` budget. The final retained distance is
`0.112286 m`.

The evaluator coordinate did not direct motion. It stopped this simulation
only after the controller independently emitted strict raw-cost
`GOAL_REACHED`. Physical execution remains manually stopped by the operator
with `Ctrl+C`.

## Offline analysis

`analyze_run` executed exactly once after the sealed run closed. It returned
zero, produced every expected table and plot, and reported:

```text
analysis_status:       complete
analysis_failures:     []
controller_success:    true
counted ranked goal:   true
fill count:            1
escape attempts:       1
escape successes:      1
escape failures:       0
escape time:           17.863802 s
path length:           13.513125 m
goal convergence time: 229.772090 s
readiness duration:    229.894012 s
terminal state:        GOAL_HOLD
```

Unlike the earlier v8.6 visible analysis, every generic state-duration metric
is valid; the artifact is fully `complete`.

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_7_primary_probe/
  2026-07-31/
  20260731T133025467173Z_simulation_phase08_v8_7_primary_visible_probe-
  v8_7_primary_probe_r1p5_a45_h25_19501-robust__4b9033ba/
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

The trajectory visibly shows start-to-local capture, one nearby fill,
revision-one northeast escape, ordinary transit, and global capture. The
candidate plot shows candidate two strictly below candidate one's retained
lower bound. The cost, weights, radial-escape, state-event, component,
saturation, and Gaussian-history plots agree with the formal evidence.

Machine-readable tables are beside the plots under
`analysis/phase07/tables/`.

## Gate disposition

The v8.7 primary visible probe passes M4.8. It authorizes a separately
checkpointed and committed ten-run primary-repeat dispatch boundary.

This is evidence for one fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility
claim, a secondary-layout claim, a three-light claim, or an arbitrary-layout
or intensity claim.
