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
    causal_record,
    load_yaml,
    NANOSECONDS_PER_SECOND,
    nearest_record,
    read_run_bag,
    records_for_alias,
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
        source, skew = nearest_record(
            sources, timestamp, tolerance_ns, 'ros_timestamp_ns'
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
        gesc_record, skew = nearest_record(
            gesc, timestamp, tolerance_ns, 'ros_timestamp_ns'
        )
        _sync_match(
            row, 'gesc', gesc_record, skew,
            lambda item: {
                'gesc_output_x': _value_at(item.filter_output, 0),
                'gesc_output_y': _value_at(item.filter_output, 1),
            },
        )
        pose_record, skew = nearest_record(
            odometry, timestamp, tolerance_ns, 'ros_timestamp_ns'
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
        control_record, skew = nearest_record(
            control, timestamp, tolerance_ns, 'ros_timestamp_ns'
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
        state_record, skew = causal_record(
            states, timestamp, tolerance_ns, 'ros_timestamp_ns'
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


def _state_intervals(records, readiness_start, readiness_end, rate_hz):
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


def _escape_attempts(state_records, event_records, odometry_records, end_ns):
    sequence = _collapsed_states(state_records)
    escape_states = {
        AlgorithmState.STATE_ESCAPE_REPULSE,
        AlgorithmState.STATE_ESCAPE_ASSIST,
    }
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
            and sequence[cursor]['state'] in escape_states
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


def _revisit_count(odometry, fills, attempts):
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


def _event_names():
    return {
        int(value): name
        for name, value in vars(AlgorithmEvent).items()
        if name.startswith('EVENT_') and isinstance(value, int)
    }


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
    goal_ids = ground_truth.get('goal_source_ids', [])
    tolerance = ground_truth.get('final_position_tolerance_m')
    if not goal_ids or not _finite(tolerance) or not odometry:
        return unavailable(
            'ground-truth goal IDs, tolerance, or final pose are unavailable',
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
        provenance='final odometry and Phase 06 ground-truth contract',
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
                provenance='absolute unwrapped odometry angle about frozen center',
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
        'revisit_count': _revisit_count(odometry, fill_records, attempts),
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
        'collision': unavailable(
            'no audited collision/contact truth topic exists',
            unit='boolean',
            provenance='Phase 00/06 interface audit',
        ),
        'event_counts': metric(
            dict(sorted(event_counts.items())),
            unit='events by type',
            provenance='/gesc_gaussian/algorithm_events',
        ),
    }


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


def analyze_run(
    run_directory,
    output_directory=None,
    channel_index=None,
    sync_tolerance_sec=None,
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
    supervisor_rate, rate_source = _resolved_setting(
        run_directory,
        None,
        'supervisor_publish_rate_hz',
        20.0,
    )
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
        )
        attempts = _escape_attempts(
            readiness_states,
            readiness_events,
            readiness_odometry,
            bag_data.readiness_end_ns,
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
            'gaussian_history.csv': fill_rows,
            'escape_attempts.csv': attempts,
        }
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
        )
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
        }
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


def _run_parser():
    parser = argparse.ArgumentParser(
        description='Analyze one Phase 05/06 GESC/Gaussian run directory.',
    )
    parser.add_argument('run_directory')
    parser.add_argument('--output-dir')
    parser.add_argument('--channel-index', type=int)
    parser.add_argument('--sync-tolerance-sec', type=float)
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
