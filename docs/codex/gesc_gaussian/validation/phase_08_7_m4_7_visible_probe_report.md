# Phase 08.7 M4.7 visible-probe report

Date: 2026-07-30
Result: FAIL
Infrastructure: PASS
Behavioral gate: Stage B FAIL
M4.7 source-resume corridor: NOT ARMED
Conditional suite: NOT RUN

## Immutable attempt

The one predeclared M4.7 visible attempt ran once on ROS domain `167`:

```text
suite: phase08_v7_m4_7_visible_probe
case:  v7_m4_7_probe_r2p0_a45_h25_18508
seed:  18508
key:   e48c200b54a7a9d9049b5965ef9c773b166e6672df155f0d9ccff459da83f3e8
```

The dispatch began at `2026-07-30T19:29:00.318676Z` and completed at
`2026-07-30T19:34:38.950422Z`. The outer timeout did not fire. The recorder
returned `0`; the runner returned `1` because the combined behavioral gate
failed.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe/
  2026-07-30/
  20260730T192901277523Z_simulation_phase08_v7_m4_7_visible_probe-
  v7_m4_7_probe_r2p0_a45_h25_18508-robust_gaussian_v_97a8eeda
```

No retry, in-run parameter change, headless-suite case, three-light case,
Phase 09 action, physical action, or hardware action occurred.

## Gate result

```text
controller startup and readiness: PASS
recording completeness:           PASS
cleanup:                          PASS
collision expectation:            PASS, no collision
forbidden states/events:           PASS, none in readiness
final zero/readiness false:        PASS
required recovery path/events:     PASS
Stage A local recovery:            PASS, 1 episode
unique fill cardinality:           PASS, exactly 1
Stage A time budget:               PASS
complete Stage B opportunity:      PASS, 120.020 s observed
Stage B global proximity:          FAIL
non-gating 1.00 m diagnostic:      FAIL
combined result:                   FAIL
```

Stage A completed at simulation time `157.610 s`. The full Stage B window
ended at `277.630 s`, position
`(1.5263398997, 1.3052441668) m`, distance `2.9516584082 m` from the
declared global. The final recorded position was
`(1.5273326808, 1.3062117783) m`, distance `2.9502750912 m`.

There were `3534` valid post-Stage-A noninterpolated odometry samples and
zero invalid samples. None entered the unchanged primary `1.20 m` radius or
the non-gating `1.00 m` radius. Read-only trajectory reconstruction found
the best post-Stage-A sample at:

```text
position:        (1.2300854352, 1.9567113561) m
global distance:  2.7448591895 m
```

## M4.7 corridor disposition

The first recovery completed normally and source-led handoff began at:

```text
simulation time: 157.500 s
anchor:          (1.2030928310, 1.8535194744) m
fill center:     (1.8363033400, 1.7101248567) m
fill distance:    0.6492438410 m
```

At `169.500 s`, source-led handoff stalled:

```text
window path:          0.9526722200 m
net displacement:     0.1953251769 m
outward progress:    -0.0264521076 m
```

The supervisor therefore armed generic fallback guidance. It did not emit
any of M4.7's source-continuity bypass, source-resume corridor,
direction-change, clearance, projected-progress, completion, or exhaustion
events.

Read-only reconstruction at the stall boundary gives:

```text
measured source direction:        (0.0693310876, -0.9975937050)
radial outward direction:         (-0.9965091969, -0.0834830556)
radial/source dot:                 +0.0141931043
configured reversal threshold:    -0.80
source/global-direction alignment: -0.5248527808
```

The detector correctly rejected this geometry: the fallback radial
direction was not reversing the measured source-led direction. More
importantly, the measured source-led displacement itself pointed mostly
downward and away from the true global. Global distance worsened by about
`0.1075 m` over this source-led window.

The subsequent sequence was the retained generic M4.6-style recovery:

```text
192.500 s  liveness direction refreshed
204.500 s  recoverable recenter requested
219.200 s  second recenter completed; new guidance epoch started
243.100 s  liveness released guidance to ordinary search
277.630 s  complete Stage B opportunity ended
```

M4.7's new selector, dynamic source reacquisition, source-resume progress
leg, and corridor release logic were consequently never exercised by this
attempt. The visible result does not qualify those mechanisms empirically.

## Failure mechanism

The fixed paired seed did not reproduce M4.6's pre-arm geometry. M4.6
measured a source-led direction aligned toward the global and a
radial/source dot of `-0.9383691118`; this M4.7 attempt measured a
global-opposing direction and a dot of `+0.0141931043`.

M4.7 changes behavior only after the reversal detector arms. Since the
detector did not arm here, the new corridor could not correct the later
behavior. The run instead consumed the retained liveness refresh and
recenter, released to ordinary search, and remained far from the global
until the complete Stage B boundary.

The supported diagnosis is:

```text
Stage A recovery:                    PASS
source-led handoff:                  EXECUTED
measured source direction:           GLOBAL-OPPOSING
reversal detector decision:          CORRECTLY NOT ARMED
M4.7 corridor selector/release:      NOT EXERCISED
generic liveness/recenter fallback:  EXECUTED
post-recovery global proximity:      FAIL
combined behavior:                   FAIL
```

One seeded ROS/Gazebo execution is deterministic at the declared input
level but is not evidence of bitwise-identical continuous trajectories.
The pre-arm difference demonstrates sensitivity in the live handoff
geometry; it does not by itself isolate scheduler, physics, or controller
timing as the cause.

## What did not cause the failure

This was not a wall-margin, collision-failsafe, room-boundary, startup,
recording, fill-cardinality, staged-budget, or global-stop failure.

During Stage B:

```text
x range:                         [0.5366039955, 1.5282551959] m
y range:                         [1.1105612286, 2.1692042906] m
minimum physical-wall clearance:  0.7866039955 m
minimum wall-inset clearance:      0.5866039955 m
post-Stage-A path:                 8.6652725566 m
```

No collision, algorithm `TIMEOUT`, in-readiness `FAILSAFE`, or
room-boundary event occurred. The stop was the planned `120 s` staged
monitor boundary. Relaxing the already operator-equivalent `1.20 m` global
stop cannot convert a best distance of `2.745 m` into success.

## Standard analysis and integrity

The standard analyzer ran exactly once into `analysis/phase07` and returned:

```text
analysis_status: complete
analysis failures: none
plots:  8
tables: 11
```

Fresh Phase 05 validation passes. Standalone installed `validate_run` also
passes. Read-only SQLite validation returns:

```text
PRAGMA quick_check: ok
messages: 587675
topics: 34
```

The bag hash was unchanged before and after analysis.

## Retained hashes

```text
cb87797d861017fe56f76262c6a818016607effafc234ff7c34afe0d50a1eead
  visible suite summary
2607e0ebadae1433c4c53ddcd7d0fc4f45f374b7e0e598c2917ed6f0b3db3ee8
  completeness.json
88a191d03bcc0cc823ddf36e1e69f0451889b3437c7a26329d39ac75954fd747
  scenario_result.yaml
8cea7809713aae717cf7bb3f6021f164b7dcf8830f43a753f6712a0dbc71c0ac
  bag/bag_0.db3
d497740ffea3cea2784a10e657420d69bc0eb36ec0257bc3e9afc388c04ed182
  analysis/phase07/analysis_completeness.json
65f7b8956a7c228f451d488b3032477d3cf5e111ba53cd51d525f9a2e4dfd992
  analysis/phase07/summary_metrics.json
728d90c0109a90c66e4b5b2c4c0a9a895e6d0f2360a00c0ab04dba4f3aebdf14
  resolved_scenario.yaml
1da37b5cdb8158723a937969447806e4d5e9e12b8f458e72fbb5764a0cb237ca
  scenario_definition.yaml
2607e0ebadae1433c4c53ddcd7d0fc4f45f374b7e0e598c2917ed6f0b3db3ee8
  /tmp/phase08_7_m4_7_validate_run.json
cbb1e31066e409c0818edddbec698acbad462bcbcd8cb46714385a62d464578f
  /tmp/phase08_7_m4_7_event_timeline.json
```

## Stop boundary

M4.7 is closed failed and cannot be retried, overwritten, relabeled, or
counted as a pass. The fixed M4.7 headless suite did not run and its evidence
root remains absent. Cleanup reconfirmed no Gazebo, runner, recorder,
analyzer, rosbag, validator, or matching launch process.

Any further correction requires a fresh reviewed version, fresh identities,
no-Gazebo qualification, checkpoint, and commit before another simulation.
