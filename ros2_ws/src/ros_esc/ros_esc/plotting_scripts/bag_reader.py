#!/usr/bin/env python3

"""Read Phase 05 sqlite3 bags without modifying their run artifacts."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
import math
from pathlib import Path

from rclpy.serialization import deserialize_message

import rosbag2_py

from rosidl_runtime_py.utilities import get_message

import yaml


NANOSECONDS_PER_SECOND = 1_000_000_000


@dataclass(frozen=True)
class BagRecord:
    """One deserialized bag record with all available timestamp domains."""

    topic: str
    type_name: str
    bag_timestamp_ns: int
    ros_timestamp_ns: int | None
    source_timestamp_sec: float | None
    source_timestamp_valid: bool
    message: object
    in_readiness_interval: bool = False
    t_motion_sec: float | None = None


@dataclass(frozen=True)
class BagData:
    """Read-only contents and run-specific topic contract for one run."""

    run_directory: Path
    topic_types: dict
    topics_by_alias: dict
    records_by_topic: dict
    readiness_start_ns: int | None
    readiness_end_ns: int | None


@dataclass(frozen=True)
class TimestampIndex:
    """Prepared records and timestamps for repeated bounded lookup."""

    records: tuple
    timestamps: tuple
    field: str


def load_yaml(path):
    """Load one YAML document."""
    with Path(path).open('r', encoding='utf-8') as stream:
        return yaml.safe_load(stream)


def stamp_nanoseconds(stamp):
    """Convert a ROS Time-like object to exact integer nanoseconds."""
    return (
        int(stamp.sec) * NANOSECONDS_PER_SECOND
        + int(stamp.nanosec)
    )


def message_ros_timestamp_ns(message):
    """Return an absolute typed/header ROS timestamp when present."""
    if hasattr(message, 'stamp'):
        return stamp_nanoseconds(message.stamp)
    header = getattr(message, 'header', None)
    if header is not None and hasattr(header, 'stamp'):
        return stamp_nanoseconds(header.stamp)
    return None


def message_source_timestamp(message):
    """Return the legacy/source timestamp and its explicit validity."""
    if hasattr(message, 'source_timestamp'):
        value = float(message.source_timestamp)
        valid = bool(getattr(message, 'source_timestamp_valid', False))
        return value, valid and math.isfinite(value)
    if hasattr(message, 'timestamp'):
        value = float(message.timestamp)
        return value, math.isfinite(value)
    return None, False


def _readiness_bounds(raw_records, readiness_topic):
    records = raw_records.get(readiness_topic, [])
    start = next(
        (
            record.bag_timestamp_ns
            for record in records
            if bool(getattr(record.message, 'data', False))
        ),
        None,
    )
    if start is None:
        return None, None
    end = next(
        (
            record.bag_timestamp_ns
            for record in records
            if (
                record.bag_timestamp_ns >= start
                and not bool(getattr(record.message, 'data', False))
            )
        ),
        None,
    )
    return start, end


def _with_readiness(record, start, end):
    in_interval = (
        start is not None
        and record.bag_timestamp_ns >= start
        and (end is None or record.bag_timestamp_ns <= end)
    )
    t_motion = None
    if start is not None:
        t_motion = (
            record.bag_timestamp_ns - start
        ) / NANOSECONDS_PER_SECOND
    return BagRecord(
        topic=record.topic,
        type_name=record.type_name,
        bag_timestamp_ns=record.bag_timestamp_ns,
        ros_timestamp_ns=record.ros_timestamp_ns,
        source_timestamp_sec=record.source_timestamp_sec,
        source_timestamp_valid=record.source_timestamp_valid,
        message=record.message,
        in_readiness_interval=in_interval,
        t_motion_sec=t_motion,
    )


def read_run_bag(run_directory, *, aliases=None):
    """Read a bag, optionally selecting resolved aliases plus readiness.

    The default still loads the complete historical analysis contract. A
    caller selecting inputs can exclude algorithm outputs during independent
    labeling and avoid decoding large, unrelated PDE histories.
    """
    run_directory = Path(run_directory).expanduser().resolve()
    resolved_path = run_directory / 'resolved_topics.yaml'
    resolved = load_yaml(resolved_path)
    entries = resolved.get('topics', []) if isinstance(resolved, dict) else []
    if not entries:
        raise ValueError('resolved_topics.yaml has no topic entries')
    topics_by_alias = {
        entry['alias']: entry
        for entry in entries
        if isinstance(entry, dict) and 'alias' in entry and 'topic' in entry
    }

    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(
            uri=str(run_directory / 'bag'),
            storage_id='sqlite3',
        ),
        rosbag2_py.ConverterOptions('', ''),
    )
    topic_types = {
        item.name: item.type
        for item in reader.get_all_topics_and_types()
    }
    if aliases is not None:
        selected = set(aliases) | {'recording_ready'}
        unknown = selected - topics_by_alias.keys()
        if unknown:
            raise ValueError(f'unknown resolved aliases: {sorted(unknown)}')
        selected_topics = {
            topics_by_alias[alias]['topic'] for alias in selected
        }
        reader.set_filter(rosbag2_py.StorageFilter(
            topics=sorted(selected_topics),
        ))
        topic_types = {
            topic: type_name for topic, type_name in topic_types.items()
            if topic in selected_topics
        }
    classes = {
        topic: get_message(type_name)
        for topic, type_name in topic_types.items()
    }
    raw_records = {topic: [] for topic in topic_types}
    while reader.has_next():
        topic, serialized, bag_timestamp = reader.read_next()
        message = deserialize_message(serialized, classes[topic])
        source_timestamp, source_valid = message_source_timestamp(message)
        raw_records[topic].append(
            BagRecord(
                topic=topic,
                type_name=topic_types[topic],
                bag_timestamp_ns=int(bag_timestamp),
                ros_timestamp_ns=message_ros_timestamp_ns(message),
                source_timestamp_sec=source_timestamp,
                source_timestamp_valid=source_valid,
                message=message,
            )
        )

    readiness_topic = topics_by_alias.get(
        'recording_ready', {}
    ).get('topic', '')
    start, end = _readiness_bounds(raw_records, readiness_topic)
    records_by_topic = {
        topic: [_with_readiness(record, start, end) for record in records]
        for topic, records in raw_records.items()
    }
    return BagData(
        run_directory=run_directory,
        topic_types=topic_types,
        topics_by_alias=topics_by_alias,
        records_by_topic=records_by_topic,
        readiness_start_ns=start,
        readiness_end_ns=end,
    )


def records_for_alias(bag_data, alias, readiness_only=False):
    """Return records for a resolved alias."""
    topic = bag_data.topics_by_alias.get(alias, {}).get('topic')
    records = bag_data.records_by_topic.get(topic, [])
    if readiness_only:
        return [record for record in records if record.in_readiness_interval]
    return list(records)


def _timestamp(record, field):
    value = getattr(record, field)
    return value if value is not None else record.bag_timestamp_ns


def build_timestamp_index(records, field):
    """Prepare one timestamp index for repeated lookup against a stream."""
    usable = [
        record for record in records
        if getattr(record, field) is not None
    ]
    return TimestampIndex(
        records=tuple(usable),
        timestamps=tuple(_timestamp(record, field) for record in usable),
        field=field,
    )


def nearest_indexed_record(index, target_timestamp_ns, tolerance_ns):
    """Return the nearest indexed record without interpolation."""
    position = bisect_left(index.timestamps, target_timestamp_ns)
    candidates = []
    if position < len(index.records):
        candidates.append(index.records[position])
    if position:
        candidates.append(index.records[position - 1])
    if not candidates:
        return None, None
    selected = min(
        candidates,
        key=lambda record: (
            abs(_timestamp(record, index.field) - target_timestamp_ns),
            _timestamp(record, index.field),
        ),
    )
    skew = _timestamp(selected, index.field) - target_timestamp_ns
    if abs(skew) > tolerance_ns:
        return None, None
    return selected, skew


def causal_indexed_record(index, target_timestamp_ns, tolerance_ns):
    """Return the latest causal indexed record within tolerance."""
    position = bisect_right(index.timestamps, target_timestamp_ns) - 1
    if position < 0:
        return None, None
    selected = index.records[position]
    skew = _timestamp(selected, index.field) - target_timestamp_ns
    if abs(skew) > tolerance_ns:
        return None, None
    return selected, skew


def nearest_record(records, target_timestamp_ns, tolerance_ns, field):
    """Return the nearest record within tolerance without interpolation."""
    return nearest_indexed_record(
        build_timestamp_index(records, field),
        target_timestamp_ns,
        tolerance_ns,
    )


def causal_record(records, target_timestamp_ns, tolerance_ns, field):
    """Return the latest causal record within tolerance."""
    return causal_indexed_record(
        build_timestamp_index(records, field),
        target_timestamp_ns,
        tolerance_ns,
    )
