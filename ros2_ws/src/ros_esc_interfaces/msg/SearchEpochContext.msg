# Lifecycle protocol version, independent of nested stream-observation schema.
uint16 schema_version
builtin_interfaces/Time stamp
builtin_interfaces/Time time_origin
string run_id
string stream_contract_id
string frame_id
uint64 search_epoch
uint64 context_sequence
builtin_interfaces/Time started_at
uint8 algorithm_state
bool valid
