"""Focused tests for Phase 08 simulation validation support."""

from pathlib import Path

from gazebo_msgs.msg import ContactsState, ContactState

from ros_esc.cost_function_node.cost_function_objects.noise_objects import (
    Gaussian,
)
from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import (
    _contact_metric,
    _observed_delay_metric,
)
from ros_esc.scenario_runner.run_scenario import build_launch_command
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite
from ros_esc.scenario_runner.simulation_disturbance_node import DelayQueue
from ros_esc.scenario_runner.simulation_disturbance_node import (
    SimulationDisturbanceNode,
)

from ros_esc_interfaces.msg import StampedFloat64MultiArray
from rosgraph_msgs.msg import Clock

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[2]
SMOKE = PACKAGE_ROOT / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
SUPPORT = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml'
)


def _record(topic, stamp_ns, message, source_timestamp=None):
    return BagRecord(
        topic=topic,
        type_name='test',
        bag_timestamp_ns=stamp_ns,
        ros_timestamp_ns=None,
        source_timestamp_sec=source_timestamp,
        source_timestamp_valid=source_timestamp is not None,
        message=message,
        in_readiness_interval=True,
        t_motion_sec=stamp_ns / 1_000_000_000,
    )


def test_delay_queue_releases_in_order_at_fixed_ros_time():
    """Release all due messages without changing their identity or order."""
    queue = DelayQueue(0.1)
    first = object()
    second = object()
    queue.append(first, 1_000_000_000)
    queue.append(second, 1_010_000_000)

    assert queue.pop_ready(1_099_999_999) == []
    assert queue.pop_ready(1_100_000_000) == [first]
    assert queue.pop_ready(1_200_000_000) == [second]
    assert len(queue) == 0


def test_seeded_gaussian_uses_repeatable_numpy_generator():
    """Use the configured seed for the NumPy sampler that produces noise."""
    values = [0.0, 0.5, -0.5, 1.0]
    first = Gaussian({'std_dev': 0.1, 'seed_num': 42})
    second = Gaussian({'std_dev': 0.1, 'seed_num': 42})

    assert first.add_noise(0.0, values) == second.add_noise(0.0, values)


def test_schema_v1_case_key_and_support_catalog_remain_compatible():
    """Preserve the Phase 06 key while enabling only schema-v2 probes."""
    smoke_runs, smoke_unsupported = expand_suite(load_suite(SMOKE))
    support_runs, support_unsupported = expand_suite(load_suite(SUPPORT))

    assert smoke_runs[0]['case_key'].startswith('f562307ac8')
    assert smoke_unsupported == []
    assert len(support_runs) == 5
    assert support_unsupported == []


def test_validation_launch_routes_only_delayed_algorithm_consumers():
    """Keep canonical publishers while routing configured delayed inputs."""
    runs, _ = expand_suite(load_suite(SUPPORT))
    sensor = next(run for run in runs if run['case_id'] == 'sensor_delay')
    command = build_launch_command(sensor)

    assert 'simulation_disturbance_enabled:=True' in command
    assert 'simulation_sensor_delay_sec:=0.1' in command
    assert (
        'algorithm_raw_cost_topic:='
        '/gesc_gaussian/simulation/raw_cost_delayed'
    ) in command
    assert (
        'algorithm_source_cost_topic:='
        '/gesc_gaussian/simulation/source_cost_delayed'
    ) in command
    assert 'algorithm_pose_topic:=/odom' in command
    assert any(item.startswith('gazebo_world:=') for item in command)
    assert 'simulation_contacts_enabled:=True' in command

    negative = next(
        run for run in runs if run['case_id'] == 'contact_negative'
    )
    negative_command = build_launch_command(negative)
    assert 'simulation_contacts_enabled:=True' in negative_command
    assert 'simulation_validation_support_enabled:=False' in negative_command
    assert 'simulation_contact_probe_enabled:=False' in negative_command

    positive = next(
        run for run in runs if run['case_id'] == 'contact_positive'
    )
    positive_command = build_launch_command(positive)
    assert 'simulation_validation_support_enabled:=True' in positive_command
    assert 'simulation_contact_probe_enabled:=True' in positive_command


def test_contact_probe_is_a_static_physical_collision():
    """Spawn a Gazebo collision object rather than synthetic contact data."""
    sdf = SimulationDisturbanceNode.contact_probe_sdf()

    assert '<static>true</static>' in sdf
    assert '<collision name="collision">' in sdf
    assert 'ContactsState' not in sdf


def test_contact_sensors_reference_gazebo_lumped_collision_names():
    """Monitor the collision names produced by URDF-to-SDF fixed-joint lumping."""
    urdf = (
        REPOSITORY_ROOT
        / 'ros2_ws/src/turtlebot3_rotating_sensor/urdf/'
        'turtlebot3_rotating_sensor.urdf'
    ).read_text(encoding='utf-8')

    assert (
        '<collision>'
        'base_footprint_fixed_joint_lump__base_body_collision_collision'
        '</collision>'
    ) in urdf
    assert (
        '<collision>'
        'rotating_frame_link_fixed_joint_lump__'
        'rotating_frame_collision_collision'
        '</collision>'
    ) in urdf


def test_delay_metric_pairs_retained_original_stamps(tmp_path):
    """Measure bag-receipt delay by pairing unchanged source timestamps."""
    original = StampedFloat64MultiArray(timestamp=2.0, data=[1.0])
    delayed = StampedFloat64MultiArray(timestamp=2.0, data=[1.0])
    first_clock = Clock()
    first_clock.clock.sec = 5
    second_clock = Clock()
    second_clock.clock.sec = 5
    second_clock.clock.nanosec = 100_000_000
    data = BagData(
        run_directory=tmp_path,
        topic_types={},
        topics_by_alias={
            'raw': {'topic': '/raw'},
            'delayed': {'topic': '/delayed'},
            'clock': {'topic': '/clock'},
        },
        records_by_topic={
            '/raw': [_record('/raw', 1_000_000_000, original, 2.0)],
            '/delayed': [
                _record('/delayed', 1_100_000_000, delayed, 2.0)
            ],
            '/clock': [
                _record('/clock', 1_000_000_000, first_clock),
                _record('/clock', 1_100_000_000, second_clock),
            ],
        },
        readiness_start_ns=0,
        readiness_end_ns=2_000_000_000,
    )

    result = _observed_delay_metric(data, 'raw', 'delayed', 0.1)

    assert result['status'] == 'valid'
    assert result['value'] == 0.1


def test_collision_metric_distinguishes_empty_and_wall_contact(tmp_path):
    """Treat valid empty messages as no collision and retain wall contact."""
    (tmp_path / 'resolved_scenario.yaml').write_text(
        yaml.safe_dump({
            'validation': {'contacts_enabled': True},
        }),
        encoding='utf-8',
    )
    empty = ContactsState()
    wall = ContactsState()
    state = ContactState()
    state.collision1_name = 'turtlebot3::base_link::base_body_collision'
    state.collision2_name = 'validation_wall_east::wall::collision'
    wall.states = [state]
    ground = ContactsState()
    ground_state = ContactState()
    ground_state.collision1_name = (
        'turtlebot3::base_link::base_body_collision'
    )
    ground_state.collision2_name = 'ground_plane::link::collision'
    ground.states = [ground_state]
    data = BagData(
        run_directory=tmp_path,
        topic_types={},
        topics_by_alias={
            'simulation_contacts': {'topic': '/contacts'},
        },
        records_by_topic={
            '/contacts': [],
        },
        readiness_start_ns=0,
        readiness_end_ns=4,
    )

    assert _contact_metric(data)['status'] == 'invalid'
    data.records_by_topic['/contacts'].append(
        _record('/contacts', 1, empty)
    )
    assert _contact_metric(data)['value'] is False
    data.records_by_topic['/contacts'].append(
        _record('/contacts', 2, ground)
    )
    assert _contact_metric(data)['value'] is False
    data.records_by_topic['/contacts'].append(
        _record('/contacts', 3, wall)
    )
    assert _contact_metric(data)['value'] is True
