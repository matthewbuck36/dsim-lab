# Post-V9 D2: preserve completed recovery during live evidence arrival

Status: ADOPTED, 2026-09-10 UTC, simulation only. This is the next source
milestone under the user's authorization for recommended bounded corrections.
It follows the materially closed [D1 diagnostic](m4_post_v9_integrity_handoff.md)
and concretizes the monitor scope in [the post-V9 plan](m4_post_v9_integrity_plan.md).
The D1 plan and all retained V9 evidence remain unchanged.

## Evidence and ordering

V9 development D and nominal B/D completed recovery and entered Stage B, then
received a later convergence event without its typed companion yet available to
the live subscriber. Current `refresh_stage_a` overwrites stage completion with
False. Subsequent odometry after the original 360-second Stage A deadline sets
an immediate Stage A timeout before the pending callback can complete the join.
The final bag can contain the companion, but it cannot restore the lost live
exposure. See [recorded diagnosis](validation/m4_v9_development_diagnostics.md).

The next incomplete criterion is a live monitor that retains completed temporal
progression while continuing strict current-evidence validation. This defect is
independent of the startup-recording correction, whose exact sender-match proof
remains under design. Implement D2 first; do not wait on that unresolved design
or weaken it. No new simulation comparison is released by D2.

## Exact source scope

Extend only existing `scenario_runner/run_scenario.py` and focused tests.
Apply the correction to the already selected M4 typed-centroid monitor path,
using `_m4_centroid_event_selection`; preserve nonselected/legacy behavior and
result shape. Preserve the current matcher and all full-history identity,
publication-order (500 ms), origin, cardinality and final-bag checks.

- Keep the first fully valid Stage A completion evidence separately for temporal
  progression. A later incomplete or contradictory join must not regress that
  completed phase or restart its timer. Do not replace the current strict
  evidence verdict with a permanently passing latch.
- The next valid post-completion odometry starts Stage B once. Later pending
  evidence consumes that same original Stage B allowance, including odometry
  arriving after the former Stage A deadline. Never pause/reset/extend Stage B,
  the recording duration, the case work deadline or the suite budget.
- Continue evaluating all accumulated events, diagnostics and fills. While the
  current verdict is invalid, withhold new proximity/approach/goal acceptance.
  A later complete consistent companion may clear a pending verdict; conflicting
  append-only evidence must remain failed. An additional fill cannot be hidden
  by the temporal completion snapshot.
- On the selected path, an unresolved terminal `staged_monitor_error` must make
  result classification an evidence failure even if final bag extraction joins
  successfully. Preserve raw error details and completed-phase timing evidence.
  No old result is reclassified.

No detector thresholds, GESC gains, Gaussian geometry, source timestamps,
controller ownership, public topics or producer behavior change in D2. No new
node, monitor implementation, recorder, validator or analysis pipeline.

## Validation and durable boundary

First save focused callback-schedule regressions and run them against unchanged
V9 source under one 120-second baseline cap. Retain failures as the reproducer;
no old bag is read and no ROS context, daemon, Gazebo or hardware is launched.
Use generated message types with the actual existing monitor and callback/executor
test seams, not a mirror of the implementation.

Cover both B/D arms and both companion arrival orders; completed recovery;
interleaved odometry beyond 360 seconds; eventual and permanent absence;
goal/proximity while pending; recovery completion followed by a missing pair
before the first Stage B odometry; exact Stage B deadline and existing proximity
precedence; conflicting identities; additional fill/cardinality failure; and
selected terminal classification despite a successful final bag result.
Retain nonselected/default result parity and the strict 500 ms join bound.

After the bounded repair, run the focused module and existing
`test_m4_centroid_event_evaluation.py` under 180 seconds. Run relevant
`test_scenario_runner.py` and `test_m4a_execution_deadline.py` regressions under
240 seconds after verifying their actual filenames and runtime scope. If a name
is stale, resolve it and record the exact substitution before execution. These
are finite maxima, not permission to retry an unchanged failed job. Corrections
after a demonstrated failure use a new saved source/test version and retain all
logs/JUnit/results. Broaden only for changes or unresolved concerns.

Use the clean installed Humble -> Q2 -> Q5 environment and existing package
owners. Retain exact commands, source/test hashes before/after, unique JUnit
counts, failures/skips and logs under external
`builds/m4_post_v9_monitor_v1/`. Independently review the correction and its
test coverage. Run context/diff checks and the existing V2 checkpoint, then
one exclusive material archive under 60 seconds before the next source milestone.
The D1 archive db9c3e1262eb176418fdabc573ce8e401b0da3613c9e4f3206e538c6446538e7
preserves the pre-edit source; all uncommitted task work and V1 remain intact.

D2 source acceptance does not establish faster detection, direction quality,
full Stage B empirical exposure or research success. Startup recording, daemon
discovery, labels throughput and fresh comparison prerequisites remain open.
