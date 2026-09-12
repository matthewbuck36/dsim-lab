# Q1 controller source-clock correction — 2026-09-09 UTC

The final controller checks pass **103 tests in3.44s**, including58 inherited
moving-controller tests,44 additional admission tests and one actual DDS
held-clock fixture. The final inherited controller/interlock/signal subset
passes19 tests (34 intentionally deselected). These are source/transport checks;
both earlier Q1 acquisition versions remain CLOSED INCOMPLETE. No Gazebo,
scientific reference evaluation, detector tuning or physical action occurred.

The governing correction is `../q1_simulation_source_plan.md`. Parent owns the
separate joint-publisher correction, integrated checks, build, checkpoint and
any new acquisition release. No recorder, launch, analytical or supervisor
owner was edited by this controller subtask.

## Recorded cause and retained receipt

The prior run's first controller FAILSAFE event has simulated stamp2.7s and bag
receipt1788948888654928817. Its detail is
`controller watchdog: V2 pose source missing, stale or future`.
The nearby `/odom` header2.721s was recorded after `/clock`2.7s and before the
next `/clock`2.8s. Prior `CustomController.state_callback` immediately replaced
the pose, while `_robust_fault_reason` rejected its negative source age. The
supervisor entered permanent FAILSAFE at2.8s. Subsequent detector inactivity
outside SEARCH explains its five diagnostics and116.1s coverage gap; the
completeness failure is preserved without changing its rule.

The small diagnostic receipt was copied from the already observed successful
bounded topic extractions, without rereading the bag or recomputing validation:

`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery1/diagnostics/controller_clock_fault.json`

SHA256 `9f7320bf3f8da381dda57ab1c377f99d187bdf902496bbbaeffdec8bdff47575`.
It binds `acquisition_closed.json` and its original bag reference/hash
`8164b58df08a3d3bc468d1e5e464fc75fe00fda4822cc855d40c020b8b0b0863`.
Bag receipt order cannot establish the independent controller subscriber's
exact callback order. The event's own simulated timestamp, surrounding clock
and header records and exact prior failing branch support this diagnosis.
No position or cost performance was interpreted.

## Existing controller behavior after correction

Only `rolling_gesc_v2` uses the new subordinate `ClockAdmission` helper. It
contains queues and source-order checks, with no control calculation or ROS
node. The existing controller remains the command owner.

- Near-future pose, filter and supervisor-state samples retain their original
  source, ROS receipt and steady receipt while waiting for clock coverage.
  Covered fresh inputs remain active. No command uses a queued future sample.
- Each queue is bounded1024; source lead and source/ROS-receipt/steady-receipt
  age use the existing500ms ceiling or a stricter selected stale limit. Overflow,
  invalid values/identity, regression, excessive lead and expired receipts revoke
  that input and force zero. Clock rollback clears active/pending authorization;
  a changed Timekeeper origin retains the existing latched fault. Pending data
  acquired before the first bound origin is rejected as well.
- Pose timestamps identify immutable acquisitions; changed duplicate poses
  fail. State and filter timestamps identify publications, so legitimate
  distinct revisions within one clock tick retain singleton publication order.
  Exact repeated payloads do not refresh either original receipt. The existing
  canonical `message_payload`/`hash_payload` owner handles optional NaN state
  fields deterministically; CDR padding bytes are not identity inputs.
- State revisions drain before poses/filter commands. A pending GOAL, FAILSAFE
  or invalid-state loss immediately fences motion; earlier queued SEARCH
  messages cannot override that stop. Moving VERIFY/initial DESIGN, redesign
  escape ownership, saturation and final authorization checks remain intact.
- A20ms steady timer drains covered queues and enforces the existing input and
  recorder bounds even while simulation time is held. An exact filter repeat
  may reevaluate the already admitted still-fresh value after readiness changes;
  it cannot refresh receipts or substitute its queued future value.
- Legacy callbacks retain their original receipt timing and default paths.
  No gain, speed ceiling, watchdog stale threshold or startup grace increased.

## Exact checks and retained intermediate failures

All commands ran from `/home/mattb/dsim-lab`. Every pytest command below used:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

The runtime environment intentionally preserves the sourced overlay and does
not prepend the source `ros_esc` directory, which previously selected stale
tracked package metadata. Final combined command:

```bash
ROS_DOMAIN_ID=178 DSIM_M3_TEST_ARTIFACT_DIR=/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_controller_clock_v5 PYTHONPATH=extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_controller_motion.py ros2_ws/src/ros_esc/test/test_q1_controller_clock.py ros2_ws/src/ros_esc/test/test_q1_controller_clock_transport.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_controller_clock_v5.log 2>&1
```

The58 inherited moving tests include actual subprocess SIGINT after observed
nonzero VERIFY control, clean exit0 and final zero. The separate actual DDS
fixture sends27 source-stamped poses between nine100ms clock ticks, plus
near-future state/filter messages, and observes no controller fault during that
normal timing pattern. It checks original receipts remain before source stamps,
covered inputs stay active, a deliberately excessive future pose forces zero,
fresh data can recover this isolated controller, and the steady timer forces
zero with no further `/clock`. It uses scoped `/m3_controller_test/*` command
topics and no Gazebo or physical `/cmd_vel` graph. It does not emulate the
supervisor's permanent FAILSAFE latch or claim a complete acquisition passed.

Final inherited subset command:

```bash
ROS_DOMAIN_ID=178 PYTHONPATH=extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_deferred_signal_shutdown.py ros2_ws/src/ros_esc/test/test_observability_contract.py -k "controller or recording or supervisor_owned_assist or sigint or robust_startup or signal_request" > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_controller_clock_legacy_v2.log 2>&1
```

The adjacent `q1_controller_clock_manifest.json` retains complete exact commands,
source hashes and every log/child-log hash. Intermediate versions were not
discarded or counted as additional experiments:

| Log suffix | Outcome | Diagnosis and correction |
| --- | --- | --- |
| `moving_v1` | 1 failed,57 passed;2.47s | Redundant covered-stop zero publication; removed the duplicate while keeping immediate future-stop zero. |
| `v2` | 1 failed,95 passed;21.92s | Fixed-clock SIGINT fixture exposed readiness recovery after an exact filter repeat; reevaluate admitted fresh data without refreshing receipts. |
| `v3` | 1 failed,96 passed;3.07s | CDR padding changed duplicate fingerprint; replaced serialization with existing canonical payload hash. |
| `transport_v1` | 1 failed;0.69s | All27 leading poses exercised; final exact floating-point3.4 assertion changed to integer-nanosecond comparison. |
| `v4` | 98 passed;3.44s | First combined admission/DDS boundary. |
| `legacy_v1` | 19 passed,34 deselected;1.03s | Inherited subset before final origin/overflow assertions. |
| `v5` | 103 passed;3.44s | Final five added checks cover node overflow and pending pre-origin rejection. |
| `legacy_v2` | 19 passed,34 deselected | Final source boundary, including preserved legacy receipt timing. |

Syntax and scoped whitespace checks passed:

```bash
python3 -m py_compile ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py ros2_ws/src/ros_esc/ros_esc/controller_node/clock_admission.py ros2_ws/src/ros_esc/test/test_q1_controller_clock.py ros2_ws/src/ros_esc/test/test_q1_controller_clock_transport.py
git diff --check -- ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py ros2_ws/src/ros_esc/test/test_v2_controller_motion.py
```

The enclosing context validator passed before editing. Final source/installed
integration and any new acquisition remain separately recorded parent-owned
steps; these checks do not qualify the detector or direction method.
