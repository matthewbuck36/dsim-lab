"""Focused unit tests for the Phase 05 recording and validation core."""

import datetime as dt
from pathlib import Path
import signal
from types import SimpleNamespace

import pytest
from rcl_interfaces.msg import ParameterDescriptor, ParameterType, ParameterValue
import yaml

from ros_esc.experiment_recording.record_run import (
    _capture_parameters,
    _full_node_name,
    _insert_parameter,
    _stop_process,
    applicable_topics,
    build_bag_command,
    generate_run_id,
    git_state,
    load_manifest,
    load_metadata_input,
    preflight_errors,
    validate_run_id,
)
from ros_esc.experiment_recording.validate_run import (
    timestamp_regressions,
    timestamps_within_clock,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPOSITORY_ROOT / "ros2_ws/src/ros_esc"
MANIFEST = PACKAGE_ROOT / "ros_esc/experiment_recording/topic_manifest.yaml"
METADATA = PACKAGE_ROOT / "test/fixtures/recording_smoke_metadata.yaml"


def test_manifest_has_unique_audited_required_topics_and_mode_filtering():
    manifest = load_manifest(MANIFEST)
    simulation = applicable_topics(manifest, "simulation")
    physical = applicable_topics(manifest, "physical")

    assert manifest["storage_id"] == "sqlite3"
    assert manifest["validation"]["timestamp_regression_tolerance_sec"] == 0.15
    assert len({entry["topic"] for entry in simulation}) == len(simulation)
    assert all(entry["topic"].startswith("/") for entry in simulation)
    required_sim = {entry["alias"] for entry in simulation if entry["required"]}
    required_physical = {entry["alias"] for entry in physical if entry["required"]}
    assert {"clock", "encoder", "joint_states"} <= required_sim
    assert not ({"clock", "encoder", "joint_states"} & required_physical)
    assert {"source_cost", "command_final", "pose", "recording_ready"} <= required_physical


def test_manifest_rejects_duplicate_topics(tmp_path):
    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    document["topics"][1]["topic"] = document["topics"][0]["topic"]
    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate manifest topic"):
        load_manifest(duplicate)


@pytest.mark.parametrize("run_id", ["../escape", "a/b", "", " space", "x" * 129])
def test_run_id_rejects_unsafe_values(run_id):
    with pytest.raises(ValueError):
        validate_run_id(run_id)


def test_generated_run_id_is_safe_and_deterministic_except_uuid():
    now = dt.datetime(2026, 7, 21, 12, 3, 4, 5678, tzinfo=dt.timezone.utc)
    run_id = generate_run_id("simulation", "three lights / smoke", now=now)

    assert run_id.startswith("20260721T120304005678Z_simulation_three-lights-smoke_")
    assert validate_run_id(run_id) == run_id


def test_metadata_accepts_audited_simulation_profiles_only(tmp_path):
    metadata = load_metadata_input(METADATA, "simulation")
    assert metadata["algorithm_profile"] == "robust_gaussian_v1"

    metadata["algorithm_profile"] = "legacy"
    legacy = tmp_path / "legacy.yaml"
    legacy.write_text(yaml.safe_dump(metadata), encoding="utf-8")
    assert load_metadata_input(legacy, "simulation")["algorithm_profile"] == "legacy"

    metadata["algorithm_profile"] = "unknown"
    unknown = tmp_path / "unknown.yaml"
    unknown.write_text(yaml.safe_dump(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="algorithm_profile"):
        load_metadata_input(unknown, "simulation")

    metadata["algorithm_profile"] = "legacy"
    metadata["mode"] = "physical"
    wrong = tmp_path / "wrong.yaml"
    wrong.write_text(yaml.safe_dump(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="algorithm_profile"):
        load_metadata_input(wrong, "physical")


def test_bag_command_uses_sqlite_explicit_topics_and_no_shell():
    entries = applicable_topics(load_manifest(MANIFEST), "simulation")
    command = build_bag_command(
        "sqlite3", "/tmp/example bag", entries, "/tmp/qos overrides.yaml"
    )

    assert command[:8] == [
        "ros2", "bag", "record", "-o", "/tmp/example bag", "-s", "sqlite3",
        "--include-unpublished-topics",
    ]
    assert command[8:10] == [
        "--qos-profile-overrides-path", "/tmp/qos overrides.yaml"
    ]
    assert "/cmd_vel" in command
    assert command.count("/cmd_vel") == 1


def test_preflight_reports_every_motion_blocker():
    entries = [
        {
            "alias": "command_final", "topic": "/cmd_vel",
            "type": "geometry_msgs/msg/Twist", "required": True,
        },
        {
            "alias": "optional", "topic": "/optional",
            "type": "std_msgs/msg/String", "required": False,
        },
    ]
    failures = preflight_errors(
        entries,
        {"/cmd_vel": ["std_msgs/msg/String"]},
        {"/cmd_vel": set()},
        set(),
        False,
        False,
    )

    assert any("expected type" in failure for failure in failures)
    assert any("no publisher" in failure for failure in failures)
    assert any("rosbag2_recorder" in failure for failure in failures)
    assert any("custom_controller" in failure for failure in failures)
    assert any("gated zero" in failure for failure in failures)


def test_preflight_rejects_duplicate_singleton_publisher_endpoints():
    entries = [{
        "alias": "algorithm_state",
        "topic": "/gesc_gaussian/algorithm_state",
        "type": "ros_esc_interfaces/msg/AlgorithmState",
        "required": True,
        "singleton_publisher": True,
    }]

    failures = preflight_errors(
        entries,
        {"/gesc_gaussian/algorithm_state": [
            "ros_esc_interfaces/msg/AlgorithmState"
        ]},
        {"/gesc_gaussian/algorithm_state": [
            "/gesc_gaussian_supervisor", "/gesc_gaussian_supervisor"
        ]},
        {"/gesc_gaussian/algorithm_state"},
        True,
        True,
    )

    assert failures == [
        "/gesc_gaussian/algorithm_state: expected one publisher endpoint, "
        "found 2 (['/gesc_gaussian_supervisor', "
        "'/gesc_gaussian_supervisor'])"
    ]


def test_parameter_snapshot_helpers_preserve_node_paths_and_ros_types(monkeypatch):
    assert _full_node_name("supervisor", "/") == "/supervisor"
    assert _full_node_name("supervisor", "/robot") == "/robot/supervisor"

    parameters = {}
    _insert_parameter(parameters, "enabled", True)
    _insert_parameter(parameters, "nested.gains", [1.0, 2.0])
    assert parameters == {
        "enabled": True,
        "nested": {"gains": [1.0, 2.0]},
    }


def test_parameter_capture_preserves_order_types_and_failures(monkeypatch):
    """Retain deterministic snapshot semantics and required failures."""
    service_waits = {}

    class FakeFuture:
        def __init__(self, response):
            self.response = response

        def done(self):
            return True

        def cancel(self):
            raise AssertionError("completed fake future must not be cancelled")

        def exception(self):
            return None

        def result(self):
            return self.response

    class FakeClient:
        def __init__(self, service_name):
            self.srv_name = service_name

        def wait_for_service(self, timeout_sec):
            assert timeout_sec == 1.0
            service_waits[self.srv_name] = service_waits.get(self.srv_name, 0) + 1
            if self.srv_name.startswith("/bad/"):
                return False
            if self.srv_name == "/flaky/list_parameters":
                return service_waits[self.srv_name] > 1
            return True

        def call_async(self, request):
            if self.srv_name.endswith("/list_parameters"):
                response = SimpleNamespace(
                    result=SimpleNamespace(names=["enabled", "nested.gains"])
                )
            elif self.srv_name.endswith("/get_parameters"):
                assert request.names == ["enabled", "nested.gains"]
                response = SimpleNamespace(values=[
                    ParameterValue(
                        type=ParameterType.PARAMETER_BOOL,
                        bool_value=True,
                    ),
                    ParameterValue(
                        type=ParameterType.PARAMETER_DOUBLE_ARRAY,
                        double_array_value=[1.0, 2.0],
                    ),
                ])
            else:
                assert request.names == ["enabled", "nested.gains"]
                response = SimpleNamespace(descriptors=[
                    ParameterDescriptor(
                        name="enabled",
                        type=ParameterType.PARAMETER_BOOL,
                    ),
                    ParameterDescriptor(
                        name="nested.gains",
                        type=ParameterType.PARAMETER_DOUBLE_ARRAY,
                    ),
                ])
            return FakeFuture(response)

    class FakeNode:
        def __init__(self):
            self.destroyed = []

        def create_client(self, _service_type, service_name):
            return FakeClient(service_name)

        def destroy_client(self, client):
            self.destroyed.append(client.srv_name)

    node = FakeNode()
    monkeypatch.setattr(
        "ros_esc.experiment_recording.record_run.time.sleep",
        lambda _seconds: None,
    )

    snapshot = _capture_parameters(
        node,
        [
            ("z", "/"),
            ("bad", "/"),
            ("a", "/"),
            ("flaky", "/"),
            ("no_params", "/"),
        ],
        {"/bad", "/flaky"},
        {"/a", "/bad", "/flaky", "/z"},
    )

    assert list(snapshot["nodes"]) == [
        "/a",
        "/bad",
        "/flaky",
        "/no_params",
        "/z",
    ]
    assert snapshot["nodes"]["/a"]["parameters"] == {
        "/a": {
            "ros__parameters": {
                "enabled": True,
                "nested": {"gains": [1.0, 2.0]},
            },
        },
    }
    assert snapshot["nodes"]["/a"]["parameter_types"] == {
        "enabled": "bool",
        "nested.gains": "double_array",
    }
    assert snapshot["nodes"]["/flaky"]["available"] is True
    assert service_waits["/flaky/list_parameters"] == 2
    assert snapshot["nodes"]["/no_params"] == {
        "parameter_services_exposed": False,
        "available": False,
        "parameters": {},
    }
    assert snapshot["failures"] == [{
        "node": "/bad",
        "required_topic_publisher": True,
        "parameter_services_exposed": True,
        "error": "TimeoutError: service unavailable after timeout: "
        "/bad/list_parameters",
    }]
    assert len(node.destroyed) == 21


def test_coordinated_shutdown_signals_only_descendant_leaves(monkeypatch):
    live_pids = {1234, 1235, 1236, 1237, 1238}

    class FakeProcess:
        pid = 1234
        returncode = 0

        def poll(self):
            return None

        def wait(self, timeout):
            assert timeout == 30.0
            live_pids.clear()
            return self.returncode

    signals = []
    snapshot = {
        1234: {
            "start_ticks": "1",
            "command": "ros2",
            "children": [1235, 1237],
        },
        1235: {
            "start_ticks": "2",
            "command": "ros2",
            "children": [1236],
        },
        1236: {
            "start_ticks": "3",
            "command": "python3",
            "children": [],
        },
        1237: {
            "start_ticks": "4",
            "command": "ros2",
            "children": [1238],
        },
        1238: {
            "start_ticks": "5",
            "command": "python3",
            "children": [],
        },
    }
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run._process_tree',
        lambda _pid: snapshot,
    )
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run._same_process',
        lambda pid, _start_ticks: pid in live_pids,
    )
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.os.kill',
        lambda pid, signum: signals.append((pid, signum)),
    )
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.os.killpg',
        lambda _pid, _signum: pytest.fail(
            'coordinated shutdown must not signal the process group'
        ),
    )
    sleeps = []
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.time.sleep',
        lambda seconds: sleeps.append(seconds),
    )

    return_code, clean = _stop_process(
        FakeProcess(),
        30.0,
        signal_descendant_leaves=True,
    )

    assert return_code == 0
    assert clean
    assert signals == [
        (1236, signal.SIGINT),
        (1238, signal.SIGINT),
    ]
    assert sleeps == [0.1]


def test_amended_timestamp_tolerance_accepts_measured_boundary_only():
    tolerance = 150_000_000

    assert timestamp_regressions([0, 300_000_000, 200_000_000], tolerance) == []
    assert timestamp_regressions(
        [0, 400_000_001, 200_000_000], tolerance
    ) == [{"previous": 400_000_001, "current": 200_000_000}]
    assert timestamps_within_clock(
        [200_000_000, 1_000_000_000], 100_000_000, 1_100_000_000, tolerance
    )
    assert not timestamps_within_clock(
        [1_784_675_298_000_000_000],
        100_000_000,
        1_100_000_000,
        tolerance,
    )


def test_git_state_hash_changes_with_untracked_content(tmp_path):
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("tracked\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=tmp_path, check=True)

    first = git_state(tmp_path)
    untracked = tmp_path / "new.txt"
    untracked.write_text("one\n", encoding="utf-8")
    second = git_state(tmp_path)
    untracked.write_text("two\n", encoding="utf-8")
    third = git_state(tmp_path)

    assert first["dirty"] is False
    assert second["dirty"] is True
    assert len({first["diff_hash_sha256"], second["diff_hash_sha256"], third["diff_hash_sha256"]}) == 3
