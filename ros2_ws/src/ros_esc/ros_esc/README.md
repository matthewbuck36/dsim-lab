# Python implementation

The active code has three parts:

- `gesc_v3`: shared algorithm core, observation adapter, command runtime and
  private bounded numerical worker. State, objective, detector and Gaussian
  registry are local to the command owner.
- Original numerical objects and `encoder_node`, `rotate_frame_node`,
  `sensor_pose_node`, `cost_function_node`, `filter_node`, `controller_node`:
  retained ESC APIs and small ROS adapters. `controller_node --v3` selects V3.
- `data_collection_node` and `run_tools`: optional live Matplotlib plotting,
  ordinary bag recording, and offline analysis. They have no motion authority.

`profiles.py` resolves installed configuration. `config_parsing.py` loads built-in
module references or existing custom file-based objects without mutating input
configuration. The shared core does not require Gazebo or Matplotlib imports;
physical adapters stay in the external `turtlebot3_vehicle_nodes` workspace.

See [usage](../../../../docs/esc_usage.md),
[architecture](../../../../docs/esc_architecture.md), and
[history](../../../../docs/esc_history.md). Old distributed Gaussian owners and
previous detailed READMEs are preserved as historical references, not active
runtime modes. Source/build checks alone do not qualify robot behavior.
