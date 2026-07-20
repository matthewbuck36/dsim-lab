uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_SIMULATION=1
uint8 SOURCE_PHYSICAL=2

builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid

uint8 source_mode
string source_name
uint32 channel_count

float64[] raw_sensor_value
float64[] filtered_sensor_value
float64[] raw_cost
float64[] source_score
float64[] gaussian_cost
float64[] affine_cost
float64[] augmented_cost

float64 sensor_weight
float64 gaussian_weight
float64 affine_weight

bool raw_sensor_valid
bool filtered_sensor_valid
bool raw_cost_valid
bool source_score_valid
bool gaussian_cost_valid
bool affine_cost_valid
bool augmented_cost_valid
bool weights_valid
