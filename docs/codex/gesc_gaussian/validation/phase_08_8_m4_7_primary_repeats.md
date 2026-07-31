# Phase 08.8 M4.7 Fixed V8.6 Primary-Repeat Result

## Disposition

**CLOSED / FIXED POPULATION FAIL / BEHAVIORAL OBJECTIVE REACHED / FORMAL
HANDOFF AND CLEANUP GATES FAILED.**

The sealed v8.6 primary population stopped after its first case, seed `19411`,
as required. Seed `19411` was not retried. Seeds `19412..19420` were not
dispatched. The v8.6 secondary probe and repeats remain prohibited.

This result does not overwrite the passing v8.6 visible probe. It also does
not relabel the fixed repeat as a pass: two required predicates failed even
though the robot completed the intended local-recovery and global-convergence
behavior.

## Frozen dispatch

Dispatch HEAD:

```text
4207b73
phase 08.8: authorize v8.6 primary repeats
```

Installed scenario:

```text
/tmp/phase08_8_v8_6_release_qual.qth8ZZ/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_6_primary_repeats.yaml
SHA-256:
  641e60c3382afca6b3f499bd1f8abc6609df30eb2dfbbc20793dbfaabab57efe
```

Execution contract:

```text
ROS domain:                  228
mode:                        serial/headless
declared seeds:              19411..19420
retry:                       prohibited
stop on first failure:       enabled
per-run simulation timeout:  720.0 s
per-run wall timeout:        900.0 s
outer timeout:               9,600 s, INT then 60 s kill-after
runner return code:          1
runner outer timeout:        false
```

The installed scenario had source parity with the committed source file, the
evidence root was absent before dispatch, the Git tree was clean, Phase 08
implementation context passed, and no Gazebo, runner, recorder, analyzer, or
ROS node was active on domain `228`.

Retained runner log:

```text
/tmp/phase08_8_m4_7_primary_repeats_dispatch.log
SHA-256:
  08228d35fc286c558baaa6fd47e72734510f18b9693dec2105c6d835f10908b0
```

## Retained evidence

Run directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_6_primary_repeats/2026-07-31/
  20260731T124148715876Z_simulation_phase08_v8_6_primary_repeats-
  v8_6_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_35b235c3
```

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_6_primary_repeats/scenario_summaries/
  20260731T124147695682Z_phase08_v8_6_primary_repeats.yaml
SHA-256:
  e1a137b6306ad4b89ae9af096fa5c87bae4382bd721eace13d08158d090a38dd
```

Per-run result SHA-256:

```text
dbe53cd1350cf4a424942b963428ab2d487ded517cfc2775341c1a6568d011d7
```

The record process returned zero without timeout. The bag is readable and
complete, final readiness is false, final commands are zero, the console is
clean, and no run-session process remained.

## Behavioral result

The complete observed state path was:

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

Stage A passed at simulation time `228.826 s`, within `360.0 s`. It contained
one local candidate, exactly one typed revision-one fill, one stalled repulse,
one supervisor-owned assisted exit, no fill merge or supersession, no
recenter, no timeout, and no failsafe.

The local recovery evidence was:

```text
fill center:                         (0.963022, 1.241932) m
selected revision-one direction:    (0.487167, 0.873309)
measured exit position:             (1.536907, 2.600729) m
fill-to-exit distance:               1.475016 m
selected/actual-exit alignment:      0.994041292
assist control samples:              2,769
fresh matching supervisor samples:   2,769
nonzero GESC proposals suppressed:   2,769
positive supervisor-linear samples:  2,058
```

After recovery, the controller found a distinct second candidate and ranked
it strictly below the retained local candidate using raw cost:

```text
candidate one retained lower bound:  -2.8453728221821186
candidate two interval:              [-3.8372093023255816,
                                      -3.8372093023255816]
strict separation margin:             0.9918364801434629
decision:                             GOAL_REACHED
```

The first valid later noninterpolated evaluator sample occurred at simulation
time `339.224 s`, `110.398 s` after Stage A and within the `300.0 s` Stage B
budget:

```text
position:          (3.613817, 3.548278) m
declared global:   (3.5, 3.5) m
distance:           0.123633 m
```

The final retained distance was `0.123614 m`. The evaluator coordinate
stopped the simulation only after controller-ranked `GOAL_REACHED`; it was
not available to controller motion. Physical operation remains coordinate
free and manually stopped with `Ctrl+C`.

## Failed gates

Twelve of the fourteen required scenario predicates passed. The two failures
were:

```text
supervisor_owned_escape_assist:  false
cleanup_complete:                false
```

Every behavioral predicate passed, including controller goal, evaluator
proximity, terminal state, state/event sequence, Stage A, and fill
cardinality.

### Post-exit ownership timestamp defect

The first post-exit `SEARCH` state was recorded at bag timestamp
`1785501942470570252`. The first zero supervisor command followed `0.777583
ms` later at `1785501942471347835`.

One control diagnostic `0.554917 ms` after that zero-command publication
still reflected the prior assist authorization:

```text
diagnostic stamp:          1785501942471902752
combined vx / wz:          0.099999824 / 0.002814256
GESC vx / wz:              2.481288760 / -4.230085162
```

The next control diagnostic, only `6.363998 ms` later, restored ordinary GESC
ownership:

```text
diagnostic stamp:          1785501942478266750
combined equals GESC:      true
supervisor contribution:   zero
```

All `13,069` subsequent control diagnostics through the next
`VERIFY_EXTREMUM` transition had zero supervisor contribution and combined
command equal to the GESC proposal. The `SEARCH` state itself immediately had
weights `(1,1,0)`, no valid safe direction, and no escape authority.

The current predicate selects the first diagnostic by bag timestamp after the
first recorded zero supervisor command. It therefore treats a single
cross-topic delivery-order sample as persistent ownership even though the
controller completed the handoff within `7.696498 ms` of the recorded state
boundary and remained correct thereafter. The fixed v8.6 predicate still
fails exactly as written; this result is not retroactively reclassified.

### Cleanup contamination

Cleanup found no remaining run-session process, Gazebo process, controller,
recorder, or analyzer. It found one new graph node:

```text
/_ros2cli_282407
```

That identity is the transient ROS CLI node created by the external
`ros2 topic echo --once` progress inspection issued on domain `228` while the
sealed run was active. It was outside the run process session but still
present in discovery when the runner audited the graph. The runner correctly
reported contamination and stopped the population.

Later sealed runs must be monitored only through retained files and process
state. No external ROS CLI command may join their active domain. The cleanup
gate itself must not be weakened or taught to ignore arbitrary external
nodes.

## One-time offline analysis

The standard analyzer was invoked exactly once after the failed population
closed:

```text
timeout --signal=INT --kill-after=30s 300s \
  ros2 run ros_esc analyze_run <run-directory>
```

It returned zero, reported `analysis_failures=[]`, passed fresh Phase 05
validation, and produced every expected table plus all nine plots. Its
summary status is `partial` only because one optional generic state-duration
gap exceeded `0.150 s`; no critical input, behavioral event, final-zero
evidence, or plot is missing.

Analyzer log:

```text
/tmp/phase08_8_m4_7_primary_repeat_19411_analyze.log
SHA-256:
  2f8822bb8ca43c66f00e9b5c973781cd297e82999c80f1ab5b79aaa2ac6d8f23
```

Analysis summary SHA-256:

```text
885b37842a55b9e6b18d8fe72328fa4066e59f1e517f8166aebb36fab732b340
```

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_6_primary_repeats/2026-07-31/
  20260731T124148715876Z_simulation_phase08_v8_6_primary_repeats-
  v8_6_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_35b235c3/
  analysis/phase07/plots/
```

It contains:

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

The inspected trajectory plot shows capture at the local, one fill, a direct
northeast exit/transit, and final capture at the global. The candidate plot
shows candidate two strictly below candidate one's retained bound.

## Fixed-version conclusion

The v8.6 primary-repeat gate is formally failed and closed at `0/1` formal
passes under its no-retry rule, with one of ten declared seeds dispatched.
Its controller behavior nevertheless completed the full scientific objective.

A fresh correction may:

1. make the ownership validator causal and bounded rather than assuming
   cross-topic bag order is controller-consumption order; and
2. prohibit external ROS graph inspection during sealed execution.

It may not change the controller behavior, source layout, intensity ratio,
candidate ranking, fill parameters, escape direction, time budgets, cleanup
requirements, or the retained v8.6 evidence.
