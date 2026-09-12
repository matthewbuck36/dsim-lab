# Q1 launch frontend correction — 2026-09-09

The final launch XML parses with the installed Humble frontend, preserves the
selected CLI values as single arguments, and supplies both V2 ROS parameters as
STRING values, including empty legacy defaults. This is a source/startup check;
no Gazebo, algorithm graph, acquisition, physical hardware or scientific
qualification was executed. The three explicit RCL type fixtures create only
an inert parameter-only node, without an executor or algorithm owner.

The original Q1 source contract
`0921e90a3d705fe1ff46abcd47f4116b559c9f542d0dd59ad7cc8d418c5a1e05`
remains preserved and UNRELEASED after its failed startup preflight. The parent
owns its separately named technical replacement freeze and checkpoint. This
correction does not release either acquisition or the M4 pilot.

## Cause and exact change

Humble's installed `launch.actions.ExecuteProcess._parse_cmdline` first parses
substitutions and calls `shlex.split` separately on each static text fragment.
A quote opened before `$(var ...)` and closed after it is therefore unmatched
when that first fragment is parsed. The old substitute-first-then-shlex tests
did not exercise this order and had passed incorrect XML.

The only runtime source changed is
`ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`:

- Remove cross-substitution quotes from `--v2-run-id=`,
  `--v2-stream-config-json=` and `--v2-sensor-geometry-config=`. Launch resolves
  each substitution inside one argv element; no shell splits its value.
- For the five existing ROS-parameter consumers, emit a YAML single-quoted
  scalar with each shell-style quote entirely inside a static fragment:
  `-p &quot;v2_run_id:='&quot;$(var v2_run_id)&quot;'&quot;`, and the same form for
  `v2_stream_config_json`. The resolved argument is, for example,
  `v2_run_id:='123'`, or `v2_run_id:=''` for the inherited empty default.
- Keep the existing executable actions, owners, command routing, conditions,
  defaults, numerical values and units. A short XML comment documents why the
  spelling is deliberate.

The single-quote wrapper is bound to the existing validated V2 grammar in
`ros_esc/v2_stream.py`: run IDs, ROS topic/frame names, hashes, basis names and
fixed geometry strings contain no apostrophes. The selected runner emits
canonical single-line JSON. This is not an escaping promise for arbitrary
invalid descriptor payloads. Spaced valid JSON for both schemas survives
exactly; CLI geometry paths independently preserve spaces and apostrophes.

An intermediate block-scalar spelling fixed frontend parsing but failed the
real RCL parser: an empty `|-` scalar produced “No value”, and `123` became an
INTEGER despite PyYAML returning a string. It was replaced with the explicit
quoted-scalar form above; neither parser/type failure was waived.

## Regression scope and retained outcomes

New `test_q1_launch_frontend.py` parses the complete actual XML, resolves all
existing executable commands including the delayed controller, and prevents
process/timer action execution. It covers empty stationary defaults, schema1
and schema2 JSON, numerical/boolean-looking IDs, geometry path punctuation,
all four actual Q1 runner configurations, real RCL argument parsing and three
actual RCL STRING declarations. It also reproduces the original unmatched
static-fragment quote as an expected parser exception.

With parent authorization, the four affected resolver fixtures in
`test_v2_stream.py`, `test_v2_source_contract.py` and
`test_v2_lifecycle_contract.py` now use actual Humble static-fragment parsing
followed by atomic LaunchConfiguration resolution. Their schema/owner checks
remain. No direct ROS transport fixture or runtime owner outside XML changed.

All logs are retained under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`:

| Log | Outcome and boundary |
| --- | --- |
| `q1_launch_parse_v1.log` | Parent's original `--show-args` preflight, exit1: No closing quotation. No launch action executed. |
| `q1_launch_frontend_v1.log` | Exit1: 8 failed, 3 passed in5.07s. New resolver fixture accidentally inspected unrelated spawn Node runtime-local arguments; restricted it to the assigned executable commands. Full XML parsing remains. |
| `q1_launch_parse_v2.log` | Exit0 after static quote correction; this predates the subsequent real RCL empty/numeric type correction. |
| `q1_launch_frontend_v2.log` | Exit1: 4 failed, 89 passed in7.94s. Real RCL found empty-block rejection and numeric block-scalar INTEGER interpretation. |
| `q1_launch_frontend_v3.log` | **Exit0: 96 passed in9.05s.** Final new frontend tests and all three affected contract modules. |
| `q1_launch_parse_v3.log` | **Exit0:** final installed launch `--show-args`, under30s timeout. |

The two successful `--show-args` outputs have the same hash because argument
declarations did not change; only the child argument transport changed.

Exact final commands, run from `/home/mattb/dsim-lab`:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=191 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_launch_frontend.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_launch_frontend_v3.log 2>&1
ROS_DOMAIN_ID=191 timeout 30s ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_launch_parse_v3.log 2>&1
```

The earlier frontend v1 used the same environment/90s limit and only the new
test module. Frontend v2 used the same four modules as v3. All failed logs remain.
Context preflight `timeout 30s
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
v2 implement` passed. The assigned tracked-file `git diff --check` passed.
The isolated installed launch path resolves by symlink to the XML in this
checkout, verified with `readlink -f`; no stale copied XML was tested.

## Frozen source and log receipts

| Path (source paths relative to repository) | SHA256 |
| --- | --- |
| `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml` | `d69d3727c942b379a040923412956bbbce4e3eaeae6fb0726eda647be31ac579` |
| `ros2_ws/src/ros_esc/test/test_q1_launch_frontend.py` | `144b82c465c43dcdab65da25f524467bff871fb7307a78ede2168504fda53f2c` |
| `ros2_ws/src/ros_esc/test/test_v2_source_contract.py` | `f68f5272f6b9c57c4d00fa2bf74ee4e81b72d40dbfe8ee084a423a6241be1cb0` |
| `ros2_ws/src/ros_esc/test/test_v2_stream.py` | `b3a65d8e5e2c50235380cdae4418c49459dc3f4e34753b1f5a865f1baf2227cf` |
| `ros2_ws/src/ros_esc/test/test_v2_lifecycle_contract.py` | `905456dbbe093fc484e639972aad9fddfefcf12b926c6c7709b9885785d651ab` |
| `q1_launch_parse_v1.log` | `f22274182058d508c36062b01cd88c73bf9a606306d78daf079e6b8069bc4213` |
| `q1_launch_parse_v2.log` and `q1_launch_parse_v3.log` | `49695eb54899e2c725aa3add8ccb183dcdefd7c868c21c115a08c37a4a20564f` |
| `q1_launch_frontend_v1.log` | `dff5bcd3315c3a82a60c0ea9b8f13476880279f25887c1c663f423fa339fc63b` |
| `q1_launch_frontend_v2.log` | `42cb5bee7fb129d7d9e7b4d8d5a2d8ce2a31480dcf33fee1664ec45b93668ecb` |
| `q1_launch_frontend_v3.log` | `358769bbccb4cc00242963f661b678c86701629c2cfee6c0ac86778ffeb06bca` |
