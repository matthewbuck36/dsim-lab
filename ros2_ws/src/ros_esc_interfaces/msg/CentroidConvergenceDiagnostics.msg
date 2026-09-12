# Opt-in centroid output. All Time fields use absolute ROS time.
# metric_mode binds score_m (metres; never r_mean_m2):
# centroid_windows_v2: sum of five adjacent centroid distances.
# centroid_two_block_v2: distance between oldest-three and newest-three means.
# Both retain six equal-duration windows and five adjacent displacement_m values.
builtin_interfaces/Time stamp
builtin_interfaces/Time receipt_stamp
builtin_interfaces/Time source_stamp
bool source_valid
builtin_interfaces/Time epoch_started_at
builtin_interfaces/Time history_start
builtin_interfaces/Time history_end

# SEARCH epochs are local to this detector within the supervisor run_id.
# A supervisor binds a candidate to (run_id, search_epoch, confirmation_sequence).
string run_id
string frame_id
string source_pose_topic
string metric_mode
uint64 search_epoch
uint64 confirmation_sequence
uint64 reset_sequence
string reset_reason

float64 window_duration_sec
float64 epsilon_m
float64 maximum_radius_m
float64 score_m
float64 confinement_radius_m
float64 center_x_m
float64 center_y_m
float64 represented_duration_sec
float64 maximum_source_gap_sec
uint32 sample_count
uint32 completed_window_count
builtin_interfaces/Time[] window_start
builtin_interfaces/Time[] window_end
float64[] centroid_x_m
float64[] centroid_y_m
float64[] displacement_m

# Invalid/incomplete values are not a zero-valued convergence score.
bool history_valid
bool metric_valid
bool confinement_valid
bool eligible
# True once per SEARCH epoch; confirmation_sequence persists in later messages.
bool confirmed
