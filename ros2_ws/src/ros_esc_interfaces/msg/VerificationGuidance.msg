# Opt-in centered collection proposal, atomically bound to an AlgorithmState.
# Existing public message wire layouts remain unchanged.
uint16 schema_version
uint64 publication_sequence
string state_sha256
builtin_interfaces/Time stamp
builtin_interfaces/Time state_stamp
builtin_interfaces/Time pose_stamp
builtin_interfaces/Time accepted_at
builtin_interfaces/Time collection_admitted_at
builtin_interfaces/Time verification_expires_at
builtin_interfaces/Time command_expires_at
string run_id
string stream_contract_id
string frame_id
string mode
uint64 search_epoch
uint64 candidate_id
uint8 algorithm_state
bool collection_started
float64 center_x_m
float64 center_y_m
float64 linear_x_mps
float64 angular_z_radps
bool valid
string reason
