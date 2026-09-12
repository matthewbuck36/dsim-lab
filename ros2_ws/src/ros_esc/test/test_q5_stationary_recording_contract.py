"""Arm B selected recording, unchanged diagnostic provenance and result joins."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
from rclpy.serialization import deserialize_message, serialize_message

from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.record_run import (
    applicable_topics, load_manifest, require_selected_algorithm_topics,
    stationary_centroid_config_from_target,
)
from ros_esc.experiment_recording.stationary_centroid_validation import (
    TOPICS, stationary_centroid_stream_errors,
)
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import _stationary_centroid_analysis
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState, GaussianFill, Timekeeper
from test_q5_stationary_fill_protocol import ORIGIN_NS, RUN, request, rehash
from test_q5_stationary_centroid_adapter import (  # noqa: F401
    arm_b, enter_confirmation, finish_verification,
)


PACKAGE = Path(__file__).resolve().parents[1]
ARGV = ['algorithm_profile:=robust_gaussian_v1', 'convergence_metric_mode:=centroid_windows_v2',
        'continuous_search_mode:=stationary_v1', 'algorithm_pose_topic:=/selected/odom']


def config():
    return stationary_centroid_config_from_target(ARGV)


def design(message):
    state = AlgorithmState()
    state.run_id, state.algorithm_profile = message.confirmation.run_id, 'robust_gaussian_v1'
    state.state_valid = state.run_id_valid = state.state_elapsed_valid = state.previous_state_valid = True
    state.state, state.previous_state = state.STATE_DESIGN_OR_MERGE_FILL, state.STATE_VERIFY_EXTREMUM
    if message.operation == message.TARGETED_REDESIGN:
        state.previous_state = state.STATE_ESCAPE_REPULSE
    state.stamp = deepcopy(message.stamp)
    state.state_elapsed_sec = 0.
    return state


def stream(message=None):
    message = request() if message is None else message
    return {
        config()['timekeeper_topic']: [(1, Timekeeper(mode='sim time', start_time=ORIGIN_NS*1e-9))],
        TOPICS['centroid_convergence_diagnostics']: [(2, deepcopy(message.confirmation))],
        TOPICS['algorithm_state']: [(4, design(message))],
        # DDS may deliver a request before its preceding DESIGN publication.
        TOPICS['stationary_fill_requests']: [(3, message)],
    }


def active_fill(message, *, fill_id=1, revision=1):
    fill = GaussianFill()
    fill.source_timestamp, fill.source_timestamp_valid = message.source_timestamp, True
    fill.frame_id, fill.fill_id, fill.cluster_id, fill.revision = 'odom', fill_id, 1, revision
    fill.active = True
    set_time(fill.stamp, time_to_ns(message.stamp)+100_000_000)
    return fill


def audit(messages, selected=None):
    return stationary_centroid_stream_errors(messages, config() if selected is None else selected)


def test_valid_request_cdr_nonzero_origin_and_cross_topic_delivery_order():
    message = request()
    message = deserialize_message(serialize_message(message), type(message))
    errors, result = audit(stream(message))
    assert errors == []
    assert result['counts']['unique_requests'] == result['counts']['requests_without_terminal_outcome'] == 1
    assert result['requests'][0]['source_timestamp'] == 25.
    assert result['timelines'][0]['duration_sec'] == pytest.approx(5.9)


def test_actual_supervisor_emitted_request_passes_same_recording_contract(arm_b):
    node, _, _ = arm_b
    original = enter_confirmation(arm_b)
    finish_verification(arm_b)
    message, = node.stationary_centroid.request_publisher.messages
    messages = stream(deserialize_message(serialize_message(message), type(message)))
    messages[TOPICS['centroid_convergence_diagnostics']] = [(1, original)]
    messages[TOPICS['algorithm_state']] = list(enumerate(node.state_publisher.messages))
    selected = config()
    selected['candidate_informed_fill_enabled'] = True
    errors, result = audit(messages, selected)
    assert errors == []
    assert result['requests'][0]['request_sha256'] == message.request_sha256


def test_no_candidate_no_request_and_no_fill_is_valid():
    messages = stream()
    messages[TOPICS['stationary_fill_requests']] = []
    messages[TOPICS['centroid_convergence_diagnostics']] = []
    errors, result = audit(messages)
    assert errors == [] and result['counts']['unique_requests'] == 0
    assert not result['timelines']


def test_exact_request_and_result_retries_are_counted_once():
    message = request()
    messages = stream(message)
    messages[TOPICS['stationary_fill_requests']].append((99, deepcopy(message)))
    fill = active_fill(message)
    messages[TOPICS['gaussian_fills']] = [(5, fill), (100, deepcopy(fill))]
    errors, result = audit(messages)
    assert errors == []
    assert result['counts']['unique_requests'] == result['counts']['request_retries'] == 1
    assert result['counts']['requests_with_active_fill'] == 1
    assert len(result['outcomes']) == 1 and len(result['timelines']) == 2


@pytest.mark.parametrize('change', [
    'hash', 'origin', 'run', 'nested_history', 'metric_configuration', 'candidate_policy',
    'missing_diagnostic', 'missing_design', 'wrong_design_entry', 'wrong_design_predecessor',
    'unobserved_origin', 'changed_origin', 'stale_confirmation_admission',
])
def test_static_and_recorded_authority_disagreements_are_invalid(change):
    message = request()
    messages = stream(message)
    if change == 'hash': message.request_sha256 = 'a'*64
    elif change == 'origin': message.time_origin.nanosec += 1
    elif change == 'run': message.confirmation.run_id = 'foreign'
    elif change == 'nested_history': message.confirmation.reset_sequence += 1
    elif change == 'metric_configuration': message.confirmation.epsilon_m = .12
    elif change == 'candidate_policy':
        message = request(informed=True)
        messages[TOPICS['stationary_fill_requests']] = [(3, message)]
    elif change == 'missing_diagnostic': messages[TOPICS['centroid_convergence_diagnostics']] = []
    elif change == 'missing_design': messages[TOPICS['algorithm_state']][0][1].state = AlgorithmState.STATE_SEARCH
    elif change == 'wrong_design_entry': messages[TOPICS['algorithm_state']][0][1].state_elapsed_sec = .1
    elif change == 'wrong_design_predecessor': messages[TOPICS['algorithm_state']][0][1].previous_state = AlgorithmState.STATE_SEARCH
    elif change == 'unobserved_origin': messages[config()['timekeeper_topic']] = []
    elif change == 'changed_origin': messages[config()['timekeeper_topic']].append((2, Timekeeper(mode='sim time', start_time=1001.)))
    elif change == 'stale_confirmation_admission': message.confirmation_accepted_at.sec += 1
    if change != 'hash': rehash(message)
    assert audit(messages)[0], change


@pytest.mark.parametrize('change', ['conflicting_sequence', 'correlation_collision', 'repeated_create'])
def test_distinct_requests_cannot_reuse_identity_correlation_or_candidate(change):
    message = request()
    another = deepcopy(message)
    if change != 'conflicting_sequence': another.request_sequence += 1
    if change != 'correlation_collision':
        another.stamp.nanosec += 100
        another.source_timestamp = (time_to_ns(another.stamp)-ORIGIN_NS)*1e-9
    rehash(another)
    messages = stream(message)
    messages[TOPICS['stationary_fill_requests']].append((10, another))
    assert audit(messages)[0]


def test_targeted_redesign_preserves_original_confirmation_and_old_supersession_correlation():
    original = request()
    messages = stream(original)
    old = active_fill(original)
    redesign = deepcopy(original)
    redesign.request_sequence = 2
    redesign.operation = redesign.TARGETED_REDESIGN
    redesign.target_fill_id = redesign.target_cluster_id = redesign.target_revision = 1
    set_time(redesign.stamp, ORIGIN_NS+35_000_000_000)
    set_time(redesign.expires_at, ORIGIN_NS+40_000_000_000)
    redesign.source_timestamp = 35.
    rehash(redesign)
    messages[TOPICS['stationary_fill_requests']].append((10, redesign))
    messages[TOPICS['algorithm_state']].append((11, design(redesign)))
    superseded = deepcopy(old)
    superseded.active, superseded.superseded = False, True
    set_time(superseded.stamp, ORIGIN_NS+35_100_000_000)
    new = active_fill(redesign, fill_id=2, revision=2)
    messages[TOPICS['gaussian_fills']] = [(5, old), (12, superseded), (13, new), (14, deepcopy(old))]
    errors, result = audit(messages)
    assert errors == []
    assert result['counts']['unique_confirmations'] == 1
    assert result['counts']['requests_with_active_fill'] == 2
    assert result['outcomes'][1]['request_sequence'] == 1
    redesign.target_revision = 2
    rehash(redesign)
    assert audit(messages)[0]


@pytest.mark.parametrize('change', ['unmatched', 'invalid_correlation', 'frame', 'before_request', 'active_superseded'])
def test_legacy_fill_result_requires_original_request_join(change):
    message = request()
    messages = stream(message)
    fill = active_fill(message)
    if change == 'unmatched': fill.source_timestamp = 24.
    elif change == 'invalid_correlation': fill.source_timestamp_valid = False
    elif change == 'frame': fill.frame_id = 'map'
    elif change == 'before_request': set_time(fill.stamp, time_to_ns(message.stamp)-1)
    elif change == 'active_superseded': fill.superseded = True
    messages[TOPICS['gaussian_fills']] = [(5, fill)]
    assert audit(messages)[0]


def test_terminal_failure_is_an_observed_outcome_and_conflicting_success_is_invalid():
    message = request()
    messages = stream(message)
    event = AlgorithmEvent()
    event.event_type = event.EVENT_FILL_REJECTED
    event.source_timestamp, event.source_timestamp_valid = message.source_timestamp, True
    event.stamp = deepcopy(message.stamp)
    messages[TOPICS['algorithm_events']] = [(5, event), (7, deepcopy(event))]
    errors, result = audit(messages)
    assert errors == [] and result['counts']['requests_with_terminal_failure'] == 1
    assert result['counts']['requests_without_terminal_outcome'] == 0
    messages[TOPICS['gaussian_fills']] = [(6, active_fill(message))]
    assert audit(messages)[0]


@pytest.mark.parametrize('metric,mode,selected', [
    ('pde_mean_v1', 'stationary_v1', False), ('centroid_windows_v2', 'stationary_v1', True),
    ('pde_mean_v1', 'rolling_gesc_v2', False), ('centroid_windows_v2', 'rolling_gesc_v2', False),
])
def test_only_explicit_robust_arm_b_selects_recording_contract(metric, mode, selected):
    target = ['algorithm_profile:=robust_gaussian_v1', 'convergence_metric_mode:='+metric,
              'continuous_search_mode:='+mode]
    assert (stationary_centroid_config_from_target(target) is not None) is selected


@pytest.mark.parametrize('override', [
    'centroid_pose_stale_sec:=nan', 'centroid_state_stale_sec:=0',
    'centroid_window_sec:=-1', 'fill_design_timeout_sec:=inf',
    'candidate_informed_fill_enabled:=possibly', 'stationary_fill_request_topic:=/other',
])
def test_invalid_selected_configuration_is_rejected(override):
    with pytest.raises(ValueError):
        stationary_centroid_config_from_target([*ARGV, override])


def test_selected_manifest_requires_typed_presence_with_zero_events_allowed():
    manifest = load_manifest(PACKAGE/'ros_esc/experiment_recording/topic_manifest.yaml')
    entries = applicable_topics(manifest, 'simulation')
    next(entry for entry in entries if entry['alias'] == 'pose')['topic'] = '/selected/odom'
    selected = require_selected_algorithm_topics(entries, 'simulation', ARGV)
    entry = next(entry for entry in selected if entry['alias'] == 'stationary_fill_requests')
    assert entry['required'] and entry['minimum_messages'] == 0
    assert entry['type'] == 'ros_esc_interfaces/msg/StationaryFillRequest'
    assert entry['stationary_centroid_config'] == config()
    assert not next(entry for entry in entries if entry['alias'] == 'stationary_fill_requests')['required']


def test_existing_full_validator_runs_selected_audit(tmp_path, monkeypatch):
    entries = applicable_topics(load_manifest(PACKAGE/'ros_esc/experiment_recording/topic_manifest.yaml'), 'simulation')
    next(entry for entry in entries if entry['alias'] == 'pose')['topic'] = '/selected/odom'
    documents = {'metadata.yaml': {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
                 'target_argv': ARGV, 'run_id': 'separate-recorder-run', 'recording': {}, 'git': {}},
                 'resolved_topics.yaml': {'topics': entries},
                 'resolved_parameters.yaml': {'nodes': {}, 'failures': []}}
    monkeypatch.setattr(validator, '_load_yaml', lambda path: documents[Path(path).name])
    (tmp_path/'notes.md').write_text('Synthetic scoped audit; unrelated streams absent.\n')
    messages = stream()
    monkeypatch.setattr(validator, '_read_bag', lambda *_args: (
        {entry['topic']: entry['type'] for entry in entries}, messages))
    report = validator.validate_run_directory(tmp_path, write_report=False)
    assert not report['passed']  # This scoped fixture is not a complete run.
    assert report['checks']['stationary_centroid_contract']['passed']
    messages[TOPICS['stationary_fill_requests']][0][1].request_sha256 = 'bad'
    report = validator.validate_run_directory(tmp_path, write_report=False)
    assert not report['checks']['stationary_centroid_contract']['passed']


def test_analyzer_adds_scoped_intervals_and_never_redefines_historical_goal_time():
    messages = stream()
    bag = SimpleNamespace(records_by_topic={topic: [SimpleNamespace(bag_timestamp_ns=stamp, message=msg)
        for stamp, msg in records] for topic, records in messages.items()},
        topics_by_alias={alias: {'topic': topic} for alias, topic in TOPICS.items()})
    summary, metrics, tables = _stationary_centroid_analysis(bag, {'target_argv': ARGV})
    assert summary['status'] == 'valid'
    assert metrics['stationary_centroid_median_accepted_confirmation_to_request_sec']['value'] == pytest.approx(5.9)
    assert metrics['stationary_centroid_median_request_to_active_fill_publication_sec']['status'] == 'unavailable'
    assert 'convergence_time' not in metrics
    assert len(tables['stationary_centroid_requests.csv']) == 1
    assert _stationary_centroid_analysis(bag, {'target_argv': []}) == (None, {}, {})


def test_actual_sqlite_bag_reader_preserves_new_type_without_guessing_source_validity(tmp_path):
    import rosbag2_py
    import yaml
    from ros_esc.plotting_scripts.bag_reader import read_run_bag, records_for_alias
    message = request()
    messages = stream(message)
    names = {topic: alias for alias, topic in TOPICS.items()}
    names[config()['timekeeper_topic']] = 'timekeeper'
    entries = []
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=str(tmp_path/'bag'), storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('', ''))
    for topic, records in messages.items():
        type_name = 'ros_esc_interfaces/msg/' + type(records[0][1]).__name__
        entries.append({'alias': names[topic], 'topic': topic, 'type': type_name})
        writer.create_topic(rosbag2_py.TopicMetadata(name=topic, type=type_name, serialization_format='cdr'))
        for stamp, wire in records:
            writer.write(topic, serialize_message(wire), stamp)
    del writer
    (tmp_path/'resolved_topics.yaml').write_text(yaml.safe_dump({'topics': entries}))
    bag = read_run_bag(tmp_path)
    record, = records_for_alias(bag, 'stationary_fill_requests')
    assert record.message == message
    assert record.ros_timestamp_ns == time_to_ns(message.stamp)
    assert record.source_timestamp_sec == 25. and not record.source_timestamp_valid
    summary, _, _ = _stationary_centroid_analysis(bag, {'target_argv': ARGV})
    assert summary['status'] == 'valid'
