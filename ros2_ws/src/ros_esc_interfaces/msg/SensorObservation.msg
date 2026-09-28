# One raw observation, assembled once by the selected environment adapter.
uint8 DEVICE_TIME=0
uint8 ESTIMATED_TIME=1
uint8 RECEIPT_TIME=2
builtin_interfaces/Time stamp
builtin_interfaces/Time receipt_stamp
string source_instance
uint64 sequence
bool device_sequence_valid
uint64 device_sequence
uint8 timestamp_basis
string frame_id
geometry_msgs/Pose2D source_pose
float64 raw_cost
float64 phase_rad
float64 sensor_x_m
float64 sensor_y_m
float64 pose_support_age_sec
float64 phase_support_age_sec
# NaN means unknown; zero must not represent an unmeasured uncertainty.
float64 acquisition_uncertainty_sec
bool valid
string reason
