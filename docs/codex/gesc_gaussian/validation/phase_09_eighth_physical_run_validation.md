# Phase 09 eighth physical-run validation

Date: 2026-08-05
Milestone: M8M evidence boundary
Result: first physical two-basin behavioral success; retained completeness
failure isolated to shutdown evidence ordering; no M8M source repair implemented

## Retained run

Preserve this run unchanged:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-05/
  20260805T004605139747Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_cd83f78f
```

The operator-owned selected `--check-only` passed before the run, including
the three-package build, installed Python parity, selected physical `False`,
legacy-default `True`, device separation, and launch construction. Codex did
not execute that command or any physical process.

The recorder finalized a `186003456`-byte sqlite3 bag. Target and bag exit
codes are zero, both shutdowns are clean, `run_error` is null, and cleanup
errors are empty. The legacy CSV manifest passed and identifies
`algorithm_odometry.csv` as onboard `/odom` used by the algorithm and
`odometry.csv` as evaluation-only Vicon data.

## Physical behavior evidence

The retained typed event/state sequence is:

1. qualified convergence candidate at `00:48:33.714 UTC`;
2. convergence confirmed after the required six-second dwell at
   `00:48:39.727 UTC`;
3. `SEARCH -> VERIFY_EXTREMUM`;
4. the nine-second counted-candidate window completed with raw-cost estimate
   `-0.435 V`;
5. one Gaussian fill was created at onboard `/odom` center
   `(2.227914, 0.264837) m`, amplitude `0.562125`, and exit radius
   `1.366771 m`;
6. `ESCAPE_REPULSE -> ESCAPE_ASSIST`; and
7. stable assisted escape completed at `00:49:21.918 UTC`, returning to
   `SEARCH` with one active fill.

There is no separate `RECENTER` state in this run. The visually observed
course correction occurred in the bounded open-field `ESCAPE_ASSIST` path.

For experiment-relative times at or after zero, onboard `/odom` starts at
`(-0.099174, 0.042055) m`, finishes at `(3.893492, 1.336800) m`, integrates
`7.797691 m`, and has `4.197350 m` net displacement. Evaluation-only Vicon
integrates `9.027076 m` with `4.088632 m` net displacement. Its raw origin is
not registered to the nominal scenario origin, so untransformed Vicon
coordinates are not used as algorithm or source-proximity evidence.

The local-candidate estimate corresponds to about `0.435 V`. Five later
rotation-scale raw-voltage peaks during the stronger-light approach are
`1.3539`, `1.6422`, `1.9648`, `2.3069`, and `1.9013 V`; their median is
`1.9013 V`, about `4.37` times the local estimate. This strongly corroborates
the operator's observation that the robot reacquired the stronger source.
Because the run was manually stopped while still in `SEARCH`, the bag has no
second convergence confirmation or `GOAL_HOLD`. It is therefore the first
physical behavioral success, not yet a formally complete second-extremum
acceptance run.

## Sole completeness failure

Completeness passed `61/62` checks. The only failure is
`rotation_status_semantics` at bag timestamp `1785891006093134065 ns`:

```text
rotation status transition content is invalid after authorization ended
```

The exact recorder receipt order is:

```text
00:50:06.048002  rotation authorization false
00:50:06.048072  stop requested true
00:50:06.054069  /cmd_vel zero
00:50:06.063417  in-flight rotation command 20 rpm
00:50:06.093134  in-flight RUNNING/authorized rotation status
00:50:06.115353  rotation command zero
00:50:06.140499  FAULT, authorization false, zero rpm,
                 "rotation authorization was revoked"
```

The current offline validator treats the recorder's first false gate receipt
as an instantaneous global ordering boundary. Independent DDS subscriptions
can observe that false before the rotation owner processes it, so the single
45-millisecond-later `RUNNING` receipt is rejected even though the owner
publishes zero 67 milliseconds after the boundary and the exact terminal
fault/zero status 92 milliseconds after it. Base command was already zero
after six milliseconds. This is a bounded cross-topic shutdown-ordering
false negative, not a controller, recorder-lane, algorithm, or managed-stop
failure.

## Proposed next boundary

Do not change controller or rotation-owner leases and do not tune the
algorithm from this run. A future M8M source amendment may change only offline
rotation evidence validation and its focused tests: permit an in-flight
pre-revocation status/command only until an exact terminal
authorization-revoked zero status arrives within the existing safety bound;
require no active/nonzero evidence after that terminal status; and retain all
preauthorization, readiness, semantic, final-zero, and lease checks. Reproduce
the exact retained receipt order in regression coverage before any transfer.

The operator intentionally unmounted `/home/mattb/tb3-pi` after the run.
Codex made no post-unmount Pi access attempt. No additional physical run is
planned for 2026-08-05.
