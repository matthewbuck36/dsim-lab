"""Focused unit tests for the Phase 05 recording and validation core."""

import datetime as dt
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from ros_esc.experiment_recording.record_run import (
    _capture_parameters,
    _full_node_name,
    _parameter_types,
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

    monkeypatch.setattr(
        "ros_esc.experiment_recording.record_run.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="  enabled (type: bool)\n  gains (type: double_array)\n"
        ),
    )
    assert _parameter_types("/supervisor") == {
        "enabled": "bool",
        "gains": "double_array",
    }


def test_parallel_parameter_capture_preserves_order_types_and_failures(
    monkeypatch,
):
    """Retain deterministic snapshot semantics across independent workers."""
    def fake_run(command, **_kwargs):
        node = command[3]
        if node == "/bad":
            raise __import__('subprocess').TimeoutExpired(command, 15.0)
        if command[2] == "dump":
            return SimpleNamespace(
                stdout=f"/{node.lstrip('/')}:\n  ros__parameters:\n"
                "    enabled: true\n"
            )
        return SimpleNamespace(stdout="  enabled (type: bool)\n")

    monkeypatch.setattr(
        "ros_esc.experiment_recording.record_run.subprocess.run",
        fake_run,
    )

    snapshot = _capture_parameters(
        [("z", "/"), ("bad", "/"), ("a", "/"), ("no_params", "/")],
        {"/bad"},
        {"/a", "/bad", "/z"},
    )

    assert list(snapshot["nodes"]) == ["/a", "/bad", "/no_params", "/z"]
    assert snapshot["nodes"]["/a"]["parameter_types"] == {"enabled": "bool"}
    assert snapshot["nodes"]["/no_params"] == {
        "parameter_services_exposed": False,
        "available": False,
        "parameters": {},
    }
    assert snapshot["failures"] == [{
        "node": "/bad",
        "required_topic_publisher": True,
        "parameter_services_exposed": True,
        "error": "TimeoutExpired: Command '['ros2', 'param', 'dump', "
        "'/bad', '--print']' timed out after 15.0 seconds",
    }]


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
