# Phase 08.8 M8.3 v8.11 Secondary Visible Probe

Date: 2026-07-31
Committed dispatch boundary: `66c7e8e`
Scenario: `phase08_v8_11_secondary_visible_probe.yaml`
Case: `v8_11_secondary_probe_r1p5_a67p5_h25_19901`
Seed: `19901`
Profile: `robust_gaussian_v1`

## Disposition

**PASS — 14/14 FORMAL PREDICATES, ONE TOPOLOGY-BOUND LOCAL RECOVERY,
STRICT SECOND-CANDIDATE RANKING, GRACEFUL GLOBAL-PROXIMITY STOP, COMPLETE
RECORDING/CLEANUP, AND 9/9 PLOTS.**

The single authorized visible run executed once with no retry. It confirmed
the shifted aggregate-field basin, created exactly one typed fill at the
measured basin, escaped through the accepted direct-repulse branch, restored
ordinary GESC ownership, confirmed and strictly ranked candidate two, entered
`GOAL_HOLD`, and triggered the evaluator-only post-recovery proximity stop
`0.185837 m` from the declared global.

This is the first fresh empirical v8.11 result. It does not alter the fixed
v8.10 secondary failure.

## Frozen dispatch and retained evidence

```text
dispatch commit:
  66c7e8e462dafe33e2cf5c3b6df4a14c60758940
installed scenario:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_11_secondary_visible_probe.yaml
installed/source SHA-256:
  ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0
ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY:
  222 / 1
presentation:
  visible Gazebo GUI
attempts / retries:
  1 / 0
```

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_probe/scenario_summaries/
  20260731T210056130307Z_phase08_v8_11_secondary_visible_probe.yaml
SHA-256:
  4f038f241e35d0e25de0a7e1f5b61b1fa01222f21f718b3c1e2cf7fccd13dd98
```

Exact summary-owned run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_probe/2026-07-31/
  20260731T210056770365Z_simulation_phase08_v8_11_secondary_visible_probe-
  v8_11_secondary_probe_r1p5_a67p5_h25_19901_c0544b8e
```

```text
started:                         2026-07-31T21:00:56.130307Z
completed:                       2026-07-31T21:05:41.464572Z
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
commit:            66c7e8e462dafe33e2cf5c3b6df4a14c60758940
dirty:             false
untracked_paths:   []
```

Dispatch log:

```text
/tmp/phase08_8_v8_11_secondary_visible_dispatch.log
SHA-256:
  eea33ce52f6c0bbe1657bf883410b1903e4e48364d6c6f7008718a796c341d50
```

The outer shell's preliminary `git status` was accidentally issued from
`/tmp` and printed a nonrepository warning to stderr. The check did not stop,
restart, or duplicate the run. Installed scenario parity had already been
proved, and the authoritative recorder metadata above independently records
the clean committed checkout. This was a shell-side preflight issue, not a
runner, recorder, controller, or evidence issue.

## Topology-bound Stage A

Observed accepted path:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
```

The first candidate and one fill were:

```text
convergence sim time:               85.0 s
observed convergence:               (1.1937773, 1.8373593) m
declared local lamp:                (0.5740251, 1.3858193) m
convergence-to-local diagnostic:    0.7667992 m
declared-local distance gate:       not applied
fill center:                        (1.1844564, 1.8233879) m
fill-to-convergence:                0.0167952 m
convergence-to-global:              2.8430683 m
created / typed / active clusters:  [1] / [1] / [1]
unassigned clusters:                []
Stage A completed:                  116.032 sim s
```

The topology qualification hash is:

```text
eb749f0cb86f7b35231bdc308365f3008c6168df07b0188c03a97f339f364d71
```

Its noise-adjusted basin depth, raw separation, basin-center separation, and
forward alignment are respectively `0.859534`, `0.988770`, `3.644390 m`, and
`0.851271`. The record includes valid source/start/bounds/disturbance/model/
sensor bindings.

## Escape ownership and strict ranking

The direct-repulse branch passed:

```text
branch / evidence:
  direct_repulse / bounded_direct_repulse_schema_v13
repulse state / raw-control samples:
  432 / 2,792
supervisor command samples:
  432
mature radial-progress samples:
  372
maximum radial distance:
  1.428242 m
frozen exit radius:
  1.366771 m
fill-to-exit distance:
  1.438932 m
selected/actual exit alignment:
  0.983184329
ordinary GESC ownership restored:
  true
supervisor authority cleared:
  true
analysis escape duration:
  21.709817 s
```

The schema-v13 label identifies the unchanged direct-ownership evidence
contract retained by schema v14; it is not a schema downgrade.

Candidate two was strictly better in raw rotational cost:

```text
filled candidate raw-cost lower bound:  -0.2348286554
candidate-two raw-cost upper bound:      -3.8372093023
strict separation margin:                 3.6023806470
candidate ordinal / known count:          2 / 2
invalid ranked-goal events:               0
```

## Stage B and final state

The controller path completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

The first valid post-ranking proximity sample caused the graceful stop:

```text
sample sim time:                    237.412 s
sample position:                    (3.5076369, 3.6856800) m
sample global distance:             0.1858370 m
proximity radius:                   0.50 m
valid / invalid samples:            1 / 0
interpolation used:                 false
graceful global-proximity stop:     true
final position:                     (3.5076223, 3.6856544) m
final global distance:              0.1858108 m
terminal state:                     GOAL_HOLD
```

The physical controller still has no coordinate stop; physical arrival
remains manual operator `Ctrl+C`.

## One-time analysis and plots

The exact summary-owned run was analyzed once:

```text
analysis status / failures:  complete / []
fresh Phase 05 validation:   PASS
stored Phase 05 validation:  PASS
recording failures:          []
raw bag SHA-256:
  e387f1be0a5410f2ef2dd8efa76d00d505e4a109d5a5a15c89c7cb67c1f9a402
analysis log:
  /tmp/phase08_8_v8_11_secondary_visible_analysis.log
analysis log SHA-256:
  b69deff2b0b655a6149fa272716d0f176d083cb97c90bb872b19ed17a67bb74a
```

Analysis directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_probe/2026-07-31/
  20260731T210056770365Z_simulation_phase08_v8_11_secondary_visible_probe-
  v8_11_secondary_probe_r1p5_a67p5_h25_19901_c0544b8e/
  analysis/phase07
```

All nine standard plots exist:

| Plot | SHA-256 |
|---|---|
| `trajectory_sources_fills.png` | `9181be5c6361944618e7417fd2917b5abb2885eda22c2234958b8c9a9e5b497c` |
| `cost.png` | `6085abbd52f44578971fc2cf00ab2d6e069e344687a45210299c40d497a95a85` |
| `candidate_ranking.png` | `361c674dcaa6b9b072d7812367407eb57907a564e50b49f6241001bf2486e47a` |
| `components.png` | `3b9049ea5fb612d95251cff1eae73188979dbdff43ca94883c698682499806db` |
| `state_events.png` | `348d66fbab9e9a334648261668e6d3fc433ebaca540ce67af86719647b9d570c` |
| `weights.png` | `d0f90f5e45b82d8e1ef929d9617f4b90b5739e5148b8584e6bbc8191bb634b7d` |
| `command_saturation.png` | `a14df5104d75455dafc57e930d836f6235e79e882fdc2a211386339f0aca698f` |
| `radial_escape.png` | `0dbc769dfc54aca3dfd395d7e388f2ae2ad5d59202bdf25e795d91c62a8eee50` |
| `gaussian_history.png` | `23f735905830aa407ddf70fe59e18f0e74a72dc8c3de3e176b81375413311d3f` |

Visual inspection confirms the shifted first basin and fill, direct escape,
ordinary transit toward the second source, final global orbit, and clear raw
cost separation between candidate one and candidate two.

## Runtime boundary

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process remains active. The one run, bag, summary, result, analysis, and plots
are retained. No retry occurred.

The next action is the Phase 08 result checkpoint and commit. Only after that
may a separately checkpointed and committed boundary authorize the fixed
headless seeds `19911..19915`.
