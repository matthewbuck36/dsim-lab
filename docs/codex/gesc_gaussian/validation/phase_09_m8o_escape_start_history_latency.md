# Phase 09 M8O escape-start history-scan latency validation

Date: `2026-08-18`

## Evidence boundary

The selected physical run
`20260818T134743817066Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_d766a6ab`
is retained unchanged on the Pi. It passes `60/62` completeness checks and is
failed evidence, not physical acceptance. M8N accepted `40/40` synchronized
samples and created a fill. The first behavioral failure was the supervisor's
`source sample invalid or stale` transition immediately after entering
`ESCAPE_REPULSE`.

The later encoder/pigpio bad-file-descriptor traceback was emitted during the
forced shutdown path, after readiness had already been revoked. It is retained
as a secondary diagnostic and was not broadened into this correction.

## Causal timing

Read-only typed decoding used a host temporary copy of the retained bag; the
Pi run directory was not modified. Relevant bag receipt times were:

| Evidence | Bag time (s) |
|---|---:|
| last source processed before escape startup | `1787061028.9260275` |
| fill-created event | `1787061029.0596564` |
| transition into escape | `1787061029.0764339` |
| valid queued source message | `1787061029.1299770` |
| valid queued source message | `1787061029.3272338` |
| escape-started event after synchronous initialization | `1787061029.4999804` |
| subsequent failsafe transition | `1787061029.5159052` |

The source publisher remained valid near 5 Hz. The approximately `0.423 s`
escape-start handler prevented the queued source callbacks from updating the
supervisor before its next timer invocation. The timer therefore evaluated
the previous receipt against the unchanged `0.50 s` lease. The retained pose
history had 3,114 entries, and the dominant helper performed multiple NumPy
operations per entry.

## Bounded correction

`approach_continuity_evidence` now makes one scalar pass over the frozen pose
history. During that pass it:

- validates every pose coordinate and timestamp;
- records any non-increasing timestamp and rejects after full validation;
- overwrites the outside-radius candidate so the newest qualified pose wins;
- updates the interior candidate only on a strict distance increase so an
  exact tie continues to select the earliest pose; and
- creates NumPy-backed evidence only once for the selected result.

`SupervisorNode._begin_escape` now creates one immutable pose-history tuple
and reuses it for recent-approach and approach-continuity calculations.

No freshness lease, grace period, state transition, command, controller,
fill/escape geometry, topic, cost sign/unit, pose source, Vicon role,
recorder, wrapper, or legacy-selection change was made.

## Exact retained-bag replay

The prior and corrected helpers were alternated 50 times on the decoded
3,114-pose history. Output equivalence passed with `rtol=1e-12` and
`atol=1e-12`:

```text
anchor=(-0.749956581913305, 2.566785203322189)
direction=(-0.753695973184382, 0.657223234529674)
displacement_m=1.367396041716432
history_age_sec=108.461905479
anchor_mode=outside_radius
prior_median_sec=0.023420
corrected_median_sec=0.002196
speedup=10.66x
```

This is host timing evidence only. It supports the diagnosis and correction
but does not substitute for a fresh physical run on the Pi.

## Source transfer and rollback

The operator authorized direct writes through the existing SSHFS mount and
explicitly directed that M8O not use the local physical snapshot. Before the
edit, the two mounted files matched checkout hashes. Their unpacked copies,
manifest, and archive are retained at:

```text
/home/pi/phase09_backups/20260818T205807Z_m8o_escape_history_latency
```

Archive SHA-256:

```text
18b0ccd2ca068462a951e32d5586afe79088e3da7a85eff37e6b73bd4e954c9c
```

Final checkout and mounted-Pi hashes:

```text
d2d4a6edb0c539638b5a8ea50fa3f85b08c311591495b6708f9a91d26e246b27  escape_recenter.py
ffb5441fb0d8a9032af87a6d52a60a1ead371a6f45aaec4bf3ebeb1843e67144  supervisor_node_script.py
```

The local physical snapshot was not read, written, or used as an intermediate
source. Snapshot parity is intentionally not asserted for M8O.

## Validation results

All process-running commands were bounded.

| Gate | Result |
|---|---:|
| canonical `test_escape_recenter.py` | `67 passed` |
| supervisor integration + state machine + observability | `174 passed` |
| canonical legacy behavior | `37 passed` |
| escape suite resolving mounted-Pi runtime source | `67 passed` |
| 3,114-pose no-per-pose-NumPy regression | PASS |
| exact retained-history output equivalence | PASS at `1e-12` |
| checkout/mounted-Pi hashes for both owners | MATCH |
| mounted AST and fatal flake8 `E9,F63,F7,F82` | PASS |
| `git diff --check` for implementation/test paths | PASS |
| Phase 09 implement-context validator | PASS |

One exploratory supervisor-suite invocation replaced ROS's sourced
`PYTHONPATH` and failed collection on `geometry_msgs`; a corrected invocation
then preserved ROS paths but sourced the wrong repository-level overlay and
failed on `ros_esc_interfaces`. Sourcing the authoritative
`ros2_ws/install/setup.bash` produced the `174 passed` result above. These
command-environment errors did not change source and are not product failures.

## Deferred physical gates

Codex did not run a Pi command, build or source the Pi overlay, start ROS or
Vicon, access devices, record, actuate, energize a lamp, or move the robot.
The operator-owned Pi build/check-only and a fresh retained physical run are
still required. M8O is implemented and host-qualified, not physically
validated.
