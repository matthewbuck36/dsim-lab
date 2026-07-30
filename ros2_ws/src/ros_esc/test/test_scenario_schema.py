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
        (lambda doc: doc.update({'schema_version': 6}), 'schema_version'),
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
