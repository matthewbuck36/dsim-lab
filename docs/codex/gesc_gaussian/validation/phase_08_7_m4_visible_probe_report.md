# Phase 08.7 M4 Visible-Probe Report

## Disposition

Phase 08.7 M4's one fixed visible two-light probe is retained as a **formal
FAIL caused by recording-evidence validation**. The robot behavior itself
passed Stage A, exact fill cardinality, primary Stage B, collision, forbidden
state/event, and clean-shutdown predicates.

The fixed eight-case two-light suite and optional three-light probe were not
run. M4 forbids either dispatch after a visible-probe infrastructure failure,
and this attempt will not be retried or relabeled.

## Qualified input and dispatch

The qualified implementation and dispatch commits were:

```text
19d413c9c129bcda9cf953741c95ed42c5913bc4  M4 implementation/input
6165cd9                                     committed visible dispatch
```

The exact visible scenario SHA-256 was:

```text
37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1
```

Exactly one attempt ran in visible Gazebo on ROS domain `153`, with seed
`18201`, case key
`a7d115b9893ee9b4ee0885a477820125ad68e21c93da689d858f69dc9aca9c32`,
and the predeclared `360 / 540 / 45 s` run, wall, and shutdown bounds.
The outer bounded command returned `1`; it did not time out.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe/
  2026-07-30/
  20260730T054527662523Z_simulation_phase08_v7_m4_visible_probe-
  v7_m4_probe_r1p5_a45_h25_18201-robust_gaussian_v1-a7_e99d857b
```

Suite summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe/
  phase08_v7_m4_visible_probe_summary.yaml
```

## Behavioral result

The observed in-readiness state path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Stage A passed under `verified_trap` association:

- one completed recovery episode;
- one convergence confirmation at source time `248.5 s`;
- convergence point `(1.2973842210, 1.3772928572) m`;
- exactly one created, typed, and active cluster, identity `1`;
- fill center `(1.1108335595, 1.3813284464) m`;
- fill-to-convergence distance `0.1865943066 m`;
- nearest declared-local distance `0.3953410337 m`, reported diagnostically;
- convergence-to-global distance `3.0589870683 m`;
- one successful escape in `8.775931438 s`;
- recenter start and complete events present;
- no redesign escalation, escape failure, timeout, or in-readiness failsafe.

Primary Stage B passed and triggered the live operator-equivalent stop on a
noninterpolated odometry sample:

```text
position:                 (3.1291616104, 2.3595487198) m
distance to global:       1.1992290164 m
primary radius:           1.20 m
valid post-A samples:     1710
invalid post-A samples:   0
interpolation used:       false
```

The final classified pose was `(3.1339323703, 2.3649465971) m`, or
`1.1926238875 m` from the global. The optional `1.00 m` closer diagnostic was
false and remained non-gating, as declared.

The bag reports one created/active fill, one successful escape, no collision,
no forbidden state/event, no in-readiness failsafe or timeout, and terminal
`SEARCH`. The path length was `20.3449037600 m`. The controller-goal
diagnostic remained false because M4 intentionally uses post-recovery global
proximity rather than `GOAL_REACHED` or `GOAL_HOLD`.

## Formal recording failure

The sole completeness failure was:

```text
typed ROS timestamps regressed by more than 0.150 s
```

The recorded detail was confined to `/joint_states`:

```text
previous header stamp: 271.747 s
current header stamp:  271.522 s
apparent regression:   0.225 s
bag receipt gap:       1.299762 ms
```

All other relevant recording checks passed, including:

- simulation `/clock` monotonicity;
- every typed stamp within the recorded `/clock` range;
- AlgorithmEvent producer identification, freshness, and source causality;
- all required topics and parameter snapshots;
- readiness and no-motion-before-readiness;
- final readiness false and all final command representations zero;
- clean shutdown metadata and console;
- collision evidence;
- strict finite JSON.

Cleanup passed with no remaining new ROS nodes or session processes.
Read-only sqlite `PRAGMA quick_check` returned `ok`. Standard analysis returned
`0`, retained eight plots and eleven tables under `analysis/phase07`, and
correctly reported `analysis_status: partial` because the immutable
completeness result is failed.

## Root cause

The recorded graph intentionally has two `/joint_states` publishers:

```text
/joint_state_broadcaster
/turtlebot3_joint_state
```

The resolved manifest records both publisher endpoints and does not declare
`/joint_states` singleton. Read-only deserialization separated two stable
message signatures and showed:

```text
merged topic:                     42,950 messages; 1 backward jump; maximum 225 ms
effort-present signature:         33,181 messages; 0 backward jumps
effort-empty signature:            9,769 messages; 0 backward jumps
```

The apparent rollback was three delayed effort-empty messages being received
after a newer effort-present message. It was cross-publisher callback/bag
ordering, not either producer's source clock moving backward.

The earlier passing M2.3 visible bag has the same two publishers and ten
merged-order rollbacks, but their maximum was only `1 ms`, below the fixed
`150 ms` tolerance. Thus the current pass/fail distinction depends on GUI
scheduling of a deliberately multi-publisher topic rather than source-time
integrity.

The validator currently special-cases `AlgorithmEvent` by identifiable
producer but otherwise applies one monotonic sequence to every topic. That
model is invalid for a merged topic whose messages do not carry publisher
identity. This is an evidence-validator integration defect, not a
wall-margin, recenter, affine, collision, or behavioral stop.

## Required fresh correction

A separately authorized and versioned correction should:

1. keep `/joint_states` required, typed, recorded, and checked against
   simulation `/clock`;
2. declare and verify its exact two expected publisher owners;
3. apply per-topic nonregression only to singleton streams, or per producer
   where producer identity is recoverable;
4. retain strict nonregression for every singleton algorithm/control/source
   stream and the existing per-producer AlgorithmEvent check;
5. add fixtures proving a delayed but individually monotonic two-publisher
   merge passes, an unexpected publisher fails, either identifiable producer
   regression fails, and out-of-clock stamps still fail;
6. qualify and commit the evidence correction before one fresh, versioned
   visible probe under a new evidence root.

The retained M4 attempt must remain failed. The correction must not increase a
global timestamp tolerance, suppress clock-range checks, alter navigation
values, or reuse this run as a fresh pass.

## Immutable evidence hashes

```text
9d3dfc0468c9b94a6f9129738bc2c6aca80bca17b20bc63925f53fb79d22cc0b  suite summary
a2905ba2a1c2cd66600cd1a789ac0e61b3adfeeed6d10c8e7b632641490be262  scenario_result.yaml
4acc311734e63896faf33c07439b7c1c81e9ebdcd6902b0514bf9c9ce0846e88  completeness.json
22e9845e2a60a2ddafc039458bf20fd5e6e6d1ac3fc2455414c70cd3d74123b3  bag/bag_0.db3
0dc86d0d8fd2684edcc9504c1300120ae66f1fc274d2bdfe30d05fe6fe24f306  analysis/phase07/summary_metrics.json
8d67ee44970c6d6b4a76b2d355f6cc57afe5b6a5043867aafbf8f61aecab671c  analysis/phase07/analysis_completeness.json
```

M4 remains simulation-only. Phase 09 and all physical commands remain
unauthorized.
