"""Typed recurrent proof through the actual existing fill transaction owner."""
from copy import deepcopy
import math

import pytest
from ros_esc_interfaces.msg import DetectorConfirmation, FillCommand, FillResult, RecurrentFillCommand, Timekeeper

from ros_esc.gaussian_fill_node.v2_fill_runtime import MovingFillRuntime
from ros_esc.v2_lifecycle import (
    ANGULAR_PROFILES_POLICY, RECURRENT_TRAPPING_POLICY, RECURRENT_FILL_COMMAND_TOPIC,
    copy_envelope, recurrent_snapshot_sha256, snapshot_sha256,
)
from ros_esc.v2_stream import set_time, time_to_ns
from test_v2_fill_transactions import Node, Worker, authorize, command, support, CONFIG
from test_r4_stationary_recurrent_protocol import confirmation as diagnostic_fixture, ORIGIN_NS


def nomination():
    """Independent fixed wire values: local detector epoch3, supervisor epoch1."""
    diagnostic = diagnostic_fixture('circle')
    for field in ('stamp', 'receipt_stamp', 'source_stamp', 'epoch_started_at',
                  'history_start', 'history_end', 'persistence_start'):
        value = getattr(diagnostic, field)
        set_time(value, time_to_ns(value)-ORIGIN_NS)
    diagnostic.run_id, diagnostic.source_pose_topic = 'test-m3', CONFIG['pose_topic']
    diagnostic.search_epoch = 3
    diagnostic.center_x_m = diagnostic.center_y_m = 0.
    diagnostic.arc_center_x_m = diagnostic.arc_center_y_m = [0., 0.]
    confirmation = DetectorConfirmation()
    copy_envelope(confirmation, support())
    confirmation.context_sequence = confirmation.confirmation_sequence = 1
    confirmation.detector_local_epoch = 3
    confirmation.metric_mode = 'recurrent_geometry_v3'
    confirmation.history_kind, confirmation.source_stamp_kind = 'recurrent_geometry', 'pose_input'
    confirmation.valid = confirmation.convergence_score_valid = True
    confirmation.convergence_score_m = diagnostic.score_m
    for field in ('stamp', 'epoch_started_at', 'history_start', 'history_end'):
        setattr(confirmation, field, deepcopy(getattr(diagnostic, field)))
    confirmation.source_stamp = deepcopy(diagnostic.history_end)
    return confirmation, diagnostic


def selected_snapshot():
    s = support()
    s.metric_mode = 'recurrent_geometry_v3'
    s.convergence_score_m = 0.
    s.pretrigger_revolutions, s.verification_revolutions = 0, 3
    s.candidate_cost_estimate = s.candidate_cost_lower = s.candidate_cost_upper = -1.
    s.candidate_cost_mad = s.candidate_cost_uncertainty = 0.
    s.information_amplitude = s.information_disagreement = 0.
    s.informative = False
    for field, ns in (('confirmation_stamp', 60_000_000_000), ('accepted_at', 60_100_000_000),
                      ('stamp', 70_100_000_000), ('evidence_start', 61_000_000_000),
                      ('evidence_end', 70_000_000_000)):
        set_time(getattr(s, field), ns)
    for value in (*s.revolution_start, *s.revolution_end):
        set_time(value, time_to_ns(value)+60_000_000_000)
    for i, observation in enumerate(s.observations):
        for field in observation.get_fields_and_field_types():
            value = getattr(observation, field)
            if hasattr(value, 'sec') and field not in ('time_origin', 'stamp'):
                set_time(value, time_to_ns(value)+60_000_000_000)
        observation.legacy_cost_source_timestamp_sec += 60.
        observation.sensor_world_phase_rad = i*math.tau/30
        observation.raw_cost = -1.
        s.observation_filter_state[i] = 2
        set_time(s.observation_filter_stamp[i], time_to_ns(observation.admission_stamp))
    return s


def wrapper():
    msg = RecurrentFillCommand(schema_version=1, policy_id=RECURRENT_TRAPPING_POLICY)
    msg.confirmation, msg.diagnostic = nomination()
    msg.command = command(snapshot=selected_snapshot())
    set_time(msg.command.stamp, 70_100_000_000)
    set_time(msg.command.expires_at, 75_100_000_000)
    rehash(msg)
    return msg


def rehash(msg):
    digest = recurrent_snapshot_sha256(msg.command.snapshot, msg)
    msg.command.snapshot.evidence_sha256 = msg.command.evidence_sha256 = digest


def selected_owner():
    node, worker = Node(), Worker()
    node.now_ns = 70_100_000_000
    node.params.update(v2_verification_evidence_policy=RECURRENT_TRAPPING_POLICY,
        v2_verification_motion_mode='centered_tracking_v1', convergence_metric_mode='recurrent_geometry_v3',
        continuous_search_mode='rolling_gesc_v2', v2_fill_command_topic=RECURRENT_FILL_COMMAND_TOPIC,
        candidate_cost_mad_scale=3.)
    runtime = MovingFillRuntime(node, worker=worker, steady_now=lambda: node.steady_ns)
    runtime.set_timekeeper(Timekeeper(mode='sim time', start_time=0.))
    authorize(node, runtime)
    return node, worker, runtime


def prepared():
    node, worker, runtime = selected_owner()
    msg = wrapper()
    runtime.recurrent_command_cb(msg)
    assert runtime.current is not None, [r.reason for r in runtime.publisher.messages]
    worker.complete(); runtime.poll()
    assert runtime.publisher.messages[-1].result == FillResult.PREPARED
    return node, worker, runtime, msg


def operation(runtime, msg, code, sequence):
    result = deepcopy(msg)
    result.command.operation, result.command.command_sequence = code, sequence
    result.command.prepared_sha256 = runtime.preparations[1].prepared_hash
    return result


def test_uninformative_raw_profiles_prepare_commit_and_retry_with_original_proof():
    node, worker, runtime, msg = prepared()
    assert runtime.command_subscription[0] is RecurrentFillCommand
    assert runtime.command_subscription[1] == RECURRENT_FILL_COMMAND_TOPIC
    assert not msg.command.snapshot.informative and len(worker.input.samples) == 90
    assert msg.diagnostic.source_stamp != msg.confirmation.source_stamp
    assert msg.diagnostic.search_epoch != msg.confirmation.search_epoch
    active = operation(runtime, msg, FillCommand.ACTIVATE, 2)
    runtime.recurrent_command_cb(active)
    assert runtime.publisher.messages[-1].result == FillResult.ACTIVATED
    assert node.fill_registry.generation == 1 and len(node.mirrors) == 1
    runtime.recurrent_command_cb(active)
    cancelled = operation(runtime, msg, FillCommand.CANCEL, 3)
    runtime.recurrent_command_cb(cancelled)
    assert runtime.publisher.messages[-1].result == FillResult.ALREADY_ACTIVATED
    assert node.fill_registry.generation == 1 and len(node.mirrors) == 1


@pytest.mark.parametrize('defect', ['missing', 'policy', 'proof_center', 'proof_epoch', 'proof_local_epoch',
    'proof_sequence', 'proof_source', 'proof_not_confirmed', 'proof_future', 'hash', 'snapshot_center',
    'snapshot_sequence', 'snapshot_acceptance', 'raw_positive', 'raw_summary', 'raw_baseline',
    'raw_phase', 'raw_gap', 'raw_departure', 'raw_informative_lie'])
def test_untrusted_or_bad_raw_nomination_never_reaches_worker(defect):
    node, worker, runtime = selected_owner(); msg = wrapper()
    if defect == 'missing':
        runtime.command_cb(msg.command)
    else:
        if defect == 'policy': msg.policy_id = ANGULAR_PROFILES_POLICY
        elif defect == 'proof_center': msg.diagnostic.center_x_m += .01
        elif defect == 'proof_epoch': msg.confirmation.search_epoch += 1
        elif defect == 'proof_local_epoch': msg.diagnostic.search_epoch += 1
        elif defect == 'proof_sequence': msg.confirmation.confirmation_sequence += 1
        elif defect == 'proof_source': msg.confirmation.source_stamp = deepcopy(msg.diagnostic.source_stamp)
        elif defect == 'proof_not_confirmed': msg.diagnostic.confirmed = False
        elif defect == 'proof_future': set_time(msg.diagnostic.stamp, 60_200_000_000)
        elif defect == 'hash': msg.command.evidence_sha256 = 'a'*64
        elif defect == 'snapshot_center': msg.command.snapshot.center_x_m += .01
        elif defect == 'snapshot_sequence': msg.command.snapshot.detector_confirmation_sequence += 1
        elif defect == 'snapshot_acceptance': set_time(msg.command.snapshot.accepted_at, 60_600_000_000)
        elif defect == 'raw_positive': msg.command.snapshot.candidate_cost_upper = .1
        elif defect == 'raw_summary': msg.command.snapshot.candidate_cost_lower -= .1
        elif defect == 'raw_baseline':
            for obs in msg.command.snapshot.observations: obs.raw_cost = .1
        elif defect == 'raw_phase': msg.command.snapshot.observations[30].sensor_world_phase_rad -= .5
        elif defect == 'raw_gap':
            msg.command.snapshot.observations[3].source_stamp = deepcopy(msg.command.snapshot.observations[2].source_stamp)
        elif defect == 'raw_departure': msg.command.snapshot.observations[10].base_x_m = 2.
        elif defect == 'raw_informative_lie': msg.command.snapshot.informative = True
        if defect not in ('policy', 'hash'): rehash(msg)
        runtime.recurrent_command_cb(msg)
    assert runtime.current is None and not hasattr(worker, 'future')
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    assert node.fill_registry.generation == 0


@pytest.mark.parametrize('code', [FillCommand.ACTIVATE, FillCommand.CANCEL])
@pytest.mark.parametrize('same_sequence', [False, True])
def test_changed_certificate_cannot_activate_cancel_or_replay(code, same_sequence):
    node, worker, runtime, msg = prepared()
    changed = operation(runtime, msg, code, 1 if same_sequence else 2)
    changed.diagnostic.reset_reason = 'substituted original evidence'
    runtime.recurrent_command_cb(changed)
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    assert node.fill_registry.generation == 0
    if same_sequence:
        assert runtime.current is None
    else:
        assert runtime.current is runtime.preparations[1]


def test_original_proof_and_command_receipts_are_detached_and_not_renewed():
    node, worker, runtime = selected_owner(); msg = wrapper()
    runtime.recurrent_command_cb(msg)
    original = deepcopy(msg); pending = runtime.current
    deadline = pending.wall_expires_ns; fingerprint = deepcopy(pending.proof_payload)
    msg.diagnostic.arc_radius_m[0] = .4
    msg.command.snapshot.observations[0].raw_cost = -99.
    assert pending.proof_payload == fingerprint and worker.input.samples[0].raw_cost == -1.
    node.steady_ns += 100_000_000
    runtime.recurrent_command_cb(original)
    assert pending.wall_expires_ns == deadline and pending.proof_payload == fingerprint
    worker.complete(); runtime.poll()
    assert runtime.publisher.messages[-1].result == FillResult.PREPARED


@pytest.mark.parametrize('defect', ['cancel', 'deadline', 'steady', 'pose', 'epoch', 'failsafe'])
def test_existing_precommit_authority_still_discards_selected_worker(defect):
    node, worker, runtime = selected_owner(); msg = wrapper()
    runtime.recurrent_command_cb(msg)
    assert runtime.current is not None
    if defect == 'cancel': runtime.recurrent_command_cb(operation(runtime, msg, FillCommand.CANCEL, 2))
    elif defect == 'deadline': node.now_ns = 75_100_000_001
    elif defect == 'steady': node.steady_ns = 5_000_000_001
    elif defect == 'pose': node.now_ns += 1; authorize(node, runtime, x=2.)
    elif defect == 'epoch': authorize(node, runtime, epoch=2)
    elif defect == 'failsafe': authorize(node, runtime, state=7)
    worker.complete(); runtime.poll()
    assert node.fill_registry.generation == 0 and runtime.current is None
    assert runtime.publisher.messages[-1].result != FillResult.PREPARED


def test_default_owner_rejects_low_amplitude_even_with_legacy_valid_hash():
    from test_v2_fill_transactions import owner
    node, worker, runtime = owner(); msg = command()
    msg.snapshot.informative = False
    msg.snapshot.evidence_sha256 = snapshot_sha256(msg.snapshot)
    msg.evidence_sha256 = msg.snapshot.evidence_sha256
    runtime.command_cb(msg)
    assert runtime.publisher.messages[-1].result == FillResult.REJECTED
    assert runtime.current is None and not hasattr(worker, 'future')


def test_actual_gaussian_constructor_selects_wrapper_subscription(monkeypatch):
    import rclpy
    from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
    from test_r3_recurrent_startup import RECORDED
    monkeypatch.setenv('ROS_DOMAIN_ID', '219')
    monkeypatch.setenv('ROS_LOCALHOST_ONLY', '1')
    rclpy.init(args=RECORDED['gaussian_fill_node']+[
        '-p', 'v2_verification_evidence_policy:=recurrent_trapping_v1',
        '-p', 'v2_verification_motion_mode:=centered_tracking_v1',
        '-p', 'v2_fill_command_topic:='+RECURRENT_FILL_COMMAND_TOPIC])
    node = None
    try:
        node = GaussianFill()
        assert node.verification_evidence_policy == RECURRENT_TRAPPING_POLICY
        assert node.v2_fill.command_subscription.topic_name == RECURRENT_FILL_COMMAND_TOPIC
        assert node.get_parameter('candidate_cost_mad_scale').value == 3.
    finally:
        if node is not None: node.destroy_node()
        rclpy.try_shutdown()
