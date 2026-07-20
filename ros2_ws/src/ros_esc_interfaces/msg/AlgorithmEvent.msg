uint16 EVENT_UNSPECIFIED=0
uint16 EVENT_CONFIGURATION=1
uint16 EVENT_CAPABILITY_UNAVAILABLE=2
uint16 EVENT_CONVERGENCE_CANDIDATE=10
uint16 EVENT_CONVERGENCE_CONFIRMED=11
uint16 EVENT_FILL_CREATED=20
uint16 EVENT_FILL_REJECTED=21
uint16 EVENT_GOAL_REACHED=30
uint16 EVENT_ESCAPE_STARTED=40
uint16 EVENT_ESCAPE_STALLED=41
uint16 EVENT_RECENTER_STARTED=50
uint16 EVENT_RECENTER_COMPLETE=51
uint16 EVENT_TIMEOUT=60
uint16 EVENT_FAILSAFE=70

builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid

uint16 event_type
uint8 state
string state_name
bool state_valid

uint64 fill_id
bool fill_id_valid
int32 reason_code
string detail

string[] value_names
float64[] values
