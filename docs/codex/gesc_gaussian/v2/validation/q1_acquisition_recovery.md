# Q1 acquisition recovery 1 validation

Current boundary: source correction/preflight PASS; the released acquisition
is CLOSED INCOMPLETE. `q1_acquisition_recovery1_failure.md` records125s exposure,
clean shutdown and failed safety/completeness. Scientific qualification remains
unmeasured. The earlier pre-dispatch entries below describe historical boundaries.
Method: `../q1_plan.md`; active amendment: `../q1_acquisition_recovery_plan.md`.

## Demonstrated cause and correction

The first release prepended the checkout's `ros2_ws/src/ros_esc` directory to
PYTHONPATH. That directory contains tracked historical `ros_esc.egg-info` with
seven console entries. Python selected it ahead of the isolated build metadata,
which contains21 entries. Because the historical metadata lacks `record_run`,
the installed wrapper raised `StopIteration` before importing the recorder.
The same problem would affect other subsequently added console nodes.

The correction is environment-only: source base Humble and the existing isolated
local overlay, retain its path order, and append `extremum-seeking/src` for the
existing shared numerical package. Do not prepend the `ros_esc` source directory.
The symlink installation already resolves Python modules to the current checkout.
No tracked metadata was deleted/regenerated and no rebuild was required.

The built `entry_points.txt` SHA256 is
`3f25b9c84f9311376675f931a6fe16eca1dfaf3318f5b5cac173c14933189d59`;
the historical source copy SHA256 is
`2fd19ef44413d5c1600855dba3bcdf5f7e73d47d2b2f33cf4ede6f9ca290af8a`.
The original failed acquisition remains closed in `q1_acquisition_failure_v1.md`.

## Installed entry-point evidence

`../tools/q1_environment.py` checks all console declarations against live
`setup.py`, requires the isolated ament prefix and its actual selected metadata,
hashes every installed wrapper, and loads its callable target without invoking
it. Each target must resolve inside this checkout. The fresh contract binds that
result. Acquisition verifies the binding and a fixed set of relevant environment
variables against the release before creating output or calling the runner.

A30s bounded Python check guarded both `rclpy.init` and `Node.__init__` against
execution, then loaded all21 targets successfully. Exact wrapper/module/metadata
paths, hashes and environment are retained in
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_entrypoint_preflight_v1.json`.
The guard remained intact; no nodes were created.

After reading `record_run.main` to verify argument parsing precedes `run`, the
actual installed wrapper was exercised:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 30s ros2 run ros_esc record_run --help > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_record_entrypoint_help_v1.log 2>&1
```

Result: exit0, expected `--sim-duration-sec` option present. Log SHA256:
`755ebf72948dbc6c829d9d35ac2aed6b85db22d7fe9ba25fcb68e15117c559fd`.
This validates launcher resolution/CLI startup, not recording or Gazebo behavior.

## Recovery routing and final source checks

Focused environment regressions PASS:23 checks in2.39s, exit0, using the same
corrected environment and `timeout 90s python3 -m pytest -q
ros2_ws/src/ros_esc/test/test_q1_entrypoint_environment.py`. The tests reject the
stale source metadata in a fresh interpreter before loading any console target;
exercise every frozen environment field, missing release data and changed
binding receipts; and exercise the real recorder help path. Retained log:
`builds/initial/q1_entrypoint_tests_v1.log` under the external V2 root, SHA256
`975b98b253896290b99191f6ff0ade38a9f35d9538170ad8e0c1f75636ba1867`.
An independent read-only selected-launch audit found no further startup blocker;
this does not substitute for the bounded recording attempt.

Recovery routing passes19 focused checks in1.79s (`q1_recovery_paths_v2.log`).
Both original and recovery identities are compared against the actual existing
runner in dry-run mode for all four cases: resolved launch argv, metadata and
recorder command agree, except the declared temporary metadata path. Bad roots,
IDs, populations and changed prior-attempt receipts reject before output. The
runner receives its existing explicit `runs_root` override. Evaluation stays in
the bound recovery root, and acquisition output remains exclusive.

After wiring the actual entry-point binding into freeze and acquisition, the
combined routing/environment suite passes42 checks in2.91s, exit0:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py ros2_ws/src/ros_esc/test/test_q1_entrypoint_environment.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_recovery_integrated_v1.log 2>&1
```

Log SHA256: `95b63538a14aa7fdf3240bac55a025e2f879e2a58f93f73db04bd74fa2f17c48`.
The earlier frontend/source/geometry/runtime tests remain applicable because
this correction changes only acquisition orchestration and its environment.
No algorithm, scenario, analytical/numerical owner or installed metadata changed.

Next: freeze the new source/entry-point/geometry contract, verify source freshness,
update the durable checkpoint and issue an exact release. No prior acquisition,
labels, numerical receipts or held-out result is replaced.
