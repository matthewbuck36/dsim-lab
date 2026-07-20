uint8 STATE_UNAVAILABLE=0
uint8 STATE_SEARCH=1
uint8 STATE_VERIFY_EXTREMUM=2
uint8 STATE_DESIGN_OR_MERGE_FILL=3
uint8 STATE_ESCAPE_REPULSE=4
uint8 STATE_ESCAPE_ASSIST=5
uint8 STATE_RECENTER=6
uint8 STATE_GOAL_HOLD=7
uint8 STATE_FAILSAFE=8

builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid

string run_id
bool run_id_valid
string algorithm_profile

uint8 state
string state_name
bool state_valid
uint8 previous_state
string previous_state_name
bool previous_state_valid
string transition_reason
bool transition_reason_valid
float64 state_elapsed_sec
bool state_elapsed_valid

uint32 active_fill_count
bool active_fill_count_valid
uint64 active_escape_fill_id
bool active_escape_fill_id_valid

float64 sensor_weight
float64 gaussian_weight
float64 affine_weight
bool weights_valid

bool failsafe
bool failsafe_valid
