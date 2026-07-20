builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid
string controller_type

float64[6] gesc_command_unsaturated
bool gesc_command_unsaturated_valid

float64[6] supervisor_contribution
bool supervisor_contribution_valid

float64[6] combined_command_unsaturated
bool combined_command_unsaturated_valid

float64[6] final_command
bool final_command_valid

bool[6] saturation_flags
bool[6] limit_valid
float64[6] lower_limits
float64[6] upper_limits

float64 k_vx
float64 k_wz
bool gains_valid
