# Local TurtleBot mount-point agent instructions

Before any file operation, check `findmnt --mountpoint /home/mattb/tb3-pi`.
When unmounted, this directory contains local guidance, not robot source;
use the offline physical snapshot for source inspection. Write local guides
here only while unmounted; never mount/unmount or write to the robot as a side
effect of updating them. These instructions are hidden while SSHFS is mounted.
For mounted work, explicitly read the always-visible tracked copies in
`/home/mattb/dsim-lab/docs/environment_guides/tb3_pi_{README,AGENTS}.md`.

## Physical code rules

- Read the root README and `/home/mattb/dsim-lab/docs/environment_parameters.md`
  before changing physical launch/configuration files.
- Require physical algorithm `use_sim_time=False` and
  `supervisor_use_sim_time=False`; controller/filter use
  `--use-sim-time False`. Preserve explicit startup overrides in the shared
  clock helper; do not globally replace simulation-compatible defaults.
- Use `observability_source_mode=physical`, recorder `--mode physical`,
  hardware sensor adapters, and OpenCR `/odom` as algorithm pose. Keep Vicon
  evaluation-only. Do not introduce Gazebo sensor/controller interfaces or
  simulated light inputs into physical control.
- Preserve the selected physical controller ceilings `set_max_vx=0.05` m/s
  and `set_max_wz=0.30` rad/s. Other differing selected/hardware values are
  in the README; these are current configured choices, not universal tuning.
- Trace the selected wrapper, launch overrides and JSON, then resolved node
  values. `phase09_selected_profile.yaml` is evidence, not a parameter loader.
  Bare launch/generic JSON defaults do not represent the selected physical run.
- Retain Pi `~/ros2_ws/src/...` paths in robot configurations. Keep shared
  algorithms aligned without overwriting physical adapters or legacy behavior.
- Preserve source, retained failed experiments, and backups. Documentation or
  source parity does not prove an installed build or physical readiness.
- Root guidance is not authorization for mounting, transfers, Pi builds,
  devices, ROS graphs, recording, or motion. Honor existing user authorization;
  otherwise leave physical execution to the operator's Pi terminal.

These folders are not Git projects on the laptop. Start an agent session at
this documented root or explicitly provide this AGENTS file; do not assume
ancestor discovery from arbitrary nested working directories. Versioned copies
of these instructions live under `dsim-lab/docs/environment_guides`.
