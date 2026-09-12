"""Actual upstream callbacks under a held ROS clock; no field or motion owner."""

from copy import deepcopy
import math
from pathlib import Path
import sys
from types import SimpleNamespace

from geometry_msgs.msg import Transform
from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.time import Time
from sensor_msgs.msg import JointState

from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.encoder_node.encoder_node_script import EncoderNode
from ros_esc.sensor_pose_node.sensor_pose_node_script import SensorPosition
from ros_esc.v2_stream import canonical_json, sensor_geometry_descriptor, time_to_ns
from ros_esc_interfaces.msg import StampedFloat64MultiArray, StampedTransformMultiArray, Timekeeper


PACKAGE = Path(__file__).parents[1]
GEOMETRY = PACKAGE / 'ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json'
COST = PACKAGE / 'paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json'


class Publisher:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(deepcopy(message))


@pytest.fixture
def upstream(monkeypatch):
    """Construct real owners; only clock progression and publications are captured."""
    rclpy.init(args=[])
    nodes = []

    def create(kind, mode='rolling_gesc_v2', schema=2, origin=0.):
        config = {
            'schema_version': schema, 'selected_channel': 0, 'frame_id': 'odom',
            **{key: '/clock_test/'+name for key, name in (
                ('raw_cost_topic', 'raw'), ('source_cost_topic', 'source'),
                ('augmented_cost_topic', 'augmented'), ('objective_cost_topic', 'objective'),
                ('provenance_topic', 'provenance'), ('pose_topic', 'pose'),
                ('encoder_topic', 'encoder'), ('timekeeper_topic', 'keeper'))},
            **sensor_geometry_descriptor(GEOMETRY),
        }
        if schema == 2:
            config['cost_key_basis'] = 'model_input_time'
        if kind == 'encoder':
            cls = EncoderNode
            argv = ['encoder_node', '/clock_test/joints', '/clock_test/keeper',
                    '/clock_test/encoder', '--joint_names', 'rotating_frame_joint']
        elif kind == 'sensor':
            cls = SensorPosition
            argv = ['sensor_pose_node', '/clock_test/pose', '/clock_test/encoder',
                    '/clock_test/keeper', '/clock_test/transforms', str(GEOMETRY)]
        else:
            cls = CostFunction
            argv = ['cost_function_node', '/clock_test/transforms', '/clock_test/keeper',
                    '/clock_test/raw', str(COST), '--algorithm_profile=robust_gaussian_v1',
                    '--v2-run-id=upstream_callback_test',
                    '--v2-stream-config-json='+canonical_json(config),
                    '--v2-sensor-geometry-config='+str(GEOMETRY)]
        monkeypatch.setattr(sys, 'argv', argv+['--continuous-search-mode='+mode])
        node = cls()
        old_clock = node._clock
        clock = SimpleNamespace(ros_ns=round(origin*1e9), steady_ns=0)
        node._clock = SimpleNamespace(now=lambda: Time(nanoseconds=clock.ros_ns))
        nodes.append((node, old_clock))
        node.timekeeping_callback(Timekeeper(mode='sim time', start_time=origin))
        if kind == 'encoder':
            node.encoder_publisher = Publisher()
        elif kind == 'sensor':
            node.sensor_pose_publisher = Publisher()
            pose = Odometry()
            pose.header.frame_id = 'odom'
            pose.pose.pose.orientation.w = 1.
            node.pose_callback(pose)
        else:
            if hasattr(node, 'v2_admission_timer'):
                node.v2_admission_timer.cancel()
            node.v2_steady_now_ns = lambda: clock.steady_ns
            node.cost_publisher = Publisher()
            node.v2_provenance_publisher = Publisher()
            node.enable_observability = False
            node.evaluations = []
            def evaluate(stamp, matrix):
                node.evaluations.append((stamp, matrix.copy()))
                return float(matrix[0, 3])
            node.cost_function.cost_output = evaluate
            node.noise_obj.add_noise = lambda stamp, values: list(values)
        return node, clock

    yield create
    for node, old_clock in reversed(nodes):
        node._clock = old_clock
        node.destroy_node()
    rclpy.try_shutdown()


def joint(stamp_ns, phase):
    msg = JointState()
    msg.header.stamp = Time(nanoseconds=stamp_ns).to_msg()
    msg.name = ['rotating_frame_joint']
    msg.position = [float(phase)]
    return msg


def transform(key, x=1.):
    t = Transform()
    t.translation.x = float(x)
    t.rotation.w = 1.
    return StampedTransformMultiArray(timestamp=float(key), transform_array=[t])


def test_distinct_joint_acquisitions_survive_all_callbacks_under_one_clock_tick(upstream):
    encoder, ec = upstream('encoder', origin=10.)
    sensor, sc = upstream('sensor', origin=10.)
    source, cc = upstream('cost', origin=10.)
    ec.ros_ns = sc.ros_ns = cc.ros_ns = 10_100_000_000
    for ns, phase in [(10_141_000_000, 0.), (10_175_000_000, .5)]:
        encoder.joint_state_callback(joint(ns, phase))
        reading = encoder.encoder_publisher.messages[-1]
        sensor.encoder_callback(reading)
        t = sensor.sensor_pose_publisher.messages[-1]
        assert t.timestamp == reading.timestamp
        source.transform_callback(t)
        t.transform_array[0].translation.x = 999.  # Queue must own a detached snapshot.
    assert len(source.v2_pending) == 2
    assert source.evaluations == [] and source.cost_publisher.messages == []
    cc.ros_ns = 10_200_000_000
    source.poll_v2_pending()
    assert [m.timestamp for m in source.cost_publisher.messages] == [
        m.timestamp for m in encoder.encoder_publisher.messages]
    assert [time_to_ns(m.model_input_stamp) for m in source.v2_provenance_publisher.messages] == [
        10_141_000_000, 10_175_000_000]
    assert [time_to_ns(m.cost_publication_stamp) for m in source.v2_provenance_publisher.messages] == [
        10_200_000_000, 10_200_000_000]
    assert all(m.schema_version == 2 and m.model_input_stamp_valid
               for m in source.v2_provenance_publisher.messages)
    assert [v[1][0, 3] for v in source.evaluations] == pytest.approx([.18, .18*math.cos(.5)])
    source.poll_v2_pending()
    assert len(source.evaluations) == 2


@pytest.mark.parametrize('owner', ['encoder', 'sensor'])
def test_upstream_retransmission_conflict_regression_and_origin_are_explicit(upstream, owner):
    node, clock = upstream(owner)
    clock.ros_ns = 100_000_000
    def send(ns, value):
        if owner == 'encoder':
            node.joint_state_callback(joint(ns, value))
        else:
            node.encoder_callback(StampedFloat64MultiArray(timestamp=ns*1e-9, data=[float(value)]))
    publisher = node.encoder_publisher if owner == 'encoder' else node.sensor_pose_publisher
    for ns, value in [(141_000_000, .1), (141_000_000, .1), (141_000_000, .2),
                      (141_000_000, .1), (140_000_000, .1), (175_000_000, .2)]:
        send(ns, value)
    assert len(publisher.messages) == 4
    assert [round(m.timestamp*1e9) for m in publisher.messages] == [
        141_000_000, 141_000_000, 140_000_000, 175_000_000]
    if owner == 'encoder':
        assert all(math.isfinite(v) for m in publisher.messages for v in m.data)
    else:
        assert all(math.isfinite(getattr(t.rotation, k)) for m in publisher.messages
                   for t in m.transform_array for k in ('x', 'y', 'z', 'w'))
    send(176_000_000, math.nan)
    send(900_000_000, .3)
    assert len(publisher.messages) == 4
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=1.))
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=0.))
    send(190_000_000, .3)
    assert node.v2_origin_invalid and len(publisher.messages) == 4


@pytest.mark.parametrize('expiry', ['ros', 'steady'])
def test_pending_duplicate_keeps_original_age_and_expires_without_new_data(upstream, expiry):
    node, clock = upstream('cost')
    clock.ros_ns = 100_000_000
    msg = transform(.175)
    node.transform_callback(msg)
    clock.steady_ns = 400_000_000
    node.transform_callback(deepcopy(msg))
    assert next(iter(node.v2_pending.values()))[2:] == (100_000_000, 0)
    if expiry == 'ros':
        clock.ros_ns = 600_000_001
    else:
        clock.steady_ns = 500_000_001
    node.poll_v2_pending()
    assert node.v2_last_fault == 'transform_original_receipt_expired'
    clock.ros_ns = 200_000_000
    node.transform_callback(msg)
    node.poll_v2_pending()
    assert node.evaluations == []


def test_conflicting_pending_key_poisoned_and_regression_does_not_reorder(upstream):
    node, clock = upstream('cost')
    clock.ros_ns = 100_000_000
    node.transform_callback(transform(.14, 1.))
    node.transform_callback(transform(.175, 2.))
    node.transform_callback(transform(.14, 3.))
    assert node.v2_last_fault == 'conflicting_transform_key'
    node.transform_callback(transform(.14, 1.))
    node.transform_callback(transform(.16, 4.))
    assert node.v2_last_fault == 'transform_source_regression'
    invalid = node.v2_provenance_publisher.messages
    assert len(invalid) == 2
    assert [m.legacy_cost_source_timestamp_sec for m in invalid] == [.14, .16]
    assert [time_to_ns(m.model_input_stamp) for m in invalid] == [140_000_000, 160_000_000]
    assert all(not m.model_input_stamp_valid and not m.sensor_transform_valid
               and m.channel_count == 0 and not m.sensor_x_m and not m.sensor_y_m
               and not m.sensor_world_phase_rad and time_to_ns(m.cost_publication_stamp) == 0
               and time_to_ns(m.stamp) == 100_000_000 for m in invalid)
    clock.ros_ns = 200_000_000
    node.poll_v2_pending()
    assert [v[0] for v in node.evaluations] == [.175]
    assert list(node.cost_publisher.messages[0].data) == [2.]
    node.transform_callback(transform(.175, 9.))
    assert len(node.evaluations) == 1
    invalid_published = node.v2_provenance_publisher.messages[-1]
    assert not invalid_published.model_input_stamp_valid
    assert time_to_ns(invalid_published.cost_publication_stamp) == 200_000_000


def test_encoder_conflict_reaches_source_invalidation_without_invalid_encoder_values(upstream):
    encoder, ec = upstream('encoder')
    sensor, sc = upstream('sensor')
    source, cc = upstream('cost')
    ec.ros_ns = sc.ros_ns = cc.ros_ns = 200_000_000
    for phase in [0., .5]:
        encoder.joint_state_callback(joint(175_000_000, phase))
        reading = encoder.encoder_publisher.messages[-1]
        assert math.isfinite(reading.data[0])
        sensor.encoder_callback(reading)
        source.transform_callback(sensor.sensor_pose_publisher.messages[-1])
    valid, invalid = source.v2_provenance_publisher.messages
    assert valid.model_input_stamp_valid and not invalid.model_input_stamp_valid
    assert invalid.source_sequence == valid.source_sequence+1
    assert invalid.run_id == valid.run_id and invalid.stream_contract_id == valid.stream_contract_id
    assert invalid.schema_version == 2 and invalid.channel_count == 0
    assert invalid.legacy_cost_source_timestamp_sec == valid.legacy_cost_source_timestamp_sec
    assert invalid.model_input_stamp == valid.model_input_stamp
    assert invalid.cost_publication_stamp == valid.cost_publication_stamp
    assert len(source.cost_publisher.messages) == 1
    encoder.joint_state_callback(joint(175_000_000, .7))
    source.transform_callback(transform(valid.legacy_cost_source_timestamp_sec, 9.))
    assert len(encoder.encoder_publisher.messages) == 2
    assert len(source.v2_provenance_publisher.messages) == 2


def test_clock_rollback_discards_pending_and_recovers_only_fresh_acquisitions(upstream):
    node, clock = upstream('cost')
    clock.ros_ns = 100_000_000
    node.transform_callback(transform(.175))
    clock.ros_ns = 90_000_000
    node.poll_v2_pending()
    assert not node.v2_pending and node.v2_last_fault == 'clock_rollback'
    clock.ros_ns = 200_000_000
    node.transform_callback(transform(.175))
    node.transform_callback(transform(.19, 2.))
    assert [v[0] for v in node.evaluations] == [.19]


def test_rollback_after_publication_resets_model_order_without_reusing_old_keys(upstream):
    node, clock = upstream('cost')
    clock.ros_ns = 300_000_000
    node.transform_callback(transform(.29))
    clock.ros_ns = 100_000_000
    node.poll_v2_pending()
    clock.ros_ns = 200_000_000
    node.transform_callback(transform(.19))
    assert [m.model_input_stamp_valid for m in node.v2_provenance_publisher.messages] == [True, True]


def test_invalid_model_evaluation_discards_key_and_later_input_can_recover(upstream):
    node, clock = upstream('cost')
    clock.ros_ns = 200_000_000
    def broken(stamp, matrix):
        raise ValueError('analytic fixture failure')
    node.cost_function.cost_output = broken
    node.transform_callback(transform(.14))
    assert node.v2_last_fault.startswith('transform_evaluation_failed:')
    assert not node.cost_publisher.messages
    node.cost_function.cost_output = lambda stamp, matrix: -1.
    node.transform_callback(transform(.14))
    node.transform_callback(transform(.175))
    assert [m.timestamp for m in node.cost_publisher.messages] == [.175]


def test_queue_and_tombstones_are_bounded(upstream):
    node, clock = upstream('cost')
    for i in range(1024):
        node.transform_callback(transform((i+1)*1e-9))
    assert len(node.v2_pending) == 1024
    node.transform_callback(transform(1025e-9))
    assert node.v2_last_fault == 'transform_capacity'
    assert not node.v2_pending and len(node.v2_seen) <= 1024
    assert not node.evaluations


@pytest.mark.parametrize('fault', ['stale', 'clock_rollback'])
def test_lost_admission_during_model_work_cannot_publish(upstream, fault):
    node, clock = upstream('cost')
    clock.ros_ns = 200_000_000
    def evaluate(stamp, matrix):
        if fault == 'stale':
            clock.steady_ns = 500_000_001
        else:
            clock.ros_ns = 100_000_000
        return -1.
    node.cost_function.cost_output = evaluate
    node.transform_callback(transform(.175))
    assert not node.cost_publisher.messages and not node.v2_provenance_publisher.messages
    assert node.v2_last_fault == 'transform_expired_during_evaluation'


@pytest.mark.parametrize('schema', [1, 2])
def test_publication_key_fixture_and_acquisition_key_are_explicitly_distinct(upstream, schema):
    node, clock = upstream('cost', schema=schema)
    clock.ros_ns = 200_000_000
    node.transform_callback(transform(.175))
    assert node.cost_publisher.messages[0].timestamp == (.2 if schema == 1 else .175)
    assert node.v2_provenance_publisher.messages[0].schema_version == schema


def test_default_owners_keep_legacy_held_clock_stamping(upstream):
    encoder, ec = upstream('encoder', mode='stationary_v1')
    sensor, sc = upstream('sensor', mode='stationary_v1')
    source, cc = upstream('cost', mode='stationary_v1')
    ec.ros_ns = sc.ros_ns = cc.ros_ns = 100_000_000
    for ns, phase in [(141_000_000, 0.), (175_000_000, .5)]:
        encoder.joint_state_callback(joint(ns, phase))
        sensor.encoder_callback(encoder.encoder_publisher.messages[-1])
        source.transform_callback(sensor.sensor_pose_publisher.messages[-1])
    assert [m.timestamp for m in encoder.encoder_publisher.messages] == [.1, .1]
    assert [m.timestamp for m in sensor.sensor_pose_publisher.messages] == [.1, .1]
    assert [m.timestamp for m in source.cost_publisher.messages] == [.1, .1]


def test_source_origin_change_and_invalid_geometry_never_evaluate(upstream):
    node, clock = upstream('cost')
    clock.ros_ns = 200_000_000
    msg = transform(.175)
    msg.transform_array[0].rotation.w = 0.
    node.transform_callback(msg)
    node.transform_callback(transform(.18, math.inf))
    node.transform_callback(transform(.9))
    assert not node.evaluations
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=1.))
    node.transform_callback(transform(.19))
    assert node.v2_origin_invalid and not node.evaluations
