"""Deterministic owner/worker races and atomic composition with real wire types."""
from concurrent.futures import Future
from copy import deepcopy
from dataclasses import replace
import math
from types import SimpleNamespace

import numpy as np
import pytest
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import (
    AlgorithmState, CandidateSnapshot, FillCommand, FillResult, SearchEpochContext,
    SynchronizedObservation, Timekeeper,
)
from ros_esc.gaussian_fill_node.basin_estimator import BasinSample, EstimatorConfig
from ros_esc.gaussian_fill_node.fill_designer import FillDesignConfig
from ros_esc.gaussian_fill_node.fill_preparation import (
    PreparationInput, PreparedProposal, combine_samples, compute_fill_proposal,
)
from ros_esc.gaussian_fill_node.fill_registry import FillRegistry, RegistryConfig
from ros_esc.gaussian_fill_node.v2_fill_runtime import MovingFillRuntime, version_message
from ros_esc.modified_cost_node.v2_fill_activation import AtomicFillActivation
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256, snapshot_sha256
from ros_esc.v2_stream import SUPPORTED_GEOMETRY, canonical_json, set_time, stream_contract_id

CONFIG = dict(schema_version=2, cost_key_basis='model_input_time', frame_id='odom', selected_channel=0,
              sensor_geometry=SUPPORTED_GEOMETRY, sensor_geometry_config_sha256='a'*64,
              **{key: '/test/'+key for key in ('raw_cost_topic', 'source_cost_topic', 'augmented_cost_topic',
                  'objective_cost_topic', 'provenance_topic', 'pose_topic', 'encoder_topic', 'timekeeper_topic')})
CONTRACT = stream_contract_id(CONFIG, 0)


def values(amplitude=1.):
    return dict(source_timestamp=1., center=(0., 0.), amplitude=amplitude,
                covariance=((.04, 0.), (0., .04)), sigma_major=.2, sigma_minor=.2,
                orientation=0., support_radius=.6, exit_radius=.5, confidence=.8,
                sample_count=91, fit_residual=0., fit_condition_number=1.,
                fit_condition_number_valid=True, design_escalations=0)


class Publisher:
    def __init__(self): self.messages = []
    def publish(self, msg): self.messages.append(deepcopy(msg))


class Worker:
    def submit(self, function, inp):
        self.function, self.input, self.future = function, inp, Future()
        self.future.set_running_or_notify_cancel()
        return self.future
    def complete(self, *, amplitude=1., target=None):
        self.future.set_result(PreparedProposal(tuple(values(amplitude).items()), self.input.samples,
            None if target is None else target[1], target, self.input.registry.generation,
            len(self.input.samples), ()))
    def shutdown(self, **kwargs): pass


class Node:
    def __init__(self):
        self.now_ns = 10_100_000_000
        self.steady_ns = 0
        self.algorithm_profile = 'robust_gaussian_v1'
        self.params = dict(v2_run_id='test-m3', v2_stream_config_json=canonical_json(CONFIG),
                           use_sim_time=True, pose_topic=CONFIG['pose_topic'],
                           v2_fill_result_topic='/gesc_gaussian/v2/fill_results', v2_fill_command_topic='/gesc_gaussian/v2/fill_commands',
                           v2_search_epoch_topic='/gesc_gaussian/v2/search_epoch')
        self.fill_registry = FillRegistry(RegistryConfig())
        self.estimator_config, self.design_config = EstimatorConfig(), FillDesignConfig()
        self.candidate_informed_fill_enabled = False
        self.candidate_informed_fill_amplitude_scale = 1.
        self.max_fills = 4
        self.reuse_retained_samples_on_redesign = False
        self.fill_request_callback_group = None
        self.mirrors, self.compatibility = [], []
        self.robust_terms, self.robust_cluster_fill_ids, self.robust_affine_terms = {}, {}, {}
        self.affine_syncs = 0
    def get_parameter(self, key): return SimpleNamespace(value=self.params[key])
    def resolve_topic_name(self, name): return name
    def get_clock(self): return SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=self.now_ns))
    def create_subscription(self, *args, **kwargs): return args
    def create_timer(self, *args, **kwargs): return args
    def create_publisher(self, *args, **kwargs): return Publisher()
    def get_logger(self): return SimpleNamespace(error=lambda message: None)
    def _publish_robust_fill(self, version, **kwargs): self.mirrors.append(version)
    def _publish_compatibility_fill(self, version): self.compatibility.append(version)
    def _sync_robust_affine(self): self.affine_syncs += 1


def envelope(msg):
    msg.schema_version, msg.run_id, msg.stream_contract_id, msg.frame_id = 1, 'test-m3', CONTRACT, 'odom'
    msg.search_epoch = 1
    return msg


def support():
    snap = envelope(CandidateSnapshot())
    snap.candidate_id = snap.objective_revision = snap.snapshot_revision = snap.detector_confirmation_sequence = 1
    snap.metric_mode = 'centroid_windows_v2'
    snap.neighborhood_radius_m, snap.centroid_tolerance_m = .5, .1
    snap.convergence_score_m, snap.convergence_score_valid = .01, True
    snap.candidate_cost_estimate, snap.candidate_cost_lower, snap.candidate_cost_upper = -1., -1.1, -.9
    snap.candidate_cost_mad, snap.candidate_cost_uncertainty = .01, .1
    snap.information_amplitude, snap.information_disagreement, snap.information_floor = .2, .01, 1e-6
    snap.informative, snap.completed_revolutions = True, 3
    set_time(snap.confirmation_stamp, 9_000_000_000)
    set_time(snap.accepted_at, 9_100_000_000)
    set_time(snap.evidence_start, 1_000_000_000)
    set_time(snap.evidence_end, 10_000_000_000)
    from builtin_interfaces.msg import Time
    snap.revolution_start = [set_time(Time(), sec*10**9) for sec in (1, 4, 7)]
    snap.revolution_end = [set_time(Time(), sec*10**9) for sec in (4, 7, 10)]
    snap.revolution_sample_start, snap.revolution_sample_end = [0,30,60], [30,60,90]
    for i in range(91):
        obs = SynchronizedObservation()
        obs.schema_version, obs.run_id, obs.stream_contract_id, obs.frame_id = 2, 'test-m3', CONTRACT, 'odom'
        obs.observation_id = obs.source_sequence = i+1
        obs.objective_revision = 1
        ns = 10**9+i*100_000_000
        obs.legacy_cost_source_timestamp_sec = ns*1e-9
        for field in ('source_stamp', 'cost_source_stamp', 'admission_stamp', 'receipt_stamp',
                      'pose_left_stamp', 'pose_right_stamp', 'encoder_left_stamp', 'encoder_right_stamp'):
            set_time(getattr(obs, field), ns)
        obs.base_x_m, obs.base_y_m = .02*math.cos(i/5), .02*math.sin(i/5)
        obs.raw_cost = -1.+.2*math.cos(i/5)
        obs.synchronized_valid = obs.raw_cost_valid = obs.sensor_transform_observed = True
        snap.observations.append(obs)
        snap.observation_filter_state.append(1)
        snap.observation_filter_stamp.append(set_time(Time(), ns))
    snap.evidence_sha256 = snapshot_sha256(snap)
    return snap


def command(sequence=1, prep=1, *, snapshot=None, generation=0, target=None):
    cmd = envelope(FillCommand())
    cmd.command_sequence, cmd.preparation_id = sequence, prep
    cmd.candidate_id = cmd.objective_revision = 1
    cmd.operation = FillCommand.PREPARE
    cmd.expected_registry_generation = generation
    cmd.snapshot = support() if snapshot is None else snapshot
    cmd.evidence_sha256 = cmd.snapshot.evidence_sha256
    cmd.return_state = 4
    set_time(cmd.expires_at, 15_100_000_000)
    if target is not None:
        cmd.redesign, cmd.return_state = True, 5
        cmd.target_fill_id, cmd.target_cluster_id, cmd.target_revision = target
    return cmd


def authorize(node, runtime, *, state=3, previous=2, epoch=1, x=0.):
    context = envelope(SearchEpochContext())
    context.search_epoch, context.valid, context.algorithm_state = epoch, True, state
    context.context_sequence = 1 if runtime.context is None else runtime.context.context_sequence+1
    set_time(context.stamp, node.now_ns)
    runtime.context_cb(context)
    msg = AlgorithmState()
    msg.algorithm_profile, msg.run_id = 'robust_gaussian_v1', 'test-m3'
    msg.state, msg.previous_state = state, previous
    msg.state_valid = msg.weights_valid = msg.run_id_valid = msg.previous_state_valid = True
    msg.sensor_weight = msg.gaussian_weight = 1.
    set_time(msg.stamp, node.now_ns)
    runtime.state_cb(msg)
    pose = Odometry()
    pose.header.frame_id, pose.pose.pose.orientation.w, pose.pose.pose.position.x = 'odom', 1., x
    set_time(pose.header.stamp, node.now_ns)
    runtime.pose_cb(pose)


def owner():
    node, worker = Node(), Worker()
    runtime = MovingFillRuntime(node, worker=worker, steady_now=lambda: node.steady_ns)
    runtime.set_timekeeper(Timekeeper(mode='sim time', start_time=0.))
    authorize(node, runtime)
    return node, worker, runtime


def prepare(node, worker, runtime, cmd=None, *, target=None):
    cmd = command() if cmd is None else cmd
    runtime.command_cb(cmd)
    assert runtime.current is not None, runtime.publisher.messages[-1].reason if runtime.publisher.messages else ''
    worker.complete(target=target)
    runtime.poll()
    assert runtime.publisher.messages[-1].result == FillResult.PREPARED, runtime.publisher.messages[-1].reason
    return cmd


def activate(runtime, cmd, sequence=2):
    act = deepcopy(cmd)
    act.operation, act.command_sequence = FillCommand.ACTIVATE, sequence
    act.prepared_sha256 = runtime.preparations[cmd.preparation_id].prepared_hash
    runtime.command_cb(act)
    return act, runtime.publisher.messages[-1]


def test_inactive_preparation_detaches_snapshot_then_single_commit_and_retries():
    node, worker, runtime = owner()
    cmd = command()
    runtime.command_cb(cmd)
    cmd.snapshot.observations[0].raw_cost = -100.
    assert worker.input.samples[0].raw_cost != -100.
    worker.complete()
    runtime.poll()
    assert node.fill_registry.generation == 0 and not node.mirrors
    assert runtime.publisher.messages[-1].fill.fill_id == 0
    assert not runtime.publisher.messages[-1].fill.active
    original = runtime.preparations[1].command
    act, result = activate(runtime, original)
    assert result.result == FillResult.ACTIVATED and result.registry_generation == 1
    assert result.committed_sha256 == result_sha256(result)
    assert node.fill_registry.history[0].fill_id == 1 and len(node.mirrors) == 1
    runtime.command_cb(act)
    assert node.fill_registry.generation == 1 and len(node.mirrors) == 1
    cancel = deepcopy(act)
    cancel.command_sequence, cancel.operation = 3, FillCommand.CANCEL
    runtime.command_cb(cancel)
    assert runtime.publisher.messages[-1].result == FillResult.ALREADY_ACTIVATED
    assert runtime.publisher.messages[-1].committed_at == result.committed_at


@pytest.mark.parametrize('event', ['cancel_running', 'cancel_prepared', 'departure', 'epoch', 'safety',
                                   'deadline', 'wall_deadline', 'stale_pose', 'conflict'])
def test_terminal_change_discards_late_worker_and_allocates_no_id(event):
    node, worker, runtime = owner()
    cmd = command()
    runtime.command_cb(cmd)
    if event == 'cancel_prepared': worker.complete(); runtime.poll()
    if event.startswith('cancel'):
        cancel = deepcopy(cmd); cancel.command_sequence = 2; cancel.operation = FillCommand.CANCEL
        runtime.command_cb(cancel)
    elif event == 'departure':
        node.now_ns += 1; authorize(node, runtime, x=1.)
    elif event == 'epoch': authorize(node, runtime, epoch=2)
    elif event == 'safety': authorize(node, runtime, state=7)
    elif event == 'deadline': node.now_ns = 15_100_000_001
    elif event == 'wall_deadline': node.steady_ns = 5_000_000_001
    elif event == 'stale_pose': node.steady_ns = 500_000_001
    elif event == 'conflict':
        altered = deepcopy(cmd); altered.reason = 'conflicting'; runtime.command_cb(altered)
    if not worker.future.done(): worker.complete()
    runtime.poll()
    assert node.fill_registry.generation == 0 and not node.mirrors and runtime.current is None
    act, result = activate(runtime, cmd, 3)
    assert result.result != FillResult.ACTIVATED


def test_activation_rechecks_freshness_after_staging_and_hashing(monkeypatch):
    node, worker, runtime = owner()
    cmd = prepare(node, worker, runtime)
    original = node.fill_registry.stage_commit
    def staging(*args, **kwargs):
        plan = original(*args, **kwargs)
        node.steady_ns = 500_000_001
        return plan
    monkeypatch.setattr(node.fill_registry, 'stage_commit', staging)
    _, result = activate(runtime, cmd)
    assert result.result == FillResult.REJECTED and node.fill_registry.generation == 0


@pytest.mark.parametrize('change', ['hash', 'generation', 'expiry', 'target', 'state'])
def test_activation_binding_changes_preserve_registry(change):
    node, worker, runtime = owner()
    cmd = prepare(node, worker, runtime)
    act = deepcopy(cmd); act.operation = FillCommand.ACTIVATE; act.command_sequence = 2
    act.prepared_sha256 = runtime.preparations[1].prepared_hash
    if change == 'hash': act.prepared_sha256 = 'wrong'
    if change == 'generation': act.expected_registry_generation = 1
    if change == 'expiry': act.expires_at.sec += 1
    if change == 'target': act.target_fill_id = 10
    if change == 'state': authorize(node, runtime, state=2)
    runtime.command_cb(act)
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    assert node.fill_registry.generation == 0


def test_registry_stages_atomically_without_consuming_ids_and_rejects_stale_plan():
    registry = FillRegistry(RegistryConfig())
    samples = (BasinSample(1.,0.,0.,0.,math.nan,False,-1.,math.nan,False,1),)
    bad = values(); bad['covariance'] = ((0.,0.),(0.,0.))
    with pytest.raises(ValueError): registry.stage_commit(bad, samples, strict=True)
    plan = registry.stage_commit(values(), samples, expected_generation=0, strict=True)
    assert registry.generation == 0 and plan.active.fill_id == 1
    registry.commit_staged(plan)
    with pytest.raises(ValueError): registry.commit_staged(plan)
    revised = registry.stage_commit(values(2.), samples, cluster_id=1,
                                    exact_target=(1,1,1), expected_generation=1, strict=True)
    assert registry.active_clusters[0].active_fill.amplitude == 1.
    registry.commit_staged(revised)
    assert registry.generation == 2 and registry.active_count == 1
    assert registry.active_clusters[0].active_fill.fill_id == 2


def test_support_conflicts_and_capacity_are_not_decimated():
    a = BasinSample(1.,0.,0.,0.,math.nan,False,-1.,math.nan,False,1)
    with pytest.raises(ValueError, match='conflict'): combine_samples((a,), (replace(a, raw_cost=-2.),), 10)
    with pytest.raises(ValueError, match='capacity'): combine_samples((a,), (replace(a, stamp_sec=2.),), 1)
    assert combine_samples((a,), (a,), 1) == (a,)


def test_actual_existing_estimator_and_designer_run_from_detached_immutable_support():
    samples = tuple(BasinSample(i*.1, .1*math.cos(i*.12), .07*math.sin(i*.12), 0.,
                              math.nan, False, -1.+.01*math.cos(i*.12)**2+.005*math.sin(i*.12)**2,
                              math.nan, False, 1) for i in range(100))
    registry = FillRegistry(RegistryConfig())
    inp = PreparationInput(samples, registry.snapshot(), EstimatorConfig(), FillDesignConfig(),
                           registry.config, 10., -1., 1., False, 4)
    result = compute_fill_proposal(inp)
    assert registry.generation == 0 and result.registry_generation == 0
    assert isinstance(dict(result.version_values)['covariance'], tuple)
    assert result.samples and dict(result.version_values)['amplitude'] > 0.


def composer(node):
    node.v2_composer = SimpleNamespace(origin_ns=0, origin_fault=False, run_id='test-m3',
        contract_id=CONTRACT, config=CONFIG, _report_fault=lambda reason: None)
    return AtomicFillActivation(node)


def test_combined_supersession_is_atomic_and_canonical_mirrors_ignored():
    node, worker, runtime = owner()
    cmd = prepare(node, worker, runtime)
    _, first = activate(runtime, cmd)
    cost = Node(); consumer = composer(cost)
    assert consumer.accept(first)
    assert set(cost.robust_terms) == {1}
    cost.robust_affine_terms[1] = {'old': True}
    authorize(node, runtime, previous=4)
    redesign = command(3,2,generation=1,target=(1,1,1))
    prepare(node, worker, runtime, redesign, target=(1,1,1))
    _, second = activate(runtime, redesign, 4)
    assert second.result == FillResult.ACTIVATED and second.has_superseded_fill
    broken = deepcopy(second); broken.registry_digest_after = 'wrong'; broken.committed_sha256 = result_sha256(broken)
    assert not consumer.accept(broken)
    assert set(cost.robust_terms) == {1} and cost.robust_affine_terms == {1: {'old': True}}
    ModifiedCost2D.robust_fill_cb(cost, second.superseded_fill)
    assert set(cost.robust_terms) == {1}
    assert consumer.accept(second)
    assert set(cost.robust_terms) == {2} and not cost.robust_affine_terms and consumer.generation == 2
    assert consumer.accept(second) and cost.affine_syncs == 2
    retry = deepcopy(second); retry.result = FillResult.ALREADY_ACTIVATED; retry.command_sequence = 5
    retry.committed_sha256 = result_sha256(retry)
    assert consumer.accept(retry) and cost.affine_syncs == 2


@pytest.mark.parametrize('change', ['skip', 'before', 'geometry', 'hash', 'stream', 'future'])
def test_atomic_consumer_rejects_whole_invalid_envelope(change):
    node, worker, runtime = owner(); cmd = prepare(node, worker, runtime)
    _, result = activate(runtime, cmd)
    cost = Node(); consumer = composer(cost)
    bad = deepcopy(result)
    if change == 'skip': bad.registry_generation = 2
    if change == 'before': bad.registry_digest_before = 'bad'
    if change == 'geometry': bad.fill.covariance_xx = -1.
    if change == 'stream': bad.run_id = 'other'
    if change == 'future': bad.committed_at.sec += 1
    if change != 'hash': bad.committed_sha256 = result_sha256(bad)
    else: bad.committed_sha256 = 'bad'
    assert not consumer.accept(bad) and not cost.robust_terms and consumer.generation == 0


def test_future_pose_keeps_mature_pose_until_clock_admits_original_receipt():
    node, worker, runtime = owner()
    cmd = prepare(node, worker, runtime)
    future = Odometry()
    future.header.frame_id, future.pose.pose.orientation.w = 'odom', 1.
    future.pose.pose.position.x = 1.
    set_time(future.header.stamp, node.now_ns+100_000_000)
    runtime.pose_cb(future)
    assert runtime._live_error(runtime.current, activation=True) == ''
    node.now_ns += 100_000_000
    assert runtime._live_error(runtime.current, activation=True) == 'candidate neighborhood departed'
    _, response = activate(runtime, cmd)
    assert response.result == FillResult.REJECTED and node.fill_registry.generation == 0


@pytest.mark.parametrize('change', ['digest', 'indices', 'duplicate', 'overflow', 'identity', 'missing_bracket'])
def test_snapshot_rejects_corruption_before_worker_submission(change):
    node, worker, runtime = owner()
    snap = support()
    if change == 'digest': snap.candidate_cost_estimate = -100.
    if change == 'indices': snap.revolution_sample_start[1] = 31
    if change == 'duplicate': snap.observations[1].observation_id = 1
    if change == 'overflow': snap.observations[1].base_x_m = math.inf
    if change == 'identity': snap.observations[1].run_id = 'other'
    if change == 'missing_bracket': snap.evidence_end.nanosec = 1
    if change != 'digest': snap.evidence_sha256 = snapshot_sha256(snap)
    runtime.command_cb(command(snapshot=snap))
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    assert not hasattr(worker, 'input') and node.fill_registry.generation == 0


def test_command_capacity_retains_tombstones(monkeypatch):
    import ros_esc.gaussian_fill_node.v2_fill_runtime as module
    assert module.MAX_COMMANDS == 4096
    monkeypatch.setattr(module, 'MAX_COMMANDS', 3)
    node, worker, runtime = owner()
    for sequence in range(1,5):
        cmd = command(sequence,sequence)
        cmd.operation = FillCommand.CANCEL
        runtime.command_cb(cmd)
    assert len(runtime.commands) == 3 and runtime.last_command_sequence == 3
    assert runtime.publisher.messages[-1].reason == 'command order or capacity'
    assert node.fill_registry.generation == 0


def test_publication_failure_after_commit_keeps_authoritative_cache(monkeypatch):
    node, worker, runtime = owner(); cmd = prepare(node, worker, runtime)
    def fail(*args, **kwargs): raise ValueError('DDS mirror failure')
    monkeypatch.setattr(node, '_publish_robust_fill', fail)
    act, result = activate(runtime, cmd)
    assert result.result == FillResult.ACTIVATED and node.fill_registry.generation == 1
    runtime.command_cb(act)
    assert runtime.publisher.messages[-1].result == FillResult.ACTIVATED


def test_changed_actual_time_origin_cannot_be_replaced_by_self_consistent_command():
    node, worker, runtime = owner(); cmd = prepare(node, worker, runtime)
    runtime.set_timekeeper(Timekeeper(mode='sim time', start_time=1.))
    assert runtime.origin_fault and runtime.current is None
    changed = deepcopy(cmd)
    changed.command_sequence, changed.preparation_id = 2,2
    set_time(changed.time_origin, 10**9)
    changed.stream_contract_id = stream_contract_id(CONFIG, 10**9)
    count = len(runtime.commands)
    runtime.command_cb(changed)
    runtime.set_timekeeper(Timekeeper(mode='sim time', start_time=0.))
    assert runtime.origin_fault and len(runtime.commands) == count and node.fill_registry.generation == 0


def test_paused_clock_duplicate_state_cannot_refresh_original_receipt():
    node, worker, runtime = owner(); prepare(node, worker, runtime)
    first = runtime.state_receipt
    node.steady_ns = 400_000_000
    runtime.state_cb(deepcopy(runtime.state))
    assert runtime.state_receipt == first
    node.steady_ns = 500_000_001
    runtime.poll()
    assert runtime.current is None and node.fill_registry.generation == 0


def test_extreme_outside_interval_bracket_cost_never_enters_raw_fit_support():
    node, worker, runtime = owner()
    baseline = runtime._input(command())
    snap = support()
    # Exact end is interpolation support only; the half-open third cycle excludes it.
    snap.observations[-1].raw_cost = -1e200
    bracket = deepcopy(snap.observations[0])
    bracket.observation_id = bracket.source_sequence = 1000
    bracket.base_x_m = 100.
    bracket.raw_cost = -1e200
    bracket.legacy_cost_source_timestamp_sec = .9
    for field in ('source_stamp', 'cost_source_stamp', 'admission_stamp', 'receipt_stamp',
                  'pose_left_stamp', 'pose_right_stamp', 'encoder_left_stamp', 'encoder_right_stamp'):
        set_time(getattr(bracket, field), 900_000_000)
    snap.observations.insert(0,bracket)
    snap.observation_filter_state.insert(0,1)
    from builtin_interfaces.msg import Time
    snap.observation_filter_stamp.insert(0,set_time(Time(),900_000_000))
    snap.revolution_sample_start = [v+1 for v in snap.revolution_sample_start]
    snap.revolution_sample_end = [v+1 for v in snap.revolution_sample_end]
    snap.evidence_sha256 = snapshot_sha256(snap)
    amended = runtime._input(command(snapshot=snap))
    assert len(amended.samples) == 90
    assert [(s.stamp_sec,s.x,s.y,s.raw_cost) for s in amended.samples] == [
        (s.stamp_sec,s.x,s.y,s.raw_cost) for s in baseline.samples]


def test_reused_preparation_id_cannot_destroy_an_accepted_commit():
    node, worker, runtime = owner(); cmd = prepare(node, worker, runtime)
    act, _ = activate(runtime, cmd)
    repeated_prepare = deepcopy(cmd); repeated_prepare.command_sequence = 3
    runtime.command_cb(repeated_prepare)
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    cancel = deepcopy(act); cancel.command_sequence = 4; cancel.operation = FillCommand.CANCEL
    runtime.command_cb(cancel)
    assert runtime.publisher.messages[-1].result == FillResult.ALREADY_ACTIVATED
    assert node.fill_registry.generation == 1


def test_old_terminal_cancel_does_not_cancel_a_different_current_preparation():
    node, worker, runtime = owner()
    first = command(); runtime.command_cb(first)
    cancel = deepcopy(first); cancel.command_sequence = 2; cancel.operation = FillCommand.CANCEL
    runtime.command_cb(cancel); worker.complete(); runtime.poll()
    second = command(3,2); runtime.command_cb(second)
    old_cancel = deepcopy(cancel); old_cancel.command_sequence = 4
    runtime.command_cb(old_cancel)
    assert runtime.current.command.preparation_id == 2
    worker.complete(); runtime.poll()
    assert runtime.current.status == FillResult.PREPARED and node.fill_registry.generation == 0


def test_hidden_lifecycle_topic_override_is_rejected_at_startup():
    node = Node(); node.params['v2_fill_command_topic'] = '/wrong/commands'
    with pytest.raises(ValueError, match='frozen contract'):
        MovingFillRuntime(node,worker=Worker())
    node = Node(); node.params['v2_fill_result_topic'] = '/wrong/results'
    with pytest.raises(ValueError, match='frozen contract'):
        composer(node)


@pytest.mark.parametrize('field,value', [
    ('candidate_cost_mad', -.01), ('candidate_cost_uncertainty', -.01),
    ('information_disagreement', -.01), ('information_floor', 0.),
    ('information_floor', -1.), ('information_amplitude', 0.), ('information_amplitude', -1.),
])
def test_malformed_signed_information_cannot_start_preparation(field, value):
    node, worker, runtime = owner()
    snap = support(); setattr(snap,field,value); snap.evidence_sha256 = snapshot_sha256(snap)
    runtime.command_cb(command(snapshot=snap))
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    assert not hasattr(worker,'input') and node.fill_registry.generation == 0


def test_dds_result_failure_after_commit_is_cached_and_successfully_retried(monkeypatch):
    node, worker, runtime = owner(); cmd = prepare(node, worker, runtime)
    publish = runtime.publisher.publish
    failed = []
    def fail_once(message):
        if message.result == FillResult.ACTIVATED and not failed:
            failed.append(True)
            raise RuntimeError('synthetic DDS publication failure')
        publish(message)
    monkeypatch.setattr(runtime.publisher,'publish',fail_once)
    act, _ = activate(runtime,cmd)
    assert failed and node.fill_registry.generation == 1 and len(node.mirrors) == 1
    assert runtime.commands[2][1].result == FillResult.ACTIVATED
    assert not any(msg.result == FillResult.ACTIVATED for msg in runtime.publisher.messages)
    runtime.command_cb(act)
    assert runtime.publisher.messages[-1].result == FillResult.ACTIVATED
    assert node.fill_registry.generation == 1 and len(node.mirrors) == 1


def test_dds_mirror_runtime_failure_preserves_commit_and_owner_responsiveness(monkeypatch):
    node, worker, runtime = owner(); cmd = prepare(node,worker,runtime)
    def fail(*args, **kwargs): raise RuntimeError('synthetic canonical DDS failure')
    monkeypatch.setattr(node,'_publish_robust_fill',fail)
    act,result = activate(runtime,cmd)
    assert result.result == FillResult.ACTIVATED and node.fill_registry.generation == 1
    runtime.command_cb(act)
    assert runtime.publisher.messages[-1].result == FillResult.ACTIVATED
    assert node.fill_registry.generation == 1
