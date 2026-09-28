# ROS ESC

Shared numerical methods and ROS adapters for the original ESC algorithms and
V3. Start with [usage](../../../docs/esc_usage.md),
[architecture](../../../docs/esc_architecture.md), and
[history](../../../docs/esc_history.md).

The V3 graph uses `controller_node --v3` as the only base-command owner. Its
local algorithm state, estimator, detector, Gaussian design and registry use a
private bounded numerical worker. `sensor_observation_node` assembles observed
cost, phase and odometry once; it supplies no source-map truth to the core.
Original methods retain `filter_node` and the original controller numerical API.

The package installs 11 console entries:

| Responsibility | Entries |
| --- | --- |
| Gazebo sensor/arm adapters | `encoder_node`, `sensor_pose_node`, `rotate_frame_node`, `cost_function_node` |
| Original filtering and shared control selection | `filter_node`, `controller_node` |
| V3 observation adapter | `sensor_observation_node` |
| Optional live Matplotlib plot | `live_plot_node`, `data_collection_node` (same plot entrypoint) |
| Optional recording and offline analysis | `record_bag`, `analyze_bag` |

[Profiles](config/profiles) own configuration; run scripts never build or rewrite
it. Plotting and recording are observers and do not authorize motion. Shared
algorithm code has no required Gazebo or plotting import. Physical adapters
remain in external `turtlebot3_vehicle_nodes`; this refactor does not deploy to
or qualify the physical robot. Gaussian V1/V2 and the previous detailed guides
are preserved in the frozen history and pre-refactor archive.
