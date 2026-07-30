# Phase 08.7 M4.1 visible-probe report

## Authority and immutable boundary

The user authorized one fresh visible two-light probe after qualifying the
M4.1 multi-publisher timestamp-evidence correction. The correction was
committed at `7068a5f27a30918e38829548a359e7a66ae25df5`; the dispatch
checkpoint was committed at `a8a0cb5`.

The retained M4 run remains a formal failure. M4.1 did not overwrite, retry,
relabel, or reuse its case, seed, run ID, evidence root, or completeness
document. The fixed eight-case suite and optional three-light probe were not
run.

## Fixed input and execution

```text
suite:       phase08_v7_m4_1_visible_probe
version:     phase08-v7-m4-1-probe
case:        v7_m4_1_probe_r1p5_a45_h25_18207
case key:    b5ac3146c6bb6b91c3d374031b3531d34c4a7506f03728c3688ae73cb7159400
seed:        18207
scenario:    2d881faa180c18c0b423671f12f91868e2b12d484a533909f607fef8372ca313
ROS domain:  159
GUI:         visible
```

The run is retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_1_probe/
  2026-07-30/
  20260730T063749069795Z_simulation_phase08_v7_m4_1_visible_probe-
  v7_m4_1_probe_r1p5_a45_h25_18207-robust_gaussian_v_a3af59ef
```

The runner started at `2026-07-30T06:37:48.094925Z`, completed at
`2026-07-30T06:45:09.172394Z`, and returned `1` because the combined
behavioral contract failed. The recorder returned `0` without timeout.
Cleanup passed with no remaining new ROS nodes or session processes.

A combined preflight/dispatch shell wrapper first stopped before launch
because its process guard matched the wrapper's own later `run_scenario`
command text. It created no evidence root and started no Gazebo process. The
guard and launch were then separated; the one actual attempt above is the
only M4.1 Gazebo run.

## Result

The formal M4.1 visible-probe result is **FAIL: Stage B global proximity not
reached**.

```text
recording completeness:                   PASS
exact /joint_states owners:               PASS
multi-publisher timestamp scope:          PASS
all typed stamps inside /clock:           PASS
singleton/event timestamp nonregression:  PASS
Stage A local recovery:                   PASS
exact fill cardinality 1/1:               PASS
Stage B primary 1.20 m proximity:         FAIL
collision expectation false:              PASS
forbidden in-readiness states/events:      PASS
final zero/readiness/cleanup:              PASS
combined result:                           FAIL
```

This cleanly separates the two conclusions:

1. the M4.1 evidence correction works and removes the false merged
   `/joint_states` failure without weakening clock or singleton checks;
2. the fresh fixed seed exposes a genuine post-recovery navigation failure.

## Evidence-correction proof

All `48` completeness checks passed. The resolved exact owners and ordering
scope are:

```text
topic: /joint_states
expected:
  /joint_state_broadcaster
  /turtlebot3_joint_state
resolved:
  /joint_state_broadcaster
  /turtlebot3_joint_state
ordering: multi_publisher_within_clock
```

`simulation_clock_monotonic`, `typed_timestamps_nonregressing`,
`typed_timestamps_within_clock`, `final_commands_zero`, and
`final_readiness_false` all passed. Read-only sqlite `PRAGMA quick_check`
returned `ok`; the bag contains `768,138` messages.

Standard analysis returned `0` with `analysis_status: complete`, no analysis
or recording failure, eight plots, and eleven tables under:

```text
analysis/phase07
```

The three analysis warnings are existing assumed fallbacks for channel index,
sync tolerance, and supervisor publish rate; none invalidates an applicable
metric or acceptance predicate.

## Stage A evidence

The accepted in-readiness path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Key ROS simulation times were:

```text
convergence confirmation:  279.9 s source time
VERIFY_EXTREMUM:            280.0 s
DESIGN_OR_MERGE_FILL:       289.0 s
ESCAPE_REPULSE:             289.2 s
RECENTER:                   297.5 s
resumed SEARCH:             311.0 s
```

Exactly one cluster was created:

```text
cluster/fill ID:             1
convergence point:           (0.9965206912, 1.0476019207) m
distance to declared local:  0.0654552587 m
distance to global:          3.5045206504 m
fill center:                 (1.1169995189, 1.0055016861) m
fill-to-convergence:         0.1276227945 m
```

There was no redesign, timeout, collision, or in-readiness `FAILSAFE`.

## Stage B evidence

After Stage A there were `1,460` valid and zero invalid noninterpolated
odometry samples. None entered `1.20 m` of `(3.5, 3.5)`.

```text
first post-A pose:       (1.7819295932, 1.4102732735) m
first global distance:   2.7053139770 m
best post-A pose:        (1.9685362975, 1.6525521679) m
best global distance:    2.3996759290 m
final in-readiness pose: (1.8995561279, 1.6673165275) m
final global distance:   2.4331356924 m
post-A duration:         49.606 s
post-A path length:      3.3343982367 m
post-A net displacement: 0.2826786800 m
best distance gain:      0.3056380480 m
```

The robot therefore moved substantially but mostly looped near the recenter
region instead of translating toward the global. The failure was not caused
by a wall margin, collision stop, safety failsafe, evidence defect, missing
fill, or premature global stop.

## Comparison with retained M4

The retained M4 behavior reached the `1.20 m` boundary, but its evidence was
formally invalid for the now-corrected reason. Its Stage A resumed `SEARCH` at
`273.6 s`, `37.4 s` earlier than M4.1. During the first equal `49.606 s`
post-A window it:

```text
traveled:                 3.1070766314 m
improved global distance: 0.9439522646 m
ended global distance:    1.6509777323 m
```

It then reached `1.1926238875 m` after `58.174 s` post-A. M4.1 traveled a
similar path length in the equal window but gained only `0.3056380480 m`.
That rules out run duration as the sole explanation.

## Diagnosis

The remaining defect is post-recovery liveness, not safety:

- the detector consumed more of the fixed run before Stage A on seed `18207`;
- recenter declared complete `0.3412297750 m` from its target, close to the
  configured `0.35 m` tolerance boundary;
- the correctly centered M4.1 fill was farther from that recenter endpoint
  than M4's less accurate fill;
- the post-recovery affine taper is fill-centered, so M4.1 resumed with only
  about `0.23` affine weight versus about `0.36` in M4 and then tapered toward
  zero as it moved away from the fill;
- the selected direction remained safe and broadly global-facing, but the
  supervisor has no post-recovery translation-progress monitor while the
  controller traces loops in `SEARCH`.

This creates an undesirable coupling: a better-localized fill plus a
legal-but-loose recenter endpoint can provide less assistance than an
off-center fill. Neither exact topology nor the existing retry counters
detect the resulting low-net-progress loop.

## Bounded correction recommended for a fresh version

No further correction or Gazebo run is authorized by M4.1. A fresh M4.2 Plan
should qualify these changes before another visible attempt:

1. start a new post-recovery guidance epoch at `RECENTER_COMPLETE`, with its
   spatial taper based on demonstrated displacement/progress away from the
   active fill rather than only distance from the fill support boundary;
2. recompute and revision-stamp the safe post-recovery direction at that
   boundary instead of carrying escape-era geometry implicitly;
3. add a bounded post-recovery liveness monitor that detects high path length
   with low net displacement and requests direction refresh/recenter rather
   than immediately entering `FAILSAFE`;
4. make recenter completion reliably place the robot near the intended room
   center while retaining recoverable wall/collision handling;
5. reset only the robust GESC search epoch/history that is invalidated by
   supervisor-owned escape/recenter motion, preserving legacy behavior;
6. allocate an explicit post-Stage-A time budget so variable local-detection
   latency cannot consume the global-search window, without weakening the
   `1.20 m` proximity gate.

The fixed eight-case suite and optional three-light run must remain blocked
until one separately versioned, committed visible two-light probe passes the
corrected evidence contract, Stage A, Stage B, collision, cleanup, and
combined gates.

## Retained hashes

```text
a76a53efe3278f63422f76127cc1645f1e3699affbc30d49e0c0b8e235cc72b9  suite summary
afd4cbd707004e2a8b6965ea08f1db1329a08ff816ff0965b821d95f28a0fcc0  completeness
9d32cd59513df7c421e7f63abe5b78fd86ba9432d16c6f680a16f68623d88ba5  scenario result
7a8a020b0a9ea024650ac4bc89530d2dfc9e975fb605db6571e2b98477ec15f0  resolved scenario
ab7c48a8af70b381b5a18344de823ac62ce7be31c077a4e594139bc57e9f9091  resolved topics
abf2e450526822113e6dc00a8fe34e18f7dd05eede2f96ee1855efe4b91ab4b7  sqlite bag
97467b02da76a65520ce3be73a8968432ec9d49aaae4c354ad61813c4760274d  analysis completeness
b7660596c7eb393192cc93c58042ec8cfd2bfa0b274627407ac719a59d40c147  summary metrics
```
