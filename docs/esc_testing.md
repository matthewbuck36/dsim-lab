# Software checks and evidence limits

Build and source the current workspace using [the usage guide](esc_usage.md).
Run the complete active suite from the repository root, with an explicit bound:

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ROS_LOCALHOST_ONLY=1 timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test
```

The ROS checks use isolated local DDS domains 187–190. They do not launch
Gazebo, connect to the Pi, start serial/GPIO devices or actuate a robot. Keep
those domains free of other experiments while running the suite.

Coverage includes original profile/configuration parity, cost signs and units,
selected numerical golden fixtures, sample timing/support, controller startup,
expiry/recovery, optional-worker deadlines/failures, stale proposal rejection,
registry commits, moving verification, original escape transitions, optional
telemetry isolation, ordinary rosbag decoding and Matplotlib rendering. An
actual local ROS subprocess test observes the final zero after SIGINT; separate
signal tests cover SIGTERM cleanup ordering.

The golden fixture records original source hashes. It checks selected numerical
cases; it is not a proof of general algorithm equivalence. The local scheduling
test checks that a busy worker does not stop command publication on this host;
it does not establish Raspberry Pi resource headroom or OS-level stopping.

Exact build/test commands, failures, corrections and retained paths belong in
[the refactor status](codex/gesc_gaussian/v3/refactor_status.md). The
[requirement audit](codex/gesc_gaussian/v3/refactor_completion_audit.md) maps the
accepted scope to current source and evidence. Large logs and bags remain in
external experiment storage, outside Git.

## Subsequent Gazebo work

Software refactoring and behavioral qualification are separate milestones.
Future V3 tests must model the approximately 5 Hz acquisition stream,
nonuniform measured arm speed, acquisition-time uncertainty, pose/phase delay,
clock/scheduling jitter, missing or duplicate data and CPU/recording pressure.
Measure actual base translation through verification/design and count every
protective interruption. Retain failed runs and distinguish complete recordings
from successful navigation.

The inherited optional ADC model is not a validated UNO quantizer. V3 presently
uses it disabled; correct/validate the observation model before claiming
realistic ADC behavior. The Arduino's fixed application rate must not be
mistaken for its ADC hardware limit. Preserve working physical V1 throughout;
no physical V3 deployment is included in this refactor.
