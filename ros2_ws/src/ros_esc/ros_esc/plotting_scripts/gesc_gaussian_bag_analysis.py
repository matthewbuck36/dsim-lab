#!/usr/bin/env python3

"""Produce standard Phase 07 evidence from one recorded run or a matrix."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import sys
import tempfile

import matplotlib.pyplot as plt

import numpy as np

from ros_esc.experiment_recording.validate_run import (
    validate_run_directory,
)

from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState

import yaml

from .bag_reader import (
    build_timestamp_index,
    causal_indexed_record,
    load_yaml,
    NANOSECONDS_PER_SECOND,
    nearest_indexed_record,
    read_run_bag,
    records_for_alias,
    stamp_nanoseconds,
)
from .plotting_helper_functions import init_plot_style


plt.switch_backend('Agg')


AXES = ('vx', 'vy', 'vz', 'wx', 'wy', 'wz')
TABLE_FILES = (
    'synchronized_samples.csv',
    'source_cost.csv',
    'cost_breakdown.csv',
    'gesc_diagnostics.csv',
    'control_diagnostics.csv',
    'odometry.csv',
    'algorithm_state.csv',
    'state_intervals.csv',
    'algorithm_events.csv',
    'candidate_ranking.csv',
    'gaussian_history.csv',
    'escape_attempts.csv',
)
PLOT_FILES = (
    'cost.png',
    'components.png',
    'state_events.png',
    'weights.png',
    'trajectory_sources_fills.png',
    'command_saturation.png',
    'radial_escape.png',
    'gaussian_history.png',
    'candidate_ranking.png',
)


def metric(value, status='valid', unit=None, reason=None, provenance=None):
    """Build one validity-marked metric."""
    return {
        'value': value,
        'status': status,
        'unit': unit,
        'reason': reason,
        'provenance': provenance,
    }


def unavailable(reason, unit=None, provenance=None, status='unavailable'):
    """Build an unavailable, invalid, or not-applicable metric."""
    return metric(
        None,
        status=status,
        unit=unit,
        reason=reason,
        provenance=provenance,
    )


def _finite(value):
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _json_cell(value):
    return json.dumps(value, sort_keys=True, allow_nan=False)


def _timestamp_columns(record):
    return {
        'bag_timestamp_ns': record.bag_timestamp_ns,
        'ros_timestamp_ns': record.ros_timestamp_ns,
        'source_timestamp_sec': record.source_timestamp_sec,
        'source_timestamp_valid': record.source_timestamp_valid,
        'in_readiness_interval': record.in_readiness_interval,
        't_motion_sec': record.t_motion_sec,
    }


def _array(value):
    return [float(item) for item in value]


def _value_at(values, index):
    if index < len(values):
        value = float(values[index])
        return value if math.isfinite(value) else None
    return None


def _cost_rows(records):
    rows = []
    for record in records:
        message = record.message
        channel_count = max(
            int(message.channel_count),
            len(message.raw_cost),
            len(message.augmented_cost),
        )
        for index in range(channel_count):
            row = _timestamp_columns(record)
            row.update({
                'channel_index': index,
                'source_mode': int(message.source_mode),
                'source_name': message.source_name,
                'raw_sensor_value': _value_at(
                    message.raw_sensor_value, index
                ),
                'filtered_sensor_value': _value_at(
                    message.filtered_sensor_value, index
                ),
                'raw_cost': _value_at(message.raw_cost, index),
                'source_score': _value_at(message.source_score, index),
                'gaussian_cost': _value_at(message.gaussian_cost, index),
                'affine_cost': _value_at(message.affine_cost, index),
                'augmented_cost': _value_at(message.augmented_cost, index),
                'sensor_weight': float(message.sensor_weight),
                'gaussian_weight': float(message.gaussian_weight),
                'affine_weight': float(message.affine_weight),
                'raw_sensor_valid': bool(message.raw_sensor_valid),
                'filtered_sensor_valid': bool(message.filtered_sensor_valid),
                'raw_cost_valid': bool(message.raw_cost_valid),
                'source_score_valid': bool(message.source_score_valid),
                'gaussian_cost_valid': bool(message.gaussian_cost_valid),
                'affine_cost_valid': bool(message.affine_cost_valid),
                'augmented_cost_valid': bool(message.augmented_cost_valid),
                'weights_valid': bool(message.weights_valid),
            })
            rows.append(row)
    return rows


def _gesc_rows(records):
    rows = []
    for record in records:
        message = record.message
        row = _timestamp_columns(record)
        row.update({
            'valid': bool(message.valid),
            'filter_input': _json_cell(_array(message.filter_input)),
            'filter_output': _json_cell(_array(message.filter_output)),
            'filter_state_before': _json_cell(
                _array(message.filter_state_before)
            ),
            'filter_state_derivative': _json_cell(
                _array(message.filter_state_derivative)
            ),
            'filter_state_after': _json_cell(
                _array(message.filter_state_after)
            ),
            'dither_phase_rad': float(message.dither_phase_rad),
            'dither_phase_valid': bool(message.dither_phase_valid),
            'dither_amplitude_m': float(message.dither_amplitude_m),
            'dither_amplitude_valid': bool(
                message.dither_amplitude_valid
            ),
            'dither_angular_frequency_rad_sec': float(
                message.dither_angular_frequency_rad_sec
            ),
            'dither_angular_frequency_valid': bool(
                message.dither_angular_frequency_valid
            ),
        })
        rows.append(row)
    return rows


def _control_rows(records):
    rows = []
    for record in records:
        message = record.message
        row = _timestamp_columns(record)
        row['controller_type'] = message.controller_type
        groups = (
            ('gesc_unsaturated', message.gesc_command_unsaturated),
            ('supervisor', message.supervisor_contribution),
            ('combined_unsaturated', message.combined_command_unsaturated),
            ('final', message.final_command),
            ('lower_limit', message.lower_limits),
            ('upper_limit', message.upper_limits),
        )
        for prefix, values in groups:
            for axis, value in zip(AXES, values):
                row[f'{prefix}_{axis}'] = float(value)
        for axis, value in zip(AXES, message.saturation_flags):
            row[f'saturated_{axis}'] = bool(value)
        for axis, value in zip(AXES, message.limit_valid):
            row[f'limit_valid_{axis}'] = bool(value)
        row.update({
            'gesc_command_unsaturated_valid': bool(
                message.gesc_command_unsaturated_valid
            ),
            'supervisor_contribution_valid': bool(
                message.supervisor_contribution_valid
            ),
            'combined_command_unsaturated_valid': bool(
                message.combined_command_unsaturated_valid
            ),
            'final_command_valid': bool(message.final_command_valid),
            'k_vx': float(message.k_vx),
            'k_wz': float(message.k_wz),
            'gains_valid': bool(message.gains_valid),
        })
        rows.append(row)
    return rows


def _yaw_from_quaternion(quaternion):
    sin_yaw = 2.0 * (
        quaternion.w * quaternion.z
        + quaternion.x * quaternion.y
    )
    cos_yaw = 1.0 - 2.0 * (
        quaternion.y * quaternion.y
        + quaternion.z * quaternion.z
    )
    return math.atan2(sin_yaw, cos_yaw)


def _odometry_rows(records):
    rows = []
    for record in records:
        message = record.message
        row = _timestamp_columns(record)
        pose = message.pose.pose
        twist = message.twist.twist
        row.update({
            'frame_id': message.header.frame_id,
            'child_frame_id': message.child_frame_id,
            'x_m': float(pose.position.x),
            'y_m': float(pose.position.y),
            'z_m': float(pose.position.z),
            'yaw_rad': _yaw_from_quaternion(pose.orientation),
            'measured_vx_mps': float(twist.linear.x),
            'measured_vy_mps': float(twist.linear.y),
            'measured_wz_rps': float(twist.angular.z),
        })
        rows.append(row)
    return rows


def _state_rows(records):
    fields = (
        'run_id', 'run_id_valid', 'algorithm_profile', 'state', 'state_name',
        'state_valid', 'previous_state', 'previous_state_name',
        'previous_state_valid', 'transition_reason',
        'transition_reason_valid', 'state_elapsed_sec',
        'state_elapsed_valid', 'active_fill_count',
        'active_fill_count_valid', 'active_escape_fill_id',
        'active_escape_fill_id_valid', 'escape_center_x', 'escape_center_y',
        'escape_exit_radius', 'escape_geometry_valid', 'radial_distance',
        'radial_distance_valid', 'radial_progress',
        'radial_progress_valid', 'escape_exit_hold_elapsed_sec',
        'escape_exit_hold_elapsed_valid', 'escape_stalled',
        'escape_stalled_valid', 'safe_direction_x', 'safe_direction_y',
        'safe_direction_clearance_m', 'safe_direction_valid',
        'safe_direction_revision', 'safe_direction_revision_valid',
        'recenter_target_x', 'recenter_target_y', 'recenter_target_valid',
        'recenter_distance', 'recenter_distance_valid', 'sensor_weight',
        'gaussian_weight', 'affine_weight', 'weights_valid', 'failsafe',
        'failsafe_valid',
    )
    rows = []
    for record in records:
        row = _timestamp_columns(record)
        row.update({
            field: getattr(record.message, field)
            for field in fields
        })
        rows.append(row)
    return rows


def _event_rows(records):
    rows = []
    for record in records:
        message = record.message
        row = _timestamp_columns(record)
        row.update({
            'event_type': int(message.event_type),
            'state': int(message.state),
            'state_name': message.state_name,
            'state_valid': bool(message.state_valid),
            'fill_id': int(message.fill_id),
            'fill_id_valid': bool(message.fill_id_valid),
            'reason_code': int(message.reason_code),
            'detail': message.detail,
            'value_names': _json_cell(list(message.value_names)),
            'values': _json_cell(_array(message.values)),
        })
        rows.append(row)
    return rows


def _candidate_rows(records):
    """Extract one preferred rotation-stable raw-cost row per observation."""
    required = {
        'candidate_raw_cost_estimate',
        'candidate_raw_cost_mad',
        'candidate_raw_cost_uncertainty',
        'candidate_raw_cost_lower',
        'candidate_raw_cost_upper',
        'candidate_rotation_count',
        'candidate_ordinal',
        'filled_candidate_count',
        'known_source_count',
    }
    event_names = _event_names()
    preferred = {}
    for record in records:
        if not record.in_readiness_interval:
            continue
        message = record.message
        names = list(message.value_names)
        values = list(message.values)
        if len(names) != len(values):
            continue
        evidence = dict(zip(names, values))
        if not required <= set(evidence):
            continue
        try:
            numeric = {
                name: float(evidence[name])
                for name in required
            }
        except (TypeError, ValueError):
            continue
        if not all(_finite(value) for value in numeric.values()):
            continue
        ordinal = int(numeric['candidate_ordinal'])
        row = _timestamp_columns(record)
        row.update({
            'event_type': int(message.event_type),
            'event_name': event_names.get(
                int(message.event_type),
                str(message.event_type),
            ),
            'state': int(message.state),
            'state_name': message.state_name,
            'detail': message.detail,
            **numeric,
            'comparison_filled_raw_cost_lower': (
                float(evidence['comparison_filled_raw_cost_lower'])
                if _finite(evidence.get(
                    'comparison_filled_raw_cost_lower'
                ))
                else None
            ),
            'candidate_strict_separation_margin': (
                float(evidence['candidate_strict_separation_margin'])
                if _finite(evidence.get(
                    'candidate_strict_separation_margin'
                ))
                else None
            ),
            'candidate_interval_valid': bool(
                numeric['candidate_raw_cost_lower']
                <= numeric['candidate_raw_cost_estimate']
                <= numeric['candidate_raw_cost_upper']
                and numeric['candidate_rotation_count'] > 0.0
                and ordinal >= 1
            ),
        })
        identity = (
            ordinal,
            numeric['candidate_raw_cost_estimate'],
            numeric['candidate_raw_cost_lower'],
            numeric['candidate_raw_cost_upper'],
            int(numeric['filled_candidate_count']),
        )
        priority = (
            2
            if message.event_type == AlgorithmEvent.EVENT_GOAL_REACHED
            else 1
        )
        current = preferred.get(identity)
        if current is None or priority > current[0]:
            preferred[identity] = (priority, row)
    return sorted(
        (item[1] for item in preferred.values()),
        key=lambda row: (
            row['bag_timestamp_ns'],
            row['candidate_ordinal'],
        ),
    )


def _fill_rows(records):
    fields = (
        'frame_id', 'fill_id', 'cluster_id', 'revision', 'center_x',
        'center_y', 'amplitude', 'covariance_xx', 'covariance_xy',
        'covariance_yy', 'sigma_major', 'sigma_minor', 'orientation',
        'support_radius', 'exit_radius', 'confidence', 'sample_count',
        'fit_residual', 'fit_condition_number', 'design_escalations',
        'covariance_valid', 'principal_widths_valid',
        'support_radius_valid', 'exit_radius_valid', 'confidence_valid',
        'sample_count_valid', 'fit_residual_valid',
        'fit_condition_number_valid', 'design_escalations_valid', 'active',
        'superseded',
    )
    rows = []
    for record in records:
        row = _timestamp_columns(record)
        row.update({
            field: getattr(record.message, field)
            for field in fields
        })
        rows.append(row)
    return rows


def _record_time(record):
    return (
        record.ros_timestamp_ns
        if record.ros_timestamp_ns is not None
        else record.bag_timestamp_ns
    )


def _sync_match(row, prefix, record, skew, formatter):
    if record is None:
        row[f'{prefix}_valid'] = False
        row[f'{prefix}_match_timestamp_ns'] = None
        row[f'{prefix}_skew_ns'] = None
        row[f'{prefix}_missing_reason'] = 'no match within tolerance'
        return
    row[f'{prefix}_valid'] = True
    row[f'{prefix}_match_timestamp_ns'] = _record_time(record)
    row[f'{prefix}_skew_ns'] = skew
    row[f'{prefix}_missing_reason'] = None
    row.update(formatter(record.message))


def _synchronized_rows(bag_data, channel_index, tolerance_sec):
    tolerance_ns = int(tolerance_sec * NANOSECONDS_PER_SECOND)
    anchors = records_for_alias(
        bag_data, 'cost_breakdown', readiness_only=True
    )
    sources = records_for_alias(bag_data, 'source_cost', readiness_only=True)
    gesc = records_for_alias(
        bag_data, 'gesc_diagnostics', readiness_only=True
    )
    control = records_for_alias(
        bag_data, 'control_diagnostics', readiness_only=True
    )
    odometry = records_for_alias(bag_data, 'pose', readiness_only=True)
    states = records_for_alias(
        bag_data, 'algorithm_state', readiness_only=True
    )
    source_index = build_timestamp_index(sources, 'ros_timestamp_ns')
    gesc_index = build_timestamp_index(gesc, 'ros_timestamp_ns')
    control_index = build_timestamp_index(control, 'ros_timestamp_ns')
    odometry_index = build_timestamp_index(odometry, 'ros_timestamp_ns')
    state_index = build_timestamp_index(states, 'ros_timestamp_ns')
    rows = []
    for anchor in anchors:
        timestamp = _record_time(anchor)
        row = _timestamp_columns(anchor)
        row['channel_index'] = channel_index
        message = anchor.message
        for name in (
            'raw_cost', 'source_score', 'gaussian_cost', 'affine_cost',
            'augmented_cost',
        ):
            row[name] = _value_at(getattr(message, name), channel_index)
        row.update({
            'sensor_weight': float(message.sensor_weight),
            'gaussian_weight': float(message.gaussian_weight),
            'affine_weight': float(message.affine_weight),
            'cost_anchor_valid': (
                bool(message.raw_cost_valid)
                and bool(message.augmented_cost_valid)
                and row['raw_cost'] is not None
                and row['augmented_cost'] is not None
            ),
        })
        source, skew = nearest_indexed_record(
            source_index, timestamp, tolerance_ns
        )
        _sync_match(
            row, 'source', source, skew,
            lambda item: {
                'source_raw_cost': _value_at(
                    item.raw_cost, channel_index
                ),
                'source_score_synced': _value_at(
                    item.source_score, channel_index
                ),
            },
        )
        gesc_record, skew = nearest_indexed_record(
            gesc_index, timestamp, tolerance_ns
        )
        _sync_match(
            row, 'gesc', gesc_record, skew,
            lambda item: {
                'gesc_output_x': _value_at(item.filter_output, 0),
                'gesc_output_y': _value_at(item.filter_output, 1),
            },
        )
        pose_record, skew = nearest_indexed_record(
            odometry_index, timestamp, tolerance_ns
        )
        _sync_match(
            row, 'pose', pose_record, skew,
            lambda item: {
                'pose_x_m': float(item.pose.pose.position.x),
                'pose_y_m': float(item.pose.pose.position.y),
                'pose_yaw_rad': _yaw_from_quaternion(
                    item.pose.pose.orientation
                ),
                'measured_vx_mps': float(item.twist.twist.linear.x),
                'measured_wz_rps': float(item.twist.twist.angular.z),
            },
        )
        control_record, skew = nearest_indexed_record(
            control_index, timestamp, tolerance_ns
        )

        def control_values(item):
            values = {}
            for prefix, data in (
                ('gesc_unsaturated', item.gesc_command_unsaturated),
                ('supervisor', item.supervisor_contribution),
                ('combined_unsaturated', item.combined_command_unsaturated),
                ('final', item.final_command),
            ):
                for axis, value in zip(AXES, data):
                    values[f'{prefix}_{axis}'] = float(value)
            for axis, value in zip(AXES, item.saturation_flags):
                values[f'saturated_{axis}'] = bool(value)
            return values

        _sync_match(
            row, 'control', control_record, skew, control_values
        )
        state_record, skew = causal_indexed_record(
            state_index, timestamp, tolerance_ns
        )
        _sync_match(
            row, 'state', state_record, skew,
            lambda item: {
                'state': int(item.state),
                'state_name': item.state_name,
                'radial_distance': float(item.radial_distance),
                'radial_distance_valid': bool(
                    item.radial_distance_valid
                ),
                'radial_progress': float(item.radial_progress),
                'radial_progress_valid': bool(item.radial_progress_valid),
                'escape_stalled': bool(item.escape_stalled),
                'escape_stalled_valid': bool(item.escape_stalled_valid),
                'recenter_distance': float(item.recenter_distance),
                'recenter_distance_valid': bool(
                    item.recenter_distance_valid
                ),
            },
        )
        rows.append(row)
    return rows


def _write_csv(path, rows):
    rows = list(rows)
    fields = []
    seen = set()
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fields.append(field)
    if not fields:
        fields = ['status']
        rows = [{'status': 'no records'}]
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _find_parameter(document, name):
    values = []

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == name:
                    values.append(item)
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(document)
    unique = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique[0] if len(unique) == 1 else None


def _resolved_setting(run_directory, cli_value, name, fallback):
    if cli_value is not None:
        return cli_value, 'cli'
    try:
        parameters = load_yaml(
            Path(run_directory) / 'resolved_parameters.yaml'
        )
        value = _find_parameter(parameters, name)
        if value is not None:
            return value, 'resolved_parameters.yaml'
    except (OSError, yaml.YAMLError):
        pass
    return fallback, 'assumed fallback'


def _path_length(records):
    points = []
    for record in records:
        position = record.message.pose.pose.position
        if _finite(position.x) and _finite(position.y):
            points.append((float(position.x), float(position.y)))
    if len(points) < 2:
        return unavailable(
            'fewer than two finite in-readiness odometry samples',
            unit='m',
            provenance='/odom',
        )
    value = sum(
        math.hypot(current[0] - previous[0], current[1] - previous[1])
        for previous, current in zip(points, points[1:])
    )
    return metric(value, unit='m', provenance='/odom consecutive samples')


def _simulation_supervisor_rate(run_directory, metadata):
    """Resolve the captured publisher parameters without parameter-type metadata."""
    if metadata.get('mode') != 'simulation':
        raise ValueError('simulation publication durations require simulation metadata')
    topics = load_yaml(Path(run_directory) / 'resolved_topics.yaml')
    selected = [item for item in topics.get('topics', [])
                if item.get('alias') == 'algorithm_state']
    if (len(selected) != 1
            or selected[0].get('type') != 'ros_esc_interfaces/msg/AlgorithmState'
            or not isinstance(selected[0].get('publishers'), list)
            or len(selected[0]['publishers']) != 1):
        raise ValueError('simulation publication durations require one captured state publisher')
    publisher = selected[0]['publishers'][0]
    if not isinstance(publisher, str) or not publisher:
        raise ValueError('captured state publisher is invalid')
    document = load_yaml(Path(run_directory) / 'resolved_parameters.yaml')
    node = document.get('nodes', {}).get(publisher, {})
    if node.get('available') is not True or not isinstance(node.get('parameters'), dict):
        raise ValueError('captured state publisher parameters are unavailable')
    parameters = node['parameters']
    if _find_parameter(parameters, 'use_sim_time') is not True:
        raise ValueError('state publisher must use the simulation clock')
    rate = _find_parameter(parameters, 'supervisor_publish_rate_hz')
    if type(rate) not in (int, float) or not math.isfinite(rate) or rate <= 0:
        raise ValueError('captured state publisher rate must be finite and positive')
    return float(rate), 'resolved_parameters.yaml:' + publisher + ':parameters'


def _simulation_publication_state_intervals(records, readiness_start, readiness_end, rate_hz):
    """Measure only consecutive publication support selected by bag readiness."""
    provenance = '/gesc_gaussian/algorithm_state.stamp; simulation_publication_v1'
    support = dict(state_duration_basis='simulation_publication_v1',
                   readiness_start_bag_timestamp_ns=readiness_start,
                   readiness_end_bag_timestamp_ns=readiness_end,
                   support_start_ros_timestamp_ns=None, support_end_ros_timestamp_ns=None,
                   boundary_extrapolation_used=False,
                   support_scope='first-to-last readiness-selected publication; readiness boundary slivers unmeasured')

    def rejected(reason, intervals=None):
        value = unavailable(reason, unit='s by state', provenance=provenance, status='invalid')
        value.update(support)
        return intervals or [], value

    if (type(readiness_start) is not int or type(readiness_end) is not int
            or not 0 <= readiness_start < readiness_end):
        return rejected('simulation publication durations require complete bag readiness bounds')
    if type(rate_hz) not in (int, float) or not math.isfinite(rate_hz) or rate_hz <= 0:
        return rejected('simulation publication duration rate must be finite and positive')
    selected = [record for record in records
                if readiness_start <= record.bag_timestamp_ns <= readiness_end]
    if len(selected) < 2:
        return rejected('fewer than two readiness-selected state publications')
    state_names = {getattr(AlgorithmState, 'STATE_' + name): name for name in (
        'SEARCH', 'VERIFY_EXTREMUM', 'DESIGN_OR_MERGE_FILL', 'ESCAPE_REPULSE',
        'ESCAPE_ASSIST', 'RECENTER', 'GOAL_HOLD', 'FAILSAFE')}
    for record in selected:
        message = record.message
        stamp = getattr(message, 'stamp', None)
        if (not bool(getattr(message, 'state_valid', False))
                or type(getattr(message, 'state', None)) is not int
                or state_names.get(message.state) != getattr(message, 'state_name', None)
                or type(record.ros_timestamp_ns) is not int or record.ros_timestamp_ns < 0
                or stamp is None or type(stamp.sec) is not int or type(stamp.nanosec) is not int
                or stamp.sec < 0 or not 0 <= stamp.nanosec < NANOSECONDS_PER_SECOND
                or stamp_nanoseconds(stamp) != record.ros_timestamp_ns):
            return rejected('invalid state or simulation publication stamp')
    support.update(support_start_ros_timestamp_ns=selected[0].ros_timestamp_ns,
                   support_end_ros_timestamp_ns=selected[-1].ros_timestamp_ns)
    intervals, durations, excessive = [], defaultdict(float), 0
    gap_limit = 3.0 / rate_hz
    for first, second in zip(selected, selected[1:]):
        duration = (second.ros_timestamp_ns - first.ros_timestamp_ns) / NANOSECONDS_PER_SECOND
        if second.bag_timestamp_ns < first.bag_timestamp_ns or duration < 0:
            return rejected('state publication ordering moved backward', intervals)
        identity = (first.message.state, first.message.state_name)
        if duration == 0 and identity != (second.message.state, second.message.state_name):
            return rejected('conflicting states at one simulation publication stamp', intervals)
        excessive += duration > gap_limit
        name = first.message.state_name or str(int(first.message.state))
        durations[name] += duration
        intervals.append(dict(state=int(first.message.state), state_name=name,
            start_bag_timestamp_ns=first.bag_timestamp_ns,
            end_bag_timestamp_ns=second.bag_timestamp_ns,
            start_ros_timestamp_ns=first.ros_timestamp_ns,
            end_ros_timestamp_ns=second.ros_timestamp_ns,
            duration_sec=duration, gap_valid=duration <= gap_limit,
            state_duration_basis='simulation_publication_v1'))
    if excessive:
        return rejected(f'{excessive} state publication gaps exceed three periods ({gap_limit:.6f} s)', intervals)
    if selected[-1].ros_timestamp_ns == selected[0].ros_timestamp_ns:
        return rejected('state publications have no positive simulation-time support', intervals)
    value = metric(dict(sorted(durations.items())), unit='s by state', provenance=provenance)
    value.update(support)
    return intervals, value


def _state_intervals(records, readiness_start, readiness_end, rate_hz, *,
                     state_duration_basis='bag_receipt_v1'):
    if state_duration_basis == 'simulation_publication_v1':
        return _simulation_publication_state_intervals(records, readiness_start, readiness_end, rate_hz)
    if state_duration_basis != 'bag_receipt_v1':
        raise ValueError('unknown state duration basis')
    valid = [
        record for record in records
        if bool(record.message.state_valid)
    ]
    if not valid or readiness_start is None:
        return [], unavailable(
            'no valid state samples in a readiness interval',
            unit='s',
            provenance='/gesc_gaussian/algorithm_state',
        )
    end_bound = (
        readiness_end
        if readiness_end is not None
        else valid[-1].bag_timestamp_ns
    )
    intervals = []
    durations = defaultdict(float)
    gap_limit = 3.0 / rate_hz if rate_hz and rate_hz > 0.0 else None
    invalid_gaps = []
    for index, record in enumerate(valid):
        start = max(record.bag_timestamp_ns, readiness_start)
        end = (
            min(valid[index + 1].bag_timestamp_ns, end_bound)
            if index + 1 < len(valid)
            else end_bound
        )
        if end < start:
            continue
        duration = (end - start) / NANOSECONDS_PER_SECOND
        if gap_limit is not None and duration > gap_limit:
            invalid_gaps.append(duration)
        name = record.message.state_name or str(int(record.message.state))
        durations[name] += duration
        intervals.append({
            'state': int(record.message.state),
            'state_name': name,
            'start_bag_timestamp_ns': start,
            'end_bag_timestamp_ns': end,
            'duration_sec': duration,
            'gap_valid': gap_limit is None or duration <= gap_limit,
        })
    if invalid_gaps:
        status = unavailable(
            (
                f'{len(invalid_gaps)} state gaps exceed three periods '
                f'({gap_limit:.6f} s)'
            ),
            unit='s by state',
            provenance='/gesc_gaussian/algorithm_state',
            status='invalid',
        )
    else:
        status = metric(
            dict(sorted(durations.items())),
            unit='s by state',
            provenance='readiness-clipped algorithm state samples',
        )
    return intervals, status


def _collapsed_states(records):
    sequence = []
    for record in records:
        message = record.message
        if not message.state_valid:
            continue
        item = {
            'state': int(message.state),
            'state_name': message.state_name,
            'bag_timestamp_ns': record.bag_timestamp_ns,
        }
        if not sequence or item['state'] != sequence[-1]['state']:
            sequence.append(item)
    return sequence


def _escape_attempts(
    state_records,
    event_records,
    odometry_records,
    end_ns,
    schema_version=1,
):
    sequence = _collapsed_states(state_records)
    escape_states = {
        AlgorithmState.STATE_ESCAPE_REPULSE,
        AlgorithmState.STATE_ESCAPE_ASSIST,
    }
    active_attempt_states = set(escape_states)
    if schema_version >= 4:
        active_attempt_states.add(
            AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
        )
    attempts = []
    index = 0
    while index < len(sequence):
        item = sequence[index]
        if item['state'] not in escape_states:
            index += 1
            continue
        start = item['bag_timestamp_ns']
        cursor = index + 1
        while (
            cursor < len(sequence)
            and sequence[cursor]['state'] in active_attempt_states
        ):
            cursor += 1
        next_item = sequence[cursor] if cursor < len(sequence) else None
        stop = next_item['bag_timestamp_ns'] if next_item else end_ns
        terminal = next_item['state'] if next_item else None
        success = terminal in {
            AlgorithmState.STATE_RECENTER,
            AlgorithmState.STATE_SEARCH,
        }
        failure = (
            terminal == AlgorithmState.STATE_FAILSAFE
            or next_item is None
        )
        events = [
            record.message
            for record in event_records
            if (
                record.bag_timestamp_ns >= start
                and (stop is None or record.bag_timestamp_ns <= stop)
            )
        ]
        escape_states_in_attempt = [
            record for record in state_records
            if (
                record.bag_timestamp_ns >= start
                and (stop is None or record.bag_timestamp_ns <= stop)
                and record.message.state in escape_states
            )
        ]
        geometry = next(
            (
                record.message for record in escape_states_in_attempt
                if record.message.escape_geometry_valid
            ),
            None,
        )
        radial_progress = [
            float(record.message.radial_progress)
            for record in escape_states_in_attempt
            if (
                record.message.radial_progress_valid
                and _finite(record.message.radial_progress)
            )
        ]
        exit_hold = [
            float(record.message.escape_exit_hold_elapsed_sec)
            for record in escape_states_in_attempt
            if (
                record.message.escape_exit_hold_elapsed_valid
                and _finite(record.message.escape_exit_hold_elapsed_sec)
            )
        ]
        orbit_count = None
        if geometry is not None:
            angles = []
            for record in odometry_records:
                if record.bag_timestamp_ns < start:
                    continue
                if stop is not None and record.bag_timestamp_ns > stop:
                    continue
                position = record.message.pose.pose.position
                angles.append(math.atan2(
                    float(position.y) - float(geometry.escape_center_y),
                    float(position.x) - float(geometry.escape_center_x),
                ))
            if len(angles) >= 2:
                unwrapped = np.unwrap(np.asarray(angles))
                orbit_count = float(
                    np.abs(np.diff(unwrapped)).sum() / (2.0 * math.pi)
                )
        attempts.append({
            'attempt_index': len(attempts) + 1,
            'start_bag_timestamp_ns': start,
            'end_bag_timestamp_ns': stop,
            'duration_sec': (
                (stop - start) / NANOSECONDS_PER_SECOND
                if stop is not None else None
            ),
            'outcome': (
                'success' if success else 'failure' if failure else 'unknown'
            ),
            'stalled': any(
                item.event_type == AlgorithmEvent.EVENT_ESCAPE_STALLED
                for item in events
            ),
            'assisted': any(
                entry['state'] == AlgorithmState.STATE_ESCAPE_ASSIST
                for entry in sequence[index:cursor]
            ),
            'timeout': any(
                item.event_type == AlgorithmEvent.EVENT_TIMEOUT
                for item in events
            ),
            'failsafe': terminal == AlgorithmState.STATE_FAILSAFE,
            'maximum_radial_progress_m': (
                max(radial_progress) if radial_progress else None
            ),
            'maximum_exit_hold_sec': max(exit_hold) if exit_hold else None,
            'approximate_orbit_count': orbit_count,
        })
        index = cursor
    return attempts


def _saturation_metrics(records):
    if not records:
        return (
            unavailable(
                'no in-readiness control diagnostics',
                unit='s',
                provenance='/gesc_gaussian/control_diagnostics',
            ),
            unavailable(
                'no in-readiness control diagnostics',
                unit='fraction',
                provenance='/gesc_gaussian/control_diagnostics',
            ),
            {},
            unavailable(
                'no in-readiness control diagnostics',
                unit='command units',
                provenance='/gesc_gaussian/control_diagnostics',
            ),
        )
    count = 0
    duration = 0.0
    axis_counts = Counter()
    maximum_excess = 0.0
    for index, record in enumerate(records):
        message = record.message
        saturated = any(message.saturation_flags)
        count += int(saturated)
        if saturated and index + 1 < len(records):
            duration += (
                records[index + 1].bag_timestamp_ns
                - record.bag_timestamp_ns
            ) / NANOSECONDS_PER_SECOND
        for axis, flag in zip(AXES, message.saturation_flags):
            axis_counts[axis] += int(flag)
        for value, lower, upper, valid in zip(
            message.combined_command_unsaturated,
            message.lower_limits,
            message.upper_limits,
            message.limit_valid,
        ):
            if valid and all(_finite(item) for item in (value, lower, upper)):
                excess = max(float(lower) - float(value), 0.0)
                excess = max(excess, float(value) - float(upper))
                maximum_excess = max(maximum_excess, excess)
    return (
        metric(
            duration,
            unit='s',
            provenance='control sample intervals with saturation flags',
        ),
        metric(
            count / len(records),
            unit='fraction',
            provenance='/gesc_gaussian/control_diagnostics',
        ),
        dict(axis_counts),
        metric(
            maximum_excess,
            unit='command units',
            provenance='combined unsaturated command versus limits',
        ),
    )


def _active_fills(fill_records):
    latest = {}
    for record in fill_records:
        message = record.message
        key = int(message.cluster_id)
        candidate = (
            int(message.revision),
            int(message.fill_id),
            record.bag_timestamp_ns,
        )
        current = latest.get(key)
        if current is None or candidate > current[0]:
            latest[key] = (candidate, record)
    return [
        item[1]
        for item in latest.values()
        if item[1].message.active and not item[1].message.superseded
    ]


def _legacy_revisit_count(odometry, fills, attempts):
    successful = [
        attempt for attempt in attempts
        if attempt['outcome'] == 'success'
    ]
    if not successful:
        return unavailable(
            'no successful escape occurred',
            unit='crossings',
            provenance='state and typed fill lifecycle',
            status='not_applicable',
        )
    active = _active_fills(fills)
    if not active:
        return unavailable(
            'successful escape has no valid active typed fill',
            unit='crossings',
            provenance='/gesc_gaussian/gaussian_fills',
            status='invalid',
        )
    after = successful[-1]['end_bag_timestamp_ns']
    count = 0
    for fill_record in active:
        message = fill_record.message
        if not message.covariance_valid or not message.exit_radius_valid:
            return unavailable(
                'active fill lacks covariance or exit-radius validity',
                unit='crossings',
                provenance='/gesc_gaussian/gaussian_fills',
                status='invalid',
            )
        covariance = np.array([
            [message.covariance_xx, message.covariance_xy],
            [message.covariance_xy, message.covariance_yy],
        ])
        try:
            inverse = np.linalg.inv(covariance)
        except np.linalg.LinAlgError:
            return unavailable(
                'active fill covariance is singular',
                unit='crossings',
                provenance='/gesc_gaussian/gaussian_fills',
                status='invalid',
            )
        scale = (
            float(message.exit_radius) / float(message.sigma_major)
            if message.sigma_major > 0.0 else None
        )
        if scale is None:
            return unavailable(
                'active fill sigma_major is not positive',
                unit='crossings',
                provenance='/gesc_gaussian/gaussian_fills',
                status='invalid',
            )
        previous_inside = None
        for record in odometry:
            if after is not None and record.bag_timestamp_ns < after:
                continue
            position = record.message.pose.pose.position
            delta = np.array([
                float(position.x) - float(message.center_x),
                float(position.y) - float(message.center_y),
            ])
            inside = float(delta.T @ inverse @ delta) <= scale * scale
            if previous_inside is False and inside:
                count += 1
            previous_inside = inside
    return metric(
        count,
        unit='outside-to-inside crossings',
        provenance='odometry against current active fill exit ellipses',
    )


def _v4_revisit_count(odometry, fills, attempts):
    successful = [
        attempt for attempt in attempts
        if attempt['outcome'] == 'success'
    ]
    if not successful:
        return unavailable(
            'no successful escape occurred',
            unit='crossings',
            provenance='state and typed fill lifecycle',
            status='not_applicable',
        )
    after = successful[0]['end_bag_timestamp_ns']
    ordered_fills = sorted(
        fills, key=lambda record: record.bag_timestamp_ns
    )
    ordered_odometry = sorted(
        odometry, key=lambda record: record.bag_timestamp_ns
    )
    active_by_cluster = {}
    geometry_cache = {}
    previous_inside = {}
    fill_index = 0
    count = 0
    active_observed = False
    for record in ordered_odometry:
        if after is not None and record.bag_timestamp_ns < after:
            continue
        while (
            fill_index < len(ordered_fills)
            and ordered_fills[fill_index].bag_timestamp_ns
            <= record.bag_timestamp_ns
        ):
            message = ordered_fills[fill_index].message
            identity = (
                int(message.cluster_id),
                int(message.revision),
                int(message.fill_id),
            )
            current = active_by_cluster.get(identity[0])
            if message.active and not message.superseded:
                active_by_cluster[identity[0]] = (
                    identity,
                    message,
                )
            elif current is not None and current[0] == identity:
                active_by_cluster.pop(identity[0], None)
            fill_index += 1
        crossed_at_sample = False
        for identity, message in active_by_cluster.values():
            active_observed = True
            geometry = geometry_cache.get(identity)
            if geometry is None:
                if (
                    not message.covariance_valid
                    or not message.exit_radius_valid
                ):
                    return unavailable(
                        'active fill lacks covariance or exit-radius validity',
                        unit='crossings',
                        provenance='/gesc_gaussian/gaussian_fills',
                        status='invalid',
                    )
                covariance = np.array([
                    [message.covariance_xx, message.covariance_xy],
                    [message.covariance_xy, message.covariance_yy],
                ])
                try:
                    inverse = np.linalg.inv(covariance)
                except np.linalg.LinAlgError:
                    return unavailable(
                        'active fill covariance is singular',
                        unit='crossings',
                        provenance='/gesc_gaussian/gaussian_fills',
                        status='invalid',
                    )
                if message.sigma_major <= 0.0:
                    return unavailable(
                        'active fill sigma_major is not positive',
                        unit='crossings',
                        provenance='/gesc_gaussian/gaussian_fills',
                        status='invalid',
                    )
                geometry = (
                    inverse,
                    float(message.exit_radius)
                    / float(message.sigma_major),
                )
                geometry_cache[identity] = geometry
            inverse, scale = geometry
            position = record.message.pose.pose.position
            delta = np.array([
                float(position.x) - float(message.center_x),
                float(position.y) - float(message.center_y),
            ])
            inside = float(delta.T @ inverse @ delta) <= scale * scale
            if previous_inside.get(identity) is False and inside:
                crossed_at_sample = True
            previous_inside[identity] = inside
        if crossed_at_sample:
            count += 1
    if not active_observed:
        return unavailable(
            'successful escape has no valid active typed fill',
            unit='crossings',
            provenance='/gesc_gaussian/gaussian_fills',
            status='invalid',
        )
    return metric(
        count,
        unit='outside-to-inside crossings',
        provenance='odometry against timestamped active fill exit ellipses',
    )


def _revisit_count(odometry, fills, attempts, schema_version=1):
    if schema_version >= 4:
        return _v4_revisit_count(odometry, fills, attempts)
    return _legacy_revisit_count(odometry, fills, attempts)


def _event_names():
    return {
        int(value): name
        for name, value in vars(AlgorithmEvent).items()
        if name.startswith('EVENT_') and isinstance(value, int)
    }


def _candidate_ranking_metric(scenario, candidate_rows):
    """Report strict counted-source raw-cost ranking without ground truth."""
    overrides = scenario.get('algorithm', {}).get('launch_overrides', {})
    if overrides.get('extremum_classification_mode') != 'counted_candidates':
        return unavailable(
            'counted-candidate classification was not selected',
            unit='boolean',
            provenance='/gesc_gaussian/algorithm_events',
            status='not_applicable',
        )
    known_count = int(overrides.get('known_source_count', 0))
    goal_rows = [
        row for row in candidate_rows
        if row['event_type'] == AlgorithmEvent.EVENT_GOAL_REACHED
    ]
    passed = any(
        row['candidate_interval_valid']
        and row['candidate_ordinal'] == float(known_count)
        and row['filled_candidate_count'] == float(known_count - 1)
        and row['known_source_count'] == float(known_count)
        and _finite(row['comparison_filled_raw_cost_lower'])
        and _finite(row['candidate_strict_separation_margin'])
        and row['candidate_raw_cost_upper']
        < row['comparison_filled_raw_cost_lower']
        and row['candidate_strict_separation_margin'] > 0.0
        for row in goal_rows
    )
    return metric(
        passed,
        unit='boolean',
        reason=(
            None
            if passed
            else 'no strict counted-candidate GOAL_REACHED interval ranking'
        ),
        provenance=(
            'rotation-stable raw-cost intervals in '
            '/gesc_gaussian/algorithm_events'
        ),
    )


def _source_points(run_directory):
    for filename in ('resolved_scenario.yaml', 'metadata.yaml'):
        path = Path(run_directory) / filename
        if not path.is_file():
            continue
        document = load_yaml(path)
        sources = (
            document.get('sources', [])
            if isinstance(document, dict) else []
        )
        if sources:
            return sources
    return []


def _ground_truth_metric(run_directory, odometry):
    scenario_path = Path(run_directory) / 'resolved_scenario.yaml'
    if not scenario_path.is_file():
        return unavailable(
            'resolved_scenario.yaml does not authorize ground truth',
            provenance='Phase 06 resolved scenario',
            status='not_applicable',
        )
    scenario = load_yaml(scenario_path)
    ground_truth = scenario.get('success', {}).get('ground_truth', {})
    if scenario.get('schema_version', 1) < 4:
        goal_ids = ground_truth.get('goal_source_ids', [])
        tolerance = ground_truth.get('final_position_tolerance_m')
        if not goal_ids or not _finite(tolerance) or not odometry:
            return unavailable(
                (
                    'ground-truth goal IDs, tolerance, or final pose '
                    'are unavailable'
                ),
                provenance='resolved_scenario.yaml and /odom',
                status='unavailable',
            )
        source_by_id = {
            str(source.get('id')): source
            for source in scenario.get('sources', [])
        }
        final = odometry[-1].message.pose.pose.position
        distances = {}
        for goal_id in goal_ids:
            source = source_by_id.get(str(goal_id))
            if source is None:
                continue
            distances[str(goal_id)] = math.hypot(
                float(final.x) - float(source['x_m']),
                float(final.y) - float(source['y_m']),
            )
        if not distances:
            return unavailable(
                'resolved goal source IDs do not map to source geometry',
                provenance='resolved_scenario.yaml',
                status='invalid',
            )
        nearest = min(distances.values())
        return metric(
            nearest <= float(tolerance),
            unit='boolean',
            reason=f'nearest goal distance={nearest:.6f} m',
            provenance=(
                'final odometry and Phase 06 ground-truth contract'
            ),
        )

    tolerance = ground_truth.get('final_position_tolerance_m')
    if not _finite(tolerance) or not odometry:
        return unavailable(
            'ground-truth tolerance or final pose is unavailable',
            provenance='resolved_scenario.yaml and /odom',
            status='unavailable',
        )
    targets = ground_truth.get('aggregate_field', {}).get('targets', [])
    target_by_id = {
        str(target.get('target_id')): target
        for target in targets
        if isinstance(target, dict)
    }
    final = odometry[-1].message.pose.pose.position
    distances = {}
    for target_id, target in target_by_id.items():
        values = (
            final.x,
            final.y,
            target.get('x_m'),
            target.get('y_m'),
        )
        if not all(_finite(value) for value in values):
            continue
        distances[target_id] = math.hypot(
            float(final.x) - float(target['x_m']),
            float(final.y) - float(target['y_m']),
        )
    if not distances:
        return unavailable(
            'aggregate-field targets are missing from resolved_scenario.yaml',
            provenance='resolved_scenario.yaml',
            status='invalid',
        )
    nearest = min(distances.values())
    return metric(
        nearest <= float(tolerance),
        unit='boolean',
        reason=f'nearest aggregate/goal distance={nearest:.6f} m',
        provenance='final odometry and schema-v4 aggregate-field contract',
    )


def _aggregate_target_distance_metric(run_directory, odometry):
    """Return numeric terminal aggregate distance for schema-v4 gates."""
    scenario = _resolved_scenario(run_directory)
    if scenario.get('schema_version', 1) < 4:
        return None
    targets = scenario.get('success', {}).get(
        'ground_truth', {}
    ).get('aggregate_field', {}).get('targets', [])
    if not odometry or not targets:
        return unavailable(
            'final pose or aggregate targets are unavailable',
            unit='m',
            provenance='resolved_scenario.yaml and /odom',
        )
    final = odometry[-1].message.pose.pose.position
    distances = [
        math.hypot(
            float(final.x) - float(target['x_m']),
            float(final.y) - float(target['y_m']),
        )
        for target in targets
        if all(
            _finite(value)
            for value in (
                final.x,
                final.y,
                target.get('x_m'),
                target.get('y_m'),
            )
        )
    ]
    if not distances:
        return unavailable(
            'aggregate distance inputs are nonfinite',
            unit='m',
            provenance='resolved_scenario.yaml and /odom',
            status='invalid',
        )
    return metric(
        min(distances),
        unit='m',
        provenance='final odometry to nearest aggregate-field target',
    )


def _resolved_scenario(run_directory):
    path = Path(run_directory) / 'resolved_scenario.yaml'
    if not path.is_file():
        return {}
    document = load_yaml(path)
    return document if isinstance(document, dict) else {}


def _contact_metric(bag_data):
    scenario = _resolved_scenario(bag_data.run_directory)
    enabled = bool(
        scenario.get('validation', {}).get('contacts_enabled', False)
    )
    records = records_for_alias(
        bag_data, 'simulation_contacts', readiness_only=True
    )
    if not enabled:
        return unavailable(
            'simulation contacts were not enabled for this scenario',
            unit='boolean',
            provenance='resolved scenario validation controls',
        )
    if not records:
        return unavailable(
            'enabled simulation contact topic has no readiness records',
            unit='boolean',
            provenance='/gesc_gaussian/simulation/contacts',
            status='invalid',
        )
    contacts = [
        {
            'collision1': state.collision1_name,
            'collision2': state.collision2_name,
        }
        for record in records
        for state in record.message.states
        if (
            'ground_plane' not in state.collision1_name
            and 'ground_plane' not in state.collision2_name
        )
    ]
    return metric(
        bool(contacts),
        unit='boolean',
        reason=(
            f'{len(contacts)} non-ground contact state records'
            if contacts else 'valid empty non-ground contact evidence'
        ),
        provenance='/gesc_gaussian/simulation/contacts',
    )


def _delay_key(record):
    if record.ros_timestamp_ns is not None:
        return ('ros', int(record.ros_timestamp_ns))
    if record.source_timestamp_valid:
        return ('source', round(float(record.source_timestamp_sec), 9))
    return None


def _observed_delay_metric(
    bag_data,
    original_alias,
    delayed_alias,
    configured_delay_sec,
):
    original = records_for_alias(
        bag_data, original_alias, readiness_only=True
    )
    delayed = records_for_alias(
        bag_data, delayed_alias, readiness_only=True
    )
    if configured_delay_sec <= 0.0:
        return unavailable(
            'delay was not enabled for this scenario',
            unit='s',
            provenance='resolved scenario disturbances',
        )
    clock = records_for_alias(bag_data, 'clock', readiness_only=False)
    if not clock:
        return unavailable(
            'simulation clock is unavailable for delay measurement',
            unit='s',
            provenance='/clock and paired retained message stamps',
            status='invalid',
        )

    clock_index = build_timestamp_index(clock, 'bag_timestamp_ns')

    def simulation_stamp(record):
        clock_record, _ = nearest_indexed_record(
            clock_index,
            record.bag_timestamp_ns,
            int(0.05 * NANOSECONDS_PER_SECOND),
        )
        if clock_record is None:
            return None
        return stamp_nanoseconds(clock_record.message.clock)

    by_key = defaultdict(list)
    for record in original:
        key = _delay_key(record)
        stamp = simulation_stamp(record)
        if key is not None and stamp is not None:
            by_key[key].append(stamp)
    offsets = []
    used = defaultdict(int)
    for record in delayed:
        key = _delay_key(record)
        candidates = by_key.get(key, [])
        index = used[key]
        delayed_stamp = simulation_stamp(record)
        if index >= len(candidates) or delayed_stamp is None:
            continue
        used[key] += 1
        offsets.append(
            (delayed_stamp - candidates[index])
            / NANOSECONDS_PER_SECOND
        )
    if not offsets:
        return unavailable(
            'original and delayed stamps could not be paired',
            unit='s',
            provenance=f'{original_alias} and {delayed_alias}',
            status='invalid',
        )
    observed = statistics.median(offsets)
    return metric(
        observed,
        unit='s',
        reason=(
            f'configured={configured_delay_sec:.6f} s; '
            f'pairs={len(offsets)}'
        ),
        provenance=(
            f'/clock-mapped bag receipt for paired retained stamps from '
            f'{original_alias} and {delayed_alias}'
        ),
    )


def _compute_metrics(
    bag_data,
    metadata,
    state_records,
    event_records,
    fill_records,
    odometry,
    control,
    state_intervals_metric,
    attempts,
    schema_version=1,
):
    names = _event_names()
    event_counts = Counter(
        names.get(
            int(record.message.event_type),
            str(record.message.event_type),
        )
        for record in event_records
    )
    sequence = _collapsed_states(state_records)
    duration = None
    if (
        bag_data.readiness_start_ns is not None
        and bag_data.readiness_end_ns is not None
    ):
        duration = (
            bag_data.readiness_end_ns - bag_data.readiness_start_ns
        ) / NANOSECONDS_PER_SECOND
    path_length = _path_length(odometry)
    saturation_time, saturation_fraction, axis_counts, maximum_excess = (
        _saturation_metrics(control)
    )
    radial_values = [
        float(record.message.radial_progress)
        for record in state_records
        if (
            record.message.radial_progress_valid
            and _finite(record.message.radial_progress)
        )
    ]
    fill_clusters = {
        int(record.message.cluster_id)
        for record in fill_records
        if record.message.active and not record.message.superseded
    }
    created_clusters = {
        int(record.message.cluster_id)
        for record in fill_records
        if int(record.message.revision) == 1
    }
    merge_count = event_counts.get('EVENT_FILL_MERGED', 0)
    profile = metadata.get('algorithm_profile')
    goal_event = event_counts.get('EVENT_GOAL_REACHED', 0) > 0
    goal_hold = any(
        entry['state'] == AlgorithmState.STATE_GOAL_HOLD
        for entry in sequence
    )
    if profile == 'legacy':
        controller_success = unavailable(
            'legacy profile has no canonical robust goal state',
            unit='boolean',
            provenance='metadata profile',
            status='not_applicable',
        )
    else:
        controller_success = metric(
            goal_event and goal_hold,
            unit='boolean',
            reason=(
                None if goal_event and goal_hold
                else 'requires EVENT_GOAL_REACHED and GOAL_HOLD'
            ),
            provenance='algorithm event and state topics',
        )
    durations = [
        attempt['duration_sec']
        for attempt in attempts
        if _finite(attempt['duration_sec'])
    ]
    orbit_counts = [
        float(attempt['approximate_orbit_count'])
        for attempt in attempts
        if _finite(attempt['approximate_orbit_count'])
    ]
    escape_time = (
        metric(
            sum(durations),
            unit='s',
            provenance='state-derived escape attempts',
        )
        if durations else unavailable(
            'no escape attempt occurred',
            unit='s',
            provenance='algorithm state',
            status='not_applicable',
        )
    )
    convergence_records = [
        record for record in event_records
        if record.message.event_type == AlgorithmEvent.EVENT_GOAL_REACHED
    ]
    convergence_time = (
        metric(
            (
                convergence_records[0].bag_timestamp_ns
                - bag_data.readiness_start_ns
            ) / NANOSECONDS_PER_SECOND,
            unit='s',
            provenance='first goal event from readiness start',
        )
        if convergence_records and bag_data.readiness_start_ns is not None
        else unavailable(
            'no goal event occurred',
            unit='s',
            provenance='algorithm events',
            status='not_applicable',
        )
    )
    scenario = _resolved_scenario(bag_data.run_directory)
    disturbances = scenario.get('disturbances', {})
    sensor_delay = float(disturbances.get('sensor_delay_sec', 0.0))
    pose_delay = float(disturbances.get('pose_delay_sec', 0.0))
    return {
        'recording_complete': metric(
            bool(metadata.get('recording', {}).get('completeness_passed')),
            unit='boolean',
            provenance='metadata recording result',
        ),
        'readiness_duration': (
            metric(
                duration,
                unit='s',
                provenance='/gesc_gaussian/recording_ready bag timestamps',
            )
            if duration is not None else unavailable(
                'readiness true-to-false interval is incomplete',
                unit='s',
                provenance='/gesc_gaussian/recording_ready',
                status='invalid',
            )
        ),
        'path_length': path_length,
        'convergence_time': convergence_time,
        'escape_time': escape_time,
        'escape_attempt_count': metric(
            len(attempts),
            unit='attempts',
            provenance='collapsed algorithm state sequence',
        ),
        'escape_success_count': metric(
            sum(item['outcome'] == 'success' for item in attempts),
            unit='attempts',
            provenance='escape-state exit transitions',
        ),
        'escape_failure_count': metric(
            sum(item['outcome'] == 'failure' for item in attempts),
            unit='attempts',
            provenance='failsafe or readiness-censored attempts',
        ),
        'approximate_orbit_count': (
            metric(
                orbit_counts,
                unit='orbits by escape attempt',
                provenance=(
                    'absolute unwrapped odometry angle about frozen center'
                ),
            )
            if orbit_counts else unavailable(
                'no escape attempt has sufficient pose and frozen geometry',
                unit='orbits',
                provenance='odometry and AlgorithmState escape geometry',
                status=(
                    'not_applicable' if not attempts else 'invalid'
                ),
            )
        ),
        'radial_progress': (
            metric(
                max(radial_values),
                unit='m',
                provenance='published AlgorithmState.radial_progress',
            )
            if radial_values else unavailable(
                'no valid published radial progress',
                unit='m',
                provenance='/gesc_gaussian/algorithm_state',
                status=(
                    'not_applicable' if not attempts else 'invalid'
                ),
            )
        ),
        'revisit_count': _revisit_count(
            odometry,
            fill_records,
            attempts,
            schema_version=schema_version,
        ),
        'fill_count': metric(
            len(created_clusters),
            unit='created clusters',
            provenance='typed fill revision-one lifecycle',
        ),
        'active_fill_count': metric(
            len(fill_clusters),
            unit='active clusters',
            provenance='latest typed fill revisions',
        ),
        'merge_count': metric(
            merge_count,
            unit='events',
            provenance='EVENT_FILL_MERGED',
        ),
        'fill_design_escalation_count': metric(
            event_counts.get('EVENT_FILL_DESIGN_ESCALATED', 0),
            unit='events',
            provenance='algorithm events',
        ),
        'state_durations': state_intervals_metric,
        'state_transition_count': metric(
            max(0, len(sequence) - 1),
            unit='transitions',
            provenance='collapsed valid algorithm state sequence',
        ),
        'terminal_state': (
            metric(
                sequence[-1]['state_name'],
                unit=None,
                provenance='last valid state in readiness interval',
            )
            if sequence else unavailable(
                'no valid algorithm state',
                provenance='algorithm state',
            )
        ),
        'saturation_time': saturation_time,
        'saturation_fraction': saturation_fraction,
        'saturation_axis_counts': metric(
            axis_counts,
            unit='samples by axis',
            provenance='control saturation flags',
        ),
        'maximum_limit_excess': maximum_excess,
        'controller_success': controller_success,
        'simulation_ground_truth_success': _ground_truth_metric(
            bag_data.run_directory, odometry
        ),
        'timeout': metric(
            event_counts.get('EVENT_TIMEOUT', 0) > 0,
            unit='boolean',
            provenance='in-readiness algorithm events',
        ),
        'failsafe': metric(
            (
                event_counts.get('EVENT_FAILSAFE', 0) > 0
                or any(
                    entry['state'] == AlgorithmState.STATE_FAILSAFE
                    for entry in sequence
                )
            ),
            unit='boolean',
            provenance='in-readiness state and event evidence',
        ),
        'collision': _contact_metric(bag_data),
        'observed_raw_cost_delay': _observed_delay_metric(
            bag_data,
            'raw_cost_legacy',
            'simulation_raw_cost_delayed',
            sensor_delay,
        ),
        'observed_source_cost_delay': _observed_delay_metric(
            bag_data,
            'source_cost',
            'simulation_source_cost_delayed',
            sensor_delay,
        ),
        'observed_pose_delay': _observed_delay_metric(
            bag_data,
            'pose',
            'simulation_pose_delayed',
            pose_delay,
        ),
        'event_counts': metric(
            dict(sorted(event_counts.items())),
            unit='events by type',
            provenance='/gesc_gaussian/algorithm_events',
        ),
    }


def _v4_attempt_metrics(attempts, applicability):
    """Expose one explicit duration and orbit status per observed attempt."""
    rows = []
    for attempt in attempts:
        if applicability['escape_duration']:
            duration = (
                metric(
                    float(attempt['duration_sec']),
                    unit='s',
                    provenance='state-derived escape attempt',
                )
                if _finite(attempt['duration_sec'])
                else unavailable(
                    'applicable escape attempt has no finite duration',
                    unit='s',
                    provenance='state-derived escape attempt',
                )
            )
        else:
            duration = unavailable(
                'escape duration declared not applicable before execution',
                unit='s',
                provenance='schema-v4 metric applicability',
                status='not_applicable',
            )
        if applicability['orbit_count']:
            orbit = (
                metric(
                    float(attempt['approximate_orbit_count']),
                    unit='orbits',
                    provenance='odometry around frozen escape center',
                )
                if _finite(attempt['approximate_orbit_count'])
                else unavailable(
                    'applicable escape attempt has no finite orbit value',
                    unit='orbits',
                    provenance='odometry and frozen escape geometry',
                )
            )
        else:
            orbit = unavailable(
                'orbit count declared not applicable before execution',
                unit='orbits',
                provenance='schema-v4 metric applicability',
                status='not_applicable',
            )
        rows.append({
            'attempt_index': attempt['attempt_index'],
            'outcome': attempt['outcome'],
            'stalled': attempt['stalled'],
            'assisted': attempt['assisted'],
            'timeout': attempt['timeout'],
            'failsafe': attempt['failsafe'],
            'duration': duration,
            'orbit_count': orbit,
        })
    return rows


def _apply_v4_metric_applicability(
    metrics,
    applicability,
    disturbances,
):
    """Apply predeclared N/A or missing-applicable semantics to v4 metrics."""
    metric_groups = {
        'escape_attempt': (
            'escape_attempt_count',
            'escape_success_count',
            'escape_failure_count',
            'radial_progress',
        ),
        'escape_duration': ('escape_time',),
        'orbit_count': ('approximate_orbit_count',),
        'revisit': ('revisit_count',),
        'saturation': (
            'saturation_time',
            'saturation_fraction',
            'saturation_axis_counts',
            'maximum_limit_excess',
        ),
    }
    for applicability_name, metric_names in metric_groups.items():
        applies = applicability[applicability_name]
        for metric_name in metric_names:
            current = metrics[metric_name]
            if not applies:
                metrics[metric_name] = unavailable(
                    f'{applicability_name} declared not applicable '
                    'before execution',
                    unit=current.get('unit'),
                    provenance='schema-v4 metric applicability',
                    status='not_applicable',
                )
            elif current['status'] == 'not_applicable':
                metrics[metric_name] = unavailable(
                    f'{applicability_name} was applicable but evidence '
                    'was unavailable',
                    unit=current.get('unit'),
                    provenance=current.get('provenance'),
                )
    delay_metrics = {
        'observed_raw_cost_delay': (
            float(disturbances.get('sensor_delay_sec', 0.0)) > 0.0
        ),
        'observed_source_cost_delay': (
            float(disturbances.get('sensor_delay_sec', 0.0)) > 0.0
        ),
        'observed_pose_delay': (
            float(disturbances.get('pose_delay_sec', 0.0)) > 0.0
        ),
    }
    for metric_name, stream_applies in delay_metrics.items():
        current = metrics[metric_name]
        if not applicability['delay'] or not stream_applies:
            metrics[metric_name] = unavailable(
                'delay stream declared not applicable before execution',
                unit=current.get('unit'),
                provenance='schema-v4 disturbances and applicability',
                status='not_applicable',
            )
        elif current['status'] == 'not_applicable':
            metrics[metric_name] = unavailable(
                'configured delay stream evidence was unavailable',
                unit=current.get('unit'),
                provenance=current.get('provenance'),
            )
    return metrics


def _v4_applicability_integrity(
    metrics,
    attempts,
    applicability,
    disturbances,
):
    """Require every applicable v4 metric and every successful attempt row."""
    reasons = []
    if applicability['escape_attempt'] and not attempts:
        reasons.append('designated escape case has no observed attempt')
    if not applicability['escape_attempt'] and attempts:
        reasons.append('escape occurred in a case declared not applicable')
    for attempt in attempts:
        if attempt.get('outcome') != 'success':
            continue
        for applicability_name, metric_name in (
            ('escape_duration', 'duration'),
            ('orbit_count', 'orbit_count'),
        ):
            expected = (
                'valid'
                if applicability[applicability_name]
                else 'not_applicable'
            )
            if attempt[metric_name].get('status') != expected:
                reasons.append(
                    f'successful attempt {attempt["attempt_index"]} '
                    f'{metric_name} status is not {expected}'
                )
    metric_groups = {
        'escape_attempt': (
            'escape_attempt_count',
            'escape_success_count',
            'escape_failure_count',
            'radial_progress',
        ),
        'escape_duration': ('escape_time',),
        'orbit_count': ('approximate_orbit_count',),
        'revisit': ('revisit_count',),
        'saturation': (
            'saturation_time',
            'saturation_fraction',
            'saturation_axis_counts',
            'maximum_limit_excess',
        ),
    }
    for name, metric_names in metric_groups.items():
        expected = 'valid' if applicability[name] else 'not_applicable'
        for metric_name in metric_names:
            if metrics[metric_name].get('status') != expected:
                reasons.append(
                    f'{metric_name} status is not {expected}'
                )
    sensor_delay = float(
        disturbances.get('sensor_delay_sec', 0.0)
    )
    pose_delay = float(disturbances.get('pose_delay_sec', 0.0))
    delay_expectations = {
        'observed_raw_cost_delay': sensor_delay > 0.0,
        'observed_source_cost_delay': sensor_delay > 0.0,
        'observed_pose_delay': pose_delay > 0.0,
    }
    for metric_name, applies in delay_expectations.items():
        expected = 'valid' if applies else 'not_applicable'
        if metrics[metric_name].get('status') != expected:
            reasons.append(f'{metric_name} status is not {expected}')
    return {'passed': not reasons, 'reasons': reasons}


def _alignment_summary(rows, prefixes):
    summary = {}
    for prefix in prefixes:
        valid = [row for row in rows if row.get(f'{prefix}_valid')]
        skews = [
            abs(int(row[f'{prefix}_skew_ns']))
            for row in valid
            if row.get(f'{prefix}_skew_ns') is not None
        ]
        summary[prefix] = {
            'anchor_count': len(rows),
            'matched_count': len(valid),
            'matched_fraction': len(valid) / len(rows) if rows else 0.0,
            'maximum_absolute_skew_ns': max(skews) if skews else None,
        }
    return summary


def _plot_unavailable(path, title, reason, style):
    figure, axis = plt.subplots(figsize=style['figsize'])
    axis.axis('off')
    axis.set_title(title)
    axis.text(
        0.5, 0.5, f'Not available\n{reason}',
        ha='center', va='center', wrap=True,
    )
    figure.savefig(path, dpi=style['dpi_level'], bbox_inches='tight')
    plt.close(figure)


def _save_plot(path, title, drawer, available, reason):
    style = init_plot_style()
    if not available:
        _plot_unavailable(path, title, reason, style)
        return
    figure, axis = plt.subplots(figsize=(6.5, 4.0))
    drawer(axis)
    axis.set_title(title)
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(path, dpi=style['dpi_level'])
    plt.close(figure)


def _generate_plots(
    plot_directory,
    synchronized,
    odometry_rows,
    state_rows,
    event_rows,
    candidate_rows,
    control_rows,
    fill_rows,
    sources,
):
    times = [row['t_motion_sec'] for row in synchronized]
    valid_cost = [
        row for row in synchronized
        if row.get('cost_anchor_valid') and row.get('t_motion_sec') is not None
    ]

    def cost_plot(axis):
        for field, label in (
            ('raw_cost', 'raw'),
            ('augmented_cost', 'augmented'),
            ('source_score', 'source score'),
        ):
            axis.plot(
                [row['t_motion_sec'] for row in valid_cost],
                [row.get(field, math.nan) for row in valid_cost],
                label=label,
            )
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('cost / score')
        axis.legend()

    _save_plot(
        plot_directory / 'cost.png', 'Cost and source score', cost_plot,
        bool(valid_cost), 'no valid synchronized cost anchors',
    )

    def component_plot(axis):
        for field, label in (
            ('raw_cost', 'raw'),
            ('gaussian_cost', 'Gaussian'),
            ('affine_cost', 'affine'),
            ('augmented_cost', 'augmented'),
        ):
            axis.plot(
                times,
                [row.get(field, math.nan) for row in synchronized],
                label=label,
            )
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('cost')
        axis.legend()

    _save_plot(
        plot_directory / 'components.png', 'Cost components',
        component_plot, bool(synchronized), 'no synchronized cost data',
    )

    def state_plot(axis):
        valid = [
            row for row in state_rows
            if row['in_readiness_interval'] and row.get('state_valid')
        ]
        axis.step(
            [row['t_motion_sec'] for row in valid],
            [row['state'] for row in valid],
            where='post',
            label='state',
        )
        for event in event_rows:
            if event['in_readiness_interval']:
                axis.axvline(event['t_motion_sec'], color='k', alpha=0.12)
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('state enum')

    _save_plot(
        plot_directory / 'state_events.png', 'State and event timeline',
        state_plot,
        any(row.get('state_valid') for row in state_rows),
        'no valid algorithm state samples',
    )

    def weights_plot(axis):
        for field, label in (
            ('sensor_weight', 'raw'),
            ('gaussian_weight', 'Gaussian'),
            ('affine_weight', 'affine'),
        ):
            axis.plot(
                times,
                [row.get(field, math.nan) for row in synchronized],
                label=label,
            )
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('weight')
        axis.legend()

    _save_plot(
        plot_directory / 'weights.png', 'Cost weights', weights_plot,
        bool(synchronized), 'no synchronized weights',
    )

    def trajectory_plot(axis):
        axis.plot(
            [
                row['x_m'] for row in odometry_rows
                if row['in_readiness_interval']
            ],
            [
                row['y_m'] for row in odometry_rows
                if row['in_readiness_interval']
            ],
            label='trajectory',
        )
        for source in sources:
            axis.scatter(
                [source.get('x_m')], [source.get('y_m')],
                marker='*', s=80, label=f"source {source.get('id')}",
            )
        for fill in fill_rows:
            if fill.get('active') and not fill.get('superseded'):
                axis.scatter(
                    [fill['center_x']], [fill['center_y']],
                    marker='x', label=f"fill {fill['fill_id']}",
                )
        axis.set_xlabel('x [m]')
        axis.set_ylabel('y [m]')
        axis.axis('equal')
        axis.legend(fontsize=6)

    _save_plot(
        plot_directory / 'trajectory_sources_fills.png',
        'Trajectory, sources, and fills', trajectory_plot,
        bool(odometry_rows), 'no odometry',
    )

    def command_plot(axis):
        rows = [
            row for row in control_rows if row['in_readiness_interval']
        ]
        axis.plot(
            [row['t_motion_sec'] for row in rows],
            [row['combined_unsaturated_vx'] for row in rows],
            label='unsaturated vx',
        )
        axis.plot(
            [row['t_motion_sec'] for row in rows],
            [row['final_vx'] for row in rows],
            label='final vx',
        )
        axis.plot(
            [row['t_motion_sec'] for row in rows],
            [row['combined_unsaturated_wz'] for row in rows],
            label='unsaturated wz',
        )
        axis.plot(
            [row['t_motion_sec'] for row in rows],
            [row['final_wz'] for row in rows],
            label='final wz',
        )
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('command')
        axis.legend(fontsize=7)

    _save_plot(
        plot_directory / 'command_saturation.png',
        'Command saturation', command_plot,
        bool(control_rows), 'no control diagnostics',
    )

    radial_rows = [
        row for row in state_rows
        if (
            row['in_readiness_interval']
            and row.get('radial_distance_valid')
        )
    ]

    def radial_plot(axis):
        axis.plot(
            [row['t_motion_sec'] for row in radial_rows],
            [row['radial_distance'] for row in radial_rows],
            label='published radial distance',
        )
        axis.plot(
            [row['t_motion_sec'] for row in radial_rows],
            [row['radial_progress'] for row in radial_rows],
            label='published radial progress',
        )
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('distance [m]')
        axis.legend()

    _save_plot(
        plot_directory / 'radial_escape.png', 'Radial escape diagnostics',
        radial_plot, bool(radial_rows), 'no escape/radial state evidence',
    )

    def fill_plot(axis):
        axis.plot(
            [row['t_motion_sec'] for row in fill_rows],
            [row['amplitude'] for row in fill_rows],
            marker='o', label='amplitude',
        )
        axis.plot(
            [row['t_motion_sec'] for row in fill_rows],
            [row['sigma_major'] for row in fill_rows],
            marker='s', label='sigma major',
        )
        axis.set_xlabel('motion time [s]')
        axis.set_ylabel('fill value')
        axis.legend()

    _save_plot(
        plot_directory / 'gaussian_history.png', 'Gaussian fill history',
        fill_plot, bool(fill_rows), 'no typed Gaussian fill lifecycle',
    )

    valid_candidate_rows = [
        row for row in candidate_rows if row['candidate_interval_valid']
    ]

    def candidate_plot(axis):
        for index, row in enumerate(valid_candidate_rows, start=1):
            estimate = row['candidate_raw_cost_estimate']
            lower = row['candidate_raw_cost_lower']
            upper = row['candidate_raw_cost_upper']
            is_goal = row['event_type'] == AlgorithmEvent.EVENT_GOAL_REACHED
            axis.errorbar(
                [index],
                [estimate],
                yerr=[[estimate - lower], [upper - estimate]],
                fmt='o',
                color='tab:green' if is_goal else 'tab:blue',
                capsize=4,
                label=(
                    'ranked goal'
                    if is_goal
                    else 'candidate observation'
                ),
            )
            axis.annotate(
                f"C{int(row['candidate_ordinal'])}",
                (index, estimate),
                xytext=(4, 4),
                textcoords='offset points',
                fontsize=8,
            )
            comparison = row.get('comparison_filled_raw_cost_lower')
            if is_goal and _finite(comparison):
                axis.axhline(
                    comparison,
                    color='tab:orange',
                    linestyle='--',
                    alpha=0.8,
                    label='retained candidate lower bound',
                )
        handles, labels = axis.get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        axis.legend(unique.values(), unique.keys(), fontsize=7)
        axis.set_xlabel('candidate evidence observation')
        axis.set_ylabel('raw cost')

    _save_plot(
        plot_directory / 'candidate_ranking.png',
        'Rotation-stable candidate raw costs',
        candidate_plot,
        bool(valid_candidate_rows),
        'no valid counted-candidate interval evidence',
    )


def _summary_csv_row(metrics, run_id, status):
    row = {'run_id': run_id, 'analysis_status': status}
    for name, item in metrics.items():
        value = item['value']
        if isinstance(value, (dict, list)):
            value = _json_cell(value)
        row[f'{name}_value'] = value
        row[f'{name}_status'] = item['status']
        row[f'{name}_reason'] = item['reason']
    return row


def _file_hashes(paths):
    hashes = {}
    for path in paths:
        digest = hashlib.sha256()
        with Path(path).open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        hashes[str(path)] = digest.hexdigest()
    return hashes


def _v2_lifecycle_analysis(bag_data, metadata, scenario, *, candidate_cost_mad_scale=None):
    """Add source-backed moving-pipeline timelines without changing goal time."""
    from ros_esc.experiment_recording.record_run import v2_identity_from_metadata
    identity = v2_identity_from_metadata(metadata)
    if identity is None:
        return None, {}, {}
    from ros_esc.experiment_recording.v2_lifecycle_validation import lifecycle_stream_errors
    from ros_esc.v2_stream import time_to_ns
    messages = {topic: [(record.bag_timestamp_ns, record.message) for record in records]
                for topic, records in bag_data.records_by_topic.items()}
    topics = {alias: entry['topic'] for alias, entry in bag_data.topics_by_alias.items()}
    overrides = scenario.get('algorithm', {}).get('launch_overrides', {})
    mode = overrides.get('convergence_metric_mode')
    mad_scale = (overrides.get('candidate_cost_mad_scale', 3.0)
                 if candidate_cost_mad_scale is None else candidate_cost_mad_scale)
    errors, audit = lifecycle_stream_errors(messages, identity, topics=topics,
        metric_mode=mode, candidate_cost_mad_scale=mad_scale,
        moving_verification_mode=overrides.get(
            'v2_verification_motion_mode', 'rolling_neighborhood_v1'),
        verification_evidence_policy=overrides.get(
            'v2_verification_evidence_policy', 'angular_profiles_v1'))
    timelines = []
    epochs = {row['search_epoch']: row['started_at_ns'] for row in audit['epochs']}
    for confirmation in audit['confirmations']:
        started = epochs.get(confirmation['search_epoch'])
        if started is not None:
            timelines.append({
                'kind': 'epoch_to_confirmation', 'search_epoch': confirmation['search_epoch'],
                'confirmation_sequence': confirmation['confirmation_sequence'],
                'start_ns': started, 'end_ns': confirmation['source_stamp_ns'],
                'duration_sec': (confirmation['source_stamp_ns'] - started) / 1e9,
            })
    snapshots = {}
    snapshot_rows = messages.get(topics.get('v2_candidate_snapshots', '/gesc_gaussian/v2/candidate_snapshots'), [])
    if overrides.get('v2_verification_evidence_policy') == 'recurrent_trapping_v1':
        snapshot_rows = [(stamp, wrapper.snapshot) for stamp, wrapper in messages.get(topics.get(
            'v2_recurrent_candidate_snapshots', '/gesc_gaussian/v2/recurrent_candidate_snapshots'), [])]
    for _, snap in snapshot_rows:
        key = (snap.candidate_id, snap.snapshot_revision)
        if key in snapshots:
            continue
        snapshots[key] = snap
        timelines.append({
            'kind': ('candidate_to_verification_snapshot' if snap.snapshot_revision == 1
                     else 'candidate_to_redesign_snapshot'), 'search_epoch': int(snap.search_epoch),
            'candidate_id': int(snap.candidate_id), 'snapshot_revision': int(snap.snapshot_revision),
            'start_ns': time_to_ns(snap.accepted_at), 'end_ns': time_to_ns(snap.stamp),
            'duration_sec': (time_to_ns(snap.stamp) - time_to_ns(snap.accepted_at)) / 1e9,
        })
    preparations = {row['preparation_id']: row for row in audit['preparations']}
    for commit in audit['commits']:
        preparation = preparations.get(commit['preparation_id'])
        if preparation is not None:
            timelines.append({
                'kind': 'prepare_to_commit', 'candidate_id': commit['candidate_id'],
                'preparation_id': commit['preparation_id'],
                'start_ns': preparation['prepare_stamp_ns'], 'end_ns': commit['committed_at_ns'],
                'duration_sec': (commit['committed_at_ns'] - preparation['prepare_stamp_ns']) / 1e9,
            })
    status = 'invalid' if errors else 'valid'
    metrics = {}
    for kind in ('epoch_to_confirmation', 'candidate_to_verification_snapshot', 'prepare_to_commit'):
        values = [row['duration_sec'] for row in timelines if row['kind'] == kind
                  and math.isfinite(row['duration_sec']) and row['duration_sec'] >= 0]
        name = 'v2_median_' + kind + '_sec'
        metrics[name] = (metric(statistics.median(values), status=status, unit='s',
                               provenance='V2 typed source/publication timeline; observed intervals only')
                         if values and not errors else unavailable(
                             'lifecycle contract errors' if errors else 'no observed matching interval',
                             unit='s', status='invalid' if errors else 'unavailable'))
        metrics[name]['observed_interval_count'] = len(values)
        metrics[name]['valid_interval_count'] = 0 if errors else len(values)
    metrics['v2_unique_fill_commits'] = metric(audit['counts'].get('unique_commits', 0),
                                              status=status, unit='commits')
    summary = {'status': status, 'errors': errors, 'audit': audit, 'timelines': timelines,
               'scope': 'Observed lifecycle timing; no independent basin-entry label or detector sensitivity claim.'}
    tables = {'v2_' + name + '.csv': rows for name, rows in audit.items() if isinstance(rows, list)}
    tables['v2_lifecycle_timelines.csv'] = timelines
    return summary, metrics, tables


def _stationary_centroid_analysis(bag_data, metadata):
    """Supplement Arm B request timing without redefining goal convergence."""
    from ros_esc.experiment_recording.record_run import stationary_centroid_config_from_target
    config = stationary_centroid_config_from_target(metadata.get('target_argv', []))
    if config is None:
        return None, {}, {}
    prefix = ('stationary_recurrent' if config['metric_mode'] == 'recurrent_geometry_v3'
              else 'stationary_centroid')
    from ros_esc.experiment_recording.stationary_centroid_validation import stationary_centroid_stream_errors
    messages = {topic: [(record.bag_timestamp_ns, record.message) for record in records]
                for topic, records in bag_data.records_by_topic.items()}
    topics = {alias: entry['topic'] for alias, entry in bag_data.topics_by_alias.items()}
    errors, audit = stationary_centroid_stream_errors(messages, config, topics=topics)
    status = 'invalid' if errors else 'valid'
    metrics = {}
    for kind in ('accepted_confirmation_to_request', 'request_to_active_fill_publication'):
        values = [row['duration_sec'] for row in audit['timelines'] if row['kind'] == kind
                  and math.isfinite(row['duration_sec']) and row['duration_sec'] >= 0]
        metrics[prefix + '_median_' + kind + '_sec'] = (
            metric(statistics.median(values), status=status, unit='s',
                   provenance='Arm B typed request and legacy result publication; observed intervals only')
            if values and not errors else unavailable(
                prefix.replace('_', ' ') + ' contract errors' if errors else 'no observed matching interval',
                unit='s', status='invalid' if errors else 'unavailable'))
        metrics[prefix + '_median_' + kind + '_sec'].update(
            observed_interval_count=len(values), valid_interval_count=0 if errors else len(values))
    for name, value in audit['counts'].items():
        metrics[prefix + '_' + name] = metric(value, status=status, unit='count')
    summary = {'status': status, 'errors': errors, 'audit': audit,
               'scope': audit['timing_scope']}
    if prefix == 'stationary_recurrent':
        summary['metric_mode'] = config['metric_mode']
    tables = {prefix + '_' + name + '.csv': rows
              for name, rows in audit.items() if isinstance(rows, list)}
    return summary, metrics, tables


def analyze_run(
    run_directory,
    output_directory=None,
    channel_index=None,
    sync_tolerance_sec=None,
    *,
    state_duration_basis='bag_receipt_v1',
):
    """Analyze one run and atomically publish a complete output directory."""
    run_directory = Path(run_directory).expanduser().resolve()
    output_directory = (
        Path(output_directory).expanduser().resolve()
        if output_directory is not None
        else run_directory / 'analysis' / 'phase07'
    )
    if output_directory.exists():
        raise FileExistsError(
            f'output directory already exists: {output_directory}'
        )
    if not run_directory.is_dir():
        raise FileNotFoundError(
            f'run directory does not exist: {run_directory}'
        )
    bag_paths = sorted((run_directory / 'bag').glob('*.db3'))
    if not bag_paths:
        raise FileNotFoundError('run bag has no .db3 files')
    before_hashes = _file_hashes(bag_paths)
    metadata = load_yaml(run_directory / 'metadata.yaml')
    channel_index, channel_source = _resolved_setting(
        run_directory,
        channel_index,
        'estimation_channel_index',
        0,
    )
    sync_tolerance_sec, tolerance_source = _resolved_setting(
        run_directory,
        sync_tolerance_sec,
        'sample_sync_tolerance_sec',
        0.05,
    )
    if state_duration_basis == 'simulation_publication_v1':
        supervisor_rate, rate_source = _simulation_supervisor_rate(run_directory, metadata)
    elif state_duration_basis == 'bag_receipt_v1':
        supervisor_rate, rate_source = _resolved_setting(
            run_directory, None, 'supervisor_publish_rate_hz', 20.0)
    else:
        raise ValueError('unknown state duration basis')
    channel_index = int(channel_index)
    sync_tolerance_sec = float(sync_tolerance_sec)
    supervisor_rate = float(supervisor_rate)
    if channel_index < 0:
        raise ValueError('channel index must be nonnegative')
    if not math.isfinite(sync_tolerance_sec) or sync_tolerance_sec < 0.0:
        raise ValueError(
            'synchronization tolerance must be finite and nonnegative'
        )

    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(
        prefix=f'.{output_directory.name}.tmp-',
        dir=output_directory.parent,
    ))
    try:
        tables = temporary / 'tables'
        plots = temporary / 'plots'
        tables.mkdir()
        plots.mkdir()
        bag_data = read_run_bag(run_directory)
        phase05_report = validate_run_directory(
            run_directory, write_report=False
        )
        stored_report = json.loads(
            (run_directory / 'completeness.json').read_text(encoding='utf-8')
        )
        source_records = records_for_alias(bag_data, 'source_cost')
        cost_records = records_for_alias(bag_data, 'cost_breakdown')
        gesc_records = records_for_alias(bag_data, 'gesc_diagnostics')
        control_records = records_for_alias(
            bag_data, 'control_diagnostics'
        )
        odometry_records = records_for_alias(bag_data, 'pose')
        state_records = records_for_alias(
            bag_data, 'algorithm_state'
        )
        event_records = records_for_alias(
            bag_data, 'algorithm_events'
        )
        fill_records = records_for_alias(bag_data, 'gaussian_fills')

        source_rows = _cost_rows(source_records)
        cost_rows = _cost_rows(cost_records)
        gesc_rows = _gesc_rows(gesc_records)
        control_rows = _control_rows(control_records)
        odometry_rows = _odometry_rows(odometry_records)
        state_rows = _state_rows(state_records)
        event_rows = _event_rows(event_records)
        candidate_rows = _candidate_rows(event_records)
        fill_rows = _fill_rows(fill_records)
        synchronized = _synchronized_rows(
            bag_data, channel_index, sync_tolerance_sec
        )
        readiness_states = [
            record for record in state_records
            if record.in_readiness_interval
        ]
        readiness_events = [
            record for record in event_records
            if record.in_readiness_interval
        ]
        readiness_odometry = [
            record for record in odometry_records
            if record.in_readiness_interval
        ]
        readiness_control = [
            record for record in control_records
            if record.in_readiness_interval
        ]
        intervals, durations_metric = _state_intervals(
            readiness_states,
            bag_data.readiness_start_ns,
            bag_data.readiness_end_ns,
            supervisor_rate,
            **({'state_duration_basis': state_duration_basis}
               if state_duration_basis != 'bag_receipt_v1' else {}),
        )
        scenario = _resolved_scenario(run_directory)
        schema_version = scenario.get('schema_version', 1)
        attempts = _escape_attempts(
            readiness_states,
            readiness_events,
            readiness_odometry,
            bag_data.readiness_end_ns,
            schema_version=schema_version,
        )
        table_rows = {
            'synchronized_samples.csv': synchronized,
            'source_cost.csv': source_rows,
            'cost_breakdown.csv': cost_rows,
            'gesc_diagnostics.csv': gesc_rows,
            'control_diagnostics.csv': control_rows,
            'odometry.csv': odometry_rows,
            'algorithm_state.csv': state_rows,
            'state_intervals.csv': intervals,
            'algorithm_events.csv': event_rows,
            'candidate_ranking.csv': candidate_rows,
            'gaussian_history.csv': fill_rows,
            'escape_attempts.csv': attempts,
        }
        mad_scale, _ = _resolved_setting(run_directory, None, 'candidate_cost_mad_scale', 3.0)
        v2_summary, v2_metrics, v2_tables = _v2_lifecycle_analysis(
            bag_data, metadata, scenario, candidate_cost_mad_scale=float(mad_scale))
        table_rows.update(v2_tables)
        stationary_summary, stationary_metrics, stationary_tables = _stationary_centroid_analysis(
            bag_data, metadata)
        table_rows.update(stationary_tables)
        for filename, rows in table_rows.items():
            _write_csv(tables / filename, rows)

        metrics = _compute_metrics(
            bag_data,
            metadata,
            readiness_states,
            readiness_events,
            fill_records,
            readiness_odometry,
            readiness_control,
            durations_metric,
            attempts,
            schema_version=schema_version,
        )
        metrics.update(v2_metrics)
        metrics.update(stationary_metrics)
        v4_summary = {}
        v4_integrity = {'passed': True, 'reasons': []}
        metrics['counted_candidate_ranked_goal'] = (
            _candidate_ranking_metric(scenario, candidate_rows)
        )
        if scenario.get('schema_version', 1) >= 4:
            applicability = scenario.get('metric_applicability')
            if not isinstance(applicability, dict):
                raise ValueError(
                    'schema-v4 resolved scenario lacks metric_applicability'
                )
            disturbances = scenario.get('disturbances', {})
            metrics = _apply_v4_metric_applicability(
                metrics,
                applicability,
                disturbances,
            )
            attempt_metrics = _v4_attempt_metrics(
                attempts,
                applicability,
            )
            v4_integrity = _v4_applicability_integrity(
                metrics,
                attempt_metrics,
                applicability,
                disturbances,
            )
            aggregate_distance = _aggregate_target_distance_metric(
                run_directory,
                readiness_odometry,
            )
            metrics['final_aggregate_target_distance'] = (
                aggregate_distance
            )
            v4_summary = {
                'acceptance_family': scenario.get('acceptance_family'),
                'acceptance_partition': scenario.get(
                    'acceptance_partition'
                ),
                'repeat_reference': scenario.get('repeat_reference'),
                'metric_applicability': applicability,
                'escape_attempts': attempt_metrics,
                'applicability_integrity': v4_integrity,
                'aggregate_truth_result_sha256': scenario.get(
                    'success', {}
                ).get('ground_truth', {}).get(
                    'aggregate_field', {}
                ).get('result_sha256'),
            }
        critical = {
            'readiness': bag_data.readiness_start_ns is not None,
            'cost': bool(cost_records),
            'pose': bool(odometry_records),
            'control': bool(control_records),
        }
        if not all(critical.values()):
            analysis_status = 'invalid'
        elif not phase05_report.get('passed'):
            analysis_status = 'partial'
        elif any(
            item['status'] == 'invalid' for item in metrics.values()
        ):
            analysis_status = 'partial'
        elif not v4_integrity['passed']:
            analysis_status = 'partial'
        else:
            analysis_status = 'complete'
        summary = {
            'schema_version': 1,
            'run_id': run_directory.name,
            'analysis_status': analysis_status,
            'algorithm_profile': metadata.get('algorithm_profile'),
            'settings': {
                'channel_index': channel_index,
                'channel_index_source': channel_source,
                'sync_tolerance_sec': sync_tolerance_sec,
                'sync_tolerance_source': tolerance_source,
                'supervisor_publish_rate_hz': supervisor_rate,
                'supervisor_publish_rate_source': rate_source,
            },
            'metrics': metrics,
            'candidate_ranking': {
                'observation_count': len(candidate_rows),
                'observations': candidate_rows,
            },
        }
        summary.update(v4_summary)
        if state_duration_basis != 'bag_receipt_v1':
            summary['settings']['state_duration_basis'] = state_duration_basis
        if v2_summary is not None:
            summary['v2_moving_pipeline'] = v2_summary
        if stationary_summary is not None:
            stationary_name = ('stationary_recurrent_pipeline'
                if stationary_summary.get('metric_mode') == 'recurrent_geometry_v3'
                else 'stationary_centroid_pipeline')
            summary[stationary_name] = stationary_summary
        (temporary / 'summary_metrics.json').write_text(
            json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)
            + '\n',
            encoding='utf-8',
        )
        _write_csv(
            temporary / 'summary_metrics.csv',
            [_summary_csv_row(metrics, run_directory.name, analysis_status)],
        )
        _generate_plots(
            plots,
            synchronized,
            odometry_rows,
            state_rows,
            event_rows,
            candidate_rows,
            control_rows,
            fill_rows,
            _source_points(run_directory),
        )
        after_hashes = _file_hashes(bag_paths)
        if before_hashes != after_hashes:
            raise RuntimeError('raw bag content changed during analysis')
        completeness = {
            'schema_version': 1,
            'run_id': run_directory.name,
            'status': analysis_status,
            'stored_phase05_passed': stored_report.get('passed'),
            'fresh_phase05_validation': phase05_report,
            'critical_inputs': critical,
            'topic_types': bag_data.topic_types,
            'topic_counts': {
                topic: len(records)
                for topic, records in bag_data.records_by_topic.items()
            },
            'timestamps': {
                'readiness_start_bag_timestamp_ns': (
                    bag_data.readiness_start_ns
                ),
                'readiness_end_bag_timestamp_ns': bag_data.readiness_end_ns,
                'preserved_domains': [
                    'bag_timestamp_ns', 'ros_timestamp_ns',
                    'source_timestamp_sec',
                ],
            },
            'alignment': _alignment_summary(
                synchronized, ('source', 'gesc', 'pose', 'control', 'state')
            ),
            'outputs': {
                'tables': {
                    name: len(rows) for name, rows in table_rows.items()
                },
                'plots': list(PLOT_FILES),
            },
            'metric_validity': {
                name: item['status'] for name, item in metrics.items()
            },
            'recording_failures': list(phase05_report.get('failures', [])),
            'analysis_failures': [],
            'warnings': [
                (
                    f'{name} used assumed fallback'
                    if source == 'assumed fallback' else None
                )
                for name, source in (
                    ('channel_index', channel_source),
                    ('sync_tolerance_sec', tolerance_source),
                    ('supervisor_publish_rate_hz', rate_source),
                )
            ],
            'raw_bag_sha256': before_hashes,
        }
        completeness['warnings'] = [
            item for item in completeness['warnings'] if item is not None
        ]
        (temporary / 'analysis_completeness.json').write_text(
            json.dumps(
                completeness, indent=2, sort_keys=True, allow_nan=False
            ) + '\n',
            encoding='utf-8',
        )
        os.replace(temporary, output_directory)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return summary


def _analysis_files(inputs):
    found = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        candidates = []
        if path.is_file() and path.name == 'summary_metrics.json':
            candidates = [path]
        elif path.is_dir():
            direct = path / 'summary_metrics.json'
            default = path / 'analysis' / 'phase07' / 'summary_metrics.json'
            if direct.is_file():
                candidates = [direct]
            elif default.is_file():
                candidates = [default]
            else:
                candidates = sorted(path.rglob('summary_metrics.json'))
        for candidate in candidates:
            if candidate not in found:
                found.append(candidate)
    return found


def summarize_matrix(inputs, output_directory):
    """Aggregate existing per-run Phase 07 summaries without altering them."""
    output_directory = Path(output_directory).expanduser().resolve()
    if output_directory.exists():
        raise FileExistsError(
            f'output directory already exists: {output_directory}'
        )
    files = _analysis_files(inputs)
    if not files:
        raise FileNotFoundError('no summary_metrics.json files were found')
    rows = []
    documents = []
    for path in files:
        document = json.loads(path.read_text(encoding='utf-8'))
        documents.append(document)
        rows.append(_summary_csv_row(
            document['metrics'],
            document['run_id'],
            document['analysis_status'],
        ))
    status_counts = Counter(item['analysis_status'] for item in documents)
    escape_times = [
        float(item['metrics']['escape_time']['value'])
        for item in documents
        if (
            item['metrics']['escape_time']['status'] == 'valid'
            and _finite(item['metrics']['escape_time']['value'])
        )
    ]
    controller_results = [
        bool(item['metrics']['controller_success']['value'])
        for item in documents
        if item['metrics']['controller_success']['status'] == 'valid'
    ]
    aggregate = {
        'schema_version': 1,
        'run_count': len(documents),
        'analysis_status_counts': dict(sorted(status_counts.items())),
        'controller_success_rate': (
            sum(controller_results) / len(controller_results)
            if controller_results else None
        ),
        'controller_success_denominator': len(controller_results),
        'median_escape_time_sec': (
            statistics.median(escape_times) if escape_times else None
        ),
        'p95_escape_time_sec': (
            float(np.percentile(escape_times, 95))
            if escape_times else None
        ),
        'source_summaries': [str(path) for path in files],
    }
    output_directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(
        prefix=f'.{output_directory.name}.tmp-',
        dir=output_directory.parent,
    ))
    try:
        _write_csv(temporary / 'matrix_summary.csv', rows)
        (temporary / 'matrix_summary.json').write_text(
            json.dumps(aggregate, indent=2, sort_keys=True, allow_nan=False)
            + '\n',
            encoding='utf-8',
        )
        os.replace(temporary, output_directory)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return aggregate


V2_LABEL_INPUT_ALIASES = (
    'pose', 'source_cost', 'raw_cost_legacy', 'encoder',
    'sensor_transform', 'clock', 'timekeeper',
)
V2_CALIBRATION_GRID = {
    'window_seconds': (3.0, 6.0, 9.0),
    'epsilon_m': (0.03, 0.06, 0.12, 0.24),
    'max_radius_m': (0.25, 0.50, 0.75),
}


def _v2_file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _v2_write_json(path, document):
    """Create prospective evidence without replacing a previous version."""
    serialized = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + '\n'
    path = Path(path)
    # A terminated writer may leave a hidden temporary file, never a partial
    # published receipt. link() supplies atomic exclusive-create semantics.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=path.parent,
                prefix=f'.{path.name}.', suffix='.incomplete', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def qualify_v2_replay_inputs(bag_data, *, tolerance_sec=0.05, gap_sec=0.50):
    """Qualify complete input streams, keeping invalid pose samples explicit.

    This function never reads convergence, fills, algorithm states or events.
    Relative source time is reconciled with absolute odometry through the
    recorded simulation timekeeper. Readiness is retained only as a later mask.
    """
    keepers = records_for_alias(bag_data, 'timekeeper')
    starts = {float(record.message.start_time) for record in keepers}
    modes = {record.message.mode for record in keepers}
    timekeeper_valid = (
        len(starts) == 1 and all(math.isfinite(value) for value in starts)
        and modes == {'sim time'}
    )
    offset = next(iter(starts)) if timekeeper_valid else 0.0
    clock_values = [stamp_nanoseconds(record.message.clock)
                    for record in records_for_alias(bag_data, 'clock')]
    clock_valid = bool(clock_values) and all(
        newer >= older for older, newer in zip(clock_values, clock_values[1:])
    )
    stream_receipts = {}
    indexes = {}
    for alias in ('source_cost', 'raw_cost_legacy', 'encoder', 'sensor_transform'):
        records = records_for_alias(bag_data, alias)
        times = []
        invalid = regressions = duplicates = gaps = 0
        publication_skews = []
        previous = None
        for record in records:
            value = record.source_timestamp_sec
            valid = record.source_timestamp_valid and _finite(value)
            if alias == 'source_cost':
                valid = valid and bool(record.message.raw_cost_valid)
                valid = valid and all(_finite(x) for x in record.message.raw_cost)
                valid = valid and record.ros_timestamp_ns is not None
                if record.ros_timestamp_ns is not None and _finite(value):
                    skew = record.ros_timestamp_ns / 1e9 - float(value) - offset
                    publication_skews.append(skew)
                    valid = valid and -1e-9 <= skew <= tolerance_sec + 1e-9
            if alias in ('raw_cost_legacy', 'encoder'):
                valid = valid and bool(len(record.message.data))
                valid = valid and all(_finite(x) for x in record.message.data)
            if alias == 'sensor_transform':
                valid = valid and bool(len(record.message.transform_array))
                for transform in record.message.transform_array:
                    valid = valid and all(_finite(x) for x in (
                        transform.translation.x, transform.translation.y,
                        transform.translation.z, transform.rotation.x,
                        transform.rotation.y, transform.rotation.z,
                        transform.rotation.w,
                    ))
            if not valid:
                invalid += 1
                continue
            stamp = round((float(value) + offset) * NANOSECONDS_PER_SECOND)
            if previous is not None:
                regressions += int(stamp < previous)
                duplicates += int(stamp == previous)
                gaps += int(stamp - previous > round(gap_sec * 1e9))
            previous = stamp
            times.append(stamp)
        stream_receipts[alias] = {
            'message_count': len(records), 'valid_count': len(times),
            'invalid_count': invalid, 'regressions': regressions,
            'duplicates': duplicates, 'excessive_gaps': gaps,
            'publication_minus_source_sec_range': (
                [min(publication_skews), max(publication_skews)]
                if publication_skews else None),
        }
        # A regressing stream cannot safely support ordered matching.
        indexes[alias] = np.asarray(times if not regressions else [], dtype=np.int64)

    samples = []
    previous = None
    previous_frame = None
    pose_receipt = Counter()
    tolerance_ns = round(tolerance_sec * 1e9)
    for record in records_for_alias(bag_data, 'pose'):
        pose = record.message.pose.pose
        xy = [float(pose.position.x), float(pose.position.y)]
        stamp = record.ros_timestamp_ns
        frame = record.message.header.frame_id
        valid = (
            timekeeper_valid and clock_valid and stamp is not None and bool(frame)
            and all(_finite(x) for x in xy)
        )
        reasons = []
        if not valid:
            reasons.append('invalid_pose_or_timekeeper')
        if previous is not None and stamp is not None:
            if stamp < previous:
                reasons.append('pose_time_regression')
            if stamp - previous > round(gap_sec * 1e9):
                reasons.append('pose_gap')
            pose_receipt['duplicate_timestamps'] += int(stamp == previous)
        if previous_frame is not None and frame != previous_frame:
            reasons.append('frame_change')
        skews = {}
        for alias, times in indexes.items():
            if stamp is None or not len(times):
                reasons.append(f'{alias}_unavailable')
                continue
            at = int(np.searchsorted(times, stamp))
            choices = times[max(0, at - 1):min(len(times), at + 1)]
            skew = min((int(t) - stamp for t in choices), key=abs)
            skews[alias] = skew
            if abs(skew) > tolerance_ns:
                reasons.append(f'{alias}_unaligned')
        for reason in reasons:
            pose_receipt[reason] += 1
        valid = valid and not reasons
        samples.append({
            'stamp_ns': stamp, 'bag_timestamp_ns': record.bag_timestamp_ns,
            'xy': xy if all(_finite(x) for x in xy) else None,
            'frame_id': frame, 'qualified': valid,
            'invalid_reasons': reasons, 'source_skews_ns': skews,
            'readiness_eligible': record.in_readiness_interval,
        })
        previous = stamp
        previous_frame = frame
    return samples, {
        'timekeeper_valid': timekeeper_valid,
        'clock_valid': clock_valid, 'clock_message_count': len(clock_values),
        'timekeeper_modes': sorted(modes),
        'experiment_start_sec': offset if timekeeper_valid else None,
        'source_streams': stream_receipts,
        'pose_messages': len(samples),
        'qualified_pose_messages': sum(x['qualified'] for x in samples),
        'pose_reasons': dict(pose_receipt),
        'sync_tolerance_sec': tolerance_sec, 'maximum_gap_sec': gap_sec,
    }


def qualify_v2_cycle_basins(scenario, *, model_config_path):
    """Revalidate cycle-mean basins using the existing evaluator cost owner."""
    from scipy.optimize import minimize
    from ros_esc.scenario_runner import aggregate_field_truth as truth

    binding = truth.sensor_geometry_binding()
    model, model_path = truth._model(  # noqa: SLF001
        scenario['sources'], model_config_path, binding,
    )
    bounds = scenario['bounds_m']

    def cycle_mean(xy, count=72):
        return float(np.mean([
            truth.evaluate_raw_cost(model, xy[0], xy[1], 2.0 * math.pi * k / count)
            for k in range(count)
        ]))

    basins = []
    for source in scenario['sources']:
        origin = np.asarray([source['x_m'], source['y_m']], dtype=float)
        search = [
            (max(bounds[0], origin[0] - 0.75), min(bounds[1], origin[0] + 0.75)),
            (max(bounds[2], origin[1] - 0.75), min(bounds[3], origin[1] + 0.75)),
        ]
        receipts = []
        for dx in (-0.25, 0.0, 0.25):
            for dy in (-0.25, 0.0, 0.25):
                initial = np.clip(origin + [dx, dy],
                                  [b[0] for b in search], [b[1] for b in search])
                result = minimize(
                    cycle_mean, initial, method='L-BFGS-B', bounds=search,
                    options={'maxiter': 200, 'ftol': 1e-12, 'gtol': 1e-7},
                )
                receipts.append({
                    'initial_xy': initial.tolist(), 'xy': result.x.tolist(),
                    'cost': float(result.fun), 'success': bool(result.success),
                    'status': int(result.status), 'message': str(result.message),
                    'iterations': int(result.nit),
                })
        successes = [r for r in receipts if r['success'] and _finite(r['cost'])]
        best = min(successes or receipts, key=lambda r: r['cost'])
        center = np.asarray(best['xy'])
        agreeing = sum(bool(np.linalg.norm(np.asarray(r['xy']) - center) <= 0.05)
                       for r in successes)
        interior = all(lo + 0.05 <= x <= hi - 0.05
                       for x, (lo, hi) in zip(center, search))
        refined = cycle_mean(center, 144)
        ring = [center + 0.50 * np.asarray([math.cos(a), math.sin(a)])
                for a in np.linspace(0.0, 2.0 * math.pi, 36, endpoint=False)]
        ring_inside = all(bounds[0] <= p[0] <= bounds[1]
                          and bounds[2] <= p[1] <= bounds[3] for p in ring)
        ring_costs = [cycle_mean(p) for p in ring] if ring_inside else []
        depth = min(ring_costs) - best['cost'] if ring_costs else None
        qualified = (agreeing >= 2 and interior and ring_inside
                     and abs(refined - best['cost']) <= 0.01
                     and depth is not None and depth >= 0.025)
        basins.append({
            'source_id': source['id'], 'center_xy': center.tolist(),
            'region_radius_m': 0.50, 'qualified': bool(qualified),
            'best_cycle_mean_raw_cost': best['cost'],
            'agreeing_successful_starts': agreeing, 'interior': bool(interior),
            'quadrature_72_to_144_difference': abs(refined - best['cost']),
            'ring_inside_bounds': bool(ring_inside), 'ring_depth_raw_cost': depth,
            'ring_costs': ring_costs, 'optimizer_receipts': receipts,
        })
    return {
        'method': 'stationary_cycle_mean_ring_qualified_v2_m1_v1',
        'model_config_path': str(model_path),
        'model_config_sha256': _v2_file_hash(model_path),
        'sensor_geometry_sha256': _v2_file_hash(truth.SENSOR_GEOMETRY_PATH),
        'sensor_transform_sha256': _v2_file_hash(truth.SENSOR_TRANSFORM_CONFIG_PATH),
        'evaluator_owner_sha256': _v2_file_hash(truth.__file__),
        'basins': basins,
    }


def _v2_enclosure_segment_prefixes(samples, masks):
    """Evaluate each immutable full segment once; never cache clipped results."""
    from .v2_enclosure import segment_outside_exclusion
    time_failures, outside_failures = [0], [0]
    for first, second in zip(samples[:-1], samples[1:]):
        time_ok = bool(first['qualified'] and second['qualified']
                       and 0 <= second['stamp_ns'] - first['stamp_ns'] <= 500_000_000)
        outside = time_ok and all(segment_outside_exclusion(
            first['xy'], second['xy'], mask) for mask in masks.values())
        time_failures.append(time_failures[-1] + int(not time_ok))
        outside_failures.append(outside_failures[-1] + int(not outside))
    return time_failures, outside_failures


def label_v2_basin_intervals(samples, geometry, *, minimum_residence_sec=12.0):
    """Label input-only modeled basin residence and directed travel."""
    if (isinstance(minimum_residence_sec, bool)
            or not isinstance(minimum_residence_sec, (int, float))
            or not math.isfinite(minimum_residence_sec) or minimum_residence_sec < 0):
        raise ValueError('minimum_residence_sec must be finite and nonnegative')
    enclosure = geometry.get('method') == 'operational_enclosure_v1'
    if enclosure:
        from .v2_enclosure import (
            point_in_positive, segment_in_positive, segment_outside_exclusion,
            prepare_membership,
        )
    qualified = [b for b in geometry['basins'] if b['qualified']]
    masks = ({b['source_id']: prepare_membership(b) for b in qualified}
             if enclosure else {})
    labels = []
    for basin in qualified:
        start = None
        last = None
        for index, sample in enumerate(samples + [None]):
            inside = sample is not None and sample['qualified'] and (
                point_in_positive(sample['xy'], masks[basin['source_id']]) if enclosure else
                np.linalg.norm(np.asarray(sample['xy']) - basin['center_xy'])
                <= basin['region_radius_m'])
            continuous = inside and (not enclosure or last is None or (
                0 <= sample['stamp_ns'] - samples[last]['stamp_ns'] <= 500_000_000
                and segment_in_positive(samples[last]['xy'], sample['xy'],
                                        masks[basin['source_id']])))
            if continuous:
                if start is None:
                    start = index
                last = index
                continue
            if start is not None:
                begin, end = samples[start]['stamp_ns'], samples[last]['stamp_ns']
                if end - begin >= minimum_residence_sec * NANOSECONDS_PER_SECOND:
                    labels.append({
                        'kind': 'positive_basin_residence',
                        'source_id': basin['source_id'],
                        'start_ns': begin, 'end_ns': end,
                        'duration_sec': (end - begin) / 1e9,
                        'common_support_eligible': end - begin >= 54 * 1e9,
                    })
            start = last = None
            if inside:
                start = last = index
    # Without every source region qualified, outside-region travel is ambiguous.
    if len(qualified) == len(geometry['basins']) and qualified:
        if enclosure:
            time_failures, outside_failures = _v2_enclosure_segment_prefixes(samples, masks)
        negative = []
        start = 0
        for end, sample in enumerate(samples):
            if not sample['qualified']:
                start = end + 1
                continue
            while (start < end and samples[start + 1]['stamp_ns']
                   <= sample['stamp_ns'] - 6 * 1e9):
                start += 1
            window = samples[start:end + 1]
            if not window or sample['stamp_ns'] - window[0]['stamp_ns'] < 6 * 1e9:
                continue
            positions = np.asarray([s['xy'] for s in window], dtype=float)
            if enclosure:
                # M1a fixes the measurement interval at exactly six seconds.
                # Clip only the represented first segment; immutable source
                # samples and the independently constructed field stay intact.
                target = sample['stamp_ns'] - 6_000_000_000
                clipped = window[0]['stamp_ns'] < target
                if clipped:
                    span = window[1]['stamp_ns'] - window[0]['stamp_ns']
                    if span <= 0:
                        continue
                    fraction = (target - window[0]['stamp_ns']) / span
                    positions[0] += fraction * (positions[1] - positions[0])
                # Preserve the original NumPy arithmetic and strict gates;
                # only predicate order and repeated mask queries are changed.
                net = float(np.linalg.norm(positions[-1] - positions[0]))
                path = float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum())
                if not (net >= 0.12 and path > 0 and net / path >= 0.80):
                    continue
                if time_failures[end] != time_failures[start]:
                    continue
                first_full_segment = start + int(clipped)
                if outside_failures[end] != outside_failures[first_full_segment]:
                    continue
                if clipped and any(not segment_outside_exclusion(
                        positions[0], positions[1], masks[basin['source_id']])
                        for basin in qualified):
                    continue
            else:
                if any(np.any(np.linalg.norm(positions - b['center_xy'], axis=1)
                              <= b['region_radius_m']) for b in qualified):
                    continue
            segments = np.diff(positions, axis=0)
            squared_lengths = np.sum(segments * segments, axis=1)
            crosses_region = False
            for basin in qualified:
                if enclosure:
                    break  # Exact mask segment exclusion was checked above.
                toward_center = np.asarray(basin['center_xy']) - positions[:-1]
                projection = np.divide(
                    np.sum(toward_center * segments, axis=1), squared_lengths,
                    out=np.zeros(len(segments)), where=squared_lengths > 0,
                )
                closest = positions[:-1] + np.clip(projection, 0.0, 1.0)[:, None] * segments
                if np.any(np.linalg.norm(closest - basin['center_xy'], axis=1)
                          <= basin['region_radius_m']):
                    crosses_region = True
                    break
            if crosses_region:
                continue
            if not enclosure:
                net = float(np.linalg.norm(positions[-1] - positions[0]))
                path = float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum())
            if net >= 0.12 and path > 0 and net / path >= 0.80:
                interval = [target if enclosure else window[0]['stamp_ns'],
                            sample['stamp_ns']]
                if negative and interval[0] <= negative[-1][1]:
                    negative[-1][1] = interval[1]
                else:
                    negative.append(interval)
        labels.extend({'kind': 'negative_directed_progress', 'start_ns': a,
                       'end_ns': b, 'duration_sec': (b - a) / 1e9}
                      for a, b in negative)
    return sorted(labels, key=lambda item: (item['start_ns'], item['kind']))


def _v2_m1a_contract(contract_path):
    """Load the explicit amendment; a markdown v1 contract retains v1 rules."""
    if Path(contract_path).suffix != '.json':
        return None
    contract = json.loads(Path(contract_path).read_text())
    if (contract.get('version') != 'm1a-enclosure-v1'
            or contract.get('status') != 'frozen'):
        raise ValueError('unknown or unfrozen replay contract')
    if _v2_file_hash(contract['plan_path']) != contract['plan_sha256']:
        raise ValueError('M1a frozen plan changed')
    expected_grid = {'window_seconds': [3.0, 6.0, 9.0],
                     'epsilon_m': [0.24, 0.30, 0.36, 0.48],
                     'max_radius_m': [0.25, 0.50, 0.75]}
    if contract.get('calibration_grid') != expected_grid:
        raise ValueError('M1a version has an unreviewed calibration grid')
    required_temporal = {
        'maximum_source_gap_sec': 0.5, 'synchronization_tolerance_sec': 0.05,
        'positive_residence_sec': 12, 'common_positive_support_sec': 54,
        'positive_opportunities_per_search_epoch': 1,
        'first_opportunity_censors_epoch': True, 'negative_progress_sec': 6,
        'negative_net_distance_m': 0.12, 'negative_net_to_path_ratio': 0.8,
        'all_source_enclosures_required_for_negative': True,
        'negative_start_boundary': 'interpolate_exact_end_minus_six_seconds',
    }
    if any(contract.get('temporal', {}).get(k) != v
           for k, v in required_temporal.items()):
        raise ValueError('M1a temporal semantics differ from the reviewed version')
    required_acceptance = {
        'all_synthetic_positives': True, 'zero_synthetic_negatives': True,
        'all_uncensored_retained_positives': True,
        'nonempty_retained_positive_denominator': True,
        'zero_retained_negative_events': True,
        'selection_order': ['median_positive_detector_delay_sec', 'max_radius_m',
                            'epsilon_m', 'window_seconds'],
        'unknown_events_are_true_positives': False,
    }
    if contract.get('acceptance') != required_acceptance:
        raise ValueError('M1a acceptance cannot change within this version')
    return contract


def _v2_verify_m1a_prior(contract, inventory_path, inventory):
    """Verify unchanged populations before any geometry/detector evaluation."""
    if _v2_file_hash(inventory_path) != contract['inventory_sha256']:
        raise ValueError('M1a frozen inventory changed')
    development = [r for r in inventory['runs']
                   if r['partition'] != 'retrospective_holdout']
    holdout = [r for r in inventory['runs']
               if r['partition'] == 'retrospective_holdout']
    if (sorted(r['seed'] for r in development) != contract['development_seeds']
            or sorted(r['seed'] for r in holdout) != contract['holdout_seeds']
            or len(development) != 8 or len(holdout) != 13):
        raise ValueError('M1a development/holdout partition changed')
    if _v2_file_hash(contract['prior_labels_path']) != contract['prior_labels_sha256']:
        raise ValueError('M1a prior label manifest changed')
    prior = json.loads(Path(contract['prior_labels_path']).read_text())
    if (prior['inventory_sha256'] != contract['inventory_sha256']
            or prior['synthetic_inputs_path'] != contract['synthetic_inputs_path']
            or prior['synthetic_inputs_sha256'] != contract['synthetic_inputs_sha256']
            or _v2_file_hash(contract['synthetic_inputs_path'])
            != contract['synthetic_inputs_sha256']):
        raise ValueError('M1a immutable synthetic or input provenance changed')
    synthetic = json.loads(Path(contract['synthetic_inputs_path']).read_text())
    if len(synthetic) != contract['synthetic_case_count'] or len(synthetic) != 79:
        raise ValueError('M1a synthetic population changed')
    if (sorted((r['seed'], r['run_id']) for r in prior['runs'])
            != sorted((r['seed'], r['run_id']) for r in development)):
        raise ValueError('M1a prior traces do not match the frozen eight inputs')
    for run in prior['runs']:
        if _v2_file_hash(run['input_trace_path']) != run['input_trace_sha256']:
            raise ValueError('M1a immutable qualified input trace changed')
    return prior


def _v2_verify_inventory_inputs(row):
    """Verify bag/config/geometry provenance before immutable trace reuse."""
    for bag in row['bag_files']:
        if _v2_file_hash(bag['path']) != bag['sha256']:
            raise ValueError(f'frozen bag changed: {bag["path"]}')
    input_names = {'metadata.yaml', 'resolved_topics.yaml',
                   'resolved_parameters.yaml', 'resolved_scenario.yaml',
                   'scenario_definition.yaml'}
    for artifact in row['artifacts']:
        if Path(artifact['path']).name in input_names:
            if _v2_file_hash(artifact['path']) != artifact['sha256']:
                raise ValueError(f'frozen input artifact changed: {artifact["path"]}')
    for config in row['parameter_file_provenance']:
        if (_v2_file_hash(config['path']) != config['recorded_blob_sha256']):
            raise ValueError('recorded configuration must be reconstructed')
    # Verify the historical mounting/configuration rather than inferring
    # parity from a mutable path or an old approximate topology result.
    import subprocess
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    repository = next(parent for parent in Path(__file__).resolve().parents
                      if (parent / 'AGENTS.md').is_file()
                      and (parent / 'ros2_ws').is_dir())
    geometry_provenance = []
    for path in (truth.SENSOR_GEOMETRY_PATH, truth.SENSOR_TRANSFORM_CONFIG_PATH):
        path = Path(path).resolve()
        relative = path.relative_to(repository)
        blob = subprocess.run(
            ['git', 'show', f'{row["recorded_git"]["commit"]}:{relative}'],
            cwd=repository, capture_output=True, timeout=10, check=True,
        ).stdout
        recorded_hash = hashlib.sha256(blob).hexdigest()
        if _v2_file_hash(path) != recorded_hash:
            raise ValueError('recorded sensor geometry must be reconstructed')
        geometry_provenance.append({'path': str(path), 'recorded_sha256': recorded_hash})
    return geometry_provenance


def _v2_enclosure_geometry_task(task):
    """One independent recorded geometry; the caller bounds the worker count."""
    from . import v2_enclosure
    from ros_esc.scenario_runner import aggregate_field_truth as truth

    scenario = task['scenario']
    model, _ = truth._model(scenario['sources'], task['model_path'],
                            truth.sensor_geometry_binding())
    basins = []
    for source in scenario['sources']:
        receipt_directory = Path(task['receipt_directory']) / f'source_{len(basins) + 1}'
        basin = v2_enclosure.qualify_enclosure(
            source, scenario['sources'], scenario['bounds_m'],
            evaluate_raw_cost=lambda x, y, angle: truth.evaluate_raw_cost(model, x, y, angle),
            contract=task['contract'], receipt_directory=receipt_directory,
            provenance=task['provenance'],
        )
        basins.append(basin)
        print(json.dumps({'source_receipt_directory': str(receipt_directory),
                          'source_id': source['id'], 'qualified': basin['qualified'],
                          'reason': basin.get('reason')}), flush=True)
    geometry = {'method': 'operational_enclosure_v1', 'basins': basins,
                'provenance': task['provenance']}
    _v2_write_json(task['geometry_path'], geometry)
    return task['key'], geometry


def _v2_m1a_geometry_tasks(inventory, verified, contract, output, owners, contract_hash):
    """Construct deterministic immutable group identities without evaluating cost."""
    tasks = {}
    for row in inventory['runs']:
        if row['partition'] == 'retrospective_holdout':
            continue
        scenario = load_yaml(Path(row['run_directory']) / 'resolved_scenario.yaml')
        geometry_provenance = verified[row['run_id']]
        key = json.dumps([scenario['sources'], scenario['bounds_m'],
                          row['parameter_file_provenance'][0]['recorded_blob_sha256'],
                          geometry_provenance], sort_keys=True)
        if key in tasks:
            continue
        model_path = row['parameter_file_provenance'][0]['path']
        tasks[key] = {
            'key': key, 'scenario': scenario, 'model_path': model_path,
            'contract': contract,
            'receipt_directory': str(output / f'geometry_{len(tasks) + 1}_sources'),
            'geometry_path': str(output / f'geometry_{len(tasks) + 1}.json'),
            'provenance': {'contract_sha256': contract_hash, 'owners': owners,
                           'model_config_path': str(model_path),
                           'model_config_sha256': _v2_file_hash(model_path),
                           'recorded_geometry_provenance': geometry_provenance},
        }
    if (len(tasks) > contract['geometry']['maximum_geometry_groups']
            or sum(len(task['scenario']['sources']) for task in tasks.values())
            > contract['geometry']['maximum_source_enclosures']):
        raise ValueError('M1a finite geometry population cap exceeded')
    return tasks


def _v2_prepare_m1a_geometries(inventory, verified, contract, output, owners, contract_hash):
    """Prepare at most three groups before submitting at most three processes."""
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing

    tasks = _v2_m1a_geometry_tasks(inventory, verified, contract, output, owners, contract_hash)
    _v2_write_json(output / 'geometry_dispatch.json', {
        'maximum_workers': min(3, len(tasks)), 'ordered_tasks': list(tasks.values()),
        'global_timeout_sec': contract['execution']['label_timeout_sec'],
        'automatic_retry': False,
    })
    if not tasks:
        return {}
    # This simulation workstation is Linux. fork allows bounded command-line
    # here-doc invocation; workers have no ROS node or detector to inherit.
    with ProcessPoolExecutor(max_workers=min(3, len(tasks)),
                             mp_context=multiprocessing.get_context('fork')) as executor:
        return dict(executor.map(_v2_enclosure_geometry_task, tasks.values()))


def _v2_recover_m1a_geometries(
        manifest_path, expected_hash, inventory, verified, contract, owners,
        contract_hash, prior, output):
    """Reuse complete geometry with its original numerical ownership intact."""
    import ast
    from . import v2_enclosure

    if not expected_hash or _v2_file_hash(manifest_path) != expected_hash:
        raise ValueError('recovery manifest does not match the explicit frozen hash')
    recovery = json.loads(Path(manifest_path).read_text())
    if (recovery.get('version') != 'm1a-technical-recovery-v1'
            or recovery.get('original_exit_code') != 124
            or recovery.get('original_timeout_sec') != 600
            or recovery.get('original_complete_labels') is not False
            or recovery.get('contract_sha256') != contract_hash
            or recovery.get('inventory_sha256') != contract['inventory_sha256']):
        raise ValueError('recovery identity/scientific contract mismatch')
    old_output = Path(recovery['original_attempt_path']).resolve()
    if (old_output / 'labels.json').exists():
        raise ValueError('recovery cannot reinterpret a complete original label attempt')
    snapshot_path = Path(recovery['original_analyzer_snapshot_path'])
    if (_v2_file_hash(snapshot_path) != recovery['original_analyzer_snapshot_sha256']
            or recovery['original_analyzer_snapshot_sha256']
            != recovery['original_analyzer_sha256']
            or Path(recovery['original_analyzer_path']).resolve() != Path(__file__).resolve()):
        raise ValueError('original analyzer snapshot identity mismatch')
    def geometry_task_body(source):
        matches = [node for node in ast.parse(source).body
                   if isinstance(node, ast.FunctionDef)
                   and node.name == '_v2_enclosure_geometry_task']
        if len(matches) != 1:
            raise ValueError('geometry task has no unique retained implementation')
        return ast.get_source_segment(source, matches[0])
    original_body = geometry_task_body(snapshot_path.read_text())
    if original_body != geometry_task_body(Path(__file__).read_text()):
        raise ValueError('geometry task changed; numerical receipts cannot be reused')
    old_owners = {item['path']: item['sha256'] for item in recovery['old_owners']}
    new_owners = {item['path']: item['sha256'] for item in owners}
    if set(old_owners) != set(new_owners):
        raise ValueError('recovery numerical owner population changed')
    for path, value in old_owners.items():
        if Path(path).resolve() == Path(__file__).resolve():
            if value != recovery['original_analyzer_sha256']:
                raise ValueError('original analyzer ownership mismatch')
        elif value != new_owners[path] or _v2_file_hash(path) != value:
            raise ValueError('recovery requires unchanged numerical owners')
    input_fields = ('seed', 'run_id', 'input_trace_path', 'input_trace_sha256', 'bag_files')
    inputs = [{key: run[key] for key in input_fields} for run in prior['runs']]
    if recovery['input_traces'] != inputs:
        raise ValueError('recovery immutable input population changed')

    # Verify every retained point, source, group and dispatch receipt before
    # consuming any mask. Existing files are read only, never overwritten.
    receipts = {}
    for entry in recovery['receipts']:
        path = Path(entry['path']).resolve()
        if not path.is_relative_to(old_output) or str(path) in receipts:
            raise ValueError('duplicate or unbound recovery receipt')
        if _v2_file_hash(path) != entry['sha256']:
            raise ValueError(f'changed recovery receipt: {path}')
        receipts[str(path)] = entry
    consumed = set()
    def read_receipt(path):
        name = str(Path(path).resolve())
        if name not in receipts:
            raise ValueError('recovery omitted a required numerical receipt')
        consumed.add(name)
        return json.loads(Path(name).read_text())
    started = read_receipt(old_output / 'started.json')
    if (started['owners'] != recovery['old_owners']
            or started['locked_contract'] != contract
            or started['contract_sha256'] != contract_hash
            or started['inventory_sha256'] != contract['inventory_sha256']
            or started['immutable_input_traces'] != inputs
            or started['verified_geometry_provenance'] != verified):
        raise ValueError('original attempt provenance does not match recovery')
    dispatch = read_receipt(old_output / 'geometry_dispatch.json')
    tasks = _v2_m1a_geometry_tasks(
        inventory, verified, contract, old_output, recovery['old_owners'], contract_hash)
    if dispatch['ordered_tasks'] != list(tasks.values()):
        raise ValueError('recovery geometry group/source/configuration bindings changed')
    geometries = {}
    point_count = 0
    for key, task in tasks.items():
        geometry = read_receipt(task['geometry_path'])
        if (geometry.get('method') != 'operational_enclosure_v1'
                or geometry['provenance'] != task['provenance']
                or len(geometry['basins']) != len(task['scenario']['sources'])):
            raise ValueError('recovery group geometry provenance is incomplete')
        for index, (source, basin) in enumerate(zip(task['scenario']['sources'], geometry['basins']), 1):
            source_dir = Path(task['receipt_directory']) / f'source_{index}'
            source_started = read_receipt(source_dir / 'started.json')
            source_geometry = read_receipt(source_dir / 'geometry.json')
            identity = source_started['enclosure_identity_sha256']
            if (source_started['source'] != source
                    or source_started['sources'] != task['scenario']['sources']
                    or source_started['bounds_m'] != task['scenario']['bounds_m']
                    or source_started['provenance'] != task['provenance']
                    or source_started['contract'] != contract
                    or source_started['helper_sha256'] != _v2_file_hash(v2_enclosure.__file__)
                    or source_geometry != basin or not basin['qualified']
                    or basin.get('reason') is not None
                    or basin['source_id'] != source['id']
                    or basin['enclosure_identity_sha256'] != identity
                    or basin['completed_location_count'] != len(basin['point_receipts'])
                    or not basin['point_receipts']):
                raise ValueError('recovery requires complete qualified source geometry')
            for point in basin['point_receipts']:
                entry = receipts.get(str(Path(point['path']).resolve()))
                if entry is None or entry['sha256'] != point['sha256']:
                    raise ValueError('source geometry does not bind its point receipts')
                value = read_receipt(point['path'])
                if (value['enclosure_identity_sha256'] != identity
                        or not value['qualified']
                        or value['canonical_contract_sha256']
                        != basin['canonical_contract_sha256']):
                    raise ValueError('point belongs to another or unqualified enclosure')
                point_count += 1
        geometries[key] = geometry
    if consumed != set(receipts):
        raise ValueError('recovery contains unbound receipts outside completed geometries')
    reuse = {
        'version': 'm1a-technical-recovery-v1',
        'recovery_manifest_path': str(Path(manifest_path).resolve()),
        'recovery_manifest_sha256': expected_hash,
        'original_attempt_path': str(old_output),
        'original_analyzer_snapshot_path': str(snapshot_path),
        'original_analyzer_sha256': recovery['original_analyzer_sha256'],
        'new_label_owner_sha256': _v2_file_hash(__file__),
        'unchanged_geometry_task_sha256': hashlib.sha256(original_body.encode()).hexdigest(),
        'original_numerical_owners': recovery['old_owners'],
        'verified_receipt_count': len(receipts), 'reused_point_count': point_count,
        'reused_geometry_count': len(geometries), 'numerical_evaluations_performed': 0,
        'group_receipts': {key: receipts[task['geometry_path']] for key, task in tasks.items()},
    }
    _v2_write_json(output / 'geometry_reuse.json', reuse)
    return geometries, reuse


def _v2_verify_recovery_freshness(reuse):
    """Recheck the complete preserved numerical chain before detector import."""
    manifest_path = Path(reuse['recovery_manifest_path'])
    if _v2_file_hash(manifest_path) != reuse['recovery_manifest_sha256']:
        raise ValueError('frozen numerical recovery manifest changed')
    manifest = json.loads(manifest_path.read_text())
    if (manifest['original_analyzer_snapshot_path'] != reuse['original_analyzer_snapshot_path']
            or manifest['original_analyzer_snapshot_sha256'] != reuse['original_analyzer_sha256']
            or _v2_file_hash(manifest['original_analyzer_snapshot_path'])
            != reuse['original_analyzer_sha256']):
        raise ValueError('preserved numerical analyzer snapshot changed')
    for receipt in manifest['receipts']:
        if _v2_file_hash(receipt['path']) != receipt['sha256']:
            raise ValueError('preserved numerical recovery receipt changed')


def freeze_v2_replay_labels(inventory_path, contract_path, output_directory, *,
                            recovery_manifest_path=None, recovery_manifest_sha256=None):
    """Freeze labels and input traces before loading any detector implementation."""
    inventory = json.loads(Path(inventory_path).read_text())
    contract = _v2_m1a_contract(contract_path)
    if (bool(recovery_manifest_path) != bool(recovery_manifest_sha256)
            or recovery_manifest_path and not contract):
        raise ValueError('recovery requires an M1a contract and explicit manifest hash')
    initial_contract_hash = _v2_file_hash(contract_path)
    output = Path(output_directory).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    prior = _v2_verify_m1a_prior(contract, inventory_path, inventory) if contract else None
    prior_by_id = {r['run_id']: r for r in prior['runs']} if prior else {}
    verified = {}
    owners = []
    if contract:
        from . import v2_enclosure
        from . import bag_reader
        from ros_esc.scenario_runner import aggregate_field_truth as truth
        import scipy
        owners = [{'path': str(Path(path).resolve()), 'sha256': _v2_file_hash(path)}
                  for path in (__file__, v2_enclosure.__file__, bag_reader.__file__,
                               truth.__file__, truth.cost_function_objects.__file__)]
        for row in inventory['runs']:
            if row['partition'] != 'retrospective_holdout':
                verified[row['run_id']] = _v2_verify_inventory_inputs(row)
        _v2_write_json(output / 'started.json', {
            'version': contract['version'], 'status': 'incomplete',
            'contract_path': str(Path(contract_path).resolve()),
            'contract_sha256': initial_contract_hash, 'locked_contract': contract,
            'inventory_sha256': _v2_file_hash(inventory_path), 'owners': owners,
            'software_versions': {'python': sys.version, 'numpy': np.__version__,
                                  'scipy': scipy.__version__},
            'prior_labels_sha256': contract['prior_labels_sha256'],
            'immutable_input_traces': [{k: r[k] for k in (
                'seed', 'run_id', 'input_trace_path', 'input_trace_sha256', 'bag_files')}
                for r in prior['runs']],
            'verified_geometry_provenance': verified,
            'synthetic_inputs_path': contract['synthetic_inputs_path'],
            'synthetic_inputs_sha256': contract['synthetic_inputs_sha256'],
            'detector_imported_for_labeling': False,
        })
    runs = []
    geometry_cache = {}
    recovery_receipt = None
    if recovery_manifest_path:
        prepared_geometries, recovery_receipt = _v2_recover_m1a_geometries(
            recovery_manifest_path, recovery_manifest_sha256, inventory, verified,
            contract, owners, initial_contract_hash, prior, output)
    else:
        prepared_geometries = (_v2_prepare_m1a_geometries(
            inventory, verified, contract, output, owners, initial_contract_hash)
            if contract else {})
    for row in inventory['runs']:
        if row['partition'] == 'retrospective_holdout':
            continue
        geometry_provenance = (verified[row['run_id']] if contract
                               else _v2_verify_inventory_inputs(row))
        scenario = load_yaml(Path(row['run_directory']) / 'resolved_scenario.yaml')
        geometry_key = json.dumps(
            [scenario['sources'], scenario['bounds_m'],
             row['parameter_file_provenance'][0]['recorded_blob_sha256'],
             geometry_provenance], sort_keys=True,
        )
        if geometry_key not in geometry_cache:
            model_path = row['parameter_file_provenance'][0]['path']
            if contract:
                geometry_cache[geometry_key] = prepared_geometries[geometry_key]
            else:
                geometry_cache[geometry_key] = qualify_v2_cycle_basins(
                    scenario, model_config_path=model_path)
            geometry_path = (Path(recovery_receipt['group_receipts'][geometry_key]['path'])
                             if recovery_receipt else output / f'geometry_{len(geometry_cache)}.json')
            if not contract:
                _v2_write_json(geometry_path, geometry_cache[geometry_key])
            for basin in geometry_cache[geometry_key]['basins']:
                print(json.dumps({'geometry_path': str(geometry_path), **{
                    key: basin[key] for key in (
                        'source_id', 'center_xy', 'qualified',
                        'agreeing_successful_starts', 'interior',
                        'ring_inside_bounds', 'ring_depth_raw_cost',
                        'quadrature_72_to_144_difference',
                    ) if key in basin}}), flush=True)
        geometry = geometry_cache[geometry_key]
        if prior:
            trace_path = Path(prior_by_id[row['run_id']]['input_trace_path'])
            trace = json.loads(trace_path.read_text())
            samples, qualification = trace['samples'], trace['qualification']
        else:
            bag_data = read_run_bag(row['run_directory'], aliases=V2_LABEL_INPUT_ALIASES)
            samples, qualification = qualify_v2_replay_inputs(bag_data)
            trace_path = output / f'{row["seed"]}_inputs.json'
            _v2_write_json(trace_path, {'samples': samples, 'qualification': qualification})
        intervals = label_v2_basin_intervals(samples, geometry)
        runs.append({
            'seed': row['seed'], 'run_id': row['run_id'],
            'run_directory': row['run_directory'], 'bag_files': row['bag_files'],
            'input_trace_path': str(trace_path),
            'input_trace_sha256': _v2_file_hash(trace_path),
            'qualification': qualification, 'geometry': geometry,
            'recorded_geometry_provenance': geometry_provenance,
            'labels': intervals,
        })
        print(json.dumps({'frozen_input_seed': row['seed'],
                          'label_count': len(intervals),
                          'qualified_basins': sum(b['qualified'] for b in geometry['basins'])}),
              flush=True)
    if contract:
        synthetic_path = Path(contract['synthetic_inputs_path'])
        _v2_verify_m1a_prior(contract, inventory_path, inventory)
        _v2_m1a_contract(contract_path)
        if _v2_file_hash(contract_path) != initial_contract_hash:
            raise ValueError('M1a contract changed during label freeze')
        for owner in owners:
            if _v2_file_hash(owner['path']) != owner['sha256']:
                raise ValueError('M1a owner changed during label freeze')
        if recovery_manifest_path and _v2_file_hash(recovery_manifest_path) != recovery_manifest_sha256:
            raise ValueError('recovery manifest changed during label freeze')
        if recovery_receipt:
            _v2_verify_recovery_freshness(recovery_receipt)
    else:
        synthetic_path = output / 'synthetic_inputs.json'
        synthetic = _v2_synthetic_traces()
        _v2_write_json(synthetic_path, synthetic)
    document = {
        'schema_version': 1, 'version': 'm1a-labels-v1' if contract else 'm1-labels-v1',
        'attempt_id': output.name,
        'inventory_path': str(Path(inventory_path).resolve()),
        'inventory_sha256': _v2_file_hash(inventory_path),
        'contract_path': str(Path(contract_path).resolve()),
        'contract_sha256': _v2_file_hash(contract_path),
        'analyzer_source_sha256': _v2_file_hash(__file__),
        'detector_imported_for_labeling': False,
        'spatial_output_topics_read': [], 'runs': runs,
        'synthetic_inputs_path': str(synthetic_path),
        'synthetic_inputs_sha256': _v2_file_hash(synthetic_path),
    }
    if contract:
        document.update({'locked_contract': contract, 'owner_receipts': owners,
                         'prior_labels_path': contract['prior_labels_path'],
                         'prior_labels_sha256': contract['prior_labels_sha256'],
                         'fixed_grid': contract['calibration_grid'],
                         'attempt_receipts': [
                             {'path': str(path), 'sha256': _v2_file_hash(path)}
                             for path in [output / 'started.json',
                                          output / 'geometry_dispatch.json',
                                          output / 'geometry_reuse.json']
                             + sorted(output.glob('geometry_[0-9]*.json')) if path.is_file()]})
        if recovery_receipt:
            document['numerical_geometry_recovery'] = recovery_receipt
    _v2_write_json(output / 'labels.json', document)
    return document


def _v2_synthetic_traces():
    """Generate the predetermined analytic positional-settling population."""
    traces = []

    def add(name, times, xy, positive):
        traces.append({
            'trace_id': name, 'label': 'positive' if positive else 'negative',
            'semantic': 'positional_settling_only',
            'times_ns': np.rint(times * 1e9).astype(np.int64).tolist(),
            'positions_xy': np.asarray(xy).tolist(),
        })

    for step in (0.05, 0.10):
        times = np.arange(round(90.0 / step) + 1, dtype=float) * step
        add(f'stationary_dt{step}', times, np.zeros((len(times), 2)), True)
        for period in (3.0, 4.5, 6.0):
            for phase in (0.0, 0.7):
                angles = 2.0 * math.pi * times / period + phase
                circle = np.column_stack((np.cos(angles), np.sin(angles)))
                add(f'circle_p{period}_phase{phase}_dt{step}',
                    times, 0.15 * circle, True)
                add(f'fore_aft_p{period}_phase{phase}_dt{step}', times,
                    np.column_stack((0.15 * np.sin(angles), np.zeros(len(times)))), True)
                for radius in (1.0, 1.5):
                    add(f'large_loop_r{radius}_p{period}_phase{phase}_dt{step}',
                        times, radius * circle, False)
                for speed in (0.02, 0.05):
                    drifting = 0.15 * circle + np.column_stack(
                        (speed * times, np.zeros(len(times))))
                    add(f'drifting_circle_v{speed}_p{period}_phase{phase}_dt{step}',
                        times, drifting, False)
        for speed in (0.02, 0.05):
            add(f'straight_v{speed}_dt{step}', times,
                np.column_stack((speed * times, np.zeros(len(times)))), False)
    times = np.concatenate((np.arange(0.0, 30.0, 0.05),
                            np.arange(30.0, 60.0, 0.10),
                            np.arange(60.0, 90.0, 0.075), [90.0]))
    angle = 2.0 * math.pi * times / 4.5 + 0.7
    add('changing_sample_rate_circle', times,
        0.15 * np.column_stack((np.cos(angle), np.sin(angle))), True)
    return traces


def _v2_search_eligibility(samples, bag_data):
    """Apply causal recorded SEARCH/readiness masks after spatial label freeze."""
    from bisect import bisect_right
    states = records_for_alias(bag_data, 'algorithm_state')
    clocks = records_for_alias(bag_data, 'clock')
    readiness = records_for_alias(bag_data, 'recording_ready')
    clock_stamps = [r.bag_timestamp_ns for r in clocks]
    ready_stamps = [r.bag_timestamp_ns for r in readiness]

    def latest(records, stamps, receipt_ns):
        index = bisect_right(stamps, receipt_ns) - 1
        return records[index] if index >= 0 else None

    previous_identity = None
    previous_valid_state = None
    previous_source_stamp = None
    epoch = 0
    epoch_start = None
    entries = []
    invalidations = []
    previous_receipt = None
    for current in states:
        message = current.message
        identity = message.run_id if message.run_id_valid else None
        clock = latest(clocks, clock_stamps, current.bag_timestamp_ns)
        now_ns = stamp_nanoseconds(clock.message.clock) if clock else None
        stamp = current.ros_timestamp_ns
        valid = (
            bool(identity) and message.state_valid and 1 <= message.state <= 8
            and message.algorithm_profile == 'robust_gaussian_v1'
            and stamp is not None and stamp >= 0 and now_ns is not None
            and -50_000_000 <= now_ns - stamp <= 500_000_000
            and (identity != previous_identity or previous_source_stamp is None
                 or stamp >= previous_source_stamp)
        )
        search = bool(valid and message.state == AlgorithmState.STATE_SEARCH)
        if valid:
            if search and (identity != previous_identity
                           or previous_valid_state != AlgorithmState.STATE_SEARCH):
                epoch += 1
                elapsed_valid = bool(getattr(message, 'state_elapsed_valid', False))
                elapsed = getattr(message, 'state_elapsed_sec', 0.0)
                epoch_start = (stamp - round(float(elapsed) * 1e9)
                               if elapsed_valid and _finite(elapsed) and elapsed >= 0
                               else now_ns)
            previous_valid_state = message.state
            previous_identity = identity
            previous_source_stamp = stamp
        else:
            invalidations.append(current.bag_timestamp_ns)
        if (previous_receipt is not None
                and current.bag_timestamp_ns - previous_receipt > 500_000_000):
            invalidations.append(previous_receipt + 500_000_000)
        previous_receipt = current.bag_timestamp_ns
        # Invalid observations disarm availability without rewriting the last
        # valid state or rearming the same SEARCH epoch on restoration.
        entries.append((current, str(epoch) if search else None, epoch_start))
    previous_receipt = None
    for ready in readiness:
        if not bool(ready.message.data):
            invalidations.append(ready.bag_timestamp_ns)
        if (previous_receipt is not None
                and ready.bag_timestamp_ns - previous_receipt > 500_000_000):
            invalidations.append(previous_receipt + 500_000_000)
        previous_receipt = ready.bag_timestamp_ns
    invalidations.sort()
    stamps = [state.bag_timestamp_ns for state, unused_epoch, unused_start in entries]
    masked = []
    for sample in samples:
        at = bisect_right(stamps, sample['bag_timestamp_ns']) - 1
        current, current_epoch, current_start = entries[at] if at >= 0 else (None, None, None)
        clock = latest(clocks, clock_stamps, sample['bag_timestamp_ns'])
        now_ns = max(sample['stamp_ns'] or 0,
                     stamp_nanoseconds(clock.message.clock) if clock else 0)
        ready = latest(readiness, ready_stamps, sample['bag_timestamp_ns'])
        state_fresh = (
            current is not None and current.ros_timestamp_ns is not None
            and sample['stamp_ns'] is not None
            and -50_000_000 <= now_ns - current.ros_timestamp_ns <= 500_000_000
            and sample['bag_timestamp_ns'] - current.bag_timestamp_ns <= 500_000_000
        )
        ready_fresh = (ready is not None and bool(ready.message.data)
                       and sample['bag_timestamp_ns'] - ready.bag_timestamp_ns <= 500_000_000)
        pose_fresh = (sample['stamp_ns'] is not None and current_start is not None
                      and sample['stamp_ns'] >= current_start
                      and -50_000_000 <= now_ns - sample['stamp_ns'] <= 500_000_000)
        eligible = bool(sample['readiness_eligible'] and current_epoch is not None
                        and state_fresh and ready_fresh and pose_fresh)
        generation = bisect_right(invalidations, sample['bag_timestamp_ns'])
        masked.append({**sample, 'search_epoch': current_epoch if eligible else None,
                       'search_epoch_start_ns': current_start,
                       'history_generation': generation})
    return masked


def _v2_common_positive_support(samples, labels, *, minimum_duration_sec=54.0):
    """Build one opportunity per epoch; historical comparison retains54s."""
    if (isinstance(minimum_duration_sec, bool) or not math.isfinite(minimum_duration_sec)
            or minimum_duration_sec <= 0):
        raise ValueError('positive finite common support duration required')
    opportunities = []
    censored = []
    for label in labels:
        if label['kind'] != 'positive_basin_residence':
            continue
        segments = []
        segment = []
        for sample in samples:
            usable = (
                sample['qualified'] and sample['search_epoch'] is not None
                and label['start_ns'] <= sample['stamp_ns'] <= label['end_ns']
            )
            changed = segment and (
                sample['search_epoch'] != segment[-1]['search_epoch']
                or sample['stamp_ns'] - segment[-1]['stamp_ns'] > 500_000_000
                or sample.get('history_generation', 0) != segment[-1].get('history_generation', 0)
            )
            if not usable or changed:
                if segment:
                    segments.append(segment)
                    segment = []
            if usable:
                segment.append(sample)
        if segment:
            segments.append(segment)
        for segment in segments:
            item = {
                'kind': label['kind'], 'source_id': label['source_id'],
                'truth_start_ns': label['start_ns'],
                'start_ns': segment[0]['stamp_ns'], 'end_ns': segment[-1]['stamp_ns'],
                'search_epoch': segment[0]['search_epoch'],
                'duration_sec': (segment[-1]['stamp_ns'] - segment[0]['stamp_ns']) / 1e9,
            }
            opportunities.append(item)
        if not segments:
            censored.append({**label, 'reason': 'no_eligible_search_support'})
    # The detector can trigger only once per SEARCH. Later basin residence
    # after the first genuine opportunity is counterfactual after potential
    # intervention, even when the first opportunity was short or interrupted.
    supported = []
    observed_epochs = set()
    for item in sorted(opportunities, key=lambda row: (row['truth_start_ns'], row['start_ns'])):
        epoch = item['search_epoch']
        if epoch in observed_epochs:
            censored.append({**item, 'reason': 'later_residence_after_first_opportunity'})
            continue
        observed_epochs.add(epoch)
        if item['duration_sec'] >= minimum_duration_sec:
            supported.append(item)
        else:
            censored.append({**item, 'reason': 'first_opportunity_short_or_interrupted'})
    return supported, censored


def classify_v2_detector_events(events, labels):
    """Keep unlabeled output separate from correct/incorrect labeled events."""
    result = []
    for event in events:
        stamp = event['stamp_ns']
        matches = [label for label in labels
                   if label['start_ns'] <= stamp <= label['end_ns']]
        positive = any(label['kind'] == 'positive_basin_residence' for label in matches)
        negative = any(label['kind'] == 'negative_directed_progress' for label in matches)
        classification = ('ambiguous' if positive and negative else
                          'positive' if positive else 'negative' if negative else 'unknown')
        result.append({**event, 'independent_label': classification})
    return result


def calibrate_v2_detector(frozen_labels_path, output_directory):
    """Evaluate the fixed grid after immutable input-only labels exist.

    The historical goal-event convergence_time metric is untouched. These
    outputs name detector confirmation and independently labeled delay directly.
    """
    labels_path = Path(frozen_labels_path).resolve()
    initial_labels_hash = _v2_file_hash(labels_path)
    frozen = json.loads(labels_path.read_text())
    if _v2_file_hash(frozen['inventory_path']) != frozen['inventory_sha256']:
        raise ValueError('frozen inventory changed')
    inventory = json.loads(Path(frozen['inventory_path']).read_text())
    inventory_by_id = {row['run_id']: row for row in inventory['runs']}
    if _v2_file_hash(frozen['contract_path']) != frozen['contract_sha256']:
        raise ValueError('frozen labeling contract changed')
    contract = _v2_m1a_contract(frozen['contract_path'])
    fixed_grid = contract['calibration_grid'] if contract else V2_CALIBRATION_GRID
    if contract:
        prior = _v2_verify_m1a_prior(contract, frozen['inventory_path'], inventory)
        if (frozen.get('version') != 'm1a-labels-v1'
                or frozen.get('locked_contract') != contract
                or frozen.get('fixed_grid') != fixed_grid):
            raise ValueError('M1a labels do not bind the complete frozen contract')
        def input_identity(run):
            return tuple(run[k] for k in ('seed', 'run_id', 'input_trace_path',
                                           'input_trace_sha256'))
        if (sorted(map(input_identity, frozen['runs']))
                != sorted(map(input_identity, prior['runs']))):
            raise ValueError('M1a calibration changed its frozen eight-input population')
        for receipt in frozen['attempt_receipts']:
            if _v2_file_hash(receipt['path']) != receipt['sha256']:
                raise ValueError('M1a attempt receipt changed before calibration')
        if frozen.get('numerical_geometry_recovery'):
            _v2_verify_recovery_freshness(frozen['numerical_geometry_recovery'])
        for run in frozen['runs']:
            for basin in run['geometry']['basins']:
                for receipt in basin.get('point_receipts', []):
                    if _v2_file_hash(receipt['path']) != receipt['sha256']:
                        raise ValueError('M1a numerical point receipt changed')
        for owner in frozen['owner_receipts']:
            if _v2_file_hash(owner['path']) != owner['sha256']:
                raise ValueError('M1a label owner changed before calibration')
    if (_v2_file_hash(frozen['synthetic_inputs_path'])
            != frozen['synthetic_inputs_sha256']):
        raise ValueError('frozen synthetic inputs changed')
    synthetic = json.loads(Path(frozen['synthetic_inputs_path']).read_text())
    # No detector is imported until an intact frozen spatial-label manifest
    # and its explicit scientific contract have passed provenance checks.
    from ros_esc.convergence_detector_node import centroid_windows as core
    initial_detector_hash = _v2_file_hash(core.__file__)
    retained = []
    for run in frozen['runs']:
        inventory_run = inventory_by_id[run['run_id']]
        for artifact in inventory_run['bag_files'] + inventory_run['artifacts']:
            path = Path(artifact['path'])
            if path.suffix == '.db3' or path.name in ('metadata.yaml', 'resolved_topics.yaml'):
                if _v2_file_hash(path) != artifact['sha256']:
                    raise ValueError(f'frozen mask input changed: {path}')
        if _v2_file_hash(run['input_trace_path']) != run['input_trace_sha256']:
            raise ValueError('frozen input trace changed')
        samples = json.loads(Path(run['input_trace_path']).read_text())['samples']
        state_data = read_run_bag(run['run_directory'], aliases=('algorithm_state', 'clock'))
        samples = _v2_search_eligibility(samples, state_data)
        positive, censored = _v2_common_positive_support(samples, run['labels'])
        retained.append({'seed': run['seed'], 'samples': samples,
                         'labels': run['labels'], 'common_positives': positive,
                         'censored_positives': censored})
    output = Path(output_directory).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    _v2_write_json(output / 'started.json', {
        'frozen_labels_path': str(labels_path),
        'frozen_labels_sha256': _v2_file_hash(labels_path),
        'detector_source_sha256': initial_detector_hash,
        'analyzer_source_sha256': _v2_file_hash(__file__),
        'fixed_grid': fixed_grid,
        'contract_path': frozen['contract_path'],
        'contract_sha256': frozen['contract_sha256'],
    })
    grid = []
    for window in fixed_grid['window_seconds']:
        for epsilon in fixed_grid['epsilon_m']:
            for radius in fixed_grid['max_radius_m']:
                config = core.CentroidConfig(
                    window_seconds=window, epsilon_m=epsilon,
                    max_radius_m=radius, max_gap_seconds=0.50,
                )
                synthetic_results = []
                delays = []
                for trace in synthetic:
                    detector = core.CentroidWindowDetector(config)
                    detector.start_epoch(trace['trace_id'])
                    event = None
                    for stamp, xy in zip(trace['times_ns'], trace['positions_xy']):
                        for value in detector.update(stamp, xy, 'synthetic'):
                            if value.confirmed_event:
                                event = value.stamp_ns
                        if event is not None:
                            break
                    positive = trace['label'] == 'positive'
                    passed = (event is not None) if positive else (event is None)
                    delay = (event - trace['times_ns'][0]) / 1e9 if event is not None else None
                    if positive and delay is not None:
                        delays.append(delay)
                    synthetic_results.append({
                        'trace_id': trace['trace_id'], 'label': trace['label'],
                        'passed': passed, 'detector_event_ns': event,
                        'detector_delay_sec': delay,
                    })
                retained_results = []
                for run in retained:
                    detector = core.CentroidWindowDetector(config)
                    current_epoch = None
                    current_generation = None
                    events = []
                    for sample in run['samples']:
                        epoch = sample['search_epoch']
                        if epoch is None:
                            detector.invalidate('recorded_readiness_or_state_unavailable')
                            continue
                        if epoch != current_epoch:
                            detector.start_epoch(epoch)
                            current_epoch = epoch
                        generation = sample.get('history_generation', 0)
                        if current_generation is not None and generation != current_generation:
                            detector.invalidate('intervening_recorded_authority_loss')
                        current_generation = generation
                        if sample['xy'] is None or sample['stamp_ns'] is None:
                            detector.invalidate('invalid_recorded_pose')
                            continue
                        for value in detector.update(
                                sample['stamp_ns'], sample['xy'], sample['frame_id']):
                            if value.confirmed_event:
                                events.append({
                                    'stamp_ns': value.stamp_ns, 'search_epoch': epoch,
                                    'score_m': value.score_m, 'radius_m': value.radius_m,
                                })
                    events = classify_v2_detector_events(events, run['labels'])
                    positives = []
                    for label in run['common_positives']:
                        matches = [event for event in events
                                   if event['search_epoch'] == label['search_epoch']
                                   and label['start_ns'] <= event['stamp_ns'] <= label['end_ns']]
                        delay = ((matches[0]['stamp_ns'] - label['truth_start_ns']) / 1e9
                                 if matches else None)
                        if delay is not None:
                            delays.append(delay)
                        positives.append({**label, 'detected': bool(matches),
                                          'detector_delay_from_basin_entry_sec': delay})
                    retained_results.append({
                        'seed': run['seed'], 'detector_events': events,
                        'common_positive_results': positives,
                        'censored_positives': run['censored_positives'],
                        'negative_event_count': sum(e['independent_label'] == 'negative' for e in events),
                        'unknown_event_count': sum(e['independent_label'] in ('unknown', 'ambiguous') for e in events),
                    })
                positives_count = sum(len(r['common_positive_results']) for r in retained_results)
                scientific_gate = (
                    all(r['passed'] for r in synthetic_results)
                    and all(p['detected'] for r in retained_results for p in r['common_positive_results'])
                    and not any(r['negative_event_count'] for r in retained_results)
                )
                record = {
                    'window_seconds': window, 'epsilon_m': epsilon, 'max_radius_m': radius,
                    'synthetic_results': synthetic_results, 'retained_results': retained_results,
                    'synthetic_passed_count': sum(r['passed'] for r in synthetic_results),
                    'synthetic_case_count': len(synthetic_results),
                    'retained_common_positive_count': positives_count,
                    'retained_positive_detected_count': sum(p['detected'] for r in retained_results for p in r['common_positive_results']),
                    'retained_negative_event_count': sum(r['negative_event_count'] for r in retained_results),
                    'retained_unknown_event_count': sum(r['unknown_event_count'] for r in retained_results),
                    'median_positive_detector_delay_sec': statistics.median(delays) if delays else None,
                    'behavioral_gate_passed': scientific_gate,
                    'retained_positive_evidence_available': positives_count > 0,
                    'qualified': scientific_gate and positives_count > 0,
                }
                grid.append(record)
                _v2_write_json(output / f'grid_{len(grid):02d}.json', record)
                print(json.dumps({k: record[k] for k in (
                    'window_seconds', 'epsilon_m', 'max_radius_m', 'qualified',
                    'synthetic_passed_count', 'synthetic_case_count',
                    'retained_positive_detected_count', 'retained_common_positive_count',
                    'retained_negative_event_count', 'retained_unknown_event_count',
                )}), flush=True)
    if _v2_file_hash(core.__file__) != initial_detector_hash:
        raise ValueError('detector source changed during fixed calibration')
    if (_v2_file_hash(labels_path) != initial_labels_hash
            or _v2_file_hash(frozen['contract_path']) != frozen['contract_sha256']):
        raise ValueError('frozen labels/contract changed during calibration')
    if contract:
        _v2_m1a_contract(frozen['contract_path'])  # Also rechecks the locked plan.
        for owner in frozen['owner_receipts']:
            if _v2_file_hash(owner['path']) != owner['sha256']:
                raise ValueError('M1a owner changed during calibration')
    passing = [row for row in grid if row['qualified']]
    selected = min(passing, key=lambda row: (
        row['median_positive_detector_delay_sec'], row['max_radius_m'],
        row['epsilon_m'], row['window_seconds'],
    )) if passing else None
    report = {
        'schema_version': 1,
        'version': 'm1a-calibration-v1' if contract else 'm1-calibration-v1',
        'frozen_labels_path': str(labels_path), 'frozen_labels_sha256': _v2_file_hash(labels_path),
        'detector_source_sha256': _v2_file_hash(core.__file__),
        'analyzer_source_sha256': _v2_file_hash(__file__),
        'fixed_grid': fixed_grid, 'grid_results': grid,
        'contract_path': frozen['contract_path'],
        'contract_sha256': frozen['contract_sha256'],
        'retained_eligibility': [{
            'seed': run['seed'],
            'pose_samples': len(run['samples']),
            'eligible_pose_samples': sum(s['search_epoch'] is not None for s in run['samples']),
            'search_epochs': sorted({s['search_epoch'] for s in run['samples'] if s['search_epoch'] is not None}),
            'history_invalidation_generations': max((s.get('history_generation', 0) for s in run['samples']), default=0),
            'spatial_label_count': len(run['labels']),
        } for run in retained],
        'status': 'passed' if selected else 'failed',
        'selected': ({key: selected[key] for key in (
            'window_seconds', 'epsilon_m', 'max_radius_m',
            'median_positive_detector_delay_sec')} if selected else None),
        'limitation': 'Retained trajectory response only; unknown outputs are not proven true positives. No counterfactual motion or broad robustness evidence.',
    }
    _v2_write_json(output / 'calibration.json', report)
    return report


def _v2_direction_yaw(quaternion):
    values = [float(getattr(quaternion, name)) for name in ('x', 'y', 'z', 'w')]
    if (not all(math.isfinite(value) for value in values)
            or abs(sum(value*value for value in values)-1.0) > 1e-3):
        raise ValueError('invalid orientation quaternion')
    return _yaw_from_quaternion(quaternion)


def _v2_direction_index(records, stamp_function, value_function):
    """Preserve received source order; only identical duplicates are idempotent."""
    result = []
    for record in records:
        stamp, value = stamp_function(record), value_function(record)
        if type(stamp) is not int:
            raise ValueError('invalid source timestamp')
        if result and stamp <= result[-1][0]:
            if stamp == result[-1][0] and value == result[-1][2]:
                continue
            raise ValueError('source regression or conflicting duplicate')
        result.append((stamp, record, value))
    return result


def _v2_direction_bracket(index, stamp, *, angle=False):
    from bisect import bisect_left
    at = bisect_left(index, stamp, key=lambda item: item[0])
    if at < len(index) and index[at][0] == stamp:
        return index[at][2], (stamp, stamp)
    if not 0 < at < len(index):
        raise ValueError('source bracket unavailable')
    left, right = index[at-1], index[at]
    if stamp-left[0] > 50_000_000 or right[0]-stamp > 50_000_000:
        raise ValueError('source bracket exceeds50ms')
    fraction = (stamp-left[0])/(right[0]-left[0])
    if angle:
        delta = math.remainder(right[2]-left[2], math.tau)
        if abs(delta) == math.pi:
            raise ValueError('ambiguous angular bracket')
        value = math.remainder(left[2]+fraction*delta, math.tau)
    else:
        if left[2][3] != right[2][3]:
            raise ValueError('pose frame changed in bracket')
        delta = math.remainder(right[2][2]-left[2][2], math.tau)
        if abs(delta) == math.pi:
            raise ValueError('ambiguous yaw bracket')
        value = ((1-fraction)*left[2][0]+fraction*right[2][0],
                 (1-fraction)*left[2][1]+fraction*right[2][1],
                 math.remainder(left[2][2]+fraction*delta, math.tau), left[2][3])
    return value, (left[0], right[0])


def prepare_v2_direction_replay_inputs(bag_data, *, raw_alias='raw_cost_legacy',
                                     pose_alias='pose'):
    """Normalize explicitly approximate retained inputs without reading q outputs.

    The old source publisher did not capture evaluated-transform identity.
    Latest bag arrival is therefore a labeled proxy, never exact M2 provenance.
    """
    from bisect import bisect_right
    keepers = records_for_alias(bag_data, 'timekeeper')
    origins = {float(record.message.start_time) for record in keepers}
    if (len(origins) != 1 or not all(_finite(value) for value in origins)
            or {record.message.mode for record in keepers} != {'sim time'}):
        return [], {'qualified': False, 'reason': 'invalid_timekeeper', 'origin_ns': None}
    origin = round(next(iter(origins))*1e9)
    clock_stamps = [stamp_nanoseconds(record.message.clock)
                    for record in records_for_alias(bag_data, 'clock')]
    if not clock_stamps or any(b < a for a, b in zip(clock_stamps, clock_stamps[1:])):
        return [], {'qualified': False, 'reason': 'missing_or_regressing_clock', 'origin_ns': None}
    def source_stamp(record):
        if not record.source_timestamp_valid or not _finite(record.source_timestamp_sec):
            raise ValueError('invalid legacy source time')
        return origin+round(float(record.source_timestamp_sec)*1e9)
    def pose_value(record):
        pose = record.message.pose.pose
        value = (float(pose.position.x), float(pose.position.y),
                 _v2_direction_yaw(pose.orientation), str(record.message.header.frame_id))
        if not value[3] or not all(_finite(item) for item in value[:3]):
            raise ValueError('invalid pose')
        return value
    def encoder_value(record):
        value = float(record.message.data[0])
        if not math.isfinite(value):
            raise ValueError('invalid encoder phase')
        return value
    try:
        poses = _v2_direction_index(records_for_alias(bag_data, pose_alias),
                                     lambda record: record.ros_timestamp_ns, pose_value)
        encoders = _v2_direction_index(records_for_alias(bag_data, 'encoder'),
                                        source_stamp, encoder_value)
        transforms = _v2_direction_index(
            records_for_alias(bag_data, 'sensor_transform'), source_stamp,
            lambda record: _v2_direction_yaw(record.message.transform_array[0].rotation))
    except (ValueError, TypeError, IndexError, AttributeError) as exc:
        return [], {'qualified': False, 'reason': str(exc), 'origin_ns': None}
    raw = records_for_alias(bag_data, raw_alias)
    first = next((record for record in raw if bag_data.readiness_start_ns is not None
                  and record.bag_timestamp_ns >= bag_data.readiness_start_ns
                  and record.source_timestamp_valid and _finite(record.source_timestamp_sec)), None)
    readiness_origin = source_stamp(first) if first is not None else None
    breakdown = {}
    conflicts = set()
    for record in records_for_alias(bag_data, 'cost_breakdown'):
        key = record.source_timestamp_sec
        if key in breakdown:
            conflicts.add(key)
        breakdown[key] = record
    encoder_receipts = [item[1].bag_timestamp_ns for item in encoders]
    transform_receipts = [item[1].bag_timestamp_ns for item in transforms]
    fills = records_for_alias(bag_data, 'gaussian_fills')
    states = records_for_alias(bag_data, 'algorithm_state')
    state_receipts = [record.bag_timestamp_ns for record in states]
    fill_at = 0
    registry = {}
    previous_source = None
    previous_cost = None
    latest_composition_receipt = -1
    context = 0
    observations = []
    reasons = Counter()
    for record in raw:
        key = record.source_timestamp_sec
        item = {'qualified': False, 'legacy_source_key': key if _finite(key) else None, 'stamp_ns': None,
                'cost_stamp_ns': None, 'invalid_reason': None,
                'timing_quality': 'retained_transform_arrival_proxy',
                'exact_m2_source_provenance': False}
        try:
            cost_stamp = source_stamp(record)
            item['cost_stamp_ns'] = cost_stamp
            cost_record = breakdown.get(key)
            if key in conflicts or cost_record is None:
                raise ValueError('missing_or_duplicate_composition')
            if cost_record.bag_timestamp_ns <= latest_composition_receipt:
                raise ValueError('composition_arrival_proxy_regression')
            latest_composition_receipt = cost_record.bag_timestamp_ns
            message = cost_record.message
            if (not message.weights_valid or not message.augmented_cost_valid
                    or not message.raw_cost_valid or not message.augmented_cost
                    or not record.message.data or not message.raw_cost
                    or float(message.raw_cost[0]) != float(record.message.data[0])):
                raise ValueError('invalid_or_unmatched_composition')
            transform_at = bisect_right(transform_receipts, record.bag_timestamp_ns)-1
            encoder_at = bisect_right(encoder_receipts, cost_record.bag_timestamp_ns)-1
            if transform_at < 0 or encoder_at < 0:
                raise ValueError('causal_transform_or_encoder_unavailable')
            model_stamp, transform_record, world_phase = transforms[transform_at]
            item['stamp_ns'] = model_stamp
            if not 0 <= cost_stamp-model_stamp <= 50_000_000:
                raise ValueError('transform_publication_proxy_skew')
            pose, pose_bracket = _v2_direction_bracket(poses, model_stamp)
            encoder, encoder_bracket = _v2_direction_bracket(encoders, model_stamp, angle=True)
            latest_stamp, _, latest_phase = encoders[encoder_at]
            composition_stamp = cost_record.ros_timestamp_ns
            if composition_stamp is None or not 0 <= composition_stamp-latest_stamp <= 500_000_000:
                raise ValueError('latest_encoder_proxy_stale_or_future')
            cost = float(message.augmented_cost[0])
            weights = [float(message.sensor_weight), float(message.gaussian_weight),
                       float(message.affine_weight)]
            if not all(math.isfinite(value) for value in (cost, *weights)):
                raise ValueError('nonfinite_composition')
            while fill_at < len(fills) and fills[fill_at].bag_timestamp_ns <= cost_record.bag_timestamp_ns:
                fill = fills[fill_at].message
                registry[int(fill.fill_id)] = fill
                fill_at += 1
            terms = []
            for fill_id, fill in sorted(registry.items()):
                if not fill.active or fill.superseded:
                    continue
                if not fill.covariance_valid or fill.frame_id != pose[3]:
                    raise ValueError('invalid_fill_snapshot')
                terms.append({'fill_id': fill_id, 'revision': int(fill.revision),
                              'center': [fill.center_x, fill.center_y], 'amplitude': fill.amplitude,
                              'covariance': [[fill.covariance_xx, fill.covariance_xy],
                                             [fill.covariance_xy, fill.covariance_yy]]})
            objective = {'weights': weights, 'gaussian_fills': terms,
                         'affine_terms': [] if weights[2] == 0.0 else None,
                         'causal_quality': 'recorded_composition_and_fill_arrival_proxy'}
            state_at = bisect_right(state_receipts, cost_record.bag_timestamp_ns)-1
            state_record = states[state_at] if state_at >= 0 else None
            state = state_record.message if state_record else None
            state_current = bool(state is not None and state.state_valid
                                 and state_record.ros_timestamp_ns is not None
                                 and 0 <= composition_stamp-state_record.ros_timestamp_ns <= 500_000_000)
            objective['complete_registry_proxy'] = bool(weights[1] == 0 or (
                state_current and state.active_fill_count_valid and int(state.active_fill_count) == len(terms)))
            blend_allowed = bool(state_current and state.state in (
                AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_VERIFY_EXTREMUM,
                AlgorithmState.STATE_DESIGN_OR_MERGE_FILL))
            objective_law = {name: objective[name] for name in ('weights', 'gaussian_fills', 'affine_terms')}
            objective_id = hashlib.sha256(json.dumps(objective_law, sort_keys=True,
                                                       allow_nan=False).encode()).hexdigest()
            if (previous_source is not None and not 0 < model_stamp-previous_source <= 500_000_000
                    or previous_cost is not None and not 0 < cost_stamp-previous_cost <= 500_000_000):
                raise ValueError('model_input_proxy_duplicate_regression_or_gap')
            item.update(qualified=True, xy=list(pose[:2]), yaw_rad=pose[2], frame_id=pose[3],
                        world_phase_rad=world_phase, projected_phase_rad=math.remainder(world_phase-pose[2], math.tau),
                        encoder_phase_rad=encoder, latest_phase_rad=latest_phase, cost=cost,
                        raw_cost=float(record.message.data[0]), objective=objective,
                        objective_id=objective_id, context_id=context,
                        blend_allowed=blend_allowed,
                        state_name=state.state_name if state_current else None,
                        pose_bracket_ns=list(pose_bracket), encoder_bracket_ns=list(encoder_bracket),
                        transform_bag_receipt_ns=transform_record.bag_timestamp_ns,
                        composition_bag_receipt_ns=cost_record.bag_timestamp_ns,
                        source_publication_minus_model_proxy_ns=cost_stamp-model_stamp,
                        readiness_eligible=record.in_readiness_interval)
            previous_source = model_stamp
            previous_cost = cost_stamp
        except (ValueError, TypeError, IndexError, AttributeError, OverflowError) as exc:
            item['invalid_reason'] = str(exc)
            reasons[str(exc)] += 1
            context += 1
            previous_source = None
            previous_cost = None
        observations.append(item)
    return observations, {'qualified': bool(observations), 'origin_ns': readiness_origin,
                          'timekeeper_origin_ns': origin, 'sample_count': len(observations),
                          'qualified_sample_count': sum(item['qualified'] for item in observations),
                          'invalid_reasons': dict(reasons), 'exact_m2_source_provenance': False,
                          'claim': 'matched_retained_proxy_not_runtime_transport_qualification'}


def _v2_direction_recorded_settings(metadata, launch_xml):
    """Resolve retained explicit launch values and that commit's own defaults."""
    import xml.etree.ElementTree as ET
    argv = metadata.get('target_argv', [])
    if argv[:4] != ['ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml']:
        raise ValueError('unsupported recorded launch owner')
    root = ET.fromstring(launch_xml)
    settings = {item.get('name'): item.get('default') for item in root.findall('arg')}
    overrides = {}
    for argument in argv[4:]:
        if ':=' not in argument:
            raise ValueError('unsupported recorded launch argument')
        name, value = argument.split(':=', 1)
        if name in overrides:
            raise ValueError('duplicate recorded launch argument')
        overrides[name] = value
    settings.update(overrides)
    for name in ('cost_function_config_filepath', 'filter_config_filepath',
                 'sensor_transform_config_filepath', 'algorithm_raw_cost_topic', 'algorithm_pose_topic'):
        value = settings.get(name)
        if not isinstance(value, str) or not value or '$(' in value:
            raise ValueError(f'unresolved recorded launch setting: {name}')
    executions = [item.get('cmd', '') for item in root.iter('executable')]
    if not any('sensor_pose_node' in command and '$(var sensor_transform_config_filepath)' in command
               for command in executions):
        raise ValueError('recorded sensor transform owner is not selected')
    return settings


def _v2_direction_recorded_binding(row, repository):
    """Bind source config to historical launch and captured live robot geometry."""
    import subprocess
    import xml.etree.ElementTree as ET
    from . import v2_direction_reference as reference
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    commit = row['recorded_git']['commit']
    def recorded_blob(path):
        relative = Path(path).resolve().relative_to(repository)
        return subprocess.run(['git', 'show', f'{commit}:{relative}'], cwd=repository,
                              capture_output=True, timeout=10, check=True).stdout
    launch_path = repository / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    launch_blob = recorded_blob(launch_path)
    metadata = load_yaml(Path(row['run_directory']) / 'metadata.yaml')
    settings = _v2_direction_recorded_settings(metadata, launch_blob)
    configs = {str(Path(item['path']).resolve()): item for item in row['parameter_file_provenance']}
    selected = {}
    for name in ('cost_function_config_filepath', 'filter_config_filepath', 'sensor_transform_config_filepath'):
        path = Path(settings[name]).expanduser().resolve()
        blob = recorded_blob(path)
        digest = hashlib.sha256(blob).hexdigest()
        if _v2_file_hash(path) != digest:
            raise ValueError(f'recorded configuration differs: {name}')
        if name != 'sensor_transform_config_filepath':
            receipt = configs.get(str(path))
            if receipt is None or receipt['recorded_blob_sha256'] != digest:
                raise ValueError(f'configuration is absent from frozen recorded parameters: {name}')
        if name == 'filter_config_filepath' and digest != reference.SELECTED_FILTER_SHA256:
            raise ValueError('recorded selected filter differs from stationary dynamics')
        selected[name] = {'path': str(path), 'sha256': digest}
    geometry_path = Path(truth.SENSOR_GEOMETRY_PATH).resolve()
    geometry_blob = recorded_blob(geometry_path)
    if _v2_file_hash(geometry_path) != hashlib.sha256(geometry_blob).hexdigest():
        raise ValueError('recorded URDF differs from reference binding')
    binding = truth.sensor_geometry_binding(selected['sensor_transform_config_filepath']['path'], geometry_path)
    reference.selected_sensor_xy([0, 0], 0, binding)  # Geometry only, no cost evaluation.
    parameters = load_yaml(Path(row['run_directory']) / 'resolved_parameters.yaml')
    descriptions = [_find_parameter(node.get('parameters', {}), 'robot_description')
                    for node in parameters.get('nodes', {}).values()]
    descriptions = [value for value in descriptions if isinstance(value, str) and value]
    if not descriptions:
        raise ValueError('captured live robot_description unavailable')
    expected = {'rotating_frame_joint': ([0., 0., .355], [0., 0., 0.], [0., 0., 1.]),
                'sensor_joint': ([.18, 0., .015], [0., 0., 0.], None)}
    for description in descriptions:
        root = ET.fromstring(description)
        for name, (xyz, rpy, axis) in expected.items():
            joint = root.find(f".//joint[@name='{name}']")
            origin = joint.find('origin') if joint is not None else None
            if origin is None or ([float(v) for v in origin.get('xyz', '').split()] != xyz
                                  or [float(v) for v in origin.get('rpy', '').split()] != rpy):
                raise ValueError('captured live sensor geometry differs from reference')
            if axis is not None:
                axis_element = joint.find('axis')
                if axis_element is None or [float(v) for v in axis_element.get('xyz', '').split()] != axis:
                    raise ValueError('captured live sensor axis differs from reference')
    return {'binding': binding, 'settings': settings, 'selected_configurations': selected,
            'recorded_launch_sha256': hashlib.sha256(launch_blob).hexdigest(),
            'captured_robot_description_hashes': sorted(set(hashlib.sha256(value.encode()).hexdigest()
                                                          for value in descriptions))}


def freeze_v2_direction_references(inventory_path, output_directory):
    """One fixed192-anchor development study with retained provenance limitations.

    Caller must use timeout300s. No actual model/reference output is produced
    until every target identity has been atomically frozen. Never auto-retry.
    """
    from . import v2_direction_reference as reference
    from . import v2_enclosure
    from ros_esc import config_parsing
    from ros_esc.filter_node import rolling_gesc
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from extremum_seeking.filters import base_filters
    inventory = json.loads(Path(inventory_path).read_text())
    if _v2_file_hash(inventory_path) != reference.INVENTORY_SHA256:
        raise ValueError('M2 frozen inventory changed')
    rows = [row for row in inventory['runs'] if row['partition'] != 'retrospective_holdout']
    if sorted(row['seed'] for row in rows) != list(reference.DEVELOPMENT_SEEDS):
        raise ValueError('M2 fixed development population changed')
    repository = next(parent for parent in Path(__file__).resolve().parents
                      if (parent / 'AGENTS.md').is_file() and (parent / 'ros2_ws').is_dir())
    plan = repository / 'docs/codex/gesc_gaussian/v2/m2_reference_plan.md'
    filter_path = repository / ('ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/'
                                'turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json')
    if _v2_file_hash(filter_path) != reference.SELECTED_FILTER_SHA256:
        raise ValueError('M2 selected filter configuration changed')
    filter_config = json.loads(filter_path.read_text())
    owner_paths = [Path(__file__), Path(reference.__file__), Path(truth.__file__),
                   Path(truth.cost_function_objects.__file__), Path(config_parsing.__file__),
                   Path(rolling_gesc.__file__), Path(base_filters.__file__), filter_path, plan]
    owners = [{'path': str(path), 'sha256': _v2_file_hash(path)} for path in owner_paths]
    verified = {row['run_id']: _v2_verify_inventory_inputs(row) for row in rows}
    bindings = {row['run_id']: _v2_direction_recorded_binding(row, repository) for row in rows}
    output = Path(output_directory).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    publish = v2_enclosure.atomic_exclusive_json
    publish(output / 'started.json', {'version': reference.VERSION, 'status': 'incomplete',
             'inventory_sha256': reference.INVENTORY_SHA256, 'owners': owners,
             'verified_geometry': verified, 'fixed_anchor_count': 192,
             'recorded_selected_bindings': bindings,
             'runtime_transport_qualified': False})
    targets, traces = [], {}
    base_aliases = ('raw_cost_legacy', 'pose', 'timekeeper', 'encoder', 'sensor_transform',
                    'cost_breakdown', 'gaussian_fills', 'clock', 'algorithm_state')
    for row in rows:
        resolved = load_yaml(Path(row['run_directory']) / 'resolved_topics.yaml')
        topic_aliases = {item['topic']: item['alias'] for item in resolved['topics']}
        selected = {}
        for parameter in ('algorithm_raw_cost_topic', 'algorithm_pose_topic'):
            topic = bindings[row['run_id']]['settings'][parameter]
            if topic not in topic_aliases:
                raise ValueError(f'selected M2 replay topic is not recorded: {topic}')
            selected[parameter] = topic_aliases[topic]
        aliases = set(base_aliases) | set(selected.values())
        bag = read_run_bag(row['run_directory'], aliases=aliases)
        observations, qualification = prepare_v2_direction_replay_inputs(
            bag, raw_alias=selected['algorithm_raw_cost_topic'], pose_alias=selected['algorithm_pose_topic'])
        qualification['selected_aliases'] = selected
        trace_path = output / f'inputs_{row["seed"]}.json'
        trace_hash = publish(trace_path, {'run_id': row['run_id'], 'seed': row['seed'],
                                         'qualification': qualification, 'observations': observations})
        traces[row['run_id']] = (str(trace_path), trace_hash)
        origin = qualification['origin_ns']
        times = reference.select_reference_targets(origin) if origin is not None else [None]*24
        for number, target in enumerate(times, 1):
            candidate = reference.select_causal_anchor(observations, target)
            targets.append({'run_id': row['run_id'], 'seed': row['seed'], 'number': number,
                            'target_ns': target, 'observation_index': candidate,
                            'input_trace_path': str(trace_path), 'input_trace_sha256': trace_hash})
    publish(output / 'targets.json', targets)
    results = []
    for row in rows:
        trace_path, trace_hash = traces[row['run_id']]
        if _v2_file_hash(trace_path) != trace_hash:
            raise ValueError('frozen M2 input trace changed')
        observations = json.loads(Path(trace_path).read_text())['observations']
        last_index = max((target['observation_index'] for target in targets
                          if target['run_id'] == row['run_id']
                          and target['observation_index'] is not None), default=-1)
        paired = reference.replay_matched_direction(observations[:last_index+1], filter_config)
        publish(output / f'method_outputs_{row["seed"]}.json', paired)
        scenario = load_yaml(Path(row['run_directory']) / 'resolved_scenario.yaml')
        binding = bindings[row['run_id']]['binding']
        model_path = bindings[row['run_id']]['selected_configurations']['cost_function_config_filepath']['path']
        model, _ = truth._model(scenario['sources'], model_path, binding)
        for target in (item for item in targets if item['run_id'] == row['run_id']):
            result = {**target, 'qualified': False, 'informative': False,
                      'reason': 'missing_causal_anchor', 'runtime_transport_qualified': False,
                      'causal_anchor_available': False,
                      'objective_reconstructable': False, 'numerically_qualified': False,
                      'exact_m2_source_provenance': False}
            index = target['observation_index']
            if index is not None:
                observation = observations[index]
                result['causal_anchor_available'] = True
                result['objective_reconstructable'] = bool(
                    observation['objective']['complete_registry_proxy']
                    and observation['objective']['affine_terms'] is not None)
                result['blend_eligible_state'] = observation['blend_allowed']
                cycle = reference.reference_cycle(observations, index)
                result.update(cycle=cycle, timing_quality=observation['timing_quality'])
                if not cycle['qualified']:
                    result['reason'] = cycle['reason']
                elif not observation['objective']['complete_registry_proxy']:
                    result['reason'] = 'active_registry_snapshot_unavailable'
                elif observation['objective']['affine_terms'] is None:
                    result['reason'] = 'affine_snapshot_unavailable'
                else:
                    try:
                        snapshot = observation['objective']
                        objective = reference.augmented_objective(
                            lambda x, y, theta: truth.evaluate_raw_cost(model, x, y, theta),
                            base_xy=observation['xy'], binding=binding, weights=snapshot['weights'],
                            gaussian_fills=snapshot['gaussian_fills'], affine_terms=snapshot['affine_terms'])
                        harmonics = reference.integrate_stationary_harmonics(
                            objective, xy=observation['xy'], sources=scenario['sources'])
                        result.update(reference.stationary_reference(
                            harmonics, omega_rad_sec=cycle['omega_rad_sec'],
                            step_sec=cycle['uniform_step_sec']))
                        result['harmonics'] = harmonics
                        result['numerically_qualified'] = harmonics['qualified']
                        result['objective_snapshot'] = snapshot
                        result['method_outputs'] = paired[index]
                        if result['informative'] and paired[index] is not None:
                            result['legacy_error_deg'] = reference.angular_error_deg(
                                paired[index]['legacy_world_vector'], result['world_vector'])
                            result['v2_error_deg'] = reference.angular_error_deg(
                                paired[index]['v2_world_vector'], result['world_vector'])
                    except (ValueError, ArithmeticError) as exc:
                        result['reason'] = f'objective_or_reference_unavailable: {exc}'
            publish(output / f'anchor_{row["seed"]}_{target["number"]:02d}.json', result)
            results.append(result)
    for owner in owners:
        if _v2_file_hash(owner['path']) != owner['sha256']:
            raise ValueError('M2 owner changed during reference freeze')
    matched = [item for item in results if item.get('legacy_error_deg') is not None
               and item.get('v2_error_deg') is not None]
    eligible = [item for item in results if item['informative'] and item.get('blend_eligible_state')]
    eligible_matched = [item for item in eligible if item.get('legacy_error_deg') is not None
                        and item.get('v2_error_deg') is not None]
    summary = {'version': reference.VERSION, 'fixed_anchor_count': 192,
               'completed_anchor_count': len(results),
               'causal_anchor_count': sum(item['causal_anchor_available'] for item in results),
               'proxy_source_anchor_count': sum(item['causal_anchor_available'] and not item['exact_m2_source_provenance'] for item in results),
               'exact_source_anchor_count': sum(item['causal_anchor_available'] and item['exact_m2_source_provenance'] for item in results),
               'objective_reconstructable_anchor_count': sum(item['objective_reconstructable'] for item in results),
               'fully_observed_input_cycle_count': sum(bool(item.get('cycle', {}).get('input_coverage_valid')) for item in results),
               'qualified_constant_rate_cycle_count': sum(bool(item.get('cycle', {}).get('qualified')) for item in results),
               'numerically_qualified_anchor_count': sum(item['numerically_qualified'] for item in results),
               'qualified_reference_count': sum(item['qualified'] for item in results),
               'informative_reference_count': sum(item['informative'] for item in results),
               'unavailable_reasons': dict(Counter(item['reason'] for item in results if item['reason'])),
               'runtime_transport_qualified': False, 'method_comparison_qualified': False,
               'matched_informative_count': len(matched),
               'legacy_median_error_deg': statistics.median(item['legacy_error_deg'] for item in matched) if matched else None,
               'v2_median_error_deg': statistics.median(item['v2_error_deg'] for item in matched) if matched else None,
               'v2_p90_error_deg': float(np.percentile([item['v2_error_deg'] for item in matched], 90)) if matched else None,
               'eligible_informative_count': len(eligible),
               'eligible_matched_direction_count': len(eligible_matched),
               'eligible_missing_method_direction_count': len(eligible)-len(eligible_matched),
               'eligible_v2_median_error_deg': statistics.median(item['v2_error_deg'] for item in eligible_matched) if eligible_matched else None,
               'eligible_v2_p90_error_deg': float(np.percentile([item['v2_error_deg'] for item in eligible_matched], 90)) if eligible_matched else None,
               'averaging_availability': (sum(bool(item.get('method_outputs', {}).get('blend_applied'))
                                               for item in eligible)/len(eligible) if eligible else None),
               'claim': 'stationary_augmented_reference_on_retained_input_proxies',
               'owners': owners, 'results': results}
    publish(output / 'references.json', summary)
    return summary


Q1_VERSION = 'q1-primary-shadow-v1'
Q1_PARTITION_SEEDS = {'discovery': (26090911, 26090912),
                      'confirmation': (26090913, 26090914)}
Q2_VERSION = 'q2-primary-shadow-v1'
Q2_CORRECTED_VERSION = 'q2-primary-shadow-v2'
Q2_VERSIONS = (Q2_VERSION, Q2_CORRECTED_VERSION)
Q2_PARTITION_SEEDS = {'discovery': (26090921, 26090922),
                      'confirmation': (26090923, 26090924)}
Q2_CORRECTED_PARTITION_SEEDS = {'discovery': (26090931, 26090932),
                               'confirmation': (26090933, 26090934)}


def qualification_partition_seeds(version):
    """Explicit finite study populations; a new version never inherits old seeds."""
    if version == Q1_VERSION:
        return dict(Q1_PARTITION_SEEDS)
    if version == Q2_VERSION:
        return dict(Q2_PARTITION_SEEDS)
    if version == Q2_CORRECTED_VERSION:
        return dict(Q2_CORRECTED_PARTITION_SEEDS)
    raise ValueError('unsupported qualification study version')


def q2_contract_fields(version=Q2_VERSION):
    """Prospective immutable Q2 decisions, with no input or confirmation reads."""
    from copy import deepcopy
    from ros_esc.v2_direction_policy import MOVING_CYCLE_POLICY, policy_metadata
    if version not in Q2_VERSIONS:
        raise ValueError('unsupported Q2 qualification study version')
    slots = []
    for partition, seeds in qualification_partition_seeds(version).items():
        for exposure, seed in zip(('residence', 'approach'), seeds):
            for number in range(1, 13):
                slots.append({
                    'run_id': f'{version}-{partition}-{exposure}-{seed}',
                    'seed': seed, 'partition': partition, 'exposure': exposure,
                    'number': number, 'target_offset_sec': number*10,
                    'source_identity_status': 'SEALED' if partition == 'confirmation' else 'UNBOUND',
                })
    fields = {
        'version': version,
        'expected_build': '/home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1',
        'runtime_source_checkpoint': {
            'path': '/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q2_policy_runtime_closed_v1/manifest.json',
            'sha256': '7df68a0af0b4fb953fc0631a4a5d0f9572d718a5ba74818deed025b583327863',
        },
        'direction_policy': policy_metadata(MOVING_CYCLE_POLICY),
        'reference': {
            'target_offsets_sec': list(range(10, 121, 10)), 'anchor_window_sec': .05,
            'minimum_confirmation_informative_anchors_per_run': 6,
            'maximum_median_error_deg': 30, 'maximum_p90_error_deg': 60,
            'minimum_usable_averaging_availability': .8,
            'output_magnitude_floor': 1e-6, 'job_timeout_sec': 300,
            'method': deepcopy(Q1_OBSERVED_PHASE_METHOD),
        },
        'reference_branch_rule': {
            'authority': 'completed_discovery_nomination',
            'PASS': 'all_48_after_nomination',
            'FAIL': 'discovery_24_diagnostic',
            'EVIDENCE_UNAVAILABLE': 'discovery_24_diagnostic',
            'incomplete_or_integrity_error': 'stop',
        },
        'planned_reference_slots': slots,
    }
    if version == Q2_CORRECTED_VERSION:
        fields.update(
            prior_acquisition_closure={
                'path': '/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v1/acquisition_closed.json',
                'sha256': '672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02',
            },
            acquisition_path_correction_checkpoint={
                'path': '/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q2_acquisition_closed_v1/manifest.json',
                'sha256': '670a20d983dd2919807e324c2a305258c9e4166853d34b8769ca26079bfaeb44',
            },
        )
    return fields


def q1_pose_search_eligibility(samples, bag_data):
    """Project exact pose knots onto explicit recorded clock coverage for Q1.

    This is an evidence proxy, not reconstruction of any subscriber's callback
    or steady clock. Original bag receipts are retained. Unknown/uncovered,
    stale, invalid or backward-clock support remains unavailable. The historical
    M1 mask is applied only after this fresh-version admission projection.
    """
    from bisect import bisect_right
    from copy import deepcopy
    from dataclasses import replace
    from ros_esc.v2_stream import time_to_ns
    clocks = records_for_alias(bag_data, 'clock')
    states = records_for_alias(bag_data, 'algorithm_state')
    readiness = records_for_alias(bag_data, 'recording_ready')
    clock_receipts, clock_values = [], []
    rollback_at = None
    for record in clocks:
        value = time_to_ns(record.message.clock)
        if (value < 0 or clock_values and value < clock_values[-1]
                or clock_receipts and record.bag_timestamp_ns < clock_receipts[-1]):
            rollback_at = record.bag_timestamp_ns
            break
        clock_receipts.append(record.bag_timestamp_ns)
        clock_values.append(value)

    def cover(source_ns, receipt_ns):
        if type(source_ns) is not int or source_ns < 0:
            return None, None, 'invalid_source_stamp'
        if rollback_at is not None and receipt_ns >= rollback_at:
            return None, None, 'recorded_clock_rollback'
        at = bisect_right(clock_receipts, receipt_ns)-1
        if at < 0:
            return None, None, 'original_receipt_clock_unavailable'
        original_clock = clock_values[at]
        if abs(source_ns-original_clock) > 500_000_000:
            return None, original_clock, 'source_outside_original_clock_bound'
        covered = at
        while covered < len(clock_values) and clock_values[covered] < source_ns:
            covered += 1
        if covered == len(clock_values):
            return None, original_clock, 'covering_clock_unavailable'
        admission_receipt = max(receipt_ns, clock_receipts[covered])
        if (admission_receipt-receipt_ns > 500_000_000
                or clock_values[covered]-original_clock > 500_000_000
                or clock_values[covered]-source_ns > 500_000_000):
            return None, original_clock, 'clock_coverage_stale'
        if rollback_at is not None and admission_receipt >= rollback_at:
            return None, original_clock, 'recorded_clock_rollback'
        return admission_receipt, original_clock, None

    projected_states, state_originals, extra_invalidations = [], [], []
    previous_admission = None
    previous_original = None
    for record in states:
        admission, original_clock, reason = cover(record.ros_timestamp_ns, record.bag_timestamp_ns)
        message = record.message
        if (not message.state_valid or not message.run_id_valid or not message.run_id
                or message.state != AlgorithmState.STATE_SEARCH
                or message.algorithm_profile != 'robust_gaussian_v1'):
            extra_invalidations.append(record.bag_timestamp_ns)
        if reason:
            message = deepcopy(message)
            message.state_valid = False
            admission = record.bag_timestamp_ns
            extra_invalidations.append(admission)
        # Preserve this publisher's receipt order while buffered clock coverage
        # becomes available; never sort a source regression into valid evidence.
        admission = max(admission, previous_admission if previous_admission is not None else admission)
        projected_states.append(replace(record, bag_timestamp_ns=admission, message=message))
        state_originals.append((admission, record.bag_timestamp_ns, original_clock))
        if previous_original is not None and record.bag_timestamp_ns-previous_original > 500_000_000:
            extra_invalidations.append(previous_original+500_000_000)
        previous_admission, previous_original = admission, record.bag_timestamp_ns
    projected_records = dict(bag_data.records_by_topic)
    state_topic = bag_data.topics_by_alias.get('algorithm_state', {}).get('topic')
    if state_topic is not None:
        projected_records[state_topic] = projected_states
    projected_bag = replace(bag_data, records_by_topic=projected_records)
    state_admissions = [item[0] for item in state_originals]
    original_state_receipts = [record.bag_timestamp_ns for record in states]
    ready_receipts = [record.bag_timestamp_ns for record in readiness]
    for index, record in enumerate(readiness):
        if not bool(record.message.data):
            extra_invalidations.append(record.bag_timestamp_ns)
        if index and record.bag_timestamp_ns-readiness[index-1].bag_timestamp_ns > 500_000_000:
            extra_invalidations.append(readiness[index-1].bag_timestamp_ns+500_000_000)
    pending_invalidations = sorted(extra_invalidations)
    projected_samples, reasons = [], []
    last_source = None
    last_admission = None
    for sample in samples:
        original_receipt = sample['bag_timestamp_ns']
        admission, original_clock, reason = cover(sample['stamp_ns'], original_receipt)
        if last_source is not None and sample['stamp_ns'] is not None and sample['stamp_ns'] <= last_source:
            reason = 'pose_source_regression_or_duplicate'
        if not sample.get('qualified', False):
            reason = reason or 'invalid_selected_pose'
        if admission is not None and last_admission is not None and admission < last_admission:
            reason = reason or 'pose_admission_order_unavailable'
        projected_receipt = admission if admission is not None else original_receipt
        ready_at = bisect_right(ready_receipts, original_receipt)-1
        state_at = bisect_right(original_state_receipts, original_receipt)-1
        if not reason and (ready_at < 0 or not bool(readiness[ready_at].message.data)
                           or original_receipt-ready_receipts[ready_at] > 500_000_000):
            reason = 'original_recording_readiness_unavailable'
        if not reason and (state_at < 0 or not states[state_at].message.state_valid
                           or not states[state_at].message.run_id_valid
                           or states[state_at].message.state != AlgorithmState.STATE_SEARCH):
            reason = 'original_search_state_unavailable'
        if not reason and bisect_right(pending_invalidations, projected_receipt) > bisect_right(
                pending_invalidations, original_receipt):
            reason = 'pending_context_invalidated'
        at = bisect_right(state_admissions, projected_receipt)-1
        if not reason and at >= 0:
            _, original_state_receipt, original_state_clock = state_originals[at]
            if (projected_receipt-original_state_receipt > 500_000_000
                    or original_state_clock is None):
                reason = 'original_state_receipt_stale_or_unknown'
        if reason:
            extra_invalidations.append(projected_receipt)
        projected_samples.append({**sample, 'bag_timestamp_ns': projected_receipt,
                                  'original_bag_timestamp_ns': original_receipt,
                                  'admission_bag_timestamp_ns': admission,
                                  'original_receipt_clock_ns': original_clock})
        reasons.append(reason)
        if sample['stamp_ns'] is not None:
            last_source = sample['stamp_ns']
        if admission is not None:
            last_admission = admission
    extra_invalidations.sort()
    masked = _v2_search_eligibility(projected_samples, projected_bag)
    result = []
    for row, reason in zip(masked, reasons):
        if reason is None and row['search_epoch'] is None:
            reason = 'recorded_search_or_readiness_unavailable'
        result.append({**row, 'bag_timestamp_ns': row['original_bag_timestamp_ns'],
                       'qualified': bool(row['qualified'] and reason is None),
                       'search_epoch': row['search_epoch'] if reason is None else None,
                       'history_generation': row['history_generation'] + bisect_right(
                           extra_invalidations, row['admission_bag_timestamp_ns']
                           if row['admission_bag_timestamp_ns'] is not None else row['original_bag_timestamp_ns']),
                       'admission_unavailable_reason': reason,
                       'admission_evidence': 'recorded_clock_and_original_bag_receipt_proxy',
                       'subscriber_timing_reconstructed': False})
    return result


def q1_observation_from_row(row):
    """Restore the exact recorded wire, including original receipts, for M3."""
    from ros_esc_interfaces.msg import SynchronizedObservation
    from ros_esc.v2_stream import set_time
    wire = SynchronizedObservation()
    payload = row['observation_wire']
    if set(payload) != set(wire.get_fields_and_field_types()):
        raise ValueError('Q1 observation wire fields changed')
    for name, value in payload.items():
        current = getattr(wire, name)
        if hasattr(current, 'sec') and hasattr(current, 'nanosec'):
            if type(value) is not int:
                raise ValueError('Q1 wire time must be integer nanoseconds')
            set_time(current, value)
        else:
            setattr(wire, name, value)
    return wire


def _q1_vector(values):
    return (list(map(float, values)) if len(values) == 2
            and all(math.isfinite(float(value)) for value in values) else None)


def _q1_method(direction):
    """Detach first publication without using output fields to select inputs."""
    instant = _q1_vector(direction.instant_world)
    body = _q1_vector(direction.output_body)
    world = None
    if direction.output_valid and body is not None and math.isfinite(direction.output_yaw_rad):
        cosine, sine = math.cos(direction.output_yaw_rad), math.sin(direction.output_yaw_rad)
        world = [cosine*body[0]-sine*body[1], sine*body[0]+cosine*body[1]]
    usable = world is not None and math.hypot(*world) > 1e-6
    blend = bool(direction.output_valid and direction.blend_weight == .5)
    return {'aligned_instant_world': instant, 'v2_output_world': world,
            'output_valid': bool(direction.output_valid),
            'averaging_qualified': bool(direction.qualified),
            'blend_applied': blend, 'usable_averaging': bool(blend and usable),
            'usable_output': usable, 'fallback_used': bool(direction.fallback_used),
            'fallback_reason': str(direction.fallback_reason),
            'diagnostic_sequence': int(direction.diagnostic_sequence),
            'comparator': 'recorded_aligned_instantaneous_vs_recorded_rolling',
            'legacy_callback_reconstruction': False}


def direction_method_for_policy(direction, *, policy_record=None, companion=None):
    """Detach an explicitly identified output; preserve the old method by default."""
    from ros_esc.v2_direction_policy import (
        THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY, validate_policy_metadata,
    )
    from ros_esc.experiment_recording.v2_direction_policy_validation import direction_policy_pair_errors
    policy = THREE_CYCLE_POLICY if policy_record is None else validate_policy_metadata(policy_record)
    if policy == THREE_CYCLE_POLICY:
        return _q1_method(direction)
    if policy != MOVING_CYCLE_POLICY:
        raise ValueError('unsupported recorded direction policy')
    errors = direction_policy_pair_errors(direction, companion)
    if errors:
        raise ValueError('; '.join(errors))
    method = _q1_method(direction)
    blend = bool(direction.output_valid and direction.blend_weight == .75)
    method.update(blend_applied=blend, usable_averaging=bool(blend and method['usable_output']),
                  direction_policy=policy, policy_config_sha256=companion.policy_config_sha256,
                  coherence_available=bool(companion.coherence_available),
                  coherence=float(companion.coherence) if math.isfinite(companion.coherence) else None,
                  coherence_lower=float(companion.coherence_lower) if math.isfinite(companion.coherence_lower) else None,
                  coherence_upper=float(companion.coherence_upper) if math.isfinite(companion.coherence_upper) else None,
                  coherence_reason=str(companion.numerical_reason),
                  comparator='recorded_aligned_instantaneous_vs_recorded_moving_cycle')
    return method


MOVING_POLICY_INPUT_VERSION = 'moving-cycle-direction-inputs-v1'
M4_DIRECTION_INPUT_VERSION = 'm4-augmented-direction-inputs-v1'
M4_MAXIMUM_OBSERVATIONS = 40000


def prepare_q1_direction_inputs(bag_data, metadata, *, contract, run_spec):
    """Preserve the old Q1 input protocol and its recorded policy interpretation."""
    from ros_esc.v2_direction_policy import THREE_CYCLE_POLICY
    if contract.get('version') != Q1_VERSION:
        raise ValueError('Q1 contract version mismatch')
    return _prepare_policy_direction_inputs(bag_data, metadata, run_spec=run_spec,
                                            input_version=Q1_VERSION, policy=THREE_CYCLE_POLICY)


def prepare_moving_policy_direction_inputs(bag_data, metadata, *, run_spec):
    """Normalize new-policy receipts only; callers separately freeze study inputs.

    This source protocol does not choose a population, compute a reference,
    replay a filter, qualify a study, or interpret old Q1 as new-policy evidence.
    """
    from ros_esc.v2_direction_policy import MOVING_CYCLE_POLICY
    return _prepare_policy_direction_inputs(bag_data, metadata, run_spec=run_spec,
                                            input_version=MOVING_POLICY_INPUT_VERSION,
                                            policy=MOVING_CYCLE_POLICY)


def prepare_m4_direction_inputs(bag_data, metadata, *, run_spec,
                                maximum_observations=M4_MAXIMUM_OBSERVATIONS):
    """Retain the complete recorded objective across M4 interventions.

    Population/targets and the numerical raw model remain separate owners.
    A bounded extraction failure excludes the whole input; it never truncates
    or replaces an augmented target with a raw-only reference.
    """
    from ros_esc.v2_direction_policy import MOVING_CYCLE_POLICY
    if (type(maximum_observations) is not int
            or not 1 <= maximum_observations <= M4_MAXIMUM_OBSERVATIONS):
        raise ValueError('M4 maximum_observations must be an integer in [1, 40000]')
    return _prepare_policy_direction_inputs(bag_data, metadata, run_spec=run_spec,
        input_version=M4_DIRECTION_INPUT_VERSION, policy=MOVING_CYCLE_POLICY,
        augmented_objectives=True, maximum_observations=maximum_observations)


def _m4_objective_snapshot(objective, law):
    """Normalize the composer law at its recorded composition time.

    Existing composer methods check components at the recorded sensor point;
    the numerical reference owner later evaluates the frozen effective terms.
    No node, bag read, model evaluation or alternate field evaluator is created.
    """
    from types import SimpleNamespace
    from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
    from ros_esc.v2_stream import canonical_json, time_to_ns
    from ros_esc.v2_lifecycle import message_payload

    def finite_number(value):
        return type(value) in (int, float) and math.isfinite(value)

    def point(value):
        if not isinstance(value, list) or len(value) != 2 or not all(map(finite_number, value)):
            raise ValueError('M4 objective requires finite planar vectors')
        return np.asarray(value, dtype=float)

    required = {'schema_version', 'weights', 'bias_all_channels', 'fills', 'affine',
                'affine_enabled', 'affine_decay_rate', 'affine_max_age', 'affine_min_norm'}
    if (not isinstance(law, dict) or set(law) != required
            or type(law['schema_version']) is not int or law['schema_version'] != 1
            or type(law['bias_all_channels']) is not bool or type(law['affine_enabled']) is not bool
            or not isinstance(law['weights'], list) or len(law['weights']) != 3
            or not all(map(finite_number, law['weights']))
            or not isinstance(law['fills'], list) or not isinstance(law['affine'], list)
            or any(not finite_number(law[name]) or law[name] < 0 for name in
                   ('affine_decay_rate', 'affine_max_age', 'affine_min_norm'))):
        raise ValueError('M4 incomplete or nonfinite recorded objective law')
    if (hashlib.sha256(canonical_json(law).encode()).hexdigest() != objective.objective_sha256
            or hashlib.sha256(canonical_json(law['fills']).encode()).hexdigest() != objective.registry_digest
            or law['weights'] != [objective.sensor_weight, objective.gaussian_weight, objective.affine_weight]
            or objective.objective_revision <= 0):
        raise ValueError('M4 objective/registry/weight identity differs from recorded law')
    composition_ns = time_to_ns(objective.composition_stamp)
    if not (0 <= time_to_ns(objective.model_input_stamp) <= composition_ns <= time_to_ns(objective.stamp)):
        raise ValueError('M4 objective composition time is not covered')
    arrays = (objective.raw_cost, objective.gaussian_cost, objective.affine_cost, objective.augmented_cost,
              objective.sensor_x_m, objective.sensor_y_m)
    if (not objective.valid or objective.channel_count != 1 or any(len(values) != 1 for values in arrays)
            or not all(finite_number(float(values[0])) for values in arrays)):
        raise ValueError('M4 objective requires one finite recorded channel')
    fills, clusters, affine = {}, set(), {}
    for term in law['fills']:
        if (not isinstance(term, dict) or set(term) !=
                {'fill_id', 'cluster_id', 'revision', 'amplitude', 'center', 'covariance'}
                or any(type(term[key]) is not int or term[key] <= 0 for key in
                       ('fill_id', 'cluster_id', 'revision'))
                or term['fill_id'] in fills or term['cluster_id'] in clusters
                or not finite_number(term['amplitude']) or term['amplitude'] <= 0):
            raise ValueError('M4 invalid or duplicate Gaussian identity/amplitude')
        try:
            covariance = np.asarray(term['covariance'], dtype=float)
            if (covariance.shape != (2, 2) or not np.isfinite(covariance).all()
                    or not np.array_equal(covariance, covariance.T)
                    or np.min(np.linalg.eigvalsh(covariance)) <= 0):
                raise ValueError('M4 Gaussian covariance is not finite positive definite')
            inverse = np.linalg.inv(covariance)
            if not np.isfinite(inverse).all():
                raise ValueError('M4 Gaussian inverse is not finite')
        except np.linalg.LinAlgError as exc:
            raise ValueError('M4 Gaussian covariance cannot be inverted') from exc
        fills[term['fill_id']] = dict(term, center=point(term['center']),
            covariance=covariance, inverse=inverse)
        clusters.add(term['cluster_id'])
    for term in law['affine']:
        if (not isinstance(term, dict) or set(term) !=
                {'cluster_id', 'fill_id', 'direction_revision', 'anchor', 'b0', 't0_sec'}
                or any(type(term[key]) is not int or term[key] <= 0 for key in
                       ('cluster_id', 'fill_id', 'direction_revision'))
                or term['cluster_id'] in affine or term['fill_id'] not in fills
                or fills[term['fill_id']]['cluster_id'] != term['cluster_id']
                or not finite_number(term['t0_sec']) or term['t0_sec'] < 0):
            raise ValueError('M4 invalid or unbound affine term')
        affine[term['cluster_id']] = dict(term, anchor=point(term['anchor']),
            b0=point(term['b0']), t0=term['t0_sec'])
    if objective.affine_revision != max((term['direction_revision'] for term in law['affine']), default=0):
        raise ValueError('M4 affine revision differs from recorded law')
    # These methods own exactly the production sign, decay, strict expiry and
    # minimum-norm pruning. The detached owner mutates only its local term map.
    owner = SimpleNamespace(robust_profile=True, robust_terms=fills,
        robust_affine_terms=affine, affine_decay_rate=law['affine_decay_rate'],
        affine_max_age=law['affine_max_age'], affine_min_norm=law['affine_min_norm'])
    x, y = float(objective.sensor_x_m[0]), float(objective.sensor_y_m[0])
    gaussian = ModifiedCost2D._gaussian_bias_at_xy(owner, x, y)
    affine_cost = ModifiedCost2D._affine_bias_at_xy(owner, x, y, composition_ns*1e-9)
    augmented = sum(weight*value for weight, value in zip(law['weights'],
                    (objective.raw_cost[0], gaussian, affine_cost)))
    for computed, recorded, name in ((gaussian, objective.gaussian_cost[0], 'Gaussian'),
            (affine_cost, objective.affine_cost[0], 'affine'),
            (augmented, objective.augmented_cost[0], 'augmented')):
        # Same fixed component tolerance as the existing stream contract.
        if not math.isfinite(computed) or not math.isclose(computed, recorded, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError('M4 recorded '+name+' cost differs from complete objective law')
    effective_affine = []
    for term in owner.robust_affine_terms.values():
        age = max(0., composition_ns*1e-9-term['t0'])
        effective_affine.append({'anchor': term['anchor'].tolist(),
            'vector': (math.exp(-law['affine_decay_rate']*age)*term['b0']).tolist()})
    return {'weights': list(law['weights']), 'gaussian_fills': law['fills'],
            'affine_terms': effective_affine, 'law': law, 'composition_stamp_ns': composition_ns,
            'objective_sha256': objective.objective_sha256, 'registry_digest': objective.registry_digest,
            'objective_revision': int(objective.objective_revision),
            'affine_revision': int(objective.affine_revision), 'receipt': message_payload(objective),
            'complete': True, 'component_costs_verified': True,
            'effective_affine_count': len(effective_affine),
            'pruned_affine_count': len(law['affine'])-len(effective_affine)}


def _prepare_policy_direction_inputs(bag_data, metadata, *, run_spec, input_version, policy,
                                     augmented_objectives=False, maximum_observations=None):
    """Normalize actual schema2 input receipts; no field/filter evaluations.

    Each row is JSON-safe and its ``qualified`` flag refers only to inputs.
    Repeated publication may change the wrapper stamp, never the immutable
    observation. First publication is this publisher's recorded sequence,
    not a claim about the supervisor's first DDS receipt.
    """
    from ros_esc.experiment_recording.record_run import v2_identity_from_metadata
    from ros_esc.experiment_recording.validate_run import v2_stream_contract_errors
    from ros_esc.v2_lifecycle import hash_payload, message_payload, observation_payload
    from ros_esc.v2_stream import time_to_ns
    from ros_esc.v2_direction_policy import THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY, POLICY_DIAGNOSTICS_TOPIC
    from ros_esc.experiment_recording.v2_direction_policy_validation import index_policy_companions
    identity = v2_identity_from_metadata(metadata)
    if (identity is None or identity['stream_config']['schema_version'] != 2
            or identity['stream_config'].get('cost_key_basis') != 'model_input_time'
            or identity['run_id'] != run_spec['run_id']):
        raise ValueError('Q1 requires matching schema2 acquisition identity')
    if identity.get('direction_policy', {}).get('policy_name', THREE_CYCLE_POLICY) != policy:
        raise ValueError('recorded direction policy differs from selected input protocol')
    config = identity['stream_config']
    messages = {topic: [(record.bag_timestamp_ns, record.message) for record in records]
                for topic, records in bag_data.records_by_topic.items()}
    direction_topic = bag_data.topics_by_alias.get('v2_direction_diagnostics', {}).get(
        'topic', '/gesc_gaussian/v2/direction_diagnostics')
    try:
        errors = v2_stream_contract_errors(messages, identity, direction_topic)
    except (ValueError, TypeError, AttributeError, KeyError, OverflowError) as exc:
        errors = [f'Q1 malformed typed input: {exc}']
    companions = {}
    companion_bag_stamps = {}
    if policy == MOVING_CYCLE_POLICY:
        companions, companion_errors = index_policy_companions(messages.get(POLICY_DIAGNOSTICS_TOPIC, []))
        errors.extend(companion_errors)
        for bag_stamp, companion in messages.get(POLICY_DIAGNOSTICS_TOPIC, []):
            try:
                if companion is not None:
                    key = (int(companion.diagnostic_sequence), time_to_ns(companion.stamp))
                    companion_bag_stamps.setdefault(key, bag_stamp)
            except (ValueError, TypeError, AttributeError, OverflowError) as exc:
                errors.append('moving-policy malformed companion clock: ' + str(exc))
    objectives = {float(message.legacy_cost_source_timestamp_sec): message
                  for _, message in messages.get(config['objective_cost_topic'], [])
                  if message is not None and message.valid}
    observations, seen, ids, sequences = [], {}, {}, {}
    previous_source, previous_reset, previous_ready, context = None, None, None, 0
    skipped, duplicates = Counter(), 0
    for record in bag_data.records_by_topic.get(direction_topic, []):
        direction = record.message
        if direction is None or not direction.observation.synchronized_valid:
            skipped['no_synchronized_observation'] += 1
            context += 1
            continue
        wire = direction.observation
        try:
            stamp = time_to_ns(wire.source_stamp)
            payload = observation_payload(wire)
            fingerprint = hash_payload(payload)
            key = (int(wire.source_sequence), stamp)
            if key in seen:
                if seen[key] != fingerprint:
                    errors.append('Q1 conflicting immutable observation repeat')
                else:
                    duplicates += 1
                continue
            if maximum_observations is not None and len(seen) >= maximum_observations:
                errors.append('M4 unique observation capacity exceeded; whole input unavailable')
                break
            if (wire.observation_id <= 0 or wire.source_sequence <= 0
                    or (wire.observation_id in ids and ids[wire.observation_id] != key)
                    or (wire.source_sequence in sequences and sequences[wire.source_sequence] != key)
                    or (previous_source is not None and stamp <= previous_source)):
                raise ValueError('observation/source identity regression or reuse')
            seen[key], ids[wire.observation_id], sequences[wire.source_sequence] = fingerprint, key, key
            objective = objectives.get(float(wire.legacy_cost_source_timestamp_sec))
            if objective is None:
                raise ValueError('missing exact objective receipt')
            law = json.loads(objective.objective_config_json)
            required = {'schema_version', 'weights', 'bias_all_channels', 'fills', 'affine',
                        'affine_enabled', 'affine_decay_rate', 'affine_max_age', 'affine_min_norm'}
            if set(law) != required or law['schema_version'] != 1:
                raise ValueError('incomplete or unsupported objective law')
            if not augmented_objectives and (law['fills'] or law['affine']):
                raise ValueError('observation-only Q1 contains an objective intervention')
            if not augmented_objectives and (any(not math.isfinite(float(law[name])) or float(law[name]) < 0
                    for name in ('affine_decay_rate', 'affine_max_age', 'affine_min_norm'))
                    or any(not math.isfinite(float(value)) for value in law['weights'])
                    or objective.gaussian_cost[0] != 0.0 or objective.affine_cost[0] != 0.0):
                raise ValueError('empty objective law does not match finite component values')
            admission, oldest = time_to_ns(wire.admission_stamp), time_to_ns(wire.oldest_receipt_stamp)
            if not (0 <= admission-stamp <= 500_000_000
                    and 0 <= admission-oldest <= 500_000_000):
                raise ValueError('synchronized input admission is stale')
            if (previous_source is not None and stamp-previous_source > 500_000_000
                    or previous_reset is not None and direction.reset_sequence != previous_reset
                    or previous_ready is not None and bool(record.in_readiness_interval) != previous_ready):
                context += 1
            if augmented_objectives:
                if any(getattr(direction, name) != getattr(objective, name) for name in (
                        'objective_revision', 'objective_sha256', 'registry_digest', 'affine_revision',
                        'sensor_weight', 'gaussian_weight', 'affine_weight')):
                    raise ValueError('M4 first direction publication differs from its exact objective receipt')
                snapshot = _m4_objective_snapshot(objective, law)
            else:
                snapshot = {'weights': list(law['weights']), 'gaussian_fills': [], 'affine_terms': [],
                            'law': law, 'composition_stamp_ns': time_to_ns(objective.composition_stamp),
                            'objective_sha256': objective.objective_sha256,
                            'registry_digest': objective.registry_digest,
                            'objective_revision': int(objective.objective_revision),
                            'affine_revision': int(objective.affine_revision),
                            'receipt': message_payload(objective), 'complete': True}
            row = {'stamp_ns': stamp, 'cost_stamp_ns': time_to_ns(wire.cost_source_stamp),
                   'source_sequence': int(wire.source_sequence), 'observation_id': int(wire.observation_id),
                   'xy': [wire.base_x_m, wire.base_y_m], 'yaw_rad': wire.base_yaw_rad,
                   'world_phase_rad': wire.sensor_world_phase_rad,
                   'projected_phase_rad': wire.sensor_phase_rad, 'encoder_phase_rad': wire.encoder_phase_rad,
                   'raw_cost': wire.raw_cost, 'cost': wire.augmented_cost, 'frame_id': wire.frame_id,
                   'qualified': True, 'readiness_eligible': bool(record.in_readiness_interval),
                   'context_id': context, 'objective_id': objective.objective_sha256, 'objective': snapshot,
                   'filter_state': int(direction.algorithm_state),
                   'filter_state_valid': bool(direction.algorithm_state_valid),
                   'filter_stamp_ns': time_to_ns(direction.stamp),
                   'blend_allowed': bool(direction.algorithm_state_valid and direction.algorithm_state in (1, 2, 3)),
                   'receipt_stamp_ns': time_to_ns(wire.receipt_stamp),
                   'oldest_receipt_stamp_ns': oldest, 'admission_stamp_ns': admission,
                   'pose_bracket_ns': [time_to_ns(wire.pose_left_stamp), time_to_ns(wire.pose_right_stamp)],
                   'encoder_bracket_ns': [time_to_ns(wire.encoder_left_stamp), time_to_ns(wire.encoder_right_stamp)],
                   'observation_wire': message_payload(wire), 'observation_sha256': fingerprint,
                   'first_diagnostic_bag_stamp_ns': record.bag_timestamp_ns,
                   'bag_timestamp_ns': record.bag_timestamp_ns,
                   'method': direction_method_for_policy(
                       direction, policy_record=identity.get('direction_policy'),
                       companion=companions.get((int(direction.diagnostic_sequence), time_to_ns(direction.stamp))))}
            if policy == MOVING_CYCLE_POLICY:
                companion_key = (int(direction.diagnostic_sequence), time_to_ns(direction.stamp))
                row['direction_policy_wire'] = message_payload(companions[companion_key])
                row['first_policy_diagnostic_bag_stamp_ns'] = companion_bag_stamps[companion_key]
            observations.append(row)
            previous_source, previous_reset = stamp, direction.reset_sequence
            previous_ready = bool(record.in_readiness_interval)
        except (ValueError, TypeError, KeyError, AttributeError, IndexError, OverflowError) as exc:
            errors.append('Q1 input: ' + str(exc))
            context += 1
    observed_count = len(observations)
    if errors:
        observations = []  # Ambiguous recordings never contribute selected anchors.
    origin = next((row['stamp_ns'] for row in observations if row['readiness_eligible']), None)
    return observations, {'version': input_version, 'run_id': run_spec['run_id'],
                          'qualified': not errors and bool(observations), 'integrity_errors': errors,
                          'observed_input_count': observed_count, 'sample_count': len(observations),
                          'readiness_eligible_count': sum(row['readiness_eligible'] for row in observations),
                          'origin_ns': origin, 'duplicate_publications': duplicates,
                          'skipped_diagnostics': dict(skipped), 'exact_m2_source_provenance': True,
                          'readiness_clock': 'recorded_bag_receipt_interval',
                          **({'maximum_observations': maximum_observations,
                              'objective_scope': 'recorded_complete_augmented_at_composition'}
                             if augmented_objectives else {}),
                          'claim': 'actual_typed_inputs_and_first_recorded_publisher_output'}


def _q1_verify_files(receipts, *, required=()):
    """Verify an explicit bounded file set before any input/model consumption."""
    if not isinstance(receipts, list) or not receipts:
        raise ValueError('Q1 requires a nonempty file receipt set')
    verified = {}
    for receipt in receipts:
        path = Path(receipt['path']).expanduser().resolve()
        digest = receipt['sha256']
        if (not path.is_file() or _v2_file_hash(path) != digest
                or str(path) in verified and verified[str(path)] != digest):
            raise ValueError(f'Q1 frozen file changed or unavailable: {path}')
        verified[str(path)] = digest
    if not {str(Path(path).resolve()) for path in required} <= verified.keys():
        raise ValueError('Q1 required input/owner is not bound by a file receipt')
    return verified


def _q1_contract(reference):
    _q1_verify_files([reference])
    contract = json.loads(Path(reference['path']).read_text())
    return _q1_validate_contract(contract)


def _q1_validate_contract(contract):
    """Unchanged scientific values and complete current-owner receipt checks."""
    expected = {'target_offsets_sec': list(range(10, 121, 10)), 'anchor_window_sec': .05,
                'minimum_confirmation_informative_anchors_per_run': 6,
                'maximum_median_error_deg': 30, 'maximum_p90_error_deg': 60,
                'minimum_usable_averaging_availability': .8,
                'output_magnitude_floor': 1e-6, 'job_timeout_sec': 300}
    if (contract.get('version') not in (Q1_VERSION, *Q2_VERSIONS)
            or any(contract.get('reference', {}).get(key) != value for key, value in expected.items())):
        raise ValueError('Q1 frozen reference contract changed')
    from . import v2_direction_reference as numeric
    from . import bag_reader
    from ros_esc import v2_lifecycle, v2_stream
    from ros_esc.experiment_recording import validate_run, record_run
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    required = [Path(module.__file__) for module in
                (numeric, bag_reader, v2_lifecycle, v2_stream, validate_run, record_run, truth,
                 truth.cost_function_objects)] + [Path(__file__)]
    if contract['version'] in Q2_VERSIONS:
        from ros_esc import v2_direction_policy
        from ros_esc.experiment_recording import v2_direction_policy_validation
        from . import q1_study
        fields = q2_contract_fields(contract['version'])
        # Canonical JSON also distinguishes bools from integers and rejects NaN.
        if any(v2_stream.canonical_json(contract.get(key)) != v2_stream.canonical_json(value)
               for key, value in fields.items()):
            raise ValueError('Q2 frozen policy, build, slot or reference branch contract changed')
        _q1_verify_files([contract['runtime_source_checkpoint']])
        if contract['version'] == Q2_CORRECTED_VERSION:
            _q1_verify_files([contract['prior_acquisition_closure'],
                              contract['acquisition_path_correction_checkpoint']])
            closure = json.loads(Path(contract['prior_acquisition_closure']['path']).read_text())
            if (closure.get('version') != Q2_VERSION or closure.get('status') != 'CLOSED_INCOMPLETE'
                    or closure.get('dispatched_cases') != 1 or closure.get('verified_runs') != 0
                    or closure.get('scientific_evaluation_started') is not False
                    or closure.get('scientific_confirmation_opened') is not False
                    or closure.get('all_cleanup_passed') is not True):
                raise ValueError('Q2 corrected acquisition lacks its preserved incomplete closure')
        planned = contract.get('runs', [])
        expected_runs = {(slot['run_id'], slot['seed'], slot['partition'], slot['exposure'])
                         for slot in fields['planned_reference_slots']}
        if (len(planned) != 4 or
                {(r.get('run_id'), r.get('seed'), r.get('partition'), r.get('exposure'))
                 for r in planned} != expected_runs):
            raise ValueError('Q2 planned runs differ from the reserved reference population')
        required.extend(Path(module.__file__) for module in
                        (v2_direction_policy, v2_direction_policy_validation, q1_study))
    _q1_verify_files(contract['source_files'], required=required)
    _q1_verify_files(contract['geometry_receipts'])
    return contract


Q1_DISCOVERY_DIRECTION_VERSION = 'q1-discovery-direction-diagnostic-v1'


def _q1_discovery_direction_lineage(reference, original_contract_ref, target_files):
    """Verify explicit historical/current analyzer lineage; never waive freshness.

    Closed-study and checkpoint manifests are historical metadata. Only their
    required discovery receipts are followed; sealed confirmation inputs are
    not opened by this route. The effective contract retains all original
    scientific/acquisition bindings with one authorized source transition.
    """
    def binding(item):
        return str(Path(item['path']).expanduser().resolve()), item['sha256']

    def receipt_map(items):
        if not isinstance(items, list):
            raise ValueError('Q1 diagnostic receipt list required')
        result = dict(binding(item) for item in items)
        if len(result) != len(items):
            raise ValueError('Q1 diagnostic duplicate receipt path')
        return result

    _q1_verify_files([reference])
    diagnostic = json.loads(Path(reference['path']).read_text())
    keys = {'version', 'original_contract', 'study_closed', 'checkpoint',
            'old_analyzer_snapshot', 'frozen_targets', 'analyzer_transition',
            'current_source_files', 'input_traces', 'partition', 'seeds',
            'target_numbers', 'fixed_anchor_count', 'job_timeout_sec', 'reference'}
    if (set(diagnostic) != keys or diagnostic['version'] != Q1_DISCOVERY_DIRECTION_VERSION
            or diagnostic['partition'] != 'discovery'
            or diagnostic['seeds'] != list(Q1_PARTITION_SEEDS['discovery'])
            or diagnostic['target_numbers'] != list(range(1, 13))
            or diagnostic['fixed_anchor_count'] != 24 or diagnostic['job_timeout_sec'] != 300
            or binding(diagnostic['original_contract']) != binding(original_contract_ref)
            or len(target_files) != 1
            or binding(diagnostic['frozen_targets']) != binding(target_files[0])):
        raise ValueError('Q1 discovery diagnostic contract/population mismatch')
    _q1_verify_files([diagnostic[name] for name in (
        'original_contract', 'study_closed', 'checkpoint', 'old_analyzer_snapshot', 'frozen_targets')])
    original = json.loads(Path(original_contract_ref['path']).read_text())
    closure = json.loads(Path(diagnostic['study_closed']['path']).read_text())
    checkpoint = json.loads(Path(diagnostic['checkpoint']['path']).read_text())
    manifest = json.loads(Path(target_files[0]['path']).read_text())
    if (closure.get('version') != Q1_VERSION
            or closure.get('status') != 'CLOSED_EVIDENCE_UNAVAILABLE'
            or closure.get('scientific_confirmation') != 'SEALED_NOT_OPENED'
            or closure.get('pilot_released') is not False
            or binding(closure['contract']) != binding(original_contract_ref)
            or diagnostic['reference'] != original['reference']):
        raise ValueError('Q1 diagnostic original study closure/reference mismatch')
    closed = receipt_map(closure['retained_artifacts'])
    for item in (diagnostic['frozen_targets'], *diagnostic['input_traces']):
        path, digest = binding(item)
        if closed.get(path) != digest:
            raise ValueError('Q1 diagnostic discovery input not bound by closed study')
    if receipt_map(checkpoint['retained_logs']).get(binding(diagnostic['study_closed'])[0]) \
            != diagnostic['study_closed']['sha256']:
        raise ValueError('Q1 diagnostic checkpoint does not bind original closure')
    _q1_verify_files(checkpoint['artifacts'])

    # Inspect every advertised run and target identity before following any
    # trace receipt, including deliberately malformed discovery manifests.
    receipts = manifest.get('input_traces', [])
    allowed_seeds = Q1_PARTITION_SEEDS['discovery']
    if (manifest.get('partition') != 'discovery' or manifest.get('nomination') is not None
            or len(receipts) != 2
            or {item['run']['seed'] for item in receipts} != set(allowed_seeds)
            or len({item['run']['run_id'] for item in receipts}) != 2
            or any(item['run']['partition'] != 'discovery'
                   or item['run']['exposure'] != ('residence' if item['run']['seed'] == allowed_seeds[0]
                                                else 'approach') for item in receipts)):
        raise ValueError('Q1 diagnostic requires exactly two discovery input traces')
    runs = {item['run']['run_id']: item['run'] for item in receipts}
    targets = manifest.get('targets', [])
    if (len(targets) != 24
            or {(item['seed'], item['number']) for item in targets}
            != {(seed, number) for seed in allowed_seeds for number in range(1, 13)}
            or any(item['partition'] != 'discovery' or item['run_id'] not in runs
                   or item['seed'] != runs[item['run_id']]['seed'] for item in targets)):
        raise ValueError('Q1 diagnostic fixed discovery target identities changed')
    if receipt_map(receipts) != receipt_map(diagnostic['input_traces']):
        raise ValueError('Q1 diagnostic input trace receipts changed')
    _q1_verify_files(diagnostic['input_traces'])

    analyzer = str(Path(__file__).resolve())
    repository = next(parent for parent in Path(analyzer).parents
                      if (parent / 'AGENTS.md').is_file() and (parent / 'ros2_ws').is_dir())
    transition = diagnostic['analyzer_transition']
    old_sources = receipt_map(original['source_files'])
    current_sources = receipt_map(diagnostic['current_source_files'])
    historical_files = {str(Path(item['path'])): item['sha256'] for item in checkpoint['files']}
    old_digest = old_sources.get(analyzer)
    if (set(transition) != {'path', 'old_sha256', 'new_sha256'}
            or str(Path(transition['path']).resolve()) != analyzer or old_digest is None
            or transition['old_sha256'] != old_digest
            or diagnostic['old_analyzer_snapshot']['sha256'] != old_digest
            or historical_files.get(str(Path(analyzer).relative_to(repository))) != old_digest
            or current_sources.get(analyzer) != transition['new_sha256']):
        raise ValueError('Q1 diagnostic analyzer lineage mismatch')
    if not old_sources.keys() <= current_sources.keys():
        raise ValueError('Q1 diagnostic removed an original source owner')
    if any(current_sources[path] != digest for path, digest in old_sources.items() if path != analyzer):
        raise ValueError('Q1 diagnostic changed an unauthorized original source owner')
    allowed_new = {str(repository / name) for name in (
        'docs/codex/gesc_gaussian/v2/q1_discovery_direction_plan.md',
        'docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py',
        'ros2_ws/src/ros_esc/test/test_q1_discovery_direction_diagnostic.py')}
    if not current_sources.keys() - old_sources.keys() <= allowed_new:
        raise ValueError('Q1 diagnostic added an unauthorized source owner')
    if not allowed_new <= current_sources.keys():
        raise ValueError('Q1 diagnostic plan/workflow/test owner receipt missing')
    effective = dict(original, source_files=diagnostic['current_source_files'])
    return effective


def _q1_discovery_direction_contract(reference, original_contract_ref, target_files):
    return _q1_validate_contract(
        _q1_discovery_direction_lineage(reference, original_contract_ref, target_files))


Q1_OBSERVED_PHASE_VERSION = 'q1-observed-phase-direction-diagnostic-v1'
Q1_OBSERVED_PHASE_METHOD = {
    'version': 'observed-phase-periodic-v1', 'alpha_per_sec': 1.0,
    'sensor_radius_m': .18, 'maximum_objective_evaluations': 25000,
    'normalized_component_error_limit': 1e-6, 'informative_absolute_floor': 1e-6,
    'informative_error_multiplier': 20.0}
Q1_OBSERVED_PHASE_LATENT = {
    'version': 'recorded-one-cycle-50-50-v1', 'instant_weight': .5,
    'recorded_mean_weight': .5, 'output_magnitude_floor': 1e-6,
    'actual_blend_component_tolerance': 1e-12}


def _q1_observed_phase_contract(reference, original_contract_ref, target_files):
    """Verify the explicit D1-to-observed-phase transition and closed supplement.

    Historical receipt validation is separated from live source validation only
    for these three declared owners. Every other original and D1 owner remains
    exact. Read discovery metadata before following any trace or bag receipt.
    """
    def binding(item):
        return str(Path(item['path']).expanduser().resolve()), item['sha256']

    def receipt_map(items):
        if not isinstance(items, list):
            raise ValueError('Q1 observed-phase receipt list required')
        result = dict(binding(item) for item in items)
        if len(result) != len(items):
            raise ValueError('Q1 observed-phase duplicate receipt path')
        return result

    def require_bound(items, bound, reason):
        if any(bound.get(binding(item)[0]) != binding(item)[1] for item in items):
            raise ValueError(reason)

    _q1_verify_files([reference])
    diagnostic = json.loads(Path(reference['path']).read_text())
    keys = {'version', 'original_contract', 'study_closed',
            'preceding_diagnostic_contract', 'preceding_diagnostic_closed',
            'preceding_diagnostic_checkpoint', 'frozen_targets', 'source_transitions',
            'current_source_files', 'input_traces', 'confidence_audit',
            'confidence_audit_manifest', 'partition', 'seeds', 'target_numbers',
            'fixed_anchor_count', 'job_timeout_sec', 'reference',
            'observed_phase_reference', 'latent_blend'}
    if (set(diagnostic) != keys or diagnostic['version'] != Q1_OBSERVED_PHASE_VERSION
            or diagnostic['partition'] != 'discovery'
            or diagnostic['seeds'] != list(Q1_PARTITION_SEEDS['discovery'])
            or diagnostic['target_numbers'] != list(range(1, 13))
            or diagnostic['fixed_anchor_count'] != 24 or diagnostic['job_timeout_sec'] != 300
            or diagnostic['observed_phase_reference'] != Q1_OBSERVED_PHASE_METHOD
            or diagnostic['latent_blend'] != Q1_OBSERVED_PHASE_LATENT
            or binding(diagnostic['original_contract']) != binding(original_contract_ref)
            or len(target_files) != 1
            or binding(diagnostic['frozen_targets']) != binding(target_files[0])):
        raise ValueError('Q1 observed-phase contract/population mismatch')
    historical_names = ('preceding_diagnostic_contract', 'preceding_diagnostic_closed',
                        'preceding_diagnostic_checkpoint', 'confidence_audit',
                        'confidence_audit_manifest')
    _q1_verify_files([diagnostic[name] for name in historical_names])
    preceding = json.loads(Path(diagnostic['preceding_diagnostic_contract']['path']).read_text())
    if (binding(preceding['study_closed']) != binding(diagnostic['study_closed'])
            or preceding['reference'] != diagnostic['reference']
            or receipt_map(preceding['input_traces']) != receipt_map(diagnostic['input_traces'])):
        raise ValueError('Q1 observed-phase preceding discovery lineage changed')
    # This verifies the unchanged historical Q1/D1 closure, original source
    # transition, exact discovery population, snapshots and archive receipts.
    historical = _q1_discovery_direction_lineage(
        diagnostic['preceding_diagnostic_contract'], original_contract_ref, target_files)
    closure = json.loads(Path(diagnostic['preceding_diagnostic_closed']['path']).read_text())
    if (closure.get('version') != Q1_DISCOVERY_DIRECTION_VERSION
            or closure.get('status') != 'CLOSED_COMPLETE_DIAGNOSTIC'
            or closure.get('qualification_status') != 'NOT_EVALUATED'
            or closure.get('confirmation') != 'SEALED' or closure.get('nomination') is not None
            or closure.get('pilot_released') is not False
            or closure.get('source_unchanged_through_analysis') is not True
            or closure.get('process_exit_code') != 0 or closure.get('fixed_anchor_count') != 24
            or binding(closure['contract']) != binding(diagnostic['preceding_diagnostic_contract'])):
        raise ValueError('Q1 observed-phase preceding diagnostic closure mismatch')
    closed = receipt_map(closure['retained_artifacts'])
    require_bound([diagnostic['preceding_diagnostic_contract'], diagnostic['frozen_targets'],
                   *diagnostic['input_traces']], closed,
                  'Q1 observed-phase discovery receipts not bound by D1 closure')
    checkpoint = json.loads(Path(diagnostic['preceding_diagnostic_checkpoint']['path']).read_text())
    require_bound([diagnostic[name] for name in ('preceding_diagnostic_contract',
                   'preceding_diagnostic_closed', 'confidence_audit', 'confidence_audit_manifest')],
                  receipt_map(checkpoint['retained_logs']),
                  'Q1 observed-phase checkpoint does not bind closed diagnostic/audit')
    _q1_verify_files(checkpoint['artifacts'])
    analyzer = Path(__file__).resolve()
    repository = next(parent for parent in analyzer.parents
                      if (parent / 'AGENTS.md').is_file() and (parent / 'ros2_ws').is_dir())
    allowed_changed = {str(repository / name) for name in (
        'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py',
        'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/v2_direction_reference.py',
        'docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py')}
    required_new = {str(repository / name) for name in (
        'docs/codex/gesc_gaussian/v2/q1_observed_phase_reference_plan.md',
        'docs/codex/gesc_gaussian/v2/q1_observed_phase_reference_design.md',
        'ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py',
        'ros2_ws/src/ros_esc/test/test_q1_observed_phase_diagnostic.py')}
    old_sources = receipt_map(historical['source_files'])
    current_sources = receipt_map(diagnostic['current_source_files'])
    transitions = diagnostic['source_transitions']
    if (not isinstance(transitions, list) or len(transitions) != 3
            or any(set(item) != {'path', 'old_sha256', 'new_sha256', 'old_snapshot'}
                   for item in transitions)
            or {str(Path(item['path']).resolve()) for item in transitions} != allowed_changed
            or not old_sources.keys() <= current_sources.keys()
            or current_sources.keys() - old_sources.keys() != required_new):
        raise ValueError('Q1 observed-phase exact three transitions/four new receipts required')
    checkpoint_files = {str(Path(item['path'])): item['sha256'] for item in checkpoint['files']}
    for item in transitions:
        path = str(Path(item['path']).resolve())
        if (old_sources.get(path) != item['old_sha256']
                or current_sources.get(path) != item['new_sha256']
                or item['old_snapshot']['sha256'] != item['old_sha256']
                or checkpoint_files.get(str(Path(path).relative_to(repository))) != item['old_sha256']):
            raise ValueError('Q1 observed-phase source transition/snapshot lineage mismatch')
        _q1_verify_files([item['old_snapshot']])
    if any(current_sources[path] != digest for path, digest in old_sources.items()
           if path not in allowed_changed):
        raise ValueError('Q1 observed-phase changed an unauthorized source owner')
    effective = _q1_validate_contract(dict(historical, source_files=diagnostic['current_source_files']))

    audit_path = Path(diagnostic['confidence_audit']['path']).resolve()
    audit = json.loads(audit_path.read_text())
    audit_manifest_path = Path(diagnostic['confidence_audit_manifest']['path']).resolve()
    audit_manifest = json.loads(audit_manifest_path.read_text())
    audit_files = audit_manifest.get('files', {})
    if (audit_manifest.get('exit_code') != 0 or not isinstance(audit_files, dict)
            or audit_path.parent != audit_manifest_path.parent
            or audit_files.get(audit_path.name, {}).get('sha256') != diagnostic['confidence_audit']['sha256']
            or audit_files.get('extract.py', {}).get('sha256') != audit.get('script_sha256')
            or audit.get('version') != 'recorded_cycle_confidence_v1'
            or audit.get('inputs_and_sources_unchanged_after_extraction') is not True
            or audit.get('confirmation_opened') is not False
            or audit.get('new_numerical_reference_or_field_evaluation') is not False):
        raise ValueError('Q1 observed-phase confidence audit closure mismatch')
    audit_receipts = []
    for name, item in audit_files.items():
        path = (audit_manifest_path.parent / name).resolve()
        if path.parent != audit_manifest_path.parent:
            raise ValueError('Q1 observed-phase audit file escaped its retained directory')
        audit_receipts.append({'path': str(path), 'sha256': item['sha256']})
    _q1_verify_files(audit_receipts)

    manifest = json.loads(Path(target_files[0]['path']).read_text())
    # Whitelist only the already checked discovery run inputs and preceding
    # source/diagnostic receipts. Never follow arbitrary audit or sealed paths.
    allowed_inputs = dict(old_sources)
    allowed_inputs.update(receipt_map([diagnostic['preceding_diagnostic_contract'],
                                      diagnostic['frozen_targets'], *diagnostic['input_traces']]))
    required_inputs = dict(allowed_inputs)
    required_inputs = {path: digest for path, digest in required_inputs.items() if path not in old_sources}
    for item in manifest['input_traces']:
        inputs = receipt_map(item['run']['input_files'])
        allowed_inputs.update(inputs)
        required_inputs.update(inputs)
    # The closed D1 references.json is an allowed diagnostic input, rather
    # than permission to follow every receipt advertised by a closure.
    for path, digest in closed.items():
        if Path(path).name == 'references.json' and Path(path).parent.name == 'analysis':
            allowed_inputs[path] = digest
    audit_inputs = audit.get('input_and_source_sha256', {})
    if (not isinstance(audit_inputs, dict)
            or any(allowed_inputs.get(str(Path(path).resolve())) != digest
                   for path, digest in audit_inputs.items())
            or any(audit_inputs.get(path) != digest for path, digest in required_inputs.items())):
        raise ValueError('Q1 observed-phase confidence audit input/source lineage mismatch')
    # Changed numerical/analyzer/workflow files, if mentioned by an audit,
    # retain their historical digests through the already verified snapshots.
    _q1_verify_files([{'path': path, 'sha256': digest} for path, digest in audit_inputs.items()
                      if str(Path(path).resolve()) not in allowed_changed])
    rows = audit.get('targets', [])
    expected = {(seed, number) for seed in Q1_PARTITION_SEEDS['discovery'] for number in range(1, 13)}
    if (len(rows) != 24 or {(row['seed'], row['number']) for row in rows} != expected):
        raise ValueError('Q1 observed-phase confidence supplement must retain exact24 targets')
    return effective, {(row['seed'], row['number']): row for row in rows}


def _q1_observed_phase_latent(target, row, supplement):
    """Validate the first recorded diagnostic join, then form one fixed blend."""
    if any(supplement.get(key) != target.get(key) for key in (
            'seed', 'number', 'run_id', 'target_ns', 'source_stamp_ns', 'source_sequence')):
        raise ValueError('Q1 observed-phase supplement target/source identity mismatch')
    result = {'version': Q1_OBSERVED_PHASE_LATENT['version'], 'available': False,
              'world_vector': None, 'reason': 'missing_causal_anchor',
              'claim': 'algebraic_sensitivity_on_recorded_trajectory_not_runtime_policy'}
    if row is None:
        if (supplement.get('unavailable_reason') != 'missing_causal_anchor'
                or 'recorded' in supplement):
            raise ValueError('Q1 observed-phase missing anchor supplement mismatch')
        return result
    method = row['method']
    if (supplement.get('diagnostic_sequence') != method['diagnostic_sequence']
            or supplement.get('diagnostic_stamp_ns') != row['filter_stamp_ns']
            or supplement.get('diagnostic_bag_stamp_ns') != row['first_diagnostic_bag_stamp_ns']
            or supplement.get('observation_sha256') != row['observation_sha256']
            or supplement.get('legacy_exact_key') != row['observation_wire']['legacy_cost_source_timestamp_sec']
            or supplement.get('first_recorded_message_exact_match') is not True
            or supplement.get('readiness_eligible') is not True or row['readiness_eligible'] is not True):
        raise ValueError('Q1 observed-phase supplement first diagnostic identity mismatch')
    recorded = supplement.get('recorded', {})
    if (recorded.get('output_units') != 'cost_units_per_metre'
            or recorded.get('instant_world') != method['aligned_instant_world']
            or recorded.get('output_valid') != method['output_valid']
            or recorded.get('qualified') != method['averaging_qualified']
            or recorded.get('fallback_used') != method['fallback_used']
            or recorded.get('fallback_reason') != method['fallback_reason']
            or recorded.get('blend_allowed') != row['blend_allowed']
            or recorded.get('blend_weight') != (.5 if method['blend_applied'] else 0.0)):
        raise ValueError('Q1 observed-phase supplement recorded method mismatch')
    result.update(first_diagnostic_sequence=supplement['diagnostic_sequence'],
                  first_diagnostic_stamp_ns=supplement['diagnostic_stamp_ns'],
                  first_diagnostic_bag_stamp_ns=supplement['diagnostic_bag_stamp_ns'],
                  observation_sha256=supplement['observation_sha256'],
                  recorded_rolling_world=recorded.get('mean_world'),
                  recorded_fallback_reason=recorded['fallback_reason'])
    def finite_vector(value):
        return isinstance(value, (tuple, list)) and len(value) == 2 and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item)
            for item in value)
    mean, instant = recorded.get('mean_world'), recorded.get('instant_world')
    # The immutable audit retains the original invalid value. New receipts use
    # JSON null plus an explicit unavailable reason, never NaN/Infinity.
    if not finite_vector(mean):
        result['recorded_rolling_world'] = None
    if recorded.get('mean_full') is not True:
        result['reason'] = 'recorded_mean_not_full'
    elif recorded.get('coverage_valid') is not True:
        result['reason'] = 'recorded_mean_not_covered'
    elif not finite_vector(mean) or not finite_vector(instant):
        result['reason'] = 'recorded_mean_or_instant_missing_or_nonfinite'
    else:
        vector = [.5*x + .5*y for x, y in zip(instant, mean)]
        result.update(world_vector=vector, magnitude=math.hypot(*vector))
        result['available'] = bool(finite_vector(vector) and math.isfinite(result['magnitude'])
                                   and result['magnitude'] > 1e-6)
        result['reason'] = 'available' if result['available'] else 'latent_output_missing_or_weak'
        if not finite_vector(vector):
            result['world_vector'] = None
        if not math.isfinite(result['magnitude']):
            result['magnitude'] = None
    if method['blend_applied']:
        actual = method['v2_output_world']
        if (result['world_vector'] is None or not finite_vector(actual)
                or any(abs(x-y) > 1e-12 for x, y in zip(result['world_vector'], actual))):
            raise ValueError('Q1 observed-phase recorded actual blend disagrees with fixed50/50 sensitivity')
        result['recorded_actual_blend_match'] = True
    else:
        result['recorded_actual_blend_match'] = None
    return result


def _q1_observed_phase_latent_summary(rows):
    eligible = [row for row in rows if row['eligible']]
    paired = [row for row in eligible if row.get('latent', {}).get('error_deg') is not None
              and row.get('aligned_instant_error_deg') is not None]
    errors = [row['latent']['error_deg'] for row in paired]
    differences = [row['aligned_instant_error_deg']-row['latent']['error_deg'] for row in paired]
    return {'fixed_anchor_count': len(rows), 'eligible_informative_count': len(eligible),
            'latent_available_count': sum(row['latent']['available'] for row in rows),
            'paired_error_count': len(paired),
            'unavailable_at_eligible_count': len(eligible)-len(paired),
            'median_error_deg': float(np.median(errors)) if errors else None,
            'p90_error_deg': float(np.percentile(errors, 90)) if errors else None,
            'paired_instant_median_error_deg': float(np.median(
                [row['aligned_instant_error_deg'] for row in paired])) if paired else None,
            'improved_count': sum(value > 0 for value in differences),
            'degraded_count': sum(value < 0 for value in differences),
            'equal_count': sum(value == 0 for value in differences),
            'angular_quantile_population': 'paired_latent_and_instant_at_same_eligible_anchors',
            'unavailable_reasons': dict(Counter(row['latent']['reason'] for row in rows
                                               if not row['latent']['available'])),
            'claim': 'fixed50/50_algebraic_sensitivity_not_recorded_policy_or_qualification'}


def q1_recorded_binding(run_directory, *, source_files):
    """Bind current recorded argv/configuration and captured robot geometry.

    Unlike the historical adapter this uses the frozen dirty-source checkpoint's
    file receipts, never HEAD blobs. Geometry parsing performs no field calls.
    """
    return _recorded_geometry_binding(run_directory, source_files=source_files)


def m4_recorded_binding(run_directory, *, source_files, expected_cost_configuration=None):
    """Bind a declared noisy config to its captured bytes and actual launch.

    Nominal configurations retain the Q1 binding. A temporary noisy argv path
    is admitted only with the strict runner's independent execution witness.
    """
    if expected_cost_configuration is None:
        return q1_recorded_binding(run_directory, source_files=source_files)
    if (not isinstance(expected_cost_configuration, dict)
            or set(expected_cost_configuration) != {'path', 'sha256'}):
        raise ValueError('M4 expected cost configuration requires an exact file receipt')
    return _recorded_geometry_binding(run_directory, source_files=source_files,
                                     expected_cost_configuration=expected_cost_configuration)


def _recorded_geometry_binding(run_directory, *, source_files, expected_cost_configuration=None):
    """Shared source/selected-config/captured-geometry binding owner."""
    import xml.etree.ElementTree as ET
    from . import v2_direction_reference as reference
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    repository = next(parent for parent in Path(__file__).resolve().parents
                      if (parent / 'AGENTS.md').is_file() and (parent / 'ros2_ws').is_dir())
    launch = repository / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    verified = _q1_verify_files(source_files, required=[launch, truth.SENSOR_GEOMETRY_PATH])
    directory = Path(run_directory)
    metadata = load_yaml(directory / 'metadata.yaml')
    settings = _v2_direction_recorded_settings(metadata, launch.read_text())
    selected = {}
    captured_cost = None
    if expected_cost_configuration is not None:
        _q1_verify_files([expected_cost_configuration])
        execution = load_yaml(directory / 'scenario_result.yaml')
        captured_cost = execution.get('captured_cost_configuration')
        captured_path = directory / 'resolved_cost_function.json'
        if (execution.get('launch_argv') != metadata.get('target_argv')
                or execution.get('run_id') != metadata.get('run_id')
                or not isinstance(metadata.get('run_id'), str) or not metadata['run_id']
                or not isinstance(captured_cost, dict)
                or set(captured_cost) != {'argv_path', 'path', 'sha256'}
                or captured_cost['argv_path'] != settings['cost_function_config_filepath']
                or Path(captured_cost['path']).resolve() != captured_path.resolve()
                or captured_path.is_symlink() or not captured_path.is_file()
                or captured_cost['sha256'] != expected_cost_configuration['sha256']
                or _v2_file_hash(captured_path) != expected_cost_configuration['sha256']):
            raise ValueError('M4 captured cost bytes/path differ from exact execution and frozen configuration')
    for name in ('cost_function_config_filepath', 'filter_config_filepath', 'sensor_transform_config_filepath'):
        if name == 'cost_function_config_filepath' and captured_cost is not None:
            selected[name] = {'path': str((directory / 'resolved_cost_function.json').resolve()),
                              'sha256': captured_cost['sha256']}
            continue
        path = Path(settings[name]).expanduser().resolve()
        if str(path) not in verified:
            raise ValueError(f'Q1 selected configuration is not frozen: {name}')
        selected[name] = {'path': str(path), 'sha256': verified[str(path)]}
    if selected['filter_config_filepath']['sha256'] != reference.SELECTED_FILTER_SHA256:
        raise ValueError('Q1 filter differs from unchanged reference dynamics')
    binding = truth.sensor_geometry_binding(
        selected['sensor_transform_config_filepath']['path'], truth.SENSOR_GEOMETRY_PATH)
    reference.selected_sensor_xy([0., 0.], 0., binding)
    parameters = load_yaml(directory / 'resolved_parameters.yaml')
    descriptions = [_find_parameter(node.get('parameters', {}), 'robot_description')
                    for node in parameters.get('nodes', {}).values()]
    descriptions = [value for value in descriptions if isinstance(value, str) and value]
    if not descriptions:
        raise ValueError('Q1 captured robot_description unavailable')
    expected = {'rotating_frame_joint': ([0., 0., .355], [0., 0., 0.], [0., 0., 1.]),
                'sensor_joint': ([.18, 0., .015], [0., 0., 0.], None)}
    for description in descriptions:
        root = ET.fromstring(description)
        for name, (xyz, rpy, axis) in expected.items():
            joint = root.find(f".//joint[@name='{name}']")
            origin = joint.find('origin') if joint is not None else None
            if origin is None or ([float(v) for v in origin.get('xyz', '').split()] != xyz
                                  or [float(v) for v in origin.get('rpy', '').split()] != rpy):
                raise ValueError('Q1 captured sensor geometry differs from reference')
            if axis is not None:
                element = joint.find('axis')
                if element is None or [float(v) for v in element.get('xyz', '').split()] != axis:
                    raise ValueError('Q1 captured sensor axis differs from reference')
    return {'binding': binding, 'settings': settings, 'selected_configurations': selected,
            **({'recorded_cost_configuration_path': captured_cost['argv_path'],
                'captured_cost_configuration': captured_cost} if captured_cost is not None else {}),
            'recorded_launch_sha256': verified[str(launch)],
            'captured_robot_description_hashes': sorted(set(hashlib.sha256(value.encode()).hexdigest()
                                                          for value in descriptions))}


def _q1_verify_run(run, contract):
    directory = Path(run['run_directory']).resolve()
    if contract.get('version') in Q2_VERSIONS:
        from datetime import date
        from ros_esc.scenario_runner.run_scenario import find_run_directory, validate_run_id
        runs_root = Path(contract.get('execution', {}).get('runs_root', '')).resolve()
        run_id = validate_run_id(run['run_id'])
        planned = [item for item in contract.get('runs', []) if item.get('run_id') == run_id]
        if (len(planned) != 1 or any(run.get(name) != planned[0].get(name)
                                    for name in ('seed', 'partition', 'exposure'))):
            raise ValueError('Q2 run identity differs from its reserved partition before input reads')
        try:
            bucket = date.fromisoformat(directory.parent.name)
        except ValueError:
            raise ValueError('Q2 run directory lacks its recorder UTC-date bucket') from None
        if (directory.name != run_id or directory.parent.parent != runs_root
                or bucket.isoformat() != directory.parent.name):
            raise ValueError('Q2 run directory differs from its reserved identity before input reads')
        try:
            located = find_run_directory(runs_root, run_id).resolve()
        except RuntimeError as exc:
            raise ValueError('Q2 run directory does not have one exact recorded identity') from exc
        if located != directory:
            raise ValueError('Q2 run directory differs from the existing recorder lookup')
    required = [directory / name for name in (
        'metadata.yaml', 'resolved_topics.yaml', 'resolved_scenario.yaml', 'resolved_parameters.yaml',
        'bag/metadata.yaml')]
    databases = sorted((directory / 'bag').glob('*.db3'))
    if not databases:
        raise ValueError('Q1 input has no retained SQLite bag files')
    _q1_verify_files(run['input_files'], required=required + databases)
    if contract.get('version') in Q2_VERSIONS:
        metadata = load_yaml(directory / 'metadata.yaml')
        if metadata.get('scenario_runner', {}).get('direction_policy') != contract['direction_policy']:
            raise ValueError('Q2 recorded policy differs from its frozen descriptor')
    if 'runs' in contract:
        planned = [item for item in contract['runs'] if item['run_id'] == run['run_id']]
        if (len(planned) != 1 or any(run.get(name) != planned[0].get(name)
                                    for name in ('seed', 'partition', 'exposure'))):
            raise ValueError('Q1 retained run differs from reserved contract population')
        scenario = load_yaml(directory / 'resolved_scenario.yaml')
        metadata = load_yaml(directory / 'metadata.yaml')
        if (scenario != planned[0]['resolved_scenario']
                or metadata.get('target_argv') != planned[0]['launch_argv']):
            raise ValueError('Q1 retained scenario/control argv differs from planned acquisition')
    binding = q1_recorded_binding(directory, source_files=contract['source_files'])
    if binding != run['binding']:
        raise ValueError('Q1 recorded binding differs from frozen study manifest')
    model = binding['selected_configurations']['cost_function_config_filepath']
    if model != run['model_configuration']:
        raise ValueError('Q1 model configuration differs from selected recorded model')


def _q1_nomination(reference, contract_hash):
    if not isinstance(reference, dict):
        raise ValueError('Q1 confirmation requires an immutable discovery nomination receipt')
    _q1_verify_files([reference])
    result = json.loads(Path(reference['path']).read_text())
    parameters = result.get('parameters', {})
    if (result.get('status') != 'PASS' or result.get('partition') != 'discovery'
            or result.get('contract_sha256') != contract_hash
            or parameters.get('window_seconds') != 6 or parameters.get('epsilon_m') != .30
            or parameters.get('radius_m') not in (.25, .5, .75)
            or parameters.get('candidate_epsilon_m') not in (.05, .10, .15)):
        raise ValueError('Q1 confirmation nomination is missing or invalid')
    return result


def _q2_evaluation_receipt(reference, contract_hash, partition, study_manifest, *, parameters=None,
                           version=Q2_VERSION):
    """Validate completed saved selection arithmetic; never rerun a detector."""
    if version not in Q2_VERSIONS:
        raise ValueError('unsupported Q2 evaluation version')
    if not isinstance(reference, dict) or set(reference) != {'path', 'sha256'}:
        raise ValueError('Q2 completed evaluation requires a file receipt')
    evaluation_directory = Path(reference['path']).resolve().parent
    directory_name = 'discovery_nomination' if partition == 'discovery' else 'confirmation_evaluation'
    if evaluation_directory.name != directory_name:
        raise ValueError('Q2 evaluation receipt is outside its declared partition directory')
    filename = 'nomination.json' if partition == 'discovery' else 'confirmation.json'
    if Path(reference['path']).resolve() != evaluation_directory/filename:
        raise ValueError('Q2 evaluation receipt filename differs from its partition')
    _q1_verify_files([reference])
    result = json.loads(Path(reference['path']).read_text())
    count = 9 if partition == 'discovery' else 1
    if (result.get('version') != version or result.get('partition') != partition
            or result.get('contract_sha256') != contract_hash
            or result.get('settings_evaluated') != count
            or len(result.get('setting_receipts', [])) != count
            or result.get('selection_rule') != 'smallest_radius_then_smallest_candidate_epsilon'):
        raise ValueError('Q2 completed evaluation identity or setting population invalid')
    label_path = evaluation_directory.parent/f'{partition}_labels/labels_manifest.json'
    if (not isinstance(result.get('labels'), dict)
            or Path(result['labels'].get('path', '')).resolve() != label_path
            or any(not isinstance(ref, dict) or Path(ref.get('path', '')).resolve()
                   != evaluation_directory/f'setting_{index+1}.json'
                   for index, ref in enumerate(result['setting_receipts']))):
        raise ValueError('Q2 evaluation child receipt would cross its partition boundary')
    _q1_verify_files([result['labels']])
    _q1_verify_files([study_manifest])
    study = json.loads(Path(study_manifest['path']).read_text())
    labels = json.loads(Path(result['labels']['path']).read_text())
    if (study.get('version') != version or labels.get('version') != version or labels.get('status') != 'FROZEN'
            or labels.get('partition') != partition or labels.get('study_manifest') != study_manifest
            or labels.get('contract') != study.get('contract')
            or study.get('contract', {}).get('sha256') != contract_hash):
        raise ValueError('Q2 evaluation is not bound to its frozen study labels')
    expected = ([{'window_seconds': 6, 'epsilon_m': .30, 'radius_m': radius,
                  'candidate_epsilon_m': epsilon}
                 for radius in (.25, .5, .75) for epsilon in (.05, .10, .15)]
                if partition == 'discovery' else [parameters])
    settings = []
    for receipt, selected in zip(result['setting_receipts'], expected):
        _q1_verify_files([receipt])
        setting = json.loads(Path(receipt['path']).read_text())
        runs = setting.get('runs', [])
        expected_runs = {(f'{version}-{partition}-{exposure}-{seed}', seed, partition, exposure)
                         for exposure, seed in zip(('residence', 'approach'), qualification_partition_seeds(version)[partition])}
        if (setting.get('version') != version or setting.get('partition') != partition
                or setting.get('contract_sha256') != contract_hash
                or setting.get('labels') != result['labels'] or setting.get('parameters') != selected
                or len(runs) != 2
                or {(r.get('run', {}).get('run_id'), r.get('run', {}).get('seed'),
                     r.get('run', {}).get('partition'), r.get('run', {}).get('exposure'))
                    for r in runs} != expected_runs
                or any(r.get('status') not in ('PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE') for r in runs)):
            raise ValueError('Q2 setting receipt differs from its finite evaluation')
        status = ('FAIL' if any(r['status'] == 'FAIL' for r in runs) else
                  'EVIDENCE_UNAVAILABLE' if any(r['status'] != 'PASS' for r in runs) else 'PASS')
        if setting.get('status') != status:
            raise ValueError('Q2 setting status contradicts its saved run outcomes')
        settings.append(setting)
    passing = next((s for s in settings if s['status'] == 'PASS'), None)
    status = ('PASS' if passing else 'EVIDENCE_UNAVAILABLE'
              if any(s['status'] == 'EVIDENCE_UNAVAILABLE' for s in settings) else 'FAIL')
    if (result.get('status') != status or
            result.get('parameters') != (passing['parameters'] if passing else None)):
        raise ValueError('Q2 nomination contradicts its saved setting outcomes')
    return result


def _q2_reference_branch(qualification_result_path, contract_ref):
    """A completed label job alone may open the declared Q2 reference branch."""
    path = Path(qualification_result_path).resolve()
    reference = {'path': str(path), 'sha256': _v2_file_hash(path)}
    job = json.loads(path.read_text())
    _q1_verify_files([contract_ref])
    version = json.loads(Path(contract_ref['path']).read_text()).get('version')
    if (version not in Q2_VERSIONS or job.get('version') != version or job.get('contract') != contract_ref
            or job.get('completed') is not True or job.get('integrity_errors') != []):
        raise ValueError('Q2 reference requires a complete integrity-valid label job')
    if (not isinstance(job.get('study_manifest'), dict)
            or Path(job['study_manifest'].get('path', '')).resolve() != path.parent.parent/'study_manifest.json'):
        raise ValueError('Q2 label job does not bind its acquisition study manifest path')
    _q1_verify_files([job['study_manifest']])
    discovery_ref = job.get('discovery_nomination')
    if (not isinstance(discovery_ref, dict) or Path(discovery_ref.get('path', '')).resolve()
            != path.parent/'discovery_nomination/nomination.json'):
        raise ValueError('Q2 reference requires its discovery nomination path before any read')
    discovery = _q2_evaluation_receipt(discovery_ref, contract_ref['sha256'],
                                     'discovery', job['study_manifest'], version=version)
    if job.get('discovery') != discovery:
        raise ValueError('Q2 label job differs from its completed nomination receipt')
    if discovery['status'] == 'PASS':
        _q1_nomination(discovery_ref, contract_ref['sha256'])
        confirmation_ref = job.get('confirmation_evaluation')
        if (not isinstance(confirmation_ref, dict) or Path(confirmation_ref.get('path', '')).resolve()
                != path.parent/'confirmation_evaluation/confirmation.json'):
            raise ValueError('Q2 held confirmation receipt path differs from the label job')
        confirmation = _q2_evaluation_receipt(job.get('confirmation_evaluation'),
            contract_ref['sha256'], 'confirmation', job['study_manifest'],
            parameters=discovery['parameters'], version=version)
        if (confirmation.get('nomination') != discovery_ref
                or job.get('confirmation') != confirmation or job.get('status') != confirmation['status']
                or job.get('reference_branch') != 'qualification48'):
            raise ValueError('Q2 qualification branch lacks its bound held confirmation evaluation')
        branch = 'qualification48'
    else:
        if (job.get('confirmation_evaluation') is not None
                or job.get('confirmation') != 'SEALED_NOT_OPENED'
                or job.get('status') != discovery['status']
                or job.get('reference_branch') != 'discovery24_diagnostic'):
            raise ValueError('Q2 discovery diagnostic would cross the confirmation seal')
        branch = 'discovery24_diagnostic'
    return {'branch': branch, 'job': job, 'receipt': reference,
            'nomination': discovery_ref if branch == 'qualification48' else None}


def freeze_q1_direction_targets(study_manifest_path, output_directory, *, partition,
                                nomination_manifest=None):
    """Freeze one sealed partition's 24 input/target identities before references.

    The shared acquisition manifest declares all four slots/runs. Confirmation
    input is not read before a hashed passing discovery nomination is supplied.
    No field or mathematical filter output is calculated by this operation.
    """
    from .v2_enclosure import atomic_exclusive_json
    from .v2_direction_reference import select_causal_anchor
    manifest_path = Path(study_manifest_path).resolve()
    manifest_hash = _v2_file_hash(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    contract_ref = manifest['contract']
    contract = _q1_contract(contract_ref)
    version = contract['version']
    seeds = qualification_partition_seeds(version)
    if manifest.get('version') != version or partition not in seeds:
        raise ValueError('Q1 manifest version or partition invalid')
    runs = manifest['runs']
    if (len(runs) != 4 or len({run['run_id'] for run in runs}) != 4
            or any(sorted(run['seed'] for run in runs if run['partition'] == name) != list(seeds)
                   for name, seeds in seeds.items())):
        raise ValueError('Q1 fixed four-run population changed')
    if partition == 'confirmation':
        if version in Q2_VERSIONS:
            _q2_evaluation_receipt(nomination_manifest, contract_ref['sha256'], 'discovery',
                                  {'path': str(manifest_path), 'sha256': manifest_hash}, version=version)
        _q1_nomination(nomination_manifest, contract_ref['sha256'])
    elif nomination_manifest is not None:
        raise ValueError('Q1 discovery cannot consume a nomination')
    selected = sorted((run for run in runs if run['partition'] == partition), key=lambda run: run['seed'])
    # Verify all selected files before publishing any new attempt or reading bags.
    for run in selected:
        _q1_verify_run(run, contract)
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=False)
    common = {'version': version, 'contract': contract_ref,
              'study_manifest': {'path': str(manifest_path), 'sha256': manifest_hash},
              'partition': partition, 'nomination': nomination_manifest,
              'fixed_anchor_count': 24, 'status': 'INCOMPLETE'}
    atomic_exclusive_json(output / 'started.json', common)
    targets, input_traces = [], []
    for run in selected:
        directory = Path(run['run_directory'])
        metadata = load_yaml(directory / 'metadata.yaml')
        resolved = load_yaml(directory / 'resolved_topics.yaml')
        config = metadata['scenario_runner']['v2_identity']['stream_config']
        topics = {entry['topic']: entry['alias'] for entry in resolved['topics']}
        topic_set = {config[name] for name in ('raw_cost_topic', 'augmented_cost_topic', 'provenance_topic',
                     'objective_cost_topic', 'pose_topic', 'encoder_topic', 'timekeeper_topic')}
        aliases = {topics[topic] for topic in topic_set} | {'v2_direction_diagnostics'}
        if version in Q2_VERSIONS:
            aliases.add('v2_direction_policy_diagnostics')
        bag = read_run_bag(directory, aliases=aliases)
        if version in Q2_VERSIONS:
            observations, qualification = prepare_moving_policy_direction_inputs(
                bag, metadata, run_spec=run)
            if qualification['integrity_errors']:
                raise ValueError('Q2 typed integrity error prevents target freeze')
        else:
            observations, qualification = prepare_q1_direction_inputs(
                bag, metadata, contract=contract, run_spec=run)
        path = output / f'inputs_{run["seed"]}.json'
        digest = atomic_exclusive_json(path, {'version': version, 'run': run,
                    'qualification': qualification, 'observations': observations})
        input_traces.append({'path': str(path), 'sha256': digest, 'run': run})
        origin = qualification['origin_ns']
        for number, offset in enumerate(contract['reference']['target_offsets_sec'], 1):
            target = None if origin is None else origin + int(offset*1_000_000_000)
            index = select_causal_anchor(observations, target)
            targets.append({'run_id': run['run_id'], 'seed': run['seed'], 'partition': partition,
                            'number': number, 'target_ns': target, 'observation_index': index,
                            'source_sequence': observations[index]['source_sequence'] if index is not None else None,
                            'source_stamp_ns': observations[index]['stamp_ns'] if index is not None else None,
                            'input_trace_path': str(path), 'input_trace_sha256': digest})
        # Raw integrity failures stop qualification; every target remains retained.
    _q1_contract(contract_ref)
    for run in selected:
        _q1_verify_run(run, contract)
    if _v2_file_hash(manifest_path) != manifest_hash:
        raise ValueError('Q1 study manifest changed during input freeze')
    result = {**common, 'status': 'FROZEN', 'input_traces': input_traces, 'targets': targets}
    atomic_exclusive_json(output / 'targets.json', result)
    return result


def _q1_reference_summary(results, *, partition=None):
    rows = [row for row in results if partition is None or row['partition'] == partition]
    eligible = [row for row in rows if row.get('eligible')]
    usable = [row for row in eligible if row.get('method', {}).get('usable_averaging')]
    errors = [row['v2_error_deg'] for row in eligible if row.get('v2_error_deg') is not None]
    instantaneous = [row['aligned_instant_error_deg'] for row in eligible
                     if row.get('aligned_instant_error_deg') is not None]
    return {'fixed_anchor_count': len(rows), 'eligible_informative_count': len(eligible),
            'causal_anchor_count': sum(row['causal_anchor_available'] for row in rows),
            'input_cycle_qualified_count': sum(row.get('cycle', {}).get('qualified', False) for row in rows),
            'informative_reference_count': sum(row.get('informative', False) for row in rows),
            'usable_averaging_count': len(usable),
            'blend_applied_count': sum(row.get('method', {}).get('blend_applied', False) for row in eligible),
            'missing_or_weak_output_count': len(eligible)-len(errors),
            'fallback_count': sum(row.get('method', {}).get('fallback_used', False) for row in eligible),
            'averaging_availability': len(usable)/len(eligible) if eligible else None,
            'v2_median_error_deg': statistics.median(errors) if errors else None,
            'v2_p90_error_deg': float(np.percentile(errors, 90)) if errors else None,
            'aligned_instant_median_error_deg': statistics.median(instantaneous) if instantaneous else None,
            'angular_quantile_population': 'usable_recorded_vectors_at_eligible_anchors',
            'unavailable_reasons': dict(Counter(row['reason'] for row in rows if row.get('reason')))}


def _q1_plain(value):
    """Convert numerical-owner scalar types without changing any result value."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _q1_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_q1_plain(item) for item in value]
    return value


def evaluate_q1_direction_references(frozen_targets_paths, output_directory, *, contract_path,
                                     diagnostic_contract_path=None,
                                     observed_phase_contract_path=None,
                                     qualification_result_path=None):
    """One bounded reference batch with an explicit, separately bound diagnostic.

    Caller must use timeout300s. All inputs, owners and nomination are verified
    before the first model instance. The selected numerical method performs all
    field calculations. The default requires both fixed48 qualification partitions.
    Only an explicit diagnostic contract permits the original discovery24,
    with no qualification or confirmation authority. Preserve partial receipts.
    """
    from . import v2_direction_reference as numeric
    from .v2_enclosure import atomic_exclusive_json
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    moving_study = qualification_result_path is not None
    branch = None
    contract_ref = {'path': str(Path(contract_path).resolve()), 'sha256': _v2_file_hash(contract_path)}
    if moving_study:
        if diagnostic_contract_path is not None or observed_phase_contract_path is not None:
            raise ValueError('Q2 qualification cannot use historical diagnostic lineage')
        contract = _q1_contract(contract_ref)
        if contract['version'] not in Q2_VERSIONS:
            raise ValueError('Q2 qualification result cannot select an old study')
        # Determine authority before hashing/reading any supplied target file.
        branch = _q2_reference_branch(qualification_result_path, contract_ref)
        count = 2 if branch['branch'] == 'qualification48' else 1
        if isinstance(frozen_targets_paths, (str, Path)) or len(frozen_targets_paths) != count:
            raise ValueError('Q2 reference paths differ from the completed nomination branch')
        analysis_root = Path(branch['receipt']['path']).parent
        authorized_paths = [analysis_root/'discovery_targets/targets.json']
        if count == 2:
            authorized_paths.append(analysis_root/'confirmation_targets/targets.json')
        if [Path(p).resolve() for p in frozen_targets_paths] != authorized_paths:
            raise ValueError('Q2 target paths would cross the declared partition boundary')
    if diagnostic_contract_path is not None and observed_phase_contract_path is not None:
        raise ValueError('Q1 reference diagnostic selectors are mutually exclusive')
    observed_phase = observed_phase_contract_path is not None
    selected_diagnostic_path = (observed_phase_contract_path if observed_phase else diagnostic_contract_path)
    diagnostic_ref = None
    if selected_diagnostic_path is not None:
        diagnostic_ref = {'path': str(Path(selected_diagnostic_path).resolve()),
                          'sha256': _v2_file_hash(selected_diagnostic_path)}
        declared = json.loads(Path(diagnostic_ref['path']).read_text())
        if (isinstance(frozen_targets_paths, (str, Path)) or len(frozen_targets_paths) != 1
                or str(Path(frozen_targets_paths[0]).resolve())
                != str(Path(declared['frozen_targets']['path']).resolve())):
            raise ValueError('Q1 diagnostic requires its one frozen discovery manifest')
    elif not moving_study and (isinstance(frozen_targets_paths, (str, Path)) or len(frozen_targets_paths) != 2):
        raise ValueError('Q1 reference requires both fixed partition manifests')
    files = [{'path': str(Path(path).resolve()), 'sha256': _v2_file_hash(path)}
             for path in frozen_targets_paths]
    supplements = {}
    if observed_phase:
        contract, supplements = _q1_observed_phase_contract(diagnostic_ref, contract_ref, files)
    elif not moving_study:
        contract = (_q1_discovery_direction_contract(diagnostic_ref, contract_ref, files)
                    if diagnostic_ref is not None else _q1_contract(contract_ref))
    if contract['version'] in Q2_VERSIONS and not moving_study:
        raise ValueError('Q2 reference requires the completed qualification-result selector')
    seeds = qualification_partition_seeds(contract['version'])
    discovery_only = diagnostic_ref is not None or (moving_study and branch['branch'] == 'discovery24_diagnostic')
    manifests = [json.loads(Path(item['path']).read_text()) for item in files]
    partitions = {'discovery'} if discovery_only else set(seeds)
    if {manifest['partition'] for manifest in manifests} != partitions:
        raise ValueError('Q1 reference population lacks one fixed partition')
    traces, targets = {}, []
    for manifest, manifest_file in zip(manifests, files):
        if (manifest['version'] != contract['version'] or manifest['contract'] != contract_ref
                or manifest['status'] != 'FROZEN' or manifest['fixed_anchor_count'] != 24
                or len(manifest['targets']) != 24):
            raise ValueError('Q1 frozen target contract mismatch')
        if moving_study and manifest['study_manifest'] != branch['job']['study_manifest']:
            raise ValueError('Q2 targets belong to another completed label job')
        _q1_verify_files([manifest['study_manifest']])
        if manifest['partition'] == 'confirmation':
            _q1_nomination(manifest['nomination'], contract_ref['sha256'])
            if moving_study and manifest['nomination'] != branch['nomination']:
                raise ValueError('Q2 confirmation target used another nomination')
        if moving_study:
            expected_runs = {(slot['run_id'], slot['seed'], slot['partition'], slot['exposure'])
                             for slot in contract['planned_reference_slots']
                             if slot['partition'] == manifest['partition']}
            receipts = manifest.get('input_traces', [])
            if (len(receipts) != 2 or
                    {(r.get('run', {}).get('run_id'), r.get('run', {}).get('seed'),
                      r.get('run', {}).get('partition'), r.get('run', {}).get('exposure'))
                     for r in receipts} != expected_runs
                    or any(Path(r['path']).resolve() != Path(manifest_file['path']).parent/f"inputs_{r['run']['seed']}.json"
                           for r in receipts)):
                raise ValueError('Q2 input trace receipt would cross its selected partition')
        for receipt in manifest['input_traces']:
            _q1_verify_files([receipt])
            run = receipt['run']
            _q1_verify_run(run, contract)
            trace = json.loads(Path(receipt['path']).read_text())
            if trace['run'] != run or run['run_id'] in traces:
                raise ValueError('Q1 input trace identity reused or changed')
            if moving_study and (trace.get('version') != contract['version']
                    or trace['qualification'].get('version') != MOVING_POLICY_INPUT_VERSION
                    or trace['qualification'].get('integrity_errors') != []):
                raise ValueError('Q2 trace lacks intact moving-policy input qualification')
            traces[run['run_id']] = (trace, receipt)
        targets.extend(manifest['targets'])
    expected = {(seed, number) for partition in partitions
                for seed in seeds[partition] for number in range(1, 13)}
    fixed_count = 24 if discovery_only else 48
    if len(targets) != fixed_count or {(target['seed'], target['number']) for target in targets} != expected:
        raise ValueError(f'Q1 fixed {fixed_count} target identities changed')
    for target in targets:
        trace, receipt = traces[target['run_id']]
        rows = trace['observations']
        origin = trace['qualification']['origin_ns']
        expected_time = None if origin is None else origin + target['number']*10_000_000_000
        index = numeric.select_causal_anchor(rows, expected_time)
        if (target['seed'] != trace['run']['seed'] or target['partition'] != trace['run']['partition']
                or target['input_trace_path'] != receipt['path']
                or target['input_trace_sha256'] != receipt['sha256']
                or target['target_ns'] != expected_time or target['observation_index'] != index
                or target['source_sequence'] != (rows[index]['source_sequence'] if index is not None else None)
                or target['source_stamp_ns'] != (rows[index]['stamp_ns'] if index is not None else None)):
            raise ValueError('Q1 anchor no longer matches frozen input-only selection')
    latent = {}
    if observed_phase:
        for target in targets:
            rows = traces[target['run_id']][0]['observations']
            index = target['observation_index']
            key = (target['seed'], target['number'])
            latent[key] = _q1_observed_phase_latent(
                target, rows[index] if index is not None else None, supplements[key])

    def recheck_inputs():
        if moving_study:
            _q1_contract(contract_ref)
            if _q2_reference_branch(qualification_result_path, contract_ref) != branch:
                raise ValueError('Q2 completed branch authority changed during references')
        elif observed_phase:
            _q1_observed_phase_contract(diagnostic_ref, contract_ref, files)
        elif diagnostic_ref is not None:
            _q1_discovery_direction_contract(diagnostic_ref, contract_ref, files)
        else:
            _q1_contract(contract_ref)
        _q1_verify_files(files)
        for manifest in manifests:
            _q1_verify_files([manifest['study_manifest']])
            if manifest['nomination'] is not None:
                _q1_nomination(manifest['nomination'], contract_ref['sha256'])
            for receipt in manifest['input_traces']:
                _q1_verify_files([receipt])
                _q1_verify_run(receipt['run'], contract)

    if diagnostic_ref is not None or moving_study:
        recheck_inputs()
    version = (contract['version'] if moving_study else Q1_OBSERVED_PHASE_VERSION if observed_phase else
               Q1_DISCOVERY_DIRECTION_VERSION if diagnostic_ref is not None else Q1_VERSION)
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = {'version': version, 'status': 'INCOMPLETE', 'contract': contract_ref,
               'target_manifests': files, 'fixed_anchor_count': fixed_count}
    if diagnostic_ref is not None:
        started.update(diagnostic_contract=diagnostic_ref, qualification_status='NOT_EVALUATED',
                       nomination=None, confirmation='SEALED', pilot_released=False)
    if observed_phase:
        started.update(observed_phase_contract=diagnostic_ref,
                       reference_method=Q1_OBSERVED_PHASE_METHOD, latent_blend=Q1_OBSERVED_PHASE_LATENT)
    if moving_study:
        started.update(qualification_result=branch['receipt'], reference_branch=branch['branch'],
                       planned_anchor_count=48, reference_method=contract['reference']['method'])
    atomic_exclusive_json(output / 'started.json', started)
    results, models = [], {}
    for target in sorted(targets, key=lambda row: (row['seed'], row['number'])):
        trace, _ = traces[target['run_id']]
        rows, run = trace['observations'], trace['run']
        index = target['observation_index']
        result = {**target, 'causal_anchor_available': index is not None, 'qualified': False,
                  'informative': False, 'eligible': False, 'reason': 'missing_causal_anchor',
                  'exact_m2_source_provenance': True, 'objective_reconstructable': False,
                  'numerically_qualified': False}
        if observed_phase:
            result['latent'] = dict(latent[(target['seed'], target['number'])])
        if index is not None:
            row = rows[index]
            cycle = (numeric.observed_phase_cycle(rows, index) if observed_phase or moving_study
                     else numeric.reference_cycle(rows, index))
            result.update(cycle=cycle, method=row['method'],
                          first_diagnostic_stamp_ns=row['filter_stamp_ns'],
                          input_state_valid=row['filter_state_valid'], input_state=row['filter_state'],
                          objective_reconstructable=bool(row['objective']['complete']),
                          reason=cycle['reason'])
            if cycle['qualified'] and row['objective']['complete']:
                if (diagnostic_ref is not None or moving_study) and run['run_id'] not in models:
                    recheck_inputs()
                try:
                    if run['run_id'] not in models:
                        scenario = load_yaml(Path(run['run_directory']) / 'resolved_scenario.yaml')
                        model, _ = truth._model(scenario['sources'], run['model_configuration']['path'],
                                               run['binding']['binding'])
                        models[run['run_id']] = model, scenario
                    model, scenario = models[run['run_id']]
                    objective = numeric.augmented_objective(
                        lambda x, y, angle: truth.evaluate_raw_cost(model, x, y, angle),
                        base_xy=row['xy'], binding=run['binding']['binding'],
                        weights=row['objective']['weights'],
                        gaussian_fills=row['objective']['gaussian_fills'],
                        affine_terms=row['objective']['affine_terms'])
                    if observed_phase or moving_study:
                        reference = numeric.observed_phase_reference(
                            objective, cycle=cycle, xy=row['xy'], sources=scenario['sources'])
                        result.update(reference)
                        result.update(numerically_qualified=reference['qualified'],
                                      objective_snapshot=row['objective'])
                    else:
                        harmonics = numeric.integrate_stationary_harmonics(
                            objective, xy=row['xy'], sources=scenario['sources'])
                        result.update(numeric.stationary_reference(
                            harmonics, omega_rad_sec=cycle['omega_rad_sec'], step_sec=cycle['uniform_step_sec']))
                        result.update(harmonics=harmonics, numerically_qualified=harmonics['qualified'],
                                      objective_snapshot=row['objective'])
                    result['eligible'] = bool(result['informative'] and row['blend_allowed'])
                    if result['informative']:
                        result['aligned_instant_error_deg'] = numeric.angular_error_deg(
                            row['method']['aligned_instant_world'], result['world_vector'])
                        result['v2_error_deg'] = numeric.angular_error_deg(
                            row['method']['v2_output_world'], result['world_vector'])
                        if observed_phase and result['eligible'] and result['latent']['available']:
                            result['latent']['error_deg'] = numeric.angular_error_deg(
                                result['latent']['world_vector'], result['world_vector'])
                            if (result['latent']['error_deg'] is not None
                                    and result['aligned_instant_error_deg'] is not None):
                                result['latent']['improvement_over_instant_deg'] = (
                                    result['aligned_instant_error_deg']-result['latent']['error_deg'])
                except TimeoutError:
                    raise
                except (ValueError, ArithmeticError) as exc:
                    result['reason'] = f'objective_or_reference_unavailable: {exc}'
        result = _q1_plain(result)
        atomic_exclusive_json(output / f'anchor_{target["seed"]}_{target["number"]:02d}.json', result)
        results.append(result)
    recheck_inputs()
    per_run = {run_id: _q1_reference_summary([row for row in results if row['run_id'] == run_id])
               for run_id in traces}
    confirmation = _q1_reference_summary(results, partition='confirmation')
    enough = all(per_run[run_id]['eligible_informative_count'] >= 6
                 for run_id, (trace, _) in traces.items() if trace['run']['partition'] == 'confirmation')
    passed = (enough and confirmation['v2_median_error_deg'] is not None
              and confirmation['v2_median_error_deg'] <= 30
              and confirmation['v2_p90_error_deg'] <= 60
              and confirmation['averaging_availability'] >= .8)
    summary = {'version': version, 'status': 'PASS' if passed else ('FAIL' if enough else 'EVIDENCE_UNAVAILABLE'),
               'contract': contract_ref, 'target_manifests': files, 'results': results,
               'all': _q1_reference_summary(results), 'confirmation': confirmation, 'per_run': per_run,
               'claim': 'selected_primary_field_stationary_reference_of_recorded_aligned_GESC_outputs',
               'legacy_callback_reconstruction': False, 'pilot_released': False}
    if diagnostic_ref is not None:
        summary.update(status='COMPLETE_DIAGNOSTIC', diagnostic_contract=diagnostic_ref,
                       qualification_status='NOT_EVALUATED', nomination=None, confirmation='SEALED',
                       fixed_anchor_count=24,
                       claim='discovery_only_stationary_reference_of_recorded_aligned_GESC_outputs')
    if observed_phase:
        summary.update(observed_phase_contract=diagnostic_ref,
                       reference_method=Q1_OBSERVED_PHASE_METHOD, latent_blend=Q1_OBSERVED_PHASE_LATENT,
                       latent=_q1_observed_phase_latent_summary(results),
                       latent_per_run={run_id: _q1_observed_phase_latent_summary(
                           [row for row in results if row['run_id'] == run_id]) for run_id in traces},
                       claim='discovery_only_stationary_position_observed_phase_periodic_reference')
    if moving_study:
        detector_status = branch['job']['status']
        direction_status = 'NOT_EVALUATED' if discovery_only else summary['status']
        combined = ('NOT_EVALUATED' if discovery_only else
                    'FAIL' if 'FAIL' in (detector_status, direction_status) else
                    'EVIDENCE_UNAVAILABLE' if 'EVIDENCE_UNAVAILABLE' in (detector_status, direction_status) else 'PASS')
        summary.update(
            status='COMPLETE_DIAGNOSTIC' if discovery_only else direction_status,
            qualification_result=branch['receipt'], reference_branch=branch['branch'],
            detector_qualification_status=detector_status,
            direction_qualification_status=direction_status,
            combined_qualification_status=combined,
            reference_method=contract['reference']['method'],
            planned_anchor_count=48, fixed_anchor_count=fixed_count,
            confirmation='SEALED' if discovery_only else confirmation,
            sealed_slots=([dict(slot, status='SEALED') for slot in contract['planned_reference_slots']
                           if slot['partition'] == 'confirmation'] if discovery_only else []),
            claim='stationary_position_observed_phase_reference_of_actual_recorded_075_policy',
        )
    atomic_exclusive_json(output / 'references.json', summary)
    return summary


def _run_parser():
    parser = argparse.ArgumentParser(
        description='Analyze one Phase 05/06 GESC/Gaussian run directory.',
    )
    parser.add_argument('run_directory')
    parser.add_argument('--output-dir')
    parser.add_argument('--channel-index', type=int)
    parser.add_argument('--sync-tolerance-sec', type=float)
    parser.add_argument('--state-duration-basis',
                        choices=('bag_receipt_v1', 'simulation_publication_v1'),
                        default='bag_receipt_v1')
    return parser


def _matrix_parser():
    parser = argparse.ArgumentParser(
        description='Summarize existing Phase 07 per-run analyses.',
    )
    parser.add_argument('inputs', nargs='+')
    parser.add_argument('--output-dir', required=True)
    return parser


def main(argv=None):
    """CLI entry point for one-run analysis."""
    arguments = _run_parser().parse_args(argv)
    try:
        result = analyze_run(
            arguments.run_directory,
            output_directory=arguments.output_dir,
            channel_index=arguments.channel_index,
            sync_tolerance_sec=arguments.sync_tolerance_sec,
            **({'state_duration_basis': arguments.state_duration_basis}
               if arguments.state_duration_basis != 'bag_receipt_v1' else {}),
        )
    except Exception as exc:
        print(
            f'analysis failed: {type(exc).__name__}: {exc}',
            file=sys.stderr,
        )
        return 2
    print(json.dumps({
        'run_id': result['run_id'],
        'analysis_status': result['analysis_status'],
    }, sort_keys=True))
    return 0


def main_matrix(argv=None):
    """CLI entry point for matrix summary aggregation."""
    arguments = _matrix_parser().parse_args(argv)
    try:
        result = summarize_matrix(arguments.inputs, arguments.output_dir)
    except Exception as exc:
        print(
            f'matrix summary failed: {type(exc).__name__}: {exc}',
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
