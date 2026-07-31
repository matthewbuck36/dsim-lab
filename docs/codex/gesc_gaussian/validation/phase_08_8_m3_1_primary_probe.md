# Phase 08.8 M3.1 V8.1 Primary Visible Probe

## Disposition

**FIXED V8.1 EXPERIMENT FAIL / INFRASTRUCTURE COMPLETE / STAGE A PASS /
RAW-CANDIDATE CHARACTERIZATION FAIL / RETAINED.**

The single authorized visible execution of
`phase08_v8_1_primary_visible_probe.yaml` completed one correct assisted local
recovery and physically reached the global basin, but the counted-source
controller rejected the second candidate because its post-confirmation
raw-cost slice did not retain the stronger raw samples observed during the
approach.

The fixed v8.1 input is closed. It must not be retried, tuned in place, or
counted as a pass. Its primary repeats, secondary cases, and broader matrix
were not dispatched.

## Executed input and retained evidence

```text
suite:
  phase08_v8_1_primary_visible_probe
scenario schema:
  8
case:
  v8_1_primary_probe_r1p5_a45_h25_18901
seed:
  18901
installed source:
  /tmp/phase08_8_1_release_qual/install/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_v8_1_primary_visible_probe.yaml
started UTC:
  2026-07-31T05:01:29.680474Z
completed UTC:
  2026-07-31T05:09:28.649745Z
Gazebo:
  visible GUI
```

Retained suite summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_1_primary_probe/scenario_summaries/20260731T050129680474Z_phase08_v8_1_primary_visible_probe.yaml
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_1_primary_probe/2026-07-31/20260731T050130632538Z_simulation_phase08_v8_1_primary_visible_probe-v8_1_primary_probe_r1p5_a45_h25_18901-robust__c2e42fbd
```

## Formal result

```text
run_scenario:
  exit 1
record process:
  return_code 0
  timed_out false
recording complete:
  true
authoritative Phase 05 validation:
  PASS
final command zero:
  PASS
cleanup:
  PASS
remaining new nodes/processes:
  none
analyze_run:
  exit 0
  partial only because behavioral acceptance failed
  analysis failures none
```

The fixed `180.0 s` post-Stage-A monitor stopped the run at simulation time
`401.158 s`. The noninterpolated timeout sample was `(3.439636, 3.643358) m`,
only `0.155548 m` from the declared evaluator global. The final recorded pose
was `(3.437095, 3.642711) m`, `0.155960 m` from that point.

| Predicate | Result |
|---|---:|
| recording complete | pass |
| cleanup complete | pass |
| Stage A assisted local recovery | pass |
| exactly one fill | pass |
| required stall and assisted state | pass |
| forbidden state/event absence | pass |
| physical approach within `0.50 m` | observed |
| controller-ranked second candidate | fail |
| ranked-goal-gated Stage B | fail |
| terminal `GOAL_HOLD` | fail |

The evaluator correctly refused to turn proximity alone into a pass. Physical
approach was observed, but `ground_truth_goal` remained failed because no
valid controller-ranked `GOAL_REACHED` preceded it.

## Successful local recovery

The observed path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> SEARCH
```

The required Stage A prefix completed once:

```text
Stage A completion sim time:
  221.128 s
fill cardinality:
  exactly one created, typed, and active cluster
fill center:
  (0.997529, 1.289396) m
confirmed local point:
  (1.168634, 1.375638) m
convergence-to-declared-local distance:
  0.332970 m
fill-to-convergence distance:
  0.191610 m
escape exit radius:
  1.356466 m
escape duration:
  23.612782 s
stalled:
  true, required
assisted:
  true, required
timeout/failsafe:
  false/false
fill merge or supersession:
  none
```

The v8.1 outward-assist correction therefore fixed the v8 departure defect.
Walls, contacts, collision failsafes, recentering, affine guidance, and
post-recovery guidance did not stop or redirect this run.

## Candidate-ranking evidence

The controller retained:

```text
candidate 1, local:
  estimate       -2.845372822
  MAD             0.0
  uncertainty     0.0
  interval       [-2.845372822, -2.845372822]

candidate 2, global-basin confirmation:
  estimate       -0.021174297
  MAD             0.000101450
  uncertainty     0.000304351
  interval       [-0.021478649, -0.020869946]

reported strict-separation margin:
  -2.824502876
decision:
  counted candidate not strictly stronger; resume search
```

That decision is correct for the two intervals it received. The defect is
that the second interval does not represent the strongest repeated raw
samples already observed in the second basin.

Direct inspection of the synchronized raw-cost evidence shows:

```text
within 0.50 m of declared local:
  minimum raw cost   -2.846198587
  maximum source score 0.741407223

within 0.50 m of declared global:
  minimum raw cost   -3.837209302
  maximum source score 1.0

global SEARCH interval before confirmation:
  multiple complete 3 s bins at -3.837209302

global VERIFY_EXTREMUM interval:
  minimum raw cost   -0.021275748
```

The real raw signal therefore contains the expected strict ordering:

```text
-3.837209302 < -2.846198587
```

The global-basin raw minimum is more negative and hence stronger for the
declared minimization problem. The existing estimator starts a new window
only after `SEARCH -> VERIFY_EXTREMUM`; by then the directional samples that
carried the basin peak had passed. It consequently compared a weak
post-confirmation sensor-angle slice against the local basin peak.

## Diagnosis and bounded correction

This is a detector-to-candidate-estimator timing defect, not a motion,
topology, cost-sign, fill, wall, collision, recorder, or cleanup failure.

A separately versioned correction should:

1. retain a bounded number of complete raw-cost rotation minima while in the
   current `SEARCH` epoch;
2. freeze those minima when a convergence confirmation enters
   `VERIFY_EXTREMUM`;
3. collect the normal post-confirmation verification rotations;
4. choose the required number of strongest, meaning most negative, repeated
   rotation minima from the bounded pretrigger plus verification pool;
5. compute the same median/MAD interval and use the unchanged strict
   nonoverlap comparison;
6. reset the bounded history on every new `SEARCH` epoch;
7. report pretrigger, verification, available, and selected rotation counts
   in the existing event value arrays.

The correction consumes only raw photoresistor-derived cost, controller state,
time, and the declared total source count. It adds no source coordinate,
source role, Vicon input, global pose, evaluator proximity, room geometry,
waypoint, route map, planner, topic, message, node, or publisher.

## Plots and tables

All plots are retained under:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_1_primary_probe/2026-07-31/20260731T050130632538Z_simulation_phase08_v8_1_primary_visible_probe-v8_1_primary_probe_r1p5_a45_h25_18901-robust__c2e42fbd/analysis/phase07/plots
```

Generated plots:

```text
trajectory_sources_fills.png
cost.png
components.png
state_events.png
weights.png
command_saturation.png
radial_escape.png
gaussian_history.png
candidate_ranking.png
```

The sibling `tables` directory contains the numerical data. The most relevant
files are `candidate_ranking.csv`, `algorithm_events.csv`,
`synchronized_samples.csv`, `escape_attempts.csv`, and `odometry.csv`.

Representative SHA-256 values:

```text
suite summary:
  0fd81935239f336539e425079d25bcc06432ecae9b49fef2aef32bfa269c8636
scenario_result.yaml:
  4967d4bfdbbb7d999c3732c21e7468cd60a93aed8a123fdb8d68f27786e5819d
completeness.json:
  3ae8e4d3c171937dff7a4560f5e837b9e834f935b46c702cf1614f7ae56f5d0c
summary_metrics.json:
  2b3f9fee6ad6d83514a6a5d9c1d560cabef863154bd4dc4ccac5743970965901
analysis_completeness.json:
  9d81da747f8b614cc7fac953ff301ddbf46fc7f697ab0bfc88c94e36c0d1c1b5
trajectory_sources_fills.png:
  3569645592bc698ed425a82fe307c64c76b089e651dfd116af55adf90b013602
cost.png:
  9af82275224da7829db6fc734bb540fe5aaec13f1a277b285118a1c0e40fefb8
candidate_ranking.png:
  1a69fed6f64a32ee37374cafe9a20af6ff23ca592dd57edc868bec94feea5251
```
