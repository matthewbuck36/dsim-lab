#!/usr/bin/env python3

"""Run one motion-gated experiment and record its complete ROS interface."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
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
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from ros_esc_interfaces.msg import ControlDiagnostics, StampedFloat64MultiArray
import rosbag2_py
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
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_manifest(path):
    """Load and validate the repository topic manifest."""

    manifest = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("topic manifest schema_version must be 1")
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
    return manifest


def applicable_topics(manifest, mode):
    """Return manifest entries for a mode, preserving manifest order."""

    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {sorted(VALID_MODES)}")
    return [entry for entry in manifest["topics"] if mode in entry["modes"]]


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
):
    """Return all motion-blocking topic/type/publisher/subscription faults."""

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
    return errors


def _endpoint_name(endpoint):
    namespace = endpoint.node_namespace.rstrip("/")
    return f"{namespace}/{endpoint.node_name}" if namespace else f"/{endpoint.node_name}"


def _is_zero(values, tolerance=1e-9):
    return all(math.isfinite(float(value)) and abs(float(value)) <= tolerance for value in values)


class RecordingCoordinator(Node):
    """Own readiness/stop publications and shutdown-zero observations."""

    def __init__(self, ready_topic, stop_topic, ready_rate_hz):
        super().__init__("gesc_gaussian_recording_coordinator")
        self.ready = False
        self.ready_topic = ready_topic
        self.ready_publisher = self.create_publisher(Bool, ready_topic, 10)
        self.stop_publisher = self.create_publisher(Bool, stop_topic, 10)
        self.zero_observed_at = {topic: None for topic in ZERO_TOPICS}
        self.nonzero_observed_at = {topic: None for topic in ZERO_TOPICS}
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
        message.data = bool(self.ready)
        self.ready_publisher.publish(message)

    def request_stop(self):
        self.ready = False
        self.publish_ready()
        message = Bool()
        message.data = True
        self.stop_publisher.publish(message)

    def _record_command(self, topic, values):
        observed = time.monotonic()
        if _is_zero(values):
            self.zero_observed_at[topic] = observed
        else:
            self.nonzero_observed_at[topic] = observed

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
        snapshot[pid] = {"start_ticks": stat[21], "command": command}
        pending.extend(int(value) for value in children_text.split())
    return snapshot


def _same_process(pid, start_ticks):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
    except OSError:
        return False
    return len(fields) > 21 and fields[21] == start_ticks


def _signal_snapshot(snapshot, names, signum):
    for pid, identity in snapshot.items():
        if identity["command"] not in names:
            continue
        if _same_process(pid, identity["start_ticks"]):
            try:
                os.kill(pid, signum)
            except ProcessLookupError:
                pass


def _live_snapshot_processes(snapshot, names=None):
    return {
        pid: identity for pid, identity in snapshot.items()
        if (names is None or identity["command"] in names)
        and _same_process(pid, identity["start_ticks"])
    }


def _stop_process(process, timeout_sec, stop_named_descendants=()):
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


def _parameter_types(full_name):
    result = subprocess.run(
        ["ros2", "param", "list", full_name, "--param-type"],
        check=True, capture_output=True, text=True, timeout=5.0,
    )
    types = {}
    pattern = re.compile(r"^\s*(.+?)\s+\(type:\s*(.+?)\)\s*$")
    for line in result.stdout.splitlines():
        match = pattern.match(line)
        if match:
            types[match.group(1)] = match.group(2)
    return types


def _capture_parameters(node_names, required_publishers, parameter_service_nodes):
    snapshot = {"captured_at_utc": _iso_now(), "nodes": {}, "failures": []}
    required_publishers = set(required_publishers)
    available = []
    for name, namespace in sorted(node_names):
        full_name = _full_node_name(name, namespace)
        if full_name not in parameter_service_nodes:
            snapshot["nodes"][full_name] = {
                "parameter_services_exposed": False,
                "available": False,
                "parameters": {},
            }
            continue
        available.append(full_name)

    def capture(full_name):
        try:
            result = subprocess.run(
                ["ros2", "param", "dump", full_name, "--print"],
                check=True, capture_output=True, text=True, timeout=5.0,
            )
            return full_name, {
                "parameter_services_exposed": True,
                "available": True,
                "parameters": yaml.safe_load(result.stdout) or {},
                "parameter_types": _parameter_types(full_name),
            }, None
        except (subprocess.SubprocessError, yaml.YAMLError) as exc:
            return full_name, {
                "parameter_services_exposed": True,
                "available": False,
                "parameters": {},
            }, {
                "node": full_name,
                "required_topic_publisher": full_name in required_publishers,
                "parameter_services_exposed": True,
                "error": f"{type(exc).__name__}: {exc}",
            }

    workers = min(4, len(available))
    if workers:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            captured = list(executor.map(capture, available))
        for full_name, node_snapshot, failure in captured:
            snapshot["nodes"][full_name] = node_snapshot
            if failure is not None:
                snapshot["failures"].append(failure)
    snapshot["nodes"] = dict(sorted(snapshot["nodes"].items()))
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
    metadata_input = load_metadata_input(arguments.metadata_input, arguments.mode)
    if arguments.storage_id != manifest.get("storage_id", "sqlite3"):
        raise ValueError("requested storage backend is not allowed by the manifest")
    if arguments.storage_id not in rosbag2_py.get_registered_writers():
        raise ValueError(f"rosbag writer is unavailable: {arguments.storage_id}")
    target = list(arguments.target)
    if target and target[0] == "--":
        target.pop(0)
    if not target:
        raise ValueError("a target command is required after --")

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
    resolved = {}
    try:
        rclpy.init(args=[])
        node = RecordingCoordinator(
            arguments.recording_ready_topic,
            arguments.stop_topic,
            arguments.recording_ready_rate_hz,
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
        atomic_yaml(run_directory / "metadata.yaml", metadata)

        deadline = time.monotonic() + max(0.0, arguments.preflight_timeout_sec)
        recorder_deadline = time.monotonic() + max(
            0.0, arguments.recorder_ready_timeout_sec
        )
        last_errors = ["preflight has not run"]
        while time.monotonic() <= deadline:
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
            last_errors = preflight_errors(
                entries, graph_types, publishers, bag_subscriptions,
                "/custom_controller" in ready_subscribers,
                node.zero_observed_at[ZERO_TOPICS[0]] is not None,
            )
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

        required_publishers = sorted({
            owner for entry in entries if entry["required"]
            for owner in publishers.get(entry["topic"], set())
        })
        resolved = {
            "schema_version": 1,
            "captured_at_utc": _iso_now(),
            "mode": arguments.mode,
            "validation": dict(manifest.get("validation", {})),
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
        atomic_yaml(run_directory / "resolved_topics.yaml", resolved)
        parameter_service_nodes = {
            service.rsplit("/", 1)[0]
            for service, types in node.get_service_names_and_types()
            if service.endswith("/list_parameters")
            and "rcl_interfaces/srv/ListParameters" in types
        }
        parameter_snapshot = _capture_parameters(
            node.get_node_names_and_namespaces(),
            required_publishers,
            parameter_service_nodes,
        )
        atomic_yaml(run_directory / "resolved_parameters.yaml", parameter_snapshot)
        required_parameter_failures = [
            item for item in parameter_snapshot["failures"]
            if item["required_topic_publisher"]
        ]
        if required_parameter_failures:
            raise RuntimeError("required publisher parameter snapshot failed")

        node.ready = True
        node.publish_ready()
        metadata["recording"]["status"] = "recording"
        metadata["recording"]["ready_at_utc"] = _iso_now()
        metadata["resolved_topics_path"] = "resolved_topics.yaml"
        metadata["resolved_parameters_path"] = "resolved_parameters.yaml"
        atomic_yaml(run_directory / "metadata.yaml", metadata)
        console.log("record_run", "preflight passed; motion readiness true")

        ready_started = time.monotonic()
        while True:
            if target_process.poll() is not None:
                raise RuntimeError(f"target exited before requested shutdown: {target_process.returncode}")
            if bag_process.poll() is not None:
                raise RuntimeError(f"rosbag exited before requested shutdown: {bag_process.returncode}")
            if arguments.duration_sec > 0.0 and time.monotonic() - ready_started >= arguments.duration_sec:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        console.log("record_run", "operator requested shutdown")
    except Exception as exc:  # Retain the failed run and all evidence.
        run_failure = f"{type(exc).__name__}: {exc}"
        console.log("record_run", run_failure)
    finally:
        shutdown_started = time.monotonic()
        console.log("record_run", "shutdown initiated; readiness false and stop requested")
        if node is not None:
            node.request_stop()
            deadline = shutdown_started + max(0.0, arguments.shutdown_zero_timeout_sec)
            while time.monotonic() <= deadline:
                if node.final_zero_after(shutdown_started):
                    zero_complete = True
                    break
                time.sleep(0.05)
            if zero_complete:
                time.sleep(max(0.0, arguments.post_zero_record_sec))
        target_code, target_clean = _stop_process(
            target_process,
            arguments.target_exit_timeout_sec,
            stop_named_descendants=("gazebo", "gzserver", "gzclient"),
        )
        bag_code, bag_clean = _stop_process(bag_process, 15.0)
        if executor is not None and node is not None:
            executor.remove_node(node)
            executor.shutdown()
            node.destroy_node()
        if rclpy.ok():
            rclpy.try_shutdown()
        if spin_thread is not None:
            spin_thread.join(timeout=2.0)
        console.close()

    metadata["recording"].update({
        "status": "finalized",
        "wall_end_utc": _iso_now(),
        "target_exit_code": target_code,
        "target_clean_shutdown": target_clean,
        "bag_exit_code": bag_code,
        "bag_clean_shutdown": bag_clean and bag_code == 0,
        "final_zero_observed": zero_complete,
        "run_error": run_failure,
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
