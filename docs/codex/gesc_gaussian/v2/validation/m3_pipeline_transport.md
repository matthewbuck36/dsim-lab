# M3 actual moving pipeline DDS validation — 2026-09-09

Status: PASS for two bounded synthetic integration cases. This exercises the
actual existing SupervisorNode, Gaussian worker/registry and ModifiedCost2D
composer together. It does not exercise Gazebo, the controller, natural detector
convergence, physical hardware or the actual upstream M2 filter in this test.
The latter's source/filter transport is separately documented under M2.
No completed runtime owner source was changed to make this test pass.

## Tested path and synthetic scope

`test/test_v2_moving_pipeline_transport.py` uses DDS for actual supervisor SEARCH
context/state, typed candidate confirmation consumption, raw-cycle evidence,
snapshot publication, PREPARE/ACTIVATE/CANCEL, Gaussian preparation and commit,
combined FillResult, atomic composer activation, actual objective digest and
supervisor escape authorization. It never fabricates a fill command/result or
objective acknowledgement. A fixture diagnostic echoes the registry digest only
from an actual received ObjectiveCostSample; withholding that echo proves actual
objective receipt alone cannot release escape. This fixture is not a GESC angular
accuracy, model-provenance or upstream filter test.

Upstream poses, raw source, typed provenance, synchronized observations and one
detector confirmation are explicit synthetic fixtures. Pose/source observations
have exact25ms acquisition stamps,3s world-phase revolutions, and a repeating
nonellipse path r=0.06+0.008*cos(3*phase), x=r*cos(phase), y=0.8*r*sin(phase).
Raw cost is -1+x²+0.5*y². Radius0.5m/epsilon0.1m are explicit synthetic settings;
no research calibration is selected. The actual inherited estimator/designer
runs on the supervisor's frozen real raw-cycle snapshot and retains its defaults.

The test worker wrapper waits on a bounded five-second fixture event, then calls
the unchanged real compute_fill_proposal function. This makes the pending-worker
race observable without fabricating a proposal. No worker result is substituted.

- Activation case: at worker entry both actual registries remain generation0;
  the published snapshot matches PREPARE exactly. Observation at the actual
  PREPARED publication confirms both registries still generation0. The real owner
  commits generation1; composer applies its actual combined result. Supervisor
  counts one accepted cost and stays DESIGN while the actual objective's new
  registry digest is known but the fixture's direction echo is withheld. After
  that echo, actual state transitions to ESCAPE_REPULSE with the accepted fill ID.
- Departure case: while the actual worker is pending, selected pose moves0.8m
  outside frozen R. Actual supervisor emits CANCEL; worker is released and really
  finishes. No activation occurs, both registry generations remain0, no canonical
  active term or counted fill appears, and actual supervisor returns SEARCH.
  No observed state enters either escape mode after that cancellation.

## Commands and retained attempts

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=185 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_moving_pipeline_transport.py
```

The test also fixes domain185 internally, uses a50s per-case wall deadline,
bounded DDS waits, a finite363-sample initial stream, bounded additional samples,
and finally releases/joins owners and shuts down rclpy. It creates no controller
or cmd_vel consumer and sends no physical commands.

Retained logs are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Version | Outcome |
| --- | --- |
| `m3_pipeline_transport_v1.log` | 1 failed/1 passed,9.43s. Pending-worker cancellation passed. Activation fixture held clock/source while waiting for real worker, so actual Gaussian correctly canceled with `stale selected pose`. Fixed fixture starvation by continuing fresh source/pose/readiness during computation; runtime was not weakened. |
| `m3_pipeline_transport_v2.log` | 2 passed,7.86s. Both actual activation/acknowledgement and pending-worker departure cases passed. |

Source hashes at this boundary:

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/test/test_v2_moving_pipeline_transport.py` | `1b186bc74f73713772f9a7b627411b41fa2b73c20b53abd64ca14851707478da` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/v2_supervisor.py` | `5e26bca8e2bdea39b765924aa308138a44041fb3be3e2d23a2adb3d620b89466` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/moving_evidence.py` | `abc29fd1ed457e207539883435ede4803d6958f8315624c74960c989b6c9ee71` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py` | `45a9c825bd680ac1256a18250d2143b6d5cf2cf8078af5a100a90f9040bf6241` |
| `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/v2_fill_runtime.py` | `4e7cfe51b4da327d2ba140148f5d018626e461e2dee0273e176496c82c3f7d1d` |
| `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_preparation.py` | `1d94e7b2ee3282236d6556febcf8c2f215ff4a73831e8f0d87a97d513a070f32` |
| `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_fill_activation.py` | `0cf1d63372c0e5908c6f67688dc49a4a510b05c82c5cacf720b6695dbe97aafa` |
| `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_objective.py` | `ff27435e9358458e2387d9c2b8e820fabfd5a84b3f58a0f514658bfd1534cd83` |

| Retained log | SHA256 |
| --- | --- |
| `m3_pipeline_transport_v1.log` | `042d714dc2f135363d4984f690d160752d4c4058f789376ae2ce2d12f47a2f17` |
| `m3_pipeline_transport_v2.log` | `b5d055c76b57adbd2707943e19a1a0cd409b3dbccea9b1edb7d68e52ebba343e` |
