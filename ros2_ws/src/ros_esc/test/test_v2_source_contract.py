"""Opt-in source/relay/runner identity and exact provenance regressions."""

import copy
import json
import math
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from geometry_msgs.msg import Transform
import numpy as np
import pytest
from rclpy.serialization import deserialize_message, serialize_message
import yaml

from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.scenario_runner.run_scenario import (
    build_launch_command, build_metadata, build_v2_stream_config,
)
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite
from ros_esc.scenario_runner.simulation_disturbance_node import (
    DelayQueue, SimulationDisturbanceNode,
)
from ros_esc.v2_stream import canonical_json, stream_contract_id, time_to_ns
from ros_esc_interfaces.msg import SourceSampleProvenance, Timekeeper
from test_v2_stream import resolve_frontend_command

PACKAGE = Path(__file__).parents[1]
ROOT = PACKAGE.parents[2]


class Publisher:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


def resolved(*, sensor_delay=0., pose_delay=0.):
    runs, _ = expand_suite(load_suite(PACKAGE / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'))
    result = copy.deepcopy(next(run for run in runs if run['profile'] == 'robust_gaussian_v1'))
    result['algorithm']['launch_overrides']['continuous_search_mode'] = 'rolling_gesc_v2'
    result['disturbances']['sensor_delay_sec'] = sensor_delay
    result['disturbances']['pose_delay_sec'] = pose_delay
    return result


def source_stub():
    config = build_v2_stream_config(resolved())
    # Preserve these original publication-key/schema1 fixtures explicitly.
    config['schema_version'] = 1
    config.pop('cost_key_basis', None)
    source = SimpleNamespace(
        v2_enabled=True, v2_config=config, v2_run_id='run_test',
        v2_origin_ns=None, v2_origin_invalid=False, v2_stream_id=None,
        v2_sequence=1, v2_last_model_ns=None,
        v2_provenance_publisher=Publisher(), start_time=None,
        timekeeping_mode=None,
    )
    source.publish_v2_provenance = lambda *args: CostFunction.publish_v2_provenance(source, *args)
    source._v2_acquisition_keys = lambda: CostFunction._v2_acquisition_keys(source)
    origin = Timekeeper(mode='sim time', start_time=10.)
    CostFunction.timekeeping_callback(source, origin)
    return source


def test_source_records_evaluated_model_time_geometry_and_distinct_publication():
    source = source_stub()
    transform = Transform()
    transform.translation.x, transform.translation.y = 2., -3.
    transform.rotation.z, transform.rotation.w = math.sin(.4), math.cos(.4)
    source.transforms = [transform]
    source.transforms_tstamp = .25
    source._clock = SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=10_270_000_000))
    source.cost_publisher = Publisher()
    evaluated = []
    def cost_output(stamp, matrix):
        evaluated.append((stamp, matrix.copy()))
        return -1.25
    source.cost_function = SimpleNamespace(cost_output=cost_output)
    source.noise_obj = SimpleNamespace(add_noise=lambda stamp, values: list(values))
    source.enable_observability = False
    CostFunction.publish_cost_value(source)
    raw = source.cost_publisher.messages[0]
    provenance = source.v2_provenance_publisher.messages[0]
    assert evaluated[0][0] == .25
    assert list(raw.data) == [-1.25]
    assert provenance.legacy_cost_source_timestamp_sec == raw.timestamp
    assert time_to_ns(provenance.model_input_stamp) == 10_250_000_000
    assert time_to_ns(provenance.cost_publication_stamp) == 10_270_000_000
    assert time_to_ns(provenance.stamp) == 10_270_000_000
    assert list(provenance.sensor_x_m) == [evaluated[0][1][0, 3]]
    assert list(provenance.sensor_y_m) == [evaluated[0][1][1, 3]]
    assert list(provenance.sensor_world_phase_rad) == pytest.approx([.8])
    assert provenance.model_input_stamp_valid and provenance.sensor_transform_valid
    assert provenance.stream_contract_id == stream_contract_id(source.v2_config, 10_000_000_000)
    restored = deserialize_message(serialize_message(provenance), SourceSampleProvenance)
    assert restored == provenance


def test_origin_conflict_is_latched_and_cannot_publish_rebound_identity():
    source = source_stub()
    CostFunction.timekeeping_callback(source, Timekeeper(mode='sim time', start_time=11.))
    assert source.v2_origin_invalid
    CostFunction.timekeeping_callback(source, Timekeeper(mode='sim time', start_time=10.))
    source.transforms_tstamp = .5
    source.publish_v2_provenance([np.eye(4)], .6, 10_600_000_000)
    assert source.v2_provenance_publisher.messages == []


@pytest.mark.parametrize('stamp', [float('nan'), -.5, .9])
def test_invalid_future_or_regressed_model_stamp_remains_explicit(stamp):
    source = source_stub()
    source.transforms_tstamp = .4
    source.publish_v2_provenance([np.eye(4)], .5, 10_500_000_000)
    source.transforms_tstamp = stamp
    source.publish_v2_provenance([np.eye(4)], .6, 10_600_000_000)
    assert not source.v2_provenance_publisher.messages[-1].model_input_stamp_valid


def test_nonfinite_transform_is_not_marked_valid():
    source = source_stub()
    source.transforms_tstamp = .4
    matrix = np.eye(4)
    matrix[0, 3] = float('nan')
    source.publish_v2_provenance([matrix], .5, 10_500_000_000)
    message = source.v2_provenance_publisher.messages[-1]
    assert not message.sensor_transform_valid
    assert list(message.sensor_x_m) == []


def test_provenance_relay_applies_same_delay_without_restamping_or_payload_change():
    raw, provenance = object(), SourceSampleProvenance(source_sequence=8)
    node = SimpleNamespace(
        raw_queue=DelayQueue(.1), source_queue=DelayQueue(.1),
        pose_queue=DelayQueue(.2), provenance_queue=DelayQueue(.1),
        raw_publisher=Publisher(), source_publisher=Publisher(),
        pose_publisher=Publisher(), provenance_publisher=Publisher(),
        get_clock=lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=1_110_000_000)),
        _spawn_contact_probe=lambda: None,
    )
    node.raw_queue.append(raw, 1_000_000_000)
    node.provenance_queue.append(provenance, 1_020_000_000)
    SimulationDisturbanceNode._release_ready(node)
    assert node.raw_publisher.messages == [raw]
    assert node.provenance_publisher.messages == []
    node.get_clock = lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=1_120_000_000))
    SimulationDisturbanceNode._release_ready(node)
    assert node.provenance_publisher.messages == [provenance]
    assert node.provenance_publisher.messages[0] is provenance


@pytest.mark.parametrize('sensor,pose', [(0., 0.), (.1, 0.), (0., .1), (.1, .1)])
def test_runner_shares_explicit_identity_and_selected_delayed_bindings(sensor, pose):
    run = resolved(sensor_delay=sensor, pose_delay=pose)
    with pytest.raises(ValueError, match='run_id'):
        build_launch_command(run)
    command = build_launch_command(run, run_id='run_test')
    args = dict(arg.split(':=', 1) for arg in command[4:])
    config = json.loads(args['v2_stream_config_json'])
    assert args['v2_run_id'] == 'run_test'
    assert config['raw_cost_topic'] == args['algorithm_raw_cost_topic']
    assert config['source_cost_topic'] == args['algorithm_source_cost_topic']
    assert config['pose_topic'] == args['algorithm_pose_topic']
    assert config['provenance_topic'] == args['v2_algorithm_provenance_topic']
    assert ('delayed' in config['provenance_topic']) == bool(sensor)
    metadata = build_metadata(run, 'test', 'v2', '', run_id='run_test')
    assert metadata['scenario_runner']['v2_identity']['stream_config'] == config
    assert metadata['scenario_runner']['v2_identity']['run_id'] == 'run_test'


def test_launch_cli_and_ros_parameter_json_survive_humble_frontend_and_yaml_roundtrip():
    tree = ET.parse(ROOT / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml')
    config = canonical_json(build_v2_stream_config(resolved()))
    values = {entry.attrib['name']: entry.attrib.get('default', '')
              for entry in tree.findall('arg')}
    values.update(v2_stream_config_json=config, v2_run_id='run_test')
    tested = []
    for element in tree.findall('executable'):
        command = element.get('cmd', '')
        if 'v2-stream-config-json' not in command and 'v2_stream_config_json' not in command:
            continue
        argv = resolve_frontend_command(command, values)
        for arg in argv:
            if arg.startswith('v2_stream_config_json:='):
                assert yaml.safe_load(arg.split(':=', 1)[1]) == config
            if arg.startswith('--v2-stream-config-json='):
                assert arg.split('=', 1)[1] == config
        tested.append(argv[3])
    assert sorted(tested) == ['convergence_detector_node', 'cost_function_node', 'cost_function_node', 'filter_node', 'filter_node', 'gaussian_fill_node', 'modified_cost_node', 'pde_history_node', 'supervisor_node']


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
def test_supervisor_uses_shared_identity_only_in_selected_mode(monkeypatch, mode):
    import rclpy
    from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
    # Identity setup does not need state/command publication or executor motion.
    monkeypatch.setattr(SupervisorNode, '_publish_state_and_command', lambda *_: None)
    config = canonical_json(build_v2_stream_config(resolved()))
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true',
                    '-p', 'continuous_search_mode:='+mode,
                    '-p', 'v2_run_id:=shared_identity_test',
                    '-p', 'v2_candidate_radius_m:=0.5',
                    '-p', 'v2_candidate_epsilon_m:=0.1',
                    '-p', 'extremum_classification_mode:=counted_candidates',
                    '-p', 'known_source_count:=2', '-p', 'max_fill_clusters:=1',
                    '-p', 'v2_stream_config_json:=|-\n  '+config])
    node = None
    try:
        node = SupervisorNode()
        if mode == 'rolling_gesc_v2':
            assert node.run_id == 'shared_identity_test'
        else:
            assert node.run_id != 'shared_identity_test' and len(node.run_id) == 32
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()
