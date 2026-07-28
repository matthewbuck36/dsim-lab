"""Versioned Phase 06 scenario validation and deterministic expansion."""

from copy import deepcopy
import hashlib
import itertools
import json
import math
from pathlib import Path
import re

from ros_esc.scenario_runner import aggregate_field_truth

import yaml


SCHEMA_VERSION = 4
SUPPORTED_SCHEMA_VERSIONS = {1, 2, 3, 4}
PROFILES = {'legacy', 'robust_gaussian_v1'}
STATUSES = {'executable_unverified', 'unsupported'}
FAMILIES = {
    'smoke',
    'two_source',
    'multi_source',
    'boundary',
    'noise_delay',
    'ablation',
    'separation_overlap',
    'close_minimum',
    'starts_saturation',
    'escape',
    'fill_merge',
    'recenter_resume',
}
ACCEPTANCE_FAMILIES = {
    'ordered_two_source',
    'multi_close_overlap',
    'wall_corner',
    'noise_delay',
    'constraint_recovery',
    'lifecycle',
    'obstructing_two_light_collinear',
    'obstructing_two_light_offset',
    'obstructing_three_light_lateral',
    'obstructing_three_light_sequential',
    'obstructing_wall_corner',
    'obstructing_noise_delay',
}
ACCEPTANCE_PARTITIONS = {
    'activation',
    'development',
    'holdout',
    'validation',
    'reproducibility',
}
RESULT_SCOPE_NAMES = {'activation_window', 'full_lifecycle'}
ACTIVATION_SCOPE_PREDICATES = {
    'required_state_sequence',
    'required_state_path',
    'required_events',
    'required_event_sequence',
}
METRIC_APPLICABILITY_KEYS = {
    'escape_attempt',
    'escape_duration',
    'orbit_count',
    'revisit',
    'delay',
    'saturation',
}
EVALUATION_ROLES = {'goal', 'local_minimum', 'obstacle', 'context'}
NOISE_MODELS = {'none', 'uniform', 'gaussian'}
ABLATIONS = {
    'gaussian_fill_enabled',
    'affine_assist_enabled',
    'recenter_enabled',
}
SUCCESS_PREDICATES = {
    'recording_complete',
    'cleanup_complete',
    'controller_goal',
    'ground_truth_goal',
    'expected_terminal_state',
    'required_state_sequence',
    'required_state_path',
    'required_events',
    'required_event_sequence',
    'no_forbidden_states',
    'no_forbidden_events',
    'minimum_saturation_samples',
    'collision_expectation',
    'route_blocker_encountered',
}
LAUNCH_OVERRIDES = {
    'approach_history_window_sec',
    'command_watchdog_rate_hz',
    'convergence_decay_rate',
    'convergence_hold_sec',
    'convergence_min_fill_periods',
    'convergence_threshold',
    'direction_candidate_step_rad',
    'direction_lookahead_m',
    'escape_exit_hold_sec',
    'escape_max_sec',
    'fill_avoidance_margin_m',
    'fill_design_timeout_sec',
    'gaussian_fill_amplitude_depth_scale',
    'gaussian_fill_amplitude_escalation_factor',
    'gaussian_fill_amplitude_max',
    'gaussian_fill_amplitude_min',
    'gaussian_fill_covariance_scale',
    'gaussian_fill_estimation_window_sec',
    'gaussian_fill_exit_sigma',
    'gaussian_fill_low_confidence_threshold',
    'gaussian_fill_maximum_design_escalations',
    'gaussian_fill_maximum_sample_age_sec',
    'gaussian_fill_merge_bandwidth_m',
    'gaussian_fill_merge_radius_scale',
    'gaussian_fill_minimum_basin_depth',
    'gaussian_fill_minimum_merge_probability',
    'gaussian_fill_minimum_valid_samples',
    'gaussian_fill_position_kernel_bandwidth_m',
    'gaussian_fill_sigma_ceiling_m',
    'gaussian_fill_sigma_floor_m',
    'gaussian_fill_support_sigma',
    'gaussian_fill_width_escalation_factor',
    'goal_hold_sec',
    'goal_score_required_rotations',
    'goal_score_rotation_period_sec',
    'goal_score_threshold',
    'minimum_radial_progress_m',
    'recenter_angular_gain',
    'recenter_hold_sec',
    'recenter_linear_gain',
    'recenter_max_angular_velocity_rps',
    'recenter_max_linear_velocity_mps',
    'recenter_max_sec',
    'recenter_rotate_in_place_angle_rad',
    'recenter_tolerance_m',
    'stall_window_sec',
    'startup_timeout_sec',
    'undesired_score_hold_sec',
    'verification_max_sec',
    'wall_margin_m',
}

TOP_LEVEL_KEYS = {
    'schema_version', 'suite_id', 'description', 'mode', 'execution',
    'metadata', 'level_map', 'defaults', 'frozen_profile', 'cases',
}
EXECUTION_KEYS = {
    'max_parallel_runs', 'gazebo_gui', 'runs_root', 'preflight_timeout_sec',
    'run_timeout_sec', 'wall_timeout_sec', 'shutdown_grace_sec',
    'stop_on_run_failure', 'stop_on_cleanup_failure',
}
METADATA_KEYS = {'experiment_version', 'operator_notes'}
DEFAULT_KEYS = {
    'bounds_m', 'room_center_m', 'disturbances', 'validation_world',
    'simulation_contacts_enabled',
}
DISTURBANCE_KEYS = {'sensor_noise', 'sensor_delay_sec', 'pose_delay_sec'}
NOISE_KEYS = {'model', 'bound', 'std_dev'}
CASE_KEYS = {
    'case_id', 'family', 'description', 'status', 'unsupported_reason',
    'profiles', 'seeds', 'starts', 'sources', 'bounds_m', 'room_center_m',
    'disturbances', 'algorithm', 'success',
    'validation_world', 'simulation_contacts_enabled',
    'acceptance_family', 'acceptance_partition', 'repeat_reference',
    'metric_applicability',
}
START_KEYS = {'id', 'x_m', 'y_m', 'yaw_rad'}
SOURCE_KEYS = {
    'id', 'x_m', 'y_m', 'relative_lumen_input', 'levels',
    'evaluation_role',
}
ALGORITHM_KEYS = {'ablations', 'launch_overrides'}
SUCCESS_KEYS = {
    'all_of', 'controller', 'ground_truth', 'minimum_saturation_samples',
    'collision_expected', 'result_scopes',
}
FROZEN_PROFILE_KEYS = {'profile_id', 'launch_overrides', 'sha256'}
CONTROLLER_KEYS = {
    'contract_id', 'expected_verification_outcome',
    'reachability_argument',
    'expected_terminal_state', 'required_state_sequence', 'required_events',
    'forbidden_events', 'required_state_path', 'required_event_sequence',
    'forbidden_states',
}
GROUND_TRUTH_KEYS = {'goal_source_ids', 'final_position_tolerance_m'}
AGGREGATE_GROUND_TRUTH_KEYS = {
    'method',
    'final_position_tolerance_m',
    'wall_margin_m',
    'minimum_source_score',
    'aggregate_field',
}
RESULT_SCOPE_KEYS = {
    'anchor_state', 'boundary_state', 'graceful_stop', 'all_of',
}
REPEAT_REFERENCE_KEYS = {'partition', 'case_key'}
SAFE_ID = re.compile('^[A-Za-z0-9][A-Za-z0-9._-]*$')
VERIFICATION_OUTCOMES = {
    'goal',
    'below_target_extremum',
    'safe_timeout',
}
CONTRACT_TIMING_OVERRIDES = {
    'goal_score_threshold',
    'goal_score_rotation_period_sec',
    'goal_score_required_rotations',
    'goal_hold_sec',
    'undesired_score_hold_sec',
    'verification_max_sec',
}
ALGORITHM_STATES = {
    'SEARCH',
    'VERIFY_EXTREMUM',
    'DESIGN_OR_MERGE_FILL',
    'ESCAPE_REPULSE',
    'ESCAPE_ASSIST',
    'RECENTER',
    'GOAL_HOLD',
    'FAILSAFE',
}
ALGORITHM_EVENTS = {
    'CONFIGURATION',
    'CAPABILITY_UNAVAILABLE',
    'STATE_TRANSITION',
    'CONVERGENCE_CANDIDATE',
    'CONVERGENCE_CONFIRMED',
    'FILL_CREATED',
    'FILL_REJECTED',
    'FILL_MERGED',
    'FILL_SUPERSEDED',
    'FILL_DESIGN_ESCALATED',
    'FILL_DESIGN_FAILED',
    'FILL_LOW_CONFIDENCE',
    'GOAL_REACHED',
    'ESCAPE_STARTED',
    'ESCAPE_STALLED',
    'RECENTER_STARTED',
    'RECENTER_COMPLETE',
    'TIMEOUT',
    'FAILSAFE',
}
ALGORITHM_TRANSITIONS = {
    'SEARCH': {'VERIFY_EXTREMUM', 'FAILSAFE'},
    'VERIFY_EXTREMUM': {
        'DESIGN_OR_MERGE_FILL', 'GOAL_HOLD', 'FAILSAFE',
    },
    'DESIGN_OR_MERGE_FILL': {
        'ESCAPE_REPULSE', 'ESCAPE_ASSIST', 'FAILSAFE',
    },
    'ESCAPE_REPULSE': {
        'DESIGN_OR_MERGE_FILL', 'RECENTER', 'SEARCH', 'FAILSAFE',
    },
    'ESCAPE_ASSIST': {'RECENTER', 'SEARCH', 'FAILSAFE'},
    'RECENTER': {'SEARCH', 'FAILSAFE'},
    'GOAL_HOLD': set(),
    'FAILSAFE': set(),
}

EXECUTION_DEFAULTS = {
    'max_parallel_runs': 1,
    'gazebo_gui': False,
    'runs_root': '~/Experiments/GESC-Gaussian/runs',
    'preflight_timeout_sec': 60.0,
    'run_timeout_sec': 180.0,
    'wall_timeout_sec': 480.0,
    'shutdown_grace_sec': 30.0,
    'stop_on_run_failure': False,
    'stop_on_cleanup_failure': True,
}
DEFAULTS = {
    'bounds_m': [-2.0, 2.0, -2.0, 2.0],
    'room_center_m': [0.0, 0.0],
    'disturbances': {
        'sensor_noise': {'model': 'none', 'bound': 0.0},
        'sensor_delay_sec': 0.0,
        'pose_delay_sec': 0.0,
    },
    'validation_world': False,
    'simulation_contacts_enabled': False,
}


def _unknown(mapping, allowed, location):
    if not isinstance(mapping, dict):
        raise ValueError(f'{location} must be a mapping')
    extra = sorted(set(mapping) - set(allowed))
    if extra:
        raise ValueError(f"{location} has unknown keys: {', '.join(extra)}")


def _identifier(value, location):
    text = str(value) if value is not None else ''
    if not SAFE_ID.fullmatch(text):
        raise ValueError(
            f'{location} must match [A-Za-z0-9][A-Za-z0-9._-]*'
        )
    return text


def _number(value, location, minimum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{location} must be numeric')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f'{location} must be finite')
    if positive and result <= 0.0:
        raise ValueError(f'{location} must be positive')
    if minimum is not None and result < minimum:
        raise ValueError(f'{location} must be at least {minimum}')
    return result


def _boolean(value, location):
    if not isinstance(value, bool):
        raise ValueError(f'{location} must be true or false')
    return value


def _contract_names(value, allowed, prefix, location, unique=True):
    """Normalize one strict schema-v3 state or event name list."""
    if not isinstance(value, list):
        raise ValueError(f'{location} must be a list')
    normalized = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f'{location}[{index}] must be a non-empty string')
        name = item.strip().removeprefix(prefix)
        if name not in allowed:
            raise ValueError(f'{location}[{index}] is unknown: {item}')
        normalized.append(name)
    if unique and len(normalized) != len(set(normalized)):
        raise ValueError(f'{location} must not contain duplicates')
    return normalized


def _validate_state_path(path, location):
    """Require a direct, first-verification-anchorable supervisor path."""
    if 'VERIFY_EXTREMUM' not in path:
        raise ValueError(f'{location} must include VERIFY_EXTREMUM')
    for previous, current in zip(path, path[1:]):
        if current not in ALGORITHM_TRANSITIONS[previous]:
            raise ValueError(
                f'{location} has unreachable transition '
                f'{previous} -> {current}'
            )


def _normalize_metric_applicability(value, location):
    _unknown(value, METRIC_APPLICABILITY_KEYS, location)
    missing = sorted(METRIC_APPLICABILITY_KEYS - set(value))
    if missing:
        raise ValueError(
            f'{location} is missing: ' + ', '.join(missing)
        )
    return {
        name: _boolean(value[name], f'{location}.{name}')
        for name in sorted(METRIC_APPLICABILITY_KEYS)
    }


def _normalize_repeat_reference(value, partition, location):
    if partition != 'reproducibility':
        if value is not None:
            raise ValueError(
                f'{location} is only valid for reproducibility cases'
            )
        return None
    _unknown(value, REPEAT_REFERENCE_KEYS, location)
    reference_partition = str(value.get('partition', ''))
    if reference_partition not in {'holdout', 'validation'}:
        raise ValueError(
            f'{location}.partition must be holdout or validation'
        )
    case_key = str(value.get('case_key', ''))
    if not re.fullmatch('[0-9a-f]{64}', case_key):
        raise ValueError(
            f'{location}.case_key must be lowercase SHA-256'
        )
    return {
        'partition': reference_partition,
        'case_key': case_key,
    }


def _normalize_result_scopes(value, all_of, partition, location):
    _unknown(value, RESULT_SCOPE_NAMES, location)
    if 'full_lifecycle' not in value:
        raise ValueError(f'{location}.full_lifecycle is required')
    normalized = {}
    assigned_predicates = []
    for name in ('activation_window', 'full_lifecycle'):
        if name not in value:
            continue
        scope = value[name]
        scope_location = f'{location}.{name}'
        _unknown(scope, RESULT_SCOPE_KEYS, scope_location)
        expected_anchor = (
            'VERIFY_EXTREMUM'
            if name == 'activation_window'
            else 'SEARCH'
        )
        anchor = _contract_names(
            [scope.get('anchor_state')],
            ALGORITHM_STATES,
            'STATE_',
            f'{scope_location}.anchor_state',
        )[0]
        if anchor != expected_anchor:
            raise ValueError(
                f'{scope_location}.anchor_state must equal {expected_anchor}'
            )
        boundary_value = scope.get('boundary_state')
        boundary = None
        if boundary_value is not None:
            boundary = _contract_names(
                [boundary_value],
                ALGORITHM_STATES,
                'STATE_',
                f'{scope_location}.boundary_state',
            )[0]
        graceful_stop = _boolean(
            scope.get('graceful_stop', False),
            f'{scope_location}.graceful_stop',
        )
        predicates = scope.get('all_of')
        if not isinstance(predicates, list) or not predicates:
            raise ValueError(f'{scope_location}.all_of must be non-empty')
        if (
            len(predicates) != len(set(predicates))
            or not set(predicates) <= SUCCESS_PREDICATES
        ):
            raise ValueError(
                f'{scope_location}.all_of has duplicates or unknown '
                'predicates'
            )
        if name == 'activation_window':
            if boundary is None:
                raise ValueError(
                    f'{scope_location}.boundary_state is required'
                )
            if graceful_stop and partition not in {
                'activation', 'development',
            }:
                raise ValueError(
                    f'{scope_location}.graceful_stop is development-only'
                )
            if not set(predicates) <= ACTIVATION_SCOPE_PREDICATES:
                raise ValueError(
                    f'{scope_location} may contain only branch-local '
                    'state and event predicates'
                )
        elif boundary is not None or graceful_stop:
            raise ValueError(
                f'{scope_location} must run through orderly shutdown'
            )
        normalized[name] = {
            'anchor_state': anchor,
            'boundary_state': boundary,
            'graceful_stop': graceful_stop,
            'all_of': list(predicates),
        }
        assigned_predicates.extend(predicates)
    if len(assigned_predicates) != len(set(assigned_predicates)):
        raise ValueError(
            f'{location} must assign each predicate to exactly one scope'
        )
    if set(assigned_predicates) != set(all_of):
        raise ValueError(
            f'{location} predicate union must equal success.all_of'
        )
    if partition in {'holdout', 'validation', 'reproducibility'} and (
        set(normalized) != {'full_lifecycle'}
    ):
        raise ValueError(
            f'{location} acceptance cases must use full_lifecycle only'
        )
    return normalized


def _verification_timing(overrides, outcome, location):
    """Validate and expose the timing budget for a schema-v3 contract."""
    missing = sorted(CONTRACT_TIMING_OVERRIDES - set(overrides))
    if missing:
        raise ValueError(
            f'{location} requires explicit launch overrides: '
            + ', '.join(missing)
        )
    threshold = _number(
        overrides['goal_score_threshold'],
        f'{location}.goal_score_threshold',
        minimum=0.0,
    )
    if threshold > 1.0:
        raise ValueError(f'{location}.goal_score_threshold must not exceed 1')
    period = _number(
        overrides['goal_score_rotation_period_sec'],
        f'{location}.goal_score_rotation_period_sec',
        positive=True,
    )
    rotations = overrides['goal_score_required_rotations']
    if (
        isinstance(rotations, bool)
        or not isinstance(rotations, int)
        or rotations <= 0
    ):
        raise ValueError(
            f'{location}.goal_score_required_rotations '
            'must be a positive integer'
        )
    goal_dwell = _number(
        overrides['goal_hold_sec'],
        f'{location}.goal_hold_sec',
        positive=True,
    )
    below_target_dwell = _number(
        overrides['undesired_score_hold_sec'],
        f'{location}.undesired_score_hold_sec',
        positive=True,
    )
    timeout = _number(
        overrides['verification_max_sec'],
        f'{location}.verification_max_sec',
        positive=True,
    )
    rotation_duration = period * rotations
    goal_required = rotation_duration + goal_dwell
    below_target_required = rotation_duration + below_target_dwell
    goal_margin = timeout - goal_required
    below_target_margin = timeout - below_target_required
    selected_margin = {
        'goal': goal_margin,
        'below_target_extremum': below_target_margin,
        'safe_timeout': max(goal_margin, below_target_margin),
    }[outcome]
    if outcome != 'safe_timeout' and selected_margin <= 0.0:
        raise ValueError(
            f'{location} has no positive verification timing margin '
            f'for {outcome}'
        )
    if (
        outcome == 'safe_timeout'
        and selected_margin >= 0.0
    ):
        raise ValueError(
            f'{location} safe_timeout must intentionally use an '
            'insufficient timing budget for both classification branches'
        )
    return {
        'goal_score_threshold': threshold,
        'rotation_period_sec': period,
        'required_rotations': rotations,
        'rotation_duration_sec': rotation_duration,
        'goal_dwell_sec': goal_dwell,
        'below_target_dwell_sec': below_target_dwell,
        'verification_timeout_sec': timeout,
        'goal_required_sec': goal_required,
        'below_target_required_sec': below_target_required,
        'goal_margin_sec': goal_margin,
        'below_target_margin_sec': below_target_margin,
        'selected_margin_sec': selected_margin,
        'timing_sufficient': selected_margin > 0.0,
    }


def _merge_disturbances(defaults, override, location):
    result = deepcopy(defaults)
    if override is None:
        return result
    _unknown(override, DISTURBANCE_KEYS, location)
    if 'sensor_noise' in override:
        _unknown(
            override['sensor_noise'], NOISE_KEYS, f'{location}.sensor_noise'
        )
        result['sensor_noise'].update(override['sensor_noise'])
    for name in ('sensor_delay_sec', 'pose_delay_sec'):
        if name in override:
            result[name] = override[name]
    noise = result['sensor_noise']
    model = str(noise.get('model', 'none'))
    if model not in NOISE_MODELS:
        raise ValueError(f'{location}.sensor_noise.model is unsupported')
    noise['model'] = model
    noise['bound'] = _number(
        noise.get('bound', 0.0), f'{location}.sensor_noise.bound', minimum=0.0
    )
    if 'std_dev' in noise:
        noise['std_dev'] = _number(
            noise['std_dev'], f'{location}.sensor_noise.std_dev', minimum=0.0
        )
    for name in ('sensor_delay_sec', 'pose_delay_sec'):
        result[name] = _number(
            result.get(name, 0.0), f'{location}.{name}', minimum=0.0
        )
    return result


def _validate_bounds(value, location):
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError(f'{location} must be [x_min, x_max, y_min, y_max]')
    values = [
        _number(item, f'{location}[{index}]')
        for index, item in enumerate(value)
    ]
    if not values[0] < values[1] or not values[2] < values[3]:
        raise ValueError(f'{location} minima must be less than maxima')
    return values


def _validate_center(value, bounds, location):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f'{location} must be [x, y]')
    center = [
        _number(item, f'{location}[{index}]')
        for index, item in enumerate(value)
    ]
    if not (bounds[0] <= center[0] <= bounds[1]):
        raise ValueError(f'{location} x is outside bounds')
    if not (bounds[2] <= center[1] <= bounds[3]):
        raise ValueError(f'{location} y is outside bounds')
    return center


def _disturbance_support(disturbances, schema_version):
    """Return an unsupported reason for a known unavailable disturbance."""
    if schema_version >= 2:
        return None
    noise = disturbances['sensor_noise']
    if disturbances['sensor_delay_sec'] > 0.0:
        return 'sensor delay injection is not implemented'
    if disturbances['pose_delay_sec'] > 0.0:
        return 'pose delay injection is not implemented'
    if noise['model'] == 'gaussian' and noise.get('std_dev', 0.0) > 0.0:
        return 'Gaussian noise does not use its configured deterministic seed'
    return None


def load_suite(path):
    """Load, strictly validate, and normalize one scenario suite."""
    source_path = Path(path).expanduser().resolve()
    document = yaml.safe_load(source_path.read_text(encoding='utf-8'))
    _unknown(document, TOP_LEVEL_KEYS, 'suite')
    schema_version = document.get('schema_version')
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            'schema_version must equal one of '
            + ', '.join(
                str(item) for item in sorted(SUPPORTED_SCHEMA_VERSIONS)
            )
        )
    if schema_version == 1 and (
        'frozen_profile' in document
        or any(
            name in document.get('defaults', {})
            for name in (
                'validation_world', 'simulation_contacts_enabled'
            )
        )
        or any(
            name in case
            for case in document.get('cases', [])
            for name in (
                'validation_world', 'simulation_contacts_enabled'
            )
        )
    ):
        raise ValueError('schema version 2 is required for validation fields')
    schema_v3_controller_keys = {
        'contract_id',
        'expected_verification_outcome',
        'reachability_argument',
        'required_state_path',
        'required_event_sequence',
        'forbidden_states',
    }
    schema_v3_predicates = {
        'expected_terminal_state',
        'required_state_path',
        'required_event_sequence',
        'no_forbidden_states',
    }
    uses_schema_v3_fields = False
    raw_cases = document.get('cases', [])
    if isinstance(raw_cases, list):
        for case in raw_cases:
            if not isinstance(case, dict):
                continue
            raw_success = case.get('success', {})
            if not isinstance(raw_success, dict):
                continue
            raw_controller = raw_success.get('controller', {})
            raw_all_of = raw_success.get('all_of', [])
            uses_schema_v3_fields = (
                isinstance(raw_controller, dict)
                and bool(schema_v3_controller_keys & set(raw_controller))
            ) or (
                isinstance(raw_all_of, list)
                and bool(schema_v3_predicates & set(raw_all_of))
            )
            if uses_schema_v3_fields:
                break
    if schema_version < 3 and uses_schema_v3_fields:
        raise ValueError(
            'schema version 3 is required for activation-contract fields'
        )
    schema_v4_case_keys = {
        'acceptance_family',
        'acceptance_partition',
        'repeat_reference',
        'metric_applicability',
    }
    uses_schema_v4_fields = False
    if isinstance(raw_cases, list):
        for case in raw_cases:
            if not isinstance(case, dict):
                continue
            raw_success = case.get('success', {})
            raw_ground_truth = (
                raw_success.get('ground_truth', {})
                if isinstance(raw_success, dict)
                else {}
            )
            uses_schema_v4_fields = bool(
                schema_v4_case_keys & set(case)
            ) or (
                isinstance(raw_success, dict)
                and 'result_scopes' in raw_success
            ) or (
                isinstance(raw_ground_truth, dict)
                and bool(
                    set(raw_ground_truth)
                    & (AGGREGATE_GROUND_TRUTH_KEYS - GROUND_TRUTH_KEYS)
                )
            )
            if uses_schema_v4_fields:
                break
    if schema_version < 4 and uses_schema_v4_fields:
        raise ValueError(
            'schema version 4 is required for v3 acceptance fields'
        )
    suite_id = _identifier(document.get('suite_id'), 'suite_id')
    if document.get('mode') != 'simulation':
        raise ValueError('mode must be simulation')

    execution = deepcopy(EXECUTION_DEFAULTS)
    supplied_execution = document.get('execution', {})
    _unknown(supplied_execution, EXECUTION_KEYS, 'execution')
    execution.update(supplied_execution)
    if execution['max_parallel_runs'] != 1:
        raise ValueError('execution.max_parallel_runs must equal 1')
    for name in (
        'gazebo_gui', 'stop_on_run_failure', 'stop_on_cleanup_failure'
    ):
        execution[name] = _boolean(execution[name], f'execution.{name}')
    for name in (
        'preflight_timeout_sec', 'run_timeout_sec', 'wall_timeout_sec',
        'shutdown_grace_sec',
    ):
        execution[name] = _number(
            execution[name], f'execution.{name}', positive=True
        )
    if execution['wall_timeout_sec'] <= execution['run_timeout_sec']:
        raise ValueError(
            'execution.wall_timeout_sec must exceed run_timeout_sec'
        )
    execution['runs_root'] = str(execution['runs_root'])

    metadata = document.get('metadata', {})
    _unknown(metadata, METADATA_KEYS, 'metadata')
    if not str(metadata.get('experiment_version', '')).strip():
        raise ValueError('metadata.experiment_version must not be empty')

    level_map = document.get('level_map', {})
    if not isinstance(level_map, dict):
        raise ValueError('level_map must be a mapping')
    normalized_levels = {}
    for label, intensity in level_map.items():
        normalized_levels[str(label)] = _number(
            intensity, f'level_map.{label}', minimum=0.0
        )

    frozen_profile = document.get('frozen_profile')
    if frozen_profile is not None:
        _unknown(frozen_profile, FROZEN_PROFILE_KEYS, 'frozen_profile')
        profile_id = _identifier(
            frozen_profile.get('profile_id'), 'frozen_profile.profile_id'
        )
        frozen_overrides = frozen_profile.get('launch_overrides', {})
        _unknown(
            frozen_overrides, LAUNCH_OVERRIDES,
            'frozen_profile.launch_overrides',
        )
        for name, value in frozen_overrides.items():
            if isinstance(value, (dict, list)) or value is None:
                raise ValueError(
                    f'frozen_profile.launch_overrides.{name} must be scalar'
                )
        frozen_sha = str(frozen_profile.get('sha256', '')).strip()
        if frozen_sha and not re.fullmatch('[0-9a-f]{64}', frozen_sha):
            raise ValueError('frozen_profile.sha256 must be lowercase SHA-256')
        frozen_profile = {
            'profile_id': profile_id,
            'launch_overrides': dict(frozen_overrides),
            'sha256': frozen_sha or None,
        }

    defaults = deepcopy(DEFAULTS)
    supplied_defaults = document.get('defaults', {})
    _unknown(supplied_defaults, DEFAULT_KEYS, 'defaults')
    defaults.update({
        name: supplied_defaults[name]
        for name in ('bounds_m', 'room_center_m')
        if name in supplied_defaults
    })
    defaults['bounds_m'] = _validate_bounds(
        defaults['bounds_m'], 'defaults.bounds_m'
    )
    defaults['room_center_m'] = _validate_center(
        defaults['room_center_m'], defaults['bounds_m'],
        'defaults.room_center_m',
    )
    defaults['disturbances'] = _merge_disturbances(
        DEFAULTS['disturbances'], supplied_defaults.get('disturbances'),
        'defaults.disturbances',
    )
    for name in ('validation_world', 'simulation_contacts_enabled'):
        defaults[name] = _boolean(
            supplied_defaults.get(name, DEFAULTS[name]),
            f'defaults.{name}',
        )

    cases = document.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('cases must be a non-empty list')
    normalized_cases = []
    case_ids = set()
    for index, case in enumerate(cases):
        location = f'cases[{index}]'
        _unknown(case, CASE_KEYS, location)
        case_id = _identifier(case.get('case_id'), f'{location}.case_id')
        if case_id in case_ids:
            raise ValueError(f'duplicate case_id: {case_id}')
        case_ids.add(case_id)
        family = str(case.get('family', ''))
        if family not in FAMILIES:
            raise ValueError(f'{location}.family is unsupported')
        status = str(case.get('status', ''))
        if status not in STATUSES:
            raise ValueError(f'{location}.status is unsupported')
        unsupported_reason = str(case.get('unsupported_reason', '')).strip()
        if status == 'unsupported' and not unsupported_reason:
            raise ValueError(
                f'{location}.unsupported_reason is required for '
                'unsupported cases'
            )
        acceptance_family = None
        acceptance_partition = None
        repeat_reference = None
        metric_applicability = None
        if schema_version >= 4:
            acceptance_family = str(case.get('acceptance_family', ''))
            if acceptance_family not in ACCEPTANCE_FAMILIES:
                raise ValueError(
                    f'{location}.acceptance_family is unsupported'
                )
            acceptance_partition = str(
                case.get('acceptance_partition', '')
            )
            if acceptance_partition not in ACCEPTANCE_PARTITIONS:
                raise ValueError(
                    f'{location}.acceptance_partition is unsupported'
                )
            repeat_reference = _normalize_repeat_reference(
                case.get('repeat_reference'),
                acceptance_partition,
                f'{location}.repeat_reference',
            )
            metric_applicability = _normalize_metric_applicability(
                case.get('metric_applicability'),
                f'{location}.metric_applicability',
            )

        profiles = case.get('profiles')
        if not isinstance(profiles, list) or not profiles:
            raise ValueError(f'{location}.profiles must be non-empty')
        if (
            len(set(profiles)) != len(profiles)
            or not set(profiles) <= PROFILES
        ):
            raise ValueError(
                f'{location}.profiles has duplicates or unknown values'
            )
        if (
            schema_version >= 3
            and status == 'executable_unverified'
            and profiles != ['robust_gaussian_v1']
        ):
            raise ValueError(
                f'{location}.profiles for an executable schema-v3 '
                'activation contract must equal [robust_gaussian_v1]'
            )

        seeds = case.get('seeds')
        if not isinstance(seeds, list) or not seeds:
            raise ValueError(
                f'{location}.seeds must contain explicit integers'
            )
        if any(
            isinstance(seed, bool) or not isinstance(seed, int)
            for seed in seeds
        ):
            raise ValueError(f'{location}.seeds must contain integers')

        bounds = _validate_bounds(
            case.get('bounds_m', defaults['bounds_m']),
            f'{location}.bounds_m',
        )
        center = _validate_center(
            case.get('room_center_m', defaults['room_center_m']),
            bounds, f'{location}.room_center_m',
        )
        disturbances = _merge_disturbances(
            defaults['disturbances'], case.get('disturbances'),
            f'{location}.disturbances',
        )
        validation_world = _boolean(
            case.get('validation_world', defaults['validation_world']),
            f'{location}.validation_world',
        )
        contacts_enabled = _boolean(
            case.get(
                'simulation_contacts_enabled',
                defaults['simulation_contacts_enabled'],
            ),
            f'{location}.simulation_contacts_enabled',
        )
        if contacts_enabled and not validation_world:
            raise ValueError(
                f'{location}.simulation_contacts_enabled requires '
                'validation_world'
            )

        starts = case.get('starts')
        if not isinstance(starts, list) or not starts:
            raise ValueError(f'{location}.starts must be non-empty')
        normalized_starts = []
        start_ids = set()
        for start_index, start in enumerate(starts):
            start_location = f'{location}.starts[{start_index}]'
            _unknown(start, START_KEYS, start_location)
            start_id = _identifier(start.get('id'), f'{start_location}.id')
            if start_id in start_ids:
                raise ValueError(
                    f'duplicate start id in {case_id}: {start_id}'
                )
            start_ids.add(start_id)
            x_value = _number(start.get('x_m'), f'{start_location}.x_m')
            y_value = _number(start.get('y_m'), f'{start_location}.y_m')
            yaw_value = _number(
                start.get('yaw_rad'), f'{start_location}.yaw_rad'
            )
            if not bounds[0] <= x_value <= bounds[1]:
                raise ValueError(f'{start_location}.x_m is outside bounds')
            if not bounds[2] <= y_value <= bounds[3]:
                raise ValueError(f'{start_location}.y_m is outside bounds')
            normalized_starts.append({
                'id': start_id, 'x_m': x_value, 'y_m': y_value,
                'yaw_rad': yaw_value,
            })

        sources = case.get('sources')
        if not isinstance(sources, list):
            raise ValueError(f'{location}.sources must be a list')
        if status == 'executable_unverified' and not 1 <= len(sources) <= 5:
            raise ValueError(
                f'{location}.sources must contain 1 to 5 executable sources'
            )
        normalized_sources = []
        source_ids = set()
        for source_index, source in enumerate(sources):
            source_location = f'{location}.sources[{source_index}]'
            _unknown(source, SOURCE_KEYS, source_location)
            source_id = _identifier(source.get('id'), f'{source_location}.id')
            if source_id in source_ids:
                raise ValueError(
                    f'duplicate source id in {case_id}: {source_id}'
                )
            source_ids.add(source_id)
            has_intensity = 'relative_lumen_input' in source
            has_levels = 'levels' in source
            if has_intensity == has_levels:
                raise ValueError(
                    f'{source_location} requires exactly one of '
                    'relative_lumen_input or levels'
                )
            role = str(source.get('evaluation_role', ''))
            if role not in EVALUATION_ROLES:
                raise ValueError(
                    f'{source_location}.evaluation_role is unknown'
                )
            normalized = {
                'id': source_id,
                'x_m': _number(source.get('x_m'), f'{source_location}.x_m'),
                'y_m': _number(source.get('y_m'), f'{source_location}.y_m'),
                'evaluation_role': role,
            }
            if has_intensity:
                normalized['relative_lumen_input'] = _number(
                    source['relative_lumen_input'],
                    f'{source_location}.relative_lumen_input', minimum=0.0,
                )
            else:
                levels = source['levels']
                if not isinstance(levels, list) or not levels:
                    raise ValueError(
                        f'{source_location}.levels must be non-empty'
                    )
                labels = [str(label) for label in levels]
                missing = [
                    label for label in labels
                    if label not in normalized_levels
                ]
                if missing and status == 'executable_unverified':
                    raise ValueError(
                        f'{source_location}.levels missing from level_map: '
                        + ', '.join(missing)
                    )
                normalized['levels'] = labels
            normalized_sources.append(normalized)

        algorithm = case.get('algorithm', {})
        _unknown(algorithm, ALGORITHM_KEYS, f'{location}.algorithm')
        ablations = {
            'gaussian_fill_enabled': True,
            'affine_assist_enabled': True,
            'recenter_enabled': True,
        }
        supplied_ablations = algorithm.get('ablations', {})
        _unknown(
            supplied_ablations, ABLATIONS, f'{location}.algorithm.ablations'
        )
        ablations.update(supplied_ablations)
        for name, value in ablations.items():
            ablations[name] = _boolean(
                value, f'{location}.algorithm.ablations.{name}'
            )
        overrides = algorithm.get('launch_overrides', {})
        _unknown(
            overrides, LAUNCH_OVERRIDES,
            f'{location}.algorithm.launch_overrides',
        )
        for name, value in overrides.items():
            if isinstance(value, (dict, list)) or value is None:
                raise ValueError(
                    f'{location}.algorithm.launch_overrides.{name} '
                    'must be scalar'
                )
        if frozen_profile is not None:
            overlap = sorted(
                set(overrides) & set(frozen_profile['launch_overrides'])
            )
            if overlap:
                raise ValueError(
                    f'{location}.algorithm.launch_overrides conflicts with '
                    'frozen_profile: ' + ', '.join(overlap)
                )
            overrides = {
                **frozen_profile['launch_overrides'],
                **overrides,
            }

        success = case.get('success', {})
        _unknown(success, SUCCESS_KEYS, f'{location}.success')
        all_of = success.get(
            'all_of', ['recording_complete', 'cleanup_complete']
        )
        if not isinstance(all_of, list) or not all_of:
            raise ValueError(f'{location}.success.all_of must be non-empty')
        if not set(all_of) <= SUCCESS_PREDICATES:
            raise ValueError(
                f'{location}.success.all_of has unknown predicates'
            )
        if schema_version >= 3 and len(all_of) != len(set(all_of)):
            raise ValueError(
                f'{location}.success.all_of must not contain duplicates'
            )
        result_scopes = None
        if schema_version >= 4:
            result_scopes = _normalize_result_scopes(
                success.get('result_scopes'),
                all_of,
                acceptance_partition,
                f'{location}.success.result_scopes',
            )
        controller = success.get('controller', {})
        _unknown(controller, CONTROLLER_KEYS, f'{location}.success.controller')
        normalized_controller = {
            'expected_terminal_state': controller.get(
                'expected_terminal_state'
            ),
            'required_state_sequence': list(
                controller.get('required_state_sequence', [])
            ),
            'required_events': list(
                controller.get('required_events', [])
            ),
            'forbidden_events': list(
                controller.get('forbidden_events', [])
            ),
        }
        if schema_version >= 3:
            controller_location = f'{location}.success.controller'
            contract_id = _identifier(
                controller.get('contract_id'),
                f'{controller_location}.contract_id',
            )
            if contract_id != case_id:
                raise ValueError(
                    f'{controller_location}.contract_id must equal case_id'
                )
            outcome = str(
                controller.get('expected_verification_outcome', '')
            )
            if outcome not in VERIFICATION_OUTCOMES:
                raise ValueError(
                    f'{controller_location}.expected_verification_outcome '
                    'is unsupported'
                )
            reachability_argument = controller.get('reachability_argument')
            if (
                not isinstance(reachability_argument, str)
                or not reachability_argument.strip()
            ):
                raise ValueError(
                    f'{controller_location}.reachability_argument '
                    'must be non-empty'
                )
            expected_terminal = controller.get('expected_terminal_state')
            if expected_terminal is not None:
                expected_terminal = _contract_names(
                    [expected_terminal],
                    ALGORITHM_STATES,
                    'STATE_',
                    f'{controller_location}.expected_terminal_state',
                )[0]
            required_states = _contract_names(
                controller.get('required_state_sequence', []),
                ALGORITHM_STATES,
                'STATE_',
                f'{controller_location}.required_state_sequence',
                unique=False,
            )
            required_path = _contract_names(
                controller.get('required_state_path', []),
                ALGORITHM_STATES,
                'STATE_',
                f'{controller_location}.required_state_path',
                unique=False,
            )
            if not required_path:
                raise ValueError(
                    f'{controller_location}.required_state_path '
                    'must be non-empty'
                )
            _validate_state_path(
                required_path,
                f'{controller_location}.required_state_path',
            )
            forbidden_states = _contract_names(
                controller.get('forbidden_states', []),
                ALGORITHM_STATES,
                'STATE_',
                f'{controller_location}.forbidden_states',
            )
            required_events = _contract_names(
                controller.get('required_events', []),
                ALGORITHM_EVENTS,
                'EVENT_',
                f'{controller_location}.required_events',
            )
            required_event_sequence = _contract_names(
                controller.get('required_event_sequence', []),
                ALGORITHM_EVENTS,
                'EVENT_',
                f'{controller_location}.required_event_sequence',
                unique=False,
            )
            if not required_events and not required_event_sequence:
                raise ValueError(
                    f'{controller_location} must require events by '
                    'membership or same-producer sequence'
                )
            forbidden_events = _contract_names(
                controller.get('forbidden_events', []),
                ALGORITHM_EVENTS,
                'EVENT_',
                f'{controller_location}.forbidden_events',
            )
            required_state_set = set(required_states) | set(required_path)
            state_overlap = sorted(
                required_state_set & set(forbidden_states)
            )
            if state_overlap:
                raise ValueError(
                    f'{controller_location} requires and forbids states: '
                    + ', '.join(state_overlap)
                )
            required_event_set = (
                set(required_events) | set(required_event_sequence)
            )
            event_overlap = sorted(
                required_event_set & set(forbidden_events)
            )
            if event_overlap:
                raise ValueError(
                    f'{controller_location} requires and forbids events: '
                    + ', '.join(event_overlap)
                )
            if expected_terminal in forbidden_states:
                raise ValueError(
                    f'{controller_location}.expected_terminal_state '
                    'is forbidden'
                )
            verify_index = required_path.index('VERIFY_EXTREMUM')
            next_state = (
                required_path[verify_index + 1]
                if verify_index + 1 < len(required_path)
                else None
            )
            required_next = {
                'goal': 'GOAL_HOLD',
                'below_target_extremum': 'DESIGN_OR_MERGE_FILL',
                'safe_timeout': 'FAILSAFE',
            }[outcome]
            if next_state != required_next:
                raise ValueError(
                    f'{controller_location}.required_state_path must '
                    f'classify first verification as {required_next}'
                )
            if outcome == 'goal':
                if expected_terminal != 'GOAL_HOLD':
                    raise ValueError(
                        f'{controller_location} goal contract must expect '
                        'terminal GOAL_HOLD'
                    )
                if 'GOAL_REACHED' not in required_event_set:
                    raise ValueError(
                        f'{controller_location} goal contract must require '
                        'GOAL_REACHED'
                    )
                if 'controller_goal' not in all_of:
                    raise ValueError(
                        f'{location}.success.all_of must bind controller_goal'
                    )
            if outcome == 'safe_timeout':
                if expected_terminal != 'FAILSAFE':
                    raise ValueError(
                        f'{controller_location} safe_timeout must expect '
                        'terminal FAILSAFE'
                    )
                if (
                    'TIMEOUT' not in required_event_sequence
                    or 'FAILSAFE' not in required_event_sequence
                    or required_event_sequence.index('TIMEOUT')
                    >= required_event_sequence.index('FAILSAFE')
                ):
                    raise ValueError(
                        f'{controller_location} safe_timeout must require '
                        'ordered TIMEOUT then FAILSAFE events'
                    )
            timing = _verification_timing(
                overrides,
                outcome,
                f'{location}.algorithm.launch_overrides',
            )
            declared_predicates = {'required_state_path'}
            if required_states:
                declared_predicates.add('required_state_sequence')
            if required_events:
                declared_predicates.add('required_events')
            if required_event_sequence:
                declared_predicates.add('required_event_sequence')
            if forbidden_states:
                declared_predicates.add('no_forbidden_states')
            if forbidden_events:
                declared_predicates.add('no_forbidden_events')
            if expected_terminal is not None:
                declared_predicates.add('expected_terminal_state')
            missing_predicates = sorted(declared_predicates - set(all_of))
            if missing_predicates:
                raise ValueError(
                    f'{location}.success.all_of does not bind declared '
                    'controller evidence: ' + ', '.join(missing_predicates)
                )
            normalized_controller = {
                'contract_id': contract_id,
                'expected_verification_outcome': outcome,
                'reachability_argument': reachability_argument.strip(),
                'verification_timing': timing,
                'expected_terminal_state': expected_terminal,
                'required_state_sequence': required_states,
                'required_state_path': required_path,
                'required_events': required_events,
                'required_event_sequence': required_event_sequence,
                'forbidden_states': forbidden_states,
                'forbidden_events': forbidden_events,
            }
            if (
                schema_version >= 4
                and acceptance_partition in {
                    'holdout', 'validation', 'reproducibility',
                }
            ):
                if (
                    expected_terminal != 'GOAL_HOLD'
                    or not required_path
                    or required_path[0] != 'SEARCH'
                    or required_path[-1] != 'GOAL_HOLD'
                    or 'GOAL_REACHED' not in required_event_set
                    or 'controller_goal' not in all_of
                ):
                    raise ValueError(
                        f'{controller_location} formal acceptance must '
                        'bind full-lifecycle GOAL_HOLD success'
                    )
                if not validation_world or not contacts_enabled:
                    raise ValueError(
                        f'{location} formal acceptance requires the '
                        'validation world and contacts'
                    )
        ground_truth = success.get('ground_truth', {})
        ground_truth_location = f'{location}.success.ground_truth'
        goal_ids = []
        if schema_version >= 4:
            _unknown(
                ground_truth,
                AGGREGATE_GROUND_TRUTH_KEYS,
                ground_truth_location,
            )
            if ground_truth.get('method') != 'aggregate_field':
                raise ValueError(
                    f'{ground_truth_location}.method must equal '
                    'aggregate_field'
                )
            tolerance = _number(
                ground_truth.get('final_position_tolerance_m'),
                f'{ground_truth_location}.final_position_tolerance_m',
                positive=True,
            )
            wall_margin = _number(
                ground_truth.get('wall_margin_m'),
                f'{ground_truth_location}.wall_margin_m',
                positive=True,
            )
            minimum_source_score = _number(
                ground_truth.get('minimum_source_score'),
                f'{ground_truth_location}.minimum_source_score',
                minimum=0.0,
            )
            if minimum_source_score > 1.0:
                raise ValueError(
                    f'{ground_truth_location}.minimum_source_score '
                    'must not exceed 1'
                )
            if (
                tolerance != 0.35
                or wall_margin != 0.35
                or minimum_source_score != 0.95
            ):
                raise ValueError(
                    f'{ground_truth_location} must retain tolerances '
                    '0.35 m, 0.35 m, and 0.95'
                )
            aggregate_field = ground_truth.get('aggregate_field')
            if (
                aggregate_field is not None
                and not isinstance(aggregate_field, dict)
            ):
                raise ValueError(
                    f'{ground_truth_location}.aggregate_field must be '
                    'a mapping or null'
                )
            normalized_ground_truth = {
                'method': 'aggregate_field',
                'final_position_tolerance_m': tolerance,
                'wall_margin_m': wall_margin,
                'minimum_source_score': minimum_source_score,
                'aggregate_field': deepcopy(aggregate_field),
            }
            has_ground_truth = True
        else:
            _unknown(
                ground_truth,
                GROUND_TRUTH_KEYS,
                ground_truth_location,
            )
            goal_ids = ground_truth.get('goal_source_ids', [])
            if (
                not isinstance(goal_ids, list)
                or not set(goal_ids) <= source_ids
            ):
                raise ValueError(
                    f'{ground_truth_location}.goal_source_ids are invalid'
                )
            tolerance = _number(
                ground_truth.get('final_position_tolerance_m', 0.35),
                f'{ground_truth_location}.final_position_tolerance_m',
                positive=True,
            )
            normalized_ground_truth = {
                'goal_source_ids': list(goal_ids),
                'final_position_tolerance_m': tolerance,
            }
            has_ground_truth = bool(goal_ids)
        minimum_saturation = success.get('minimum_saturation_samples', 0)
        if (
            isinstance(minimum_saturation, bool)
            or not isinstance(minimum_saturation, int)
            or minimum_saturation < 0
        ):
            raise ValueError(
                f'{location}.success.minimum_saturation_samples '
                'must be a nonnegative integer'
            )
        if schema_version >= 4:
            if (
                metric_applicability['escape_duration']
                or metric_applicability['orbit_count']
                or metric_applicability['revisit']
            ) and not metric_applicability['escape_attempt']:
                raise ValueError(
                    f'{location}.metric_applicability attempt-derived '
                    'metrics require escape_attempt'
                )
            has_delay = (
                disturbances['sensor_delay_sec'] > 0.0
                or disturbances['pose_delay_sec'] > 0.0
            )
            if metric_applicability['delay'] != has_delay:
                raise ValueError(
                    f'{location}.metric_applicability.delay must match '
                    'the declared sensor or pose delay'
                )
            if (
                metric_applicability['saturation']
                != (minimum_saturation > 0)
            ):
                raise ValueError(
                    f'{location}.metric_applicability.saturation must '
                    'match minimum_saturation_samples'
                )
        collision_expected = success.get('collision_expected')
        if collision_expected is not None:
            collision_expected = _boolean(
                collision_expected,
                f'{location}.success.collision_expected',
            )
            if not contacts_enabled:
                raise ValueError(
                    f'{location}.success.collision_expected requires '
                    'simulation contacts'
                )
        formal_acceptance = (
            schema_version >= 4
            and acceptance_partition in {
                'holdout', 'validation', 'reproducibility',
            }
        )
        if formal_acceptance:
            required_core = {
                'recording_complete',
                'cleanup_complete',
                'controller_goal',
                'ground_truth_goal',
                'expected_terminal_state',
                'required_state_path',
                'required_events',
                'no_forbidden_states',
                'no_forbidden_events',
                'collision_expectation',
            }
            missing_core = sorted(required_core - set(all_of))
            if missing_core:
                raise ValueError(
                    f'{location}.success formal acceptance omits: '
                    + ', '.join(missing_core)
                )
            if collision_expected is not False:
                raise ValueError(
                    f'{location}.success formal acceptance requires '
                    'collision_expected=false'
                )
            if (
                'FAILSAFE' not in forbidden_states
                or not {'TIMEOUT', 'FAILSAFE'} <= set(forbidden_events)
            ):
                raise ValueError(
                    f'{controller_location} formal acceptance must '
                    'forbid FAILSAFE and TIMEOUT'
                )
            has_escape_path = bool(
                {'ESCAPE_REPULSE', 'ESCAPE_ASSIST'} & set(required_path)
            )
            has_escape_event = 'ESCAPE_STARTED' in required_event_set
            if has_escape_path != has_escape_event:
                raise ValueError(
                    f'{controller_location} escape path/event binding '
                    'is inconsistent'
                )
            if metric_applicability['escape_attempt'] != has_escape_path:
                raise ValueError(
                    f'{location}.metric_applicability.escape_attempt '
                    'must match the required escape path'
                )
            for name in ('escape_duration', 'orbit_count'):
                if (
                    metric_applicability[name]
                    != metric_applicability['escape_attempt']
                ):
                    raise ValueError(
                        f'{location}.metric_applicability.{name} must '
                        'match escape_attempt'
                    )
        normalized_success = {
            'all_of': list(all_of),
            'controller': normalized_controller,
            'ground_truth': normalized_ground_truth,
            'minimum_saturation_samples': minimum_saturation,
        }
        if schema_version >= 2:
            normalized_success['collision_expected'] = collision_expected
        if schema_version >= 3:
            if collision_expected is not None:
                declared_predicates.add('collision_expectation')
            if minimum_saturation > 0:
                declared_predicates.add('minimum_saturation_samples')
            backed_predicates = set(declared_predicates)
            if has_ground_truth:
                backed_predicates.add('ground_truth_goal')
            route_qualification = (
                normalized_ground_truth
                .get('aggregate_field', {})
                .get('route_barrier_qualification')
                if isinstance(
                    normalized_ground_truth.get('aggregate_field'),
                    dict,
                )
                else None
            )
            if route_qualification is not None:
                backed_predicates.add('route_blocker_encountered')
                declared_predicates.add('route_blocker_encountered')
            if (
                outcome == 'goal'
                or (
                    schema_version >= 4
                    and normalized_controller[
                        'expected_terminal_state'
                    ] == 'GOAL_HOLD'
                    and 'GOAL_REACHED' in (
                        set(normalized_controller['required_events'])
                        | set(
                            normalized_controller[
                                'required_event_sequence'
                            ]
                        )
                    )
                )
            ):
                backed_predicates.add('controller_goal')
            predicates_requiring_backing = {
                'controller_goal',
                'ground_truth_goal',
                'expected_terminal_state',
                'required_state_sequence',
                'required_events',
                'required_event_sequence',
                'no_forbidden_states',
                'no_forbidden_events',
                'minimum_saturation_samples',
                'collision_expectation',
                'route_blocker_encountered',
            }
            unbacked_predicates = sorted(
                (set(all_of) & predicates_requiring_backing)
                - backed_predicates
            )
            if unbacked_predicates:
                raise ValueError(
                    f'{location}.success.all_of selects undeclared or '
                    'vacuous evidence: ' + ', '.join(unbacked_predicates)
                )
            missing_predicates = sorted(
                declared_predicates - set(all_of)
            )
            if missing_predicates:
                raise ValueError(
                    f'{location}.success.all_of does not bind declared '
                    'evidence: ' + ', '.join(missing_predicates)
                )
        if schema_version >= 4:
            normalized_success['result_scopes'] = result_scopes
        support_reason = _disturbance_support(disturbances, schema_version)
        if support_reason and status == 'executable_unverified':
            status = 'unsupported'
            unsupported_reason = support_reason
        normalized_case = {
            'case_id': case_id,
            'family': family,
            'description': str(case.get('description', '')),
            'status': status,
            'unsupported_reason': unsupported_reason,
            'profiles': list(profiles),
            'seeds': list(seeds),
            'starts': normalized_starts,
            'sources': normalized_sources,
            'bounds_m': bounds,
            'room_center_m': center,
            'disturbances': disturbances,
            'validation': {
                'world': validation_world,
                'contacts_enabled': contacts_enabled,
            },
            'frozen_profile': deepcopy(frozen_profile),
            'algorithm': {
                'ablations': ablations,
                'launch_overrides': dict(overrides),
            },
            'success': normalized_success,
        }
        if schema_version >= 4:
            normalized_case.update({
                'acceptance_family': acceptance_family,
                'acceptance_partition': acceptance_partition,
                'repeat_reference': repeat_reference,
                'metric_applicability': metric_applicability,
            })
        normalized_cases.append(normalized_case)

    return {
        'source_path': str(source_path),
        'schema_version': schema_version,
        'suite_id': suite_id,
        'description': str(document.get('description', '')),
        'mode': 'simulation',
        'execution': execution,
        'metadata': {
            'experiment_version': str(metadata['experiment_version']),
            'operator_notes': str(metadata.get('operator_notes', '')),
        },
        'level_map': normalized_levels,
        'defaults': defaults,
        'frozen_profile': frozen_profile,
        'cases': normalized_cases,
        'original': document,
    }


def _level_combinations(case, level_map):
    choices = []
    for source in case['sources']:
        if 'levels' in source:
            choices.append(source['levels'])
        else:
            choices.append([None])
    return itertools.product(*choices)


def deterministic_case_key(resolved):
    """Return a stable digest of every dimension that identifies a run case."""
    fields = [
        'suite_id', 'case_id', 'profile', 'start', 'sources', 'bounds_m',
        'room_center_m', 'disturbances', 'algorithm', 'success', 'seed',
    ]
    if resolved.get('schema_version', 1) >= 2:
        fields.extend(('validation', 'frozen_profile'))
    if resolved.get('schema_version', 1) >= 4:
        fields.extend((
            'acceptance_family',
            'acceptance_partition',
            'repeat_reference',
            'metric_applicability',
        ))
    identity = {
        name: resolved[name]
        for name in fields
    }
    payload = json.dumps(
        identity, sort_keys=True, separators=(',', ':'), allow_nan=False
    ).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def expand_suite(suite, case_ids=None):
    """Expand in case, profile, start, ordered-level, then seed order."""
    selected = set(case_ids or [])
    known = {case['case_id'] for case in suite['cases']}
    unknown = sorted(selected - known)
    if unknown:
        raise ValueError('unknown --case-id values: ' + ', '.join(unknown))
    runs = []
    unsupported = []
    for case in suite['cases']:
        if selected and case['case_id'] not in selected:
            continue
        if case['status'] == 'unsupported':
            unsupported.append({
                'case_id': case['case_id'],
                'family': case['family'],
                'reason': case['unsupported_reason'],
            })
            continue
        for profile in case['profiles']:
            for start in case['starts']:
                for level_labels in _level_combinations(
                    case, suite['level_map']
                ):
                    sources = []
                    level_tuple = []
                    for source, label in zip(case['sources'], level_labels):
                        resolved_source = deepcopy(source)
                        if label is not None:
                            resolved_source.pop('levels', None)
                            resolved_source['level'] = label
                            resolved_source['relative_lumen_input'] = (
                                suite['level_map'][label]
                            )
                            level_tuple.append(label)
                        else:
                            level_tuple.append(None)
                        sources.append(resolved_source)
                    resolved_success_template = deepcopy(case['success'])
                    if suite['schema_version'] >= 4:
                        ground_truth = resolved_success_template[
                            'ground_truth'
                        ]
                        aggregate_record = ground_truth['aggregate_field']
                        truth_arguments = {
                            'sources': sources,
                            'bounds_m': case['bounds_m'],
                            'disturbances': case['disturbances'],
                            'wall_margin_m': ground_truth['wall_margin_m'],
                            'minimum_source_score': ground_truth[
                                'minimum_source_score'
                            ],
                        }
                        if aggregate_record is None:
                            aggregate_record = (
                                aggregate_field_truth
                                .derive_aggregate_field_truth(
                                    **truth_arguments
                                )
                            )
                            if case['metric_applicability'][
                                'escape_attempt'
                            ]:
                                local_ids = [
                                    source['id']
                                    for source in sources
                                    if source['evaluation_role']
                                    == 'local_minimum'
                                ]
                                aggregate_record = (
                                    aggregate_field_truth
                                    .attach_local_branch_qualifications(
                                        aggregate_record,
                                        sources,
                                        local_ids,
                                        case['disturbances'],
                                    )
                                )
                        else:
                            if (
                                case['metric_applicability'][
                                    'escape_attempt'
                                ]
                                and not aggregate_record.get(
                                    'local_branch_qualifications'
                                )
                            ):
                                raise ValueError(
                                    f'{case["case_id"]} designated escape '
                                    'lacks local branch qualification'
                                )
                            aggregate_record = (
                                aggregate_field_truth
                                .validate_aggregate_field_truth(
                                    aggregate_record,
                                    **truth_arguments,
                                )
                            )
                        ground_truth['aggregate_field'] = aggregate_record
                    for seed in case['seeds']:
                        resolved_success = deepcopy(
                            resolved_success_template
                        )
                        resolved = {
                            'schema_version': suite['schema_version'],
                            'suite_id': suite['suite_id'],
                            'case_id': case['case_id'],
                            'family': case['family'],
                            'description': case['description'],
                            'profile': profile,
                            'start': deepcopy(start),
                            'sources': sources,
                            'source_level_tuple': level_tuple,
                            'bounds_m': list(case['bounds_m']),
                            'room_center_m': list(case['room_center_m']),
                            'disturbances': deepcopy(case['disturbances']),
                            'validation': deepcopy(case['validation']),
                            'frozen_profile': deepcopy(
                                case['frozen_profile']
                            ),
                            'algorithm': deepcopy(case['algorithm']),
                            'success': resolved_success,
                            'seed': seed,
                        }
                        if suite['schema_version'] >= 4:
                            resolved.update({
                                'acceptance_family': case[
                                    'acceptance_family'
                                ],
                                'acceptance_partition': case[
                                    'acceptance_partition'
                                ],
                                'repeat_reference': deepcopy(
                                    case['repeat_reference']
                                ),
                                'metric_applicability': deepcopy(
                                    case['metric_applicability']
                                ),
                            })
                        resolved['case_key'] = deterministic_case_key(resolved)
                        runs.append(resolved)
    return runs, unsupported
