"""Generated sqlite3 integration tests for the Phase 07 bag analyzer."""

import csv
import hashlib
import json

from builtin_interfaces.msg import Time

from nav_msgs.msg import Odometry

from rclpy.serialization import serialize_message

from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import (
    analyze_run,
    PLOT_FILES,
    TABLE_FILES,
)

from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    ControlDiagnostics,
    CostBreakdown,
    GaussianFill,
    GescDiagnostics,
)

import rosbag2_py

from std_msgs.msg import Bool

import yaml


TOPICS = {
    'recording_ready': (
        '/gesc_gaussian/recording_ready',
        'std_msgs/msg/Bool',
        Bool,
    ),
    'source_cost': (
        '/gesc_gaussian/source_cost',
        'ros_esc_interfaces/msg/CostBreakdown',
        CostBreakdown,
    ),
    'cost_breakdown': (
        '/gesc_gaussian/cost_breakdown',
        'ros_esc_interfaces/msg/CostBreakdown',
        CostBreakdown,
    ),
    'gesc_diagnostics': (
        '/gesc_gaussian/gesc_diagnostics',
        'ros_esc_interfaces/msg/GescDiagnostics',
        GescDiagnostics,
    ),
    'control_diagnostics': (
        '/gesc_gaussian/control_diagnostics',
        'ros_esc_interfaces/msg/ControlDiagnostics',
        ControlDiagnostics,
    ),
    'pose': ('/odom', 'nav_msgs/msg/Odometry', Odometry),
    'algorithm_state': (
        '/gesc_gaussian/algorithm_state',
        'ros_esc_interfaces/msg/AlgorithmState',
        AlgorithmState,
    ),
    'algorithm_events': (
        '/gesc_gaussian/algorithm_events',
        'ros_esc_interfaces/msg/AlgorithmEvent',
        AlgorithmEvent,
    ),
    'gaussian_fills': (
        '/gesc_gaussian/gaussian_fills',
        'ros_esc_interfaces/msg/GaussianFill',
        GaussianFill,
    ),
}


def _time(timestamp_ns):
    return Time(
        sec=timestamp_ns // 1_000_000_000,
        nanosec=timestamp_ns % 1_000_000_000,
    )


def _cost(timestamp_ns, raw, gaussian=0.0):
    message = CostBreakdown()
    message.stamp = _time(timestamp_ns)
    message.source_timestamp = timestamp_ns / 1e9
    message.source_timestamp_valid = True
    message.source_mode = CostBreakdown.SOURCE_SIMULATION
    message.source_name = 'fixture'
    message.channel_count = 1
    message.raw_sensor_value = [float('nan')]
    message.filtered_sensor_value = [float('nan')]
    message.raw_cost = [raw]
    message.source_score = [max(0.0, min(1.0, 1.0 - raw))]
    message.gaussian_cost = [gaussian]
    message.affine_cost = [0.0]
    message.augmented_cost = [raw + gaussian]
    message.sensor_weight = 1.0
    message.gaussian_weight = 1.0
    message.affine_weight = 0.0
    message.raw_cost_valid = True
    message.source_score_valid = True
    message.gaussian_cost_valid = True
    message.affine_cost_valid = True
    message.augmented_cost_valid = True
    message.weights_valid = True
    return message


def _gesc(timestamp_ns):
    message = GescDiagnostics()
    message.stamp = _time(timestamp_ns)
    message.source_timestamp = timestamp_ns / 1e9
    message.source_timestamp_valid = True
    message.valid = True
    message.filter_input = [1.0]
    message.filter_output = [0.1, -0.2]
    message.filter_state_before = [0.0]
    message.filter_state_derivative = [0.1]
    message.filter_state_after = [0.1]
    return message


def _control(timestamp_ns, saturated=False):
    message = ControlDiagnostics()
    message.stamp = _time(timestamp_ns)
    message.source_timestamp = timestamp_ns / 1e9
    message.source_timestamp_valid = True
    message.controller_type = 'Directional_Controller'
    message.gesc_command_unsaturated = [0.2, 0.0, 0.0, 0.0, 0.0, 0.8]
    message.gesc_command_unsaturated_valid = True
    message.supervisor_contribution = [0.0] * 6
    message.supervisor_contribution_valid = True
    message.combined_command_unsaturated = [0.2, 0.0, 0.0, 0.0, 0.0, 0.8]
    message.combined_command_unsaturated_valid = True
    message.final_command = [0.1, 0.0, 0.0, 0.0, 0.0, 0.5]
    message.final_command_valid = True
    message.saturation_flags = [
        saturated, False, False, False, False, saturated
    ]
    message.limit_valid = [True] * 6
    message.lower_limits = [-0.1, 0.0, 0.0, 0.0, 0.0, -0.5]
    message.upper_limits = [0.1, 0.0, 0.0, 0.0, 0.0, 0.5]
    message.k_vx = 1.0
    message.k_wz = 5.0
    message.gains_valid = True
    return message


def _odom(timestamp_ns, x, y):
    message = Odometry()
    message.header.stamp = _time(timestamp_ns)
    message.header.frame_id = 'odom'
    message.child_frame_id = 'base_footprint'
    message.pose.pose.position.x = x
    message.pose.pose.position.y = y
    message.pose.pose.orientation.w = 1.0
    message.twist.twist.linear.x = 0.1
    return message


def _state(timestamp_ns, state, previous, radial=None):
    message = AlgorithmState()
    message.stamp = _time(timestamp_ns)
    message.source_timestamp = timestamp_ns / 1e9
    message.source_timestamp_valid = True
    message.run_id = 'fixture'
    message.run_id_valid = True
    message.algorithm_profile = 'robust_gaussian_v1'
    message.state = state
    message.state_name = {
        1: 'SEARCH',
        4: 'ESCAPE_REPULSE',
        5: 'ESCAPE_ASSIST',
        6: 'RECENTER',
        7: 'GOAL_HOLD',
    }[state]
    message.state_valid = True
    message.previous_state = previous
    message.previous_state_name = 'fixture_previous'
    message.previous_state_valid = True
    message.state_elapsed_sec = 0.0
    message.state_elapsed_valid = True
    message.active_fill_count = 1
    message.active_fill_count_valid = True
    message.sensor_weight = 0.0 if state in (4, 5, 6, 7) else 1.0
    message.gaussian_weight = 1.0
    message.affine_weight = 1.0 if state == 5 else 0.0
    message.weights_valid = True
    message.failsafe = False
    message.failsafe_valid = True
    if radial is not None:
        message.escape_center_x = 0.0
        message.escape_center_y = 0.0
        message.escape_exit_radius = 1.0
        message.escape_geometry_valid = True
        message.radial_distance = radial
        message.radial_distance_valid = True
        message.radial_progress = radial - 0.2
        message.radial_progress_valid = True
        message.escape_stalled = state == 5
        message.escape_stalled_valid = True
    return message


def _event(timestamp_ns, event_type):
    message = AlgorithmEvent()
    message.stamp = _time(timestamp_ns)
    message.source_timestamp = timestamp_ns / 1e9
    message.source_timestamp_valid = True
    message.event_type = event_type
    message.state = AlgorithmState.STATE_ESCAPE_REPULSE
    message.state_name = 'ESCAPE_REPULSE'
    message.state_valid = True
    message.detail = 'fixture event'
    message.value_names = ['known']
    message.values = [1.0]
    return message


def _fill(timestamp_ns, revision=1):
    message = GaussianFill()
    message.stamp = _time(timestamp_ns)
    message.source_timestamp = timestamp_ns / 1e9
    message.source_timestamp_valid = True
    message.frame_id = 'odom'
    message.fill_id = revision
    message.cluster_id = 1
    message.revision = revision
    message.center_x = 0.0
    message.center_y = 0.0
    message.amplitude = 1.0 + revision
    message.covariance_xx = 0.25
    message.covariance_xy = 0.0
    message.covariance_yy = 0.25
    message.sigma_major = 0.5
    message.sigma_minor = 0.5
    message.orientation = 0.0
    message.support_radius = 1.5
    message.exit_radius = 1.0
    message.confidence = 0.9
    message.sample_count = 50
    message.fit_residual = 0.01
    message.fit_condition_number = 2.0
    message.design_escalations = revision - 1
    message.covariance_valid = True
    message.principal_widths_valid = True
    message.support_radius_valid = True
    message.exit_radius_valid = True
    message.confidence_valid = True
    message.sample_count_valid = True
    message.fit_residual_valid = True
    message.fit_condition_number_valid = True
    message.design_escalations_valid = True
    message.active = True
    return message


def _write_document(path, document):
    path.write_text(
        yaml.safe_dump(document, sort_keys=False),
        encoding='utf-8',
    )


def _create_run(tmp_path):
    run_directory = tmp_path / 'fixture_run'
    bag_directory = run_directory / 'bag'
    run_directory.mkdir()
    writer = rosbag2_py.SequentialWriter()
    writer.open(
        rosbag2_py.StorageOptions(
            uri=str(bag_directory), storage_id='sqlite3'
        ),
        rosbag2_py.ConverterOptions('', ''),
    )
    for topic, type_name, _ in TOPICS.values():
        writer.create_topic(rosbag2_py.TopicMetadata(
            name=topic,
            type=type_name,
            serialization_format='cdr',
        ))
    records = [
        (900_000_000, 'recording_ready', Bool(data=False)),
        (1_000_000_000, 'recording_ready', Bool(data=True)),
    ]
    sample_times = [
        1_100_000_000,
        2_000_000_000,
        3_000_000_000,
        4_000_000_000,
        5_000_000_000,
        6_000_000_000,
    ]
    poses = [
        (0.0, 0.0), (0.2, 0.0), (0.8, 0.0),
        (1.2, 0.0), (0.2, 0.0), (0.3, 0.0),
    ]
    states = [
        (1, 1, None),
        (4, 1, 0.2),
        (5, 4, 0.8),
        (6, 5, 1.2),
        (1, 6, None),
        (7, 1, None),
    ]
    for index, timestamp in enumerate(sample_times):
        records.extend([
            (timestamp, 'source_cost', _cost(timestamp, 1.0 - index * 0.1)),
            (timestamp, 'cost_breakdown', _cost(
                timestamp, 1.0 - index * 0.1, 0.1
            )),
            (timestamp, 'gesc_diagnostics', _gesc(timestamp)),
            (timestamp, 'control_diagnostics', _control(
                timestamp, saturated=index == 2
            )),
            (timestamp, 'pose', _odom(timestamp, *poses[index])),
            (timestamp, 'algorithm_state', _state(
                timestamp, *states[index]
            )),
        ])
    records.extend([
        (2_000_000_000, 'gaussian_fills', _fill(2_000_000_000)),
        (2_000_000_000, 'algorithm_events', _event(
            2_000_000_000, AlgorithmEvent.EVENT_FILL_CREATED
        )),
        (2_100_000_000, 'algorithm_events', _event(
            2_100_000_000, AlgorithmEvent.EVENT_ESCAPE_STARTED
        )),
        (3_000_000_000, 'algorithm_events', _event(
            3_000_000_000, AlgorithmEvent.EVENT_ESCAPE_STALLED
        )),
        (3_100_000_000, 'gaussian_fills', _fill(3_100_000_000, 2)),
        (3_100_000_000, 'algorithm_events', _event(
            3_100_000_000, AlgorithmEvent.EVENT_FILL_MERGED
        )),
        (6_000_000_000, 'algorithm_events', _event(
            6_000_000_000, AlgorithmEvent.EVENT_GOAL_REACHED
        )),
        (7_000_000_000, 'recording_ready', Bool(data=False)),
    ])
    for timestamp, alias, message in sorted(records, key=lambda item: item[0]):
        writer.write(
            TOPICS[alias][0],
            serialize_message(message),
            timestamp,
        )
    del writer

    _write_document(
        run_directory / 'resolved_topics.yaml',
        {
            'storage_id': 'sqlite3',
            'topics': [
                {
                    'alias': alias,
                    'topic': topic,
                    'type': type_name,
                    'required': alias != 'gaussian_fills',
                }
                for alias, (topic, type_name, _) in TOPICS.items()
            ],
        },
    )
    _write_document(
        run_directory / 'resolved_parameters.yaml',
        {
            'nodes': {
                '/gaussian_fill': {'parameters': {
                    'estimation_channel_index': 0,
                    'sample_sync_tolerance_sec': 0.05,
                }},
                '/gesc_gaussian_supervisor': {'parameters': {
                    'supervisor_publish_rate_hz': 1.0,
                }},
            },
        },
    )
    _write_document(
        run_directory / 'metadata.yaml',
        {
            'run_id': 'fixture_run',
            'mode': 'simulation',
            'algorithm_profile': 'robust_gaussian_v1',
            'sources': [{'id': 'goal', 'x_m': 0.3, 'y_m': 0.0}],
            'recording': {'completeness_passed': True},
        },
    )
    (run_directory / 'completeness.json').write_text(
        json.dumps({'passed': True, 'failures': [], 'warnings': []}),
        encoding='utf-8',
    )
    return run_directory


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_generated_sqlite_bag_produces_complete_evidence(
    tmp_path, monkeypatch
):
    """A generated real sqlite3 bag must yield every standard artifact."""
    run_directory = _create_run(tmp_path)
    bag_path = next((run_directory / 'bag').glob('*.db3'))
    before_hash = _sha256(bag_path)
    before_mtime = bag_path.stat().st_mtime_ns
    monkeypatch.setattr(
        'ros_esc.plotting_scripts.gesc_gaussian_bag_analysis.'
        'validate_run_directory',
        lambda *_args, **_kwargs: {
            'passed': True, 'failures': [], 'warnings': [],
        },
    )
    output = tmp_path / 'analysis'

    result = analyze_run(run_directory, output_directory=output)

    assert result['analysis_status'] == 'complete'
    assert result['metrics']['path_length']['value'] > 0.0
    assert result['metrics']['escape_time']['value'] == 2.0
    assert result['metrics']['radial_progress']['value'] == 1.0
    assert result['metrics']['revisit_count']['value'] == 1
    assert result['metrics']['fill_count']['value'] == 1
    assert result['metrics']['merge_count']['value'] == 1
    assert result['metrics']['saturation_time']['value'] == 1.0
    assert result['metrics']['controller_success']['value'] is True
    for filename in TABLE_FILES:
        assert (output / 'tables' / filename).is_file()
    for filename in PLOT_FILES:
        assert (output / 'plots' / filename).is_file()
    assert _sha256(bag_path) == before_hash
    assert bag_path.stat().st_mtime_ns == before_mtime
    completeness = json.loads(
        (output / 'analysis_completeness.json').read_text(encoding='utf-8')
    )
    assert completeness['timestamps']['preserved_domains'] == [
        'bag_timestamp_ns',
        'ros_timestamp_ns',
        'source_timestamp_sec',
    ]
    assert completeness['alignment']['pose']['matched_fraction'] == 1.0
    with (output / 'tables/synchronized_samples.csv').open(
        'r', encoding='utf-8', newline=''
    ) as stream:
        synchronized = list(csv.DictReader(stream))
    assert synchronized[0]['bag_timestamp_ns'] == '1100000000'
    assert synchronized[0]['ros_timestamp_ns'] == '1100000000'
    assert synchronized[0]['source_timestamp_sec'] == '1.1'


def test_schema_v4_summary_exposes_applicability_and_attempt_scalars(
    tmp_path,
    monkeypatch,
):
    """Publish aggregate distance and per-attempt v4 acceptance evidence."""
    run_directory = _create_run(tmp_path)
    _write_document(
        run_directory / 'resolved_scenario.yaml',
        {
            'schema_version': 4,
            'acceptance_family': 'lifecycle',
            'acceptance_partition': 'validation',
            'repeat_reference': None,
            'metric_applicability': {
                'escape_attempt': True,
                'escape_duration': True,
                'orbit_count': True,
                'revisit': True,
                'delay': False,
                'saturation': True,
            },
            'validation': {
                'world': False,
                'contacts_enabled': False,
            },
            'disturbances': {
                'sensor_delay_sec': 0.0,
                'pose_delay_sec': 0.0,
            },
            'success': {
                'ground_truth': {
                    'method': 'aggregate_field',
                    'final_position_tolerance_m': 0.35,
                    'aggregate_field': {
                        'result_sha256': 'b' * 64,
                        'targets': [{
                            'target_id': 'aggregate_001',
                            'x_m': 0.3,
                            'y_m': 0.0,
                        }],
                    },
                },
            },
        },
    )
    monkeypatch.setattr(
        'ros_esc.plotting_scripts.gesc_gaussian_bag_analysis.'
        'validate_run_directory',
        lambda *_args, **_kwargs: {
            'passed': True, 'failures': [], 'warnings': [],
        },
    )
    output = tmp_path / 'v4_analysis'

    result = analyze_run(run_directory, output_directory=output)

    assert result['analysis_status'] == 'complete'
    assert result['acceptance_family'] == 'lifecycle'
    assert result['metric_applicability']['delay'] is False
    assert result['metrics']['observed_pose_delay']['status'] == (
        'not_applicable'
    )
    assert result['metrics'][
        'final_aggregate_target_distance'
    ]['value'] == 0.0
    assert len(result['escape_attempts']) == 1
    assert result['escape_attempts'][0]['duration']['status'] == 'valid'
    assert result['escape_attempts'][0]['orbit_count']['status'] == 'valid'
    stored = json.loads(
        (output / 'summary_metrics.json').read_text(encoding='utf-8')
    )
    assert stored['escape_attempts'] == result['escape_attempts']


def test_failed_recording_is_analyzed_as_partial(tmp_path, monkeypatch):
    """A readable failed recording must remain first-class partial evidence."""
    run_directory = _create_run(tmp_path)
    monkeypatch.setattr(
        'ros_esc.plotting_scripts.gesc_gaussian_bag_analysis.'
        'validate_run_directory',
        lambda *_args, **_kwargs: {
            'passed': False,
            'failures': ['known recording failure'],
            'warnings': [],
        },
    )
    output = tmp_path / 'failed_analysis'

    result = analyze_run(run_directory, output_directory=output)

    assert result['analysis_status'] == 'partial'
    completeness = json.loads(
        (output / 'analysis_completeness.json').read_text(encoding='utf-8')
    )
    assert completeness['recording_failures'] == [
        'known recording failure'
    ]


def test_analysis_refuses_existing_output(tmp_path):
    """One-run analysis must refuse to overwrite an existing directory."""
    run_directory = _create_run(tmp_path)
    output = tmp_path / 'analysis'
    output.mkdir()

    try:
        analyze_run(run_directory, output_directory=output)
    except FileExistsError:
        pass
    else:
        raise AssertionError('existing output directory was not rejected')


def test_missing_critical_topic_is_marked_invalid(tmp_path, monkeypatch):
    """A missing critical topic must invalidate rather than fabricate data."""
    run_directory = _create_run(tmp_path)
    resolved_path = run_directory / 'resolved_topics.yaml'
    resolved = yaml.safe_load(resolved_path.read_text(encoding='utf-8'))
    for entry in resolved['topics']:
        if entry['alias'] == 'cost_breakdown':
            entry['topic'] = '/missing/cost_breakdown'
    _write_document(resolved_path, resolved)
    monkeypatch.setattr(
        'ros_esc.plotting_scripts.gesc_gaussian_bag_analysis.'
        'validate_run_directory',
        lambda *_args, **_kwargs: {
            'passed': False,
            'failures': ['critical cost topic missing'],
            'warnings': [],
        },
    )
    output = tmp_path / 'invalid_analysis'

    result = analyze_run(run_directory, output_directory=output)

    assert result['analysis_status'] == 'invalid'
    completeness = json.loads(
        (output / 'analysis_completeness.json').read_text(encoding='utf-8')
    )
    assert completeness['critical_inputs']['cost'] is False
    assert (output / 'plots/cost.png').stat().st_size > 0
