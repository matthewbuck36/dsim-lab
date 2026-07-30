"""Focused unit tests for the Phase 05 recording and validation core."""

import datetime as dt
import json
from pathlib import Path
import signal
import threading
from types import SimpleNamespace

import pytest
from rcl_interfaces.msg import ParameterDescriptor, ParameterType, ParameterValue
import rclpy

from ros_esc.experiment_recording import record_run as recorder
from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.record_run import (
    _bounded_timeout,
    _capture_parameters,
    _full_node_name,
    _insert_parameter,
    _shutdown_recording_resources,
    _stop_process,
    applicable_topics,
    atomic_json,
    build_bag_command,
    controller_state_error,
    generate_run_id,
    git_state,
    load_manifest,
    load_metadata_input,
    operational_config_for_mode,
    operational_heartbeat_errors,
    operational_message_error,
    preauthorization_lifecycle_errors,
    preflight_errors,
    PreflightDeadlineExceeded,
    RecordingCoordinator,
    require_operational_topics,
    resolve_operational_heartbeat_aliases,
    validate_operational_target_coupling,
    validate_run_id,
)
from ros_esc.experiment_recording.validate_run import (
    _json_compatible,
    algorithm_event_emission_lags,
    algorithm_event_producer_stream,
    algorithm_event_stream_regressions,
    fill_event_source_causality,
    timestamp_regressions,
    timestamps_within_clock,
    validate_run_directory,
)
import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
PACKAGE_ROOT = REPOSITORY_ROOT / "ros2_ws/src/ros_esc"
MANIFEST = PACKAGE_ROOT / "ros_esc/experiment_recording/topic_manifest.yaml"
METADATA = PACKAGE_ROOT / "test/fixtures/recording_smoke_metadata.yaml"


def _canonical_simulation_target(
    profile='legacy',
    sensor_delay=0.0,
    pose_delay=0.0,
):
    sensor_delayed = sensor_delay > 0.0
    pose_delayed = pose_delay > 0.0
    return [
        'ros2',
        'launch',
        'turtlebot3_rotating_sensor',
        'gazebo.launch.xml',
        f'algorithm_profile:={profile}',
        'use_pde_extensions:=True',
        'recording_ready_required:=True',
        'simulation_validation_support_enabled:='
        + ('True' if sensor_delayed or pose_delayed else 'False'),
        f'simulation_sensor_delay_sec:={sensor_delay}',
        f'simulation_pose_delay_sec:={pose_delay}',
        'algorithm_raw_cost_topic:='
        + (
            '/gesc_gaussian/simulation/raw_cost_delayed'
            if sensor_delayed
            else '/turtlebot3/cost_value_chatter'
        ),
        'algorithm_source_cost_topic:='
        + (
            '/gesc_gaussian/simulation/source_cost_delayed'
            if sensor_delayed
            else '/gesc_gaussian/source_cost'
        ),
        'pde_cost_history_topic:='
        + (
            '/gesc_gaussian/simulation/raw_cost_delayed'
            if sensor_delayed
            else '/turtlebot3/cost_value_chatter'
        ),
        'algorithm_pose_topic:='
        + (
            '/gesc_gaussian/simulation/pose_delayed'
            if pose_delayed
            else '/odom'
        ),
        'gaussian_fill_pose_topic:='
        + (
            '/gesc_gaussian/simulation/pose_delayed'
            if pose_delayed
            else '/odom'
        ),
    ]


def test_manifest_has_unique_audited_required_topics_and_mode_filtering():
    manifest = load_manifest(MANIFEST)
    simulation = applicable_topics(manifest, "simulation")
    physical = applicable_topics(manifest, "physical")

    assert manifest["storage_id"] == "sqlite3"
    assert manifest["validation"]["timestamp_regression_tolerance_sec"] == 0.15
    readiness = manifest['operational_readiness']['simulation']
    assert readiness['heartbeat_aliases'] == [
        'pose', 'source_cost', 'filter_output_legacy', 'timekeeper'
    ]
    assert readiness['profile_heartbeat_aliases'] == {
        'robust_gaussian_v1': [
            'algorithm_state', 'supervisor_command'
        ]
    }
    assert readiness['heartbeat_stale_sec'] == 0.5
    assert readiness['heartbeat_alias_overrides'] == {
        'sensor_delay_sec': {
            'source_cost': 'simulation_source_cost_delayed'
        },
        'pose_delay_sec': {
            'pose': 'simulation_pose_delayed'
        },
    }
    assert readiness['heartbeat_override_target_arguments'] == {
        'sensor_delay_sec': 'simulation_sensor_delay_sec',
        'pose_delay_sec': 'simulation_pose_delay_sec',
    }
    assert readiness['heartbeat_override_consumer_topics'] == {
        'sensor_delay_sec': {
            'algorithm_raw_cost_topic': [
                '/turtlebot3/cost_value_chatter',
                '/gesc_gaussian/simulation/raw_cost_delayed',
            ],
            'algorithm_source_cost_topic': [
                '/gesc_gaussian/source_cost',
                '/gesc_gaussian/simulation/source_cost_delayed',
            ],
            'pde_cost_history_topic': [
                '/turtlebot3/cost_value_chatter',
                '/gesc_gaussian/simulation/raw_cost_delayed',
            ],
        },
        'pose_delay_sec': {
            'algorithm_pose_topic': [
                '/odom',
                '/gesc_gaussian/simulation/pose_delayed',
            ],
            'gaussian_fill_pose_topic': [
                '/odom',
                '/gesc_gaussian/simulation/pose_delayed',
            ],
        },
    }
    assert readiness['controller_manager_service'] == (
        '/controller_manager/list_controllers'
    )
    assert readiness['required_active_controllers'] == [
        'joint_state_broadcaster', 'velocity_controller'
    ]
    assert 'physical' not in manifest['operational_readiness']
    metadata = {
        'algorithm_profile': 'robust_gaussian_v1',
        'environment': {
            'disturbances': {
                'sensor_delay_sec': 0.2,
                'pose_delay_sec': 0.1,
            }
        }
    }
    assert resolve_operational_heartbeat_aliases(
        readiness,
        metadata,
    ) == [
        'simulation_pose_delayed',
        'simulation_source_cost_delayed',
        'filter_output_legacy',
        'timekeeper',
        'algorithm_state',
        'supervisor_command',
    ]
    assert len({entry["topic"] for entry in simulation}) == len(simulation)
    assert all(entry["topic"].startswith("/") for entry in simulation)
    required_sim = {entry["alias"] for entry in simulation if entry["required"]}
    required_physical = {entry["alias"] for entry in physical if entry["required"]}
    assert {"clock", "encoder", "joint_states"} <= required_sim
    assert not ({"clock", "encoder", "joint_states"} & required_physical)
    assert {"source_cost", "command_final", "pose", "recording_ready"} <= required_physical
    joint_states = {
        entry['alias']: entry for entry in simulation
    }['joint_states']
    assert joint_states['expected_publishers'] == [
        '/joint_state_broadcaster',
        '/turtlebot3_joint_state',
    ]
    assert joint_states['timestamp_ordering'] == (
        'multi_publisher_within_clock'
    )


def test_manifest_rejects_duplicate_topics(tmp_path):
    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    document["topics"][1]["topic"] = document["topics"][0]["topic"]
    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate manifest topic"):
        load_manifest(duplicate)


def test_manifest_rejects_nonfinite_timestamp_tolerance(tmp_path):
    document = yaml.safe_load(MANIFEST.read_text(encoding='utf-8'))
    document['validation']['timestamp_regression_tolerance_sec'] = (
        float('nan')
    )
    invalid = tmp_path / 'invalid-tolerance.yaml'
    invalid.write_text(yaml.safe_dump(document), encoding='utf-8')

    with pytest.raises(ValueError, match='tolerance must be finite'):
        load_manifest(invalid)


def test_manifest_rejects_invalid_multi_publisher_timestamp_contracts(
    tmp_path,
):
    """Make the ordering exception narrow, explicit, and simulation-only."""
    base = yaml.safe_load(MANIFEST.read_text(encoding='utf-8'))
    joint_index = next(
        index
        for index, entry in enumerate(base['topics'])
        if entry['alias'] == 'joint_states'
    )
    mutations = [
        (
            {'expected_publishers': []},
            'expected_publishers must be a non-empty list',
        ),
        (
            {
                'expected_publishers': [
                    '/joint_state_broadcaster',
                    '/joint_state_broadcaster',
                ],
            },
            'unique absolute ROS node names',
        ),
        (
            {
                'expected_publishers': [
                    'joint_state_broadcaster',
                    '/turtlebot3_joint_state',
                ],
            },
            'unique absolute ROS node names',
        ),
        (
            {'timestamp_ordering': 'ignore_regressions'},
            'invalid timestamp_ordering',
        ),
        (
            {'expected_publishers': ['/joint_state_broadcaster']},
            'requires at least two exact expected_publishers',
        ),
        (
            {'singleton_publisher': True},
            'conflicts with singleton_publisher',
        ),
        (
            {'modes': ['simulation', 'physical']},
            'requires a simulation-only topic',
        ),
        (
            {'required': False},
            'requires a required topic',
        ),
    ]

    for sequence, (changes, expected_error) in enumerate(mutations):
        document = yaml.safe_load(yaml.safe_dump(base))
        document['topics'][joint_index].update(changes)
        invalid = tmp_path / f'invalid-multi-publisher-{sequence}.yaml'
        invalid.write_text(
            yaml.safe_dump(document),
            encoding='utf-8',
        )
        with pytest.raises(ValueError, match=expected_error):
            load_manifest(invalid)


def test_simulation_requires_operational_barrier_but_physical_bypasses_it():
    """Reject schema-v1 simulation bypasses without coupling physical mode."""
    manifest = load_manifest(MANIFEST)
    manifest['operational_readiness'] = {}

    with pytest.raises(ValueError, match='simulation manifest requires'):
        operational_config_for_mode(manifest, 'simulation')
    assert operational_config_for_mode(manifest, 'physical') == {}
    manifest['operational_readiness']['physical'] = {
        'heartbeat_aliases': ['pose'],
    }
    with pytest.raises(ValueError, match='physical mode cannot import'):
        operational_config_for_mode(manifest, 'physical')


def test_physical_coordinator_does_not_create_simulation_dependencies():
    """Keep physical preflight free of Gazebo/controller-manager checks."""
    rclpy.init()
    coordinator = RecordingCoordinator(
        '/test/physical_recording_ready',
        '/test/physical_stop',
        10.0,
        mode='physical',
        algorithm_profile='robust_gaussian_v1',
    )
    try:
        assert coordinator.heartbeat_observed_at == {}
        assert coordinator.controller_manager_client is None
        assert coordinator.controller_manager_service_type is None
    finally:
        coordinator.destroy_node()
        rclpy.shutdown()


def test_manifest_rejects_partial_simulation_operational_bypass(tmp_path):
    """Require the complete consumer-aligned simulation readiness contract."""
    document = yaml.safe_load(MANIFEST.read_text(encoding='utf-8'))
    document['operational_readiness']['simulation'][
        'heartbeat_aliases'
    ].remove('filter_output_legacy')
    partial = tmp_path / 'partial.yaml'
    partial.write_text(yaml.safe_dump(document), encoding='utf-8')

    with pytest.raises(ValueError, match='readiness is incomplete'):
        load_manifest(partial)


def test_manifest_allows_additive_operational_schema_extensions(tmp_path):
    """Require the canonical subset without blocking future consumers."""
    document = yaml.safe_load(MANIFEST.read_text(encoding='utf-8'))
    document['operational_readiness']['simulation'][
        'heartbeat_override_consumer_topics'
    ]['sensor_delay_sec']['future_consumer_topic'] = [
        '/gesc_gaussian/source_cost',
        '/gesc_gaussian/simulation/source_cost_delayed',
    ]
    extended = tmp_path / 'extended-operational.yaml'
    extended.write_text(yaml.safe_dump(document), encoding='utf-8')

    assert load_manifest(extended)['operational_readiness']['simulation'][
        'heartbeat_override_consumer_topics'
    ]['sensor_delay_sec']['future_consumer_topic']


def test_manifest_rejects_physical_operational_dependencies(tmp_path):
    """Make the physical simulation-dependency bypass code-enforced."""
    document = yaml.safe_load(MANIFEST.read_text(encoding='utf-8'))
    document['operational_readiness']['physical'] = {
        'heartbeat_aliases': ['pose'],
        'heartbeat_stale_sec': 0.5,
    }
    configured = tmp_path / 'physical-operational.yaml'
    configured.write_text(yaml.safe_dump(document), encoding='utf-8')

    with pytest.raises(ValueError, match='physical mode must not configure'):
        load_manifest(configured)


def test_selected_operational_topics_become_retained_requirements():
    """Require graph, singleton, rosbag, and minimum-count evidence."""
    entries = applicable_topics(load_manifest(MANIFEST), 'simulation')
    promoted = require_operational_topics(
        entries,
        ['simulation_pose_delayed', 'supervisor_command'],
    )
    by_alias = {entry['alias']: entry for entry in promoted}

    for alias in ('simulation_pose_delayed', 'supervisor_command'):
        assert by_alias[alias]['required'] is True
        assert by_alias[alias]['minimum_messages'] == 1
        assert by_alias[alias]['singleton_publisher'] is True
        assert by_alias[alias]['operational_required'] is True
    assert by_alias['fill_requests']['required'] is False


def test_operational_aliases_are_profile_specific_and_target_coupled():
    """Select consumed streams and reject stale delay metadata."""
    manifest = load_manifest(MANIFEST)
    readiness = operational_config_for_mode(manifest, 'simulation')
    legacy = {
        'algorithm_profile': 'legacy',
        'environment': {
            'disturbances': {
                'sensor_delay_sec': 0.0,
                'pose_delay_sec': 0.0,
            }
        },
    }
    assert resolve_operational_heartbeat_aliases(
        readiness,
        legacy,
    ) == [
        'pose',
        'source_cost',
        'filter_output_legacy',
        'timekeeper',
    ]
    target = _canonical_simulation_target()
    coupling = validate_operational_target_coupling(
        readiness,
        legacy,
        target,
    )
    assert {
        field: coupling[field]
        for field in ('sensor_delay_sec', 'pose_delay_sec')
    } == {
        'sensor_delay_sec': 0.0,
        'pose_delay_sec': 0.0,
    }
    assert coupling['consumer_topics']['pose_delay_sec'] == {
        'algorithm_pose_topic': '/odom',
        'gaussian_fill_pose_topic': '/odom',
    }
    legacy['environment']['disturbances']['pose_delay_sec'] = 0.2
    with pytest.raises(ValueError, match='metadata/target mismatch'):
        validate_operational_target_coupling(
            readiness,
            legacy,
            target,
        )
    target = _canonical_simulation_target(pose_delay=0.2)
    assert validate_operational_target_coupling(
        readiness,
        legacy,
        target,
    )['pose_delay_sec'] == 0.2
    target[-2] = 'algorithm_pose_topic:=/odom'
    with pytest.raises(ValueError, match='consumer target mismatch'):
        validate_operational_target_coupling(
            readiness,
            legacy,
            target,
        )


@pytest.mark.parametrize(
    ('sensor_delay', 'pose_delay'),
    [(0.0, 0.0), (0.2, 0.0), (0.0, 0.1), (0.2, 0.1)],
)
def test_operational_target_couples_all_delay_combinations(
    sensor_delay,
    pose_delay,
):
    manifest = load_manifest(MANIFEST)
    readiness = operational_config_for_mode(manifest, 'simulation')
    metadata = {
        'algorithm_profile': 'robust_gaussian_v1',
        'environment': {
            'disturbances': {
                'sensor_delay_sec': sensor_delay,
                'pose_delay_sec': pose_delay,
            },
        },
    }
    target = _canonical_simulation_target(
        profile='robust_gaussian_v1',
        sensor_delay=sensor_delay,
        pose_delay=pose_delay,
    )

    coupling = validate_operational_target_coupling(
        readiness,
        metadata,
        target,
    )

    assert coupling['sensor_delay_sec'] == sensor_delay
    assert coupling['pose_delay_sec'] == pose_delay


def test_operational_target_rejects_wrong_graph_profile_or_relay_gate():
    manifest = load_manifest(MANIFEST)
    readiness = operational_config_for_mode(manifest, 'simulation')
    metadata = {
        'algorithm_profile': 'robust_gaussian_v1',
        'environment': {
            'disturbances': {
                'sensor_delay_sec': 0.2,
                'pose_delay_sec': 0.0,
            },
        },
    }
    target = _canonical_simulation_target(
        profile='robust_gaussian_v1',
        sensor_delay=0.2,
    )

    wrong_graph = list(target)
    wrong_graph[2] = 'another_package'
    with pytest.raises(ValueError, match='canonical Gazebo'):
        validate_operational_target_coupling(
            readiness,
            metadata,
            wrong_graph,
        )
    wrong_profile = list(target)
    wrong_profile[4] = 'algorithm_profile:=legacy'
    with pytest.raises(ValueError, match='algorithm_profile'):
        validate_operational_target_coupling(
            readiness,
            metadata,
            wrong_profile,
        )
    relay_disabled = list(target)
    relay_disabled[7] = 'simulation_validation_support_enabled:=False'
    with pytest.raises(ValueError, match='validation_support_enabled'):
        validate_operational_target_coupling(
            readiness,
            metadata,
            relay_disabled,
        )


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
        operational_errors=['controller manager service unavailable'],
        pre_ready_nonzero_seen=True,
    )

    assert any("expected type" in failure for failure in failures)
    assert any("no publisher" in failure for failure in failures)
    assert any("rosbag2_recorder" in failure for failure in failures)
    assert any("custom_controller" in failure for failure in failures)
    assert any("gated zero" in failure for failure in failures)
    assert any('controller manager' in failure for failure in failures)
    assert any('nonzero command' in failure for failure in failures)


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


def test_preflight_requires_exact_declared_multi_publisher_owners():
    entry = {
        'alias': 'joint_states',
        'topic': '/joint_states',
        'type': 'sensor_msgs/msg/JointState',
        'required': True,
        'expected_publishers': [
            '/joint_state_broadcaster',
            '/turtlebot3_joint_state',
        ],
        'timestamp_ordering': 'multi_publisher_within_clock',
    }
    graph_types = {'/joint_states': ['sensor_msgs/msg/JointState']}
    subscriptions = {'/joint_states'}
    exact = [
        '/joint_state_broadcaster',
        '/turtlebot3_joint_state',
    ]

    assert preflight_errors(
        [entry],
        graph_types,
        {'/joint_states': exact},
        subscriptions,
        True,
        True,
    ) == []

    for actual in (
        ['/joint_state_broadcaster'],
        [*exact, '/unexpected_joint_owner'],
        [
            '/joint_state_broadcaster',
            '/joint_state_broadcaster',
        ],
    ):
        failures = preflight_errors(
            [entry],
            graph_types,
            {'/joint_states': actual},
            subscriptions,
            True,
            True,
        )
        expected_failure = (
            f'/joint_states: expected publisher endpoints {sorted(exact)}, '
            f'found {len(actual)} ({sorted(actual)})'
        )
        assert failures == [expected_failure]


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


def test_recording_shutdown_keeps_context_until_executor_thread_stops(
    monkeypatch,
):
    """Publish shutdown evidence before ordered ROS context teardown."""
    trace = []

    class FakeNode:
        def request_stop(self):
            trace.append('request_stop')

        def final_zero_after(self, _started):
            trace.append('final_zero')
            return True

        def destroy_node(self):
            trace.append('destroy_node')

    class FakeExecutor:
        def remove_node(self, _node):
            trace.append('remove_node')

        def shutdown(self, timeout_sec=None):
            trace.append(f'executor_shutdown:{timeout_sec}')
            return True

    class FakeThread:
        def join(self, timeout=None):
            trace.append(f'thread_join:{timeout}')

        def is_alive(self):
            trace.append('thread_is_alive')
            return False

    target = SimpleNamespace(label='target')
    bag = SimpleNamespace(label='bag')

    def stop_process(process, *_args, **_kwargs):
        trace.append(f'stop_{process.label}')
        return 0, True

    monkeypatch.setattr(recorder, '_stop_process', stop_process)
    monkeypatch.setattr(
        recorder.rclpy,
        'ok',
        lambda: trace.append('context_ok') or True,
    )
    monkeypatch.setattr(
        recorder.rclpy,
        'try_shutdown',
        lambda: trace.append('context_shutdown'),
    )

    result = _shutdown_recording_resources(
        node=FakeNode(),
        executor=FakeExecutor(),
        spin_thread=FakeThread(),
        target_process=target,
        bag_process=bag,
        shutdown_zero_timeout_sec=1.0,
        post_zero_record_sec=0.0,
        target_exit_timeout_sec=1.0,
    )

    assert result['errors'] == []
    assert result['zero_complete'] is True
    assert result['target_clean'] is True
    assert result['bag_clean'] is True
    assert trace == [
        'request_stop',
        'final_zero',
        'stop_target',
        'stop_bag',
        'remove_node',
        'executor_shutdown:2.0',
        'thread_join:2.0',
        'thread_is_alive',
        'destroy_node',
        'context_ok',
        'context_shutdown',
    ]


def test_recording_shutdown_continues_after_individual_cleanup_errors(
    monkeypatch,
):
    """Retain failures while still stopping every later resource owner."""
    trace = []

    class FakeNode:
        def request_stop(self):
            trace.append('request_stop')
            raise RuntimeError('publish failed')

        def final_zero_after(self, _started):
            trace.append('final_zero')
            return True

        def destroy_node(self):
            trace.append('destroy_node')

    class FakeExecutor:
        def remove_node(self, _node):
            trace.append('remove_node')

        def shutdown(self, timeout_sec=None):
            trace.append(f'executor_shutdown:{timeout_sec}')
            raise RuntimeError('executor failed')

    class FakeThread:
        def join(self, timeout=None):
            trace.append(f'thread_join:{timeout}')

        def is_alive(self):
            trace.append('thread_is_alive')
            return False

    target = SimpleNamespace(label='target')
    bag = SimpleNamespace(label='bag')

    def stop_process(process, *_args, **_kwargs):
        trace.append(f'stop_{process.label}')
        if process is target:
            raise RuntimeError('target failed')
        return 0, True

    monkeypatch.setattr(recorder, '_stop_process', stop_process)
    monkeypatch.setattr(
        recorder.rclpy,
        'ok',
        lambda: trace.append('context_ok') or True,
    )
    monkeypatch.setattr(
        recorder.rclpy,
        'try_shutdown',
        lambda: trace.append('context_shutdown'),
    )

    result = _shutdown_recording_resources(
        node=FakeNode(),
        executor=FakeExecutor(),
        spin_thread=FakeThread(),
        target_process=target,
        bag_process=bag,
        shutdown_zero_timeout_sec=1.0,
        post_zero_record_sec=0.0,
        target_exit_timeout_sec=1.0,
    )

    assert result['zero_complete'] is True
    assert result['target_clean'] is False
    assert result['bag_clean'] is True
    assert result['errors'] == [
        'publish readiness false and stop true: '
        'RuntimeError: publish failed',
        'stop target process: RuntimeError: target failed',
        'stop coordinator executor: RuntimeError: executor failed',
    ]
    assert 'stop_bag' in trace
    assert trace[-3:] == [
        'destroy_node',
        'context_ok',
        'context_shutdown',
    ]


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


def _stamp(seconds):
    whole = int(seconds)
    return SimpleNamespace(
        sec=whole,
        nanosec=int(round((seconds - whole) * 1_000_000_000)),
    )


def _event(
    event_type,
    stamp_sec,
    detail='',
    source_timestamp=float('nan'),
    source_timestamp_valid=False,
    reason_code=0,
):
    return SimpleNamespace(
        event_type=event_type,
        stamp=_stamp(stamp_sec),
        detail=detail,
        source_timestamp=source_timestamp,
        source_timestamp_valid=source_timestamp_valid,
        reason_code=reason_code,
        value_names=[],
        values=[],
    )


def test_operational_readiness_waits_for_fresh_valid_data_and_active_controllers(
    monkeypatch,
):
    observed = {
        'pose': 9.8,
        'source_cost': 9.7,
        'algorithm_state': 9.6,
    }
    assert operational_heartbeat_errors(observed, 10.0, 0.5) == []
    observed['pose'] = None
    observed['algorithm_state'] = 9.0
    errors = operational_heartbeat_errors(observed, 10.0, 0.5)
    assert 'operational heartbeat missing: pose' in errors
    assert any('algorithm_state' in error for error in errors)

    pose = SimpleNamespace(
        pose=SimpleNamespace(
            pose=SimpleNamespace(
                position=SimpleNamespace(x=1.0, y=2.0, z=0.0),
                orientation=SimpleNamespace(
                    x=0.0, y=0.0, z=0.0, w=1.0
                ),
            )
        )
    )
    assert operational_message_error(
        'pose', pose, 'simulation', 'robust_gaussian_v1'
    ) is None
    assert operational_message_error(
        'simulation_pose_delayed',
        pose,
        'simulation',
        'robust_gaussian_v1',
    ) is None
    pose.pose.pose.orientation.w = float('nan')
    assert 'pose' in operational_message_error(
        'pose', pose, 'simulation', 'robust_gaussian_v1'
    )

    source = SimpleNamespace(
        SOURCE_SIMULATION=1,
        source_mode=1,
        source_timestamp_valid=True,
        source_timestamp=9.7,
        channel_count=1,
        raw_cost_valid=True,
        source_score_valid=True,
        raw_cost=[-1.0],
        source_score=[0.8],
    )
    assert operational_message_error(
        'simulation_source_cost_delayed',
        source,
        'simulation',
        'robust_gaussian_v1',
    ) is None
    source.source_score = [float('nan')]
    assert 'source-cost' in operational_message_error(
        'source_cost',
        source,
        'simulation',
        'robust_gaussian_v1',
    )
    source.source_score = [0.8]
    source.channel_count = 2
    assert 'source-cost' in operational_message_error(
        'source_cost',
        source,
        'simulation',
        'robust_gaussian_v1',
    )
    source.channel_count = 1
    source.source_timestamp_valid = False
    assert 'source-cost' in operational_message_error(
        'source_cost',
        source,
        'simulation',
        'robust_gaussian_v1',
    )

    filter_output = SimpleNamespace(timestamp=9.7, data=[0.1, 0.2])
    assert operational_message_error(
        'filter_output_legacy',
        filter_output,
        'simulation',
        'robust_gaussian_v1',
    ) is None
    filter_output.data = [0.1]
    assert 'filter-output' in operational_message_error(
        'filter_output_legacy',
        filter_output,
        'simulation',
        'robust_gaussian_v1',
    )

    supervisor_command = SimpleNamespace(
        linear=SimpleNamespace(x=0.0, y=0.0, z=0.0),
        angular=SimpleNamespace(x=0.0, y=0.0, z=0.0),
    )
    assert operational_message_error(
        'supervisor_command',
        supervisor_command,
        'simulation',
        'robust_gaussian_v1',
    ) is None
    supervisor_command.angular.z = float('nan')
    assert 'supervisor-command' in operational_message_error(
        'supervisor_command',
        supervisor_command,
        'simulation',
        'robust_gaussian_v1',
    )

    timekeeper = SimpleNamespace(mode='sim time', start_time=0.0)
    assert operational_message_error(
        'timekeeper',
        timekeeper,
        'simulation',
        'robust_gaussian_v1',
    ) is None
    timekeeper.mode = 'real time'
    assert 'timekeeper' in operational_message_error(
        'timekeeper',
        timekeeper,
        'simulation',
        'robust_gaussian_v1',
    )

    state = SimpleNamespace(
        STATE_SEARCH=1,
        STATE_FAILSAFE=8,
        algorithm_profile='robust_gaussian_v1',
        state_valid=True,
        weights_valid=True,
        state=1,
        failsafe_valid=True,
        failsafe=False,
        sensor_weight=1.0,
        gaussian_weight=1.0,
        affine_weight=0.0,
    )
    assert operational_message_error(
        'algorithm_state',
        state,
        'simulation',
        'robust_gaussian_v1',
    ) is None
    state.state = state.STATE_FAILSAFE
    assert 'algorithm-state' in operational_message_error(
        'algorithm_state',
        state,
        'simulation',
        'robust_gaussian_v1',
    )
    state.state = 2
    assert 'algorithm-state' in operational_message_error(
        'algorithm_state',
        state,
        'simulation',
        'robust_gaussian_v1',
    )
    state.state = state.STATE_SEARCH
    state.sensor_weight = float('nan')
    assert 'algorithm-state' in operational_message_error(
        'algorithm_state',
        state,
        'simulation',
        'robust_gaussian_v1',
    )

    active = [
        SimpleNamespace(name='joint_state_broadcaster', state='active'),
        SimpleNamespace(name='velocity_controller', state='active'),
    ]
    assert controller_state_error(active) is None
    active[1].state = 'inactive'
    assert 'velocity_controller=inactive' in controller_state_error(active)

    class FakeFuture:
        def done(self):
            return True

        def exception(self):
            return None

        def result(self):
            return SimpleNamespace(controller=[
                SimpleNamespace(
                    name='joint_state_broadcaster', state='active'
                ),
                SimpleNamespace(
                    name='velocity_controller', state='active'
                ),
            ])

    class FakeClient:
        available = True

        def service_is_ready(self):
            return self.available

        def call_async(self, _request):
            return FakeFuture()

    coordinator = object.__new__(RecordingCoordinator)
    coordinator._state_lock = threading.RLock()
    coordinator.ready = False
    coordinator.pre_ready_nonzero_observed_at = {
        topic: None for topic in (
            '/cmd_vel',
            '/turtlebot3/control_value_chatter',
            '/gesc_gaussian/control_diagnostics',
        )
    }
    coordinator.heartbeat_observed_at = {}
    coordinator.heartbeat_messages = {}
    coordinator.heartbeat_stale_sec = 0.5
    coordinator.mode = 'simulation'
    coordinator.algorithm_profile = 'robust_gaussian_v1'
    coordinator.operational_epoch_monotonic = 1.0
    coordinator.controller_manager_service = (
        '/controller_manager/list_controllers'
    )
    coordinator.controller_manager_service_type = SimpleNamespace(
        Request=lambda: object()
    )
    coordinator.required_controllers = (
        'joint_state_broadcaster',
        'velocity_controller',
    )
    coordinator.last_operational_snapshot = {}
    coordinator.controller_manager_client = FakeClient()

    assert coordinator.operational_errors() == []
    coordinator.controller_manager_client.available = False
    assert any(
        'service unavailable' in error
        for error in coordinator.operational_errors()
    )

    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.time.monotonic',
        lambda: 10.0,
    )
    assert _bounded_timeout(10.4, 1.0) == pytest.approx(0.4)
    with pytest.raises(TimeoutError, match='preflight deadline'):
        _bounded_timeout(9.9, 1.0)


def test_atomic_authorization_waits_then_rejects_disappearance_and_motion(
    monkeypatch,
):
    """Keep readiness false across slow data, service loss, and callback race."""

    class FakeFuture:
        def done(self):
            return True

        def exception(self):
            return None

        def result(self):
            return SimpleNamespace(controller=[
                SimpleNamespace(
                    name='joint_state_broadcaster',
                    state='active',
                ),
                SimpleNamespace(
                    name='velocity_controller',
                    state='active',
                ),
            ])

    class FakeClient:
        available = True

        def service_is_ready(self):
            return self.available

        def call_async(self, _request):
            return FakeFuture()

    pose = SimpleNamespace(
        pose=SimpleNamespace(
            pose=SimpleNamespace(
                position=SimpleNamespace(x=0.0, y=0.0, z=0.0),
                orientation=SimpleNamespace(
                    x=0.0,
                    y=0.0,
                    z=0.0,
                    w=1.0,
                ),
            )
        )
    )
    source = SimpleNamespace(
        SOURCE_SIMULATION=1,
        source_mode=1,
        source_timestamp_valid=True,
        source_timestamp=10.0,
        channel_count=1,
        raw_cost_valid=True,
        source_score_valid=True,
        raw_cost=[-1.0],
        source_score=[0.8],
    )
    filter_output = SimpleNamespace(timestamp=10.0, data=[0.1, 0.2])
    timekeeper = SimpleNamespace(mode='sim time', start_time=0.0)
    state = SimpleNamespace(
        STATE_SEARCH=1,
        algorithm_profile='robust_gaussian_v1',
        state_valid=True,
        weights_valid=True,
        state=1,
        failsafe_valid=True,
        failsafe=False,
        sensor_weight=1.0,
        gaussian_weight=1.0,
        affine_weight=0.0,
    )
    command = SimpleNamespace(
        linear=SimpleNamespace(x=0.0, y=0.0, z=0.0),
        angular=SimpleNamespace(x=0.0, y=0.0, z=0.0),
    )
    messages = {
        'pose': pose,
        'source_cost': source,
        'filter_output_legacy': filter_output,
        'timekeeper': timekeeper,
        'algorithm_state': state,
        'supervisor_command': command,
    }
    coordinator = object.__new__(RecordingCoordinator)
    coordinator._state_lock = threading.RLock()
    coordinator.ready = False
    coordinator.authorization_ever_succeeded = False
    coordinator.preauthorization_monitoring_closed = False
    coordinator.pre_ready_lifecycle_violations = []
    coordinator.heartbeat_observed_at = {
        alias: None for alias in messages
    }
    coordinator.heartbeat_messages = {
        alias: None for alias in messages
    }
    coordinator.heartbeat_stale_sec = 0.5
    coordinator.mode = 'simulation'
    coordinator.algorithm_profile = 'robust_gaussian_v1'
    coordinator.operational_epoch_monotonic = 9.0
    coordinator.controller_manager_service = (
        '/controller_manager/list_controllers'
    )
    coordinator.controller_manager_service_type = SimpleNamespace(
        Request=lambda: object()
    )
    coordinator.required_controllers = (
        'joint_state_broadcaster',
        'velocity_controller',
    )
    coordinator.last_operational_snapshot = {}
    coordinator.controller_manager_client = FakeClient()
    coordinator.pre_ready_nonzero_observed_at = {
        topic: None for topic in (
            '/cmd_vel',
            '/turtlebot3/control_value_chatter',
            '/gesc_gaussian/control_diagnostics',
        )
    }
    coordinator.zero_observed_at = {
        topic: None
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    coordinator.nonzero_observed_at = {
        topic: None
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.time.monotonic',
        lambda: 10.0,
    )

    assert coordinator.authorize_if_safe()
    assert coordinator.ready is False
    for alias, message in messages.items():
        coordinator._record_heartbeat(alias, message)
    advanced_state = SimpleNamespace(**vars(state))
    advanced_state.state = 2
    advanced_state.state_name = 'VERIFY_EXTREMUM'
    coordinator._record_heartbeat('algorithm_state', advanced_state)
    coordinator._record_heartbeat('algorithm_state', state)
    assert any(
        'lifecycle violation' in error
        for error in coordinator.authorize_if_safe()
    )
    assert coordinator.ready is False

    coordinator.begin_operational_epoch()
    for alias, message in messages.items():
        coordinator._record_heartbeat(alias, message)
    assert any(
        'lifecycle violation' in error
        for error in coordinator.authorize_if_safe()
    )
    assert coordinator.ready is False

    coordinator.pre_ready_lifecycle_violations.clear()
    assert coordinator.authorize_if_safe() == []
    assert coordinator.ready is True

    coordinator.ready = False
    coordinator.authorization_ever_succeeded = False
    coordinator.preauthorization_monitoring_closed = False
    coordinator.begin_operational_epoch()
    for alias, message in messages.items():
        coordinator._record_heartbeat(alias, message)
    coordinator.controller_manager_client.available = False
    assert any(
        'service unavailable' in error
        for error in coordinator.authorize_if_safe()
    )
    assert coordinator.ready is False

    coordinator.controller_manager_client.available = True
    coordinator._record_command(
        '/cmd_vel',
        [0.1, 0.0, 0.0, 0.0, 0.0, 0.0],
    )
    assert any(
        'nonzero command' in error
        for error in coordinator.authorize_if_safe()
    )
    assert coordinator.ready is False

    coordinator.pre_ready_nonzero_observed_at = {
        topic: None
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    coordinator.ready = False
    coordinator.controller_manager_client.available = True
    coordinator.heartbeat_observed_at = {
        alias: 10.0 for alias in messages
    }
    coordinator.heartbeat_messages = dict(messages)
    times = iter([10.0, 10.0, 10.2, 10.2])
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.time.monotonic',
        lambda: next(times, 10.2),
    )
    assert any(
        'after deadline' in error or 'deadline expired' in error
        for error in coordinator.authorize_if_safe(deadline=10.1)
    )
    assert coordinator.ready is False


def test_never_authorized_shutdown_closes_preauthorization_monitoring():
    """Do not relabel expected post-stop state or command evidence."""
    coordinator = object.__new__(RecordingCoordinator)
    coordinator._state_lock = threading.RLock()
    coordinator.ready = False
    coordinator.authorization_ever_succeeded = False
    coordinator.preauthorization_monitoring_closed = False
    coordinator.pre_ready_lifecycle_violations = []
    coordinator.heartbeat_observed_at = {'algorithm_state': None}
    coordinator.heartbeat_messages = {'algorithm_state': None}
    coordinator.mode = 'simulation'
    coordinator.algorithm_profile = 'robust_gaussian_v1'
    coordinator.pre_ready_nonzero_observed_at = {
        topic: None for topic in (
            '/cmd_vel',
            '/turtlebot3/control_value_chatter',
            '/gesc_gaussian/control_diagnostics',
        )
    }
    coordinator.zero_observed_at = {
        topic: None
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    coordinator.nonzero_observed_at = {
        topic: None
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    coordinator.publish_ready = lambda: None
    coordinator.stop_publisher = SimpleNamespace(
        publish=lambda _message: None,
    )

    coordinator.request_stop()
    assert coordinator.preauthorization_monitoring_closed is True

    stopped_state = SimpleNamespace(
        state=8,
        state_name='FAILSAFE',
        state_valid=True,
        previous_state=1,
        previous_state_name='SEARCH',
        previous_state_valid=True,
        active_fill_count=0,
        active_fill_count_valid=True,
        active_escape_fill_id=0,
        active_escape_fill_id_valid=False,
        failsafe=True,
        failsafe_valid=True,
    )
    coordinator._record_heartbeat('algorithm_state', stopped_state)
    coordinator._record_command(
        '/cmd_vel',
        [0.1, 0.0, 0.0, 0.0, 0.0, 0.0],
    )

    assert coordinator.pre_ready_lifecycle_snapshot() == []
    assert coordinator.pre_ready_nonzero_snapshot() == {}


@pytest.mark.parametrize(
    ('field_updates', 'expected_error'),
    [
        (
            {'state': 2, 'state_name': 'VERIFY_EXTREMUM'},
            'state advanced',
        ),
        (
            {'failsafe': True},
            'entered failsafe',
        ),
        (
            {
                'previous_state': 2,
                'previous_state_name': 'VERIFY_EXTREMUM',
                'previous_state_valid': True,
            },
            'transition history',
        ),
        (
            {'active_fill_count': 1},
            'active Gaussian fill lifecycle',
        ),
        (
            {
                'active_escape_fill_id': 7,
                'active_escape_fill_id_valid': True,
            },
            'active escape fill',
        ),
    ],
)
def test_preauthorization_lifecycle_latches_each_history_signal(
    field_updates,
    expected_error,
):
    """Latch every independent robust lifecycle-history signal."""
    state = SimpleNamespace(
        state=1,
        state_name='SEARCH',
        state_valid=True,
        previous_state=0,
        previous_state_name='UNAVAILABLE',
        previous_state_valid=False,
        active_fill_count=0,
        active_fill_count_valid=True,
        active_escape_fill_id=0,
        active_escape_fill_id_valid=False,
        failsafe=False,
        failsafe_valid=True,
    )
    for field, value in field_updates.items():
        setattr(state, field, value)

    assert any(
        expected_error in error
        for error in preauthorization_lifecycle_errors(
            state,
            'robust_gaussian_v1',
        )
    )

    coordinator = object.__new__(RecordingCoordinator)
    coordinator._state_lock = threading.RLock()
    coordinator.preauthorization_monitoring_closed = False
    coordinator.pre_ready_lifecycle_violations = []
    coordinator.heartbeat_observed_at = {'algorithm_state': None}
    coordinator.heartbeat_messages = {'algorithm_state': None}
    coordinator.mode = 'simulation'
    coordinator.algorithm_profile = 'robust_gaussian_v1'
    coordinator._record_heartbeat('algorithm_state', state)
    assert any(
        expected_error in violation['error']
        for violation in coordinator.pre_ready_lifecycle_snapshot()
    )


def test_global_preflight_deadline_is_not_downgraded_to_node_failure(
    monkeypatch,
):
    """Propagate the total deadline through parameter capture unchanged."""
    monkeypatch.setattr(
        'ros_esc.experiment_recording.record_run.time.monotonic',
        lambda: 10.0,
    )
    with pytest.raises(PreflightDeadlineExceeded):
        _capture_parameters(
            SimpleNamespace(),
            [('/required', '/')],
            {'/required'},
            {'/required'},
            deadline=9.0,
        )


def test_run_rechecks_operational_epoch_after_parameter_capture(
    monkeypatch,
    tmp_path,
):
    """Exercise both run barriers and reject post-capture service loss."""

    class FakeClock:
        def __init__(self):
            self.value = 10.0

        def monotonic(self):
            return self.value

        def sleep(self, seconds):
            self.value += float(seconds)

    class FakeFuture:
        def done(self):
            return True

        def exception(self):
            return None

        def result(self):
            return SimpleNamespace(controller=[
                SimpleNamespace(
                    name='joint_state_broadcaster',
                    state='active',
                ),
                SimpleNamespace(
                    name='velocity_controller',
                    state='active',
                ),
            ])

    class FakeClient:
        available = True

        def service_is_ready(self):
            return self.available

        def call_async(self, _request):
            return FakeFuture()

    class FakeProcess:
        pid = 1234
        returncode = 0

        def poll(self):
            return None

    class FakeConsole:
        fatal_lines = []

        def __init__(self, _path):
            self.lines = []

        def log(self, source, line):
            self.lines.append((source, line))

        def attach(self, _source, _process):
            return None

        def close(self):
            return None

    class FakeExecutor:
        def add_node(self, _node):
            return None

        def spin(self):
            return None

        def remove_node(self, _node):
            return None

        def shutdown(self, timeout_sec=None):
            del timeout_sec
            return None

    pose = SimpleNamespace(
        pose=SimpleNamespace(
            pose=SimpleNamespace(
                position=SimpleNamespace(x=0.0, y=0.0, z=0.0),
                orientation=SimpleNamespace(
                    x=0.0,
                    y=0.0,
                    z=0.0,
                    w=1.0,
                ),
            ),
        ),
    )
    source = SimpleNamespace(
        SOURCE_SIMULATION=1,
        source_mode=1,
        source_timestamp_valid=True,
        source_timestamp=10.0,
        channel_count=1,
        raw_cost_valid=True,
        source_score_valid=True,
        raw_cost=[-1.0],
        source_score=[0.8],
    )
    messages = {
        'pose': pose,
        'source_cost': source,
        'filter_output_legacy': SimpleNamespace(
            timestamp=10.0,
            data=[0.1, 0.2],
        ),
        'timekeeper': SimpleNamespace(
            mode='sim time',
            start_time=0.0,
        ),
        'algorithm_state': SimpleNamespace(
            STATE_SEARCH=1,
            algorithm_profile='robust_gaussian_v1',
            state_valid=True,
            weights_valid=True,
            state=1,
            failsafe_valid=True,
            failsafe=False,
            sensor_weight=1.0,
            gaussian_weight=1.0,
            affine_weight=0.0,
        ),
        'supervisor_command': SimpleNamespace(
            linear=SimpleNamespace(x=0.0, y=0.0, z=0.0),
            angular=SimpleNamespace(x=0.0, y=0.0, z=0.0),
        ),
    }
    coordinator = object.__new__(RecordingCoordinator)
    coordinator._state_lock = threading.RLock()
    coordinator.ready = False
    coordinator.ready_topic = '/gesc_gaussian/recording_ready'
    coordinator.heartbeat_observed_at = {
        alias: None for alias in messages
    }
    coordinator.heartbeat_messages = {
        alias: None for alias in messages
    }
    coordinator.heartbeat_stale_sec = 0.5
    coordinator.mode = 'simulation'
    coordinator.algorithm_profile = 'robust_gaussian_v1'
    coordinator.operational_epoch_monotonic = None
    coordinator.controller_manager_service = (
        '/controller_manager/list_controllers'
    )
    coordinator.controller_manager_service_type = SimpleNamespace(
        Request=lambda: object(),
    )
    coordinator.required_controllers = (
        'joint_state_broadcaster',
        'velocity_controller',
    )
    coordinator.last_operational_snapshot = {}
    coordinator.controller_manager_client = FakeClient()
    coordinator.pre_ready_nonzero_observed_at = {
        topic: None for topic in (
            '/cmd_vel',
            '/turtlebot3/control_value_chatter',
            '/gesc_gaussian/control_diagnostics',
        )
    }
    coordinator.zero_observed_at = {
        topic: 10.0
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    coordinator.nonzero_observed_at = {
        topic: None
        for topic in coordinator.pre_ready_nonzero_observed_at
    }
    coordinator.get_service_names_and_types = lambda: []
    coordinator.get_node_names_and_namespaces = lambda: []
    coordinator.request_stop = lambda: setattr(
        coordinator,
        'ready',
        False,
    )
    coordinator.final_zero_after = lambda _started: True
    coordinator.destroy_node = lambda: None
    coordinator.pre_ready_nonzero_snapshot = lambda: {}

    clock = FakeClock()
    trace = []
    real_begin_epoch = coordinator.begin_operational_epoch
    real_operational_errors = coordinator.operational_errors

    def begin_epoch():
        real_begin_epoch()
        epoch = len([item for item in trace if item.startswith('epoch:')]) + 1
        trace.append(f'epoch:{epoch}')
        for alias, message in messages.items():
            coordinator.heartbeat_observed_at[alias] = clock.monotonic()
            coordinator.heartbeat_messages[alias] = message

    def operational_errors(deadline=None):
        epoch = len([item for item in trace if item.startswith('epoch:')])
        service = (
            'up'
            if coordinator.controller_manager_client.available
            else 'down'
        )
        trace.append(f'check:{epoch}:{service}')
        return real_operational_errors(deadline)

    def capture_parameters(*_args, **_kwargs):
        trace.append('capture')
        coordinator.controller_manager_client.available = False
        return {
            'captured_at_utc': '2026-07-25T00:00:00Z',
            'nodes': {},
            'failures': [],
        }

    coordinator.begin_operational_epoch = begin_epoch
    coordinator.operational_errors = operational_errors
    coordinator.authorize_if_safe = lambda _deadline=None: trace.append(
        'authorize',
    ) or []

    def graph_snapshot(_node, entries):
        graph_types = {
            entry['topic']: [entry['type']]
            for entry in entries
        }
        publishers = {
            entry['topic']: entry.get(
                'expected_publishers',
                ['/owner'],
            )
            for entry in entries
        }
        recorder_subscriptions = {
            entry['topic'] for entry in entries
        }
        return (
            graph_types,
            publishers,
            recorder_subscriptions,
            {'/custom_controller'},
        )

    monkeypatch.setattr(recorder.time, 'monotonic', clock.monotonic)
    monkeypatch.setattr(recorder.time, 'sleep', clock.sleep)
    monkeypatch.setattr(
        recorder.rosbag2_py,
        'get_registered_writers',
        lambda: ['sqlite3'],
    )
    init_calls = []
    monkeypatch.setattr(
        recorder.rclpy,
        'init',
        lambda **kwargs: init_calls.append(kwargs),
    )
    monkeypatch.setattr(recorder.rclpy, 'ok', lambda: True)
    monkeypatch.setattr(recorder.rclpy, 'try_shutdown', lambda: None)
    monkeypatch.setattr(
        recorder,
        'RecordingCoordinator',
        lambda *_args, **_kwargs: coordinator,
    )
    monkeypatch.setattr(recorder, 'SingleThreadedExecutor', FakeExecutor)
    monkeypatch.setattr(recorder, '_ConsoleCapture', FakeConsole)
    monkeypatch.setattr(recorder, '_process', lambda *_args: FakeProcess())
    monkeypatch.setattr(
        recorder,
        '_stop_process',
        lambda *_args, **_kwargs: (0, True),
    )
    monkeypatch.setattr(recorder, '_graph_snapshot', graph_snapshot)
    monkeypatch.setattr(recorder, '_capture_parameters', capture_parameters)
    monkeypatch.setattr(
        recorder,
        'git_state',
        lambda _root: {
            'commit': 'test',
            'branch': 'test',
            'dirty': False,
            'diff_hash_sha256': 'test',
        },
    )
    monkeypatch.setattr(
        recorder,
        '_default_asset',
        lambda name: MANIFEST.with_name(name),
    )
    monkeypatch.setattr(
        validator,
        'validate_run_directory',
        lambda *_args, **_kwargs: {'passed': False},
    )

    arguments = SimpleNamespace(
        manifest=str(MANIFEST),
        mode='simulation',
        metadata_input=str(METADATA),
        target=_canonical_simulation_target(
            profile='robust_gaussian_v1',
        ),
        storage_id='sqlite3',
        run_id='m4-two-barrier-test',
        runs_root=str(tmp_path),
        duration_sec=0.0,
        preflight_timeout_sec=1.0,
        recorder_ready_timeout_sec=1.0,
        shutdown_zero_timeout_sec=0.0,
        target_exit_timeout_sec=0.0,
        post_zero_record_sec=0.0,
        recording_ready_rate_hz=10.0,
        recording_ready_topic='/gesc_gaussian/recording_ready',
        stop_topic='/gesc_gaussian/stop_requested',
    )

    assert recorder.run(arguments) == 1
    assert init_calls == [{
        'args': [],
        'signal_handler_options': recorder.SignalHandlerOptions.NO,
    }]

    relevant = [
        item for item in trace
        if (
            item == 'capture'
            or item == 'authorize'
            or item.startswith('epoch:')
            or item.startswith('check:')
        )
    ]
    assert relevant[:5] == [
        'epoch:1',
        'check:1:up',
        'capture',
        'epoch:2',
        'check:2:down',
    ]
    assert coordinator.ready is False
    assert 'authorize' not in relevant

    run_directory = next(tmp_path.glob('*/m4-two-barrier-test'))
    metadata = yaml.safe_load(
        (run_directory / 'metadata.yaml').read_text(encoding='utf-8'),
    )
    resolved = yaml.safe_load(
        (run_directory / 'resolved_topics.yaml').read_text(
            encoding='utf-8',
        ),
    )
    recording = metadata['recording']
    assert recording['initial_barrier_passed'] is True
    assert recording['initial_operational_readiness_passed'] is True
    assert recording['preflight_passed'] is False
    assert recording['operational_readiness_passed'] is False
    assert recording['readiness_ever_true'] is False
    assert recording['failure_stage'] == 'final_operational_readiness'
    assert recording['infrastructure_status'] == (
        'operational_readiness_failed'
    )
    assert 'controller manager service unavailable' in (
        recording['run_error']
    )
    operational = resolved['operational_readiness']
    assert operational['pre_parameter_capture']['passed'] is True
    assert operational['post_parameter_capture']['passed'] is False
    assert operational['authorization_passed'] is False


def test_algorithm_event_timestamp_domains_are_strict_and_separate():
    tolerance = 150_000_000
    interleaved = [
        (1, _event(10, 149.3, 'candidate')),
        (2, _event(20, 141.3, 'fill created')),
    ]
    regressions, unidentified = algorithm_event_stream_regressions(
        interleaved,
        tolerance,
    )
    assert regressions == []
    assert unidentified == []

    same_producer = [
        (1, _event(20, 141.3, 'fill created')),
        (2, _event(22, 140.0, 'fill merged')),
    ]
    regressions, unidentified = algorithm_event_stream_regressions(
        same_producer,
        tolerance,
    )
    assert unidentified == []
    assert regressions[0]['producer_stream'] == 'gaussian_fill'

    shared_supervisor = [
        (1, _event(3, 10.0, 'RECENTER->SEARCH')),
        (
            2,
            _event(
                1,
                8.0,
                'post-recovery guidance epoch started',
            ),
        ),
    ]
    regressions, unidentified = algorithm_event_stream_regressions(
        shared_supervisor,
        tolerance,
    )
    assert unidentified == []
    assert len(regressions) == 1
    assert regressions[0]['producer_stream'] == 'supervisor'

    assert algorithm_event_producer_stream(
        _event(
            70,
            1.0,
            'controller watchdog: pose stale',
            reason_code=1,
        )
    ) == 'controller'
    assert algorithm_event_producer_stream(
        _event(70, 1.0, 'supervisor input invalid')
    ) == 'supervisor'
    assert algorithm_event_producer_stream(
        _event(0, 1.0, 'unknown')
    ) is None
    assert algorithm_event_producer_stream(
        _event(
            70,
            1.0,
            'controller watchdog: malformed reason',
            reason_code=0,
        )
    ) is None
    assert algorithm_event_producer_stream(
        _event(70, 1.0, 'supervisor input invalid', reason_code=1)
    ) is None
    assert algorithm_event_producer_stream(
        _event(1, 1.0, 'unrecognized configuration signature')
    ) is None


@pytest.mark.parametrize(
    ('event_type', 'detail', 'reason_code', 'producer'),
    [
        (1, 'source_mode=simulation', 0, 'cost_function'),
        (1, 'state-driven robust weights', 0, 'modified_cost'),
        (1, 'legacy fixed observational weights', 0, 'modified_cost'),
        (1, 'convergence detector configuration', 0, 'convergence_detector'),
        (1, 'robust Gaussian estimator configuration', 0, 'gaussian_fill'),
        (1, 'Gaussian fill configuration; policy=none', 0, 'gaussian_fill'),
        (1, 'measured escape configuration', 0, 'supervisor'),
        (
            1,
            'post-recovery guidance epoch started',
            0,
            'supervisor',
        ),
        (
            1,
            'post-recovery outward progress completed',
            0,
            'supervisor',
        ),
        (2, 'rotation-aware features unavailable', 1, 'cost_function'),
        (10, 'candidate', 0, 'convergence_detector'),
        (20, 'fill created', 0, 'gaussian_fill'),
        (3, 'SEARCH->VERIFY_EXTREMUM', 0, 'supervisor'),
        (70, 'controller watchdog: pose stale', 1, 'controller'),
        (70, 'pose missing', 0, 'supervisor'),
    ],
)
def test_algorithm_event_classifier_covers_current_publisher_signatures(
    event_type,
    detail,
    reason_code,
    producer,
):
    """Lock completeness classification to every current publisher owner."""
    assert algorithm_event_producer_stream(
        _event(
            event_type,
            1.0,
            detail,
            reason_code=reason_code,
        )
    ) == producer


def test_algorithm_event_emission_freshness_and_source_causality_are_separate():
    fresh = _event(
        20,
        156.9,
        'fill created',
        source_timestamp=141.2,
        source_timestamp_valid=True,
    )
    stale = _event(
        20,
        141.3,
        'fill created',
        source_timestamp=141.2,
        source_timestamp_valid=True,
    )
    clock = SimpleNamespace(clock=_stamp(156.9))
    fresh_skew = algorithm_event_emission_lags(
        [(20, fresh)],
        [(19, clock)],
    )[0]['clock_skew_nanoseconds']
    stale_skew = algorithm_event_emission_lags(
        [(20, stale)],
        [(19, clock)],
    )[0]['clock_skew_nanoseconds']
    future = _event(20, 172.5, 'future fill')
    future_skew = algorithm_event_emission_lags(
        [(20, future)],
        [(19, clock)],
    )[0]['clock_skew_nanoseconds']
    no_clock = algorithm_event_emission_lags([(18, fresh)], [(19, clock)])
    assert fresh_skew == 0
    assert stale_skew == 15_600_000_000
    assert future_skew == -15_600_000_000
    assert no_clock[0]['clock_skew_nanoseconds'] is None

    request = SimpleNamespace(timestamp=141.2)
    assert fill_event_source_causality(
        [(1, fresh)],
        [(2, request)],
    ) == []
    near_miss = SimpleNamespace(timestamp=141.2 + 5e-10)
    assert fill_event_source_causality(
        [(1, fresh)],
        [(2, near_miss)],
    )
    failures = fill_event_source_causality([(1, fresh)], [])
    assert failures[0]['source_timestamp'] == 141.2
    corrupt = _event(
        20,
        1.0,
        'fill created',
        source_timestamp=float('nan'),
        source_timestamp_valid=True,
    )
    assert fill_event_source_causality(
        [(1, corrupt)],
        [],
    )[0]['source_timestamp'] is None


def test_durable_json_is_strict_and_rejects_nonfinite_values(tmp_path):
    """Keep JSON evidence RFC-compatible instead of emitting NaN tokens."""
    output = tmp_path / 'strict.json'
    atomic_json(output, {'value': 1.0, 'missing': None})
    assert json.loads(output.read_text(encoding='utf-8')) == {
        'value': 1.0,
        'missing': None,
    }

    with pytest.raises(ValueError, match='Out of range float'):
        atomic_json(output, {'value': float('nan')})

    nonfinite_paths = []
    converted = _json_compatible(
        {'topic_counts': {float('nan'): 1}},
        nonfinite_paths=nonfinite_paths,
    )
    assert nonfinite_paths == ['$.topic_counts.<nonfinite-key>']
    json.dumps(converted, allow_nan=False)


def test_run_validator_wires_event_stream_freshness_and_causality(
    monkeypatch,
    tmp_path,
):
    """Exercise the complete report wiring without creating a real bag."""
    topics = {
        'algorithm_events': (
            '/gesc_gaussian/algorithm_events',
            'ros_esc_interfaces/msg/AlgorithmEvent',
        ),
        'clock': ('/clock', 'rosgraph_msgs/msg/Clock'),
        'recording_ready': (
            '/gesc_gaussian/recording_ready',
            'std_msgs/msg/Bool',
        ),
        'fill_requests': (
            '/gesc_gaussian/fill_requests',
            'ros_esc_interfaces/msg/StampedFloat64MultiArray',
        ),
        'algorithm_state': (
            '/gesc_gaussian/algorithm_state',
            'ros_esc_interfaces/msg/AlgorithmState',
        ),
        'stop_requested': (
            '/gesc_gaussian/stop_requested',
            'std_msgs/msg/Bool',
        ),
        'command_final': (
            '/cmd_vel',
            'geometry_msgs/msg/Twist',
        ),
        'joint_states': (
            '/joint_states',
            'sensor_msgs/msg/JointState',
        ),
        'typed_singleton': (
            '/test/singleton_stamped',
            'sensor_msgs/msg/JointState',
        ),
    }
    resolved = {
        'schema_version': 1,
        'validation': {
            'timestamp_regression_tolerance_sec': 0.15,
        },
        'topics': [
            {
                'alias': alias,
                'topic': topic,
                'type': message_type,
                'required': False,
            }
            for alias, (topic, message_type) in topics.items()
        ],
    }
    joint_entry = next(
        entry
        for entry in resolved['topics']
        if entry['alias'] == 'joint_states'
    )
    joint_entry.update({
        'modes': ['simulation'],
        'required': True,
        'expected_publishers': [
            '/joint_state_broadcaster',
            '/turtlebot3_joint_state',
        ],
        'publishers': [
            '/joint_state_broadcaster',
            '/turtlebot3_joint_state',
        ],
        'timestamp_ordering': 'multi_publisher_within_clock',
    })
    metadata = {
        'mode': 'simulation',
        'algorithm_profile': 'robust_gaussian_v1',
        'recording': {
            'readiness_ever_true': True,
            'pre_ready_nonzero_topics': {},
            'pre_ready_lifecycle_violations': [],
        },
    }
    (tmp_path / 'metadata.yaml').write_text(
        yaml.safe_dump(metadata),
        encoding='utf-8',
    )
    (tmp_path / 'resolved_topics.yaml').write_text(
        yaml.safe_dump(resolved),
        encoding='utf-8',
    )
    (tmp_path / 'resolved_parameters.yaml').write_text(
        yaml.safe_dump({'failures': []}),
        encoding='utf-8',
    )
    (tmp_path / 'notes.md').write_text('# test\n', encoding='utf-8')
    (tmp_path / 'console.log').write_text('', encoding='utf-8')

    readiness = [
        (10, SimpleNamespace(data=True)),
        (100, SimpleNamespace(data=False)),
    ]
    stops = [(100, SimpleNamespace(data=True))]
    zero_command = SimpleNamespace(
        linear=SimpleNamespace(x=0.0, y=0.0, z=0.0),
        angular=SimpleNamespace(x=0.0, y=0.0, z=0.0),
    )
    nonzero_command = SimpleNamespace(
        linear=SimpleNamespace(x=0.1, y=0.0, z=0.0),
        angular=SimpleNamespace(x=0.0, y=0.0, z=0.0),
    )
    commands = [(5, zero_command), (110, zero_command)]
    clocks = [
        (1, SimpleNamespace(clock=_stamp(1.0))),
        (200, SimpleNamespace(clock=_stamp(2.0))),
    ]
    request = SimpleNamespace(timestamp=42.0)
    clean_state = SimpleNamespace(
        STATE_SEARCH=1,
        state=1,
        state_name='SEARCH',
        state_valid=True,
        previous_state=0,
        previous_state_name='UNAVAILABLE',
        previous_state_valid=False,
        active_fill_count=0,
        active_fill_count_valid=True,
        active_escape_fill_id=0,
        active_escape_fill_id_valid=False,
        failsafe=False,
        failsafe_valid=True,
    )

    def validate(
        events,
        requests,
        profile='robust_gaussian_v1',
        states=None,
        readiness_records=None,
        stop_records=None,
        command_records=None,
        joint_records=None,
        singleton_records=None,
        resolved_joint_publishers=None,
    ):
        selected_readiness = (
            readiness
            if readiness_records is None
            else readiness_records
        )
        selected_stops = (
            stops
            if stop_records is None
            else stop_records
        )
        selected_commands = (
            commands
            if command_records is None
            else command_records
        )
        metadata['algorithm_profile'] = profile
        metadata['recording']['readiness_ever_true'] = any(
            bool(message.data)
            for _, message in selected_readiness
        )
        (tmp_path / 'metadata.yaml').write_text(
            yaml.safe_dump(metadata),
            encoding='utf-8',
        )
        joint_entry['publishers'] = (
            [
                '/joint_state_broadcaster',
                '/turtlebot3_joint_state',
            ]
            if resolved_joint_publishers is None
            else resolved_joint_publishers
        )
        (tmp_path / 'resolved_topics.yaml').write_text(
            yaml.safe_dump(resolved),
            encoding='utf-8',
        )
        messages = {
            topics['algorithm_events'][0]: events,
            topics['clock'][0]: clocks,
            topics['recording_ready'][0]: selected_readiness,
            topics['fill_requests'][0]: requests,
            topics['algorithm_state'][0]: (
                states
                if states is not None
                else [(5, clean_state)]
            ),
            topics['stop_requested'][0]: selected_stops,
            topics['command_final'][0]: selected_commands,
            topics['joint_states'][0]: (
                joint_records
                if joint_records is not None
                else [
                    (
                        20,
                        SimpleNamespace(
                            header=SimpleNamespace(stamp=_stamp(1.8)),
                        ),
                    ),
                    (
                        30,
                        SimpleNamespace(
                            header=SimpleNamespace(stamp=_stamp(1.2)),
                        ),
                    ),
                ]
            ),
            topics['typed_singleton'][0]: (
                singleton_records
                if singleton_records is not None
                else [
                    (
                        20,
                        SimpleNamespace(
                            header=SimpleNamespace(stamp=_stamp(1.2)),
                        ),
                    ),
                    (
                        30,
                        SimpleNamespace(
                            header=SimpleNamespace(stamp=_stamp(1.8)),
                        ),
                    ),
                ]
            ),
        }
        bag_types = {
            topic: message_type
            for topic, message_type in topics.values()
        }
        monkeypatch.setattr(
            validator,
            '_read_bag',
            lambda *_args, **_kwargs: (bag_types, messages),
        )
        return validate_run_directory(tmp_path, write_report=False)

    convergence = _event(10, 1.0, 'candidate')
    fill = _event(
        20,
        1.0,
        'fill created',
        source_timestamp=42.0,
        source_timestamp_valid=True,
    )
    report = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
    )
    json.dumps(report, allow_nan=False)
    assert report['checks']['algorithm_event_producer_identified'][
        'passed'
    ]
    assert report['checks']['timestamp_ordering_contract_valid']['passed']
    assert report['checks']['expected_publishers_match']['passed']
    assert report['checks']['multi_publisher_timestamp_scope']['detail'] == [{
        'topic': '/joint_states',
        'expected_publishers': [
            '/joint_state_broadcaster',
            '/turtlebot3_joint_state',
        ],
        'resolved_publishers': [
            '/joint_state_broadcaster',
            '/turtlebot3_joint_state',
        ],
    }]
    assert report['checks']['typed_timestamps_nonregressing']['passed']
    assert report['checks']['typed_timestamps_within_clock']['passed']
    assert report['checks']['algorithm_event_emission_fresh']['passed']
    assert report['checks']['algorithm_event_source_causality']['passed']

    unexpected_owner = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
        resolved_joint_publishers=[
            '/joint_state_broadcaster',
            '/turtlebot3_joint_state',
            '/unexpected_joint_owner',
        ],
    )
    assert not unexpected_owner['checks']['expected_publishers_match'][
        'passed'
    ]

    out_of_clock = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
        joint_records=[
            (
                20,
                SimpleNamespace(
                    header=SimpleNamespace(stamp=_stamp(1.8)),
                ),
            ),
            (
                30,
                SimpleNamespace(
                    header=SimpleNamespace(stamp=_stamp(3.0)),
                ),
            ),
        ],
    )
    assert out_of_clock['checks']['typed_timestamps_nonregressing']['passed']
    assert not out_of_clock['checks']['typed_timestamps_within_clock'][
        'passed'
    ]

    singleton_regression = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
        singleton_records=[
            (
                20,
                SimpleNamespace(
                    header=SimpleNamespace(stamp=_stamp(1.8)),
                ),
            ),
            (
                30,
                SimpleNamespace(
                    header=SimpleNamespace(stamp=_stamp(1.0)),
                ),
            ),
        ],
    )
    assert not singleton_regression['checks'][
        'typed_timestamps_nonregressing'
    ]['passed']

    regressed = validate(
        [
            (20, _event(20, 1.0, 'fill created')),
            (30, _event(22, 0.5, 'fill merged')),
        ],
        [(40, request)],
    )
    assert not regressed['checks']['typed_timestamps_nonregressing'][
        'passed'
    ]

    future = validate(
        [(20, _event(10, 2.0, 'candidate'))],
        [(40, request)],
    )
    assert not future['checks']['algorithm_event_emission_fresh']['passed']

    orphan = validate([(20, fill)], [])
    assert not orphan['checks']['algorithm_event_source_causality'][
        'passed'
    ]

    lifecycle_updates = [
        {'state': 2, 'state_name': 'VERIFY_EXTREMUM'},
        {'failsafe': True},
        {
            'previous_state': 2,
            'previous_state_name': 'VERIFY_EXTREMUM',
            'previous_state_valid': True,
        },
        {'active_fill_count': 1},
        {
            'active_escape_fill_id': 7,
            'active_escape_fill_id_valid': True,
        },
    ]
    for updates in lifecycle_updates:
        violating_state = SimpleNamespace(**vars(clean_state))
        for field, value in updates.items():
            setattr(violating_state, field, value)
        lifecycle = validate(
            [(20, convergence), (30, fill)],
            [(40, request)],
            states=[(5, violating_state), (6, clean_state)],
        )
        assert not lifecycle[
            'checks'
        ]['clean_lifecycle_before_readiness']['passed']

    shutdown_state = SimpleNamespace(**vars(clean_state))
    shutdown_state.state = 8
    shutdown_state.state_name = 'FAILSAFE'
    shutdown_state.previous_state = 1
    shutdown_state.previous_state_name = 'SEARCH'
    shutdown_state.previous_state_valid = True
    shutdown_state.failsafe = True
    post_stop = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
        states=[(60, shutdown_state)],
        readiness_records=[
            (10, SimpleNamespace(data=False)),
            (100, SimpleNamespace(data=False)),
        ],
        stop_records=[(50, SimpleNamespace(data=True))],
        command_records=[
            (60, nonzero_command),
            (110, zero_command),
        ],
    )
    assert post_stop['checks']['clean_lifecycle_before_readiness'][
        'passed'
    ]
    assert post_stop['checks']['no_motion_before_readiness']['passed']

    metadata['recording']['pre_ready_lifecycle_violations'] = [{
        'alias': 'algorithm_state',
        'observed_at_monotonic': 1.0,
        'error': 'algorithm state advanced before readiness',
    }]
    retained_lifecycle = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
    )
    assert not retained_lifecycle['checks'][
        'clean_lifecycle_before_readiness'
    ]['passed']
    metadata['recording']['pre_ready_lifecycle_violations'] = []

    legacy = validate([(20, fill)], [], profile='legacy')
    causality = legacy['checks']['algorithm_event_source_causality']
    assert causality['passed']
    assert causality['detail'] == {'status': 'not_applicable'}
    lifecycle_check = legacy['checks']['clean_lifecycle_before_readiness']
    assert lifecycle_check['passed']
    assert lifecycle_check['detail'] == {'status': 'not_applicable'}

    metadata['recording']['pre_ready_nonzero_topics'] = {
        '/cmd_vel': float('nan'),
    }
    nonfinite = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
    )
    assert not nonfinite['checks']['strict_json_finite']['passed']
    assert nonfinite['checks']['no_motion_before_readiness']['detail'][
        'coordinator_observations'
    ]['/cmd_vel'] is None
    json.dumps(nonfinite, allow_nan=False)

    resolved['validation']['timestamp_regression_tolerance_sec'] = (
        float('nan')
    )
    (tmp_path / 'resolved_topics.yaml').write_text(
        yaml.safe_dump(resolved),
        encoding='utf-8',
    )
    invalid_tolerance = validate(
        [(20, convergence), (30, fill)],
        [(40, request)],
    )
    assert not invalid_tolerance['checks']['timestamp_tolerance_valid'][
        'passed'
    ]
    json.dumps(invalid_tolerance, allow_nan=False)


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
