# M2 upstream source-clock correction validation

Verified 2026-09-09 UTC against `m2_source_clock_correction.md`. This records
source implementation and actual-callback tests, not a new retained-bag replay,
field evaluation, Gazebo run, or complete M2 scientific qualification.

The existing encoder and sensor-pose owners now accept
`--continuous-search-mode=rolling_gesc_v2`. They preserve JointState acquisition
time as one relative key through the transform, freeze the Timekeeper origin,
and discard/log invalid input. The first finite contradictory or regressed
observation is forwarded once for downstream invalidation, as specified in the
amendment below. Identical packets are idempotent; bounded 1024-entry histories
retain conflict tombstones. The sensor
transform still uses its cached pose, without a simultaneous-acquisition claim.

For descriptor schema2 (`cost_key_basis=model_input_time`), the existing source
cost owner queues detached transforms in received order. Evaluation waits for
local ROS-clock coverage. Pending inputs are bounded by 1024 entries and 0.5s
of original ROS/steady receipt and source age; a steady-clock timer expires
inputs even while ROS time is held. Retransmissions cannot refresh age. Source
rollback/conflict/capacity, clock rollback, expiry, and numerical exceptions are
explicit discard conditions. Clock rollback clears the pending/model-order
history. Raw, provenance, and source-cost keys use the acquisition-relative
value; provenance separately retains actual integer publication time and uses
wire schema2. Default behavior and schema1 publication-key fixtures remain.

Owned source and tests:

- `ros2_ws/src/ros_esc/ros_esc/encoder_node/encoder_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/sensor_pose_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py`
- `ros2_ws/src/ros_esc/test/test_v2_source_contract.py` (explicit schema1 fixture)

The new tests construct real owner nodes and call their actual callbacks;
clock progression, publications, and cost/noise functions are deterministic
fixtures. They cover 141ms and175ms acquisitions under one held100ms clock,
both published at200ms with distinct exact keys; nonzero origin; unchanged
schema1/default keys; detached geometry; duplicate/conflict/regression handling;
origin mismatch; expiry without new input; original age despite retransmission;
1024-entry capacity; rollback recovery; model exceptions; and freshness loss
during model work. No command or motion owner is started. Full upstream DDS is
a separate agent-owned transport test and is not claimed by this record.

Exact preflight from repository root:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

Result: exit0, context complete.

Both pytest commands used:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

Initial focused run:

```bash
ROS_DOMAIN_ID=181 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_upstream_clock_v1.log 2>&1
```

Result: exit0, 28 passed in1.19s. Source review then added explicit model-error
discard/recovery and model-order reset on clock rollback, with two tests.

Second focused regression:

```bash
ROS_DOMAIN_ID=181 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_light_brightness.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_upstream_clock_v2.log 2>&1
```

Result: exit0, **60 passed in1.92s**, no skips or failed runs. Both runs report
one inherited `calculate_quaternions` square-root warning for a tiny negative
unused component; the tested emitted transforms remain finite and valid.
Quaternion conversion is unchanged. Scoped `git diff --check` passed.

Source SHA256 receipts at the second focused regression:

| File | SHA256 |
| --- | --- |
| encoder_node_script.py | `113a76ae528a94504b9ef9e6a02608b9bd1a6bd65e58a70ae0360840aa1d288c` |
| sensor_pose_node_script.py | `f2beaf4dfb9eb01a9d189dfe9f36c8e59705998b5b42a3314b67528793e9f726` |
| cost_function_node_script.py | `5cd0ea5a5600045e45ec652175a159c92539c47aa30fc3a9fb4ca584d79b4f78` |
| test_v2_upstream_clock.py | `46cbd547350d7c4f91e4a6b2340d91b1079c6a62ba1437d940ffbae3b2b6be53` |
| test_v2_source_contract.py | `3abc9d5134987e13190de72f9089440e49506c8fe233b09e5e25925a26f54b0b` |

## Narrow conflict-propagation amendment and final checks

Independent review found that silently dropping a contradiction upstream could
leave an already consumed sample in rolling confidence. The approved correction
therefore forwards exactly the first finite contradictory/regressed encoder
reading, with its real phase and original key. The sensor-pose owner likewise
forwards one finite contradictory transform. Neither shared stream carries an
invented NaN or empty encoder array; the rotation owner continues receiving a
finite observed phase. Local tombstones suppress subsequent packets for the
disputed key.

The source-cost owner cancels/tombstones that key and sends one schema2 invalid
`SourceSampleProvenance` through its existing sole publisher. It keeps the same
run/stream/frame/origin, disputed key and model stamp, and advances source
sequence. Both validity flags are false; channel count is zero and geometry
arrays empty. Its notification stamp is the current clock. The cost publication
stamp is the remembered original actual publication when one exists, otherwise
zero; the notification never invents a new raw cost publication. Publication
receipts and tombstones are each bounded to1024 entries.

The paired composer/filter change belongs to the root integration owner:
envelope-validated invalid provenance must tombstone the disputed key as well as
reset history, preventing late valid packets from restoring it. That complete
transport race is separately tested in the full upstream DDS fixture.

The upstream callback tests now assert finite first-conflict forwarding,
suppression of repeats, pending-key invalid notification with zero publication,
published-key notification with the original publication, and the entire actual
encoder-to-sensor-to-source invalidation chain. No model or legacy behavior
changed in this amendment.

```bash
ROS_DOMAIN_ID=181 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_light_brightness.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_upstream_clock_v3.log 2>&1
```

Using the same ROS/isolated overlay setup above: exit0, **61 passed in1.89s**,
no skips or failures. The same inherited square-root warning remains; tests
explicitly assert finite transmitted quaternion components. Source edits stopped
at these final receipts:

| File | SHA256 |
| --- | --- |
| encoder_node_script.py | `26daa65446c79a99c6cc09b752a476e64ae110231ac302a203913d56f009b230` |
| sensor_pose_node_script.py | `027c2633274ec1f58b1b70045b0e7ddef4444b35fab9226bde63fd0f86e44f7e` |
| cost_function_node_script.py | `2bccf998b56967e91ea090d3aad56e55273abe5243f047cfdf867581130be29e` |
| test_v2_upstream_clock.py | `3b5193d581ec3f6d81092bbbcac01ae9d2629e4bf2e4d3f0643fcb87121c9cbd` |
| test_v2_source_contract.py | `3abc9d5134987e13190de72f9089440e49506c8fe233b09e5e25925a26f54b0b` |

The fixed failed reference version and all historical artifacts remain untouched.
No commits, pushes, physical edits, or clock-rate changes were performed.
