"""Moving fill owner publications through the selected recording validator.

Synthetic source support and a controlled pure worker isolate publication
authority. Actual command/commit and Gaussian publication methods run; wire
messages are serialized. These fixtures do not claim complete run acceptance.
"""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import AlgorithmState, FillCommand, FillResult, Timekeeper

from ros_esc.experiment_recording import validate_run as validator
from ros_esc.experiment_recording.record_run import applicable_topics, load_manifest
from ros_esc.experiment_recording.v2_lifecycle_validation import TOPICS, lifecycle_stream_errors
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill as GaussianOwner
from ros_esc.gaussian_fill_node.fill_preparation import PreparedProposal
from ros_esc.gaussian_fill_node.v2_fill_runtime import MovingFillRuntime
from ros_esc.v2_stream import canonical_json, time_to_ns
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256, snapshot_sha256, hash_payload, message_payload
from test_v2_fill_transactions import Node, Publisher, Worker, values
from test_v2_lifecycle_recording import fixture, time_at, response


EVENT_TOPIC = '/gesc_gaussian/algorithm_events'
PACKAGE = Path(__file__).resolve().parents[1]


class PublicationHost(Node):
    _publish_event = GaussianOwner._publish_event
    _publish_robust_fill = GaussianOwner._publish_robust_fill
    _publish_compatibility_fill = GaussianOwner._publish_compatibility_fill

    def get_clock(self):
        return SimpleNamespace(now=lambda: SimpleNamespace(
            nanoseconds=self.now_ns, to_msg=lambda: time_at(self.now_ns*1e-9)))


def later_candidate():
    """Independent epoch/candidate and source support twenty seconds later."""
    messages, _, prepare, *_ = fixture('pde_mean_v1', activated=False)
    seen = set()

    def shift(message, field=None):
        if field == 'time_origin' or not hasattr(message, 'get_fields_and_field_types') or id(message) in seen:
            return
        seen.add(id(message))
        fields = message.get_fields_and_field_types()
        if set(fields) == {'sec', 'nanosec'}:
            message.sec += 20
            return
        for name in fields:
            value = getattr(message, name)
            if name in ('timestamp', 'legacy_cost_source_timestamp_sec'):
                setattr(message, name, value+20.)
            elif name in ('search_epoch', 'candidate_id', 'objective_revision') and value:
                setattr(message, name, value+1)
            elif name in ('context_sequence',) and value:
                setattr(message, name, value+2)
            elif name in ('confirmation_sequence', 'detector_confirmation_sequence', 'history_sequence') and value:
                setattr(message, name, value+1)
            elif name in ('source_sequence', 'observation_id', 'diagnostic_sequence') and value:
                setattr(message, name, value+1000)
            elif hasattr(value, 'get_fields_and_field_types'):
                shift(value, name)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    shift(item, name)

    for rows in messages.values():
        for _, message in rows:
            shift(message)
    shift(prepare)
    snap = prepare.snapshot
    snap.evidence_sha256 = snapshot_sha256(snap); prepare.evidence_sha256 = snap.evidence_sha256
    published = messages[TOPICS['v2_candidate_snapshots']][0][1]
    published.evidence_sha256 = snapshot_sha256(published)
    history = messages[TOPICS['v2_pde_history_evidence']][0][1]
    history.history_sha256 = hash_payload(message_payload(history, exclude=('stamp', 'history_sha256')))
    return messages, prepare


def producer_messages(*, redesign=False, postcommit_cancel=False, distinct_confirmation=False):
    messages, identity, prepare, *_ = fixture('pde_mean_v1', activated=False)
    node, worker = PublicationHost(), Worker()
    node.now_ns = 9_050_000_000
    node.params.update(v2_run_id=identity['run_id'],
                       v2_stream_config_json=canonical_json(identity['stream_config']),
                       pose_topic=identity['stream_config']['pose_topic'])
    node.algorithm_event_publisher = Publisher()
    node.gaussian_fill_diagnostics_publisher = Publisher()
    node.pub = Publisher()
    runtime = MovingFillRuntime(node, worker=worker, steady_now=lambda: node.steady_ns)
    runtime.set_timekeeper(Timekeeper(mode='sim time', start_time=0.))
    context = deepcopy(messages[TOPICS['v2_search_epoch']][0][1])
    context.context_sequence, context.algorithm_state = 2, 3
    context.stamp = time_at(9.05)
    messages[TOPICS['v2_search_epoch']].append((10, context))
    runtime.context_cb(context)
    state = AlgorithmState(algorithm_profile='robust_gaussian_v1', run_id=identity['run_id'],
        state=3, previous_state=2, state_valid=True, previous_state_valid=True,
        weights_valid=True, run_id_valid=True, sensor_weight=1., gaussian_weight=1.)
    state.stamp = time_at(9.05)
    runtime.state_cb(state)
    pose = deepcopy(messages[identity['stream_config']['pose_topic']][-1][1])
    pose.header.stamp = time_at(9.05)
    runtime.pose_cb(pose)
    runtime.command_cb(prepare)
    assert runtime.current is not None, [r.reason for r in runtime.publisher.messages]
    proposal = values()
    proposal['source_timestamp'] = worker.input.source_timestamp
    worker.future.set_result(PreparedProposal(tuple(proposal.items()), worker.input.samples,
        None, None, worker.input.registry.generation, len(worker.input.samples), ()))
    runtime.poll()
    assert runtime.publisher.messages[-1].result == FillResult.PREPARED
    activate = deepcopy(prepare)
    activate.operation, activate.command_sequence = FillCommand.ACTIVATE, 2
    activate.stamp = time_at(9.05)
    activate.prepared_sha256 = runtime.publisher.messages[-1].prepared_sha256
    runtime.command_cb(activate)
    assert runtime.publisher.messages[-1].result == FillResult.ACTIVATED
    assert node.fill_registry.generation == 1
    messages[TOPICS['v2_fill_commands']] = [(11, prepare), (12, activate)]
    if redesign:
        base = 20. if distinct_confirmation else 0.
        if distinct_confirmation:
            later, second = later_candidate()
            excluded = {TOPICS['v2_fill_commands'], TOPICS['v2_fill_results'], identity['stream_config']['timekeeper_topic']}
            for topic, rows in later.items():
                if topic not in excluded:
                    messages.setdefault(topic, []).extend(rows)
            context = deepcopy(later[TOPICS['v2_search_epoch']][0][1])
        else:
            second = deepcopy(prepare)
        node.now_ns = round((base+9.15)*1e9)
        context = deepcopy(context); context.context_sequence, context.algorithm_state = 3, 3
        if distinct_confirmation:
            context.context_sequence = 4
        context.stamp = time_at(base+9.15); runtime.context_cb(context)
        messages[TOPICS['v2_search_epoch']].append((20, context))
        state.state, state.previous_state, state.stamp = 3, 4, time_at(base+9.15)
        runtime.state_cb(state)
        pose.header.stamp = time_at(base+9.15); runtime.pose_cb(pose)
        second.command_sequence, second.preparation_id = 3, 2
        second.expected_registry_generation = 1
        second.redesign, second.return_state = True, 5
        second.target_fill_id = second.target_cluster_id = second.target_revision = 1
        second.stamp, second.expires_at = time_at(base+9.15), time_at(base+14.15)
        if not distinct_confirmation:
            second.snapshot.snapshot_revision = 2
        second.snapshot.stamp = time_at(base+9.14)
        second.snapshot.evidence_sha256 = snapshot_sha256(second.snapshot)
        second.evidence_sha256 = second.snapshot.evidence_sha256
        if not distinct_confirmation:
            messages[TOPICS['v2_candidate_snapshots']].append((21, deepcopy(second.snapshot)))
        else:
            messages[TOPICS['v2_candidate_snapshots']][-1] = (21, deepcopy(second.snapshot))
        runtime.command_cb(second)
        assert runtime.current is not None, [r.reason for r in runtime.publisher.messages]
        proposal = values(1.2); proposal['source_timestamp'] = worker.input.source_timestamp
        worker.future.set_result(PreparedProposal(tuple(proposal.items()), worker.input.samples,
            1, (1, 1, 1), worker.input.registry.generation, len(worker.input.samples), ()))
        runtime.poll()
        assert runtime.publisher.messages[-1].result == FillResult.PREPARED
        activate2 = deepcopy(second)
        activate2.operation, activate2.command_sequence = FillCommand.ACTIVATE, 4
        activate2.prepared_sha256 = runtime.publisher.messages[-1].prepared_sha256
        runtime.command_cb(activate2)
        assert runtime.publisher.messages[-1].result == FillResult.ACTIVATED
        assert node.fill_registry.generation == 2
        messages[TOPICS['v2_fill_commands']].extend([(22, second), (23, activate2)])
    if postcommit_cancel:
        cancel = deepcopy(messages[TOPICS['v2_fill_commands']][-1][1])
        cancel.operation = FillCommand.CANCEL
        cancel.command_sequence += 1
        runtime.command_cb(cancel)
        assert runtime.publisher.messages[-1].result == FillResult.ALREADY_ACTIVATED
        messages[TOPICS['v2_fill_commands']].append((30, cancel))
    messages[TOPICS['v2_fill_results']] = list(enumerate(runtime.publisher.messages, 13))
    messages[TOPICS['gaussian_fills']] = list(enumerate(node.gaussian_fill_diagnostics_publisher.messages, 15))
    messages[EVENT_TOPIC] = list(enumerate(node.algorithm_event_publisher.messages, 16))
    assert len(messages[EVENT_TOPIC]) == (3 if redesign else 1)
    runtime.close()
    messages = {topic: [(stamp, deserialize_message(serialize_message(msg), type(msg)))
                        for stamp, msg in rows] for topic, rows in messages.items()}
    return messages, identity


def selected_report(tmp_path, monkeypatch, messages, identity, *, selected=True):
    config = identity['stream_config']
    entries = applicable_topics(load_manifest(PACKAGE/'ros_esc/experiment_recording/topic_manifest.yaml'), 'simulation')
    metadata = {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
        'recording': {}, 'git': {}, 'run_id': identity['run_id'], 'target_argv': [
            'algorithm_profile:=robust_gaussian_v1', 'convergence_metric_mode:=pde_mean_v1',
            'continuous_search_mode:=' + ('rolling_gesc_v2' if selected else 'stationary_v1'),
            'v2_run_id:='+identity['run_id'], 'v2_stream_config_json:='+canonical_json(config)]}
    if selected:
        metadata['scenario_runner'] = {'v2_identity': {
            **identity, 'continuous_search_mode': 'rolling_gesc_v2'}}
    documents = {'metadata.yaml': metadata, 'resolved_topics.yaml': {'topics': entries},
                 'resolved_parameters.yaml': {'nodes': {}, 'failures': []}}
    monkeypatch.setattr(validator, '_load_yaml', lambda path: documents[Path(path).name])
    monkeypatch.setattr(validator, '_read_bag', lambda *_args: (
        {entry['topic']: entry['type'] for entry in entries}, messages))
    (tmp_path/'notes.md').write_text('Synthetic moving fill publication authority only.\n')
    report = validator.validate_run_directory(tmp_path, write_report=False)
    assert not report['passed']  # Unrelated complete-recording streams are absent.
    return report


def test_actual_moving_publication_has_typed_request_authority(tmp_path, monkeypatch):
    messages, identity = producer_messages()
    assert lifecycle_stream_errors(messages, identity)[0] == []
    assert not messages.get('/gesc_gaussian/fill_requests')
    event = messages[EVENT_TOPIC][0][1]
    prepare = messages[TOPICS['v2_fill_commands']][0][1]
    assert event.source_timestamp == (
        time_to_ns(prepare.snapshot.confirmation_stamp)-time_to_ns(prepare.time_origin))*1e-9
    result = selected_report(tmp_path, monkeypatch, messages, identity)
    assert result['checks']['v2_lifecycle_contract']['passed'], result
    assert result['checks']['algorithm_event_source_causality']['passed'], result['checks']['algorithm_event_source_causality']


def strict_check(messages, identity):
    return lifecycle_stream_errors(messages, identity, validate_fill_events=True)


@pytest.mark.parametrize('fault', [
    'wrong_origin', 'wrong_epoch', 'wrong_run', 'wrong_stream', 'wrong_frame',
    'wrong_candidate', 'wrong_preparation', 'wrong_evidence', 'wrong_prepared_hash',
    'wrong_result_hash', 'missing_prepared', 'cancel_as_activate', 'only_retry',
    'conflicting_retry', 'missing_snapshot', 'missing_canonical', 'wrong_fill',
    'wrong_cluster', 'wrong_revision', 'wrong_generation', 'wrong_amplitude',
    'wrong_source', 'unavailable_source', 'nan_source', 'wrong_kind',
    'duplicate_event', 'duplicate_value_name', 'before_commit', 'before_activation',
    'self_consistent_wrong_fill_source', 'future_only_mirror',
])
def test_typed_authority_rejects_substitution_and_missing_support(fault):
    messages, identity = producer_messages()
    commands, results = messages[TOPICS['v2_fill_commands']], messages[TOPICS['v2_fill_results']]
    activate, result = commands[-1][1], results[-1][1]
    event = messages[EVENT_TOPIC][0][1]
    if fault == 'wrong_origin':
        activate.time_origin = time_at(.001)
    elif fault in ('wrong_epoch', 'wrong_candidate', 'wrong_preparation'):
        field = {'wrong_epoch': 'search_epoch', 'wrong_candidate': 'candidate_id',
                 'wrong_preparation': 'preparation_id'}[fault]
        setattr(activate, field, getattr(activate, field)+1)
    elif fault in ('wrong_run', 'wrong_stream', 'wrong_frame'):
        setattr(activate, {'wrong_run': 'run_id', 'wrong_stream': 'stream_contract_id',
                          'wrong_frame': 'frame_id'}[fault], 'foreign')
    elif fault == 'wrong_evidence':
        activate.evidence_sha256 = 'f'*64
    elif fault == 'wrong_prepared_hash':
        activate.prepared_sha256 = 'f'*64
    elif fault == 'wrong_result_hash':
        result.committed_sha256 = 'f'*64
    elif fault == 'missing_prepared':
        messages[TOPICS['v2_fill_results']] = results[1:]
    elif fault == 'cancel_as_activate':
        activate.operation = FillCommand.CANCEL
    elif fault == 'only_retry':
        result.result = FillResult.ALREADY_ACTIVATED
        result.committed_sha256 = result_sha256(result)
    elif fault == 'conflicting_retry':
        retry = deepcopy(activate); retry.candidate_id += 1
        commands.append((100, retry))
    elif fault == 'missing_snapshot':
        messages[TOPICS['v2_candidate_snapshots']] = []
    elif fault == 'missing_canonical':
        messages[TOPICS['gaussian_fills']] = []
    elif fault == 'wrong_fill':
        event.fill_id += 1
    elif fault in ('wrong_cluster', 'wrong_revision', 'wrong_generation', 'wrong_amplitude'):
        index = ['wrong_cluster', 'wrong_revision', 'wrong_generation', 'wrong_amplitude'].index(fault)
        event.values[index] += 1.
    elif fault == 'wrong_source':
        event.source_timestamp += 5e-10  # Exact-source semantics reject even a sub-ns change.
    elif fault == 'unavailable_source':
        event.source_timestamp_valid = False
    elif fault == 'nan_source':
        event.source_timestamp = float('nan')
    elif fault == 'wrong_kind':
        event.event_type = event.EVENT_FILL_MERGED
    elif fault == 'duplicate_event':
        messages[EVENT_TOPIC].append((100, deepcopy(event)))
    elif fault == 'duplicate_value_name':
        event.value_names[1] = event.value_names[0]
    elif fault == 'before_commit':
        event.stamp = time_at(9.049)
    elif fault == 'before_activation':
        activate.stamp = time_at(9.051)
    elif fault == 'future_only_mirror':
        messages[TOPICS['gaussian_fills']][0][1].stamp = time_at(9.051)
    elif fault == 'self_consistent_wrong_fill_source':
        # Rehash a mutually matching event/result/mirror: only the original
        # confirmation/Timekeeper source binding distinguishes this forgery.
        result.fill.source_timestamp += .001
        result.registry_digest_after = fill_registry_digest([result.fill])
        result.committed_sha256 = result_sha256(result)
        event.source_timestamp = result.fill.source_timestamp
        messages[TOPICS['gaussian_fills']] = [(15, deepcopy(result.fill))]
    errors, metrics = strict_check(messages, identity)
    assert errors, fault
    assert not metrics['fill_event_source_causality']['passed'], fault


def test_actual_postcommit_cancel_retry_has_one_original_event():
    messages, identity = producer_messages(postcommit_cancel=True)
    errors, metrics = strict_check(messages, identity)
    assert not errors
    assert len(metrics['fill_event_source_causality']['events']) == 1
    del messages[TOPICS['v2_fill_results']][1]  # Retry is not original commit authority.
    assert strict_check(messages, identity)[0]


@pytest.mark.parametrize('fault', ['new_cancel_claims_activated', 'new_activate_claims_activated',
                                 'same_sequence_changes_result_kind', 'postcommit_same_sequence_rejected'])
def test_postcommit_reply_cannot_relabel_original_activation(fault):
    messages, identity = producer_messages(postcommit_cancel=True)
    commands, results = messages[TOPICS['v2_fill_commands']], messages[TOPICS['v2_fill_results']]
    if fault == 'postcommit_same_sequence_rejected':
        results.append((100, response(commands[-1][1], FillResult.REJECTED, 9.1)))
    elif fault == 'same_sequence_changes_result_kind':
        forged = deepcopy(results[1][1])
        forged.result = FillResult.ALREADY_ACTIVATED
        forged.committed_sha256 = result_sha256(forged)
        results.append((100, forged))
    else:
        if fault == 'new_activate_claims_activated':
            commands[-1][1].operation = FillCommand.ACTIVATE
        results[-1][1].result = FillResult.ACTIVATED
        results[-1][1].committed_sha256 = result_sha256(results[-1][1])
    assert strict_check(messages, identity)[0], fault


def test_postcommit_reply_cannot_borrow_another_preparation_identity():
    messages, identity = producer_messages()
    commands, results = messages[TOPICS['v2_fill_commands']], messages[TOPICS['v2_fill_results']]
    foreign = deepcopy(commands[0][1])
    foreign.command_sequence, foreign.preparation_id, foreign.candidate_id = 3, 2, 2
    foreign.snapshot.candidate_id = 2
    foreign.snapshot.evidence_sha256 = snapshot_sha256(foreign.snapshot)
    foreign.evidence_sha256 = foreign.snapshot.evidence_sha256
    messages[TOPICS['v2_candidate_snapshots']].append((50, deepcopy(foreign.snapshot)))
    prepared = deepcopy(results[0][1])
    prepared.command_sequence, prepared.preparation_id, prepared.candidate_id = 3, 2, 2
    prepared.evidence_sha256, prepared.prepared_sha256 = foreign.evidence_sha256, 'b'*64
    prepared.committed_sha256 = result_sha256(prepared)
    cancel = deepcopy(foreign); cancel.operation, cancel.command_sequence = FillCommand.CANCEL, 4
    reply = deepcopy(results[1][1])
    reply.command_sequence, reply.preparation_id, reply.candidate_id = 4, 2, 2
    reply.result = FillResult.ALREADY_ACTIVATED
    reply.evidence_sha256, reply.prepared_sha256 = foreign.evidence_sha256, prepared.prepared_sha256
    reply.committed_sha256 = result_sha256(reply)
    commands.extend([(51, foreign), (52, cancel)])
    results.extend([(53, prepared), (54, reply)])
    # The old standalone audit still shows this targeted selected-contract gap;
    # the strict selected route must bind the original transaction as well.
    assert not lifecycle_stream_errors(messages, identity)[0]
    errors, _ = strict_check(messages, identity)
    assert any('changed original transaction identity' in error for error in errors), errors


def test_exact_original_result_replay_and_queued_cancel_remain_valid():
    messages, identity = producer_messages(postcommit_cancel=True)
    messages[TOPICS['v2_fill_results']].append((100, deepcopy(messages[TOPICS['v2_fill_results']][1][1])))
    # Publication before commit does not imply owner receipt before commit.
    messages[TOPICS['v2_fill_commands']][-1][1].stamp = time_at(9.04)
    assert not strict_check(messages, identity)[0]


@pytest.mark.parametrize('operation', [FillCommand.ACTIVATE, FillCommand.CANCEL])
def test_earlier_command_sequence_cannot_claim_postcommit_reply(operation):
    messages, identity = producer_messages()
    commands, results = messages[TOPICS['v2_fill_commands']], messages[TOPICS['v2_fill_results']]
    prior_command = deepcopy(commands[-1][1])
    prior_command.operation, prior_command.command_sequence = operation, 2
    prior_command.stamp = time_at(9.04)
    commands[-1][1].command_sequence = 3
    results[-1][1].command_sequence = 3
    results[-1][1].committed_sha256 = result_sha256(results[-1][1])
    commands.insert(1, (11, prior_command))
    reply = deepcopy(results[-1][1])
    reply.command_sequence, reply.result = 2, FillResult.ALREADY_ACTIVATED
    reply.stamp = time_at(9.1)
    reply.committed_sha256 = result_sha256(reply)
    results.append((100, reply))
    # Publication order alone is insufficient: the single owner cannot process
    # the earlier sequence as a new command after committing a later sequence.
    assert not lifecycle_stream_errors(messages, identity)[0]
    assert strict_check(messages, identity)[0]


@pytest.mark.parametrize('terminal', [FillResult.CANCELLED, FillResult.EXPIRED])
def test_prepare_may_publish_a_later_terminal_update(terminal):
    messages, identity = producer_messages()
    prepare = messages[TOPICS['v2_fill_commands']][0][1]
    messages[TOPICS['v2_fill_commands']] = messages[TOPICS['v2_fill_commands']][:1]
    messages[TOPICS['v2_fill_results']] = messages[TOPICS['v2_fill_results']][:1]
    messages[TOPICS['v2_fill_results']].append((100, response(prepare, terminal, 9.1)))
    messages[TOPICS['gaussian_fills']] = []
    messages[EVENT_TOPIC] = []
    assert not strict_check(messages, identity)[0]


def test_legacy_recording_and_standalone_audit_keep_their_defaults(tmp_path, monkeypatch):
    messages, identity = producer_messages()
    assert not lifecycle_stream_errors(messages, identity)[0]
    assert 'fill_event_source_causality' not in lifecycle_stream_errors(messages, identity)[1]
    event = messages[EVENT_TOPIC][0][1]
    assert validator.fill_event_source_causality(messages[EVENT_TOPIC], [])
    request = SimpleNamespace(timestamp=event.source_timestamp)
    assert not validator.fill_event_source_causality(messages[EVENT_TOPIC], [(1, request)])
    result = selected_report(tmp_path, monkeypatch, messages, identity, selected=False)
    assert not result['checks']['algorithm_event_source_causality']['passed']


@pytest.mark.parametrize('failure', ['missing_identity', 'bad_identity', 'lifecycle_exception'])
def test_selected_recording_never_falls_back_to_legacy_requests(tmp_path, monkeypatch, failure):
    messages, identity = producer_messages()
    event = messages[EVENT_TOPIC][0][1]
    messages['/gesc_gaussian/fill_requests'] = [(1, SimpleNamespace(timestamp=event.source_timestamp))]
    if failure == 'missing_identity':
        monkeypatch.setattr(validator, 'v2_identity_from_metadata', lambda _metadata: None)
    elif failure == 'bad_identity':
        monkeypatch.setattr(validator, 'v2_identity_from_metadata', lambda _metadata: (_ for _ in ()).throw(ValueError('bad identity')))
    else:
        monkeypatch.setattr(validator, 'lifecycle_stream_errors', lambda *args, **kwargs: (_ for _ in ()).throw(ValueError('bad lifecycle')))
    result = selected_report(tmp_path, monkeypatch, messages, identity)
    assert not result['checks']['algorithm_event_source_causality']['passed']


def test_missing_owner_event_is_not_a_new_occurrence_requirement():
    messages, identity = producer_messages()
    messages[EVENT_TOPIC] = []
    errors, metrics = strict_check(messages, identity)
    assert not errors
    assert metrics['fill_event_source_causality'] == {'passed': True, 'errors': [], 'events': []}


@pytest.mark.parametrize('fault', [None, 'wrong_predecessor', 'wrong_old_source',
                                 'reversed_events', 'missing_old_mirror', 'wrong_new_fill'])
def test_actual_redesign_binds_predecessor_and_owner_event_order(fault):
    messages, identity = producer_messages(redesign=True)
    old, merged = [row[1] for row in messages[EVENT_TOPIC][1:]]
    assert (old.event_type, merged.event_type) == (old.EVENT_FILL_SUPERSEDED, merged.EVENT_FILL_MERGED)
    if fault == 'wrong_predecessor':
        result = messages[TOPICS['v2_fill_results']][-1][1]
        result.superseded_fill.center_x += .001
        result.committed_sha256 = result_sha256(result)
    elif fault == 'wrong_old_source':
        old.source_timestamp += .001
    elif fault == 'reversed_events':
        messages[EVENT_TOPIC][1:] = list(reversed(messages[EVENT_TOPIC][1:]))
    elif fault == 'missing_old_mirror':
        messages[TOPICS['gaussian_fills']] = [row for row in messages[TOPICS['gaussian_fills']] if not row[1].superseded]
    elif fault == 'wrong_new_fill':
        old.values[-1] += 1.
    errors, metrics = strict_check(messages, identity)
    assert bool(errors) is (fault is not None), errors
    if fault is None:
        assert [row['event_type'] for row in metrics['fill_event_source_causality']['events']] == [20, 23, 22]
        assert [row['registry_generation'] for row in metrics['fill_event_source_causality']['events']] == [1, 2, 2]


@pytest.mark.parametrize('fault', [None, 'swapped_sources', 'superseded_uses_current', 'merged_uses_old'])
def test_actual_distinct_confirmation_redesign_keeps_old_and_new_sources(fault):
    messages, identity = producer_messages(redesign=True, distinct_confirmation=True)
    original, superseded, merged = [row[1] for row in messages[EVENT_TOPIC]]
    assert original.source_timestamp == superseded.source_timestamp == 6.
    assert merged.source_timestamp == 26.
    initial_errors, _ = strict_check(messages, identity)
    assert not initial_errors, initial_errors
    if fault == 'swapped_sources':
        superseded.source_timestamp, merged.source_timestamp = merged.source_timestamp, superseded.source_timestamp
    elif fault == 'superseded_uses_current':
        superseded.source_timestamp = merged.source_timestamp
    elif fault == 'merged_uses_old':
        merged.source_timestamp = superseded.source_timestamp
    errors, metrics = strict_check(messages, identity)
    assert bool(errors) is (fault is not None), errors
    if fault is None:
        audit = metrics['fill_event_source_causality']['events']
        assert [row['source_timestamp'] for row in audit] == [6., 6., 26.]
        assert [row['search_epoch'] for row in audit] == [1, 2, 2]


def test_actual_gaussian_dds_publications_reach_selected_recording_gate(tmp_path, monkeypatch):
    """Actual Gaussian node and DDS; deterministic pure-worker proposal only."""
    import time
    import rclpy
    from nav_msgs.msg import Odometry
    from rclpy.executors import SingleThreadedExecutor
    from rclpy.node import Node as RosNode
    from rosgraph_msgs.msg import Clock
    from ros_esc_interfaces.msg import AlgorithmEvent, GaussianFill, SearchEpochContext

    messages, identity, prepare, *_ = fixture('pde_mean_v1', activated=False)
    config = identity['stream_config']
    params = {'use_sim_time': 'true', 'algorithm_profile': 'robust_gaussian_v1',
        'continuous_search_mode': 'rolling_gesc_v2', 'enable_observability': 'true',
        'v2_run_id': identity['run_id'], 'v2_stream_config_json': "'"+canonical_json(config)+"'",
        'pose_topic': config['pose_topic'], 'algorithm_state_topic': '/m4_v5/state',
        'source_cost_topic': config['source_cost_topic'],
        'gaussian_fill_diagnostics_topic': TOPICS['gaussian_fills'], 'algorithm_event_topic': EVENT_TOPIC}
    args = ['--ros-args']
    for name, value in params.items():
        args.extend(['-p', name+':='+value])
    monkeypatch.setenv('ROS_DOMAIN_ID', '186')
    rclpy.init(args=args)
    executor = SingleThreadedExecutor()
    nodes = []
    try:
        gaussian = GaussianOwner(); nodes.append(gaussian)
        # This test isolates transport and authoritative publication, leaving
        # estimator/designer coverage to the retained actual-worker regressions.
        gaussian.v2_fill.pool.shutdown(wait=True, cancel_futures=True)
        worker = Worker(); gaussian.v2_fill.pool = worker
        driver = RosNode('m4_v5_typed_authority_driver', use_global_arguments=False)
        nodes.append(driver)
        for node in nodes:
            executor.add_node(node)
        captured = {topic: [] for topic in [TOPICS['v2_fill_results'], TOPICS['gaussian_fills'], EVENT_TOPIC]}
        for kind, topic in [(FillResult, TOPICS['v2_fill_results']), (GaussianFill, TOPICS['gaussian_fills']),
                            (AlgorithmEvent, EVENT_TOPIC)]:
            driver.create_subscription(kind, topic, captured[topic].append, 100)
        publishers = {name: driver.create_publisher(kind, topic, 100) for name, kind, topic in [
            ('clock', Clock, '/clock'), ('timekeeper', Timekeeper, config['timekeeper_topic']),
            ('context', SearchEpochContext, TOPICS['v2_search_epoch']), ('state', AlgorithmState, '/m4_v5/state'),
            ('pose', Odometry, config['pose_topic']), ('command', FillCommand, TOPICS['v2_fill_commands'])]}
        deadline = time.monotonic()+40.

        def until(predicate):
            end = min(deadline, time.monotonic()+8.)
            while not predicate() and time.monotonic() < end:
                executor.spin_once(timeout_sec=.005)
            assert predicate(), [(r.result, r.reason) for r in captured[TOPICS['v2_fill_results']]]

        until(lambda: all(p.get_subscription_count() for p in publishers.values()))
        publishers['clock'].publish(Clock(clock=time_at(9.05)))
        until(lambda: gaussian.get_clock().now().nanoseconds == 9_050_000_000)
        publishers['timekeeper'].publish(Timekeeper(mode='sim time', start_time=0.))
        until(lambda: gaussian.v2_fill.origin_ns == 0)
        context = deepcopy(messages[TOPICS['v2_search_epoch']][0][1])
        context.context_sequence, context.algorithm_state, context.stamp = 2, 3, time_at(9.05)
        publishers['context'].publish(context)
        messages[TOPICS['v2_search_epoch']].append((10, context))
        state = AlgorithmState(algorithm_profile='robust_gaussian_v1', run_id=identity['run_id'],
            state=3, previous_state=2, state_valid=True, previous_state_valid=True,
            weights_valid=True, run_id_valid=True, sensor_weight=1., gaussian_weight=1.)
        state.stamp = time_at(9.05); publishers['state'].publish(state)
        pose = deepcopy(messages[config['pose_topic']][-1][1]); pose.header.stamp = time_at(9.05)
        publishers['pose'].publish(pose)
        until(lambda: gaussian.v2_fill.context is not None and gaussian.v2_fill.state is not None and gaussian.v2_fill.poses)
        publishers['command'].publish(prepare)
        until(lambda: gaussian.v2_fill.current is not None)
        proposal = values(); proposal['source_timestamp'] = worker.input.source_timestamp
        worker.future.set_result(PreparedProposal(tuple(proposal.items()), worker.input.samples,
            None, None, worker.input.registry.generation, len(worker.input.samples), ()))
        until(lambda: any(r.result == FillResult.PREPARED for r in captured[TOPICS['v2_fill_results']]))
        activate = deepcopy(prepare); activate.operation, activate.command_sequence = FillCommand.ACTIVATE, 2
        activate.stamp = time_at(9.05)
        activate.prepared_sha256 = captured[TOPICS['v2_fill_results']][0].prepared_sha256
        publishers['command'].publish(activate)
        until(lambda: any(e.event_type == AlgorithmEvent.EVENT_FILL_CREATED for e in captured[EVENT_TOPIC])
              and captured[TOPICS['gaussian_fills']]
              and any(r.result == FillResult.ACTIVATED for r in captured[TOPICS['v2_fill_results']]))
        cancel = deepcopy(activate); cancel.operation, cancel.command_sequence = FillCommand.CANCEL, 3
        publishers['command'].publish(cancel)
        until(lambda: any(r.result == FillResult.ALREADY_ACTIVATED for r in captured[TOPICS['v2_fill_results']]))
        messages[TOPICS['v2_fill_commands']] = [(11, prepare), (12, activate), (13, cancel)]
        for topic, values_ in captured.items():
            messages[topic] = list(enumerate(values_, 15))
        messages = {topic: [(stamp, deserialize_message(serialize_message(msg), type(msg))) for stamp, msg in rows]
                    for topic, rows in messages.items()}
        errors, metrics = strict_check(messages, identity)
        assert not errors, errors
        assert len(metrics['fill_event_source_causality']['events']) == 1
        report = selected_report(tmp_path, monkeypatch, messages, identity)
        assert report['checks']['algorithm_event_source_causality']['passed'], report
        assert report['checks']['v2_lifecycle_contract']['passed'], report
    finally:
        for node in nodes:
            executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.try_shutdown()
