#!/usr/bin/env python3

"""Offline run-completeness validator for unified GESC/Gaussian recordings."""

import argparse
import json
import math
from pathlib import Path
import sys

from rclpy.serialization import deserialize_message
import rosbag2_py
from rosidl_runtime_py.utilities import get_message
import yaml

from .record_run import (
    DEFAULT_TIMESTAMP_ORDERING,
    MULTI_PUBLISHER_TIMESTAMP_ORDERING,
    REQUIRED_METADATA,
    VALID_PROFILES_BY_MODE,
    atomic_json,
    expected_publisher_error,
    preauthorization_lifecycle_errors,
    topic_evidence_contract_errors,
)


FORBIDDEN_CONSOLE_MARKERS = (
    "traceback (most recent call last)",
    "rclerror",
    "publisher's context is invalid",
    "failed to terminate",
)
MOTION_COVERAGE_ALIASES = {
    "source_cost",
    "cost_breakdown",
    "gesc_diagnostics",
    "control_diagnostics",
    "algorithm_state",
    "pose",
    "command_final",
    "command_array_final",
}
FILL_EVENT_TYPES = {20, 22, 23}
FILL_OWNER_EVENT_TYPES = set(range(20, 27))


def _stamp_nanoseconds(stamp):
    return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)


def _message_stamp_nanoseconds(message):
    """Return a typed absolute ROS stamp, excluding legacy float timestamps."""

    if hasattr(message, "stamp"):
        return _stamp_nanoseconds(message.stamp)
    if hasattr(message, "header") and hasattr(message.header, "stamp"):
        return _stamp_nanoseconds(message.header.stamp)
    return None


def timestamp_regressions(values, tolerance_nanoseconds):
    """Return ordered pairs that regress beyond the configured tolerance."""

    regressions = []
    previous = None
    for current in values:
        if previous is not None and current + tolerance_nanoseconds < previous:
            regressions.append({"previous": previous, "current": current})
        previous = current
    return regressions


def algorithm_event_producer_stream(message):
    """Identify the producer of one shared-bus event."""  # noqa: Q000
    event_type = int(message.event_type)
    detail = str(message.detail)
    if event_type in (10, 11):
        return 'convergence_detector'
    if event_type in FILL_OWNER_EVENT_TYPES:
        return 'gaussian_fill'
    if event_type in (3, 30, 40, 41, 50, 51, 60):
        return 'supervisor'
    if event_type == 70:
        reason_code = int(message.reason_code)
        if detail.startswith('controller watchdog:') and reason_code == 1:
            return 'controller'
        if not detail.startswith('controller watchdog:') and reason_code == 0:
            return 'supervisor'
        return None
    if event_type == 2:
        return 'cost_function'
    if event_type != 1:
        return None
    configuration_prefixes = (
        ('source_mode=', 'cost_function'),
        ('state-driven robust weights', 'modified_cost'),
        ('legacy fixed observational weights', 'modified_cost'),
        ('convergence detector configuration', 'convergence_detector'),
        ('robust Gaussian estimator', 'gaussian_fill'),
        ('Gaussian fill configuration', 'gaussian_fill'),
        ('measured escape', 'supervisor'),
        ('post-recovery ', 'supervisor'),
    )
    return next(
        (
            producer
            for prefix, producer in configuration_prefixes
            if detail.startswith(prefix)
        ),
        None,
    )


def algorithm_event_stream_regressions(records, tolerance_nanoseconds):
    """Check AlgorithmEvent stamps independently per producer."""  # noqa: Q000
    streams = {}
    unidentified = []
    for bag_stamp, message in records:
        producer = algorithm_event_producer_stream(message)
        if producer is None:
            unidentified.append({
                'bag_timestamp': int(bag_stamp),
                'event_type': int(message.event_type),
                'detail': str(message.detail),
            })
            continue
        streams.setdefault(producer, []).append(
            (int(bag_stamp), _message_stamp_nanoseconds(message))
        )
    regressions = []
    for producer, values in streams.items():
        previous = None
        for bag_stamp, current in values:
            if current is None:
                continue
            if (
                previous is not None
                and current + tolerance_nanoseconds < previous['stamp']
            ):
                regressions.append({
                    'producer_stream': producer,
                    'previous': previous['stamp'],
                    'current': current,
                    'previous_bag_timestamp': previous['bag_timestamp'],
                    'current_bag_timestamp': bag_stamp,
                })
            previous = {
                'stamp': current,
                'bag_timestamp': bag_stamp,
            }
    return regressions, unidentified


def algorithm_event_emission_lags(event_records, clock_records):
    """Map event receipts to the latest received simulation clock."""  # noqa: Q000
    clocks = sorted(
        (
            int(bag_stamp),
            _stamp_nanoseconds(message.clock),
        )
        for bag_stamp, message in clock_records
        if message is not None
    )
    results = []
    clock_index = 0
    latest_clock = None
    for bag_stamp, message in sorted(event_records, key=lambda item: item[0]):
        while (
            clock_index < len(clocks)
            and clocks[clock_index][0] <= int(bag_stamp)
        ):
            latest_clock = clocks[clock_index][1]
            clock_index += 1
        event_stamp = _message_stamp_nanoseconds(message)
        results.append({
            'bag_timestamp': int(bag_stamp),
            'producer_stream': algorithm_event_producer_stream(message),
            'event_stamp': event_stamp,
            'clock_at_receipt': latest_clock,
            'clock_skew_nanoseconds': (
                None
                if latest_clock is None or event_stamp is None
                else latest_clock - event_stamp
            ),
        })
    return results


def fill_event_source_causality(event_records, request_records):
    """Require exact fill-event correlation to a recorded request."""  # noqa: Q000
    request_sources = [
        float(message.timestamp)
        for _, message in request_records
        if message is not None and math.isfinite(float(message.timestamp))
    ]
    failures = []
    for bag_stamp, message in event_records:
        if message is None:
            continue
        if int(message.event_type) not in FILL_OWNER_EVENT_TYPES:
            continue
        source = float(message.source_timestamp)
        matched = (
            message.source_timestamp_valid
            and math.isfinite(source)
            and source in request_sources
        )
        if not matched:
            failures.append({
                'bag_timestamp': int(bag_stamp),
                'event_type': int(message.event_type),
                'source_timestamp': source if math.isfinite(source) else None,
                'source_timestamp_valid': bool(
                    message.source_timestamp_valid
                ),
            })
    return failures


def timestamps_within_clock(values, clock_minimum, clock_maximum, tolerance_nanoseconds):
    """Check typed stamps against the selected run's simulation clock range."""

    return all(
        clock_minimum - tolerance_nanoseconds
        <= value
        <= clock_maximum + tolerance_nanoseconds
        for value in values
    )


def _twist_values(message):
    return (
        message.linear.x, message.linear.y, message.linear.z,
        message.angular.x, message.angular.y, message.angular.z,
    )


def _command_values(alias, message):
    if alias == "command_final":
        return _twist_values(message)
    if alias == "command_array_final":
        return tuple(message.data)
    if alias == "control_diagnostics":
        return tuple(message.final_command)
    raise ValueError(f"not a command alias: {alias}")


def _is_zero(values, tolerance=1e-9):
    return (
        len(values) == 6
        and all(
            math.isfinite(float(value)) and abs(float(value)) <= tolerance
            for value in values
        )
    )


def _check(report, name, passed, failure=None, detail=None):
    item = {"passed": bool(passed)}
    if detail is not None:
        item["detail"] = detail
    report["checks"][name] = item
    if not passed and failure:
        report["failures"].append(failure)


def _json_compatible(value, path='$', nonfinite_paths=None):
    """Replace nonfinite evidence scalars with null and retain their paths."""
    if nonfinite_paths is None:
        nonfinite_paths = []
    if isinstance(value, dict):
        converted = {}
        for index, (key, item) in enumerate(value.items()):
            converted_key = key
            if isinstance(key, float) and not math.isfinite(key):
                nonfinite_paths.append(f'{path}.<nonfinite-key>')
                converted_key = f'<nonfinite-key-{index}>'
            elif not isinstance(
                key,
                (str, int, float, bool, type(None)),
            ):
                converted_key = str(key)
            converted[converted_key] = _json_compatible(
                item,
                f'{path}.{converted_key}',
                nonfinite_paths,
            )
        return converted
    if isinstance(value, (list, tuple)):
        return [
            _json_compatible(
                item,
                f'{path}[{index}]',
                nonfinite_paths,
            )
            for index, item in enumerate(value)
        ]
    if isinstance(value, float) and not math.isfinite(value):
        nonfinite_paths.append(path)
        return None
    return value


def _load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _read_bag(bag_directory, expected_types, report):
    storage_options = rosbag2_py.StorageOptions(
        uri=str(bag_directory), storage_id="sqlite3"
    )
    converter_options = rosbag2_py.ConverterOptions("", "")
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    bag_types = {
        item.name: item.type for item in reader.get_all_topics_and_types()
    }
    messages = {topic: [] for topic in bag_types}
    classes = {}
    for topic, type_name in bag_types.items():
        try:
            classes[topic] = get_message(type_name)
        except (AttributeError, ModuleNotFoundError, ValueError) as exc:
            if topic in expected_types:
                report["failures"].append(
                    f"cannot load required type {type_name} for {topic}: {exc}"
                )
    while reader.has_next():
        topic, serialized, bag_stamp = reader.read_next()
        message_class = classes.get(topic)
        message = None
        if message_class is not None:
            message = deserialize_message(serialized, message_class)
        messages.setdefault(topic, []).append((int(bag_stamp), message))
    return bag_types, messages


def validate_run_directory(run_directory, write_report=True):
    """Validate a run directory and optionally replace completeness.json."""

    run_directory = Path(run_directory).expanduser().resolve()
    report = {
        "schema_version": 1,
        "run_id": run_directory.name,
        "passed": False,
        "checks": {},
        "topic_counts": {},
        "failures": [],
        "warnings": [],
    }
    metadata_path = run_directory / "metadata.yaml"
    resolved_topics_path = run_directory / "resolved_topics.yaml"
    resolved_parameters_path = run_directory / "resolved_parameters.yaml"
    notes_path = run_directory / "notes.md"
    bag_directory = run_directory / "bag"

    try:
        metadata = _load_yaml(metadata_path)
        metadata_ok = isinstance(metadata, dict)
    except (OSError, yaml.YAMLError) as exc:
        metadata = {}
        metadata_ok = False
        report["failures"].append(f"metadata unreadable: {exc}")
    missing_metadata = [
        name for name in (*REQUIRED_METADATA, "run_id", "git", "recording")
        if name not in metadata
    ]
    _check(
        report, "metadata_complete", metadata_ok and not missing_metadata,
        "metadata is incomplete",
        {"missing": missing_metadata},
    )
    _check(
        report, "notes_present", notes_path.is_file() and notes_path.stat().st_size > 0,
        "notes.md is missing or empty",
    )

    resolved = {}
    try:
        resolved = _load_yaml(resolved_topics_path)
        entries = resolved.get("topics", []) if isinstance(resolved, dict) else []
    except (OSError, yaml.YAMLError) as exc:
        entries = []
        report["failures"].append(f"resolved topics unreadable: {exc}")
    _check(
        report, "resolved_topics_present", bool(entries),
        "resolved_topics.yaml has no topic manifest",
    )
    by_topic = {entry["topic"]: entry for entry in entries if isinstance(entry, dict)}
    by_alias = {entry["alias"]: entry for entry in entries if isinstance(entry, dict)}
    expected_types = {topic: entry["type"] for topic, entry in by_topic.items()}
    timestamp_contract_errors = []
    publisher_contract_errors = []
    multi_publisher_timestamp_topics = set()
    multi_publisher_scope = []
    for topic, entry in by_topic.items():
        entry_errors = topic_evidence_contract_errors(entry)
        timestamp_contract_errors.extend(entry_errors)
        publisher_error = None
        if not entry_errors:
            publisher_error = expected_publisher_error(
                entry,
                entry.get('publishers', ()),
            )
            if publisher_error is not None:
                publisher_contract_errors.append(publisher_error)
        if (
            not entry_errors
            and publisher_error is None
            and entry.get(
                'timestamp_ordering',
                DEFAULT_TIMESTAMP_ORDERING,
            ) == MULTI_PUBLISHER_TIMESTAMP_ORDERING
        ):
            multi_publisher_timestamp_topics.add(topic)
            multi_publisher_scope.append({
                'topic': topic,
                'expected_publishers': sorted(
                    entry['expected_publishers']
                ),
                'resolved_publishers': sorted(entry.get('publishers', ())),
            })
    _check(
        report,
        'timestamp_ordering_contract_valid',
        not timestamp_contract_errors,
        'resolved timestamp-ordering contract is invalid',
        timestamp_contract_errors,
    )
    _check(
        report,
        'expected_publishers_match',
        not publisher_contract_errors,
        'resolved publishers do not match the declared owners',
        publisher_contract_errors,
    )
    _check(
        report,
        'multi_publisher_timestamp_scope',
        True,
        detail=multi_publisher_scope,
    )

    try:
        parameters = _load_yaml(resolved_parameters_path)
        parameter_failures = parameters.get("failures", [])
        required_parameter_failures = [
            item for item in parameter_failures
            if item.get("required_topic_publisher") and item.get("parameter_services_exposed", True)
        ]
        parameters_ok = isinstance(parameters, dict) and not required_parameter_failures
    except (OSError, yaml.YAMLError) as exc:
        parameters_ok = False
        required_parameter_failures = [{"error": str(exc)}]
    _check(
        report, "parameters_captured", parameters_ok,
        "required publisher parameter snapshot is incomplete",
        required_parameter_failures,
    )

    try:
        bag_types, messages = _read_bag(bag_directory, expected_types, report)
        bag_readable = True
    except Exception as exc:
        bag_types, messages = {}, {}
        bag_readable = False
        report["failures"].append(f"bag unreadable: {type(exc).__name__}: {exc}")
    _check(report, "bag_readable", bag_readable, "sqlite3 bag is not readable")

    for topic, entry in by_topic.items():
        count = len(messages.get(topic, []))
        report["topic_counts"][topic] = count
        if entry.get("required"):
            exact_type = bag_types.get(topic) == entry["type"]
            minimum = int(entry.get("minimum_messages", 1))
            _check(
                report, f"required_topic:{entry['alias']}",
                exact_type and count >= minimum,
                f"required topic {topic} missing, wrong type, or below {minimum} messages",
                {"expected_type": entry["type"], "actual_type": bag_types.get(topic), "count": count},
            )

    clock_messages = messages.get(by_alias.get("clock", {}).get("topic", ""), [])
    if metadata.get("mode") == "simulation":
        clock_values = [
            _stamp_nanoseconds(message.clock)
            for _, message in clock_messages if message is not None
        ]
        clock_ok = bool(clock_values) and all(
            current >= previous for previous, current in zip(clock_values, clock_values[1:])
        )
        _check(report, "simulation_clock_monotonic", clock_ok, "simulation /clock regressed or is absent")

    readiness_topic = by_alias.get("recording_ready", {}).get("topic", "")
    early_readiness_records = [
        (stamp, bool(message.data))
        for stamp, message in messages.get(readiness_topic, []) if message is not None
    ]
    first_ready_true = next(
        (stamp for stamp, value in early_readiness_records if value), None
    )
    first_ready_false_after_true = next(
        (
            stamp for stamp, value in early_readiness_records
            if not value and first_ready_true is not None and stamp >= first_ready_true
        ),
        None,
    )
    try:
        tolerance_sec = float(
            resolved.get("validation", {}).get(
                "timestamp_regression_tolerance_sec", 0.05
            )
        )
    except (TypeError, ValueError):
        tolerance_sec = float('nan')
    tolerance_valid = (
        math.isfinite(tolerance_sec)
        and tolerance_sec >= 0.0
    )
    _check(
        report,
        'timestamp_tolerance_valid',
        tolerance_valid,
        'timestamp regression tolerance is invalid',
        {
            'configured_sec': (
                tolerance_sec if math.isfinite(tolerance_sec) else None
            ),
        },
    )
    if not tolerance_valid:
        tolerance_sec = 0.0
    tolerance_nanoseconds = int(tolerance_sec * 1_000_000_000)
    stamp_regressions = []
    typed_stamps_in_interval = []
    event_topic = by_alias.get('algorithm_events', {}).get('topic', '')
    event_interval_records = []
    for topic, topic_messages in messages.items():
        topic_stamps = []
        for bag_stamp, message in topic_messages:
            if message is None:
                continue
            if first_ready_true is not None and bag_stamp < first_ready_true:
                continue
            if first_ready_false_after_true is not None and bag_stamp > first_ready_false_after_true:
                continue
            current = _message_stamp_nanoseconds(message)
            if current is not None:
                typed_stamps_in_interval.append({"topic": topic, "stamp": current})
                if topic == event_topic:
                    event_interval_records.append((bag_stamp, message))
                elif topic not in multi_publisher_timestamp_topics:
                    topic_stamps.append(current)
        if topic != event_topic:
            for regression in timestamp_regressions(
                topic_stamps, tolerance_nanoseconds
            ):
                stamp_regressions.append({'topic': topic, **regression})
    event_regressions, unidentified_events = (
        algorithm_event_stream_regressions(
            event_interval_records,
            tolerance_nanoseconds,
        )
    )
    stamp_regressions.extend(
        {'topic': event_topic, **regression}
        for regression in event_regressions
    )
    _check(
        report,
        'algorithm_event_producer_identified',
        not unidentified_events,
        'one or more AlgorithmEvent producers could not be identified',
        unidentified_events[:20],
    )
    _check(
        report, "typed_timestamps_nonregressing", not stamp_regressions,
        f"typed ROS timestamps regressed by more than {tolerance_sec:.3f} s",
        stamp_regressions[:20],
    )
    if metadata.get("mode") == "simulation" and clock_values:
        out_of_clock = [
            item for item in typed_stamps_in_interval
            if not timestamps_within_clock(
                [item["stamp"]], min(clock_values), max(clock_values),
                tolerance_nanoseconds,
            )
        ]
        _check(
            report, "typed_timestamps_within_clock",
            not out_of_clock,
            "typed ROS timestamps fall outside the recorded simulation clock",
            out_of_clock[:20],
        )
        event_lags = algorithm_event_emission_lags(
            event_interval_records,
            clock_messages,
        )
        stale_events = [
            item for item in event_lags
            if item['clock_skew_nanoseconds'] is None
            or abs(item['clock_skew_nanoseconds']) > tolerance_nanoseconds
        ]
        _check(
            report,
            'algorithm_event_emission_fresh',
            not stale_events,
            'AlgorithmEvent emission stamps lead or lag receipt-time '
            'simulation clock',
            stale_events[:20],
        )

    source_entry = by_alias.get("source_cost", {})
    source_messages = messages.get(source_entry.get("topic", ""), [])
    source_semantics_ok = bool(source_messages)
    for _, message in source_messages:
        if message is None:
            source_semantics_ok = False
            continue
        if metadata.get("mode") == "simulation":
            source_semantics_ok &= (
                message.source_mode == message.SOURCE_SIMULATION
                and message.raw_cost_valid
                and message.source_score_valid
                and not message.raw_sensor_valid
            )
        else:
            source_semantics_ok &= (
                message.source_mode == message.SOURCE_PHYSICAL
                and message.raw_sensor_valid
                and message.raw_cost_valid
                and message.source_score_valid
            )
    _check(
        report, "source_cost_semantics", source_semantics_ok,
        "source cost validity/source mode does not match run mode",
    )
    mode = metadata.get("mode")
    profile = metadata.get("algorithm_profile")
    profile_ok = (
        mode in VALID_PROFILES_BY_MODE
        and profile in VALID_PROFILES_BY_MODE[mode]
    )
    _check(
        report, "audited_profile", profile_ok,
        f"algorithm_profile {profile!r} is not audited for mode {mode!r}",
    )

    event_entry = by_alias.get("algorithm_events", {})
    event_messages = messages.get(event_entry.get("topic", ""), [])
    event_lengths_ok = all(
        message is not None and len(message.value_names) == len(message.values)
        for _, message in event_messages
    )
    _check(report, "event_value_pairs", event_lengths_ok, "AlgorithmEvent value_names/values mismatch")
    fill_request_entry = by_alias.get('fill_requests', {})
    source_causality_failures = (
        fill_event_source_causality(
            event_messages,
            messages.get(fill_request_entry.get('topic', ''), []),
        )
        if profile == 'robust_gaussian_v1'
        else []
    )
    _check(
        report,
        'algorithm_event_source_causality',
        not source_causality_failures,
        'fill-owner AlgorithmEvent source timestamps lack a recorded request',
        (
            source_causality_failures[:20]
            if profile == 'robust_gaussian_v1'
            else {'status': 'not_applicable'}
        ),
    )

    state_entry = by_alias.get("algorithm_state", {})
    state_messages = messages.get(state_entry.get("topic", ""), [])
    fill_required = any(
        message is not None and message.event_type in FILL_EVENT_TYPES
        for _, message in event_messages
    ) or any(
        message is not None and message.active_fill_count_valid and message.active_fill_count > 0
        for _, message in state_messages
    )
    fill_count = len(messages.get(by_alias.get("gaussian_fills", {}).get("topic", ""), []))
    _check(
        report, "fill_lifecycle_conditional", not fill_required or fill_count > 0,
        "fill lifecycle was reported without GaussianFill records",
        {"fill_required": fill_required, "fill_messages": fill_count},
    )

    command_records = {}
    nonzero_times = []
    for alias in ("command_final", "command_array_final", "control_diagnostics"):
        entry = by_alias.get(alias, {})
        records = messages.get(entry.get("topic", ""), [])
        parsed = [
            (stamp, _command_values(alias, message))
            for stamp, message in records if message is not None
        ]
        command_records[alias] = parsed
        nonzero_times.extend(stamp for stamp, values in parsed if not _is_zero(values))

    readiness_entry = by_alias.get("recording_ready", {})
    readiness_records = [
        (stamp, bool(message.data))
        for stamp, message in messages.get(readiness_entry.get("topic", ""), [])
        if message is not None
    ]
    stop_entry = by_alias.get("stop_requested", {})
    stop_times = [
        stamp
        for stamp, message in messages.get(stop_entry.get("topic", ""), [])
        if message is not None and message.data
    ]
    first_stop_true = stop_times[0] if stop_times else None
    preauthorization_boundaries = [
        boundary
        for boundary in (first_ready_true, first_stop_true)
        if boundary is not None
    ]
    preauthorization_boundary = (
        min(preauthorization_boundaries)
        if preauthorization_boundaries
        else None
    )
    pre_ready_nonzero = [
        {'alias': alias, 'bag_timestamp': stamp}
        for alias, records in command_records.items()
        for stamp, values in records
        if (
            not _is_zero(values)
            and (
                preauthorization_boundary is None
                or stamp < preauthorization_boundary
            )
        )
    ]
    recording = (
        metadata.get('recording', {})
        if isinstance(metadata, dict)
        else {}
    )
    metadata_pre_ready_nonzero = (
        recording.get('pre_ready_nonzero_topics', {})
        if isinstance(recording, dict)
        else {}
    )
    _check(
        report,
        'no_motion_before_readiness',
        not pre_ready_nonzero and not metadata_pre_ready_nonzero,
        'nonzero command was recorded before motion readiness',
        {
            'bag_observations': pre_ready_nonzero[:20],
            'coordinator_observations': metadata_pre_ready_nonzero,
        },
    )
    bag_lifecycle_violations = []
    for stamp, message in state_messages:
        if (
            message is None
            or (
                preauthorization_boundary is not None
                and stamp >= preauthorization_boundary
            )
        ):
            continue
        lifecycle_errors = preauthorization_lifecycle_errors(
            message,
            profile,
        )
        if lifecycle_errors:
            bag_lifecycle_violations.append({
                'bag_timestamp': stamp,
                'errors': lifecycle_errors,
            })
    metadata_lifecycle_violations = (
        recording.get('pre_ready_lifecycle_violations', [])
        if isinstance(recording, dict)
        else []
    )
    lifecycle_clean = (
        profile != 'robust_gaussian_v1'
        or (
            not bag_lifecycle_violations
            and not metadata_lifecycle_violations
        )
    )
    _check(
        report,
        'clean_lifecycle_before_readiness',
        lifecycle_clean,
        'robust lifecycle advanced before recording readiness',
        (
            {
                'bag_observations': bag_lifecycle_violations[:20],
                'coordinator_observations': (
                    metadata_lifecycle_violations
                ),
            }
            if profile == 'robust_gaussian_v1'
            else {'status': 'not_applicable'}
        ),
    )
    shutdown_boundary = stop_times[-1] if stop_times else (
        readiness_records[-1][0] if readiness_records else None
    )
    _check(
        report, "final_readiness_false",
        bool(readiness_records) and readiness_records[-1][1] is False,
        "last recording-ready heartbeat is not false",
    )
    final_zero_ok = True
    final_zero_details = {}
    last_nonzero = max(nonzero_times) if nonzero_times else -1
    for alias, records in command_records.items():
        last = records[-1] if records else None
        passed = (
            last is not None and _is_zero(last[1])
            and last[0] >= last_nonzero
            and shutdown_boundary is not None and last[0] >= shutdown_boundary
        )
        final_zero_ok &= passed
        final_zero_details[alias] = {"passed": passed, "last_timestamp": last[0] if last else None}
    _check(
        report, "final_commands_zero", final_zero_ok,
        "one or more final command representations lack post-shutdown zero evidence",
        final_zero_details,
    )

    if nonzero_times:
        interval_start, interval_end = min(nonzero_times), max(nonzero_times)
    else:
        true_times = [stamp for stamp, value in readiness_records if value]
        false_after = [
            stamp for stamp, value in readiness_records
            if not value and true_times and stamp >= true_times[0]
        ]
        interval_start = true_times[0] if true_times else None
        interval_end = false_after[0] if false_after else None
    coverage_failures = []
    if interval_start is None or interval_end is None:
        coverage_failures.append("motion/readiness coverage interval is unavailable")
    else:
        tolerance = 1_000_000_000
        for alias in MOTION_COVERAGE_ALIASES:
            entry = by_alias.get(alias)
            if not entry:
                coverage_failures.append(f"{alias}: absent from resolved manifest")
                continue
            timestamps = [stamp for stamp, _ in messages.get(entry["topic"], [])]
            if not timestamps or timestamps[0] > interval_start + tolerance or timestamps[-1] < interval_end - tolerance:
                coverage_failures.append(f"{alias}: does not cover interval within 1 second")
    _check(
        report, "motion_interval_coverage", not coverage_failures,
        "required state/cost/pose/command topics do not cover motion interval",
        coverage_failures,
    )

    readiness_metadata_consistent = (
        'readiness_ever_true' not in recording
        or bool(recording.get('readiness_ever_true'))
        == (first_ready_true is not None)
    )
    _check(
        report,
        'readiness_metadata_consistent',
        readiness_metadata_consistent,
        'recording readiness metadata disagrees with the bag',
    )
    process_ok = (
        recording.get("complete") is True
        and recording.get("bag_clean_shutdown") is True
        and recording.get("target_clean_shutdown") is True
        and recording.get("final_zero_observed") is True
        and not recording.get("run_error")
    )
    _check(report, "clean_shutdown_metadata", process_ok, "recording shutdown metadata is incomplete or failed")

    try:
        console_text = (run_directory / "console.log").read_text(
            encoding="utf-8", errors="replace"
        ).lower()
        console_failures = [marker for marker in FORBIDDEN_CONSOLE_MARKERS if marker in console_text]
        shutdown_index = console_text.find(
            "shutdown initiated; readiness false and stop requested"
        )
        for line in console_text.splitlines():
            if "process has died" not in line:
                continue
            line_index = console_text.find(line)
            allowed_gazebo_interrupt = (
                shutdown_index >= 0
                and line_index >= shutdown_index
                and ("gzserver" in line or "gzclient" in line or "gazebo-" in line)
                and "exit code 255" in line
            )
            allowed_controlled_sigint = (
                shutdown_index >= 0
                and line_index >= shutdown_index
                and "exit code -2" in line
            )
            if not (allowed_gazebo_interrupt or allowed_controlled_sigint):
                console_failures.append(line)
    except OSError as exc:
        console_failures = [f"console.log unreadable: {exc}"]
    _check(
        report, "console_clean", not console_failures,
        "console contains a ROS/process failure marker", console_failures,
    )

    nonfinite_paths = []
    report = _json_compatible(
        report,
        nonfinite_paths=nonfinite_paths,
    )
    _check(
        report,
        'strict_json_finite',
        not nonfinite_paths,
        'nonfinite evidence values were normalized to null',
        {'normalized_paths': nonfinite_paths},
    )
    report["passed"] = not report["failures"]
    if write_report:
        atomic_json(run_directory / "completeness.json", report)
    return report


def _parser():
    parser = argparse.ArgumentParser(description="Validate one recorded run directory.")
    parser.add_argument("run_directory")
    return parser


def main(args=None):
    """Console entry point."""

    parsed = _parser().parse_args(args)
    try:
        report = validate_run_directory(parsed.run_directory, write_report=True)
    except Exception as exc:
        print(f"validate_run: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
