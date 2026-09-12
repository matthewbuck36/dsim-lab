"""Finite DDS regression for real source owners under coarse simulation clocks.

Run with ROS_DOMAIN_ID=176 and an external timeout120s. No Gazebo, command
publisher, field evaluator, fabricated downstream source message, or direct
production callback is used. Only the cost and noise functions are analytic.
"""

from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
import math
import os
from pathlib import Path
import sys
import time

from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.serialization import serialize_message
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import JointState

from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.encoder_node.encoder_node_script import EncoderNode
from ros_esc.filter_node.filter_node_script import CustomFilter
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.scenario_runner.simulation_disturbance_node import SimulationDisturbanceNode
from ros_esc.sensor_pose_node.sensor_pose_node_script import SensorPosition
from ros_esc.v2_stream import (
    canonical_json, relative_stamp_ns, sensor_geometry_descriptor, set_time,
    stream_contract_id, time_to_ns,
)
from ros_esc_interfaces.msg import (
    AlgorithmState, CostBreakdown, GaussianFill, FillResult, GescDirectionDiagnostics,
    ObjectiveCostSample, SourceSampleProvenance, StampedFloat64MultiArray,
    StampedTransformMultiArray, Timekeeper,
)


PACKAGE = Path(__file__).parents[1]
ROOT = PACKAGE / "ros_esc"
GEOMETRY = ROOT / "sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json"
FILTER = ROOT / "filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
COST = PACKAGE / "paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json"
PREFIX = "/v2_upstream_transport"
RUN = "upstream-clock-v2"
ORIGIN = 10_000_000_000
NS = 1_000_000_000
TICK = 100_000_000
JOINT = "rotating_frame_joint_1"


def gaussian(x, y):
    return 2.0 * math.exp(-.5 * (x*x + y*y))


class Harness:
    """Drive source inputs and acknowledge DDS delivery with finite wall bounds."""

    def __init__(self, nodes, executor, v2):
        self.nodes, self.executor, self.v2 = nodes, executor, v2
        self.deadline = time.monotonic() + (80.0 if v2 else 15.0)
        self.driver = nodes[-1]
        self.clock_value = self.consumer_clock_value = ORIGIN
        self.messages = {key: [] for key in (
            "encoder", "transforms", "raw", "source", "provenance", "delayed",
            "selected_raw", "selected_pose", "objective", "direction", "output",
        )}
        topics = (
            ("encoder", StampedFloat64MultiArray, "/encoder"),
            ("transforms", StampedTransformMultiArray, "/transforms"),
            ("raw", StampedFloat64MultiArray, "/raw"),
            ("source", CostBreakdown, "/source"),
            ("provenance", SourceSampleProvenance, "/provenance"),
            ("delayed", SourceSampleProvenance, "/provenance_delayed"),
            ("selected_raw", StampedFloat64MultiArray, "/raw_delayed"),
            ("selected_pose", Odometry, "/pose_delayed"),
            ("objective", ObjectiveCostSample, "/objective"),
            ("direction", GescDirectionDiagnostics, "/direction"),
            ("output", StampedFloat64MultiArray, "/output"),
        )
        for key, kind, suffix in topics:
            self.driver.create_subscription(kind, PREFIX+suffix, self.messages[key].append, 100)
        self.clock = self.driver.create_publisher(Clock, "/clock", 10)
        self.consumer_clock = self.driver.create_publisher(Clock, PREFIX+"/consumer_clock", 10)
        self.timekeeper = self.driver.create_publisher(Timekeeper, PREFIX+"/timekeeper", 10)
        self.pose = self.driver.create_publisher(Odometry, PREFIX+"/pose", 10)
        self.joint = self.driver.create_publisher(JointState, PREFIX+"/joints", 10)
        self.state = self.driver.create_publisher(AlgorithmState, PREFIX+"/state", 10)
        self.fills = self.driver.create_publisher(FillResult, "/gesc_gaussian/v2/fill_results", 10)

    def until(self, predicate, description, seconds=2.0):
        end = min(self.deadline, time.monotonic()+seconds)
        while not predicate() and time.monotonic() < end:
            self.executor.spin_once(timeout_sec=.002)
        assert predicate(), description + "; counts=" + repr(
            {key: len(value) for key, value in self.messages.items()})

    def drain(self, seconds=.04):
        end = min(self.deadline, time.monotonic()+seconds)
        while time.monotonic() < end:
            self.executor.spin_once(timeout_sec=.002)
        assert time.monotonic() < self.deadline, "upstream fixture wall deadline expired"

    def advance_source(self, stamp):
        self.clock.publish(Clock(clock=set_time(Time(), stamp)))
        self.until(lambda: all(node.get_clock().now().nanoseconds == stamp
                              for node in self.nodes[:4 if self.v2 else 3]),
                   "source owners did not receive /clock")
        self.clock_value = stamp

    def advance_consumers(self, stamp):
        self.consumer_clock.publish(Clock(clock=set_time(Time(), stamp)))
        self.until(lambda: all(node.get_clock().now().nanoseconds == stamp
                              for node in self.nodes[4:6]),
                   "composer/filter did not receive their clock delivery")
        self.consumer_clock_value = stamp
        self.publish_state(stamp)

    def publish_state(self, stamp):
        msg = AlgorithmState()
        msg.stamp = set_time(Time(), stamp)
        msg.algorithm_profile, msg.run_id, msg.run_id_valid = "robust_gaussian_v1", RUN, True
        msg.state = (AlgorithmState.STATE_SEARCH if stamp-ORIGIN < 10*NS
                     else AlgorithmState.STATE_VERIFY_EXTREMUM)
        msg.state_valid, msg.weights_valid = True, True
        msg.sensor_weight, msg.gaussian_weight, msg.affine_weight = 1., 1., 0.
        self.state.publish(msg)
        self.until(lambda: self.nodes[4].algorithm_state is not None
                   and time_to_ns(self.nodes[4].algorithm_state.stamp) == stamp
                   and self.nodes[5].v2_adapter.state_receipt_ns == stamp,
                   "state did not reach both existing consumers")

    def pose_message(self, stamp):
        elapsed = (stamp-ORIGIN)/NS
        yaw = .2 * elapsed
        msg = Odometry()
        msg.header.stamp = set_time(Time(), stamp)
        msg.header.frame_id, msg.child_frame_id = "odom", "base_footprint"
        msg.pose.pose.position.x, msg.pose.pose.position.y = .01*elapsed, -.005*elapsed
        msg.pose.pose.orientation.z = math.sin(yaw/2)
        msg.pose.pose.orientation.w = math.cos(yaw/2)
        return msg

    def acquisition(self, stamp, frame="joint_source_a"):
        """Odom and joints have actual source headers; all later wires are real."""
        pose = self.pose_message(stamp)
        self.pose.publish(pose)
        # Acknowledge the real sensor-owner cache before triggering its encoder.
        self.until(lambda: self.nodes[1].odom_data is not None
                   and self.nodes[1].odom_data[0] == pose.pose.pose.position.x,
                   "sensor owner did not receive exact fixture odometry")
        elapsed = (stamp-ORIGIN)/NS
        joint = JointState()
        joint.header.stamp = set_time(Time(), stamp)
        joint.header.frame_id = frame
        joint.name = ["unselected_joint", JOINT]
        joint.position = [.123, 2*math.pi*elapsed/3 - .2*elapsed]
        joint.velocity = [0., 2*math.pi/3-.2]
        before = len(self.messages["transforms"])
        self.joint.publish(joint)
        self.until(lambda: len(self.messages["transforms"]) == before+1,
                   "real encoder/sensor owners lost an acquisition")
        return joint


@contextmanager
def upstream_graph(monkeypatch, *, v2):
    if os.environ.get("ROS_DOMAIN_ID") != "176":
        pytest.skip("requires isolated ROS_DOMAIN_ID=176 for synthetic /clock")
    config = dict(
        schema_version=2, cost_key_basis="model_input_time", frame_id="odom", selected_channel=0,
        raw_cost_topic=PREFIX+"/raw_delayed", source_cost_topic=PREFIX+"/source_delayed",
        augmented_cost_topic=PREFIX+"/augmented", objective_cost_topic=PREFIX+"/objective",
        provenance_topic=PREFIX+"/provenance_delayed", pose_topic=PREFIX+"/pose_delayed",
        encoder_topic=PREFIX+"/encoder", timekeeper_topic=PREFIX+"/timekeeper",
        **sensor_geometry_descriptor(GEOMETRY),
    )
    serialized = canonical_json(config)
    ros_args = ["--ros-args"]
    if v2:
        params = {
            "modified_cost_2d": {
                "use_sim_time": "true", "algorithm_profile": "robust_gaussian_v1",
                "continuous_search_mode": "rolling_gesc_v2", "v2_run_id": RUN,
                "v2_stream_config_json": "|-\n  "+serialized,
                "source_cost_topic": config["source_cost_topic"],
                "algorithm_state_topic": PREFIX+"/state", "cost_breakdown_topic": PREFIX+"/breakdown",
                "algorithm_event_topic": PREFIX+"/events", "gaussian_fill_diagnostics_topic": PREFIX+"/fills",
                "v2_fill_result_topic": "/gesc_gaussian/v2/fill_results",
                "v2_objective_cost_topic": config["objective_cost_topic"],
                "input_pde_history_topic": PREFIX+"/unused_pde_history",
            },
            "gesc_gaussian_simulation_disturbance": {
                "use_sim_time": "true", "continuous_search_mode": "rolling_gesc_v2",
                "raw_cost_input_topic": PREFIX+"/raw", "raw_cost_output_topic": config["raw_cost_topic"],
                "source_cost_input_topic": PREFIX+"/source", "source_cost_output_topic": config["source_cost_topic"],
                "provenance_input_topic": PREFIX+"/provenance", "provenance_output_topic": config["provenance_topic"],
                "pose_input_topic": PREFIX+"/pose", "pose_output_topic": config["pose_topic"],
                "sensor_delay_sec": "0.1", "pose_delay_sec": "0.0", "contact_probe_enabled": "false",
            },
        }
        for node, values in params.items():
            for key, value in values.items():
                ros_args.extend(("-p", node+":"+key+":="+value))
        for node in ("modified_cost_2d", "custom_filter"):
            ros_args.extend(("-r", node+":/clock:="+PREFIX+"/consumer_clock"))
    rclpy.init(args=ros_args)
    nodes, evaluations = [], []
    executor = SingleThreadedExecutor()
    try:
        def create(kind, argv):
            monkeypatch.setattr(sys, "argv", argv)
            node = kind()
            nodes.append(node)
            return node

        mode = ["--continuous-search-mode", "rolling_gesc_v2"] if v2 else []
        create(EncoderNode, ["encoder_node", PREFIX+"/joints", PREFIX+"/timekeeper",
                            PREFIX+"/encoder", "--joint_names", JOINT]+mode)
        create(SensorPosition, ["sensor_pose_node", PREFIX+"/pose", PREFIX+"/encoder",
                               PREFIX+"/timekeeper", PREFIX+"/transforms", str(GEOMETRY)]+mode)
        source_args = ["cost_function_node", PREFIX+"/transforms", PREFIX+"/timekeeper",
                       PREFIX+"/raw", str(COST)]
        if v2:
            source_args += mode + ["--algorithm_profile", "robust_gaussian_v1", "--v2-run-id", RUN,
                "--v2-stream-config-json", serialized, "--v2-sensor-geometry-config", str(GEOMETRY),
                "--v2-provenance-topic", PREFIX+"/provenance", "--source_cost_topic", PREFIX+"/source",
                "--algorithm_event_topic", PREFIX+"/source_events"]
        source = create(CostFunction, source_args)
        def analytic_cost(stamp, matrix):
            evaluations.append((stamp, matrix.copy(), source.get_clock().now().nanoseconds))
            return -matrix[0, 0] - gaussian(matrix[0, 3], matrix[1, 3])
        source.cost_function.cost_output = analytic_cost
        source.noise_obj.add_noise = lambda stamp, values: list(values)
        if v2:
            create(SimulationDisturbanceNode, ["simulation_disturbance_node"])
            create(ModifiedCost2D, ["modified_cost_2d", config["raw_cost_topic"], PREFIX+"/legacy_fill",
                config["augmented_cost_topic"], "--input_odom_topic", config["pose_topic"],
                "--input_sensor_transform_topic", PREFIX+"/transforms"])
            create(CustomFilter, ["filter_node", config["augmented_cost_topic"], config["encoder_topic"],
                config["timekeeper_topic"], PREFIX+"/output", "--filter_file", str(FILTER),
                "--append_encoder_data", "True", "--algorithm_profile", "robust_gaussian_v1",
                "--enable_observability", "True", "--gesc_diagnostics_topic", PREFIX+"/instant"]
                +mode+["--v2-run-id", RUN, "--v2-stream-config-json", serialized,
                "--algorithm-state-topic", PREFIX+"/state", "--v2-direction-diagnostics-topic",
                PREFIX+"/direction", "--use-sim-time", "true"])
        nodes.append(Node("upstream_transport_driver", use_global_arguments=False))
        for node in nodes:
            executor.add_node(node)
        harness = Harness(nodes, executor, v2)
        harness.until(lambda: harness.joint.get_subscription_count() >= 1
                      and harness.pose.get_subscription_count() >= (2 if v2 else 1)
                      and harness.timekeeper.get_subscription_count() >= (5 if v2 else 3)
                      and nodes[1].sensor_pose_publisher.get_subscription_count() >= 2
                      and source.cost_publisher.get_subscription_count() >= (2 if v2 else 1)
                      and (not v2 or harness.state.get_subscription_count() >= 2),
                      "DDS graph discovery incomplete", seconds=5.)
        harness.advance_source(ORIGIN)
        if v2:
            harness.advance_consumers(ORIGIN)
        harness.timekeeper.publish(Timekeeper(mode="sim time", start_time=10.))
        harness.until(lambda: all(node.start_time == 10. for node in nodes[:3])
                      and (not v2 or nodes[5].v2_adapter.identity is not None),
                      "Timekeeper did not initialize actual owners")
        if v2:
            fill = GaussianFill()
            fill.stamp = set_time(Time(), ORIGIN)
            fill.fill_id, fill.cluster_id, fill.revision, fill.active = 1, 1, 1, True
            fill.center_x, fill.center_y, fill.amplitude = 0., 0., 2.
            fill.covariance_xx = fill.covariance_yy = 1.
            fill.sigma_major = fill.sigma_minor = 1.
            fill.covariance_valid = fill.principal_widths_valid = True
            # Explicit transaction fixture; the actual fill owner is covered separately.
            from v2_fill_fixture import fixture_activation
            harness.fills.publish(fixture_activation(fill, config, RUN, ORIGIN, ORIGIN))
            harness.until(lambda: 1 in nodes[4].robust_terms, "actual composer did not accept fixture fill")
        yield harness, evaluations, config
    finally:
        for node in nodes:
            executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.try_shutdown()


def test_actual_upstream_held_clock_source_admission_and_three_cycles(monkeypatch):
    with upstream_graph(monkeypatch, v2=True) as (h, evaluations, config):
        messages = h.messages
        expected = []
        # 30 Hz acquisitions precede their held 10 Hz source/publication clock.
        for index in (1, 2, 3):
            stamp = ORIGIN+round(index*NS/30)
            h.acquisition(stamp)
            expected.append(stamp)
        h.drain()
        assert not evaluations and not messages["raw"] and not messages["output"]
        h.advance_source(ORIGIN+TICK)
        h.until(lambda: len(messages["provenance"]) == 3, "clock coverage did not release three source acquisitions")
        assert len(evaluations) == 3 and not messages["delayed"]
        h.advance_source(ORIGIN+2*TICK)
        h.until(lambda: len(messages["delayed"]) == 3
                and len(h.nodes[4].v2_composer.provenance) == 3
                and len(h.nodes[5].v2_adapter.pending) == 3,
                "actual delayed metadata did not reach clock-lagging consumers")
        assert not messages["objective"] and not messages["output"]
        h.advance_consumers(ORIGIN+2*TICK)
        h.until(lambda: len(messages["output"]) == 3, "consumer clock catch-up did not admit all source identities")

        # The initial consumer-clock lag deliberately skips one acquisition batch.
        # Subsequent 100 ms batches contain three distinct 30 Hz acquisitions;
        # acquisition headers and order, never /clock, determine numerical time.
        for batch in range(2, 152):
            before = len(evaluations)
            for index in range(3*batch+1, 3*batch+4):
                stamp = ORIGIN+round(index*NS/30)
                last_joint = h.acquisition(stamp, frame="joint_source_a" if index % 2 else "joint_source_b")
                expected.append(stamp)
            assert len(evaluations) == before, "future source was evaluated before /clock coverage"
            clock_ns = ORIGIN+(batch+1)*TICK
            h.advance_source(clock_ns)
            h.advance_consumers(clock_ns)
            h.until(lambda: len(messages["provenance"]) == len(expected),
                    "held-clock acquisitions collapsed in the real source owner")

        # One more clock tick releases the final batch through the real delay timer.
        end_ns = ORIGIN+153*TICK
        h.advance_source(end_ns)
        h.advance_consumers(end_ns)
        h.until(lambda: len(messages["output"]) == len(expected)
                and len(messages["objective"]) == len(expected)
                and len(messages["selected_raw"]) == len(expected)
                and len(messages["delayed"]) == len(expected)
                and len({time_to_ns(diag.observation.source_stamp)
                         for diag in messages["direction"]
                         if diag.output_valid and diag.observation.observation_id}) == len(expected),
                "full upstream path lost or duplicated an accepted acquisition")

        assert len(evaluations) == len(expected) == 453
        assert [relative_stamp_ns(ORIGIN, message.timestamp) for message in messages["encoder"]] == expected
        assert [message.timestamp for message in messages["encoder"]] == [
            message.timestamp for message in messages["transforms"]]
        keys = [message.timestamp for message in messages["raw"]]
        assert len(set(keys)) == len(expected)
        assert keys == [entry[0] for entry in evaluations]
        assert keys == [message.timestamp for message in messages["encoder"]]
        assert keys == [message.source_timestamp for message in messages["source"]]
        assert keys == [message.legacy_cost_source_timestamp_sec for message in messages["provenance"]]
        assert keys == [message.legacy_cost_source_timestamp_sec for message in messages["objective"]]
        assert [message.source_sequence for message in messages["provenance"]] == list(range(1, 454))
        assert [time_to_ns(message.model_input_stamp) for message in messages["provenance"]] == expected
        assert all(message.schema_version == 2 for message in messages["provenance"])
        assert all(message.schema_version == 2 for message in messages["objective"])
        publication_counts = Counter(time_to_ns(message.cost_publication_stamp) for message in messages["provenance"])
        assert all(count == 3 for count in publication_counts.values())
        assert len(publication_counts) == 151
        assert [serialize_message(message) for message in messages["provenance"]] == [
            serialize_message(message) for message in messages["delayed"]]
        assert [serialize_message(message) for message in messages["raw"]] == [
            serialize_message(message) for message in messages["selected_raw"]]
        for stamp, (key, matrix, publication), provenance, objective in zip(
                expected, evaluations, messages["provenance"], messages["objective"]):
            elapsed = (stamp-ORIGIN)/NS
            phase = 2*math.pi*elapsed/3
            xy = [.01*elapsed+.18*math.cos(phase), -.005*elapsed+.18*math.sin(phase)]
            assert relative_stamp_ns(ORIGIN, key) == stamp <= publication
            assert provenance.stream_contract_id == stream_contract_id(config, ORIGIN)
            assert time_to_ns(provenance.cost_publication_stamp) == publication
            assert provenance.model_input_stamp_valid and provenance.sensor_transform_valid
            assert list(matrix[:2, 3]) == pytest.approx(xy, abs=1e-10)
            assert list(provenance.sensor_x_m) == pytest.approx([xy[0]], abs=1e-10)
            assert list(provenance.sensor_y_m) == pytest.approx([xy[1]], abs=1e-10)
            assert objective.gaussian_cost[0] == pytest.approx(gaussian(*xy), abs=1e-10)
            assert objective.augmented_cost[0] == pytest.approx(-math.cos(phase), abs=1e-10)

        admitted = {time_to_ns(diag.observation.source_stamp): diag for diag in messages["direction"]
                    if diag.output_valid and diag.observation.observation_id}
        assert set(admitted) == set(expected)
        assert any(time_to_ns(diag.observation.oldest_receipt_stamp) < stamp
                   for stamp, diag in admitted.items())
        for stamp, diag in admitted.items():
            obs = diag.observation
            assert diag.schema_version == obs.schema_version == 2
            assert time_to_ns(obs.source_stamp) == time_to_ns(obs.pose_left_stamp) == time_to_ns(obs.pose_right_stamp)
            assert time_to_ns(obs.source_stamp) == time_to_ns(obs.encoder_left_stamp) == time_to_ns(obs.encoder_right_stamp)
            assert stamp <= time_to_ns(obs.admission_stamp) <= time_to_ns(diag.stamp)
            assert time_to_ns(obs.receipt_stamp) <= time_to_ns(obs.admission_stamp)
            assert time_to_ns(obs.oldest_receipt_stamp) <= time_to_ns(obs.receipt_stamp)
            assert time_to_ns(obs.cost_source_stamp) <= time_to_ns(obs.admission_stamp)
            assert time_to_ns(diag.output_pose_stamp) <= time_to_ns(diag.stamp)
            assert obs.sync_error_sec == 0.0 and obs.demodulation_phase_reconstructed
            assert all(math.isfinite(value) for value in diag.output_body)
        qualified = [diag for diag in admitted.values() if diag.qualified]
        assert qualified and all(diag.completed_revolutions >= 3 for diag in qualified)
        assert all(diag.blend_weight == .5 and min(diag.sector_counts) >= 2 for diag in qualified)
        assert any(diag.algorithm_state == AlgorithmState.STATE_VERIFY_EXTREMUM for diag in qualified)
        assert len({objective.objective_sha256 for objective in messages["objective"]}) == 1
        assert h.nodes[4].v2_composer.fault_count == 0

        # A finite contradiction must invalidate earlier confidence downstream;
        # silently dropping it at the encoder would hide the ambiguity.
        before = (len(messages["encoder"]), len(evaluations), len(messages["output"]))
        previous_reset = h.nodes[5].v2_adapter.rolling.reset_sequence
        for _ in range(3):
            h.joint.publish(deepcopy(last_joint))
        h.drain(.04)
        assert (len(messages["encoder"]), len(evaluations), len(messages["output"])) == before
        conflict = deepcopy(last_joint)
        conflict.header.frame_id = "another_writer_is_not_an_authority"
        conflict.position[1] += .4
        h.joint.publish(conflict)
        regressed = deepcopy(last_joint)
        regressed.header.stamp = set_time(Time(), expected[-1]-1_000_000)
        h.joint.publish(regressed)
        h.until(lambda: len(messages["provenance"]) == len(expected)+2
                and len(messages["encoder"]) == before[0]+2
                and len(messages["transforms"]) == len(expected)+2,
                "finite contradictory/regressed inputs did not reach source invalidation")
        invalidations = messages["provenance"][-2:]
        disputed_keys = [keys[-1], (expected[-1]-1_000_000-ORIGIN)*1e-9]
        assert [msg.legacy_cost_source_timestamp_sec for msg in invalidations] == disputed_keys
        assert [msg.source_sequence for msg in invalidations] == [454, 455]
        assert [time_to_ns(msg.cost_publication_stamp) for msg in invalidations] == [expected[-1], 0]
        assert all(msg.schema_version == 2 and not msg.model_input_stamp_valid
                   and not msg.sensor_transform_valid and msg.channel_count == 0
                   and not msg.sensor_x_m and not msg.sensor_y_m and not msg.sensor_world_phase_rad
                   for msg in invalidations)
        assert len(evaluations) == before[1] and len(messages["raw"]) == len(expected)
        assert len(messages["source"]) == len(expected)
        invalidation_delivery_ns = end_ns+TICK
        h.advance_source(invalidation_delivery_ns)
        h.advance_consumers(invalidation_delivery_ns)
        h.until(lambda: len(messages["delayed"]) == len(expected)+2
                and all(h.nodes[5].v2_adapter.completed.get(key, {}).get("poisoned")
                        for key in disputed_keys)
                and all(key in h.nodes[4].v2_composer.seen for key in disputed_keys)
                and messages["direction"][-1].reset_sequence > previous_reset
                and not messages["direction"][-1].output_valid,
                "actual delayed invalidation failed to clear filter confidence")
        assert not messages["direction"][-1].qualified
        assert len(messages["output"]) == before[2]
        assert [serialize_message(msg) for msg in invalidations] == [
            serialize_message(msg) for msg in messages["delayed"][-2:]]
        for replay in (last_joint, conflict, regressed):
            h.joint.publish(deepcopy(replay))
        h.drain(.08)
        assert len(messages["encoder"]) == before[0]+2
        assert len(messages["provenance"]) == len(expected)+2
        assert len(evaluations) == before[1] and len(messages["output"]) == before[2]

        # Fresh evidence can resume bounded instantaneous GESC, without restoring
        # the invalidated three-cycle confidence or resurrecting either old key.
        fresh_ns = invalidation_delivery_ns+TICK
        h.acquisition(fresh_ns)
        h.advance_source(fresh_ns)
        h.advance_consumers(fresh_ns)
        h.until(lambda: len(messages["raw"]) == len(expected)+1,
                "fresh source did not resume after invalidation")
        fresh_delivery_ns = fresh_ns+TICK
        h.advance_source(fresh_delivery_ns)
        h.advance_consumers(fresh_delivery_ns)
        h.until(lambda: len(messages["output"]) == before[2]+1
                and any(diag.output_valid and time_to_ns(diag.observation.source_stamp) == fresh_ns
                        for diag in messages["direction"]),
                "fresh evidence did not resume actual filter output")
        fresh_diag = next(diag for diag in reversed(messages["direction"])
                          if diag.output_valid and time_to_ns(diag.observation.source_stamp) == fresh_ns)
        assert not fresh_diag.qualified and fresh_diag.fallback_used and fresh_diag.blend_weight == 0.
        valid_evaluations, valid_outputs = len(evaluations), len(messages["output"])
        assert valid_evaluations == valid_outputs == len(expected)+1

        # Original receipt lifetime also expires while ROS /clock is held.
        # Repeated source packets cannot turn this into a newly received sample.
        expiring_ns = fresh_delivery_ns+TICK
        expiring_joint = h.acquisition(expiring_ns)
        expiring_key = h.messages["transforms"][-1].timestamp
        h.until(lambda: expiring_key in h.nodes[2].v2_pending,
                "future transform did not enter the actual bounded source queue")
        original_receipt = h.nodes[2].v2_pending[expiring_key][2:]
        h.drain(.30)
        h.joint.publish(deepcopy(expiring_joint))
        h.drain(.04)
        assert h.nodes[2].v2_pending[expiring_key][2:] == original_receipt
        h.drain(.30)
        assert expiring_key not in h.nodes[2].v2_pending
        assert h.nodes[2].v2_last_fault == "transform_original_receipt_expired"
        assert len(evaluations) == valid_evaluations
        h.advance_source(expiring_ns)
        h.advance_consumers(expiring_ns)
        h.drain(.04)
        assert len(evaluations) == valid_evaluations
        assert len(messages["output"]) == valid_outputs

        # Fresh pose/state cannot hide a source stream that has stopped.
        stale_ns = expiring_ns+700_000_000
        h.advance_source(stale_ns)
        h.advance_consumers(stale_ns)
        h.pose.publish(h.pose_message(stale_ns))
        h.advance_source(stale_ns+TICK)
        h.until(lambda: h.nodes[5].v2_adapter.latest_pose is not None
                and h.nodes[5].v2_adapter.latest_pose.stamp_ns == stale_ns,
                "fresh selected pose did not reach the filter before stale-source check")
        h.advance_consumers(stale_ns+TICK)
        h.until(lambda: messages["direction"] and not messages["direction"][-1].output_valid
                and time_to_ns(messages["direction"][-1].stamp) == stale_ns+TICK,
                "stale input did not inhibit filter output")
        h.drain()
        assert len(messages["output"]) == valid_outputs
        for node in h.nodes[:-1]:
            published = {name for name, _ in h.driver.get_publisher_names_and_types_by_node(
                node.get_name(), node.get_namespace())}
            assert not any("cmd_vel" in name or "stop" in name for name in published)
        print(f"upstream DDS: {len(expected)} distinct acquisitions, {len(publication_counts)} publication ticks, "
              f"{len(qualified)} qualified observations; clock-leading input, lagging consumers, "
              "real delay, 2 explicit invalidations, fresh instantaneous recovery, "
              "source expiry and stale inhibition passed")


def test_default_upstream_keeps_legacy_publication_clock_stamps(monkeypatch):
    with upstream_graph(monkeypatch, v2=False) as (h, evaluations, _):
        h.advance_source(ORIGIN+2*TICK)
        for index in (1, 2):
            h.acquisition(ORIGIN+round(index*NS/30))
        h.until(lambda: len(h.messages["raw"]) == 2, "legacy real upstream failed to publish")
        expected_stamp = float((ORIGIN+2*TICK)*1e-9)-10.
        for kind, header in (("encoder", "Encoder Values"),
                             ("transforms", "Sensor Transformation Matrices"), ("raw", "Cost Values")):
            assert [message.timestamp for message in h.messages[kind]] == [expected_stamp]*2
            assert all(message.header == header for message in h.messages[kind])
        assert h.messages["encoder"][0].data != h.messages["encoder"][1].data
        assert len(evaluations) == 2 and not h.messages["provenance"]
        assert h.nodes[2].v2_provenance_publisher is None
