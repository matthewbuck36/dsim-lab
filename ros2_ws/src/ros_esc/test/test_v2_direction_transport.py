"""Bounded ROS transport through the actual modified-cost and custom-filter owners.

This is synthetic stream/owner validation, not Gazebo, a stationary reference,
or a claim about controller motion. External pytest invocation also uses a
120-second timeout; the DDS graph is isolated on ROS_DOMAIN_ID=122.
"""

import math
from pathlib import Path
import sys
import time

from builtin_interfaces.msg import Time
from geometry_msgs.msg import Transform
from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock

from ros_esc.filter_node.filter_node_script import CustomFilter
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.v2_stream import (
    canonical_json, sensor_geometry_descriptor, set_time, stream_contract_id,
    time_to_ns,
)
from ros_esc_interfaces.msg import (
    AlgorithmState, CostBreakdown, GaussianFill, FillResult, GescDirectionDiagnostics,
    ObjectiveCostSample, SourceSampleProvenance, StampedFloat64MultiArray,
    StampedTransformMultiArray, Timekeeper,
)


from v2_fill_fixture import fixture_activation


NS = 1_000_000_000
ROOT = Path(__file__).parents[1] / "ros_esc"
FILTER = ROOT / "filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
GEOMETRY = ROOT / "sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json"
PREFIX = "/direction_transport"
RUN = "direction-transport-v2"


def test_real_composer_filter_transport_without_stationary_acquisition(monkeypatch):
    monkeypatch.setenv("ROS_DOMAIN_ID", "122")
    config = dict(
        schema_version=1, frame_id="odom", selected_channel=0,
        raw_cost_topic=PREFIX + "/raw", source_cost_topic=PREFIX + "/source",
        augmented_cost_topic=PREFIX + "/augmented", objective_cost_topic=PREFIX + "/objective",
        provenance_topic=PREFIX + "/provenance", pose_topic=PREFIX + "/pose",
        encoder_topic=PREFIX + "/encoder", timekeeper_topic=PREFIX + "/timekeeper",
        **sensor_geometry_descriptor(GEOMETRY),
    )
    serialized = canonical_json(config)
    params = {
        "use_sim_time": "true", "algorithm_profile": "robust_gaussian_v1",
        "continuous_search_mode": "rolling_gesc_v2", "v2_run_id": RUN,
        "v2_stream_config_json": "'" + serialized + "'",
        "source_cost_topic": config["source_cost_topic"],
        "algorithm_state_topic": PREFIX + "/state",
        "cost_breakdown_topic": PREFIX + "/breakdown",
        "algorithm_event_topic": PREFIX + "/events",
        "gaussian_fill_diagnostics_topic": PREFIX + "/fills",
        "v2_fill_result_topic": "/gesc_gaussian/v2/fill_results",
        "v2_objective_cost_topic": config["objective_cost_topic"],
        "input_pde_history_topic": PREFIX + "/unused_pde_history",
    }
    ros_args = ["--ros-args"]
    for key, value in params.items():
        ros_args.extend(("-p", key + ":=" + value))
    rclpy.init(args=ros_args)
    nodes = []
    executor = SingleThreadedExecutor()
    deadline = time.monotonic() + 80.0
    try:
        monkeypatch.setattr(sys, "argv", [
            "modified_cost_2d", config["raw_cost_topic"], PREFIX + "/legacy_fill",
            config["augmented_cost_topic"], "--input_odom_topic", config["pose_topic"],
            "--input_sensor_transform_topic", PREFIX + "/cached_transform",
        ])
        composer = ModifiedCost2D()
        nodes.append(composer)
        monkeypatch.setattr(sys, "argv", [
            "filter_node", config["augmented_cost_topic"], config["encoder_topic"],
            config["timekeeper_topic"], PREFIX + "/output", "--filter_file", str(FILTER),
            "--append_encoder_data", "True", "--algorithm_profile", "robust_gaussian_v1",
            "--enable_observability", "True", "--gesc_diagnostics_topic", PREFIX + "/instant",
            "--continuous-search-mode", "rolling_gesc_v2", "--v2-run-id", RUN,
            "--v2-stream-config-json", serialized, "--algorithm-state-topic", PREFIX + "/state",
            "--v2-direction-diagnostics-topic", PREFIX + "/direction", "--use-sim-time", "true",
        ])
        filtered = CustomFilter()
        nodes.append(filtered)
        driver = Node("direction_transport_driver", use_global_arguments=False)
        nodes.append(driver)
        for node in nodes:
            executor.add_node(node)

        diagnostics, outputs, objectives = [], [], []
        driver.create_subscription(GescDirectionDiagnostics, PREFIX + "/direction", diagnostics.append, 100)
        driver.create_subscription(StampedFloat64MultiArray, PREFIX + "/output", outputs.append, 100)
        driver.create_subscription(ObjectiveCostSample, config["objective_cost_topic"], objectives.append, 100)
        clock = driver.create_publisher(Clock, "/clock", 10)
        timekeeper = driver.create_publisher(Timekeeper, config["timekeeper_topic"], 10)
        state = driver.create_publisher(AlgorithmState, PREFIX + "/state", 10)
        pose = driver.create_publisher(Odometry, config["pose_topic"], 10)
        encoder = driver.create_publisher(StampedFloat64MultiArray, config["encoder_topic"], 10)
        raw = driver.create_publisher(StampedFloat64MultiArray, config["raw_cost_topic"], 10)
        source = driver.create_publisher(CostBreakdown, config["source_cost_topic"], 10)
        provenance = driver.create_publisher(SourceSampleProvenance, config["provenance_topic"], 10)
        fills = driver.create_publisher(FillResult, "/gesc_gaussian/v2/fill_results", 10)
        cached = driver.create_publisher(StampedTransformMultiArray, PREFIX + "/cached_transform", 10)

        def spin_until(predicate, limit=2.0):
            local_deadline = min(deadline, time.monotonic() + limit)
            while not predicate() and time.monotonic() < local_deadline:
                executor.spin_once(timeout_sec=.002)
            assert predicate(), (
                "bounded ROS delivery failed; "
                f"sync={filtered.v2_adapter.sync.reset_sequence}, "
                f"rolling={filtered.v2_adapter.rolling.reset_reason}, "
                f"composer={composer.v2_composer.last_fault_reason}"
            )

        def advance(stamp_ns):
            clock.publish(Clock(clock=set_time(Time(), stamp_ns)))
            spin_until(lambda: all(n.get_clock().now().nanoseconds == stamp_ns
                                   for n in (composer, filtered)))

        def publish_state(stamp_ns, mode=AlgorithmState.STATE_SEARCH):
            msg = AlgorithmState()
            msg.stamp = set_time(Time(), stamp_ns)
            msg.algorithm_profile = "robust_gaussian_v1"
            msg.run_id, msg.run_id_valid = RUN, True
            msg.state, msg.state_valid, msg.weights_valid = mode, True, True
            msg.sensor_weight, msg.gaussian_weight, msg.affine_weight = 1.0, 1.0, 0.0
            state.publish(msg)
            spin_until(lambda: filtered.v2_adapter.state_receipt_ns == stamp_ns
                       and composer.algorithm_state is not None
                       and time_to_ns(composer.algorithm_state.stamp) == stamp_ns)

        def publish_support(stamp_ns, phase):
            heading = .2 * (stamp_ns / NS - 1.0)
            msg = Odometry()
            msg.header.stamp, msg.header.frame_id = set_time(Time(), stamp_ns), "odom"
            msg.pose.pose.orientation.z = math.sin(heading / 2)
            msg.pose.pose.orientation.w = math.cos(heading / 2)
            pose.publish(msg)
            encoder.publish(StampedFloat64MultiArray(
                timestamp=stamp_ns / NS, data=[phase - heading]))
            spin_until(lambda: filtered.v2_adapter.latest_pose is not None
                       and filtered.v2_adapter.latest_pose.stamp_ns == stamp_ns
                       and filtered.v2_adapter.sync._encoders
                       and filtered.v2_adapter.sync._encoders[-1].stamp_ns == stamp_ns)

        gaussian = 2.0 * math.exp(-.5 * .18**2)

        def source_messages(stamp_ns, sequence):
            elapsed = stamp_ns / NS - 1.0
            phase = 2 * math.pi * elapsed / 3
            cost = -gaussian - math.cos(phase)
            raw_msg = StampedFloat64MultiArray(timestamp=stamp_ns / NS, data=[cost])
            breakdown = CostBreakdown()
            breakdown.stamp = set_time(Time(), stamp_ns)
            breakdown.source_timestamp, breakdown.source_timestamp_valid = stamp_ns / NS, True
            breakdown.channel_count, breakdown.raw_cost, breakdown.raw_cost_valid = 1, [cost], True
            prov = SourceSampleProvenance()
            prov.schema_version, prov.run_id, prov.frame_id = 1, RUN, "odom"
            prov.stream_contract_id = stream_contract_id(config, 0)
            prov.source_sequence, prov.channel_count = sequence, 1
            prov.model_input_stamp = set_time(Time(), stamp_ns)
            prov.cost_publication_stamp = set_time(Time(), stamp_ns)
            prov.legacy_cost_source_timestamp_sec = stamp_ns / NS
            prov.sensor_x_m, prov.sensor_y_m = [.18 * math.cos(phase)], [.18 * math.sin(phase)]
            prov.sensor_world_phase_rad = [phase]
            prov.model_input_stamp_valid = prov.sensor_transform_valid = True
            return phase, raw_msg, breakdown, prov

        spin_until(lambda: all(p.get_subscription_count() for p in
                   (clock, timekeeper, state, pose, encoder, raw, source, provenance, fills, cached)), 8.0)
        advance(NS)
        timekeeper.publish(Timekeeper(mode="sim time", start_time=0.0))
        spin_until(lambda: filtered.v2_adapter.identity is not None
                   and composer.v2_composer.origin_ns == 0)
        publish_state(NS)

        fill = GaussianFill()
        fill.fill_id, fill.cluster_id, fill.revision = 1, 1, 1
        fill.active = True
        fill.amplitude = 2.0
        fill.covariance_xx = fill.covariance_yy = 1.0
        fill.sigma_major = fill.sigma_minor = 1.0
        fill.covariance_valid = fill.principal_widths_valid = True
        # Explicit transaction fixture; the actual fill owner is covered separately.
        fills.publish(fixture_activation(fill, config, RUN, 0, NS))
        transform = Transform()
        transform.translation.x = transform.translation.y = 99.0
        transform.rotation.w = 1.0
        cached.publish(StampedTransformMultiArray(timestamp=1.0, transform_array=[transform]))
        spin_until(lambda: 1 in composer.robust_terms and composer.sensor_xy is not None)
        assert composer.sensor_xy.tolist() == [[99.0, 99.0]]

        # Typed source/provenance cannot bypass the selected delayed raw stream.
        phase, first_raw, first_source, first_prov = source_messages(NS, 1)
        publish_support(NS, phase)
        source.publish(first_source)
        provenance.publish(first_prov)
        spin_until(lambda: 1.0 in composer.v2_composer.raw
                   and 1.0 in composer.v2_composer.provenance
                   and 1.0 in filtered.v2_adapter.pending)
        advance(1_100_000_000)
        publish_state(1_100_000_000)
        assert not objectives and not outputs
        raw.publish(first_raw)
        spin_until(lambda: outputs and any(
            d.observation.observation_id and time_to_ns(d.observation.source_stamp) == NS
            and d.output_valid for d in diagnostics))
        first = next(d for d in diagnostics if d.observation.observation_id and d.output_valid)
        assert time_to_ns(first.observation.source_stamp) == NS
        assert time_to_ns(first.observation.receipt_stamp) == 1_100_000_000
        assert time_to_ns(first.output_pose_stamp) == NS  # Actual held pose, not invented current time.
        assert objectives[0].gaussian_cost[0] == pytest.approx(gaussian)
        assert objectives[0].augmented_cost[0] == pytest.approx(-1.0)
        assert list(objectives[0].sensor_x_m) == [.18]

        search_reset = None
        before_verify_cycles = None
        # 300 additional 50ms source observations: 14.95s finite simulated stream.
        # Every callback travels through DDS; actual CustomFilter dynamics run.
        for index in range(300):
            stamp_ns = 1_150_000_000 + index * 50_000_000
            advance(stamp_ns)
            mode = (AlgorithmState.STATE_SEARCH if index < 200
                    else AlgorithmState.STATE_VERIFY_EXTREMUM)
            publish_state(stamp_ns, mode)
            phase, raw_msg, breakdown, prov = source_messages(stamp_ns, index + 2)
            publish_support(stamp_ns, phase)
            source.publish(breakdown)
            provenance.publish(prov)
            raw.publish(raw_msg)
            spin_until(lambda: any(d.output_valid and d.observation.observation_id
                       and time_to_ns(d.observation.source_stamp) == stamp_ns for d in diagnostics[-8:]))
            latest = next(d for d in reversed(diagnostics) if d.observation.observation_id
                          and time_to_ns(d.observation.source_stamp) == stamp_ns)
            if index == 199:
                assert latest.qualified
                search_reset, before_verify_cycles = latest.reset_sequence, latest.completed_revolutions
            if index == 200:
                assert latest.qualified and latest.reset_sequence == search_reset
                assert latest.completed_revolutions >= before_verify_cycles

        # Separate DDS subscriptions need their own delivery acknowledgement;
        # receiving diagnostics does not imply the output callback ran already.
        spin_until(lambda: len(outputs) == 301 and len(objectives) == 301)
        qualified = [d for d in diagnostics if d.qualified and d.output_valid]
        assert qualified
        assert min(d.completed_revolutions for d in qualified) >= 3
        assert all(all(count >= 2 for count in d.sector_counts) for d in qualified)
        assert all(d.blend_weight == .5 for d in qualified)
        assert all(d.observation.demodulation_phase_reconstructed for d in qualified)
        assert any(d.algorithm_state == AlgorithmState.STATE_VERIFY_EXTREMUM for d in qualified)
        assert {o.objective_revision for o in objectives} == {1}
        assert len({o.objective_sha256 for o in objectives}) == 1
        assert len(outputs) == 301
        assert len(objectives) == 301
        assert composer.v2_composer.fault_count == 0
        for obj in objectives:
            assert obj.gaussian_cost[0] == pytest.approx(gaussian, abs=1e-12)
            assert obj.augmented_cost[0] == pytest.approx(obj.raw_cost[0] + gaussian, abs=1e-12)
        for diag in qualified:
            obs = diag.observation
            assert obs.source_stamp == obs.pose_left_stamp == obs.pose_right_stamp
            assert obs.source_stamp == obs.encoder_left_stamp == obs.encoder_right_stamp
            assert obs.sync_error_sec == 0.0
            assert time_to_ns(diag.output_pose_stamp) >= time_to_ns(obs.source_stamp)

        # These owners do not create a stop or PDE-acquisition command. Full
        # controller/supervisor moving verification remains a separate M3 gate.
        for node in (composer, filtered):
            published = {name for name, _ in driver.get_publisher_names_and_types_by_node(
                node.get_name(), node.get_namespace())}
            assert not any("cmd_vel" in name or "stop" in name or "pde" in name for name in published)
        assert not any("pde" in sub.topic_name for sub in filtered.subscriptions)

        # Keep state and current pose fresh while the actual cost source expires.
        # No new valid filter heartbeat may hide that loss from controller safety.
        count = len(outputs)
        end_ns = 1_150_000_000 + 299 * 50_000_000 + 700_000_000
        advance(end_ns)
        publish_state(end_ns, AlgorithmState.STATE_VERIFY_EXTREMUM)
        publish_support(end_ns, phase)
        # A new timer tick must occur after the fresh state/pose callbacks;
        # the tick that advanced the clock may have run before those callbacks.
        advance(end_ns + 50_000_000)
        spin_until(lambda: diagnostics and time_to_ns(diagnostics[-1].stamp) == end_ns + 50_000_000
                   and not diagnostics[-1].output_valid)
        for _ in range(30):
            executor.spin_once(timeout_sec=.002)
        assert len(outputs) == count
        assert diagnostics[-1].fallback_reason == "stale_or_invalid_output_input"
        print(f"transport: {len(outputs)} outputs, {len(objectives)} atomic objectives, "
              f"{len(qualified)} qualified diagnostics, 15.1s source span; raw delay, "
              "exact geometry, SEARCH-to-VERIFY continuity and stale suppression passed")
    finally:
        for node in nodes:
            executor.remove_node(node)
        executor.shutdown(timeout_sec=2.0)
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.shutdown()
