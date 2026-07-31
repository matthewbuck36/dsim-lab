# Phase 08.8 M3 Fixed Primary Visible Probe

## Disposition

**FIXED EXPERIMENT FAIL / INFRASTRUCTURE COMPLETE / RETAINED.**

The single authorized visible execution of
`phase08_v8_primary_visible_probe.yaml` completed with a healthy recording and
clean shutdown, but it did not complete the declared local-recovery state path
or reach a ranked second candidate. The fixed v8 probe is closed and must not
be retried or tuned in place.

This result does not invalidate the Phase 08.8 counted-source policy. The first
candidate was correctly treated as an unknown candidate, exactly one fill was
created, and later confirmations associated with that fill were not counted as
source two. The empirical failure is in the open-field departure behavior
after the fill was created.

## Executed input and retained evidence

```text
suite:
  phase08_v8_primary_visible_probe
scenario schema:
  8
case:
  v8_primary_probe_r1p5_a45_h25_18801
seed:
  18801
installed source:
  /tmp/phase08_8_qual_final/install/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_v8_primary_visible_probe.yaml
started UTC:
  2026-07-31T04:05:55.626244Z
completed UTC:
  2026-07-31T04:13:08.631921Z
Gazebo:
  visible GUI
```

The retained run is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_primary_probe/2026-07-31/20260731T040556569481Z_simulation_phase08_v8_primary_visible_probe-v8_primary_probe_r1p5_a45_h25_18801-robust_gaus_5fa57e59
```

The suite summary is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_primary_probe/scenario_summaries/20260731T040555626244Z_phase08_v8_primary_visible_probe.yaml
```

An earlier dispatch wrapper stopped before scenario dispatch because its
process guard matched the wrapper command itself. It created no run root and
started no Gazebo process, so it is not an execution or retry of the fixed
case.

## Formal result

```text
run_scenario:
  exit 1
record process:
  return_code 0
  timed_out false
recording_complete:
  true
authoritative completeness:
  PASS
cleanup:
  PASS
remaining new nodes:
  none
remaining session processes:
  none
analysis command:
  exit 0
analysis status:
  partial because behavior failed
analysis failures:
  none
```

The staged live monitor stopped the run after the fixed `360.0 s` Stage A
budget. It did not observe the required direct recovery path. No Stage B
budget began, no controller-ranked goal occurred, and the evaluator-only
global-proximity stop did not fire.

| Predicate | Result |
|---|---:|
| recording complete | pass |
| cleanup complete | pass |
| exactly one fill | pass |
| counted ranked goal | fail |
| required state path | fail |
| required events/order | fail |
| forbidden states/events absent | fail |
| Stage A local recovery | fail |
| Stage B global proximity | fail |
| final zero/completeness | pass |

The terminal pose was `(1.255092, 1.140857) m`, `3.256557 m` from the declared
global evaluation point. The total recorded path length was `24.089129 m`;
the long path reflects repeated motion around the local basin, not travel
toward the global candidate.

## Observed behavior

The collapsed state sequence was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> SEARCH
-> VERIFY_EXTREMUM
-> SEARCH
```

The frozen v8 contract required:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
```

The first convergence occurred at source time `142.4 s`:

```text
convergence point:
  (0.962001, 1.315755) m
distance to declared local:
  0.273508 m
fill center:
  (0.888007, 1.166254) m
fill-to-convergence distance:
  0.166811 m
created fill clusters:
  [1]
active fill clusters:
  [1]
```

The first complete-rotation raw-cost summary was also valid:

```text
candidate ordinal:
  1
rotation count:
  2
raw estimate:
  -2.339437
MAD:
  0.506357
uncertainty:
  1.519071
interval:
  [-3.858508, -0.820366]
decision:
  fill and escape; never classify candidate one as global
```

The fill geometry was:

```text
amplitude:
  0.1
sigma:
  0.169558 m
support radius:
  0.508675 m
exit radius:
  0.423896 m
confidence:
  0.6549
sample count:
  53
residual minimum:
  0.000661
```

The escape episode lasted `10.263057 s`. It emitted `ESCAPE_STALLED`, entered
the legacy redesign/assist path, and achieved only `0.213563 m` of sustained
radial progress. The redesign superseded and merged a second revision of the
same cluster instead of extending the physical departure. When the old
`0.423896 m` exit criterion was eventually met, ordinary search resumed and
the trajectory returned to the same local basin. The subsequent confirmed
events were correctly rejected as active-fill revisits, so no false second
candidate or false global decision occurred.

## Diagnosis

The failure point is the detector-topology-supervisor integration after a
correct local classification:

1. The Gaussian-only `ESCAPE_REPULSE` path stalled just short of a durable
   departure.
2. The legacy stall response redesigned the same fill and entered
   `ESCAPE_ASSIST`.
3. In the selected no-affine, no-recenter open-field profile, that assist state
   had no explicit supervisor motion command that could continue a bounded
   outward departure.
4. The small historical exit radius released the robot while it was still
   close enough for ordinary GESC to fall back into the local basin.

This is not evidence that the source count, raw candidate ordering, adaptive
fill fit, fill cardinality, revisit suppression, recorder, validator, or
cleanup failed. It is evidence that the first v8 open-field profile removed
the historical recenter/guidance mechanisms without replacing their useful
finite-departure function.

## Versioned correction boundary

A correction may be attempted only as a new fixed experiment version. The
bounded correction should:

- keep every historical default and the failed v8 inputs unchanged;
- add an opt-in open-field escape-assist mode;
- on a repulse stall, continue the same escape episode without redesigning,
  superseding, or merging the fill;
- command a bounded direction radially outward from the frozen fill center
  using the existing supervisor/controller command arbitration;
- keep source positions, source roles, Vicon, room dimensions, and evaluator
  geometry out of controller inputs;
- keep affine authorization, recentering, recoverable navigation, wall bounds,
  and post-recovery guidance disabled;
- require a substantially larger finite departure before ordinary GESC
  resumes;
- accept and report the assisted recovery path explicitly rather than hiding
  it as the former direct path;
- complete no-Gazebo qualification and a material checkpoint before any new
  visible run.

This correction is a finite local-recovery action based on onboard odometry
relative to a confirmed fill center. It is not a global pose, route map,
planner, or direct-global controller.

## Plots and tables

All plots are retained under:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_primary_probe/2026-07-31/20260731T040556569481Z_simulation_phase08_v8_primary_visible_probe-v8_primary_probe_r1p5_a45_h25_18801-robust_gaus_5fa57e59/analysis/phase07/plots
```

The generated plots are:

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

The corresponding CSV tables are retained in the sibling `tables` directory.
In particular, `candidate_ranking.csv`, `escape_attempts.csv`,
`algorithm_events.csv`, `algorithm_state.csv`, `odometry.csv`, and
`synchronized_samples.csv` contain the numerical evidence behind the figures.

Representative evidence hashes:

```text
scenario_result.yaml:
  7408a046baf313645ea3ff64e824121db91202ee4cf813ae7da337a94f373806
completeness.json:
  f1f7eb8731f5a4483b8dc37ba010d5e1a59b9e35fc7332a5a245a58be1bebbe3
summary_metrics.json:
  62868b483a25f0af4543a98b2a764817622076d3b33de427a2e3cec32cd8cf7c
trajectory_sources_fills.png:
  4054a6d59e170a458f765334bd019f02b1e3f9d5f454ccb5f2ee65eb08a5284f
cost.png:
  f19385df000a5322d1129ad504b32c2ecf082fe312185be7bc281b175faf995e
candidate_ranking.png:
  14b885c155339bb8b964406f2d6889c7b945eda7b17343282e7a215464c8f2df
```
