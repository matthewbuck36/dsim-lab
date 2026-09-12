"""Pure, shared identity and source-time contract for opted-in simulation V2."""

import hashlib
import json
import math
import re
from pathlib import Path


ROLLING_MODE = 'rolling_gesc_v2'
STATIONARY_MODE = 'stationary_v1'
TOPIC_KEYS = (
    'raw_cost_topic', 'source_cost_topic', 'augmented_cost_topic',
    'objective_cost_topic', 'provenance_topic', 'pose_topic',
    'encoder_topic', 'timekeeper_topic',
)
SUPPORTED_GEOMETRY = {
    'mount_yaw_rad': 0.0, 'joint_x_m': 0.0, 'joint_y_m': 0.0,
    'radial_offset_m': 0.18,
}
CONFIG_KEYS = set(TOPIC_KEYS) | {
    'schema_version', 'frame_id', 'selected_channel',
    'sensor_geometry_config_sha256', 'sensor_geometry',
}
SCHEMA2_CONFIG_KEYS = CONFIG_KEYS | {'cost_key_basis'}


def canonical_json(value):
    """Produce one portable, non-NaN spelling for an identity payload."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def validate_stream_config(config_json):
    """Reject incomplete/unsupported descriptors; return a detached normalized dict."""
    config = json.loads(config_json) if isinstance(config_json, str) else config_json
    if not isinstance(config, dict):
        raise ValueError('V2 stream descriptor has missing or unknown keys')
    version = config.get('schema_version')
    if type(version) is not int or version not in (1, 2):
        raise ValueError('V2 stream schema_version must be 1 or 2')
    expected_keys = CONFIG_KEYS if version == 1 else SCHEMA2_CONFIG_KEYS
    if set(config) != expected_keys:
        raise ValueError('V2 stream descriptor has missing or unknown keys')
    if version == 2 and config['cost_key_basis'] != 'model_input_time':
        raise ValueError('V2 stream schema 2 requires cost_key_basis=model_input_time')
    if type(config['selected_channel']) is not int or config['selected_channel'] != 0:
        raise ValueError('V2 supports selected_channel 0 only')
    for key in TOPIC_KEYS:
        value = config[key]
        if not isinstance(value, str) or not re.fullmatch(r'/[A-Za-z_][A-Za-z0-9_]*(?:/[A-Za-z_][A-Za-z0-9_]*)*', value):
            raise ValueError(f'{key} must be a fully resolved absolute ROS topic')
    if len({config[key] for key in TOPIC_KEYS}) != len(TOPIC_KEYS):
        raise ValueError('V2 streams must have distinct topic bindings')
    frame = config['frame_id']
    if not isinstance(frame, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:/[A-Za-z_][A-Za-z0-9_]*)*', frame):
        raise ValueError('V2 frame_id must be a nonempty unprefixed frame')
    if not isinstance(config['sensor_geometry_config_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', config['sensor_geometry_config_sha256']):
        raise ValueError('sensor_geometry_config_sha256 must be a lowercase SHA256')
    geometry = config['sensor_geometry']
    if not isinstance(geometry, dict) or set(geometry) != set(SUPPORTED_GEOMETRY):
        raise ValueError('V2 sensor geometry is incomplete')
    for key, expected in SUPPORTED_GEOMETRY.items():
        value = geometry[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or float(value) != expected:
            raise ValueError(f'unsupported V2 sensor geometry: {key}')
    result = dict(config)
    result['sensor_geometry'] = dict(SUPPORTED_GEOMETRY)
    return result


def _valid_ns(value):
    if type(value) is not int or not 0 <= value <= 2_147_483_647_999_999_999:
        raise ValueError('absolute ROS source time is outside valid integer nanoseconds')
    return value


def relative_stamp_ns(origin_ns, relative_sec):
    """Keep legacy joins exact separately; this conversion is for source-time math."""
    _valid_ns(origin_ns)
    if isinstance(relative_sec, bool) or not isinstance(relative_sec, (int, float)) or not math.isfinite(relative_sec):
        raise ValueError('relative source timestamp must be finite')
    scaled = relative_sec * 1_000_000_000
    if not math.isfinite(scaled):
        raise ValueError('relative source timestamp exceeds representable nanoseconds')
    return _valid_ns(origin_ns + round(scaled))


def time_to_ns(stamp):
    """Read a builtin_interfaces Time, validating normalization and range."""
    if type(stamp.sec) is not int or type(stamp.nanosec) is not int or not 0 <= stamp.nanosec < 1_000_000_000:
        raise ValueError('invalid ROS time fields')
    return _valid_ns(stamp.sec * 1_000_000_000 + stamp.nanosec)


def set_time(stamp, value_ns):
    """Populate an existing Time message without importing ROS into this helper."""
    _valid_ns(value_ns)
    stamp.sec, stamp.nanosec = divmod(value_ns, 1_000_000_000)
    return stamp


def stream_contract_id(config_json, origin_ns):
    """Bind the static stream descriptor to its actual first Timekeeper origin."""
    payload = {'config': validate_stream_config(config_json), 'origin_ns': _valid_ns(origin_ns)}
    return hashlib.sha256(canonical_json(payload).encode('utf-8')).hexdigest()


def validate_mode_identity(mode, profile, run_id, config_json, *, simulation=True):
    """Leave legacy optional configuration alone; fail early for incomplete V2."""
    if mode not in (STATIONARY_MODE, ROLLING_MODE):
        raise ValueError('unsupported continuous_search_mode')
    if mode == STATIONARY_MODE:
        return None
    if profile != 'robust_gaussian_v1' or not simulation:
        raise ValueError('rolling_gesc_v2 requires robust_gaussian_v1 simulation')
    if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', run_id):
        raise ValueError('rolling_gesc_v2 requires an explicit valid shared v2_run_id')
    return validate_stream_config(config_json)


def sensor_geometry_descriptor(config_path):
    """Verify the actual selected transform configuration and retain its exact hash."""
    raw = Path(config_path).expanduser().read_bytes()
    config = json.loads(raw)
    if not isinstance(config, dict) or len(config) != 1:
        raise ValueError('V2 requires exactly one configured sensor channel')
    entry = next(iter(config.values()))
    params = entry.get('params', {})
    if entry.get('object_name') != 'Transform_Odom_To_Sensor_Pose':
        raise ValueError('V2 requires the selected odometry-to-sensor transform')
    joint, axis, transform = (params.get(key) for key in ('joint_position', 'rotation_axis', 'sensor_transform'))
    try:
        valid = (joint == [0, 0, .355] and axis == [0, 0, 1]
                 and len(transform) == 4 and all(len(row) == 4 for row in transform)
                 and [row[:3] for row in transform[:3]] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                 and transform[0][3] == .18 and transform[1][3] == 0 and transform[2][3] == .015
                 and transform[3] == [0, 0, 0, 1]
                 and all(math.isfinite(float(value)) for row in transform for value in row)
                 and all(math.isfinite(float(value)) for value in joint))
    except (TypeError, ValueError, IndexError):
        valid = False
    if not valid:
        raise ValueError('V2 selected sensor geometry is unsupported')
    return {'sensor_geometry_config_sha256': hashlib.sha256(raw).hexdigest(),
            'sensor_geometry': dict(SUPPORTED_GEOMETRY)}
