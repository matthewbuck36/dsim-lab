"""Selected recorder/lifecycle evidence and independent counted-cost decisions."""
from copy import deepcopy
from pathlib import Path
import pytest
from nav_msgs.msg import Odometry
from rclpy.serialization import serialize_message, deserialize_message
from ros_esc_interfaces.msg import (AlgorithmState, GescDirectionDiagnostics,
                                    SourceSampleProvenance, Timekeeper)
from ros_esc.experiment_recording.record_run import (
    applicable_topics, require_selected_algorithm_topics, v2_identity_from_metadata,
)
from ros_esc.experiment_recording.v2_lifecycle_validation import TOPICS, lifecycle_stream_errors
from ros_esc.supervisor_node.escape_recenter import OperatingBounds, Pose2D
from ros_esc.supervisor_node.state_machine import (
    CandidateCostSummary, State, StateMachineConfig, SupervisorStateMachine, TransitionInputs,
)
from ros_esc.v2_lifecycle import message_payload, recurrent_snapshot_sha256
from ros_esc.v2_stream import time_to_ns
from test_r21_trapping_supervisor import selected_owner, deliver
from test_v2_recording_contract import prepared
import test_v2_supervisor as legacy

POLICY = 'recurrent_trapping_v1'
SNAPSHOT = 'v2_recurrent_candidate_snapshots'
COMMAND = 'v2_recurrent_fill_commands'


def recorded_case(monkeypatch):
    """Actual selected callbacks produce the immutable certificate/raw wrapper."""
    case = selected_owner(monkeypatch)
    deliver(case)
    assert legacy.step(case.owner).current == State.VERIFY_EXTREMUM
    case.owner.inputs(TransitionInputs())
    wrapper = deepcopy(case.owner.snapshot_publisher.messages[-1])
    snap = wrapper.snapshot
    identity = {'run_id': case.node.run_id, 'stream_config': case.owner.config}
    messages = {
        case.owner.config['timekeeper_topic']: [(0, Timekeeper(mode='sim time', start_time=0.))],
        TOPICS['v2_search_epoch']: [(1, deepcopy(case.owner.epoch_publisher.messages[0]))],
        # Intentionally different bag order from callback/publication order.
        TOPICS['v2_detector_confirmation']: [(4, deepcopy(wrapper.confirmation))],
        TOPICS['recurrent_convergence_diagnostics']: [(7, deepcopy(wrapper.diagnostic))],
        TOPICS[SNAPSHOT]: [(2, wrapper)],
        TOPICS['algorithm_events']: [(8+i, deepcopy(m)) for i,m in enumerate(case.node.event_publisher.messages)],
        TOPICS['v2_direction_diagnostics']: [], case.owner.config['provenance_topic']: [],
        case.owner.config['pose_topic']: [],
    }
    for index, (obs, state, first) in enumerate(zip(snap.observations,
            snap.observation_filter_state, snap.observation_filter_stamp)):
        diag = GescDirectionDiagnostics(schema_version=2, run_id=obs.run_id,
            stream_contract_id=obs.stream_contract_id, frame_id=obs.frame_id,
            observation=deepcopy(obs), algorithm_state=state,
            algorithm_state_valid=True, output_valid=True, diagnostic_sequence=index+1)
        diag.time_origin, diag.stamp = deepcopy(obs.time_origin), deepcopy(first)
        messages[TOPICS['v2_direction_diagnostics']].append((index, diag))
        prov = SourceSampleProvenance(schema_version=2, run_id=obs.run_id,
            stream_contract_id=obs.stream_contract_id, frame_id=obs.frame_id,
            source_sequence=obs.source_sequence, model_input_stamp_valid=True,
            sensor_transform_valid=True, channel_count=1,
            legacy_cost_source_timestamp_sec=obs.legacy_cost_source_timestamp_sec)
        prov.time_origin = deepcopy(obs.time_origin)
        prov.stamp = prov.model_input_stamp = prov.cost_publication_stamp = deepcopy(obs.source_stamp)
        messages[case.owner.config['provenance_topic']].append((index, prov))
    # The actual selected guidance owner creates its exact AlgorithmState join.
    case.node.latest_pose = Pose2D(case.owner.now()*1e-9, 0., 0., 0.)
    case.node.bounds = OperatingBounds()
    case.node.supervisor_command_stale_sec = .5
    case.node.boundary_recovery_trigger_clearance_m = .1
    case.node._active_fill_avoidances = lambda: []
    state = AlgorithmState(run_id=case.node.run_id, run_id_valid=True,
        algorithm_profile='robust_gaussian_v1', state=2, state_name='VERIFY_EXTREMUM',
        state_valid=True, previous_state=1, previous_state_valid=True)
    state.stamp = deepcopy(snap.stamp)
    case.owner.publish_guidance(state)
    guidance = deepcopy(case.owner.guidance_publisher.messages[-1])
    assert guidance.valid
    pose = Odometry()
    pose.header.stamp, pose.header.frame_id = deepcopy(guidance.pose_stamp), guidance.frame_id
    pose.pose.pose.orientation.w = 1.
    messages[case.owner.config['pose_topic']].append((600, pose))
    messages[TOPICS['algorithm_state']] = [(601, state)]
    messages[TOPICS['v2_verification_guidance']] = [(602, guidance)]
    # Exercise the generated new wire and canonical fields, including optional NaNs.
    messages = {topic: [(stamp, deserialize_message(serialize_message(msg), type(msg)))
                        for stamp, msg in rows] for topic, rows in messages.items()}
    return messages, identity


def check(data, **overrides):
    options = dict(metric_mode='recurrent_geometry_v3',
                   moving_verification_mode='centered_tracking_v1',
                   verification_evidence_policy=POLICY)
    options.update(overrides)
    return lifecycle_stream_errors(*data, **options)


def test_selected_cdr_certificate_and_actual_raw_support_join_without_angular_claim(monkeypatch):
    data = recorded_case(monkeypatch)
    before = {topic: [(stamp, message_payload(msg)) for stamp,msg in rows]
              for topic,rows in data[0].items()}
    errors, metrics = check(data)
    assert errors == []
    assert metrics['verification_evidence_policy'] == POLICY
    assert len(metrics['candidates']) == len(metrics['confirmations']) == 1
    assert not data[0][TOPICS[SNAPSHOT]][0][1].snapshot.informative
    assert {topic: [(stamp, message_payload(msg)) for stamp,msg in rows]
            for topic,rows in data[0].items()} == before


@pytest.mark.parametrize('fault', ['missing_diagnostic', 'missing_confirmation', 'context_state',
    'context_origin', 'proof_reset', 'proof_policy', 'raw_summary', 'raw_positive',
    'source_revoked', 'source_frame', 'legacy_topic', 'unselected_policy'])
def test_cached_certificate_cannot_replace_recorded_authority_or_raw_quality(monkeypatch, fault):
    data = recorded_case(monkeypatch)
    messages = data[0]
    wrapper = messages[TOPICS[SNAPSHOT]][0][1]
    if fault == 'missing_diagnostic': messages[TOPICS['recurrent_convergence_diagnostics']] = []
    elif fault == 'missing_confirmation': messages[TOPICS['v2_detector_confirmation']] = []
    elif fault == 'context_state': messages[TOPICS['v2_search_epoch']][0][1].algorithm_state = 2
    elif fault == 'context_origin': messages[TOPICS['v2_search_epoch']][0][1].started_at.nanosec = 1
    elif fault == 'proof_reset': wrapper.diagnostic.reset_sequence += 1
    elif fault == 'proof_policy': wrapper.policy_id = 'angular_profiles_v1'
    elif fault == 'raw_summary': wrapper.snapshot.candidate_cost_estimate -= .01
    elif fault == 'raw_positive':
        for obs in wrapper.snapshot.observations: obs.raw_cost = 1.
    elif fault == 'source_revoked':
        messages[data[1]['stream_config']['provenance_topic']][0][1].sensor_transform_valid = False
    elif fault == 'source_frame': wrapper.snapshot.observations[0].frame_id = 'map'
    elif fault == 'legacy_topic':
        messages[TOPICS['v2_candidate_snapshots']] = [(3, deepcopy(wrapper.snapshot))]
    if fault not in ('proof_policy', 'unselected_policy'):
        wrapper.snapshot.evidence_sha256 = recurrent_snapshot_sha256(wrapper.snapshot, wrapper)
    options = {'verification_evidence_policy': 'angular_profiles_v1'} if fault == 'unselected_policy' else {}
    assert check(data, **options)[0]


def recorder_inputs():
    target, metadata, manifest = prepared()
    replacements = {'convergence_metric_mode': 'recurrent_geometry_v3',
                    'v2_verification_motion_mode': 'centered_tracking_v1',
                    'v2_verification_evidence_policy': POLICY}
    target = [arg for arg in target if not any(arg.startswith(k+':=') for k in replacements)]
    target.extend(k+':='+v for k,v in replacements.items())
    metadata['scenario_runner']['algorithm']['launch_overrides'].update(replacements)
    return applicable_topics(manifest, 'simulation'), target, metadata


def test_recorder_selects_new_event_wires_and_records_explicit_policy_identity():
    entries, target, metadata = recorder_inputs()
    original = deepcopy(entries)
    selected = require_selected_algorithm_topics(entries, 'simulation', target)
    rows = {row['alias']: row for row in selected}
    for alias, kind in ((SNAPSHOT, 'RecurrentCandidateSnapshot'), (COMMAND, 'RecurrentFillCommand')):
        assert rows[alias]['required'] and rows[alias]['minimum_messages'] == 0
        assert rows[alias]['singleton_publisher'] and rows[alias]['coverage'] == 'none'
        assert rows[alias]['type'] == 'ros_esc_interfaces/msg/'+kind
    assert not rows['v2_candidate_snapshots']['required']
    assert not rows['v2_fill_commands']['required']
    assert rows['recurrent_convergence_diagnostics']['required']
    assert v2_identity_from_metadata(metadata)['verification_evidence_policy'] == POLICY
    assert require_selected_algorithm_topics(selected, 'simulation', target) == selected
    assert entries == original


@pytest.mark.parametrize('fault', ['missing_snapshot', 'missing_command', 'type', 'topic', 'pde', 'legacy_motion'])
def test_recorder_rejects_missing_or_wrong_selected_certificate_route(fault):
    entries, target, _ = recorder_inputs()
    if fault in ('missing_snapshot', 'missing_command'):
        alias = SNAPSHOT if fault == 'missing_snapshot' else COMMAND
        entries = [row for row in entries if row['alias'] != alias]
    elif fault in ('type', 'topic'):
        row = next(row for row in entries if row['alias'] == SNAPSHOT)
        row[fault] = ('ros_esc_interfaces/msg/CandidateSnapshot' if fault == 'type' else '/wrong')
    else:
        target = [arg.replace('recurrent_geometry_v3', 'pde_mean_v1') if fault == 'pde'
                  else arg.replace('centered_tracking_v1', 'rolling_neighborhood_v1') for arg in target]
    with pytest.raises(ValueError):
        require_selected_algorithm_topics(entries, 'simulation', target)


def machine(policy=POLICY, *, retained=None):
    owner = SupervisorStateMachine(config=StateMachineConfig(
        moving_verification_enabled=True, extremum_classification_mode='counted_candidates',
        verification_evidence_policy=policy, known_source_count=2, max_fill_clusters=1,
        candidate_cost_required_rotations=3))
    owner.state = State.VERIFY_EXTREMUM
    if retained is not None:
        owner.filled_candidate_costs = [retained]
        owner.active_fill_count = 1
    return owner


def evidence(**changes):
    fields = dict(candidate_cost_observed=True, candidate_cost_valid=True, candidate_cost_ready=True,
        candidate_cost_summary=CandidateCostSummary(-3., 0., 0., 3),
        candidate_verification_passed=True, candidate_informative=False)
    fields.update(changes)
    return TransitionInputs(**fields)


def test_new_verification_input_is_separate_and_default_still_requires_angular_information():
    assert machine().step(.1, evidence(candidate_verification_passed=False, candidate_informative=True)) is None
    assert machine('angular_profiles_v1').step(.1, evidence()) is None
    selected = machine()
    assert selected.step(.1, evidence()).current == State.DESIGN_OR_MERGE_FILL
    assert selected.pending_candidate_cost.estimate == -3.


@pytest.mark.parametrize('estimate,uncertainty,expected', [(-3., .1, State.GOAL_HOLD),
                                                       (-2., .1, State.SEARCH),
                                                       (-2.5, .6, State.SEARCH)])
def test_authenticated_trapping_keeps_strict_interval_ranking(estimate, uncertainty, expected):
    retained = CandidateCostSummary(-2., .1, .3, 3)
    owner = machine(retained=retained)
    summary = CandidateCostSummary(estimate, .1, uncertainty, 3)
    assert owner.step(.1, evidence(candidate_cost_summary=summary, active_fill_count=1)).current == expected


@pytest.mark.parametrize('changes,expected', [
    ({'candidate_cost_valid': False}, State.FAILSAFE),
    ({'candidate_cost_summary': None}, State.FAILSAFE),
    ({'candidate_associated_with_fill': True}, State.SEARCH),
    ({'moving_candidate_cancelled': True}, State.SEARCH),
])
def test_trapping_does_not_bypass_raw_validity_association_or_cancellation(changes, expected):
    assert machine().step(.1, evidence(**changes)).current == expected
