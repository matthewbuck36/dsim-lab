"""Typed lifecycle tests with actual ROS message classes and detached owners."""
from copy import deepcopy
from types import SimpleNamespace
import math
import pytest
from ros_esc_interfaces.msg import (DetectorConfirmation, FillCommand, FillResult,
    GaussianFill, GescDirectionDiagnostics, ObjectiveCostSample, SourceSampleProvenance, Timekeeper)
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256, snapshot_sha256
from ros_esc.v2_stream import SUPPORTED_GEOMETRY, TOPIC_KEYS, set_time
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor, stamp
from ros_esc.supervisor_node.state_machine import (State, StateMachineConfig,
    SupervisorStateMachine, TransitionInputs)
from test_v2_moving_evidence import observation


@pytest.fixture(autouse=True)
def deterministic_unit_steady_clock(monkeypatch, request):
    # Pure fixtures control ROS time explicitly. Computation speed under an
    # integrated pytest load must not accidentally consume their wall budget.
    # Actual node callback and separate DDS tests retain the real steady clock.
    if request.node.name.startswith('test_actual_node_'):
        return
    monkeypatch.setattr('ros_esc.supervisor_node.v2_supervisor.time.monotonic_ns',
                        lambda: 1_000_000_000)


class Publisher:
    def __init__(self): self.messages=[]
    def publish(self, msg): self.messages.append(deepcopy(msg))


class Node:
    def __init__(self, known=2):
        self.clock_ns=0; self.run_id='synthetic'; self.graph_fault=None
        self.recording_ready_required=True
        self.machine=SupervisorStateMachine(config=StateMachineConfig(
            moving_verification_enabled=True, extremum_classification_mode='counted_candidates',
            known_source_count=known, max_fill_clusters=known-1, candidate_cost_required_rotations=3))
        self.escape_tracker=None; self.received=[]
    def get_clock(self): return SimpleNamespace(now=lambda:SimpleNamespace(nanoseconds=self.clock_ns))
    def create_publisher(self,*args): return Publisher()
    def create_subscription(self,*args): return args
    def fill_callback(self,msg,authoritative=False): self.received.append((deepcopy(msg),authoritative))
    def _publish_state_and_command(self,*args): self.adapter.publish_context()


def config():
    value=dict(schema_version=2,frame_id='odom',selected_channel=0,
        sensor_geometry_config_sha256='a'*64, sensor_geometry=SUPPORTED_GEOMETRY,
        cost_key_basis='model_input_time')
    value.update({k:'/synthetic/'+k for k in TOPIC_KEYS})
    return value


def adapter(known=2):
    node=Node(known); owner=MovingSupervisor(node,config(),.5,.1); node.adapter=owner
    clock=Timekeeper(); clock.mode='sim time'; clock.start_time=0.
    owner.timekeeper(clock)
    owner.readiness(Bool(data=True))
    return node,owner


def identity(owner,msg):
    msg.schema_version=1 if isinstance(msg,(DetectorConfirmation,FillResult)) else 2
    msg.run_id=owner.node.run_id; msg.stream_contract_id=owner.contract; msg.frame_id='odom'
    msg.time_origin=stamp(owner.origin)
    msg.stamp=stamp(owner.now())
    return msg


def pose(owner, source=None, xy=(0.,0.)):
    msg=Odometry(); msg.header.frame_id='odom'
    msg.header.stamp=stamp(owner.now() if source is None else source)
    msg.pose.pose.position.x, msg.pose.pose.position.y=xy
    msg.pose.pose.orientation.w=1.
    owner.add_pose(msg)


def stream(owner, *, start=0.,end=9.,raw=None):
    for i in range(round(start/.025),round(end/.025)+1):
        t=i*.025; owner.node.clock_ns=round(t*1e9)
        owner.readiness(Bool(data=True))
        msg=identity(owner,GescDirectionDiagnostics())
        msg.algorithm_state=int(owner.node.machine.state); msg.algorithm_state_valid=True
        msg.output_valid=True; msg.qualified=False # verifier must ignore this gate
        msg.registry_digest=owner.registry_digest
        msg.observation=identity(owner,observation(t,raw=raw))
        owner.direction(msg)
        pose(owner)


def confirm(owner, mode='centroid_windows_v2'):
    owner.publish_context()
    msg=identity(owner,DetectorConfirmation())
    msg.search_epoch=owner.epoch; msg.context_sequence=owner.context_sequence
    msg.epoch_started_at=stamp(owner.started); msg.source_stamp=stamp(owner.now())
    msg.history_start=stamp(owner.started); msg.history_end=stamp(owner.now())
    msg.metric_mode=mode; msg.history_kind='centroid_windows' if mode=='centroid_windows_v2' else 'pde_input_support'
    msg.source_stamp_kind='pose_input'; msg.confirmation_sequence=1
    msg.center_x_m=msg.center_y_m=0.; msg.convergence_score_m=.01; msg.convergence_score_valid=True
    msg.legacy_r_mean_valid=True; msg.legacy_r_mean_m2=.01
    msg.legacy_snapshot=[0.,.01,0.,0.,0.,0.,0.,0.]
    msg.valid=True
    owner.confirmation(msg)
    return msg


def step(owner):
    inputs=owner.inputs(TransitionInputs())
    transition=owner.node.machine.step(owner.now()*1e-9,inputs)
    if transition is not None: owner.on_transition(transition)
    return transition


def test_verification_deadline_transition_retains_last_evidence_guard():
    node, owner = adapter()
    stream(owner, raw=-3.)
    confirm(owner)
    assert step(owner).current == State.VERIFY_EXTREMUM
    assert step(owner) is None
    retained = owner.candidate.last_evidence_detail
    assert retained.startswith('uninformative_raw_profiles ')
    assert 'signal_margin' in retained
    node.clock_ns = owner.candidate.deadline_ns
    owner.readiness(Bool(data=True))
    pose(owner)
    transition = step(owner)
    assert transition.current == State.SEARCH
    assert 'verification_deadline; last_evidence=' + retained in transition.reason
    assert owner.candidate is None  # transition survived the epoch cleanup


def design(owner):
    stream(owner); confirm(owner)
    assert step(owner).current==State.VERIFY_EXTREMUM
    assert step(owner).current==State.DESIGN_OR_MERGE_FILL
    return owner.current_preparation


def result_base(owner,prep,kind,seq=None):
    msg=identity(owner,FillResult())
    cmd=prep.command
    msg.search_epoch=cmd.search_epoch; msg.candidate_id=cmd.candidate_id
    msg.objective_revision=cmd.objective_revision
    msg.preparation_id=cmd.preparation_id
    msg.command_sequence=seq if seq is not None else max(prep.sequences)
    msg.expected_registry_generation=cmd.expected_registry_generation
    msg.evidence_sha256=cmd.evidence_sha256; msg.prepared_sha256='b'*64
    msg.expires_at=deepcopy(cmd.expires_at); msg.return_state=cmd.return_state
    msg.prepared_at=stamp(owner.now()); msg.registry_generation=owner.generation
    msg.result=kind
    return msg


def prepared(owner,prep):
    msg=result_base(owner,prep,FillResult.PREPARED); owner.result(msg)
    assert prep.prepared is not None
    assert owner.command_publisher.messages[-1].operation==FillCommand.ACTIVATE
    return msg


def committed(owner,prep):
    msg=result_base(owner,prep,FillResult.ACTIVATED)
    msg.registry_generation=owner.generation+1
    msg.registry_digest_before=owner.registry_digest
    msg.committed_at=stamp(owner.now())
    fill=GaussianFill(); fill.fill_id=1; fill.cluster_id=1; fill.revision=1
    fill.active=True; fill.frame_id='odom'; fill.amplitude=1.
    fill.center_x=fill.center_y=0.
    fill.covariance_xx=fill.covariance_yy=.2; fill.covariance_xy=0.
    fill.sigma_major=fill.sigma_minor=math.sqrt(.2)
    fill.support_radius=fill.exit_radius=.5
    fill.covariance_valid=fill.principal_widths_valid=True
    fill.support_radius_valid=fill.exit_radius_valid=True
    fill.source_timestamp_valid=True; fill.source_timestamp=9.
    msg.fill=fill
    msg.registry_digest_after=fill_registry_digest([fill])
    msg.committed_sha256=result_sha256(msg)
    return msg


def ack(owner,digest):
    msg=identity(owner,ObjectiveCostSample()); msg.valid=True; msg.registry_digest=digest
    owner.objective(msg)
    msg=identity(owner,GescDirectionDiagnostics()); msg.algorithm_state=int(owner.node.machine.state)
    msg.algorithm_state_valid=True; msg.registry_digest=digest
    owner.direction(msg)


@pytest.mark.parametrize('mode',['centroid_windows_v2','pde_mean_v1'])
def test_typed_confirmation_binds_fresh_authoritative_epoch_and_once_only(mode):
    node,owner=adapter(); stream(owner)
    msg=confirm(owner,mode)
    assert owner.candidate is not None
    first=owner.candidate.candidate_id
    owner.confirmation(msg)
    assert owner.candidate.candidate_id==first
    assert step(owner).current==State.VERIFY_EXTREMUM
    bad=deepcopy(msg); bad.search_epoch+=1
    owner.confirmation(bad)
    assert owner.candidate.candidate_id==first


def test_old_history_and_stale_context_do_not_authorize():
    node,owner=adapter(); node.clock_ns=10_000_000_000; pose(owner)
    owner.started=9_000_000_000; owner.raw.start_epoch(2,owner.started); owner.epoch=2
    msg=confirm(owner); owner.candidate=None; owner.accepted_epoch=None
    msg.history_start=stamp(8_999_999_999)
    owner.confirmation(msg); assert owner.candidate is None
    msg.history_start=stamp(owner.started)
    node.clock_ns+=500_000_001
    owner.confirmation(msg); assert owner.candidate is None


def test_snapshot_frozen_pretrigger_and_prepare_is_not_activation():
    node,owner=adapter(); prep=design(owner)
    snap=deepcopy(prep.command.snapshot)
    assert snap.pretrigger_revolutions==3 and snap.verification_revolutions==0
    assert not prep.command.redesign
    assert snapshot_sha256(snap)==snap.evidence_sha256
    assert node.machine.active_fill_count==0 and not node.received
    stream(owner,start=9.025,end=9.2)
    assert prep.command.snapshot==snap
    prepared(owner,prep)
    assert node.machine.state==State.DESIGN_OR_MERGE_FILL and node.machine.active_fill_count==0


def test_activation_accounting_requires_exact_result_and_both_registry_acks():
    node,owner=adapter(); prep=design(owner); prepared(owner,prep)
    msg=committed(owner,prep)
    bad=deepcopy(msg); bad.fill.amplitude=2.
    owner.result(bad); assert owner.generation==0
    owner.result(msg)
    assert owner.generation==1 and len(node.machine.filled_candidate_costs)==1
    assert node.received[-1][1]
    assert step(owner) is None
    ack(owner,msg.registry_digest_after)
    assert step(owner).current==State.ESCAPE_REPULSE
    owner.result(msg)
    assert len(node.machine.filled_candidate_costs)==1


def test_cancel_before_prepared_prevents_activate_and_retains_original_deadline():
    node,owner=adapter(); prep=design(owner)
    expires=deepcopy(prep.command.expires_at)
    node.clock_ns+=100_000_000; pose(owner,xy=(.6,0.))
    assert owner.command_publisher.messages[-1].operation==FillCommand.CANCEL
    late=result_base(owner,prep,FillResult.PREPARED,seq=1)
    owner.result(late)
    assert prep.prepared is None and prep.command.expires_at==expires
    assert step(owner).current==State.SEARCH
    assert owner.epoch==2


def test_accepted_result_after_search_exit_updates_ledger_without_returning_robot():
    node,owner=adapter(); prep=design(owner); prepared(owner,prep)
    accepted=committed(owner,prep)
    owner.cancel('departure')
    assert step(owner).current==State.SEARCH
    owner.result(accepted)
    assert owner.generation==1 and node.machine.active_fill_count==1
    assert node.machine.state==State.SEARCH and len(node.machine.filled_candidate_costs)==1
    ack(owner,accepted.registry_digest_after)
    assert step(owner) is None and node.machine.state==State.SEARCH
    replay=deepcopy(accepted); replay.result=FillResult.ALREADY_ACTIVATED
    replay.command_sequence=3; replay.committed_sha256=result_sha256(replay)
    owner.result(replay)
    assert len(node.machine.filled_candidate_costs)==1


def test_revocation_poison_invalidates_frozen_candidate_and_delayed_valid_cannot_restore():
    node,owner=adapter(); prep=design(owner)
    revoked=identity(owner,SourceSampleProvenance()); revoked.model_input_stamp=stamp(8_000_000_000)
    revoked.source_sequence=999
    owner.provenance(revoked)
    assert prep.candidate.cancelled
    assert not owner.raw.records
    msg=identity(owner,GescDirectionDiagnostics()); msg.algorithm_state=2; msg.algorithm_state_valid=True
    msg.observation=identity(owner,observation(8.))
    owner.direction(msg)
    assert not owner.raw.records


def test_uninformative_wait_does_not_extend_twelve_second_deadline():
    node,owner=adapter(known=1); stream(owner,raw=-3.); confirm(owner)
    assert step(owner).current==State.VERIFY_EXTREMUM
    deadline=owner.candidate.deadline_ns
    assert step(owner) is None
    node.clock_ns=deadline; pose(owner)
    assert step(owner).current==State.SEARCH and owner.epoch==2


def test_explicit_neighborhood_is_mandatory():
    with pytest.raises(ValueError,match='v2_candidate_radius_m'):
        MovingSupervisor(Node(),config(),0.,.1)


def test_future_pose_keeps_current_authorization_then_drains_original_receipt():
    node,owner=adapter(); prep=design(owner)
    old=owner.pose
    pose(owner,source=node.clock_ns+100_000_000,xy=(.01,0.))
    assert owner.pose==old and len(owner.pending_poses)==1
    assert owner.pose_inside(prep.candidate) and not prep.candidate.cancelled
    original_receipt=owner.pending_poses[0][2:4]
    pose(owner,source=node.clock_ns+100_000_000,xy=(.01,0.))
    assert len(owner.pending_poses)==1 and owner.pending_poses[0][2:4]==original_receipt
    node.clock_ns+=100_000_000
    owner.drain_poses()
    assert not owner.pending_poses and owner.pose[1]==(.01,0.)
    assert owner.pose[2:4]==original_receipt


def test_future_pose_expiry_and_conflict_cannot_refresh_or_resurrect(monkeypatch):
    node,owner=adapter(); pose(owner)
    pose(owner,source=100_000_000,xy=(.01,0.))
    first=owner.pending_poses[0]
    monkeypatch.setattr('ros_esc.supervisor_node.v2_supervisor.time.monotonic_ns',lambda:first[3]+500_000_001)
    node.clock_ns=100_000_000; owner.drain_poses()
    assert not owner.pending_poses and owner.pose[0]==0
    pose(owner,source=200_000_000,xy=(.01,0.))
    pose(owner,source=200_000_000,xy=(.02,0.))
    assert 200_000_000 in owner.pose_tombstones and owner.pose is None
    pose(owner,source=200_000_000,xy=(.01,0.))
    assert not owner.pending_poses


def test_readiness_required_blocks_direct_confirmation_and_activation():
    node,owner=adapter(); stream(owner)
    owner.readiness(Bool(data=False))
    confirm(owner)
    assert owner.candidate is None
    owner.readiness(Bool(data=True)); stream(owner,start=9.025,end=18.025)
    confirm(owner); assert step(owner).current==State.VERIFY_EXTREMUM
    assert step(owner).current==State.DESIGN_OR_MERGE_FILL
    prep=owner.current_preparation
    owner.readiness(Bool(data=False))
    owner.result(result_base(owner,prep,FillResult.PREPARED,seq=1))
    assert prep.prepared is None
    assert owner.command_publisher.messages[-1].operation==FillCommand.CANCEL


def test_nonzero_origin_fences_initial_authoritative_history():
    node=Node(); owner=MovingSupervisor(node,config(),.5,.1); node.adapter=owner
    assert owner.started==0
    clock=Timekeeper(); clock.mode='sim time'; clock.start_time=123.25
    owner.timekeeper(clock)
    assert owner.started==owner.raw.epoch_start_ns==123_250_000_000
    owner.readiness(Bool(data=True)); owner.publish_context()
    assert owner.epoch_publisher.messages[-1].started_at==stamp(owner.started)
    assert not owner.epoch_publisher.messages[-1].valid
    node.clock_ns=owner.started
    owner.publish_context()
    assert owner.epoch_publisher.messages[-1].valid


def test_invalid_geometry_cannot_enter_ledger_even_with_recomputed_wire_hash():
    node,owner=adapter(); prep=design(owner); prepared(owner,prep)
    msg=committed(owner,prep); msg.fill.amplitude=-1.
    msg.registry_digest_after=fill_registry_digest([msg.fill]); msg.committed_sha256=result_sha256(msg)
    owner.result(msg)
    assert owner.generation==0 and node.machine.active_fill_count==0 and not node.received


def test_design_expiry_never_renews_on_prepared_response():
    node,owner=adapter(); prep=design(owner)
    deadline=prep.command.expires_at
    node.clock_ns+=4_900_000_000; pose(owner)
    owner.readiness(Bool(data=True)); prepared(owner,prep)
    assert prep.command.expires_at==deadline
    node.clock_ns=14_000_000_000; pose(owner)
    assert step(owner).current==State.SEARCH
    assert owner.command_publisher.messages[-1].operation==FillCommand.CANCEL


def test_actual_node_requires_explicit_neighborhood_and_uses_admitted_pose(monkeypatch):
    import rclpy
    from rclpy.parameter import Parameter
    from ros_esc.v2_stream import canonical_json
    from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
    rclpy.init(args=[])
    node=None
    params=[Parameter('use_sim_time',value=True),Parameter('continuous_search_mode',value='rolling_gesc_v2'),
            Parameter('v2_run_id',value='actual_supervisor'),
            Parameter('v2_stream_config_json',value=canonical_json(config())),
            Parameter('extremum_classification_mode',value='counted_candidates'),
            Parameter('known_source_count',value=2),Parameter('max_fill_clusters',value=1),
            Parameter('v2_candidate_radius_m',value=.5),Parameter('v2_candidate_epsilon_m',value=.1)]
    try:
        node=SupervisorNode(parameter_overrides=params)
        now=[1_000_000_000]
        monkeypatch.setattr(node,'get_clock',lambda:SimpleNamespace(now=lambda:SimpleNamespace(
            nanoseconds=now[0],to_msg=lambda:stamp(now[0]))))
        clock=Timekeeper();clock.mode='sim time';clock.start_time=0.;node.moving_v2.timekeeper(clock)
        msg=Odometry();msg.header.frame_id='odom';msg.header.stamp=stamp(now[0]);msg.pose.pose.orientation.w=1.
        node.pose_callback(msg)
        assert node.latest_pose.position[0]==0.
        future=deepcopy(msg);future.header.stamp=stamp(now[0]+100_000_000);future.pose.pose.position.x=.1
        node.pose_callback(future)
        assert node.latest_pose.position[0]==0. and node.moving_v2.pose[1][0]==0.
        now[0]+=100_000_000;node.moving_v2.drain_poses()
        assert node.latest_pose.position[0]==.1 and node.latest_pose_receipt_sec==1.
        assert not node.moving_v2.ready_required and node.moving_v2.ready()
        node.machine._transition(State.VERIFY_EXTREMUM,1.1,'test')
        node.machine._transition(State.DESIGN_OR_MERGE_FILL,1.1,'test')
        assert node.machine.weights==(1.,1.,0.)
    finally:
        if node is not None: node.destroy_node()
        rclpy.try_shutdown()


def test_redesign_freezes_same_candidate_new_snapshot_exact_target_and_original_escape_clock():
    node,owner=adapter(); first=design(owner); prepared(owner,first)
    accepted=committed(owner,first);owner.result(accepted);ack(owner,accepted.registry_digest_after)
    assert step(owner).current==State.ESCAPE_REPULSE
    original=node.machine.escape_started_sec
    stream(owner,start=9.025,end=12.)
    node.machine.design_returns_to_assist=True
    transition=node.machine._transition(State.DESIGN_OR_MERGE_FILL,12.,'escape stalled')
    owner.on_transition(transition)
    prep=owner.current_preparation
    assert prep is not first and prep.command.redesign
    assert prep.command.candidate_id==first.command.candidate_id
    assert prep.command.snapshot.snapshot_revision==2
    assert (prep.command.target_fill_id,prep.command.target_cluster_id,prep.command.target_revision)==(1,1,1)
    assert prep.command.expires_at==stamp(17_000_000_000)
    assert node.machine.escape_started_sec==original
    rejection=result_base(owner,prep,FillResult.REJECTED);owner.result(rejection)
    assert step(owner).current==State.ESCAPE_ASSIST
    assert node.machine.escape_started_sec==original and owner.generation==1


def test_unavailable_redesign_does_not_rewait_or_renew_escape():
    node,owner=adapter(); first=design(owner); prepared(owner,first)
    accepted=committed(owner,first);owner.result(accepted);ack(owner,accepted.registry_digest_after)
    assert step(owner).current==State.ESCAPE_REPULSE
    original=node.machine.escape_started_sec
    owner.raw.reset('synthetic_missing_new_history')
    node.machine.design_returns_to_assist=True
    transition=node.machine._transition(State.DESIGN_OR_MERGE_FILL,9.,'escape stalled')
    owner.on_transition(transition)
    assert owner.candidate.cancelled
    assert step(owner).current==State.ESCAPE_ASSIST
    assert node.machine.escape_started_sec==original and owner.generation==1


def test_verified_no_fill_goal_publishes_same_immutable_candidate_evidence_once():
    node,owner=adapter(known=1);stream(owner);confirm(owner)
    assert step(owner).current==State.VERIFY_EXTREMUM
    assert not owner.snapshot_publisher.messages
    assert step(owner).current==State.GOAL_HOLD
    assert len(owner.snapshot_publisher.messages)==1 and not owner.command_publisher.messages
    saved=owner.snapshot_publisher.messages[0]
    assert saved.informative and saved.completed_revolutions==3
    assert snapshot_sha256(saved)==saved.evidence_sha256
    assert step(owner) is None and len(owner.snapshot_publisher.messages)==1


def test_first_received_filter_metadata_survives_readiness_and_state_repeat():
    node,owner=adapter();owner.readiness(Bool(data=False))
    node.clock_ns=1_000_000_000
    msg=identity(owner,GescDirectionDiagnostics());msg.algorithm_state=1;msg.algorithm_state_valid=True
    msg.observation=identity(owner,observation(1.))
    owner.direction(msg)
    assert not owner.raw.records
    first=owner.first_filter_metadata[1_000_000_000]
    owner.readiness(Bool(data=True));node.clock_ns=1_100_000_000
    msg.stamp=stamp(node.clock_ns);msg.algorithm_state=2
    owner.direction(msg)
    assert owner.raw.records[0].filter_state==1
    assert owner.raw.records[0].filter_stamp_ns==1_000_000_000
    assert owner.first_filter_metadata[1_000_000_000]==first


def test_controlled_original_steady_expiry_reproduces_integrated_fixture_cancellation(monkeypatch):
    node,owner=adapter();prep=design(owner);prepared(owner,prep)
    owner.result(committed(owner,prep))
    assert owner.generation==1 and node.clock_ns==9_000_000_000
    monkeypatch.setattr('ros_esc.supervisor_node.v2_supervisor.time.monotonic_ns',lambda:1_500_000_001)
    inputs=owner.inputs(TransitionInputs())
    assert prep.candidate.reason=='candidate_pose_unavailable_or_departed'
    transition=node.machine.step(owner.now()*1e-9,inputs)
    owner.on_transition(transition)
    assert transition.current==State.SEARCH
    assert transition.reason.startswith('moving preparation cancelled; resume search; candidate_pose_unavailable_or_departed')
    assert not owner.ready() and owner.candidate is None
    assert owner.generation==1 # accepted registry fact is retained


@pytest.mark.parametrize('value',[1e308,2_147_483_648.,-1.,float('inf'),float('nan')])
def test_malformed_or_oversized_time_origin_latches_invalid_without_assignment(value):
    node=Node();owner=MovingSupervisor(node,config(),.5,.1);node.adapter=owner
    owner.timekeeper(Timekeeper(mode='sim time',start_time=value))
    assert owner.origin_fault and owner.origin is None and owner.contract is None
    owner.readiness(Bool(data=True));owner.publish_context()
    assert not owner.epoch_publisher.messages[-1].valid
    owner.timekeeper(Timekeeper(mode='sim time',start_time=0.))
    assert owner.origin_fault and owner.origin is None


def test_changed_valid_origin_preserves_first_identity_and_invalidates():
    node,owner=adapter();original=(owner.origin,owner.contract)
    owner.timekeeper(Timekeeper(mode='sim time',start_time=1.))
    assert owner.origin_fault and (owner.origin,owner.contract)==original
    owner.publish_context();assert not owner.epoch_publisher.messages[-1].valid
