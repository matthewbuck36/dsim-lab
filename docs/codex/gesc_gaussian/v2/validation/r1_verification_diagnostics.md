# R1 moving-verification rejection observability

SOURCE_VALIDATION_PASS, 2026-09-10. Adopted in
[the development amendment](../method_development_20260910.md). This adds
diagnostic detail to future recorded transition events. It does not recover
historical callback ordering or establish successful moving verification.

The existing raw-evidence owner now retains completed/qualified/inside/eligible
cycle counts, closest inside-cycle centroid distance and centroid tolerance,
sector-trajectory margin, signal margin, baseline-negative margin and
upper-cost-negative margin. The existing supervisor retains the latest evaluated
detail separately from the later cancellation cause. Moving verification/design
cancellation transitions append that information to their existing reason;
the existing AlgorithmEvent publication records the transition. Legacy/default
text with no supplied detail stays unchanged. No topic/interface/controller,
guard threshold, evidence selection, deadline or state decision changed.

Focused evidence and actual-message detached-supervisor fixtures pass **54/54**,
zero failures/errors/skips, pytest 9.36 seconds. New cases distinguish a
phase-qualified cycle inside the outer radius but outside the center tolerance,
constant-signal rejection, and negative-cost rejection with adequate amplitude.
A deadline test proves the last evidence reason survives cancellation and epoch
cleanup into the returned transition. Existing fill/goal/safety lifecycle tests
in those modules also pass. Fresh ROS/Gazebo empirical validation remains open.

Exact command from repository root:

```bash
timeout --signal=INT --kill-after=5s 85s env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 bash --noprofile --norc -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q5_stationary_centroid_adapter_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py ros2_ws/src/ros_esc/test/test_v2_supervisor.py --junitxml=/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/verification_diagnostics_v1/focused_v1.xml' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/verification_diagnostics_v1/focused_v1.log 2>&1
```

Terminal return code 0; explicit 85-second interrupt plus 5-second kill bound.
Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/verification_diagnostics_v1/`.
It retains three pre-edit source copies, log, JUnit and `receipt_v1.json` with
final source/test/log hashes. Git work remains uncommitted on V2 at3369cfc.

Final compatibility correction places the new TransitionInputs field after all
preexisting fields, preserving positional construction. The same exact command
above was run with both `focused_v1` output names changed to `focused_v2`:54/54
PASS, pytest9.08s, terminal0. `receipt_v2.json` binds final source/test/log hashes;
v1 remains retained. Independent read-only review of all three pre-edit diffs
passes: guard selection, strict thresholds, destinations and deadlines are
unchanged. Cancellations before any evaluation correctly report cause only.
