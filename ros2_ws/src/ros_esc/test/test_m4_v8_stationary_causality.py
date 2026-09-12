"""Selected stationary typed authority through the existing full run validator.

Q5 wire fixtures supply a typed request, active fill and owner event together.
Only recorded file/bag inputs are substituted; stationary authority and the
legacy causal checker run unchanged. These incomplete synthetic recordings do
not establish complete-run acceptance, live callback authority or robot motion.
Moving precedence tests isolate dispatch with an explicit supplied lifecycle
verdict; the separately selected moving regressions own that protocol evidence.
"""
from copy import deepcopy
from pathlib import Path

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import AlgorithmEvent, StampedFloat64MultiArray

from ros_esc.experiment_recording import stationary_centroid_validation as stationary
from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.record_run import applicable_topics, load_manifest
from ros_esc.v2_stream import set_time, time_to_ns
from test_q5_stationary_fill_protocol import ORIGIN_NS, POSE, RUN, request, rehash
from test_q5_stationary_recording_contract import TOPICS, active_fill, design, stream


PACKAGE = Path(__file__).resolve().parents[1]
MODES = [('centroid_windows_v2', 'five_shift'), ('centroid_two_block_v2', 'two_block')]
MODE_CASES = [pytest.param(mode, id=name) for mode, name in MODES]
LEGACY_TOPIC = '/gesc_gaussian/fill_requests'
FAULTS = ['missing_request', 'missing_origin', 'request_hash', 'wrong_run',
          'before_request', 'wrong_event_source']
UNAVAILABLE = [
    'invalid_window', 'wrong_request_topic', 'authority_value_error',
    'authority_key_error', 'missing_error_list', 'missing_audit',
]


def target(metric_mode):
    return ['algorithm_profile:=robust_gaussian_v1',
            'convergence_metric_mode:=' + metric_mode,
            'continuous_search_mode:=stationary_v1', 'algorithm_pose_topic:=' + POSE]


def selected_wire(metric_mode):
    typed = request()
    typed.confirmation.metric_mode = metric_mode
    rehash(typed)
    messages = stream(typed)
    fill = active_fill(typed)
    event = AlgorithmEvent()
    event.event_type, event.fill_id, event.fill_id_valid = event.EVENT_FILL_CREATED, fill.fill_id, True
    event.source_timestamp, event.source_timestamp_valid = typed.source_timestamp, True
    event.stamp = deepcopy(fill.stamp)
    event.detail = 'synthetic recorded robust fill publication'
    messages[TOPICS['gaussian_fills']] = [(5, fill)]
    messages[TOPICS['algorithm_events']] = [(6, event)]
    # Use actual CDR wire objects, including the nonzero-origin confirmation.
    messages = {topic: [(stamp, deserialize_message(serialize_message(msg), type(msg)))
                        for stamp, msg in rows] for topic, rows in messages.items()}
    return messages


def full_report(tmp_path, monkeypatch, messages, argv, *, run_id='separate-recorder-run'):
    entries = applicable_topics(load_manifest(
        PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml'), 'simulation')
    next(entry for entry in entries if entry['alias'] == 'pose')['topic'] = POSE
    documents = {
        'metadata.yaml': {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
            'target_argv': argv, 'run_id': run_id, 'recording': {}, 'git': {}},
        'resolved_topics.yaml': {'topics': entries},
        'resolved_parameters.yaml': {'nodes': {}, 'failures': []},
    }
    monkeypatch.setattr(validator, '_load_yaml', lambda path: documents[Path(path).name])
    monkeypatch.setattr(validator, '_read_bag', lambda *_args: (
        {entry['topic']: entry['type'] for entry in entries}, messages))
    (tmp_path / 'notes.md').write_text('Synthetic scoped stationary causality fixture; unrelated streams absent.\n')
    result = validator.validate_run_directory(tmp_path, write_report=False)
    assert not result['passed'], 'Missing complete-recording streams must remain failures'
    assert not (tmp_path / 'completeness.json').exists(), 'Read-only validator wrote a report'
    return result


def causal(report):
    return report['checks']['algorithm_event_source_causality']


def matching_legacy_request(messages):
    event = messages[TOPICS['algorithm_events']][0][1]
    messages[LEGACY_TOPIC] = [(0, StampedFloat64MultiArray(timestamp=event.source_timestamp))]


def forbidden_legacy(*_args, **_kwargs):
    raise AssertionError('selected typed authority must not call the legacy causal helper')


@pytest.mark.parametrize('metric_mode', MODE_CASES)
def test_full_validator_accepts_typed_request_fill_event_without_legacy(tmp_path, monkeypatch, metric_mode):
    messages = selected_wire(metric_mode)
    original = deepcopy(messages)
    typed = messages[TOPICS['stationary_fill_requests']][0][1]
    event = messages[TOPICS['algorithm_events']][0][1]
    assert time_to_ns(typed.time_origin) == ORIGIN_NS
    assert event.source_timestamp == typed.source_timestamp == 25.
    assert time_to_ns(event.stamp) >= time_to_ns(typed.stamp)
    assert not messages.get(LEGACY_TOPIC)
    # The standalone legacy owner must keep rejecting exactly this input.
    assert validator.fill_event_source_causality(messages[TOPICS['algorithm_events']], [])
    result = full_report(tmp_path, monkeypatch, messages, target(metric_mode))
    assert result['checks']['stationary_centroid_contract']['passed']
    audit = result['stationary_centroid_audit']
    assert audit['counts']['unique_requests'] == audit['counts']['requests_with_active_fill'] == 1
    assert [row['kind'] for row in audit['outcomes']] == ['fill', 'event']
    assert causal(result)['passed'] and causal(result)['detail'] == []
    assert messages == original, 'Validator must not synthesize requests or rewrite wire messages'


@pytest.mark.parametrize('metric_mode', MODE_CASES)
def test_quiet_selected_authority_stays_selected_without_invented_occurrences(tmp_path, monkeypatch, metric_mode):
    messages = selected_wire(metric_mode)
    for alias in ('stationary_fill_requests', 'centroid_convergence_diagnostics', 'gaussian_fills', 'algorithm_events'):
        messages[TOPICS[alias]] = []
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    result = full_report(tmp_path, monkeypatch, messages, target(metric_mode))
    assert result['checks']['stationary_centroid_contract']['passed']
    assert result['stationary_centroid_audit']['counts']['unique_requests'] == 0
    assert causal(result)['passed'] and causal(result)['detail'] == []


@pytest.mark.parametrize('fault', FAULTS)
def test_invalid_typed_authority_cannot_be_rescued_by_matching_legacy(tmp_path, monkeypatch, fault):
    metric_mode = 'centroid_two_block_v2'
    messages = selected_wire(metric_mode)
    typed = messages[TOPICS['stationary_fill_requests']][0][1]
    event = messages[TOPICS['algorithm_events']][0][1]
    if fault == 'missing_request':
        messages[TOPICS['stationary_fill_requests']] = []
    elif fault == 'missing_origin':
        messages['/turtlebot3/timekeeper_chatter'] = []
    elif fault == 'request_hash':
        typed.request_sha256 = 'a' * 64
    elif fault == 'wrong_run':
        typed.confirmation.run_id = 'foreign-supervisor'
    elif fault == 'before_request':
        set_time(event.stamp, time_to_ns(typed.stamp) - 1)
    elif fault == 'wrong_event_source':
        event.source_timestamp += 1.
    else:
        raise AssertionError(fault)
    if fault != 'request_hash':
        rehash(typed)
    matching_legacy_request(messages)
    result = full_report(tmp_path, monkeypatch, messages, target(metric_mode))
    assert not result['checks']['stationary_centroid_contract']['passed'], fault
    assert not causal(result)['passed'] and causal(result)['detail'], fault


@pytest.mark.parametrize('fault', UNAVAILABLE)
def test_unavailable_selected_authority_fails_closed_without_legacy_fallback(tmp_path, monkeypatch, fault):
    metric_mode = 'centroid_two_block_v2'
    messages = selected_wire(metric_mode)
    matching_legacy_request(messages)
    argv = target(metric_mode)
    if fault == 'invalid_window':
        argv.append('centroid_window_sec:=nan')
    elif fault == 'wrong_request_topic':
        argv.append('stationary_fill_request_topic:=/unapproved/request')
    else:
        def unavailable(*_args, **_kwargs):
            if fault == 'authority_value_error':
                raise ValueError('injected unavailable stationary authority')
            if fault == 'authority_key_error':
                raise KeyError('injected missing stationary authority field')
            return (None, {}) if fault == 'missing_error_list' else ([], None)
        monkeypatch.setattr(stationary, 'stationary_centroid_stream_errors', unavailable)
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    result = full_report(tmp_path, monkeypatch, messages, argv)
    assert not result['checks']['stationary_centroid_contract']['passed']
    assert not causal(result)['passed'] and causal(result)['detail']


@pytest.mark.parametrize('metric_mode', MODE_CASES)
def test_exact_typed_retries_and_original_supersession_correlation_remain_valid(tmp_path, monkeypatch, metric_mode):
    messages = selected_wire(metric_mode)
    original = messages[TOPICS['stationary_fill_requests']][0][1]
    old_fill = messages[TOPICS['gaussian_fills']][0][1]
    old_event = messages[TOPICS['algorithm_events']][0][1]
    redesign = deepcopy(original)
    redesign.request_sequence = 2
    redesign.operation = redesign.TARGETED_REDESIGN
    redesign.target_fill_id = redesign.target_cluster_id = redesign.target_revision = 1
    set_time(redesign.stamp, ORIGIN_NS + 35_000_000_000)
    set_time(redesign.expires_at, ORIGIN_NS + 40_000_000_000)
    redesign.source_timestamp = 35.
    rehash(redesign)
    messages[TOPICS['stationary_fill_requests']] += [(7, deepcopy(original)), (8, redesign)]
    messages[TOPICS['algorithm_state']].append((9, design(redesign)))
    retired = deepcopy(old_fill)
    retired.active, retired.superseded = False, True
    set_time(retired.stamp, ORIGIN_NS + 35_100_000_000)
    active = active_fill(redesign, fill_id=2, revision=2)
    superseded, merged = deepcopy(old_event), deepcopy(old_event)
    superseded.event_type = superseded.EVENT_FILL_SUPERSEDED
    superseded.stamp = deepcopy(retired.stamp)
    merged.event_type, merged.fill_id = merged.EVENT_FILL_MERGED, 2
    merged.source_timestamp, merged.stamp = redesign.source_timestamp, deepcopy(active.stamp)
    messages[TOPICS['gaussian_fills']] += [(10, retired), (11, active), (15, deepcopy(active))]
    messages[TOPICS['algorithm_events']] += [(12, superseded), (13, merged), (16, deepcopy(merged))]
    result = full_report(tmp_path, monkeypatch, messages, target(metric_mode))
    assert result['checks']['stationary_centroid_contract']['passed']
    assert causal(result)['passed']
    audit = result['stationary_centroid_audit']
    assert audit['counts']['unique_requests'] == 2 and audit['counts']['request_retries'] == 1
    events = [row for row in audit['outcomes'] if row['kind'] == 'event']
    assert [row['request_sequence'] for row in events] == [1, 1, 2]


@pytest.mark.parametrize('fault,expected', [
    ('exact', True), ('missing', False), ('nearby', False),
    ('invalid_source', False), ('nonfill_event', True)])
def test_legacy_profile_keeps_exact_standalone_source_matching(tmp_path, monkeypatch, fault, expected):
    event = selected_wire('centroid_windows_v2')[TOPICS['algorithm_events']][0][1]
    messages = {TOPICS['algorithm_events']: [(1, event)]}
    matching_legacy_request(messages)
    if fault == 'missing':
        messages[LEGACY_TOPIC] = []
    elif fault == 'nearby':
        messages[LEGACY_TOPIC][0][1].timestamp += 0.5e-9
    elif fault == 'invalid_source':
        event.source_timestamp_valid = False
    elif fault == 'nonfill_event':
        event.event_type = event.EVENT_CONVERGENCE_CONFIRMED
    monkeypatch.setattr(stationary, 'stationary_centroid_stream_errors', forbidden_legacy)
    direct = validator.fill_event_source_causality(messages[TOPICS['algorithm_events']], messages[LEGACY_TOPIC])
    result = full_report(tmp_path, monkeypatch, messages, target('pde_mean_v1'))
    assert 'stationary_centroid_contract' not in result['checks']
    assert causal(result)['passed'] is expected
    assert causal(result)['detail'] == direct


@pytest.mark.parametrize('moving_error', [False, True], ids=['moving_pass', 'moving_failure'])
def test_moving_authority_keeps_precedence_over_available_stationary_authority(tmp_path, monkeypatch, moving_error):
    messages = selected_wire('centroid_two_block_v2')
    identity = {'run_id': RUN, 'stream_config': {'frame_id': 'odom'}}
    errors = ['injected moving authority failure'] if moving_error else []
    calls = []
    monkeypatch.setattr(validator, 'v2_identity_from_metadata', lambda _metadata: identity)
    monkeypatch.setattr(validator, 'v2_stream_contract_errors', lambda *_args: [])
    def moving_authority(*_args, **kwargs):
        calls.append(kwargs)
        return list(errors), {'fill_event_source_causality': {'errors': list(errors)}}
    monkeypatch.setattr(validator, 'lifecycle_stream_errors', moving_authority)
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    # Deliberately supply both authorities to isolate dispatch precedence; this
    # is not a claim that contradictory stationary/moving metadata is admissible.
    result = full_report(tmp_path, monkeypatch, messages, target('centroid_two_block_v2'), run_id=RUN)
    assert calls and calls[0]['validate_fill_events'] is True
    assert result['checks']['stationary_centroid_contract']['passed']
    assert causal(result)['passed'] is (not moving_error)
    assert causal(result)['detail'] == errors
