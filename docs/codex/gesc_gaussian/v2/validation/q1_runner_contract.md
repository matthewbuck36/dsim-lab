# Q1 duration and launch wiring

The initial Q1 wiring checks pass: explicit observation selection reaches the
supervisor launch argument, simulated duration reaches the existing recorder,
and the inherited wall-duration/default-off path remains selectable. Invalid
durations and nonboolean observation selectors are rejected. This is source
validation, not acquisition or scientific qualification.

From the repository root, after sourcing `/opt/ros/humble/setup.bash` and
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash`:

```bash
ROS_DOMAIN_ID=188 PYTHONPATH="ros2_ws/src/ros_esc:extremum-seeking/src${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_runner_contract.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_contract.py ros2_ws/src/ros_esc/test/test_v2_stream.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_runner_contract_v2.log 2>&1
```

Result:76 passed in1.09s. Log SHA256:
`914de358e218d35cc60f1a061e0dacae27d4080d362ddab50acbf91509c68c5a`.
The retained v1 attempt had75 passes and one fixture failure in0.98s: the test
expected lowercase `true`, while the existing launch builder emits `True`.
Only the expectation changed. Its log at the same root,
`q1_runner_contract_v1.log`, has SHA256
`3af2b3b975c0e83f2af19e7f8612242ef53c1b8f42e963ced0eb368d8142f96e`.

The later explicit acquisition-purpose/single-run-ID extension has separate
focused evidence in `q1_acquisition_safety.md`; this76-check result predates it.
The package directly declares its existing supervisor's new `rcl_interfaces`
use, and installs the Q1 scenario through the existing setup data-file list.
Those packaging changes require the final Q1 build/installed-binding preflight.

## Prospective time budget

No additional simulation was run to select a wall budget. Frozen inventory
seed19801 records clock0.1–294.5s between wall bag receipts
1785519061791162584 and1785519358383918688ns (296.592756104s).
Its retained recorder metadata has ready_at_utc17:31:04.039841 and
wall_end_utc17:36:04.391734 on2026-07-31 (300.351893s). This is approximately
real-time historical operation, not proof of current speed. Q1 retains its
240s per-process ceiling and1200s outer acquisition budget, explicitly
partitioned in `../q1_plan.md`. A timeout remains a failed/incomplete exposure.
