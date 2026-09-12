"""Selected recurrent Arm B joins through real CDR and existing evidence owners."""
from copy import deepcopy
from pathlib import Path

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import AlgorithmEvent, Timekeeper

from ros_esc.experiment_recording import stationary_centroid_validation as stationary
from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.record_run import (
    applicable_topics, load_manifest, require_selected_algorithm_topics,
    stationary_centroid_config_from_target,
)
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import _stationary_centroid_analysis
from ros_esc.stationary_fill_protocol import stationary_contract
from ros_esc.v2_lifecycle import message_payload
from ros_esc.v2_stream import time_to_ns
from test_r4_stationary_recurrent_protocol import ORIGIN_NS, POSE, request, rehash
from test_q5_stationary_recording_contract import active_fill, design
from test_m4_v8_stationary_causality import (
    full_report, causal, matching_legacy_request, forbidden_legacy,
)

PACKAGE = Path(__file__).resolve().parents[1]
MODE = 'recurrent_geometry_v3'
CONTRACT = stationary_contract(MODE)
ARGV = ['algorithm_profile:=robust_gaussian_v1', 'convergence_metric_mode:=' + MODE,
        'continuous_search_mode:=stationary_v1', 'algorithm_pose_topic:=' + POSE]


def config():
    return stationary_centroid_config_from_target(ARGV)


def stream(message=None):
    message = request() if message is None else message
    fill = active_fill(message)
    event = AlgorithmEvent()
    event.event_type, event.fill_id, event.fill_id_valid = event.EVENT_FILL_CREATED, fill.fill_id, True
    event.source_timestamp, event.source_timestamp_valid = message.source_timestamp, True
    event.stamp = deepcopy(fill.stamp)
    messages = {
        config()['timekeeper_topic']: [(1, Timekeeper(mode='sim time', start_time=ORIGIN_NS * 1e-9))],
        CONTRACT['diagnostics_topic']: [(2, deepcopy(message.confirmation))],
        CONTRACT['request_topic']: [(3, message)],
        stationary.TOPICS['algorithm_state']: [(4, design(message))],
        stationary.TOPICS['gaussian_fills']: [(5, fill)],
        stationary.TOPICS['algorithm_events']: [(6, event)],
    }
    return {topic: [(stamp, deserialize_message(serialize_message(wire), type(wire)))
                    for stamp, wire in rows] for topic, rows in messages.items()}


def entries():
    result = applicable_topics(load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml'),
                               'simulation')
    next(row for row in result if row['alias'] == 'pose')['topic'] = POSE
    return result


def wire_payloads(messages):
    # Use the protocol's full canonical field representation: NaN is not
    # Python-equal to itself and native CDR padding bytes are not deterministic.
    return {topic: [(stamp, message_payload(wire)) for stamp, wire in rows]
            for topic, rows in messages.items()}


@pytest.mark.parametrize('branch', ['static', 'circle', 'oscillation'])
def test_cdr_request_diagnostic_fill_event_and_full_validator_join(tmp_path, monkeypatch, branch):
    messages = stream(request(branch=branch))
    before = wire_payloads(messages)
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    report = full_report(tmp_path, monkeypatch, messages, ARGV)
    assert report['checks']['stationary_recurrent_contract']['passed']
    assert causal(report)['passed']
    audit = report['stationary_recurrent_audit']
    assert audit['counts']['unique_confirmations'] == audit['counts']['unique_requests'] == 1
    assert audit['counts']['requests_with_active_fill'] == 1
    assert audit['requests'][0]['source_timestamp'] == 70.
    assert audit['confirmations'][0]['branch'] == branch
    assert audit['confirmations'][0]['history_end_ns'] == ORIGIN_NS + 60_000_000_000
    assert audit['confirmations'][0]['persistence_start_ns'] >= ORIGIN_NS
    assert 'stationary_centroid_audit' not in report
    assert wire_payloads(messages) == before


def test_quiet_recurrent_pairing_keeps_typed_authority_selected(tmp_path, monkeypatch):
    messages = stream()
    for topic in (CONTRACT['request_topic'], CONTRACT['diagnostics_topic'],
                  stationary.TOPICS['gaussian_fills'], stationary.TOPICS['algorithm_events']):
        messages[topic] = []
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    report = full_report(tmp_path, monkeypatch, messages, ARGV)
    assert report['checks']['stationary_recurrent_contract']['passed'] and causal(report)['passed']
    assert report['stationary_recurrent_audit']['counts']['unique_requests'] == 0


@pytest.mark.parametrize('argument', ['stationary_recurrent_fill_request_topic', 'recurrent_diagnostics_topic'])
def test_invalid_selected_configuration_stays_recurrent_failure(tmp_path, monkeypatch, argument):
    messages = stream()
    matching_legacy_request(messages)
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    report = full_report(tmp_path, monkeypatch, messages,
                         [*ARGV, argument + ':=/wrong'])
    assert not report['checks']['stationary_recurrent_contract']['passed']
    assert not causal(report)['passed']


@pytest.mark.parametrize('fault', [
    'missing_request', 'missing_diagnostic', 'nested_hash', 'request_hash',
    'correlation', 'persistence_origin', 'wrong_envelope', 'unavailable_audit',
])
def test_invalid_recurrent_authority_cannot_use_matching_legacy(tmp_path, monkeypatch, fault):
    messages = stream()
    message = messages[CONTRACT['request_topic']][0][1]
    if fault == 'missing_request': messages[CONTRACT['request_topic']] = []
    elif fault == 'missing_diagnostic': messages[CONTRACT['diagnostics_topic']] = []
    elif fault == 'nested_hash': message.confirmation.reset_sequence += 1
    elif fault == 'request_hash': message.request_sha256 = 'invalid'
    elif fault == 'correlation': message.source_timestamp += 1.
    elif fault == 'persistence_origin': message.confirmation.persistence_start.sec = 999
    elif fault == 'wrong_envelope':
        from test_q5_stationary_fill_protocol import request as old_request
        messages[CONTRACT['request_topic']] = [(3, old_request())]
    elif fault == 'unavailable_audit':
        monkeypatch.setattr(stationary, 'stationary_centroid_stream_errors', lambda *_a, **_k: (None, None))
    if fault != 'request_hash': rehash(message)
    matching_legacy_request(messages)
    monkeypatch.setattr(validator, 'fill_event_source_causality', forbidden_legacy)
    report = full_report(tmp_path, monkeypatch, messages, ARGV)
    assert not report['checks']['stationary_recurrent_contract']['passed']
    assert not causal(report)['passed']


def test_selected_presence_descriptor_and_fixed_configuration():
    original = entries()
    before = deepcopy(original)
    selected = require_selected_algorithm_topics(original, 'simulation', ARGV)
    by_alias = {row['alias']: row for row in selected}
    req = by_alias[CONTRACT['request_alias']]
    assert req['required'] and req['singleton_publisher'] and req['minimum_messages'] == 0
    assert req['type'] == CONTRACT['request_type'] and req['stationary_centroid_config'] == config()
    assert by_alias[CONTRACT['diagnostics_alias']]['algorithm_required']
    assert not by_alias['stationary_fill_requests']['required']
    assert not any(key in config() for key in ('window_sec', 'epsilon_m', 'maximum_radius_m'))
    assert require_selected_algorithm_topics(selected, 'simulation', ARGV) == selected
    assert original == before
    req['stationary_centroid_config'] = dict(config(), design_timeout_sec=6.)
    with pytest.raises(ValueError, match='recorded stationary configuration differs'):
        require_selected_algorithm_topics(selected, 'simulation', ARGV)


@pytest.mark.parametrize('fault', ['missing', 'type', 'topic', 'timekeeper'])
def test_recording_requires_the_selected_request_and_origin(fault):
    rows = entries()
    if fault == 'missing': rows = [row for row in rows if row['alias'] != CONTRACT['request_alias']]
    else:
        row = next(row for row in rows if row['alias'] == (
            'timekeeper' if fault == 'timekeeper' else CONTRACT['request_alias']))
        if fault == 'type': row['type'] = 'ros_esc_interfaces/msg/StationaryFillRequest'
        else: row['topic'] = '/wrong'
    with pytest.raises(ValueError, match='selected stationary stream missing or incompatible'):
        require_selected_algorithm_topics(rows, 'simulation', ARGV)


def test_unselected_old_request_is_not_silently_ignored():
    from test_q5_stationary_fill_protocol import request as old_request
    messages = stream()
    messages[stationary.TOPICS['stationary_fill_requests']] = [(7, old_request())]
    errors, _ = stationary.stationary_centroid_stream_errors(messages, config())
    assert any('unselected stationary envelope' in error for error in errors)


def test_sqlite_reader_and_analyzer_preserve_recurrent_evidence_names(tmp_path):
    import rosbag2_py
    import yaml
    from ros_esc.plotting_scripts.bag_reader import read_run_bag, records_for_alias
    messages = stream()
    names = {topic: alias for alias, topic in stationary.TOPICS.items()}
    names[config()['timekeeper_topic']] = 'timekeeper'
    resolved = []
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=str(tmp_path / 'bag'), storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('', ''))
    for topic, rows in messages.items():
        wire_type = 'ros_esc_interfaces/msg/' + type(rows[0][1]).__name__
        resolved.append({'alias': names[topic], 'topic': topic, 'type': wire_type})
        writer.create_topic(rosbag2_py.TopicMetadata(name=topic, type=wire_type, serialization_format='cdr'))
        for stamp, wire in rows: writer.write(topic, serialize_message(wire), stamp)
    del writer
    (tmp_path / 'resolved_topics.yaml').write_text(yaml.safe_dump({'topics': resolved}))
    bag = read_run_bag(tmp_path)
    record, = records_for_alias(bag, CONTRACT['request_alias'])
    assert message_payload(record.message) == message_payload(messages[CONTRACT['request_topic']][0][1])
    assert record.ros_timestamp_ns == time_to_ns(record.message.stamp)
    summary, metrics, tables = _stationary_centroid_analysis(bag, {'target_argv': ARGV})
    assert summary['status'] == 'valid' and summary['metric_mode'] == MODE
    assert metrics['stationary_recurrent_median_accepted_confirmation_to_request_sec']['value'] == pytest.approx(9.8)
    assert len(tables['stationary_recurrent_requests.csv']) == 1
    assert not any(key.startswith('stationary_centroid') for key in [*metrics, *tables])
    # A changed nested observation invalidates the same analyzer owner.
    record.message.confirmation.reset_sequence += 1
    invalid, invalid_metrics, _ = _stationary_centroid_analysis(bag, {'target_argv': ARGV})
    assert invalid['status'] == 'invalid'
    assert invalid_metrics['stationary_recurrent_median_accepted_confirmation_to_request_sec']['status'] == 'invalid'
