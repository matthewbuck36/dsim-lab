"""One durable fill delivery to the actual composer over DDS, without Gazebo.

The typed commit is supplied test input built with the existing registry and
wire/hash owners. No estimator, field evaluator, supervisor or filter is run;
the acknowledgment asserted here is the actual composer's objective receipt.
"""

import json
import math
import sys
import time

from builtin_interfaces.msg import Time
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock

from ros_esc.gaussian_fill_node.basin_estimator import BasinSample
from ros_esc.gaussian_fill_node.fill_registry import FillRegistry, RegistryConfig
from ros_esc.gaussian_fill_node.v2_fill_runtime import version_message
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256
from ros_esc.v2_stream import canonical_json, set_time, stream_contract_id, time_to_ns
from ros_esc_interfaces.msg import (
    AlgorithmState, CostBreakdown, FillResult, ObjectiveCostSample,
    SourceSampleProvenance, StampedFloat64MultiArray, Timekeeper,
)
from test_v2_fill_transactions import CONFIG, values


NS = 1_000_000_000
ORIGIN = 1000 * NS
BEFORE = ORIGIN + 10 * NS
COMMIT = BEFORE + 100_000_000
RUN = 'q4-committed-fill-transport'
CONTRACT = stream_contract_id(CONFIG, ORIGIN)


def stamp(value):
    return set_time(Time(), value)


def supplied_commit():
    """Produce a valid digest chain with a real registry commit, no fit job."""
    registry = FillRegistry(RegistryConfig())
    samples = tuple(BasinSample(
        1. + index * .1, 0., 0., 0., math.nan, False, -1., math.nan, False, 1,
    ) for index in range(91))
    plan = registry.stage_commit(values(), samples, expected_generation=0, strict=True)
    result = FillResult()
    result.schema_version, result.run_id, result.frame_id = 1, RUN, CONFIG['frame_id']
    result.stream_contract_id = CONTRACT
    result.time_origin, result.stamp = stamp(ORIGIN), stamp(COMMIT)
    result.prepared_at = stamp(BEFORE)
    result.committed_at, result.expires_at = stamp(COMMIT), stamp(COMMIT + 5 * NS)
    result.search_epoch = result.candidate_id = result.objective_revision = 1
    result.command_sequence, result.preparation_id = 2, 1
    result.evidence_sha256, result.prepared_sha256 = 'a' * 64, 'b' * 64
    result.result, result.return_state = FillResult.ACTIVATED, 4
    result.registry_digest_before = fill_registry_digest([])
    registry.commit_staged(plan)
    result.registry_generation = registry.generation
    result.fill = version_message(plan.active, COMMIT, CONFIG['frame_id'])
    result.registry_digest_after = fill_registry_digest([result.fill])
    result.committed_sha256 = result_sha256(result)
    assert registry.generation == 1
    return result


def test_single_leading_commit_waits_for_clock_then_publishes_objective_ack(monkeypatch):
    monkeypatch.setenv('ROS_DOMAIN_ID', '184')
    parameters = dict(
        use_sim_time='true', algorithm_profile='robust_gaussian_v1',
        continuous_search_mode='rolling_gesc_v2', v2_run_id=RUN,
        v2_stream_config_json="'" + canonical_json(CONFIG) + "'",
        source_cost_topic=CONFIG['source_cost_topic'], algorithm_state_topic='/q4/state',
        v2_fill_result_topic='/gesc_gaussian/v2/fill_results',
    )
    args = ['--ros-args']
    for key, value in parameters.items():
        args.extend(['-p', key + ':=' + value])
    rclpy.init(args=args)
    executor, nodes = SingleThreadedExecutor(), []
    deadline = time.monotonic() + 25.
    try:
        monkeypatch.setattr(sys, 'argv', [
            'modified_cost_2d', CONFIG['raw_cost_topic'], '/q4/unused_legacy_fill',
            CONFIG['augmented_cost_topic'], '--input_odom_topic', CONFIG['pose_topic'],
        ])
        cost = ModifiedCost2D()
        driver = Node('q4_committed_fill_transport_driver', use_global_arguments=False)
        nodes.extend((cost, driver))
        for node in nodes:
            executor.add_node(node)
        objectives, deliveries = [], []
        driver.create_subscription(ObjectiveCostSample, CONFIG['objective_cost_topic'], objectives.append, 100)
        driver.create_subscription(FillResult, '/gesc_gaussian/v2/fill_results', deliveries.append, 100)
        publishers = {key: driver.create_publisher(kind, topic, 100) for key, kind, topic in (
            ('clock', Clock, '/clock'), ('origin', Timekeeper, CONFIG['timekeeper_topic']),
            ('state', AlgorithmState, '/q4/state'),
            ('source', CostBreakdown, CONFIG['source_cost_topic']),
            ('raw', StampedFloat64MultiArray, CONFIG['raw_cost_topic']),
            ('provenance', SourceSampleProvenance, CONFIG['provenance_topic']),
            ('result', FillResult, '/gesc_gaussian/v2/fill_results'),
        )}

        def until(predicate, seconds=3.):
            end = min(deadline, time.monotonic() + seconds)
            while not predicate() and time.monotonic() < end:
                executor.spin_once(timeout_sec=.002)
            assert predicate(), dict(
                clock=cost.get_clock().now().nanoseconds,
                generation=cost.v2_fill_activation.generation,
                activation_fault=cost.v2_fill_activation.last_fault,
                composer_fault=cost.v2_composer.last_fault_reason,
                objective_count=len(objectives), result_deliveries=len(deliveries),
            )

        def advance(value):
            publishers['clock'].publish(Clock(clock=stamp(value)))
            until(lambda: cost.get_clock().now().nanoseconds == value)

        def source_sample(value, sequence):
            state = AlgorithmState()
            state.run_id, state.algorithm_profile = RUN, 'robust_gaussian_v1'
            state.state = AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
            state.previous_state = AlgorithmState.STATE_VERIFY_EXTREMUM
            state.state_valid = state.run_id_valid = state.weights_valid = True
            state.previous_state_valid = True
            state.stamp = stamp(value)
            state.sensor_weight = state.gaussian_weight = 1.
            publishers['state'].publish(state)
            until(lambda: cost.algorithm_state is not None
                  and time_to_ns(cost.algorithm_state.stamp) == value)
            relative = (value - ORIGIN) / NS
            raw = StampedFloat64MultiArray(timestamp=relative, data=[-1.])
            source = CostBreakdown()
            source.stamp, source.source_timestamp = stamp(value), relative
            source.source_timestamp_valid = source.raw_cost_valid = True
            source.channel_count, source.raw_cost = 1, [-1.]
            provenance = SourceSampleProvenance()
            provenance.schema_version, provenance.run_id, provenance.frame_id = 2, RUN, 'odom'
            provenance.stream_contract_id = CONTRACT
            provenance.time_origin, provenance.stamp = stamp(ORIGIN), stamp(value)
            provenance.model_input_stamp = provenance.cost_publication_stamp = stamp(value)
            provenance.legacy_cost_source_timestamp_sec = relative
            provenance.source_sequence, provenance.channel_count = sequence, 1
            provenance.sensor_x_m, provenance.sensor_y_m = [.18], [0.]
            provenance.sensor_world_phase_rad = [0.]
            provenance.model_input_stamp_valid = provenance.sensor_transform_valid = True
            publishers['source'].publish(source)
            publishers['provenance'].publish(provenance)
            publishers['raw'].publish(raw)
            until(lambda: any(message.source_sequence == sequence for message in objectives))
            return next(message for message in objectives if message.source_sequence == sequence)

        until(lambda: all(publisher.get_subscription_count() for publisher in publishers.values()), 8.)
        until(lambda: publishers['result'].get_subscription_count() >= 2)
        until(lambda: cost.v2_composer.publisher.get_subscription_count() > 0)
        advance(BEFORE)
        publishers['origin'].publish(Timekeeper(mode='sim time', start_time=ORIGIN / NS))
        until(lambda: cost.v2_composer.origin_ns == ORIGIN)
        empty_digest = fill_registry_digest([])
        before = source_sample(BEFORE, 1)
        assert before.valid and before.registry_digest == empty_digest
        assert list(before.gaussian_cost) == [0.] and not cost.robust_terms

        result = supplied_commit()
        publishers['result'].publish(result)  # Exactly one application delivery.
        until(lambda: len(deliveries) == 1 and cost.v2_fill_activation.pending is not None)
        pending = cost.v2_fill_activation.pending
        assert pending.receipt_ns == BEFORE
        assert time_to_ns(pending.result.committed_at) == COMMIT
        assert cost.v2_fill_activation.generation == 0 and not cost.robust_terms
        assert not cost.v2_fill_activation.last_fault
        advance(BEFORE + 50_000_000)
        waiting = source_sample(BEFORE + 50_000_000, 2)
        assert waiting.valid and waiting.registry_digest == empty_digest
        assert list(waiting.gaussian_cost) == [0.]
        assert cost.v2_fill_activation.pending.receipt_ns == BEFORE
        assert cost.v2_fill_activation.generation == 0 and not cost.robust_terms
        assert all(message.registry_digest == empty_digest for message in objectives)

        # Only /clock advances: no result retry or fresh source input triggers
        # the application. The existing composer's timer must drain it.
        advance(COMMIT)
        until(lambda: cost.v2_fill_activation.generation == 1)
        assert cost.v2_fill_activation.pending is None
        assert len(cost.robust_terms) == len(cost.v2_fill_activation.commits) == 1
        assert fill_registry_digest(cost.v2_fill_activation.active.values()) == result.registry_digest_after
        after = source_sample(COMMIT, 3)
        assert after.valid and after.registry_digest == result.registry_digest_after
        assert time_to_ns(after.composition_stamp) == time_to_ns(after.stamp) == COMMIT
        assert time_to_ns(after.time_origin) == ORIGIN
        assert after.objective_revision == before.objective_revision + 1
        assert after.gaussian_cost[0] > 0.
        assert after.augmented_cost[0] == after.raw_cost[0] + after.gaussian_cost[0]

        advance(COMMIT + 100_000_000)
        later = source_sample(COMMIT + 100_000_000, 4)
        assert later.registry_digest == after.registry_digest
        assert later.objective_revision == after.objective_revision
        assert len(deliveries) == len(cost.v2_fill_activation.commits) == 1
        assert cost.v2_fill_activation.generation == 1
        assert not cost.v2_fill_activation.last_fault
        print('Q4_COMPOSER_ACK ' + json.dumps(dict(
            origin_ns=ORIGIN, first_receipt_ns=BEFORE, committed_at_ns=COMMIT,
            result_deliveries=len(deliveries), objective_count=len(objectives),
            before_registry_digest=before.registry_digest,
            waiting_registry_digest=waiting.registry_digest,
            after_registry_digest=after.registry_digest,
            generation=cost.v2_fill_activation.generation,
            scope='actual composer DDS acknowledgment; supplied registry commit input',
        ), sort_keys=True))
    finally:
        for node in nodes:
            executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.try_shutdown()
