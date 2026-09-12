"""Actual filter DDS recovery with one intentionally missing raw-cost delivery.

Synthetic typed inputs exercise the selected numerical filter and ROS callbacks;
this is not a Gazebo run, a field reference, or a quality qualification.
"""

from copy import deepcopy
import math
from pathlib import Path
import sys
import time

from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock

from ros_esc.filter_node.filter_node_script import CustomFilter
from ros_esc.modified_cost_node.v2_objective import digest
from ros_esc.v2_stream import (
    canonical_json, sensor_geometry_descriptor, set_time, stream_contract_id,
    time_to_ns,
)
from ros_esc_interfaces.msg import (
    AlgorithmState, GescDirectionDiagnostics, ObjectiveCostSample,
    SourceSampleProvenance, StampedFloat64MultiArray, Timekeeper,
)


NS = 1_000_000_000
ROOT = Path(__file__).parents[1] / "ros_esc"
FILTER = ROOT / "filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
GEOMETRY = ROOT / "sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json"
PREFIX, RUN = "/q1_filter_expiry_transport", "q1-filter-expiry-transport"


def test_actual_filter_recovers_after_lost_prefix_with_held_clock(monkeypatch):
    monkeypatch.setenv("ROS_DOMAIN_ID", "186")
    config = dict(
        schema_version=2, cost_key_basis="model_input_time", frame_id="odom",
        selected_channel=0, raw_cost_topic=PREFIX+"/raw",
        source_cost_topic=PREFIX+"/source", augmented_cost_topic=PREFIX+"/augmented",
        objective_cost_topic=PREFIX+"/objective", provenance_topic=PREFIX+"/provenance",
        pose_topic=PREFIX+"/pose", encoder_topic=PREFIX+"/encoder",
        timekeeper_topic=PREFIX+"/timekeeper", **sensor_geometry_descriptor(GEOMETRY),
    )
    law = dict(schema_version=1, weights=[1., 1., 0.], bias_all_channels=True,
               fills=[], affine=[], affine_enabled=True, affine_decay_rate=.0000005,
               affine_max_age=30., affine_min_norm=1e-4)
    monkeypatch.setattr(sys, "argv", [
        "filter_node", config["augmented_cost_topic"], config["encoder_topic"],
        config["timekeeper_topic"], PREFIX+"/output", "--filter_file", str(FILTER),
        "--append_encoder_data", "True", "--algorithm_profile", "robust_gaussian_v1",
        "--enable_observability", "True", "--gesc_diagnostics_topic", PREFIX+"/instant",
        "--continuous-search-mode", "rolling_gesc_v2", "--v2-run-id", RUN,
        "--v2-stream-config-json", canonical_json(config),
        "--algorithm-state-topic", PREFIX+"/state",
        "--v2-direction-diagnostics-topic", PREFIX+"/direction", "--use-sim-time", "true",
    ])
    rclpy.init(args=[])
    executor, nodes = SingleThreadedExecutor(), []
    deadline = time.monotonic()+45.
    try:
        filtered = CustomFilter()
        driver = Node("q1_filter_expiry_transport_driver", use_global_arguments=False)
        nodes.extend((filtered, driver))
        for node in nodes:
            executor.add_node(node)
        adapter = filtered.v2_adapter
        diagnostics, outputs = [], []
        driver.create_subscription(GescDirectionDiagnostics, PREFIX+"/direction", diagnostics.append, 100)
        driver.create_subscription(StampedFloat64MultiArray, PREFIX+"/output", outputs.append, 100)
        clock = driver.create_publisher(Clock, "/clock", 10)
        timekeeper = driver.create_publisher(Timekeeper, config["timekeeper_topic"], 10)
        state = driver.create_publisher(AlgorithmState, PREFIX+"/state", 10)
        pose = driver.create_publisher(Odometry, config["pose_topic"], 100)
        encoder = driver.create_publisher(StampedFloat64MultiArray, config["encoder_topic"], 100)
        publishers = {
            name: driver.create_publisher(kind, config[topic], 100)
            for name, kind, topic in (
                ("raw", StampedFloat64MultiArray, "raw_cost_topic"),
                ("augmented", StampedFloat64MultiArray, "augmented_cost_topic"),
                ("provenance", SourceSampleProvenance, "provenance_topic"),
                ("objective", ObjectiveCostSample, "objective_cost_topic"),
            )
        }

        def spin_until(predicate, limit=2.):
            end = min(deadline, time.monotonic()+limit)
            while not predicate() and time.monotonic() < end:
                executor.spin_once(timeout_sec=.002)
            assert predicate(), (adapter.sync.reset_sequence, adapter.rolling.reset_reason,
                                 tuple(adapter.pending), tuple(adapter.sync._pending))

        def advance(stamp):
            clock.publish(Clock(clock=set_time(Time(), stamp)))
            spin_until(lambda: filtered.get_clock().now().nanoseconds == stamp)
            msg = AlgorithmState()
            set_time(msg.stamp, stamp)
            msg.algorithm_profile, msg.run_id = "robust_gaussian_v1", RUN
            msg.run_id_valid = msg.state_valid = msg.weights_valid = True
            msg.state = AlgorithmState.STATE_SEARCH
            msg.sensor_weight = msg.gaussian_weight = 1.
            state.publish(msg)
            spin_until(lambda: adapter.state_receipt_ns == stamp)

        def support(stamp, phase):
            msg = Odometry()
            msg.header.frame_id, msg.pose.pose.orientation.w = "odom", 1.
            set_time(msg.header.stamp, stamp)
            pose.publish(msg)
            encoder.publish(StampedFloat64MultiArray(timestamp=stamp/NS, data=[phase]))
            spin_until(lambda: adapter.sync._poses and adapter.sync._encoders
                       and adapter.sync._poses[-1].stamp_ns == stamp
                       and adapter.sync._encoders[-1].stamp_ns == stamp)

        def bundle(stamp, publication, sequence, phase):
            cost = -math.cos(phase)
            raw = StampedFloat64MultiArray(timestamp=stamp/NS, data=[cost])
            prov = SourceSampleProvenance()
            prov.schema_version, prov.run_id, prov.frame_id = 2, RUN, "odom"
            prov.stream_contract_id = stream_contract_id(config, 0)
            prov.source_sequence, prov.channel_count = sequence, 1
            set_time(prov.stamp, publication)
            set_time(prov.model_input_stamp, stamp)
            set_time(prov.cost_publication_stamp, publication)
            prov.legacy_cost_source_timestamp_sec = stamp/NS
            prov.sensor_x_m = [.18*math.cos(phase)]
            prov.sensor_y_m = [.18*math.sin(phase)]
            prov.sensor_world_phase_rad = [phase]
            prov.model_input_stamp_valid = prov.sensor_transform_valid = True
            obj = ObjectiveCostSample()
            for name in ("schema_version", "run_id", "stream_contract_id", "frame_id", "time_origin",
                         "source_sequence", "model_input_stamp", "legacy_cost_source_timestamp_sec",
                         "channel_count", "sensor_x_m", "sensor_y_m"):
                setattr(obj, name, deepcopy(getattr(prov, name)))
            set_time(obj.stamp, publication)
            set_time(obj.composition_stamp, publication)
            obj.objective_revision = 1
            obj.objective_config_json, obj.objective_sha256 = canonical_json(law), digest(law)
            obj.registry_digest = digest([])
            obj.sensor_weight = obj.gaussian_weight = 1.
            obj.raw_cost, obj.augmented_cost = [cost], [cost]
            obj.gaussian_cost, obj.affine_cost, obj.valid = [0.], [0.], True
            return dict(raw=raw, augmented=deepcopy(raw), provenance=prov, objective=obj)

        def deliver(rows, order):
            key = rows["raw"].timestamp
            for name in order:
                publishers[name].publish(rows[name])
                spin_until(lambda: (name in adapter.pending.get(key, {})
                                    or key in adapter.completed))

        spin_until(lambda: all(p.get_subscription_count() for p in
                               (clock, timekeeper, state, pose, encoder, *publishers.values())), 8.)
        advance(NS)
        timekeeper.publish(Timekeeper(mode="sim time", start_time=0.))
        spin_until(lambda: adapter.identity is not None)
        initial_reset = adapter.rolling.reset_sequence
        missing = None
        preserved_support = None
        fault_reset = None
        recovered = []
        for tick in range(36):
            held = NS+tick*100_000_000
            covered = held+100_000_000
            for third in (1, 2, 3):
                index = tick*3+third
                stamp = NS+round(index*NS/30)
                phase = 2*math.pi*(stamp-NS)/NS/3
                support(stamp, phase)
                rows = bundle(stamp, covered, index, phase)
                if index == 1:
                    missing = rows
                    deliver(rows, ("provenance", "augmented", "objective"))
                else:
                    order = (("objective", "raw", "provenance", "augmented") if index % 2
                             else ("augmented", "provenance", "raw", "objective"))
                    deliver(rows, order)
            # Three distinct 30 Hz acquisition headers lead the held 10 Hz clock;
            # no source whose clock has not caught up may publish an output.
            assert all(round(out.timestamp*NS) <= held for out in outputs)
            if tick == 5:
                preserved_support = (adapter.sync._poses[-1], adapter.sync._encoders[-1])
            advance(covered)
            spin_until(lambda: any(time_to_ns(d.stamp) == covered for d in diagnostics))
            if tick == 5:
                spin_until(lambda: adapter.sync.is_retired(missing["raw"].timestamp))
                fault_reset = adapter.rolling.reset_sequence
                assert fault_reset > initial_reset
                assert adapter.rolling.reset_reason in ("pending_receipt_expired", "pending_expired")
                assert preserved_support[0] in adapter.sync._poses
                assert preserved_support[1] in adapter.sync._encoders
                assert preserved_support[0].receipt_ns == held
                assert not adapter.pending and not adapter.sync._pending
            if tick >= 6:
                spin_until(lambda: any(d.output_valid and time_to_ns(d.stamp) == covered
                                      for d in diagnostics))
                current = [d for d in diagnostics if d.output_valid and time_to_ns(d.stamp) == covered]
                recovered.extend(current)
                assert adapter.rolling.reset_sequence == fault_reset
                if tick == 6:
                    first = current[0]
                    assert first.completed_revolutions == 0 and not first.qualified
                    assert first.blend_weight == 0. and first.fallback_used
                    assert first.rolling_sample_count <= 1
            if tick in (10, 20, 30):
                # Valid but long-expired fragments cannot resurrect a join. DDS
                # delivery is drained before checking both pending owners.
                for name in ("objective", "provenance", "raw", "augmented"):
                    publishers[name].publish(missing[name])
                for _ in range(24):
                    executor.spin_once(timeout_sec=.001)
                assert missing["raw"].timestamp not in adapter.pending
                assert missing["raw"].timestamp not in adapter.sync._pending
                assert adapter.rolling.reset_sequence == fault_reset

        assert recovered and len(outputs) >= 90
        assert max(time_to_ns(d.observation.source_stamp) for d in recovered) >= 4_500_000_000
        for diagnostic in recovered:
            obs = diagnostic.observation
            published = time_to_ns(diagnostic.stamp)
            assert 0 <= published-time_to_ns(obs.source_stamp) <= 500_000_000
            assert 0 <= published-time_to_ns(obs.oldest_receipt_stamp) <= 500_000_000
            assert time_to_ns(obs.source_stamp) <= time_to_ns(obs.admission_stamp) <= published
            assert all(math.isfinite(v) for v in diagnostic.output_body)
    finally:
        executor.shutdown()
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.shutdown()
