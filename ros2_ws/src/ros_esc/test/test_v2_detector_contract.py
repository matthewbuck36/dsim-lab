"""V2 detector configuration, launch routing and typed recording contracts."""

from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import AlgorithmState, CentroidConvergenceDiagnostics

from ros_esc.experiment_recording.record_run import applicable_topics, load_manifest
from ros_esc.experiment_recording.record_run import require_selected_algorithm_topics
from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.validate_run import (
    centroid_diagnostic_errors, centroid_stream_errors,
)
from ros_esc.scenario_runner.scenario_schema import _validate_correction_overrides


PACKAGE = Path(__file__).resolve().parents[1]


def validate(overrides):
    _validate_correction_overrides(
        overrides,
        {'affine_assist_enabled': True, 'gaussian_fill_enabled': True,
         'recenter_enabled': True},
        'test.algorithm.launch_overrides',
    )


def test_default_contract_and_opt_in_do_not_require_inherited_dwell():
    validate({})
    validate({'convergence_metric_mode': 'centroid_windows_v2',
              'convergence_state_gating_enabled': True,
              'centroid_window_sec': 3.0, 'centroid_epsilon_m': 0.06,
              'centroid_maximum_radius_m': 0.5,
              'centroid_maximum_gap_sec': 0.5})


@pytest.mark.parametrize('name', [
    'centroid_window_sec', 'centroid_epsilon_m',
    'centroid_maximum_radius_m', 'centroid_maximum_gap_sec',
])
@pytest.mark.parametrize('value', [0.0, -1.0, float('nan'), float('inf'), True, '3'])
def test_invalid_centroid_tuning_rejected(name, value):
    with pytest.raises(ValueError, match=name):
        validate({name: value})


def test_unknown_mode_and_ungated_centroid_rejected():
    with pytest.raises(ValueError, match='metric_mode'):
        validate({'convergence_metric_mode': 'centroid_typo'})
    with pytest.raises(ValueError, match='state_gating_enabled'):
        validate({'convergence_metric_mode': 'centroid_windows_v2'})


def test_launch_retains_default_and_routes_selected_pose_to_detector():
    launch = ET.parse(PACKAGE.parent / 'turtlebot3_rotating_sensor/launch/gazebo.launch.xml')
    defaults = {arg.attrib['name']: arg.attrib.get('default')
                for arg in launch.findall('arg')}
    assert defaults['convergence_metric_mode'] == 'pde_mean_v1'
    commands = [item.attrib.get('cmd', '') for item in launch.findall('executable')]
    detector = next(cmd for cmd in commands if 'ros_esc convergence_detector_node' in cmd)
    assert '-p pose_topic:=$(var algorithm_pose_topic)' in detector
    for name in ('convergence_metric_mode', 'centroid_window_sec',
                 'centroid_epsilon_m', 'centroid_maximum_radius_m',
                 'centroid_maximum_gap_sec', 'convergence_diagnostics_topic'):
        assert f'-p {name}:=$(var {name})' in detector


def test_typed_diagnostic_roundtrip_preserves_absolute_time_and_metre_score():
    msg = CentroidConvergenceDiagnostics()
    msg.source_stamp.sec = 123
    msg.source_stamp.nanosec = 456
    msg.run_id = 'roundtrip'
    msg.search_epoch = 4
    msg.confirmation_sequence = 2
    msg.score_m = 0.03
    msg.displacement_m = [0.006] * 5
    msg.source_valid = msg.metric_valid = msg.confirmed = True
    decoded = deserialize_message(serialize_message(msg), type(msg))
    assert decoded.source_stamp.sec == 123 and decoded.source_stamp.nanosec == 456
    assert decoded.run_id == 'roundtrip' and decoded.search_epoch == 4
    assert decoded.score_m == pytest.approx(sum(decoded.displacement_m))
    assert decoded.metric_valid and decoded.confirmed
    assert not hasattr(decoded, 'r_mean_m2')


def test_recorder_includes_new_diagnostics_only_for_simulation():
    manifest = load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml')
    alias = 'centroid_convergence_diagnostics'
    simulation = {item['alias']: item for item in applicable_topics(manifest, 'simulation')}
    physical = {item['alias']: item for item in applicable_topics(manifest, 'physical')}
    assert simulation[alias]['type'] == 'ros_esc_interfaces/msg/CentroidConvergenceDiagnostics'
    assert not simulation[alias]['required']  # Inherited mode emits no V2 stream.
    assert alias not in physical


def valid_centroid_diagnostic():
    message = CentroidConvergenceDiagnostics()
    message.metric_mode = 'centroid_windows_v2'
    message.source_pose_topic = '/odom'
    message.run_id, message.frame_id = 'test', 'odom'
    message.search_epoch = message.confirmation_sequence = 1
    message.window_duration_sec = 3.0
    message.epsilon_m, message.maximum_radius_m = 0.06, 0.5
    message.represented_duration_sec = 18.0
    message.maximum_source_gap_sec = 0.1
    message.sample_count = 181
    message.completed_window_count = 6
    message.centroid_x_m = [1.0] * 6
    message.centroid_y_m = [2.0] * 6
    message.center_x_m, message.center_y_m = 1.0, 2.0
    message.displacement_m = [0.0] * 5
    message.source_valid = message.history_valid = True
    message.metric_valid = message.confinement_valid = True
    message.eligible = message.confirmed = True
    stamp_type = type(message.stamp)
    message.window_start = [stamp_type(sec=1 + 3*i) for i in range(6)]
    message.window_end = [stamp_type(sec=4 + 3*i) for i in range(6)]
    message.history_start.sec = 1
    message.history_end.sec = 19
    message.source_stamp.sec = message.receipt_stamp.sec = message.stamp.sec = 19
    return message


def test_recorded_centroid_can_be_complete_without_confirmation():
    message = valid_centroid_diagnostic()
    assert centroid_diagnostic_errors([message]) == []
    ongoing = deepcopy(message)
    ongoing.confirmed = False
    assert centroid_diagnostic_errors([message, ongoing]) == []
    assert any('repeated SEARCH' in error for error in centroid_diagnostic_errors([message, message]))
    new_epoch = deepcopy(message)
    new_epoch.search_epoch = new_epoch.confirmation_sequence = 2
    assert centroid_diagnostic_errors([message, new_epoch]) == []


def test_original_receipt_can_precede_source_only_with_selected_clock_admission():
    message = valid_centroid_diagnostic()
    message.receipt_stamp.sec = 18
    message.receipt_stamp.nanosec = 900_000_000
    assert centroid_diagnostic_errors([message])
    assert centroid_diagnostic_errors([message], allow_clock_admission=True,
                                      expected_frame_id='odom') == []
    assert centroid_diagnostic_errors([message], allow_clock_admission=True,
                                      expected_frame_id='map')
    message.receipt_stamp.nanosec = 499_999_999
    assert centroid_diagnostic_errors([message], allow_clock_admission=True)


@pytest.mark.parametrize(('field', 'value', 'error'), [
    ('score_m', 0.02, 'five centroid distances'),
    ('confinement_radius_m', 0.6, 'radius threshold'),
    ('center_x_m', 1.2, 'six equal-duration centroids'),
    ('represented_duration_sec', 17.0, 'support'),
    ('completed_window_count', 5, 'six finite windows'),
    ('history_valid', False, 'source/history validity'),
    ('eligible', False, 'confirmation without eligibility'),
    ('metric_mode', 'pde_mean_v1', 'wrong metric mode'),
])
def test_recording_rejects_internally_inconsistent_centroid_claims(field, value, error):
    message = valid_centroid_diagnostic()
    setattr(message, field, value)
    assert any(error in reason for reason in centroid_diagnostic_errors([message]))


def test_incomplete_history_is_not_a_zero_score_claim():
    message = CentroidConvergenceDiagnostics()
    message.metric_mode = 'centroid_windows_v2'
    message.source_pose_topic = '/odom'
    message.score_m = float('nan')
    assert centroid_diagnostic_errors([message]) == []
    message.eligible = True
    assert centroid_diagnostic_errors([message])


def test_selected_detector_makes_typed_recording_required_and_checks_routing():
    manifest = load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml')
    entries = applicable_topics(manifest, 'simulation')
    target = ['convergence_metric_mode:=centroid_windows_v2']
    selected = require_selected_algorithm_topics(entries, 'simulation', target)
    alias = 'centroid_convergence_diagnostics'
    assert next(entry for entry in selected if entry['alias'] == alias)['required']
    selected_entry = next(entry for entry in selected if entry['alias'] == alias)
    assert selected_entry['coverage'] == 'motion'
    assert selected_entry['algorithm_source_pose_topic'] == '/odom'
    assert selected_entry['algorithm_maximum_diagnostic_gap_sec'] == 1.0
    assert not next(entry for entry in entries if entry['alias'] == alias)['required']
    with pytest.raises(ValueError, match='matching typed recording topic'):
        require_selected_algorithm_topics(entries, 'simulation', target + [
            'convergence_diagnostics_topic:=/wrong/stream'])
    with pytest.raises(ValueError, match='requires simulation'):
        require_selected_algorithm_topics(entries, 'physical', target)


@pytest.mark.parametrize(('field', 'value', 'error'), [
    ('window_duration_sec', 1e308, 'positive nanoseconds'),
    ('maximum_source_gap_sec', 1e308, 'positive nanoseconds'),
    ('maximum_source_gap_sec', 0.0, 'positive nanoseconds'),
    ('maximum_source_gap_sec', 1e-300, 'positive nanoseconds'),
    ('maximum_source_gap_sec', float('nan'), 'finite windows'),
    ('maximum_source_gap_sec', float('inf'), 'finite windows'),
    ('sample_count', 0, 'sample count'),
    ('source_pose_topic', '', 'source pose topic'),
])
def test_rejects_unsupported_sample_and_timing_claims(field, value, error):
    message = valid_centroid_diagnostic()
    setattr(message, field, value)
    assert any(error in reason for reason in centroid_diagnostic_errors([message]))


def test_sample_count_bound_allows_interpolated_support_without_internal_samples():
    message = valid_centroid_diagnostic()
    message.maximum_source_gap_sec = 0.5
    message.sample_count = 35
    assert centroid_diagnostic_errors([message]) == []
    message.sample_count = 34
    assert any('sample count' in reason for reason in centroid_diagnostic_errors([message]))
    message.maximum_source_gap_sec = 19.0
    message.sample_count = 0
    assert centroid_diagnostic_errors([message]) == []


def test_support_must_follow_epoch_and_match_observed_supervisor_identity():
    message = valid_centroid_diagnostic()
    message.epoch_started_at.sec = 2
    assert any('precedes' in reason for reason in centroid_diagnostic_errors([message]))
    message.epoch_started_at.sec = 1
    assert centroid_diagnostic_errors([message], supervisor_run_ids={'test'}) == []
    assert any('supervisor run' in reason for reason in centroid_diagnostic_errors(
        [message], supervisor_run_ids={'another-supervisor'},
    ))
    assert centroid_diagnostic_errors(
        [message], expected_source_pose_topic='/odom', maximum_source_gap_sec=0.5,
    ) == []
    assert centroid_diagnostic_errors(
        [message], expected_source_pose_topic='/delayed_pose',
    )
    assert centroid_diagnostic_errors([message], maximum_source_gap_sec=0.05)


@pytest.mark.parametrize('wall_scale', [1, 100])
def test_diagnostic_coverage_uses_simulation_time_and_rejects_missing_middle(wall_scale):
    def bag_stamp(sim_second):
        return round((1000 + sim_second * wall_scale) * 1e9)

    def stamp(sim_second):
        nanoseconds = round(sim_second * 1e9)
        return SimpleNamespace(sec=nanoseconds // 1_000_000_000,
                               nanosec=nanoseconds % 1_000_000_000)

    times = [i * 0.5 for i in range(21)]
    clocks = [(bag_stamp(t), SimpleNamespace(clock=stamp(t))) for t in times]
    diagnostics = [(bag_stamp(t), SimpleNamespace(stamp=stamp(t))) for t in times]
    bounds = (bag_stamp(1), bag_stamp(9))
    assert centroid_stream_errors(diagnostics, clocks, *bounds, 1.0) == []
    missing_middle = [(bag, msg) for bag, msg in diagnostics
                      if not bag_stamp(3) < bag < bag_stamp(6)]
    assert any('coverage gap' in error for error in centroid_stream_errors(
        missing_middle, clocks, *bounds, 1.0,
    ))
    assert centroid_stream_errors(diagnostics[:1], clocks, *bounds, 1.0)
    assert centroid_stream_errors(diagnostics, [], *bounds, 1.0)


def test_selected_contract_binds_delayed_pose_and_preserves_inherited_manifest():
    manifest = load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml')
    entries = applicable_topics(manifest, 'simulation')
    original = deepcopy(entries)
    assert require_selected_algorithm_topics(entries, 'simulation', []) == original
    assert entries == original
    target = ['convergence_metric_mode:=centroid_windows_v2',
              'algorithm_pose_topic:=/gesc_gaussian/simulation/pose_delayed',
              'centroid_maximum_gap_sec:=0.25', 'centroid_pose_stale_sec:=0.50']
    selected = require_selected_algorithm_topics(entries, 'simulation', target)
    diagnostic = next(item for item in selected if item.get('algorithm_required'))
    assert diagnostic['algorithm_source_pose_topic'].endswith('/pose_delayed')
    assert diagnostic['algorithm_maximum_diagnostic_gap_sec'] == 0.75
    assert entries == original
    with pytest.raises(ValueError, match='pose topic'):
        require_selected_algorithm_topics(entries, 'simulation', target + [
            'algorithm_pose_topic:=/not_recorded',
        ])
    with pytest.raises(ValueError, match='positive seconds'):
        require_selected_algorithm_topics(entries, 'simulation', target + [
            'centroid_maximum_gap_sec:=1e308',
        ])


def test_run_validator_wires_selected_coverage_and_supervisor_identity(tmp_path, monkeypatch):
    manifest = load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml')
    entries = applicable_topics(manifest, 'simulation')
    aliases = {entry['alias']: entry['topic'] for entry in entries}
    metadata = {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
                'recording': {}, 'git': {}, 'run_id': 'different-recorder-id',
                'target_argv': ['convergence_metric_mode:=centroid_windows_v2']}
    documents = {'metadata.yaml': metadata,
                 'resolved_topics.yaml': {'topics': entries},
                 'resolved_parameters.yaml': {'nodes': {}, 'failures': []}}
    monkeypatch.setattr(validator, '_load_yaml', lambda path: documents[Path(path).name])
    (tmp_path / 'notes.md').write_text('Bounded synthetic validator integration.\n')
    times = [19.0 + index * 0.5 for index in range(9)]

    def bag_stamp(time):
        return round((1000 + 20 * time) * 1e9)

    def stamp(time):
        value = round(time * 1e9)
        return type(CentroidConvergenceDiagnostics().stamp)(
            sec=value // 1_000_000_000, nanosec=value % 1_000_000_000,
        )

    state = AlgorithmState()
    state.stamp = stamp(19)
    state.state = AlgorithmState.STATE_SEARCH
    state.state_valid = state.run_id_valid = True
    state.run_id = 'test'
    messages = {
        aliases['clock']: [(bag_stamp(t), SimpleNamespace(clock=stamp(t))) for t in times],
        aliases['recording_ready']: [(bag_stamp(19), SimpleNamespace(data=True)),
                                     (bag_stamp(23), SimpleNamespace(data=False))],
        aliases['algorithm_state']: [(bag_stamp(19), state)],
    }
    diagnostic_records = []
    for index, time in enumerate(times):
        message = valid_centroid_diagnostic()
        message.stamp = message.source_stamp = message.receipt_stamp = stamp(time)
        message.confirmed = index == 0
        diagnostic_records.append((bag_stamp(time), message))
    topic = aliases['centroid_convergence_diagnostics']
    messages[topic] = diagnostic_records
    monkeypatch.setattr(validator, '_read_bag', lambda *_args: (
        {entry['topic']: entry['type'] for entry in entries}, messages,
    ))

    def run():
        return validator.validate_run_directory(tmp_path, write_report=False)

    report = run()
    assert report['checks']['centroid_diagnostics_consistent']['passed']
    assert not any('centroid' in error for error in report['checks'][
        'motion_interval_coverage']['detail'])
    # Other streams are deliberately absent; this fixture claims only the
    # conditional detector checks, not complete recording acceptance.
    messages[topic] = [diagnostic_records[0], diagnostic_records[-1]]
    report = run()
    assert any('centroid' in error for error in report['checks'][
        'motion_interval_coverage']['detail'])
    messages[topic] = diagnostic_records
    state.run_id = 'unrelated-supervisor'
    assert not run()['checks']['centroid_diagnostics_consistent']['passed']
    metadata['target_argv'] = []
    messages[topic] = []
    report = run()
    assert 'centroid_diagnostics_consistent' not in report['checks']
    assert not any('centroid' in error for error in report['checks'][
        'motion_interval_coverage']['detail'])
