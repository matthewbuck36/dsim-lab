"""Finite ROS transport of evaluated source provenance through its delay owner.

Run on an isolated ROS_DOMAIN_ID: this fixture owns its domain's /clock and
publishes no commands, starts no launch graph, and replaces field evaluation
with an analytic test function.
"""

import os
from pathlib import Path
import sys
import time

from geometry_msgs.msg import Transform
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rosgraph_msgs.msg import Clock

from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.scenario_runner.simulation_disturbance_node import SimulationDisturbanceNode
from ros_esc.v2_stream import (
    canonical_json, sensor_geometry_descriptor, stream_contract_id, time_to_ns,
)
from ros_esc_interfaces.msg import SourceSampleProvenance, StampedTransformMultiArray, Timekeeper

PACKAGE = Path(__file__).parents[1]
GEOMETRY = PACKAGE / 'ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json'
COST = PACKAGE / 'paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json'


def test_source_to_provenance_delay_preserves_actual_evaluation_identity(monkeypatch):
    if os.environ.get('ROS_DOMAIN_ID') != '173':
        pytest.skip('requires isolated ROS_DOMAIN_ID=173 for its synthetic /clock')
    prefix = '/v2_source_transport'
    config = {
        'schema_version': 1, 'selected_channel': 0, 'frame_id': 'odom',
        'raw_cost_topic': prefix+'/raw_delayed', 'source_cost_topic': prefix+'/source_delayed',
        'augmented_cost_topic': prefix+'/augmented', 'objective_cost_topic': prefix+'/objective',
        'provenance_topic': prefix+'/provenance_delayed', 'pose_topic': prefix+'/pose',
        'encoder_topic': prefix+'/encoder', 'timekeeper_topic': prefix+'/timekeeper',
        **sensor_geometry_descriptor(GEOMETRY),
    }
    config_json = canonical_json(config)
    argv = ['cost_function_node', prefix+'/transforms', prefix+'/timekeeper', prefix+'/raw', str(COST),
            '--algorithm_profile=robust_gaussian_v1', '--continuous-search-mode=rolling_gesc_v2',
            '--v2-run-id=transport_test', '--v2-stream-config-json='+config_json,
            '--v2-sensor-geometry-config='+str(GEOMETRY), '--v2-provenance-topic='+prefix+'/provenance',
            '--source_cost_topic='+prefix+'/source']
    monkeypatch.setattr(sys, 'argv', argv)
    ros_args = ['--ros-args']
    for name, value in {
        'continuous_search_mode': 'rolling_gesc_v2',
        'raw_cost_input_topic': prefix+'/raw', 'raw_cost_output_topic': prefix+'/raw_delayed',
        'source_cost_input_topic': prefix+'/source', 'source_cost_output_topic': prefix+'/source_delayed',
        'pose_input_topic': prefix+'/pose', 'pose_output_topic': prefix+'/pose_delayed',
        'provenance_input_topic': prefix+'/provenance', 'provenance_output_topic': prefix+'/provenance_delayed',
        'sensor_delay_sec': '0.1',
    }.items():
        ros_args.extend(['-p', 'gesc_gaussian_simulation_disturbance:'+name+':='+value])
    # Exercise the actual rcl YAML scalar parser used by executable launch args.
    ros_args.extend(['-p', 'v2_stream_config_json:=|-\n  '+config_json])
    rclpy.init(args=ros_args)
    executor = SingleThreadedExecutor()
    nodes = []
    try:
        harness = Node('v2_source_transport_harness')
        harness.declare_parameter('v2_stream_config_json', '')
        assert harness.get_parameter('v2_stream_config_json').value == config_json
        source = CostFunction()
        source.cost_function.cost_output = lambda stamp, matrix: -.5-matrix[0,3]*.1
        source.noise_obj.add_noise = lambda stamp, values: list(values)
        relay = SimulationDisturbanceNode()
        relay.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        nodes = [harness, source, relay]
        for node in nodes:
            executor.add_node(node)
        upstream, delayed = [], []
        harness.create_subscription(SourceSampleProvenance, prefix+'/provenance', upstream.append, 100)
        harness.create_subscription(SourceSampleProvenance, prefix+'/provenance_delayed', delayed.append, 100)
        clock = harness.create_publisher(Clock, '/clock', 10)
        timekeeper = harness.create_publisher(Timekeeper, prefix+'/timekeeper', 10)
        transforms = harness.create_publisher(StampedTransformMultiArray, prefix+'/transforms', 10)
        end = time.monotonic()+20.
        def spin_until(predicate):
            while time.monotonic() < end and not predicate():
                executor.spin_once(timeout_sec=.02)
            assert predicate(), 'bounded source/relay transport condition timed out'
        spin_until(lambda: transforms.get_subscription_count() >= 1
                   and timekeeper.get_subscription_count() >= 1
                   and source.v2_provenance_publisher.get_subscription_count() >= 2
                   and relay.provenance_publisher.get_subscription_count() >= 1)
        clock_message = Clock()
        clock_message.clock.sec, clock_message.clock.nanosec = 10, 200_000_000
        clock.publish(clock_message)
        timekeeper.publish(Timekeeper(mode='sim time', start_time=10.))
        spin_until(lambda: source.v2_origin_ns == 10_000_000_000
                   and source.get_clock().now().nanoseconds == 10_200_000_000
                   and relay.get_clock().now().nanoseconds == 10_200_000_000)
        transform = Transform()
        transform.translation.x, transform.translation.y, transform.rotation.w = 2., -1., 1.
        transforms.publish(StampedTransformMultiArray(timestamp=.1, transform_array=[transform]))
        spin_until(lambda: len(upstream) == 1 and len(relay.provenance_queue) == 1)
        assert delayed == []
        clock_message.clock.nanosec = 299_000_000
        clock.publish(clock_message)
        spin_until(lambda: relay.get_clock().now().nanoseconds == 10_299_000_000)
        relay._release_ready()
        assert delayed == []
        clock_message.clock.nanosec = 310_000_000
        clock.publish(clock_message)
        spin_until(lambda: len(delayed) == 1)
        assert delayed[0] == upstream[0]
        result = delayed[0]
        assert result.source_sequence == 1
        assert result.run_id == 'transport_test'
        assert result.stream_contract_id == stream_contract_id(config, 10_000_000_000)
        assert time_to_ns(result.model_input_stamp) == 10_100_000_000
        assert time_to_ns(result.cost_publication_stamp) == 10_200_000_000
        assert result.sensor_transform_valid and result.model_input_stamp_valid
        assert list(result.sensor_x_m) == [2.] and list(result.sensor_y_m) == [-1.]
    finally:
        for node in nodes:
            executor.remove_node(node)
            node.destroy_node()
        executor.shutdown(timeout_sec=2.)
        rclpy.try_shutdown()
