# Phase 08.8 M8.8 v8.12 Visible Corrective Probe

Date: 2026-07-31
Committed dispatch boundary: `4094087`
Scenario: `phase08_v8_12_interior_anchor_visible_probe.yaml`
Case: `v8_12_interior_anchor_r1p25_a45_ratio1to3_20001`
Seed: `20001`
Profile: `robust_gaussian_v1`

## Disposition

**PASS — 14/14 FORMAL PREDICATES, ONE LOCAL RECOVERY AND FILL, THE
EXPECTED INTERIOR-FARTHEST APPROACH ANCHOR, ASSISTED ESCAPE, STRICT
SECOND-CANDIDATE RAW-COST RANKING, GRACEFUL GLOBAL-PROXIMITY STOP, COMPLETE
RECORDING/CLEANUP, AND 9/9 PLOTS.**

The one authorized visible run executed once without a retry. The controller
confirmed candidate one, created exactly one typed Gaussian fill, selected the
new odometry-only `interior_farthest` approach anchor, traversed
`ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH`, restored ordinary GESC ownership,
confirmed candidate two, and strictly ranked it as the stronger raw-cost
minimum. The evaluator then stopped the simulation on the first valid
post-recovery proximity sample, `0.116717 m` from the declared global.

This is the fixed v8.12 corrective result. It neither retries nor reclassifies
the retained failed v8.11 seed `19931`.

## Frozen dispatch and retained evidence

```text
dispatch commit:
  40940877a67920653cca2378c91336803cfd5761
installed scenario:
  /tmp/phase08_8_v8_12_release_qual.HnEptF/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_12_interior_anchor_visible_probe.yaml
installed/source SHA-256:
  d4607649546f8301112a0cbbb5ded10a2a167146efed143dbfff64e4d5810c65
case key:
  5d8ed8295d910a52c28561e7d9f8172cb63d7158debef9eb7597b8befe285dbb
ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY:
  219 / 1
presentation:
  visible Gazebo GUI
attempts / retries:
  1 / 0
```

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_12_interior_anchor_probe/scenario_summaries/
  20260731T231350696332Z_phase08_v8_12_interior_anchor_visible_probe.yaml
SHA-256:
  b9e3f9711600dd36a9d897bf550cf432ce8dcdb9f34ba444921ad030c1322cde
```

Exact summary-owned run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_12_interior_anchor_probe/2026-07-31/
  20260731T231351648763Z_simulation_phase08_v8_12_interior_anchor_visible_probe-
  v8_12_interior_anchor_r1p25_a45_rati_439a8eac
```

```text
started:                         2026-07-31T23:13:50.696332Z
completed:                       2026-07-31T23:18:15.519683Z
runner / recorder return code:   0 / 0
record process timed out:        false
recording complete:              true
authoritative completeness:      PASS
final command zero:              PASS
final readiness false:           PASS
bag SQLite quick_check:          ok
cleanup:                         PASS
remaining new nodes:             none
remaining session processes:     none
formal predicates:               14/14 PASS
```

Recorder metadata proves the clean dispatch boundary:

```text
working_directory: /home/mattb/dsim-lab
repository_root:   /home/mattb/dsim-lab
commit:            40940877a67920653cca2378c91336803cfd5761
dirty:             false
untracked_paths:   []
```

Primary retained hashes:

```text
raw bag:
  2f18323d18fd6969443f268a114d3487b04e1bd27ff6abb11e6df94394b699cf
scenario_result.yaml:
  69f4d78aace44fac1accb09845f232f8f90df3f757cb677711f72396a6049d91
completeness.json:
  9b56227d444baeb813af136e15e54e7c96dd88e87e9949ca2cf355af590491d5
metadata.yaml:
  e714f39dbac540bc2deea4571726149afdabaac135a46bad44c50adcb2802a82
dispatch log:
  /tmp/phase08_8_v8_12_visible_dispatch.log
  5ab4cef0cbc190cd0eaf6935ad82a87fb92ce599cc9bbf87d5bd20ab7cd7bce8
evidence log:
  /tmp/phase08_8_v8_12_visible_evidence.log
  5410b40a8fbcf43bc7d8b655e6c9be2b8b7b4c0ccffd4f00a3f74cef763c5ec3
```

## Stage A and fill cardinality

The accepted local-recovery path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
```

The measured first candidate and fill were:

```text
first convergence source time:      79.700 sim s
first convergence point:            (1.0132784, 0.7787284) m
declared local lamp:                 (0.8838835, 0.8838835) m
convergence-to-local diagnostic:     0.1667352 m
declared-local distance gate:        not applied
fill center:                         (1.1054757, 0.7412409) m
fill-to-convergence:                 0.0995272 m
created / typed / active clusters:   [1] / [1] / [1]
unassigned clusters:                 []
Stage A completed:                   106.609 sim s
```

The evaluator used source coordinates only for topology and outcome
classification. They were not launch arguments or controller inputs.

## Interior anchor and escape ownership

The correction was exercised exactly as planned:

```text
approach anchor mode / value:        interior_farthest / 1
minimum displacement:                0.500000 m
measured displacement:               1.330955 m
frozen fill exit radius:              1.366771 m
anchor:                               (0.0000116, 0.0000324) m
anchor source time / history age:     0.700000 / 88.300000 s
approach direction:                   (0.8305797, 0.5568998)
escape branch:                        assisted
escape-stalled event:                 observed
escape attempts / successes / fails: 1 / 1 / 0
analysis escape duration:             17.559531 s
fill-to-exit distance:                1.468904 m
fill-to-exit alignment:               0.999989559
```

Supervisor assist owned all `1,850` assist control samples and suppressed
ordinary nonzero GESC commands during that interval. Its entry handoff took
`0.003286 s`, its exit handoff took `0.006149 s`, both under the `0.15 s`
bound, and ordinary GESC ownership was restored for `13,847` subsequent
control samples. No failsafe occurred.

## Strict ranking and Stage B

Candidate two was strictly better under the controller-owned rotational raw
cost comparison:

```text
filled candidate raw-cost lower bound:  -3.1887054620
candidate-two raw-cost upper bound:      -3.8372093023
strict separation margin:                 0.6485038403
candidate ordinal / known count:          2 / 2
invalid ranked-goal events:               0
```

The complete controller path was:

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

The first valid post-ranking proximity sample caused the graceful simulation
stop:

```text
Stage A sample time:                106.609 sim s
proximity sample time:              222.719 sim s
post-Stage-A elapsed time:          116.110 s
sample position:                    (3.5642621, 3.5974337) m
sample global distance:             0.1167174 m
proximity radius:                   0.50 m
interpolation used:                 false
graceful global-proximity stop:     true
final position:                     (3.5642515, 3.5974277) m
final global distance:              0.1167065 m
terminal state:                     GOAL_HOLD
path length:                        12.9851298 m
```

This distance stop is simulation-evaluator evidence only. The physical
controller has no coordinate-distance arrival stop; physical arrival remains
manual operator `Ctrl+C`.

## One-time analysis and plots

The exact summary-owned run was analyzed exactly once:

```text
analysis status / failures:        complete / []
fresh Phase 05 validation:         PASS
stored Phase 05 validation:        PASS
recording failures:                []
summary_metrics.json SHA-256:
  33a3487b0e58ced56ac1aa57d0c0500e7e80cacfcbfcb44aec16b6c5c6a0150e
analysis log:
  /tmp/phase08_8_v8_12_visible_analysis.log
analysis log SHA-256:
  4ac9d5a162c8172d61a55329e558ba7970324319cea92083eeabc45c927f699a
analysis manifest SHA-256:
  078c42b9a5a7eeb296a4c65462f8529dffd028a96ac1598285df510ff2455882
analysis artifact-list SHA-256:
  c54fcba851217adcf58d6dc1865a9e1fbaeeb7d55450b69fb73597398389a3de
```

Analysis directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_12_interior_anchor_probe/2026-07-31/
  20260731T231351648763Z_simulation_phase08_v8_12_interior_anchor_visible_probe-
  v8_12_interior_anchor_r1p25_a45_rati_439a8eac/analysis/phase07
```

All nine standard plots exist:

| Plot | SHA-256 |
|---|---|
| `trajectory_sources_fills.png` | `24ab2d0727e4a0525be91d022f2efaf3854a730c5b2ab99120e0d147a54c83d0` |
| `cost.png` | `d59e89478314e07e8a3419ad1f4cb5029e3b7b8360eded409ba30caf291c188f` |
| `candidate_ranking.png` | `f43db649bad56209a1f5c17a499207bf033e20c26707d39cba0aeb3ba7e768b4` |
| `components.png` | `3e96e78c22de57ddc3eb44b93c958c090587f0ee5bd3a8b3bb17b43ed0f3ad80` |
| `state_events.png` | `a365beb846440c740e592921e7866e42f2464853a1949a44d920d3401ff52cfc` |
| `weights.png` | `2cc88030778c20a3d588f79e5236904887a427e95b29bb8abad6a7086b43128b` |
| `command_saturation.png` | `041a8ec1f63a74ce6d0ce9b30eb6258a87d9ed9caabcf3d7ae36ab8a3338dafd` |
| `radial_escape.png` | `1329b010928535a617f0a6e788be73a1bb22a91e3b3f71ad97f4361c32060056` |
| `gaussian_history.png` | `c32d4971a7ce74747fc3216c4462a03bdf3c086ff21f1f0b365bcf2890d21714` |

Visual inspection of the trajectory, candidate-ranking, and cost plots
confirms a start near the origin, motion into and around the first basin, one
fill near that basin, escape and transit toward the second source, final
motion near the global basin, and clear candidate-one/candidate-two raw-cost
separation.

The analyzer initially reported no plots only because the follow-up shell
looked in the nonexistent `analysis/plots` directory. The standard output was
already complete under `analysis/phase07/plots`; the analyzer was not rerun.

## Runtime and next boundary

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process remains active. The one run, bag, summary, result, analysis, and plots
are retained. No retry occurred.

The next action is the Phase 08 visible-result checkpoint and commit. Only
after that may a separately checkpointed and committed boundary authorize the
fixed headless matrix seeds `20031..20034`.
