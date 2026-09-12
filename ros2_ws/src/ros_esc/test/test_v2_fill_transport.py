"""Actual Gaussian worker and atomic cost owner over DDS; synthetic frozen input."""
from copy import deepcopy
import math
import sys
import time

import pytest
import rclpy
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from ros_esc_interfaces.msg import AlgorithmState, FillCommand, FillResult, GaussianFill, SearchEpochContext, Timekeeper
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill as GaussianOwner
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.v2_lifecycle import fill_registry_digest, snapshot_sha256
from ros_esc.v2_stream import canonical_json, set_time
from test_v2_fill_transactions import CONFIG, command, envelope


def test_real_prepare_activate_and_cancel_over_dds(monkeypatch):
    monkeypatch.setenv('ROS_DOMAIN_ID', '177')
    params = dict(use_sim_time='true', algorithm_profile='robust_gaussian_v1',
                  continuous_search_mode='rolling_gesc_v2', v2_run_id='test-m3',
                  v2_stream_config_json="'"+canonical_json(CONFIG)+"'",
                  pose_topic=CONFIG['pose_topic'], algorithm_state_topic='/test/state',
                  v2_fill_command_topic='/gesc_gaussian/v2/fill_commands', v2_fill_result_topic='/gesc_gaussian/v2/fill_results',
                  v2_search_epoch_topic='/gesc_gaussian/v2/search_epoch', source_cost_topic=CONFIG['source_cost_topic'],
                  gaussian_fill_diagnostics_topic='/test/fills', algorithm_event_topic='/test/events')
    args = ['--ros-args']
    for key,value in params.items(): args += ['-p', key+':='+value]
    rclpy.init(args=args)
    executor = SingleThreadedExecutor()
    nodes=[]
    try:
        gaussian = GaussianOwner(); nodes.append(gaussian)
        monkeypatch.setattr(sys, 'argv', ['modified_cost_2d',CONFIG['raw_cost_topic'],'/test/legacy_fill',
            CONFIG['augmented_cost_topic'],'--input_odom_topic',CONFIG['pose_topic']])
        cost = ModifiedCost2D(); nodes.append(cost)
        driver = Node('fill_transport_driver',use_global_arguments=False); nodes.append(driver)
        for node in nodes: executor.add_node(node)
        results, mirrors = [],[]
        driver.create_subscription(FillResult,'/gesc_gaussian/v2/fill_results',results.append,100)
        driver.create_subscription(GaussianFill,'/test/fills',mirrors.append,100)
        publishers = {key:driver.create_publisher(kind,topic,100) for key,kind,topic in (
            ('clock',Clock,'/clock'),('timekeeper',Timekeeper,CONFIG['timekeeper_topic']),
            ('state',AlgorithmState,'/test/state'),('context',SearchEpochContext,'/gesc_gaussian/v2/search_epoch'),
            ('pose',Odometry,CONFIG['pose_topic']),('command',FillCommand,'/gesc_gaussian/v2/fill_commands'))}
        def until(predicate, seconds=3.):
            end=time.monotonic()+seconds
            while not predicate() and time.monotonic()<end: executor.spin_once(timeout_sec=.002)
            assert predicate(), [(r.result,r.reason) for r in results]
        until(lambda: all(p.get_subscription_count() for p in publishers.values()),8.)
        ns=10_100_000_000
        publishers['clock'].publish(Clock(clock=set_time(Time(),ns)))
        until(lambda: gaussian.get_clock().now().nanoseconds==cost.get_clock().now().nanoseconds==ns)
        publishers['timekeeper'].publish(Timekeeper(mode='sim time',start_time=0.))
        until(lambda: gaussian.v2_fill.origin_ns==cost.v2_composer.origin_ns==0)
        context=envelope(SearchEpochContext()); context.valid=True; context.context_sequence=1; context.algorithm_state=3
        set_time(context.stamp,ns); publishers['context'].publish(context)
        state=AlgorithmState(); state.run_id='test-m3'; state.algorithm_profile='robust_gaussian_v1'
        state.state,state.previous_state=3,2
        state.state_valid=state.weights_valid=state.run_id_valid=state.previous_state_valid=True
        state.sensor_weight=state.gaussian_weight=1.; set_time(state.stamp,ns)
        publishers['state'].publish(state)
        pose=Odometry(); pose.header.frame_id='odom'; pose.pose.pose.orientation.w=1.
        set_time(pose.header.stamp,ns); publishers['pose'].publish(pose)
        until(lambda: gaussian.v2_fill.context is not None and gaussian.v2_fill.state is not None
              and len(gaussian.v2_fill.poses)>0)
        cmd=command()
        # Analytic shallow bowl exercises the real unchanged estimator/designer.
        for i,obs in enumerate(cmd.snapshot.observations):
            obs.base_x_m=.1*math.cos(i*.12); obs.base_y_m=.07*math.sin(i*.12)
            obs.raw_cost=-1.+.01*math.cos(i*.12)**2+.005*math.sin(i*.12)**2
        cmd.snapshot.evidence_sha256=snapshot_sha256(cmd.snapshot)
        cmd.evidence_sha256=cmd.snapshot.evidence_sha256
        publishers['command'].publish(cmd)
        until(lambda: any(r.result==FillResult.PREPARED for r in results))
        assert gaussian.fill_registry.generation==0 and not mirrors and not cost.robust_terms
        prepared=next(r for r in results if r.result==FillResult.PREPARED)
        act=deepcopy(cmd); act.operation=FillCommand.ACTIVATE; act.command_sequence=2
        act.prepared_sha256=prepared.prepared_sha256
        publishers['command'].publish(act)
        until(lambda: cost.v2_fill_activation.generation==1 and len(mirrors)==1)
        accepted=next(r for r in results if r.result==FillResult.ACTIVATED)
        assert accepted.registry_digest_after==fill_registry_digest(cost.v2_fill_activation.active.values())
        assert len(cost.robust_terms)==1 and gaussian.fill_registry.generation==1
        cancel=deepcopy(act); cancel.command_sequence=3; cancel.operation=FillCommand.CANCEL
        publishers['command'].publish(cancel)
        until(lambda: any(r.result==FillResult.ALREADY_ACTIVATED for r in results))
        assert gaussian.fill_registry.generation==cost.v2_fill_activation.generation==1
        assert len(mirrors)==1
    finally:
        for node in nodes: executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in reversed(nodes): node.destroy_node()
        rclpy.try_shutdown()
