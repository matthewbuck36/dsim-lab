"""Full recorder validation of original centroid receipts after clock coverage.

The metric is emitted by the actual node/core on synthetic stationary poses.
Only bag/YAML transport is substituted; unrelated missing streams deliberately
prevent this narrow fixture from claiming complete recording acceptance.
"""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
from rclpy.serialization import deserialize_message, serialize_message

from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.record_run import (
    applicable_topics, load_manifest, require_selected_algorithm_topics,
)
from ros_esc_interfaces.msg import AlgorithmState
from test_convergence_detector_policy import centroid_node, _centroid_drive  # noqa: F401
from test_q3_centroid_clock_admission import clock_node, pose, state  # noqa: F401


PACKAGE = Path(__file__).resolve().parents[1]
ALIAS = 'centroid_convergence_diagnostics'
MARKER = 'centroid_original_receipt_v1'


def ns(stamp):
    return stamp.sec * 1_000_000_000 + stamp.nanosec


def set_ns(stamp, value):
    stamp.sec, stamp.nanosec = divmod(value, 1_000_000_000)


@pytest.fixture
def emitted_confirmation(clock_node):
    node, now, _ = clock_node
    _centroid_drive(node, now, 17.9)
    receipt, source = now[0], now[0] + 100_000_000
    node.algorithm_state_cb(state(node, source))
    node.pose_cb(pose(node, source))
    assert not any(message.confirmed for message in node.centroid_publisher.messages)
    now[0] = source
    node._centroid_watchdog_cb()
    message, = [message for message in node.centroid_publisher.messages if message.confirmed]
    assert message.represented_duration_sec == 18.0
    assert ns(message.receipt_stamp) == receipt
    assert ns(message.source_stamp) == ns(message.stamp) == source
    # Exercise the actual generated message transport representation as well.
    return deserialize_message(serialize_message(message), type(message))


@pytest.fixture
def recorded_run(tmp_path, monkeypatch, emitted_confirmation):
    message = emitted_confirmation
    manifest = load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml')
    entries = applicable_topics(manifest, 'simulation')
    next(entry for entry in entries if entry['alias'] == 'pose')['topic'] = message.source_pose_topic
    aliases = {entry['alias']: entry['topic'] for entry in entries}
    metadata = {
        'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
        'recording': {}, 'git': {}, 'run_id': 'independent-recorder-name',
        'target_argv': ['convergence_metric_mode:=centroid_windows_v2',
                        'algorithm_pose_topic:=' + message.source_pose_topic],
    }
    documents = {
        'metadata.yaml': metadata, 'resolved_topics.yaml': {'topics': entries},
        'resolved_parameters.yaml': {'nodes': {}, 'failures': []},
    }
    monkeypatch.setattr(validator, '_load_yaml', lambda path: documents[Path(path).name])
    (tmp_path / 'notes.md').write_text('Synthetic actual-node centroid recorder contract.\n')
    supervisor = AlgorithmState()
    supervisor.stamp = deepcopy(message.stamp)
    supervisor.run_id = message.run_id
    supervisor.state = AlgorithmState.STATE_SEARCH
    supervisor.state_valid = supervisor.run_id_valid = True
    receipt = 10_000_000_000_000
    messages = {
        aliases['clock']: [(receipt, SimpleNamespace(clock=deepcopy(message.stamp)))],
        aliases['recording_ready']: [(receipt, SimpleNamespace(data=True))],
        aliases['algorithm_state']: [(receipt, supervisor)],
        aliases[ALIAS]: [(receipt, message)],
    }
    monkeypatch.setattr(validator, '_read_bag', lambda *_args: (
        {entry['topic']: entry['type'] for entry in entries}, messages,
    ))

    def run():
        report = validator.validate_run_directory(tmp_path, write_report=False)
        assert not report['passed']  # This is not a complete recording fixture.
        return report['checks']['centroid_diagnostics_consistent']

    return SimpleNamespace(run=run, message=message, metadata=metadata,
                           entries=entries, supervisor=supervisor)


def test_actual_deferred_confirmation_passes_selected_full_validator(recorded_run):
    run = recorded_run
    original = deepcopy(run.entries)
    selected = require_selected_algorithm_topics(
        run.entries, 'simulation', run.metadata['target_argv'])
    entry = next(entry for entry in selected if entry['alias'] == ALIAS)
    assert entry['algorithm_clock_admission'] == MARKER
    assert entry['algorithm_pose_stale_sec'] == 0.5
    assert run.entries == original
    assert run.run()['passed']


def test_unselected_full_validator_keeps_historical_receipt_order(recorded_run):
    run = recorded_run
    run.metadata['target_argv'] = []
    result = run.run()
    assert not result['passed']
    assert any('times disagree' in error for error in result['detail'])
    run.message.receipt_stamp = deepcopy(run.message.source_stamp)
    assert run.run()['passed']


@pytest.mark.parametrize(('limit', 'receipt_age_ns', 'passed'), [
    (0.2, 200_000_000, True), (0.2, 200_000_001, False),
    (0.75, 700_000_000, True), (0.5, 700_000_000, False),
])
def test_declared_positive_limit_is_effective_without_hardcoded_clamping(
        recorded_run, limit, receipt_age_ns, passed):
    run = recorded_run
    run.metadata['target_argv'].append(f'centroid_pose_stale_sec:={limit}')
    set_ns(run.message.receipt_stamp, ns(run.message.stamp) - receipt_age_ns)
    assert run.run()['passed'] is passed


@pytest.mark.parametrize('fault', [
    'publication_before_source', 'publication_before_receipt',
    'expired_original_receipt', 'expired_source', 'wrong_run', 'wrong_pose_topic',
])
def test_selected_admission_does_not_relax_support_identity_or_freshness(recorded_run, fault):
    run, message = recorded_run, recorded_run.message
    source = ns(message.source_stamp)
    if fault == 'publication_before_source':
        set_ns(message.stamp, source - 1)
    elif fault == 'publication_before_receipt':
        set_ns(message.receipt_stamp, source + 1)
    elif fault == 'expired_original_receipt':
        set_ns(message.receipt_stamp, source - 500_000_001)
    elif fault == 'expired_source':
        set_ns(message.stamp, source + 500_000_001)
        message.receipt_stamp = deepcopy(message.stamp)
    elif fault == 'wrong_run':
        message.run_id = 'another-supervisor'
    elif fault == 'wrong_pose_topic':
        message.source_pose_topic = '/unselected_pose'
    assert not run.run()['passed']


@pytest.mark.parametrize('bound', [None, True, '0.5', 0.0, -1.0,
                                  float('nan'), float('inf'), 1e308, 1e-300])
def test_saved_selected_marker_requires_valid_explicit_bound(recorded_run, bound):
    run = recorded_run
    # Exercise the saved-entry validator route directly. With selected launch
    # argv the canonical recorder owner reconstructs these same fields.
    run.metadata['target_argv'] = []
    entry = next(entry for entry in run.entries if entry['alias'] == ALIAS)
    entry['algorithm_clock_admission'] = MARKER
    if bound is not None:
        entry['algorithm_pose_stale_sec'] = bound
    result = run.run()
    assert not result['passed']
    assert any('pose freshness' in error for error in result['detail'])


@pytest.mark.parametrize('marker', ['unknown', '', None])
def test_unknown_saved_admission_marker_is_not_authority(recorded_run, marker):
    run = recorded_run
    run.metadata['target_argv'] = []
    entry = next(entry for entry in run.entries if entry['alias'] == ALIAS)
    entry.update(algorithm_clock_admission=marker, algorithm_pose_stale_sec=0.5)
    result = run.run()
    assert not result['passed']
    assert any('unknown clock admission policy' in error for error in result['detail'])
