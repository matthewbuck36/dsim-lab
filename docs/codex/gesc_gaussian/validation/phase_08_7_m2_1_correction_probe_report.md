# Phase 08.7 M2.1 correction-probe report

Date: 2026-07-29

## Result

The one fixed M2.1 attempt is retained as **FAIL**.

- infrastructure, recording, validation, final-zero, and cleanup: **PASS**;
- detector SEARCH-state gating and recording: active and complete;
- Stage A local recovery: **FAIL** because no convergence confirmation
  occurred;
- exact fill cardinality: **FAIL** because no fill was created;
- Stage B post-recovery global proximity: **FAIL** because Stage A never
  completed;
- combined behavioral result: **FAIL**.

M2.1 is not retried or relabeled. Its failure is distinct from retained M2:
M2 reached and completed Stage A, while M2.1 remained in `SEARCH` for the full
motion interval.

## Frozen input

```text
qualified commit:
  46a06c665fafb19edcd6d3ef7553907f1656b05e
suite:
  phase08_v7_m2_1_correction_probe
experiment version:
  phase08-v7-m2.1
case:
  v7_m2_1_diagonal_r1p5_h25_18001
case key:
  2db8a5e49c8068373c22c621be13506419f9f2d7364ec50274f9f7d9895840eb
scenario SHA-256:
  541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b
seed:
  18001
maximum fills:
  1
detector:
  SEARCH-only, minimum path 0.20 m, maximum efficiency 0.35
post-recovery affine:
  enabled, maximum age 60.0 s, gain 0.5
post-Stage-A global proximity:
  0.60 m
```

The installed scenario and source hashes matched before dispatch. The run
metadata identifies the exact qualified commit. Its `dirty=true` field is the
predeclared live-status dispatch entry made after that commit; there were no
untracked paths and no algorithm or scenario byte change.

## Invocation and retained run

A first shell wrapper used `set -u` before sourcing the ROS setup and stopped
on ROS's unset `AMENT_TRACE_SETUP_FILES` reference. `run_scenario` was never
invoked, the evidence root remained absent, and no ROS or Gazebo process
started. It is retained in the live status as a pre-dispatch shell error, not
an experimental attempt.

The already-declared command was then invoked without that wrapper error:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_1_qual/install/setup.bash
export ROS_DOMAIN_ID=89
export ROS_LOG_DIR=/tmp/phase08_7_m2_1_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m2_1_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_1_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m2_1_correction_probe.yaml \
  --operator phase08_7_m2_1 \
  --case-id v7_m2_1_diagonal_r1p5_h25_18001 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1/\
phase08_v7_m2_1_correction_probe_summary.yaml \
  --gui
```

The one attempt is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1/
  2026-07-29/
  20260729T234858803958Z_simulation_phase08_v7_m2_1_correction_probe-
  v7_m2_1_diagonal_r1p5_h25_18001-robust_gaussian_80ca5c97
```

The runner exited `1` for the failed behavioral classification. The recorder
exited `0`, did not time out, and retained a complete run.

## Infrastructure and lifecycle

Infrastructure is classified `completed`.

- the readiness interval is available and spans `360.128014908 s`;
- recording and cleanup passed;
- no new nodes or session processes remained;
- `/cmd_vel` and all declared evidence topics were present;
- the bag contains `10,654` odometry samples, `3,622` PDE-history samples,
  `7,246` typed state samples, `740` convergence-status samples, and
  `72,345` contact samples;
- no non-ground collision was observed;
- all three final command streams are zero and final readiness is false;
- `validate_run` returned `0`, `passed=true`, with no failures or warnings;
- the read-only Python sqlite fallback returned `ok` from
  `PRAGMA quick_check`.

The outer run duration requested an explicit stop at the end of the fixed
motion window. That shutdown transition is outside readiness and does not
relabel the in-readiness terminal state, which remained `SEARCH`.

## Behavioral evidence

The only in-readiness state was:

```text
SEARCH: 360.096129064 s
```

No convergence candidate or convergence-confirmed event occurred. No
verification, fill design, escape, recenter, post-recovery affine state, or
global-proximity stop was reached. The final pose was
`(1.2341683317, 1.3995177394) m`, `3.0896632302 m` from the declared global
source. Across all recorded odometry, the closest local distance was
`0.0539395645 m`, proving the robot did reach and orbit the intended local,
while the closest global distance was `2.8623873320 m`.

The total odometry path length was `22.0617045159 m`. This rules out a
stationary-path explanation for the missing event.

## Detector diagnosis

The M2.1 detector was configured as recorded:

```text
k_periods:                 20
threshold:                 0.20
decay_rate:                0.15
n_buffer:                  2000
minimum fresh SEARCH time: 50.265... s
minimum path:              0.20 m
maximum path efficiency:   0.35
candidate count required:  3
```

Read-only replay of each recorded PDE-history buffer with the implemented
`k=20` motion statistic found:

```text
total buffers:                  3,622
motion-qualified buffers:         746
path-length range:       0.0000275 to 2.0161832 m
efficiency range:        0.2859211 to 1.0000000
longest qualified interval:      17.1 s
published detector metrics:       740
minimum metric:             +0.0657099110
negative metrics:                       0
counter values observed:              {3}
```

The implemented policy resets its decay reference and crossing state whenever
the motion window exceeds the efficiency cap. At `0.35`, legitimate local
orbit windows repeatedly crossed the cap before the positive decay term could
fall far enough. The smallest recorded metric still had
`r=0.1815469208` and remained positive.

The cap was also inconsistent with the retained successful M2 local
convergence. Replaying M2's PDE buffer at its three actual local candidates
gives path efficiencies:

```text
candidate 1 at 121.4 s: 0.3639431494
candidate 2 at 156.4 s: 0.4434453791
candidate 3 at 180.1 s: 0.3605826563
```

All three legitimate signatures exceed the M2.1 `0.35` cap. The state gate was
therefore sound, but the uncalibrated compactness threshold over-constrained
the detector.

## Bounded counterfactual

A read-only replay of the exact failed M2.1 PDE path with no source mutation
shows that changing only the maximum path efficiency to `0.50` would produce
three candidates under the implemented reset/counter logic:

```text
candidate 1: 172.9 s, count 2
candidate 2: 198.9 s, count 1
candidate 3: 220.7 s, count 0
```

Their recent-window means were respectively `0.19395`, `0.35529`, and
`0.04452 m` from the declared local source. The same replay produced no
candidate before `172.9 s`; directed translation remained rejected. A `0.50`
cap is also above the largest retained M2 legitimate candidate (`0.44345`)
with bounded margin, while remaining materially below straight-line
efficiency `1.0`.

This counterfactual supports a fresh experiment version changing only the
motion-efficiency cap from `0.35` to `0.50`. It does not claim that Stage B or
the affine path passed: M2.1 never reached them.

## Offline analysis

The standard bounded analyzer completed with exit code `0`, produced eight
plots and eleven CSV tables, and wrote `summary_metrics.json` plus
`analysis_completeness.json` under `<run>/analysis`.

Its `analysis_status=partial` is retained honestly because an escape was
declared applicable but never occurred, and generic aggregate-target metrics
are unavailable. There are no analysis failures. Fresh embedded Phase 05
validation passes.

## Evidence identities

```text
b2d714392e4d17cca0fac7e054a6c48a4d2fb7cdece2e8caa42d1681f17b7db7  suite summary
c04ddbc912686693f045c3ae34b31ae692b2182361521448b309f459a7895414  scenario_result.yaml
02bf4614df8a4645cc29ef06cfe8a752fcace91dff2bfdd47e7946786b99e43b  completeness.json
c7d4eec24fbd272267447cb2d63f5add1095afc0f395b5fc0a451f1a9d426b5c  bag/bag_0.db3
74c467cef88e6c270c4b2d72284be6bb9fb58eaeeb3932f1c6f9cd5615fc7e3c  analysis/summary_metrics.json
1cd4d7001d8b981cf8cd88c0165858014b592f4cb4be09fac87433339ba0c8d9  analysis/analysis_completeness.json
```

## Boundary

M2.1 is closed and immutable as a failed fixed experiment. Its result does not
authorize M3, weaken exact one-fill cardinality, alter the relaxed `0.60 m`
Stage B stop, or establish affine runtime success. A separately versioned
M2.2 may retain all qualified implementation and scenario values while
changing only the evidence-supported efficiency cap to `0.50`, subject to a
new scenario hash, case key, evidence root, no-Gazebo qualification,
checkpoint, and commit.
