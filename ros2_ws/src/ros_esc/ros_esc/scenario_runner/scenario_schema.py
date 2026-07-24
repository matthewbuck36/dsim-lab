"""Versioned Phase 06 scenario validation and deterministic expansion."""

import hashlib
import itertools
import json
import math
import re
from copy import deepcopy
from pathlib import Path

import yaml


SCHEMA_VERSION = 1
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
    'required_state_sequence',
    'required_events',
    'no_forbidden_events',
    'minimum_saturation_samples',
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
    'metadata', 'level_map', 'defaults', 'cases',
}
EXECUTION_KEYS = {
    'max_parallel_runs', 'gazebo_gui', 'runs_root', 'preflight_timeout_sec',
    'run_timeout_sec', 'wall_timeout_sec', 'shutdown_grace_sec',
    'stop_on_run_failure', 'stop_on_cleanup_failure',
}
METADATA_KEYS = {'experiment_version', 'operator_notes'}
DEFAULT_KEYS = {'bounds_m', 'room_center_m', 'disturbances'}
DISTURBANCE_KEYS = {'sensor_noise', 'sensor_delay_sec', 'pose_delay_sec'}
NOISE_KEYS = {'model', 'bound', 'std_dev'}
CASE_KEYS = {
    'case_id', 'family', 'description', 'status', 'unsupported_reason',
    'profiles', 'seeds', 'starts', 'sources', 'bounds_m', 'room_center_m',
    'disturbances', 'algorithm', 'success',
}
START_KEYS = {'id', 'x_m', 'y_m', 'yaw_rad'}
SOURCE_KEYS = {
    'id', 'x_m', 'y_m', 'relative_lumen_input', 'levels',
    'evaluation_role',
}
ALGORITHM_KEYS = {'ablations', 'launch_overrides'}
SUCCESS_KEYS = {
    'all_of', 'controller', 'ground_truth', 'minimum_saturation_samples',
}
CONTROLLER_KEYS = {
    'expected_terminal_state', 'required_state_sequence', 'required_events',
    'forbidden_events',
}
GROUND_TRUTH_KEYS = {'goal_source_ids', 'final_position_tolerance_m'}
SAFE_ID = re.compile('^[A-Za-z0-9][A-Za-z0-9._-]*$')

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


def _disturbance_support(disturbances):
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
    if document.get('schema_version') != SCHEMA_VERSION:
        raise ValueError(f'schema_version must equal {SCHEMA_VERSION}')
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
        controller = success.get('controller', {})
        _unknown(controller, CONTROLLER_KEYS, f'{location}.success.controller')
        ground_truth = success.get('ground_truth', {})
        _unknown(
            ground_truth, GROUND_TRUTH_KEYS,
            f'{location}.success.ground_truth',
        )
        goal_ids = ground_truth.get('goal_source_ids', [])
        if not isinstance(goal_ids, list) or not set(goal_ids) <= source_ids:
            raise ValueError(
                f'{location}.success.ground_truth.goal_source_ids are invalid'
            )
        tolerance = _number(
            ground_truth.get('final_position_tolerance_m', 0.35),
            f'{location}.success.ground_truth.final_position_tolerance_m',
            positive=True,
        )
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
        normalized_success = {
            'all_of': list(all_of),
            'controller': {
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
            },
            'ground_truth': {
                'goal_source_ids': list(goal_ids),
                'final_position_tolerance_m': tolerance,
            },
            'minimum_saturation_samples': minimum_saturation,
        }
        support_reason = _disturbance_support(disturbances)
        if support_reason and status == 'executable_unverified':
            status = 'unsupported'
            unsupported_reason = support_reason
        normalized_cases.append({
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
            'algorithm': {
                'ablations': ablations,
                'launch_overrides': dict(overrides),
            },
            'success': normalized_success,
        })

    return {
        'source_path': str(source_path),
        'schema_version': SCHEMA_VERSION,
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
    identity = {
        name: resolved[name]
        for name in (
            'suite_id', 'case_id', 'profile', 'start', 'sources', 'bounds_m',
            'room_center_m', 'disturbances', 'algorithm', 'success', 'seed',
        )
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
                    for seed in case['seeds']:
                        resolved = {
                            'schema_version': SCHEMA_VERSION,
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
                            'algorithm': deepcopy(case['algorithm']),
                            'success': deepcopy(case['success']),
                            'seed': seed,
                        }
                        resolved['case_key'] = deterministic_case_key(resolved)
                        runs.append(resolved)
    return runs, unsupported
