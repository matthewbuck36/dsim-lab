#!/usr/bin/env python3
"""Inspect an ordinary ROS bag; missing topics leave metrics unavailable."""

import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import statistics
import sys
from urllib.parse import quote


def finite(*values):
    return all(isinstance(value, (int, float)) and math.isfinite(value) for value in values)


def stamp_seconds(stamp):
    return int(stamp.sec) + int(stamp.nanosec) * 1e-9


def message_row(topic_type, message, receipt_ns):
    """Decode useful fields while preserving source and bag times separately."""
    row = {'bag_time_ns': int(receipt_ns)}
    stamp = getattr(message, 'stamp', getattr(getattr(message, 'header', None), 'stamp', None))
    if stamp is not None:
        row['source_time_s'] = stamp_seconds(stamp)
        row['source_time_basis'] = 'ros_stamp'
    elif hasattr(message, 'timestamp'):
        row['source_time_s'] = float(message.timestamp)
        row['source_time_basis'] = 'legacy_relative'
    if topic_type == 'nav_msgs/msg/Odometry':
        pose = message.pose.pose
        row.update(x=pose.position.x, y=pose.position.y, z=pose.position.z,
                   frame_id=message.header.frame_id)
    elif topic_type == 'geometry_msgs/msg/Twist':
        row.update(vx=message.linear.x, vy=message.linear.y, vz=message.linear.z,
                   wx=message.angular.x, wy=message.angular.y, wz=message.angular.z)
    elif topic_type.endswith('/StampedFloat64MultiArray'):
        row['values'] = list(message.data)
    elif topic_type.endswith('/SensorObservation'):
        # Report the producer's validity and timing basis, without inventing
        # an ADC timestamp or imposing another live acceptance contract.
        row.update(valid=message.valid, reason=message.reason,
                   receipt_time_s=stamp_seconds(message.receipt_stamp),
                   timestamp_basis=int(message.timestamp_basis),
                   source_instance=message.source_instance,
                   sequence=int(message.sequence),
                   device_sequence=int(message.device_sequence) if message.device_sequence_valid else None,
                   acquisition_uncertainty_sec=message.acquisition_uncertainty_sec,
                   raw_cost=message.raw_cost, phase_rad=message.phase_rad,
                   sensor_x_m=message.sensor_x_m, sensor_y_m=message.sensor_y_m,
                   x=message.source_pose.x, y=message.source_pose.y,
                   yaw=message.source_pose.theta, frame_id=message.frame_id,
                   pose_support_age_sec=message.pose_support_age_sec,
                   phase_support_age_sec=message.phase_support_age_sec)
    elif topic_type.endswith('/GaussianFill'):
        for name in ('fill_id', 'revision', 'center_x', 'center_y', 'amplitude',
                     'sigma_major', 'sigma_minor', 'orientation', 'active', 'superseded',
                     'principal_widths_valid', 'frame_id'):
            row[name] = getattr(message, name)
    elif topic_type.endswith('/AlgorithmEvent'):
        row.update(event_type=int(message.event_type),
                   state=message.state_name if message.state_valid else None,
                   detail=message.detail,
                   fill_id=int(message.fill_id) if message.fill_id_valid else None,
                   value_names=list(message.value_names), values=list(message.values))
    elif topic_type == 'rosgraph_msgs/msg/Clock':
        row['source_time_s'] = stamp_seconds(message.clock)
        row['source_time_basis'] = 'simulation_clock'
    return row


def read_bag(path):
    """Discover types from standard bag metadata; no project manifest is needed."""
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from rosidl_runtime_py.utilities import get_message

    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=str(path), storage_id=''),
                rosbag2_py.ConverterOptions('', ''))
    types = {item.name: item.type for item in reader.get_all_topics_and_types()}
    messages, classes, warnings = {topic: [] for topic in types}, {}, []
    supported = {'nav_msgs/msg/Odometry', 'geometry_msgs/msg/Twist',
                 'rosgraph_msgs/msg/Clock', 'ros_esc_interfaces/msg/StampedFloat64MultiArray',
                 'ros_esc_interfaces/msg/SensorObservation', 'ros_esc_interfaces/msg/GaussianFill',
                 'ros_esc_interfaces/msg/AlgorithmEvent'}
    for topic, kind in types.items():
        if kind in supported:
            try:
                classes[topic] = get_message(kind)
            except (ImportError, AttributeError, ModuleNotFoundError, ValueError) as error:
                warnings.append(f'{topic}: decoder unavailable: {error}')
    failed = Counter()
    while reader.has_next():
        topic, serialized, receipt_ns = reader.read_next()
        row = {'bag_time_ns': int(receipt_ns)}
        if topic in classes:
            try:
                row = message_row(types[topic], deserialize_message(serialized, classes[topic]), receipt_ns)
            except (ValueError, TypeError, AttributeError, RuntimeError) as error:
                failed[topic] += 1
                if failed[topic] == 1:
                    warnings.append(f'{topic}: message decoding failed: {error}')
        messages[topic].append(row)
    # Closing the C++ reader here also releases sqlite handles before plotting.
    del reader
    return types, messages, warnings


def cadence(times):
    """Describe actual observations without classifying a requested rate."""
    if len(times) < 2:
        return {'rate_hz': None, 'maximum_gap_sec': None, 'median_gap_sec': None,
                'timestamp_regressions': 0, 'duplicate_timestamps': 0}
    gaps = [right - left for left, right in zip(times, times[1:])]
    duration = times[-1] - times[0]
    regressions = sum(gap < 0 for gap in gaps)
    return {'rate_hz': (len(times) - 1) / duration if duration > 0 and not regressions else None,
            'maximum_gap_sec': max(gaps), 'median_gap_sec': statistics.median(gaps),
            'timestamp_regressions': regressions, 'duplicate_timestamps': sum(gap == 0 for gap in gaps)}


def observation_topic(types):
    """Prefer the canonical combined sensor stream without joining producers."""
    topics = [topic for topic, kind in types.items() if kind.endswith('/SensorObservation')]
    return '/gesc/observation' if '/gesc/observation' in topics else next(iter(topics), None)


def observation_arm_summary(topic, records):
    """Estimate phase speed only across adjacent, compatible fresh observations.

    The 0.5-second pair bound is an offline reporting policy, not a new runtime
    gate. Keeping invalid rows in the adjacency test prevents bridging them.
    Wrapped increments cannot reveal extra revolutions between observations.
    """
    maximum_gap = 0.5
    excluded = Counter()
    elapsed = travel = 0.0
    accepted = 0
    retained_gaps = []
    bases = set()
    for left, right in zip(records, records[1:]):
        if any(row.get('valid') is not True
               or not finite(row.get('source_time_s'), row.get('phase_rad'))
               or not isinstance(row.get('source_instance'), str)
               or not row['source_instance'].strip() for row in (left, right)):
            excluded['invalid_observation_or_phase'] += 1
            continue
        if left['source_instance'] != right['source_instance']:
            excluded['source_instance_changed'] += 1
            continue
        if (left.get('timestamp_basis') not in (0, 1, 2)
                or left.get('timestamp_basis') != right.get('timestamp_basis')):
            excluded['timestamp_basis_unavailable_or_changed'] += 1
            continue
        gap = right['source_time_s']-left['source_time_s']
        if gap <= 0:
            excluded['nonincreasing_source_time'] += 1
            continue
        if gap > maximum_gap:
            excluded['source_gap_over_policy_limit'] += 1
            continue
        travel += abs(math.remainder(right['phase_rad']-left['phase_rad'], 2*math.pi))
        elapsed += gap
        retained_gaps.append(gap)
        bases.add(str(left['timestamp_basis']))
        accepted += 1
    return {
        'mean_observed_rpm': travel/elapsed*60/(2*math.pi) if accepted else None,
        'source_topic': topic,
        'method': ('absolute wrapped phase increments over retained adjacent valid observations; '
                   'assumes actual travel is less than pi radians per pair; extra turns alias'),
        'time_basis': ('SensorObservation source stamps with producer timestamp_basis '
                       '(0=device, 1=estimated, 2=receipt); ADC timing is not inferred'),
        'retained_timestamp_bases': sorted(bases),
        'maximum_pair_gap_sec': maximum_gap,
        'pair_gap_policy': 'offline reporting bound matching 0.5-second input freshness',
        'accepted_pairs': accepted,
        'excluded_pairs': sum(excluded.values()),
        'excluded_pair_reasons': dict(excluded),
        'retained_elapsed_sec': elapsed,
        'retained_absolute_wrapped_travel_rad': travel,
        'minimum_pair_alias_limit_rpm': 30/max(retained_gaps) if retained_gaps else None,
        'alias_limit_basis': '30 / pair duration in seconds; equality or greater can alias',
    }


def cost_plot_rows(types, rows):
    """Use legacy cost unchanged, or the combined observation's valid raw cost."""
    if '/turtlebot3/cost_value_chatter' in rows:
        return rows['/turtlebot3/cost_value_chatter'], False
    topic = observation_topic(types)
    return [dict(row, values=[row['raw_cost']]) for row in rows.get(topic, [])
            if row.get('valid') is True and finite(row.get('raw_cost'))], True


def summarize(types, rows):
    """Unavailable data stays null; recorded commands are not measured stopping."""
    topics = {}
    for topic, records in rows.items():
        receipts = [row['bag_time_ns'] * 1e-9 for row in records]
        source = [row['source_time_s'] for row in records if finite(row.get('source_time_s'))]
        topics[topic] = {'type': types[topic], 'messages': len(records),
                         'receipt_timing': cadence(receipts),
                         'source_timing': cadence(source) if source else None}
        if types[topic].endswith('/SensorObservation'):
            valid = [row for row in records if row.get('valid') is True]
            topics[topic]['valid_observations'] = len(valid)
            topics[topic]['invalid_observations'] = sum(row.get('valid') is False for row in records)
            topics[topic]['valid_source_timing'] = cadence(
                [row['source_time_s'] for row in valid if finite(row.get('source_time_s'))])
            topics[topic]['timestamp_bases'] = dict(Counter(
                str(row['timestamp_basis']) for row in records if 'timestamp_basis' in row))
    odom_topic = '/odom' if '/odom' in rows else next(
        (topic for topic, kind in types.items() if kind == 'nav_msgs/msg/Odometry'), None)
    poses = [row for row in rows.get(odom_topic, []) if finite(row.get('x'), row.get('y'))]
    motion = {'pose_topic': odom_topic, 'net_displacement_m': None, 'path_length_m': None,
              'final_command_zero': None, 'final_command_topic': '/cmd_vel',
              'pose_frames': sorted({row.get('frame_id', '') for row in poses}),
              'measured_stop': 'not established by command messages'}
    if len(poses) >= 2 and len(motion['pose_frames']) == 1 and motion['pose_frames'][0]:
        distance = lambda a, b: math.hypot(b['x'] - a['x'], b['y'] - a['y'])
        motion.update(net_displacement_m=distance(poses[0], poses[-1]),
                      path_length_m=sum(distance(a, b) for a, b in zip(poses, poses[1:])))
    commands = rows.get('/cmd_vel', [])
    if commands:
        final = [commands[-1].get(key) for key in ('vx', 'vy', 'vz', 'wx', 'wy', 'wz')]
        if finite(*final):
            motion['final_command_zero'] = all(abs(value) <= 1e-9 for value in final)
    encoder = [row for row in rows.get('/turtlebot3/encoder_chatter', [])
               if len(row.get('values', [])) == 1 and finite(row.get('source_time_s'), row['values'][0])]
    rpm = None
    if len(encoder) > 1:
        times = [row['source_time_s'] for row in encoder]
        gaps = [b - a for a, b in zip(times, times[1:])]
        if all(gap > 0 for gap in gaps):
            travel = sum(abs(math.remainder(b['values'][0] - a['values'][0], 2 * math.pi))
                         for a, b in zip(encoder, encoder[1:]))
            rpm = travel / sum(gaps) * 60 / (2 * math.pi)
    arm = {'mean_observed_rpm': rpm, 'method': 'absolute wrapped angle increments; ambiguous if travel exceeds pi between samples'}
    sensor_topic = observation_topic(types)
    if '/turtlebot3/encoder_chatter' not in rows and sensor_topic is not None:
        arm = observation_arm_summary(sensor_topic, rows.get(sensor_topic, []))
    fills = {}
    events = Counter()
    for topic, kind in types.items():
        if kind.endswith('/GaussianFill'):
            for row in rows[topic]:
                if 'fill_id' in row:
                    fills[row['fill_id']] = row
        elif kind.endswith('/AlgorithmEvent'):
            events.update(str(row['event_type']) for row in rows[topic] if 'event_type' in row)
    return {'topics': topics, 'motion': motion,
            'arm': arm,
            'gaussian': {'observed_fill_ids': len(fills) if any(kind.endswith('/GaussianFill') for kind in types.values()) else None,
                         'last_fill_records': list(fills.values())},
            'events_by_type': dict(events)}


def write_plots(directory, types, rows):
    """Use the observed trajectory and fill geometry, never hidden source truth."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse

    files = []
    pose_topic = '/odom' if '/odom' in rows else next(
        (topic for topic, kind in types.items() if kind == 'nav_msgs/msg/Odometry'), None)
    poses = [row for row in rows.get(pose_topic, []) if finite(row.get('x'), row.get('y'))]
    if poses and len({row.get('frame_id', '') for row in poses}) == 1 and poses[0].get('frame_id'):
        figure, axis = plt.subplots(figsize=(7, 6))
        axis.plot([row['x'] for row in poses], [row['y'] for row in poses], label=pose_topic)
        latest = {row['fill_id']: row for topic, kind in types.items() if kind.endswith('/GaussianFill')
                  for row in rows[topic] if 'fill_id' in row}
        for fill in latest.values():
            values = [fill.get(key) for key in ('center_x', 'center_y', 'sigma_major', 'sigma_minor', 'orientation')]
            same_frame = fill.get('frame_id', '') == poses[0].get('frame_id', '')
            if (same_frame and fill.get('principal_widths_valid', True)
                    and finite(*values) and values[2] > 0 and values[3] > 0):
                axis.add_patch(Ellipse(values[:2], 2 * values[2], 2 * values[3],
                                       angle=math.degrees(values[4]), fill=False, color='tab:orange',
                                       linestyle='-' if fill['active'] else '--'))
        axis.set(xlabel='x [m]', ylabel='y [m]', title='Recorded trajectory and Gaussian widths')
        axis.axis('equal')
        axis.legend()
        axis.grid(True)
        figure.tight_layout()
        figure.savefig(directory / 'trajectory.png', dpi=150)
        plt.close(figure)
        files.append('trajectory.png')
    costs, observation_cost = cost_plot_rows(types, rows)
    commands = rows.get('/cmd_vel', [])
    if costs or commands:
        figure, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        all_times = [row['bag_time_ns'] for row in [*costs, *commands]]
        origin = min(all_times)
        for topic_rows, axis in ((costs, axes[0]), (commands, axes[1])):
            if topic_rows is costs:
                channel_count = max((len(row.get('values', [])) for row in costs), default=0)
                for channel in range(channel_count):
                    valid = [row for row in costs if len(row.get('values', [])) > channel and finite(row['values'][channel])]
                    axis.plot([(row['bag_time_ns'] - origin) * 1e-9 for row in valid],
                              [row['values'][channel] for row in valid],
                              label='Observation raw cost' if observation_cost else f'Cost {channel + 1}')
            else:
                for key in ('vx', 'wz'):
                    valid = [row for row in commands if finite(row.get(key))]
                    axis.plot([(row['bag_time_ns'] - origin) * 1e-9 for row in valid],
                              [row[key] for row in valid], label=key)
            axis.grid(True)
            if axis.lines:
                axis.legend()
        axes[0].set_ylabel('Raw cost')
        axes[1].set(ylabel='Command [m/s, rad/s]', xlabel='Bag receipt elapsed [s]')
        figure.tight_layout()
        figure.savefig(directory / 'signals.png', dpi=150)
        plt.close(figure)
        files.append('signals.png')
    return files


def json_finite(value):
    if isinstance(value, dict):
        return {str(key): json_finite(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_finite(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def analyze_bag(path, output=None, export_csv=False):
    path = Path(path).expanduser().resolve()
    output = Path(output).expanduser().resolve() if output else path.parent / (path.stem + '_analysis')
    types, rows, warnings = read_bag(path)
    report = summarize(types, rows)
    report.update(bag_path=str(path), warnings=warnings)
    output.mkdir(parents=True, exist_ok=False)
    try:
        report['plots'] = write_plots(output, types, rows)
    except ImportError as error:
        report['plots'] = []
        warnings.append(f'Plots unavailable: {error}')
    if export_csv:
        csv_directory = output / 'csv'
        csv_directory.mkdir()
        for topic, records in rows.items():
            if not records:
                continue
            columns = list(dict.fromkeys(key for row in records for key in row))
            with (csv_directory / (quote(topic, safe='') + '.csv')).open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=columns)
                writer.writeheader()
                for row in records:
                    writer.writerow({key: json.dumps(json_finite(value)) if isinstance(value, (dict, list, tuple))
                                     else json_finite(value) for key, value in row.items()})
    report = json_finite(report)
    (output / 'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return report


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bag', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--csv', action='store_true', help='Export decoded topics after recording.')
    options = parser.parse_args(args)
    try:
        report = analyze_bag(options.bag, options.output, options.csv)
    except (OSError, ValueError, RuntimeError) as error:
        print(f'analyze_bag: {error}', file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
