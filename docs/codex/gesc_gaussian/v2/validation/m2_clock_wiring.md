# M2 source-clock configuration and launch checks — 2026-09-09 UTC

The bounded wiring part of [m2_source_clock_correction.md](../m2_source_clock_correction.md)
is implemented and its focused checks pass. This record covers descriptor,
runner, launch syntax and recorder selection. It does not qualify acquisition
transport, natural trajectories, detector parameters or the Gazebo pilot.

`v2_stream.py` preserves schema1's exact key set and canonical stream hash;
its absent `cost_key_basis` means `publication_time`. Schema2 requires the
additional key `cost_key_basis` with the exact value `model_input_time`.
Missing/unknown keys and unsupported versions/bases fail validation. The actual
rolling-mode runner now emits schema2 consistently in launch arguments and
retained metadata, including the selected nominal/delayed topic bindings.
These descriptor versions are separate from ROS message schema versions.

Post-wiring integration note,2026-09-09 UTC: these remain distinct fields, but
the source-clock correction now requires matching versions in the typed
source/objective/direction/observation envelopes. Schema2 integration/build
checks are recorded in [m2_clock_admission.md](m2_clock_admission.md); the
focused wiring results below are preserved at their original boundary.

The existing encoder and sensor-pose launch entries receive
`--continuous-search-mode=$(var continuous_search_mode)`. The default selector
remains `stationary_v1`; upstream positional topics/configuration are preserved.
Both descriptor versions survive XML substitution, shell argument splitting
and ROS-parameter YAML-string syntax through all six existing downstream
consumer entries. These are parsing checks, not process launches.

The inherited `test_v2_recording_contract.chain()` message fixture is explicitly
pinned to schema1 because it represents publication-key `.27` and model-input
time `.25`. The selected runner/metadata fixtures remain schema2; the timestamp
correction's schema2 validator/transport checks are recorded by their owners.

## Exact focused commands and results

Working directory: `/home/mattb/dsim-lab`. Preflight:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

Result: exit0, `Phase v2 implement context is complete.`

Each pytest invocation was executed in a fresh `bash -c` shell with this prefix:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/ros2_ws/src/extremum_seeking_control:$PYTHONPATH
```

The initial command, before the two additional schema-specific downstream
argument-roundtrip checks, was:

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_stream.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_wiring_tests.log 2>&1
```

Result: exit0, **44 passed in0.66s**. The final command was:

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_stream.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_wiring_tests_final.log 2>&1
```

Result: exit0, **46 passed in0.66s**. Selected existing runner/recorder checks:

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py -k "runner_shares or launch_cli or selected_streams_required or selection_requires" > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_selection_tests.log 2>&1
```

Result: exit0, **8 passed,32 deselected in1.59s**. Deselection deliberately
limits this check to configuration/launch/selection; it is not a passing result
for those other tests. None of these tests instantiates ROS nodes or evaluates
the light model. Existing source/recording modules are imported from the source
tree and generated messages from the retained overlay.

Syntax and scoped whitespace checks also passed, exit0:

```bash
python3 -m py_compile ros2_ws/src/ros_esc/ros_esc/v2_stream.py ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py
git diff --check -- ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml
```

## Byte provenance at this wiring boundary

Logs are retained under `/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Log | SHA256 |
| --- | --- |
| `m2_clock_wiring_tests.log` | `1e3664b06a50bcce1e0b5994bb96954d532362bedacffbc9e5f9de38eb6aa29b` |
| `m2_clock_wiring_tests_final.log` | `3b8df262c18ea9f3083910f1cd36601382f124a6ba0c8f9610b8e6389047c148` |
| `m2_clock_selection_tests.log` | `526b248db04e4c41f01c6c25af0a2a88118063928ba6d0c358e0b101396d13a1` |

| Source/test owner | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/v2_stream.py` | `7e4caf66723d6dd8159478995799c076ec3fb45da91060141cacef70bbb842d2` |
| `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py` | `33397915123bf8821c4a8307d6c5658fb92ff2111d0839e261bda81c3274ea47` |
| `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml` | `9eaa534fc7c0f67a50590a45d2228df7769ae02b74eb076c18ef2009908857e4` |
| `ros2_ws/src/ros_esc/test/test_v2_stream.py` | `146e6b0c03af15adcb0ee499bb398ebe4675c22ae6fce0537aeccf83d9daa716` |

No preserved reference, evidence snapshot, field calculation, bag replay,
Gazebo run or physical action was changed or executed by this wiring task.
