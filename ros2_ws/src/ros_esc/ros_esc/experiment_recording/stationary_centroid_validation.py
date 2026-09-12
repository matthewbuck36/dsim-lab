"""Recorded Arm B provenance and result joins for the existing run validator.

Cross-topic order uses source/publication stamps. Bag receipt order cannot
reconstruct subscriber receipts or the unrecorded steady-clock commit guard.
These are observed pipeline intervals, not independent settling/goal labels.
"""

import math

from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC

from ros_esc.stationary_fill_protocol import (
    centroid_configuration_errors, stationary_request_errors, stationary_contract,
)
from ros_esc.v2_lifecycle import MAX_COMMANDS, hash_payload, message_payload
from ros_esc.v2_stream import relative_stamp_ns, time_to_ns


TOPICS = {
    'stationary_fill_requests': '/gesc_gaussian/v2/stationary_fill_requests',
    'stationary_recurrent_fill_requests': '/gesc_gaussian/v2/stationary_recurrent_fill_requests',
    'centroid_convergence_diagnostics': '/gesc_gaussian/v2/convergence_diagnostics',
    'recurrent_convergence_diagnostics': RECURRENT_TOPIC,
    'algorithm_state': '/gesc_gaussian/algorithm_state',
    'gaussian_fills': '/gesc_gaussian/gaussian_fills',
    'algorithm_events': '/gesc_gaussian/algorithm_events',
}


def stationary_centroid_stream_errors(messages, config, *, topics=None):
    """Return errors and audit tables from ``topic: [(bag_ns, wire), ...]``.

No request or terminal result is a valid recorded outcome. Existing manifest
type/presence checks own required topics even when their event count is zero.
"""
    selected = dict(TOPICS)
    selected.update({key: value for key, value in (topics or {}).items() if value})
    recurrent = config.get('metric_mode') == RECURRENT_MODE
    contract = stationary_contract(config.get('metric_mode', 'centroid_windows_v2'))
    request_alias, diagnostic_alias = contract['request_alias'], contract['diagnostics_alias']
    contract_name = 'stationary recurrent' if recurrent else 'stationary centroid'
    errors = []
    audit = {'confirmations': [], 'requests': [], 'outcomes': [], 'timelines': [],
             'counts': {}, 'timing_scope': 'observed source/publication intervals only; '
             'no independent settling label or reconstructed callback authority'}

    def rows(alias):
        return messages.get(selected.get(alias, alias), [])

    def require(condition, reason):
        if not condition:
            raise ValueError(reason)

    def failure(kind, error):
        errors.append(contract_name + ' ' + kind + ': ' + str(error))

    # The configured stream owns authority, even if only an incompatible
    # alternative request was recorded. Never reinterpret the other envelope.
    other_alias = 'stationary_fill_requests' if recurrent else 'stationary_recurrent_fill_requests'
    if rows(other_alias):
        failure('selection', 'requests recorded on the unselected stationary envelope')
    if recurrent:
        audit['metric_mode'] = RECURRENT_MODE

    origins = set()
    for _, message in messages.get(config['timekeeper_topic'], []):
        try:
            require(message.mode == 'sim time', 'Timekeeper mode is not simulation')
            origins.add(relative_stamp_ns(0, message.start_time))
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            failure('origin', error)
    if len(origins) != 1:
        failure('origin', 'one immutable observed Timekeeper origin is required')
        return errors, audit
    origin = next(iter(origins))

    states = [message for _, message in rows('algorithm_state') if message is not None
              and message.state_valid and message.run_id_valid and message.run_id
              and message.algorithm_profile == 'robust_gaussian_v1']
    runs = {message.run_id for message in states}
    confirmations = {}
    for bag_ns, message in rows(diagnostic_alias):
        if message is None or not message.confirmed:
            continue
        digest = hash_payload(message_payload(message))
        if digest not in confirmations:
            confirmations[digest] = message
            audit['confirmations'].append({
                'run_id': message.run_id, 'search_epoch': int(message.search_epoch),
                'confirmation_sequence': int(message.confirmation_sequence),
                'confirmation_sha256': digest, 'source_stamp_ns': time_to_ns(message.source_stamp),
                'publication_ns': time_to_ns(message.stamp), 'bag_receipt_ns': bag_ns,
            })
            if recurrent:
                audit['confirmations'][-1].update(
                    branch=message.branch,
                    history_start_ns=time_to_ns(message.history_start),
                    history_end_ns=time_to_ns(message.history_end),
                    persistence_start_ns=time_to_ns(message.persistence_start),
                    persistence_count=int(message.persistence_count),
                    persistence_required=int(message.persistence_required),
                    center_x_m=float(message.center_x_m), center_y_m=float(message.center_y_m),
                    drift_m_s=float(message.drift_m_s),
                    confinement_radius_m=float(message.confinement_radius_m))

    requests, previous_sequence, retries, used_candidates = {}, {}, 0, set()
    for bag_ns, message in rows(request_alias):
        try:
            require(message is not None, 'missing request message')
            run = message.confirmation.run_id
            require(run in runs, 'request has no matching observed robust supervisor run')
            static = stationary_request_errors(message, run, config['frame_id'],
                config['source_pose_topic'], origin, config['maximum_source_gap_sec'],
                config['pose_freshness_sec'], expected_metric_mode=config.get('metric_mode'))
            if not recurrent:
                static += centroid_configuration_errors(message.confirmation, config['window_sec'],
                    config['epsilon_m'], config['maximum_radius_m'],
                    expected_metric_mode=config.get('metric_mode'))
            require(not static, '; '.join(static))
            key = (run, int(message.request_sequence))
            if key in requests:
                require(requests[key][0].request_sha256 == message.request_sha256,
                        'conflicting request sequence')
                retries += 1
                continue
            require(len(requests) < MAX_COMMANDS, 'request ledger capacity exceeded')
            require(key[1] > previous_sequence.get(run, 0), 'request sequence regressed')
            require(not any(abs(old.source_timestamp-message.source_timestamp) <= 1e-9
                            for old, _ in requests.values()), 'request correlation collision')
            digest = hash_payload(message_payload(message.confirmation))
            require(digest in confirmations, 'nested confirmation differs from recorded diagnostic')
            if message.operation == message.CREATE:
                require(message.candidate_evidence_valid == config['candidate_informed_fill_enabled'],
                        'candidate evidence differs from selected policy')
                require(digest not in used_candidates, 'confirmation reused by a distinct CREATE request')
            publication, deadline = time_to_ns(message.stamp), time_to_ns(message.expires_at)
            # Source entry, not cross-topic delivery order, binds the original
            # DESIGN deadline. Float seconds may round by one nanosecond.
            entries = []
            for state in states:
                if (state.run_id != run or state.state != state.STATE_DESIGN_OR_MERGE_FILL
                        or not state.state_elapsed_valid or not math.isfinite(state.state_elapsed_sec)
                        or state.state_elapsed_sec < 0 or not state.previous_state_valid
                        or state.previous_state != (state.STATE_VERIFY_EXTREMUM
                            if message.operation == message.CREATE else state.STATE_ESCAPE_REPULSE)):
                    continue
                entered = time_to_ns(state.stamp)-round(state.state_elapsed_sec*1e9)
                if (entered <= publication and abs(deadline-entered
                        -round(config['design_timeout_sec']*1e9)) <= 1):
                    entries.append(entered)
            require(entries, 'request lacks matching recorded original DESIGN deadline')
            previous_sequence[run] = key[1]
            if message.operation == message.CREATE:
                used_candidates.add(digest)
            row = {
                'run_id': run, 'request_sequence': key[1], 'request_sha256': message.request_sha256,
                'operation': int(message.operation), 'confirmation_sha256': digest,
                'search_epoch': int(message.confirmation.search_epoch),
                'confirmation_sequence': int(message.confirmation.confirmation_sequence),
                'confirmation_received_ns': time_to_ns(message.confirmation_received_at),
                'confirmation_accepted_ns': time_to_ns(message.confirmation_accepted_at),
                'publication_ns': publication, 'deadline_ns': deadline, 'time_origin_ns': origin,
                'source_timestamp': float(message.source_timestamp), 'bag_receipt_ns': bag_ns,
                'target_fill_id': int(message.target_fill_id),
                'target_cluster_id': int(message.target_cluster_id),
                'target_revision': int(message.target_revision),
            }
            requests[key] = (message, row)
            audit['requests'].append(row)
            audit['timelines'].append({
                'kind': 'accepted_confirmation_to_request', 'run_id': run,
                'request_sequence': key[1], 'start_ns': row['confirmation_accepted_ns'],
                'end_ns': publication,
                'duration_sec': (publication-row['confirmation_accepted_ns'])*1e-9,
            })
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            failure('request', error)

    def match(message):
        require(message.source_timestamp_valid and math.isfinite(message.source_timestamp),
                'result has no valid relative correlation')
        matches = [(key, request, row) for key, (request, row) in requests.items()
                   if abs(message.source_timestamp-request.source_timestamp) <= 1e-9]
        require(len(matches) == 1, 'result lacks a unique request correlation')
        return matches[0]

    fills, seen_fills, successes, failures = [], set(), set(), set()
    for bag_ns, message in rows('gaussian_fills'):
        try:
            key, request, row = match(message)
            require(message.frame_id == config['frame_id'], 'fill frame differs from request')
            publication = time_to_ns(message.stamp)
            require(publication >= row['publication_ns'], 'fill published before request')
            # A superseded version retains its ORIGINAL request correlation;
            # its later supersession publication is not a new fit or deadline.
            require(not message.active or not message.superseded, 'fill is active and superseded')
            digest = hash_payload(message_payload(message))
            if digest in seen_fills:
                continue
            seen_fills.add(digest)
            fills.append(message)
            outcome = dict(run_id=key[0], request_sequence=key[1], kind='fill',
                           fill_id=int(message.fill_id), cluster_id=int(message.cluster_id),
                           revision=int(message.revision), active=bool(message.active),
                           superseded=bool(message.superseded), publication_ns=publication,
                           bag_receipt_ns=bag_ns, outcome_sha256=digest)
            audit['outcomes'].append(outcome)
            if message.active and key not in successes:
                successes.add(key)
                audit['timelines'].append({
                    'kind': 'request_to_active_fill_publication', 'run_id': key[0],
                    'request_sequence': key[1], 'start_ns': row['publication_ns'],
                    'end_ns': publication, 'duration_sec': (publication-row['publication_ns'])*1e-9,
                })
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            failure('fill', error)

    for key, (request, row) in requests.items():
        if request.operation != request.TARGETED_REDESIGN:
            continue
        # Only versions already published by the request can justify its exact
        # target. Later supersession/retry publications do not rewrite history.
        prior = [fill for fill in fills if time_to_ns(fill.stamp) <= row['publication_ns']
                 and fill.cluster_id == request.target_cluster_id]
        revisions = [fill.revision for fill in prior]
        target = [fill for fill in prior if fill.active and not fill.superseded
                  and (fill.fill_id, fill.revision) == (request.target_fill_id, request.target_revision)]
        retired = any(fill.fill_id == request.target_fill_id and fill.superseded for fill in prior)
        if not target or retired or request.target_revision != max(revisions, default=0):
            failure('redesign', 'request target lacks an exact current recorded active version')

    seen_events = set()
    for bag_ns, message in rows('algorithm_events'):
        if message is None or not 20 <= message.event_type <= 26:
            continue
        try:
            key, request, row = match(message)
            require(time_to_ns(message.stamp) >= row['publication_ns'], 'event published before request')
            digest = hash_payload(message_payload(message))
            if digest in seen_events:
                continue
            seen_events.add(digest)
            audit['outcomes'].append({
                'run_id': key[0], 'request_sequence': key[1], 'kind': 'event',
                'event_type': int(message.event_type), 'reason_code': int(message.reason_code),
                'fill_id': int(message.fill_id) if message.fill_id_valid else None,
                'publication_ns': time_to_ns(message.stamp), 'bag_receipt_ns': bag_ns,
                'outcome_sha256': digest,
            })
            if message.event_type in (message.EVENT_FILL_REJECTED, message.EVENT_FILL_DESIGN_FAILED):
                failures.add(key)
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            failure('event', error)
    if successes & failures:
        failure('outcome', 'same request has both an active fill and terminal rejection')
    audit['counts'] = dict(unique_confirmations=len(confirmations), unique_requests=len(requests),
        request_retries=retries, requests_with_active_fill=len(successes),
        requests_with_terminal_failure=len(failures),
        requests_without_terminal_outcome=len(requests.keys()-successes-failures))
    return errors, audit
