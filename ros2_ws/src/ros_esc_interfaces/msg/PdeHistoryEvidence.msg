# Additive identity wrapper for inherited PDE transport-filter state.
# These bounds describe actual admitted input support, not exact PDE-bin times.
uint16 schema_version
builtin_interfaces/Time stamp
builtin_interfaces/Time time_origin
string run_id
string stream_contract_id
string frame_id
uint64 search_epoch
uint64 context_sequence
uint64 history_sequence
builtin_interfaces/Time epoch_started_at
builtin_interfaces/Time input_start
builtin_interfaces/Time input_end
builtin_interfaces/Time latest_input_receipt
StampedFloat64MultiArray history
string history_sha256
bool valid
