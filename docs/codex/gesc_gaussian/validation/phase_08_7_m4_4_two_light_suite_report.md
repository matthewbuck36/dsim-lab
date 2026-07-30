# Phase 08.7 M4.4 Two-Light Suite Report

## Verdict

The fixed M4.4 serial two-light qualification is **CLOSED / FAIL**. The
visible probe passed, but the eight-case suite produced five complete
behavioral passes, two complete behavioral failures, and one
infrastructure-invalid startup attempt. The readiness rule requires every
fixed attempt to pass.

The retained aggregate is:

- fixed visible probe: `1/1` passed;
- spatial suite cases: `3/5` passed, one failed, one unavailable;
- repeat suite cases: `2/3` passed;
- suite combined result: `5/8` passed;
- visible plus suite combined result: `6/9` passed;
- Stage A local recovery: `7/8` passed, one unavailable;
- exact one-fill cardinality: `7/8` passed, one unavailable;
- Stage B global proximity: `5/8` passed, two failed, one unavailable;
- complete Phase 05 recording: `7/8`, each complete case `48/48`;
- cleanup: `8/8`;
- non-ground collision absence: `7/7` behavioral attempts;
- forbidden in-readiness state/event absence: `7/7` behavioral attempts.

M4.4 corrected the retained M4.3 corner recenter failure: the former
fixed-horizon corner case now passed Stage A and Stage B without `FAILSAFE`.
It did not establish two-light readiness. No case was retried or changed, and
the optional three-light probe did not run.

## Fixed execution

The exact committed suite input had SHA-256:

```text
78be277362ac060c7cb77c5d2215836cb914a95bd81a5ed9221f0db4bc62a188
```

It ran once, serially and headlessly, on ROS domain `164` from the isolated
M4.4 install:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_4_qual/install/setup.bash
export ROS_DOMAIN_ID=164
export ROS_LOG_DIR=/tmp/phase08_7_m4_4_suite_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_4_suite_mpl
export TURTLEBOT3_MODEL=burger
timeout --signal=INT --kill-after=90s 5400s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_4_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_4_two_light_suite.yaml \
  --operator Codex \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4/\
phase08_v7_m4_4_two_light_suite_summary.yaml
```

The suite started at `2026-07-30T10:55:19.930174Z`, completed at
`2026-07-30T11:38:21.719708Z`, and returned `1` because the fixed gate did
not pass. The outer timeout did not fire. All eight cases executed exactly
once in committed order.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4/
  phase08_v7_m4_4_two_light_suite_summary.yaml
```

## Per-case result

| Fixed case | Infrastructure | Stage A | Stage B | Combined | Recording | Cleanup | Primary observation |
|---|---:|---:|---:|---:|---:|---:|---|
| `v7_m4_4_r1p0_a45_h25_18409` | complete | pass | pass | pass | 48/48 | pass | former M4.3 corner defect passed at `1.198139 m` |
| `v7_m4_4_r1p5_a22p5_h25_18409` | invalid | unavailable | unavailable | fail | 26-check invalid | pass | velocity-controller load response was lost |
| `v7_m4_4_r1p5_a45_h25_18409` | complete | pass | pass | pass | 48/48 | pass | primary boundary reached at `1.199021 m` |
| `v7_m4_4_r1p5_a67p5_h25_18409` | complete | pass | pass | pass | 48/48 | pass | primary boundary reached at `1.199725 m` |
| `v7_m4_4_r2p0_a45_h25_18409` | complete | pass | fail | fail | 48/48 | pass | full `120.020 s` Stage B budget expired at `3.330003 m` |
| `v7_m4_4_repeat_r1p5_a45_h25_18410` | complete | pass | fail | fail | 48/48 | pass | recording ended after only `29.104 s` of the declared Stage B budget |
| `v7_m4_4_repeat_r1p5_a45_h25_18411` | complete | pass | pass | pass | 48/48 | pass | primary boundary reached at `1.196996 m` |
| `v7_m4_4_repeat_r1p5_a45_h25_18412` | complete | pass | pass | pass | 48/48 | pass | primary boundary reached at `1.198603 m` |

The `1.00 m` closer diagnostic remained non-gating. None of the seven
behavioral attempts collided, entered `FAILSAFE`, emitted a forbidden event,
or violated final-zero/cleanup.

## Corrected corner behavior

Case `v7_m4_4_r1p0_a45_h25_18409` is the fresh regression for the retained
M4.3 corner failure. It completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Adaptive recenter therefore removed the false terminal classification at the
wall/fill pinch. Its source-led handoff started at simulation time `162.2 s`,
stalled at `174.2 s` after `0.592642 m` path and `0.142868 m` net
displacement, then completed the existing fallback at `192.8 s` with
`1.105223 m` outward progress. Stage B passed at `1.1981386677 m`.

This is direct evidence that the M4.4 wall-margin correction works. It is
also evidence that the remaining failures are not caused by collision or an
overly eager wall `FAILSAFE`.

## Infrastructure-invalid startup

Case `v7_m4_4_r1p5_a22p5_h25_18409` never reached operational readiness.
Gazebo's controller manager accepted and loaded `velocity_controller`, but
the Humble spawner did not receive the first `/load_controller` response.
After its fixed internal `10.0 s` wait it repeated the non-idempotent load,
received “controller already loaded,” and exited `1`:

```text
controller_manager: Loading controller 'velocity_controller'
controller_manager.rclcpp: failed to send response to
  /controller_manager/load_controller (timeout)
spawner_velocity_controller:
  Failed getting a result ... in 10.0. (Attempt 1 of 3.)
controller_manager:
  A controller named 'velocity_controller' was already loaded
spawner_velocity_controller:
  Failed loading controller velocity_controller
```

The launched command did contain `--service-call-timeout 30.0`, but the
installed Humble spawner calls `load_controller(...)` without forwarding
that value; the service helper therefore retained its internal `10.0 s`
default. This is a controller-startup idempotency defect, not behavioral
evidence.

The attempt was retained as `infrastructure_invalid`, cleanup passed, and its
partial bag returned SQLite `quick_check: ok`. The completeness file
correctly failed nine of its 26 available checks. No Stage A or Stage B
result is available and the attempt is not counted as a behavioral pass.

## Behavioral failure: exact fallback reversal

Case `v7_m4_4_r2p0_a45_h25_18409` passed Stage A, exact one-fill
cardinality, recording, collision, forbidden-state/event, final-zero, and
cleanup predicates. Its accepted fill was:

```text
fill center:             (1.8278297781, 1.7700514862) m
support radius:           0.5086747487 m
avoidance radius:         0.6086747487 m
```

The first post-recovery anchor was `(1.2320122160, 1.4710422281) m`.
During the source-led window, ordinary raw-plus-Gaussian GESC traveled
`0.619500 m` and translated `0.163114 m` toward
`(1.3775, 1.5451) m`. That displacement was strongly aligned with the
northeast route, reducing the evidence-only distance to the declared global
from `3.043 m` to `2.886 m`.

Because net displacement did not exceed the fixed `0.20 m` threshold, M4.4
classified the window as stalled. The unchanged fallback then selected
`(-0.894328, -0.447412)`, the radial direction maximizing fill clearance.
Its dot product with the observed source-led displacement direction was
approximately `-1.000`; it was an exact reversal. Its evidence-only
alignment with the northeast global route was approximately `-0.961`.

The retained segment evidence is:

| Segment | Simulation interval | Path | Net | Global distance, start/min/end | Fill distance, start/end |
|---|---:|---:|---:|---:|---:|
| source-led | `149.9-161.9 s` | `0.623 m` | `0.163 m` | `3.043/2.886/2.886 m` | `0.667/0.503 m` |
| fallback before refresh | `161.9-192.1 s` | `2.214 m` | `0.768 m` | `2.886/2.798/3.638 m` | `0.503/1.271 m` |
| refreshed fallback | `192.1-205.0 s` | `0.756 m` | `0.250 m` | `3.636/3.623/3.828 m` | `1.269/1.435 m` |
| recoverable recenter | `205.0-221.3 s` | `0.976 m` | `0.786 m` | `3.827/3.096/3.096 m` | `1.435/0.799 m` |
| guided after recenter | `221.3-248.0 s` | `1.893 m` | `0.595 m` | `3.096/3.006/3.677 m` | `0.799/1.384 m` |
| ordinary SEARCH | `248.0-270.0 s` | `1.529 m` | `0.825 m` | `3.673/3.327/3.328 m` | `1.381/0.926 m` |

The typed sequence was:

```text
149.9 s  source-led handoff started
161.9 s  source-led handoff stalled; fallback armed
192.1 s  liveness direction refreshed
205.0 s  recoverable recenter requested
221.3 s  post-recovery guidance restarted after recenter
248.0 s  liveness released guidance to ordinary SEARCH
270.0 s  full Stage B budget expired
```

The final stop at `(1.2580616031, 1.0377582023) m`, `3.3300033703 m`
from the global, is not a near-boundary miss. A looser wall/collision
failsafe, a slightly larger global radius, or a longer execution timeout
would not correct the supervisor's initial exact reversal.

## Runner-budget failure

Case `v7_m4_4_repeat_r1p5_a45_h25_18410` did not receive the declared
`120.0 s` Stage B opportunity. Stage A completed only at simulation time
`452.022 s`; the fixed `480.0 s` recorder ended at `481.126 s`. The runner
therefore observed only `29.104 s` after Stage A, did not emit the
post-Stage-A timeout stop, and classified Stage B false when the process
ended.

The final distance was `1.6128810116 m`, so the robot had not yet passed the
unchanged `1.20 m` boundary. This is a scenario/runner contract gap: schema
v7 verifies only that `post_stage_a_timeout_sec < run_timeout_sec`; it does
not reserve that budget after a late Stage A completion. The behavioral
outcome remains a formal failure, but it is not evidence that the full
Stage B budget was exhausted.

## Cross-case source-led result

All seven behavioral attempts completed a first `12.0 s` source-led window
at net displacement at most `0.20 m`; none directly released as a qualifying
source-led translation. The five suite passes reached Stage B only after the
existing fill-clearance fallback was armed. Thus M4.4 proved that withholding
early affine/supervisor authority avoids an immediate forced direction, but
it did not prove source-led completion and it did not incorporate the
observed source-led displacement into fallback selection.

The radius-2.0 failure is uniquely diagnostic: its first radial fallback was
an exact reversal of a source-led displacement that was strongly aligned
with the eventual global route. Other passing cases did not exhibit that
combination. The next bounded behavioral correction should therefore:

1. retain the source-led displacement vector when it has a finite,
   meaningful magnitude;
2. detect a radial fallback that would reverse that vector;
3. choose a hard-safe forward-half-plane/tangential bypass around the known
   fill rather than authorizing the reversal;
4. use bounded affine/supervisor assistance only for that clearance bypass,
   then return to ordinary raw-plus-Gaussian SEARCH;
5. use no global coordinate, source role, or simulation ground truth.

Separately, the runner must reserve a full post-Stage-A budget, and
controller spawning must recover idempotently from the observed
loaded-but-response-lost state. These corrections should be default-off for
historical scenarios and verified before any fresh Gazebo run.

## Standard analysis and evidence health

The standard analyzer was invoked exactly once for each retained attempt.
The seven behaviorally complete bags returned analyzer code `0`; the
infrastructure-invalid startup returned code `2`, as expected for its
incomplete recording.

Six behavioral analyses report `complete`, no failures, eight plots, and
eleven tables. Case `v7_m4_4_r1p0_a45_h25_18409` reports `partial`, with no
analysis or recording failure, all critical inputs present, eight plots, and
eleven tables. One `0.358869 s` gap in `/algorithm_state` invalidated only
the derived `state_durations` metric. Its Phase 05 completeness remains
`48/48`, including motion coverage, producer attribution, typed timestamps,
final zero, final readiness false, and publisher ownership.

Read-only SQLite `PRAGMA quick_check` returned `ok` for every bag:

| Case | Messages | Analyzer |
|---|---:|---:|
| `r1p0_a45` | 406,082 | partial; state durations only |
| `r1p5_a22p5` | 22,238 | unavailable; infrastructure invalid |
| `r1p5_a45` | 733,376 | complete |
| `r1p5_a67p5` | 526,641 | complete |
| `r2p0_a45` | 570,370 | complete |
| repeat `18410` | 1,026,976 | complete |
| repeat `18411` | 603,680 | complete |
| repeat `18412` | 631,739 | complete |

## Retained hashes

Suite summary:

```text
d5ab58ad26c8329c20e08b4954697daca6a5f01bd4a821856202fc16761d2897
```

Per-case hashes are ordered as:

```text
completeness.json
scenario_result.yaml
bag/bag_0.db3
analysis/phase07/analysis_completeness.json
analysis/phase07/summary_metrics.json
```

The two analysis hashes are absent for the infrastructure-invalid case.

```text
v7_m4_4_r1p0_a45_h25_18409
200a10e94d97554661bf49606eb2e635d09be2a7e9c7b66f523920e923002cac
f4bea49e976142bb04eaa4f6252732a8778da3290d7c06d4e4805dad2758bb6b
472cf142b6944eb505eee7be7b44ef8a04f2992c24cfffb4bfdb7e4cda24e220
2ee1240d2dd46bcf5a1c770a1efd2e98f8d95c6e646def6480db7c3cca289f47
59181526a2cd92cb1f1521133d15ba50aec1c52040fea78759dff329a0d90cf2

v7_m4_4_r1p5_a22p5_h25_18409
6c583b806998fe62248966ed5b4102953a0c6c2992ea15af9da78e467eaca0b3
d23ad60143677d2fb154bbd7d08317e684310fc5f436bb893cf47a74d2ea2535
1763e437b2496d177ffdb3b4419e1a4ef9e03316f904d5eb8aa2741338f82a3c

v7_m4_4_r1p5_a45_h25_18409
dfdc0938aafb634f5ff8d7f89570af0a21487f3d33bd7243edafb82742f3fa72
4f194081d04ca471007f528cc09cfa6f7edb9ba0775bf3e9b3a8b1d65a969a77
817d0d031f1236261e019e3f997b3d8b55f3af02ee3a5df5b851942e03ce930c
534ea7895ed81bc50ac43504277eeb15f290ba03a5b0af50604c28028b184f89
0cf7a6d429936c79573b1b79f2f6f51f8c85853321ef499a1acec887f2095f68

v7_m4_4_r1p5_a67p5_h25_18409
eedf03438c4d967677a3241752cc39e0183322086800380e0d9df45cacbf7db4
7ce748e4b10d44919639816b905c3fa8672fd688370b97f3a71bcfda0e92dcec
c210c278bdfe84560bae0fb2aeae43026da7fc5c12748907b80f8c1f28c35a0e
ffd04f620a3249468a713089b2efabae971c92db47d3a19782fa4f2723603ab6
f57f16fd9ecdc27b42c2cd9fd09809347e9e0e9891bd54e5ec728c345e8f4ae2

v7_m4_4_r2p0_a45_h25_18409
b32a5df9d4783fb9695b97fe1682694c6259022178875d9130636a73b0b19912
f42a84979fef10f47af169f16d89995357361357611a4ac8c0400b3652410eca
807d5760e241e5206e535df980448a39fc1c399f346b109385eb51677587f8bd
a27791112d4de26d4da472325f87e55244ac017b7452c3cb5fe5a9a74a73de84
8300d5c296890954896070b0f1db97206e89b31f0fd976cfcd1e34c8f370da12

v7_m4_4_repeat_r1p5_a45_h25_18410
0a60cc938c81f89b3d92b8ddc4ca7c46c64013279623e257d583811b593888ea
4fdcd104e1b9794e650856c5b5e06a02d21f3385d1a6d6727f8e101b5c7f2b9b
662c720dab2b0ccbc18dff2a749f4012ce34171fd16ed4b1571749db6d22449b
0bc14c0ab612a47d541a4f8a8f8f70798cd5ab3de89bb3d1d70ed376c9e5015f
dc09a385e2a42b62d88bd041e610fb83fd07f2b22e0f5be6b3b3f5054bc1598e

v7_m4_4_repeat_r1p5_a45_h25_18411
a559f0fb17d86e33dc073b526f4807a6668305a0f773ea45b5a590c036f45ab1
946c6f1f469c25275057cf694c30c2bbf2717cc633d88aee8fbad4aa3881781a
7f715a79f0ffa111166d77519d6cef6d2a017424e0d8c08a2d6fc3a409791fdb
4ebd92c89fffa7d91ef9086f97473140bffad7c4ee1717b016c61853accea49a
2b50243784676434e04679fea525eb1fb8991de2d18bd548ffe25ba715297ac8

v7_m4_4_repeat_r1p5_a45_h25_18412
6c6146d7a5bfd517bcab0923ad96effe43ca1e438090dfb2e8e97dcaee069ee2
33501843668854346911920d54c5220a00a6bbf928ee04b16e1a826926765831
55558f717f505960d49f34c1c9a87ce9294f8cbf1a922ac9a87665ade2de63a7
49c94d56f69f6bfedf34aad89accaaa91f0dcab2b5afa57f1f62a60953f56d36
d3147205fea122ddcd0073cbd934408645f00462a3834a7509387dbe23ec349d
```

## Closeout

M4.4 is **CLOSED / NOT SIMULATION-READY**. Its adaptive-recenter correction,
source-led observability, visible pass, all suite attempts, and all failures
remain immutable. A further attempt requires a fresh planned version,
default-off compatibility controls, no-Gazebo qualification, a committed
dispatch boundary, and fresh fixed simulation identities. M4.4, M4.3, V6,
and all historical scenarios/evidence must remain unchanged.
