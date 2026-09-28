# DSIM Lab

ROS 2 Humble/Gazebo workspace for extremum-seeking source seeking. The active
implementation contains the original ESC methods and the V3 GESC/Gaussian
algorithm. V3 is under software qualification; Gazebo behavioral testing follows
this refactor. Physical V1 remains the protected robot installation.

Start with [usage and build commands](docs/esc_usage.md),
[architecture and recovery behavior](docs/esc_architecture.md), and
[environment parameters](docs/environment_parameters.md). Use the
[software test guide](docs/esc_testing.md) for bounded checks. The
[refactor status](docs/codex/gesc_gaussian/v3/refactor_status.md) records what has
actually been checked and what remains incomplete.

Interactive Gazebo runs keep automatic Matplotlib live plots. A small standard
rosbag records by default; plotting and recording are optional observers.
Ordinary runs continue until Ctrl+C. Neither a recorder failure nor a rejected
Gaussian candidate authorizes a terminal control failure.

## Workspace boundaries

- `ros2_ws/src/ros_esc`: shared algorithms, original configurable objects,
  observation interface, optional plotting/bag analysis and simulated adapters.
- `ros2_ws/src/ros_esc_interfaces`: eight messages; no command/acknowledgment
  protocol between Gaussian runtime nodes.
- `ros2_ws/src/turtlebot3_rotating_sensor`: Gazebo model, worlds, launch and
  short original-method aliases.
- `extremum-seeking`: original mathematical library.
- `/home/mattb/physical_TB3_files_snapshot`: offline physical source mirror.
  Physical `turtlebot3_vehicle_nodes` stays there and on the Pi, outside this
  repository. `/home/mattb/tb3-pi` is live only when mounted.

Read [AGENTS.md](AGENTS.md) before agent work. Source clocks, hardware adapters,
calibration and speed settings must be resolved for the selected environment;
a simulation change does not authorize deployment or motion.

## Preserved research

[Historical references and restoration evidence](docs/esc_history.md) locate
frozen V1/V2 source, reports, failed experiments and the verified pre-refactor
archive. Old implementations and policy tests are outside the active install.
Historical results retain their original acceptance limits.

V1 remains frozen at `1af67c6`; accepted V2 simulation remains at `d1779b6`.
Physical V2 remains paused and unqualified. This refactor has not modified the
Pi or run a new physical experiment.
