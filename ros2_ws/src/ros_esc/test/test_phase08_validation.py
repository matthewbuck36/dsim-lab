"""Focused tests for the Phase 08 validation harness and frozen suites."""

from collections import Counter
import json
from pathlib import Path

import pytest
import yaml

import ros_esc.scenario_runner.phase08_validation as phase08_validation
from ros_esc.scenario_runner.phase08_validation import (
    _materialize_suite,
    _v2_manifest_document,
    _v2_require_pass,
    candidate_metrics,
    CANDIDATES_PATH,
    canonical_sha256,
    evaluate_gate_set,
    EXPECTED_COUNTS,
    FACTOR_NAMES,
    FULL_MATRIX_PATH,
    load_candidates,
    main,
    select_candidate,
    suite_counts,
    TRAINING_PATH,
    V2_CANDIDATES,
    V2_EXPECTED_ALLOCATION,
    V2_EXPECTED_COUNTS,
    v2_allocation_bucket,
    v2_suite_counts,
    validate_suite_counts,
    wilson_interval,
)
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite
from ros_esc.supervisor_node.state_machine import (
    RotationScoreWindow,
    State,
    SupervisorStateMachine,
    TransitionInputs,
)
from ros_esc.supervisor_node.supervisor_node_script import (
    convergence_snapshot_from_confirmation,
)
from ros_esc_interfaces.msg import AlgorithmEvent, StampedFloat64MultiArray


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
FROZEN_PATH = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
    'phase08_frozen_parameters.yaml'
)
V1_REPLAY_FIXTURE = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/ros_esc/test/fixtures/'
    'phase08_v1_activation_excerpt.json'
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
            'forbidden_events_absent': True,
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


def test_v2_suite_arithmetic_and_allocations_are_exact():
    """Resolve the staged 120-run budget without reusing v1 identities."""
    assert v2_suite_counts() == V2_EXPECTED_COUNTS
    assert [item['candidate_id'] for item in V2_CANDIDATES] == [
        'V2-C0',
        'V2-C1',
        'V2-C2',
    ]
    assert sum(V2_EXPECTED_ALLOCATION['holdout'].values()) == 20
    assert sum(V2_EXPECTED_ALLOCATION['validation'].values()) == 50
    assert sum(V2_EXPECTED_ALLOCATION['reproducibility'].values()) == 10
    assert v2_allocation_bucket('fill_merge') == 'lifecycle'
    assert v2_allocation_bucket('boundary') == 'wall_corner'


def test_v2_manifest_seals_cases_without_referencing_v1_evidence(tmp_path):
    """Seal identities and source hashes without importing v1 run paths."""
    document = _v2_manifest_document(tmp_path / 'phase08_v2')
    text = json.dumps(document, sort_keys=True)

    assert document['schema_version'] == 2
    assert document['counts']['total'] == 120
    assert document['historical_v1_evidence_excluded'] is True
    assert '/runs/phase08"' not in text
    assert len(document['stages']['holdout']['runs']) == 20
    assert len(document['stages']['validation']['runs']) == 50


def test_v2_workflow_manifest_is_repeatable_and_rejects_mixed_v1(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        phase08_validation,
        'VALIDATION_ROOT',
        tmp_path / 'durable_validation',
    )
    root = tmp_path / 'evidence'

    _, first = phase08_validation._ensure_v2_workflow(root)
    _, second = phase08_validation._ensure_v2_workflow(root)

    assert first == second
    assert first['schema_version'] == 2
    assert (
        tmp_path / 'durable_validation/phase_08_v2_run_manifest.json'
    ).exists()

    mixed = tmp_path / 'mixed/workflow_state'
    mixed.mkdir(parents=True)
    (mixed / 'sweep.json').write_text('{}\n', encoding='utf-8')
    with pytest.raises(RuntimeError, match='must not be mixed'):
        phase08_validation._ensure_v2_workflow(mixed.parent)


def test_v2_stage_order_rejects_missing_or_failed_prior_state(tmp_path):
    """A later stage cannot reinterpret a missing or failed predecessor."""
    with pytest.raises(RuntimeError, match='activation must complete first'):
        _v2_require_pass(tmp_path, 'activation')

    state_root = tmp_path / 'workflow_state'
    state_root.mkdir()
    (state_root / 'v2_activation.json').write_text(
        json.dumps({'schema_version': 2, 'passed': False}),
        encoding='utf-8',
    )
    with pytest.raises(RuntimeError, match='activation failed'):
        _v2_require_pass(tmp_path, 'activation')


def test_historical_v1_execution_commands_are_retired(tmp_path):
    state_root = tmp_path / 'workflow_state'
    state_root.mkdir()
    (state_root / 'sweep.json').write_text(
        json.dumps({'schema_version': 1}),
        encoding='utf-8',
    )

    assert main([
        'sweep',
        '--operator', 'test',
        '--evidence-root', str(tmp_path),
    ]) == 2
    assert main([
        'full-pass',
        '--pass-index', '1',
        '--operator', 'test',
        '--evidence-root', str(tmp_path),
    ]) == 2


def test_wilson_interval_is_bounded_and_uses_full_denominator():
    interval = wilson_interval(63, 70)

    assert interval['rate'] == 0.9
    assert 0.80 < interval['lower'] < interval['rate']
    assert interval['rate'] < interval['upper'] < 1.0
    with pytest.raises(ValueError):
        wilson_interval(1, 0)


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


def test_v1_excerpt_replays_confirmed_activation_and_rotation_goal():
    """Replay a minimal v1 bag excerpt without treating it as v2 evidence."""
    fixture = json.loads(V1_REPLAY_FIXTURE.read_text(encoding='utf-8'))
    status_data = fixture['convergence_status']
    confirmation_data = fixture['historical_confirmation']

    fallback = StampedFloat64MultiArray()
    fallback.timestamp = status_data['timestamp']
    fallback.data = status_data['data']
    event = AlgorithmEvent()
    event.event_type = AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED
    event.source_timestamp = status_data['timestamp']
    event.source_timestamp_valid = True
    event.value_names = confirmation_data['value_names']
    event.values = confirmation_data['values']

    snapshot = convergence_snapshot_from_confirmation(event, fallback)
    assert snapshot is not None
    assert snapshot.header == 'CONVERGED_FILL_READY'
    assert list(snapshot.data) == status_data['data']

    machine = SupervisorStateMachine()
    transition = machine.step(
        0.0,
        TransitionInputs(convergence_confirmed=True),
    )
    assert transition.current == State.VERIFY_EXTREMUM

    window = RotationScoreWindow(3.0, required_rotations=2)
    for stamp, score in fixture['source_score_samples']:
        window.update(stamp, score)
    assert fixture['source_score_samples'][-1][1] < 0.95
    assert window.ready is True
    assert window.score > 0.95

    assert machine.step(
        6.0,
        TransitionInputs(
            source_score=window.score,
            source_score_valid=True,
            source_score_ready=True,
        ),
    ) is None
    transition = machine.step(
        9.0,
        TransitionInputs(
            source_score=window.score,
            source_score_valid=True,
            source_score_ready=True,
        ),
    )
    assert transition.current == State.GOAL_HOLD
