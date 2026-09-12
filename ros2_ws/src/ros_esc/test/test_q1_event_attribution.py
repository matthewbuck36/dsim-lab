"""Exact centroid CONFIG attribution without loosening shared event checks."""

from pathlib import Path

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from rosgraph_msgs.msg import Clock
import yaml

from ros_esc.experiment_recording import validate_run as validator
from ros_esc_interfaces.msg import AlgorithmEvent
from ros_esc.v2_stream import set_time
from test_convergence_detector_policy import centroid_node, _centroid_pose, _centroid_state


SIGNATURE = 'centroid_windows_v2 source-time configuration'


def event(detail=SIGNATURE, event_type=AlgorithmEvent.EVENT_CONFIGURATION, sec=10.):
    result = AlgorithmEvent()
    result.event_type, result.detail = event_type, detail
    set_time(result.stamp, round(sec * 1e9))
    return result


def test_actual_centroid_callback_publishes_recognized_configuration_once(centroid_node):
    node, now = centroid_node
    _centroid_state(node, now)
    _centroid_pose(node, now)
    _centroid_pose(node, now)
    configuration, = [message for message in node.algorithm_event_publisher.messages
                       if message.event_type == AlgorithmEvent.EVENT_CONFIGURATION]
    # Use the owner's message and actual wire serialization, not a fixture's
    # hand-authored detail, to catch future producer/classifier drift.
    configuration = deserialize_message(serialize_message(configuration), AlgorithmEvent)
    assert configuration.detail == SIGNATURE
    assert not configuration.source_timestamp_valid
    assert configuration.reason_code == 0
    assert configuration.value_names == [
        'centroid_window_sec', 'centroid_epsilon_m', 'centroid_maximum_radius_m',
        'centroid_maximum_gap_sec', 'centroid_pose_stale_sec', 'centroid_state_stale_sec',
        'recording_ready_required', 'recording_ready_stale_sec',
    ]
    assert validator.algorithm_event_producer_stream(configuration) == 'convergence_detector'


@pytest.mark.parametrize('detail', [
    '', 'unknown configuration', 'centroid_windows_v2',
    'centroid_windows_v2 source-time configuration extra',
    'centroid_windows_v2 source-time configuration ',
    ' centroid_windows_v2 source-time configuration',
    'centroid_windows_v3 source-time configuration',
])
def test_empty_unknown_and_near_match_configurations_remain_unidentified(detail):
    assert validator.algorithm_event_producer_stream(event(detail)) is None
    regressions, unknown = validator.algorithm_event_stream_regressions([(100, event(detail))], 0)
    assert regressions == []
    assert unknown == [{'bag_timestamp': 100, 'event_type': 1, 'detail': detail}]


@pytest.mark.parametrize('event_type', [AlgorithmEvent.EVENT_UNSPECIFIED, 999])
def test_signature_does_not_authorize_an_unknown_event_type(event_type):
    assert validator.algorithm_event_producer_stream(event(event_type=event_type)) is None


def test_known_other_event_owner_is_not_overridden_by_configuration_text():
    assert validator.algorithm_event_producer_stream(
        event(event_type=AlgorithmEvent.EVENT_CAPABILITY_UNAVAILABLE)) == 'cost_function'


@pytest.mark.parametrize('first_type,second_type', [
    (AlgorithmEvent.EVENT_CONFIGURATION, AlgorithmEvent.EVENT_CONVERGENCE_CANDIDATE),
    (AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED, AlgorithmEvent.EVENT_CONFIGURATION),
])
def test_configuration_participates_in_same_detector_timestamp_stream(first_type, second_type):
    messages = [(100, event(event_type=first_type, sec=10.)),
                (200, event(event_type=second_type, sec=9.))]
    regressions, unknown = validator.algorithm_event_stream_regressions(messages, 150_000_000)
    assert unknown == []
    assert len(regressions) == 1
    assert regressions[0]['producer_stream'] == 'convergence_detector'
    assert regressions[0]['previous'] == 10_000_000_000
    assert regressions[0]['current'] == 9_000_000_000


def test_cross_owner_interleaving_keeps_separate_timestamp_streams():
    messages = [(100, event(sec=10.)),
                (200, event('source_mode=simulation', sec=9.)),
                (300, event('convergence detector configuration', sec=10.1))]
    assert validator.algorithm_event_stream_regressions(messages, 0) == ([], [])


@pytest.mark.parametrize('detail,event_type,event_sec,attributed,fresh', [
    (SIGNATURE, AlgorithmEvent.EVENT_CONFIGURATION, 10., True, True),
    ('', AlgorithmEvent.EVENT_CONFIGURATION, 10., False, True),
    ('unknown configuration', AlgorithmEvent.EVENT_CONFIGURATION, 10., False, True),
    (SIGNATURE + ' extra', AlgorithmEvent.EVENT_CONFIGURATION, 10., False, True),
    (SIGNATURE, AlgorithmEvent.EVENT_UNSPECIFIED, 10., False, True),
    (SIGNATURE, AlgorithmEvent.EVENT_CONFIGURATION, 9., True, False),
])
def test_central_report_preserves_attribution_and_freshness_gates(
        monkeypatch, tmp_path, detail, event_type, event_sec, attributed, fresh):
    # Synthetic event-only records test the central check wiring. Missing
    # unrelated streams intentionally prevent claiming a complete run.
    entries = [
        {'alias': 'algorithm_events', 'topic': '/gesc_gaussian/algorithm_events',
         'type': 'ros_esc_interfaces/msg/AlgorithmEvent', 'required': False},
        {'alias': 'clock', 'topic': '/clock', 'type': 'rosgraph_msgs/msg/Clock', 'required': False},
    ]
    metadata = {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
                'recording': {'readiness_ever_true': True, 'pre_ready_nonzero_topics': {},
                              'pre_ready_lifecycle_violations': []}}
    for name, content in (
        ('metadata.yaml', metadata),
        ('resolved_topics.yaml', {'topics': entries,
                                  'validation': {'timestamp_regression_tolerance_sec': .15}}),
        ('resolved_parameters.yaml', {'failures': []}),
    ):
        (tmp_path / name).write_text(yaml.safe_dump(content))
    (tmp_path / 'notes.md').write_text('Synthetic event attribution fixture.\n')
    (tmp_path / 'console.log').write_text('')
    clock_records = []
    for receipt, sec in ((1, 9), (19, 10), (50, 11)):
        clock = Clock()
        set_time(clock.clock, sec * 1_000_000_000)
        clock_records.append((receipt, clock))
    messages = {'/clock': clock_records,
                '/gesc_gaussian/algorithm_events': [(20, event(detail, event_type, event_sec))]}
    bag_types = {entry['topic']: entry['type'] for entry in entries}
    monkeypatch.setattr(validator, '_read_bag', lambda *_: (bag_types, messages))
    report = validator.validate_run_directory(tmp_path, write_report=False)
    assert report['checks']['algorithm_event_producer_identified']['passed'] is attributed
    assert report['checks']['algorithm_event_emission_fresh']['passed'] is fresh
    assert report['checks']['algorithm_event_source_causality']['passed']
    assert not report['passed']  # This partial fixture is never a complete run.
