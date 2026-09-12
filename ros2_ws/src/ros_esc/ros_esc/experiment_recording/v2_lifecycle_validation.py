"""Recorded M3 wire consistency, subordinate to the existing run validator.

Per-topic order is retained. Cross-topic joins use immutable identities and
source/publication stamps, never pretend bag receipt order is callback order.
This audit does not reconstruct unrecorded owner wall-clock authorization.
"""

import math
import re
from bisect import bisect_left

from ros_esc.v2_lifecycle import (
    FRESHNESS_NS, MAX_COMMANDS, envelope_identity, fill_registry_digest,
    hash_payload, message_payload, observation_payload, result_sha256,
    snapshot_sha256,
    recurrent_proof_payload, recurrent_snapshot_sha256,
)
from ros_esc.v2_stream import relative_stamp_ns, stream_contract_id, time_to_ns
from ros_esc.supervisor_node.state_machine import RotationCostWindow
from ros_esc.convergence_detector_node.centroid_contract import CENTROID_METRIC_MODES
from ros_esc.convergence_detector_node.recurrent_contract import (
    RECURRENT_GEOMETRY_V3, RECURRENT_HISTORY_KIND, RECURRENT_TOPIC,
)
from .record_run import v2_message_identity_error


TOPICS = {
    'v2_search_epoch': '/gesc_gaussian/v2/search_epoch',
    'v2_detector_confirmation': '/gesc_gaussian/v2/detector_confirmation',
    'v2_candidate_snapshots': '/gesc_gaussian/v2/candidate_snapshots',
    'v2_recurrent_candidate_snapshots': '/gesc_gaussian/v2/recurrent_candidate_snapshots',
    'v2_pde_history_evidence': '/gesc_gaussian/v2/pde_history_evidence',
    'v2_fill_commands': '/gesc_gaussian/v2/fill_commands',
    'v2_recurrent_fill_commands': '/gesc_gaussian/v2/recurrent_fill_commands',
    'v2_fill_results': '/gesc_gaussian/v2/fill_results',
    'v2_direction_diagnostics': '/gesc_gaussian/v2/direction_diagnostics',
    'centroid_convergence_diagnostics': '/gesc_gaussian/v2/convergence_diagnostics',
    'recurrent_convergence_diagnostics': RECURRENT_TOPIC,
    'convergence_status': '/gesc_gaussian/convergence_status',
    'gaussian_fills': '/gesc_gaussian/gaussian_fills',
    'algorithm_state': '/gesc_gaussian/algorithm_state',
    'algorithm_events': '/gesc_gaussian/algorithm_events',
    'v2_verification_guidance': '/gesc_gaussian/v2/verification_guidance',
}


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _finite(*values):
    return all(math.isfinite(float(value)) for value in values)


def _digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _same(left, right):
    return math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-12)


def _commit_key(result):
    return hash_payload({
        'generation': result.registry_generation,
        'before': result.registry_digest_before, 'after': result.registry_digest_after,
        'committed_at': time_to_ns(result.committed_at),
        'fill': message_payload(result.fill),
        'superseded': message_payload(result.superseded_fill) if result.has_superseded_fill else None,
    })


def lifecycle_stream_errors(messages, identity, *, topics=None, metric_mode=None,
                            candidate_cost_mad_scale=3.0, validate_fill_events=False,
                            moving_verification_mode='rolling_neighborhood_v1',
                            verification_evidence_policy='angular_profiles_v1'):
    """Return ``(errors, metrics)`` for already deserialized bag topic records.

``messages`` has the existing reader shape ``topic: [(bag_ns, wire), ...]``.
``topics`` optionally maps manifest aliases to selected topic strings. Missing
event messages are valid; topic registration/type checks remain in validate_run.
Metrics are audit tables, not detector sensitivity or behavioral acceptance.
The selected recording route enables ``validate_fill_events`` to bind Gaussian
owner events and committed source times to this same admitted transaction chain.
The historical standalone audit/default does not change its event requirements.
Selected centered verification requires its actual immutable collection admission
event; historical snapshots never infer a new deadline from their duration.
"""
    selected = dict(TOPICS)
    selected.update({key: value for key, value in (topics or {}).items() if value})
    config = identity['stream_config']
    errors = []
    metrics = {'epochs': [], 'confirmations': [], 'candidates': [], 'preparations': [],
               'commits': [], 'counts': {}, 'acknowledgements': [],
               'timing_scope': 'source/publication timestamps; bag receipts are not callback receipts'}
    if validate_fill_events:
        metrics['fill_event_source_causality'] = {
            'passed': False, 'errors': ['selected moving lifecycle authority unavailable'], 'events': []}
    candidate_cost_mad_scale = float(candidate_cost_mad_scale)
    if not math.isfinite(candidate_cost_mad_scale) or candidate_cost_mad_scale < 0:
        return ['V2 lifecycle invalid resolved candidate_cost_mad_scale'], metrics
    metrics['candidate_cost_mad_scale'] = candidate_cost_mad_scale
    if metric_mode is not None and metric_mode not in (
            'pde_mean_v1', *CENTROID_METRIC_MODES, RECURRENT_GEOMETRY_V3):
        return ['V2 lifecycle unknown selected detector metric'], metrics
    if moving_verification_mode not in ('rolling_neighborhood_v1', 'centered_tracking_v1'):
        return ['V2 lifecycle unknown selected moving verification mode'], metrics
    centered_verification = moving_verification_mode == 'centered_tracking_v1'
    if verification_evidence_policy not in ('angular_profiles_v1', 'recurrent_trapping_v1'):
        return ['V2 lifecycle unknown verification evidence policy'], metrics
    trapping = verification_evidence_policy == 'recurrent_trapping_v1'
    if trapping and (metric_mode != RECURRENT_GEOMETRY_V3 or not centered_verification):
        return ['V2 lifecycle trapping policy requires recurrent centered selection'], metrics
    if trapping:
        metrics['verification_evidence_policy'] = verification_evidence_policy
    if centered_verification:
        metrics['moving_verification_mode'] = moving_verification_mode
        metrics['verification_collection_admissions'] = []

    wrapped_rows, proofs = {}, {}
    for plain, wrapped, member in (
            ('v2_candidate_snapshots', 'v2_recurrent_candidate_snapshots', 'snapshot'),
            ('v2_fill_commands', 'v2_recurrent_fill_commands', 'command')):
        records = messages.get(selected[wrapped], [])
        if not trapping:
            if records:
                errors.append('V2 lifecycle unselected recurrent wrapper stream')
            continue
        if messages.get(selected[plain], []):
            errors.append('V2 lifecycle legacy transaction stream under trapping selection')
        wrapped_rows[plain] = []
        for _, wrapper in records:
            try:
                recurrent_proof_payload(wrapper)
                inner = getattr(wrapper, member)
                proofs[id(inner)] = wrapper
                wrapped_rows[plain].append(inner)
            except (ValueError, TypeError, AttributeError) as exc:
                errors.append('V2 lifecycle invalid recurrent wrapper: '+str(exc))

    def rows(alias):
        if alias in wrapped_rows:
            return wrapped_rows[alias]
        return [message for _, message in messages.get(selected.get(alias, alias), [])]

    def audit(kind, callback, message):
        try:
            callback(message)
        except (ValueError, TypeError, AttributeError, OverflowError, IndexError, KeyError) as exc:
            errors.append('V2 lifecycle ' + kind + ': ' + str(exc))

    origins = []
    for message in rows(config['timekeeper_topic']):
        try:
            _require(message.mode == 'sim time', 'simulation origin mode')
            origins.append(relative_stamp_ns(0, message.start_time))
        except (ValueError, TypeError, AttributeError, OverflowError):
            errors.append('V2 lifecycle invalid Timekeeper')
    if not origins or len(set(origins)) != 1:
        errors.append('V2 lifecycle lacks one immutable Timekeeper origin')
        return errors, metrics
    origin = origins[0]

    def envelope(message, *, stream=False, unbound=False):
        error = v2_message_identity_error(
            message, identity, origin, allow_unbound=unbound,
            protocol_version=None if stream else 1)
        _require(error is None, error)
        if not unbound:
            _require(time_to_ns(message.stamp) >= origin, 'publication precedes origin')

    contexts, epochs = {}, {}
    previous_context = [0, 0, origin]

    def epoch(message):
        envelope(message, unbound=not message.valid and not message.stream_contract_id)
        sequence = int(message.context_sequence)
        _require(sequence > 0, 'context sequence must be positive')
        payload = message_payload(message)
        if sequence in contexts:
            _require(contexts[sequence][1] == payload, 'conflicting context sequence')
            return
        _require(sequence > previous_context[0], 'context sequence regression')
        contexts[sequence] = (message, payload)
        previous_context[0] = sequence
        if not message.valid:
            return
        start, publication = time_to_ns(message.started_at), time_to_ns(message.stamp)
        _require(1 <= message.algorithm_state <= 8 and message.search_epoch > 0,
                 'invalid authoritative state or epoch')
        _require(origin <= start <= publication and publication >= previous_context[2],
                 'epoch timestamp regression or bounds')
        _require(message.search_epoch >= previous_context[1], 'authoritative epoch regression')
        if message.search_epoch in epochs:
            _require(epochs[message.search_epoch] == start, 'changed authoritative epoch start')
        else:
            epochs[message.search_epoch] = start
            metrics['epochs'].append({'search_epoch': int(message.search_epoch), 'started_at_ns': start})
        previous_context[1:] = [int(message.search_epoch), publication]

    for message in rows('v2_search_epoch'):
        audit('epoch', epoch, message)
    if not rows('v2_search_epoch'):
        errors.append('V2 lifecycle missing authoritative epoch heartbeat')

    def context_for(message):
        pair = contexts.get(int(message.context_sequence))
        _require(pair is not None, 'referenced context not recorded')
        context = pair[0]
        _require(context.valid and context.algorithm_state == 1,
                 'referenced context is not valid SEARCH')
        _require(envelope_identity(context) == envelope_identity(message), 'context identity differs')
        _require(time_to_ns(context.started_at) == time_to_ns(message.epoch_started_at),
                 'context epoch start differs')
        _require(0 <= time_to_ns(message.stamp)-time_to_ns(context.stamp) <= FRESHNESS_NS,
                 'referenced SEARCH context not fresh at publication')
        return time_to_ns(context.started_at)

    poses = {}
    for pose in rows(config['pose_topic']):
        try:
            key = time_to_ns(pose.header.stamp)
            value = (pose.header.frame_id, pose.pose.pose.position.x, pose.pose.pose.position.y)
            poses[key] = value if key not in poses or poses[key] == value else None
        except (ValueError, AttributeError, TypeError):
            continue
    histories, previous_history = {}, [0]

    def history(message):
        envelope(message)
        payload = hash_payload(message_payload(message, exclude=('stamp', 'history_sha256')))
        _require(_digest(message.history_sha256) and payload == message.history_sha256,
                 'PDE evidence hash/validity')
        sequence = int(message.history_sequence)
        if sequence in histories:
            _require(histories[sequence].history_sha256 == payload, 'conflicting PDE sequence')
            return
        _require(sequence > previous_history[0], 'PDE sequence regression')
        previous_history[0] = sequence
        if not message.valid:
            _require(not message.history.data and message.history.header.startswith('V2_INVALID:'),
                     'invalid PDE wrapper must explicitly invalidate support')
            histories[sequence] = message
            return
        start = context_for(message)
        lo, hi, receipt, publication = [time_to_ns(getattr(message, key)) for key in
                                     ('input_start', 'input_end', 'latest_input_receipt', 'stamp')]
        _require(start <= lo <= hi <= publication and 0 <= receipt <= publication
                 and publication-hi <= FRESHNESS_NS and publication-receipt <= FRESHNESS_NS,
                 'PDE actual support time bounds/freshness')
        _require(len(message.history.data) >= 2 and len(message.history.data) % 2 == 0
                 and _finite(message.history.timestamp, *message.history.data)
                 and abs(round(message.history.timestamp*1e9)-publication) <= 2,
                 'PDE legacy payload or absolute timestamp')
        for stamp in (lo, hi):
            support = poses.get(stamp)
            _require(support is not None and support[0] == config['frame_id']
                     and _finite(*support[1:]), 'PDE bounds lack unambiguous actual pose support')
        histories[sequence] = message

    for message in rows('v2_pde_history_evidence'):
        audit('PDE', history, message)

    if metric_mode == RECURRENT_GEOMETRY_V3 or any(
            getattr(message, 'metric_mode', None) == RECURRENT_GEOMETRY_V3
            for message in rows('v2_detector_confirmation')):
        from ros_esc.convergence_detector_node.recurrent_contract import recurrent_diagnostic_errors
        recurrent_rows = rows('recurrent_convergence_diagnostics')
        if not recurrent_rows:
            errors.append('V2 lifecycle missing selected recurrent diagnostic stream')
        def recurrent_diagnostics(_):
            errors.extend('V2 lifecycle ' + reason for reason in recurrent_diagnostic_errors(
                recurrent_rows, expected_source_pose_topic=config['pose_topic'],
                supervisor_run_ids={identity['run_id']}, expected_frame_id=config['frame_id'],
                expected_metric_mode=RECURRENT_GEOMETRY_V3, allow_clock_admission=True))
        audit('recurrent diagnostic', recurrent_diagnostics, None)

    confirmations, confirmation_epochs, previous_confirmation = {}, {}, [0]

    def confirmation(message):
        envelope(message)
        start = context_for(message)
        sequence = int(message.confirmation_sequence)
        if sequence in confirmations:
            _require(message_payload(confirmations[sequence], exclude=('stamp',)) ==
                     message_payload(message, exclude=('stamp',)), 'conflicting confirmation sequence')
            return
        _require(sequence > previous_confirmation[0], 'confirmation sequence regression')
        _require(message.search_epoch not in confirmation_epochs, 'multiple confirmations in one epoch')
        _require(message.valid and message.source_stamp_kind == 'pose_input'
                 and _finite(message.center_x_m, message.center_y_m), 'invalid confirmation')
        lo, hi, source, publication = [time_to_ns(getattr(message, key)) for key in
                                    ('history_start', 'history_end', 'source_stamp', 'stamp')]
        _require(start <= lo <= hi == source <= publication and publication-source <= FRESHNESS_NS,
                 'confirmation complete support bounds/freshness')
        _require(metric_mode is None or metric_mode == message.metric_mode, 'selected detector metric differs')
        if message.metric_mode == 'pde_mean_v1':
            _require(message.history_kind == 'pde_input_support' and message.legacy_r_mean_valid
                     and len(message.legacy_snapshot) == 8 and _finite(message.legacy_r_mean_m2, *message.legacy_snapshot)
                     and _same(message.legacy_snapshot[1], message.legacy_r_mean_m2)
                     and _same(message.legacy_snapshot[3], message.center_x_m)
                     and _same(message.legacy_snapshot[4], message.center_y_m), 'legacy confirmation snapshot')
            support = [h for h in histories.values() if h.search_epoch == message.search_epoch
                       and time_to_ns(h.stamp) <= publication]
            matching = [h for h in support if h.valid and time_to_ns(h.input_start) == lo
                        and time_to_ns(h.input_end) == hi]
            _require(matching and not any(not h.valid and h.history_sequence > max(
                item.history_sequence for item in matching) for h in support),
                'legacy confirmation lacks matching unrevoked PDE support')
            _require(any(list(m.data) == list(message.legacy_snapshot) for m in rows('convergence_status')),
                     'legacy confirmation snapshot lacks canonical observation mirror')
        elif message.metric_mode in CENTROID_METRIC_MODES:
            _require(message.history_kind == 'centroid_windows' and message.convergence_score_valid
                     and _finite(message.convergence_score_m) and message.convergence_score_m >= 0,
                     'centroid confirmation metric')
            _require(any(d.confirmed and d.metric_valid and time_to_ns(d.history_start) == lo
                         and time_to_ns(d.history_end) == hi and _same(d.center_x_m, message.center_x_m)
                         and _same(d.center_y_m, message.center_y_m) and _same(d.score_m, message.convergence_score_m)
                         and d.run_id == message.run_id
                         and d.metric_mode == message.metric_mode
                         for d in rows('centroid_convergence_diagnostics')),
                     'centroid confirmation lacks matching diagnostic support')
        elif message.metric_mode == RECURRENT_GEOMETRY_V3:
            _require(message.history_kind == RECURRENT_HISTORY_KIND and message.convergence_score_valid
                     and _finite(message.convergence_score_m) and message.convergence_score_m >= 0
                     and not message.legacy_r_mean_valid and not message.legacy_snapshot,
                     'recurrent confirmation metric/history differs')
            if trapping:
                from ros_esc.convergence_detector_node.recurrent_contract import recurrent_nomination_errors
                _require(any(not recurrent_nomination_errors(message, d,
                    expected_source_pose_topic=config['pose_topic'], epoch_start_ns=start)
                    for d in rows('recurrent_convergence_diagnostics')),
                    'recurrent trapping confirmation lacks matching original diagnostic')
            else:
                _require(any(d.confirmed and d.eligible and d.metric_valid
                         and d.run_id == message.run_id and d.frame_id == message.frame_id
                         and d.metric_mode == message.metric_mode and d.search_epoch == message.search_epoch
                         and d.confirmation_sequence == message.confirmation_sequence
                         and time_to_ns(d.epoch_started_at) == start
                         and time_to_ns(d.history_start) == lo and time_to_ns(d.history_end) == hi
                         and time_to_ns(d.stamp) <= publication
                         and _same(d.center_x_m, message.center_x_m)
                         and _same(d.center_y_m, message.center_y_m)
                         and _same(d.score_m, message.convergence_score_m)
                         for d in rows('recurrent_convergence_diagnostics')),
                         'recurrent confirmation lacks matching typed diagnostic support')
        else:
            raise ValueError('unknown confirmation metric')
        confirmations[sequence] = message
        confirmation_epochs[message.search_epoch] = sequence
        previous_confirmation[0] = sequence
        metrics['confirmations'].append({'search_epoch': int(message.search_epoch),
            'confirmation_sequence': sequence, 'metric_mode': message.metric_mode,
            'history_start_ns': lo, 'source_stamp_ns': source, 'published_at_ns': publication})

    for message in rows('v2_detector_confirmation'):
        audit('confirmation', confirmation, message)

    observations = {}
    for diagnostic in rows('v2_direction_diagnostics'):
        try:
            observation = diagnostic.observation
            if not (diagnostic.algorithm_state_valid and 1 <= diagnostic.algorithm_state <= 5
                    and observation.synchronized_valid and observation.raw_cost_valid
                    and observation.sensor_transform_observed):
                continue
            envelope(diagnostic, stream=True)
            envelope(observation, stream=True)
            key = (int(observation.observation_id), int(observation.source_sequence))
            fingerprint = hash_payload(observation_payload(observation))
            if key in observations:
                _require(observations[key][0] == fingerprint, 'conflicting recorded observation identity')
                observations[key][1].add((int(diagnostic.algorithm_state), time_to_ns(diagnostic.stamp)))
                continue
            observations[key] = (fingerprint, {(int(diagnostic.algorithm_state), time_to_ns(diagnostic.stamp))}, observation)
        except (ValueError, TypeError, AttributeError, OverflowError) as exc:
            errors.append('V2 lifecycle observation: ' + str(exc))

    provenance = {}
    revoked = set()
    for message in rows(config['provenance_topic']):
        try:
            envelope(message, stream=True)
            key = (int(message.source_sequence), time_to_ns(message.model_input_stamp))
            if not message.model_input_stamp_valid or not message.sensor_transform_valid:
                revoked.add(key[1])  # Notices consume a new sequence; source identity stays poisoned.
            elif key not in provenance:
                provenance[key] = message
        except (ValueError, TypeError, AttributeError, OverflowError):
            continue  # Strict M2 validation reports malformed independent sources.

    collection_admissions = {}
    def collection_admission(message):
        _require(message.detail == 'moving verification collection admitted'
                 and message.state_valid and message.state == 2
                 and message.state_name == 'VERIFY_EXTREMUM',
                 'collection admission detail/state differs')
        _require(list(message.value_names) == ['candidate_id', 'search_epoch']
                 and len(message.values) == 2 and _finite(*message.values)
                 and all(0 < value <= MAX_COMMANDS and float(value).is_integer()
                         for value in message.values),
                 'collection admission candidate/epoch fields malformed')
        candidate, search_epoch = (int(value) for value in message.values)
        stamp = time_to_ns(message.stamp)
        _require(search_epoch in epochs and epochs[search_epoch] <= stamp,
                 'collection admission epoch/time differs')
        previous = collection_admissions.get(candidate)
        _require(previous is None or previous == (search_epoch, stamp),
                 'conflicting repeated collection admission')
        if previous is None:
            _require(len(collection_admissions) < MAX_COMMANDS,
                     'collection admission capacity')
            collection_admissions[candidate] = (search_epoch, stamp)
            metrics['verification_collection_admissions'].append({
                'candidate_id': candidate, 'search_epoch': search_epoch,
                'collection_admitted_at_ns': stamp})

    if centered_verification:
        for message in rows('algorithm_events'):
            if message is not None and getattr(message, 'event_type', None) == 12:
                audit('verification stage', collection_admission, message)

    claimed_filter_provenance = {}
    def snapshot(snap, command=None):
        envelope(snap)
        if command is not None:
            _require(envelope_identity(snap) == envelope_identity(command)
                     and snap.candidate_id == command.candidate_id
                     and snap.objective_revision == command.objective_revision
                     and snap.evidence_sha256 == command.evidence_sha256,
                     'snapshot command identity differs')
        proof = proofs.get(id(command if command is not None else snap))
        computed_hash = (recurrent_snapshot_sha256(snap, proof) if trapping
                         else snapshot_sha256(snap))
        _require(_digest(snap.evidence_sha256)
                 and computed_hash == snap.evidence_sha256, 'snapshot evidence hash differs')
        confirm = confirmations.get(int(snap.detector_confirmation_sequence))
        _require(confirm is not None and confirm.search_epoch == snap.search_epoch, 'snapshot confirmation missing')
        if trapping:
            from ros_esc.convergence_detector_node.recurrent_contract import recurrent_nomination_errors
            _require(message_payload(proof.confirmation) == message_payload(confirm),
                     'trapping proof differs from recorded confirmation')
            _require(any(message_payload(d) == message_payload(proof.diagnostic)
                         for d in rows('recurrent_convergence_diagnostics')),
                     'trapping proof differs from recorded diagnostic')
            _require(not recurrent_nomination_errors(proof.confirmation, proof.diagnostic,
                expected_source_pose_topic=config['pose_topic'],
                epoch_start_ns=time_to_ns(confirm.epoch_started_at)),
                'invalid recurrent trapping nomination proof')
        _require(snap.metric_mode == confirm.metric_mode
                 and time_to_ns(snap.confirmation_stamp) == time_to_ns(confirm.source_stamp)
                 and _same(snap.center_x_m, confirm.center_x_m) and _same(snap.center_y_m, confirm.center_y_m),
                 'snapshot frozen confirmation differs')
        _require(snap.convergence_score_valid == confirm.convergence_score_valid
                 and snap.legacy_r_mean_valid == confirm.legacy_r_mean_valid
                 and (not snap.convergence_score_valid or _same(snap.convergence_score_m, confirm.convergence_score_m))
                 and (not snap.legacy_r_mean_valid or _same(snap.legacy_r_mean_m2, confirm.legacy_r_mean_m2)),
                 'snapshot frozen detector metric differs')
        publication, accepted = time_to_ns(snap.stamp), time_to_ns(snap.accepted_at)
        _require(time_to_ns(confirm.stamp) <= accepted <= publication
                 and (command is None or publication <= time_to_ns(command.stamp))
                 and accepted-time_to_ns(confirm.source_stamp) <= FRESHNESS_NS,
                 'candidate acceptance/publication time bounds')
        if snap.snapshot_revision == 1 and centered_verification:
            admission = collection_admissions.get(int(snap.candidate_id))
            _require(admission is not None and admission[0] == snap.search_epoch,
                     'initial verification lacks matching collection admission')
            admitted = admission[1]
            _require(accepted <= admitted <= accepted+8_000_000_000,
                     'initial verification approach admission exceeded original deadline')
            _require(admitted <= publication <= admitted+12_000_000_000,
                     'initial verification collection publication exceeded first admission deadline')
            _require(publication <= accepted+20_000_000_000,
                     'initial verification extended original absolute deadline')
        else:
            _require(snap.snapshot_revision > 1 or publication <= accepted+12_000_000_000,
                     'initial verification extended original deadline')
        _require(snap.snapshot_revision > 0 and snap.completed_revolutions == 3
                 and snap.pretrigger_revolutions+snap.verification_revolutions == 3,
                 'snapshot revision or three-cycle counts')
        numeric = [getattr(snap, key) for key in ('neighborhood_radius_m', 'centroid_tolerance_m',
            'candidate_cost_estimate', 'candidate_cost_mad', 'candidate_cost_uncertainty',
            'candidate_cost_lower', 'candidate_cost_upper', 'information_amplitude',
            'information_disagreement', 'information_floor')]
        _require(_finite(*numeric) and min(numeric[:2]) > 0 and (trapping or snap.informative)
                 and snap.information_floor >= 1e-6 and snap.information_disagreement >= 0
                 and snap.information_amplitude >= 0
                 and (trapping or snap.information_amplitude > max(3*snap.information_disagreement, snap.information_floor))
                 and snap.candidate_cost_lower <= snap.candidate_cost_estimate <= snap.candidate_cost_upper
                 and snap.candidate_cost_upper < -snap.information_floor
                 and min(snap.candidate_cost_mad, snap.candidate_cost_uncertainty) >= 0,
                 'snapshot finite informative negative-cost contract')
        if trapping:
            from ros_esc.supervisor_node.moving_evidence import snapshot_raw_evidence
            reproduced = snapshot_raw_evidence(snap, evidence_policy=verification_evidence_policy,
                                              mad_scale=candidate_cost_mad_scale)
            _require(reproduced.ready, 'trapping raw snapshot quality unavailable')
        count = len(snap.observations)
        _require(0 < count <= 4000 and len(snap.observation_filter_state) == count
                 and len(snap.observation_filter_stamp) == count, 'snapshot observation capacity/parallel arrays')
        _require(all(len(getattr(snap, key)) == 3 for key in ('revolution_start', 'revolution_end',
                    'revolution_sample_start', 'revolution_sample_end')), 'snapshot revolution arrays')
        stamps, ids = [], set()
        for obs, state, first_stamp in zip(snap.observations, snap.observation_filter_state,
                                          snap.observation_filter_stamp):
            envelope(obs, stream=True)
            key = (int(obs.observation_id), int(obs.source_sequence))
            recorded = observations.get(key)
            _require(key not in ids and min(key) > 0, 'duplicate snapshot observation identity')
            ids.add(key)
            claimed = (state, time_to_ns(first_stamp))
            _require(recorded is not None and recorded[0] == hash_payload(observation_payload(obs))
                     and claimed in recorded[1],
                     'snapshot does not match a recorded filter observation/state/stamp')
            prior_claim = claimed_filter_provenance.get((int(snap.candidate_id), *key))
            _require(prior_claim is None or prior_claim == claimed,
                     'snapshot revision changed first supervisor-received filter provenance')
            source = time_to_ns(obs.source_stamp)
            _require((obs.source_sequence, source) in provenance and source not in revoked,
                     'snapshot source provenance missing or revoked')
            prov = provenance[(obs.source_sequence, source)]
            _require(prov.legacy_cost_source_timestamp_sec == obs.legacy_cost_source_timestamp_sec,
                     'snapshot source key differs from provenance')
            _require(epochs[snap.search_epoch] <= source <= time_to_ns(obs.admission_stamp)
                     <= time_to_ns(first_stamp) <= publication, 'snapshot source/admission/filter times')
            _require(_finite(obs.base_x_m, obs.base_y_m, obs.raw_cost), 'nonfinite snapshot support')
            _require(not stamps or source > stamps[-1], 'snapshot source regression/duplicate')
            stamps.append(source)
        _require(snap.objective_revision > 0 and snap.objective_revision == snap.observations[-1].objective_revision,
                 'snapshot latest objective revision differs')
        _require(_same(snap.information_floor, max(1e-6, 64*max(math.ulp(obs.raw_cost) for obs in snap.observations))),
                 'snapshot raw-unit numerical information floor differs')
        lo, hi = time_to_ns(snap.evidence_start), time_to_ns(snap.evidence_end)
        _require(stamps[0] <= lo < hi <= stamps[-1] and hi <= publication,
                 'snapshot boundary brackets missing')
        previous_end, assigned, minima = None, set(), []
        pre = 0
        def boundary_xy(stamp):
            right = bisect_left(stamps, stamp)
            obs = snap.observations[right]
            if stamps[right] == stamp:
                return obs.base_x_m, obs.base_y_m
            left = right-1
            _require(left >= 0 and stamps[right]-stamps[left] <= FRESHNESS_NS,
                     'snapshot boundary source gap')
            prior = snap.observations[left]
            alpha = (stamp-stamps[left])/(stamps[right]-stamps[left])
            return (prior.base_x_m+alpha*(obs.base_x_m-prior.base_x_m),
                    prior.base_y_m+alpha*(obs.base_y_m-prior.base_y_m))
        for start, end, left, right in zip(snap.revolution_start, snap.revolution_end,
                                         snap.revolution_sample_start, snap.revolution_sample_end):
            start, end = time_to_ns(start), time_to_ns(end)
            _require(lo <= start < end <= hi and end-start <= 30_000_000_000
                     and (previous_end is None or previous_end <= start), 'snapshot cycle overlap/bounds')
            actual = [index for index, stamp in enumerate(stamps) if start <= stamp < end]
            _require(actual == list(range(left, right)) and len(actual) >= 24
                     and not assigned.intersection(actual), 'snapshot half-open actual support assignment')
            represented = [boundary_xy(start), boundary_xy(end)] + [
                (snap.observations[index].base_x_m, snap.observations[index].base_y_m) for index in actual]
            _require(all(math.dist(point, (snap.center_x_m, snap.center_y_m)) <=
                         snap.neighborhood_radius_m+1e-12 for point in represented),
                     'represented snapshot position outside frozen neighborhood')
            involved = [index for index in range(len(stamps)-1)
                        if stamps[index] < end and stamps[index+1] > start]
            _require(all(stamps[index+1]-stamps[index] <= FRESHNESS_NS for index in involved),
                     'snapshot represented source gap')
            assigned.update(actual)
            minima.append(min(snap.observations[index].raw_cost for index in actual))
            previous_end = end
            pre += end <= time_to_ns(snap.confirmation_stamp)
        _require(time_to_ns(snap.revolution_start[0]) == lo and previous_end == hi
                 and pre == snap.pretrigger_revolutions, 'snapshot aggregate revolution bounds/counts')
        summary = RotationCostWindow.summarize_minima(
            minima, required_rotations=3, mad_scale=candidate_cost_mad_scale,
            pretrigger_rotation_count=pre, verification_rotation_count=3-pre)
        _require(summary is not None and summary.valid and all(
            _same(getattr(snap, 'candidate_cost_'+key), getattr(summary, key))
            for key in ('estimate', 'mad', 'uncertainty', 'lower', 'upper')),
            'snapshot raw minima/median/MAD interval differs from actual assigned samples')
        return minima

    published_snapshots = {}
    def published_snapshot(message):
        key = (int(message.candidate_id), int(message.snapshot_revision))
        _require(min(key) > 0, 'published candidate identity')
        if key in published_snapshots:
            _require(published_snapshots[key].evidence_sha256 == snapshot_sha256(message),
                     'conflicting published candidate snapshot revision')
            return
        minima = snapshot(message)
        prior = [value for (candidate, _), value in published_snapshots.items() if candidate == key[0]]
        if prior:
            original = prior[0]
            _require(key[1] == max(value.snapshot_revision for value in prior)+1
                     and envelope_identity(message) == envelope_identity(original)
                     and message.detector_confirmation_sequence == original.detector_confirmation_sequence
                     and time_to_ns(message.accepted_at) == time_to_ns(original.accepted_at),
                     'candidate revision changed frozen association')
        else:
            _require(key[1] == 1, 'candidate lacks first snapshot revision')
        published_snapshots[key] = message
        for obs, state, first_stamp in zip(message.observations, message.observation_filter_state,
                                          message.observation_filter_stamp):
            claimed_filter_provenance[(key[0], int(obs.observation_id), int(obs.source_sequence))] = (
                state, time_to_ns(first_stamp))
        metrics['candidates'].append({'candidate_id': key[0], 'snapshot_revision': key[1],
            'search_epoch': int(message.search_epoch), 'evidence_sha256': message.evidence_sha256,
            'published_at_ns': time_to_ns(message.stamp), 'accepted_at_ns': time_to_ns(message.accepted_at),
            'confirmation_stamp_ns': time_to_ns(message.confirmation_stamp),
            'evidence_start_ns': time_to_ns(message.evidence_start), 'evidence_end_ns': time_to_ns(message.evidence_end),
            'pretrigger_revolutions': int(message.pretrigger_revolutions),
            'verification_revolutions': int(message.verification_revolutions),
            'actual_raw_cycle_minima': minima,
            'candidate_cost_estimate': float(message.candidate_cost_estimate),
            'candidate_cost_mad': float(message.candidate_cost_mad),
            'candidate_cost_lower': float(message.candidate_cost_lower),
            'candidate_cost_upper': float(message.candidate_cost_upper),
            'informative': bool(message.informative)})

    for message in rows('v2_candidate_snapshots'):
        audit('candidate', published_snapshot, message)

    commands, preparations, previous_sequence = {}, {}, [0]
    def command(message):
        envelope(message)
        sequence = int(message.command_sequence)
        proof = proofs.get(id(message))
        fingerprint = hash_payload((dict(command=message_payload(message, exclude=('stamp',)),
                                        proof=recurrent_proof_payload(proof))) if trapping
                                   else message_payload(message, exclude=('stamp',)))
        if sequence in commands:
            _require(commands[sequence][1] == fingerprint, 'conflicting command sequence')
            return
        _require(sequence > previous_sequence[0] and len(commands) < MAX_COMMANDS,
                 'command sequence regression/capacity')
        _require(min(message.search_epoch, message.candidate_id, message.preparation_id, message.objective_revision) > 0,
                 'command candidate/preparation identity')
        _require(message.operation in (1, 2, 3), 'unknown command operation')
        previous_sequence[0] = sequence
        preparation = int(message.preparation_id)
        if message.operation == 1:
            _require(preparation not in preparations, 'reused preparation identity')
            _require(time_to_ns(message.stamp) < time_to_ns(message.expires_at), 'PREPARE expired at publication')
            _require(not message.prepared_sha256, 'PREPARE already claims prepared hash')
            _require((message.redesign and min(message.target_fill_id, message.target_cluster_id, message.target_revision) > 0
                      and message.return_state == 5) or
                     (not message.redesign and not any((message.target_fill_id, message.target_cluster_id, message.target_revision))
                      and message.return_state == 4), 'preparation target/return state')
            key = (int(message.candidate_id), int(message.snapshot.snapshot_revision))
            published = published_snapshots.get(key)
            _require(published is not None and published.evidence_sha256 == message.evidence_sha256
                     and time_to_ns(published.stamp) <= time_to_ns(message.stamp),
                     'PREPARE lacks matching published candidate snapshot')
            snapshot(message.snapshot, message)
            preparations[preparation] = message
            metrics['preparations'].append({'preparation_id': preparation, 'candidate_id': int(message.candidate_id),
                'search_epoch': int(message.search_epoch), 'redesign': bool(message.redesign),
                'snapshot_revision': int(message.snapshot.snapshot_revision), 'evidence_sha256': message.evidence_sha256,
                'prepare_stamp_ns': time_to_ns(message.stamp), 'expires_at_ns': time_to_ns(message.expires_at),
                'pretrigger_revolutions': int(message.snapshot.pretrigger_revolutions),
                'verification_revolutions': int(message.snapshot.verification_revolutions)})
        else:
            original = preparations.get(preparation)
            _require(original is not None, 'command lacks recorded PREPARE')
            if trapping:
                _require(recurrent_proof_payload(proof) == recurrent_proof_payload(proofs.get(id(original))),
                         'command changed recurrent trapping proof')
            fields = ('search_epoch', 'candidate_id', 'objective_revision', 'expected_registry_generation',
                      'evidence_sha256', 'target_fill_id', 'target_cluster_id', 'target_revision', 'redesign', 'return_state')
            unused = message.snapshot
            supplied = bool(unused.candidate_id or unused.evidence_sha256 or unused.observations)
            _require(all(getattr(original, key) == getattr(message, key) for key in fields)
                     and time_to_ns(original.expires_at) == time_to_ns(message.expires_at)
                     and (not supplied or (recurrent_snapshot_sha256(unused, proof) if trapping
                          else snapshot_sha256(unused)) == original.evidence_sha256),
                     'command changed frozen preparation binding')
            _require(message.operation != 2 or _digest(message.prepared_sha256), 'ACTIVATE missing prepared hash')
        commands[sequence] = (message, fingerprint)

    for message in rows('v2_fill_commands'):
        audit('command', command, message)

    if centered_verification:
        guidance_rows = rows('v2_verification_guidance')
        metrics['verification_guidance'] = []
        if not guidance_rows:
            errors.append('V2 lifecycle missing selected verification guidance stream')
        state_revisions = {}
        for state in rows('algorithm_state'):
            try:
                key = (time_to_ns(state.stamp), hash_payload(message_payload(state)))
                state_revisions[key] = state
            except (ValueError, TypeError, AttributeError, OverflowError):
                continue
        guidance_candidates = {}
        guidance_frontier = [0, None]
        pending_approaches = []
        first_collections = {}

        def guidance(message):
            publication = time_to_ns(message.stamp)
            _require(message.schema_version == 2 and message.mode == moving_verification_mode
                     and message.run_id == identity['run_id'] and message.frame_id == config['frame_id']
                     and _finite(message.linear_x_mps, message.angular_z_radps),
                     'guidance identity or finite command differs')
            sequence = int(message.publication_sequence)
            _require(sequence > 0 and _digest(message.state_sha256),
                     'guidance publication sequence/state hash malformed')
            fingerprint = hash_payload(message_payload(message))
            _require(sequence >= guidance_frontier[0], 'guidance publication sequence regressed')
            if sequence == guidance_frontier[0]:
                _require(fingerprint == guidance_frontier[1], 'conflicting guidance publication sequence')
                return  # Exact latest replay does not create new authority or metrics.
            guidance_frontier[:] = [sequence, fingerprint]
            state = state_revisions.get((publication, message.state_sha256))
            _require(state is not None and time_to_ns(message.state_stamp) == publication
                     and state.state == message.algorithm_state,
                     'guidance lacks exact selected AlgorithmState companion')
            if not message.valid:
                _require(message.linear_x_mps == message.angular_z_radps == 0.,
                         'invalid guidance has nonzero command')
                return
            _require(state.run_id_valid and state.run_id == message.run_id
                     and state.state_valid and state.state == message.algorithm_state
                     and message.algorithm_state in (2, 3)
                     and (state.state != 3 or (state.previous_state_valid and state.previous_state == 2)),
                     'valid guidance lacks exact selected AlgorithmState companion')
            _require(message.stream_contract_id == stream_contract_id(config, origin)
                     and 0 < message.candidate_id <= MAX_COMMANDS
                     and message.search_epoch in confirmation_epochs,
                     'valid guidance contract/candidate/epoch differs')
            confirm = confirmations[confirmation_epochs[message.search_epoch]]
            accepted = time_to_ns(message.accepted_at)
            center = (message.center_x_m, message.center_y_m)
            _require(time_to_ns(confirm.stamp) <= accepted <= publication
                     and accepted-time_to_ns(confirm.source_stamp) <= FRESHNESS_NS
                     and _finite(*center) and _same(center[0], confirm.center_x_m)
                     and _same(center[1], confirm.center_y_m),
                     'guidance frozen confirmation/acceptance differs')
            frozen = (int(message.search_epoch), accepted, *center)
            previous = guidance_candidates.get(int(message.candidate_id))
            _require(previous is None or previous == frozen,
                     'guidance changed immutable candidate association')
            guidance_candidates[int(message.candidate_id)] = frozen
            snap = published_snapshots.get((int(message.candidate_id), 1))
            _require(snap is None or (snap.search_epoch == message.search_epoch
                     and time_to_ns(snap.accepted_at) == accepted
                     and _same(snap.center_x_m, center[0]) and _same(snap.center_y_m, center[1])),
                     'guidance differs from frozen initial snapshot')
            admission = collection_admissions.get(int(message.candidate_id))
            admitted = time_to_ns(message.collection_admitted_at)
            pending_admission = False
            if message.collection_started:
                _require(admission == (int(message.search_epoch), admitted)
                         and accepted <= admitted <= min(publication, accepted+8_000_000_000),
                         'guidance collection differs from actual first admission')
                deadline = min(admitted+12_000_000_000, accepted+20_000_000_000)
            else:
                pending_admission = admission == (int(message.search_epoch), publication)
                _require(admitted == 0 and (admission is None or publication < admission[1]
                         or pending_admission),
                         'guidance approach hides an admitted collection')
                deadline = accepted+8_000_000_000
            _require(time_to_ns(message.verification_expires_at) == deadline,
                     'guidance changed immutable verification deadline')
            command_deadline = time_to_ns(message.command_expires_at)
            if message.algorithm_state == 2:
                _require(command_deadline == deadline, 'VERIFY guidance command deadline differs')
            else:
                _require(message.collection_started and any(
                    not prepare.redesign and prepare.candidate_id == message.candidate_id
                    and prepare.search_epoch == message.search_epoch
                    and time_to_ns(prepare.stamp) <= publication
                    and time_to_ns(prepare.expires_at) == command_deadline
                    for prepare in preparations.values()),
                    'initial DESIGN guidance lacks matching preparation deadline')
            pose_stamp = time_to_ns(message.pose_stamp)
            pose = poses.get(pose_stamp)
            _require(publication < command_deadline and 0 <= publication-pose_stamp <= FRESHNESS_NS
                     and pose is not None and pose[0] == message.frame_id and _finite(*pose[1:]),
                     'guidance expired or lacks fresh recorded pose')
            metrics['verification_guidance'].append({
                'candidate_id': int(message.candidate_id), 'search_epoch': int(message.search_epoch),
                'publication_sequence': sequence, 'state_sha256': message.state_sha256,
                'publication_ns': publication, 'pose_stamp_ns': pose_stamp,
                'algorithm_state': int(message.algorithm_state),
                'collection_started': bool(message.collection_started),
                'verification_expires_at_ns': deadline, 'command_expires_at_ns': command_deadline})
            # Only fully checked rows can witness a transition. The first COLLECT
            # at any timestamp prevents a later backdated row from rescuing a
            # regression to APPROACH. Each row retains its own exact state join.
            if message.collection_started:
                key = (int(message.candidate_id), int(message.search_epoch), admitted)
                first_collections.setdefault(key, (sequence, publication, int(message.algorithm_state)))
            elif pending_admission:
                key = (int(message.candidate_id), int(message.search_epoch), publication)
                pending_approaches.append((key, sequence))

        for message in guidance_rows:
            audit('verification guidance', guidance, message)

        rejected_sequences = set()
        for key, sequence in pending_approaches:
            witness = first_collections.get(key)
            if witness is None or not (sequence < witness[0] and witness[1] == key[2]
                                       and witness[2] == 2):
                errors.append('V2 lifecycle verification guidance: '
                              'guidance approach hides an admitted collection')
                rejected_sequences.add(sequence)
        if rejected_sequences:
            metrics['verification_guidance'] = [row for row in metrics['verification_guidance']
                if row['publication_sequence'] not in rejected_sequences]

    prepared, commits, result_identities, terminal = {}, {}, {}, {}
    command_result_kinds = {}
    active, generation = {}, [0]
    def result(message):
        envelope(message)
        _require(message.result in (1, 2, 3, 4, 5, 6), 'unknown result')
        _require(_digest(message.committed_sha256) and result_sha256(message) == message.committed_sha256,
                 'result hash differs')
        pair = commands.get(int(message.command_sequence))
        _require(pair is not None, 'result lacks recorded command')
        sent = pair[0]
        fields = ('search_epoch', 'candidate_id', 'objective_revision', 'preparation_id',
                  'expected_registry_generation', 'evidence_sha256', 'return_state')
        _require(all(getattr(sent, key) == getattr(message, key) for key in fields)
                 and time_to_ns(sent.expires_at) == time_to_ns(message.expires_at), 'result command binding differs')
        if validate_fill_events and sent.operation in (2, 3):
            original_kind = command_result_kinds.setdefault(int(message.command_sequence), int(message.result))
            _require(original_kind == message.result, 'ACTIVATE/CANCEL command changed its cached result kind')
        key = (int(message.command_sequence), int(message.result))
        if key in result_identities:
            _require(result_identities[key] == message.committed_sha256, 'conflicting result identity')
            return
        result_identities[key] = message.committed_sha256
        preparation = int(message.preparation_id)
        if message.result == 1:
            _require(sent.operation == 1 and _digest(message.prepared_sha256), 'PREPARED command/hash')
            _require(not message.fill.fill_id and not message.has_superseded_fill
                     and time_to_ns(message.committed_at) == 0, 'PREPARED allocated or activated fill')
            _require(time_to_ns(sent.stamp) <= time_to_ns(message.prepared_at) <= time_to_ns(message.stamp)
                     and time_to_ns(message.prepared_at) < time_to_ns(message.expires_at)
                     and message.registry_generation == message.expected_registry_generation,
                     'PREPARED time/generation')
            _require(preparation not in prepared, 'multiple distinct PREPARED results')
            prepared[preparation] = message
            return
        if message.result in (3, 4, 5):
            _require(not message.fill.fill_id and not message.has_superseded_fill
                     and time_to_ns(message.committed_at) == 0, 'terminal rejection carries activation')
            if message.result != 5 or sent.operation == 1:
                terminal.setdefault(preparation, []).append(message)
            return
        _require(sent.operation in (2, 3) and preparation in prepared,
                 'activation lacks ACTIVATE/CANCEL and PREPARED evidence')
        prior = prepared[preparation]
        _require(message.prepared_sha256 == prior.prepared_sha256
                 and (sent.operation == 3 or sent.prepared_sha256 == prior.prepared_sha256),
                 'activation prepared hash differs')
        commit_ns = time_to_ns(message.committed_at)
        _require(time_to_ns(prior.prepared_at) == time_to_ns(message.prepared_at)
                 and time_to_ns(prior.stamp) <= commit_ns < time_to_ns(message.expires_at)
                 and commit_ns <= time_to_ns(message.stamp), 'commit preparation/deadline/publication ordering')
        commit_key = _commit_key(message)
        if message.registry_generation in commits:
            _require(commits[message.registry_generation][0] == commit_key, 'conflicting committed generation')
            if validate_fill_events:
                original_commit = commits[message.registry_generation][1]
                _require(message.result == 6
                         and message.command_sequence > original_commit.command_sequence,
                         'postcommit reply requires newer command sequence and ALREADY_ACTIVATED')
                original_command = commands[int(original_commit.command_sequence)][0]
                immutable = ('candidate_id', 'objective_revision', 'preparation_id',
                             'expected_registry_generation', 'evidence_sha256',
                             'target_fill_id', 'target_cluster_id', 'target_revision', 'redesign', 'return_state')
                _require(envelope_identity(sent) == envelope_identity(original_command)
                         and all(getattr(sent, field) == getattr(original_command, field) for field in immutable)
                         and time_to_ns(sent.expires_at) == time_to_ns(original_command.expires_at)
                         and message.prepared_sha256 == original_commit.prepared_sha256,
                         'postcommit retry changed original transaction identity')
            return
        _require(message.result == 2 and sent.operation == 2, 'ALREADY_ACTIVATED lacks original ACTIVATED authority')
        _require(message.expected_registry_generation == generation[0]
                 and message.registry_generation == generation[0]+1
                 and message.registry_digest_before == fill_registry_digest(active.values()),
                 'activation registry generation/before digest chain')
        fill = message.fill
        _require(fill.active and not fill.superseded and fill.covariance_valid
                 and min(fill.fill_id, fill.cluster_id, fill.revision) > 0
                 and fill.fill_id not in active and fill.frame_id == config['frame_id']
                 and _finite(fill.amplitude, fill.center_x, fill.center_y, fill.covariance_xx, fill.covariance_xy, fill.covariance_yy)
                 and fill.amplitude > 0 and fill.covariance_xx > 0
                 and fill.covariance_xx*fill.covariance_yy-fill.covariance_xy**2 > 0,
                 'activated fill law/identity invalid')
        updated = dict(active)
        original = preparations[preparation]
        if validate_fill_events:
            expected_source = (time_to_ns(original.snapshot.confirmation_stamp)-origin)*1e-9
            _require(fill.source_timestamp_valid and _finite(fill.source_timestamp)
                     and fill.source_timestamp == expected_source,
                     'committed fill source differs from original confirmation and Timekeeper origin')
            _require(time_to_ns(sent.stamp) <= commit_ns <= time_to_ns(fill.stamp)
                     <= time_to_ns(message.stamp), 'activation command/fill publication ordering')
        if message.has_superseded_fill:
            old = updated.get(int(message.superseded_fill.fill_id))
            _require(original.redesign and old is not None
                     and (old.fill_id, old.cluster_id, old.revision) ==
                         (original.target_fill_id, original.target_cluster_id, original.target_revision)
                     and not message.superseded_fill.active and message.superseded_fill.superseded
                     and fill.cluster_id == old.cluster_id and fill.revision == old.revision+1,
                     'atomic supersession does not match exact active target')
            prior_law = message_payload(old, exclude=('stamp', 'active', 'superseded'))
            _require(message_payload(message.superseded_fill, exclude=('stamp', 'active', 'superseded')) == prior_law,
                     'superseded fill changed retained version')
            del updated[old.fill_id]
        else:
            _require(not original.redesign and fill.revision == 1
                     and all(f.cluster_id != fill.cluster_id for f in updated.values()), 'new fill target/revision')
        updated[fill.fill_id] = fill
        _require(fill_registry_digest(updated.values()) == message.registry_digest_after,
                 'activation after digest differs from combined fill map')
        active.clear(); active.update(updated)
        generation[0] = int(message.registry_generation)
        commits[generation[0]] = (commit_key, message)
        metrics['commits'].append({'registry_generation': generation[0], 'candidate_id': int(message.candidate_id),
            'preparation_id': preparation, 'fill_id': int(fill.fill_id), 'committed_at_ns': commit_ns,
            'registry_digest_before': message.registry_digest_before, 'registry_digest_after': message.registry_digest_after})

    result_order = {id(message): index for index, message in enumerate(rows('v2_fill_results'))}
    for message in rows('v2_fill_results'):
        audit('result', result, message)
    for _, commit in commits.values():
        for event in terminal.get(commit.preparation_id, []):
            if result_order[id(event)] < result_order[id(commit)]:
                errors.append('V2 lifecycle commit follows terminal cancellation/rejection in result publisher order')
            else:
                errors.append('V2 lifecycle terminal cancellation/rejection contradicts accepted commit')
        digest = commit.registry_digest_after
        def acknowledgement_stamps(alias, flag):
            stamps = []
            for message in rows(alias):
                try:
                    if getattr(message, flag) and message.registry_digest == digest:
                        envelope(message, stream=True)
                        stamps.append(time_to_ns(message.stamp))
                except (ValueError, TypeError, AttributeError, OverflowError):
                    continue  # Strict M2 checks separately report malformed acknowledgements.
            return stamps
        objective_stamps = acknowledgement_stamps(config['objective_cost_topic'], 'valid')
        direction_stamps = acknowledgement_stamps('v2_direction_diagnostics', 'algorithm_state_valid')
        metrics['acknowledgements'].append({'registry_generation': int(commit.registry_generation),
            'first_objective_stamp_ns': min(objective_stamps, default=None),
            'first_direction_stamp_ns': min(direction_stamps, default=None)})
    authorities = []
    for _, commit in commits.values():
        authorities.append(commit.fill)
        if commit.has_superseded_fill:
            authorities.append(commit.superseded_fill)
    for mirror in rows('gaussian_fills'):
        payload = message_payload(mirror, exclude=('stamp',))
        if not any(message_payload(authority, exclude=('stamp',)) == payload
                   and time_to_ns(mirror.stamp) >= time_to_ns(authority.stamp) for authority in authorities):
            errors.append('V2 lifecycle canonical fill mirror lacks matching typed activation authority')
    authorized_digests = {fill_registry_digest([]): origin}
    authorized_digests.update({commit.registry_digest_after: time_to_ns(commit.committed_at)
                               for _, commit in commits.values()})
    def objective_authority(message):
        if not message.valid:
            return
        envelope(message, stream=True)
        created = authorized_digests.get(message.registry_digest)
        _require(created is not None and time_to_ns(message.composition_stamp) >= created,
                 'objective registry digest lacks prior typed activation authority')
    for message in rows(config['objective_cost_topic']):
        audit('objective', objective_authority, message)
    metrics['goal_states'] = []
    def goal_state(state):
        if state.state_valid and state.run_id_valid and state.run_id == identity['run_id'] and state.state == 7:
            stamp = time_to_ns(state.stamp)
            prior_epochs = [(time_to_ns(ctx.stamp), ctx.search_epoch) for ctx, _ in contexts.values()
                            if ctx.valid and time_to_ns(ctx.stamp) <= stamp]
            search_epoch = max(prior_epochs, default=(0, None))[1]
            matching = [snap for snap in published_snapshots.values() if snap.search_epoch == search_epoch
                        and time_to_ns(snap.stamp) <= stamp]
            metrics['goal_states'].append({'stamp_ns': stamp, 'search_epoch': search_epoch,
                'candidate_ids': sorted({int(snap.candidate_id) for snap in matching}),
                'association': 'same recorded epoch; AlgorithmState has no candidate ID'})
            if not matching:
                errors.append('V2 lifecycle GOAL lacks published verified candidate evidence in its recorded epoch')
    for state in rows('algorithm_state'):
        audit('GOAL state', goal_state, state)
    if validate_fill_events:
        # Reuse only original ACTIVATED authorities admitted above. A PREPARE,
        # cancellation or retry acknowledgement cannot independently authorize
        # an event, and a failure anywhere in the chain cannot mint authority.
        event_errors, event_audit = [], []
        if errors:
            event_errors.append({'error': 'selected moving lifecycle chain is invalid',
                                 'lifecycle_errors': list(errors)})
        authorities = []
        for _, commit in commits.values():
            fill = commit.fill
            names = ['cluster_id', 'revision', 'registry_generation', 'amplitude_cost_units', 'sample_count']
            values = [fill.cluster_id, fill.revision, commit.registry_generation, fill.amplitude, fill.sample_count]
            authorities.append((22 if commit.has_superseded_fill else 20, commit, fill, names, values))
            if commit.has_superseded_fill:
                old = commit.superseded_fill
                authorities.append((23, commit, old,
                    ['cluster_id', 'revision', 'superseded_fill_id', 'new_fill_id'],
                    [old.cluster_id, old.revision, old.fill_id, fill.fill_id]))
        seen_events, previous_stamp = set(), None
        recorded_superseded_ids = {
            event.fill_id for _, event in messages.get(selected['algorithm_events'], [])
            if event is not None and getattr(event, 'event_type', None) == 23
            and getattr(event, 'fill_id_valid', False)}
        for bag_stamp, event in messages.get(selected['algorithm_events'], []):
            try:
                _require(event is not None, 'malformed AlgorithmEvent')
                kind = int(event.event_type)
                if not 20 <= kind <= 26:
                    continue
                _require(event.source_timestamp_valid and _finite(event.source_timestamp),
                         'fill event source is unavailable or nonfinite')
                _require(event.fill_id_valid and event.fill_id > 0, 'fill event identity unavailable')
                _require(len(event.value_names) == len(event.values)
                         and len(set(event.value_names)) == len(event.value_names)
                         and _finite(*event.values), 'fill event value fields malformed')
                stamp = time_to_ns(event.stamp)
                _require(stamp >= origin and (previous_stamp is None or stamp >= previous_stamp),
                         'fill owner event publication order regressed')
                previous_stamp = stamp
                matches = [item for item in authorities if item[0] == kind and item[2].fill_id == event.fill_id]
                _require(len(matches) == 1, 'fill event lacks unique original activation authority')
                _, commit, fill, names, values = matches[0]
                if kind == 22 and commit.superseded_fill.fill_id in recorded_superseded_ids:
                    _require((int(commit.registry_generation), 23, int(commit.superseded_fill.fill_id)) in seen_events,
                             'merged event precedes recorded supersession in owner publication order')
                key = (int(commit.registry_generation), kind, int(fill.fill_id))
                _require(key not in seen_events, 'duplicate fill owner event identity')
                seen_events.add(key)
                _require(event.source_timestamp == fill.source_timestamp,
                         'fill event source differs from exact committed version')
                _require(list(event.value_names) == names and list(event.values) == [float(v) for v in values],
                         'fill event kind/cluster/revision/generation/payload differs from authority')
                _require(stamp >= time_to_ns(commit.stamp)
                         and relative_stamp_ns(origin, event.source_timestamp) <= stamp,
                         'fill event precedes committed authority or source')
                payload = message_payload(fill, exclude=('stamp',))
                _require(any(message_payload(mirror, exclude=('stamp',)) == payload
                             and time_to_ns(fill.stamp) <= time_to_ns(mirror.stamp) <= stamp
                             for mirror in rows('gaussian_fills')),
                         'fill event lacks exact canonical GaussianFill publication')
                _require(not errors, 'fill event has an invalid lifecycle authority chain')
                event_audit.append({'bag_timestamp': int(bag_stamp), 'event_type': kind,
                    'event_stamp_ns': stamp, 'source_timestamp': float(event.source_timestamp),
                    'fill_id': int(fill.fill_id), 'cluster_id': int(fill.cluster_id),
                    'revision': int(fill.revision), 'registry_generation': int(commit.registry_generation),
                    'search_epoch': int(commit.search_epoch), 'candidate_id': int(commit.candidate_id),
                    'preparation_id': int(commit.preparation_id), 'command_sequence': int(commit.command_sequence),
                    'run_id': commit.run_id, 'stream_contract_id': commit.stream_contract_id,
                    'frame_id': commit.frame_id, 'time_origin_ns': origin,
                    'objective_revision': int(commit.objective_revision),
                    'evidence_sha256': commit.evidence_sha256, 'prepared_sha256': commit.prepared_sha256,
                    'committed_sha256': commit.committed_sha256})
            except (ValueError, TypeError, AttributeError, OverflowError, IndexError, KeyError) as exc:
                event_errors.append({'bag_timestamp': int(bag_stamp), 'error': str(exc)})
        metrics['fill_event_source_causality'] = {
            'passed': not event_errors, 'errors': event_errors, 'events': event_audit}
        errors.extend('V2 lifecycle fill event: ' + entry['error'] for entry in event_errors)
    metrics['counts'] = {'epoch_heartbeats': len(rows('v2_search_epoch')), 'valid_epochs': len(epochs),
        'confirmations': len(confirmations), 'pde_histories': len(histories),
        'candidate_snapshots': len(published_snapshots), 'commands': len(commands),
        'preparations': len(preparations), 'prepared': len(prepared),
        'unique_commits': len(commits), 'terminal_results': sum(map(len, terminal.values())),
        'errors': len(errors)}
    return errors, metrics
