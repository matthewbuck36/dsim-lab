"""Focused tests for the Phase 08 validation harness and frozen suites."""

import base64
from collections import Counter
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

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
    v2_allocation_bucket,
    V2_CANDIDATES,
    V2_EXPECTED_ALLOCATION,
    V2_EXPECTED_COUNTS,
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
import yaml


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


def _fake_v3_truth(sources, bounds, disturbances, solver_settings=None):
    del bounds, disturbances, solver_settings
    return {
        'result_sha256': phase08_validation.canonical_sha256(sources),
    }


def _fake_v3_local_qualifications(
    aggregate_record,
    sources,
    source_ids,
    disturbances,
):
    result = json.loads(json.dumps(aggregate_record))
    result.pop('result_sha256', None)
    proof = {
        'source_ids': list(source_ids),
        'source_list_sha256': phase08_validation.canonical_sha256(sources),
        'disturbances_sha256': phase08_validation.canonical_sha256(
            disturbances
        ),
    }
    proof['result_sha256'] = phase08_validation.canonical_sha256(proof)
    result['local_branch_qualifications'] = proof
    result['result_sha256'] = phase08_validation.canonical_sha256(result)
    return result


def _generate_fast_v3_population(monkeypatch):
    monkeypatch.setattr(
        phase08_validation,
        'derive_aggregate_field_truth',
        _fake_v3_truth,
    )
    monkeypatch.setattr(
        phase08_validation,
        'validate_aggregate_field_truth',
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        'attach_local_branch_qualifications',
        _fake_v3_local_qualifications,
    )
    return phase08_validation.generate_v3_acceptance_population(
        bytes(range(32)),
    )


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


def test_v2_report_closes_early_failure_without_later_stage_evidence(
    tmp_path,
    monkeypatch,
):
    """Report a failed activation without fabricating downstream metrics."""
    validation_root = tmp_path / 'durable_validation'
    monkeypatch.setattr(
        phase08_validation,
        'VALIDATION_ROOT',
        validation_root,
    )
    evidence_root = tmp_path / 'phase08_v2'
    phase08_validation._ensure_v2_workflow(evidence_root)
    activation = {
        'schema_version': 2,
        'stage': 'activation',
        'passed': False,
        'run_count': 10,
        'integrity_pass_count': 1,
        'functional_tests': {'passed': True},
        'reasons': ['activation coverage was incomplete'],
    }
    failure = {
        'schema_version': 2,
        'stage': 'activation',
        'passed': False,
        'level_c': True,
        'later_stages_forbidden': True,
        'simulation_ready_tag_permitted': False,
    }
    phase08_validation.atomic_json(
        phase08_validation._v2_state(evidence_root, 'activation'),
        activation,
    )
    phase08_validation.atomic_json(
        phase08_validation._v2_state(evidence_root, 'failure'),
        failure,
    )

    result = phase08_validation.run_v2_report(evidence_root)

    assert result['simulation_ready'] is False
    assert result['stopped_stage'] == 'activation'
    assert result['executed_run_count'] == 10
    assert result['unique_run_count'] == 0
    assert result['confidence_intervals']['status'] == 'not_applicable'
    assert result['gates'][0]['status'] == 'evaluated'
    assert result['gates'][1]['passed'] is False
    assert all(
        gate['status'] == 'not_run' for gate in result['gates'][2:]
    )
    assert (
        validation_root / 'phase_08_v2_gate_results.json'
    ).exists()
    report = (
        validation_root / 'phase_08_v2_validation_report.md'
    ).read_text(encoding='utf-8')
    assert 'FAIL (EARLY STOP)' in report
    assert 'Not applicable: the 70-run acceptance denominator' in report
    assert main([
        'report',
        '--operator', 'test',
        '--evidence-root', str(evidence_root),
    ]) == 1


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


def test_v3_population_is_deterministic_and_has_exact_allocations(
    monkeypatch,
):
    """Precommit exactly 70 unique cases and ten distinct references."""
    first = _generate_fast_v3_population(monkeypatch)
    second = phase08_validation.generate_v3_acceptance_population(
        bytes(range(32)),
    )

    assert phase08_validation.canonical_json_bytes(first) == (
        phase08_validation.canonical_json_bytes(second)
    )
    validation = phase08_validation.validate_v3_population(first)
    assert validation['passed'] is True
    assert validation['partition_counts'] == {
        'holdout': 20,
        'reproducibility': 10,
        'validation': 50,
    }
    repeat_families = Counter(
        case['acceptance_family']
        for case in first['cases']
        if case['acceptance_partition'] == 'reproducibility'
    )
    assert repeat_families == Counter({
        family: allocation['reproducibility']
        for family, allocation
        in phase08_validation.V3_FAMILY_ALLOCATION.items()
    })


def test_v3_population_rejects_repeat_family_allocation_drift(monkeypatch):
    """The sealed repeat allocation is part of the fixed contract."""
    population = _generate_fast_v3_population(monkeypatch)
    repeat = next(
        case for case in population['cases']
        if case['acceptance_partition'] == 'reproducibility'
        and case['acceptance_family'] == 'ordered_two_source'
    )
    repeat['acceptance_family'] = 'lifecycle'

    validation = phase08_validation.validate_v3_population(population)

    assert validation['passed'] is False
    assert any(
        'reproducibility allocation drifted' in reason
        for reason in validation['reasons']
    )


def test_v3_replacement_policy_is_pre_readiness_and_bounded():
    """Never replace a behavioral failure or the same declared slot twice."""
    evidence = {
        'classification': 'infrastructure_invalid',
        'readiness_ever_true': False,
        'nonzero_command_observed': False,
        'non_search_lifecycle_observed': False,
        'active_fill_or_escape_observed': False,
        'external_startup_cause': True,
        'cleanup_passed': True,
        'classification_recorded': True,
    }
    state = phase08_validation._v3_authorize_replacement(
        'activation',
        'activation.slot-1',
        evidence,
        {},
    )
    assert state['total'] == 1
    assert state['by_stage'] == {'activation': 1}

    with pytest.raises(RuntimeError, match='second replacement'):
        phase08_validation._v3_authorize_replacement(
            'activation',
            'activation.slot-1',
            evidence,
            state,
        )
    behavioral = {**evidence, 'readiness_ever_true': True}
    with pytest.raises(RuntimeError, match='not infrastructure-replaceable'):
        phase08_validation._v3_authorize_replacement(
            'holdout',
            'holdout.slot-1',
            behavioral,
            {},
        )


def test_v3_candidate_selection_uses_declared_tie_break_order():
    """Choose only eligible candidates and then the exact lexical winner."""
    baseline = {
        'eligible': True,
        'end_to_end_success_count': 10,
        'behavior_contract_pass_count': 10,
        'local_escape_success_rate': 1.0,
        'minimum_family_success_rate': 1.0,
        'escape_time_p95_sec': 12.0,
        'escape_time_median_sec': 10.0,
        'median_orbit_count': 1.0,
        'revisit_rate': 0.0,
        'median_convergence_time_sec': 30.0,
        'median_path_length_m': 4.0,
    }
    first = {**baseline, 'candidate_id': 'V3-C0'}
    second = {
        **baseline,
        'candidate_id': 'V3-C1',
        'escape_time_p95_sec': 11.0,
    }
    ineligible = {
        **baseline,
        'candidate_id': 'V3-C2',
        'eligible': False,
        'end_to_end_success_count': 99,
    }

    assert phase08_validation.select_v3_candidate(
        [first, ineligible, second]
    )['candidate_id'] == 'V3-C1'


def _passing_v3_candidate_fixture():
    records = []
    expected_cases = []
    for index in range(10):
        record, expected = _v3_acceptance_record(
            index,
            'lifecycle',
            index,
        )
        record['acceptance_partition'] = 'development'
        record['analysis']['acceptance_partition'] = 'development'
        expected['acceptance_partition'] = 'development'
        record['success_contract'] = json.loads(json.dumps(
            expected['success']
        ))
        records.append(record)
        expected_cases.append(expected)
    return records, expected_cases


def test_v3_candidate_metrics_use_bound_analyzer_outcomes():
    """Candidate scoring uses analyzer truth and exact declared identities."""
    records, expected_cases = _passing_v3_candidate_fixture()
    records[0]['analysis']['metrics']['controller_success'] = _metric(False)
    records[0]['classification']['predicate_results'][
        'controller_goal'
    ] = False

    metrics = phase08_validation._v3_candidate_metrics(
        'V3-C0',
        records,
        expected_cases,
    )

    assert metrics['eligible'] is True
    assert metrics['identity_binding_passed'] is True
    assert metrics['end_to_end_success_count'] == 9
    assert metrics['behavior_contract_pass_count'] == 10


def test_v3_candidate_metrics_fail_closed_on_identity_or_metric_drift():
    """Do not tune from a substituted slot or unavailable applicable metric."""
    records, expected_cases = _passing_v3_candidate_fixture()
    records[0]['case_key'] = 'f' * 64
    records[1]['analysis']['metrics']['revisit_count'] = _metric(
        None,
        'unavailable',
    )

    metrics = phase08_validation._v3_candidate_metrics(
        'V3-C0',
        records,
        expected_cases,
    )

    assert metrics['eligible'] is False
    assert metrics['identity_binding_passed'] is False
    assert any('declared slots' in reason for reason in metrics['reasons'])


def test_v3_development_hard_stop_marks_later_candidates_not_run(
    tmp_path,
    monkeypatch,
):
    """A safety/evidence stop is global across the 30-run matrix."""
    root = tmp_path / 'evidence'
    qualification = phase08_validation._v3_write_state(
        root,
        'qualification',
        {'passed': True, 'repository': {}},
    )
    phase08_validation._v3_write_state(
        root,
        'activation',
        {
            'passed': True,
            'qualification_state_sha256': qualification['state_sha256'],
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_repository_snapshot',
        lambda *unused: None,
    )
    calls = []

    def materialize(unused_source, unused_profile, destination):
        destination = Path(destination)
        phase08_validation.atomic_bytes(
            destination,
            phase08_validation.V3_DEVELOPMENT_PATH.read_bytes(),
            mode=0o400,
        )
        return destination

    def execute(
        unused_suite,
        unused_operator,
        unused_root,
        stage_root,
        unused_stage,
        *,
        candidate_id,
        runtime_snapshot,
    ):
        del runtime_snapshot
        calls.append(candidate_id)
        stage_root = Path(stage_root)
        summary_path = stage_root / 'scenario_summary.yaml'
        records_path = stage_root / 'records.json'
        attempts_path = stage_root / 'attempt_records.json'
        phase08_validation.atomic_yaml(
            summary_path,
            {'summary_path': str(summary_path), 'runs': []},
        )
        phase08_validation.atomic_json(records_path, [])
        phase08_validation.atomic_json(attempts_path, [])
        return (
            {'summary_path': str(summary_path)},
            [],
            {
                'progress_sha256': 'a' * 64,
                'stopped_early_reason': 'collision evidence unavailable',
                'not_run_slot_ids': ['all-ten'],
            },
        )

    monkeypatch.setattr(
        phase08_validation,
        '_v3_materialize_profile_suite',
        materialize,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_execute_serial_slots',
        execute,
    )

    state = phase08_validation.run_v3_development('test', root)

    assert calls == ['V3-C0']
    assert state['passed'] is False
    assert state['selected_candidate'] is None
    assert state['not_run_candidates'] == ['V3-C1', 'V3-C2']
    assert any('hard stop' in reason for reason in state['reasons'])


@pytest.mark.parametrize(
    ('subcommand', 'function_name'),
    [
        ('v3-qualify', 'run_v3_qualify'),
        ('v3-activation', 'run_v3_activation'),
        ('v3-development', 'run_v3_development'),
        ('v3-freeze', 'run_v3_freeze'),
        ('v3-seal', 'run_v3_seal'),
        ('v3-holdout', 'run_v3_holdout'),
        ('v3-validation', 'run_v3_validation'),
        ('v3-reproducibility', 'run_v3_reproducibility'),
        ('v3-report', 'run_v3_report'),
    ],
)
def test_v3_cli_routes_flat_subcommands(
    tmp_path,
    monkeypatch,
    subcommand,
    function_name,
):
    """Route every v3 command before legacy v1/v2 detection."""
    observed = []

    def fake(operator, evidence_root):
        observed.append((operator, evidence_root))
        return {'passed': True}

    monkeypatch.setattr(phase08_validation, function_name, fake)

    assert main([
        subcommand,
        '--operator', 'v3-test',
        '--evidence-root', str(tmp_path),
    ]) == 0
    assert observed == [('v3-test', str(tmp_path))]


def test_v3_empirical_cli_converts_sigterm_and_restores_handler(
    tmp_path,
    monkeypatch,
):
    """Let timeout TERM unwind empirical execution as KeyboardInterrupt."""
    previous_handler = object()
    signal_state = {'handler': previous_handler}
    installed_handlers = []

    def fake_getsignal(signum):
        assert signum == phase08_validation.signal.SIGTERM
        return signal_state['handler']

    def fake_signal(signum, handler):
        assert signum == phase08_validation.signal.SIGTERM
        installed_handlers.append(handler)
        signal_state['handler'] = handler

    def fake_activation(operator, evidence_root):
        del operator, evidence_root
        signal_state['handler'](
            phase08_validation.signal.SIGTERM,
            None,
        )

    monkeypatch.setattr(
        phase08_validation.signal,
        'getsignal',
        fake_getsignal,
    )
    monkeypatch.setattr(
        phase08_validation.signal,
        'signal',
        fake_signal,
    )
    monkeypatch.setattr(
        phase08_validation,
        'run_v3_activation',
        fake_activation,
    )

    assert main([
        'v3-activation',
        '--operator', 'v3-test',
        '--evidence-root', str(tmp_path),
    ]) == 130
    assert installed_handlers == [
        phase08_validation._empirical_sigterm_handler,
        previous_handler,
    ]
    assert signal_state['handler'] is previous_handler


def test_v3_prepare_cli_routes_without_encryption_key(
    tmp_path,
    monkeypatch,
):
    """Prepare the fixed visible suite without any key material."""
    observed = []

    def fake(operator, evidence_root):
        observed.append((operator, evidence_root))
        return {'passed': True}

    monkeypatch.setattr(phase08_validation, 'run_v3_prepare', fake)

    assert main([
        'v3-prepare',
        '--operator', 'v3-test',
        '--evidence-root', str(tmp_path),
    ]) == 0
    assert observed == [('v3-test', str(tmp_path))]

    with pytest.raises(SystemExit):
        main([
            'v3-prepare',
            '--operator', 'v3-test',
            '--evidence-root', str(tmp_path),
            '--holdout-recipient', 'A1' * 20,
        ])


def test_v3_adopt_precommit_cli_routes_superseded_root(
    tmp_path,
    monkeypatch,
):
    """Route the fresh corrected lineage with its immutable predecessor."""
    observed = []

    def fake(operator, evidence_root, superseded_evidence_root):
        observed.append((
            operator,
            evidence_root,
            superseded_evidence_root,
        ))
        return {'passed': True}

    monkeypatch.setattr(
        phase08_validation,
        'run_v3_adopt_precommit',
        fake,
    )
    fresh = tmp_path / 'v3b'
    superseded = tmp_path / 'v3a'

    assert main([
        'v3-adopt-precommit',
        '--operator', 'v3-test',
        '--evidence-root', str(fresh),
        '--superseded-evidence-root', str(superseded),
    ]) == 0
    assert observed == [(
        'v3-test',
        str(fresh),
        str(superseded),
    )]


def test_v3_adopt_precommit_preserves_old_root_and_exact_population(
    tmp_path,
    monkeypatch,
):
    """Create a fresh lineage without rewriting V3A or the precommit."""
    superseded = tmp_path / 'v3a'
    superseded.mkdir()
    marker = superseded / 'immutable.bin'
    marker.write_bytes(b'original-v3a-evidence')
    original_marker = marker.read_bytes()
    fresh = tmp_path / 'v3b'
    suite_path = tmp_path / 'suite.json'
    commitment_path = tmp_path / 'commitment.json'
    suite_bytes = phase08_validation.canonical_json_bytes({
        'schema_version': 4,
        'cases': [],
    })
    suite_path.write_bytes(suite_bytes)
    commitment = {
        'schema_version': 1,
        'suite_sha256': phase08_validation.file_sha256(suite_path),
        'population_visibility': 'researcher_visible_before_activation',
        'selection_blind': False,
        'counts': {'unique': 70, 'reproducibility': 10},
        'family_counts': {},
    }
    commitment['commitment_sha256'] = (
        phase08_validation.omission_sha256(
            commitment,
            'commitment_sha256',
        )
    )
    phase08_validation.atomic_json(commitment_path, commitment)
    phase08_validation.atomic_json(
        tmp_path / 'audit.json',
        {'classification': 'instrumentation_contaminated'},
    )
    repository = {
        'commit': 'a' * 40,
        'tree': 'b' * 40,
        'clean': True,
        'input_hashes': {},
        'runtime_inputs_sha256': phase08_validation.canonical_sha256({}),
    }
    proof = {
        'kind': 'contact_probe_instrumentation_contamination',
        'superseded_evidence_root': str(superseded.resolve()),
        'correction_audit_path': str(tmp_path / 'audit.json'),
        'superseded_suite_sha256': (
            phase08_validation.file_sha256(suite_path)
        ),
        'superseded_commitment_sha256': commitment[
            'commitment_sha256'
        ],
        'policy': {
            'fresh_evidence_root': str(fresh.resolve()),
            'fresh_lineage_id': 'phase08-v3c',
        },
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_precommit_in_head',
        lambda: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: repository,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_required_free_bytes',
        lambda *unused: 1,
    )
    proof_calls = []

    def recovery_proof(*unused, **unused_keywords):
        proof_calls.append((unused, unused_keywords))
        return proof

    monkeypatch.setattr(
        phase08_validation,
        '_v3_harness_recovery_proof',
        recovery_proof,
    )

    first = phase08_validation.run_v3_adopt_precommit(
        'test',
        fresh,
        superseded,
        suite_path=suite_path,
        commitment_path=commitment_path,
        correction_path=tmp_path / 'audit.json',
    )
    second = phase08_validation.run_v3_adopt_precommit(
        'test',
        fresh,
        superseded,
        suite_path=suite_path,
        commitment_path=commitment_path,
        correction_path=tmp_path / 'audit.json',
    )

    assert first == second
    assert len(proof_calls) == 2
    assert first['passed'] is True
    assert first['suite_sha256'] == phase08_validation.file_sha256(
        suite_path
    )
    assert first['commitment_sha256'] == commitment[
        'commitment_sha256'
    ]
    assert first['lineage_id'] == 'phase08-v3b'
    assert first['recovery'] == proof
    assert marker.read_bytes() == original_marker
    transaction = phase08_validation._v3_load_prepare_transaction(
        phase08_validation._v3_prepare_transaction_path(fresh)
    )
    assert transaction['recovery'] == proof
    assert transaction['evidence_root'] == str(fresh.resolve())
    assert transaction['suite_base64'] == (
        phase08_validation.base64.b64encode(suite_bytes).decode('ascii')
    )

    with pytest.raises(RuntimeError, match='invocation drifted'):
        phase08_validation.run_v3_adopt_precommit(
            'different-operator',
            fresh,
            superseded,
            suite_path=suite_path,
            commitment_path=commitment_path,
            correction_path=tmp_path / 'audit.json',
        )

    relocated = tmp_path / 'relocated-v3b'
    fresh.rename(relocated)
    with pytest.raises(RuntimeError, match='invocation drifted'):
        phase08_validation.run_v3_adopt_precommit(
            'test',
            relocated,
            superseded,
            suite_path=suite_path,
            commitment_path=commitment_path,
            correction_path=tmp_path / 'audit.json',
        )

    drifted_suite = phase08_validation.canonical_json_bytes({
        'schema_version': 4,
        'cases': [{'case_id': 'post-v3a-change'}],
    })
    suite_path.write_bytes(drifted_suite)
    commitment['suite_sha256'] = phase08_validation.file_sha256(
        suite_path
    )
    commitment['commitment_sha256'] = (
        phase08_validation.omission_sha256(
            commitment,
            'commitment_sha256',
        )
    )
    phase08_validation.atomic_json(commitment_path, commitment)
    drifted_root = tmp_path / 'drifted-v3b'
    proof['policy']['fresh_evidence_root'] = str(
        drifted_root.resolve()
    )
    with pytest.raises(RuntimeError, match='cleartext commitment'):
        phase08_validation.run_v3_adopt_precommit(
            'test',
            drifted_root,
            superseded,
            suite_path=suite_path,
            commitment_path=commitment_path,
            correction_path=tmp_path / 'audit.json',
        )


def test_v3_adopt_precommit_creates_diagnostic_v3c_lineage(
    tmp_path,
    monkeypatch,
):
    """Adopt the fixed population without changing the closed V3B root."""
    superseded = tmp_path / 'v3b'
    superseded.mkdir()
    marker = superseded / 'immutable.bin'
    marker.write_bytes(b'original-v3b-evidence')
    original_marker = marker.read_bytes()
    fresh = tmp_path / 'v3c'
    suite_path = tmp_path / 'suite.json'
    commitment_path = tmp_path / 'commitment.json'
    suite_bytes = phase08_validation.canonical_json_bytes({
        'schema_version': 4,
        'cases': [],
    })
    suite_path.write_bytes(suite_bytes)
    commitment = {
        'schema_version': 1,
        'suite_sha256': phase08_validation.file_sha256(suite_path),
        'population_visibility': 'researcher_visible_before_activation',
        'selection_blind': False,
        'counts': {'unique': 70, 'reproducibility': 10},
        'family_counts': {},
    }
    commitment['commitment_sha256'] = (
        phase08_validation.omission_sha256(
            commitment,
            'commitment_sha256',
        )
    )
    phase08_validation.atomic_json(commitment_path, commitment)
    input_hashes = {
        path: f'{index + 1:064x}'
        for index, path in enumerate(
            phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        )
    }
    input_hashes['ros2_ws/src/ros_esc/package.xml'] = 'f' * 64
    repository = {
        'commit': 'c' * 40,
        'tree': 'd' * 40,
        'clean': True,
        'input_hashes': input_hashes,
        'runtime_inputs_sha256': phase08_validation.canonical_sha256(
            input_hashes
        ),
    }
    proof = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': str(superseded.resolve()),
        'correction_audit_path': str(tmp_path / 'audit.json'),
        'superseded_suite_sha256': phase08_validation.file_sha256(
            suite_path
        ),
        'superseded_commitment_sha256': commitment[
            'commitment_sha256'
        ],
        'policy': {
            'fresh_evidence_root': str(fresh.resolve()),
            'fresh_lineage_id': 'phase08-v3c',
        },
    }
    proof['baseline_runtime_projection'] = (
        phase08_validation._v3_runtime_input_projection(repository)
    )
    proof['allowed_runtime_correction_sha256'] = {
        path: input_hashes[path]
        for path in (
            phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        )
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_precommit_in_head',
        lambda: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: repository,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_required_free_bytes',
        lambda *unused: 1,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_adoption_recovery_proof',
        lambda *unused, **unused_keywords: proof,
    )

    state = phase08_validation.run_v3_adopt_precommit(
        'test',
        fresh,
        superseded,
        suite_path=suite_path,
        commitment_path=commitment_path,
    )

    assert state['passed'] is True
    assert state['lineage_id'] == 'phase08-v3c'
    assert state['recovery'] == proof
    assert state['suite_sha256'] == phase08_validation.file_sha256(
        suite_path
    )
    assert marker.read_bytes() == original_marker
    transaction = phase08_validation._v3_load_prepare_transaction(
        phase08_validation._v3_prepare_transaction_path(fresh)
    )
    assert transaction['experiment_version'] == 'phase08-v3c'
    assert transaction['recovery'] == proof
    drifted = dict(transaction)
    drifted['experiment_version'] = 'phase08-v3b'
    with pytest.raises(RuntimeError, match='invocation drifted'):
        phase08_validation._v3_adoption_matches_invocation(
            drifted,
            'test',
            fresh,
            superseded,
        )


def test_v3_recovery_dispatcher_preserves_all_lineage_kinds(
    monkeypatch,
):
    """Revalidate the exact proof owner selected by each recovery kind."""
    prelaunch_path = Path('/tmp/prelaunch.json')
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRELAUNCH_CORRECTION_PATH',
        prelaunch_path,
    )
    contact = {
        'kind': 'contact_probe_instrumentation_contamination',
        'superseded_evidence_root': '/tmp/v3a',
        'correction_audit_path': '/tmp/contact.json',
    }
    diagnostic = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': '/tmp/v3b',
        'correction_audit_path': '/tmp/diagnostic.json',
        'policy': {'fresh_lineage_id': 'phase08-v3c'},
    }
    prelaunch = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': '/tmp/v3b',
        'failed_evidence_root': '/tmp/phase08_v3c',
        'correction_audit_path': str(prelaunch_path),
        'retained_v3c': {},
        'retained_root_manifests': {},
        'prelaunch_failure': {},
        'nested_recovery': {},
        'policy': {'fresh_lineage_id': 'phase08-v3d'},
    }
    observed = []
    monkeypatch.setattr(
        phase08_validation,
        '_v3_harness_recovery_proof',
        lambda root, correction_path: (
            observed.append(('contact', root, str(correction_path)))
            or contact
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_hard_stop_policy_recovery_proof',
        lambda root, correction_path: (
            observed.append(('diagnostic', root, str(correction_path)))
            or diagnostic
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_prelaunch_failure_recovery_proof',
        lambda root, correction_path: (
            observed.append(('prelaunch', root, str(correction_path)))
            or prelaunch
        ),
    )

    assert phase08_validation._v3_revalidate_recovery(contact) == contact
    assert (
        phase08_validation._v3_revalidate_recovery(diagnostic)
        == diagnostic
    )
    assert (
        phase08_validation._v3_revalidate_recovery(prelaunch)
        == prelaunch
    )
    assert phase08_validation._v3_recovery_fresh_lineage_id(
        contact
    ) == 'phase08-v3b'
    assert phase08_validation._v3_recovery_fresh_lineage_id(
        diagnostic
    ) == 'phase08-v3c'
    assert phase08_validation._v3_recovery_fresh_lineage_id(
        prelaunch
    ) == 'phase08-v3d'
    assert observed == [
        ('contact', '/tmp/v3a', '/tmp/contact.json'),
        ('diagnostic', '/tmp/v3b', '/tmp/diagnostic.json'),
        ('prelaunch', '/tmp/v3b', '/tmp/prelaunch.json'),
    ]
    with pytest.raises(RuntimeError, match='unsupported v3 recovery'):
        phase08_validation._v3_recovery_fresh_lineage_id({
            'kind': 'unknown',
        })


def test_v3_adoption_recovery_selects_v3d_default_and_explicit(
    tmp_path,
    monkeypatch,
):
    """Route V3D only from its classified audit and V3B default."""
    prelaunch_path = tmp_path / 'prelaunch.json'
    diagnostic_path = tmp_path / 'diagnostic.json'
    contact_path = tmp_path / 'contact.json'
    unknown_path = tmp_path / 'unknown.json'
    for path, classification in (
        (prelaunch_path, 'prelaunch_failure_recovery'),
        (diagnostic_path, 'behavioral_miss_diagnostic_completion'),
        (contact_path, 'instrumentation_contaminated'),
        (unknown_path, 'not_a_recovery_contract'),
    ):
        phase08_validation.atomic_json(
            path,
            {'classification': classification},
        )
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRELAUNCH_CORRECTION_PATH',
        prelaunch_path,
    )
    observed = []
    monkeypatch.setattr(
        phase08_validation,
        '_v3_prelaunch_failure_recovery_proof',
        lambda root, correction_path=prelaunch_path: (
            observed.append(('prelaunch', str(root), Path(correction_path)))
            or {'proof': 'prelaunch'}
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_hard_stop_policy_recovery_proof',
        lambda root, correction_path=diagnostic_path: (
            observed.append(('diagnostic', str(root), Path(correction_path)))
            or {'proof': 'diagnostic'}
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_harness_recovery_proof',
        lambda root, correction_path=contact_path: (
            observed.append(('contact', str(root), Path(correction_path)))
            or {'proof': 'contact'}
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_state',
        lambda *unused, **unused_keywords: {
            'lineage_id': 'phase08-v3b',
        },
    )

    assert phase08_validation._v3_adoption_recovery_proof(
        '/tmp/v3b',
    ) == {'proof': 'prelaunch'}
    assert phase08_validation._v3_adoption_recovery_proof(
        '/tmp/v3b',
        correction_path=prelaunch_path,
    ) == {'proof': 'prelaunch'}
    assert phase08_validation._v3_adoption_recovery_proof(
        '/tmp/v3b',
        correction_path=diagnostic_path,
    ) == {'proof': 'diagnostic'}
    assert phase08_validation._v3_adoption_recovery_proof(
        '/tmp/v3a',
        correction_path=contact_path,
    ) == {'proof': 'contact'}
    with pytest.raises(
        RuntimeError,
        match='unsupported v3 correction-audit classification',
    ):
        phase08_validation._v3_adoption_recovery_proof(
            '/tmp/v3b',
            correction_path=unknown_path,
        )
    assert observed == [
        ('prelaunch', '/tmp/v3b', prelaunch_path),
        ('prelaunch', '/tmp/v3b', prelaunch_path),
        ('diagnostic', '/tmp/v3b', diagnostic_path),
        ('contact', '/tmp/v3a', contact_path),
    ]


def _v3d_prelaunch_fixture(
    tmp_path,
    monkeypatch,
    *,
    activation_operator='test',
    nested_fresh_evidence_root=None,
    nested_suite_sha256=None,
    nested_commitment_sha256=None,
    qualification_activation_contract=None,
    transaction_suite_bytes=None,
):
    """Build a minimal hash-valid V3B -> V3C -> V3D recovery chain."""
    v3a_root = tmp_path / 'phase08_v3'
    v3b_root = tmp_path / 'v3b'
    v3c_root = tmp_path / 'phase08_v3c'
    v3d_root = tmp_path / 'phase08_v3d'
    v3a_marker = v3a_root / 'immutable.txt'
    v3a_marker.parent.mkdir(parents=True)
    v3a_marker.write_text('retained V3A\n', encoding='utf-8')
    old_audit_path = tmp_path / 'v3b-audit.json'
    new_audit_path = tmp_path / 'v3c-prelaunch-audit.json'
    old_audit = {'schema_version': 1, 'classification': 'retained'}
    old_audit['correction_sha256'] = (
        phase08_validation.omission_sha256(
            old_audit,
            'correction_sha256',
        )
    )
    phase08_validation.atomic_json(old_audit_path, old_audit)
    monkeypatch.setattr(
        phase08_validation,
        'V3_HARD_STOP_CORRECTION_PATH',
        old_audit_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRELAUNCH_CORRECTION_PATH',
        new_audit_path,
    )

    suite_path = tmp_path / 'phase08_v3_acceptance_suite.json'
    suite_path.write_bytes(b'{\"cases\":[],\"schema_version\":4}\\n')
    suite_sha256 = phase08_validation.file_sha256(suite_path)
    commitment_path = tmp_path / 'phase_08_v3_suite_commitment.json'
    commitment = {
        'schema_version': 1,
        'suite_sha256': suite_sha256,
    }
    commitment['commitment_sha256'] = (
        phase08_validation.omission_sha256(
            commitment,
            'commitment_sha256',
        )
    )
    phase08_validation.atomic_json(commitment_path, commitment)
    commitment_sha256 = commitment['commitment_sha256']
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRECOMMITTED_SUITE_PATH',
        suite_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_COMMITMENT_PATH',
        commitment_path,
    )
    v3b_prepare = phase08_validation._v3_write_state(
        v3b_root,
        'prepare',
        {
            'passed': True,
            'lineage_id': 'phase08-v3b',
            'suite_sha256': suite_sha256,
            'commitment_sha256': commitment_sha256,
        },
    )
    v3b_qualification = phase08_validation._v3_write_state(
        v3b_root,
        'qualification',
        {
            'passed': True,
            'lineage_id': 'phase08-v3b',
            'prepare_state_sha256': v3b_prepare['state_sha256'],
        },
    )
    v3b_activation = phase08_validation._v3_write_state(
        v3b_root,
        'activation',
        {
            'passed': False,
            'qualification_state_sha256': (
                v3b_qualification['state_sha256']
            ),
        },
    )
    baseline_hashes = {
        path: phase08_validation.file_sha256(
            phase08_validation.REPOSITORY_ROOT / path
        )
        for path in (
            phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        )
    }
    baseline_hashes['ros2_ws/src/ros_esc/package.xml'] = (
        phase08_validation.file_sha256(
            phase08_validation.REPOSITORY_ROOT
            / 'ros2_ws/src/ros_esc/package.xml'
        )
    )
    repository = {
        'commit': 'c' * 40,
        'tree': 'd' * 40,
        'clean': True,
        'input_hashes': baseline_hashes,
        'runtime_inputs_sha256': phase08_validation.canonical_sha256(
            baseline_hashes
        ),
    }
    nested_recovery = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': str(v3b_root.resolve()),
        'superseded_prepare_state_sha256': (
            v3b_prepare['state_sha256']
        ),
        'superseded_qualification_state_sha256': (
            v3b_qualification['state_sha256']
        ),
        'superseded_activation_state_sha256': (
            v3b_activation['state_sha256']
        ),
        'superseded_suite_sha256': (
            suite_sha256
            if nested_suite_sha256 is None
            else nested_suite_sha256
        ),
        'superseded_commitment_sha256': (
            commitment_sha256
            if nested_commitment_sha256 is None
            else nested_commitment_sha256
        ),
        'correction_audit_path': str(old_audit_path.resolve()),
        'correction_audit_sha256': old_audit['correction_sha256'],
        'run_id': 'retained-v3b-run',
        'carried_record': {
            'case_id': (
                phase08_validation.V3_DIAGNOSTIC_CARRIED_CASE_ID
            ),
            'record_path': '/immutable/v3b/record.json',
            'record_sha256': 'e' * 64,
            'run_id': 'retained-v3b-run',
            'source_lineage_id': 'phase08-v3b',
        },
        'run_directory_manifest': {
            'root': '/immutable/v3b/run',
            'file_count': 1,
            'input_hashes': {'bag.db3': 'f' * 64},
            'manifest_sha256': '1' * 64,
        },
        'composite_activation': {
            'carried_record_count': 1,
            'new_execution_count': 9,
            'composite_slot_count': 10,
            'terminal_activation_passed': False,
            'execute_case_ids': list(
                phase08_validation.V3_DIAGNOSTIC_EXECUTION_CASE_IDS
            ),
        },
        'baseline_runtime_projection': (
            phase08_validation._v3_runtime_input_projection(repository)
        ),
        'allowed_runtime_correction_sha256': {
            path: baseline_hashes[path]
            for path in (
                phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
            )
        },
        'activation_invocation_contract': {'contract': 'unchanged'},
        'execution_commit': '2' * 40,
        'original_artifacts': {'retained': '3' * 64},
        'behavioral_result': {'status': 'failed'},
        'retained_evidence_audit': {'path': 'retained'},
        'nested_recovery': {
            'kind': 'contact',
            'superseded_evidence_root': str(v3a_root.resolve()),
        },
        'policy': {
            'fresh_lineage_id': 'phase08-v3c',
            'fresh_evidence_root': str(Path(
                v3c_root
                if nested_fresh_evidence_root is None
                else nested_fresh_evidence_root
            ).resolve()),
        },
    }
    transaction = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3c',
        'operator': 'test',
        'evidence_root': str(v3c_root.resolve()),
        'suite_path': str(suite_path.resolve()),
        'commitment_path': str(commitment_path.resolve()),
        'suite_base64': base64.b64encode(
            suite_path.read_bytes()
            if transaction_suite_bytes is None
            else transaction_suite_bytes
        ).decode('ascii'),
        'commitment': commitment,
        'commitment_sha256': commitment_sha256,
        'repository': repository,
        'processes_before': [],
        'recovery': nested_recovery,
    }
    transaction['transaction_sha256'] = (
        phase08_validation.omission_sha256(
            transaction,
            'transaction_sha256',
        )
    )
    phase08_validation.atomic_json(
        phase08_validation._v3_prepare_transaction_path(v3c_root),
        transaction,
    )
    v3c_prepare = phase08_validation._v3_write_state(
        v3c_root,
        'prepare',
        {
            'passed': True,
            'operator': 'test',
            'lineage_id': 'phase08-v3c',
            'suite_sha256': suite_sha256,
            'commitment_sha256': commitment_sha256,
            'suite_path': str(suite_path.resolve()),
            'commitment_path': str(commitment_path.resolve()),
            'repository': repository,
            'processes_before': [],
            'transaction_path': str(
                phase08_validation._v3_prepare_transaction_path(
                    v3c_root
                ).resolve()
            ),
            'transaction_sha256': transaction[
                'transaction_sha256'
            ],
            'recovery': nested_recovery,
        },
    )
    v3c_qualification = phase08_validation._v3_write_state(
        v3c_root,
        'qualification',
        {
            'passed': True,
            'operator': 'test',
            'lineage_id': 'phase08-v3c',
            'prepare_state_sha256': v3c_prepare['state_sha256'],
            'repository': repository,
            'activation_invocation_contract': (
                {'contract': 'unchanged'}
                if qualification_activation_contract is None
                else qualification_activation_contract
            ),
            'processes_before': [],
            'processes_after': [],
            'recovery_validation': {
                'passed': True,
                'recovery_sha256': (
                    phase08_validation.canonical_sha256(
                        nested_recovery
                    )
                ),
            },
        },
    )

    activation_root = v3c_root / 'activation'
    resolved_suite_path = activation_root / 'resolved_suite.yaml'
    phase08_validation.atomic_yaml(
        resolved_suite_path,
        {'schema_version': 4, 'cases': []},
    )
    attempt_root = (
        activation_root
        / 'attempts/002_v3a_below_target_fill/attempt_01'
    )
    execution_error_path = attempt_root / 'execution_error.json'
    phase08_validation.atomic_json(
        execution_error_path,
        {
            'schema_version': 1,
            'slot_id': 'activation.v3a_below_target_fill',
            'attempt_index': 1,
            'error': 'AttributeError: __enter__',
        },
    )
    attempt_summary_path = attempt_root / 'scenario_summary.yaml'
    attempt_record_path = attempt_root / 'record.json'
    attempt_runs_root = attempt_root / 'runs'
    carried_record = {
        'case_id': phase08_validation.V3_DIAGNOSTIC_CARRIED_CASE_ID,
        'record_path': '/immutable/v3b/record.json',
        'record_sha256': 'e' * 64,
        'run_id': 'retained-v3b-run',
        'source_lineage_id': 'phase08-v3b',
        'source_evidence_root': str(v3b_root.resolve()),
        'source_activation_state_sha256': (
            v3b_activation['state_sha256']
        ),
        'run_directory_manifest': dict(
            nested_recovery['run_directory_manifest']
        ),
        'disposition': 'carried_immutable_behavioral_failure',
        'rerun': False,
    }
    execute_case_ids = list(
        phase08_validation.V3_DIAGNOSTIC_EXECUTION_CASE_IDS
    )
    stopped_reason = (
        'activation.v3a_below_target_fill: execution error'
    )
    progress = phase08_validation._v3_write_progress(
        activation_root,
        {
            'schema_version': 1,
            'experiment_version': 'phase08-v3',
            'stage': 'activation',
            'candidate_id': None,
            'suite_path': str(resolved_suite_path.resolve()),
            'suite_sha256': phase08_validation.file_sha256(
                resolved_suite_path
            ),
            'slot_ids': [
                phase08_validation.V3_DIAGNOSTIC_CARRIED_CASE_ID,
                *execute_case_ids,
            ],
            'attempts': [{
                'attempt_index': 1,
                'case_id': 'v3a_below_target_fill',
                'error_path': str(execution_error_path),
                'error_sha256': phase08_validation.file_sha256(
                    execution_error_path
                ),
                'expected_error_path': str(execution_error_path),
                'expected_record_path': str(attempt_record_path),
                'expected_summary_path': str(attempt_summary_path),
                'outcome': 'execution_error',
                'record_path': None,
                'record_sha256': None,
                'slot_id': 'activation.v3a_below_target_fill',
                'summary_path': None,
                'summary_sha256': None,
            }],
            'carried_records': [carried_record],
            'carried_count': 1,
            'newly_executed_count': 0,
            'carried_record_count': 1,
            'new_execution_count': 0,
            'required_execution_case_ids': execute_case_ids,
            'ambiguous_interrupted_dispatch_case_ids': [],
            'final_record_paths': {
                phase08_validation.V3_DIAGNOSTIC_CARRIED_CASE_ID: (
                    carried_record['record_path']
                ),
            },
            'stopped_early_reason': stopped_reason,
            'not_run_slot_ids': execute_case_ids,
        },
    )
    records_path = activation_root / 'records.json'
    attempt_records_path = activation_root / 'attempt_records.json'
    scenario_summary_path = activation_root / 'scenario_summary.yaml'
    phase08_validation.atomic_json(
        records_path,
        [{
            'schema_version': 1,
            'case_id': (
                phase08_validation.V3_DIAGNOSTIC_CARRIED_CASE_ID
            ),
            'disposition': 'carried_immutable_behavioral_failure',
            'carried_record': carried_record,
        }],
    )
    phase08_validation.atomic_json(attempt_records_path, [])
    phase08_validation.atomic_yaml(
        scenario_summary_path,
        {
            'schema_version': 1,
            'source_path': str(resolved_suite_path.resolve()),
            'declared_slot_count': 10,
            'completed_slot_count': 1,
            'attempted_slot_count': 1,
            'ambiguous_interrupted_dispatch_case_ids': [],
            'carried_record_count': 1,
            'new_execution_count': 0,
            'carried_count': 1,
            'newly_executed_count': 0,
            'carried_records': [carried_record],
            'stopped_early_reason': stopped_reason,
            'attempt_count': 1,
            'runs': [],
        },
    )
    v3c_activation = phase08_validation._v3_write_state(
        v3c_root,
        'activation',
        {
            'passed': False,
            'operator': activation_operator,
            'qualification_state_sha256': (
                v3c_qualification['state_sha256']
            ),
            'run_count': 1,
            'composite_slot_count': 1,
            'carried_record_count': 1,
            'new_execution_count': 0,
            'carried_count': 1,
            'newly_executed_count': 0,
            'pass_eligible': False,
            'diagnostic_completion': True,
            'integrity_pass_count': 0,
            'contract_pass_count': 0,
            'scenario_summary_path': str(scenario_summary_path),
            'scenario_summary_sha256': (
                phase08_validation.file_sha256(
                    scenario_summary_path
                )
            ),
            'records_path': str(records_path),
            'records_sha256': phase08_validation.file_sha256(
                records_path
            ),
            'attempt_records_sha256': (
                phase08_validation.file_sha256(attempt_records_path)
            ),
            'progress_sha256': progress['progress_sha256'],
            'stopped_early_reason': stopped_reason,
            'ambiguous_interrupted_dispatch_case_ids': [],
            'not_run_slot_ids': execute_case_ids,
            'replacement_state_sha256': None,
        },
    )
    symlink_root = v3c_root / 'qualification/isolated_build/logs'
    original_build_root = symlink_root / 'build_original'
    alternate_build_root = symlink_root / 'build_alternate'
    original_build_root.mkdir(parents=True)
    alternate_build_root.mkdir()
    latest_build_link = symlink_root / 'latest_build'
    latest_build_link.symlink_to(
        original_build_root.name,
        target_is_directory=True,
    )
    (symlink_root / 'latest').symlink_to(
        latest_build_link.name,
        target_is_directory=True,
    )
    artifact_paths = {
        'prepare_state_file_sha256': (
            phase08_validation._v3_state_path(v3c_root, 'prepare')
        ),
        'qualification_state_file_sha256': (
            phase08_validation._v3_state_path(
                v3c_root, 'qualification'
            )
        ),
        'activation_state_file_sha256': (
            phase08_validation._v3_state_path(v3c_root, 'activation')
        ),
        'prepare_transaction_file_sha256': (
            phase08_validation._v3_prepare_transaction_path(v3c_root)
        ),
        'activation_progress_file_sha256': (
            activation_root / 'progress.json'
        ),
        'activation_records_file_sha256': records_path,
        'activation_attempt_records_file_sha256': (
            attempt_records_path
        ),
        'activation_scenario_summary_file_sha256': (
            scenario_summary_path
        ),
        'activation_resolved_suite_file_sha256': resolved_suite_path,
        'execution_error_file_sha256': execution_error_path,
    }
    allowed_hashes = {
        path: phase08_validation.file_sha256(
            phase08_validation.REPOSITORY_ROOT / path
        )
        for path in (
            phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        )
    }
    policy = {
        'hard_stop_policy': (
            'pure_applicability_partial_is_behavioral_miss'
        ),
        'fresh_lineage_id': 'phase08-v3d',
        'fresh_evidence_root': str(v3d_root.resolve()),
        'carry_superseded_behavioral_failure': True,
        'carry_failed_slot_byte_identically': True,
        'execute_only_never_run_activation_cases': True,
        'composite_activation_forced_fail': True,
        'rerun_all_activation_cases': False,
        'rerun_carried_case': False,
        'm4_prohibited': True,
        'phase08_v3_terminal_failure_required': True,
        'reuse_precommitted_population_byte_identically': True,
        'activation_cases_changed': False,
        'analyzer_output_changed': False,
        'behavior_contract_changed': False,
        'collision_gate_changed': False,
        'final_record_integrity_gate_changed': False,
        'allowed_runtime_correction_sha256': allowed_hashes,
        'preserve_failed_v3c_root': True,
        'prelaunch_failure_not_behavioral_attempt': True,
        'rerun_v3c_execution_error': False,
    }
    audit = {
        'schema_version': 1,
        'classification': 'prelaunch_failure_recovery',
        'superseded_evidence_root': str(v3b_root.resolve()),
        'failed_evidence_root': str(v3c_root.resolve()),
        'retained_root_manifests': {
            'v3a': phase08_validation._v3_compact_root_manifest(
                v3a_root
            ),
            'v3b': phase08_validation._v3_compact_root_manifest(
                v3b_root
            ),
            'v3c': phase08_validation._v3_compact_root_manifest(
                v3c_root
            ),
        },
        'retained_v3c': {
            'prepare_state_sha256': v3c_prepare['state_sha256'],
            'qualification_state_sha256': (
                v3c_qualification['state_sha256']
            ),
            'activation_state_sha256': (
                v3c_activation['state_sha256']
            ),
            'activation_progress_sha256': progress['progress_sha256'],
            'nested_v3b_recovery_sha256': (
                phase08_validation.canonical_sha256(nested_recovery)
            ),
            'original_artifacts': {
                field: phase08_validation.file_sha256(path)
                for field, path in artifact_paths.items()
            },
        },
        'prelaunch_failure': {
            'case_id': 'v3a_below_target_fill',
            'slot_id': 'activation.v3a_below_target_fill',
            'attempt_index': 1,
            'outcome': 'execution_error',
            'error': 'AttributeError: __enter__',
            'execution_error_path': str(execution_error_path),
            'expected_summary_path': str(attempt_summary_path),
            'expected_record_path': str(attempt_record_path),
            'expected_runs_root': str(attempt_runs_root),
            'new_execution_count': 0,
            'ambiguous_interrupted_dispatch_case_ids': [],
            'not_run_slot_ids': execute_case_ids,
        },
        'composite_activation': dict(
            nested_recovery['composite_activation']
        ),
        'correction': policy,
    }
    audit['correction_sha256'] = (
        phase08_validation.omission_sha256(
            audit,
            'correction_sha256',
        )
    )
    phase08_validation.atomic_json(new_audit_path, audit)
    old_proof_calls = []

    def old_proof(
        root,
        correction_path,
        *,
        runtime_input_hashes=None,
    ):
        old_proof_calls.append((
            Path(root).resolve(),
            Path(correction_path).resolve(),
            runtime_input_hashes,
        ))
        return nested_recovery

    monkeypatch.setattr(
        phase08_validation,
        '_v3_hard_stop_policy_recovery_proof',
        old_proof,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_diagnostic_carried_records',
        lambda observed: (
            [carried_record]
            if observed == nested_recovery
            else pytest.fail('unexpected nested recovery')
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    return {
        'v3a_root': v3a_root,
        'v3b_root': v3b_root,
        'v3c_root': v3c_root,
        'v3d_root': v3d_root,
        'old_audit_path': old_audit_path,
        'new_audit_path': new_audit_path,
        'audit': audit,
        'nested_recovery': nested_recovery,
        'repository': repository,
        'artifact_paths': artifact_paths,
        'attempt_summary_path': attempt_summary_path,
        'attempt_record_path': attempt_record_path,
        'attempt_runs_root': attempt_runs_root,
        'latest_build_link': latest_build_link,
        'alternate_build_root': alternate_build_root,
        'old_proof_calls': old_proof_calls,
    }


def test_v3d_prelaunch_recovery_binds_v3c_and_nested_v3b(
    tmp_path,
    monkeypatch,
):
    """Admit V3D only from the exact zero-execution V3C failure."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)

    proof = phase08_validation._v3_prelaunch_failure_recovery_proof(
        fixture['v3b_root'],
        correction_path=fixture['new_audit_path'],
    )

    assert phase08_validation._v3_recovery_fresh_lineage_id(
        proof
    ) == 'phase08-v3d'
    assert proof['superseded_evidence_root'] == str(
        fixture['v3b_root'].resolve()
    )
    assert proof['failed_evidence_root'] == str(
        fixture['v3c_root'].resolve()
    )
    assert proof['nested_recovery'] == fixture['nested_recovery']
    assert proof['prelaunch_failure']['new_execution_count'] == 0
    assert proof['composite_activation']['execute_case_ids'] == list(
        phase08_validation.V3_DIAGNOSTIC_EXECUTION_CASE_IDS
    )
    assert fixture['old_proof_calls'] == [(
        fixture['v3b_root'].resolve(),
        fixture['old_audit_path'].resolve(),
        fixture['repository']['input_hashes'],
    )]


@pytest.mark.parametrize('lineage', ['v3a', 'v3b', 'v3c'])
def test_v3d_prelaunch_recovery_rejects_full_root_drift(
    tmp_path,
    monkeypatch,
    lineage,
):
    """Any added retained-root byte invalidates the compact manifest."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    root = fixture[f'{lineage}_root']
    (root / 'unrecorded-byte.txt').write_text(
        'drift\n',
        encoding='utf-8',
    )

    with pytest.raises(
        RuntimeError,
        match='retained full-root contents drifted',
    ):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


def test_v3d_prelaunch_recovery_rejects_symlink_target_drift(
    tmp_path,
    monkeypatch,
):
    """The excluded directory-symlink targets are immutable too."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    link = fixture['latest_build_link']
    link.unlink()
    link.symlink_to(
        fixture['alternate_build_root'].name,
        target_is_directory=True,
    )

    with pytest.raises(
        RuntimeError,
        match='retained full-root contents drifted',
    ):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


def test_v3d_prelaunch_recovery_rechecks_retained_runtime_projection(
    tmp_path,
    monkeypatch,
):
    """Do not trust V3C states without replaying the V3B projection gate."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    calls = []

    def reject_projection(recovery, repository):
        calls.append((recovery, repository))
        raise RuntimeError('retained runtime projection drifted')

    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_diagnostic_runtime_projection',
        reject_projection,
    )
    with pytest.raises(
        RuntimeError,
        match='retained runtime projection drifted',
    ):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )
    assert calls == [(
        fixture['nested_recovery'],
        fixture['repository'],
    )]


@pytest.mark.parametrize(
    'fixture_keywords',
    [
        {'activation_operator': 'different-operator'},
        {'nested_suite_sha256': '0' * 64},
        {'nested_commitment_sha256': '0' * 64},
        {
            'qualification_activation_contract': {
                'contract': 'changed',
            },
        },
        {'transaction_suite_bytes': b'different-suite\n'},
    ],
)
def test_v3d_prelaunch_recovery_rejects_adoption_lineage_drift(
    tmp_path,
    monkeypatch,
    fixture_keywords,
):
    """Re-prove V3C adoption ownership, payload, and qualification."""
    fixture = _v3d_prelaunch_fixture(
        tmp_path,
        monkeypatch,
        **fixture_keywords,
    )

    with pytest.raises(RuntimeError):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


def test_v3d_prelaunch_recovery_rejects_wrong_nested_fresh_root(
    tmp_path,
    monkeypatch,
):
    """The retained V3B recovery must have adopted this exact V3C root."""
    fixture = _v3d_prelaunch_fixture(
        tmp_path,
        monkeypatch,
        nested_fresh_evidence_root=tmp_path / 'wrong-v3c',
    )

    with pytest.raises(
        RuntimeError,
        match='adoption lineage binding drifted',
    ):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


def test_v3d_prelaunch_recovery_rejects_wrong_superseded_root(
    tmp_path,
    monkeypatch,
):
    """The V3D correction cannot be applied to another evidence root."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    wrong_root = tmp_path / 'wrong-v3b'
    wrong_root.mkdir()

    with pytest.raises(
        RuntimeError,
        match='names a different failure',
    ):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            wrong_root,
            correction_path=fixture['new_audit_path'],
        )


@pytest.mark.parametrize(
    'artifact_field',
    [
        'prepare_state_file_sha256',
        'qualification_state_file_sha256',
        'activation_state_file_sha256',
        'prepare_transaction_file_sha256',
        'activation_progress_file_sha256',
        'activation_records_file_sha256',
        'activation_attempt_records_file_sha256',
        'activation_scenario_summary_file_sha256',
        'activation_resolved_suite_file_sha256',
        'execution_error_file_sha256',
    ],
)
def test_v3d_prelaunch_recovery_rejects_every_artifact_drift(
    tmp_path,
    monkeypatch,
    artifact_field,
):
    """Every V3C state, aggregate, suite, and error byte is immutable."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    path = fixture['artifact_paths'][artifact_field]
    path.write_bytes(path.read_bytes() + b'\nDRIFT')

    with pytest.raises(RuntimeError, match='retained V3C artifact'):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


@pytest.mark.parametrize(
    'path_name,is_directory',
    [
        ('attempt_summary_path', False),
        ('attempt_record_path', False),
        ('attempt_runs_root', True),
    ],
)
def test_v3d_prelaunch_recovery_rejects_runtime_evidence(
    tmp_path,
    monkeypatch,
    path_name,
    is_directory,
):
    """A summary, record, or runs root would make dispatch ambiguous."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    path = fixture[path_name]
    if is_directory:
        path.mkdir(parents=True)
    else:
        path.write_text('unexpected\n', encoding='utf-8')

    with pytest.raises(RuntimeError, match='contains runtime evidence'):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


@pytest.mark.parametrize(
    'section,field,value',
    [
        ('prelaunch_failure', 'new_execution_count', 1),
        (
            'prelaunch_failure',
            'ambiguous_interrupted_dispatch_case_ids',
            ['v3a_below_target_fill'],
        ),
        ('prelaunch_failure', 'not_run_slot_ids', []),
        ('prelaunch_failure', 'error', 'RuntimeError: other'),
        ('composite_activation', 'new_execution_count', 8),
        ('correction', 'fresh_lineage_id', 'phase08-v3c'),
        ('correction', 'preserve_failed_v3c_root', False),
        ('retained_v3c', 'nested_v3b_recovery_sha256', '0' * 64),
    ],
)
def test_v3d_prelaunch_recovery_rejects_policy_and_semantic_drift(
    tmp_path,
    monkeypatch,
    section,
    field,
    value,
):
    """Rehashing a scientifically different audit cannot authorize V3D."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    audit = json.loads(
        fixture['new_audit_path'].read_text(encoding='utf-8')
    )
    audit[section][field] = value
    audit['correction_sha256'] = (
        phase08_validation.omission_sha256(
            audit,
            'correction_sha256',
        )
    )
    phase08_validation.atomic_json(fixture['new_audit_path'], audit)

    with pytest.raises(RuntimeError):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


def test_v3d_prelaunch_recovery_rejects_audit_hash_and_processes(
    tmp_path,
    monkeypatch,
):
    """Reject both an unsigned audit mutation and a live process set."""
    fixture = _v3d_prelaunch_fixture(tmp_path, monkeypatch)
    audit = json.loads(
        fixture['new_audit_path'].read_text(encoding='utf-8')
    )
    audit['classification'] = 'drifted'
    phase08_validation.atomic_json(fixture['new_audit_path'], audit)
    with pytest.raises(RuntimeError, match='correction hash drifted'):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )

    phase08_validation.atomic_json(
        fixture['new_audit_path'],
        fixture['audit'],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [{'pid': 99, 'command': 'gzserver'}],
    )
    with pytest.raises(RuntimeError, match='process set is not clean'):
        phase08_validation._v3_prelaunch_failure_recovery_proof(
            fixture['v3b_root'],
            correction_path=fixture['new_audit_path'],
        )


def test_v3_adopt_precommit_rejects_the_superseded_root(
    tmp_path,
):
    """Never append corrected evidence to the closed V3A namespace."""
    superseded = tmp_path / 'v3a'

    with pytest.raises(RuntimeError, match='must not reuse'):
        phase08_validation.run_v3_adopt_precommit(
            'test',
            superseded,
            superseded,
            suite_path=tmp_path / 'suite.json',
            commitment_path=tmp_path / 'commitment.json',
        )


def test_v3_harness_recovery_rejects_audited_precommit_drift(
    tmp_path,
    monkeypatch,
):
    """Bind the corrected lineage to V3A's exact committed population."""
    superseded = tmp_path / 'v3a'
    correction_path = tmp_path / 'audit.json'
    prepare = {
        'state_sha256': 'p' * 64,
        'suite_sha256': 'a' * 64,
        'commitment_sha256': 'b' * 64,
    }
    qualification = {
        'state_sha256': 'q' * 64,
        'prepare_state_sha256': prepare['state_sha256'],
    }
    activation = {
        'passed': False,
        'state_sha256': 'z' * 64,
        'qualification_state_sha256': qualification['state_sha256'],
        'run_count': 1,
        'integrity_pass_count': 0,
        'contract_pass_count': 0,
        'not_run_slot_ids': [f'not-run-{index}' for index in range(9)],
        'stopped_early_reason': 'non-ground collision',
    }
    states = {
        'prepare': prepare,
        'qualification': qualification,
        'activation': activation,
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_state',
        lambda unused_root, stage, **unused: states[stage],
    )
    correction = {
        'schema_version': 1,
        'superseded_evidence_root': str(superseded.resolve()),
        'precommit': {
            'suite_sha256': 'c' * 64,
            'commitment_sha256': 'd' * 64,
        },
        'correction': {
            'probe_policy': 'collision_expected_true_only',
            'analysis_collision_filter_changed': False,
            'formal_collision_gate_changed': False,
            'fresh_activation_required': True,
            'reuse_precommitted_population_byte_identically': True,
        },
        'contact_audit': {
            'non_ground_contact_state_count': 105,
            'positive_control_contact_state_count': 105,
            'other_non_ground_contact_state_count': 0,
        },
    }
    correction['correction_sha256'] = (
        phase08_validation.omission_sha256(
            correction,
            'correction_sha256',
        )
    )
    phase08_validation.atomic_json(correction_path, correction)

    with pytest.raises(RuntimeError, match='precommit differs'):
        phase08_validation._v3_harness_recovery_proof(
            superseded,
            correction_path=correction_path,
        )


def _v3_activation_dry_run_summary(case_ids=None):
    """Build a complete installed activation invocation fixture."""
    case_ids = case_ids or [
        f'activation-{index}' for index in range(10)
    ]
    launch = [
        'ros2',
        'launch',
        'turtlebot3_rotating_sensor',
        'gazebo.launch.xml',
        'gazebo_gui:=True',
        'simulation_contacts_enabled:=True',
        'simulation_contact_probe_enabled:=False',
    ]
    return {
        'schema_version': 1,
        'suite_id': 'phase08_v3_activation',
        'scenario_schema_version': 4,
        'source_path': '/workspace/phase08_v3_activation.yaml',
        'serial_execution': True,
        'selected_case_ids': [],
        'resolved_run_count': len(case_ids),
        'unsupported_count': 0,
        'unsupported': [],
        'dry_run': True,
        'runs': [
            {
                'run_id': f'ephemeral-{case_id}',
                'case_id': case_id,
                'case_key': f'{index + 1:064x}',
                'profile': 'robust_gaussian_v1',
                'seed': 9301 + index,
                'launch_argv': list(launch),
                'record_argv': [
                    'ros2',
                    'run',
                    'ros_esc',
                    'record_run',
                    '--metadata-input',
                    f'/tmp/{case_id}/metadata.yaml',
                    '--run-id',
                    f'ephemeral-{case_id}',
                    '--duration-sec',
                    '240.0',
                    '--',
                    *launch,
                ],
                'activation_contract': {
                    'contract_id': case_id,
                    'expected_verification_outcome': 'goal',
                },
                'metadata': {
                    'schema_version': 1,
                    'experiment_version': 'phase08-v3-activation',
                    'mode': 'simulation',
                    'algorithm_profile': 'robust_gaussian_v1',
                    'random_seed': 9301 + index,
                    'environment': {
                        'disturbances': {
                            'sensor_noise': {
                                'model': 'none',
                                'bound': 0.0,
                            },
                            'sensor_delay_sec': 0.0,
                            'pose_delay_sec': 0.0,
                        },
                    },
                    'parameter_files': [
                        '/workspace/base_cost.json',
                        '/workspace/filter.json',
                        '/workspace/controller.json',
                    ],
                    'scenario_runner': {
                        'case_id': case_id,
                        'case_key': f'{index + 1:064x}',
                        'seed': 9301 + index,
                    },
                },
            }
            for index, case_id in enumerate(case_ids)
        ],
    }


def test_v3_activation_invocation_normalizes_only_ephemeral_values():
    """Normalize run IDs, metadata paths, and generated noise configs."""
    baseline = _v3_activation_dry_run_summary()
    old_noise_config = (
        'cost_function_config_filepath:=/tmp/'
        'gesc_phase06_old123/resolved_cost_function.json'
    )
    baseline['runs'][8]['launch_argv'].append(old_noise_config)
    baseline['runs'][8]['record_argv'].append(old_noise_config)
    observed = json.loads(json.dumps(baseline))
    for index, run in enumerate(observed['runs']):
        run['run_id'] = f'new-ephemeral-{index}'
        for flag in ('--metadata-input', '--run-id'):
            flag_index = run['record_argv'].index(flag)
            run['record_argv'][flag_index + 1] = (
                f'/new/ephemeral/{flag}/{index}'
            )
    new_noise_config = (
        'cost_function_config_filepath:=/tmp/'
        'gesc_phase06_new456/resolved_cost_function.json'
    )
    observed['runs'][8]['launch_argv'][-1] = new_noise_config
    observed['runs'][8]['record_argv'][-1] = new_noise_config

    assert (
        phase08_validation._v3_activation_invocation_contract(
            observed
        )
        == phase08_validation._v3_activation_invocation_contract(
            baseline
        )
    )


@pytest.mark.parametrize(
    'defect',
    [
        'case_id',
        'case_key',
        'seed',
        'profile',
        'launch_argv',
        'record_argv',
        'activation_contract',
        'metadata',
        'repository_config_path',
    ],
)
def test_v3_activation_invocation_rejects_non_ephemeral_drift(defect):
    """Bind every non-ephemeral activation invocation input exactly."""
    baseline = _v3_activation_dry_run_summary()
    if defect == 'repository_config_path':
        repository_config = (
            'cost_function_config_filepath:=/home/mattb/dsim-lab/'
            'ros2_ws/src/ros_esc/base_cost.json'
        )
        baseline['runs'][0]['launch_argv'].append(repository_config)
        baseline['runs'][0]['record_argv'].append(repository_config)
    observed = json.loads(json.dumps(baseline))
    run = observed['runs'][0]
    if defect == 'case_id':
        run['case_id'] = 'drifted-case'
    elif defect == 'case_key':
        run['case_key'] = 'f' * 64
    elif defect == 'seed':
        run['seed'] += 1
    elif defect == 'profile':
        run['profile'] = 'legacy'
    elif defect == 'launch_argv':
        run['launch_argv'][-1] = (
            'simulation_contact_probe_enabled:=True'
        )
    elif defect == 'record_argv':
        duration_index = run['record_argv'].index('--duration-sec')
        run['record_argv'][duration_index + 1] = '239.0'
    elif defect == 'activation_contract':
        run['activation_contract'][
            'expected_verification_outcome'
        ] = 'safe_timeout'
    elif defect == 'metadata':
        run['metadata']['environment']['disturbances'][
            'sensor_delay_sec'
        ] = 0.05
    else:
        run['launch_argv'][-1] = (
            'cost_function_config_filepath:=/home/mattb/dsim-lab/'
            'ros2_ws/src/ros_esc/changed_cost.json'
        )
        run['record_argv'][-1] = run['launch_argv'][-1]

    assert (
        phase08_validation._v3_activation_invocation_contract(
            observed
        )
        != phase08_validation._v3_activation_invocation_contract(
            baseline
        )
    )


def test_v3_activation_contact_launch_contract_requires_passive_probe():
    """Require every installed direct and recorder launch to omit the probe."""
    required = [
        'gazebo_gui:=True',
        'simulation_contacts_enabled:=True',
        'simulation_contact_probe_enabled:=False',
    ]
    summary = {
        'runs': [
            {
                'case_id': f'activation-{index}',
                'launch_argv': list(required),
                'record_argv': list(required),
            }
            for index in range(10)
        ],
    }

    passed = (
        phase08_validation._v3_activation_contact_launch_contract(
            summary
        )
    )
    assert passed['passed'] is True
    assert passed['direct_pass_count'] == 10
    assert passed['recorder_pass_count'] == 10

    summary['runs'][3]['record_argv'] = [
        'gazebo_gui:=True',
        'simulation_contacts_enabled:=True',
        'simulation_contact_probe_enabled:=True',
    ]
    failed = (
        phase08_validation._v3_activation_contact_launch_contract(
            summary
        )
    )
    assert failed['passed'] is False
    assert failed['recorder_pass_count'] == 9


def test_v3_qualification_requires_adopted_recovery(tmp_path):
    """Do not qualify a post-V3A root outside the corrected lineage."""
    phase08_validation._v3_write_state(
        tmp_path,
        'prepare',
        {
            'passed': True,
            'operator': 'test',
            'repository': {},
        },
    )

    with pytest.raises(RuntimeError, match='v3-adopt-precommit recovery'):
        phase08_validation.run_v3_qualify('test', tmp_path)


def test_v3_activation_revalidates_corrected_recovery(
    tmp_path,
    monkeypatch,
):
    """Reject V3A evidence drift before corrected Gazebo dispatch."""
    recovery = {
        'kind': 'contact_probe_instrumentation_contamination',
        'superseded_evidence_root': '/tmp/v3a',
        'correction_audit_path': '/tmp/audit.json',
    }
    prepare = {
        'state_sha256': 'p' * 64,
        'lineage_id': 'phase08-v3b',
        'recovery': recovery,
    }
    dry_run_path = tmp_path / 'activation_dry_run.yaml'
    dry_run_summary = _v3_activation_dry_run_summary()
    phase08_validation.atomic_yaml(dry_run_path, dry_run_summary)
    contact_contract = (
        phase08_validation._v3_activation_contact_launch_contract(
            dry_run_summary
        )
    )
    invocation_contract = (
        phase08_validation._v3_activation_invocation_contract(
            dry_run_summary
        )
    )
    recovery['activation_invocation_contract'] = invocation_contract
    qualification = {
        'prepare_state_sha256': prepare['state_sha256'],
        'lineage_id': 'phase08-v3b',
        'recovery_validation': {
            'passed': True,
            'recovery_sha256': phase08_validation.canonical_sha256(
                recovery
            ),
        },
        'activation_contact_launch_contract': contact_contract,
        'activation_invocation_contract': invocation_contract,
        'installed_dry_runs': {
            'activation': {
                'path': str(dry_run_path),
                'sha256': phase08_validation.file_sha256(
                    dry_run_path
                ),
            },
        },
    }
    observed = dict(recovery)
    monkeypatch.setattr(
        phase08_validation,
        '_v3_harness_recovery_proof',
        lambda *unused, **unused_keywords: observed,
    )

    phase08_validation._v3_verify_corrected_recovery_before_activation(
        prepare,
        qualification,
    )
    dry_run_path.write_text('runs: []\n', encoding='utf-8')
    with pytest.raises(RuntimeError, match='dry-run artifact drifted'):
        phase08_validation._v3_verify_corrected_recovery_before_activation(
            prepare,
            qualification,
        )
    phase08_validation.atomic_yaml(dry_run_path, dry_run_summary)
    qualification['installed_dry_runs']['activation']['sha256'] = (
        phase08_validation.file_sha256(dry_run_path)
    )
    observed['run_id'] = 'drifted'
    with pytest.raises(RuntimeError, match='proof drifted'):
        phase08_validation._v3_verify_corrected_recovery_before_activation(
            prepare,
            qualification,
        )


def test_v3c_activation_revalidates_diagnostic_recovery(
    tmp_path,
    monkeypatch,
):
    """Bind V3C predispatch to V3B and its retained installed dry run."""
    recovery = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': '/tmp/v3b',
        'correction_audit_path': '/tmp/diagnostic.json',
        'policy': {'fresh_lineage_id': 'phase08-v3c'},
    }
    prepare = {
        'state_sha256': 'p' * 64,
        'lineage_id': 'phase08-v3c',
        'recovery': recovery,
    }
    dry_run_path = tmp_path / 'activation_dry_run.yaml'
    dry_run_summary = _v3_activation_dry_run_summary()
    phase08_validation.atomic_yaml(dry_run_path, dry_run_summary)
    contact_contract = (
        phase08_validation._v3_activation_contact_launch_contract(
            dry_run_summary
        )
    )
    invocation_contract = (
        phase08_validation._v3_activation_invocation_contract(
            dry_run_summary
        )
    )
    recovery['activation_invocation_contract'] = invocation_contract
    prepare['recovery'] = recovery
    qualification = {
        'prepare_state_sha256': prepare['state_sha256'],
        'lineage_id': 'phase08-v3c',
        'recovery_validation': {
            'passed': True,
            'recovery_sha256': phase08_validation.canonical_sha256(
                recovery
            ),
        },
        'activation_contact_launch_contract': contact_contract,
        'activation_invocation_contract': invocation_contract,
        'installed_dry_runs': {
            'activation': {
                'path': str(dry_run_path),
                'sha256': phase08_validation.file_sha256(
                    dry_run_path
                ),
            },
        },
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_revalidate_recovery',
        lambda value: value,
    )

    phase08_validation._v3_verify_corrected_recovery_before_activation(
        prepare,
        qualification,
    )
    drifted_summary = json.loads(json.dumps(dry_run_summary))
    drifted_summary['runs'][0]['seed'] += 1
    phase08_validation.atomic_yaml(dry_run_path, drifted_summary)
    qualification['installed_dry_runs']['activation']['sha256'] = (
        phase08_validation.file_sha256(dry_run_path)
    )
    with pytest.raises(RuntimeError, match='invocation contract drifted'):
        phase08_validation._v3_verify_corrected_recovery_before_activation(
            prepare,
            qualification,
        )
    phase08_validation.atomic_yaml(dry_run_path, dry_run_summary)
    qualification['installed_dry_runs']['activation']['sha256'] = (
        phase08_validation.file_sha256(dry_run_path)
    )
    qualification['lineage_id'] = 'phase08-v3b'
    with pytest.raises(RuntimeError, match='lineage drifted'):
        phase08_validation._v3_verify_corrected_recovery_before_activation(
            prepare,
            qualification,
        )


def test_v3c_carried_record_is_rehashed_and_remains_failed(tmp_path):
    """Reference the original V3B record without copying or relabeling."""
    record_path = tmp_path / 'record.json'
    record = _v3_applicability_partial_record(
        tmp_path,
        'v3a_goal_aggregate_direct',
        run_id='retained-v3b-run',
    )
    phase08_validation.atomic_json(record_path, record)
    original_bytes = record_path.read_bytes()
    recovery = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': '/tmp/v3b',
        'superseded_activation_state_sha256': 's' * 64,
        'run_directory_manifest': (
            phase08_validation._v3_directory_manifest(
                record['run_directory']
            )
        ),
        'carried_record': {
            'case_id': 'v3a_goal_aggregate_direct',
            'record_path': str(record_path),
            'record_sha256': phase08_validation.file_sha256(record_path),
            'run_id': record['run_id'],
            'source_lineage_id': 'phase08-v3b',
        },
    }

    carried = phase08_validation._v3_diagnostic_carried_records(
        recovery
    )

    assert len(carried) == 1
    assert carried[0]['record_path'] == str(record_path.resolve())
    assert carried[0]['rerun'] is False
    assert carried[0]['disposition'] == (
        'carried_immutable_behavioral_failure'
    )
    assert record_path.read_bytes() == original_bytes
    bag_metadata = (
        Path(record['run_directory']) / 'bag/metadata.yaml'
    )
    original_bag_metadata = bag_metadata.read_bytes()
    bag_metadata.write_text('drifted: true\n', encoding='utf-8')
    with pytest.raises(RuntimeError, match='run directory drifted'):
        phase08_validation._v3_diagnostic_carried_records(recovery)
    bag_metadata.write_bytes(original_bag_metadata)
    record_path.write_text('{}\n', encoding='utf-8')
    with pytest.raises(RuntimeError, match='carried record drifted'):
        phase08_validation._v3_diagnostic_carried_records(recovery)


def test_v3c_activation_composite_is_permanently_not_pass_eligible(
    tmp_path,
    monkeypatch,
):
    """Report one carried plus nine new slots and prohibit development."""
    recovery = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'policy': {'fresh_lineage_id': 'phase08-v3c'},
    }
    prepare = {
        'passed': True,
        'operator': 'test',
        'state_sha256': 'p' * 64,
        'lineage_id': 'phase08-v3c',
        'recovery': recovery,
    }
    qualification = {
        'passed': True,
        'operator': 'test',
        'state_sha256': 'q' * 64,
        'lineage_id': 'phase08-v3c',
        'repository': {},
    }
    states = {
        'prepare': prepare,
        'qualification': qualification,
    }
    case_ids = [
        'v3a_goal_aggregate_direct',
        *[f'new-slot-{index}' for index in range(9)],
    ]
    recovery['composite_activation'] = {
        'execute_case_ids': case_ids[1:],
    }
    carried = [{
        'case_id': case_ids[0],
        'record_path': '/immutable/v3b/record.json',
        'record_sha256': 'a' * 64,
        'rerun': False,
    }]
    records = [
        _v3_serial_record(
            case_id,
            status='failed' if index == 0 else 'passed',
        )
        for index, case_id in enumerate(case_ids)
    ]

    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_state',
        lambda unused_root, stage, **unused: states[stage],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_corrected_recovery_before_activation',
        lambda *unused: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_precommit_in_head',
        lambda: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_repository_snapshot',
        lambda *unused, **unused_keywords: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_materialize_profile_suite',
        lambda unused_source, unused_profile, destination: destination,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_diagnostic_carried_records',
        lambda unused_recovery: carried,
    )

    def fake_execute(
        unused_suite,
        unused_operator,
        unused_root,
        stage_root,
        unused_stage,
        **kwargs,
    ):
        assert kwargs['carried_records'] == carried
        assert kwargs['required_execution_case_ids'] == case_ids[1:]
        assert kwargs['allow_pure_applicability_miss'] is True
        assert kwargs['allow_infrastructure_replacements'] is False
        stage_root = Path(stage_root)
        summary_path = stage_root / 'scenario_summary.yaml'
        records_path = stage_root / 'records.json'
        attempts_path = stage_root / 'attempt_records.json'
        phase08_validation.atomic_yaml(summary_path, {'runs': []})
        phase08_validation.atomic_json(records_path, records)
        phase08_validation.atomic_json(attempts_path, records[1:])
        attempts = [
            {'case_id': case_id, 'attempt_index': 1}
            for case_id in case_ids[1:]
        ]
        return (
            {'summary_path': str(summary_path)},
            records,
            {
                'progress_sha256': 'r' * 64,
                'stopped_early_reason': None,
                'not_run_slot_ids': [],
                'attempts': attempts,
                'carried_count': 1,
                'newly_executed_count': 9,
                'carried_records': carried,
            },
        )

    monkeypatch.setattr(
        phase08_validation,
        '_v3_execute_serial_slots',
        fake_execute,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_record_integrity',
        lambda record: {
            'passed': record['case_id'] != case_ids[0],
            'reasons': [],
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        '_run_functional_tests',
        lambda: {'passed': True},
    )

    state = phase08_validation.run_v3_activation('test', tmp_path)

    assert state['passed'] is False
    assert state['pass_eligible'] is False
    assert state['diagnostic_completion'] is True
    assert state['composite_slot_count'] == 10
    assert state['carried_count'] == 1
    assert state['newly_executed_count'] == 9
    assert state['carried_record_count'] == 1
    assert state['new_execution_count'] == 9
    assert state['ambiguous_interrupted_dispatch_case_ids'] == []
    assert state['contract_pass_count'] == 9
    assert any(
        'not pass-eligible' in reason for reason in state['reasons']
    )


def test_v3_prepare_recovers_from_post_transaction_interruption(
    tmp_path,
    monkeypatch,
):
    """Resume safely without regenerating the precommitted suite."""
    root = tmp_path / 'fresh-evidence'
    suite_path = tmp_path / 'suite.json'
    commitment_path = tmp_path / 'commitment.json'
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: {
            'commit': 'a' * 40,
            'tree': 'b' * 40,
            'clean': True,
            'input_hashes': {},
            'runtime_inputs_sha256': phase08_validation.canonical_sha256({}),
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_repository_snapshot',
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_assert_worktree_changes',
        lambda *unused: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_required_free_bytes',
        lambda *unused: 1,
    )
    monkeypatch.setattr(
        phase08_validation.shutil,
        'disk_usage',
        lambda unused: SimpleNamespace(free=10_000),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_historical_case_keys',
        lambda: (set(), {}),
    )
    monkeypatch.setattr(
        phase08_validation,
        'generate_v3_acceptance_population',
        lambda *args, **kwargs: {'cases': []},
    )
    real_atomic_bytes = phase08_validation.atomic_bytes
    interrupted = {'armed': True}

    def flaky_atomic_bytes(path, value, mode=None):
        if Path(path) == suite_path and interrupted['armed']:
            interrupted['armed'] = False
            raise RuntimeError('simulated interruption')
        return real_atomic_bytes(path, value, mode=mode)

    monkeypatch.setattr(
        phase08_validation,
        'atomic_bytes',
        flaky_atomic_bytes,
    )
    with pytest.raises(RuntimeError, match='simulated interruption'):
        phase08_validation.run_v3_prepare(
            'test',
            root,
            seed_bytes=b'x' * 32,
            suite_path=suite_path,
            commitment_path=commitment_path,
        )
    assert phase08_validation._v3_prepare_transaction_path(
        root
    ).is_file()
    assert not suite_path.exists()

    state = phase08_validation.run_v3_prepare(
        'test',
        root,
        suite_path=suite_path,
        commitment_path=commitment_path,
    )

    assert state['passed'] is True
    assert state['selection_blind'] is False
    assert suite_path.is_file()
    assert json.loads(suite_path.read_text(encoding='utf-8')) == {'cases': []}
    commitment = json.loads(commitment_path.read_text(encoding='utf-8'))
    assert commitment['suite_sha256'] == phase08_validation.file_sha256(
        suite_path
    )
    assert commitment['population_visibility'] == (
        'researcher_visible_before_activation'
    )


def test_v3_prepare_rejects_a_preexisting_unowned_root(tmp_path):
    """Never mix the fresh v3 evidence chain with existing contents."""
    root = tmp_path / 'existing'
    root.mkdir()

    with pytest.raises(RuntimeError, match='absent fresh evidence root'):
        phase08_validation.run_v3_prepare(
            'test',
            root,
            suite_path=tmp_path / 'suite.json',
            commitment_path=tmp_path / 'commitment.json',
        )


def test_v3_prepare_failure_before_transaction_leaves_root_absent(
    tmp_path,
    monkeypatch,
):
    """Publish no evidence root until a recoverable transaction is ready."""
    root = tmp_path / 'fresh-evidence'
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: {
            'commit': 'a' * 40,
            'tree': 'b' * 40,
            'clean': True,
            'input_hashes': {},
            'runtime_inputs_sha256': phase08_validation.canonical_sha256({}),
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_required_free_bytes',
        lambda *unused: 1,
    )
    monkeypatch.setattr(
        phase08_validation.shutil,
        'disk_usage',
        lambda unused: SimpleNamespace(free=10_000),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_historical_case_keys',
        lambda: (set(), {}),
    )

    def fail_generation(*unused, **unused_keywords):
        del unused, unused_keywords
        raise RuntimeError('simulated population failure')

    monkeypatch.setattr(
        phase08_validation,
        'generate_v3_acceptance_population',
        fail_generation,
    )

    with pytest.raises(RuntimeError, match='population failure'):
        phase08_validation.run_v3_prepare(
            'test',
            root,
            seed_bytes=b'x' * 32,
            suite_path=tmp_path / 'suite.json',
            commitment_path=tmp_path / 'commitment.json',
        )

    assert not root.exists()
    assert not list(tmp_path.glob('.fresh-evidence.prepare-*'))


def test_v3_commitment_declares_visible_sha256_precommit():
    """Record the exact non-blind precommit semantics in the hash document."""
    suite_bytes = b'{"cases":[]}'
    commitment = phase08_validation._v3_commitment_document(
        {'cases': []},
        suite_bytes,
        {},
    )

    assert commitment['suite_sha256'] == (
        phase08_validation._sha256_bytes(suite_bytes)
    )
    assert commitment['selection_blind'] is False
    assert commitment['population_visibility'] == (
        'researcher_visible_before_activation'
    )
    assert commitment['precommit_mechanism'] == 'canonical_json_sha256'
    assert 'ciphertext_sha256' not in commitment
    assert 'recipient_fingerprint' not in commitment


def test_v3_precommit_requires_exact_tracked_head_blobs(
    tmp_path,
    monkeypatch,
):
    """Require committed suite bytes before activation dispatch."""
    suite_path = tmp_path / 'suite.json'
    commitment_path = tmp_path / 'commitment.json'
    suite_path.write_text('{}', encoding='utf-8')
    commitment_path.write_text('{}', encoding='utf-8')
    monkeypatch.setattr(
        phase08_validation,
        'REPOSITORY_ROOT',
        tmp_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRECOMMITTED_SUITE_PATH',
        suite_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_COMMITMENT_PATH',
        commitment_path,
    )

    def exact(*arguments):
        if arguments[0] == 'hash-object':
            return {
                'suite.json': 'suite-blob',
                'commitment.json': 'commitment-blob',
            }[arguments[1]]
        return {
            'HEAD:suite.json': 'suite-blob',
            'HEAD:commitment.json': 'commitment-blob',
        }[arguments[1]]

    monkeypatch.setattr(phase08_validation, '_git', exact)
    phase08_validation._v3_require_precommit_in_head()

    def mismatch(*arguments):
        if arguments[0] == 'hash-object':
            return 'working-tree-blob'
        return 'head-blob'

    monkeypatch.setattr(phase08_validation, '_git', mismatch)
    with pytest.raises(RuntimeError, match='differs from HEAD'):
        phase08_validation._v3_require_precommit_in_head()

    def untracked(*arguments):
        if arguments[0] == 'hash-object':
            return 'working-tree-blob'
        raise subprocess.CalledProcessError(128, ['git', *arguments])

    monkeypatch.setattr(phase08_validation, '_git', untracked)
    with pytest.raises(RuntimeError, match='not tracked in HEAD'):
        phase08_validation._v3_require_precommit_in_head()


def test_v3_state_hash_detects_mutation(tmp_path):
    """Do not resume a stage from a mutated external state record."""
    phase08_validation._v3_write_state(
        tmp_path,
        'qualification',
        {'passed': True, 'operator': 'test'},
    )
    path = phase08_validation._v3_state_path(
        tmp_path,
        'qualification',
    )
    state = json.loads(path.read_text(encoding='utf-8'))
    state['operator'] = 'mutated'
    path.write_text(json.dumps(state), encoding='utf-8')

    with pytest.raises(RuntimeError, match='state hash drifted'):
        phase08_validation._v3_require_state(
            tmp_path,
            'qualification',
        )


def test_v3_process_scan_excludes_the_invocation_ancestry(monkeypatch):
    """The outer timeout/ros2 wrappers are not orphan-process failures."""
    process_table = '\n'.join([
        '100 1 bash -lc timeout 1800s ros2 run ros_esc '
        'validate_robustness v3-qualify',
        '101 100 timeout 1800s ros2 run ros_esc '
        'validate_robustness v3-qualify',
        '102 101 python3 validate_robustness v3-qualify',
        '200 1 gzserver --verbose',
        '201 1 python3 unrelated_worker.py',
    ])
    monkeypatch.setattr(
        phase08_validation.subprocess,
        'run',
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0],
            0,
            stdout=process_table,
        ),
    )
    monkeypatch.setattr(phase08_validation.os, 'getpid', lambda: 102)

    assert phase08_validation._v3_active_processes() == [{
        'pid': 200,
        'command': 'gzserver --verbose',
    }]


def test_v3_runtime_snapshot_rejects_committed_source_drift(monkeypatch):
    """A later clean commit cannot silently replace qualified inputs."""
    snapshot = {
        'input_hashes': {'ros2_ws/src/ros_esc/package.xml': 'a' * 64},
        'runtime_inputs_sha256': phase08_validation.canonical_sha256({
            'ros2_ws/src/ros_esc/package.xml': 'a' * 64,
        }),
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: {
            'input_hashes': {
                'ros2_ws/src/ros_esc/package.xml': 'b' * 64,
            },
        },
    )

    with pytest.raises(RuntimeError, match='differ'):
        phase08_validation._v3_verify_repository_snapshot(snapshot)


@pytest.mark.parametrize(
    'drifted_path',
    [
        (
            'ros2_ws/src/ros_esc/ros_esc/supervisor_node/'
            'state_machine.py'
        ),
        (
            'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
            'phase08_v3_activation.yaml'
        ),
    ],
)
def test_v3c_runtime_projection_allows_only_four_workflow_files(
    drifted_path,
):
    """Allow four workflow files while rejecting algorithm/scenario drift."""
    assert phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT == (
        (
            'ros2_ws/src/ros_esc/ros_esc/scenario_runner/'
            'phase08_validation.py'
        ),
        (
            'ros2_ws/src/ros_esc/ros_esc/scenario_runner/'
            'run_scenario.py'
        ),
        'ros2_ws/src/ros_esc/test/test_phase08_validation.py',
        'ros2_ws/src/ros_esc/test/test_scenario_runner.py',
    )
    input_hashes = {
        path: f'{index + 1:064x}'
        for index, path in enumerate(
            phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        )
    }
    input_hashes.update({
        (
            'ros2_ws/src/ros_esc/ros_esc/supervisor_node/'
            'state_machine.py'
        ): 'a' * 64,
        (
            'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
            'phase08_v3_activation.yaml'
        ): 'b' * 64,
    })

    def snapshot(hashes):
        return {
            'input_hashes': hashes,
            'runtime_inputs_sha256': (
                phase08_validation.canonical_sha256(hashes)
            ),
        }

    baseline = snapshot(dict(input_hashes))
    recovery = {
        'kind': 'behavioral_miss_diagnostic_completion',
        'baseline_runtime_projection': (
            phase08_validation._v3_runtime_input_projection(baseline)
        ),
    }
    allowed = dict(input_hashes)
    for path in phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT:
        allowed[path] = 'e' * 64
    recovery['allowed_runtime_correction_sha256'] = {
        path: allowed[path]
        for path in (
            phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        )
    }
    phase08_validation._v3_verify_diagnostic_runtime_projection(
        recovery,
        snapshot(allowed),
    )
    unapproved_correction = dict(allowed)
    unapproved_correction[
        phase08_validation.V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT[0]
    ] = 'd' * 64
    with pytest.raises(RuntimeError, match='hash mapping drifted'):
        phase08_validation._v3_verify_diagnostic_runtime_projection(
            recovery,
            snapshot(unapproved_correction),
        )
    drifted = dict(allowed)
    drifted[drifted_path] = 'f' * 64

    with pytest.raises(RuntimeError, match='outside the allowed'):
        phase08_validation._v3_verify_diagnostic_runtime_projection(
            recovery,
            snapshot(drifted),
        )


def test_v3_qualification_rejects_kill_after_instantiation(
    tmp_path,
    monkeypatch,
):
    """Timeout 124 passes only when SIGINT exits without the KILL fallback."""
    def run(
        identifier,
        command,
        cwd,
        log_root,
        timeout_sec,
        expected_return_codes=(0,),
        environment=None,
    ):
        del command, cwd, log_root, timeout_sec
        del expected_return_codes, environment
        output = ''
        if identifier == 'supervisor_instantiation':
            output = 'timeout: sending signal INT to command'
        elif identifier == 'fill_instantiation':
            output = (
                'timeout: sending signal INT to command\n'
                'timeout: sending signal KILL to command'
            )
        return {
            'identifier': identifier,
            'passed': True,
            'output_tail': output,
        }

    monkeypatch.setattr(
        phase08_validation,
        '_v3_run_qualification_command',
        run,
    )

    commands, unused_install = (
        phase08_validation._v3_qualification_commands(tmp_path)
    )

    assert commands[-1]['identifier'] == 'fill_instantiation'
    assert commands[-1]['passed'] is False
    assert commands[-1]['clean_sigint_shutdown'] is False


def test_v3_qualification_builds_declared_dependency_closure(
    tmp_path,
    monkeypatch,
):
    """Do not mask missing package dependencies with an explicit build list."""
    captured = {}

    def run(
        identifier,
        command,
        cwd,
        log_root,
        timeout_sec,
        expected_return_codes=(0,),
        environment=None,
    ):
        del cwd, log_root, timeout_sec, expected_return_codes, environment
        captured[identifier] = command
        return {
            'identifier': identifier,
            'passed': False,
        }

    monkeypatch.setattr(
        phase08_validation,
        '_v3_run_qualification_command',
        run,
    )

    commands, unused_install = (
        phase08_validation._v3_qualification_commands(tmp_path)
    )

    assert len(commands) == 1
    assert '--packages-up-to' in captured['isolated_build']
    assert captured['isolated_build'][-2:] == [
        '--packages-up-to',
        'ros_esc',
    ]
    assert '--packages-select' not in captured['isolated_build']


def test_v3_qualification_runs_installed_boundary_observer_smoke(
    tmp_path,
    monkeypatch,
):
    """Exercise the private-context observer without Gazebo or a recorder."""
    captured = {}

    def run(
        identifier,
        command,
        cwd,
        log_root,
        timeout_sec,
        expected_return_codes=(0,),
        environment=None,
    ):
        del cwd, log_root, environment
        captured[identifier] = {
            'command': command,
            'timeout_sec': timeout_sec,
            'expected_return_codes': expected_return_codes,
        }
        output = ''
        if identifier in {
            'supervisor_instantiation',
            'fill_instantiation',
        }:
            output = 'timeout: sending signal INT to command'
        return {
            'identifier': identifier,
            'passed': True,
            'output_tail': output,
        }

    monkeypatch.setattr(
        phase08_validation,
        '_v3_run_qualification_command',
        run,
    )

    commands, unused_install = (
        phase08_validation._v3_qualification_commands(tmp_path)
    )

    smoke = captured['boundary_observer_smoke']
    assert smoke['command'][:2] == ['bash', '-c']
    script = smoke['command'][2]
    assert 'source ' in script
    assert 'cd /tmp' in script
    assert 'timeout --signal=TERM --kill-after=2s 15s' in script
    assert 'run_record_process' in script
    assert "anchor_state='VERIFY_EXTREMUM'" in script
    assert "boundary_state='ESCAPE_REPULSE'" in script
    assert "boundary_required_events=['ESCAPE_STARTED']" in script
    assert 'boundary-probe' in script
    assert 'gazebo' not in script.lower()
    assert 'record_run' not in script
    assert smoke['timeout_sec'] == 30.0
    assert smoke['expected_return_codes'] == (0,)
    assert any(
        item['identifier'] == 'boundary_observer_smoke'
        and item['passed']
        for item in commands
    )


def test_v3_qualification_stops_on_boundary_observer_failure(
    tmp_path,
    monkeypatch,
):
    """A broken private-context observer must fail qualification early."""
    observed = []

    def run(
        identifier,
        command,
        cwd,
        log_root,
        timeout_sec,
        expected_return_codes=(0,),
        environment=None,
    ):
        del command, cwd, log_root, timeout_sec
        del expected_return_codes, environment
        observed.append(identifier)
        return {
            'identifier': identifier,
            'passed': identifier != 'boundary_observer_smoke',
            'output_tail': '',
        }

    monkeypatch.setattr(
        phase08_validation,
        '_v3_run_qualification_command',
        run,
    )

    commands, unused_install = (
        phase08_validation._v3_qualification_commands(tmp_path)
    )

    assert commands[-1] == {
        'identifier': 'boundary_observer_smoke',
        'passed': False,
        'output_tail': '',
    }
    assert observed[-1] == 'boundary_observer_smoke'
    assert 'launch_arguments' not in observed


def test_v3_freeze_enforces_the_full_m5_requalification(
    tmp_path,
    monkeypatch,
):
    """The clean freeze cannot bypass repeated build/dry-run evidence."""
    root = tmp_path / 'evidence'
    selected = {
        'candidate_id': 'V3-C0',
        'eligible': True,
        'end_to_end_success_count': 10,
        'behavior_contract_pass_count': 10,
        'local_escape_success_rate': 1.0,
        'minimum_family_success_rate': 1.0,
        'escape_time_p95_sec': 10.0,
        'escape_time_median_sec': 9.0,
        'median_orbit_count': 1.0,
        'revisit_rate': 0.0,
        'median_convergence_time_sec': 20.0,
        'median_path_length_m': 2.0,
    }
    qualification = phase08_validation._v3_write_state(
        root,
        'qualification',
        {'passed': True, 'repository': {}},
    )
    development = phase08_validation._v3_write_state(
        root,
        'development',
        {
            'passed': True,
            'qualification_state_sha256': qualification['state_sha256'],
            'selected_candidate': selected,
            'candidates': [selected],
        },
    )
    suite_path = tmp_path / 'phase08_v3_suite.json'
    commitment_path = tmp_path / 'phase08_v3_commitment.json'
    frozen_path = tmp_path / 'phase08_v3_frozen.yaml'
    selection_path = tmp_path / 'phase08_v3_selection.json'
    freeze_path = tmp_path / 'phase08_v3_freeze.json'
    suite_bytes = b'{"cases":[]}'
    phase08_validation.atomic_bytes(suite_path, suite_bytes)
    historical = {'phase08_v3_activation.yaml': 'c' * 64}
    commitment = {
        'schema_version': 1,
        'generator_version': 'test',
        'scenario_schema_version': 4,
        'counts': {
            'unique': 70,
            'holdout': 20,
            'validation': 50,
            'reproducibility': 10,
        },
        'family_counts': {},
        'historical_exclusion_hashes': historical,
        'suite_sha256': phase08_validation._sha256_bytes(suite_bytes),
        'population_visibility': (
            'researcher_visible_before_activation'
        ),
        'selection_blind': False,
        'precommit_mechanism': 'canonical_json_sha256',
    }
    commitment['commitment_sha256'] = (
        phase08_validation.omission_sha256(
            commitment,
            'commitment_sha256',
        )
    )
    phase08_validation.atomic_json(commitment_path, commitment)
    phase08_validation._v3_write_state(
        root,
        'prepare',
        {
            'passed': True,
            'commitment_sha256': commitment['commitment_sha256'],
            'suite_sha256': commitment['suite_sha256'],
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRECOMMITTED_SUITE_PATH',
        suite_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_COMMITMENT_PATH',
        commitment_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_FROZEN_PATH',
        frozen_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_SELECTION_PATH',
        selection_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_FREEZE_PATH',
        freeze_path,
    )
    snapshot_checks = []

    def verify_snapshot(snapshot, *, require_clean=True):
        del snapshot
        snapshot_checks.append(require_clean)

    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_repository_snapshot',
        verify_snapshot,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_assert_worktree_changes',
        lambda *unused: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    monkeypatch.setattr(
        phase08_validation,
        '_run_functional_tests',
        lambda: {'passed': True, 'return_code': 0},
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_historical_case_keys',
        lambda: (set(), historical),
    )
    snapshot = {
        'commit': 'a' * 40,
        'tree': 'b' * 40,
        'clean': False,
        'input_hashes': {},
        'runtime_inputs_sha256': phase08_validation.canonical_sha256({}),
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: snapshot,
    )
    observed = []

    def qualify(
        evidence_root,
        directory_name='qualification',
        *,
        require_frozen=False,
    ):
        observed.append((directory_name, require_frozen))
        directory = Path(evidence_root) / directory_name
        for name, count in (('activation', 10), ('development', 10)):
            phase08_validation.atomic_yaml(
                directory / f'{name}_dry_run.yaml',
                {
                    'resolved_run_count': count,
                    'unsupported_count': 0,
                    'scenario_schema_version': 4,
                },
            )
        return ([{'passed': True}], directory / 'install')

    monkeypatch.setattr(
        phase08_validation,
        '_v3_qualification_commands',
        qualify,
    )
    frozen = {
        'schema_version': 1,
        'profile_id': selected['candidate_id'],
        'launch_overrides': dict(
            phase08_validation.V3_CANDIDATES[0]['launch_overrides']
        ),
    }
    frozen['sha256'] = phase08_validation.canonical_sha256(
        frozen['launch_overrides']
    )
    selection = {
        'schema_version': 1,
        'selected_candidate': selected,
        'candidate_results': [selected],
        'selection_key': list(
            phase08_validation._v3_selection_key(selected)
        ),
    }
    phase08_validation.atomic_yaml(frozen_path, frozen)
    phase08_validation.atomic_json(selection_path, selection)

    state = phase08_validation.run_v3_freeze('test', root)

    assert development['state_sha256'] == state[
        'development_state_sha256'
    ]
    assert observed == [('freeze_qualification', True)]
    assert state['passed'] is True
    assert state['requalification']['functional_tests']['passed'] is True
    assert freeze_path.is_file()
    assert snapshot_checks == [False]


def test_v3_seal_rerun_uses_immutable_state_fast_path(
    tmp_path,
    monkeypatch,
):
    """Never reread or overwrite sealed artifacts after state publication."""
    freeze = phase08_validation._v3_write_state(
        tmp_path,
        'freeze',
        {
            'passed': True,
            'operator': 'test',
        },
    )
    contract_state = phase08_validation._v3_write_state(
        tmp_path,
        'contract',
        {
            'passed': True,
            'operator': 'test',
            'freeze_state_sha256': freeze['state_sha256'],
            'contract_sha256': 'c' * 64,
        },
    )
    contract = {
        'contract_sha256': 'c' * 64,
        'execution_repository': {
            'commit': 'a' * 40,
            'tree': 'b' * 40,
        },
    }
    verified = []
    published = []
    monkeypatch.setattr(
        phase08_validation,
        '_v3_assert_worktree_changes',
        lambda *unused: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_runtime_contract',
        lambda root, observed_freeze, state, require_clean: (
            verified.append(
                (root, observed_freeze, state, require_clean)
            )
            or contract
        ),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_publish_sealed_durable_freeze',
        lambda observed_freeze, observed_contract: published.append(
            (observed_freeze, observed_contract)
        ),
    )

    result = phase08_validation.run_v3_seal('test', tmp_path)

    assert result == contract_state
    assert verified == [
        (tmp_path, freeze, contract_state, False),
    ]
    assert published == [(freeze, contract)]


def test_v3_freeze_rerun_recovers_missing_durable_projection(
    tmp_path,
    monkeypatch,
):
    """Recover a crash after external state but before tracked projection."""
    freeze_path = tmp_path / 'phase08_v3_freeze.json'
    monkeypatch.setattr(
        phase08_validation,
        'V3_FREEZE_PATH',
        freeze_path,
    )
    state = phase08_validation._v3_write_state(
        tmp_path,
        'freeze',
        {
            'passed': True,
            'operator': 'test',
        },
    )
    expected = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'recovered': True,
    }
    monkeypatch.setattr(
        phase08_validation,
        '_v3_durable_freeze_document',
        lambda *unused, **unused_keywords: expected,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_assert_worktree_changes',
        lambda *unused: None,
    )
    verified = []

    def verify(observed, *, require_clean=True):
        assert json.loads(freeze_path.read_text(encoding='utf-8')) == expected
        verified.append((observed, require_clean))

    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_freeze_inputs',
        verify,
    )

    result = phase08_validation.run_v3_freeze('test', tmp_path)

    assert result == state
    assert verified == [(state, False)]


def test_v3_qualification_rejects_historical_hash_drift(
    tmp_path,
    monkeypatch,
):
    """Detect exclusion-input drift before any activation run."""
    root = tmp_path / 'evidence'
    suite_path = tmp_path / 'phase08_v3_suite.json'
    commitment_path = tmp_path / 'phase08_v3_commitment.json'
    suite_bytes = b'{"cases":[]}'
    phase08_validation.atomic_bytes(suite_path, suite_bytes)
    commitment = {
        'schema_version': 1,
        'generator_version': 'test',
        'scenario_schema_version': 4,
        'counts': {
            'unique': 70,
            'holdout': 20,
            'validation': 50,
            'reproducibility': 10,
        },
        'family_counts': {},
        'historical_exclusion_hashes': {'before': 'a' * 64},
        'suite_sha256': phase08_validation._sha256_bytes(suite_bytes),
        'population_visibility': (
            'researcher_visible_before_activation'
        ),
        'selection_blind': False,
        'precommit_mechanism': 'canonical_json_sha256',
    }
    commitment['commitment_sha256'] = (
        phase08_validation.omission_sha256(
            commitment,
            'commitment_sha256',
        )
    )
    phase08_validation.atomic_json(commitment_path, commitment)
    recovery = {
        'kind': 'contact_probe_instrumentation_contamination',
        'superseded_evidence_root': str(tmp_path / 'v3a'),
        'correction_audit_path': str(tmp_path / 'audit.json'),
    }
    phase08_validation._v3_write_state(
        root,
        'prepare',
        {
            'passed': True,
            'operator': 'test',
            'lineage_id': 'phase08-v3b',
            'recovery': recovery,
            'suite_sha256': commitment['suite_sha256'],
            'commitment_sha256': commitment['commitment_sha256'],
            'repository': {},
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_PRECOMMITTED_SUITE_PATH',
        suite_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        'V3_COMMITMENT_PATH',
        commitment_path,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_assert_worktree_changes',
        lambda *unused: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_repository_snapshot',
        lambda *unused, **kwargs: None,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_harness_recovery_proof',
        lambda *unused, **unused_keywords: recovery,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_active_processes',
        lambda: [],
    )
    monkeypatch.setattr(
        phase08_validation.shutil,
        'disk_usage',
        lambda unused: SimpleNamespace(free=10 ** 15),
    )
    monkeypatch.setattr(
        phase08_validation,
        '_run_functional_tests',
        lambda: {'passed': True, 'return_code': 0},
    )

    def history(include_v3_development=True):
        if include_v3_development:
            return set(), {'after': 'c' * 64}
        return set(), {}

    monkeypatch.setattr(
        phase08_validation,
        '_v3_historical_case_keys',
        history,
    )

    def qualify(evidence_root):
        directory = Path(evidence_root) / 'qualification'
        for name, count in (('activation', 10), ('development', 10)):
            phase08_validation.atomic_yaml(
                directory / f'{name}_dry_run.yaml',
                {
                    'resolved_run_count': count,
                    'unsupported_count': 0,
                    'scenario_schema_version': 4,
                },
            )
        return ([{'passed': True}], directory / 'install')

    monkeypatch.setattr(
        phase08_validation,
        '_v3_qualification_commands',
        qualify,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_repository_snapshot',
        lambda **unused: {
            'commit': 'a' * 40,
            'tree': 'b' * 40,
            'clean': False,
            'input_hashes': {},
            'runtime_inputs_sha256': phase08_validation.canonical_sha256({}),
        },
    )

    state = phase08_validation.run_v3_qualify('test', root)

    assert state['passed'] is False
    assert any(
        'historical exclusion hashes differ' in reason
        for reason in state['reasons']
    )


def _v3_acceptance_record(index, family, family_index):
    allocation = phase08_validation.V3_FAMILY_ALLOCATION[family]
    escape = family_index < allocation['escape_attempt']
    revisit = family_index < phase08_validation.V3_REVISIT_COUNTS[family]
    assist = family == 'lifecycle' and family_index < 6
    merge = family == 'lifecycle' and family_index < 4
    success, applicability = phase08_validation._v3_case_success(
        f'v3-test-{index:02d}',
        escape,
        revisit,
        False,
        merge=merge,
        assist=assist,
    )
    partition = (
        'holdout'
        if family_index < allocation['holdout']
        else 'validation'
    )
    case_key = f'{index + 1:064x}'
    truth_hash = f'{index + 1000:064x}'
    success['ground_truth']['aggregate_field'] = {
        'result_sha256': truth_hash,
    }
    disturbances = {
        'sensor_noise': {'model': 'none', 'bound': 0.0},
        'sensor_delay_sec': 0.0,
        'pose_delay_sec': 0.0,
    }
    metrics = {
        'collision': _metric(False),
        'controller_success': _metric(True),
        'simulation_ground_truth_success': _metric(True),
        'timeout': _metric(False),
        'failsafe': _metric(False),
        'escape_time': (
            _metric(10.0) if escape
            else _metric(None, 'not_applicable')
        ),
        'approximate_orbit_count': (
            _metric([1.0]) if escape
            else _metric(None, 'not_applicable')
        ),
        'revisit_count': _metric(0),
        'convergence_time': _metric(20.0),
        'path_length': _metric(2.0),
        'final_aggregate_target_distance': _metric(0.1),
        'fill_count': _metric(1 if escape else 0),
        'merge_count': _metric(1 if merge else 0),
        'observed_raw_cost_delay': _metric(None, 'not_applicable'),
        'observed_source_cost_delay': _metric(None, 'not_applicable'),
        'observed_pose_delay': _metric(None, 'not_applicable'),
    }
    attempts = []
    if escape:
        attempts.append({
            'outcome': 'success',
            'duration': _metric(10.0),
            'orbit_count': _metric(1.0),
            'assisted': assist,
        })
    outcomes = {
        'controller_goal': 'passed',
        'simulation_ground_truth': 'passed',
        'expected_terminal_state_passed': True,
        'required_state_path_passed': True,
        'required_event_sequence_passed': True,
        'required_events_passed': True,
        'forbidden_states_absent': True,
        'forbidden_events_absent': True,
        'minimum_saturation_samples_passed': True,
        'collision_expectation_passed': True,
    }
    record = {
        'run_id': f'v3-test-{index:02d}-run',
        'case_id': f'v3-test-{index:02d}',
        'case_key': case_key,
        'acceptance_family': family,
        'acceptance_partition': partition,
        'disturbances': disturbances,
        'metric_applicability': applicability,
        'recording_complete': True,
        'cleanup': {'passed': True},
        'record_process': {'timed_out': False},
        'classification': {
            'infrastructure_status': 'completed',
            'passed': True,
            'predicate_results': {
                'controller_goal': True,
                'ground_truth_goal': True,
            },
            'result_scopes': {
                'full_lifecycle': {
                    'passed': True,
                    'anchor_observed': True,
                    'required_predicates': list(
                        success['result_scopes'][
                            'full_lifecycle'
                        ]['all_of']
                    ),
                    'predicate_results': {
                        name: True for name in success[
                            'result_scopes'
                        ]['full_lifecycle']['all_of']
                    },
                },
            },
        },
        'outcomes': {
            **outcomes,
            'observed_state_sequence': list(
                success['controller']['required_state_path']
            ),
            'observed_events': list(
                success['controller']['required_events']
            ),
        },
        'analysis_error': None,
        'resolved_scenario_sha256': f'{index + 2000:064x}',
        'analysis_summary_sha256': f'{index + 3000:064x}',
        'analysis_completeness': {
            'status': 'complete',
            'raw_bag_sha256': {
                str(V1_REPLAY_FIXTURE): (
                    phase08_validation.file_sha256(V1_REPLAY_FIXTURE)
                ),
            },
        },
        'analysis': {
            'analysis_status': 'complete',
            'acceptance_family': family,
            'acceptance_partition': partition,
            'metric_applicability': json.loads(json.dumps(applicability)),
            'applicability_integrity': {'passed': True},
            'aggregate_truth_result_sha256': truth_hash,
            'escape_attempts': attempts,
            'metrics': metrics,
        },
    }
    contract_case = {
        'case_id': record['case_id'],
        'case_key': case_key,
        'acceptance_family': family,
        'acceptance_partition': partition,
        'disturbances': json.loads(json.dumps(disturbances)),
        'metric_applicability': json.loads(json.dumps(applicability)),
        'success': success,
    }
    return record, contract_case


def _passing_v3_unique_fixture():
    records = []
    resolved_cases = []
    index = 0
    for family, allocation in (
        phase08_validation.V3_FAMILY_ALLOCATION.items()
    ):
        for family_index in range(allocation['unique']):
            record, contract_case = _v3_acceptance_record(
                index,
                family,
                family_index,
            )
            records.append(record)
            resolved_cases.append(contract_case)
            index += 1
    contract = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'resolved_cases': resolved_cases,
        'unique_case_keys': sorted(
            record['case_key'] for record in records
        ),
        'partition_case_keys': {
            partition: sorted(
                record['case_key']
                for record in records
                if record['acceptance_partition'] == partition
            )
            for partition in ('holdout', 'validation')
        },
        'family_allocation': json.loads(json.dumps(
            phase08_validation.V3_FAMILY_ALLOCATION
        )),
    }
    contract['contract_sha256'] = phase08_validation.omission_sha256(
        contract,
        'contract_sha256',
    )
    return records, contract


def _v3_gate_map(evaluation):
    return {gate['gate']: gate for gate in evaluation['gates']}


def test_v3_unique_gates_accept_complete_bound_fixture():
    """Keep every conjunctive v3 gate reachable by valid evidence."""
    records, contract = _passing_v3_unique_fixture()

    evaluation = phase08_validation.evaluate_v3_unique_gates(
        records,
        contract,
    )

    assert evaluation['passed'] is True
    assert all(gate['passed'] for gate in evaluation['gates'])


@pytest.mark.parametrize(
    'mutation',
    ['duplicate_case_key', 'unsealed_case_key', 'family_drift'],
)
def test_v3_unique_gates_enforce_exact_sealed_population(mutation):
    """Bind the exact 70-case identity and family allocation to the seal."""
    records, contract = _passing_v3_unique_fixture()
    if mutation == 'duplicate_case_key':
        records[-1]['case_key'] = records[0]['case_key']
    elif mutation == 'unsealed_case_key':
        records[-1]['case_key'] = 'f' * 64
    else:
        records[-1]['acceptance_family'] = 'ordered_two_source'

    evaluation = phase08_validation.evaluate_v3_unique_gates(
        records,
        contract,
    )

    assert evaluation['passed'] is False


@pytest.mark.parametrize(
    ('attempt_field', 'gate_name'),
    [
        ('duration', 'escape_duration'),
        ('orbit_count', 'orbit_count'),
    ],
)
def test_v3_unique_gates_reject_unavailable_success_evidence(
    attempt_field,
    gate_name,
):
    """An applicable successful attempt cannot lose scalar evidence."""
    records, contract = _passing_v3_unique_fixture()
    designated = next(
        record for record in records
        if record['metric_applicability']['escape_attempt']
    )
    designated['analysis']['escape_attempts'][0][attempt_field] = (
        _metric(None, 'unavailable')
    )

    evaluation = phase08_validation.evaluate_v3_unique_gates(
        records,
        contract,
    )
    gates = _v3_gate_map(evaluation)

    assert evaluation['passed'] is False
    assert gates[gate_name]['passed'] is False
    assert gates['metric_applicability']['passed'] is False


def _write_passing_v3_report_fixture(root, monkeypatch):
    outputs = root / 'outputs'
    outputs.mkdir()
    for name, filename in {
        'V3_CONTRACT_PATH': 'contract.json',
        'V3_GATE_RESULTS_PATH': 'gates.json',
        'V3_MANIFEST_PATH': 'manifest.json',
        'V3_REPORT_PATH': 'report.md',
        'V3_FAILURE_PATH': 'failure.md',
    }.items():
        monkeypatch.setattr(
            phase08_validation,
            name,
            outputs / filename,
        )
    contract_document = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
    }
    contract_document['contract_sha256'] = (
        phase08_validation.omission_sha256(
            contract_document,
            'contract_sha256',
        )
    )
    phase08_validation.atomic_json(
        phase08_validation.V3_CONTRACT_PATH,
        contract_document,
    )
    prepare = phase08_validation._v3_write_state(
        root,
        'prepare',
        {'passed': True},
    )
    qualification = phase08_validation._v3_write_state(
        root,
        'qualification',
        {
            'passed': True,
            'prepare_state_sha256': prepare['state_sha256'],
        },
    )
    activation = phase08_validation._v3_write_state(
        root,
        'activation',
        {
            'passed': True,
            'qualification_state_sha256': (
                qualification['state_sha256']
            ),
            'contract_pass_count': 10,
        },
    )
    development = phase08_validation._v3_write_state(
        root,
        'development',
        {
            'passed': True,
            'activation_state_sha256': activation['state_sha256'],
            'selected_candidate': {'candidate_id': 'V3-C0'},
        },
    )
    freeze = phase08_validation._v3_write_state(
        root,
        'freeze',
        {
            'passed': True,
            'development_state_sha256': development['state_sha256'],
        },
    )
    contract = phase08_validation._v3_write_state(
        root,
        'contract',
        {
            'passed': True,
            'freeze_state_sha256': freeze['state_sha256'],
            'contract_sha256': contract_document['contract_sha256'],
        },
    )
    holdout = phase08_validation._v3_write_state(
        root,
        'holdout',
        {
            'passed': True,
            'contract_state_sha256': contract['state_sha256'],
            'end_to_end_success_count': 20,
        },
    )
    unique_gates = [
        phase08_validation._v3_gate(
            identifier,
            True,
            'synthetic-pass',
            'synthetic-pass',
        )
        for identifier in (
            'completeness_analysis_integrity',
            'behavior_contracts',
            'end_to_end',
            'family_floors',
            'local_escape',
            'escape_duration',
            'orbit_count',
            'revisit',
            'metric_applicability',
        )
    ]
    validation = phase08_validation._v3_write_state(
        root,
        'validation',
        {
            'passed': True,
            'holdout_state_sha256': holdout['state_sha256'],
            'contract_state_sha256': contract['state_sha256'],
            'unique_gate_evaluation': {
                'passed': True,
                'gates': unique_gates,
                'confidence_intervals': {},
            },
        },
    )
    phase08_validation._v3_write_state(
        root,
        'reproducibility',
        {
            'passed': True,
            'validation_state_sha256': validation['state_sha256'],
            'contract_state_sha256': contract['state_sha256'],
            'evaluation': {'passed': True, 'repeat_count': 10},
        },
    )


@pytest.mark.parametrize(
    'missing',
    [
        'qualification',
        'freeze',
        'contract',
        'contract_document',
        'holdout',
        'validation',
        'reproducibility',
    ],
)
def test_v3_report_fails_closed_when_required_state_is_missing(
    tmp_path,
    monkeypatch,
    missing,
):
    """A partial state chain can never produce simulation readiness."""
    _write_passing_v3_report_fixture(tmp_path, monkeypatch)
    if missing == 'contract_document':
        phase08_validation.V3_CONTRACT_PATH.unlink()
    else:
        phase08_validation._v3_state_path(tmp_path, missing).unlink()

    result = phase08_validation.run_v3_report('test', tmp_path)

    assert result['simulation_ready'] is False
    assert result['outcome'] == 'failed'


def test_v3_terminal_report_rerun_never_overwrites_drift(
    tmp_path,
    monkeypatch,
):
    """A terminal rerun verifies immutable outputs before returning."""
    _write_passing_v3_report_fixture(tmp_path, monkeypatch)
    phase08_validation._v3_state_path(
        tmp_path,
        'qualification',
    ).unlink()
    phase08_validation.run_v3_report('test', tmp_path)
    contract = json.loads(
        phase08_validation.V3_CONTRACT_PATH.read_text(encoding='utf-8')
    )
    failure_text = phase08_validation.V3_FAILURE_PATH.read_text(
        encoding='utf-8'
    )
    assert (
        f'Contract: `{contract["contract_sha256"]}`.'
        in failure_text
    )
    gate_results = json.loads(
        phase08_validation.V3_GATE_RESULTS_PATH.read_text(
            encoding='utf-8'
        )
    )
    gate_results['outcome'] = 'tampered'
    phase08_validation.atomic_json(
        phase08_validation.V3_GATE_RESULTS_PATH,
        gate_results,
    )

    with pytest.raises(RuntimeError, match='terminal artifact drifted'):
        phase08_validation.run_v3_report('test', tmp_path)


def test_v3_passing_terminal_rejects_late_failure_report(
    tmp_path,
    monkeypatch,
):
    """A passing immutable terminal state requires failure-report absence."""
    outputs = tmp_path / 'outputs'
    outputs.mkdir()
    for name, filename in {
        'V3_GATE_RESULTS_PATH': 'gates.json',
        'V3_MANIFEST_PATH': 'manifest.json',
        'V3_REPORT_PATH': 'report.md',
        'V3_FAILURE_PATH': 'failure.md',
    }.items():
        monkeypatch.setattr(
            phase08_validation,
            name,
            outputs / filename,
        )
    phase08_validation.atomic_json(
        phase08_validation.V3_GATE_RESULTS_PATH,
        {'simulation_ready': True},
    )
    phase08_validation.atomic_json(
        phase08_validation.V3_MANIFEST_PATH,
        {'simulation_ready': True},
    )
    phase08_validation.atomic_bytes(
        phase08_validation.V3_REPORT_PATH,
        b'passing report\n',
    )
    phase08_validation._v3_write_state(
        tmp_path,
        'terminal',
        {
            'passed': True,
            'operator': 'test',
            'gate_results_sha256': phase08_validation.file_sha256(
                phase08_validation.V3_GATE_RESULTS_PATH
            ),
            'manifest_sha256': phase08_validation.file_sha256(
                phase08_validation.V3_MANIFEST_PATH
            ),
            'report_sha256': phase08_validation.file_sha256(
                phase08_validation.V3_REPORT_PATH
            ),
            'failure_report_sha256': None,
        },
    )
    phase08_validation.atomic_bytes(
        phase08_validation.V3_FAILURE_PATH,
        b'contradictory failure\n',
    )

    with pytest.raises(RuntimeError, match='contradictory failure report'):
        phase08_validation.run_v3_report('test', tmp_path)


def _v3_repro_record(index, *, repeat=False, direct_goal=False):
    case_key = f'{index + 1000:064x}'
    metrics = {
        'controller_success': _metric(True),
        'simulation_ground_truth_success': _metric(True),
        'timeout': _metric(False),
        'failsafe': _metric(False),
        'collision': _metric(False),
        'escape_time': (
            _metric(None, 'not_applicable')
            if direct_goal else _metric(10.0)
        ),
        'approximate_orbit_count': (
            _metric(None, 'not_applicable')
            if direct_goal else _metric([1.0])
        ),
        'convergence_time': _metric(20.0),
        'path_length': _metric(2.0),
        'final_aggregate_target_distance': _metric(0.1),
    }
    record = {
        'run_id': f'repro-{index}-{"repeat" if repeat else "reference"}',
        'case_id': f'repro-{index}-{"repeat" if repeat else "reference"}',
        'case_key': (
            f'{index + 2000:064x}' if repeat else case_key
        ),
        'recording_complete': True,
        'cleanup': {'passed': True},
        'record_process': {'timed_out': False},
        'classification': {
            'infrastructure_status': 'completed',
            'passed': True,
            'result_scopes': {
                'full_lifecycle': {'passed': True},
            },
        },
        'outcomes': {
            'controller_goal': 'passed',
            'simulation_ground_truth': 'passed',
            'expected_terminal_state_passed': True,
            'required_state_path_passed': True,
            'required_event_sequence_passed': True,
            'required_events_passed': True,
            'forbidden_states_absent': True,
            'forbidden_events_absent': True,
            'collision_expectation_passed': True,
        },
        'analysis_error': None,
        'analysis': {
            'analysis_status': 'complete',
            'escape_attempts': [],
            'metrics': metrics,
        },
    }
    if repeat:
        record['repeat_reference'] = {'case_key': case_key}
    return record


def _v3_repro_fixture(*, direct_goal=False):
    references = [
        _v3_repro_record(index, direct_goal=direct_goal)
        for index in range(10)
    ]
    repeats = [
        _v3_repro_record(
            index,
            repeat=True,
            direct_goal=direct_goal,
        )
        for index in range(10)
    ]
    return repeats, references


def test_v3_reproducibility_accepts_paired_direct_goal_na():
    """Predeclared direct-goal escape and orbit N/A values agree."""
    repeats, references = _v3_repro_fixture(direct_goal=True)

    evaluation = phase08_validation.evaluate_v3_reproducibility(
        repeats,
        references,
    )

    assert evaluation['passed'] is True
    assert all(item['passed'] for item in evaluation['results'])


@pytest.mark.parametrize(
    'metric_name',
    [
        'controller_success',
        'simulation_ground_truth_success',
        'timeout',
        'failsafe',
        'collision',
    ],
)
def test_v3_reproducibility_rejects_unavailable_categorical(metric_name):
    """Equal unavailable categorical values are not reproducible evidence."""
    repeats, references = _v3_repro_fixture()
    for record in (references[0], repeats[0]):
        record['analysis']['metrics'][metric_name] = _metric(
            None,
            'unavailable',
        )

    evaluation = phase08_validation.evaluate_v3_reproducibility(
        repeats,
        references,
    )

    assert evaluation['passed'] is False
    assert evaluation['results'][0]['passed'] is False


@pytest.mark.parametrize(
    'defect',
    ['missing_required_events', 'integrity_failure'],
)
def test_v3_reproducibility_rejects_missing_evidence(defect):
    """Required coverage and repeat integrity must be positively valid."""
    repeats, references = _v3_repro_fixture()
    if defect == 'missing_required_events':
        for record in (references[0], repeats[0]):
            record['outcomes'].pop('required_events_passed')
    else:
        repeats[0]['cleanup']['passed'] = False

    evaluation = phase08_validation.evaluate_v3_reproducibility(
        repeats,
        references,
    )

    assert evaluation['passed'] is False
    assert evaluation['results'][0]['passed'] is False


def _v3_serial_suite(tmp_path, case_ids, partition='activation'):
    document = yaml.safe_load(
        phase08_validation.V3_ACTIVATION_PATH.read_text(encoding='utf-8')
    )
    template = document['cases'][0]
    cases = []
    for index, case_id in enumerate(case_ids):
        case = json.loads(json.dumps(template))
        case['case_id'] = case_id
        case['success']['controller']['contract_id'] = case_id
        case['acceptance_partition'] = partition
        if partition == 'reproducibility':
            case['repeat_reference'] = {
                'partition': 'holdout',
                'case_key': f'{index + 5000:064x}',
            }
        cases.append(case)
    document['suite_id'] = f'v3_serial_{partition}_test'
    document['execution']['gazebo_gui'] = False
    document['cases'] = cases
    path = tmp_path / f'{document["suite_id"]}.yaml'
    path.write_text(yaml.safe_dump(document), encoding='utf-8')
    return path


def _v3_serial_record(
    case_id,
    *,
    status='passed',
    cleanup=True,
    collision=False,
    run_directory=None,
):
    infrastructure = (
        'infrastructure_invalid'
        if status == 'infrastructure_invalid'
        else 'completed'
    )
    return {
        'run_id': f'{case_id}-run',
        'run_directory': (
            str(run_directory) if run_directory is not None else None
        ),
        'case_id': case_id,
        'recording_complete': infrastructure == 'completed',
        'cleanup': {'passed': cleanup},
        'record_process': {'timed_out': False},
        'classification': {
            'status': status,
            'passed': status == 'passed',
            'infrastructure_status': infrastructure,
        },
        'analysis_error': None,
        'analysis': {
            'analysis_status': 'complete',
            'metrics': {
                'collision': _metric(collision),
                'controller_success': _metric(status == 'passed'),
                'simulation_ground_truth_success': _metric(
                    status == 'passed'
                ),
            },
        },
    }


def _v3_applicability_partial_record(
    tmp_path,
    case_id='behavior-miss',
    *,
    run_id=None,
):
    """Build a complete record whose only analysis miss is applicability."""
    run_directory = tmp_path / f'{case_id}-run-directory'
    raw_bag = run_directory / 'bag/bag_0.db3'
    raw_bag.parent.mkdir(parents=True, exist_ok=True)
    raw_bag.write_bytes(b'complete retained bag')
    applicability = {
        'escape_attempt': False,
        'escape_duration': False,
        'orbit_count': False,
        'revisit': False,
        'delay': False,
        'saturation': False,
    }
    metrics = {
        'collision': _metric(False),
        'timeout': _metric(False),
        'failsafe': _metric(False),
        'controller_success': _metric(True),
        'simulation_ground_truth_success': _metric(True),
        'escape_attempt_count': _metric(None, 'not_applicable'),
    }
    run_id = run_id or f'{case_id}-run'
    analysis = {
        'run_id': run_id,
        'analysis_status': 'partial',
        'metric_applicability': applicability,
        'applicability_integrity': {
            'passed': False,
            'reasons': [
                'escape occurred in a case declared not applicable',
            ],
        },
        'metrics': metrics,
    }
    completeness = {
        'run_id': run_id,
        'status': 'partial',
        'stored_phase05_passed': True,
        'fresh_phase05_validation': {
            'passed': True,
            'failures': [],
        },
        'critical_inputs': {
            'readiness': True,
            'cost': True,
            'pose': True,
            'control': True,
        },
        'recording_failures': [],
        'analysis_failures': [],
        'metric_validity': {
            name: metric['status']
            for name, metric in metrics.items()
        },
        'raw_bag_sha256': {
            str(raw_bag): phase08_validation.file_sha256(raw_bag),
        },
    }
    resolved_path = run_directory / 'resolved_scenario.yaml'
    analysis_path = (
        run_directory / 'analysis/phase08/summary_metrics.json'
    )
    completeness_path = (
        run_directory
        / 'analysis/phase08/analysis_completeness.json'
    )
    phase08_validation.atomic_yaml(
        resolved_path,
        {'case_id': case_id, 'run_id': run_id},
    )
    phase08_validation.atomic_json(analysis_path, analysis)
    phase08_validation.atomic_json(completeness_path, completeness)
    phase08_validation.atomic_json(
        run_directory / 'completeness.json',
        {'run_id': run_id, 'passed': True},
    )
    phase08_validation.atomic_yaml(
        run_directory / 'bag/metadata.yaml',
        {'rosbag2_bagfile_information': {'storage_identifier': 'sqlite3'}},
    )
    return {
        'run_id': run_id,
        'run_directory': str(run_directory),
        'case_id': case_id,
        'recording_complete': True,
        'cleanup': {'passed': True},
        'record_process': {'timed_out': False},
        'classification': {
            'status': 'failed',
            'passed': False,
            'infrastructure_status': 'completed',
            'predicate_results': {
                'recording_complete': True,
                'cleanup_complete': True,
                'collision_expectation': True,
                'controller_goal': True,
                'ground_truth_goal': True,
                'expected_terminal_state': True,
                'required_state_path': False,
                'required_events': True,
                'no_forbidden_states': False,
                'no_forbidden_events': False,
            },
        },
        'outcomes': {
            'observed_state_sequence': [
                'SEARCH',
                'VERIFY_EXTREMUM',
                'DESIGN_OR_MERGE_FILL',
                'ESCAPE_REPULSE',
            ],
        },
        'analysis_error': None,
        'metric_applicability': applicability,
        'resolved_scenario_sha256': (
            phase08_validation.file_sha256(resolved_path)
        ),
        'analysis_summary_sha256': (
            phase08_validation.file_sha256(analysis_path)
        ),
        'analysis_completeness_sha256': (
            phase08_validation.file_sha256(completeness_path)
        ),
        'success_contract': {
            'controller': {
                'expected_verification_outcome': 'goal',
            },
        },
        'analysis': analysis,
        'analysis_completeness': completeness,
    }


def _install_v3_serial_mocks(monkeypatch, record_factory):
    calls = []
    attempts = Counter()
    monkeypatch.setattr(
        phase08_validation,
        '_git',
        lambda *unused: '',
    )

    def fake_execute(
        suite_path,
        operator,
        *,
        case_ids,
        runs_root,
        summary_output,
    ):
        del suite_path, operator, runs_root
        assert len(case_ids) == 1
        case_id = case_ids[0]
        attempts[case_id] += 1
        calls.append(list(case_ids))
        summary = {
            'schema_version': 1,
            'test_attempt': attempts[case_id],
            'runs': [{'case_id': case_id}],
        }
        phase08_validation.atomic_yaml(summary_output, summary)
        return summary

    def fake_analyze(summary):
        case_id = summary['runs'][0]['case_id']
        return [
            record_factory(case_id, summary['test_attempt'])
        ]

    monkeypatch.setattr(
        phase08_validation,
        'execute_suite',
        fake_execute,
    )
    monkeypatch.setattr(
        phase08_validation,
        '_analyze_scenario_summary',
        fake_analyze,
    )
    return calls


def test_v3_serial_activation_dispatches_one_case_and_keeps_valid_miss(
    tmp_path,
    monkeypatch,
):
    """A behavioral miss is final evidence, not a serial-stage stop."""
    case_ids = ['serial-a', 'serial-b', 'serial-c']
    suite = _v3_serial_suite(tmp_path, case_ids)

    def record_factory(case_id, attempt):
        del attempt
        return _v3_serial_record(
            case_id,
            status='failed' if case_id == case_ids[0] else 'passed',
        )

    calls = _install_v3_serial_mocks(monkeypatch, record_factory)
    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
        )
    )

    assert calls == [[case_id] for case_id in case_ids]
    assert [record['classification']['status'] for record in records] == [
        'failed',
        'passed',
        'passed',
    ]
    assert progress['stopped_early_reason'] is None
    assert progress['not_run_slot_ids'] == []


def test_v3_serial_keeps_pure_applicability_behavior_miss(
    tmp_path,
    monkeypatch,
):
    """An applicability-driven partial is final evidence, not a hard stop."""
    case_ids = ['partial-miss', 'serial-b', 'serial-c']
    suite = _v3_serial_suite(tmp_path, case_ids)

    def record_factory(case_id, attempt):
        del attempt
        if case_id == case_ids[0]:
            return _v3_applicability_partial_record(
                tmp_path,
                case_id,
            )
        return _v3_serial_record(case_id)

    calls = _install_v3_serial_mocks(monkeypatch, record_factory)
    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
            allow_pure_applicability_miss=True,
        )
    )

    assert calls == [[case_id] for case_id in case_ids]
    assert len(records) == 3
    assert progress['stopped_early_reason'] is None
    assert progress['not_run_slot_ids'] == []
    assert phase08_validation._v3_record_integrity(
        records[0]
    )['passed'] is False


def test_v3_nonactivation_keeps_applicability_hard_stop(
    tmp_path,
    monkeypatch,
):
    """Never apply a diagnostic exception to another stage."""
    case_ids = ['partial-miss', 'must-not-run']
    suite = _v3_serial_suite(tmp_path, case_ids)
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: (
            _v3_applicability_partial_record(tmp_path, case_id)
            if case_id == case_ids[0]
            else _v3_serial_record(case_id)
        ),
    )

    unused_summary, unused_records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/development',
            'development',
        )
    )

    assert calls == [[case_ids[0]]]
    assert 'analysis is not complete' in progress[
        'stopped_early_reason'
    ]
    assert progress['not_run_slot_ids'] == [case_ids[1]]
    with pytest.raises(RuntimeError, match='diagnostic activation-only'):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'other-evidence',
            tmp_path / 'other-evidence/development',
            'development',
            allow_pure_applicability_miss=True,
        )


def test_v3_pure_applicability_miss_keeps_final_integrity_gate(tmp_path):
    """Change dispatch routing without relabeling the retained record."""
    record = _v3_applicability_partial_record(tmp_path)

    assert phase08_validation._v3_hard_stop_reason(record) is not None
    assert phase08_validation._v3_hard_stop_reason(
        record,
        allow_pure_applicability_miss=True,
    ) is None
    integrity = phase08_validation._v3_record_integrity(record)
    assert integrity['passed'] is False
    assert set(integrity['reasons']) == {
        'analysis is not complete',
        'metric applicability integrity failed',
        'analysis completeness status is not complete',
    }


def test_v3_serial_carries_failed_slot_and_executes_only_unseen_slots(
    tmp_path,
    monkeypatch,
):
    """Bind an original record in place without rerun or rewriting."""
    case_ids = ['carried-failure', 'serial-b', 'serial-c']
    suite = _v3_serial_suite(tmp_path, case_ids)
    carried_record = _v3_applicability_partial_record(
        tmp_path,
        case_ids[0],
    )
    carried_path = tmp_path / 'original_record.json'
    phase08_validation.atomic_json(carried_path, carried_record)
    carried = [{
        'case_id': case_ids[0],
        'record_path': str(carried_path.resolve()),
        'record_sha256': phase08_validation.file_sha256(carried_path),
        'run_directory_manifest': (
            phase08_validation._v3_directory_manifest(
                carried_record['run_directory']
            )
        ),
        'source_lineage_id': 'phase08-v3b',
        'disposition': 'carried_immutable_behavioral_failure',
        'rerun': False,
    }]
    original_bytes = carried_path.read_bytes()

    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
            carried_records=carried,
            required_execution_case_ids=case_ids[1:],
        )
    )

    assert calls == [['serial-b'], ['serial-c']]
    assert records[0] == carried_record
    assert progress['carried_count'] == 1
    assert progress['newly_executed_count'] == 2
    assert progress['carried_record_count'] == 1
    assert progress['new_execution_count'] == 2
    assert progress['carried_records'] == carried
    assert progress['final_record_paths'][case_ids[0]] == str(
        carried_path.resolve()
    )
    assert all(
        attempt['case_id'] != case_ids[0]
        for attempt in progress['attempts']
    )
    assert carried_path.read_bytes() == original_bytes
    aggregate = json.loads(
        (
            tmp_path / 'evidence/activation/records.json'
        ).read_text(encoding='utf-8')
    )
    assert aggregate[0] == {
        'schema_version': 1,
        'case_id': case_ids[0],
        'disposition': 'carried_immutable_behavioral_failure',
        'carried_record': carried[0],
    }
    assert 'analysis' not in aggregate[0]
    attempt_records = json.loads(
        (
            tmp_path / 'evidence/activation/attempt_records.json'
        ).read_text(encoding='utf-8')
    )
    assert [item['case_id'] for item in attempt_records] == case_ids[1:]
    state = {
        'records_path': str(
            tmp_path / 'evidence/activation/records.json'
        ),
        'progress_sha256': progress['progress_sha256'],
        'attempt_records_sha256': phase08_validation.file_sha256(
            tmp_path / 'evidence/activation/attempt_records.json'
        ),
    }
    assert phase08_validation._v3_serial_artifact_errors(
        'activation',
        state,
    ) == []


def test_v3_serial_rejects_carried_record_hash_drift(
    tmp_path,
    monkeypatch,
):
    """Rehash the original carried record on every resume."""
    suite = _v3_serial_suite(tmp_path, ['carried-failure'])
    carried_path = tmp_path / 'original_record.json'
    phase08_validation.atomic_json(
        carried_path,
        _v3_applicability_partial_record(
            tmp_path,
            'carried-failure',
        ),
    )
    carried = [{
        'case_id': 'carried-failure',
        'record_path': str(carried_path),
        'record_sha256': phase08_validation.file_sha256(carried_path),
        'run_directory_manifest': (
            phase08_validation._v3_directory_manifest(
                json.loads(
                    carried_path.read_text(encoding='utf-8')
                )['run_directory']
            )
        ),
    }]
    _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    phase08_validation._v3_execute_serial_slots(
        suite,
        'test',
        tmp_path / 'evidence',
        tmp_path / 'evidence/activation',
        'activation',
        carried_records=carried,
    )
    carried_path.write_text('{}\n', encoding='utf-8')

    with pytest.raises(RuntimeError, match='carried record binding'):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
            carried_records=carried,
        )


def test_v3_serial_requires_exact_new_case_order(
    tmp_path,
    monkeypatch,
):
    """Bind the nine-run completion to the audited IDs and order."""
    case_ids = ['carried-failure', 'serial-b', 'serial-c']
    suite = _v3_serial_suite(tmp_path, case_ids)
    record = _v3_applicability_partial_record(
        tmp_path,
        case_ids[0],
    )
    record_path = tmp_path / 'carried.json'
    phase08_validation.atomic_json(record_path, record)
    carried = [{
        'case_id': case_ids[0],
        'record_path': str(record_path),
        'record_sha256': phase08_validation.file_sha256(record_path),
        'run_directory_manifest': (
            phase08_validation._v3_directory_manifest(
                record['run_directory']
            )
        ),
    }]
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )

    with pytest.raises(RuntimeError, match='IDs/order drifted'):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
            carried_records=carried,
            required_execution_case_ids=list(reversed(case_ids[1:])),
        )

    assert calls == []


@pytest.mark.parametrize('new_case_ids', [['serial-b'], ['serial-b', 'serial-c']])
def test_v3_serial_rehashes_carry_before_dispatch_and_final_reload(
    tmp_path,
    monkeypatch,
    new_case_ids,
):
    """Detect carried-record drift before every dispatch and final load."""
    case_ids = ['carried-failure', *new_case_ids]
    suite = _v3_serial_suite(tmp_path, case_ids)
    record = _v3_applicability_partial_record(
        tmp_path,
        case_ids[0],
    )
    record_path = tmp_path / 'carried.json'
    phase08_validation.atomic_json(record_path, record)
    carried = [{
        'case_id': case_ids[0],
        'record_path': str(record_path),
        'record_sha256': phase08_validation.file_sha256(record_path),
        'run_directory_manifest': (
            phase08_validation._v3_directory_manifest(
                record['run_directory']
            )
        ),
    }]
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    original_execute = phase08_validation.execute_suite

    def execute_and_drift(*args, **kwargs):
        result = original_execute(*args, **kwargs)
        if len(calls) == 1:
            record_path.write_text('{}\n', encoding='utf-8')
        return result

    monkeypatch.setattr(
        phase08_validation,
        'execute_suite',
        execute_and_drift,
    )

    with pytest.raises(RuntimeError, match='carried record binding'):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
            carried_records=carried,
            required_execution_case_ids=new_case_ids,
        )

    assert calls == [['serial-b']]


@pytest.mark.parametrize(
    'defect',
    [
        'analysis_error',
        'phase05_failure',
        'invalid_metric',
        'unavailable_metric',
        'raw_bag_drift',
        'nonbehavior_predicate',
        'missing_applicability_reason',
        'unknown_applicability_reason',
        'missing_critical_input',
        'artifact_drift',
    ],
)
def test_v3_partial_analysis_corruption_still_hard_stops(
    tmp_path,
    defect,
):
    """Only the rigorously complete applicability partial may continue."""
    record = _v3_applicability_partial_record(tmp_path)
    if defect == 'analysis_error':
        record['analysis_error'] = 'RuntimeError: failed analysis'
    elif defect == 'phase05_failure':
        record['analysis_completeness'][
            'fresh_phase05_validation'
        ]['passed'] = False
    elif defect == 'invalid_metric':
        record['analysis']['metrics'][
            'controller_success'
        ]['status'] = 'invalid'
        record['analysis_completeness']['metric_validity'][
            'controller_success'
        ] = 'invalid'
    elif defect == 'unavailable_metric':
        record['analysis']['metrics'][
            'controller_success'
        ]['status'] = 'unavailable'
        record['analysis_completeness']['metric_validity'][
            'controller_success'
        ] = 'unavailable'
    elif defect == 'raw_bag_drift':
        raw_path = Path(next(iter(
            record['analysis_completeness']['raw_bag_sha256']
        )))
        raw_path.write_bytes(b'drifted retained bag')
    elif defect == 'nonbehavior_predicate':
        record['classification']['predicate_results'][
            'recording_complete'
        ] = False
    elif defect == 'missing_applicability_reason':
        record['analysis']['applicability_integrity']['reasons'] = []
    elif defect == 'unknown_applicability_reason':
        record['analysis']['applicability_integrity']['reasons'] = [
            'some other nonempty applicability reason',
        ]
    elif defect == 'missing_critical_input':
        del record['analysis_completeness']['critical_inputs']['pose']
    else:
        run_directory = Path(record['run_directory'])
        (run_directory / 'resolved_scenario.yaml').write_text(
            'case_id: drifted\n',
            encoding='utf-8',
        )

    reason = phase08_validation._v3_hard_stop_reason(
        record,
        allow_pure_applicability_miss=True,
    )

    assert reason is not None
    assert reason.startswith('evidence integrity:')


def test_v3_serial_rechecks_the_qualified_runtime_snapshot(
    tmp_path,
    monkeypatch,
):
    """Bind dispatch and each attempt to the exact qualified input map."""
    suite = _v3_serial_suite(tmp_path, ['snapshot-bound'])
    _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    verified = []
    snapshot = {'runtime_inputs_sha256': 'qualified'}
    monkeypatch.setattr(
        phase08_validation,
        '_v3_verify_repository_snapshot',
        lambda value: verified.append(value),
    )

    phase08_validation._v3_execute_serial_slots(
        suite,
        'test',
        tmp_path / 'evidence',
        tmp_path / 'evidence/activation',
        'activation',
        runtime_snapshot=snapshot,
    )

    assert verified == [snapshot, snapshot]


def test_v3_serial_rehashes_suite_before_every_dispatch(
    tmp_path,
    monkeypatch,
):
    """Stop before a later slot if the resolved suite changes in place."""
    suite = _v3_serial_suite(tmp_path, ['first', 'second'])
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    original_execute = phase08_validation.execute_suite

    def execute_and_drift(*args, **kwargs):
        result = original_execute(*args, **kwargs)
        if len(calls) == 1:
            suite.write_text(
                suite.read_text(encoding='utf-8') + '\n# drift\n',
                encoding='utf-8',
            )
        return result

    monkeypatch.setattr(
        phase08_validation,
        'execute_suite',
        execute_and_drift,
    )

    with pytest.raises(RuntimeError, match='suite drifted before dispatch'):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
        )

    assert calls == [['first']]


def test_v3_serial_rejects_analyzed_record_from_another_slot(
    tmp_path,
    monkeypatch,
):
    """Never attribute one analyzed run to a different dispatched case."""
    case_ids = ['expected-slot', 'must-not-run']
    suite = _v3_serial_suite(tmp_path, case_ids)
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record('wrong-slot'),
    )

    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
        )
    )

    assert calls == [[case_ids[0]]]
    assert records == []
    assert 'execution error' in progress['stopped_early_reason']
    assert progress['attempts'][0]['outcome'] == 'execution_error'
    error = json.loads(Path(
        progress['attempts'][0]['error_path']
    ).read_text(encoding='utf-8'))
    assert 'wrong-slot' in error['error']


def test_v3_serial_does_not_redispatch_ambiguous_intent(
    tmp_path,
    monkeypatch,
):
    """An interrupted dispatch with no summary is permanently ambiguous."""
    suite = _v3_serial_suite(tmp_path, ['interrupted-slot'])
    _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    dispatch_count = 0

    def interrupt_before_summary(*unused, **unused_keywords):
        nonlocal dispatch_count
        dispatch_count += 1
        raise KeyboardInterrupt

    monkeypatch.setattr(
        phase08_validation,
        'execute_suite',
        interrupt_before_summary,
    )
    stage_root = tmp_path / 'evidence/activation'
    with pytest.raises(KeyboardInterrupt):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
        )
    intent = phase08_validation._v3_load_progress(stage_root)
    assert len(intent['attempts']) == 1
    assert intent['attempts'][0]['outcome'] == 'dispatch_intent'

    summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
        )
    )

    assert dispatch_count == 1
    assert records == []
    assert len(progress['attempts']) == 1
    assert progress['ambiguous_interrupted_dispatch_case_ids'] == [
        'interrupted-slot',
    ]
    assert progress['not_run_slot_ids'] == []
    assert summary['attempted_slot_count'] == 1
    assert summary['completed_slot_count'] == 0
    assert summary[
        'ambiguous_interrupted_dispatch_case_ids'
    ] == ['interrupted-slot']
    assert 'ambiguous interrupted dispatch intent' in progress[
        'stopped_early_reason'
    ]


def test_v3_serial_resumes_summary_without_redispatch(
    tmp_path,
    monkeypatch,
):
    """Analyze a completed journaled summary after an interruption."""
    suite = _v3_serial_suite(tmp_path, ['recoverable-slot'])
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    original_execute = phase08_validation.execute_suite

    def interrupt_after_summary(*args, **kwargs):
        original_execute(*args, **kwargs)
        raise KeyboardInterrupt

    monkeypatch.setattr(
        phase08_validation,
        'execute_suite',
        interrupt_after_summary,
    )
    stage_root = tmp_path / 'evidence/activation'
    with pytest.raises(KeyboardInterrupt):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
        )

    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
        )
    )

    assert calls == [['recoverable-slot']]
    assert [record['case_id'] for record in records] == [
        'recoverable-slot',
    ]
    assert len(progress['attempts']) == 1
    assert progress['attempts'][0]['outcome'] == 'passed'
    assert progress['stopped_early_reason'] is None


def test_v3_serial_artifact_audit_detects_attempt_aggregate_drift(
    tmp_path,
    monkeypatch,
):
    """Terminal readiness rehashes progress and every retained attempt."""
    suite = _v3_serial_suite(tmp_path, ['artifact-bound'])
    _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    stage_root = tmp_path / 'evidence/activation'
    unused_summary, unused_records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
        )
    )
    state = {
        'records_path': str(stage_root / 'records.json'),
        'progress_sha256': progress['progress_sha256'],
        'attempt_records_sha256': phase08_validation.file_sha256(
            stage_root / 'attempt_records.json'
        ),
    }
    assert phase08_validation._v3_serial_artifact_errors(
        'activation',
        state,
    ) == []
    original_suite = suite.read_bytes()
    suite.write_bytes(original_suite + b'\n# drift\n')

    assert any(
        'serial suite hash drifted' in reason
        for reason in phase08_validation._v3_serial_artifact_errors(
            'activation',
            state,
        )
    )
    suite.write_bytes(original_suite)

    phase08_validation.atomic_json(
        stage_root / 'attempt_records.json',
        [],
    )

    assert any(
        'attempt-record aggregate drifted' in reason
        for reason in phase08_validation._v3_serial_artifact_errors(
            'activation',
            state,
        )
    )


def test_v3_serial_links_one_pre_readiness_replacement(
    tmp_path,
    monkeypatch,
):
    """One qualified invalid attempt receives one linked replacement."""
    suite = _v3_serial_suite(tmp_path, ['replace-me'])

    def record_factory(case_id, attempt):
        if attempt > 1:
            return _v3_serial_record(case_id)
        run_directory = tmp_path / 'invalid-attempt'
        phase08_validation.atomic_yaml(
            run_directory / 'metadata.yaml',
            {
                'recording': {
                    'failure_stage': 'graph_preflight',
                    'infrastructure_status': 'infrastructure_invalid',
                    'readiness_ever_true': False,
                    'pre_ready_nonzero_topics': {},
                    'pre_ready_lifecycle_violations': [],
                },
            },
        )
        phase08_validation.atomic_json(
            run_directory / 'completeness.json',
            {
                'checks': {
                    'no_motion_before_readiness': {'passed': True},
                    'clean_lifecycle_before_readiness': {'passed': True},
                },
            },
        )
        return _v3_serial_record(
            case_id,
            status='infrastructure_invalid',
            run_directory=run_directory,
        )

    calls = _install_v3_serial_mocks(monkeypatch, record_factory)
    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
        )
    )
    replacement = phase08_validation._v3_load_replacement_state(
        tmp_path / 'evidence'
    )

    assert calls == [['replace-me'], ['replace-me']]
    assert len(records) == 1
    assert len(progress['attempts']) == 2
    assert replacement['total'] == 1
    assert replacement['slots'] == ['activation.replace-me']
    assert replacement['attempt_links'][0][
        'replacement_attempt_index'
    ] == 2


def test_v3_diagnostic_serial_never_replaces_infrastructure_invalid(
    tmp_path,
    monkeypatch,
):
    """A diagnostic successor executes each remaining case at most once."""
    case_ids = ['infra-invalid', 'must-not-run']
    suite = _v3_serial_suite(tmp_path, case_ids)
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, unused_attempt: _v3_serial_record(
            case_id,
            status='infrastructure_invalid',
        ),
    )

    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
            required_execution_case_ids=case_ids,
            allow_pure_applicability_miss=True,
            allow_infrastructure_replacements=False,
        )
    )

    assert calls == [['infra-invalid']]
    assert [record['case_id'] for record in records] == [
        'infra-invalid',
    ]
    assert [
        (item['case_id'], item['attempt_index'])
        for item in progress['attempts']
    ] == [('infra-invalid', 1)]
    assert progress['not_run_slot_ids'] == ['must-not-run']
    assert 'replacement prohibited' in progress['stopped_early_reason']
    assert not phase08_validation._v3_replacement_state_path(
        tmp_path / 'evidence'
    ).exists()


def test_v3_serial_resumes_persisted_replacement_after_crash(
    tmp_path,
    monkeypatch,
):
    """A crash after authorization cannot consume a second replacement."""
    suite = _v3_serial_suite(tmp_path, ['replace-me'])
    evidence_root = tmp_path / 'evidence'
    stage_root = evidence_root / 'activation'
    attempt_root = (
        stage_root
        / 'attempts/001_replace-me/attempt_01'
    )
    run_directory = tmp_path / 'invalid-attempt'
    phase08_validation.atomic_yaml(
        run_directory / 'metadata.yaml',
        {
            'recording': {
                'failure_stage': 'graph_preflight',
                'infrastructure_status': 'infrastructure_invalid',
                'readiness_ever_true': False,
                'pre_ready_nonzero_topics': {},
                'pre_ready_lifecycle_violations': [],
            },
        },
    )
    phase08_validation.atomic_json(
        run_directory / 'completeness.json',
        {
            'checks': {
                'no_motion_before_readiness': {'passed': True},
                'clean_lifecycle_before_readiness': {'passed': True},
            },
        },
    )
    invalid = _v3_serial_record(
        'replace-me',
        status='infrastructure_invalid',
        run_directory=run_directory,
    )
    summary_path = attempt_root / 'scenario_summary.yaml'
    record_path = attempt_root / 'record.json'
    phase08_validation.atomic_yaml(
        summary_path,
        {
            'schema_version': 1,
            'test_attempt': 1,
            'runs': [{'case_id': 'replace-me'}],
        },
    )
    phase08_validation.atomic_json(record_path, invalid)
    evidence = phase08_validation._v3_replacement_evidence(invalid)
    phase08_validation._v3_authorize_or_resume_replacement(
        evidence_root,
        'activation',
        'activation.replace-me',
        evidence,
        {},
        record_path,
        2,
    )
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )

    unused_summary, records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            evidence_root,
            stage_root,
            'activation',
        )
    )

    assert calls == [['replace-me']]
    assert len(records) == 1
    assert len(progress['attempts']) == 2
    assert phase08_validation._v3_load_replacement_state(
        evidence_root
    )['total'] == 1
    states = {
        'activation': {
            'replacement_state_sha256': (
                phase08_validation.file_sha256(
                    phase08_validation._v3_replacement_state_path(
                        evidence_root
                    )
                )
            ),
        },
    }
    assert phase08_validation._v3_replacement_artifact_errors(
        evidence_root,
        states,
    ) == []

    metadata_path = run_directory / 'metadata.yaml'
    metadata = yaml.safe_load(metadata_path.read_text(encoding='utf-8'))
    metadata['recording']['readiness_ever_true'] = True
    phase08_validation.atomic_yaml(metadata_path, metadata)

    assert any(
        'eligible invalid evidence' in reason
        for reason in phase08_validation._v3_replacement_artifact_errors(
            evidence_root,
            states,
        )
    )


@pytest.mark.parametrize(
    ('defect', 'reason'),
    [
        ('cleanup', 'cleanup contamination'),
        ('collision', 'non-ground collision'),
        ('analysis', 'analysis is not complete'),
    ],
)
def test_v3_serial_hard_stop_prevents_remaining_dispatch(
    tmp_path,
    monkeypatch,
    defect,
    reason,
):
    """Cleanup and collision failures stop all later declared slots."""
    case_ids = ['hard-stop', 'not-run-a', 'not-run-b']
    suite = _v3_serial_suite(tmp_path, case_ids)

    def record_factory(case_id, attempt):
        del attempt
        record = _v3_serial_record(
            case_id,
            cleanup=defect != 'cleanup',
            collision=defect == 'collision',
        )
        if defect == 'analysis':
            record['analysis']['analysis_status'] = 'incomplete'
        return record

    calls = _install_v3_serial_mocks(monkeypatch, record_factory)
    unused_summary, unused_records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/activation',
            'activation',
        )
    )

    assert calls == [['hard-stop']]
    assert reason in progress['stopped_early_reason']
    assert progress['not_run_slot_ids'] == case_ids[1:]


def _v3_holdout_decider_fixture(monkeypatch, tmp_path):
    family_order = [
        family
        for family, allocation in (
            phase08_validation.V3_FAMILY_ALLOCATION.items()
        )
        for unused in range(allocation['holdout'])
    ]
    cases = [
        {
            'case_id': f'holdout-{index:02d}',
            'acceptance_partition': 'holdout',
            'acceptance_family': family,
        }
        for index, family in enumerate(family_order)
    ]
    monkeypatch.setattr(
        phase08_validation,
        '_v3_case_evaluation',
        lambda *unused: {
            'integrity': {'passed': True},
            'binding_reasons': [],
            'reasons': [],
            'lifecycle_passed': True,
        },
    )
    decider = phase08_validation._v3_partition_stop_decider(
        'holdout',
        {},
        {'resolved_cases': cases},
        tmp_path,
    )
    records = [
        {
            'case_id': case['case_id'],
            'acceptance_family': case['acceptance_family'],
            'analysis': {
                'metrics': {
                    'controller_success': _metric(False),
                    'simulation_ground_truth_success': _metric(True),
                },
            },
        }
        for case in cases
    ]
    return cases, records, decider


@pytest.mark.parametrize(
    ('completed', 'expected'),
    [
        (3, '18/20 floor is mathematically unreachable'),
        (2, 'ordered_two_source floor is mathematically unreachable'),
    ],
)
def test_v3_holdout_optimistic_stop_bounds_are_enforced(
    tmp_path,
    monkeypatch,
    completed,
    expected,
):
    """Stop once the fixed overall or family floor cannot be recovered."""
    cases, records, decider = _v3_holdout_decider_fixture(
        monkeypatch,
        tmp_path,
    )

    reason = decider(
        records[:completed],
        [case['case_id'] for case in cases[completed:]],
    )

    assert expected in reason


def test_v3_serial_reproducibility_stops_on_first_mismatch(
    tmp_path,
    monkeypatch,
):
    """The first reproducibility mismatch leaves all later pairs not run."""
    case_ids = ['repeat-a', 'repeat-b', 'repeat-c']
    suite = _v3_serial_suite(
        tmp_path,
        case_ids,
        partition='reproducibility',
    )
    records_path = tmp_path / 'unique-records.json'
    phase08_validation.atomic_json(records_path, [])
    monkeypatch.setattr(
        phase08_validation,
        '_v3_require_state',
        lambda *unused: {'records_path': str(records_path)},
    )
    monkeypatch.setattr(
        phase08_validation,
        '_v3_case_evaluation',
        lambda *unused: {
            'integrity': {'passed': True},
            'binding_reasons': [],
            'reasons': [],
            'lifecycle_passed': True,
        },
    )
    monkeypatch.setattr(
        phase08_validation,
        'evaluate_v3_reproducibility',
        lambda *unused: {'results': [{'passed': False}]},
    )
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    contract = {
        'resolved_cases': [
            {
                'case_id': case_id,
                'acceptance_partition': 'reproducibility',
            }
            for case_id in case_ids
        ],
    }
    decider = phase08_validation._v3_partition_stop_decider(
        'reproducibility',
        {},
        contract,
        tmp_path / 'evidence',
    )

    unused_summary, unused_records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            tmp_path / 'evidence/reproducibility',
            'reproducibility',
            stop_decider=decider,
        )
    )

    assert calls == [['repeat-a']]
    assert 'first mismatch' in progress['stopped_early_reason']
    assert progress['not_run_slot_ids'] == case_ids[1:]


def test_v3_serial_progress_hash_rejects_mutation(
    tmp_path,
    monkeypatch,
):
    """Retain not-run slots and reject a mutated resume document."""
    case_ids = ['complete', 'not-run']
    suite = _v3_serial_suite(tmp_path, case_ids)
    calls = _install_v3_serial_mocks(
        monkeypatch,
        lambda case_id, attempt: _v3_serial_record(case_id),
    )
    stage_root = tmp_path / 'evidence/activation'
    unused_summary, unused_records, progress = (
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
            stop_decider=lambda records, remaining: 'test stop',
        )
    )
    assert calls == [['complete']]
    assert progress['not_run_slot_ids'] == ['not-run']

    progress_path = phase08_validation._v3_progress_path(stage_root)
    mutated = json.loads(progress_path.read_text(encoding='utf-8'))
    mutated['not_run_slot_ids'] = []
    progress_path.write_text(json.dumps(mutated), encoding='utf-8')

    with pytest.raises(RuntimeError, match='progress hash drifted'):
        phase08_validation._v3_execute_serial_slots(
            suite,
            'test',
            tmp_path / 'evidence',
            stage_root,
            'activation',
        )
