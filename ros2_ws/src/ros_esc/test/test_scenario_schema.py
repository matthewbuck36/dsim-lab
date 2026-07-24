"""Focused tests for strict Phase 06 scenario parsing and expansion."""

from copy import deepcopy
from pathlib import Path

import pytest

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


def test_checked_in_suites_validate_and_catalog_marks_gaps():
    """Validate checked-in suites and their declared unsupported gaps."""
    smoke = load_suite(SMOKE)
    catalog = load_suite(CATALOG)
    smoke_runs, smoke_unsupported = expand_suite(smoke)
    catalog_runs, catalog_unsupported = expand_suite(catalog)

    assert [run['profile'] for run in smoke_runs] == [
        'robust_gaussian_v1', 'legacy'
    ]
    assert smoke_unsupported == []
    assert len(catalog_runs) >= 20
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
        (lambda doc: doc.update({'schema_version': 2}), 'schema_version'),
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
