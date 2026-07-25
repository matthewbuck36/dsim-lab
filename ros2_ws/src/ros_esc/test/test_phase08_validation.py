"""Focused tests for the Phase 08 validation harness and frozen suites."""

from collections import Counter
from pathlib import Path

import yaml

from ros_esc.scenario_runner.phase08_validation import (
    _materialize_suite,
    candidate_metrics,
    CANDIDATES_PATH,
    canonical_sha256,
    evaluate_gate_set,
    EXPECTED_COUNTS,
    FACTOR_NAMES,
    FULL_MATRIX_PATH,
    load_candidates,
    select_candidate,
    suite_counts,
    TRAINING_PATH,
    validate_suite_counts,
)
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
FROZEN_PATH = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
    'phase08_frozen_parameters.yaml'
)


def _metric(value, status='valid'):
    return {
        'value': value,
        'status': status,
        'unit': None,
        'reason': None,
        'provenance': 'test',
    }


def _record(case_id='robust_pure_escape', family='escape'):
    metrics = {
        'collision': _metric(False),
        'controller_success': _metric(True),
        'simulation_ground_truth_success': _metric(True),
        'escape_attempt_count': _metric(1),
        'escape_success_count': _metric(1),
        'escape_time': _metric(10.0),
        'approximate_orbit_count': _metric(1.0),
        'fill_count': _metric(1),
        'revisit_count': _metric(0),
        'convergence_time': _metric(20.0),
        'path_length': _metric(2.0),
        'terminal_state': _metric('GOAL_HOLD'),
        'timeout': _metric(False),
    }
    return {
        'run_id': f'{case_id}-run',
        'case_id': case_id,
        'case_key': 'a' * 64,
        'family': family,
        'profile': 'robust_gaussian_v1',
        'recording_complete': True,
        'cleanup': {'passed': True},
        'classification': {'passed': True},
        'record_process': {'timed_out': False},
        'outcomes': {
            'required_state_sequence_passed': True,
            'required_events_passed': True,
        },
        'analysis_error': None,
        'analysis': {'analysis_status': 'complete', 'metrics': metrics},
    }


def test_candidate_grid_is_exact_and_hashed_deterministically():
    """Retain the authoritative C0-C8 order and five-factor boundary."""
    document = load_candidates(CANDIDATES_PATH)

    assert [item['candidate_id'] for item in document['candidates']] == [
        f'C{index}' for index in range(9)
    ]
    assert all(
        set(item['launch_overrides']) == set(FACTOR_NAMES)
        for item in document['candidates']
    )
    assert canonical_sha256({'b': 2, 'a': 1}) == canonical_sha256(
        {'a': 1, 'b': 2}
    )


def test_selected_profile_is_frozen_and_package_installed():
    """Retain the selected C8 values without changing launch defaults."""
    document = yaml.safe_load(FROZEN_PATH.read_text(encoding='utf-8'))
    selected = load_candidates()['candidates'][8]
    setup_source = (
        REPOSITORY_ROOT / 'ros2_ws/src/ros_esc/setup.py'
    ).read_text(encoding='utf-8')

    assert document['selected_candidate_id'] == 'C8'
    assert document['launch_overrides'] == selected['launch_overrides']
    assert document['sha256'] == canonical_sha256(
        document['launch_overrides']
    )
    assert 'phase08_frozen_parameters.yaml' in setup_source


def test_checked_in_suite_arithmetic_is_frozen():
    """Resolve 81 training, 12 holdout, 519 full, and 483 required runs."""
    assert suite_counts() == {**EXPECTED_COUNTS, 'unsupported': 0}
    assert validate_suite_counts()['full'] == 519

    runs, unsupported = expand_suite(load_suite(FULL_MATRIX_PATH))
    counts = Counter(run['case_id'] for run in runs)
    assert unsupported == []
    assert counts['robust_ordered_levels'] == 375
    assert counts['diagnostic_legacy_ordered_levels'] == 25
    assert counts['diagnostic_recorded_smoke'] == 2


def test_materialized_training_profile_applies_without_changing_source(
    tmp_path,
):
    """Apply candidate factors through schema-v2 frozen-profile plumbing."""
    before = TRAINING_PATH.read_bytes()
    destination = tmp_path / 'training.yaml'
    overrides = load_candidates()['candidates'][0]['launch_overrides']

    _materialize_suite(
        TRAINING_PATH,
        {'profile_id': 'test-C0', 'launch_overrides': overrides},
        destination,
    )
    suite = load_suite(destination)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    assert len(runs) == 9
    assert all(
        run['algorithm']['launch_overrides'][name] == value
        for run in runs
        for name, value in overrides.items()
    )
    assert TRAINING_PATH.read_bytes() == before


def test_candidate_eligibility_and_lexicographic_selection():
    """Reject invalid infrastructure and apply the declared tie breakers."""
    first = candidate_metrics('C1', [_record()])
    second = candidate_metrics('C2', [_record()])
    first['eligible'] = True
    second['eligible'] = True
    first['run_count'] = EXPECTED_COUNTS['training_per_candidate']
    second['run_count'] = EXPECTED_COUNTS['training_per_candidate']
    second['path_length_median_m'] = 3.0

    assert select_candidate([second, first])['candidate_id'] == 'C1'

    invalid = _record()
    invalid['analysis']['metrics']['collision'] = _metric(None, 'invalid')
    result = candidate_metrics(
        'C0',
        [invalid] * EXPECTED_COUNTS['training_per_candidate'],
    )
    assert result['eligible'] is False
    assert result['ineligible_run_ids'] == ['robust_pure_escape-run']


def test_gate_evaluation_requires_valid_evidence_and_declared_coverage():
    """Calculate every behavioral gate without converting invalid data to zero."""
    records = [
        _record('robust_pure_escape', 'escape'),
        _record('robust_assisted_escape', 'escape'),
        _record('robust_fill_merge', 'fill_merge'),
        _record('robust_recenter', 'recenter_resume'),
    ]

    result = evaluate_gate_set(records, functional_passed=True)

    assert result['passed'] is True
    assert len(result['gates']) == 11

    records[0]['analysis']['metrics']['collision'] = _metric(None, 'invalid')
    failed = evaluate_gate_set(records, functional_passed=True)
    collision_gate = next(
        gate for gate in failed['gates'] if gate['gate'] == '3_collision'
    )
    assert collision_gate['passed'] is False
