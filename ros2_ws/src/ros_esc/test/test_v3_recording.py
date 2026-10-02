"""Optional recording lifecycle and real ordinary-bag analysis."""

import json
import math
import sys
import threading
import time
from types import SimpleNamespace

import pytest

from ros_esc.run_tools.record_bag import bag_command, run_recorder
from ros_esc.run_tools.analyze_bag import (
    analyze_bag, cadence, cost_plot_rows, json_finite, message_row, summarize,
)


def test_recording_failure_is_nonfatal_without_control_messages(capsys):
    assert run_recorder(['/does/not/exist'], threading.Event()) == 0
    assert run_recorder([sys.executable, '-c', 'raise SystemExit(23)'], threading.Event()) == 0
    assert 'control continues' in capsys.readouterr().err
    command = bag_command('/tmp/bag', 'simulation')
    assert command[:3] == ['ros2', 'bag', 'record']
    assert '/clock' in command and '--use-sim-time' not in command
    assert not any('ready' in item or 'stop_requested' in item for item in command)
    assert '/clock' not in bag_command('/tmp/bag', 'physical')


def test_shutdown_tail_reaches_child_before_graceful_close(tmp_path):
    started, closed = tmp_path / 'started', tmp_path / 'closed'
    script = (
        'import signal,time,sys\nfrom pathlib import Path\n'
        'def finish(sig, frame):\n'
        ' Path(sys.argv[2]).write_text(str(time.monotonic()))\n'
        ' raise SystemExit(0)\n'
        'signal.signal(signal.SIGINT, finish)\n'
        'Path(sys.argv[1]).write_text("ready")\n'
        'while True: time.sleep(.01)\n'
    )
    stop = threading.Event()
    runner = threading.Thread(target=run_recorder,
                              args=([sys.executable, '-c', script, str(started), str(closed)], stop, 0.15))
    runner.start()
    try:
        deadline = time.monotonic() + 3
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        assert started.exists()
        requested = time.monotonic()
        stop.set()
        runner.join(timeout=4)
        assert not runner.is_alive()
        assert float(closed.read_text()) - requested >= .14
    finally:
        stop.set()
        runner.join(timeout=12)


def test_analysis_reads_standard_bag_without_project_manifests(tmp_path):
    rosbag2_py = pytest.importorskip('rosbag2_py')
    from rclpy.serialization import serialize_message
    from nav_msgs.msg import Odometry
    from geometry_msgs.msg import Twist
    from std_msgs.msg import String

    bag = tmp_path / 'ordinary'
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=str(bag), storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('', ''))
    for name, kind in [('/odom', 'nav_msgs/msg/Odometry'), ('/cmd_vel', 'geometry_msgs/msg/Twist'),
                       ('/notes', 'std_msgs/msg/String')]:
        writer.create_topic(rosbag2_py.TopicMetadata(name=name, type=kind, serialization_format='cdr'))
    for index, x in enumerate((0., .6, 1.2), 1):
        odom = Odometry()
        odom.header.stamp.sec = index
        odom.header.frame_id = 'odom'
        odom.pose.pose.position.x = x
        odom.pose.pose.orientation.w = 1.
        command = Twist()
        command.linear.x = .05 if index < 3 else 0.
        writer.write('/odom', serialize_message(odom), index * 1_000_000_000)
        writer.write('/cmd_vel', serialize_message(command), index * 1_000_000_000 + 1)
    writer.write('/notes', serialize_message(String(data='no custom manifest')), 3_000_000_002)
    del writer
    output = tmp_path / 'analysis'
    report = analyze_bag(bag, output, export_csv=True)
    assert report['motion']['net_displacement_m'] == pytest.approx(1.2)
    assert report['motion']['path_length_m'] == pytest.approx(1.2)
    assert report['motion']['final_command_zero'] is True
    assert report['arm']['mean_observed_rpm'] is None
    assert report['gaussian']['observed_fill_ids'] is None
    assert report['topics']['/notes']['messages'] == 1
    assert report['topics']['/odom']['source_timing']['rate_hz'] == 1.
    assert (output / 'trajectory.png').stat().st_size > 1000
    assert (output / 'signals.png').stat().st_size > 1000
    assert len(list((output / 'csv').glob('*.csv'))) == 3
    assert json.loads((output / 'summary.json').read_text()) == report
    assert not (bag / 'resolved_topics.yaml').exists()


def test_missing_invalid_and_regressing_data_are_not_success():
    report = summarize({}, {})
    assert report['motion']['net_displacement_m'] is None
    assert report['motion']['final_command_zero'] is None
    assert cadence([1., 2., 1.5])['rate_hz'] is None
    assert cadence([1., 2., 1.5])['timestamp_regressions'] == 1
    report = summarize({'/cmd_vel': 'geometry_msgs/msg/Twist'},
                       {'/cmd_vel': [{'bag_time_ns': 1, 'vx': float('nan')}]})
    assert report['motion']['final_command_zero'] is None


def test_observation_timing_keeps_unknown_acquisition_uncertainty_and_invalid_samples():
    stamp = SimpleNamespace(sec=1, nanosec=0)
    message = SimpleNamespace(stamp=stamp, receipt_stamp=stamp, valid=True, reason='',
                              timestamp_basis=2, source_instance='sensor', sequence=3,
                              device_sequence_valid=False, device_sequence=0,
                              acquisition_uncertainty_sec=float('nan'), raw_cost=-2., phase_rad=.5,
                              sensor_x_m=.1, sensor_y_m=.2,
                              source_pose=SimpleNamespace(x=0., y=0., theta=0.), frame_id='odom',
                              pose_support_age_sec=.02, phase_support_age_sec=.01)
    row = message_row('ros_esc_interfaces/msg/SensorObservation', message, 1_200_000_000)
    assert row['source_time_s'] == 1.
    assert row['bag_time_ns'] == 1_200_000_000
    assert row['device_sequence'] is None
    assert json_finite(row)['acquisition_uncertainty_sec'] is None
    invalid = dict(row, valid=False, source_time_s=1.2, bag_time_ns=1_400_000_000)
    report = summarize({'/gesc/observation': 'ros_esc_interfaces/msg/SensorObservation'},
                       {'/gesc/observation': [row, invalid]})
    metrics = report['topics']['/gesc/observation']
    assert metrics['valid_observations'] == 1 and metrics['invalid_observations'] == 1
    assert metrics['valid_source_timing']['rate_hz'] is None
    assert metrics['timestamp_bases'] == {'2': 2}


def test_v3_messages_decode_from_a_standard_bag(tmp_path):
    rosbag2_py = pytest.importorskip('rosbag2_py')
    messages = pytest.importorskip('ros_esc_interfaces.msg')
    if not hasattr(messages, 'SensorObservation'):
        pytest.skip('build the eight-interface V3 package before bag interface tests')
    from rclpy.serialization import serialize_message
    bag = tmp_path / 'v3_messages'
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=str(bag), storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('', ''))
    observation = messages.SensorObservation(
        source_instance='observed', sequence=1, frame_id='odom',
        raw_cost=-2., sensor_x_m=.18, acquisition_uncertainty_sec=float('nan'),
        valid=True, timestamp_basis=messages.SensorObservation.ESTIMATED_TIME)
    observation.stamp.sec, observation.receipt_stamp.sec = 1, 2
    event = messages.AlgorithmEvent(event_type=messages.AlgorithmEvent.EVENT_FILL_REJECTED,
                                   detail='candidate rejected; control continued')
    fill = messages.GaussianFill(fill_id=3, revision=1, frame_id='odom', amplitude=2.,
                                sigma_major=.4, sigma_minor=.2,
                                principal_widths_valid=True, active=True)
    for topic, message in [('/gesc/observation', observation), ('/gesc/events', event), ('/gesc/fills', fill)]:
        kind = 'ros_esc_interfaces/msg/' + type(message).__name__
        writer.create_topic(rosbag2_py.TopicMetadata(name=topic, type=kind, serialization_format='cdr'))
        writer.write(topic, serialize_message(message), 2_100_000_000)
    del writer
    report = analyze_bag(bag, tmp_path / 'v3_analysis', export_csv=True)
    assert not report['warnings']
    assert report['topics']['/gesc/observation']['valid_observations'] == 1
    assert report['topics']['/gesc/observation']['timestamp_bases'] == {'1': 1}
    assert report['gaussian']['last_fill_records'][0]['fill_id'] == 3
    row = message_row('ros_esc_interfaces/msg/AlgorithmEvent', event, 1)
    assert row['fill_id'] is None and row['state'] is None


def test_motion_metrics_do_not_combine_different_pose_frames():
    report = summarize({'/odom': 'nav_msgs/msg/Odometry'}, {'/odom': [
        {'bag_time_ns': 1, 'x': 0., 'y': 0., 'frame_id': 'odom'},
        {'bag_time_ns': 2, 'x': 1., 'y': 0., 'frame_id': 'map'},
    ]})
    assert report['motion']['pose_frames'] == ['map', 'odom']
    assert report['motion']['net_displacement_m'] is None
    assert report['motion']['path_length_m'] is None


def observation_row(stamp, *, source='physical_sensor', valid=True, basis=2):
    return {'bag_time_ns': round((100+stamp)*1e9), 'source_time_s': stamp,
            'source_instance': source, 'valid': valid, 'timestamp_basis': basis,
            'phase_rad': (1.2+stamp*2*math.pi/3) % (2*math.pi),
            'raw_cost': -2.5, 'acquisition_uncertainty_sec': math.nan}


def test_observation_rpm_fallback_uses_measured_five_hz_phase_with_wrap():
    topic = '/gesc/observation'
    records = [observation_row(index*.2) for index in range(21)]
    arm = summarize({topic: 'ros_esc_interfaces/msg/SensorObservation'}, {topic: records})['arm']
    assert arm['mean_observed_rpm'] == pytest.approx(20.)
    assert arm['source_topic'] == topic
    assert arm['accepted_pairs'] == 20 and arm['excluded_pairs'] == 0
    assert arm['retained_elapsed_sec'] == pytest.approx(4.)
    assert arm['minimum_pair_alias_limit_rpm'] == pytest.approx(150.)
    assert arm['retained_timestamp_bases'] == ['2']
    assert 'ADC timing is not inferred' in arm['time_basis']
    assert 'extra turns alias' in arm['method']
    # No nominal20RPM constant: changing only the observed phase changes result.
    for row in records:
        row['phase_rad'] = (row['source_time_s']*2*math.pi*17.2/60) % (2*math.pi)
    assert summarize({topic: 'ros_esc_interfaces/msg/SensorObservation'},
                     {topic: records})['arm']['mean_observed_rpm'] == pytest.approx(17.2)


def test_observation_rpm_never_bridges_invalid_restart_long_gap_or_clock_change():
    topic = '/gesc/observation'
    records = [observation_row(0), observation_row(.2), observation_row(.4),
               observation_row(.6, valid=False), observation_row(.8),
               observation_row(1., source='reopened'), observation_row(1.2, source='reopened'),
               observation_row(2., source='reopened'), observation_row(2.2, source='reopened'),
               observation_row(2.2, source='reopened'), observation_row(2.1, source='reopened'),
               observation_row(2.3, source='reopened', basis=1),
               observation_row(2.5, source='reopened', basis=1)]
    arm = summarize({topic: 'ros_esc_interfaces/msg/SensorObservation'}, {topic: records})['arm']
    assert arm['mean_observed_rpm'] == pytest.approx(20.)
    assert arm['accepted_pairs'] == 5 and arm['excluded_pairs'] == 7
    assert arm['excluded_pair_reasons'] == {
        'invalid_observation_or_phase': 2, 'source_instance_changed': 1,
        'source_gap_over_policy_limit': 1, 'nonincreasing_source_time': 2,
        'timestamp_basis_unavailable_or_changed': 1,
    }
    assert arm['retained_elapsed_sec'] == pytest.approx(1.)
    assert arm['maximum_pair_gap_sec'] == .5
    assert 'offline reporting bound' in arm['pair_gap_policy']
    assert arm['retained_timestamp_bases'] == ['1', '2']


def test_observation_rpm_does_not_cross_undecodable_phase_records():
    topic = '/gesc/observation'
    records = [observation_row(0), dict(observation_row(.2), phase_rad=math.nan),
               observation_row(.4), observation_row(.6)]
    arm = summarize({topic: 'ros_esc_interfaces/msg/SensorObservation'}, {topic: records})['arm']
    assert arm['mean_observed_rpm'] == pytest.approx(20.)
    assert arm['accepted_pairs'] == 1
    assert arm['excluded_pair_reasons'] == {'invalid_observation_or_phase': 2}


def test_legacy_encoder_and_cost_keep_precedence_over_observation_fallback():
    topic = '/gesc/observation'
    types = {topic: 'ros_esc_interfaces/msg/SensorObservation',
             '/turtlebot3/encoder_chatter': 'ros_esc_interfaces/msg/StampedFloat64MultiArray'}
    rows = {topic: [observation_row(0), observation_row(.2)],
            '/turtlebot3/encoder_chatter': [
                {'bag_time_ns': 1, 'source_time_s': 0., 'values': [0.]},
                {'bag_time_ns': 2, 'source_time_s': .2, 'values': [math.pi/10]}]}
    assert summarize(types, rows)['arm'] == {
        'mean_observed_rpm': pytest.approx(15.),
        'method': 'absolute wrapped angle increments; ambiguous if travel exceeds pi between samples',
    }
    legacy_cost = [{'bag_time_ns': 1, 'values': [-4.]}]
    types['/turtlebot3/cost_value_chatter'] = 'ros_esc_interfaces/msg/StampedFloat64MultiArray'
    rows['/turtlebot3/cost_value_chatter'] = legacy_cost
    selected, fallback = cost_plot_rows(types, rows)
    assert selected is legacy_cost and fallback is False
    # Existing but empty legacy topics retain their historical unavailable state.
    rows['/turtlebot3/encoder_chatter'] = []
    rows['/turtlebot3/cost_value_chatter'] = []
    assert summarize(types, rows)['arm']['mean_observed_rpm'] is None
    assert cost_plot_rows(types, rows) == ([], False)


def test_cost_plot_fallback_uses_only_valid_observed_negative_voltage():
    topic = '/gesc/observation'
    records = [observation_row(0), dict(observation_row(.2), raw_cost=-3.1),
               dict(observation_row(.4, valid=False), raw_cost=-9.),
               dict(observation_row(.6), raw_cost=math.nan)]
    costs, fallback = cost_plot_rows({topic: 'ros_esc_interfaces/msg/SensorObservation'},
                                    {topic: records})
    assert fallback is True
    assert [row['values'] for row in costs] == [[-2.5], [-3.1]]
    assert [row['bag_time_ns'] for row in costs] == [records[0]['bag_time_ns'], records[1]['bag_time_ns']]
    assert all('values' not in row for row in records)  # Analysis never mutates decoded evidence.


def test_closed_physical_observation_only_bag_produces_rpm_and_voltage_plot(tmp_path, monkeypatch):
    rosbag2_py = pytest.importorskip('rosbag2_py')
    messages = pytest.importorskip('ros_esc_interfaces.msg')
    from rclpy.serialization import serialize_message
    from matplotlib.axes import Axes
    topic = '/gesc/observation'
    bag = tmp_path / 'physical_observation_only'
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=str(bag), storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('', ''))
    writer.create_topic(rosbag2_py.TopicMetadata(
        name=topic, type='ros_esc_interfaces/msg/SensorObservation', serialization_format='cdr'))
    expected_costs = []
    for index in range(21):
        stamp_ns = 10_000_000_000+index*200_000_000
        cost = -2.5-.1*math.cos(index*.2)
        expected_costs.append(cost)
        observation = messages.SensorObservation(
            source_instance='physical', sequence=index+1, frame_id='odom',
            raw_cost=cost, phase_rad=(1.2+index*.2*2*math.pi/3) % (2*math.pi),
            acquisition_uncertainty_sec=math.nan, valid=True,
            timestamp_basis=messages.SensorObservation.RECEIPT_TIME)
        observation.stamp.sec, observation.stamp.nanosec = divmod(stamp_ns, 1_000_000_000)
        observation.receipt_stamp = observation.stamp
        writer.write(topic, serialize_message(observation), stamp_ns+50_000_000)
    del writer  # Analyzer opens only the closed ordinary bag.
    plotted = []
    original_plot = Axes.plot

    def capture_plot(self, *args, **kwargs):
        if kwargs.get('label') == 'Observation raw cost':
            plotted.append(list(args[1]))
        return original_plot(self, *args, **kwargs)

    monkeypatch.setattr(Axes, 'plot', capture_plot)
    output = tmp_path / 'physical_analysis'
    report = analyze_bag(bag, output)
    assert not report['warnings']
    assert report['arm']['mean_observed_rpm'] == pytest.approx(20.)
    assert report['arm']['accepted_pairs'] == 20
    assert report['arm']['excluded_pairs'] == 0
    assert report['plots'] == ['signals.png']
    assert (output / 'signals.png').stat().st_size > 1000
    assert plotted == [expected_costs]
    assert json.loads((output / 'summary.json').read_text()) == report


def test_recorder_started_before_best_effort_clock_records_late_publisher(tmp_path):
    """Exercise real CLI discovery; a command-list assertion misses QoS races."""
    import os
    import subprocess
    import rclpy
    import rosbag2_py
    from rclpy.context import Context
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from rosgraph_msgs.msg import Clock
    from ros_esc.run_tools.record_bag import stop_bag

    bag = tmp_path / 'late_clock'
    log = tmp_path / 'late_clock.log'
    environment = dict(os.environ, ROS_DOMAIN_ID='195', ROS_LOCALHOST_ONLY='1')
    context = Context()
    node = None
    with log.open('w') as stream:
        process = subprocess.Popen(bag_command(bag, topics=['/clock']), env=environment,
                                   stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            deadline = time.monotonic() + 8
            while 'Listening for topics' not in log.read_text() and time.monotonic() < deadline:
                assert process.poll() is None, log.read_text()
                time.sleep(.05)
            assert 'Listening for topics' in log.read_text(), log.read_text()
            rclpy.init(context=context, domain_id=195)
            node = Node('late_clock_test', context=context)
            publisher = node.create_publisher(Clock, '/clock', qos_profile_sensor_data)
            deadline = time.monotonic() + 5
            sequence = 0
            while time.monotonic() < deadline:
                message = Clock()
                sequence += 1
                message.clock.sec = sequence
                publisher.publish(message)
                time.sleep(.05)
        finally:
            stop_bag(process, tail_sec=0)
            if node is not None:
                node.destroy_node()
            context.try_shutdown()
    assert process.returncode == 0, log.read_text()
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=str(bag), storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('', ''))
    recorded = []
    while reader.has_next():
        recorded.append(reader.read_next()[0])
    assert recorded.count('/clock') >= 10, log.read_text()
