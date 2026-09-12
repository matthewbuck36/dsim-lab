# R2 recurrent recorder and scenario routing

Source validation PASS, 2026-09-10. These are source/evidence-contract checks,
not empirical algorithm qualification. Exact logs, JUnit and source-at-receipt
pins are under `development/20260910/recurrent_recording_v1/` at the external V2
root. Scoped pre-edit copies remain beside them. No Gazebo or bag was read.

The existing manifest/recorder now selects the independent typed recurrent
stream, validates launch/topic/type/source/timing metadata, requires singleton
publication and full simulated-time coverage, and rejects incompatible retained
descriptors and stationary routing. Old centroid/PDE routes remain unchanged.
The existing recording validator reuses the recurrent contract and the existing
coverage function, whose default centroid output text stays unchanged.

Existing scenario selection, live monitor subscription, retained outcome reader
and exact AlgorithmEvent/typed-diagnostic join route by the selected metric.
Only recurrent mode replaces the six-centroid arithmetic checker; old source,
run/epoch/sequence/center/score/freshness matching remains. Schema admission and
actual scenario-to-launch-to-metadata roundtrip pass. Recurrent+stationary and
the old centroid heartbeat selector on recurrent are explicitly rejected.

The existing V2 binding was reviewed and exercised with actual recurrent core
and generated confirmation envelopes: authoritative SEARCH origin is preserved,
the original pose receipt expires independently, and a source fault cannot
rearm the confirmation latch within the same epoch.

All commands used the installed Humble/Q2/Q5 plus new-interface environment:
`source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v1/environment.sh`
inside `env -u PYTHONPATH bash -c`. Python arguments were:

- `timeout --signal=INT --kill-after=2s 88s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_recurrent_recording_selection.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py --junitxml=.../focused_v1.xml`:45 PASS in2.86s.
- `timeout --signal=INT --kill-after=2s 88s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q7_recording_selection.py ros2_ws/src/ros_esc/test/test_m4_v6_centroid_heartbeat_selection.py ros2_ws/src/ros_esc/test/test_m4_centroid_event_evaluation.py ros2_ws/src/ros_esc/test/test_m4_monitor_progression.py ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py --junitxml=.../regressions_v1.xml`:160 PASS in7.04s.
- `timeout 30s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py -k recurrent --junitxml=.../binding_v1.xml`:2 PASS in.30s,30 intentionally deselected old cases already checked.
- `timeout 30s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_recurrent_recording_selection.py -k scenario --junitxml=.../scenario_v1.xml`:7 PASS in2.73s,19 intentionally deselected prior cases.

Here `.../` is the exact external `recurrent_recording_v1/` directory named above;
each job redirected stdout/stderr to its same-stem `.log`. The JUnit inventory
contains214 unique passing cases across these incremental boundaries, no skips
or unavailable tests. This is not an additive total with other agent regressions.
The new guidance schema2 correction remains a separate source boundary; its
selected runtime tests/build are required before the prepared visible case.
Context validator and `git diff --check` pass. No commit or push was made.
