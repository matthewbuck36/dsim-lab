"""Focused tests for strict Phase 06 scenario parsing and expansion."""

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from ros_esc.scenario_runner import aggregate_field_truth
from ros_esc.scenario_runner.scenario_schema import (
    deterministic_case_key,
    expand_suite,
    load_suite,
)

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SMOKE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
)
CATALOG = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase06_catalog.yaml'
)
DIAGNOSTIC_ACTIVATION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_1_diagnostic_activation.yaml'
)
RECENTER_RECOVERY = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_2_recenter.yaml'
)
V6_HUE_SWEEP = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_v6_hue_sweep.yaml'
)
M2_1_CORRECTION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m2_1_correction_probe.yaml'
)
M2_2_CORRECTION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m2_2_efficiency_correction_probe.yaml'
)
M2_3_CORRECTION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m2_3_assisted_recovery_stop_probe.yaml'
)
M3_SPATIAL_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m3_spatial_suite.yaml'
)
M4_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_visible_probe.yaml'
)
M4_1_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_1_visible_probe.yaml'
)
M4_2_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_2_visible_probe.yaml'
)
M4_2_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_2_two_light_suite.yaml'
)
M4_3_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_3_visible_probe.yaml'
)
M4_3_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_3_two_light_suite.yaml'
)
M4_4_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_4_visible_probe.yaml'
)
M4_4_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_4_two_light_suite.yaml'
)
M4_5_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_5_visible_probe.yaml'
)
M4_5_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_5_two_light_suite.yaml'
)
M4_6_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_6_visible_probe.yaml'
)
M4_6_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_6_two_light_suite.yaml'
)
M4_7_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_7_visible_probe.yaml'
)
M4_7_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_7_two_light_suite.yaml'
)
M4_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_two_light_suite.yaml'
)
M4_THREE_LIGHT_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_three_light_probe.yaml'
)
V8_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_primary_visible_probe.yaml'
)
V8_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_primary_repeats.yaml'
)
V8_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_secondary_visible_probe.yaml'
)
V8_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_secondary_repeats.yaml'
)
V8_1_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_primary_visible_probe.yaml'
)
V8_1_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_primary_repeats.yaml'
)
V8_1_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_secondary_visible_probe.yaml'
)
V8_1_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_secondary_repeats.yaml'
)
V8_2_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_primary_visible_probe.yaml'
)
V8_2_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_primary_repeats.yaml'
)
V8_2_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_secondary_visible_probe.yaml'
)
V8_2_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_secondary_repeats.yaml'
)
V8_3_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_3_primary_visible_probe.yaml'
)
V8_3_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_3_primary_repeats.yaml'
)
V8_3_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_3_secondary_visible_probe.yaml'
)
V8_3_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_3_secondary_repeats.yaml'
)
V8_4_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_4_primary_visible_probe.yaml'
)
V8_4_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_4_primary_repeats.yaml'
)
V8_4_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_4_secondary_visible_probe.yaml'
)
V8_4_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_4_secondary_repeats.yaml'
)
HISTORICAL_V2_ACTIVATION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml'
)
CORNER_ORIGIN_WORLD = (
    PACKAGE_ROOT.parent
    / 'turtlebot3_rotating_sensor/worlds/'
    'gesc_gaussian_corner_origin_validation.world'
)
HISTORICAL_WORLD = (
    PACKAGE_ROOT.parent
    / 'turtlebot3_rotating_sensor/worlds/'
    'gesc_gaussian_validation.world'
)
HISTORICAL_IMMUTABILITY = (
    PACKAGE_ROOT.parents[2]
    / 'docs/codex/gesc_gaussian/validation/'
    'phase_08_7_m1_historical_immutability.json'
)


def _document():
    return {
        'schema_version': 1,
        'suite_id': 'unit_suite',
        'description': 'schema fixture',
        'mode': 'simulation',
        'execution': {
            'max_parallel_runs': 1,
            'run_timeout_sec': 10.0,
            'wall_timeout_sec': 20.0,
        },
        'metadata': {
            'experiment_version': 'phase06-test',
            'operator_notes': '',
        },
        'level_map': {},
        'defaults': {
            'bounds_m': [-2.0, 2.0, -2.0, 2.0],
            'room_center_m': [0.0, 0.0],
        },
        'cases': [{
            'case_id': 'case_a',
            'family': 'smoke',
            'status': 'executable_unverified',
            'profiles': ['robust_gaussian_v1'],
            'seeds': [3],
            'starts': [
                {'id': 'center', 'x_m': 0.0, 'y_m': 0.0, 'yaw_rad': 0.0}
            ],
            'sources': [{
                'id': 'goal',
                'x_m': 1.0,
                'y_m': 0.5,
                'relative_lumen_input': 1000.0,
                'evaluation_role': 'goal',
            }],
            'algorithm': {
                'ablations': {
                    'gaussian_fill_enabled': True,
                    'affine_assist_enabled': True,
                    'recenter_enabled': True,
                },
                'launch_overrides': {},
            },
            'success': {
                'all_of': ['recording_complete', 'cleanup_complete'],
                'controller': {
                    'expected_terminal_state': None,
                    'required_state_sequence': [],
                    'required_events': [],
                    'forbidden_events': [],
                },
                'ground_truth': {
                    'goal_source_ids': ['goal'],
                    'final_position_tolerance_m': 0.35,
                },
                'minimum_saturation_samples': 0,
            },
        }],
    }


def _load(tmp_path, document):
    path = tmp_path / 'suite.yaml'
    path.write_text(
        yaml.safe_dump(document, sort_keys=False), encoding='utf-8'
    )
    return load_suite(path)


def _raw_document(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def _v3_document():
    document = _document()
    document['schema_version'] = 3
    document['defaults'].update({
        'validation_world': True,
        'simulation_contacts_enabled': True,
    })
    document['cases'][0]['algorithm']['launch_overrides'] = {
        'goal_score_threshold': 0.95,
        'goal_score_rotation_period_sec': 3.0,
        'goal_score_required_rotations': 2,
        'goal_hold_sec': 3.0,
        'undesired_score_hold_sec': 3.0,
        'verification_max_sec': 12.0,
    }
    document['cases'][0]['success'] = {
        'all_of': [
            'recording_complete',
            'cleanup_complete',
            'controller_goal',
            'expected_terminal_state',
            'required_state_path',
            'required_events',
            'no_forbidden_states',
            'no_forbidden_events',
            'collision_expectation',
        ],
        'controller': {
            'contract_id': 'case_a',
            'expected_verification_outcome': 'goal',
            'reachability_argument': (
                'A calibrated source sustains the target.'
            ),
            'expected_terminal_state': 'GOAL_HOLD',
            'required_state_path': [
                'SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD',
            ],
            'required_events': [
                'CONVERGENCE_CONFIRMED', 'GOAL_REACHED',
            ],
            'forbidden_states': ['FAILSAFE'],
            'forbidden_events': ['TIMEOUT', 'FAILSAFE'],
        },
        'ground_truth': {
            'goal_source_ids': ['goal'],
            'final_position_tolerance_m': 0.35,
        },
        'collision_expected': False,
    }
    return document


def _v4_document():
    document = _v3_document()
    document['schema_version'] = 4
    case = document['cases'][0]
    case.update({
        'acceptance_family': 'lifecycle',
        'acceptance_partition': 'validation',
        'metric_applicability': {
            'escape_attempt': False,
            'escape_duration': False,
            'orbit_count': False,
            'revisit': False,
            'delay': False,
            'saturation': False,
        },
    })
    case['sources'][0].update({
        'x_m': 0.0,
        'y_m': 0.0,
        'relative_lumen_input': 2500.0,
    })
    record = deepcopy(_v4_production_truth())
    success = case['success']
    success['all_of'].append('ground_truth_goal')
    success['ground_truth'] = {
        'method': 'aggregate_field',
        'final_position_tolerance_m': 0.35,
        'wall_margin_m': 0.35,
        'minimum_source_score': 0.95,
        'aggregate_field': record,
    }
    success['result_scopes'] = {
        'full_lifecycle': {
            'anchor_state': 'SEARCH',
            'boundary_state': None,
            'graceful_stop': False,
            'all_of': list(success['all_of']),
        },
    }
    return document


def _v5_document():
    document = _v3_document()
    document['schema_version'] = 5
    document['defaults'].update({
        'bounds_m': [-0.25, 3.75, -0.25, 3.75],
        'room_center_m': [1.75, 1.75],
        'validation_world': True,
        'simulation_contacts_enabled': True,
        'geometry_profile': 'corner_origin_diagonal_sector_v1',
    })
    case = document['cases'][0]
    case.update({
        'family': 'corner_origin',
        'acceptance_family': 'corner_origin_diagonal_sector',
        'acceptance_partition': 'development',
        'known_topology': {
            'expected_local_minima': 1,
            'expected_global_minima': 1,
        },
        'metric_applicability': {
            'escape_attempt': True,
            'escape_duration': True,
            'orbit_count': True,
            'revisit': False,
            'delay': False,
            'saturation': False,
        },
        'starts': [{
            'id': 'corner_start',
            'x_m': 0.0,
            'y_m': 0.0,
            'yaw_rad': 0.0,
        }],
        'sources': [
            {
                'id': 'local',
                'x_m': 1.0606601717798212,
                'y_m': 1.0606601717798212,
                'relative_lumen_input': 400.0,
                'evaluation_role': 'local_minimum',
            },
            {
                'id': 'global',
                'x_m': 3.5,
                'y_m': 3.5,
                'relative_lumen_input': 1600.0,
                'evaluation_role': 'goal',
            },
        ],
    })
    case['algorithm']['launch_overrides'].update({
        'wall_margin_m': 0.20,
        'gaussian_fill_max_fills': 1,
    })
    case['success'] = {
        'all_of': [
            'recording_complete',
            'cleanup_complete',
            'required_state_path',
            'required_events',
            'no_forbidden_states',
            'no_forbidden_events',
            'collision_expectation',
            'local_recovery_stage',
            'post_recovery_global_proximity',
            'fill_cardinality',
        ],
        'controller': {
            'contract_id': 'case_a',
            'expected_verification_outcome': 'below_target_extremum',
            'reachability_argument': (
                'The declared weaker local precedes the stronger global.'
            ),
            'required_state_path': [
                'SEARCH',
                'VERIFY_EXTREMUM',
                'DESIGN_OR_MERGE_FILL',
                'ESCAPE_REPULSE',
                'RECENTER',
                'SEARCH',
            ],
            'required_events': [
                'CONVERGENCE_CONFIRMED',
                'FILL_CREATED',
                'ESCAPE_STARTED',
                'RECENTER_STARTED',
                'RECENTER_COMPLETE',
            ],
            'forbidden_states': ['FAILSAFE'],
            'forbidden_events': ['TIMEOUT', 'FAILSAFE'],
        },
        'ground_truth': {
            'method': 'declared_global_proximity',
            'global_source_id': 'global',
            'proximity_radius_m': 0.35,
        },
        'staged_recovery': {
            'local_source_ids': ['local'],
            'global_source_id': 'global',
            'convergence_to_local_max_m': 0.60,
            'convergence_to_global_min_m': 0.75,
            'fill_to_convergence_max_m': 0.50,
            'global_proximity_radius_m': 0.35,
        },
        'collision_expected': False,
    }
    case['success']['result_scopes'] = {
        'full_lifecycle': {
            'anchor_state': 'SEARCH',
            'boundary_state': None,
            'graceful_stop': False,
            'all_of': list(case['success']['all_of']),
        },
    }
    return document


def _v6_document():
    document = _v5_document()
    document['schema_version'] = 6
    case = document['cases'][0]
    case['algorithm']['launch_overrides'].update({
        'convergence_state_gating_enabled': True,
        'convergence_minimum_path_length_m': 0.20,
        'convergence_maximum_path_efficiency': 0.50,
        'post_recovery_guidance_enabled': True,
        'post_recovery_guidance_max_sec': 60.0,
        'post_recovery_retry_limit': 3,
        'modified_cost_affine_gain': 0.50,
        'modified_cost_affine_decay_rate': 0.05,
        'modified_cost_affine_max_age': 20.0,
        'gaussian_fill_reuse_retained_samples_on_redesign': True,
        'recoverable_navigation_enabled': True,
        'recovery_retry_limit': 3,
        'boundary_recovery_trigger_clearance_m': 0.025,
        'boundary_recovery_release_clearance_m': 0.10,
        'recenter_target_fill_clearance_m': 0.05,
        'recenter_max_sec': 60.0,
        'recenter_tolerance_m': 0.35,
        'post_recovery_affine_weight': 0.50,
        'post_recovery_affine_taper_distance_m': 0.50,
    })
    case['success']['ground_truth']['proximity_radius_m'] = 1.20
    case['success']['staged_recovery'].update({
        'local_association_mode': 'verified_trap',
        'global_proximity_radius_m': 1.20,
        'global_closer_radius_m': 1.00,
    })
    return document


def _v7_document():
    document = _v6_document()
    document['schema_version'] = 7
    document['execution'].update({
        'run_timeout_sec': 480.0,
        'wall_timeout_sec': 660.0,
    })
    case = document['cases'][0]
    case['algorithm']['launch_overrides'].update({
        'post_recovery_guidance_max_sec': 90.0,
        'post_recovery_progress_enabled': True,
        'post_recovery_guidance_min_progress_m': 0.60,
        'post_recovery_liveness_window_sec': 12.0,
        'post_recovery_liveness_min_path_length_m': 0.60,
        'post_recovery_liveness_max_displacement_m': 0.20,
        'post_recovery_direction_refresh_limit': 1,
        'robust_search_epoch_reset_enabled': True,
        'recenter_tolerance_m': 0.15,
    })
    case['success']['staged_recovery'][
        'post_stage_a_timeout_sec'
    ] = 120.0
    return document


@lru_cache(maxsize=1)
def _v4_production_truth():
    return aggregate_field_truth.derive_aggregate_field_truth(
        [{
            'id': 'goal',
            'x_m': 0.0,
            'y_m': 0.0,
            'relative_lumen_input': 2500.0,
            'evaluation_role': 'goal',
        }],
        [-2.0, 2.0, -2.0, 2.0],
        {'sensor_noise': {'model': 'none'}},
    )


def test_checked_in_suites_validate_and_catalog_marks_gaps():
    """Validate checked-in suites and their declared unsupported gaps."""
    smoke = load_suite(SMOKE)
    catalog = load_suite(CATALOG)
    diagnostic = load_suite(DIAGNOSTIC_ACTIVATION)
    recenter = load_suite(RECENTER_RECOVERY)
    smoke_runs, smoke_unsupported = expand_suite(smoke)
    catalog_runs, catalog_unsupported = expand_suite(catalog)
    diagnostic_runs, diagnostic_unsupported = expand_suite(diagnostic)
    recenter_runs, recenter_unsupported = expand_suite(recenter)

    assert [run['profile'] for run in smoke_runs] == [
        'robust_gaussian_v1', 'legacy'
    ]
    assert smoke_unsupported == []
    assert len(catalog_runs) >= 20
    assert len(diagnostic_runs) == 10
    assert diagnostic_unsupported == []
    assert len(recenter_runs) == 1
    assert recenter_unsupported == []
    recenter_path = recenter_runs[0]['success']['controller'][
        'required_state_path'
    ]
    assert recenter_path == [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'RECENTER',
        'SEARCH',
    ]
    assert all(
        run['success']['controller']['verification_timing'][
            'selected_margin_sec'
        ] == pytest.approx(3.0)
        for run in diagnostic_runs
    )
    assert {item['case_id'] for item in catalog_unsupported} >= {
        'ordered_levels_1_to_5',
        'sensor_pose_delay',
        'deterministic_gaussian_noise',
        'physical_wall_collision',
        'raw_attraction_static_ablation',
        'more_than_five_sources',
        'plain_legacy_without_pde',
    }


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (lambda doc: doc.update({'schema_version': 9}), 'schema_version'),
        (
            lambda doc: doc.update({'mode': 'physical'}),
            'mode must be simulation',
        ),
        (
            lambda doc: doc['execution'].update({'max_parallel_runs': 2}),
            'max_parallel_runs',
        ),
        (
            lambda doc: doc['cases'][0].update({'mystery': True}),
            'unknown keys',
        ),
        (
            lambda doc: doc['cases'][0].update({'success': []}),
            'must be a mapping',
        ),
        (
            lambda doc: doc['cases'][0].update({'profiles': ['unknown']}),
            'profiles',
        ),
        (
            lambda doc: doc['cases'][0].update({'seeds': []}),
            'seeds',
        ),
        (
            lambda doc: doc['cases'][0]['starts'][0].update({'x_m': 3.0}),
            'outside bounds',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm']['ablations'].update(
                {'raw_cost_enabled': False}
            ),
            'unknown keys',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {'all_of': ['invented_gate']}
            ),
            'unknown predicates',
        ),
    ],
)
def test_strict_schema_rejects_unknown_invalid_or_unsafe_values(
    tmp_path, mutation, match
):
    """Reject malformed, unknown, nonserial, or unsafe suite values."""
    document = _document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_source_count_is_one_to_five_for_executable_cases(tmp_path):
    """Enforce the simulator's executable one-to-five-source range."""
    document = _document()
    document['cases'][0]['sources'] = []
    with pytest.raises(ValueError, match='1 to 5'):
        _load(tmp_path, document)

    document = _document()
    document['cases'][0]['sources'] *= 6
    for index, source in enumerate(document['cases'][0]['sources']):
        source['id'] = f'source_{index}'
    with pytest.raises(ValueError, match='1 to 5'):
        _load(tmp_path, document)


def test_two_ordered_level_dimensions_expand_to_25(tmp_path):
    """Expand two ordered five-level sources to 25 deterministic cases."""
    document = _document()
    document['level_map'] = {
        str(level): float(level * 100) for level in range(1, 6)
    }
    document['cases'][0]['sources'] = [
        {
            'id': 'local',
            'x_m': -1.0,
            'y_m': 0.0,
            'levels': [1, 2, 3, 4, 5],
            'evaluation_role': 'local_minimum',
        },
        {
            'id': 'goal',
            'x_m': 1.0,
            'y_m': 0.0,
            'levels': [1, 2, 3, 4, 5],
            'evaluation_role': 'goal',
        },
    ]
    suite = _load(tmp_path, document)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    assert len(runs) == 25
    assert runs[0]['source_level_tuple'] == ['1', '1']
    assert runs[-1]['source_level_tuple'] == ['5', '5']
    assert [
        source['relative_lumen_input']
        for source in runs[0]['sources']
    ] == [100.0, 100.0]


def test_expansion_order_and_case_keys_are_stable(tmp_path):
    """Keep profile, start, level, seed order and case keys stable."""
    document = _document()
    case = document['cases'][0]
    case['profiles'] = ['legacy', 'robust_gaussian_v1']
    case['starts'].append(
        {'id': 'north', 'x_m': 0.0, 'y_m': 1.0, 'yaw_rad': -1.0}
    )
    case['seeds'] = [7, 5]
    suite = _load(tmp_path, document)
    first, _ = expand_suite(suite)
    second, _ = expand_suite(suite)

    assert [
        (run['profile'], run['start']['id'], run['seed']) for run in first
    ] == [
        ('legacy', 'center', 7),
        ('legacy', 'center', 5),
        ('legacy', 'north', 7),
        ('legacy', 'north', 5),
        ('robust_gaussian_v1', 'center', 7),
        ('robust_gaussian_v1', 'center', 5),
        ('robust_gaussian_v1', 'north', 7),
        ('robust_gaussian_v1', 'north', 5),
    ]
    assert [run['case_key'] for run in first] == [
        run['case_key'] for run in second
    ]
    changed = deepcopy(first[0])
    changed['seed'] = 99
    assert deterministic_case_key(changed) != first[0]['case_key']


@pytest.mark.parametrize(
    ('disturbance', 'reason'),
    [
        ({'sensor_delay_sec': 0.1}, 'sensor delay'),
        ({'pose_delay_sec': 0.1}, 'pose delay'),
        (
            {'sensor_noise': {'model': 'gaussian', 'std_dev': 0.1}},
            'Gaussian noise',
        ),
    ],
)
def test_unsupported_disturbances_are_classified_without_launch(
    tmp_path, disturbance, reason
):
    """Classify unavailable disturbance infrastructure without launching."""
    document = _document()
    document['cases'][0]['disturbances'] = disturbance
    suite = _load(tmp_path, document)
    runs, unsupported = expand_suite(suite)

    assert runs == []
    assert reason in unsupported[0]['reason']


def test_case_filter_rejects_unknown_names(tmp_path):
    """Reject filters that name no declared scenario case."""
    suite = _load(tmp_path, _document())
    with pytest.raises(ValueError, match='unknown --case-id'):
        expand_suite(suite, case_ids=['missing'])


def test_schema_v3_binds_reachable_activation_contract(tmp_path):
    """Expose a strict path and positive verification margin."""
    suite = _load(tmp_path, _v3_document())
    run = expand_suite(suite)[0][0]
    controller = run['success']['controller']

    assert controller['contract_id'] == run['case_id']
    assert controller['required_state_path'] == [
        'SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD',
    ]
    assert controller['verification_timing'] == {
        'goal_score_threshold': 0.95,
        'rotation_period_sec': 3.0,
        'required_rotations': 2,
        'rotation_duration_sec': 6.0,
        'goal_dwell_sec': 3.0,
        'below_target_dwell_sec': 3.0,
        'verification_timeout_sec': 12.0,
        'goal_required_sec': 9.0,
        'below_target_required_sec': 9.0,
        'goal_margin_sec': 3.0,
        'below_target_margin_sec': 3.0,
        'selected_margin_sec': 3.0,
        'timing_sufficient': True,
    }


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'contract_id': 'shared_anchor'}
            ),
            'must equal case_id',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {
                    'required_state_path': [
                        'SEARCH', 'GOAL_HOLD',
                    ]
                }
            ),
            'must include VERIFY_EXTREMUM',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'][
                'forbidden_states'
            ].append('GOAL_HOLD'),
            'requires and forbids states',
        ),
        (
            lambda doc: doc['cases'][0]['success']['all_of'].remove(
                'no_forbidden_events'
            ),
            'does not bind declared controller evidence',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'verification_max_sec': 9.0}),
            'no positive verification timing margin',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'goal_hold_sec': 0.0}),
            'must be positive',
        ),
        (
            lambda doc: doc['cases'][0].update({'profiles': ['legacy']}),
            'must equal \\[robust_gaussian_v1\\]',
        ),
    ],
)
def test_schema_v3_rejects_decorative_or_unreachable_contracts(
    tmp_path, mutation, match
):
    """Reject inherited, porous, contradictory, or untimed contracts."""
    document = _v3_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_required_state_path_alternatives_are_schema_v5_only(tmp_path):
    """Keep schema-v1 through schema-v4 controller contracts unchanged."""
    document = _v3_document()
    controller = document['cases'][0]['success']['controller']
    controller['required_state_paths'] = [
        list(controller['required_state_path'])
    ]

    with pytest.raises(ValueError, match='requires schema version 5'):
        _load(tmp_path, document)


def test_schema_v3_allows_only_explicit_timing_insufficient_safe_timeout(
    tmp_path,
):
    """Reserve inadequate verification timing for a bound timeout proof."""
    document = _v3_document()
    case = document['cases'][0]
    case['algorithm']['launch_overrides']['verification_max_sec'] = 8.0
    success = case['success']
    success['all_of'].remove('controller_goal')
    success['all_of'].append('required_event_sequence')
    controller = success['controller']
    controller.update({
        'expected_verification_outcome': 'safe_timeout',
        'expected_terminal_state': 'FAILSAFE',
        'required_state_path': [
            'SEARCH', 'VERIFY_EXTREMUM', 'FAILSAFE',
        ],
        'required_event_sequence': [
            'TIMEOUT', 'FAILSAFE',
        ],
        'required_events': ['CONVERGENCE_CONFIRMED'],
        'forbidden_states': ['GOAL_HOLD'],
        'forbidden_events': ['GOAL_REACHED'],
    })

    suite = _load(tmp_path, document)
    timing = suite['cases'][0]['success']['controller'][
        'verification_timing'
    ]
    assert timing['selected_margin_sec'] == pytest.approx(-1.0)
    assert timing['timing_sufficient'] is False


def _remove_controller_list(document, field, predicate):
    document['cases'][0]['success']['controller'][field] = []
    all_of = document['cases'][0]['success']['all_of']
    if predicate not in all_of:
        all_of.append(predicate)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'expected_terminal_state': None}
            ),
            'must expect terminal GOAL_HOLD',
        ),
        (
            lambda doc: _remove_controller_list(
                doc, 'required_state_sequence', 'required_state_sequence'
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: _remove_controller_list(
                doc, 'required_events', 'required_events'
            ),
            'must require events',
        ),
        (
            lambda doc: doc['cases'][0]['success']['all_of'].append(
                'required_event_sequence'
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'forbidden_states': []}
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'forbidden_events': []}
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {'collision_expected': None}
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {
                    'minimum_saturation_samples': 0,
                    'all_of': (
                        doc['cases'][0]['success']['all_of']
                        + ['minimum_saturation_samples']
                    ),
                }
            ),
            'undeclared or vacuous evidence',
        ),
    ],
)
def test_schema_v3_rejects_selected_vacuous_predicates(
    tmp_path,
    mutation,
    match,
):
    """Do not let an empty declaration satisfy a selected success fact."""
    document = _v3_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v3_safe_timeout_requires_ordered_timeout_then_failsafe(
    tmp_path,
):
    """Reject an unordered or reversed timeout lifecycle declaration."""
    document = _v3_document()
    case = document['cases'][0]
    case['algorithm']['launch_overrides']['verification_max_sec'] = 8.0
    success = case['success']
    success['all_of'].remove('controller_goal')
    success['all_of'].append('required_event_sequence')
    success['controller'].update({
        'expected_verification_outcome': 'safe_timeout',
        'expected_terminal_state': 'FAILSAFE',
        'required_state_path': [
            'SEARCH', 'VERIFY_EXTREMUM', 'FAILSAFE',
        ],
        'required_event_sequence': [
            'FAILSAFE', 'TIMEOUT',
        ],
        'required_events': ['CONVERGENCE_CONFIRMED'],
        'forbidden_states': ['GOAL_HOLD'],
        'forbidden_events': ['GOAL_REACHED'],
    })

    with pytest.raises(ValueError, match='ordered TIMEOUT then FAILSAFE'):
        _load(tmp_path, document)


def test_schema_v4_resolves_aggregate_truth_and_named_scope(tmp_path):
    """Bind aggregate targets and every formal predicate to full lifecycle."""
    document = _v4_document()
    suite = _load(tmp_path, document)
    runs, unsupported = expand_suite(suite)
    run = runs[0]

    assert unsupported == []
    assert run['acceptance_family'] == 'lifecycle'
    assert run['acceptance_partition'] == 'validation'
    assert run['repeat_reference'] is None
    assert run['success']['result_scopes'] == {
        'full_lifecycle': {
            'anchor_state': 'SEARCH',
            'boundary_state': None,
            'graceful_stop': False,
            'all_of': document['cases'][0]['success']['all_of'],
        },
    }
    assert (
        run['success']['ground_truth']['aggregate_field']['result_sha256']
        == document['cases'][0]['success']['ground_truth'][
            'aggregate_field'
        ]['result_sha256']
    )
    assert deterministic_case_key(run) == run['case_key']


def test_schema_v4_allows_development_only_graceful_activation_scope(
    tmp_path,
):
    """Permit a declared branch boundary while retaining global shutdown."""
    document = _v4_document()
    case = document['cases'][0]
    case['acceptance_partition'] = 'activation'
    scoped = case['success']['result_scopes']
    activation_predicates = [
        'required_state_path',
        'required_events',
    ]
    scoped['activation_window'] = {
        'anchor_state': 'VERIFY_EXTREMUM',
        'boundary_state': 'GOAL_HOLD',
        'graceful_stop': True,
        'all_of': activation_predicates,
    }
    scoped['full_lifecycle']['all_of'] = [
        predicate
        for predicate in scoped['full_lifecycle']['all_of']
        if predicate not in activation_predicates
    ]

    run = expand_suite(_load(tmp_path, document))[0][0]

    assert run['success']['result_scopes'][
        'activation_window'
    ]['graceful_stop'] is True


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['ground_truth'].update(
                {'goal_source_ids': ['goal']}
            ),
            'unknown keys',
        ),
        (
            lambda doc: doc['cases'][0]['success']['result_scopes'].update({
                'activation_window': {
                    'anchor_state': 'VERIFY_EXTREMUM',
                    'boundary_state': 'GOAL_HOLD',
                    'graceful_stop': False,
                    'all_of': ['required_state_path'],
                },
            }),
            'assign each predicate',
        ),
        (
            lambda doc: doc['cases'][0]['metric_applicability'].update(
                {'escape_duration': True}
            ),
            'require escape_attempt',
        ),
        (
            lambda doc: doc['cases'][0].update({
                'repeat_reference': {
                    'partition': 'validation',
                    'case_key': 'a' * 64,
                },
            }),
            'only valid for reproducibility',
        ),
        (
            lambda doc: doc['cases'][0]['success']['ground_truth'].update(
                {'minimum_source_score': 0.94}
            ),
            'must retain tolerances',
        ),
    ],
)
def test_schema_v4_rejects_porosity_or_contract_drift(
    tmp_path,
    mutation,
    match,
):
    """Reject manual goals, overlapping scopes, and applicability drift."""
    document = _v4_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v4_requires_repeat_reference_only_for_reproducibility(
    tmp_path,
):
    """Bind every reproducibility case to one sealed unique-case key."""
    document = _v4_document()
    case = document['cases'][0]
    case['acceptance_partition'] = 'reproducibility'
    case['repeat_reference'] = {
        'partition': 'validation',
        'case_key': 'a' * 64,
    }

    run = expand_suite(_load(tmp_path, document))[0][0]

    assert run['repeat_reference']['case_key'] == 'a' * 64


def test_schema_v5_resolves_corner_geometry_and_known_topology(tmp_path):
    """Bind the shifted world, local polar metadata, and exact fill limit."""
    suite = _load(tmp_path, _v5_document())
    runs, unsupported = expand_suite(suite)
    run = runs[0]

    assert unsupported == []
    assert run['schema_version'] == 5
    assert run['validation'] == {
        'world': True,
        'contacts_enabled': True,
        'geometry_profile': 'corner_origin_diagonal_sector_v1',
    }
    assert run['known_topology'] == {
        'expected_global_minima': 1,
        'expected_local_minima': 1,
    }
    assert run['algorithm']['launch_overrides'][
        'gaussian_fill_max_fills'
    ] == 1
    geometry = run['geometry']
    assert geometry['world_file'] == (
        'gesc_gaussian_corner_origin_validation.world'
    )
    assert geometry['bounds_m'] == [-0.25, 3.75, -0.25, 3.75]
    assert geometry['allowed_center_domain_m'] == pytest.approx([
        -0.05, 3.55, -0.05, 3.55
    ])
    local = geometry['local_placements'][0]
    assert local['radius_m'] == pytest.approx(1.5)
    assert local['angle_rad'] == pytest.approx(math.pi / 4.0)
    assert local['angle_deg'] == pytest.approx(45.0)
    assert deterministic_case_key(run) == run['case_key']


def test_schema_v6_resolves_recovery_controls_and_non_gating_closer_radius(
    tmp_path,
):
    suite = _load(tmp_path, _v6_document())
    run = expand_suite(suite)[0][0]
    staged = run['success']['staged_recovery']
    overrides = run['algorithm']['launch_overrides']

    assert run['schema_version'] == 6
    assert staged['local_association_mode'] == 'verified_trap'
    assert staged['global_proximity_radius_m'] == 1.20
    assert staged['global_closer_radius_m'] == 1.00
    assert run['success']['ground_truth']['proximity_radius_m'] == 1.20
    assert overrides['recoverable_navigation_enabled'] is True
    assert overrides['recovery_retry_limit'] == 3
    assert overrides[
        'gaussian_fill_reuse_retained_samples_on_redesign'
    ] is True
    assert overrides['modified_cost_affine_decay_rate'] == 0.05
    assert overrides['post_recovery_affine_weight'] == 0.50
    assert deterministic_case_key(run) == run['case_key']


def test_schema_v7_resolves_progress_guidance_and_post_stage_a_budget(
    tmp_path,
):
    run = expand_suite(_load(tmp_path, _v7_document()))[0][0]
    overrides = run['algorithm']['launch_overrides']
    staged = run['success']['staged_recovery']

    assert run['schema_version'] == 7
    assert overrides['post_recovery_progress_enabled'] is True
    assert overrides['post_recovery_guidance_min_progress_m'] == 0.60
    assert overrides['post_recovery_liveness_window_sec'] == 12.0
    assert overrides[
        'post_recovery_liveness_min_path_length_m'
    ] == 0.60
    assert overrides[
        'post_recovery_liveness_max_displacement_m'
    ] == 0.20
    assert overrides['post_recovery_direction_refresh_limit'] == 1
    assert overrides['robust_search_epoch_reset_enabled'] is True
    assert overrides['recenter_tolerance_m'] == 0.15
    assert staged['post_stage_a_timeout_sec'] == 120.0
    assert 'stage_a_timeout_sec' not in staged


def test_schema_v7_fields_require_v7_and_complete_dependencies(tmp_path):
    document = _v7_document()
    document['schema_version'] = 6
    with pytest.raises(ValueError, match='schema version 7'):
        _load(tmp_path, document)

    document = _v7_document()
    del document['cases'][0]['success']['staged_recovery'][
        'post_stage_a_timeout_sec'
    ]
    with pytest.raises(ValueError, match='post_stage_a_timeout_sec'):
        _load(tmp_path, document)

    document = _v7_document()
    del document['cases'][0]['algorithm']['launch_overrides'][
        'robust_search_epoch_reset_enabled'
    ]
    with pytest.raises(
        ValueError, match='post_recovery_progress_enabled requires'
    ):
        _load(tmp_path, document)

    document = _v7_document()
    document['cases'][0]['profiles'] = ['legacy']
    with pytest.raises(ValueError, match='robust_gaussian_v1'):
        _load(tmp_path, document)


def test_schema_v8_resolves_four_fixed_counted_open_field_suites():
    """Bind the approved probe/repeat populations without wall evidence."""
    expected = {
        V8_PRIMARY_VISIBLE_PROBE: (1, True, {18801}),
        V8_PRIMARY_REPEATS: (10, False, set(range(18811, 18821))),
        V8_SECONDARY_VISIBLE_PROBE: (1, True, {18851}),
        V8_SECONDARY_REPEATS: (5, False, set(range(18861, 18866))),
    }
    profile_keys = None
    for path, (run_count, gui, seeds) in expected.items():
        suite = load_suite(path)
        runs, unsupported = expand_suite(suite)

        assert unsupported == []
        assert len(runs) == run_count
        assert suite['execution']['gazebo_gui'] is gui
        assert {run['seed'] for run in runs} == seeds
        for run in runs:
            overrides = run['algorithm']['launch_overrides']
            assert run['schema_version'] == 8
            assert run['family'] == 'open_field'
            assert run['acceptance_family'] == (
                'counted_two_source_open_field'
            )
            assert run['validation'] == {
                'world': False,
                'contacts_enabled': False,
                'geometry_profile': None,
            }
            assert run['geometry'] is None
            assert run['known_topology'] == {
                'expected_global_minima': 1,
                'expected_local_minima': 1,
            }
            assert overrides['extremum_classification_mode'] == (
                'counted_candidates'
            )
            assert overrides['known_source_count'] == 2
            assert overrides['gaussian_fill_max_fills'] == 1
            assert overrides['convergence_confirmation_policy'] == (
                'qualified_dwell'
            )
            assert overrides['robust_search_epoch_reset_enabled'] is True
            assert overrides['operating_bounds_enabled'] is False
            assert run['success']['collision_expected'] is None
            assert 'collision_expectation' not in run['success']['all_of']
            assert run['success']['ground_truth'][
                'proximity_radius_m'
            ] == 0.50
            assert run['success']['staged_recovery'][
                'post_stage_a_timeout_sec'
            ] == 180.0
            current_keys = frozenset(overrides)
            profile_keys = current_keys if profile_keys is None else profile_keys
            assert current_keys == profile_keys


def test_schema_v8_resolves_four_versioned_outward_assist_suites():
    """Bind v8.1 to one assisted path without mutating fixed v8."""
    expected = {
        V8_1_PRIMARY_VISIBLE_PROBE: (1, True, {18901}),
        V8_1_PRIMARY_REPEATS: (10, False, set(range(18911, 18921))),
        V8_1_SECONDARY_VISIBLE_PROBE: (1, True, {18951}),
        V8_1_SECONDARY_REPEATS: (5, False, set(range(18961, 18966))),
    }
    required_path = [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'ESCAPE_ASSIST',
        'SEARCH',
        'VERIFY_EXTREMUM',
        'GOAL_HOLD',
    ]
    for path, (run_count, gui, seeds) in expected.items():
        suite = load_suite(path)
        runs, unsupported = expand_suite(suite)

        assert unsupported == []
        assert len(runs) == run_count
        assert suite['execution']['gazebo_gui'] is gui
        assert {run['seed'] for run in runs} == seeds
        for run in runs:
            overrides = run['algorithm']['launch_overrides']
            controller = run['success']['controller']
            assert overrides['open_field_escape_assist_enabled'] is True
            assert overrides['gaussian_fill_exit_sigma'] == 8.0
            assert overrides['escape_max_sec'] == 35.0
            assert overrides['operating_bounds_enabled'] is False
            assert overrides['post_recovery_guidance_enabled'] is False
            assert overrides['recoverable_navigation_enabled'] is False
            assert controller['required_state_path'] == required_path
            assert 'ESCAPE_STALLED' in controller['required_events']
            assert 'ESCAPE_STALLED' not in controller['forbidden_events']
            assert 'FILL_MERGED' in controller['forbidden_events']
            assert 'FILL_SUPERSEDED' in controller['forbidden_events']
            assert 'RECENTER' in controller['forbidden_states']
            assert run['validation']['world'] is False
            assert run['validation']['contacts_enabled'] is False


def test_schema_v8_resolves_four_versioned_pretrigger_raw_rank_suites():
    """Bind v8.2 to bounded raw history without changing its assisted path."""
    expected = {
        V8_2_PRIMARY_VISIBLE_PROBE: (1, True, {19001}),
        V8_2_PRIMARY_REPEATS: (10, False, set(range(19011, 19021))),
        V8_2_SECONDARY_VISIBLE_PROBE: (1, True, {19051}),
        V8_2_SECONDARY_REPEATS: (5, False, set(range(19061, 19066))),
    }
    for path, (run_count, gui, seeds) in expected.items():
        suite = load_suite(path)
        runs, unsupported = expand_suite(suite)

        assert unsupported == []
        assert len(runs) == run_count
        assert suite['execution']['gazebo_gui'] is gui
        assert {run['seed'] for run in runs} == seeds
        for run in runs:
            overrides = run['algorithm']['launch_overrides']
            assert overrides['candidate_cost_rotation_period_sec'] == 3.0
            assert overrides['candidate_cost_required_rotations'] == 3
            assert overrides['candidate_cost_pretrigger_rotations'] == 6
            assert overrides['candidate_cost_mad_scale'] == 3.0
            assert overrides['open_field_escape_assist_enabled'] is True
            assert overrides['operating_bounds_enabled'] is False
            assert run['validation']['world'] is False
            assert run['validation']['contacts_enabled'] is False


def test_schema_v8_resolves_four_candidate_informed_fill_suites():
    expected = {
        V8_3_PRIMARY_VISIBLE_PROBE: (1, True, {19101}),
        V8_3_PRIMARY_REPEATS: (10, False, set(range(19111, 19121))),
        V8_3_SECONDARY_VISIBLE_PROBE: (1, True, {19151}),
        V8_3_SECONDARY_REPEATS: (5, False, set(range(19161, 19166))),
    }
    direct = [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'SEARCH',
        'VERIFY_EXTREMUM',
        'GOAL_HOLD',
    ]
    assisted = [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'ESCAPE_ASSIST',
        'SEARCH',
        'VERIFY_EXTREMUM',
        'GOAL_HOLD',
    ]
    for path, (run_count, gui, seeds) in expected.items():
        suite = load_suite(path)
        runs, unsupported = expand_suite(suite)

        assert unsupported == []
        assert len(runs) == run_count
        assert suite['execution']['gazebo_gui'] is gui
        assert {run['seed'] for run in runs} == seeds
        for run in runs:
            overrides = run['algorithm']['launch_overrides']
            controller = run['success']['controller']
            assert overrides['candidate_informed_fill_enabled'] is True
            assert (
                overrides['candidate_informed_fill_amplitude_scale']
                == 1.25
            )
            assert overrides['gaussian_fill_amplitude_max'] == 6.25
            assert overrides['gaussian_fill_sigma_floor_m'] == 0.50
            assert overrides['gaussian_fill_sigma_ceiling_m'] == 1.25
            assert overrides['gaussian_fill_exit_sigma'] == 2.70
            assert overrides['candidate_cost_required_rotations'] == 3
            assert overrides['candidate_cost_pretrigger_rotations'] == 6
            assert overrides['open_field_escape_assist_enabled'] is True
            assert overrides['operating_bounds_enabled'] is False
            assert controller['required_state_path'] == direct
            assert controller['required_state_paths'] == [direct, assisted]
            assert 'ESCAPE_STALLED' not in controller['required_events']
            assert 'FILL_REJECTED' in controller['forbidden_events']
            assert run['validation']['world'] is False
            assert run['validation']['contacts_enabled'] is False


def test_schema_v8_resolves_four_approach_continuity_suites():
    expected = {
        V8_4_PRIMARY_VISIBLE_PROBE: (1, True, {19201}),
        V8_4_PRIMARY_REPEATS: (10, False, set(range(19211, 19221))),
        V8_4_SECONDARY_VISIBLE_PROBE: (1, True, {19251}),
        V8_4_SECONDARY_REPEATS: (5, False, set(range(19261, 19266))),
    }
    for path, (run_count, gui, seeds) in expected.items():
        suite = load_suite(path)
        runs, unsupported = expand_suite(suite)

        assert unsupported == []
        assert len(runs) == run_count
        assert suite['execution']['gazebo_gui'] is gui
        assert {run['seed'] for run in runs} == seeds
        for run in runs:
            overrides = run['algorithm']['launch_overrides']
            assert run['case_id'].startswith('v8_4_')
            assert (
                run['success']['controller']['contract_id']
                == run['case_id']
            )
            assert (
                overrides[
                    'open_field_escape_approach_continuity_enabled'
                ]
                is True
            )
            assert overrides['open_field_escape_assist_enabled'] is True
            assert overrides['candidate_informed_fill_enabled'] is True
            assert overrides['operating_bounds_enabled'] is False
            assert overrides['recoverable_navigation_enabled'] is False
            assert overrides['post_recovery_guidance_enabled'] is False
            assert overrides['modified_cost_affine_gain'] == 0.50
            assert (
                overrides['modified_cost_affine_decay_rate']
                == 0.0000005
            )
            assert overrides['modified_cost_affine_max_age'] == 35.0
            assert overrides['modified_cost_affine_direction_sign'] == 1.0
            assert run['algorithm']['ablations'] == {
                'gaussian_fill_enabled': True,
                'affine_assist_enabled': True,
                'recenter_enabled': False,
            }
            assert run['validation']['world'] is False
            assert run['validation']['contacts_enabled'] is False


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda document, overrides: overrides.update(
                {'open_field_escape_approach_continuity_enabled': 1}
            ),
            'must be true or false',
        ),
        (
            lambda document, overrides: overrides.update(
                {'candidate_informed_fill_enabled': False}
            ),
            'requires candidate-informed fill',
        ),
        (
            lambda document, overrides: overrides.update(
                {'open_field_escape_assist_enabled': False}
            ),
            'requires open-field escape assist',
        ),
        (
            lambda document, overrides: document['cases'][0][
                'algorithm'
            ]['ablations'].update({'affine_assist_enabled': False}),
            'requires algorithm.ablations.affine_assist_enabled',
        ),
        (
            lambda document, overrides: overrides.pop(
                'modified_cost_affine_direction_sign'
            ),
            'open-field escape approach continuity omits',
        ),
        (
            lambda document, overrides: overrides.update(
                {'operating_bounds_enabled': True}
            ),
            'must disable operating bounds',
        ),
        (
            lambda document, overrides: document['cases'][0][
                'algorithm'
            ]['ablations'].update({'recenter_enabled': True}),
            'requires affine, recenter',
        ),
        (
            lambda document, overrides: overrides.update(
                {'recoverable_navigation_enabled': True}
            ),
            'requires affine, recenter',
        ),
        (
            lambda document, overrides: overrides.update(
                {'post_recovery_guidance_enabled': True}
            ),
            'requires affine, recenter',
        ),
    ],
)
def test_schema_v8_rejects_incomplete_approach_continuity_contract(
    tmp_path,
    mutation,
    match,
):
    document = yaml.safe_load(
        V8_4_PRIMARY_VISIBLE_PROBE.read_text(encoding='utf-8')
    )
    overrides = document['frozen_profile']['launch_overrides']
    mutation(document, overrides)

    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda overrides: overrides.pop(
                'candidate_informed_fill_amplitude_scale'
            ),
            'requires candidate_informed_fill_amplitude_scale',
        ),
        (
            lambda overrides: overrides.update(
                {'candidate_informed_fill_enabled': 1}
            ),
            'must be true or false',
        ),
        (
            lambda overrides: overrides.update(
                {'candidate_cost_required_rotations': 1}
            ),
            'requires at least two selected rotations',
        ),
    ],
)
def test_schema_v8_rejects_invalid_candidate_informed_fill_contract(
    tmp_path,
    mutation,
    match,
):
    document = yaml.safe_load(
        V8_3_PRIMARY_VISIBLE_PROBE.read_text(encoding='utf-8')
    )
    mutation(document['frozen_profile']['launch_overrides'])
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('value', 'match'),
    [
        (-1, 'nonnegative integer'),
        (True, 'nonnegative integer'),
        (2, 'at least candidate_cost_required_rotations'),
    ],
)
def test_schema_v8_rejects_invalid_candidate_pretrigger_history(
    tmp_path,
    value,
    match,
):
    document = yaml.safe_load(
        V8_2_PRIMARY_VISIBLE_PROBE.read_text(encoding='utf-8')
    )
    document['frozen_profile']['launch_overrides'][
        'candidate_cost_pretrigger_rotations'
    ] = value

    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v8_rejects_pretrigger_history_outside_counted_mode(tmp_path):
    document = yaml.safe_load(
        V8_2_PRIMARY_VISIBLE_PROBE.read_text(encoding='utf-8')
    )
    document['frozen_profile']['launch_overrides'][
        'extremum_classification_mode'
    ] = 'absolute_source_score'

    with pytest.raises(
        ValueError,
        match='pretrigger rotations require counted-candidate',
    ):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc.update({'schema_version': 7}),
            'schema version 8',
        ),
        (
            lambda doc: doc['frozen_profile']['launch_overrides'].update(
                {'operating_bounds_enabled': True}
            ),
            'disable operating bounds',
        ),
        (
            lambda doc: doc['frozen_profile']['launch_overrides'].update(
                {'robust_search_epoch_reset_enabled': False}
            ),
            'search-epoch reset',
        ),
        (
            lambda doc: doc['frozen_profile']['launch_overrides'].update(
                {'convergence_confirmation_policy': 'crossing_count'}
            ),
            'require qualified dwell',
        ),
        (
            lambda doc: doc['frozen_profile']['launch_overrides'].update(
                {'known_source_count': 3}
            ),
            'known count two',
        ),
        (
            lambda doc: doc['frozen_profile']['launch_overrides'].update(
                {'gaussian_fill_max_fills': 2}
            ),
            'one fill',
        ),
        (
            lambda doc: doc['defaults'].update({'validation_world': True}),
            'no validation world',
        ),
        (
            lambda doc: doc['cases'][0]['sources'][0].update(
                {'relative_lumen_input': 0.0}
            ),
            'positive direct-input local',
        ),
        (
            lambda doc: doc['cases'][0]['sources'][1].update(
                {'relative_lumen_input': 400.0}
            ),
            'stronger positive direct-input global',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {'collision_expected': False}
            ),
            'requires simulation contacts',
        ),
        (
            lambda doc: doc['cases'][0]['success']['all_of'].remove(
                'controller_goal'
            ),
            'staged contract omits',
        ),
    ],
)
def test_schema_v8_rejects_count_topology_and_open_field_drift(
    tmp_path,
    mutation,
    match,
):
    document = _raw_document(V8_PRIMARY_VISIBLE_PROBE)
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_m4_4_controls_are_boolean_and_require_recoverable_progress(tmp_path):
    document = _v7_document()
    overrides = document['cases'][0]['algorithm']['launch_overrides']
    overrides.update({
        'adaptive_recenter_lookahead_enabled': True,
        'post_recovery_source_led_handoff_enabled': True,
    })
    run = expand_suite(_load(tmp_path, document))[0][0]

    assert run['algorithm']['launch_overrides'][
        'adaptive_recenter_lookahead_enabled'
    ] is True
    assert run['algorithm']['launch_overrides'][
        'post_recovery_source_led_handoff_enabled'
    ] is True

    document = _v7_document()
    document['cases'][0]['algorithm']['launch_overrides'][
        'adaptive_recenter_lookahead_enabled'
    ] = 1
    with pytest.raises(ValueError, match='must be true or false'):
        _load(tmp_path, document)

    document = _v7_document()
    overrides = document['cases'][0]['algorithm']['launch_overrides']
    overrides['recoverable_navigation_enabled'] = False
    overrides['post_recovery_progress_enabled'] = False
    overrides['adaptive_recenter_lookahead_enabled'] = True
    with pytest.raises(
        ValueError,
        match='adaptive_recenter_lookahead_enabled requires',
    ):
        _load(tmp_path, document)

    document = _v7_document()
    overrides = document['cases'][0]['algorithm']['launch_overrides']
    overrides['post_recovery_progress_enabled'] = False
    overrides['post_recovery_source_led_handoff_enabled'] = True
    with pytest.raises(
        ValueError,
        match='post_recovery_source_led_handoff_enabled requires',
    ):
        _load(tmp_path, document)


def test_schema_v7_rejects_non_liveness_window_and_unbounded_budget(
    tmp_path,
):
    document = _v7_document()
    document['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_liveness_max_displacement_m'
    ] = 0.60
    with pytest.raises(ValueError, match='must be below'):
        _load(tmp_path, document)

    document = _v7_document()
    document['cases'][0]['success']['staged_recovery'][
        'post_stage_a_timeout_sec'
    ] = 480.0
    with pytest.raises(
        ValueError, match='below execution.run_timeout_sec'
    ):
        _load(tmp_path, document)


def test_m4_5_controls_and_complete_staged_budget_are_strict(tmp_path):
    document = _v7_document()
    document['execution'].update({
        'run_timeout_sec': 600.0,
        'wall_timeout_sec': 780.0,
    })
    case = document['cases'][0]
    overrides = case['algorithm']['launch_overrides']
    overrides.update({
        'post_recovery_source_led_handoff_enabled': True,
        'post_recovery_source_continuity_enabled': True,
        'post_recovery_source_continuity_min_displacement_m': 0.05,
        'post_recovery_source_reversal_dot_threshold': -0.90,
        'post_recovery_source_bypass_clearance_m': 0.10,
        'controller_spawner_load_recovery_enabled': True,
    })
    case['success']['staged_recovery']['stage_a_timeout_sec'] = 480.0

    run = expand_suite(_load(tmp_path, document))[0][0]
    normalized = run['algorithm']['launch_overrides']
    staged = run['success']['staged_recovery']
    assert normalized['post_recovery_source_continuity_enabled'] is True
    assert normalized[
        'post_recovery_source_continuity_min_displacement_m'
    ] == 0.05
    assert normalized[
        'post_recovery_source_reversal_dot_threshold'
    ] == -0.90
    assert normalized['post_recovery_source_bypass_clearance_m'] == 0.10
    assert normalized['controller_spawner_load_recovery_enabled'] is True
    assert staged['stage_a_timeout_sec'] == 480.0
    assert staged['post_stage_a_timeout_sec'] == 120.0

    missing_dependency = deepcopy(document)
    del missing_dependency['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_source_led_handoff_enabled'
    ]
    with pytest.raises(
        ValueError,
        match='requires post_recovery_source_led_handoff_enabled',
    ):
        _load(tmp_path, missing_dependency)

    invalid_threshold = deepcopy(document)
    invalid_threshold['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_source_reversal_dot_threshold'
    ] = -1.01
    with pytest.raises(ValueError, match=r'must be in \[-1, 0\)'):
        _load(tmp_path, invalid_threshold)

    invalid_boolean = deepcopy(document)
    invalid_boolean['cases'][0]['algorithm']['launch_overrides'][
        'controller_spawner_load_recovery_enabled'
    ] = 1
    with pytest.raises(ValueError, match='must be true or false'):
        _load(tmp_path, invalid_boolean)

    unreserved = deepcopy(document)
    unreserved['cases'][0]['success']['staged_recovery'][
        'stage_a_timeout_sec'
    ] = 480.001
    with pytest.raises(ValueError, match='must not exceed'):
        _load(tmp_path, unreserved)


def test_m4_7_source_resume_controls_are_default_off_and_strict(tmp_path):
    document = _v7_document()
    overrides = document['cases'][0]['algorithm']['launch_overrides']
    overrides.update({
        'post_recovery_source_led_handoff_enabled': True,
        'post_recovery_source_continuity_enabled': True,
        'post_recovery_source_continuity_min_displacement_m': 0.05,
        'post_recovery_source_reversal_dot_threshold': -0.80,
        'post_recovery_source_bypass_clearance_m': 0.10,
        'post_recovery_source_resume_enabled': True,
        'post_recovery_source_resume_min_progress_m': 0.20,
    })

    run = expand_suite(_load(tmp_path, document))[0][0]
    normalized = run['algorithm']['launch_overrides']
    assert normalized['post_recovery_source_resume_enabled'] is True
    assert normalized['post_recovery_source_resume_min_progress_m'] == 0.20

    default_off = _v7_document()
    default_run = expand_suite(_load(tmp_path, default_off))[0][0]
    default_overrides = default_run['algorithm']['launch_overrides']
    assert 'post_recovery_source_resume_enabled' not in default_overrides
    assert (
        'post_recovery_source_resume_min_progress_m'
        not in default_overrides
    )

    invalid_boolean = deepcopy(document)
    invalid_boolean['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_source_resume_enabled'
    ] = 1
    with pytest.raises(ValueError, match='must be true or false'):
        _load(tmp_path, invalid_boolean)

    missing_progress_distance = deepcopy(document)
    del missing_progress_distance['cases'][0]['algorithm'][
        'launch_overrides'
    ]['post_recovery_source_resume_min_progress_m']
    with pytest.raises(
        ValueError,
        match='requires post_recovery_source_resume_min_progress_m',
    ):
        _load(tmp_path, missing_progress_distance)

    zero_progress_distance = deepcopy(document)
    zero_progress_distance['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_source_resume_min_progress_m'
    ] = 0.0
    with pytest.raises(ValueError, match='must be positive'):
        _load(tmp_path, zero_progress_distance)

    no_continuity = deepcopy(document)
    no_continuity['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_source_continuity_enabled'
    ] = False
    with pytest.raises(
        ValueError,
        match='requires post_recovery_source_continuity_enabled',
    ):
        _load(tmp_path, no_continuity)

    no_progress = deepcopy(document)
    no_progress['cases'][0]['algorithm']['launch_overrides'][
        'post_recovery_progress_enabled'
    ] = False
    with pytest.raises(
        ValueError,
        match='requires post_recovery_progress_enabled',
    ):
        _load(tmp_path, no_progress)

    no_recoverable_navigation = deepcopy(document)
    no_recoverable_navigation['cases'][0]['algorithm'][
        'launch_overrides'
    ]['recoverable_navigation_enabled'] = False
    with pytest.raises(
        ValueError,
        match='requires recoverable_navigation_enabled',
    ):
        _load(tmp_path, no_recoverable_navigation)


def test_schema_v6_supports_two_declared_traps_for_optional_three_light(
    tmp_path,
):
    document = _v6_document()
    case = document['cases'][0]
    case['sources'].insert(1, {
        'id': 'local_2',
        'x_m': 0.6888301782571618,
        'y_m': 1.662983158520316,
        'relative_lumen_input': 400.0,
        'evaluation_role': 'local_minimum',
    })
    case['sources'][0].update({
        'x_m': 1.1086554390135441,
        'y_m': 0.4592201188381077,
    })
    case['known_topology']['expected_local_minima'] = 2
    case['algorithm']['launch_overrides']['gaussian_fill_max_fills'] = 2
    case['success']['staged_recovery']['local_source_ids'] = [
        'local',
        'local_2',
    ]

    run = expand_suite(_load(tmp_path, document))[0][0]

    assert run['known_topology']['expected_local_minima'] == 2
    assert [
        placement['source_id']
        for placement in run['geometry']['local_placements']
    ] == ['local', 'local_2']
    assert run['algorithm']['launch_overrides'][
        'gaussian_fill_max_fills'
    ] == 2


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['staged_recovery'].update({
                'local_association_mode': 'invented',
            }),
            'local_association_mode',
        ),
        (
            lambda doc: doc['cases'][0]['success']['staged_recovery'].update({
                'global_closer_radius_m': 1.20,
            }),
            'strictly smaller',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({
                'boundary_recovery_release_clearance_m': 0.025,
            }),
            'must exceed',
        ),
    ],
)
def test_schema_v6_rejects_recovery_contract_drift(
    tmp_path,
    mutation,
    match,
):
    document = _v6_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v5_rejects_schema_v6_fields_without_changing_v5_output(
    tmp_path,
):
    baseline = expand_suite(_load(tmp_path, _v5_document()))[0][0]
    document = _v5_document()
    document['cases'][0]['success']['staged_recovery'][
        'local_association_mode'
    ] = 'verified_trap'

    with pytest.raises(ValueError, match='schema version 6'):
        _load(tmp_path, document)

    assert 'local_association_mode' not in (
        baseline['success']['staged_recovery']
    )
    assert 'global_closer_radius_m' not in (
        baseline['success']['staged_recovery']
    )


def test_m2_1_resolves_opt_in_correction_and_relaxed_stop():
    """Freeze the fresh detector/topology/affine correction contract."""
    runs, unsupported = expand_suite(load_suite(M2_1_CORRECTION))
    run = runs[0]

    assert unsupported == []
    assert len(runs) == 1
    assert run['algorithm']['ablations']['affine_assist_enabled'] is True
    overrides = run['algorithm']['launch_overrides']
    assert overrides['convergence_state_gating_enabled'] is True
    assert overrides['convergence_minimum_path_length_m'] == 0.20
    assert overrides['convergence_maximum_path_efficiency'] == 0.35
    assert overrides['gaussian_fill_max_fills'] == 1
    assert overrides['post_recovery_guidance_enabled'] is True
    assert overrides['post_recovery_guidance_max_sec'] == 60.0
    assert overrides['post_recovery_retry_limit'] == 3
    assert overrides['modified_cost_affine_max_age'] == 60.0
    assert run['success']['staged_recovery'][
        'global_proximity_radius_m'
    ] == 0.60
    assert run['success']['ground_truth']['proximity_radius_m'] == 0.60
    assert deterministic_case_key(run) == run['case_key']


def test_m2_2_changes_only_evidence_calibrated_efficiency_contract():
    """Preserve M2.1 inputs except its empirically contradicted cap."""
    m2_1 = expand_suite(load_suite(M2_1_CORRECTION))[0][0]
    m2_2 = expand_suite(load_suite(M2_2_CORRECTION))[0][0]

    assert m2_2['algorithm']['launch_overrides'][
        'convergence_maximum_path_efficiency'
    ] == 0.50
    ignored = {
        'case_id',
        'case_key',
        'description',
        'experiment_version',
        'scenario_sha256',
        'suite_id',
    }
    m2_1_comparable = {
        key: value for key, value in m2_1.items() if key not in ignored
    }
    m2_2_comparable = {
        key: value for key, value in m2_2.items() if key not in ignored
    }
    m2_1_comparable['algorithm'] = deepcopy(m2_1_comparable['algorithm'])
    m2_1_comparable['algorithm']['launch_overrides'] = dict(
        m2_1_comparable['algorithm']['launch_overrides']
    )
    m2_1_comparable['algorithm']['launch_overrides'][
        'convergence_maximum_path_efficiency'
    ] = 0.50
    m2_1_comparable['success'] = deepcopy(m2_1_comparable['success'])
    m2_2_comparable['success'] = deepcopy(m2_2_comparable['success'])
    m2_1_comparable['success']['controller']['contract_id'] = 'normalized'
    m2_2_comparable['success']['controller']['contract_id'] = 'normalized'
    assert m2_2_comparable == m2_1_comparable
    assert deterministic_case_key(m2_2) == m2_2['case_key']


def test_m2_3_changes_only_recovery_paths_and_operator_stop():
    """Bind the two evidence-backed M2.3 contract corrections."""
    m2_2 = expand_suite(load_suite(M2_2_CORRECTION))[0][0]
    m2_3 = expand_suite(load_suite(M2_3_CORRECTION))[0][0]

    direct_path = m2_2['success']['controller'][
        'required_state_path'
    ]
    assisted_path = [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_ASSIST',
        'RECENTER',
        'SEARCH',
    ]
    assert m2_3['success']['controller']['required_state_paths'] == [
        direct_path,
        assisted_path,
    ]
    assert m2_3['success']['ground_truth'][
        'proximity_radius_m'
    ] == 1.20
    assert m2_3['success']['staged_recovery'][
        'global_proximity_radius_m'
    ] == 1.20
    assert 'global_approach_radius_m' not in (
        m2_3['success']['staged_recovery']
    )

    ignored = {
        'case_id',
        'case_key',
        'description',
        'experiment_version',
        'scenario_sha256',
        'suite_id',
    }
    m2_2_comparable = {
        key: deepcopy(value)
        for key, value in m2_2.items()
        if key not in ignored
    }
    m2_3_comparable = {
        key: deepcopy(value)
        for key, value in m2_3.items()
        if key not in ignored
    }
    expected_success = m2_2_comparable['success']
    expected_controller = expected_success['controller']
    expected_controller['contract_id'] = 'normalized'
    expected_controller['reachability_argument'] = (
        m2_3_comparable['success']['controller'][
            'reachability_argument'
        ]
    )
    expected_controller['required_state_paths'] = [
        list(direct_path),
        assisted_path,
    ]
    expected_success['ground_truth']['proximity_radius_m'] = 1.20
    expected_success['staged_recovery'][
        'global_proximity_radius_m'
    ] = 1.20
    m2_3_comparable['success']['controller'][
        'contract_id'
    ] = 'normalized'

    assert m2_3_comparable == m2_2_comparable
    assert deterministic_case_key(m2_3) == m2_3['case_key']


def test_m3_freezes_five_position_cross_and_stricter_stop():
    """Resolve the exact prospective spatial cross without tuning inputs."""
    suite = load_suite(M3_SPATIAL_SUITE)
    runs, unsupported = expand_suite(suite)
    expected = [
        (
            'v7_m3_r1p0_a45_h25_18101',
            0.7071067811865476,
            0.7071067811865475,
            1.0,
            45.0,
        ),
        (
            'v7_m3_r1p5_a22p5_h25_18101',
            1.38581929876693,
            0.5740251485476346,
            1.5,
            22.5,
        ),
        (
            'v7_m3_r1p5_a45_h25_18101',
            1.0606601717798214,
            1.0606601717798212,
            1.5,
            45.0,
        ),
        (
            'v7_m3_r1p5_a67p5_h25_18101',
            0.5740251485476348,
            1.38581929876693,
            1.5,
            67.5,
        ),
        (
            'v7_m3_r2p0_a45_h25_18101',
            1.4142135623730951,
            1.414213562373095,
            2.0,
            45.0,
        ),
    ]

    assert suite['execution']['max_parallel_runs'] == 1
    assert suite['execution']['gazebo_gui'] is False
    assert suite['execution']['stop_on_run_failure'] is False
    assert suite['execution']['stop_on_cleanup_failure'] is True
    assert unsupported == []
    assert len(runs) == 5
    for run, (case_id, x_m, y_m, radius_m, angle_deg) in zip(
        runs, expected
    ):
        assert run['case_id'] == case_id
        assert run['acceptance_partition'] == 'validation'
        assert run['seed'] == 18101
        local = next(
            source for source in run['sources']
            if source['evaluation_role'] == 'local_minimum'
        )
        assert (local['x_m'], local['y_m']) == (x_m, y_m)
        placement = run['geometry']['local_placements'][0]
        assert placement['radius_m'] == pytest.approx(radius_m)
        assert placement['angle_deg'] == pytest.approx(angle_deg)
        staged = run['success']['staged_recovery']
        assert staged['global_proximity_radius_m'] == 1.00
        assert staged['global_approach_radius_m'] == 1.20
        assert run['success']['ground_truth'][
            'proximity_radius_m'
        ] == 1.00
        assert deterministic_case_key(run) == run['case_key']


def test_m4_freezes_visible_two_light_and_optional_three_light_inputs():
    visible_suite = load_suite(M4_VISIBLE_PROBE)
    visible, visible_unsupported = expand_suite(visible_suite)
    two_suite = load_suite(M4_TWO_LIGHT_SUITE)
    two_light, two_unsupported = expand_suite(two_suite)
    three_suite = load_suite(M4_THREE_LIGHT_PROBE)
    three_light, three_unsupported = expand_suite(three_suite)

    assert visible_unsupported == two_unsupported == three_unsupported == []
    assert visible_suite['execution']['gazebo_gui'] is True
    assert visible_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_probe'
    )
    assert [
        (run['case_id'], run['seed'])
        for run in visible
    ] == [('v7_m4_probe_r1p5_a45_h25_18201', 18201)]
    assert [
        (
            source['x_m'],
            source['y_m'],
            source['relative_lumen_input'],
        )
        for source in visible[0]['sources']
    ] == [
        (1.0606601717798214, 1.0606601717798212, 400.0),
        (3.5, 3.5, 1600.0),
    ]

    assert two_suite['execution']['gazebo_gui'] is False
    assert two_suite['execution']['runs_root'].endswith('/phase08_v7_m4')
    assert [
        (run['case_id'], run['seed'])
        for run in two_light
    ] == [
        ('v7_m4_r1p0_a45_h25_18202', 18202),
        ('v7_m4_r1p5_a22p5_h25_18202', 18202),
        ('v7_m4_r1p5_a45_h25_18202', 18202),
        ('v7_m4_r1p5_a67p5_h25_18202', 18202),
        ('v7_m4_r2p0_a45_h25_18202', 18202),
        ('v7_m4_repeat_r1p5_a45_h25_18203', 18203),
        ('v7_m4_repeat_r1p5_a45_h25_18204', 18204),
        ('v7_m4_repeat_r1p5_a45_h25_18205', 18205),
    ]
    expected_local_positions = [
        (0.7071067811865476, 0.7071067811865475),
        (1.38581929876693, 0.5740251485476346),
        (1.0606601717798214, 1.0606601717798212),
        (0.5740251485476348, 1.38581929876693),
        (1.4142135623730951, 1.414213562373095),
        (1.0606601717798214, 1.0606601717798212),
        (1.0606601717798214, 1.0606601717798212),
        (1.0606601717798214, 1.0606601717798212),
    ]
    for run, expected_local in zip(two_light, expected_local_positions):
        local, global_source = run['sources']
        assert (local['x_m'], local['y_m']) == expected_local
        assert local['relative_lumen_input'] == 400.0
        assert (
            global_source['x_m'],
            global_source['y_m'],
            global_source['relative_lumen_input'],
        ) == (3.5, 3.5, 1600.0)
        assert (
            run['start']['x_m'],
            run['start']['y_m'],
            run['start']['yaw_rad'],
        ) == (0.0, 0.0, 0.0)
    central = next(
        run for run in two_light
        if run['case_id'] == 'v7_m4_r1p5_a45_h25_18202'
    )
    repeats = [
        run for run in two_light
        if run['acceptance_partition'] == 'reproducibility'
    ]
    assert len(repeats) == 3
    assert {
        run['repeat_reference']['case_key'] for run in repeats
    } == {central['case_key']}
    for run in visible + two_light:
        overrides = run['algorithm']['launch_overrides']
        staged = run['success']['staged_recovery']
        assert overrides['wall_margin_m'] == 0.20
        assert overrides['recoverable_navigation_enabled'] is True
        assert overrides['recovery_retry_limit'] == 3
        assert overrides['recenter_max_sec'] == 60.0
        assert overrides['recenter_tolerance_m'] == 0.35
        assert overrides['modified_cost_affine_decay_rate'] == 0.05
        assert overrides['modified_cost_affine_max_age'] == 20.0
        assert overrides['post_recovery_affine_weight'] == 0.50
        assert overrides[
            'gaussian_fill_reuse_retained_samples_on_redesign'
        ] is True
        assert staged['local_association_mode'] == 'verified_trap'
        assert staged['global_proximity_radius_m'] == 1.20
        assert staged['global_closer_radius_m'] == 1.00
        assert deterministic_case_key(run) == run['case_key']

    assert three_suite['execution']['gazebo_gui'] is True
    assert len(three_light) == 1
    three = three_light[0]
    assert three['case_id'] == 'v7_m4_three_light_sequential_18206'
    assert three['seed'] == 18206
    assert three['known_topology'] == {
        'expected_global_minima': 1,
        'expected_local_minima': 2,
    }
    assert [
        source['id'] for source in three['sources']
    ] == ['local_1', 'local_2', 'global']
    assert [
        (
            source['x_m'],
            source['y_m'],
            source['relative_lumen_input'],
        )
        for source in three['sources']
    ] == [
        (1.1086554390135441, 0.4592201188381077, 400.0),
        (0.6888301782571618, 1.662983158520316, 400.0),
        (3.5, 3.5, 1600.0),
    ]
    assert three['algorithm']['launch_overrides'][
        'gaussian_fill_max_fills'
    ] == 2


def test_m4_1_is_fresh_identity_with_exact_m4_behavior_values():
    m4_suite = load_suite(M4_VISIBLE_PROBE)
    m4_runs, m4_unsupported = expand_suite(m4_suite)
    m4_1_suite = load_suite(M4_1_VISIBLE_PROBE)
    m4_1_runs, m4_1_unsupported = expand_suite(m4_1_suite)

    assert m4_unsupported == m4_1_unsupported == []
    assert len(m4_runs) == len(m4_1_runs) == 1
    m4 = deepcopy(m4_runs[0])
    m4_1 = deepcopy(m4_1_runs[0])
    assert m4_1_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_1_probe'
    )
    assert m4_1_suite['metadata']['experiment_version'] == (
        'phase08-v7-m4-1-probe'
    )
    assert (
        m4_1['case_id'],
        m4_1['seed'],
    ) == (
        'v7_m4_1_probe_r1p5_a45_h25_18207',
        18207,
    )
    assert m4_1['case_key'] == (
        'b5ac3146c6bb6b91c3d374031b3531d34c4a7506f03728c3688ae73cb7159400'
    )

    m4_execution = dict(m4_suite['execution'])
    m4_1_execution = dict(m4_1_suite['execution'])
    m4_execution.pop('runs_root')
    m4_1_execution.pop('runs_root')
    assert m4_1_execution == m4_execution

    for run in (m4, m4_1):
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            run.pop(field)
        run['success']['controller']['contract_id'] = '<fresh-identity>'
    assert m4_1 == m4


def test_m4_2_freezes_progress_guidance_probe_and_two_light_gate():
    visible_suite = load_suite(M4_2_VISIBLE_PROBE)
    visible, visible_unsupported = expand_suite(visible_suite)
    two_suite = load_suite(M4_2_TWO_LIGHT_SUITE)
    two_light, two_unsupported = expand_suite(two_suite)

    assert visible_unsupported == two_unsupported == []
    assert visible_suite['schema_version'] == 7
    assert visible_suite['execution'] == {
        'max_parallel_runs': 1,
        'gazebo_gui': True,
        'runs_root': (
            '/home/mattb/Experiments/GESC-Gaussian/runs/'
            'phase08_v7_m4_2_probe'
        ),
        'preflight_timeout_sec': 150.0,
        'run_timeout_sec': 480.0,
        'wall_timeout_sec': 660.0,
        'shutdown_grace_sec': 45.0,
        'stop_on_run_failure': False,
        'stop_on_cleanup_failure': True,
    }
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in visible
    ] == [(
        'v7_m4_2_probe_r1p5_a45_h25_18208',
        18208,
        'd4aaa0d2d7e4af20c7721d2912620fe2a0a2f9f16004c462a0299e235f2866c8',
    )]

    expected = [
        (
            'v7_m4_2_r1p0_a45_h25_18209',
            18209,
            (0.7071067811865476, 0.7071067811865475),
        ),
        (
            'v7_m4_2_r1p5_a22p5_h25_18209',
            18209,
            (1.38581929876693, 0.5740251485476346),
        ),
        (
            'v7_m4_2_r1p5_a45_h25_18209',
            18209,
            (1.0606601717798214, 1.0606601717798212),
        ),
        (
            'v7_m4_2_r1p5_a67p5_h25_18209',
            18209,
            (0.5740251485476348, 1.38581929876693),
        ),
        (
            'v7_m4_2_r2p0_a45_h25_18209',
            18209,
            (1.4142135623730951, 1.414213562373095),
        ),
        (
            'v7_m4_2_repeat_r1p5_a45_h25_18210',
            18210,
            (1.0606601717798214, 1.0606601717798212),
        ),
        (
            'v7_m4_2_repeat_r1p5_a45_h25_18211',
            18211,
            (1.0606601717798214, 1.0606601717798212),
        ),
        (
            'v7_m4_2_repeat_r1p5_a45_h25_18212',
            18212,
            (1.0606601717798214, 1.0606601717798212),
        ),
    ]
    assert two_suite['execution']['gazebo_gui'] is False
    assert two_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_2'
    )
    assert len(two_light) == len(expected)
    for run, (case_id, seed, local_position) in zip(two_light, expected):
        assert (run['case_id'], run['seed']) == (case_id, seed)
        local, global_source = run['sources']
        assert (local['x_m'], local['y_m']) == local_position
        assert local['relative_lumen_input'] == 400.0
        assert (
            global_source['x_m'],
            global_source['y_m'],
            global_source['relative_lumen_input'],
        ) == (3.5, 3.5, 1600.0)
        assert deterministic_case_key(run) == run['case_key']

    central = two_light[2]
    repeats = [
        run for run in two_light
        if run['acceptance_partition'] == 'reproducibility'
    ]
    assert len(repeats) == 3
    assert {
        run['repeat_reference']['case_key'] for run in repeats
    } == {central['case_key']}
    assert all(
        run['repeat_reference']['partition'] == 'validation'
        for run in repeats
    )

    for run in visible + two_light:
        overrides = run['algorithm']['launch_overrides']
        staged = run['success']['staged_recovery']
        assert overrides['post_recovery_progress_enabled'] is True
        assert overrides[
            'post_recovery_guidance_min_progress_m'
        ] == 0.60
        assert overrides['post_recovery_liveness_window_sec'] == 12.0
        assert overrides[
            'post_recovery_liveness_min_path_length_m'
        ] == 0.60
        assert overrides[
            'post_recovery_liveness_max_displacement_m'
        ] == 0.20
        assert overrides['post_recovery_direction_refresh_limit'] == 1
        assert overrides['robust_search_epoch_reset_enabled'] is True
        assert overrides['recenter_tolerance_m'] == 0.15
        assert overrides['post_recovery_guidance_max_sec'] == 90.0
        assert staged['post_stage_a_timeout_sec'] == 120.0
        assert staged['global_proximity_radius_m'] == 1.20
        assert staged['global_closer_radius_m'] == 1.00


def test_m4_3_changes_only_evidence_and_fresh_experiment_identity():
    m4_2_visible_suite = load_suite(M4_2_VISIBLE_PROBE)
    m4_2_visible, m4_2_visible_unsupported = expand_suite(
        m4_2_visible_suite
    )
    m4_3_visible_suite = load_suite(M4_3_VISIBLE_PROBE)
    m4_3_visible, m4_3_visible_unsupported = expand_suite(
        m4_3_visible_suite
    )
    m4_2_two_suite = load_suite(M4_2_TWO_LIGHT_SUITE)
    m4_2_two, m4_2_two_unsupported = expand_suite(m4_2_two_suite)
    m4_3_two_suite = load_suite(M4_3_TWO_LIGHT_SUITE)
    m4_3_two, m4_3_two_unsupported = expand_suite(m4_3_two_suite)

    assert (
        m4_2_visible_unsupported
        == m4_3_visible_unsupported
        == m4_2_two_unsupported
        == m4_3_two_unsupported
        == []
    )
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_3_visible
    ] == [(
        'v7_m4_3_probe_r1p5_a45_h25_18308',
        18308,
        'a5ea7f8b3d12aa01be4018ba059d12f9366f722687f95403e1c47c6929fc4655',
    )]
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_3_two
    ] == [
        (
            'v7_m4_3_r1p0_a45_h25_18309',
            18309,
            'cf5bea10bd2d904bea008d4d9f6d22cc4a026862fdbda2e45fe7b63358cd5fab',
        ),
        (
            'v7_m4_3_r1p5_a22p5_h25_18309',
            18309,
            'd58512ad9cc4488243861b89bd7120a9bce309473fa18ac0dc71966d69830540',
        ),
        (
            'v7_m4_3_r1p5_a45_h25_18309',
            18309,
            '896201a5ad6b907860270b109aaac4ff4666878c08e502d3e96c8b91fa08940a',
        ),
        (
            'v7_m4_3_r1p5_a67p5_h25_18309',
            18309,
            'a90044d4ed94d4ebd03ac6fdc78369d06f19235d1aadc86706fc6718e9e68cf0',
        ),
        (
            'v7_m4_3_r2p0_a45_h25_18309',
            18309,
            '71f003ea659ab8f0a3ae8193fa24b6a0e43b9cd65b67d5c23d3d7108e53116d2',
        ),
        (
            'v7_m4_3_repeat_r1p5_a45_h25_18310',
            18310,
            '9fd3b4a5d3c8aefaca899bd73f6a273c8d1d88c61304794ed9631aeefc54a0c4',
        ),
        (
            'v7_m4_3_repeat_r1p5_a45_h25_18311',
            18311,
            '0542aa9a360e470ab9db2533ee350276b772312996a43503329f6493f78d047b',
        ),
        (
            'v7_m4_3_repeat_r1p5_a45_h25_18312',
            18312,
            'acac96fa8659c2e8efc042292d56b3a9e2cb099bcb18fcf840ee44419c618206',
        ),
    ]

    assert m4_3_visible_suite['metadata']['experiment_version'] == (
        'phase08-v7-m4-3-probe'
    )
    assert m4_3_two_suite['metadata']['experiment_version'] == (
        'phase08-v7-m4-3'
    )
    assert m4_3_visible_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_3_probe'
    )
    assert m4_3_two_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_3'
    )

    def without_fresh_identity(run):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = '<fresh-identity>'
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = '<fresh-central-case>'
        return result

    assert without_fresh_identity(m4_3_visible[0]) == (
        without_fresh_identity(m4_2_visible[0])
    )
    assert [
        without_fresh_identity(run) for run in m4_3_two
    ] == [
        without_fresh_identity(run) for run in m4_2_two
    ]

    for previous, fresh in (
        (m4_2_visible_suite, m4_3_visible_suite),
        (m4_2_two_suite, m4_3_two_suite),
    ):
        previous_execution = dict(previous['execution'])
        fresh_execution = dict(fresh['execution'])
        previous_execution.pop('runs_root')
        fresh_execution.pop('runs_root')
        assert fresh_execution == previous_execution

    assert {
        run['repeat_reference']['case_key']
        for run in m4_3_two
        if run['acceptance_partition'] == 'reproducibility'
    } == {m4_3_two[2]['case_key']}


def test_m4_4_changes_only_two_controls_and_fresh_experiment_identity():
    m4_3_visible_suite = load_suite(M4_3_VISIBLE_PROBE)
    m4_3_visible, m4_3_visible_unsupported = expand_suite(
        m4_3_visible_suite
    )
    m4_4_visible_suite = load_suite(M4_4_VISIBLE_PROBE)
    m4_4_visible, m4_4_visible_unsupported = expand_suite(
        m4_4_visible_suite
    )
    m4_3_two_suite = load_suite(M4_3_TWO_LIGHT_SUITE)
    m4_3_two, m4_3_two_unsupported = expand_suite(m4_3_two_suite)
    m4_4_two_suite = load_suite(M4_4_TWO_LIGHT_SUITE)
    m4_4_two, m4_4_two_unsupported = expand_suite(m4_4_two_suite)

    assert (
        m4_3_visible_unsupported
        == m4_4_visible_unsupported
        == m4_3_two_unsupported
        == m4_4_two_unsupported
        == []
    )
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_4_visible
    ] == [(
        'v7_m4_4_probe_r1p5_a45_h25_18408',
        18408,
        '22ce182a7f02becf7d5f53e8193e99fdb11266ebd0fc51018ca27b8ab23aafff',
    )]
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_4_two
    ] == [
        (
            'v7_m4_4_r1p0_a45_h25_18409',
            18409,
            '699ff166fc90149cf52e528f82f064e3b4c2fd9fed338969a20966c6d46c4b86',
        ),
        (
            'v7_m4_4_r1p5_a22p5_h25_18409',
            18409,
            'eb3ff82af459346e884bfc2a8a304dfd8f0d242475efe1b36a7a83e13e527566',
        ),
        (
            'v7_m4_4_r1p5_a45_h25_18409',
            18409,
            'cacad8b96a05e2bcda31072284edeeb4dea23f62a7bf016f46527a86d8e19b8f',
        ),
        (
            'v7_m4_4_r1p5_a67p5_h25_18409',
            18409,
            '8ee88d3ef6a9a74edcf5d41ef428b4d81414c82ea15379d3a577d884cdc437eb',
        ),
        (
            'v7_m4_4_r2p0_a45_h25_18409',
            18409,
            '8697df57b64a97f070c3f0657684bec265cadf38c0bae856ac3ee2e79e1daa03',
        ),
        (
            'v7_m4_4_repeat_r1p5_a45_h25_18410',
            18410,
            '6f979d54f1cc796740003a1613d2e1f07e783590ad829e205e9a0d2efc304e4f',
        ),
        (
            'v7_m4_4_repeat_r1p5_a45_h25_18411',
            18411,
            '443625cf507b870b420c383126b414f0fd5dc12490e7b6ec83165864017fd469',
        ),
        (
            'v7_m4_4_repeat_r1p5_a45_h25_18412',
            18412,
            '6f3ae4792673cf2176e62d54319efc152902b716444042a82be11d7bfbe21260',
        ),
    ]

    def without_m4_4_delta(run):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = '<fresh-identity>'
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = '<fresh-central-case>'
        overrides = result['algorithm']['launch_overrides']
        assert overrides.pop(
            'adaptive_recenter_lookahead_enabled',
            False,
        ) is True
        assert overrides.pop(
            'post_recovery_source_led_handoff_enabled',
            False,
        ) is True
        return result

    def without_fresh_identity(run):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = '<fresh-identity>'
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = '<fresh-central-case>'
        return result

    assert without_m4_4_delta(m4_4_visible[0]) == (
        without_fresh_identity(m4_3_visible[0])
    )
    assert [
        without_m4_4_delta(run) for run in m4_4_two
    ] == [
        without_fresh_identity(run) for run in m4_3_two
    ]
    assert {
        run['repeat_reference']['case_key']
        for run in m4_4_two
        if run['acceptance_partition'] == 'reproducibility'
    } == {m4_4_two[2]['case_key']}

    assert m4_4_visible_suite['metadata']['experiment_version'] == (
        'phase08-v7-m4-4-probe'
    )
    assert m4_4_two_suite['metadata']['experiment_version'] == (
        'phase08-v7-m4-4'
    )
    assert m4_4_visible_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_4_probe'
    )
    assert m4_4_two_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_4'
    )


def test_m4_4_preserves_m4_3_v6_and_world_source_hashes():
    expected = {
        M4_3_VISIBLE_PROBE: (
            'cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658'
        ),
        M4_3_TWO_LIGHT_SUITE: (
            '37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc'
        ),
        V6_HUE_SWEEP: (
            '3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655'
        ),
        CORNER_ORIGIN_WORLD: (
            '88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf'
        ),
    }

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in expected
    } == expected


def test_m4_5_fixed_inputs_add_only_declared_controls_and_budgets():
    m4_4_suite = load_suite(M4_4_TWO_LIGHT_SUITE)
    m4_4_runs, m4_4_unsupported = expand_suite(m4_4_suite)
    visible_suite = load_suite(M4_5_VISIBLE_PROBE)
    visible, visible_unsupported = expand_suite(visible_suite)
    m4_5_suite = load_suite(M4_5_TWO_LIGHT_SUITE)
    m4_5_runs, m4_5_unsupported = expand_suite(m4_5_suite)

    assert (
        m4_4_unsupported
        == visible_unsupported
        == m4_5_unsupported
        == []
    )
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in visible
    ] == [(
        'v7_m4_5_probe_r2p0_a45_h25_18508',
        18508,
        '4058b99c8e404cdc9eea12e3ecabef5a6befc3085dc9f541faaec204745ec1d2',
    )]
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_5_runs
    ] == [
        (
            'v7_m4_5_r1p0_a45_h25_18509',
            18509,
            '55c2915ad5505f91655732677bcf27a8a00ec5541131f1cc2e402eee9243a9a0',
        ),
        (
            'v7_m4_5_r1p5_a22p5_h25_18509',
            18509,
            '5e65ee0056c18f709a7ffa98aeadd98b76895ffca4fc7651ffda3ebf3017b2a5',
        ),
        (
            'v7_m4_5_r1p5_a45_h25_18509',
            18509,
            '78fc949728c62ed94eb5a4c298f1f7548c0f41b78a595a97ca0200270e88f2a5',
        ),
        (
            'v7_m4_5_r1p5_a67p5_h25_18509',
            18509,
            '83f022dbfa5a686b80d6802ae1e573ccb5e13fb3dc0377939c085a50a05decb9',
        ),
        (
            'v7_m4_5_r2p0_a45_h25_18509',
            18509,
            'd1091f0c7dc2341c7383e37f31e8973b40075c62d761407377cb656e38627c5c',
        ),
        (
            'v7_m4_5_repeat_r1p5_a45_h25_18510',
            18510,
            'c75b44f23fc62ff1b7b96e1525c0eeb0a05cc3b26a3ac5ca831f7f59acb38ef2',
        ),
        (
            'v7_m4_5_repeat_r1p5_a45_h25_18511',
            18511,
            'be5caf65d545c0a11544db51e845f22094ced94441aaa100a4ef50d15176db86',
        ),
        (
            'v7_m4_5_repeat_r1p5_a45_h25_18512',
            18512,
            'fb97070aa6f6fe5fde17a1a1356cfde46fc3b4dfb23966aa640763c93f363161',
        ),
    ]

    for run in visible + m4_5_runs:
        overrides = run['algorithm']['launch_overrides']
        staged = run['success']['staged_recovery']
        assert overrides['post_recovery_source_continuity_enabled'] is True
        assert overrides[
            'post_recovery_source_continuity_min_displacement_m'
        ] == 0.05
        assert overrides[
            'post_recovery_source_reversal_dot_threshold'
        ] == -0.90
        assert overrides[
            'post_recovery_source_bypass_clearance_m'
        ] == 0.10
        assert overrides['controller_spawner_load_recovery_enabled'] is True
        assert staged['stage_a_timeout_sec'] == 480.0
        assert staged['post_stage_a_timeout_sec'] == 120.0
        assert staged['global_proximity_radius_m'] == 1.20
        assert staged['global_closer_radius_m'] == 1.00

    def without_m4_5_delta(run):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = '<fresh-identity>'
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = '<fresh-central-case>'
        overrides = result['algorithm']['launch_overrides']
        for name in (
            'controller_spawner_load_recovery_enabled',
            'post_recovery_source_bypass_clearance_m',
            'post_recovery_source_continuity_enabled',
            'post_recovery_source_continuity_min_displacement_m',
            'post_recovery_source_reversal_dot_threshold',
        ):
            overrides.pop(name)
        result['success']['staged_recovery'].pop('stage_a_timeout_sec')
        return result

    def without_fresh_identity(run):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = '<fresh-identity>'
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = '<fresh-central-case>'
        return result

    assert [
        without_m4_5_delta(run) for run in m4_5_runs
    ] == [
        without_fresh_identity(run) for run in m4_4_runs
    ]
    assert {
        run['repeat_reference']['case_key']
        for run in m4_5_runs
        if run['acceptance_partition'] == 'reproducibility'
    } == {m4_5_runs[2]['case_key']}

    assert visible_suite['execution']['gazebo_gui'] is True
    assert m4_5_suite['execution']['gazebo_gui'] is False
    for suite, suffix in (
        (visible_suite, '/phase08_v7_m4_5_probe'),
        (m4_5_suite, '/phase08_v7_m4_5'),
    ):
        assert suite['execution']['runs_root'].endswith(suffix)
        assert suite['execution']['run_timeout_sec'] == 600.0
        assert suite['execution']['wall_timeout_sec'] == 780.0


def test_m4_5_preserves_m4_4_m4_3_v6_and_world_source_hashes():
    expected = {
        M4_4_VISIBLE_PROBE: (
            '1559ee2ab0a7d2fa26834bc0bfd226aaa2b8d6d7dad62dcdac85ca2e83293eb4'
        ),
        M4_4_TWO_LIGHT_SUITE: (
            '78be277362ac060c7cb77c5d2215836cb914a95bd81a5ed9221f0db4bc62a188'
        ),
        M4_3_VISIBLE_PROBE: (
            'cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658'
        ),
        M4_3_TWO_LIGHT_SUITE: (
            '37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc'
        ),
        V6_HUE_SWEEP: (
            '3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655'
        ),
        CORNER_ORIGIN_WORLD: (
            '88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf'
        ),
    }

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in expected
    } == expected


def test_m4_6_fixed_inputs_change_only_identity_seed_and_threshold():
    m4_5_visible, m4_5_visible_unsupported = expand_suite(
        load_suite(M4_5_VISIBLE_PROBE)
    )
    m4_5_runs, m4_5_unsupported = expand_suite(
        load_suite(M4_5_TWO_LIGHT_SUITE)
    )
    m4_6_visible_suite = load_suite(M4_6_VISIBLE_PROBE)
    m4_6_visible, m4_6_visible_unsupported = expand_suite(
        m4_6_visible_suite
    )
    m4_6_suite = load_suite(M4_6_TWO_LIGHT_SUITE)
    m4_6_runs, m4_6_unsupported = expand_suite(m4_6_suite)

    assert (
        m4_5_visible_unsupported
        == m4_5_unsupported
        == m4_6_visible_unsupported
        == m4_6_unsupported
        == []
    )
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_6_visible
    ] == [(
        'v7_m4_6_probe_r2p0_a45_h25_18508',
        18508,
        '0adae0a552ae5f715240dcc22d1478e710711e8e82429e6752daa7c45f6045a4',
    )]
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_6_runs
    ] == [
        (
            'v7_m4_6_r1p0_a45_h25_18609',
            18609,
            '62fa7a7915cedc4dd3081c3a3e5764e22e1880e971e32c70a744d2afdbbe4d54',
        ),
        (
            'v7_m4_6_r1p5_a22p5_h25_18609',
            18609,
            '06764d07ea8620a20278594a03fcab28d14f90d6259a9290a658c1bbb2e8b5b5',
        ),
        (
            'v7_m4_6_r1p5_a45_h25_18609',
            18609,
            '2a66c20df5b62dcde548ec5e3a824fc435459f30f403851c2027f2dcf1d0ff35',
        ),
        (
            'v7_m4_6_r1p5_a67p5_h25_18609',
            18609,
            '89a1676db7d053a044d4a2e93c753a0d16ed598dd4870caa75beaee84209cdb6',
        ),
        (
            'v7_m4_6_r2p0_a45_h25_18609',
            18609,
            'd220251e34434435b41fa16cd63fb7c78508e331b4de71dac5c48f209927a906',
        ),
        (
            'v7_m4_6_repeat_r1p5_a45_h25_18610',
            18610,
            'de71b4594bd24790fd216cb7ceee74cb08ef5a4275f8a3acc49d26c94137251e',
        ),
        (
            'v7_m4_6_repeat_r1p5_a45_h25_18611',
            18611,
            'bd7613efe4ece2a6f44602aa15fee0d8187aaae167966a7c9c61941690dd836e',
        ),
        (
            'v7_m4_6_repeat_r1p5_a45_h25_18612',
            18612,
            '27dc48ef6bf727776b89d519bb41794e3eedaaf0271ad788ba3938643884c09b',
        ),
    ]

    def without_fresh_delta(run, expected_threshold):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = (
            '<fresh-identity>'
        )
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = (
                '<fresh-central-case>'
            )
        threshold = result['algorithm']['launch_overrides'].pop(
            'post_recovery_source_reversal_dot_threshold'
        )
        assert threshold == expected_threshold
        return result

    assert without_fresh_delta(
        m4_6_visible[0], -0.80
    ) == without_fresh_delta(m4_5_visible[0], -0.90)
    assert [
        without_fresh_delta(run, -0.80)
        for run in m4_6_runs
    ] == [
        without_fresh_delta(run, -0.90)
        for run in m4_5_runs
    ]
    assert {
        run['repeat_reference']['case_key']
        for run in m4_6_runs
        if run['acceptance_partition'] == 'reproducibility'
    } == {m4_6_runs[2]['case_key']}

    for run in m4_6_visible + m4_6_runs:
        overrides = run['algorithm']['launch_overrides']
        staged = run['success']['staged_recovery']
        assert overrides[
            'post_recovery_source_reversal_dot_threshold'
        ] == -0.80
        assert overrides['post_recovery_source_continuity_enabled'] is True
        assert overrides['controller_spawner_load_recovery_enabled'] is True
        assert staged['stage_a_timeout_sec'] == 480.0
        assert staged['post_stage_a_timeout_sec'] == 120.0
        assert staged['global_proximity_radius_m'] == 1.20
        assert staged['global_closer_radius_m'] == 1.00
    assert m4_6_visible_suite['execution']['gazebo_gui'] is True
    assert m4_6_suite['execution']['gazebo_gui'] is False
    assert m4_6_visible_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_6_probe'
    )
    assert m4_6_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_6'
    )


def test_m4_6_preserves_m4_5_m4_4_m4_3_v6_and_world_hashes():
    expected = {
        M4_5_VISIBLE_PROBE: (
            '3653a46c5a0ee4cf866cd257c6df2d9c18c745335f93b4fac400d0d51a313f97'
        ),
        M4_5_TWO_LIGHT_SUITE: (
            '0eecc1337371ba75d8a6ae80e766415f8bdabe2a925d0034eaa2c6f2af34e384'
        ),
        M4_4_VISIBLE_PROBE: (
            '1559ee2ab0a7d2fa26834bc0bfd226aaa2b8d6d7dad62dcdac85ca2e83293eb4'
        ),
        M4_4_TWO_LIGHT_SUITE: (
            '78be277362ac060c7cb77c5d2215836cb914a95bd81a5ed9221f0db4bc62a188'
        ),
        M4_3_VISIBLE_PROBE: (
            'cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658'
        ),
        M4_3_TWO_LIGHT_SUITE: (
            '37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc'
        ),
        V6_HUE_SWEEP: (
            '3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655'
        ),
        CORNER_ORIGIN_WORLD: (
            '88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf'
        ),
    }

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in expected
    } == expected


def test_m4_7_fixed_inputs_add_only_source_resume_corridor():
    m4_6_visible, m4_6_visible_unsupported = expand_suite(
        load_suite(M4_6_VISIBLE_PROBE)
    )
    m4_6_runs, m4_6_unsupported = expand_suite(
        load_suite(M4_6_TWO_LIGHT_SUITE)
    )
    m4_7_visible_suite = load_suite(M4_7_VISIBLE_PROBE)
    m4_7_visible, m4_7_visible_unsupported = expand_suite(
        m4_7_visible_suite
    )
    m4_7_suite = load_suite(M4_7_TWO_LIGHT_SUITE)
    m4_7_runs, m4_7_unsupported = expand_suite(m4_7_suite)

    assert (
        m4_6_visible_unsupported
        == m4_6_unsupported
        == m4_7_visible_unsupported
        == m4_7_unsupported
        == []
    )
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_7_visible
    ] == [(
        'v7_m4_7_probe_r2p0_a45_h25_18508',
        18508,
        'e48c200b54a7a9d9049b5965ef9c773b166e6672df155f0d9ccff459da83f3e8',
    )]
    assert [
        (run['case_id'], run['seed'], run['case_key'])
        for run in m4_7_runs
    ] == [
        (
            'v7_m4_7_r1p0_a45_h25_18709',
            18709,
            'd6b696af48a722e6427bca42ac04a862d50a6fa6689134b16278382326eca48b',
        ),
        (
            'v7_m4_7_r1p5_a22p5_h25_18709',
            18709,
            'bbbddb2f326b455b30db9fa90d5d1ca8cd8cc75d1b9d86c1a95fce581dfbcc87',
        ),
        (
            'v7_m4_7_r1p5_a45_h25_18709',
            18709,
            '382a4903d6128d43293ae583df072bd5f446f51fd0dc8ec76a7157f0fae9ef6b',
        ),
        (
            'v7_m4_7_r1p5_a67p5_h25_18709',
            18709,
            '1c225b8cf109a134d41818c2044ee7c6843bce69f4530bd8e821b0836fb4283a',
        ),
        (
            'v7_m4_7_r2p0_a45_h25_18709',
            18709,
            '8d98c2754cd8496fde985ac28a1f31178989e734c1021f1edfe20559df751c6d',
        ),
        (
            'v7_m4_7_repeat_r1p5_a45_h25_18710',
            18710,
            '386f6ccd6d1ddad5ad530e9cfe7a4083e66f3d9756d7f8e5fe97e8fe6fbfade6',
        ),
        (
            'v7_m4_7_repeat_r1p5_a45_h25_18711',
            18711,
            '65b61f3c8070f7cfb973424ed5aaf26e434c1dbe9761b3d7ad40d7f26b324781',
        ),
        (
            'v7_m4_7_repeat_r1p5_a45_h25_18712',
            18712,
            '593ecd33bb05cb90b065b2896707b3c1c3c2c2b858347a67cffb4c0503e9b33c',
        ),
    ]

    def without_fresh_identity(run):
        result = deepcopy(run)
        for field in (
            'case_id',
            'case_key',
            'description',
            'seed',
            'suite_id',
        ):
            result.pop(field)
        result['success']['controller']['contract_id'] = (
            '<fresh-identity>'
        )
        if result['repeat_reference'] is not None:
            result['repeat_reference']['case_key'] = (
                '<fresh-central-case>'
            )
        return result

    def without_m4_7_delta(run):
        result = without_fresh_identity(run)
        overrides = result['algorithm']['launch_overrides']
        enabled = overrides.pop('post_recovery_source_resume_enabled')
        progress = overrides.pop(
            'post_recovery_source_resume_min_progress_m'
        )
        assert enabled is True
        assert progress == 0.20
        return result

    assert without_m4_7_delta(
        m4_7_visible[0]
    ) == without_fresh_identity(m4_6_visible[0])
    assert [
        without_m4_7_delta(run)
        for run in m4_7_runs
    ] == [
        without_fresh_identity(run)
        for run in m4_6_runs
    ]
    assert {
        run['repeat_reference']['case_key']
        for run in m4_7_runs
        if run['acceptance_partition'] == 'reproducibility'
    } == {m4_7_runs[2]['case_key']}

    for run in m4_7_visible + m4_7_runs:
        overrides = run['algorithm']['launch_overrides']
        assert overrides['post_recovery_source_resume_enabled'] is True
        assert (
            overrides['post_recovery_source_resume_min_progress_m']
            == 0.20
        )
        assert (
            overrides['post_recovery_source_reversal_dot_threshold']
            == -0.80
        )

    assert m4_7_visible_suite['execution']['gazebo_gui'] is True
    assert m4_7_suite['execution']['gazebo_gui'] is False
    assert m4_7_visible_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_7_probe'
    )
    assert m4_7_suite['execution']['runs_root'].endswith(
        '/phase08_v7_m4_7'
    )
    for suite in (m4_7_visible_suite, m4_7_suite):
        assert suite['execution']['run_timeout_sec'] == 600.0
        assert suite['execution']['wall_timeout_sec'] == 780.0


def test_m4_7_preserves_m4_6_m4_5_v6_and_world_hashes():
    expected = {
        M4_6_VISIBLE_PROBE: (
            'deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11'
        ),
        M4_6_TWO_LIGHT_SUITE: (
            'c005e2c921f588b1363c231df9c0562591ea9c42671a0c8a1470dcf233a537cf'
        ),
        M4_5_VISIBLE_PROBE: (
            '3653a46c5a0ee4cf866cd257c6df2d9c18c745335f93b4fac400d0d51a313f97'
        ),
        M4_5_TWO_LIGHT_SUITE: (
            '0eecc1337371ba75d8a6ae80e766415f8bdabe2a925d0034eaa2c6f2af34e384'
        ),
        V6_HUE_SWEEP: (
            '3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655'
        ),
        CORNER_ORIGIN_WORLD: (
            '88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf'
        ),
    }

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in expected
    } == expected


def test_m4_2_preserves_m4_m4_1_v6_m3_and_world_source_hashes():
    expected = {
        M4_VISIBLE_PROBE: (
            '37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1'
        ),
        M4_1_VISIBLE_PROBE: (
            '2d881faa180c18c0b423671f12f91868e2b12d484a533909f607fef8372ca313'
        ),
        M4_TWO_LIGHT_SUITE: (
            '6e67e657b11f080a545abe6b87a8730112c350163e47f85ec6ac83ab32abb937'
        ),
        M4_THREE_LIGHT_PROBE: (
            '1a9ac4774094d43822b7d33f5eba24566e15cf745b9481ce8f25720a8e42c721'
        ),
        V6_HUE_SWEEP: (
            '3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655'
        ),
        M3_SPATIAL_SUITE: (
            '1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae'
        ),
        M4_2_VISIBLE_PROBE: (
            'e6ec6120df271afab3ae71192b601c4bcf866105a8cdaa13a10dcd94b7632973'
        ),
        M4_2_TWO_LIGHT_SUITE: (
            '8d56eb4872aafc485103f8ddd2e03a7105101fd97b8b26b532e880a9d7c84219'
        ),
        CORNER_ORIGIN_WORLD: (
            '88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf'
        ),
    }
    repeat_suite = (
        PACKAGE_ROOT
        / 'ros_esc/scenario_runner/scenarios/'
        'phase08_v6_selected_repeats.yaml'
    )
    expected[repeat_suite] = (
        '3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688'
    )

    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in expected
    } == expected


@pytest.mark.parametrize(
    ('approach_radius_m', 'match'),
    [
        (1.00, 'must be strictly greater'),
        (0.99, 'must be strictly greater'),
        (1.21, 'no greater than 1.20'),
    ],
)
def test_m3_rejects_invalid_approach_diagnostic_radius(
    tmp_path,
    approach_radius_m,
    match,
):
    """Keep the optional diagnostic outside the primary acceptance gate."""
    document = yaml.safe_load(
        M3_SPATIAL_SUITE.read_text(encoding='utf-8')
    )
    document['cases'][0]['success']['staged_recovery'][
        'global_approach_radius_m'
    ] = approach_radius_m
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_global_approach_requires_post_recovery_guidance(tmp_path):
    """Reject the optional approach report for the historical profile."""
    document = _v5_document()
    document['cases'][0]['success']['staged_recovery'][
        'global_approach_radius_m'
    ] = 1.20
    with pytest.raises(
        ValueError,
        match='requires post-recovery guidance',
    ):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'required_state_paths': []}
            ),
            'must be a non-empty list',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'][
                'required_state_paths'
            ].append(
                deepcopy(
                    doc['cases'][0]['success']['controller'][
                        'required_state_path'
                    ]
                )
            ),
            'must not contain duplicate paths',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'][
                'required_state_paths'
            ].reverse(),
            'required_state_paths\\[0\\] must equal required_state_path',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'][
                'required_state_paths'
            ][1].remove('DESIGN_OR_MERGE_FILL'),
            'unreachable transition',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'][
                'required_state_paths'
            ].__setitem__(
                1,
                ['SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD'],
            ),
            'must classify first verification as DESIGN_OR_MERGE_FILL',
        ),
        (
            lambda doc: (
                doc['cases'][0]['success']['ground_truth'].update(
                    {'proximity_radius_m': 0.59}
                ),
                doc['cases'][0]['success']['staged_recovery'].update(
                    {'global_proximity_radius_m': 0.59}
                ),
            ),
            'must be between 0.60 and 1.20',
        ),
        (
            lambda doc: (
                doc['cases'][0]['success']['ground_truth'].update(
                    {'proximity_radius_m': 1.21}
                ),
                doc['cases'][0]['success']['staged_recovery'].update(
                    {'global_proximity_radius_m': 1.21}
                ),
            ),
            'must be between 0.60 and 1.20',
        ),
        (
            lambda doc: doc['cases'][0]['success']['ground_truth'].update(
                {'proximity_radius_m': 1.19}
            ),
            'must declare the same global proximity boundary',
        ),
    ],
)
def test_m2_3_rejects_path_or_stop_contract_drift(
    tmp_path,
    mutation,
    match,
):
    """Reject ambiguous paths and radii outside the retained evidence."""
    document = yaml.safe_load(
        M2_3_CORRECTION.read_text(encoding='utf-8')
    )
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['algorithm']['ablations'].update(
                {'affine_assist_enabled': False}
            ),
            'requires algorithm.ablations.affine_assist_enabled',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'post_recovery_guidance_max_sec': 0.0}),
            'requires a positive post_recovery_guidance_max_sec',
        ),
        (
            lambda doc: doc['cases'][0]['success'][
                'staged_recovery'
            ].update({'global_proximity_radius_m': 0.35}),
            'must declare the same global proximity boundary',
        ),
    ],
)
def test_m2_1_rejects_partial_correction_contract(tmp_path, mutation, match):
    document = yaml.safe_load(M2_1_CORRECTION.read_text(encoding='utf-8'))
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['defaults'].update({
                'bounds_m': [-2.0, 2.0, -2.0, 2.0],
            }),
            'bounds_m must match',
        ),
        (
            lambda doc: doc['cases'][0]['starts'][0].update({
                'x_m': 0.1,
            }),
            'fixed geometry-profile start',
        ),
        (
            lambda doc: doc['cases'][0]['sources'][1].update({
                'x_m': 3.4,
            }),
            'fixed global point',
        ),
        (
            lambda doc: doc['cases'][0]['sources'][0].update({
                'x_m': -1.0,
                'y_m': 0.0,
            }),
            'angle is outside',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'wall_margin_m': 0.35}),
            'wall_margin_m must equal',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'gaussian_fill_max_fills': 2}),
            'must be an integer equal',
        ),
        (
            lambda doc: doc['cases'][0]['known_topology'].update({
                'expected_global_minima': 2,
            }),
            'supports exactly one declared local',
        ),
        (
            lambda doc: doc['defaults'].update({
                'simulation_contacts_enabled': False,
            }),
            'requires simulation contacts',
        ),
        (
            lambda doc: doc['cases'][0]['success'][
                'staged_recovery'
            ].update({'global_proximity_radius_m': 0.34}),
            'global proximity boundary',
        ),
    ],
)
def test_schema_v5_rejects_geometry_topology_or_stop_drift(
    tmp_path,
    mutation,
    match,
):
    """Reject any drift from the user-approved M1 launch contract."""
    document = _v5_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


@pytest.mark.parametrize(
    ('x_m', 'y_m', 'radius_m', 'angle_rad'),
    [
        (1.0, 0.0, 1.0, 0.0),
        (0.0, 2.0, 2.0, math.pi / 2.0),
    ],
)
def test_schema_v5_accepts_inclusive_sector_boundaries(
    tmp_path,
    x_m,
    y_m,
    radius_m,
    angle_rad,
):
    """Keep both axes and both radial endpoints inside the closed sector."""
    document = _v5_document()
    document['cases'][0]['sources'][0].update({
        'x_m': x_m,
        'y_m': y_m,
    })

    run = expand_suite(_load(tmp_path, document))[0][0]
    placement = run['geometry']['local_placements'][0]

    assert placement['radius_m'] == pytest.approx(radius_m)
    assert placement['angle_rad'] == pytest.approx(angle_rad)


def test_corner_origin_world_has_exact_inner_faces_and_preserves_old_world():
    """Verify shifted wall poses without changing the centered V1-V6 world."""
    assert hashlib.sha256(HISTORICAL_WORLD.read_bytes()).hexdigest() == (
        '8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef'
    )
    world = ET.parse(CORNER_ORIGIN_WORLD).getroot().find('world')
    assert world is not None
    models = {
        model.attrib['name']: model
        for model in world.findall('model')
    }
    expected = {
        'corner_origin_validation_wall_west': {
            'pose': [-0.30, 1.75],
            'size': [0.10, 4.20],
            'inner_face': -0.25,
        },
        'corner_origin_validation_wall_east': {
            'pose': [3.80, 1.75],
            'size': [0.10, 4.20],
            'inner_face': 3.75,
        },
        'corner_origin_validation_wall_south': {
            'pose': [1.75, -0.30],
            'size': [4.00, 0.10],
            'inner_face': -0.25,
        },
        'corner_origin_validation_wall_north': {
            'pose': [1.75, 3.80],
            'size': [4.00, 0.10],
            'inner_face': 3.75,
        },
    }
    for name, contract in expected.items():
        model = models[name]
        pose = [float(value) for value in model.findtext('pose').split()]
        size = [
            float(value)
            for value in model.findtext(
                'link/collision/geometry/box/size'
            ).split()
        ]
        assert pose[:2] == pytest.approx(contract['pose'])
        assert size[:2] == pytest.approx(contract['size'])
        if name.endswith(('west', 'east')):
            face = pose[0] + (
                size[0] / 2.0 if name.endswith('west')
                else -size[0] / 2.0
            )
        else:
            face = pose[1] + (
                size[1] / 2.0 if name.endswith('south')
                else -size[1] / 2.0
            )
        assert face == pytest.approx(contract['inner_face'])


def test_phase08_7_manifest_seals_all_historical_scenario_bytes_and_keys():
    """Keep every pre-M1 scenario plus v1-v4 normalized launch identity."""
    from ros_esc.scenario_runner.run_scenario import build_launch_command

    manifest = json.loads(HISTORICAL_IMMUTABILITY.read_text(encoding='utf-8'))
    scenario_root = (
        PACKAGE_ROOT / 'ros_esc/scenario_runner/scenarios'
    )
    repository_root = PACKAGE_ROOT.parents[2]
    historical_world = manifest['historical_world']
    assert hashlib.sha256(
        (repository_root / historical_world['path']).read_bytes()
    ).hexdigest() == historical_world['sha256']

    for filename, expected_sha in manifest[
        'scenario_source_sha256'
    ].items():
        assert hashlib.sha256(
            (scenario_root / filename).read_bytes()
        ).hexdigest() == expected_sha

    for filename, expected in manifest[
        'normalized_suite_digests'
    ].items():
        suite = load_suite(scenario_root / filename)
        runs, unsupported = expand_suite(suite)
        case_key_bytes = json.dumps(
            [run['case_key'] for run in runs],
            separators=(',', ':'),
        ).encode('utf-8')
        launch_bytes = json.dumps(
            [
                build_launch_command(
                    run,
                    gui=suite['execution']['gazebo_gui'],
                )
                for run in runs
            ],
            separators=(',', ':'),
        ).encode('utf-8')
        assert suite['schema_version'] == expected['schema_version']
        assert len(runs) == expected['resolved_run_count']
        assert len(unsupported) == expected['unsupported_count']
        assert hashlib.sha256(case_key_bytes).hexdigest() == expected[
            'case_keys_sha256'
        ]
        assert hashlib.sha256(launch_bytes).hexdigest() == expected[
            'launch_argv_sha256'
        ]


def test_historical_v2_activation_hash_and_case_keys_are_unchanged():
    """Keep sealed v2 YAML and normalized identities immutable under v3."""
    historical_sha = hashlib.sha256(
        HISTORICAL_V2_ACTIVATION.read_bytes()
    ).hexdigest()
    assert historical_sha == (
        'a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72'
    )
    runs, unsupported = expand_suite(load_suite(HISTORICAL_V2_ACTIVATION))
    assert unsupported == []
    assert [run['case_key'] for run in runs] == [
        'ab47b3264bcfa5da8880354c998b6152b9990be4f05e22b9da5d47ebdddd2f3e',
        '966c661dc8282b140efaf8b87ee2215b6dc7696798647a03b09d61b31cfa9603',
        '3877fb6052d7a0efd94070d6a7b6771b9726eea4fef900c4c317f6ad144cc040',
        '5f1597bda8d261e7845568f1f2246d27fc275d4426d2b2131ad6551461fce608',
        'b16f10d2ba9b8cfa62571bd5ace28014ee6fed979c4d8b91b49b238e17d5c587',
        '70bc3ab8801d66939eef679bc0934480358fa5b8c5947aebd04fbb735aaa13fd',
        'd5039ba75fcf0db9e36921b686f607406cbfcfc25a6dc924a3ce3424c84f9886',
        '86c8af432cfe9570267bc10911472c2561b1415907939bbf9d7c134009e41e08',
        '2d9d00a07b06fc59151054b7b1936eacdbfab7146c459ea6f9c6d106d2c69e93',
        'c91832a5506809efe3f1f181e0e422dd67e0f64219bd5c03497e86bf98249066',
    ]


def test_v6_hue_sweep_is_four_unassisted_two_light_cases():
    """Seal the focused Hue ratios and local-recovery evidence contract."""
    suite = load_suite(V6_HUE_SWEEP)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    assert len(runs) == 4
    assert [
        run['sources'][0]['relative_lumen_input'] for run in runs
    ] == [400.0, 800.0, 1120.0, 1360.0]
    for run in runs:
        assert len(run['sources']) == 2
        assert run['start']['yaw_rad'] == 0.0
        assert run['algorithm']['ablations']['affine_assist_enabled'] is False
        assert (
            'observed_local_recovery'
            in run['success']['all_of']
        )
        assert run['success']['local_recovery'][
            'convergence_to_local_max_m'
        ] == 0.60
