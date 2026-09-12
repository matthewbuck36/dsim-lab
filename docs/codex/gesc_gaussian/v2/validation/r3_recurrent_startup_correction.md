# R3 recurrent moving startup selector validation

SOURCE_VALIDATION_PASS, 2026-09-10, under the
[prospective correction](../r3_recurrent_startup_correction_plan.md).
Attempt 01 remains startup INCOMPLETE, with no recording readiness/motion and
successful scoped cleanup. Its original files and evidence were not changed.

Both GaussianFill and SupervisorNode called the same stationary-adapter selector
before reaching their moving adapters. That selector omitted recurrent mode.
The only production correction in this owner adds an explicit branch admitting
`recurrent_geometry_v3` only with `rolling_gesc_v2`, `robust_gaussian_v1`, and
actual boolean simulation time True, then returns False for stationary selection.
Recurrent stationary/physical/nonrobust/unknown selections reject. The centroid
tuple, stationary request envelope, old defaults, numerical methods and wire
layouts remain unchanged.

The new fixture `test/fixtures/r3_recurrent_startup_parameters.json` retains the
exact ROS parameter arguments from both recorded failed-process command receipts
in attempt-01 `console.log`, with that input's SHA256. GaussianFill has 78 selected
parameters; SupervisorNode has 110. The actual node classes construct successfully
with those arguments and select moving adapters with stationary adapters absent.
Supervisor selects centered tracking and its 20-second cap. Actual constructor
negative cases reject stationary mode, physical time and legacy profile.

The finite test invocation was:

```text
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 bash /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/recurrent_startup_correction_v1/focused_v1/command.sh
```

The saved script sources `centered_runtime_v2/environment.sh`, selects isolated
`ROS_DOMAIN_ID=203` and `ROS_LOCALHOST_ONLY=1`, then runs
`timeout --signal=TERM --kill-after=5 90 python3 -m pytest -q` on
`test_r3_recurrent_startup.py` and `test_q5_stationary_fill_protocol.py`, with
saved JUnit output. Exit 0: 63 passed, no failure/error/skip, 1.040 s. This is
14 new startup/selector cases and 49 existing stationary protocol cases. All six
scoped source/fixture pins match before/after; the job is terminal/reaped.
No executor was spun, readiness published, command consumer started or Gazebo
launched. Context and scoped whitespace checks pass. No interface build needed.

External result:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/recurrent_startup_correction_v1/result.json`,
SHA256 `bccbb6231a4734ca15bc16e40810efb5aa024a02d2b6949f80f13f811e56db8f`.
Exact command, log, JUnit and source hashes are in `focused_v1/`.

Targeted caller search finds only GaussianFill and SupervisorNode using this
selector. Detector, moving supervisor, scenario schema, recording route and
lifecycle confirmation validation already have explicit recurrent branches;
centroid-only evidence validators remain correctly restricted to their old
formula. Independent D3 inspection found a separate missing recurrent
configuration-event classifier entry in validate_run; root owns that bounded
correction and its fixture. Parent owns final source checkpoint/status/handoff
and any fresh attempt-02 release. Startup construction is not integrated or
behavioral qualification.
