# Additive policy companion; existing GescDirectionDiagnostics CDR is unchanged.
# Join exactly on all publication, run/stream, reset and observation identities.
# policy_schema_version identifies this protocol; source_schema_version retains
# the independent acquisition schema. NaN marks unavailable numerical values.
uint16 policy_schema_version
uint16 source_schema_version
builtin_interfaces/Time stamp
builtin_interfaces/Time time_origin
string run_id
string stream_contract_id
string frame_id
uint64 diagnostic_sequence
uint64 reset_sequence
string reset_reason
uint64 source_sequence
uint64 observation_id
builtin_interfaces/Time source_stamp
builtin_interfaces/Time cost_source_stamp
uint64 objective_revision
string objective_sha256
string registry_digest
uint64 affine_revision
string direction_policy
string policy_config_sha256
string output_units
float64 configured_mean_weight
float64 actual_blend_weight
builtin_interfaces/Time rolling_start
builtin_interfaces/Time rolling_end
float64 mean_magnitude
# Normalized by the original source cycle duration; units are cost/metre.
float64 norm_denominator
float64 norm_error
float64 numerator_margin
float64 coherence
float64 coherence_lower
float64 coherence_upper
float64 coherence_threshold
uint32 norm_new_evaluations
uint32 norm_window_evaluations
bool mean_full
bool coverage_valid
bool warmup_valid
bool coherence_available
bool selected_policy_qualified
bool output_valid
bool fallback_used
bool blend_allowed
string numerical_reason
string fallback_reason
