"""Prospective acquisition validation, actual wire receipts, and finite dispatch."""

from copy import deepcopy
import datetime as dt
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import rclpy
from rclpy.serialization import serialize_message
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState, CostBreakdown, Timekeeper
from std_msgs.msg import Bool
from nav_msgs.msg import Odometry
import yaml

from ros_esc.experiment_recording import record_run as recorder
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.scenario_schema import load_suite, expand_suite, deterministic_case_key
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.v2_supervisor import stamp
from test_q1_observation_policy import parameters


SCENARIOS = Path(__file__).resolve().parents[1] / 'ros_esc/scenario_runner/scenarios'
PRIMARY = SCENARIOS / 'phase08_v8_10_primary_visible_probe.yaml'
READY = '/gesc_gaussian/recording_ready'
EVENT = '/gesc_gaussian/algorithm_events'
STATE = '/gesc_gaussian/algorithm_state'


def document():
    primary = yaml.safe_load(PRIMARY.read_text())
    source = primary['cases'][0]
    result = {key: deepcopy(primary[key]) for key in (
        'mode', 'metadata', 'level_map', 'defaults', 'frozen_profile')}
    result.update(schema_version=2, purpose='qualification_observation',
                  suite_id='q1_safety_fixture', execution=dict(
                      run_timeout_sec=0., simulation_duration_sec=125.,
                      wall_timeout_sec=180., preflight_timeout_sec=60.,
                      shutdown_grace_sec=45., stop_on_run_failure=True,
                      stop_on_cleanup_failure=True))
    result['frozen_profile']['launch_overrides'].update(
        continuous_search_mode='rolling_gesc_v2',
        v2_qualification_observation_only=True,
        v2_candidate_radius_m=.75, v2_candidate_epsilon_m=.15)
    case = {key: deepcopy(source[key]) for key in (
        'case_id', 'family', 'description', 'status', 'profiles', 'seeds',
        'starts', 'sources', 'algorithm')}
    case['case_id'] = 'q1_first'
    case['success'] = dict(
        all_of=['recording_complete', 'cleanup_complete', 'no_forbidden_events'],
        controller=dict(expected_terminal_state=None, required_state_sequence=[],
                        required_events=[], forbidden_events=['FAILSAFE', 'RECENTER_STARTED']),
        ground_truth=dict(goal_source_ids=['global'], final_position_tolerance_m=.5))
    result['cases'] = [case]
    return result


def save(tmp_path, value=None):
    path = tmp_path / 'qualification.yaml'
    path.write_text(yaml.safe_dump(document() if value is None else value))
    return path


def resolved(tmp_path):
    return expand_suite(load_suite(save(tmp_path)))[0][0]


def event(kind):
    result = AlgorithmEvent(); result.event_type = int(kind)
    return result


def state():
    result = AlgorithmState(); result.state_valid = True
    result.state = result.STATE_SEARCH; result.state_name = 'SEARCH'
    return result


def wire_rows(kind=None, *, event_receipt=30, false_receipt=40):
    rows = [(READY, Bool(data=False), 10), (READY, Bool(data=True), 20),
            (STATE, state(), 21)]
    if kind is not None:
        rows.append((EVENT, event(kind), event_receipt))
    rows.append((READY, Bool(data=False), false_receipt))
    return [(topic, serialize_message(message), when)
            for topic, message, when in sorted(rows, key=lambda row: row[2])]


def read_rows(monkeypatch, tmp_path, selected, rows):
    class Reader:
        def __init__(self): self.rows = iter(rows); self.pending = next(self.rows, None)
        def open(self, *_args): pass
        def has_next(self): return self.pending is not None
        def read_next(self):
            value = self.pending; self.pending = next(self.rows, None)
            return value
    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', Reader)
    return runner._bag_outcomes(tmp_path, selected)


def test_purpose_keeps_primary_controls_and_exact_identity_in_every_output(tmp_path):
    path = save(tmp_path)
    suite = load_suite(path); selected = expand_suite(suite)[0][0]
    assert suite['purpose'] == selected['purpose'] == 'qualification_observation'
    assert selected['schema_version'] == 2
    controls = selected['algorithm']['launch_overrides']
    assert controls['open_field_escape_supervisor_owned_assist_enabled']
    assert controls['known_source_count'] == 2 and controls['gaussian_fill_max_fills'] == 1
    assert selected['success']['all_of'] == ['recording_complete', 'cleanup_complete', 'no_forbidden_events']
    assert selected['success']['controller']['forbidden_events'] == ['FAILSAFE', 'RECENTER_STARTED']
    summary = runner.execute_suite(path, 'fixture', dry_run=True, run_id='q1-exact-id')
    run = summary['runs'][0]
    assert summary['purpose'] == run['purpose'] == run['metadata']['scenario_runner']['purpose']
    assert run['run_id'] == 'q1-exact-id'
    assert 'v2_run_id:=q1-exact-id' in run['launch_argv']
    assert run['record_argv'][run['record_argv'].index('--run-id') + 1] == 'q1-exact-id'
    assert run['record_argv'][run['record_argv'].index('--sim-duration-sec') + 1] == '125.0'
    assert run['metadata']['scenario_runner']['v2_identity']['run_id'] == 'q1-exact-id'
    old = deepcopy(selected); old.pop('purpose')
    assert deterministic_case_key(old) != selected['case_key']
    assert runner._parser().parse_args([str(path), '--operator', 'fixture', '--run-id', 'q1-exact-id']).run_id == 'q1-exact-id'


@pytest.mark.parametrize('version,purpose', [(1, 'qualification_observation'), (13, 'qualification_observation'), (2, 'unknown'), (2, None)])
def test_purpose_rejects_unsupported_schemas_and_spellings(tmp_path, version, purpose):
    value = document(); value.update(schema_version=version, purpose=purpose)
    with pytest.raises(ValueError, match='purpose qualification_observation'):
        load_suite(save(tmp_path, value))


def test_older_schema_controls_remain_rejected_without_explicit_purpose(tmp_path):
    value = document(); value.pop('purpose')
    with pytest.raises(ValueError, match='schema version'):
        load_suite(save(tmp_path, value))
    # The existing primary lifecycle remains usable under its original schema.
    original = load_suite(PRIMARY)
    assert original['schema_version'] >= 13 and 'purpose' not in original
    assert 'simulation_duration_sec' not in original['execution']


@pytest.mark.parametrize('key,value', [
    ('v2_qualification_observation_only', False), ('continuous_search_mode', 'stationary_v1'),
    ('known_source_count', 3), ('gaussian_fill_max_fills', 2), ('gaussian_fill_max_fills', True),
    ('v2_candidate_radius_m', 0.), ('candidate_cost_rotation_period_sec', -1.),
])
def test_acquisition_still_validates_merged_primary_controls(tmp_path, key, value):
    source = document(); source['frozen_profile']['launch_overrides'][key] = value
    with pytest.raises(ValueError): load_suite(save(tmp_path, source))


def test_frozen_rolling_selector_cannot_evade_profile_scope(tmp_path):
    value = document(); value['cases'][0]['profiles'] = ['legacy']
    with pytest.raises(ValueError, match='rolling_gesc_v2 requires only robust'):
        load_suite(save(tmp_path, value))


@pytest.mark.parametrize('change', ['count', 'order', 'bounds', 'safety', 'duration', 'stop', 'lifecycle'])
def test_acquisition_rejects_wrong_source_or_acceptance_contract(tmp_path, change):
    value = document(); case = value['cases'][0]
    if change == 'count': case['sources'].pop()
    elif change == 'order': case['sources'][1]['relative_lumen_input'] = 100.
    elif change == 'bounds': case['sources'][0]['x_m'] = -10.
    elif change == 'safety': case['success']['controller']['forbidden_events'].remove('FAILSAFE')
    elif change == 'duration': value['execution']['simulation_duration_sec'] = 0.
    elif change == 'stop': value['execution']['stop_on_run_failure'] = False
    elif change == 'lifecycle': case['success']['controller']['required_events'] = ['GOAL_REACHED']
    with pytest.raises(ValueError): load_suite(save(tmp_path, value))


@pytest.mark.parametrize('run_id', ['', '../escape', True])
def test_invalid_explicit_identity_is_rejected_before_ros(tmp_path, monkeypatch, run_id):
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: pytest.fail('must reject before ROS'))
    with pytest.raises(ValueError): runner.execute_suite(save(tmp_path), 'fixture', run_id=run_id)


def test_explicit_identity_requires_one_expanded_run(tmp_path, monkeypatch):
    value = document(); value['cases'][0]['seeds'] = [1, 2]
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: pytest.fail('must reject before ROS'))
    with pytest.raises(ValueError, match='exactly one expanded run'):
        runner.execute_suite(save(tmp_path, value), 'fixture', run_id='q1-exact-id')


def test_existing_identity_still_uses_recorder_directory_refusal(tmp_path, monkeypatch):
    now = dt.datetime(2026, 9, 9, tzinfo=dt.timezone.utc)
    existing = tmp_path / '2026-09-09/q1-exact-id'; existing.mkdir(parents=True)
    marker = existing / 'retained.txt'; marker.write_text('never overwrite')
    monkeypatch.setattr(recorder, '_utc_now', lambda: now)
    monkeypatch.setattr(recorder, 'load_manifest', lambda *_args: {'storage_id': 'sqlite3'})
    monkeypatch.setattr(recorder, 'applicable_topics', lambda *_args: [])
    monkeypatch.setattr(recorder, 'operational_config_for_mode', lambda *_args: {})
    monkeypatch.setattr(recorder, 'load_metadata_input', lambda *_args: {})
    monkeypatch.setattr(recorder, '_process', lambda *_args: pytest.fail('existing ID must fail before launch'))
    args = recorder._parser().parse_args(['--mode', 'simulation', '--metadata-input', '/fixture',
        '--runs-root', str(tmp_path), '--run-id', 'q1-exact-id', '--', 'fixture_target'])
    with pytest.raises(FileExistsError, match='run directory already exists'):
        recorder.run(args)
    assert marker.read_text() == 'never overwrite'


@pytest.mark.parametrize('kind', [AlgorithmEvent.EVENT_FAILSAFE, AlgorithmEvent.EVENT_RECENTER_STARTED])
@pytest.mark.parametrize('when,allowed', [(19, True), (30, False), (40, False), (41, True)])
def test_actual_serialized_event_enums_obey_recorded_ready_boundaries(tmp_path, monkeypatch, kind, when, allowed):
    outcome = read_rows(monkeypatch, tmp_path, resolved(tmp_path), wire_rows(kind, event_receipt=when))
    assert outcome['forbidden_events_absent'] is allowed
    assert outcome['outcome_error'] is None


@pytest.mark.parametrize('kind,allowed', [
    (AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED, True),
    (AlgorithmEvent.EVENT_FILL_CREATED, False),
    (AlgorithmEvent.EVENT_GOAL_REACHED, False),
    (AlgorithmEvent.EVENT_FAILSAFE, False),
    (AlgorithmEvent.EVENT_RECENTER_STARTED, False),
])
def test_fixed_q1_scenario_allows_shadow_confirmation_and_vetoes_intervention(tmp_path, monkeypatch, kind, allowed):
    suite = load_suite(SCENARIOS / 'q1_primary_shadow_v1.yaml')
    runs, unsupported = expand_suite(suite)
    assert not unsupported and [run['seed'] for run in runs] == list(range(26090911, 26090915))
    for selected in runs:
        outcome = read_rows(monkeypatch, tmp_path, selected, wire_rows(kind))
        classification = runner.classify_result(
            selected, {'passed': True}, {'passed': True}, outcome,
            {'timed_out': False, 'return_code': 0},
            metadata={'recording': {'readiness_ever_true': True,
                                   'infrastructure_status': 'completed'}},
            run_directory_available=True)
        assert classification['predicate_results']['no_forbidden_events'] is allowed
        assert classification['passed'] is allowed


@pytest.mark.parametrize('failure,expected_count,reason', [
    ('FAILSAFE', 1, 'run_failure'), ('RECENTER_STARTED', 1, 'run_failure'),
    ('cleanup', 1, 'cleanup_failure'), (None, 2, None),
])
def test_existing_dispatch_stops_after_safety_or_cleanup_and_retains_run(tmp_path, monkeypatch, failure, expected_count, reason):
    value = document(); second = deepcopy(value['cases'][0]); second['case_id'] = 'q1_second'
    value['cases'].append(second); path = save(tmp_path, value); root = tmp_path / 'runs'
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda: set())
    monkeypatch.setattr(runner, 'generate_scenario_run_id', lambda case: case['case_id'])
    calls = []
    def process(command, *_args, **kwargs):
        assert not kwargs  # No inherited staged/live-proximity stop contract.
        run_id = command[command.index('--run-id') + 1]; calls.append(run_id)
        target = root / '2026-09-09' / run_id; target.mkdir(parents=True)
        (target / 'completeness.json').write_text(json.dumps({'passed': True}))
        (target / 'metadata.yaml').write_text(yaml.safe_dump(dict(recording=dict(
            readiness_ever_true=True, infrastructure_status='completed'))))
        return dict(return_code=0, timed_out=False, stdout='retained fixture', session_id=123)
    monkeypatch.setattr(runner, 'run_record_process', process)
    monkeypatch.setattr(runner, 'cleanup_evidence', lambda *_args: {'passed': failure != 'cleanup'})
    kind = getattr(AlgorithmEvent, 'EVENT_' + failure) if failure in ('FAILSAFE', 'RECENTER_STARTED') else None
    rows = wire_rows(kind)
    # Keep the actual receipt parser and classification; only bag transport is stubbed.
    class Reader:
        def __init__(self): self.rows = list(rows)
        def open(self, *_args): pass
        def has_next(self): return bool(self.rows)
        def read_next(self): return self.rows.pop(0)
    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', Reader)
    summary = runner.execute_suite(path, 'fixture', runs_root=root, summary_output=tmp_path / 'summary.yaml')
    assert len(calls) == len(summary['runs']) == expected_count
    assert summary.get('stopped_early_reason') == reason
    assert (root / '2026-09-09/q1_first/scenario_result.yaml').exists()
    if failure in ('FAILSAFE', 'RECENTER_STARTED'):
        assert summary['runs'][0]['classification']['predicate_results']['no_forbidden_events'] is False


@pytest.mark.parametrize('delay_false_receipt', [False, True])
def test_actual_shutdown_callbacks_separate_publication_order_from_receipt_order(tmp_path, monkeypatch, delay_false_receipt):
    rclpy.init(args=[])
    coordinator = supervisor = None
    rows, published, delayed = [], [], []
    receipt = [0]
    def receive(topic, message):
        receipt[0] += 10
        rows.append((topic, serialize_message(message), receipt[0]))
    class Publisher:
        def __init__(self, callback): self.callback = callback
        def publish(self, message): self.callback(deepcopy(message))
    try:
        supervisor = SupervisorNode(parameter_overrides=parameters())
        monkeypatch.setattr(supervisor, 'get_clock', lambda: SimpleNamespace(now=lambda: SimpleNamespace(
            nanoseconds=1_000_000_000, to_msg=lambda: stamp(1_000_000_000))))
        supervisor.event_publisher = Publisher(lambda message: receive(EVENT, message))
        supervisor.state_publisher = Publisher(lambda message: receive(STATE, message))
        clock = Timekeeper(); clock.mode = 'sim time'; clock.start_time = 0.
        supervisor.moving_v2.timekeeper(clock)
        pose = Odometry(); pose.header.frame_id = 'odom'; pose.header.stamp = stamp(1_000_000_000)
        pose.pose.pose.orientation.w = 1.; supervisor.pose_callback(pose)
        raw = CostBreakdown(); raw.source_timestamp_valid = raw.raw_cost_valid = True
        raw.source_timestamp = 1.; raw.channel_count = 1; raw.raw_cost = [-1.]
        supervisor.source_callback(raw)
        coordinator = recorder.RecordingCoordinator(READY, '/gesc_gaussian/stop_requested', 10., mode='simulation')
        def ready(message):
            published.append(('ready', message.data))
            supervisor.moving_v2.readiness(message)
            if not message.data and delay_false_receipt: delayed.append(message)
            else: receive(READY, message)
        def stop(message):
            published.append(('stop', message.data))
            supervisor.stop_callback(message)
            supervisor.timer_callback()
        coordinator.ready_publisher = Publisher(ready)
        coordinator.stop_publisher = Publisher(stop)
        assert coordinator.authorize_if_safe() == []
        coordinator.publish_ready(); supervisor.timer_callback()
        assert supervisor.machine.state.name == 'SEARCH'
        published.clear()
        coordinator.request_stop()
        for message in delayed: receive(READY, message)
        assert published == [('ready', False), ('stop', True)]
        assert supervisor.machine.state.name == 'FAILSAFE'
        outcome = read_rows(monkeypatch, tmp_path, resolved(tmp_path), rows)
        # No claim that cross-topic DDS delivery obeys publication order: a
        # delayed false receipt must conservatively reject this apparent fault.
        assert outcome['forbidden_events_absent'] is (not delay_false_receipt)
    finally:
        if supervisor is not None: supervisor.destroy_node()
        if coordinator is not None: coordinator.destroy_node()
        rclpy.try_shutdown()
