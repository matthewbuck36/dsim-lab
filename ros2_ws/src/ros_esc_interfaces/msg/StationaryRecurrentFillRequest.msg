# Recurrent Arm B input to the existing stationary robust fill owner; schema 1.
# Full model and original source/admission identity remain in confirmation.
# source_timestamp is this request's (stamp - time_origin), in seconds.
uint32 schema_version
builtin_interfaces/Time stamp
builtin_interfaces/Time time_origin
builtin_interfaces/Time expires_at
builtin_interfaces/Time confirmation_received_at
builtin_interfaces/Time confirmation_accepted_at
uint64 request_sequence
uint8 CREATE=1
uint8 TARGETED_REDESIGN=2
uint8 operation
uint64 target_fill_id
uint64 target_cluster_id
uint32 target_revision
ros_esc_interfaces/RecurrentConvergenceDiagnostics confirmation
bool candidate_evidence_valid
float64 candidate_cost_estimate
float64 candidate_cost_mad
float64 candidate_cost_uncertainty
float64 candidate_cost_lower
uint32 candidate_rotation_count
float64 source_timestamp
string request_sha256
