"""Finite serialized-wire lifecycle audits; no Gazebo or full-owner DDS claim."""

from copy import deepcopy
import math
from types import SimpleNamespace

import pytest
from nav_msgs.msg import Odometry
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import (
    AlgorithmEvent, AlgorithmState, CandidateSnapshot, CentroidConvergenceDiagnostics, DetectorConfirmation,
    FillCommand, FillResult, GaussianFill, GescDirectionDiagnostics,
    PdeHistoryEvidence, SearchEpochContext, SourceSampleProvenance,
    StampedFloat64MultiArray, SynchronizedObservation, Timekeeper,
)
from ros_esc.experiment_recording.v2_lifecycle_validation import TOPICS, lifecycle_stream_errors
from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor
from ros_esc.v2_lifecycle import (
    fill_registry_digest, hash_payload, message_payload, result_sha256, snapshot_sha256,
)
from ros_esc.v2_stream import set_time, stream_contract_id
from test_v2_stream import descriptor


def time_at(value):
    from builtin_interfaces.msg import Time
    result = Time()
    set_time(result, round(value*1e9))
    return result


def fixture(metric='centroid_windows_v2', *, activated=True):
    config = descriptor(2)
    identity = {'run_id': 'recording-test', 'stream_config': config}
    def wire(cls, at, **values):
        msg = cls(**values)
        msg.schema_version = 2 if cls in (SynchronizedObservation, SourceSampleProvenance, GescDirectionDiagnostics) else 1
        msg.run_id, msg.frame_id = identity['run_id'], config['frame_id']
        msg.stream_contract_id = stream_contract_id(config, 0)
        msg.stamp = time_at(at)
        return msg
    context = wire(SearchEpochContext, 6., search_epoch=1, context_sequence=1, algorithm_state=1, valid=True)
    confirmation = wire(DetectorConfirmation, 6.01, search_epoch=1, context_sequence=1,
        confirmation_sequence=1, detector_local_epoch=7, metric_mode=metric,
        source_stamp_kind='pose_input', valid=True)
    confirmation.source_stamp = confirmation.history_end = time_at(6.)
    if metric in ('centroid_windows_v2', 'centroid_two_block_v2'):
        confirmation.history_kind = 'centroid_windows'
        confirmation.convergence_score_valid = True
    else:
        confirmation.history_kind = 'pde_input_support'
        confirmation.legacy_r_mean_valid = True
        confirmation.legacy_snapshot = [0., 0., 0., 0., 0., 0., 0., 0.]
    messages = {config['timekeeper_topic']: [(0, Timekeeper(mode='sim time', start_time=0.))],
                TOPICS['v2_search_epoch']: [(1, context)],
                TOPICS['v2_detector_confirmation']: [(2, confirmation)]}
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    diagnostics, provenance, poses = [], [], []
    for index in range(181):
        t = index*.05
        obs = wire(SynchronizedObservation, t+.01,
                   source_sequence=index+1, observation_id=index+1, objective_revision=1,
                   raw_cost_valid=True, augmented_cost_valid=True, synchronized_valid=True,
                   sensor_transform_observed=True)
        for name in ('source_stamp', 'cost_source_stamp', 'pose_left_stamp', 'pose_right_stamp',
                     'encoder_left_stamp', 'encoder_right_stamp', 'receipt_stamp',
                     'oldest_receipt_stamp', 'admission_stamp'):
            setattr(obs, name, time_at(t))
        obs.legacy_cost_source_timestamp_sec = t
        obs.sensor_world_phase_rad = 2*math.pi*t/3
        obs.raw_cost = -2.+.5*math.cos(obs.sensor_world_phase_rad)
        obs.augmented_cost = obs.raw_cost
        state = 1 if t < 6 else 2
        core.add(obs, state, round((t+.01)*1e9))
        diag = wire(GescDirectionDiagnostics, t+.01, diagnostic_sequence=index+1,
                    observation=deepcopy(obs), algorithm_state=state,
                    algorithm_state_valid=True, output_valid=True)
        diagnostics.append((index, diag))
        prov = wire(SourceSampleProvenance, t, source_sequence=index+1,
                    legacy_cost_source_timestamp_sec=t, model_input_stamp_valid=True,
                    sensor_transform_valid=True, channel_count=1)
        prov.model_input_stamp = prov.cost_publication_stamp = time_at(t)
        provenance.append((index, prov))
        pose = Odometry(); pose.header.stamp = time_at(t); pose.header.frame_id = config['frame_id']
        pose.pose.pose.orientation.w = 1.
        poses.append((index, pose))
    evidence = core.evaluate((0., 0.), .5, .1, 6_000_000_000)
    assert evidence.ready
    publications = []
    host = SimpleNamespace(now=lambda: 9_020_000_000, center=lambda candidate:(0., 0.), radius=.5, epsilon=.1,
                           published_snapshots={}, snapshot_publisher=SimpleNamespace(publish=publications.append))
    candidate = SimpleNamespace(confirmation=confirmation, candidate_id=1, accepted_ns=6_020_000_000)
    snap = MovingSupervisor.snapshot(host, candidate, evidence)
    assert isinstance(snap, CandidateSnapshot)
    prepare = wire(FillCommand, 9.04, search_epoch=1, candidate_id=1, objective_revision=1,
        operation=FillCommand.PREPARE, command_sequence=1, preparation_id=1,
        evidence_sha256=snap.evidence_sha256, snapshot=snap, return_state=4)
    prepare.expires_at = time_at(14.04)
    prepared = response(prepare, FillResult.PREPARED, 9.1)
    prepared.prepared_sha256 = 'a'*64
    prepared.prepared_at = time_at(9.1)
    prepared.committed_sha256 = result_sha256(prepared)
    activate = deepcopy(prepare); activate.operation = FillCommand.ACTIVATE
    activate.command_sequence = 2; activate.stamp = time_at(9.2)
    activate.prepared_sha256 = prepared.prepared_sha256
    result = response(activate, FillResult.ACTIVATED, 9.25)
    result.prepared_at = deepcopy(prepared.prepared_at)
    result.committed_at = time_at(9.25)
    result.registry_generation = 1
    result.fill = GaussianFill(fill_id=1, cluster_id=1, revision=1,
        amplitude=.4, covariance_xx=.2, covariance_yy=.2,
        active=True, covariance_valid=True, frame_id=config['frame_id'])
    result.fill.stamp = deepcopy(result.committed_at)
    result.registry_digest_before = fill_registry_digest([])
    result.registry_digest_after = fill_registry_digest([result.fill])
    result.committed_sha256 = result_sha256(result)
    messages[TOPICS['v2_direction_diagnostics']] = diagnostics
    messages[TOPICS['v2_candidate_snapshots']] = [(2, snap)]
    messages[config['provenance_topic']] = provenance
    messages[config['pose_topic']] = poses
    messages[TOPICS['v2_fill_commands']] = [(3, prepare), (4, activate)] if activated else [(3, prepare)]
    messages[TOPICS['v2_fill_results']] = [(5, prepared), (6, result)] if activated else [(5, prepared)]
    if activated:
        messages[TOPICS['gaussian_fills']] = [(0, deepcopy(result.fill))]  # bag order deliberately before authority
    if metric in ('centroid_windows_v2', 'centroid_two_block_v2'):
        diag = CentroidConvergenceDiagnostics(run_id=identity['run_id'], confirmed=True,
            metric_valid=True, metric_mode=metric)
        diag.history_end = time_at(6.)
        messages[TOPICS['centroid_convergence_diagnostics']] = [(2, diag)]
    else:
        history = wire(PdeHistoryEvidence, 6., search_epoch=1, context_sequence=1, history_sequence=1, valid=True)
        history.input_end = history.latest_input_receipt = time_at(6.)
        history.history = StampedFloat64MultiArray(timestamp=6., data=[0., 0.]*6)
        history.history_sha256 = hash_payload(message_payload(history, exclude=('stamp', 'history_sha256')))
        messages[TOPICS['v2_pde_history_evidence']] = [(2, history)]
        messages[TOPICS['convergence_status']] = [(2, StampedFloat64MultiArray(data=list(confirmation.legacy_snapshot)))]
    return messages, identity, prepare, prepared, activate, result


def response(command, outcome, at):
    result = FillResult()
    for name in ('schema_version', 'time_origin', 'run_id', 'stream_contract_id', 'frame_id',
                 'search_epoch', 'candidate_id', 'objective_revision', 'command_sequence',
                 'preparation_id', 'expected_registry_generation', 'evidence_sha256',
                 'prepared_sha256', 'expires_at', 'return_state'):
        setattr(result, name, deepcopy(getattr(command, name)))
    result.stamp = time_at(at)
    result.result = outcome
    result.committed_sha256 = result_sha256(result)
    return result


def check(data):
    return lifecycle_stream_errors(data[0], data[1])


def centered_fixture(*, admission_ns=13_020_000_000, publication_ns=24_020_000_000):
    """Real recorded support may precede the later centered collection allowance."""
    data = fixture(activated=False)
    messages = data[0]
    for alias in ('v2_fill_commands', 'v2_fill_results', 'gaussian_fills'):
        messages.pop(TOPICS[alias], None)
    snap = messages[TOPICS['v2_candidate_snapshots']][0][1]
    set_time(snap.stamp, publication_ns)
    snap.evidence_sha256 = snapshot_sha256(snap)
    admission = AlgorithmEvent(event_type=12, state=2, state_name='VERIFY_EXTREMUM',
        state_valid=True, detail='moving verification collection admitted',
        value_names=['candidate_id', 'search_epoch'], values=[1., 1.])
    set_time(admission.stamp, admission_ns)
    messages[TOPICS['algorithm_events']] = [(1000, admission)]
    add_centered_guidance(data, publication_ns=9_020_000_000)
    return data


def add_centered_guidance(data, *, publication_ns, design_command=None):
    from ros_esc_interfaces.msg import VerificationGuidance
    messages, identity = data[:2]
    event = messages[TOPICS['algorithm_events']][0][1]
    admission_ns = event.stamp.sec*1_000_000_000+event.stamp.nanosec
    admitted = publication_ns >= admission_ns
    deadline = min(admission_ns+12_000_000_000, 26_020_000_000) if admitted else 14_020_000_000
    state = AlgorithmState(run_id=identity['run_id'], run_id_valid=True,
        algorithm_profile='robust_gaussian_v1', state=3 if design_command else 2,
        state_name='DESIGN_OR_MERGE_FILL' if design_command else 'VERIFY_EXTREMUM',
        state_valid=True, previous_state=2 if design_command else 1, previous_state_valid=True)
    set_time(state.stamp, publication_ns)
    guide = VerificationGuidance(schema_version=2, run_id=identity['run_id'],
        publication_sequence=len(messages.get(TOPICS['v2_verification_guidance'], []))+1,
        state_sha256=hash_payload(message_payload(state)),
        stream_contract_id=stream_contract_id(identity['stream_config'], 0),
        frame_id=identity['stream_config']['frame_id'], mode='centered_tracking_v1',
        search_epoch=1, candidate_id=1, algorithm_state=state.state,
        collection_started=admitted, center_x_m=0., center_y_m=0.,
        linear_x_mps=.03, angular_z_radps=.1, valid=True, reason='centered_tracking')
    for field in ('stamp', 'state_stamp'):
        set_time(getattr(guide, field), publication_ns)
    set_time(guide.pose_stamp, publication_ns-20_000_000)
    set_time(guide.accepted_at, 6_020_000_000)
    set_time(guide.collection_admitted_at, admission_ns if admitted else 0)
    set_time(guide.verification_expires_at, deadline)
    guide.command_expires_at = deepcopy(design_command.expires_at) if design_command else time_at(deadline/1e9)
    pose = Odometry()
    pose.header.stamp = deepcopy(guide.pose_stamp)
    pose.header.frame_id = guide.frame_id
    pose.pose.pose.orientation.w = 1.
    messages[identity['stream_config']['pose_topic']].append((3000, pose))
    messages.setdefault(TOPICS['algorithm_state'], []).append((3000, state))
    messages.setdefault(TOPICS['v2_verification_guidance'], []).append((3000, guide))
    return guide, state


def check_centered(data):
    return lifecycle_stream_errors(data[0], data[1],
        moving_verification_mode='centered_tracking_v1')


@pytest.mark.parametrize('metric', ['centroid_windows_v2', 'pde_mean_v1'])
def test_real_wire_roundtrip_complete_lifecycle_and_cross_topic_reorder(metric):
    data = fixture(metric)
    for topic, records in data[0].items():
        data[0][topic] = [(stamp, deserialize_message(serialize_message(message), type(message)))
                          for stamp, message in records]
    errors, metrics = check(data)
    assert errors == []
    assert metrics['counts']['unique_commits'] == 1
    assert metrics['preparations'][0]['pretrigger_revolutions'] == 2
    assert metrics['acknowledgements'][0]['first_direction_stamp_ns'] is None


def test_quiet_run_needs_epoch_but_no_candidate_or_event_occurrence():
    messages, identity, *_ = fixture()
    messages = {key: value for key, value in messages.items()
                if key in (identity['stream_config']['timekeeper_topic'], TOPICS['v2_search_epoch'])}
    assert lifecycle_stream_errors(messages, identity)[0] == []
    del messages[TOPICS['v2_search_epoch']]
    assert 'missing authoritative epoch' in ';'.join(lifecycle_stream_errors(messages, identity)[0])


def test_pde_original_receipt_before_origin_is_allowed_only_with_fresh_source_support():
    config = descriptor(2)
    identity = {'run_id': 'receipt-before-origin', 'stream_config': config}
    shared = dict(schema_version=1, run_id=identity['run_id'], frame_id=config['frame_id'],
                  stream_contract_id=stream_contract_id(config, 10_000_000_000),
                  time_origin=time_at(10.), stamp=time_at(10.), search_epoch=1,
                  context_sequence=1, valid=True)
    context = SearchEpochContext(**shared, started_at=time_at(10.), algorithm_state=1)
    history = PdeHistoryEvidence(**shared, epoch_started_at=time_at(10.),
                                history_sequence=1, input_start=time_at(10.),
                                input_end=time_at(10.), latest_input_receipt=time_at(9.9),
                                history=StampedFloat64MultiArray(timestamp=10., data=[1.,2.]))
    history.history_sha256 = hash_payload(message_payload(history, exclude=('stamp','history_sha256')))
    pose = Odometry(); pose.header.stamp = time_at(10.); pose.header.frame_id = config['frame_id']
    messages = {
        config['timekeeper_topic']: [(0, Timekeeper(mode='sim time', start_time=10.))],
        config['pose_topic']: [(1, pose)],
        TOPICS['v2_search_epoch']: [(1, context)],
        TOPICS['v2_pde_history_evidence']: [(2, history)],
    }
    assert lifecycle_stream_errors(messages, identity)[0] == []
    history.latest_input_receipt = time_at(9.4)
    history.history_sha256 = hash_payload(message_payload(history, exclude=('stamp','history_sha256')))
    assert any('freshness' in error for error in lifecycle_stream_errors(messages, identity)[0])


def test_invalid_unbound_startup_context_is_observable_not_authority():
    data = fixture()
    context = deepcopy(data[0][TOPICS['v2_search_epoch']][0][1])
    context.context_sequence = 1; context.valid = False; context.stream_contract_id = ''
    data[0][TOPICS['v2_search_epoch']] = [(0, context)]
    for name in ('v2_detector_confirmation', 'v2_candidate_snapshots', 'v2_fill_commands', 'v2_fill_results', 'gaussian_fills'):
        data[0].pop(TOPICS[name], None)
    assert check(data)[0] == []


@pytest.mark.parametrize('mutation, expected', [
    (lambda d: setattr(d[2], 'evidence_sha256', 'b'*64), 'matching published candidate snapshot'),
    (lambda d: setattr(d[2].snapshot, 'center_x_m', .1), 'snapshot evidence hash'),
    (lambda d: setattr(d[4], 'expected_registry_generation', 1), 'frozen preparation binding'),
    (lambda d: setattr(d[4], 'prepared_sha256', 'b'*64), 'prepared hash differs'),
    (lambda d: setattr(d[5], 'registry_generation', 2), 'result hash differs'),
    (lambda d: setattr(d[3].fill, 'fill_id', 1), 'result hash differs'),
    (lambda d: d[0].pop(TOPICS['v2_direction_diagnostics']), 'recorded filter'),
    (lambda d: d[0].pop(d[1]['stream_config']['provenance_topic']), 'source provenance missing'),
    (lambda d: d[0].pop(TOPICS['centroid_convergence_diagnostics']), 'matching diagnostic'),
])
def test_mutated_wire_claims_fail(mutation, expected):
    data = fixture(); mutation(data)
    assert expected in ';'.join(check(data)[0])


def rehash_snapshot(data):
    data[2].snapshot.evidence_sha256 = snapshot_sha256(data[2].snapshot)
    data[2].evidence_sha256 = data[2].snapshot.evidence_sha256


@pytest.mark.parametrize('mutate, expected', [
    (lambda s: setattr(s, 'observation_filter_state', [2]*len(s.observations)), 'recorded filter'),
    (lambda s: setattr(s.observations[0], 'raw_cost', -20.), 'recorded filter'),
    (lambda s: setattr(s, 'revolution_sample_end', [61, 120, 180]), 'half-open actual'),
    (lambda s: setattr(s, 'accepted_at', time_at(7.)), 'acceptance/publication'),
    (lambda s: setattr(s, 'information_amplitude', 0.), 'informative negative-cost'),
    (lambda s: setattr(s, 'pretrigger_revolutions', 1), 'three-cycle counts'),
])
def test_rehashed_but_unsupported_snapshot_rejected(mutate, expected):
    data = fixture(activated=False)
    mutate(data[2].snapshot); rehash_snapshot(data)
    assert expected in ';'.join(check(data)[0])


def test_identical_retries_count_one_commit_and_do_not_refresh_first_provenance():
    data = fixture()
    for name in ('v2_fill_commands', 'v2_fill_results'):
        data[0][TOPICS[name]] += deepcopy(data[0][TOPICS[name]])
    diagnostic = deepcopy(data[0][TOPICS['v2_direction_diagnostics']][0][1])
    diagnostic.stamp = time_at(10.); diagnostic.algorithm_state = 5
    data[0][TOPICS['v2_direction_diagnostics']].append((1000, diagnostic))
    errors, metrics = check(data)
    assert errors == [] and metrics['counts']['unique_commits'] == 1


def test_conflicting_command_reuse_is_not_idempotent():
    data = fixture()
    duplicate = deepcopy(data[2]); duplicate.reason = 'changed'
    data[0][TOPICS['v2_fill_commands']].append((100, duplicate))
    assert 'conflicting command sequence' in ';'.join(check(data)[0])


def test_reordered_new_command_sequence_is_not_sorted_away():
    data = fixture()
    data[0][TOPICS['v2_fill_commands']].reverse()
    assert check(data)[0]


@pytest.mark.parametrize('notice_sequence', [1, 9999])
def test_revoked_source_cannot_back_preparation(notice_sequence):
    data = fixture()
    prov = deepcopy(data[0][data[1]['stream_config']['provenance_topic']][0][1])
    prov.model_input_stamp_valid = False
    prov.source_sequence = notice_sequence
    data[0][data[1]['stream_config']['provenance_topic']].append((999, prov))
    assert 'source provenance missing or revoked' in ';'.join(check(data)[0])


def test_prepared_never_consumes_or_publishes_a_fill():
    data = fixture(activated=False)
    data[3].fill.fill_id = 1
    data[3].committed_sha256 = result_sha256(data[3])
    assert 'PREPARED allocated' in ';'.join(check(data)[0])


def test_combined_activation_digest_is_recomputed_not_trusted():
    data = fixture()
    data[5].registry_digest_after = 'd'*64
    data[5].committed_sha256 = result_sha256(data[5])
    assert 'after digest' in ';'.join(check(data)[0])


def test_canonical_mirror_alone_cannot_activate():
    data = fixture(activated=False)
    data[0][TOPICS['gaussian_fills']] = [(0, deepcopy(data[5].fill))]
    assert 'lacks matching typed activation authority' in ';'.join(check(data)[0])


def test_cancel_before_commit_terminal_and_after_commit_already_activated():
    data = fixture()
    cancel = deepcopy(data[4]); cancel.operation = FillCommand.CANCEL; cancel.command_sequence = 3
    cancel.stamp = time_at(9.3)
    already = deepcopy(data[5]); already.command_sequence = 3
    already.result = FillResult.ALREADY_ACTIVATED; already.stamp = time_at(9.31)
    already.committed_sha256 = result_sha256(already)
    data[0][TOPICS['v2_fill_commands']].append((7, cancel))
    data[0][TOPICS['v2_fill_results']].append((8, already))
    assert check(data)[0] == []
    cancel.stamp = time_at(9.21)
    cancelled = response(cancel, FillResult.CANCELLED, 9.22)
    data[0][TOPICS['v2_fill_results']].insert(1, (5, cancelled))
    assert 'commit follows terminal' in ';'.join(check(data)[0])


def test_cancel_published_before_commit_is_not_assumed_received_before_commit():
    data = fixture()
    cancel = deepcopy(data[4]); cancel.operation = FillCommand.CANCEL; cancel.command_sequence = 3
    cancel.stamp = time_at(9.21)
    already = deepcopy(data[5]); already.command_sequence = 3; already.result = FillResult.ALREADY_ACTIVATED
    already.stamp = time_at(9.3); already.committed_sha256 = result_sha256(already)
    data[0][TOPICS['v2_fill_commands']].append((0, cancel))
    data[0][TOPICS['v2_fill_results']].append((1, already))
    assert check(data)[0] == []


def test_pde_hash_support_and_explicit_invalidation():
    data = fixture('pde_mean_v1')
    history = data[0][TOPICS['v2_pde_history_evidence']][0][1]
    history.history.data[0] = .2
    assert 'PDE evidence hash' in ';'.join(check(data)[0])
    data = fixture('pde_mean_v1')
    invalid = deepcopy(data[0][TOPICS['v2_pde_history_evidence']][0][1])
    invalid.valid = False; invalid.history_sequence = 2; invalid.history.data = []
    invalid.history.header = 'V2_INVALID: conflicting_pose'
    invalid.stamp = time_at(6.005)
    invalid.history_sha256 = hash_payload(message_payload(invalid, exclude=('stamp', 'history_sha256')))
    data[0][TOPICS['v2_pde_history_evidence']].append((3, invalid))
    assert 'matching unrevoked PDE support' in ';'.join(check(data)[0])
    data[0].pop(TOPICS['v2_detector_confirmation'])
    data[0].pop(TOPICS['v2_candidate_snapshots'])
    data[0].pop(TOPICS['v2_fill_commands']); data[0].pop(TOPICS['v2_fill_results'])
    data[0].pop(TOPICS['gaussian_fills'])
    assert check(data)[0] == []


@pytest.mark.parametrize('which', ['context', 'confirmation'])
def test_lifecycle_schema_is_one_not_nested_stream_schema_two(which):
    data = fixture()
    alias = 'v2_search_epoch' if which == 'context' else 'v2_detector_confirmation'
    data[0][TOPICS[alias]][0][1].schema_version = 2
    assert 'schema/run/frame' in ';'.join(check(data)[0])


def test_manifest_topic_overrides_are_used():
    data = fixture()
    overrides = {alias: '/relocated/'+alias for alias in TOPICS}
    messages = {next((overrides[a] for a,t in TOPICS.items() if t == topic), topic): values
                for topic, values in data[0].items()}
    assert lifecycle_stream_errors(messages, data[1], topics=overrides)[0] == []


def add_redesign(data):
    prepare = deepcopy(data[2]); prepare.command_sequence = 3; prepare.preparation_id = 2
    prepare.expected_registry_generation = 1; prepare.redesign = True; prepare.return_state = 5
    prepare.target_fill_id = prepare.target_cluster_id = prepare.target_revision = 1
    prepare.snapshot.snapshot_revision = 2
    prepare.snapshot.stamp = time_at(10.)
    prepare.snapshot.evidence_sha256 = snapshot_sha256(prepare.snapshot)
    prepare.evidence_sha256 = prepare.snapshot.evidence_sha256
    prepare.stamp = time_at(10.01); prepare.expires_at = time_at(14.)
    prepared = response(prepare, FillResult.PREPARED, 10.1)
    prepared.prepared_sha256 = 'b'*64; prepared.prepared_at = time_at(10.1)
    prepared.registry_generation = 1
    prepared.committed_sha256 = result_sha256(prepared)
    activate = deepcopy(prepare); activate.command_sequence = 4; activate.operation = FillCommand.ACTIVATE
    activate.stamp = time_at(10.2); activate.prepared_sha256 = prepared.prepared_sha256
    result = response(activate, FillResult.ACTIVATED, 10.3)
    result.prepared_at = deepcopy(prepared.prepared_at); result.committed_at = time_at(10.3)
    result.registry_generation = 2
    result.fill = deepcopy(data[5].fill); result.fill.fill_id = 2; result.fill.revision = 2
    result.fill.amplitude = .5; result.fill.stamp = time_at(10.3)
    result.has_superseded_fill = True; result.superseded_fill = deepcopy(data[5].fill)
    result.superseded_fill.active = False; result.superseded_fill.superseded = True
    result.superseded_fill.stamp = time_at(10.3)
    result.registry_digest_before = data[5].registry_digest_after
    result.registry_digest_after = fill_registry_digest([result.fill])
    result.committed_sha256 = result_sha256(result)
    data[0][TOPICS['v2_fill_commands']] += [(9, prepare), (10, activate)]
    data[0][TOPICS['v2_candidate_snapshots']].append((10, prepare.snapshot))
    data[0][TOPICS['v2_fill_results']] += [(11, prepared), (12, result)]
    data[0][TOPICS['gaussian_fills']] += [(1, deepcopy(result.superseded_fill)), (2, deepcopy(result.fill))]
    return prepare, prepared, activate, result


def test_atomic_redesign_preserves_exact_previous_version_and_generation():
    data = fixture(); add_redesign(data)
    errors, metrics = check(data)
    assert errors == [] and metrics['counts']['unique_commits'] == 2
    assert metrics['preparations'][1]['redesign']


@pytest.mark.parametrize('mutate, expected', [
    (lambda r: setattr(r.superseded_fill, 'amplitude', .3), 'changed retained version'),
    (lambda r: setattr(r.fill, 'revision', 3), 'exact active target'),
    (lambda r: setattr(r, 'has_superseded_fill', False), 'new fill target/revision'),
    (lambda r: setattr(r, 'registry_digest_before', 'e'*64), 'before digest chain'),
    (lambda r: setattr(r, 'committed_at', time_at(14.)), 'deadline/publication ordering'),
])
def test_rehashed_invalid_redesign_cannot_pass(mutate, expected):
    data = fixture(); result = add_redesign(data)[3]
    mutate(result); result.committed_sha256 = result_sha256(result)
    assert expected in ';'.join(check(data)[0])


def test_interpolation_only_bracket_outside_radius_is_not_raw_support():
    data = fixture(activated=False)
    snap = data[2].snapshot
    snap.observations[0].base_x_m = 2.
    data[0][TOPICS['v2_direction_diagnostics']][0][1].observation.base_x_m = 2.
    snap.evidence_start = snap.revolution_start[0] = time_at(.05)
    snap.revolution_sample_start[0] = 1
    rehash_snapshot(data)
    data[3].evidence_sha256 = data[2].evidence_sha256
    data[3].committed_sha256 = result_sha256(data[3])
    assert check(data)[0] == []
    snap.revolution_start[0] = snap.evidence_start = time_at(.025)
    rehash_snapshot(data)
    assert 'represented snapshot position outside' in ';'.join(check(data)[0])


def test_context_identity_regression_and_confirmation_rearm_rejected():
    data = fixture()
    context = deepcopy(data[0][TOPICS['v2_search_epoch']][0][1])
    context.context_sequence = 2; context.started_at = time_at(.1); context.stamp = time_at(6.1)
    data[0][TOPICS['v2_search_epoch']].append((3, context))
    assert 'changed authoritative epoch start' in ';'.join(check(data)[0])
    data = fixture()
    confirmation = deepcopy(data[0][TOPICS['v2_detector_confirmation']][0][1])
    confirmation.confirmation_sequence = 2
    data[0][TOPICS['v2_detector_confirmation']].append((3, confirmation))
    assert 'multiple confirmations' in ';'.join(check(data)[0])


def test_validator_is_integrated_without_replacing_strict_m2_check():
    from pathlib import Path
    owner = Path(__file__).resolve().parents[1]/'ros_esc/experiment_recording/validate_run.py'
    code = owner.read_text()
    assert "'v2_synchronized_stream_contract'" in code
    assert "'v2_lifecycle_contract'" in code
    assert "report['v2_lifecycle_metrics'] = lifecycle_metrics" in code


def test_nonprepare_unused_snapshot_may_be_empty():
    data = fixture()
    data[4].snapshot = CandidateSnapshot()
    assert check(data)[0] == []


def test_goal_without_fill_requires_independent_published_verified_snapshot():
    from ros_esc_interfaces.msg import AlgorithmState
    data = fixture(activated=False)
    data[0].pop(TOPICS['v2_fill_commands']); data[0].pop(TOPICS['v2_fill_results'])
    goal = AlgorithmState(run_id=data[1]['run_id'], run_id_valid=True, state_valid=True, state=7)
    goal.stamp = time_at(9.1)
    data[0][TOPICS['algorithm_state']] = [(0, goal)]
    errors, metrics = check(data)
    assert errors == [] and metrics['goal_states'][0]['candidate_ids'] == [1]
    data[0].pop(TOPICS['v2_candidate_snapshots'])
    assert 'GOAL lacks published verified candidate' in ';'.join(check(data)[0])


def test_prepare_cannot_silently_substitute_for_candidate_publication():
    data = fixture(); data[0].pop(TOPICS['v2_candidate_snapshots'])
    assert 'matching published candidate snapshot' in ';'.join(check(data)[0])


def test_same_ros_tick_uses_result_publisher_order_for_terminal_race():
    data = fixture()
    cancel = deepcopy(data[4]); cancel.operation = FillCommand.CANCEL; cancel.command_sequence = 3
    cancel.stamp = time_at(9.25)
    cancelled = response(cancel, FillResult.CANCELLED, 9.25)
    data[0][TOPICS['v2_fill_commands']].append((0, cancel))
    data[0][TOPICS['v2_fill_results']].insert(1, (0, cancelled))
    assert 'result publisher order' in ';'.join(check(data)[0])


@pytest.mark.parametrize('field, value', [('estimate', -2.6), ('mad', .1),
                                       ('uncertainty', .1), ('lower', -2.6), ('upper', -2.4)])
def test_rehashed_raw_summary_is_recomputed_from_exact_actual_minima(field, value):
    data = fixture(activated=False)
    setattr(data[2].snapshot, 'candidate_cost_'+field, value)
    rehash_snapshot(data)
    assert check(data)[0]


def test_resolution_of_nondefault_mad_scale_is_explicit():
    data = fixture(activated=False)
    snap = data[2].snapshot
    # Shift every actual raw value in cycle 3; it remains negative and the
    # immutable snapshot is reissued with the actual existing summary owner.
    for index in range(120, 180):
        snap.observations[index].raw_cost -= .2
        data[0][TOPICS['v2_direction_diagnostics']][index][1].observation.raw_cost -= .2
    for index in range(60, 120):
        snap.observations[index].raw_cost -= .1
        data[0][TOPICS['v2_direction_diagnostics']][index][1].observation.raw_cost -= .1
    from ros_esc.supervisor_node.state_machine import RotationCostWindow
    minima = [min(obs.raw_cost for obs in snap.observations[lo:hi]) for lo,hi in
              zip(snap.revolution_sample_start, snap.revolution_sample_end)]
    summary = RotationCostWindow.summarize_minima(minima, 3, 2.)
    for key in ('estimate', 'mad', 'uncertainty', 'lower', 'upper'):
        setattr(snap, 'candidate_cost_'+key, getattr(summary, key))
    rehash_snapshot(data)
    data[3].evidence_sha256 = data[2].evidence_sha256
    data[3].committed_sha256 = result_sha256(data[3])
    assert lifecycle_stream_errors(data[0], data[1], candidate_cost_mad_scale=2.)[0] == []
    assert 'raw minima/median/MAD' in ';'.join(check(data)[0])


def test_supervisor_first_receipt_may_match_later_recorded_publication():
    data = fixture(activated=False)
    diagnostic = deepcopy(data[0][TOPICS['v2_direction_diagnostics']][0][1])
    diagnostic.stamp = time_at(.02)
    data[0][TOPICS['v2_direction_diagnostics']].append((1000, diagnostic))
    data[2].snapshot.observation_filter_stamp[0] = time_at(.02)
    rehash_snapshot(data)
    data[3].evidence_sha256 = data[2].evidence_sha256
    data[3].committed_sha256 = result_sha256(data[3])
    assert check(data)[0] == []  # Separate subscribers do not prove first callback order.


@pytest.mark.parametrize('admission_ns, publication_ns', [
    (13_020_000_000, 24_020_000_000),  # 7 s approach and 11 s collection.
    (14_020_000_000, 26_020_000_000),  # All inclusive wire bounds exactly.
    (6_020_000_000, 18_020_000_000),   # First admission at acceptance.
])
def test_centered_deadline_is_bound_to_first_actual_admission(admission_ns, publication_ns):
    data = centered_fixture(admission_ns=admission_ns, publication_ns=publication_ns)
    errors, metrics = check_centered(data)
    assert errors == []
    assert metrics['verification_collection_admissions'] == [{
        'candidate_id': 1, 'search_epoch': 1, 'collection_admitted_at_ns': admission_ns}]
    assert metrics['candidates'][0]['evidence_start_ns'] < admission_ns
    assert metrics['candidates'][0]['actual_raw_cycle_minima'] == pytest.approx([-2.5]*3)
    if publication_ns > 18_020_000_000:
        assert 'original deadline' in ';'.join(check(data)[0])


@pytest.mark.parametrize('admission_ns, publication_ns, reason', [
    (6_019_999_999, 18_000_000_000, 'approach admission'),
    (14_020_000_001, 24_020_000_000, 'approach admission'),
    (13_020_000_000, 13_019_999_999, 'collection publication'),
    (13_020_000_000, 25_020_000_001, 'collection publication'),
    (14_020_000_000, 26_020_000_001, 'collection publication'),
])
def test_centered_deadline_rejects_one_nanosecond_boundary_violations(
        admission_ns, publication_ns, reason):
    data = centered_fixture(admission_ns=admission_ns, publication_ns=publication_ns)
    assert reason in ';'.join(check_centered(data)[0])


def test_centered_admission_repeat_cannot_renew_or_rebind_candidate():
    data = centered_fixture()
    rows = data[0][TOPICS['algorithm_events']]
    rows.append((0, deepcopy(rows[0][1])))  # Exact repeat, receipt order unrelated.
    errors, metrics = check_centered(data)
    assert errors == [] and len(metrics['verification_collection_admissions']) == 1
    rows[-1][1].stamp = time_at(14.02)
    errors, metrics = check_centered(data)
    assert 'conflicting repeated collection admission' in ';'.join(errors)
    assert metrics['verification_collection_admissions'][0]['collection_admitted_at_ns'] == 13_020_000_000


@pytest.mark.parametrize('mutation', [
    lambda event: setattr(event, 'values', [2., 1.]),
    lambda event: setattr(event, 'values', [1., 2.]),
    lambda event: setattr(event, 'values', [float('nan'), 1.]),
    lambda event: setattr(event, 'values', [1.5, 1.]),
    lambda event: setattr(event, 'values', [4097., 1.]),
    lambda event: setattr(event, 'values', [0., 1.]),
    lambda event: setattr(event, 'values', [1.]),
    lambda event: setattr(event, 'value_names', ['search_epoch', 'candidate_id']),
    lambda event: setattr(event, 'state_valid', False),
    lambda event: setattr(event, 'state', 1),
    lambda event: setattr(event, 'state_name', 'SEARCH'),
    lambda event: setattr(event, 'detail', 'collection renewed'),
    lambda event: setattr(event, 'event_type', 11),
])
def test_centered_snapshot_requires_well_formed_matching_actual_stage(mutation):
    data = centered_fixture()
    mutation(data[0][TOPICS['algorithm_events']][0][1])
    assert check_centered(data)[0]


def test_centered_stage_required_even_for_short_initial_snapshot():
    data = fixture()
    assert 'lacks matching collection admission' in ';'.join(check_centered(data)[0])
    assert check(data)[0] == []
    assert 'verification_collection_admissions' not in check(data)[1]


def test_centered_mode_keeps_actual_raw_evidence_integrity():
    data = centered_fixture()
    snap = data[0][TOPICS['v2_candidate_snapshots']][0][1]
    snap.observations[50].raw_cost += .01
    snap.evidence_sha256 = snapshot_sha256(snap)
    assert 'recorded filter observation' in ';'.join(check_centered(data)[0])


def test_centered_redesign_retains_existing_later_snapshot_timing():
    data = centered_fixture()
    first = data[0][TOPICS['v2_candidate_snapshots']][0][1]
    later = deepcopy(first)
    later.snapshot_revision = 2
    later.stamp = time_at(30.)
    later.evidence_sha256 = snapshot_sha256(later)
    data[0][TOPICS['v2_candidate_snapshots']].append((2000, later))
    errors, metrics = check_centered(data)
    assert errors == [] and len(metrics['candidates']) == 2


def test_unknown_verification_mode_is_rejected_without_inference():
    data = fixture()
    errors, _ = lifecycle_stream_errors(data[0], data[1], moving_verification_mode='future')
    assert errors == ['V2 lifecycle unknown selected moving verification mode']


def test_actual_verification_stage_is_classified_as_supervisor():
    from ros_esc.experiment_recording.validate_run import algorithm_event_producer_stream
    event = centered_fixture()[0][TOPICS['algorithm_events']][0][1]
    assert algorithm_event_producer_stream(event) == 'supervisor'


def test_centered_guidance_joins_real_state_pose_and_first_admission():
    data = centered_fixture()
    add_centered_guidance(data, publication_ns=13_040_000_000)
    errors, metrics = check_centered(data)
    assert errors == []
    assert [row['collection_started'] for row in metrics['verification_guidance']] == [False, True]


def same_tick_collection_fixture():
    data = centered_fixture()
    collect, _ = add_centered_guidance(data, publication_ns=13_020_000_000)
    approach = deepcopy(collect)
    approach.collection_started = False
    approach.collection_admitted_at = time_at(0.)
    approach.verification_expires_at = time_at(14.02)
    approach.command_expires_at = time_at(14.02)
    collect.publication_sequence += 1
    data[0][TOPICS['v2_verification_guidance']].insert(-1, (9000, approach))
    return data, approach, collect


def test_centered_same_tick_approach_then_collection_uses_sender_order():
    data, approach, collect = same_tick_collection_fixture()
    # Transport receipts deliberately disagree with sender order.
    rows = data[0][TOPICS['v2_verification_guidance']]
    rows.insert(-1, (10000, deepcopy(approach)))  # Exact latest replay.
    rows[:] = [(stamp, deserialize_message(serialize_message(message), type(message)))
               for stamp, message in rows]
    errors, metrics = check_centered(data)
    assert errors == []
    assert [(r['publication_sequence'], r['collection_started'])
            for r in metrics['verification_guidance']] == [(1, False), (2, False), (3, True)]


@pytest.mark.parametrize('fault', ['missing', 'invalid', 'deadline', 'state', 'later_tick',
                                  'candidate', 'admission'])
def test_centered_same_tick_approach_requires_fully_valid_first_witness(fault):
    data, approach, collect = same_tick_collection_fixture()
    if fault == 'missing':
        data[0][TOPICS['v2_verification_guidance']].pop()
    elif fault == 'invalid':
        collect.valid = False
        collect.linear_x_mps = collect.angular_z_radps = 0.
    elif fault == 'deadline':
        collect.command_expires_at = time_at(25.021)
    elif fault == 'state':
        collect.state_sha256 = 'f'*64
    elif fault == 'later_tick':
        data[0][TOPICS['v2_verification_guidance']].pop()
        add_centered_guidance(data, publication_ns=13_040_000_000)
    elif fault == 'candidate':
        collect.candidate_id = 2
    else:
        collect.collection_admitted_at = time_at(13.021)
    errors, metrics = check_centered(data)
    assert 'guidance approach hides an admitted collection' in ';'.join(errors)
    assert 2 not in [r['publication_sequence'] for r in metrics['verification_guidance']]


@pytest.mark.parametrize('first_collect_ns', [13_020_000_000, 13_040_000_000])
def test_centered_collection_then_backdated_approach_cannot_use_later_witness(first_collect_ns):
    data, approach, collect = same_tick_collection_fixture()
    rows = data[0][TOPICS['v2_verification_guidance']]
    rows.pop()
    rows.pop()
    first, _ = add_centered_guidance(data, publication_ns=first_collect_ns)
    approach.publication_sequence = first.publication_sequence+1
    rows.append((0, approach))
    collect.publication_sequence = approach.publication_sequence+1
    rows.append((0, collect))
    errors, metrics = check_centered(data)
    assert 'guidance approach hides an admitted collection' in ';'.join(errors)
    assert approach.publication_sequence not in [r['publication_sequence']
                                                 for r in metrics['verification_guidance']]


def test_centered_same_tick_approach_still_rejects_hidden_admission_field():
    data, approach, _ = same_tick_collection_fixture()
    approach.collection_admitted_at = time_at(13.02)
    assert 'guidance approach hides an admitted collection' in ';'.join(check_centered(data)[0])


def test_centered_approach_after_admission_is_not_a_same_tick_transition():
    data = centered_fixture()
    approach, _ = add_centered_guidance(data, publication_ns=13_020_000_001)
    approach.collection_started = False
    approach.collection_admitted_at = time_at(0.)
    approach.verification_expires_at = approach.command_expires_at = time_at(14.02)
    add_centered_guidance(data, publication_ns=13_040_000_000)
    assert 'guidance approach hides an admitted collection' in ';'.join(check_centered(data)[0])


def test_centered_multiple_earlier_same_tick_approaches_share_first_collection_witness():
    data, approach, collect = same_tick_collection_fixture()
    later = deepcopy(approach)
    later.publication_sequence += 1
    later.linear_x_mps = .02
    collect.publication_sequence += 1
    data[0][TOPICS['v2_verification_guidance']].insert(-1, (0, later))
    errors, metrics = check_centered(data)
    assert errors == []
    assert [row['publication_sequence'] for row in metrics['verification_guidance']] == [1, 2, 3, 4]


@pytest.mark.parametrize('field, value', [
    ('run_id', 'foreign'), ('stream_contract_id', 'foreign'), ('frame_id', 'foreign'),
    ('candidate_id', 2), ('search_epoch', 2), ('algorithm_state', 4),
    ('mode', 'rolling_neighborhood_v1'), ('center_x_m', .1),
    ('linear_x_mps', float('nan')), ('collection_started', True),
])
def test_centered_guidance_rejects_malformed_or_changed_authority(field, value):
    data = centered_fixture()
    guide = data[0][TOPICS['v2_verification_guidance']][0][1]
    setattr(guide, field, value)
    if field == 'candidate_id':
        # A different real candidate may exist, but cannot mutate this candidate's publication.
        original = deepcopy(guide)
        original.candidate_id = 1
        data[0][TOPICS['v2_verification_guidance']].insert(0, (0, original))
    assert check_centered(data)[0]


@pytest.mark.parametrize('field, stamp', [
    ('state_stamp', 9_010_000_000), ('pose_stamp', 8_000_000_000),
    ('accepted_at', 6_030_000_000), ('verification_expires_at', 14_020_000_001),
    ('command_expires_at', 14_020_000_001), ('collection_admitted_at', 1),
])
def test_centered_guidance_rejects_timestamp_substitution(field, stamp):
    data = centered_fixture()
    guide = data[0][TOPICS['v2_verification_guidance']][0][1]
    set_time(getattr(guide, field), stamp)
    assert check_centered(data)[0]


def test_centered_guidance_requires_recorded_stream_and_exact_state_companion():
    data = centered_fixture()
    data[0].pop(TOPICS['v2_verification_guidance'])
    assert 'missing selected verification guidance' in ';'.join(check_centered(data)[0])
    data = centered_fixture()
    data[0].pop(TOPICS['algorithm_state'])
    assert 'exact selected AlgorithmState companion' in ';'.join(check_centered(data)[0])


def test_centered_invalid_guidance_must_zero_command():
    data = centered_fixture()
    guide = data[0][TOPICS['v2_verification_guidance']][0][1]
    guide.valid = False
    assert 'invalid guidance has nonzero command' in ';'.join(check_centered(data)[0])
    guide.linear_x_mps = guide.angular_z_radps = 0.
    assert check_centered(data)[0] == []


def test_centered_design_guidance_uses_existing_initial_preparation_expiry():
    data = centered_fixture()
    prepare = data[2]
    prepare.stamp = time_at(24.04)
    prepare.expires_at = time_at(29.04)
    data[0][TOPICS['v2_fill_commands']] = [(3000, prepare)]
    guide, state = add_centered_guidance(data, publication_ns=26_040_000_000, design_command=prepare)
    assert check_centered(data)[0] == []  # Existing DESIGN allowance extends beyond verification.
    guide.command_expires_at = time_at(29.05)
    assert 'matching preparation deadline' in ';'.join(check_centered(data)[0])


def test_centered_same_tick_guidance_revision_retains_new_publication():
    data = centered_fixture()
    rows = data[0][TOPICS['v2_verification_guidance']]
    revised = deepcopy(rows[0][1])
    revised.publication_sequence = 2
    revised.linear_x_mps = .02
    rows.append((0, revised))
    errors, metrics = check_centered(data)
    assert errors == []
    assert [row['publication_sequence'] for row in metrics['verification_guidance']] == [1, 2]


def test_centered_same_tick_full_state_revisions_are_independently_bound():
    data = centered_fixture()
    states = data[0][TOPICS['algorithm_state']]
    later_state = deepcopy(states[0][1])
    later_state.sensor_weight = .5
    later_state.weights_valid = True
    states.append((0, later_state))
    rows = data[0][TOPICS['v2_verification_guidance']]
    revised = deepcopy(rows[0][1])
    revised.publication_sequence = 2
    revised.state_sha256 = hash_payload(message_payload(later_state))
    rows.append((0, revised))
    errors, metrics = check_centered(data)
    assert errors == []
    assert len({row['state_sha256'] for row in metrics['verification_guidance']}) == 2
    states.pop()
    assert 'exact selected AlgorithmState companion' in ';'.join(check_centered(data)[0])


def test_centered_latest_identical_guidance_replay_does_not_add_authority():
    data = centered_fixture()
    rows = data[0][TOPICS['v2_verification_guidance']]
    rows.append((4000, deepcopy(rows[0][1])))
    errors, metrics = check_centered(data)
    assert errors == [] and len(metrics['verification_guidance']) == 1
    rows[-1][1].linear_x_mps = .02
    assert 'conflicting guidance publication sequence' in ';'.join(check_centered(data)[0])


def test_centered_guidance_older_replay_is_sequence_rollback():
    data = centered_fixture()
    rows = data[0][TOPICS['v2_verification_guidance']]
    newer = deepcopy(rows[0][1])
    newer.publication_sequence = 2
    rows.extend([(0, newer), (0, deepcopy(rows[0][1]))])
    assert 'guidance publication sequence regressed' in ';'.join(check_centered(data)[0])


@pytest.mark.parametrize('field, value', [('publication_sequence', 0),
                                       ('state_sha256', 'bad'), ('state_sha256', '0'*64)])
def test_centered_guidance_requires_typed_revision_identity(field, value):
    data = centered_fixture()
    setattr(data[0][TOPICS['v2_verification_guidance']][0][1], field, value)
    assert check_centered(data)[0]


def test_centered_same_tick_design_pending_zero_then_prepared_guidance():
    data = centered_fixture()
    prepare = data[2]
    prepare.stamp, prepare.expires_at = time_at(24.04), time_at(29.04)
    data[0][TOPICS['v2_fill_commands']] = [(3000, prepare)]
    ready, _ = add_centered_guidance(data, publication_ns=24_040_000_000, design_command=prepare)
    pending = deepcopy(ready)
    pending.valid = False
    pending.reason = 'centered_preparation_pending'
    pending.linear_x_mps = pending.angular_z_radps = 0.
    pending.command_expires_at = deepcopy(pending.verification_expires_at)
    ready.publication_sequence = 3
    rows = data[0][TOPICS['v2_verification_guidance']]
    rows.insert(1, (3000, pending))
    errors, metrics = check_centered(data)
    assert errors == []
    assert [row['publication_sequence'] for row in metrics['verification_guidance']] == [1, 3]


def test_centered_startup_unbound_guidance_keeps_exact_state_and_zero():
    data = centered_fixture()
    guide = data[0][TOPICS['v2_verification_guidance']][0][1]
    guide.valid = False
    guide.stream_contract_id = ''
    guide.candidate_id = 0
    guide.linear_x_mps = guide.angular_z_radps = 0.
    assert check_centered(data)[0] == []


def recurrent_fixture():
    """Actual static trajectory -> numerical owner -> new typed diagnostic join."""
    from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics
    from ros_esc.convergence_detector_node.recurrent_geometry import (
        RecurrentGeometryDetector, diagnostic_model_fields,
    )
    from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE
    data = fixture()
    messages, identity = data[:2]
    for alias in ('v2_candidate_snapshots', 'v2_fill_commands', 'v2_fill_results',
                  'gaussian_fills', 'v2_direction_diagnostics', 'centroid_convergence_diagnostics'):
        messages.pop(TOPICS[alias], None)
    core = RecurrentGeometryDetector()
    core.start_epoch('1', 0)
    results = []
    poses = []
    for index in range(151):
        stamp_ns = index*200_000_000
        results.extend(core.update(stamp_ns, (0., 0.), identity['stream_config']['frame_id']))
        pose = Odometry()
        set_time(pose.header.stamp, stamp_ns)
        pose.header.frame_id = identity['stream_config']['frame_id']
        pose.pose.pose.orientation.w = 1.
        poses.append((stamp_ns, pose))
    selected = [result for result in results if result.confirmed_event]
    assert len(selected) == 1 and selected[0].branch == 'static'
    result = selected[0]
    diagnostic = RecurrentConvergenceDiagnostics(**diagnostic_model_fields(result),
        run_id=identity['run_id'], frame_id=identity['stream_config']['frame_id'],
        source_pose_topic=identity['stream_config']['pose_topic'], metric_mode=RECURRENT_MODE,
        search_epoch=1, confirmation_sequence=1, reset_sequence=result.reset_sequence,
        center_x_m=float(result.mean_xy[0]), center_y_m=float(result.mean_xy[1]),
        score_m=float(result.score_m), confinement_radius_m=float(result.radius_m), maximum_radius_m=.5,
        represented_duration_sec=result.represented_duration_ns/1e9,
        maximum_source_gap_sec=result.max_source_gap_ns/1e9, sample_count=result.sample_count,
        source_valid=True, history_valid=True, metric_valid=True, confinement_valid=True,
        eligible=True, confirmed=True)
    for field, stamp_ns in [('stamp', 30_010_000_000), ('receipt_stamp', 30_000_000_000),
                           ('source_stamp', 30_000_000_000), ('history_start', result.start_ns),
                           ('history_end', result.end_ns), ('persistence_start', result.persistence_start_ns)]:
        set_time(getattr(diagnostic, field), stamp_ns)
    confirmation = messages[TOPICS['v2_detector_confirmation']][0][1]
    confirmation.stamp = time_at(30.01)
    confirmation.source_stamp = confirmation.history_end = time_at(30.)
    confirmation.metric_mode, confirmation.history_kind = RECURRENT_MODE, 'recurrent_geometry'
    confirmation.convergence_score_m = diagnostic.score_m
    messages[TOPICS['v2_search_epoch']][0][1].stamp = time_at(30.)
    messages[TOPICS['recurrent_convergence_diagnostics']] = [(30_010_000_000, diagnostic)]
    messages[identity['stream_config']['pose_topic']] = poses
    return data


def test_recurrent_numerical_confirmation_has_distinct_typed_support():
    data = recurrent_fixture()
    for topic, rows in data[0].items():
        data[0][topic] = [(stamp, deserialize_message(serialize_message(message), type(message)))
                         for stamp, message in rows]
    errors, metrics = lifecycle_stream_errors(data[0], data[1], metric_mode='recurrent_geometry_v3')
    assert errors == []
    assert metrics['confirmations'][0]['metric_mode'] == 'recurrent_geometry_v3'
    assert metrics['confirmations'][0]['source_stamp_ns'] == 30_000_000_000
    assert metrics['counts']['candidate_snapshots'] == 0


@pytest.mark.parametrize('field, value', [
    ('run_id', 'foreign'), ('frame_id', 'foreign'), ('search_epoch', 2),
    ('confirmation_sequence', 2), ('center_x_m', .1), ('score_m', .01),
    ('persistence_count', 0), ('maximum_drift_m_s', .006),
])
def test_recurrent_confirmation_rejects_changed_typed_evidence(field, value):
    data = recurrent_fixture()
    diagnostic = data[0][TOPICS['recurrent_convergence_diagnostics']][0][1]
    setattr(diagnostic, field, value)
    assert lifecycle_stream_errors(data[0], data[1], metric_mode='recurrent_geometry_v3')[0]


@pytest.mark.parametrize('field, stamp', [('stamp', 30.02), ('history_start', .01),
                                       ('epoch_started_at', .01), ('source_stamp', 29.99)])
def test_recurrent_confirmation_rejects_time_substitution(field, stamp):
    data = recurrent_fixture()
    diagnostic = data[0][TOPICS['recurrent_convergence_diagnostics']][0][1]
    setattr(diagnostic, field, time_at(stamp))
    assert lifecycle_stream_errors(data[0], data[1], metric_mode='recurrent_geometry_v3')[0]


def test_recurrent_confirmation_cannot_borrow_legacy_centroid_diagnostic():
    data = recurrent_fixture()
    data[0].pop(TOPICS['recurrent_convergence_diagnostics'])
    data[0][TOPICS['centroid_convergence_diagnostics']] = fixture()[0][TOPICS['centroid_convergence_diagnostics']]
    errors, _ = lifecycle_stream_errors(data[0], data[1], metric_mode='recurrent_geometry_v3')
    assert 'missing selected recurrent diagnostic stream' in ';'.join(errors)
    assert 'lacks matching typed diagnostic support' in ';'.join(errors)


def test_snapshot_revisions_cannot_rewrite_retained_first_received_provenance():
    data = fixture(); prepare, prepared, _, _ = add_redesign(data)
    diagnostic = deepcopy(data[0][TOPICS['v2_direction_diagnostics']][0][1])
    diagnostic.stamp = time_at(.02)
    data[0][TOPICS['v2_direction_diagnostics']].append((1000, diagnostic))
    prepare.snapshot.observation_filter_stamp[0] = time_at(.02)
    prepare.snapshot.evidence_sha256 = snapshot_sha256(prepare.snapshot)
    prepare.evidence_sha256 = prepare.snapshot.evidence_sha256
    assert 'changed first supervisor-received' in ';'.join(check(data)[0])


def test_objective_registry_changes_need_typed_authority_even_without_mirrors():
    from ros_esc_interfaces.msg import ObjectiveCostSample
    data = fixture()
    objective = ObjectiveCostSample(valid=True, schema_version=2,
        run_id=data[1]['run_id'], frame_id=data[1]['stream_config']['frame_id'],
        stream_contract_id=data[2].stream_contract_id, registry_digest=data[5].registry_digest_after)
    objective.stamp = objective.composition_stamp = time_at(9.3)
    data[0][data[1]['stream_config']['objective_cost_topic']] = [(0, objective)]
    assert check(data)[0] == []
    objective.composition_stamp = time_at(9.2)
    assert 'prior typed activation authority' in ';'.join(check(data)[0])
    objective.composition_stamp = time_at(9.3); objective.registry_digest = 'f'*64
    assert 'prior typed activation authority' in ';'.join(check(data)[0])


def test_canonical_publication_cannot_precede_its_source_commit():
    data = fixture()
    data[0][TOPICS['gaussian_fills']][0][1].stamp = time_at(9.2)
    assert 'typed activation authority' in ';'.join(check(data)[0])
