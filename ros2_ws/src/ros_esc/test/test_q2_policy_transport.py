"""Actual filter/controller DDS under a held simulation clock; no Gazebo.

Only source/pose/state inputs are synthetic. Both direction messages, their
policy companion and bounded velocity output come from the existing nodes.
"""
from copy import deepcopy
import math
from pathlib import Path
import sys
import time

from builtin_interfaces.msg import Time
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool

from ros_esc.controller_node.controller_node_script import CustomController
from ros_esc.filter_node.filter_node_script import CustomFilter
from ros_esc.modified_cost_node.v2_objective import digest
from ros_esc.experiment_recording.v2_direction_policy_validation import direction_policy_pair_errors
from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY, POLICY_DIAGNOSTICS_TOPIC,
    policy_config_sha256,
)
from ros_esc.v2_stream import (
    canonical_json, sensor_geometry_descriptor, set_time, stream_contract_id, time_to_ns,
)
from ros_esc_interfaces.msg import (
    AlgorithmState, GescDirectionDiagnostics, GescDirectionPolicyDiagnostics,
    ObjectiveCostSample, SourceSampleProvenance, StampedFloat64MultiArray, Timekeeper,
)

NS = 1_000_000_000
ROOT = Path(__file__).parents[1] / 'ros_esc'
FILTER = ROOT / 'filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json'
GEOMETRY = ROOT / 'sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json'
CONTROLLER = ROOT / 'controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json'


@pytest.mark.parametrize('policy,domain', [(THREE_CYCLE_POLICY, '193'), (MOVING_CYCLE_POLICY, '194')])
def test_actual_policy_companion_and_controller_through_held_clock(monkeypatch, policy, domain):
    monkeypatch.setenv('ROS_DOMAIN_ID', domain)
    prefix, run = '/q2_policy_transport', 'q2-policy-transport-'+policy
    config = dict(schema_version=2, cost_key_basis='model_input_time', frame_id='odom',
                  selected_channel=0, raw_cost_topic=prefix+'/raw', source_cost_topic=prefix+'/source',
                  augmented_cost_topic=prefix+'/augmented', objective_cost_topic=prefix+'/objective',
                  provenance_topic=prefix+'/provenance', pose_topic=prefix+'/pose',
                  encoder_topic=prefix+'/encoder', timekeeper_topic=prefix+'/timekeeper',
                  **sensor_geometry_descriptor(GEOMETRY))
    law = dict(schema_version=1, weights=[1., 1., 0.], bias_all_channels=True,
               fills=[], affine=[], affine_enabled=True, affine_decay_rate=.0000005,
               affine_max_age=30., affine_min_norm=1e-4)
    args = ['filter_node', config['augmented_cost_topic'], config['encoder_topic'],
            config['timekeeper_topic'], prefix+'/output', '--filter_file', str(FILTER),
            '--append_encoder_data', 'True', '--algorithm_profile', 'robust_gaussian_v1',
            '--enable_observability', 'True', '--gesc_diagnostics_topic', prefix+'/instant',
            '--continuous-search-mode', 'rolling_gesc_v2', '--v2-run-id', run,
            '--v2-stream-config-json', canonical_json(config), '--algorithm-state-topic', prefix+'/state',
            '--v2-direction-diagnostics-topic', prefix+'/direction', '--use-sim-time', 'true']
    # Omission must really exercise the inherited default CLI path.
    if policy == MOVING_CYCLE_POLICY:
        args.extend(['--v2-direction-policy', policy])
    monkeypatch.setattr(sys, 'argv', args)
    rclpy.init(args=[])
    executor, nodes = SingleThreadedExecutor(), []
    deadline = time.monotonic()+50.
    try:
        filtered = CustomFilter()
        nodes.append(filtered)
        monkeypatch.setattr(sys, 'argv', [
            'controller_node', prefix+'/output', config['pose_topic'], config['timekeeper_topic'],
            prefix+'/control', prefix+'/cmd_vel', str(CONTROLLER),
            '--algorithm_profile', 'robust_gaussian_v1', '--continuous-search-mode', 'rolling_gesc_v2',
            '--v2-run-id', run, '--algorithm_state_topic', prefix+'/state',
            '--supervisor_command_topic', prefix+'/supervisor', '--startup_timeout_sec', '30',
            '--recording_ready_required', 'True', '--recording_ready_topic', prefix+'/ready',
            '--use-sim-time', 'true',
        ])
        controlled = CustomController()
        driver = Node('q2_policy_transport_driver', use_global_arguments=False)
        nodes.extend((controlled, driver))
        for node in nodes:
            executor.add_node(node)
        adapter = filtered.v2_adapter
        directions, companions, outputs, commands = [], [], [], []
        for kind, topic, sink in (
            (GescDirectionDiagnostics, prefix+'/direction', directions),
            (GescDirectionPolicyDiagnostics, POLICY_DIAGNOSTICS_TOPIC, companions),
            (StampedFloat64MultiArray, prefix+'/output', outputs),
            (Twist, prefix+'/cmd_vel', commands),
        ):
            driver.create_subscription(kind, topic, sink.append, 1000)
        clock = driver.create_publisher(Clock, '/clock', 10)
        origin = driver.create_publisher(Timekeeper, config['timekeeper_topic'], 10)
        state = driver.create_publisher(AlgorithmState, prefix+'/state', 10)
        ready = driver.create_publisher(Bool, prefix+'/ready', 10)
        supervisor = driver.create_publisher(Twist, prefix+'/supervisor', 10)
        pose = driver.create_publisher(Odometry, config['pose_topic'], 100)
        encoder = driver.create_publisher(StampedFloat64MultiArray, config['encoder_topic'], 100)
        publishers = {
            name: driver.create_publisher(kind, config[topic], 100)
            for name, kind, topic in (
                ('raw', StampedFloat64MultiArray, 'raw_cost_topic'),
                ('augmented', StampedFloat64MultiArray, 'augmented_cost_topic'),
                ('provenance', SourceSampleProvenance, 'provenance_topic'),
                ('objective', ObjectiveCostSample, 'objective_cost_topic'),
            )}

        def until(predicate, limit=2.):
            end = min(deadline, time.monotonic()+limit)
            while not predicate() and time.monotonic() < end:
                executor.spin_once(timeout_sec=.001)
            assert predicate(), (policy, adapter.rolling.reset_reason,
                                 tuple(adapter.pending), len(directions), len(companions))

        def authorize(stamp, kind, weight=1.):
            message = AlgorithmState()
            set_time(message.stamp, stamp)
            message.algorithm_profile, message.run_id = 'robust_gaussian_v1', run
            message.run_id_valid = message.state_valid = message.weights_valid = True
            message.failsafe_valid = message.previous_state_valid = True
            message.state = kind
            message.previous_state = (AlgorithmState.STATE_VERIFY_EXTREMUM
                                      if kind == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL else AlgorithmState.STATE_SEARCH)
            message.sensor_weight, message.gaussian_weight = weight, 1.
            state.publish(message)
            ready.publish(Bool(data=True))
            supervisor.publish(Twist())
            until(lambda: adapter.state_receipt_ns == stamp and controlled.recording_ready
                  and controlled.latest_algorithm_state is not None
                  and time_to_ns(controlled.latest_algorithm_state.stamp) == stamp)

        def advance(stamp, kind=AlgorithmState.STATE_SEARCH, weight=1.):
            clock.publish(Clock(clock=set_time(Time(), stamp)))
            until(lambda: filtered.get_clock().now().nanoseconds == stamp
                  and controlled.get_clock().now().nanoseconds == stamp)
            authorize(stamp, kind, weight)

        def support(stamp, phase):
            yaw = .1*(stamp-NS)/NS
            message = Odometry()
            message.header.frame_id = 'odom'
            set_time(message.header.stamp, stamp)
            message.pose.pose.position.x = .002*(stamp-NS)/NS
            message.pose.pose.orientation.z = math.sin(yaw/2)
            message.pose.pose.orientation.w = math.cos(yaw/2)
            pose.publish(message)
            encoder.publish(StampedFloat64MultiArray(timestamp=stamp/NS, data=[phase-yaw]))
            until(lambda: adapter.sync._poses and adapter.sync._encoders
                  and adapter.sync._poses[-1].stamp_ns == stamp
                  and adapter.sync._encoders[-1].stamp_ns == stamp)

        def bundle(stamp, publication, sequence, phase, revision=1):
            elapsed = (stamp-NS)/NS
            source_heading = .35*elapsed if policy == MOVING_CYCLE_POLICY else 0.
            cost = -math.cos(phase-source_heading)
            raw = StampedFloat64MultiArray(timestamp=stamp/NS, data=[cost])
            augmented = StampedFloat64MultiArray(timestamp=stamp/NS, data=[law['weights'][0]*cost])
            provenance = SourceSampleProvenance()
            provenance.schema_version, provenance.run_id, provenance.frame_id = 2, run, 'odom'
            provenance.stream_contract_id = stream_contract_id(config, 0)
            provenance.source_sequence, provenance.channel_count = sequence, 1
            set_time(provenance.stamp, publication)
            set_time(provenance.model_input_stamp, stamp)
            set_time(provenance.cost_publication_stamp, publication)
            provenance.legacy_cost_source_timestamp_sec = stamp/NS
            provenance.sensor_x_m = [.002*elapsed+.18*math.cos(phase)]
            provenance.sensor_y_m = [.18*math.sin(phase)]
            provenance.sensor_world_phase_rad = [phase]
            provenance.model_input_stamp_valid = provenance.sensor_transform_valid = True
            objective = ObjectiveCostSample()
            for name in ('schema_version', 'run_id', 'stream_contract_id', 'frame_id', 'time_origin',
                         'source_sequence', 'model_input_stamp', 'legacy_cost_source_timestamp_sec',
                         'channel_count', 'sensor_x_m', 'sensor_y_m'):
                setattr(objective, name, deepcopy(getattr(provenance, name)))
            set_time(objective.stamp, publication)
            set_time(objective.composition_stamp, publication)
            objective.objective_revision = revision
            objective.objective_config_json, objective.objective_sha256 = canonical_json(law), digest(law)
            objective.registry_digest = digest([])
            objective.sensor_weight, objective.gaussian_weight = law['weights'][0], 1.
            objective.raw_cost, objective.augmented_cost = [cost], list(augmented.data)
            objective.gaussian_cost, objective.affine_cost, objective.valid = [0.], [0.], True
            return dict(raw=raw, augmented=augmented, provenance=provenance, objective=objective)

        def deliver(rows):
            key = rows['raw'].timestamp
            for name in ('objective', 'raw', 'provenance', 'augmented'):
                publishers[name].publish(rows[name])
                until(lambda: name in adapter.pending.get(key, {}) or key in adapter.completed)

        until(lambda: all(p.get_subscription_count() for p in
                          (clock, origin, state, ready, supervisor, pose, encoder, *publishers.values())), 8.)
        advance(NS)
        origin.publish(Timekeeper(mode='sim time', start_time=0.))
        until(lambda: adapter.identity is not None and controlled.v2_origin_ns == 0)
        reset = adapter.rolling.reset_sequence
        state_commands = {}
        for tick in range(150):
            held, covered = NS+tick*100_000_000, NS+(tick+1)*100_000_000
            kind = (AlgorithmState.STATE_SEARCH if tick < 105 else
                    AlgorithmState.STATE_VERIFY_EXTREMUM if tick < 125 else AlgorithmState.STATE_DESIGN_OR_MERGE_FILL)
            before_commands = len(commands)
            for third in (1, 2, 3):
                index = tick*3+third
                stamp = NS+round(index*NS/30)
                phase = 2*math.pi*(stamp-NS)/NS/3
                support(stamp, phase)
                deliver(bundle(stamp, covered, index, phase))
            assert all(round(output.timestamp*NS) <= held for output in outputs)
            advance(covered, kind)
            until(lambda: any(d.observation.source_sequence == index and time_to_ns(d.stamp) == covered
                              for d in directions))
            until(lambda: companions and companions[-1].diagnostic_sequence >= directions[-1].diagnostic_sequence)
            if tick == 0:
                # The first source binds the previously empty stream/objective.
                assert adapter.rolling.reset_reason == 'context_changed'
                reset = adapter.rolling.reset_sequence
            assert adapter.rolling.reset_sequence == reset
            state_commands.setdefault(kind, []).extend(commands[before_commands:])

        paired = {(m.diagnostic_sequence, time_to_ns(m.stamp)): m for m in companions}
        valid = [d for d in directions if d.output_valid and d.observation.source_sequence]
        applied = [d for d in valid if d.blend_weight]
        assert applied, (policy, [(d.completed_revolutions, d.fallback_reason) for d in valid[-5:]])
        expected_weight = .75 if policy == MOVING_CYCLE_POLICY else .5
        assert {d.blend_weight for d in applied} == {expected_weight}
        if policy == MOVING_CYCLE_POLICY:
            assert any(d.qualified and not d.cycles_valid for d in applied)
        for direction in directions:
            companion = paired[(direction.diagnostic_sequence, time_to_ns(direction.stamp))]
            assert companion.direction_policy == policy
            assert companion.policy_config_sha256 == policy_config_sha256(policy)
            assert companion.source_schema_version == direction.schema_version
            assert companion.source_sequence == direction.observation.source_sequence
            assert companion.observation_id == direction.observation.observation_id
            assert time_to_ns(companion.source_stamp) == time_to_ns(direction.observation.source_stamp)
            assert time_to_ns(companion.cost_source_stamp) == time_to_ns(direction.observation.cost_source_stamp)
            assert companion.selected_policy_qualified == direction.qualified
            assert companion.actual_blend_weight == direction.blend_weight
            if policy == MOVING_CYCLE_POLICY:
                assert not direction_policy_pair_errors(direction, companion)
        for direction in applied:
            world = [(1-expected_weight)*a+expected_weight*b
                     for a,b in zip(direction.instant_world, direction.mean_world)]
            yaw = direction.output_yaw_rad
            body = [math.cos(yaw)*world[0]+math.sin(yaw)*world[1],
                    -math.sin(yaw)*world[0]+math.cos(yaw)*world[1]]
            assert direction.output_body == pytest.approx(body, abs=1e-12)
            assert time_to_ns(direction.observation.source_stamp) <= time_to_ns(direction.observation.admission_stamp)
            assert time_to_ns(direction.observation.admission_stamp) <= time_to_ns(direction.stamp)
            assert time_to_ns(direction.output_pose_stamp) <= time_to_ns(direction.stamp)
        for kind in (AlgorithmState.STATE_VERIFY_EXTREMUM, AlgorithmState.STATE_DESIGN_OR_MERGE_FILL):
            assert any(abs(m.linear.x)+abs(m.angular.z)>0 for m in state_commands[kind])
        assert commands
        assert all(abs(m.linear.x) <= .1+1e-12 and abs(m.angular.z) <= .5+1e-12 for m in commands)

        # The real objective change invalidates all three warmup cycles. It does
        # not turn a stale source into a fresh fallback.
        law['weights'][0] = .9
        stamp, publication, index = NS+15_033_333_333, NS+15_100_000_000, 451
        phase = 2*math.pi*(stamp-NS)/NS/3
        support(stamp, phase)
        deliver(bundle(stamp, publication, index, phase, revision=2))
        advance(publication, AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, .9)
        until(lambda: any(d.objective_revision == 2 and d.output_valid for d in directions))
        changed = next(d for d in reversed(directions) if d.objective_revision == 2 and d.output_valid)
        assert changed.reset_sequence > reset and changed.completed_revolutions == 0
        assert not changed.qualified and changed.blend_weight == 0. and changed.fallback_used
        until(lambda: any(c.diagnostic_sequence == changed.diagnostic_sequence for c in companions))
        changed_companion = next(c for c in companions if c.diagnostic_sequence == changed.diagnostic_sequence)
        assert not changed_companion.warmup_valid
        # Drain the last valid output on its own DDS topic before counting;
        # diagnostic arrival does not imply cross-topic callback completion.
        until(lambda: any(round(out.timestamp*NS) == publication for out in outputs))
        count = len(outputs)
        advance(publication+600_000_000, AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, .9)
        until(lambda: directions and time_to_ns(directions[-1].stamp) == publication+600_000_000
              and not directions[-1].output_valid)
        until(lambda: commands and commands[-1].linear.x == commands[-1].angular.z == 0.)
        assert len(outputs) == count
        stale_direction = directions[-1]
        until(lambda: any(c.diagnostic_sequence == stale_direction.diagnostic_sequence for c in companions))
        stale_companion = next(c for c in companions if c.diagnostic_sequence == stale_direction.diagnostic_sequence)
        assert not stale_companion.output_valid and not stale_companion.fallback_used
        assert stale_companion.actual_blend_weight == 0.
        # Existing owner sends the final command as it shuts down.
        before = len(commands)
        executor.remove_node(controlled)
        controlled.destroy_node()
        nodes.remove(controlled)
        until(lambda: len(commands)>before)
        assert commands[-1].linear.x == commands[-1].angular.z == 0.
    finally:
        for node in reversed(nodes):
            executor.remove_node(node)
            node.destroy_node()
        executor.shutdown(timeout_sec=2.)
        rclpy.try_shutdown()
