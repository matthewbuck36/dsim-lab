#!/usr/bin/env python3

"""Run one motion-gated experiment and record its complete ROS interface."""

import argparse
import datetime as dt
from functools import partial
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from rcl_interfaces.srv import DescribeParameters, GetParameters, ListParameters
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter, parameter_value_to_python
from rclpy.signals import SignalHandlerOptions
from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc_interfaces.msg import (
    AlgorithmState,
    ControlDiagnostics,
    StampedFloat64MultiArray,
)
import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from std_msgs.msg import Bool
import yaml


VALID_MODES = {"simulation", "physical"}
VALID_PROFILES_BY_MODE = {
    "simulation": {"legacy", "robust_gaussian_v1"},
    "physical": {"robust_gaussian_v1"},
}
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
REQUIRED_METADATA = (
    "experiment_version",
    "operator",
    "mode",
    "algorithm_profile",
    "scenario_id",
    "random_seed",
    "environment",
    "robot_starting_pose",
    "sources",
    "calibration",
    "parameter_files",
    "human_intervention",
    "operator_notes",
)
ZERO_TOPICS = (
    "/cmd_vel",
    "/turtlebot3/control_value_chatter",
    "/gesc_gaussian/control_diagnostics",
)
PARAMETER_SNAPSHOT_TIMEOUT_SEC = 15.0
PARAMETER_SERVICE_AVAILABILITY_TIMEOUT_SEC = 1.0
REQUIRED_PARAMETER_CAPTURE_ATTEMPTS = 3
PARAMETER_CAPTURE_RETRY_DELAY_SEC = 0.25
LEAF_SHUTDOWN_STAGGER_SEC = 0.1
OPERATIONAL_HEARTBEAT_STALE_SEC = 0.5
REQUIRED_SIMULATION_CONTROLLERS = (
    'joint_state_broadcaster',
    'velocity_controller',
)
REQUIRED_SIMULATION_HEARTBEATS = (
    'pose',
    'source_cost',
    'filter_output_legacy',
    'timekeeper',
)
REQUIRED_ROBUST_SIMULATION_HEARTBEATS = (
    'algorithm_state',
    'supervisor_command',
)
CONTROLLER_MANAGER_SERVICE = '/controller_manager/list_controllers'
CONTROLLER_MANAGER_RESPONSE_TIMEOUT_SEC = 1.0
REQUIRED_SIMULATION_CONSUMER_TOPICS = {
    'sensor_delay_sec': {
        'algorithm_raw_cost_topic': (
            '/turtlebot3/cost_value_chatter',
            '/gesc_gaussian/simulation/raw_cost_delayed',
        ),
        'algorithm_source_cost_topic': (
            '/gesc_gaussian/source_cost',
            '/gesc_gaussian/simulation/source_cost_delayed',
        ),
        'pde_cost_history_topic': (
            '/turtlebot3/cost_value_chatter',
            '/gesc_gaussian/simulation/raw_cost_delayed',
        ),
    },
    'pose_delay_sec': {
        'algorithm_pose_topic': (
            '/odom',
            '/gesc_gaussian/simulation/pose_delayed',
        ),
        'gaussian_fill_pose_topic': (
            '/odom',
            '/gesc_gaussian/simulation/pose_delayed',
        ),
    },
}
SIMULATION_TARGET_PREFIX = (
    'ros2',
    'launch',
    'turtlebot3_rotating_sensor',
    'gazebo.launch.xml',
)
SIMULATION_CANONICAL_TARGET_DEFAULTS = {
    'entity_name': 'turtlebot3',
    'source_cost_topic': '/gesc_gaussian/source_cost',
    'algorithm_state_topic': '/gesc_gaussian/algorithm_state',
    'supervisor_command_topic': '/gesc_gaussian/supervisor_command',
    'recording_ready_topic': '/gesc_gaussian/recording_ready',
    'simulation_raw_cost_delayed_topic': (
        '/gesc_gaussian/simulation/raw_cost_delayed'
    ),
    'simulation_source_cost_delayed_topic': (
        '/gesc_gaussian/simulation/source_cost_delayed'
    ),
    'simulation_pose_delayed_topic': (
        '/gesc_gaussian/simulation/pose_delayed'
    ),
}


class PreflightDeadlineExceeded(TimeoutError):
    """Identify exhaustion of the one total startup-evidence deadline."""


def _utc_now():
    return dt.datetime.now(dt.timezone.utc)


def _iso_now():
    return _utc_now().isoformat().replace("+00:00", "Z")


def atomic_yaml(path, value):
    """Write YAML through a sibling temporary file and atomic replacement."""

    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    os.replace(temporary, path)


def atomic_json(path, value):
    """Write JSON through a sibling temporary file and atomic replacement."""

    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def load_manifest(path):
    """Load and validate the repository topic manifest."""

    manifest = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("topic manifest schema_version must be 1")
    validation = manifest.get('validation', {})
    try:
        timestamp_tolerance = float(
            validation['timestamp_regression_tolerance_sec']
        )
    except (KeyError, TypeError, ValueError):
        raise ValueError(
            'manifest timestamp regression tolerance must be finite and '
            'nonnegative'
        ) from None
    if (
        not math.isfinite(timestamp_tolerance)
        or timestamp_tolerance < 0.0
    ):
        raise ValueError(
            'manifest timestamp regression tolerance must be finite and '
            'nonnegative'
        )
    topics = manifest.get("topics")
    if not isinstance(topics, list) or not topics:
        raise ValueError("topic manifest must contain a non-empty topics list")
    aliases = set()
    names = set()
    for index, entry in enumerate(topics):
        required = {"alias", "topic", "type", "modes", "required"}
        if not isinstance(entry, dict) or not required.issubset(entry):
            raise ValueError(f"manifest topic {index} is missing required fields")
        if entry["alias"] in aliases:
            raise ValueError(f"duplicate manifest alias: {entry['alias']}")
        aliases.add(entry["alias"])
        if entry["topic"] in names:
            raise ValueError(f"duplicate manifest topic: {entry['topic']}")
        names.add(entry["topic"])
        if not str(entry["topic"]).startswith("/"):
            raise ValueError(f"manifest topic must be absolute: {entry['topic']}")
        if not set(entry["modes"]).issubset(VALID_MODES):
            raise ValueError(f"invalid modes for {entry['topic']}")
        if int(entry.get("minimum_messages", 0)) < 0:
            raise ValueError(f"negative minimum_messages for {entry['topic']}")
        if not isinstance(entry.get("singleton_publisher", False), bool):
            raise ValueError(
                f"singleton_publisher must be boolean for {entry['topic']}"
            )
    operational = manifest.get('operational_readiness', {})
    if not isinstance(operational, dict):
        raise ValueError('operational_readiness must be a mapping')
    topics_by_alias = {entry['alias']: entry for entry in topics}
    for mode, config in operational.items():
        if mode not in VALID_MODES or not isinstance(config, dict):
            raise ValueError(f'invalid operational readiness mode: {mode}')
        if mode != 'simulation':
            raise ValueError(
                'physical mode must not configure simulation operational '
                'readiness'
            )
        heartbeat_aliases = config.get('heartbeat_aliases')
        if (
            not isinstance(heartbeat_aliases, list)
            or not heartbeat_aliases
            or len(set(heartbeat_aliases)) != len(heartbeat_aliases)
        ):
            raise ValueError(
                f'{mode} operational heartbeat_aliases must be unique'
            )
        for alias in heartbeat_aliases:
            entry = topics_by_alias.get(alias)
            if entry is None or mode not in entry['modes']:
                raise ValueError(
                    f'{mode} operational heartbeat alias is invalid: {alias}'
                )
        profile_aliases = config.get('profile_heartbeat_aliases', {})
        if not isinstance(profile_aliases, dict):
            raise ValueError(
                f'{mode} profile_heartbeat_aliases must be a mapping'
            )
        for profile, aliases_for_profile in profile_aliases.items():
            if profile not in VALID_PROFILES_BY_MODE[mode]:
                raise ValueError(
                    f'{mode} operational heartbeat profile is invalid: '
                    f'{profile}'
                )
            if (
                not isinstance(aliases_for_profile, list)
                or len(set(aliases_for_profile)) != len(aliases_for_profile)
                or set(aliases_for_profile).intersection(heartbeat_aliases)
            ):
                raise ValueError(
                    f'{mode} profile heartbeat aliases must be unique'
                )
            for alias in aliases_for_profile:
                entry = topics_by_alias.get(alias)
                if entry is None or mode not in entry['modes']:
                    raise ValueError(
                        f'{mode} profile heartbeat alias is invalid: {alias}'
                    )
        overrides = config.get('heartbeat_alias_overrides', {})
        if not isinstance(overrides, dict):
            raise ValueError(
                f'{mode} heartbeat_alias_overrides must be a mapping'
            )
        for field, replacements in overrides.items():
            if not isinstance(field, str) or not isinstance(
                replacements, dict
            ):
                raise ValueError(
                    f'{mode} heartbeat alias override is invalid'
                )
            for original, replacement in replacements.items():
                entry = topics_by_alias.get(replacement)
                if (
                    original not in heartbeat_aliases
                    or entry is None
                    or mode not in entry['modes']
                ):
                    raise ValueError(
                        f'{mode} heartbeat alias override is invalid: '
                        f'{original} -> {replacement}'
                    )
        target_arguments = config.get(
            'heartbeat_override_target_arguments',
            {},
        )
        if (
            not isinstance(target_arguments, dict)
            or any(
                field not in overrides
                or not isinstance(argument, str)
                or not argument
                for field, argument in target_arguments.items()
            )
        ):
            raise ValueError(
                f'{mode} heartbeat override target arguments are invalid'
            )
        consumer_topics = config.get(
            'heartbeat_override_consumer_topics',
            {},
        )
        if not isinstance(consumer_topics, dict):
            raise ValueError(
                f'{mode} heartbeat override consumer topics are invalid'
            )
        for field, arguments in consumer_topics.items():
            if field not in overrides or not isinstance(arguments, dict):
                raise ValueError(
                    f'{mode} heartbeat override consumer topics are invalid'
                )
            for argument, topics_for_state in arguments.items():
                if (
                    not isinstance(argument, str)
                    or not argument
                    or not isinstance(topics_for_state, list)
                    or len(topics_for_state) != 2
                    or any(
                        not isinstance(topic, str)
                        or not topic.startswith('/')
                        for topic in topics_for_state
                    )
                ):
                    raise ValueError(
                        f'{mode} heartbeat override consumer topics are '
                        'invalid'
                    )
        stale_sec = float(config.get('heartbeat_stale_sec', 0.0))
        if not math.isfinite(stale_sec) or stale_sec <= 0.0:
            raise ValueError(
                f'{mode} operational heartbeat_stale_sec must be positive'
            )
        service = config.get('controller_manager_service')
        controllers = config.get('required_active_controllers', [])
        if service is not None and not str(service).startswith('/'):
            raise ValueError(
                f'{mode} controller_manager_service must be absolute'
            )
        if not isinstance(controllers, list) or len(set(controllers)) != len(
            controllers
        ):
            raise ValueError(
                f'{mode} required_active_controllers must be unique'
            )
        if mode == 'simulation':
            missing_base = sorted(
                set(REQUIRED_SIMULATION_HEARTBEATS)
                - set(heartbeat_aliases)
            )
            missing_robust = sorted(
                set(REQUIRED_ROBUST_SIMULATION_HEARTBEATS)
                - set(
                    profile_aliases.get('robust_gaussian_v1', [])
                )
            )
            required_overrides = {
                'sensor_delay_sec': {
                    'source_cost': 'simulation_source_cost_delayed'
                },
                'pose_delay_sec': {
                    'pose': 'simulation_pose_delayed'
                },
            }
            required_target_arguments = {
                'sensor_delay_sec': 'simulation_sensor_delay_sec',
                'pose_delay_sec': 'simulation_pose_delay_sec',
            }
            required_consumer_topics = {
                field: {
                    argument: list(topics_for_state)
                    for argument, topics_for_state in arguments.items()
                }
                for field, arguments in (
                    REQUIRED_SIMULATION_CONSUMER_TOPICS.items()
                )
            }
            if missing_base or missing_robust:
                raise ValueError(
                    'simulation operational readiness is incomplete: '
                    f'base={missing_base}, robust={missing_robust}'
                )
            if any(
                any(
                    overrides.get(field, {}).get(alias) != replacement
                    for alias, replacement in replacements.items()
                )
                for field, replacements in required_overrides.items()
            ):
                raise ValueError(
                    'simulation operational delayed-input overrides are '
                    'incomplete'
                )
            if any(
                target_arguments.get(field) != argument
                for field, argument in required_target_arguments.items()
            ):
                raise ValueError(
                    'simulation operational delayed-input target arguments '
                    'are incomplete'
                )
            if any(
                any(
                    consumer_topics.get(field, {}).get(argument)
                    != topics_for_state
                    for argument, topics_for_state in arguments.items()
                )
                for field, arguments in required_consumer_topics.items()
            ):
                raise ValueError(
                    'simulation operational delayed-input consumer topics '
                    'are incomplete'
                )
            if stale_sec > OPERATIONAL_HEARTBEAT_STALE_SEC:
                raise ValueError(
                    'simulation operational heartbeat_stale_sec exceeds '
                    'controller freshness'
                )
            if service != CONTROLLER_MANAGER_SERVICE:
                raise ValueError(
                    'simulation operational controller-manager service is '
                    'not canonical'
                )
            missing_controllers = sorted(
                set(REQUIRED_SIMULATION_CONTROLLERS) - set(controllers)
            )
            if missing_controllers:
                raise ValueError(
                    'simulation operational controllers are incomplete: '
                    + ', '.join(missing_controllers)
                )
    return manifest


def applicable_topics(manifest, mode):
    """Return manifest entries for a mode, preserving manifest order."""

    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {sorted(VALID_MODES)}")
    return [entry for entry in manifest["topics"] if mode in entry["modes"]]


def operational_config_for_mode(manifest, mode):
    """Return the required simulation barrier or the physical bypass."""  # noqa: Q000
    config = dict(
        manifest.get('operational_readiness', {}).get(mode, {})
    )
    if mode == 'physical':
        if config:
            raise ValueError(
                'physical mode cannot import simulation operational readiness'
            )
        return {}
    if mode == 'simulation' and not config:
        raise ValueError(
            'simulation manifest requires operational_readiness.simulation'
        )
    return config


def resolve_operational_heartbeat_aliases(config, metadata):
    """Select the actual algorithm input streams for one resolved run."""  # noqa: Q000
    aliases = list(config.get('heartbeat_aliases', []))
    profile_aliases = config.get('profile_heartbeat_aliases', {})
    aliases.extend(
        profile_aliases.get(str(metadata.get('algorithm_profile')), [])
    )
    environment = metadata.get('environment', {})
    disturbances = (
        environment.get('disturbances', {})
        if isinstance(environment, dict)
        else {}
    )
    if not isinstance(disturbances, dict):
        disturbances = {}
    for field, replacements in config.get(
        'heartbeat_alias_overrides',
        {},
    ).items():
        if float(disturbances.get(field, 0.0)) <= 0.0:
            continue
        aliases = [
            replacements.get(alias, alias)
            for alias in aliases
        ]
    return aliases


def require_operational_topics(entries, heartbeat_aliases):
    """Promote selected heartbeat streams into retained run requirements."""
    selected = set(heartbeat_aliases)
    available = {entry['alias'] for entry in entries}
    missing = sorted(selected - available)
    if missing:
        raise ValueError(
            'operational heartbeat aliases are absent from mode topics: '
            + ', '.join(missing)
        )
    return [
        {
            **entry,
            'required': True,
            'minimum_messages': max(
                1,
                int(entry.get('minimum_messages', 0)),
            ),
            'singleton_publisher': True,
            'operational_required': True,
        }
        if entry['alias'] in selected
        else dict(entry)
        for entry in entries
    ]


def validate_operational_target_coupling(config, metadata, target):
    """Cross-check delayed-input metadata against the launched graph argv."""  # noqa: Q000
    if tuple(target[:len(SIMULATION_TARGET_PREFIX)]) != (
        SIMULATION_TARGET_PREFIX
    ):
        raise ValueError(
            'simulation operational readiness requires the canonical Gazebo '
            'launch target'
        )
    assignments = {}
    for token in target:
        if ':=' not in str(token):
            continue
        name, value = str(token).split(':=', 1)
        assignments[name] = value
    expected_profile = str(metadata.get('algorithm_profile'))
    if assignments.get('algorithm_profile') != expected_profile:
        raise ValueError(
            'operational target algorithm_profile does not match metadata'
        )
    for argument in ('use_pde_extensions', 'recording_ready_required'):
        if assignments.get(argument, '').lower() != 'true':
            raise ValueError(
                f'operational target requires {argument}:=True'
            )
    for argument, expected_value in (
        SIMULATION_CANONICAL_TARGET_DEFAULTS.items()
    ):
        if assignments.get(argument, expected_value) != expected_value:
            raise ValueError(
                f'operational target overrides canonical {argument}'
            )
    environment = metadata.get('environment', {})
    disturbances = (
        environment.get('disturbances', {})
        if isinstance(environment, dict)
        else {}
    )
    if not isinstance(disturbances, dict):
        disturbances = {}
    resolved = {}
    resolved_consumers = {}
    target_arguments = config.get(
        'heartbeat_override_target_arguments',
        {},
    )
    consumer_topics = config.get(
        'heartbeat_override_consumer_topics',
        {},
    )
    for field in config.get('heartbeat_alias_overrides', {}):
        expected = float(disturbances.get(field, 0.0))
        target_argument = target_arguments.get(field, field)
        actual = float(assignments.get(target_argument, 0.0))
        if (
            not math.isfinite(expected)
            or not math.isfinite(actual)
            or expected < 0.0
            or actual < 0.0
        ):
            raise ValueError(
                f'operational disturbance {field} must be finite/nonnegative'
            )
        if not math.isclose(expected, actual, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                f'operational metadata/target mismatch for {field}: '
                f'metadata={expected}, target={actual}'
            )
        resolved[field] = actual
        delayed = actual > 0.0
        if (
            delayed
            and assignments.get(
                'simulation_validation_support_enabled',
                '',
            ).lower() != 'true'
        ):
            raise ValueError(
                'operational delayed inputs require '
                'simulation_validation_support_enabled:=True'
            )
        resolved_consumers[field] = {}
        for argument, topics_for_state in consumer_topics.get(
            field,
            {},
        ).items():
            expected_topic = topics_for_state[1 if delayed else 0]
            actual_topic = assignments.get(argument)
            if actual_topic != expected_topic:
                raise ValueError(
                    'operational consumer target mismatch for '
                    f'{argument}: expected={expected_topic}, '
                    f'target={actual_topic}'
                )
            resolved_consumers[field][argument] = actual_topic
    resolved['consumer_topics'] = resolved_consumers
    return resolved


def load_metadata_input(path, mode):
    """Validate operator input without inventing missing experimental facts."""

    metadata = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("metadata input must be a YAML mapping")
    missing = [name for name in REQUIRED_METADATA if name not in metadata]
    if missing:
        raise ValueError(f"metadata input missing fields: {', '.join(missing)}")
    if metadata["mode"] != mode:
        raise ValueError("metadata mode does not match --mode")
    if metadata["algorithm_profile"] not in VALID_PROFILES_BY_MODE[mode]:
        allowed = ", ".join(sorted(VALID_PROFILES_BY_MODE[mode]))
        raise ValueError(
            f"algorithm_profile must be one of [{allowed}] for {mode}"
        )
    for name in ("experiment_version", "operator", "scenario_id"):
        if not str(metadata[name]).strip():
            raise ValueError(f"metadata field {name} must not be empty")
    if not isinstance(metadata["human_intervention"], bool):
        raise ValueError("human_intervention must be true or false")
    if not isinstance(metadata["parameter_files"], list):
        raise ValueError("parameter_files must be a list")
    return metadata


def generate_run_id(mode, scenario_id, now=None):
    """Generate a UTC, mode, scenario, and UUID based run identifier."""

    now = now or _utc_now()
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", str(scenario_id)).strip("-._")
    slug = slug[:48] or "scenario"
    stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    return f"{stamp}_{mode}_{slug}_{uuid.uuid4().hex[:8]}"


def validate_run_id(run_id):
    """Reject path separators, traversal, and unsafe run identifiers."""

    if not RUN_ID_PATTERN.fullmatch(str(run_id)):
        raise ValueError("run ID must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}")
    return str(run_id)


def git_state(repository_root):
    """Capture commit/branch/dirty state and deterministic dirty-tree hash."""

    requested_root = Path(repository_root).resolve()
    root = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=requested_root, check=True, capture_output=True, text=True,
    ).stdout.strip()).resolve()

    def git(*arguments, text=True):
        return subprocess.run(
            ["git", *arguments], cwd=root, check=True,
            capture_output=True, text=text,
        ).stdout

    commit = git("rev-parse", "HEAD").strip()
    branch = git("branch", "--show-current").strip()
    diff = git("diff", "--binary", "HEAD", text=False)
    untracked_raw = git(
        "ls-files", "--others", "--exclude-standard", "-z", text=False
    )
    untracked = sorted(
        item.decode("utf-8", errors="surrogateescape")
        for item in untracked_raw.split(b"\0") if item
    )
    digest = hashlib.sha256()
    digest.update(b"tracked-diff\0")
    digest.update(diff)
    for relative in untracked:
        digest.update(b"untracked-path\0")
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0content-sha256\0")
        file_hash = hashlib.sha256()
        path = root / relative
        if path.is_file():
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    file_hash.update(chunk)
        digest.update(file_hash.hexdigest().encode("ascii"))
        digest.update(b"\0")
    return {
        "repository_root": str(root),
        "commit": commit,
        "branch": branch,
        "detached": not bool(branch),
        "dirty": bool(diff or untracked),
        "diff_hash_sha256": digest.hexdigest(),
        "untracked_paths": untracked,
    }


def build_bag_command(storage_id, output_path, entries, qos_overrides_path=None):
    """Build the Humble ros2 bag command with explicit de-duplicated topics."""

    topics = list(dict.fromkeys(entry["topic"] for entry in entries))
    command = [
        "ros2", "bag", "record", "-o", str(output_path), "-s", storage_id,
        "--include-unpublished-topics",
    ]
    if qos_overrides_path is not None:
        command.extend(["--qos-profile-overrides-path", str(qos_overrides_path)])
    return [*command, *topics]


def preflight_errors(
    entries,
    graph_types,
    publisher_nodes,
    recorder_subscriptions,
    controller_ready_subscription,
    gated_zero_seen,
    operational_errors=(),
    pre_ready_nonzero_seen=False,
):
    """Return all endpoint and operational motion-readiness faults."""

    errors = []
    for entry in entries:
        if not entry["required"]:
            continue
        topic = entry["topic"]
        actual_types = set(graph_types.get(topic, ()))
        if entry["type"] not in actual_types:
            errors.append(
                f"{topic}: expected type {entry['type']}, found {sorted(actual_types)}"
            )
        publishers = publisher_nodes.get(topic, ())
        if not publishers:
            errors.append(f"{topic}: no publisher")
        if entry.get("singleton_publisher") and len(publishers) != 1:
            errors.append(
                f"{topic}: expected one publisher endpoint, found "
                f"{len(publishers)} ({sorted(publishers)})"
            )
        if topic not in recorder_subscriptions:
            errors.append(f"{topic}: rosbag2_recorder is not subscribed")
    if not controller_ready_subscription:
        errors.append("/custom_controller is not subscribed to recording readiness")
    if not gated_zero_seen:
        errors.append("no gated zero /cmd_vel observed before readiness")
    if pre_ready_nonzero_seen:
        errors.append('nonzero command observed before readiness')
    errors.extend(str(error) for error in operational_errors)
    return errors


def _endpoint_name(endpoint):
    namespace = endpoint.node_namespace.rstrip("/")
    return f"{namespace}/{endpoint.node_name}" if namespace else f"/{endpoint.node_name}"


def _is_zero(values, tolerance=1e-9):
    return all(math.isfinite(float(value)) and abs(float(value)) <= tolerance for value in values)


def operational_heartbeat_errors(
    observed_at,
    now_monotonic,
    stale_sec=OPERATIONAL_HEARTBEAT_STALE_SEC,
):
    """Return missing/stale data-plane heartbeat errors."""  # noqa: Q000
    errors = []
    for alias, observed in observed_at.items():
        if observed is None:
            errors.append(f'operational heartbeat missing: {alias}')
            continue
        age = float(now_monotonic) - float(observed)
        if age < 0.0 or age > float(stale_sec):
            errors.append(
                f'operational heartbeat stale: {alias} ({age:.3f} s)'
            )
    return errors


def operational_message_error(alias, message, mode, algorithm_profile):
    """Return why a fresh operational heartbeat is not usable."""  # noqa: Q000
    if message is None:
        return f'operational heartbeat has no message: {alias}'
    if alias in ('pose', 'simulation_pose_delayed'):
        pose = message.pose.pose
        numeric = (
            pose.position.x,
            pose.position.y,
            pose.position.z,
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
            pose.orientation.w,
        )
        quaternion_norm = math.sqrt(sum(float(value) ** 2 for value in numeric[3:]))
        x_value, y_value, z_value, w_value = (
            float(value) for value in numeric[3:]
        )
        pitch_argument = 2.0 * (
            w_value * y_value - x_value * z_value
        )
        if (
            not all(math.isfinite(float(value)) for value in numeric)
            or quaternion_norm <= 1e-9
            or not -1.0 <= pitch_argument <= 1.0
        ):
            return 'operational pose heartbeat is invalid'
    elif (
        alias in ('source_cost', 'simulation_source_cost_delayed')
        and mode == 'simulation'
    ):
        raw_cost = tuple(message.raw_cost)
        source_score = tuple(message.source_score)
        if (
            message.source_mode != message.SOURCE_SIMULATION
            or not message.source_timestamp_valid
            or not math.isfinite(float(message.source_timestamp))
            or not message.raw_cost_valid
            or not message.source_score_valid
            or not raw_cost
            or int(message.channel_count) != len(raw_cost)
            or len(raw_cost) != len(source_score)
            or not all(
                math.isfinite(float(value))
                for value in (*raw_cost, *source_score)
            )
        ):
            return 'operational simulation source-cost heartbeat is invalid'
    elif alias == 'filter_output_legacy':
        values = tuple(message.data)
        if (
            not math.isfinite(float(message.timestamp))
            or len(values) < 2
            or not all(math.isfinite(float(value)) for value in values)
        ):
            return 'operational filter-output heartbeat is invalid'
    elif alias == 'supervisor_command':
        values = (
            message.linear.x,
            message.linear.y,
            message.linear.z,
            message.angular.x,
            message.angular.y,
            message.angular.z,
        )
        if not all(math.isfinite(float(value)) for value in values):
            return 'operational supervisor-command heartbeat is invalid'
    elif alias == 'timekeeper':
        if (
            not math.isfinite(float(message.start_time))
            or (
                mode == 'simulation'
                and str(message.mode) != 'sim time'
            )
        ):
            return 'operational timekeeper heartbeat is invalid'
    elif (
        alias == 'algorithm_state'
        and algorithm_profile == 'robust_gaussian_v1'
    ):
        weights = (
            message.sensor_weight,
            message.gaussian_weight,
            message.affine_weight,
        )
        if (
            message.algorithm_profile != algorithm_profile
            or not message.state_valid
            or not message.weights_valid
            or message.state != message.STATE_SEARCH
            or not message.failsafe_valid
            or message.failsafe
            or not all(math.isfinite(float(value)) for value in weights)
        ):
            return 'operational robust algorithm-state heartbeat is invalid'
    return None


def preauthorization_lifecycle_errors(message, algorithm_profile):
    """Return robust lifecycle evidence that predates motion authorization."""
    if message is None or algorithm_profile != 'robust_gaussian_v1':
        return []
    errors = []
    state_valid = bool(getattr(message, 'state_valid', False))
    state = int(getattr(message, 'state', AlgorithmState.STATE_UNAVAILABLE))
    state_name = str(getattr(message, 'state_name', state))
    if state_valid and state != AlgorithmState.STATE_SEARCH:
        errors.append(
            'algorithm state advanced before readiness: '
            f'{state_name} ({state})'
        )
    if (
        bool(getattr(message, 'failsafe_valid', False))
        and bool(getattr(message, 'failsafe', False))
    ):
        errors.append('algorithm entered failsafe before readiness')
    if bool(getattr(message, 'previous_state_valid', False)):
        previous_state = int(
            getattr(
                message,
                'previous_state',
                AlgorithmState.STATE_UNAVAILABLE,
            )
        )
        previous_name = str(
            getattr(message, 'previous_state_name', previous_state)
        )
        errors.append(
            'algorithm transition history observed before readiness: '
            f'{previous_name} ({previous_state}) -> {state_name} ({state})'
        )
    if (
        bool(getattr(message, 'active_fill_count_valid', False))
        and int(getattr(message, 'active_fill_count', 0)) > 0
    ):
        errors.append(
            'active Gaussian fill lifecycle observed before readiness: '
            f"{int(getattr(message, 'active_fill_count', 0))}"
        )
    if bool(getattr(message, 'active_escape_fill_id_valid', False)):
        errors.append(
            'active escape fill observed before readiness: '
            f"{int(getattr(message, 'active_escape_fill_id', 0))}"
        )
    return errors


def controller_state_error(
    controllers,
    required_controllers=REQUIRED_SIMULATION_CONTROLLERS,
):
    """Return why required simulation controllers are not active."""  # noqa: Q000
    states = {
        str(controller.name): str(controller.state)
        for controller in controllers
    }
    unavailable = [
        f"{name}={states.get(name, 'missing')}"
        for name in required_controllers
        if states.get(name) != 'active'
    ]
    if unavailable:
        return 'controller manager not operational: ' + ', '.join(unavailable)
    return None


class RecordingCoordinator(Node):
    """Own readiness/stop publications and shutdown-zero observations."""

    def __init__(
        self,
        ready_topic,
        stop_topic,
        ready_rate_hz,
        heartbeat_entries=(),
        heartbeat_stale_sec=OPERATIONAL_HEARTBEAT_STALE_SEC,
        controller_manager_service=None,
        required_controllers=(),
        mode=None,
        algorithm_profile=None,
    ):
        super().__init__("gesc_gaussian_recording_coordinator")
        self._state_lock = threading.RLock()
        self.ready = False
        self.ready_topic = ready_topic
        self.ready_publisher = self.create_publisher(Bool, ready_topic, 10)
        self.stop_publisher = self.create_publisher(Bool, stop_topic, 10)
        self.zero_observed_at = {topic: None for topic in ZERO_TOPICS}
        self.nonzero_observed_at = {topic: None for topic in ZERO_TOPICS}
        self.pre_ready_nonzero_observed_at = {
            topic: None for topic in ZERO_TOPICS
        }
        self.authorization_ever_succeeded = False
        self.preauthorization_monitoring_closed = False
        self.pre_ready_lifecycle_violations = []
        self.heartbeat_observed_at = {
            entry['alias']: None for entry in heartbeat_entries
        }
        self.heartbeat_messages = {
            entry['alias']: None for entry in heartbeat_entries
        }
        self.heartbeat_stale_sec = float(heartbeat_stale_sec)
        self.mode = mode
        self.algorithm_profile = algorithm_profile
        self.operational_epoch_monotonic = None
        self.controller_manager_service = controller_manager_service
        self.required_controllers = tuple(required_controllers)
        self.last_operational_snapshot = {}
        self.heartbeat_subscriptions = []
        for entry in heartbeat_entries:
            alias = entry['alias']
            self.heartbeat_subscriptions.append(
                self.create_subscription(
                    get_message(entry['type']),
                    entry['topic'],
                    partial(self._record_heartbeat, alias),
                    10,
                )
            )
        self.controller_manager_service_type = None
        self.controller_manager_client = None
        if controller_manager_service:
            from controller_manager_msgs.srv import ListControllers
            self.controller_manager_service_type = ListControllers
            self.controller_manager_client = self.create_client(
                ListControllers,
                controller_manager_service,
            )
        self.create_subscription(Twist, ZERO_TOPICS[0], self._twist_callback, 10)
        self.create_subscription(
            StampedFloat64MultiArray, ZERO_TOPICS[1], self._array_callback, 10
        )
        self.create_subscription(
            ControlDiagnostics, ZERO_TOPICS[2], self._diagnostics_callback, 10
        )
        self.create_timer(1.0 / max(1e-6, ready_rate_hz), self.publish_ready)
        self.publish_ready()

    def publish_ready(self):
        message = Bool()
        with self._state_lock:
            message.data = bool(self.ready)
        self.ready_publisher.publish(message)

    def request_stop(self):
        with self._state_lock:
            self.ready = False
            self.preauthorization_monitoring_closed = True
        self.publish_ready()
        message = Bool()
        message.data = True
        self.stop_publisher.publish(message)

    def _record_command(self, topic, values):
        observed = time.monotonic()
        with self._state_lock:
            if _is_zero(values):
                self.zero_observed_at[topic] = observed
            else:
                self.nonzero_observed_at[topic] = observed
                if not getattr(
                    self,
                    'preauthorization_monitoring_closed',
                    False,
                ):
                    self.pre_ready_nonzero_observed_at[topic] = observed

    def _record_heartbeat(self, alias, message):
        with self._state_lock:
            observed = time.monotonic()
            self.heartbeat_observed_at[alias] = observed
            self.heartbeat_messages[alias] = message
            if (
                alias == 'algorithm_state'
                and not getattr(
                    self,
                    'preauthorization_monitoring_closed',
                    False,
                )
            ):
                known_errors = {
                    violation['error']
                    for violation in getattr(
                        self,
                        'pre_ready_lifecycle_violations',
                        (),
                    )
                }
                for error in preauthorization_lifecycle_errors(
                    message,
                    self.algorithm_profile,
                ):
                    if error not in known_errors:
                        self.pre_ready_lifecycle_violations.append({
                            'alias': alias,
                            'observed_at_monotonic': observed,
                            'error': error,
                        })
                        known_errors.add(error)

    def begin_operational_epoch(self):
        """Require fresh heartbeat receipts after graph preflight."""  # noqa: Q000
        with self._state_lock:
            self.operational_epoch_monotonic = time.monotonic()
            for alias in self.heartbeat_observed_at:
                self.heartbeat_observed_at[alias] = None
                self.heartbeat_messages[alias] = None

    def pre_ready_nonzero_seen(self):
        """Return whether any command representation moved before readiness."""  # noqa: Q000
        with self._state_lock:
            return any(
                observed is not None
                for observed in self.pre_ready_nonzero_observed_at.values()
            )

    def zero_seen(self, topic):
        """Return whether one command representation has emitted zero."""  # noqa: Q000
        with self._state_lock:
            return self.zero_observed_at.get(topic) is not None

    def _heartbeat_status(self, now):
        with self._state_lock:
            observed_at = dict(self.heartbeat_observed_at)
            heartbeat_messages = dict(self.heartbeat_messages)
            lifecycle_violations = list(
                getattr(self, 'pre_ready_lifecycle_violations', ())
            )
        errors = operational_heartbeat_errors(
            observed_at,
            now,
            self.heartbeat_stale_sec,
        )
        errors.extend(
            'pre-readiness lifecycle violation: ' + violation['error']
            for violation in lifecycle_violations
        )
        validity = {}
        for alias, observed in observed_at.items():
            message_error = (
                operational_message_error(
                    alias,
                    heartbeat_messages.get(alias),
                    self.mode,
                    self.algorithm_profile,
                )
                if observed is not None
                else None
            )
            validity[alias] = observed is not None and message_error is None
            if message_error is not None:
                errors.append(message_error)
        ages = {
            alias: None if observed is None else now - observed
            for alias, observed in observed_at.items()
        }
        return errors, ages, validity

    def _save_operational_snapshot(self, snapshot):
        with self._state_lock:
            self.last_operational_snapshot = snapshot

    def operational_snapshot(self):
        """Return an isolated copy of the latest readiness evidence."""  # noqa: Q000
        with self._state_lock:
            return dict(self.last_operational_snapshot)

    def pre_ready_nonzero_snapshot(self):
        """Return all permanently retained pre-authorization motion."""  # noqa: Q000
        with self._state_lock:
            return {
                topic: observed
                for topic, observed in (
                    self.pre_ready_nonzero_observed_at.items()
                )
                if observed is not None
            }

    def pre_ready_lifecycle_snapshot(self):
        """Return permanently retained pre-authorization lifecycle evidence."""
        with self._state_lock:
            return [
                dict(violation)
                for violation in getattr(
                    self,
                    'pre_ready_lifecycle_violations',
                    (),
                )
            ]

    def operational_errors(self, deadline=None):
        """Return current heartbeat and simulation-controller faults."""  # noqa: Q000
        now = time.monotonic()
        errors, heartbeat_ages, heartbeat_validity = (
            self._heartbeat_status(now)
        )
        snapshot = {
            'checked_at_monotonic': now,
            'epoch_monotonic': self.operational_epoch_monotonic,
            'heartbeat_stale_sec': self.heartbeat_stale_sec,
            'heartbeat_ages_sec': heartbeat_ages,
            'heartbeat_valid': heartbeat_validity,
            'pre_ready_lifecycle_violations': (
                self.pre_ready_lifecycle_snapshot()
            ),
            'controller_manager_service': self.controller_manager_service,
            'required_active_controllers': list(self.required_controllers),
            'controller_states': {},
        }
        if self.controller_manager_client is None:
            snapshot['errors'] = list(errors)
            snapshot['passed'] = not errors
            self._save_operational_snapshot(snapshot)
            return errors
        if not self.controller_manager_client.service_is_ready():
            errors = [
                *errors,
                f'controller manager service unavailable: '
                f'{self.controller_manager_service}',
            ]
            snapshot['errors'] = list(errors)
            snapshot['passed'] = False
            self._save_operational_snapshot(snapshot)
            return errors
        future = self.controller_manager_client.call_async(
            self.controller_manager_service_type.Request()
        )
        response_deadline = (
            time.monotonic() + CONTROLLER_MANAGER_RESPONSE_TIMEOUT_SEC
        )
        if deadline is not None:
            response_deadline = min(response_deadline, float(deadline))
        while not future.done() and time.monotonic() < response_deadline:
            time.sleep(0.01)
        if not future.done():
            future.cancel()
            errors = [
                *errors,
                'controller manager response timed out: '
                f'{self.controller_manager_service}',
            ]
            snapshot['errors'] = list(errors)
            snapshot['passed'] = False
            self._save_operational_snapshot(snapshot)
            return errors
        completed_at = time.monotonic()
        if (
            completed_at > response_deadline
            or deadline is not None
            and completed_at > float(deadline)
        ):
            errors = [
                *errors,
                'controller manager response completed after deadline: '
                f'{self.controller_manager_service}',
            ]
            snapshot['checked_at_monotonic'] = completed_at
            snapshot['errors'] = list(errors)
            snapshot['passed'] = False
            self._save_operational_snapshot(snapshot)
            return errors
        if future.exception() is not None:
            errors = [
                *errors,
                'controller manager call failed: '
                f'{future.exception()}',
            ]
            snapshot['errors'] = list(errors)
            snapshot['passed'] = False
            self._save_operational_snapshot(snapshot)
            return errors
        controllers = list(future.result().controller)
        now = time.monotonic()
        errors, heartbeat_ages, heartbeat_validity = (
            self._heartbeat_status(now)
        )
        snapshot['checked_at_monotonic'] = now
        snapshot['heartbeat_ages_sec'] = heartbeat_ages
        snapshot['heartbeat_valid'] = heartbeat_validity
        snapshot['controller_states'] = {
            str(controller.name): str(controller.state)
            for controller in controllers
        }
        controller_error = controller_state_error(
            controllers,
            self.required_controllers,
        )
        if controller_error is not None:
            errors.append(controller_error)
        snapshot['errors'] = list(errors)
        snapshot['passed'] = not errors
        self._save_operational_snapshot(snapshot)
        return errors

    def authorize_if_safe(self, deadline=None):
        """Atomically authorize only after a final live safety snapshot."""  # noqa: Q000
        errors = list(self.operational_errors(deadline))
        now = time.monotonic()
        with self._state_lock:
            heartbeat_errors, heartbeat_ages, heartbeat_validity = (
                self._heartbeat_status(now)
            )
            errors.extend(
                error for error in heartbeat_errors if error not in errors
            )
            if any(
                observed is not None
                for observed in self.pre_ready_nonzero_observed_at.values()
            ):
                errors.append(
                    'nonzero command observed before readiness authorization'
                )
            if deadline is not None and now > float(deadline):
                errors.append(
                    'preflight deadline expired before readiness authorization'
                )
            if getattr(
                self,
                'preauthorization_monitoring_closed',
                False,
            ):
                errors.append(
                    'preauthorization monitoring closed before readiness '
                    'authorization'
                )
            snapshot = dict(self.last_operational_snapshot)
            snapshot['authorization_checked_at_monotonic'] = now
            snapshot['heartbeat_ages_sec'] = heartbeat_ages
            snapshot['heartbeat_valid'] = heartbeat_validity
            snapshot['authorization_errors'] = list(errors)
            snapshot['authorization_passed'] = not errors
            self.last_operational_snapshot = snapshot
            if not errors:
                self.ready = True
                self.authorization_ever_succeeded = True
                self.preauthorization_monitoring_closed = True
        return errors

    def _twist_callback(self, message):
        self._record_command(
            ZERO_TOPICS[0],
            (message.linear.x, message.linear.y, message.linear.z,
             message.angular.x, message.angular.y, message.angular.z),
        )

    def _array_callback(self, message):
        self._record_command(ZERO_TOPICS[1], message.data)

    def _diagnostics_callback(self, message):
        self._record_command(ZERO_TOPICS[2], message.final_command)

    def final_zero_after(self, monotonic_time):
        with self._state_lock:
            return all(
                observed is not None and observed >= monotonic_time
                for observed in self.zero_observed_at.values()
            )


class _ConsoleCapture:
    """Line-buffer subprocess output into one durable console log."""

    def __init__(self, path):
        self._stream = Path(path).open("a", encoding="utf-8", buffering=1)
        self._lock = threading.Lock()
        self._threads = []
        self.fatal_lines = []

    def log(self, source, line):
        timestamp = _iso_now()
        with self._lock:
            self._stream.write(f"[{timestamp}] [{source}] {line.rstrip()}\n")
            lowered = line.lower()
            if source == "target" and (
                "process has died" in lowered
                or "traceback (most recent call last)" in lowered
                or "rclerror" in lowered
            ):
                self.fatal_lines.append(line.rstrip())

    def attach(self, source, process):
        def consume():
            for line in iter(process.stdout.readline, ""):
                self.log(source, line)
        thread = threading.Thread(target=consume, daemon=True)
        thread.start()
        self._threads.append(thread)

    def close(self):
        for thread in self._threads:
            thread.join(timeout=2.0)
        self._stream.close()


def _process(command, cwd):
    return subprocess.Popen(
        command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, start_new_session=True,
    )


def _process_tree(root_pid):
    """Snapshot descendants with start ticks so PID reuse cannot be signaled."""

    snapshot = {}
    pending = [int(root_pid)]
    while pending:
        pid = pending.pop()
        try:
            stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
            command = Path(f"/proc/{pid}/comm").read_text(encoding="utf-8").strip()
            children_text = Path(
                f"/proc/{pid}/task/{pid}/children"
            ).read_text(encoding="utf-8")
        except OSError:
            continue
        children = [int(value) for value in children_text.split()]
        snapshot[pid] = {
            "start_ticks": stat[21],
            "command": command,
            "children": children,
        }
        pending.extend(children)
    return snapshot


def _same_process(pid, start_ticks):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
    except OSError:
        return False
    return len(fields) > 21 and fields[21] == start_ticks


def _signal_snapshot(snapshot, names, signum, interval_sec=0.0):
    targets = [
        (pid, identity)
        for pid, identity in sorted(snapshot.items())
        if identity["command"] in names
    ]
    for index, (pid, identity) in enumerate(targets):
        if identity["command"] not in names:
            continue
        if _same_process(pid, identity["start_ticks"]):
            try:
                os.kill(pid, signum)
            except ProcessLookupError:
                pass
        if interval_sec > 0.0 and index + 1 < len(targets):
            time.sleep(interval_sec)


def _live_snapshot_processes(snapshot, names=None):
    return {
        pid: identity for pid, identity in snapshot.items()
        if (names is None or identity["command"] in names)
        and _same_process(pid, identity["start_ticks"])
    }


def _live_leaf_processes(snapshot):
    live = _live_snapshot_processes(snapshot)
    live_pids = set(live)
    return {
        pid: identity
        for pid, identity in live.items()
        if not live_pids.intersection(identity.get("children", ()))
    }


def _stop_process(
    process,
    timeout_sec,
    stop_named_descendants=(),
    signal_descendant_leaves=False,
):
    if process is None:
        return None, True
    descendants = {}
    clean = True
    if process.poll() is None:
        descendants = _process_tree(process.pid)
        if stop_named_descendants:
            names = set(stop_named_descendants)
            _signal_snapshot(descendants, names, signal.SIGINT)
            deadline = time.monotonic() + min(3.0, max(0.0, timeout_sec))
            while (
                time.monotonic() < deadline
                and _live_snapshot_processes(descendants, names)
            ):
                time.sleep(0.05)
        if signal_descendant_leaves:
            leaves = _live_leaf_processes(descendants)
            _signal_snapshot(
                leaves,
                {identity["command"] for identity in leaves.values()},
                signal.SIGINT,
                interval_sec=LEAF_SHUTDOWN_STAGGER_SEC,
            )
        else:
            os.killpg(process.pid, signal.SIGINT)
        try:
            process.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3.0)
            clean = False
    if descendants:
        # Launch can exit before all of its children. The start-time identity
        # prevents signaling a reused PID while ensuring no run contaminates
        # the next experiment.
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline and _live_snapshot_processes(descendants):
            time.sleep(0.05)
        survivors = _live_snapshot_processes(descendants)
        if survivors:
            _signal_snapshot(
                survivors,
                {identity["command"] for identity in survivors.values()},
                signal.SIGTERM,
            )
            clean = False
    return process.returncode, clean


def _cleanup_call(errors, label, callback, default=None):
    """Run one cleanup step, retaining its error without aborting teardown."""
    try:
        return callback()
    except Exception as exc:  # Cleanup must continue after a local failure.
        errors.append(f'{label}: {type(exc).__name__}: {exc}')
        return default


def _shutdown_recording_resources(
    *,
    node,
    executor,
    spin_thread,
    target_process,
    bag_process,
    shutdown_zero_timeout_sec,
    post_zero_record_sec,
    target_exit_timeout_sec,
):
    """Stop recording resources in signal-safe dependency order."""
    errors = []
    shutdown_started = time.monotonic()
    zero_complete = False
    if node is not None:
        _cleanup_call(
            errors,
            'publish readiness false and stop true',
            node.request_stop,
        )
        deadline = (
            shutdown_started + max(0.0, shutdown_zero_timeout_sec)
        )
        while time.monotonic() <= deadline:
            observed = _cleanup_call(
                errors,
                'observe final zero',
                lambda: node.final_zero_after(shutdown_started),
                default=False,
            )
            if errors and errors[-1].startswith('observe final zero:'):
                break
            if observed:
                zero_complete = True
                break
            time.sleep(0.05)
        if zero_complete:
            _cleanup_call(
                errors,
                'retain post-zero recording window',
                lambda: time.sleep(max(0.0, post_zero_record_sec)),
            )

    target_code, target_clean = _cleanup_call(
        errors,
        'stop target process',
        lambda: _stop_process(
            target_process,
            target_exit_timeout_sec,
            stop_named_descendants=('gazebo', 'gzserver', 'gzclient'),
            signal_descendant_leaves=True,
        ),
        default=(None, False),
    )
    bag_code, bag_clean = _cleanup_call(
        errors,
        'stop rosbag process',
        lambda: _stop_process(bag_process, 15.0),
        default=(None, False),
    )

    if executor is not None and node is not None:
        _cleanup_call(
            errors,
            'remove coordinator from executor',
            lambda: executor.remove_node(node),
        )
    if executor is not None:
        shutdown_result = _cleanup_call(
            errors,
            'stop coordinator executor',
            lambda: executor.shutdown(timeout_sec=2.0),
            default=False,
        )
        if shutdown_result is False and not any(
            item.startswith('stop coordinator executor:')
            for item in errors
        ):
            errors.append(
                'stop coordinator executor: executor did not stop in 2.0 s'
            )
    if spin_thread is not None:
        _cleanup_call(
            errors,
            'join coordinator spin thread',
            lambda: spin_thread.join(timeout=2.0),
        )
        is_alive = _cleanup_call(
            errors,
            'inspect coordinator spin thread',
            spin_thread.is_alive,
            default=True,
        )
        if is_alive:
            errors.append(
                'join coordinator spin thread: thread remained alive'
            )
    if node is not None:
        _cleanup_call(
            errors,
            'destroy recording coordinator',
            node.destroy_node,
        )
    context_ok = _cleanup_call(
        errors,
        'inspect rclpy context',
        rclpy.ok,
        default=False,
    )
    if context_ok:
        _cleanup_call(
            errors,
            'shutdown rclpy context',
            rclpy.try_shutdown,
        )
    return {
        'shutdown_started': shutdown_started,
        'zero_complete': zero_complete,
        'target_code': target_code,
        'target_clean': target_clean,
        'bag_code': bag_code,
        'bag_clean': bag_clean,
        'errors': errors,
    }


def _graph_snapshot(node, entries):
    graph_types = dict(node.get_topic_names_and_types())
    publishers = {}
    recorder_subscriptions = set()
    for entry in entries:
        topic = entry["topic"]
        publishers[topic] = [
            _endpoint_name(endpoint)
            for endpoint in node.get_publishers_info_by_topic(topic)
        ]
        for endpoint in node.get_subscriptions_info_by_topic(topic):
            if endpoint.node_name == "rosbag2_recorder":
                recorder_subscriptions.add(topic)
    ready_subscribers = {
        _endpoint_name(endpoint)
        for endpoint in node.get_subscriptions_info_by_topic(node.ready_topic)
    }
    return graph_types, publishers, recorder_subscriptions, ready_subscribers


def _full_node_name(name, namespace):
    namespace = namespace.rstrip("/")
    return f"{namespace}/{name}" if namespace else f"/{name}"


def _bounded_timeout(deadline, maximum):
    """Return a positive timeout capped by an optional absolute deadline."""  # noqa: Q000
    if deadline is None:
        return float(maximum)
    remaining = float(deadline) - time.monotonic()
    if remaining <= 0.0:
        raise PreflightDeadlineExceeded('preflight deadline expired')
    return min(float(maximum), remaining)


def _wait_for_parameter_response(client, request, deadline=None):
    service_name = client.srv_name
    if not client.wait_for_service(
        timeout_sec=_bounded_timeout(
            deadline,
            PARAMETER_SERVICE_AVAILABILITY_TIMEOUT_SEC,
        )
    ):
        raise TimeoutError(f"service unavailable after timeout: {service_name}")
    future = client.call_async(request)
    response_deadline = (
        time.monotonic() + PARAMETER_SNAPSHOT_TIMEOUT_SEC
    )
    if deadline is not None:
        response_deadline = min(response_deadline, float(deadline))
    while not future.done() and time.monotonic() < response_deadline:
        time.sleep(0.01)
    if not future.done():
        future.cancel()
        if deadline is not None and time.monotonic() >= float(deadline):
            raise PreflightDeadlineExceeded(
                f'preflight deadline expired waiting for {service_name}'
            )
        raise TimeoutError(f"service response timed out: {service_name}")
    if deadline is not None and time.monotonic() > float(deadline):
        raise PreflightDeadlineExceeded(
            f'preflight deadline expired waiting for {service_name}'
        )
    if future.exception() is not None:
        raise RuntimeError(
            f"service call failed for {service_name}: {future.exception()}"
        )
    return future.result()


def _insert_parameter(parameters, name, value):
    target = parameters
    components = name.split(".")
    for component in components[:-1]:
        target = target.setdefault(component, {})
    target[components[-1]] = value


def _capture_node_parameters_once(node, full_name, deadline=None):
    service_types = (
        (ListParameters, "list_parameters"),
        (GetParameters, "get_parameters"),
        (DescribeParameters, "describe_parameters"),
    )
    clients = {
        suffix: node.create_client(service_type, f"{full_name}/{suffix}")
        for service_type, suffix in service_types
    }
    try:
        listed = _wait_for_parameter_response(
            clients["list_parameters"],
            ListParameters.Request(),
            deadline,
        )
        names = sorted(listed.result.names)
        get_request = GetParameters.Request()
        get_request.names = names
        values = _wait_for_parameter_response(
            clients["get_parameters"],
            get_request,
            deadline,
        ).values
        describe_request = DescribeParameters.Request()
        describe_request.names = names
        descriptors = _wait_for_parameter_response(
            clients["describe_parameters"],
            describe_request,
            deadline,
        ).descriptors
    finally:
        for client in clients.values():
            node.destroy_client(client)

    if len(values) != len(names) or len(descriptors) != len(names):
        raise RuntimeError(
            f"parameter response length mismatch for {full_name}: "
            f"{len(names)} names, {len(values)} values, "
            f"{len(descriptors)} descriptors"
        )
    parameters = {}
    parameter_types = {}
    for name, value, descriptor in zip(names, values, descriptors):
        _insert_parameter(parameters, name, parameter_value_to_python(value))
        parameter_types[name] = Parameter.Type(descriptor.type).name.lower()
    return {
        full_name: {
            "ros__parameters": parameters,
        }
    }, parameter_types


def _capture_node_parameters(node, full_name, attempts=1, deadline=None):
    attempts = max(1, int(attempts))
    for attempt in range(attempts):
        try:
            return _capture_node_parameters_once(
                node,
                full_name,
                deadline,
            )
        except PreflightDeadlineExceeded:
            raise
        except (RuntimeError, TimeoutError, ValueError):
            if attempt + 1 >= attempts:
                raise
            time.sleep(
                _bounded_timeout(
                    deadline,
                    PARAMETER_CAPTURE_RETRY_DELAY_SEC,
                )
            )


def _capture_parameters(
    node,
    node_names,
    required_publishers,
    parameter_service_nodes,
    deadline=None,
):
    snapshot = {"captured_at_utc": _iso_now(), "nodes": {}, "failures": []}
    required_publishers = set(required_publishers)
    for name, namespace in sorted(node_names):
        _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
        full_name = _full_node_name(name, namespace)
        if full_name not in parameter_service_nodes:
            snapshot["nodes"][full_name] = {
                "parameter_services_exposed": False,
                "available": False,
                "parameters": {},
            }
            continue
        try:
            parameters, parameter_types = _capture_node_parameters(
                node,
                full_name,
                attempts=(
                    REQUIRED_PARAMETER_CAPTURE_ATTEMPTS
                    if full_name in required_publishers
                    else 1
                ),
                deadline=deadline,
            )
            snapshot["nodes"][full_name] = {
                "parameter_services_exposed": True,
                "available": True,
                "parameters": parameters,
                "parameter_types": parameter_types,
            }
        except PreflightDeadlineExceeded:
            raise
        except (RuntimeError, TimeoutError, ValueError) as exc:
            snapshot["nodes"][full_name] = {
                "parameter_services_exposed": True,
                "available": False,
                "parameters": {},
            }
            snapshot["failures"].append({
                "node": full_name,
                "required_topic_publisher": full_name in required_publishers,
                "parameter_services_exposed": True,
                "error": f"{type(exc).__name__}: {exc}",
            })
    _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
    return snapshot


def _default_asset(name):
    return Path(get_package_share_directory("ros_esc")) / "experiment_recording" / name


def _parser():
    parser = argparse.ArgumentParser(
        description="Record one simulation or physical GESC/Gaussian run."
    )
    parser.add_argument("--mode", choices=sorted(VALID_MODES), required=True)
    parser.add_argument("--metadata-input", required=True)
    parser.add_argument(
        "--runs-root", default="~/Experiments/GESC-Gaussian/runs"
    )
    parser.add_argument("--manifest", default=str(_default_asset("topic_manifest.yaml")))
    parser.add_argument("--run-id")
    parser.add_argument("--storage-id", default="sqlite3")
    parser.add_argument("--duration-sec", type=float, default=0.0)
    parser.add_argument("--preflight-timeout-sec", type=float, default=45.0)
    parser.add_argument("--recorder-ready-timeout-sec", type=float, default=15.0)
    parser.add_argument("--shutdown-zero-timeout-sec", type=float, default=3.0)
    parser.add_argument("--target-exit-timeout-sec", type=float, default=15.0)
    parser.add_argument("--post-zero-record-sec", type=float, default=0.5)
    parser.add_argument("--recording-ready-rate-hz", type=float, default=10.0)
    parser.add_argument("--recording-ready-topic", default="/gesc_gaussian/recording_ready")
    parser.add_argument("--stop-topic", default="/gesc_gaussian/stop_requested")
    parser.add_argument("target", nargs=argparse.REMAINDER)
    return parser


def run(arguments):
    """Execute a managed recording and return a process exit code."""

    manifest = load_manifest(arguments.manifest)
    entries = applicable_topics(manifest, arguments.mode)
    operational_config = operational_config_for_mode(
        manifest,
        arguments.mode,
    )
    metadata_input = load_metadata_input(arguments.metadata_input, arguments.mode)
    target = list(arguments.target)
    if target and target[0] == "--":
        target.pop(0)
    if not target:
        raise ValueError("a target command is required after --")
    heartbeat_aliases = resolve_operational_heartbeat_aliases(
        operational_config,
        metadata_input,
    )
    entries = require_operational_topics(entries, heartbeat_aliases)
    entries_by_alias = {entry['alias']: entry for entry in entries}
    heartbeat_entries = [
        entries_by_alias[alias]
        for alias in heartbeat_aliases
    ]
    if operational_config:
        operational_config['resolved_heartbeat_aliases'] = heartbeat_aliases
        operational_config['target_disturbance_coupling'] = (
            validate_operational_target_coupling(
                operational_config,
                metadata_input,
                target,
            )
        )
    if arguments.storage_id != manifest.get('storage_id', 'sqlite3'):
        raise ValueError('requested storage backend is not allowed by the manifest')
    if arguments.storage_id not in rosbag2_py.get_registered_writers():
        raise ValueError(f'rosbag writer is unavailable: {arguments.storage_id}')
    run_id = validate_run_id(
        arguments.run_id or generate_run_id(arguments.mode, metadata_input["scenario_id"])
    )
    now = _utc_now()
    run_directory = (
        Path(arguments.runs_root).expanduser().resolve()
        / now.strftime("%Y-%m-%d") / run_id
    )
    if run_directory.exists():
        raise FileExistsError(f"run directory already exists: {run_directory}")
    run_directory.mkdir(parents=True)
    bag_directory = run_directory / "bag"
    (run_directory / "notes.md").write_text(
        f"# Run notes: {run_id}\n\n{metadata_input['operator_notes']}\n",
        encoding="utf-8",
    )

    metadata = dict(metadata_input)
    metadata.update({
        "schema_version": 1,
        "run_id": run_id,
        "created_at_utc": now.isoformat().replace("+00:00", "Z"),
        "target_argv": target,
        "working_directory": str(Path.cwd()),
        "host": socket.gethostname(),
        "ros_distribution": os.environ.get("ROS_DISTRO", "unknown"),
        "rmw_implementation": os.environ.get("RMW_IMPLEMENTATION", "default"),
        "git": git_state(Path.cwd()),
        "recording": {
            "storage_id": arguments.storage_id,
            "status": "initializing",
            'infrastructure_status': 'initializing',
            'failure_stage': None,
            'preflight_passed': False,
            'initial_barrier_passed': False,
            'initial_operational_readiness_passed': (
                False if operational_config else None
            ),
            'operational_readiness_passed': (
                False if operational_config else None
            ),
            'operational_readiness_required': bool(operational_config),
            'readiness_ever_true': False,
            'preflight_timeout_sec': float(
                arguments.preflight_timeout_sec
            ),
            "complete": False,
            "completeness_passed": False,
        },
    })
    atomic_yaml(run_directory / "metadata.yaml", metadata)
    atomic_json(run_directory / "completeness.json", {
        "schema_version": 1, "run_id": run_id, "passed": False,
        "checks": {}, "topic_counts": {}, "failures": ["run did not finalize"],
        "warnings": [],
    })

    console = _ConsoleCapture(run_directory / "console.log")
    bag_process = None
    target_process = None
    node = None
    executor = None
    spin_thread = None
    run_failure = None
    zero_complete = False
    target_clean = False
    bag_clean = False
    target_code = None
    bag_code = None
    cleanup_errors = []
    resolved = {}
    current_stage = 'initialization'
    shutdown = DeferredSignalShutdown()
    shutdown.__enter__()
    try:
        rclpy.init(
            args=[],
            signal_handler_options=SignalHandlerOptions.NO,
        )
        node = RecordingCoordinator(
            arguments.recording_ready_topic,
            arguments.stop_topic,
            arguments.recording_ready_rate_hz,
            heartbeat_entries=heartbeat_entries,
            heartbeat_stale_sec=operational_config.get(
                'heartbeat_stale_sec',
                OPERATIONAL_HEARTBEAT_STALE_SEC,
            ),
            controller_manager_service=operational_config.get(
                'controller_manager_service'
            ),
            required_controllers=operational_config.get(
                'required_active_controllers',
                (),
            ),
            mode=arguments.mode,
            algorithm_profile=metadata_input['algorithm_profile'],
        )
        executor = SingleThreadedExecutor()
        executor.add_node(node)
        spin_thread = threading.Thread(target=executor.spin, daemon=True)
        spin_thread.start()

        qos_overrides = _default_asset("qos_overrides.yaml")
        bag_command = build_bag_command(
            arguments.storage_id, bag_directory, entries, qos_overrides
        )
        console.log("record_run", f"starting bag: {json.dumps(bag_command)}")
        bag_process = _process(bag_command, Path.cwd())
        console.attach("rosbag2", bag_process)
        target_process = _process(target, Path.cwd())
        console.attach("target", target_process)
        metadata["recording"]["wall_start_utc"] = _iso_now()
        metadata["recording"]["qos_overrides_path"] = str(qos_overrides)
        metadata["recording"]["status"] = "preflight"
        metadata['recording']['infrastructure_status'] = 'preflight'
        atomic_yaml(run_directory / "metadata.yaml", metadata)

        current_stage = 'graph_preflight'
        deadline = time.monotonic() + max(0.0, arguments.preflight_timeout_sec)
        recorder_deadline = time.monotonic() + max(
            0.0, arguments.recorder_ready_timeout_sec
        )
        last_errors = ["preflight has not run"]
        operational_epoch_started = False
        while time.monotonic() <= deadline:
            if shutdown.requested:
                raise KeyboardInterrupt
            if bag_process.poll() is not None:
                raise RuntimeError(f"rosbag exited during preflight: {bag_process.returncode}")
            if target_process.poll() is not None:
                raise RuntimeError(f"target exited during preflight: {target_process.returncode}")
            if console.fatal_lines:
                raise RuntimeError(
                    "target reported a preflight process failure: "
                    + console.fatal_lines[-1]
                )
            graph_types, publishers, bag_subscriptions, ready_subscribers = _graph_snapshot(node, entries)
            endpoint_errors = preflight_errors(
                entries, graph_types, publishers, bag_subscriptions,
                "/custom_controller" in ready_subscribers,
                node.zero_seen(ZERO_TOPICS[0]),
                pre_ready_nonzero_seen=node.pre_ready_nonzero_seen(),
            )
            if node.pre_ready_nonzero_seen():
                raise RuntimeError(
                    'preflight safety failure: nonzero command observed '
                    'before readiness'
                )
            if not endpoint_errors and operational_config:
                if not operational_epoch_started:
                    node.begin_operational_epoch()
                    operational_epoch_started = True
                    current_stage = 'operational_readiness'
                operational_errors = node.operational_errors(deadline)
                last_errors = preflight_errors(
                    entries, graph_types, publishers, bag_subscriptions,
                    '/custom_controller' in ready_subscribers,
                    node.zero_seen(ZERO_TOPICS[0]),
                    operational_errors=operational_errors,
                )
            else:
                last_errors = endpoint_errors
            if not last_errors:
                break
            missing_recorder = [
                error for error in last_errors if "rosbag2_recorder" in error
            ]
            if missing_recorder and time.monotonic() > recorder_deadline:
                raise RuntimeError(
                    "recorder subscription preflight failed: "
                    + "; ".join(missing_recorder)
                )
            time.sleep(0.1)
        if last_errors:
            raise RuntimeError("preflight failed: " + "; ".join(last_errors))
        metadata['recording']['initial_barrier_passed'] = True
        if operational_config:
            metadata['recording'][
                'initial_operational_readiness_passed'
            ] = True
        metadata['recording']['initial_barrier_passed_at_utc'] = _iso_now()
        metadata['recording']['infrastructure_status'] = 'parameter_capture'
        atomic_yaml(run_directory / 'metadata.yaml', metadata)

        required_publishers = sorted({
            owner for entry in entries if entry["required"]
            for owner in publishers.get(entry["topic"], set())
        })
        resolved = {
            "schema_version": 1,
            "captured_at_utc": _iso_now(),
            "mode": arguments.mode,
            "validation": dict(manifest.get("validation", {})),
            'operational_readiness': {
                'required': bool(operational_config),
                'configuration': operational_config,
                'pre_parameter_capture': node.operational_snapshot(),
            },
            "topics": [
                {
                    **entry,
                    "live_types": sorted(graph_types.get(entry["topic"], [])),
                    "publishers": sorted(publishers.get(entry["topic"], [])),
                    "publisher_endpoint_count": len(
                        publishers.get(entry["topic"], [])
                    ),
                    "recorder_subscribed": entry["topic"] in bag_subscriptions,
                }
                for entry in entries
            ],
        }
        _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
        atomic_yaml(run_directory / "resolved_topics.yaml", resolved)
        _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
        current_stage = 'parameter_capture'
        parameter_service_nodes = {
            service.rsplit("/", 1)[0]
            for service, types in node.get_service_names_and_types()
            if service.endswith("/list_parameters")
            and "rcl_interfaces/srv/ListParameters" in types
        }
        parameter_snapshot = _capture_parameters(
            node,
            node.get_node_names_and_namespaces(),
            required_publishers,
            parameter_service_nodes,
            deadline=deadline,
        )
        _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
        atomic_yaml(run_directory / "resolved_parameters.yaml", parameter_snapshot)
        _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
        required_parameter_failures = [
            item for item in parameter_snapshot["failures"]
            if item["required_topic_publisher"]
        ]
        if required_parameter_failures:
            raise RuntimeError("required publisher parameter snapshot failed")

        current_stage = 'final_operational_readiness'
        _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
        if operational_config:
            node.begin_operational_epoch()
        final_errors = ['post-capture readiness has not run']
        authorization_passed = False
        while time.monotonic() <= deadline:
            if shutdown.requested:
                raise KeyboardInterrupt
            if bag_process.poll() is not None:
                raise RuntimeError(
                    'rosbag exited during post-capture readiness: '
                    f'{bag_process.returncode}'
                )
            if target_process.poll() is not None:
                raise RuntimeError(
                    'target exited during post-capture readiness: '
                    f'{target_process.returncode}'
                )
            if console.fatal_lines:
                raise RuntimeError(
                    'target reported a post-capture process failure: '
                    + console.fatal_lines[-1]
                )
            (
                graph_types,
                publishers,
                bag_subscriptions,
                ready_subscribers,
            ) = _graph_snapshot(node, entries)
            final_operational_errors = (
                node.operational_errors(deadline)
                if operational_config
                else []
            )
            final_errors = preflight_errors(
                entries,
                graph_types,
                publishers,
                bag_subscriptions,
                '/custom_controller' in ready_subscribers,
                node.zero_seen(ZERO_TOPICS[0]),
                operational_errors=final_operational_errors,
                pre_ready_nonzero_seen=node.pre_ready_nonzero_seen(),
            )
            if node.pre_ready_nonzero_seen():
                raise RuntimeError(
                    'post-capture safety failure: nonzero command observed '
                    'before readiness'
                )
            if not final_errors:
                resolved['operational_readiness'][
                    'post_parameter_capture'
                ] = node.operational_snapshot()
                resolved['operational_readiness'][
                    'post_parameter_capture_errors'
                ] = []
                _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
                atomic_yaml(
                    run_directory / 'resolved_topics.yaml',
                    resolved,
                )
                _bounded_timeout(deadline, PARAMETER_SNAPSHOT_TIMEOUT_SEC)
                final_errors = node.authorize_if_safe(deadline)
                if not final_errors:
                    authorization_passed = True
                    break
            time.sleep(0.1)
        resolved['operational_readiness']['post_parameter_capture'] = (
            node.operational_snapshot()
        )
        resolved['operational_readiness']['post_parameter_capture_errors'] = (
            list(final_errors)
        )
        resolved['operational_readiness']['authorization_passed'] = (
            authorization_passed
        )
        if final_errors or not authorization_passed:
            atomic_yaml(run_directory / 'resolved_topics.yaml', resolved)
            raise RuntimeError(
                'post-capture operational readiness failed: '
                + '; '.join(final_errors)
            )
        if shutdown.requested:
            raise KeyboardInterrupt

        current_stage = 'recording'
        metadata['recording']['preflight_passed'] = True
        if operational_config:
            metadata['recording']['operational_readiness_passed'] = True
        metadata["recording"]["status"] = "recording"
        metadata['recording']['infrastructure_status'] = 'operational'
        metadata['recording']['readiness_ever_true'] = True
        metadata['recording'][
            'post_capture_barrier_passed_at_utc'
        ] = _iso_now()
        metadata["recording"]["ready_at_utc"] = _iso_now()
        metadata["resolved_topics_path"] = "resolved_topics.yaml"
        metadata["resolved_parameters_path"] = "resolved_parameters.yaml"
        atomic_yaml(run_directory / 'resolved_topics.yaml', resolved)
        atomic_yaml(run_directory / "metadata.yaml", metadata)
        node.publish_ready()
        console.log("record_run", "preflight passed; motion readiness true")

        ready_started = time.monotonic()
        while True:
            if shutdown.requested:
                raise KeyboardInterrupt
            if target_process.poll() is not None:
                raise RuntimeError(f"target exited before requested shutdown: {target_process.returncode}")
            if bag_process.poll() is not None:
                raise RuntimeError(f"rosbag exited before requested shutdown: {bag_process.returncode}")
            if arguments.duration_sec > 0.0 and time.monotonic() - ready_started >= arguments.duration_sec:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        if not metadata['recording'].get('readiness_ever_true'):
            run_failure = (
                'KeyboardInterrupt: operator requested shutdown before '
                'readiness'
            )
            metadata['recording']['failure_stage'] = current_stage
        console.log("record_run", "operator requested shutdown")
    except Exception as exc:  # Retain the failed run and all evidence.
        run_failure = f"{type(exc).__name__}: {exc}"
        metadata['recording']['failure_stage'] = current_stage
        console.log("record_run", run_failure)
    finally:
        try:
            console.log(
                'record_run',
                'shutdown initiated; readiness false and stop requested',
            )
            cleanup = _shutdown_recording_resources(
                node=node,
                executor=executor,
                spin_thread=spin_thread,
                target_process=target_process,
                bag_process=bag_process,
                shutdown_zero_timeout_sec=(
                    arguments.shutdown_zero_timeout_sec
                ),
                post_zero_record_sec=arguments.post_zero_record_sec,
                target_exit_timeout_sec=arguments.target_exit_timeout_sec,
            )
            zero_complete = cleanup['zero_complete']
            target_code = cleanup['target_code']
            target_clean = cleanup['target_clean']
            bag_code = cleanup['bag_code']
            bag_clean = cleanup['bag_clean']
            cleanup_errors.extend(cleanup['errors'])
            for error in cleanup_errors:
                console.log('record_run', f'cleanup error: {error}')
            try:
                console.close()
            except Exception as exc:
                cleanup_errors.append(
                    f'close console: {type(exc).__name__}: {exc}'
                )
        finally:
            shutdown.__exit__(None, None, None)

    if cleanup_errors:
        cleanup_failure = 'cleanup failure: ' + '; '.join(cleanup_errors)
        run_failure = (
            f'{run_failure}; {cleanup_failure}'
            if run_failure is not None else cleanup_failure
        )
        if metadata['recording'].get('failure_stage') is None:
            metadata['recording']['failure_stage'] = 'shutdown'

    readiness_ever_true = bool(
        metadata['recording'].get('readiness_ever_true')
    )
    if readiness_ever_true and run_failure is None:
        infrastructure_status = 'completed'
    elif readiness_ever_true:
        infrastructure_status = 'runtime_failed'
    else:
        infrastructure_status = {
            'graph_preflight': 'graph_preflight_failed',
            'operational_readiness': 'operational_readiness_failed',
            'parameter_capture': 'parameter_capture_failed',
            'final_operational_readiness': 'operational_readiness_failed',
            'initialization': 'startup_failed',
        }.get(current_stage, 'startup_failed')
        if metadata['recording'].get('failure_stage') is None:
            metadata['recording']['failure_stage'] = current_stage
    pre_ready_nonzero_topics = {}
    pre_ready_lifecycle_violations = []
    if node is not None:
        pre_ready_nonzero_topics = node.pre_ready_nonzero_snapshot()
        pre_ready_lifecycle_violations = (
            node.pre_ready_lifecycle_snapshot()
        )
    metadata["recording"].update({
        "status": "finalized",
        'infrastructure_status': infrastructure_status,
        "wall_end_utc": _iso_now(),
        "target_exit_code": target_code,
        "target_clean_shutdown": target_clean,
        "bag_exit_code": bag_code,
        "bag_clean_shutdown": bag_clean and bag_code == 0,
        "final_zero_observed": zero_complete,
        'pre_ready_nonzero_topics': pre_ready_nonzero_topics,
        'pre_ready_lifecycle_violations': (
            pre_ready_lifecycle_violations
        ),
        "run_error": run_failure,
        'cleanup_errors': cleanup_errors,
        "complete": bag_clean and target_clean and zero_complete and run_failure is None,
    })
    atomic_yaml(run_directory / "metadata.yaml", metadata)

    from .validate_run import validate_run_directory
    report = validate_run_directory(run_directory, write_report=True)
    metadata["recording"]["completeness_passed"] = bool(report["passed"])
    atomic_yaml(run_directory / "metadata.yaml", metadata)
    print(str(run_directory))
    return 0 if report["passed"] else 1


def main(args=None):
    """Console entry point."""

    parsed = _parser().parse_args(args)
    try:
        return run(parsed)
    except Exception as exc:
        print(f"record_run: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
