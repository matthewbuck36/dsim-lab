# Actual model transform; acquisition time of cached odometry is not implied.
uint16 schema_version
builtin_interfaces/Time stamp
builtin_interfaces/Time time_origin
string run_id
string stream_contract_id
string frame_id
uint64 source_sequence
builtin_interfaces/Time model_input_stamp
builtin_interfaces/Time cost_publication_stamp
float64 legacy_cost_source_timestamp_sec
uint32 channel_count
float64[] sensor_x_m
float64[] sensor_y_m
float64[] sensor_world_phase_rad
bool model_input_stamp_valid
bool sensor_transform_valid
