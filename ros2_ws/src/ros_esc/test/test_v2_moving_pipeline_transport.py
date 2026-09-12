"""Actual moving supervisor -> worker -> activation -> composer DDS pipeline.

Pose/source/detector/M2 observations are declared synthetic inputs. Direction
registry acknowledgements only echo actual received composer objective receipts.
No controller, Gazebo, hardware, cmd_vel subscriber, or fabricated fill result.
"""
from copy import deepcopy
import math
import sys
import threading
import time

import pytest
import rclpy
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import (AlgorithmEvent, AlgorithmState, CandidateSnapshot, CostBreakdown,
    DetectorConfirmation, FillCommand, FillResult, GescDirectionDiagnostics,
    ObjectiveCostSample, SearchEpochContext, SourceSampleProvenance,
    StampedFloat64MultiArray, SynchronizedObservation, Timekeeper)
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill as GaussianOwner
from ros_esc.gaussian_fill_node import v2_fill_runtime
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor
from ros_esc.v2_lifecycle import fill_registry_digest, snapshot_sha256
from ros_esc.v2_stream import SUPPORTED_GEOMETRY, canonical_json, set_time, stream_contract_id, time_to_ns

NS=1_000_000_000
PREFIX='/moving_pipeline'
RUN='m3-moving-pipeline'
CONFIG=dict(schema_version=2,cost_key_basis='model_input_time',frame_id='odom',selected_channel=0,
    sensor_geometry=SUPPORTED_GEOMETRY,sensor_geometry_config_sha256='a'*64,
    **{key:PREFIX+'/'+key for key in ('raw_cost_topic','source_cost_topic','augmented_cost_topic',
        'objective_cost_topic','provenance_topic','pose_topic','encoder_topic','timekeeper_topic')})


def stamp(ns): return set_time(Time(),int(ns))


@pytest.mark.parametrize('depart_during_worker',[False,True])
def test_actual_moving_candidate_pipeline_and_pending_worker_cancel(
        monkeypatch, depart_during_worker, metric_mode='centroid_windows_v2', ros_domain_id=185,
        escape_case=None):
    monkeypatch.setenv('ROS_DOMAIN_ID',str(ros_domain_id))
    release=threading.Event();started=threading.Event();computed=threading.Event()
    producer_stop=threading.Event();producer_resume=threading.Event();depart=threading.Event()
    producer=None;producer_errors=[];source_lock=threading.Lock()
    hold_objective=escape_case is not None and escape_case.get('held_ack')=='objective'
    release_objective=threading.Event()
    if hold_objective:
        original_objective=MovingSupervisor.objective
        def gated_objective(owner,message):
            # Withhold delivery of genuine composer acknowledgements only;
            # never manufacture registry identity or callback freshness.
            if message.registry_digest!=fill_registry_digest([]) and not release_objective.is_set():
                return
            return original_objective(owner,message)
        monkeypatch.setattr(MovingSupervisor,'objective',gated_objective)
    original_compute=v2_fill_runtime.compute_fill_proposal
    def bounded_actual_worker(inp):
        started.set()
        if not release.wait(5.): raise RuntimeError('test worker release deadline')
        try: return original_compute(inp)
        finally: computed.set()
    monkeypatch.setattr(v2_fill_runtime,'compute_fill_proposal',bounded_actual_worker)
    params=dict(use_sim_time='true',algorithm_profile='robust_gaussian_v1',
        convergence_metric_mode=metric_mode,
        continuous_search_mode='rolling_gesc_v2',v2_run_id=RUN,
        v2_stream_config_json="'"+canonical_json(CONFIG)+"'",pose_topic=CONFIG['pose_topic'],
        source_cost_topic=CONFIG['source_cost_topic'],algorithm_state_topic=PREFIX+'/state',
        algorithm_event_topic=PREFIX+'/events',gaussian_fill_diagnostics_topic=PREFIX+'/fills',
        cost_breakdown_topic=PREFIX+'/breakdown',input_pde_history_topic=PREFIX+'/unused_pde',
        v2_objective_cost_topic=CONFIG['objective_cost_topic'],
        v2_direction_diagnostics_topic=PREFIX+'/direction',
        extremum_classification_mode='counted_candidates',known_source_count='2',max_fill_clusters='1',
        v2_candidate_radius_m='0.5',v2_candidate_epsilon_m='0.1',
        recording_ready_required='true',recording_ready_topic=PREFIX+'/ready',
        supervisor_command_topic=PREFIX+'/supervisor_command',recenter_after_escape='false')
    if escape_case is not None:
        assert not depart_during_worker
        params.update(operating_bounds_enabled='false',
            v2_candidate_radius_m='0.75',v2_candidate_epsilon_m='0.15',
            open_field_escape_assist_enabled='true',
            open_field_escape_approach_continuity_enabled='true',
            open_field_escape_active_fill_transit_enabled='true',
            open_field_escape_supervisor_owned_assist_enabled='true',
            open_field_escape_interior_anchor_fallback_enabled=str(escape_case['interior']).lower(),
            open_field_escape_interior_anchor_min_displacement_m='0.50',
            sigma_floor_m='0.5',sigma_ceiling_m='1.25',exit_sigma='2.7',
            covariance_scale='2.5',amplitude_max='6.25',
            candidate_informed_fill_enabled='true',candidate_informed_fill_amplitude_scale='1.25',
            supervisor_stop_topic=PREFIX+'/stop')
    args=['--ros-args']
    for key,value in params.items():args+=['-p',key+':='+value]
    rclpy.init(args=args)
    # Production launches these owners independently. Concurrent node callbacks
    # preserve their existing mutually exclusive groups while allowing source
    # delivery during another node's immutable snapshot serialization.
    executor=MultiThreadedExecutor(num_threads=4);nodes=[]
    deadline=time.monotonic()+50.
    try:
        supervisor=SupervisorNode();nodes.append(supervisor)
        gaussian=GaussianOwner();nodes.append(gaussian)
        monkeypatch.setattr(sys,'argv',['modified_cost_2d',CONFIG['raw_cost_topic'],PREFIX+'/legacy_fill',
            CONFIG['augmented_cost_topic'],'--input_odom_topic',CONFIG['pose_topic']])
        composer=ModifiedCost2D();nodes.append(composer)
        driver=Node('moving_pipeline_driver',use_global_arguments=False,
            parameter_overrides=[Parameter('use_sim_time',value=True)]);nodes.append(driver)
        for node in nodes:executor.add_node(node)
        states=[];contexts=[];results=[];commands=[];snapshots=[];objectives=[];events=[]
        pending_ack=[];allow_ack=[False];sample_geometry={};now_ns=[0];sequence=[0]
        pub={key:driver.create_publisher(kind,topic,100) for key,kind,topic in (
            ('clock',Clock,'/clock'),('timekeeper',Timekeeper,CONFIG['timekeeper_topic']),
            ('pose',Odometry,CONFIG['pose_topic']),('source',CostBreakdown,CONFIG['source_cost_topic']),
            ('raw',StampedFloat64MultiArray,CONFIG['raw_cost_topic']),
            ('provenance',SourceSampleProvenance,CONFIG['provenance_topic']),
            ('direction',GescDirectionDiagnostics,PREFIX+'/direction'),('ready',Bool,PREFIX+'/ready'),
            ('confirmation',DetectorConfirmation,'/gesc_gaussian/v2/detector_confirmation'))}
        for kind,topic,target in (
            (AlgorithmState,PREFIX+'/state',states),(SearchEpochContext,'/gesc_gaussian/v2/search_epoch',contexts),
            (FillCommand,'/gesc_gaussian/v2/fill_commands',commands),(FillResult,'/gesc_gaussian/v2/fill_results',results),
            (CandidateSnapshot,'/gesc_gaussian/v2/candidate_snapshots',snapshots)):
            driver.create_subscription(kind,topic,target.append,100)
        if escape_case is not None:
            driver.create_subscription(AlgorithmEvent,PREFIX+'/events',events.append,100)
            pub['stop']=driver.create_publisher(Bool,PREFIX+'/stop',10)
        empty_digest=fill_registry_digest([])
        def on_objective(obj):
            objectives.append(deepcopy(obj))
            source=time_to_ns(obj.model_input_stamp)
            if not obj.valid or source not in sample_geometry or not states:return
            phase,x,y,seq=sample_geometry[source]
            diag=GescDirectionDiagnostics();diag.schema_version=2
            diag.run_id=RUN;diag.stream_contract_id=stream_contract_id(CONFIG,0);diag.frame_id='odom'
            diag.stamp=stamp(driver.get_clock().now().nanoseconds);diag.time_origin=stamp(0)
            diag.algorithm_state=states[-1].state;diag.algorithm_state_valid=True
            diag.registry_digest=obj.registry_digest;diag.objective_revision=obj.objective_revision
            diag.objective_sha256=obj.objective_sha256;diag.output_valid=True;diag.qualified=False
            obs=SynchronizedObservation();obs.schema_version=2
            obs.run_id=RUN;obs.stream_contract_id=diag.stream_contract_id;obs.frame_id='odom'
            obs.stamp=deepcopy(diag.stamp);obs.time_origin=stamp(0)
            for field in ('source_stamp','cost_source_stamp','pose_left_stamp','pose_right_stamp',
                          'encoder_left_stamp','encoder_right_stamp','receipt_stamp','oldest_receipt_stamp'):
                setattr(obs,field,stamp(source))
            obs.admission_stamp=deepcopy(obj.composition_stamp)
            obs.legacy_cost_source_timestamp_sec=source/NS
            obs.base_x_m=x;obs.base_y_m=y;obs.base_yaw_rad=0.
            obs.sensor_world_phase_rad=phase;obs.sensor_phase_rad=phase;obs.encoder_phase_rad=phase
            obs.demodulation_phase_reconstructed=True
            obs.sensor_x_m=obj.sensor_x_m[0];obs.sensor_y_m=obj.sensor_y_m[0]
            obs.raw_cost=obj.raw_cost[0];obs.augmented_cost=obj.augmented_cost[0]
            obs.raw_cost_valid=obs.augmented_cost_valid=obs.synchronized_valid=obs.sensor_transform_observed=True
            obs.observation_id=seq;obs.source_sequence=seq;obs.objective_revision=obj.objective_revision
            diag.observation=obs
            if obj.registry_digest!=empty_digest and not allow_ack[0]:
                pending_ack.append(diag)
                if hold_objective:pub['direction'].publish(diag)
            else:pub['direction'].publish(diag)
        driver.create_subscription(ObjectiveCostSample,CONFIG['objective_cost_topic'],on_objective,100)
        prepared_generations=[]
        original_publish=gaussian.v2_fill._publish
        def observe_result(result):
            if result.result==FillResult.PREPARED:
                prepared_generations.append((gaussian.fill_registry.generation,composer.v2_fill_activation.generation))
            return original_publish(result)
        monkeypatch.setattr(gaussian.v2_fill,'_publish',observe_result)

        def spin_until(predicate,limit=2.):
            end=min(deadline,time.monotonic()+limit)
            while not predicate() and time.monotonic()<end:
                assert not producer_errors,producer_errors
                executor.spin_once(timeout_sec=.001)
            assert not producer_errors,producer_errors
            assert predicate(),dict(state=supervisor.machine.state.name,
                reason=supervisor.machine.transition_reason,raw=supervisor.moving_v2.last_reason,
                results=[(r.result,r.reason) for r in results[-5:]],
                composer=composer.v2_composer.last_fault_reason)
        def advance(value):
            now_ns[0]=value
            pub['clock'].publish(Clock(clock=stamp(value)))
            spin_until(lambda:all(n.get_clock().now().nanoseconds==value for n in nodes))
            pub['ready'].publish(Bool(data=True))
            spin_until(lambda:supervisor.moving_v2.ready())
        def publish_pose(value,x,y):
            pose=Odometry();pose.header.frame_id='odom';pose.header.stamp=stamp(value)
            pose.pose.pose.position.x=float(x);pose.pose.pose.position.y=float(y);pose.pose.pose.orientation.w=1.
            pub['pose'].publish(pose)
        def sample(value,index):
            # Independent source acquisition continues even while the supervisor
            # serializes a snapshot. No waits for algorithm consumption here.
            with source_lock:
                now_ns[0]=value;sequence[0]=index
            pub['clock'].publish(Clock(clock=stamp(value)))
            pub['ready'].publish(Bool(data=True))
            phase=2*math.pi*((value-NS)/NS)/3
            radius=.06+.008*math.cos(3*phase)
            x=radius*math.cos(phase);y=.8*radius*math.sin(phase)
            if depart.is_set():x,y=.8,0.
            raw=-1+x*x+.5*y*y
            seq=index
            sample_geometry[value]=(math.atan2(math.sin(phase),math.cos(phase)),x,y,seq)
            publish_pose(value,x,y)
            raw_msg=StampedFloat64MultiArray(timestamp=value/NS,data=[raw])
            source=CostBreakdown();source.stamp=stamp(value);source.source_timestamp=value/NS
            source.source_timestamp_valid=source.raw_cost_valid=True;source.channel_count=1;source.raw_cost=[raw]
            prov=SourceSampleProvenance();prov.schema_version=2;prov.run_id=RUN;prov.frame_id='odom'
            prov.stream_contract_id=stream_contract_id(CONFIG,0);prov.time_origin=stamp(0);prov.stamp=stamp(value)
            prov.source_sequence=seq;prov.model_input_stamp=prov.cost_publication_stamp=stamp(value)
            prov.legacy_cost_source_timestamp_sec=value/NS;prov.channel_count=1
            prov.sensor_x_m=[x+.18*math.cos(phase)];prov.sensor_y_m=[y+.18*math.sin(phase)]
            prov.sensor_world_phase_rad=[math.atan2(math.sin(phase),math.cos(phase))];prov.model_input_stamp_valid=prov.sensor_transform_valid=True
            pub['source'].publish(source);pub['provenance'].publish(prov);pub['raw'].publish(raw_msg)
        def source_sequence():
            with source_lock:return sequence[0]
        def produce():
            try:
                for index in range(1,2001):
                    if producer_stop.is_set():return
                    if index==364:
                        while not producer_resume.wait(.025):
                            if producer_stop.is_set():return
                    sample(NS+100_000_000+(index-1)*25_000_000,index)
                    # Pace acquisition by actual wall time; never catch up with
                    # a burst after scheduling delay or refresh duplicate keys.
                    if producer_stop.wait(.025):return
                producer_errors.append('finite synthetic source capacity reached')
            except BaseException as exc:
                producer_errors.append(repr(exc))
        spin_until(lambda:all(p.get_subscription_count() for p in pub.values()),8.)
        advance(NS)
        pub['timekeeper'].publish(Timekeeper(mode='sim time',start_time=0.))
        spin_until(lambda:supervisor.moving_v2.origin==gaussian.v2_fill.origin_ns==composer.v2_composer.origin_ns==0)
        # Let an actual supervisor timer publish its SEARCH context and weights.
        advance(NS+50_000_000)
        spin_until(lambda:states and contexts and contexts[-1].valid and composer.algorithm_state is not None)
        if escape_case is not None and escape_case['anchor'] is not None:
            # A synthetic historical pose enters through the ordinary selected
            # DDS pose subscription before candidate evidence acquisition.
            anchor=escape_case['anchor']
            publish_pose(NS+50_000_000,*anchor)
            spin_until(lambda:any(abs(p.x-anchor[0])<1e-12 and abs(p.y-anchor[1])<1e-12
                                  for p in supervisor.pose_history))
        producer=threading.Thread(target=produce,name='moving_pipeline_source',daemon=False)
        producer.start()
        prefix_end=NS+100_000_000+362*25_000_000
        spin_until(lambda:source_sequence()==363 and supervisor.moving_v2.raw.records
                   and supervisor.moving_v2.raw.records[-1].stamp_ns==prefix_end,15.)
        spin_until(lambda:supervisor.moving_v2.raw.evaluate((0.,0.),.5,.1,prefix_end).ready)
        context=contexts[-1]
        confirmation=DetectorConfirmation();confirmation.schema_version=1
        confirmation.run_id=RUN;confirmation.stream_contract_id=context.stream_contract_id;confirmation.frame_id='odom'
        confirmation.time_origin=stamp(0);confirmation.stamp=stamp(now_ns[0])
        confirmation.search_epoch=context.search_epoch;confirmation.context_sequence=context.context_sequence
        confirmation.epoch_started_at=deepcopy(context.started_at)
        confirmation.source_stamp=confirmation.history_end=stamp(now_ns[0])
        confirmation.history_start=stamp(NS+100_000_000)
        confirmation.metric_mode=metric_mode;confirmation.history_kind='centroid_windows'
        confirmation.source_stamp_kind='pose_input';confirmation.confirmation_sequence=1
        confirmation.convergence_score_m=.01;confirmation.convergence_score_valid=True;confirmation.valid=True
        if metric_mode=='pde_mean_v1':
            confirmation.history_kind='pde_input_support'
            confirmation.legacy_snapshot=[-.01,.01,0.,0.,0.,0.,0.,0.]
            confirmation.legacy_r_mean_m2=.01;confirmation.legacy_r_mean_valid=True
        pub['confirmation'].publish(confirmation)
        spin_until(lambda:supervisor.moving_v2.candidate is not None)
        producer_resume.set()
        spin_until(started.is_set,3.)
        assert supervisor.machine.state==3 and gaussian.fill_registry.generation==composer.v2_fill_activation.generation==0
        spin_until(lambda:snapshots and commands)
        assert commands[0].operation==FillCommand.PREPARE
        assert snapshot_sha256(snapshots[0])==commands[0].evidence_sha256
        assert not any(r.result==FillResult.ACTIVATED for r in results)
        if depart_during_worker:
            depart.set()
            spin_until(lambda:any(c.operation==FillCommand.CANCEL for c in commands))
            release.set()
            spin_until(lambda:computed.is_set() and supervisor.machine.state==1)
            spin_until(lambda:any(r.result in (FillResult.CANCELLED,FillResult.REJECTED) for r in results))
            assert gaussian.fill_registry.generation==composer.v2_fill_activation.generation==0
            assert not composer.robust_terms and supervisor.machine.active_fill_count==0
            assert not any(s.state in (4,5) for s in states)
        else:
            release.set()
            # At most120 new source samples for activation, matching the old
            # fixture allowance; original ROS and steady freshness stay active.
            release_sequence=source_sequence()
            spin_until(lambda:gaussian.fill_registry.generation==composer.v2_fill_activation.generation==1
                       or source_sequence()-release_sequence>=120,8.)
            assert gaussian.fill_registry.generation==composer.v2_fill_activation.generation==1
            spin_until(lambda:supervisor.machine.active_fill_count==1)
            assert prepared_generations==[(0,0)]
            assert supervisor.machine.state==3
            spin_until(lambda:pending_ack)
            assert supervisor.machine.state==3
            available_ack='direction_ack' if hold_objective else 'objective_ack'
            spin_until(lambda:getattr(supervisor.moving_v2,available_ack) is not None
                       and getattr(supervisor.moving_v2,available_ack)[0]==pending_ack[-1].registry_digest)
            if escape_case is not None:
                # Several real supervisor timer opportunities with exactly one
                # acknowledged consumer must not authorize escape.
                one_ack_sequence=source_sequence()
                spin_until(lambda:source_sequence()>=one_ack_sequence+6)
                assert supervisor.machine.state==3
                assert not any(s.state in (4,5) for s in states)
                assert not any(e.event_type==AlgorithmEvent.EVENT_ESCAPE_STARTED for e in events)
                assert supervisor.machine.config.open_field_escape_approach_continuity_enabled
                assert supervisor.machine.config.open_field_escape_interior_anchor_fallback_enabled==escape_case['interior']
                assert supervisor.machine.config.open_field_escape_interior_anchor_min_displacement_m==.5
                assert supervisor.moving_v2.radius==.75 and supervisor.moving_v2.epsilon==.15
            release_objective.set()
            allow_ack[0]=True;pub['direction'].publish(pending_ack[-1])
            ack_sequence=source_sequence()
            expected_state=8 if escape_case is not None and escape_case['expected']=='failsafe' else 4
            spin_until(lambda:supervisor.machine.state==expected_state or source_sequence()-ack_sequence>=8)
            assert supervisor.machine.state==expected_state
            spin_until(lambda:any(r.result==FillResult.ACTIVATED for r in results))
            accepted=next(r for r in results if r.result==FillResult.ACTIVATED)
            assert accepted.registry_digest_after==fill_registry_digest(composer.v2_fill_activation.active.values())
            assert len(composer.robust_terms)==len(supervisor.machine.filled_candidate_costs)==1
            # Node transition and DDS observer delivery are separate events.
            expected_escape_fill=accepted.fill.fill_id if expected_state==4 else 0
            spin_until(lambda:states and states[-1].state==expected_state
                       and states[-1].active_escape_fill_id==expected_escape_fill)
            assert states[-1].active_escape_fill_id==expected_escape_fill
            if escape_case is not None:
                if expected_state==4:
                    spin_until(lambda:any(e.event_type==AlgorithmEvent.EVENT_ESCAPE_STARTED for e in events))
                    continuity=supervisor.escape_approach_continuity
                    assert continuity.anchor_mode==escape_case['expected']
                    assert continuity.displacement_m>=.5
                    if continuity.anchor_mode=='outside_radius':
                        assert continuity.displacement_m>accepted.fill.exit_radius
                    else:
                        assert continuity.displacement_m<=accepted.fill.exit_radius
                    assert not any(e.event_type==AlgorithmEvent.EVENT_FAILSAFE for e in events)
                    # An actual stop callback ends motion after successful
                    # escape admission; the owner itself emits postcommit CANCEL.
                    pub['stop'].publish(Bool(data=True))
                else:
                    reason=('open-field escape approach continuity has no qualified outside-radius or interior anchor'
                            if escape_case['interior'] else
                            'open-field escape approach continuity has no pose outside the frozen exit radius')
                    assert supervisor.machine.transition_reason==reason
                    spin_until(lambda:any(e.event_type==AlgorithmEvent.EVENT_FAILSAFE and e.detail==reason
                                          for e in events))
                    assert not any(e.event_type==AlgorithmEvent.EVENT_ESCAPE_STARTED for e in events)
                    assert not any(s.state in (4,5) for s in states)
                spin_until(lambda:any(c.operation==FillCommand.CANCEL for c in commands)
                           and any(r.result==FillResult.ALREADY_ACTIVATED for r in results))
                spin_until(lambda:states[-1].state==8)
                assert supervisor.current_supervisor_command.linear.x==0.
                assert supervisor.current_supervisor_command.angular.z==0.
                assert gaussian.fill_registry.generation==composer.v2_fill_activation.generation==1
                assert len(composer.robust_terms)==len(supervisor.machine.filled_candidate_costs)==1
                assert sum(r.result==FillResult.ACTIVATED for r in results)==1
                retried=next(r for r in results if r.result==FillResult.ALREADY_ACTIVATED)
                assert retried.registry_digest_after==accepted.registry_digest_after
                assert retried.fill==accepted.fill
                print('M4_V5_ESCAPE',dict(case=escape_case,prepared_generations=prepared_generations,
                    generation=gaussian.fill_registry.generation,accepted_fill_id=accepted.fill.fill_id,
                    exit_radius_m=accepted.fill.exit_radius,filled_candidate_count=len(supervisor.machine.filled_candidate_costs),
                    postcommit_cancel_result=int(retried.result),final_state=int(states[-1].state),
                    escape_started=sum(e.event_type==AlgorithmEvent.EVENT_ESCAPE_STARTED for e in events)))
    finally:
        producer_stop.set();producer_resume.set();release.set()
        if producer is not None:
            producer.join(timeout=2.)
            assert not producer.is_alive(),'synthetic source did not terminate'
        for node in nodes:executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in reversed(nodes):node.destroy_node()
        rclpy.try_shutdown()
