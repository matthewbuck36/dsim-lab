# M2 reference launcher correction — 2026-09-09 UTC

The first shell launcher failed with exit1 while sourcing ROS, before Python
or the fixed reference function started:

`/opt/ros/humble/setup.bash: line 8: AMENT_TRACE_SETUP_FILES: unbound variable`.

Retain the exact launcher and log:
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1.{sh,log}`.
Inspection immediately after failure confirmed that `m2_references_v1/` did
not exist. There are no target, method or model receipts from this invocation.

Create a separate `m2_reference_command_v1a.sh` with `set -eo pipefail` in place
of `set -euo pipefail`, allowing the installed ROS setup's optional variables.
All Python content, frozen source owners, input population, output namespace,
numerical settings and the timeout300s bound remain identical. This is the first
scientific execution of the fixed version, not repetition or replacement of a
failed scientific result. Its log is separate and neither launcher is overwritten.

The recoverable pre-reference source snapshot has 76 files at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m2_pre_reference_v1/`.
Manifest SHA256:
`22de2c6fc4032bfbee87ab9be1182de59e9b5deca3db44dd91e77823eca67059`.
This note changes no reference owner or protocol file in that frozen study.

## First Python invocation: preflight failure

The corrected launcher reached Python and exited1 in
`_v2_direction_recorded_binding` with
`ValueError: captured live robot_description unavailable`. Retain
`m2_reference_command_v1a.log`. The `m2_references_v1/` output directory still
does not exist: configuration preflight precedes directory creation, target
freezing, method replay and any field calculation. There are no scientific
results or numerical receipts from this invocation.

Read-only diagnosis must determine whether the recorded parameter structure was
misread or live robot-description data was not captured. Do not silently remove
the check or assert unavailable live geometry. Any justified correction gets a
separate documented launcher/evidence version before execution; the original
command, source snapshot and failed log remain recoverable.
