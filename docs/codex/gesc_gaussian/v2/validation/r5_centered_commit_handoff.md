# R5 centered commit handoff source validation

2026-09-10: SOURCE_VALIDATED. The existing MovingSupervisor now excludes only
its current authenticated activated fill during bounded initial centered DESIGN.
The supplied state must be DESIGN with valid previous VERIFY; the actual machine
must also be initial DESIGN. Current uncancelled candidate/preparation, typed
commit/hash/registry chain, original unexpired lease, full active fill and exact
node mirror/avoidance geometry must agree. Other fills remain in the unchanged
sweep check. Tracking, controller, ACK/state-transition and activation owners are
unchanged. The exemption does not authorize escape before both original ACKs.

Source diff75 added/1 removed, one existing function changed and one added in
`supervisor_node/v2_supervisor.py`. All other existing functions are AST-identical
to the retained baseline. New source SHA256
`4b411fc9d52c21115d7ea860114d7845d84dfe25eb853bfe8d96d4662a70dffa`.
Independent review found no remaining blocker after the supplied-state guard.
The [prospective plan](../r5_centered_commit_handoff_plan.md) and
[original C failure](m4_pilot_v10_result.md) remain authoritative for scope.

## Retained pre-fix reproducer

The fixture uses actual MovingSupervisor admission/result/publication and the
real SupervisorNode fill callback, retaining C's measured candidate/fill geometry.
Other timeline/stream inputs are controlled test fixtures; this is not a replay
of every C observation. The unchanged tracking law proposes v0.0320559805m/s,
w0.1267490962rad/s; adding the activated fill caused `centered_command_sweep_unsafe`,
invalid zero guidance, cancellation and SEARCH on the original source.

Baseline_v1 failed in0.959449s before reproduction because generated array slice
assignment rejected a list. Only the fixture's full-field assignment changed.
Baseline_v2 reproduced the actual failure in1.198057s,80 imported source/input
pins stable, session61366 exit0/reaped. Original source SHA256
`bbb5d6e8bdccad119881603576734fac213562f874cde990aad10fbd3ea1b593`.
All baseline helpers, source copy, exact commands and receipts are retained at
external `development/20260910/r5_centered_handoff_v1/`. Baseline_v2 receipt
SHA256 `2b141dad9d14fe90495262962b838b361c23218ce200a2f77712422b5996acc9`.

## Focused result

Eight-module bundle PASS272 unique cases, pytest47.02s, inclusive49.247001s.
All760 source/test/plan/helper pins and21 installed entry-point bindings stayed
unchanged. Session51226 is terminal/reaped. No Gazebo, bag read or numerical
reference job ran. Existing isolated controller/supervisor ROS fixtures exercised
actual callback/publication and final-command behavior, including shutdown.

New main/adversarial cases prove preserved nonzero post-commit guidance/final
diagnostics, both state/guidance arrival orders, missing/single/stale/wrong ACKs,
current and supplied state boundaries, identity/registry/mirror mismatch,
PREPARED-only, original expiry, cancellation, unrelated obstruction with a valid
self exemption, room bounds, freshness and legacy/redesign behavior.
Existing centered, supervisor, controller, transaction and lifecycle regressions
passed in the same bundle. No post-pass broad rerun or CLI/build was needed.

Exact command:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 255s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r5_validation_v1/validate_source.py --version focused_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r5_validation_v1/tests_v1.json > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r5_validation_v1/focused_outer_v1.log 2>&1'
```

Receipt external `development/20260910/r5_validation_v1/focused_v1/source_validation.json`,
SHA256 `764652c9f59d75988576cf6c5aa76163d9a05e0ff8fb69310f8a6fa55dbcc524`.
The explicit eight-module selection, JUnit, log and before/after maps are retained
alongside it. Context and diff checks pass. Material archive follows in status.

This validates the bounded source correction. A short visible C acquisition and
its analysis remain required before any new comparison. M4v10 stays failed and
unmodified; A/B arrival evidence remains valid. No detector/estimator/controller
tuning, IDL, topic, physical/Pi/snapshot/V1, commit or push change occurred.
